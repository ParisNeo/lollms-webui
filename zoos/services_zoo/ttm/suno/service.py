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
    print("ERROR: pipmaster library not found.")
    print("Please install it using: pip install pipmaster")
    raise ImportError("pipmaster is mandatory for Lollms binding installation.")

# --- Lollms Imports ---
from lollms.app import LollmsApplication
from lollms.config import TypedConfig, BaseConfig, ConfigTemplate
from lollms.ttm import LollmsTTM
from lollms.helpers import ASCIIColors
from lollms.utilities import PackageManager, show_yes_no_dialog, alert_warning # Import alert_warning

# --- Helper Function (Placeholder - No local torch needed) ---
# N/A for API

# --- Configuration ---
DEFAULT_CONFIG = {
    "api_key": "YOUR_SUNO_API_KEY_HERE", # Needs user configuration!
    "base_url": "https://studio-api.suno.ai", # Hypothetical or actual base URL
    "model_version": "chirp-v3-0", # Example model identifier used by Suno
    "make_instrumental": False,
    "wait_audio": True, # Whether to wait for generation or just submit
    "polling_interval_s": 5, # How often to check status if wait_audio is True
    "generation_timeout_s": 300, # Max time to wait for generation
    # --- No Hardware config needed for API ---
}

class SunoApiTTMConfig(BaseConfig):
    def __init__(self, config: dict = None):
        effective_config = {**DEFAULT_CONFIG, **(config or {})}
        super().__init__(effective_config)

    def validate(self):
        if not self.api_key or self.api_key == "YOUR_SUNO_API_KEY_HERE":
            raise ValueError("Suno API Key is required. Please configure it.")
        if not self.base_url:
            raise ValueError("Suno API Base URL cannot be empty.")


# --- Main Binding Class ---
class SunoApiTTM(LollmsTTM):
    """
    Lollms binding for the Suno Text-to-Music API.
    Requires a Suno API key and uses the `requests` library.
    Note: API details are based on common patterns and may need adjustment.
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
            # Important: Add 'is_secret=True' if Lollms supports masking API keys in UI
            {"name": "api_key", "type": "str", "value": DEFAULT_CONFIG["api_key"], "help": "Your Suno API Key (essential). Obtain from your Suno account."},
            {"name": "base_url", "type": "str", "value": DEFAULT_CONFIG["base_url"], "help": "The base URL for the Suno API."},
            {"name": "model_version", "type": "str", "value": DEFAULT_CONFIG["model_version"], "help": "Specific Suno model version to use (if applicable)."},
            {"name": "make_instrumental", "type": "bool", "value": DEFAULT_CONFIG["make_instrumental"], "help": "Generate instrumental music only (no vocals)."},
            {"name": "wait_audio", "type": "bool", "value": DEFAULT_CONFIG["wait_audio"], "help": "Wait for audio generation to complete before returning."},
            {"name": "polling_interval_s", "type": "int", "value": DEFAULT_CONFIG["polling_interval_s"], "min": 1, "help": "Seconds between status checks if waiting."},
            {"name": "generation_timeout_s", "type": "int", "value": DEFAULT_CONFIG["generation_timeout_s"], "min": 30, "help": "Maximum seconds to wait for generation."},
        ])
        typed_config = TypedConfig(config_template)

        super().__init__(
            name="suno_api", # Unique name
            app=app,
            service_config=typed_config,
            output_folder=output_folder
        )

        # No local model state
        self.requests = None
        self.scipy_wavfile = None
        self.np = None

        # --- Dependency Check and Installation ---
        if not self.verify(app):
            if show_yes_no_dialog("Confirmation", f"The Suno API binding requires installing dependencies (requests, scipy, numpy). Install now?"):
                self.install(app)
                if not self.verify(app):
                    app.error("Suno API binding dependencies still missing after installation attempt.")
                    # raise RuntimeError(...)
            else:
                app.error("Suno API binding dependencies not installed.")
                # raise RuntimeError(...)

    def settings_updated(self):
        # No model reload needed, but might re-check API key validity if desired
        if not self.service_config.api_key or self.service_config.api_key == "YOUR_SUNO_API_KEY_HERE":
             alert_warning(self.app, "Suno API Key is not configured. Generation will fail.")

    @staticmethod
    def get_dependencies() -> List[str]:
        # Only need requests for API calls and scipy/numpy for saving
        return ["requests", "scipy", "numpy"]

    @staticmethod
    def verify(app: LollmsApplication) -> bool:
        missing = []
        for package in SunoApiTTM.get_dependencies():
            try:
                importlib.import_module(package)
            except ImportError:
                missing.append(package)
        if missing:
            app.warning(f"Suno API binding verification failed. Missing: {', '.join(missing)}")
            return False
        return True

    @staticmethod
    def install(app: LollmsApplication) -> bool:
        app.ShowBlockingMessage("Installing Suno API dependencies (requests, scipy, numpy)...")
        try:
            pm.install_if_missing("requests")
            pm.install_if_missing("scipy")
            pm.install_if_missing("numpy")
            app.InfoMessage("Suno API dependencies installed successfully.")
            PackageManager.rebuild_packages()
            return True
        except Exception as e:
            app.error(f"Failed to install Suno API dependencies: {e}")
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

            if not self.service_config.api_key or self.service_config.api_key == "YOUR_SUNO_API_KEY_HERE":
                self.app.error("Suno API Key is not configured in the binding settings.")
                # Use alert_warning for a non-blocking popup
                alert_warning(self.app, "Suno API Key is not configured. Please set it in the binding settings.")
                return False
            return True
        except ImportError as e:
            self.app.error(f"Failed to import required libraries for Suno API: {e}")
            return False
        except Exception as e:
             self.app.error(f"Error during Suno API setup: {e}")
             return False


    def _get_bearer_token(self):
        # Placeholder: Suno's auth might involve getting a session token first
        # This function would handle that logic. For now, assume API key is Bearer token.
        # Example if you needed to exchange a key for a token:
        # try:
        #    auth_url = f"{self.service_config.base_url}/api/auth/session"
        #    response = self.requests.post(auth_url, headers={'Authorization': f'Bearer {self.service_config.api_key}'})
        #    response.raise_for_status()
        #    return response.json().get('token')
        # except Exception as e:
        #    self.app.error(f"Failed to get Suno bearer token: {e}")
        #    return None
        # For simplicity, assuming the api_key IS the bearer token
        return self.service_config.api_key


    def generate(self,
                    prompt: str, # Often includes lyrics and style description for Suno
                    # Suno specific parameters (optional overrides)
                    make_instrumental: Optional[bool] = None,
                    model_version: Optional[str] = None,
                    # Standard TTM params (less relevant here, duration controlled by Suno)
                    negative_prompt: str = "",
                    duration_s: Optional[float] = None, # May not be directly controllable
                    seed: Optional[int] = None,         # May not be controllable
                    guidance_scale: Optional[float] = None, # N/A
                    temperature: Optional[float] = None,    # N/A
                    top_k: Optional[int] = None,            # N/A
                    top_p: Optional[float] = None,          # N/A
                    max_new_tokens: Optional[int] = None,   # N/A
                    output_dir: Optional[str | Path] = None,
                    output_file_name: Optional[str] = None
                    ) -> List[Dict[str, str]]:

            if not self._load_model():
                self.app.error("Suno API binding not ready (libs missing or API key not set).")
                return []

            self.app.ShowBlockingMessage(f"Requesting Suno generation for: '{prompt[:70]}...'")

            try:
                bearer_token = self._get_bearer_token()
                if not bearer_token:
                     self.app.error("Could not obtain Suno authentication token/key.")
                     return []

                headers = {
                    'Authorization': f'Bearer {bearer_token}',
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                }

                # --- Prepare API Payload ---
                # This needs to match the specific Suno API endpoint requirements
                # It often involves separate fields for lyrics, style, title etc.
                # We'll use the single 'prompt' for simplicity here, assuming it contains all info.
                gen_make_instrumental = make_instrumental if make_instrumental is not None else self.service_config.make_instrumental
                gen_model_version = model_version if model_version is not None else self.service_config.model_version

                # Example payload structure (ADAPT BASED ON ACTUAL API DOCS)
                payload = {
                    "prompt": prompt, # Or structure like {"lyrics": "...", "style_of_music": "...", "title": "..."}
                    "make_instrumental": gen_make_instrumental,
                    "model": gen_model_version,
                    "wait_audio": self.service_config.wait_audio # Tell API if we want to poll or get URLs immediately
                }

                # --- Submit Generation Request ---
                submit_url = f"{self.service_config.base_url}/api/generate" # Hypothetical endpoint
                self.app.InfoMessage(f"Submitting request to {submit_url}")
                response = self.requests.post(submit_url, headers=headers, json=payload)
                response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
                submit_data = response.json()
                self.app.InfoMessage(f"Suno submission response: {submit_data}")

                # --- Handle Response (Polling if wait_audio is True) ---
                clip_ids = []
                if isinstance(submit_data, list): # Assuming response is a list of submitted jobs/clips
                    clip_ids = [item.get('id') for item in submit_data if item.get('id')]
                elif isinstance(submit_data, dict) and 'id' in submit_data: # Single job submission
                    clip_ids = [submit_data.get('id')]
                # Add more robust parsing based on actual API response

                if not clip_ids:
                    self.app.error("Did not receive valid clip IDs from Suno API.")
                    return []

                self.app.InfoMessage(f"Received clip IDs: {clip_ids}")

                generated_files = []
                start_time = time.time()

                while clip_ids and (time.time() - start_time) < self.service_config.generation_timeout_s:
                    self.app.ShowBlockingMessage(f"Polling Suno status for clips: {', '.join(clip_ids)}...")
                    time.sleep(self.service_config.polling_interval_s)

                    # --- Check Status (Hypothetical Endpoint) ---
                    status_url = f"{self.service_config.base_url}/api/feed/" # Needs IDs appended usually
                    # Example: GET /api/feed/?ids=clip_id1,clip_id2
                    ids_param = ",".join(clip_ids)
                    try:
                        status_response = self.requests.get(f"{status_url}?ids={ids_param}", headers=headers)
                        status_response.raise_for_status()
                        status_data = status_response.json()
                    except Exception as poll_err:
                        self.app.warning(f"Error polling Suno status: {poll_err}. Retrying...")
                        continue # Retry polling

                    # Process status data (Highly API dependent)
                    remaining_clip_ids = []
                    for clip_info in status_data: # Assuming status_data is a list
                         clip_id = clip_info.get('id')
                         status = clip_info.get('status')
                         audio_url = clip_info.get('audio_url')
                         metadata = clip_info.get('metadata', {}) # Prompt, tags etc.

                         if status == 'complete' and audio_url:
                             self.app.InfoMessage(f"Clip {clip_id} complete. Downloading from {audio_url}")
                             try:
                                 # --- Download Audio ---
                                 audio_response = self.requests.get(audio_url, stream=True)
                                 audio_response.raise_for_status()
                                 audio_bytes = audio_response.content

                                 # --- Save Audio ---
                                 output_path = Path(output_dir or self.output_folder)
                                 output_path.mkdir(parents=True, exist_ok=True)
                                 # Create filename
                                 if output_file_name:
                                     # Use provided name, maybe add index if multiple clips
                                     idx_suffix = f"_{generated_files.count(output_file_name)}" if generated_files.count(output_file_name) > 0 else ""
                                     base_filename = f"{Path(output_file_name).stem}{idx_suffix}"
                                 else:
                                     timestamp = int(time.time())
                                     safe_prompt = "".join(c if c.isalnum() else "_" for c in prompt[:20]).rstrip('_')
                                     # Use clip ID for uniqueness if possible
                                     base_filename = f"suno_{safe_prompt}_{clip_id}_{timestamp}"

                                 # Determine format (Suno often provides MP3 or WAV)
                                 # We will save as WAV for consistency using scipy
                                 # This requires decoding the original format first if it's not WAV
                                 # For simplicity, let's assume we can save the bytes directly or need a library like pydub/soundfile
                                 # Using scipy requires WAV format data or conversion.

                                 # Simplification: Assume it's WAV-compatible bytes (or decode first)
                                 # You might need:
                                 # import soundfile as sf
                                 # audio_numpy, sampling_rate = sf.read(io.BytesIO(audio_bytes))
                                 # OR: Use wave module for basic WAV handling if headers are correct
                                 import wave
                                 try:
                                     output_filepath = (output_path / f"{base_filename}.wav").resolve()
                                     with wave.open(io.BytesIO(audio_bytes), 'rb') as wf:
                                         sampling_rate = wf.getframerate()
                                         n_frames = wf.getnframes()
                                         audio_frames = wf.readframes(n_frames)
                                         # Convert bytes to numpy array (requires knowing sample width and channels)
                                         sample_width = wf.getsampwidth()
                                         n_channels = wf.getnchannels()
                                         dtype_map = {1: np.int8, 2: np.int16, 4: np.int32} # Mapping sampwidth to numpy dtype
                                         if sample_width not in dtype_map:
                                             raise ValueError(f"Unsupported sample width: {sample_width}")
                                         audio_numpy = np.frombuffer(audio_frames, dtype=dtype_map[sample_width])
                                         if n_channels > 1:
                                             audio_numpy = audio_numpy.reshape(-1, n_channels)

                                     # Save with scipy (now that we have numpy array and rate)
                                     # Ensure float32 for consistency if needed by downstream apps
                                     if audio_numpy.dtype != np.float32:
                                          # Normalize int to float -1.0 to 1.0
                                          max_val = np.iinfo(audio_numpy.dtype).max
                                          audio_numpy = audio_numpy.astype(np.float32) / max_val

                                     self.scipy_wavfile.write(output_filepath, sampling_rate, audio_numpy)
                                     actual_duration_s = n_frames / sampling_rate

                                 except wave.Error as wave_err:
                                     # Fallback: Save as received format if WAV parsing fails (e.g., MP3)
                                     self.app.warning(f"Could not parse audio as WAV ({wave_err}). Saving raw bytes with likely incorrect extension.")
                                     ext = ".mp3" if audio_response.headers.get('Content-Type') == 'audio/mpeg' else ".bin"
                                     output_filepath = (output_path / f"{base_filename}{ext}").resolve()
                                     with open(output_filepath, 'wb') as f:
                                         f.write(audio_bytes)
                                     sampling_rate = "N/A (non-WAV)"
                                     actual_duration_s = "N/A (non-WAV)"


                                 self.app.InfoMessage(f"Audio saved to: {output_filepath}")

                                 # --- Prepare Result Dictionary ---
                                 result = {
                                     "path": str(output_filepath),
                                     "prompt": metadata.get('prompt', prompt), # Use metadata prompt if available
                                     "duration_s": round(actual_duration_s, 2) if isinstance(actual_duration_s, (int, float)) else actual_duration_s,
                                     "sampling_rate": sampling_rate,
                                     "seed": metadata.get('seed', "N/A"), # Report if API provides it
                                     "format": Path(output_filepath).suffix.lower().strip('.'),
                                     "model": metadata.get('model_name', gen_model_version),
                                     "suno_clip_id": clip_id,
                                     "tags": metadata.get('tags', None),
                                     "service": "Suno API"
                                 }
                                 generated_files.append(result)

                             except Exception as download_err:
                                 self.app.error(f"Failed to download or save audio for clip {clip_id}: {download_err}")
                                 # Keep the ID to potentially retry? Or just report error.

                         elif status in ['queued', 'streaming', 'generating']:
                             remaining_clip_ids.append(clip_id) # Keep polling for this one
                         else: # Failed, error, etc.
                             self.app.error(f"Suno clip {clip_id} failed with status: {status}. Info: {clip_info.get('error_message', 'No details')}")
                             # Don't add to remaining_clip_ids

                    clip_ids = remaining_clip_ids # Update list for next poll iteration

                    if not clip_ids: # All clips processed (completed or failed)
                        break

                if (time.time() - start_time) >= self.service_config.generation_timeout_s and clip_ids:
                    self.app.error(f"Suno generation timed out after {self.service_config.generation_timeout_s}s. Remaining clips: {clip_ids}")

                return generated_files

            except self.requests.exceptions.RequestException as e:
                self.app.error(f"Suno API request failed: {e}")
                return []
            except Exception as e:
                self.app.error(f"Error generating music with Suno API: {e}")
                import traceback
                self.app.error(traceback.format_exc())
                return []
            finally:
                self.app.HideBlockingMessage()

    @staticmethod
    def get(app: LollmsApplication) -> 'SunoApiTTM':
        return SunoApiTTM