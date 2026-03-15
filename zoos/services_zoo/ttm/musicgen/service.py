import importlib
import sys
import subprocess
from pathlib import Path
from typing import List, Dict, Optional
import numpy as np # Needed for audio data manipulation

# --- Dependency Management ---

# Attempt to import pipmaster. If it fails, provide instructions and raise error.
try:
    import pipmaster as pm
except ImportError:
    print("ERROR: pipmaster library not found.")
    print("Please install it using: pip install pipmaster")
    print("Lollms requires pipmaster to automatically install binding dependencies.")
    # Raise an exception to halt execution if pipmaster is critical at this point
    raise ImportError("pipmaster is mandatory for Lollms binding installation.")

# --- Optional: Pre-install specific PyTorch versions if needed ---
# Note: This forces a specific CUDA version (12.4). Consider if this is universally desired
# or if letting pip/pipmaster resolve the best version automatically is better.
# If automatic resolution is preferred, remove these lines and rely on the install() method.
# pm.install_if_missing("torch", index_url="https://download.pytorch.org/whl/cu124")
# pm.install_if_missing("torchvision", index_url="https://download.pytorch.org/whl/cu124")
# pm.install_if_missing("torchaudio", index_url="https://download.pytorch.org/whl/cu124")

# --- Lollms Imports ---
from lollms.app import LollmsApplication
from lollms.config import TypedConfig, BaseConfig, ConfigTemplate
from lollms.ttm import LollmsTTM # Base class for Text-To-Music
from lollms.helpers import ASCIIColors
from lollms.utilities import PackageManager, show_yes_no_dialog

# --- Helper Functions ---
def check_torch_cuda():
    """Checks if PyTorch and CUDA are available."""
    try:
        import torch
        return torch.cuda.is_available()
    except Exception as e:
        # print(f"Debug: Error checking torch CUDA: {e}") # Optional debug print
        return False

def check_torch_mps():
    """Checks if PyTorch and MPS (Apple Silicon) are available."""
    try:
        import torch
        # Check for MPS availability based on PyTorch version
        if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
             # Potentially add a check for torch version >= 1.12 or similar if needed
            return True
        else:
            return False
    except Exception as e:
        # print(f"Debug: Error checking torch MPS: {e}") # Optional debug print
        return False


# --- Configuration ---
# Default configuration values
DEFAULT_CONFIG = {
    # ----- Model selection -----
    "model_name": "facebook/musicgen-small", # Or "facebook/musicgen-medium", "facebook/musicgen-large"
    # ----- Generation parameters -----
    "max_new_tokens": 256, # Corresponds roughly to duration. ~50 tokens/sec.
    "guidance_scale": 3.0, # Higher values follow prompt more closely.
    "temperature": 1.0, # Controls randomness. Higher values = more random.
    "top_k": 250, # Limits sampling to the top K tokens. 0 disables.
    "top_p": 0.0, # Nucleus sampling. 0 disables.
    "seed": -1, # Random seed. -1 for random.
    # ----- Hardware -----
    "device": "auto", # "auto", "cpu", "cuda", "mps"
    # ----- Installation -----
    "always_update_transformers": False # Force update transformers library on init
}

# Configuration class inheriting from BaseConfig
class MusicGenTTMConfig(BaseConfig):
    def __init__(self, config: dict = None):
        # Use provided config or fall back to defaults
        effective_config = {**DEFAULT_CONFIG, **(config or {})}
        super().__init__(effective_config)

    # Example validation (optional)
    def validate(self):
        allowed_devices = ["auto", "cpu", "cuda", "mps"]
        if self.device not in allowed_devices:
            raise ValueError(f"Invalid device '{self.device}'. Must be one of: {allowed_devices}")
        if self.max_new_tokens <= 0:
             raise ValueError("'max_new_tokens' must be positive.")


# --- Main Binding Class ---
class MusicGenTTM(LollmsTTM):
    """
    Lollms binding for Facebook's MusicGen Text-to-Music model using Hugging Face transformers.
    """
    def __init__(
        self,
        app: LollmsApplication,
        config: Optional[dict] = None, # Allow passing config dict directly
        service_config: Optional[TypedConfig] = None, # Accept TypedConfig
        output_folder: Optional[str | Path] = None,
        **kwargs # Accept extra arguments from Lollms generic service loading
    ):
        """
        Initializes the MusicGenTTM binding.

        Args:
            app (LollmsApplication): The Lollms application instance.
            config (dict, optional): Configuration dictionary. Defaults to None.
            service_config (TypedConfig, optional): TypedConfig object. Overrides `config`.
            output_folder (str | Path, optional): Folder for saving generated audio.
        """
        # --- Configuration Setup ---
        config_template = ConfigTemplate([
            # ----- Model selection -----
            {"name": "model_name", "type": "str", "value": DEFAULT_CONFIG["model_name"], "help": "The specific MusicGen model checkpoint (e.g., 'facebook/musicgen-small', 'medium', 'large'). Larger models need more VRAM/RAM."},
            # ----- Generation parameters -----
            {"name": "max_new_tokens", "type": "int", "value": DEFAULT_CONFIG["max_new_tokens"], "min": 10, "help": "Max tokens influence duration (~50 tokens ≈ 1 second)."},
            {"name": "guidance_scale", "type": "float", "value": DEFAULT_CONFIG["guidance_scale"], "min": 1.0, "help": "Controls prompt adherence vs. creativity."},
            {"name": "temperature", "type": "float", "value": DEFAULT_CONFIG["temperature"], "min": 0.01, "max": 2.0, "help": "Controls randomness (higher = more random)."},
            {"name": "top_k", "type": "int", "value": DEFAULT_CONFIG["top_k"], "min": 0, "help": "Restricts sampling to top K tokens (0 disables)."},
            {"name": "top_p", "type": "float", "value": DEFAULT_CONFIG["top_p"], "min": 0.0, "max": 1.0, "help": "Nucleus sampling threshold (0 disables)."},
            {"name": "seed", "type": "int", "value": DEFAULT_CONFIG["seed"], "help": "Seed for reproducibility (-1 for random)."},
            # ----- Hardware -----
            {"name": "device", "type": "str", "value": DEFAULT_CONFIG["device"], "help": "Device: 'auto', 'cpu', 'cuda', 'mps'. 'auto' tries CUDA/MPS then CPU."},
            # ----- Installation -----
            {"name": "always_update_transformers", "type": "bool", "value": DEFAULT_CONFIG["always_update_transformers"], "help": "Update transformers library on each load."}
        ])
        typed_config = TypedConfig(config_template)

        # Initialize the base LollmsTTM class
        super().__init__(
            name="musicgen", # Unique name for this service
            app=app,
            service_config=typed_config,
            output_folder=output_folder
        )

        # --- Initialize State ---
        self.model = None
        self.processor = None
        self.torch = None
        self.transformers = None
        self.scipy_wavfile = None
        self._device = None # Internal storage for the determined device

        # --- Dependency Check and Installation ---
        if not self.verify(app):
             # Use PackageManager for installation prompts
            if show_yes_no_dialog("Confirmation", f"The MusicGen binding requires installing dependencies (torch, transformers, scipy). Install now?"):
                self.install(app)
                 # Re-verify after installation attempt
                if not self.verify(app):
                    app.error("MusicGen binding dependencies still missing after installation attempt. The binding may not function correctly.")
                    # Consider raising an exception if strict dependency enforcement is needed
                    # raise RuntimeError("Failed to install required MusicGen dependencies.")
            else:
                app.error("MusicGen binding dependencies not installed. The binding may not function correctly.")
                # Optionally raise error here too
                # raise RuntimeError("User declined to install required MusicGen dependencies.")

        # Optionally force update transformers if configured
        if self.service_config.always_update_transformers:
            self.app.ShowBlockingMessage("Checking for transformers library update...")
            try:
                pm.install("transformers", force_reinstall=True, upgrade=True) # Use pipmaster to force update
                app.InfoMessage("Transformers library updated successfully.")
                 # Reload the module if it was already imported
                if "transformers" in sys.modules:
                    try:
                        importlib.reload(sys.modules["transformers"])
                        self.transformers = sys.modules["transformers"] # Update reference
                    except Exception as reload_err:
                        app.warning(f"Could not reload transformers after update: {reload_err}")
            except Exception as e:
                app.error(f"Failed to update transformers library: {e}")
            finally:
                self.app.HideBlockingMessage()

    def settings_updated(self):
        pass
    
    @staticmethod
    def get_dependencies() -> List[str]:
        """Returns a list of required Python packages."""
        # Include accelerate if you plan to use it or recommend it
        return ["torch", "transformers", "scipy", "numpy"] # Added numpy

    @staticmethod
    def verify(app: LollmsApplication) -> bool:
        """Verifies if the necessary libraries are installed."""
        missing = []
        for package in MusicGenTTM.get_dependencies():
            try:
                importlib.import_module(package)
            except ImportError:
                missing.append(package)

        if missing:
            app.warning(f"MusicGen binding verification failed. Missing packages: {', '.join(missing)}")
            return False
        else:
            # Optional: More specific check, e.g., for torch version or CUDA
            # if not check_torch_cuda() and not check_torch_mps():
            #     app.InfoMessage("PyTorch found, but CUDA or MPS acceleration is not available. MusicGen will run on CPU.")
            # elif check_torch_cuda():
            #     app.InfoMessage("PyTorch with CUDA support found.")
            # elif check_torch_mps():
            #     app.InfoMessage("PyTorch with MPS support found.")
            return True

    @staticmethod
    def install(app: LollmsApplication) -> bool:
        """Installs the necessary libraries using pipmaster."""
        app.ShowBlockingMessage("Installing MusicGen dependencies (torch, transformers, scipy, numpy)... This might take a while.")

        try:
            # Let pipmaster handle torch installation (it should find appropriate versions)
            # If specific CUDA versions are needed, you might add index_url here, but
            # it's often better to let the user manage their PyTorch installation
            # or let pip find a compatible version.
            pm.install_if_missing("torch")
            pm.install_if_missing("transformers")
            pm.install_if_missing("scipy")
            pm.install_if_missing("numpy") # Ensure numpy is installed

            # Optional: Install accelerate for potential performance gains
            # pm.install_if_missing("accelerate")

            app.InfoMessage("MusicGen dependencies installed successfully.")
            # Rebuild packages list after installation
            PackageManager.rebuild_packages()
            return True

        except Exception as e:
            app.error(f"Failed to install MusicGen dependencies: {e}")
            return False
        finally:
            app.HideBlockingMessage()

    def _load_model(self):
        """Loads the MusicGen model and processor using transformers."""
        if self.model is not None and self.processor is not None:
            self.app.InfoMessage("MusicGen model and processor already loaded.")
            return True # Already loaded

        self.app.ShowBlockingMessage(f"Loading MusicGen model: {self.service_config.model_name}...")
        try:
            # Import necessary libraries only when needed (lazy loading)
            self.torch = importlib.import_module("torch")
            self.transformers = importlib.import_module("transformers")
            self.scipy_wavfile = importlib.import_module("scipy.io.wavfile") # Specific import

            # Determine device
            requested_device = self.service_config.device.lower()
            if requested_device == "auto":
                if check_torch_cuda():
                    self._device = "cuda"
                elif check_torch_mps():
                     self._device = "mps"
                else:
                    self._device = "cpu"
            elif requested_device == "cuda":
                if check_torch_cuda():
                    self._device = "cuda"
                else:
                    self.app.warning("CUDA requested but not available. Falling back to CPU.")
                    self._device = "cpu"
            elif requested_device == "mps":
                if check_torch_mps():
                     self._device = "mps"
                else:
                    self.app.warning("MPS requested but not available. Falling back to CPU.")
                    self._device = "cpu"
            else: # Assume CPU
                self._device = "cpu"

            self.app.InfoMessage(f"Using device: {self._device}")

            # Load processor and model from Hugging Face Hub
            AutoProcessor = self.transformers.AutoProcessor
            MusicgenForConditionalGeneration = self.transformers.MusicgenForConditionalGeneration

            self.processor = AutoProcessor.from_pretrained(self.service_config.model_name)
            self.model = MusicgenForConditionalGeneration.from_pretrained(self.service_config.model_name)

            # Move model to the selected device
            self.model.to(self._device)
            self.model.eval() # Set model to evaluation mode

            self.app.InfoMessage(f"MusicGen model '{self.service_config.model_name}' loaded successfully onto {self._device}.")
            return True

        except Exception as e:
            self.app.error(f"Failed to load MusicGen model '{self.service_config.model_name}': {e}")
            import traceback
            self.app.error(traceback.format_exc()) # Log full traceback
            self.model = None
            self.processor = None
            self._device = None
            return False
        finally:
             self.app.HideBlockingMessage()


    def generate(self,
                    prompt: str,
                    negative_prompt: str = "", # Keep for interface consistency, though not directly used by MusicGen's generate args
                    duration_s: Optional[float] = None,
                    seed: Optional[int] = None,
                    guidance_scale: Optional[float] = None,
                    temperature: Optional[float] = None,
                    top_k: Optional[int] = None,
                    top_p: Optional[float] = None,
                    max_new_tokens: Optional[int] = None,
                    output_dir: Optional[str | Path] = None,
                    output_file_name: Optional[str] = None
                    ) -> List[Dict[str, str]]:
            """
            Generates audio based on the text prompt using the loaded MusicGen model.

            Args: (Refer to previous docstring, largely the same)

            Returns:
                List[Dict[str, str]]: List containing metadata of the generated audio file(s). Empty list on failure.
            """
            if not self._load_model(): # Ensure model is loaded
                self.app.error("MusicGen model not loaded. Cannot generate audio.")
                return []

            self.app.ShowBlockingMessage(f"Generating music for prompt: '{prompt[:70]}...'")

            try:
                # --- Parameter Preparation ---
                # Use call-specific args > config args > defaults (already handled by self.service_config)
                gen_seed = seed if seed is not None else self.service_config.seed
                gen_guidance_scale = guidance_scale if guidance_scale is not None else self.service_config.guidance_scale
                gen_temperature = temperature if temperature is not None else self.service_config.temperature
                gen_top_k = top_k if top_k is not None else self.service_config.top_k
                gen_top_p = top_p if top_p is not None else self.service_config.top_p

                # Determine max_new_tokens based on duration or explicit arg
                if duration_s is not None and duration_s > 0:
                    # Estimate tokens (approximate, ~50 tokens/sec is common)
                    try:
                        # Attempt to get model's sampling rate if possible, otherwise use default
                        sampling_rate = self.model.config.audio_encoder.sampling_rate
                    except AttributeError:
                        sampling_rate = 32000 # Default for many MusicGen models
                        self.app.warning(f"Could not determine model sampling rate, assuming {sampling_rate} Hz for token calculation.")

                    # Rough estimate - adjust if needed based on model specifics
                    tokens_per_second = 50 # Adjust this value based on empirical results if needed
                    gen_max_new_tokens = int(duration_s * tokens_per_second)
                    self.app.InfoMessage(f"Duration {duration_s}s requested, estimated max_new_tokens: {gen_max_new_tokens}")
                else:
                    # Use explicit max_new_tokens arg or fallback to config
                    gen_max_new_tokens = max_new_tokens if max_new_tokens is not None else self.service_config.max_new_tokens

                # Ensure max_new_tokens is valid
                if gen_max_new_tokens <= 0:
                    self.app.warning(f"max_new_tokens was <= 0 ({gen_max_new_tokens}), setting to default 256.")
                    gen_max_new_tokens = 256 # Fallback to a reasonable default


                # --- Input Processing (using self.processor) ---
                inputs = self.processor(
                    text=[prompt], # Process prompt as a list
                    padding=True, # Pad to handle variable lengths if batching > 1
                    return_tensors="pt", # Return PyTorch tensors
                ).to(self._device) # Move input tensors to the same device as the model


                # --- Seed Handling ---
                # Set the seed using torch.Generator for the specific device before calling generate.
                # Note: We do NOT pass the generator object to model.generate() itself.
                if gen_seed is not None and gen_seed != -1:
                    generator = self.torch.Generator(device=self._device).manual_seed(gen_seed)
                    self.app.info(f"Using seed: {gen_seed}")
                    # The generate function below will implicitly use this seeded generator state
                    # for the specified device.
                else:
                    self.app.info("Using random seed.")
                    # If no seed is set, PyTorch uses its default random state.
                    generator = None # Explicitly set to None for clarity, though not used below

                # --- Generation Call (using self.model.generate) ---
                # **FIX:** Removed the 'generator' key from this dictionary.
                generation_args = {
                    "max_new_tokens": gen_max_new_tokens,
                    "guidance_scale": gen_guidance_scale,
                    "temperature": gen_temperature,
                    "top_k": gen_top_k,
                    "top_p": gen_top_p,
                    "do_sample": True, # Crucial for music generation
                    # Removed -> "generator": generator
                }

                with self.torch.no_grad(): # Disable gradient calculation for inference
                    audio_values = self.model.generate(**inputs, **generation_args)[0] # Get the first (and only) waveform


                # --- Post-processing and Saving ---
                # Move audio tensor to CPU and convert to NumPy array
                audio_numpy = audio_values.cpu().numpy().squeeze() # Remove batch dim if present

                # Get sampling rate from the model's config
                try:
                    sampling_rate = self.model.config.audio_encoder.sampling_rate
                except AttributeError:
                    sampling_rate = 32000 # Fallback if config structure changes
                    self.app.warning(f"Could not find sampling_rate in model config, defaulting to {sampling_rate} Hz.")

                # Determine output path and filename
                output_path = Path(output_dir or self.output_folder)
                output_path.mkdir(parents=True, exist_ok=True)

                if output_file_name:
                    base_filename = Path(output_file_name).stem # Remove extension if present
                else:
                    # Generate a unique filename
                    import time
                    timestamp = int(time.time())
                    safe_prompt = "".join(c if c.isalnum() else "_" for c in prompt[:30]).rstrip('_')
                    base_filename = f"musicgen_{safe_prompt}_{timestamp}"

                output_filepath = (output_path / f"{base_filename}.wav").resolve()

                # Save as WAV file using scipy
                # Ensure data is float32, as expected by some WAV writers after normalization
                if audio_numpy.dtype != np.float32:
                    audio_numpy = audio_numpy.astype(np.float32)

                # Optional: Normalize audio to prevent clipping if values exceed [-1, 1]
                # max_abs_val = np.max(np.abs(audio_numpy))
                # if max_abs_val > 1.0:
                #     self.app.warning(f"Audio signal amplitude exceeded 1.0 (max: {max_abs_val:.2f}). Normalizing.")
                #     audio_numpy = audio_numpy / max_abs_val

                self.scipy_wavfile.write(output_filepath, rate=sampling_rate, data=audio_numpy)

                actual_duration_s = len(audio_numpy) / sampling_rate
                self.app.InfoMessage(f"Music generated ({actual_duration_s:.2f}s) and saved to: {output_filepath}")

                # --- Prepare Result Dictionary ---
                result = {
                    "path": str(output_filepath),
                    "prompt": prompt,
                    "duration_s": round(actual_duration_s, 2),
                    "sampling_rate": sampling_rate,
                    "seed": gen_seed if gen_seed != -1 else "random", # Report used seed
                    "guidance_scale": gen_guidance_scale,
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
                self.app.error(f"Error generating music with MusicGen: {e}")
                import traceback
                self.app.error(traceback.format_exc()) # Log full traceback for debugging
                return []
            finally:
                self.app.HideBlockingMessage()

    @staticmethod
    def get(app: LollmsApplication) -> 'MusicGenTTM':
        """ Static method to return the class type. """
        return MusicGenTTM