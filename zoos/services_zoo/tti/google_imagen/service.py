# Title: LollmsGoogleGemini
# Licence: Apache 2.0
# Author : Paris Neo & Contributing Community
# Maintainer : Paris Neo
# Status : Maintaining
# Description:
# This binding allows Lollms to generate images using Google's Gemini and Imagen 3 models
# via the google-generativeai SDK, following specific documentation examples provided by the user.
# Requirements:
# 1. Install the SDK: pip install google-generativeai
# 2. Obtain a Gemini API Key: https://aistudio.google.com/app/apikey
# 3. Set the GEMINI_API_KEY environment variable or configure it in the Lollms binding settings.

from pathlib import Path
import sys
from lollms.app import LollmsApplication
from lollms.paths import LollmsPaths
from lollms.config import TypedConfig, ConfigTemplate, BaseConfig
import time
import io
import sys
import requests
import os
import base64
import subprocess
import time
import json
import platform
from dataclasses import dataclass
from PIL import Image, PngImagePlugin
from enum import Enum
from typing import List, Dict, Any, Optional, Tuple
import importlib

from ascii_colors import ASCIIColors, trace_exception
from lollms.paths import LollmsPaths
from lollms.utilities import PackageManager, find_next_available_filename, short_desc
from lollms.tti import LollmsTTI
import subprocess
import shutil
from tqdm import tqdm
import threading
from io import BytesIO
import pipmaster as pm

pm.ensure_packages(["google-genai>=1.10.0"])

# Ensure google-generativeai installation
try:
    # Use the import style from the documentation examples
    from google import genai
    from google.genai import types
    importlib.import_module("google.ai.generativelanguage")
except ImportError:
    ASCIIColors.info("Google Generative AI package not found. Installing...")
    PackageManager.install_package("google-generativeai")
    try:
        from google import genai
        from google.genai import types
        importlib.import_module("google.ai.generativelanguage")
        ASCIIColors.success("google-generativeai installed and imported successfully.")
    except ImportError as e:
        ASCIIColors.error("Failed to import google-generativeai even after attempting installation.")
        trace_exception(e)
        raise ImportError("Could not install or import google-generativeai.") from e

# Import necessary Google API Core libraries for exceptions
try:
    from google.api_core import exceptions as google_api_exceptions
except ImportError as e:
    ASCIIColors.error("google-api-core library import failed.")
    trace_exception(e)
    raise e from e


class LollmsGoogleGemini(LollmsTTI):
    """
    Lollms binding for Google Gemini and Imagen 3 image generation.
    Uses client = genai.Client(api_key=...) initialization and specific API calls.
    """
    def __init__(
            self,
            app: LollmsApplication,
            config: Optional[dict] = None,
            lollms_paths: Optional[LollmsPaths] = None,
            ):
        output_folder: Path = Path("./outputs/tti/google_gemini")
        if lollms_paths:
            output_folder = lollms_paths.personal_outputs_path / "tti" / "google_gemini"
        elif hasattr(app, "lollms_paths"):
             output_folder = app.lollms_paths.personal_outputs_path / "tti" / "google_gemini"

        default_api_key = os.getenv("GEMINI_API_KEY", "")

        service_config_template = ConfigTemplate([
            {"name": "gemini_api_key", "type": "str", "value": default_api_key, "help": "Your Google Gemini API Key. Required."},
            {"name": "model_name", "type": "str", "value": "imagen-3.0-generate-002", "options":["imagen-3.0-generate-002", "imagen-3.0-generate-001", "gemini-2.0-flash-exp-image-generation", "gemini-1.5-flash"], "help": "Generation model. Imagen uses generate_images, Gemini uses generate_content. Note: imagen-3.0-generate-002 requires specific API access."},
            {"name": "number_of_images", "type": "int", "value": 1, "min":1, "max":4, "help": "Images per request (Max 4 for Imagen 3). Only first image saved."},
            {"name": "aspect_ratio", "type": "str", "value":"1:1", "options":["1:1", "16:9", "9:16", "4:3", "3:4"], "help":"Image aspect ratio (Used for Imagen 3 call)."},
            {"name": "output_text_with_image", "type": "bool", "value": False, "help": "For Gemini: Include generated text in metadata."},
            {"name": "request_text_modality", "type": "bool", "value": False, "help": "For Gemini experimental: Request TEXT modality with IMAGE."},
        ])
        service_config = TypedConfig(service_config_template)
        super().__init__("google_gemini", app, service_config, output_folder)

        self.client = None # Store the client instance
        self.client_initialized = False
        # Attempt initialization immediately if key exists
        if self.service_config.gemini_api_key:
            self._initialize_client()
        else:
            ASCIIColors.warning("Gemini API Key not found. Configure in settings.")

    # --- _ensure_output_folder remains the same ---
    def _ensure_output_folder(self, output_folder: Optional[str | Path] = None) -> Path:
        if output_folder is None: output_folder_path = self.output_folder
        else: output_folder_path = Path(output_folder)
        if not output_folder_path:
             output_folder_path = Path("./outputs/tti/google_gemini")
             ASCIIColors.error("Output folder not determined, using fallback.")
             self.output_folder = output_folder_path
        try:
            output_folder_path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            ASCIIColors.error(f"Could not create output folder: {output_folder_path}")
            trace_exception(e); raise IOError(f"Failed to create output dir: {output_folder_path}") from e
        return output_folder_path

    # --- _list_models adapted to use self.client if available ---
    def _list_models(self):
        """Helper to list models using the client object if initialized."""
        if not self.client: # Check if client exists
             # Try to create a temporary client just for listing if API key is present
             api_key = self.service_config.gemini_api_key
             if api_key:
                 try:
                     temp_client = genai.Client(api_key=api_key)
                     models = temp_client.models.list()
                     ASCIIColors.info("(Listing via temporary client instance)")
                 except Exception as e:
                     self.app.warning(f"Failed to create temporary client or list models: {e}")
                     return None
             else:
                 self.app.warning("Cannot list models, client not initialized and no API key found.")
                 return None
        else: # Use the existing client
            try:
                models = self.client.models.list()
                ASCIIColors.info("(Listing via self.client instance)")
            except Exception as e:
                self.app.error(f"Failed to list models using existing client: {e}")
                trace_exception(e)
                return None

        # Process the retrieved models list
        try:
            model_info = []
            for m in models:
                 model_info.append({
                     "name": m.name, "display_name": m.display_name,
                     "supported_methods": ["TEXT","IMAGE"]
                 })
                 ASCIIColors.info(f"  - {m.name} ({m.display_name})")
            return model_info
        except Exception as e:
            self.app.error(f"Failed to process listed models: {e}")
            trace_exception(e)
            return None


    # --- _initialize_client using genai.Client(api_key=...) ---
    def _initialize_client(self):
        """Initializes the Google Generative AI client using Client(api_key=...)."""
        if self.client_initialized and self.client: # Check both flag and object
            return True

        api_key = self.service_config.gemini_api_key
        if not api_key:
            self.app.error("Gemini API Key is missing. Cannot initialize client.")
            return False

        try:
            ASCIIColors.info("Initializing Google Generative AI client using genai.Client(api_key=...).")
            # Directly instantiate the client with the API key
            self.client = genai.Client(api_key=api_key)
            self.client_initialized = True
            ASCIIColors.success("Google Generative AI client initialized successfully.")

            # Optional: Verify models after initialization
            self._list_models() # Helps confirm client works
            return True

        # Catch specific initialization errors if Client() raises them
        except (google_api_exceptions.PermissionDenied, google_api_exceptions.Unauthenticated) as e:
            self.app.error(f"Authentication Failed during client initialization: {type(e).__name__}. Check API Key/Permissions.")
            trace_exception(e)
            self.client_initialized = False
            self.client = None
            return False
        except requests.exceptions.RequestException as e:
             self.app.error(f"Network Error during client initialization: {e}")
             trace_exception(e)
             self.client_initialized = False
             self.client = None
             return False
        except Exception as e:
            # Catch potential errors from genai.Client() itself
            self.app.error(f"Failed to initialize Google Generative AI client with genai.Client(api_key=...): {e}")
            trace_exception(e)
            self.client_initialized = False
            self.client = None
            return False

    def settings_updated(self):
        """Called when settings are updated. Re-initializes the client."""
        ASCIIColors.info("Google Gemini/Imagen settings updated.")
        self.client_initialized = False
        self.client = None # Reset client object
        if self.service_config.gemini_api_key:
             self._initialize_client() # Attempt re-init
        else:
            ASCIIColors.warning("Gemini API Key is not set. Client not initialized.")

    # --- paint Method using specific calls based on model name ---
    def paint(
        self,
        positive_prompt: str,
        negative_prompt: str = "",
        sampler_name: str = "Default", # Ignored
        seed: Optional[int] = None,   # Ignored
        scale: Optional[float] = None, # Ignored
        steps: Optional[int] = None,   # Ignored
        width: Optional[int] = None,   # Ignored
        height: Optional[int] = None,  # Ignored
        output_folder: Optional[str | Path] = None,
        output_file_name: Optional[str] = None
    ) -> Tuple[Path | None, Dict | None]:
        """
        Generates an image using the selected Google model, following user-provided example structure.
        """
        saved_path: Optional[Path] = None
        metadata_or_error: Optional[Dict] = None
        generated_text: Optional[str] = None

        # Ensure client is initialized
        if not self.client_initialized:
            if not self._initialize_client():
                 return None, {"error": "Google Generative AI client failed to initialize."}
        if not self.client: # Double check client object exists
             return None, {"error": "Google Generative AI client object is not available after initialization attempt."}

        output_folder_path = self._ensure_output_folder(output_folder)
        model_name_config = self.service_config.model_name

        full_prompt = positive_prompt.strip()
        if negative_prompt and negative_prompt.strip():
             full_prompt += f". Avoid: {negative_prompt.strip()}"
             ASCIIColors.warning("Negative prompt appended.")

        start_time = time.time()

        try:
            # --- Determine API Call based on Model Name Convention ---
            if "imagen" in model_name_config:
                # --- Imagen API Call (using client.models.generate_images) ---
                num_images = self.service_config.number_of_images
                aspect_ratio = self.service_config.aspect_ratio # Get aspect ratio from config

                if num_images > 1: ASCIIColors.info(f"Requesting {num_images} images, saving first.")
                self.app.info(f"Generating image(s) with Imagen ({model_name_config})...\nPrompt: {short_desc(full_prompt)}")
                ASCIIColors.info(f"Using client.models.generate_images with aspect_ratio: {aspect_ratio}")

                # Config object as per example - aspect_ratio goes inside config
                imagen_config = types.GenerateImagesConfig(
                    number_of_images=num_images,
                    aspect_ratio=aspect_ratio  # Pass aspect_ratio inside config
                )

                # Try different model name formats for Imagen
                # The API might expect models/ prefix or different version
                model_names_to_try = [
                    model_name_config,
                    f"models/{model_name_config}",
                    "imagen-3.0-generate-001",
                    "models/imagen-3.0-generate-001",
                ]
                
                response = None
                last_error = None
                for model_name_attempt in model_names_to_try:
                    try:
                        ASCIIColors.info(f"Attempting with model name: {model_name_attempt}")
                        response = self.client.models.generate_images(
                            model=model_name_attempt,
                            prompt=full_prompt,
                            config=imagen_config
                        )
                        ASCIIColors.success(f"Successfully used model: {model_name_attempt}")
                        break  # Success, exit the loop
                    except Exception as e:
                        last_error = e
                        error_str = str(e)
                        if "404" in error_str or "NOT_FOUND" in error_str or "not found" in error_str.lower():
                            ASCIIColors.warning(f"Model {model_name_attempt} not found, trying next...")
                            continue
                        else:
                            # Re-raise if it's not a 404 error
                            raise
                
                if response is None:
                    # All attempts failed
                    raise last_error if last_error else Exception("All model name attempts failed")

                elapsed_time = time.time() - start_time
                ASCIIColors.info(f"Imagen API call finished in {elapsed_time:.2f}s.")

                if not hasattr(response, 'generated_images') or not response.generated_images:
                     return None, {"error": "Imagen API call returned no generated_images."}

                first_image_data = response.generated_images[0].image
                if not hasattr(first_image_data, 'image_bytes'):
                     return None, {"error": "First Imagen result missing image_bytes."}

                image_bytes = first_image_data.image_bytes
                file_path = find_next_available_filename(output_folder_path, "imagen_img_", "png")
                if output_file_name: file_path = output_folder_path / f"{Path(output_file_name).stem}.png"

                try:
                    img = Image.open(BytesIO(image_bytes)).save(file_path)
                    saved_path = file_path
                    ASCIIColors.yellow(f"Saved Imagen image to: {saved_path}")
                    metadata_or_error = {
                        "positive_prompt": positive_prompt, "negative_prompt": negative_prompt,
                        "full_prompt_sent": full_prompt, "model": model_name_config,
                        "aspect_ratio_used": aspect_ratio, # Record used aspect ratio
                        "generation_time_sec": round(elapsed_time, 2),
                        "safety_attributes": str(getattr(response.generated_images[0], 'safety_attributes', 'N/A')),
                        "num_generated": len(response.generated_images)
                    }
                except Exception as e:
                    self.app.error(f"Failed to save Imagen image: {e}"); trace_exception(e)
                    return None, {"error": f"Failed to save Imagen image: {e}"}

            elif "gemini" in model_name_config:
                # --- Gemini API Call (using client.models.generate_content) ---
                self.app.info(f"Generating content with Gemini ({model_name_config})...\nPrompt: {short_desc(full_prompt)}")

                content_config_params = {}
                if model_name_config == "gemini-2.0-flash-preview-image-generation":
                     modalities = ["IMAGE","TEXT"]
                     content_config_params['response_modalities'] = modalities
                     ASCIIColors.info(f"Using response_modalities: {modalities}")
                else: # Try mime type for other Gemini
                    try: content_config_params['response_mime_type'] = "image/png"
                    except Exception: pass # Ignore if key not valid

                content_config = types.GenerateContentConfig(**content_config_params)

                # THE CALL FROM OTHER DOC EXAMPLE
                response = self.client.models.generate_content(
                    model=model_name_config, # Use short name
                    contents=full_prompt,
                    config=content_config
                )

                elapsed_time = time.time() - start_time
                ASCIIColors.info(f"Gemini API call finished in {elapsed_time:.2f}s.")

                if not response.candidates:
                     # ... (error handling) ...
                    self.app.warning(f"Gemini ({model_name_config}) returned no candidates.")
                    error_msg = f"Model ({model_name_config}) API call returned no candidates."
                    p_feedback = getattr(response, "prompt_feedback", None)
                    b_reason = getattr(p_feedback, "block_reason", None) if p_feedback else None
                    if b_reason: error_msg += f" Prompt blocked: {b_reason}"
                    self.app.error(error_msg)
                    return None, {"error": error_msg}

                first_candidate = response.candidates[0]
                if not first_candidate.content or not first_candidate.content.parts:
                     # ... (error handling) ...
                    self.app.warning(f"Gemini first candidate has no content parts.")
                    error_msg = "First candidate has no content parts."
                    f_reason = getattr(first_candidate, 'finish_reason', None)
                    if f_reason and f_reason != types.FinishReason.STOP: error_msg += f" Stop Reason: {f_reason}"
                    self.app.error(error_msg)
                    return None, {"error": error_msg}

                # Process parts
                first_image_part = None
                for part in first_candidate.content.parts:
                     if not first_image_part and part.inline_data and part.inline_data.mime_type.startswith("image/"):
                          first_image_part = part
                     elif self.service_config.output_text_with_image and part.text:
                          generated_text = (generated_text + "\n" + part.text) if generated_text else part.text

                if first_image_part:
                     image_bytes = first_image_part.inline_data.data
                     file_path = find_next_available_filename(output_folder_path, "gemini_img_", "png")
                     if output_file_name: file_path = output_folder_path / f"{Path(output_file_name).stem}.png"

                     try:
                         img = Image.open(BytesIO(image_bytes)).save(file_path)
                         saved_path = file_path
                         ASCIIColors.yellow(f"Saved Gemini image to: {saved_path}")
                         metadata_or_error = {
                             "positive_prompt": positive_prompt, "negative_prompt": negative_prompt,
                             "full_prompt_sent": full_prompt, "model": model_name_config,
                             "generation_time_sec": round(elapsed_time, 2),
                             "safety_ratings": str(getattr(first_candidate, 'safety_ratings', 'N/A')),
                             "finish_reason": str(getattr(first_candidate, 'finish_reason', 'N/A')),
                             "num_candidates": len(response.candidates)
                         }
                         if generated_text: metadata_or_error["generated_text"] = generated_text

                     except Exception as e:
                         self.app.error(f"Failed to save Gemini image: {e}"); trace_exception(e)
                         return None, {"error": f"Failed to save Gemini image: {e}"}
                else:
                     # ... (No image found handling) ...
                     self.app.warning(f"No image data found in Gemini response.")
                     error_detail = "No image data found."
                     if generated_text: error_detail += f" Only text generated: {short_desc(generated_text, 50)}"
                     metadata_or_error = {"error": error_detail}

            else:
                return None, {"error": f"Unknown model type: {model_name_config}"}

            # Final return
            if saved_path and metadata_or_error and "error" not in metadata_or_error:
                return saved_path, metadata_or_error
            elif metadata_or_error and "error" in metadata_or_error:
                 return None, metadata_or_error
            else: # Fallback
                 return None, {"error": "Generation failed post-API call."}

        # --- Error Handling ---
        # Catch AttributeError specifically for generate_images
        except AttributeError as e:
             if 'generate_images' in str(e):
                  self.app.error("AttributeError: `client.models.generate_images` failed.")
                  self.app.error("The user-provided example may be incompatible with the installed SDK version.")
                  self.app.error("Consider using the unified `GenerativeModel(...).generate_content` approach if this persists.")
                  trace_exception(e)
                  return None, {"error": "AttributeError: generate_images method not found. SDK/Doc mismatch?"}
             else: # Other AttributeErrors
                  self.app.error(f"Unexpected AttributeError: {e}"); trace_exception(e)
                  return None, {"error": f"Unexpected AttributeError: {e}"}
        # Other exceptions...
        except google_api_exceptions.NotFound as e:
             # ... (Specific check for experimental model 404) ...
             if model_name_config == "gemini-2.0-flash-exp-image-generation" and "is not found for API version v1beta" in str(e):
                   return None, {"error": f"Model Not Found (404): Experimental model '{model_name_config}' unavailable."}
             else: return None, {"error": f"Model Not Found Error (404): {model_name_config}. {e}"}
        except (google_api_exceptions.PermissionDenied, google_api_exceptions.Unauthenticated) as e:
             self.client_initialized = False; self.client = None # Reset
             return None, {"error": f"Authentication Failed ({type(e).__name__}): {e}"}
        except google_api_exceptions.InvalidArgument as e: return None, {"error": f"Invalid Argument: {e}"}
        except google_api_exceptions.ResourceExhausted as e: return None, {"error": f"Quota Exceeded: {e}"}
        except google_api_exceptions.FailedPrecondition as e: return None, {"error": f"Failed Precondition: {e}"}
        except Exception as e:
            self.app.error(f"Unexpected error: {type(e).__name__}"); trace_exception(e)
            return None, {"error": f"Unexpected error: {type(e).__name__} - {e}"}


    # --- paint_from_images Method using client.models.generate_content ---
    def paint_from_images(
        self,
        positive_prompt: str,
        images: List[str],
        negative_prompt: str = "",
        # ... other params ignored ...
        output_folder=None,
        output_file_name=None
        ) -> Tuple[Path | None, Dict | None]:
        """
        Generates an image based on prompt and input image using client.models.generate_content.
        """
        saved_path: Optional[Path] = None
        metadata_or_error: Optional[Dict] = None
        generated_text: Optional[str] = None
        model_name_config = self.service_config.model_name

        if not self.client_initialized:
            if not self._initialize_client(): return None, {"error": "Client failed to initialize."}
        if not self.client: return None, {"error": "Client object unavailable."}
        if not images: return None, {"error": "No input images."}

        # Load Image
        try:
            input_image_path = Path(images[0])
            if not input_image_path.exists(): return None, {"error": f"Input image not found: {input_image_path.name}"}
            pil_image = Image.open(input_image_path)
            if pil_image.mode != 'RGB': pil_image = pil_image.convert('RGB')
            if len(images) > 1: ASCIIColors.warning(f"Using only first input image.")
        except Exception as e: return None, {"error": f"Failed to load input image: {e}"}

        output_folder_path = self._ensure_output_folder(output_folder)
        full_prompt = positive_prompt.strip()
        if negative_prompt and negative_prompt.strip():
             full_prompt += f". Avoid: {negative_prompt.strip()}"

        start_time = time.time()

        try:
            self.app.info(f"Generating image with {model_name_config} (from image)...")

            content_config_params = {}
            if model_name_config == "gemini-2.0-flash-exp-image-generation":
                 modalities = ["IMAGE"]
                 if self.service_config.request_text_modality: modalities.append("TEXT")
                 content_config_params['response_modalities'] = modalities
            else:
                try: content_config_params['response_mime_type'] = "image/png"
                except Exception: pass

            content_config = types.GenerateContentConfig(**content_config_params)
            contents = [full_prompt, pil_image] # Prompt + PIL Image object

            # Use client.models.generate_content
            response = self.client.models.generate_content(
                    model=model_name_config,
                    contents=contents,
                    config=content_config
                )

            elapsed_time = time.time() - start_time

            # Process response (similar logic to paint/Gemini)
            if not response.candidates:
                 # ... (error handling) ...
                 self.app.warning(f"{model_name_config} (img2img) returned no candidates.")
                 error_msg = f"API call returned no candidates (img2img)."
                 p_feedback = getattr(response, "prompt_feedback", None)
                 b_reason = getattr(p_feedback, "block_reason", None) if p_feedback else None
                 if b_reason: error_msg += f" Prompt blocked: {b_reason}"
                 self.app.error(error_msg)
                 return None, {"error": error_msg}

            first_candidate = response.candidates[0]
            if not first_candidate.content or not first_candidate.content.parts:
                 # ... (error handling) ...
                 self.app.warning(f"{model_name_config} (img2img) first candidate has no parts.")
                 error_msg = "First candidate has no content parts (img2img)."
                 f_reason = getattr(first_candidate, 'finish_reason', None)
                 if f_reason and f_reason != types.FinishReason.STOP: error_msg += f" Stop Reason: {f_reason}"
                 self.app.error(error_msg)
                 return None, {"error": error_msg}

            first_image_part = None
            for part in first_candidate.content.parts:
                 if not first_image_part and part.inline_data and part.inline_data.mime_type.startswith("image/"):
                      first_image_part = part
                 elif self.service_config.output_text_with_image and part.text:
                      generated_text = (generated_text + "\n" + part.text) if generated_text else part.text

            if first_image_part:
                 image_bytes = first_image_part.inline_data.data
                 file_prefix = "imagen_edit_" if "imagen" in model_name_config else "gemini_edit_"
                 if output_file_name: file_path = output_folder_path / f"{Path(output_file_name).stem}_edit.png"
                 else: file_path = find_next_available_filename(output_folder_path, file_prefix, "png")

                 try:
                     img = Image.open(BytesIO(image_bytes)).save(file_path)
                     saved_path = file_path
                     ASCIIColors.yellow(f"Saved edited image to: {saved_path}")
                     metadata_or_error = {
                         "positive_prompt": positive_prompt, "negative_prompt": negative_prompt,
                         "full_prompt_sent": full_prompt, "input_image": str(input_image_path.name),
                         "model": model_name_config, "generation_time_sec": round(elapsed_time, 2),
                         "safety_ratings": str(getattr(first_candidate, 'safety_ratings', 'N/A')),
                         "finish_reason": str(getattr(first_candidate, 'finish_reason', 'N/A')),
                         "num_candidates": len(response.candidates)
                     }
                     if generated_text: metadata_or_error["generated_text"] = generated_text

                 except Exception as e:
                     self.app.error(f"Failed to save edited image: {e}"); trace_exception(e)
                     return None, {"error": f"Failed to save edited image: {e}"}
            else:
                 # ... (No image found handling) ...
                 self.app.warning(f"No image data found in img2img response.")
                 error_detail = "No image data found (img2img)."
                 if generated_text: error_detail += f" Only text generated: {short_desc(generated_text, 50)}"
                 metadata_or_error = {"error": error_detail}

            # Return logic
            if saved_path and metadata_or_error and "error" not in metadata_or_error:
                return saved_path, metadata_or_error
            elif metadata_or_error and "error" in metadata_or_error:
                 return None, metadata_or_error
            else: return None, {"error": "Img2Img failed post-API call."}

        # --- Error Handling ---
        # (Similar exceptions as paint)
        except google_api_exceptions.NotFound as e:
             # ... (Check experimental model) ...
             if model_name_config == "gemini-2.0-flash-exp-image-generation" and "is not found for API version v1beta" in str(e):
                 return None, {"error": f"Model Not Found (404) (img2img): Experimental model '{model_name_config}' unavailable."}
             else: return None, {"error": f"Model Not Found (404) (img2img): {model_name_config}. {e}"}
        except (google_api_exceptions.PermissionDenied, google_api_exceptions.Unauthenticated) as e:
             self.client_initialized = False; self.client = None
             return None, {"error": f"Authentication Failed ({type(e).__name__}) (img2img): {e}"}
        except google_api_exceptions.InvalidArgument as e:
             return None, {"error": f"Invalid Argument (img2img): Input: {input_image_path.name}. {e}"}
        except google_api_exceptions.ResourceExhausted as e: return None, {"error": f"Quota Exceeded (img2img): {e}"}
        except google_api_exceptions.FailedPrecondition as e: return None, {"error": f"Failed Precondition (img2img): {e}"}
        except Exception as e:
            self.app.error(f"Unexpected error (img2img): {type(e).__name__}"); trace_exception(e)
            return None, {"error": f"Unexpected error (img2img): {type(e).__name__} - {e}"}


    # --- Static Methods (verify, install, get) ---
    @staticmethod
    def verify(app: LollmsApplication) -> bool:
        return PackageManager.check_package_installed("google-generativeai")

    @staticmethod
    def install(app: LollmsApplication) -> bool:
        return PackageManager.install_package("google-generativeai") or False

    @staticmethod
    def get(app: LollmsApplication, config: Optional[dict]=None, lollms_paths: Optional[LollmsPaths] = None) -> 'LollmsGoogleGemini':
        return LollmsGoogleGemini(app=app, config=config, lollms_paths=lollms_paths)