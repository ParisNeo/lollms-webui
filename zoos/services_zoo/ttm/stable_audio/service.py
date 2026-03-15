import importlib
import sys
import subprocess
from pathlib import Path
from typing import List, Dict, Optional
import numpy as np
import io
import time
import requests # For API calls
import json

# --- Dependency Management ---
try:
    import pipmaster as pm
except ImportError:
    # ... (Standard pipmaster error message) ...
    raise ImportError("pipmaster is mandatory for Lollms binding installation.")

# --- Lollms Imports ---
from lollms.app import LollmsApplication
from lollms.config import TypedConfig, BaseConfig, ConfigTemplate
from lollms.ttm import LollmsTTM
from lollms.helpers import ASCIIColors
from lollms.utilities import PackageManager, show_yes_no_dialog, alert_warning

# --- Configuration ---
DEFAULT_CONFIG = {
    "api_key": "YOUR_STABLE_AUDIO_API_KEY_HERE", # Needs user configuration!
    "base_url": "https://api.stability.ai",     # Official Stability API base
    "model_id": "stable-audio-1.0", # Default Stable Audio model
    "duration_s": 20,               # Default duration request
    "seed": -1,                     # -1 for random, or specific seed
    "polling_interval_s": 3,
    "generation_timeout_s": 180,
}

class StableAudioApiTTMConfig(BaseConfig):
    def __init__(self, config: dict = None):
        effective_config = {**DEFAULT_CONFIG, **(config or {})}
        super().__init__(effective_config)

    def validate(self):
        if not self.api_key or self.api_key == "YOUR_STABLE_AUDIO_API_KEY_HERE":
            raise ValueError("Stable Audio API Key is required.")
        if not self.base_url:
            raise ValueError("Stable Audio API Base URL cannot be empty.")
        if self.duration_s <= 0:
             raise ValueError("Duration must be positive.")


# --- Main Binding Class ---
class StableAudioApiTTM(LollmsTTM):
    """
    Lollms binding for the Stability AI Stable Audio API.
    Requires a Stability API key and uses the `requests` library.
    Generates music loops and sound effects.
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
            # Important: Add 'is_secret=True' if Lollms supports masking API keys
            {"name": "api_key", "type": "str", "value": DEFAULT_CONFIG["api_key"], "help": "Your Stability AI API Key (essential)."},
            {"name": "base_url", "type": "str", "value": DEFAULT_CONFIG["base_url"], "help": "The base URL for the Stability AI API."},
            {"name": "model_id", "type": "str", "value": DEFAULT_CONFIG["model_id"], "help": "The Stable Audio model ID to use (e.g., 'stable-audio-1.0')."},
            {"name": "duration_s", "type": "int", "value": DEFAULT_CONFIG["duration_s"], "min": 1, "max": 90, "help": "Desired audio duration in seconds (max varies by model/plan, often ~90s)."},
            {"name": "seed", "type": "int", "value": DEFAULT_CONFIG["seed"], "help": "Seed for reproducibility (-1 for random)."},
            {"name": "polling_interval_s", "type": "int", "value": DEFAULT_CONFIG["polling_interval_s"], "min": 1, "help": "Seconds between status checks (if API uses polling)."},
            {"name": "generation_timeout_s", "type": "int", "value": DEFAULT_CONFIG["generation_timeout_s"], "min": 10, "help": "Maximum seconds to wait for generation."},
        ])
        typed_config = TypedConfig(config_template)

        super().__init__(
            name="stable_audio_api", # Unique name
            app=app,
            service_config=typed_config,
            output_folder=output_folder
        )

        self.requests = None
        self.scipy_wavfile = None
        self.np = None

        # --- Dependency Check and Installation (Identical to Suno API) ---
        if not self.verify(app):
            if show_yes_no_dialog("Confirmation", f"The Stable Audio API binding requires installing dependencies (requests, scipy, numpy). Install now?"):
                self.install(app)
                if not self.verify(app):
                    app.error("Stable Audio API binding dependencies still missing.")
            else:
                app.error("Stable Audio API binding dependencies not installed.")

    def settings_updated(self):
        if not self.service_config.api_key or self.service_config.api_key == "YOUR_STABLE_AUDIO_API_KEY_HERE":
             alert_warning(self.app, "Stable Audio API Key is not configured. Generation will fail.")

    @staticmethod
    def get_dependencies() -> List[str]:
        return ["requests", "scipy", "numpy"]

    @staticmethod
    def verify(app: LollmsApplication) -> bool:
        # ... (Identical verification logic as Suno API) ...
        missing = []
        for package in StableAudioApiTTM.get_dependencies():
            try:
                importlib.import_module(package)
            except ImportError:
                missing.append(package)
        if missing:
            app.warning(f"Stable Audio API binding verification failed. Missing: {', '.join(missing)}")
            return False
        return True


    @staticmethod
    def install(app: LollmsApplication) -> bool:
        # ... (Identical installation logic as Suno API) ...
        app.ShowBlockingMessage("Installing Stable Audio API dependencies (requests, scipy, numpy)...")
        try:
            pm.install_if_missing("requests")
            pm.install_if_missing("scipy")
            pm.install_if_missing("numpy")
            app.InfoMessage("Stable Audio API dependencies installed successfully.")
            PackageManager.rebuild_packages()
            return True
        except Exception as e:
            app.error(f"Failed to install Stable Audio API dependencies: {e}")
            return False
        finally:
            app.HideBlockingMessage()

    def _load_model(self):
        # No model to load, just ensure libraries are imported and API key is present
        if self.requests and self.scipy_wavfile and self.np:
             return True
        try:
            self.requests = importlib.import_module("requests")
            self.scipy_wavfile = importlib.import_module("scipy.io.wavfile")
            self.np = importlib.import_module("numpy")

            if not self.service_config.api_key or self.service_config.api_key == "YOUR_STABLE_AUDIO_API_KEY_HERE":
                self.app.error("Stable Audio API Key is not configured.")
                alert_warning(self.app, "Stable Audio API Key is not configured. Please set it in the binding settings.")
                return False
            return True
        except ImportError as e:
             self.app.error(f"Failed to import required libraries for Stable Audio API: {e}")
             return False
        except Exception as e:
              self.app.error(f"Error during Stable Audio API setup: {e}")
              return False

    def generate(self,
                    prompt: str,
                    negative_prompt: str = "", # Stable Audio API supports negative prompts
                    duration_s: Optional[float] = None,
                    seed: Optional[int] = None,
                    # Standard TTM params (less relevant here)
                    guidance_scale: Optional[float] = None, # N/A
                    temperature: Optional[float] = None,    # N/A
                    top_k: Optional[int] = None,            # N/A
                    top_p: Optional[float] = None,          # N/A
                    max_new_tokens: Optional[int] = None,   # N/A
                    output_dir: Optional[str | Path] = None,
                    output_file_name: Optional[str] = None
                    ) -> List[Dict[str, str]]:

            if not self._load_model():
                self.app.error("Stable Audio API binding not ready.")
                return []

            self.app.ShowBlockingMessage(f"Requesting Stable Audio generation for: '{prompt[:70]}...'")

            try:
                headers = {
                    "Authorization": f"Bearer {self.service_config.api_key}",
                    "Accept": "audio/wav", # Request WAV output directly
                    # Content-Type will be multipart/form-data
                }

                # --- Prepare API Payload (Form Data) ---
                gen_duration = int(duration_s) if duration_s is not None else self.service_config.duration_s
                gen_seed = seed if seed is not None and seed != -1 else None # API might expect null/absent for random

                data = {
                    "prompt": prompt,
                    "duration": str(gen_duration), # API expects string duration
                    "model": self.service_config.model_id
                }
                if negative_prompt:
                    data["negative_prompt"] = negative_prompt
                if gen_seed is not None:
                    data["seed"] = str(gen_seed) # API expects string seed

                # --- Submit Generation Request ---
                # Endpoint for Stable Audio generation (check current Stability API docs)
                submit_url = f"{self.service_config.base_url}/v1alpha/generation/{self.service_config.model_id}/text-to-audio"
                # Alternative endpoint might exist, verify documentation

                self.app.InfoMessage(f"Submitting request to {submit_url}")
                # Stability API uses form-data for this endpoint
                response = self.requests.post(submit_url, headers=headers, data=data, stream=True) # Use stream=True for audio

                # --- Handle Response ---
                if response.status_code == 200:
                    self.app.InfoMessage("Stable Audio generation successful. Receiving audio stream...")
                    audio_bytes = response.content

                    # --- Save Audio ---
                    output_path = Path(output_dir or self.output_folder)
                    output_path.mkdir(parents=True, exist_ok=True)

                    if output_file_name:
                        base_filename = Path(output_file_name).stem
                    else:
                        timestamp = int(time.time())
                        safe_prompt = "".join(c if c.isalnum() else "_" for c in prompt[:30]).rstrip('_')
                        base_filename = f"stableaudio_{safe_prompt}_{timestamp}"

                    output_filepath = (output_path / f"{base_filename}.wav").resolve()

                    # Since we requested audio/wav, we can attempt to parse and save it
                    try:
                        import wave
                        with wave.open(io.BytesIO(audio_bytes), 'rb') as wf:
                             sampling_rate = wf.getframerate()
                             n_frames = wf.getnframes()
                             audio_frames = wf.readframes(n_frames)
                             sample_width = wf.getsampwidth()
                             n_channels = wf.getnchannels()
                             dtype_map = {1: np.int8, 2: np.int16, 4: np.int32}
                             if sample_width not in dtype_map:
                                 raise ValueError(f"Unsupported sample width: {sample_width}")
                             audio_numpy = np.frombuffer(audio_frames, dtype=dtype_map[sample_width])
                             if n_channels > 1:
                                 audio_numpy = audio_numpy.reshape(-1, n_channels)

                        # Normalize and save with scipy
                        max_val = np.iinfo(audio_numpy.dtype).max
                        audio_numpy = audio_numpy.astype(np.float32) / max_val
                        self.scipy_wavfile.write(output_filepath, sampling_rate, audio_numpy)
                        actual_duration_s = n_frames / sampling_rate

                        self.app.InfoMessage(f"Audio saved to: {output_filepath}")

                         # --- Prepare Result Dictionary ---
                        result = {
                            "path": str(output_filepath),
                            "prompt": prompt,
                            "negative_prompt": negative_prompt,
                            "duration_s": round(actual_duration_s, 2),
                            "requested_duration_s": gen_duration,
                            "sampling_rate": sampling_rate,
                            "seed": gen_seed if gen_seed is not None else "random",
                            "format": "wav",
                            "model": self.service_config.model_id,
                            "service": "Stable Audio API"
                        }
                        return [result]

                    except Exception as save_err:
                         self.app.error(f"Failed to parse/save received WAV data: {save_err}")
                         # Fallback: save raw bytes anyway
                         with open(output_filepath, 'wb') as f:
                             f.write(audio_bytes)
                         self.app.warning(f"Saved raw audio bytes to {output_filepath}. File might be valid.")
                         # Return minimal info
                         result = {"path": str(output_filepath), "prompt": prompt, "service": "Stable Audio API", "error": "Failed to parse WAV"}
                         return [result]

                else:
                    # Handle API errors
                    try:
                        error_data = response.json()
                        error_message = error_data.get("message", response.text)
                    except json.JSONDecodeError:
                        error_message = response.text
                    self.app.error(f"Stable Audio API request failed (Status {response.status_code}): {error_message}")
                    return []


            except self.requests.exceptions.RequestException as e:
                self.app.error(f"Stable Audio API request failed: {e}")
                return []
            except Exception as e:
                self.app.error(f"Error generating audio with Stable Audio API: {e}")
                import traceback
                self.app.error(traceback.format_exc())
                return []
            finally:
                self.app.HideBlockingMessage()

    @staticmethod
    def get(app: LollmsApplication) -> 'StableAudioApiTTM':
        return StableAudioApiTTM