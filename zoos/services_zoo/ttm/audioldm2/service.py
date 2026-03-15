import importlib
import sys
import subprocess
from pathlib import Path
from typing import List, Dict, Optional
import numpy as np
import io # Needed for handling audio bytes with scipy

# --- Dependency Management ---
try:
    import pipmaster as pm
except ImportError:
    print("ERROR: pipmaster library not found.")
    print("Please install it using: pip install pipmaster")
    raise ImportError("pipmaster is mandatory for Lollms binding installation.")

# --- Optional PyTorch Pre-install (Keep commented unless specifically needed) ---
# pm.install_if_missing("torch", index_url="https://download.pytorch.org/whl/cu124")
# pm.install_if_missing("torchvision", index_url="https://download.pytorch.org/whl/cu124")
# pm.install_if_missing("torchaudio", index_url="https://download.pytorch.org/whl/cu124")

# --- Lollms Imports ---
from lollms.app import LollmsApplication
from lollms.config import TypedConfig, BaseConfig, ConfigTemplate
from lollms.ttm import LollmsTTM
from lollms.helpers import ASCIIColors
from lollms.utilities import PackageManager, show_yes_no_dialog

# --- Helper Functions (Copied from MusicGen example) ---
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
    "model_name": "cvssp/audioldm2-music", # Or "cvssp/audioldm-m-full" for general audio/sfx
    # ----- Generation parameters -----
    "audio_length_in_s": 10.0, # Duration in seconds (specific to AudioLDM pipeline)
    "num_inference_steps": 200, # Number of diffusion steps
    "guidance_scale": 3.5,      # Controls prompt adherence
    "negative_prompt": "Low quality, average quality, noise, muffled, distorted", # Default negative prompt
    "seed": -1,                 # Random seed. -1 for random.
    # ----- Hardware -----
    "device": "auto", # "auto", "cpu", "cuda", "mps"
    # ----- Installation -----
    "always_update_diffusers": False # Force update diffusers library on init
}

class AudioLdm2TTMConfig(BaseConfig):
    def __init__(self, config: dict = None):
        effective_config = {**DEFAULT_CONFIG, **(config or {})}
        super().__init__(effective_config)

    def validate(self):
        allowed_devices = ["auto", "cpu", "cuda", "mps"]
        if self.device not in allowed_devices:
            raise ValueError(f"Invalid device '{self.device}'. Must be one of: {allowed_devices}")
        if self.audio_length_in_s <= 0:
             raise ValueError("'audio_length_in_s' must be positive.")
        if self.num_inference_steps <= 0:
             raise ValueError("'num_inference_steps' must be positive.")


# --- Main Binding Class ---
class AudioLdm2TTM(LollmsTTM):
    """
    Lollms binding for AudioLDM 2 Text-to-Audio/Music model using Hugging Face diffusers.
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
            {"name": "model_name", "type": "str", "value": DEFAULT_CONFIG["model_name"], "help": "The specific AudioLDM model checkpoint (e.g., 'cvssp/audioldm2-music', 'cvssp/audioldm-m-full')."},
            {"name": "audio_length_in_s", "type": "float", "value": DEFAULT_CONFIG["audio_length_in_s"], "min": 1.0, "help": "Desired duration of the generated audio in seconds."},
            {"name": "num_inference_steps", "type": "int", "value": DEFAULT_CONFIG["num_inference_steps"], "min": 10, "help": "Number of denoising steps. More steps usually mean higher quality but slower generation."},
            {"name": "guidance_scale", "type": "float", "value": DEFAULT_CONFIG["guidance_scale"], "min": 1.0, "help": "Controls how strongly the generation follows the prompt."},
            {"name": "negative_prompt", "type": "str", "value": DEFAULT_CONFIG["negative_prompt"], "help": "Prompt describing things to avoid in the audio."},
            {"name": "seed", "type": "int", "value": DEFAULT_CONFIG["seed"], "help": "Seed for reproducibility (-1 for random)."},
            {"name": "device", "type": "str", "value": DEFAULT_CONFIG["device"], "help": "Device: 'auto', 'cpu', 'cuda', 'mps'. 'auto' tries CUDA/MPS then CPU."},
            {"name": "always_update_diffusers", "type": "bool", "value": DEFAULT_CONFIG["always_update_diffusers"], "help": "Update diffusers library on each load."}
        ])
        typed_config = TypedConfig(config_template)

        super().__init__(
            name="audioldm2", # Unique name
            app=app,
            service_config=typed_config,
            output_folder=output_folder
        )

        self.pipeline = None
        self.torch = None
        self.diffusers = None
        self.scipy_wavfile = None
        self._device = None

        # --- Dependency Check and Installation ---
        if not self.verify(app):
            if show_yes_no_dialog("Confirmation", f"The AudioLDM 2 binding requires installing dependencies (torch, diffusers, transformers, scipy, numpy). Install now?"):
                self.install(app)
                if not self.verify(app):
                    app.error("AudioLDM 2 binding dependencies still missing after installation attempt.")
                    # raise RuntimeError("Failed to install required AudioLDM 2 dependencies.")
            else:
                app.error("AudioLDM 2 binding dependencies not installed.")
                # raise RuntimeError("User declined to install required AudioLDM 2 dependencies.")

        if self.service_config.always_update_diffusers:
            self.app.ShowBlockingMessage("Checking for diffusers library update...")
            try:
                pm.install("diffusers", force_reinstall=True, upgrade=True)
                app.InfoMessage("Diffusers library updated successfully.")
                if "diffusers" in sys.modules:
                    try:
                        importlib.reload(sys.modules["diffusers"])
                        self.diffusers = sys.modules["diffusers"]
                    except Exception as reload_err:
                        app.warning(f"Could not reload diffusers after update: {reload_err}")
            except Exception as e:
                app.error(f"Failed to update diffusers library: {e}")
            finally:
                self.app.HideBlockingMessage()

    def settings_updated(self):
        # If model name or device changes, might need to reload
        self.pipeline = None # Force reload on next generate
        self._device = None

    @staticmethod
    def get_dependencies() -> List[str]:
        # transformers is often a dependency of diffusers pipelines
        return ["torch", "diffusers", "transformers", "scipy", "numpy", "accelerate"] # Added accelerate

    @staticmethod
    def verify(app: LollmsApplication) -> bool:
        missing = []
        for package in AudioLdm2TTM.get_dependencies():
            try:
                importlib.import_module(package)
            except ImportError:
                missing.append(package)
        if missing:
            app.warning(f"AudioLDM 2 binding verification failed. Missing: {', '.join(missing)}")
            return False
        return True

    @staticmethod
    def install(app: LollmsApplication) -> bool:
        app.ShowBlockingMessage("Installing AudioLDM 2 dependencies (torch, diffusers, transformers, scipy, numpy, accelerate)... This might take a while.")
        try:
            pm.install_if_missing("torch")
            pm.install_if_missing("diffusers")
            pm.install_if_missing("transformers")
            pm.install_if_missing("scipy")
            pm.install_if_missing("numpy")
            pm.install_if_missing("accelerate") # Useful for diffusers performance

            app.InfoMessage("AudioLDM 2 dependencies installed successfully.")
            PackageManager.rebuild_packages()
            return True
        except Exception as e:
            app.error(f"Failed to install AudioLDM 2 dependencies: {e}")
            return False
        finally:
            app.HideBlockingMessage()

    def _load_model(self):
        if self.pipeline is not None:
            return True # Already loaded

        self.app.ShowBlockingMessage(f"Loading AudioLDM 2 model: {self.service_config.model_name}...")
        try:
            self.torch = importlib.import_module("torch")
            self.diffusers = importlib.import_module("diffusers")
            self.scipy_wavfile = importlib.import_module("scipy.io.wavfile")

            # Determine device (copied logic)
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

            # Load the pipeline
            # Use torch_dtype=torch.float16 for potential memory savings on GPU
            dtype = self.torch.float16 if self._device in ["cuda", "mps"] else self.torch.float32

            # Determine pipeline class based on model name (heuristic)
            if "audioldm2" in self.service_config.model_name.lower():
                AudioPipeline = self.diffusers.AudioLDM2Pipeline
            else:
                AudioPipeline = self.diffusers.AudioLDMPipeline # Default to original

            self.pipeline = AudioPipeline.from_pretrained(
                self.service_config.model_name,
                torch_dtype=dtype
            ).to(self._device)

            # Optional: Enable memory-efficient attention if accelerate is installed
            try:
                 self.pipeline.enable_attention_slicing()
                 self.app.InfoMessage("Enabled attention slicing for potential memory savings.")
            except Exception:
                 self.app.warning("Could not enable attention slicing (perhaps accelerate is missing or incompatible).")


            self.app.InfoMessage(f"AudioLDM 2 model '{self.service_config.model_name}' loaded successfully onto {self._device}.")
            return True

        except Exception as e:
            self.app.error(f"Failed to load AudioLDM 2 model '{self.service_config.model_name}': {e}")
            import traceback
            self.app.error(traceback.format_exc())
            self.pipeline = None
            self._device = None
            return False
        finally:
             self.app.HideBlockingMessage()


    def generate(self,
                    prompt: str,
                    negative_prompt: Optional[str] = None, # Allow overriding default negative prompt
                    duration_s: Optional[float] = None,
                    seed: Optional[int] = None,
                    guidance_scale: Optional[float] = None,
                    num_inference_steps: Optional[int] = None,
                    # Removed TTM params not directly used by AudioLDM pipeline:
                    # temperature, top_k, top_p, max_new_tokens
                    output_dir: Optional[str | Path] = None,
                    output_file_name: Optional[str] = None
                    ) -> List[Dict[str, str]]:
            if not self._load_model():
                self.app.error("AudioLDM 2 model not loaded. Cannot generate audio.")
                return []

            self.app.ShowBlockingMessage(f"Generating audio for prompt: '{prompt[:70]}...'")

            try:
                # --- Parameter Preparation ---
                gen_seed = seed if seed is not None else self.service_config.seed
                gen_guidance_scale = guidance_scale if guidance_scale is not None else self.service_config.guidance_scale
                gen_duration_s = duration_s if duration_s is not None else self.service_config.audio_length_in_s
                gen_num_inference_steps = num_inference_steps if num_inference_steps is not None else self.service_config.num_inference_steps
                gen_negative_prompt = negative_prompt if negative_prompt is not None else self.service_config.negative_prompt


                # --- Seed Handling ---
                generator = None
                if gen_seed is not None and gen_seed != -1:
                    generator = self.torch.Generator(device=self._device).manual_seed(gen_seed)
                    self.app.info(f"Using seed: {gen_seed}")
                else:
                    self.app.info("Using random seed.")

                # --- Generation Call (using pipeline) ---
                # Note: AudioLDM pipelines expect audio_length_in_s, not max_tokens
                # Use torch.inference_mode() for potentially better performance than torch.no_grad()
                with self.torch.inference_mode():
                    audio_output = self.pipeline(
                        prompt=prompt,
                        negative_prompt=gen_negative_prompt,
                        audio_length_in_s=gen_duration_s,
                        num_inference_steps=gen_num_inference_steps,
                        guidance_scale=gen_guidance_scale,
                        generator=generator # Pass the generator object here
                    )
                    # Diffusers pipelines usually return an object with an 'audio' attribute
                    # This is typically a list of NumPy arrays or a single NumPy array
                    # Shape is often (num_channels, num_samples) or (batch_size, num_channels, num_samples)
                    # We expect a single output here.
                    audio_data = audio_output.audios[0] # Get the first audio output

                # --- Post-processing and Saving ---
                # Audio data from diffusers is usually already a NumPy array.
                # It might be float32, check range (often -1 to 1).
                # Scipy expects (num_samples,) or (num_samples, num_channels).
                # Diffusers output is often (num_channels, num_samples), so transpose if needed.
                if audio_data.ndim == 2 and audio_data.shape[0] < audio_data.shape[1]: # Likely (channels, samples)
                    audio_numpy = audio_data.T # Transpose to (samples, channels)
                else:
                    audio_numpy = audio_data # Assume it's already (samples,) or (samples, channels)

                # Ensure float32 for saving, normalize if needed (optional)
                if audio_numpy.dtype != np.float32:
                    audio_numpy = audio_numpy.astype(np.float32)
                # max_abs_val = np.max(np.abs(audio_numpy))
                # if max_abs_val > 1.0:
                #     audio_numpy /= max_abs_val

                # Get sampling rate from the pipeline's scheduler/config
                try:
                    # Accessing sampling rate varies slightly between pipelines
                    if hasattr(self.pipeline, 'scheduler') and hasattr(self.pipeline.scheduler, 'config'):
                         sampling_rate = self.pipeline.scheduler.config.sampling_rate
                    elif hasattr(self.pipeline, 'config') and 'sampling_rate' in self.pipeline.config:
                         sampling_rate = self.pipeline.config['sampling_rate']
                    else: # Fallback
                        sampling_rate = 16000 # Common default for AudioLDM
                        self.app.warning(f"Could not reliably determine sampling rate, defaulting to {sampling_rate} Hz.")
                except Exception:
                    sampling_rate = 16000 # Fallback
                    self.app.warning(f"Error getting sampling rate, defaulting to {sampling_rate} Hz.")


                # Determine output path and filename
                output_path = Path(output_dir or self.output_folder)
                output_path.mkdir(parents=True, exist_ok=True)
                if output_file_name:
                    base_filename = Path(output_file_name).stem
                else:
                    import time
                    timestamp = int(time.time())
                    safe_prompt = "".join(c if c.isalnum() else "_" for c in prompt[:30]).rstrip('_')
                    base_filename = f"audioldm2_{safe_prompt}_{timestamp}"
                output_filepath = (output_path / f"{base_filename}.wav").resolve()

                # Save as WAV file using scipy
                self.scipy_wavfile.write(output_filepath, rate=sampling_rate, data=audio_numpy)

                actual_duration_s = audio_numpy.shape[0] / sampling_rate
                self.app.InfoMessage(f"Audio generated ({actual_duration_s:.2f}s) and saved to: {output_filepath}")

                # --- Prepare Result Dictionary ---
                result = {
                    "path": str(output_filepath),
                    "prompt": prompt,
                    "negative_prompt": gen_negative_prompt,
                    "duration_s": round(actual_duration_s, 2),
                    "requested_duration_s": gen_duration_s,
                    "sampling_rate": sampling_rate,
                    "seed": gen_seed if gen_seed != -1 else "random",
                    "guidance_scale": gen_guidance_scale,
                    "num_inference_steps": gen_num_inference_steps,
                    "format": "wav",
                    "model": self.service_config.model_name,
                    "device": self._device
                }
                return [result]

            except Exception as e:
                self.app.error(f"Error generating audio with AudioLDM 2: {e}")
                import traceback
                self.app.error(traceback.format_exc())
                return []
            finally:
                self.app.HideBlockingMessage()

    @staticmethod
    def get(app: LollmsApplication) -> 'AudioLdm2TTM':
        return AudioLdm2TTM