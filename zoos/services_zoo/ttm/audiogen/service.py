import importlib
import sys
import subprocess
from pathlib import Path
from typing import List, Dict, Optional
import numpy as np
import io

# --- Dependency Management ---
try:
    import pipmaster as pm
except ImportError:
    print("ERROR: pipmaster library not found.")
    print("Please install it using: pip install pipmaster")
    raise ImportError("pipmaster is mandatory for Lollms binding installation.")

# --- Optional PyTorch Pre-install ---
# pm.install_if_missing("torch", index_url="https://download.pytorch.org/whl/cu124")
# ...

# --- Lollms Imports ---
from lollms.app import LollmsApplication
from lollms.config import TypedConfig, BaseConfig, ConfigTemplate
from lollms.ttm import LollmsTTM
from lollms.helpers import ASCIIColors
from lollms.utilities import PackageManager, show_yes_no_dialog

# --- Helper Functions ---
def check_torch_cuda():
    try:
        import torch
        return torch.cuda.is_available()
    except Exception:
        return False

def check_torch_mps():
    try:
        import torch
        if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            return True
        else:
            return False
    except Exception:
        return False

# --- Configuration ---
DEFAULT_CONFIG = {
    # ----- Model selection -----
    "model_name": "facebook/audiogen-medium", # Or other audiogen models
    # ----- Generation parameters -----
    "max_new_tokens": 512, # Corresponds roughly to duration. Adjust based on model's token/sec rate.
    "guidance_scale": 3.0, # Higher values follow prompt more closely.
    "temperature": 1.0, # Controls randomness.
    "top_k": 250,       # Limits sampling to top K tokens.
    "top_p": 0.0,       # Nucleus sampling threshold (0 disables).
    "seed": -1,         # Random seed. -1 for random.
    # ----- Hardware -----
    "device": "auto", # "auto", "cpu", "cuda", "mps"
    # ----- Installation -----
    "always_update_transformers": False
}

class AudioGenTTMConfig(BaseConfig):
    def __init__(self, config: dict = None):
        effective_config = {**DEFAULT_CONFIG, **(config or {})}
        super().__init__(effective_config)

    def validate(self):
        allowed_devices = ["auto", "cpu", "cuda", "mps"]
        if self.device not in allowed_devices:
            raise ValueError(f"Invalid device '{self.device}'. Must be one of: {allowed_devices}")
        if self.max_new_tokens <= 0:
             raise ValueError("'max_new_tokens' must be positive.")

# --- Main Binding Class ---
class AudioGenTTM(LollmsTTM):
    """
    Lollms binding for Facebook's AudioGen Text-to-Audio model using Hugging Face transformers.
    """
    def __init__(
        self,
        app: LollmsApplication,
        config: Optional[dict] = None,
        service_config: Optional[TypedConfig] = None,
        output_folder: Optional[str | Path] = None,
        **kwargs
    ):
        config_template = ConfigTemplate([
            {"name": "model_name", "type": "str", "value": DEFAULT_CONFIG["model_name"], "help": "The specific AudioGen model checkpoint (e.g., 'facebook/audiogen-medium')."},
            {"name": "max_new_tokens", "type": "int", "value": DEFAULT_CONFIG["max_new_tokens"], "min": 10, "help": "Max tokens influence duration. Exact tokens/sec varies."},
            {"name": "guidance_scale", "type": "float", "value": DEFAULT_CONFIG["guidance_scale"], "min": 1.0, "help": "Controls prompt adherence vs. creativity."},
            {"name": "temperature", "type": "float", "value": DEFAULT_CONFIG["temperature"], "min": 0.01, "max": 2.0, "help": "Controls randomness."},
            {"name": "top_k", "type": "int", "value": DEFAULT_CONFIG["top_k"], "min": 0, "help": "Restricts sampling to top K tokens (0 disables)."},
            {"name": "top_p", "type": "float", "value": DEFAULT_CONFIG["top_p"], "min": 0.0, "max": 1.0, "help": "Nucleus sampling threshold (0 disables)."},
            {"name": "seed", "type": "int", "value": DEFAULT_CONFIG["seed"], "help": "Seed for reproducibility (-1 for random)."},
            {"name": "device", "type": "str", "value": DEFAULT_CONFIG["device"], "help": "Device: 'auto', 'cpu', 'cuda', 'mps'."},
            {"name": "always_update_transformers", "type": "bool", "value": DEFAULT_CONFIG["always_update_transformers"], "help": "Update transformers library on each load."}
        ])
        typed_config = TypedConfig(config_template)

        super().__init__(
            name="audiogen", # Unique name
            app=app,
            service_config=typed_config,
            output_folder=output_folder
        )

        self.model = None
        self.processor = None
        self.torch = None
        self.transformers = None
        self.scipy_wavfile = None
        self._device = None

        # --- Dependency Check and Installation (Identical to MusicGen) ---
        if not self.verify(app):
            if show_yes_no_dialog("Confirmation", f"The AudioGen binding requires installing dependencies (torch, transformers, scipy, numpy). Install now?"):
                self.install(app)
                if not self.verify(app):
                    app.error("AudioGen binding dependencies still missing after installation attempt.")
                    # raise RuntimeError("Failed to install required AudioGen dependencies.")
            else:
                app.error("AudioGen binding dependencies not installed.")
                # raise RuntimeError("User declined to install required AudioGen dependencies.")

        if self.service_config.always_update_transformers:
             # Identical update logic as MusicGen
            self.app.ShowBlockingMessage("Checking for transformers library update...")
            try:
                pm.install("transformers", force_reinstall=True, upgrade=True)
                app.InfoMessage("Transformers library updated successfully.")
                if "transformers" in sys.modules:
                    try:
                        importlib.reload(sys.modules["transformers"])
                        self.transformers = sys.modules["transformers"]
                    except Exception as reload_err:
                        app.warning(f"Could not reload transformers after update: {reload_err}")
            except Exception as e:
                app.error(f"Failed to update transformers library: {e}")
            finally:
                self.app.HideBlockingMessage()

    def settings_updated(self):
        self.model = None # Force reload on config change
        self.processor = None
        self._device = None

    @staticmethod
    def get_dependencies() -> List[str]:
        return ["torch", "transformers", "scipy", "numpy"]

    @staticmethod
    def verify(app: LollmsApplication) -> bool:
        # Identical to MusicGen verify
        missing = []
        for package in AudioGenTTM.get_dependencies():
            try:
                importlib.import_module(package)
            except ImportError:
                missing.append(package)
        if missing:
            app.warning(f"AudioGen binding verification failed. Missing: {', '.join(missing)}")
            return False
        return True

    @staticmethod
    def install(app: LollmsApplication) -> bool:
        # Identical to MusicGen install
        app.ShowBlockingMessage("Installing AudioGen dependencies (torch, transformers, scipy, numpy)...")
        try:
            pm.install_if_missing("torch")
            pm.install_if_missing("transformers")
            pm.install_if_missing("scipy")
            pm.install_if_missing("numpy")
            app.InfoMessage("AudioGen dependencies installed successfully.")
            PackageManager.rebuild_packages()
            return True
        except Exception as e:
            app.error(f"Failed to install AudioGen dependencies: {e}")
            return False
        finally:
            app.HideBlockingMessage()

    def _load_model(self):
        if self.model is not None and self.processor is not None:
            return True

        self.app.ShowBlockingMessage(f"Loading AudioGen model: {self.service_config.model_name}...")
        try:
            self.torch = importlib.import_module("torch")
            self.transformers = importlib.import_module("transformers")
            self.scipy_wavfile = importlib.import_module("scipy.io.wavfile")

            # Determine device (Identical logic)
            requested_device = self.service_config.device.lower()
            if requested_device == "auto":
                if check_torch_cuda(): self._device = "cuda"
                elif check_torch_mps(): self._device = "mps"
                else: self._device = "cpu"
            elif requested_device == "cuda" and check_torch_cuda(): self._device = "cuda"
            elif requested_device == "mps" and check_torch_mps(): self._device = "mps"
            else:
                if requested_device in ["cuda", "mps"]:
                     self.app.warning(f"{requested_device.upper()} requested but not available. Falling back to CPU.")
                self._device = "cpu"
            self.app.InfoMessage(f"Using device: {self._device}")

            # Load processor and model (Adjust class names if necessary for AudioGen)
            AutoProcessor = self.transformers.AutoProcessor
            # Check Hugging Face Hub for the correct AutoModel class for AudioGen
            # It might be AutoModelForTextToWaveform or similar
            AutoModelForTextToWaveform = self.transformers.AutoModelForTextToWaveform

            self.processor = AutoProcessor.from_pretrained(self.service_config.model_name)
            self.model = AutoModelForTextToWaveform.from_pretrained(self.service_config.model_name)

            self.model.to(self._device)
            self.model.eval()

            self.app.InfoMessage(f"AudioGen model '{self.service_config.model_name}' loaded successfully onto {self._device}.")
            return True

        except Exception as e:
            self.app.error(f"Failed to load AudioGen model '{self.service_config.model_name}': {e}")
            import traceback
            self.app.error(traceback.format_exc())
            self.model = None
            self.processor = None
            self._device = None
            return False
        finally:
             self.app.HideBlockingMessage()


    def generate(self,
                    prompt: str,
                    negative_prompt: str = "", # Keep for consistency, may not be used by model.generate
                    duration_s: Optional[float] = None, # Will be estimated via max_new_tokens
                    seed: Optional[int] = None,
                    guidance_scale: Optional[float] = None,
                    temperature: Optional[float] = None,
                    top_k: Optional[int] = None,
                    top_p: Optional[float] = None,
                    max_new_tokens: Optional[int] = None,
                    output_dir: Optional[str | Path] = None,
                    output_file_name: Optional[str] = None
                    ) -> List[Dict[str, str]]:
            if not self._load_model():
                self.app.error("AudioGen model not loaded. Cannot generate audio.")
                return []

            self.app.ShowBlockingMessage(f"Generating audio for prompt: '{prompt[:70]}...'")

            try:
                # --- Parameter Preparation (Mostly identical to MusicGen) ---
                gen_seed = seed if seed is not None else self.service_config.seed
                gen_guidance_scale = guidance_scale if guidance_scale is not None else self.service_config.guidance_scale
                gen_temperature = temperature if temperature is not None else self.service_config.temperature
                gen_top_k = top_k if top_k is not None else self.service_config.top_k
                gen_top_p = top_p if top_p is not None else self.service_config.top_p

                # Determine max_new_tokens (similar estimation logic)
                if duration_s is not None and duration_s > 0:
                    try:
                        sampling_rate = self.model.config.sampling_rate # AudioGen might store it here
                    except AttributeError:
                        sampling_rate = 16000 # Common default for AudioGen
                        self.app.warning(f"Could not determine model sampling rate, assuming {sampling_rate} Hz.")

                    # Adjust tokens_per_second based on AudioGen's characteristics if known, otherwise guess
                    tokens_per_second = 50 # Placeholder - adjust if needed
                    gen_max_new_tokens = int(duration_s * tokens_per_second)
                    self.app.InfoMessage(f"Duration {duration_s}s requested, estimated max_new_tokens: {gen_max_new_tokens}")
                else:
                    gen_max_new_tokens = max_new_tokens if max_new_tokens is not None else self.service_config.max_new_tokens

                if gen_max_new_tokens <= 0:
                    self.app.warning(f"max_new_tokens was <= 0 ({gen_max_new_tokens}), setting to default.")
                    gen_max_new_tokens = DEFAULT_CONFIG["max_new_tokens"]


                # --- Input Processing ---
                inputs = self.processor(
                    text=[prompt],
                    padding=True,
                    return_tensors="pt",
                ).to(self._device)


                # --- Seed Handling ---
                generator = None
                if gen_seed is not None and gen_seed != -1:
                    # Use torch.manual_seed for generate in transformers < 4.31?
                    # Or check if model.generate accepts a generator for newer versions
                    # For simplicity and broad compatibility, using the global seed might be easier here.
                    self.torch.manual_seed(gen_seed)
                    if self._device == 'cuda': self.torch.cuda.manual_seed_all(gen_seed)
                    # MPS seeding might require specific handling if applicable
                    self.app.info(f"Using seed: {gen_seed}")
                else:
                    self.app.info("Using random seed.")

                # --- Generation Call ---
                # Check AudioGen's specific generate arguments
                generation_args = {
                    "max_new_tokens": gen_max_new_tokens,
                    # "guidance_scale": gen_guidance_scale, # Check if AudioGen supports this
                    "temperature": gen_temperature,
                    "top_k": gen_top_k,
                    "top_p": gen_top_p,
                    "do_sample": True,
                    # Add other specific AudioGen parameters if needed
                }
                # Filter out None values if model.generate doesn't like them
                # generation_args = {k: v for k, v in generation_args.items() if v is not None}

                with self.torch.no_grad():
                    # Output structure might differ from MusicGen
                    # It might directly return waveforms or an object containing them
                    output = self.model.generate(**inputs, **generation_args)
                    # Assuming output is a tensor [batch, channels, samples] or similar
                    # Squeeze to remove batch if batch_size is 1
                    audio_values = output.squeeze().cpu()


                # --- Post-processing and Saving ---
                # Check tensor dimensions and convert to NumPy
                # Assuming output is [channels, samples] after squeeze
                if audio_values.ndim == 2:
                    audio_numpy = audio_values.numpy() # Keep channels if stereo
                elif audio_values.ndim == 1:
                     audio_numpy = audio_values.numpy() # Mono
                else:
                     raise ValueError(f"Unexpected audio tensor shape: {audio_values.shape}")

                try:
                    sampling_rate = self.model.config.sampling_rate
                except AttributeError:
                    sampling_rate = 16000 # Default fallback
                    self.app.warning(f"Could not find sampling_rate in model config, defaulting to {sampling_rate} Hz.")

                # Determine output path and filename (Identical logic)
                output_path = Path(output_dir or self.output_folder)
                output_path.mkdir(parents=True, exist_ok=True)
                if output_file_name:
                    base_filename = Path(output_file_name).stem
                else:
                    import time
                    timestamp = int(time.time())
                    safe_prompt = "".join(c if c.isalnum() else "_" for c in prompt[:30]).rstrip('_')
                    base_filename = f"audiogen_{safe_prompt}_{timestamp}"
                output_filepath = (output_path / f"{base_filename}.wav").resolve()

                # Save as WAV file
                if audio_numpy.dtype != np.float32:
                    audio_numpy = audio_numpy.astype(np.float32)

                # Transpose if shape is (channels, samples) for scipy
                if audio_numpy.ndim == 2 and audio_numpy.shape[0] < audio_numpy.shape[1]:
                    audio_numpy = audio_numpy.T # To (samples, channels)

                self.scipy_wavfile.write(output_filepath, rate=sampling_rate, data=audio_numpy)

                actual_duration_s = audio_numpy.shape[0] / sampling_rate
                self.app.InfoMessage(f"Audio generated ({actual_duration_s:.2f}s) and saved to: {output_filepath}")

                # --- Prepare Result Dictionary ---
                result = {
                    "path": str(output_filepath),
                    "prompt": prompt,
                    "duration_s": round(actual_duration_s, 2),
                    "sampling_rate": sampling_rate,
                    "seed": gen_seed if gen_seed != -1 else "random",
                    # "guidance_scale": gen_guidance_scale, # Include if used
                    "temperature": gen_temperature,
                    "top_k": gen_top_k,
                    "top_p": gen_top_p,
                    "max_new_tokens_requested": gen_max_new_tokens,
                    "format": "wav",
                    "model": self.service_config.model_name,
                    "device": self._device
                }
                return [result]

            except Exception as e:
                self.app.error(f"Error generating audio with AudioGen: {e}")
                import traceback
                self.app.error(traceback.format_exc())
                return []
            finally:
                self.app.HideBlockingMessage()

    @staticmethod
    def get(app: LollmsApplication) -> 'AudioGenTTM':
        return AudioGenTTM