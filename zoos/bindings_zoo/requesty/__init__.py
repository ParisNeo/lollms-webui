######
# Project       : lollms
# File          : binding.py
# Author        : ParisNeo with the help of the community
# Underlying
# engine author : Requesty
# license       : Apache 2.0
# Description   :
# This binding provides an interface to the Requesty API, routing requests
# to various AI models. Supports dynamic model fetching and auto-routing.
# Update date   : 19/07/2024
######
from pathlib import Path
from typing import Callable, Any, Optional, List, Dict, Union, Tuple
from lollms.config import BaseConfig, TypedConfig, ConfigTemplate, InstallOption
from lollms.paths import LollmsPaths
from lollms.binding import LLMBinding, LOLLMSConfig, BindingType
from lollms.helpers import ASCIIColors, trace_exception, is_valid_url
from lollms.types import MSG_OPERATION_TYPE
from lollms.utilities import find_first_available_file_path, is_file_path, encode_image

from lollms.com import LoLLMsCom
import subprocess
import yaml
import sys
import os
import json
import requests
import base64
from time import perf_counter, time

# Try to install necessary packages using pipmaster
try:
    import pipmaster as pm
    if not pm.is_installed("openai"):
        pm.install("openai>=1.0.0") # Ensure modern openai lib
    if not pm.is_installed("requests"):
        pm.install("requests")
except ImportError:
    print("Warning: pipmaster not found. Please install required packages manually: pip install openai requests")
    # Attempt direct import, assuming they might already be installed
    pass

# Import required libraries
try:
    import openai
    from openai import OpenAI # Explicit import for clarity
except ImportError as e:
    print(f"Error importing required libraries: {e}")
    print("Please ensure 'openai' and 'requests' are installed (`pip install openai requests`)")
    raise e # Re-raise the exception

__author__ = "parisneo"
__github__ = "https://github.com/ParisNeo/lollms_bindings_zoo"
__copyright__ = "Copyright 2023-2024, ParisNeo"
__license__ = "Apache 2.0"

binding_name = "Requesty"
binding_folder_name = "requesty" # Ensure this matches the directory name
binding_path = Path(__file__).parent

DEFAULT_CONFIG = {
    "requesty_key": "",
    "auto_fetch_models": True,
    "models_refresh_interval": 60, # Minutes
    "enable_auto_routing": False,
    "auto_route_models": "openai/gpt-4o-mini", # Example default, comma-separated
    "auto_set_ctx_size": True,
    "ctx_size": 4096,        # Fallback/manual context size
    "max_n_predict": 4096,   # Fallback/manual max prediction tokens
    "seed": -1,
    "temperature": 0.7,      # Added from old default_params
    "top_p": 0.96,           # Added from old default_params
    "presence_penalty": 0.0, # Added standard param
    "frequency_penalty": 0.0,# Added standard param
    "max_image_width": -1,   # For vision models
    "turn_on_cost_estimation": True, # Default to true for API bindings
    "total_input_tokens": 0.0,
    "total_output_tokens": 0.0,
    "total_input_cost": 0.0,
    "total_output_cost": 0.0,
    "total_cost": 0.0,
    "override_api_url": "https://router.requesty.ai/v1",
}

class Requesty(LLMBinding):
    """
    Binding class for interacting with the Requesty API.
    """
    API_URL = "https://router.requesty.ai/v1/models" # For fetching models

    def __init__(self,
                config: LOLLMSConfig,
                lollms_paths: LollmsPaths = None,
                installation_option:InstallOption=InstallOption.INSTALL_IF_NECESSARY,
                lollmsCom:Optional[LoLLMsCom]=None) -> None:
        """
        Initialize the Binding.
        """
        if lollms_paths is None:
            lollms_paths = LollmsPaths()
        self.lollmsCom = lollmsCom

        # Configuration definition using ConfigTemplate
        binding_config_template = ConfigTemplate([
            # --- Credentials & Basic Setup ---
            {"name":"requesty_key","type":"str","value":DEFAULT_CONFIG["requesty_key"],"help":"Your Requesty API key. Found at https://app.requesty.ai/api-keys"},
            {"name":"auto_fetch_models", "type":"bool", "value":DEFAULT_CONFIG["auto_fetch_models"], "help":"Automatically fetch the list of available models from Requesty."},
            {"name":"models_refresh_interval", "type":"int", "value":DEFAULT_CONFIG["models_refresh_interval"], "min":1, "help":"Interval in minutes to refresh the models list if auto-fetch is enabled."},

            # --- Auto Routing ---
            {"name":"enable_auto_routing", "type":"bool", "value":DEFAULT_CONFIG["enable_auto_routing"], "help":"Enable Requesty's auto-routing feature to select the best model from a list."},
            {"name":"auto_route_models", "type":"str", "value":DEFAULT_CONFIG["auto_route_models"], "help":"Comma-separated list of model IDs to consider for auto-routing (e.g., 'openai/gpt-4o-mini,anthropic/claude-3-5-sonnet'). Only used if auto-routing is enabled."},

            # --- Model Limits ---
            {"name":"auto_set_ctx_size", "type":"bool", "value":DEFAULT_CONFIG["auto_set_ctx_size"], "help":"Automatically set the context size based on the selected model's information. If disabled, uses the manual value below."},
            {"name":"ctx_size","type":"int","value":DEFAULT_CONFIG["ctx_size"], "min":1, "help":"Manual context size (input tokens). Used if 'auto_set_ctx_size' is disabled or if detection fails."},
            {"name":"max_n_predict","type":"int","value":DEFAULT_CONFIG["max_n_predict"], "min":1, "help":"Maximum number of tokens to generate per response. Should be compatible with the model's limits."},

            # --- Generation Parameters ---
            {"name":"seed","type":"int","value":DEFAULT_CONFIG["seed"],"help":"Random seed for generation (-1 for random)."},
            {"name":"temperature","type":"float","value":DEFAULT_CONFIG["temperature"],"min":0.0, "max":2.0, "help":"Temperature for sampling (0.0-2.0). Higher values mean more randomness."},
            {"name":"top_p","type":"float","value":DEFAULT_CONFIG["top_p"],"min":0.0, "max":1.0, "help":"Top-p (nucleus) sampling threshold (0.0-1.0)."},
            {"name":"presence_penalty","type":"float","value":DEFAULT_CONFIG["presence_penalty"],"min":-2.0, "max":2.0, "help":"Presence penalty (-2.0 to 2.0). Positive values encourage new topics."},
            {"name":"frequency_penalty","type":"float","value":DEFAULT_CONFIG["frequency_penalty"],"min":-2.0, "max":2.0, "help":"Frequency penalty (-2.0 to 2.0). Positive values discourage repetition."},
            # repetition_penalty seems less standard in OpenAI API structure used by OR, use frequency/presence instead

            # --- Vision ---
            {"name":"max_image_width","type":"int","value":DEFAULT_CONFIG["max_image_width"],"help":"Resize images if wider than this before sending to vision models (-1 for no change)."},

            # --- Cost Estimation ---
            {"name":"turn_on_cost_estimation","type":"bool", "value":DEFAULT_CONFIG["turn_on_cost_estimation"],"help":"Estimate query costs based on fetched pricing and estimated token counts (Note: Token count is an estimate, actual cost might vary)."},
            {"name":"total_input_tokens","type":"float", "value":DEFAULT_CONFIG["total_input_tokens"],"help":"Accumulated input tokens (estimate)."},
            {"name":"total_output_tokens","type":"float", "value":DEFAULT_CONFIG["total_output_tokens"],"help":"Accumulated output tokens (estimate)."},
            {"name":"total_input_cost","type":"float", "value":DEFAULT_CONFIG["total_input_cost"],"help":"Accumulated input cost ($) (estimate)."},
            {"name":"total_output_cost","type":"float", "value":DEFAULT_CONFIG["total_output_cost"],"help":"Accumulated output cost ($) (estimate)."},
            {"name":"total_cost","type":"float", "value":DEFAULT_CONFIG["total_cost"],"help":"Total accumulated cost ($) (estimate)."},

            # --- Advanced ---
            {"name":"override_api_url","type":"str","value":DEFAULT_CONFIG["override_api_url"],"help":"Advanced: Override the default Requesty API base URL."},
        ])
        # Default values for the configuration
        binding_config_defaults = BaseConfig(config=DEFAULT_CONFIG)

        binding_config = TypedConfig(
            binding_config_template,
            binding_config_defaults
        )
        super().__init__(
                            binding_path,
                            lollms_paths,
                            config,
                            binding_config,
                            installation_option,
                            SAFE_STORE_SUPPORTED_FILE_EXTENSIONS=['.png', '.jpg', '.jpeg', '.webp', '.gif'], # For vision models
                            lollmsCom=lollmsCom
                        )
        self.config.ctx_size = self.binding_config.config["ctx_size"] # Initial sync
        self.config.max_n_predict = self.binding_config.config["max_n_predict"] # Initial sync
        self.models_data: List[Dict] = []
        self.last_model_fetch_time: float = 0
        self.openai_client: Optional[OpenAI] = None
        self.current_model_metadata: Optional[Dict] = None


    def _get_api_key(self) -> Optional[str]:
        """Retrieves the API key from config or environment."""
        key = self.binding_config.config.get("requesty_key", "")
        if key and key.strip():
            return key
        # Fallback to environment variable
        key = os.getenv('REQUESTY_API_KEY')
        if key:
            # Update config if found in env var and config is empty
            # self.binding_config.config["requesty_key"] = key # Optionally update config
            # self.binding_config.save()
            return key
        return None

    def _fetch_models_from_api(self) -> List[Dict]:
        """Fetches the model data from the Requesty API"""
        api_url = self.binding_config.config.get("override_api_url", DEFAULT_CONFIG["override_api_url"])
        if not api_url.endswith('/'):
             api_url += '/'
        models_url = api_url + "models"

        if not is_valid_url(models_url):
             self.error(f"Invalid API URL for fetching models: {models_url}")
             return []

        try:
            headers = {"Accept": "application/json"} # No key needed for model list
            response = requests.get(models_url, headers=headers, timeout=60) # Added timeout
            response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)
            data = response.json()
            models = data.get('data', [])
            if not isinstance(models, list):
                self.error(f"Unexpected format for models data: {type(models)}")
                return []
            ASCIIColors.success(f"Fetched {len(models)} models from Requesty API.")
            return models
        except requests.exceptions.Timeout:
            self.error(f"Timeout fetching models from {models_url}.")
            return []
        except requests.exceptions.RequestException as e:
            self.error(f"Error fetching models from {models_url}: {e}")
            trace_exception(e)
            # Attempt to return previously fetched models if available?
            return self.models_data if self.models_data else []
        except Exception as e:
            self.error(f"An unexpected error occurred fetching models: {e}")
            trace_exception(e)
            return []

    def _fetch_models_if_needed(self) -> None:
        """Fetches models from the API if auto-fetch is enabled and interval has passed."""
        if not self.binding_config.config.get("auto_fetch_models", True):
            if not self.models_data:
                 self.warning("Model auto-fetching is disabled, and no models are loaded. Listing/selection might fail.")
            return # Auto-fetch disabled

        now = time()
        interval = self.binding_config.config.get("models_refresh_interval", 60) * 60 # Convert minutes to seconds
        if not self.models_data or (now - self.last_model_fetch_time > interval):
            ASCIIColors.info("Fetching or refreshing Requesty models list...")
            self.models_data = self._fetch_models_from_api()
            if self.models_data:
                self.last_model_fetch_time = now
            else:
                 # Fetch failed, keep potentially stale data if it exists
                 self.error("Failed to fetch models. Using previous list if available.")
        else:
            ASCIIColors.info("Using cached Requesty models list.")


    def settings_updated(self) -> None:
        """Callback triggered when binding settings are updated in the UI."""
        ASCIIColors.info("Requesty settings updated.")
        # Re-initialize client if API key or URL changed
        # Check if client exists and if relevant settings changed
        current_key = self._get_api_key()
        current_url = self.binding_config.config.get("override_api_url", DEFAULT_CONFIG["override_api_url"])

        client_needs_rebuild = False
        if self.openai_client:
             if self.openai_client.api_key != current_key or str(self.openai_client.base_url) != current_url.rstrip('/') + '/':
                  client_needs_rebuild = True
        else: # Client doesn't exist yet
             client_needs_rebuild = True

        if client_needs_rebuild:
             self.build_model() # Rebuild will re-create the client

        # Force model list refresh if interval changed or auto-fetch toggled
        # Or just let the interval check handle it naturally? Let interval handle it.

        # Update main Lollms config context/prediction from binding settings ONLY if auto-set is OFF
        if not self.binding_config.config.get("auto_set_ctx_size", True):
             self.config.ctx_size = self.binding_config.config["ctx_size"]
        # Always update max_n_predict from binding config as it's not auto-detected
        self.config.max_n_predict = self.binding_config.config["max_n_predict"]

        # Info message if auto-routing is enabled
        if self.binding_config.config.get("enable_auto_routing"):
             route_models = self.binding_config.config.get('auto_route_models', '')
             self.info(f"Auto-routing enabled. Will use 'model=auto' and route between: [{route_models}]")


    def build_model(self, model_name: Optional[str] = None) -> LLMBinding:
        """
        Sets up the binding for the selected model or auto-routing.
        Fetches models if needed, initializes the OpenAI client.
        """
        super().build_model(model_name) # Sets self.config.model_name from argument or config

        api_key = self._get_api_key()
        if not api_key:
            self.error("Requesty API key not found in configuration or environment variables. Binding will not function.")
            if self.lollmsCom: self.lollmsCom.InfoMessage("Requesty Error: API Key is missing. Please configure it in the binding settings.")
            self.openai_client = None
            return self # Return self to allow potential recovery if key is added later

        base_url = self.binding_config.config.get("override_api_url", DEFAULT_CONFIG["override_api_url"])
        if not is_valid_url(base_url):
             self.error(f"Invalid API URL configured: {base_url}. Using default.")
             base_url = DEFAULT_CONFIG["override_api_url"]

        try:
            self.openai_client = OpenAI(
                base_url=base_url,
                api_key=api_key,
                # Can add timeout, max_retries here if needed
            )
            # Optional: Test connection with a simple call like listing models (requires key for some endpoints)
            # self.openai_client.models.list() # This might incur cost or fail depending on Requesty implementation
            ASCIIColors.success("OpenAI client initialized for Requesty API.")
        except Exception as e:
            self.error(f"Failed to initialize OpenAI client for Requesty: {e}")
            trace_exception(e)
            self.openai_client = None
            if self.lollmsCom: self.lollmsCom.InfoMessage("Requesty Error: Failed to initialize API client.")
            return self

        # Fetch models if needed
        self._fetch_models_if_needed()

        # Find metadata for the currently selected model (unless auto-routing is enabled)
        self.current_model_metadata = None
        current_model_name = self.config.model_name
        effective_ctx_size = self.binding_config.config["ctx_size"] # Start with manual/default

        if not self.binding_config.config.get("enable_auto_routing", False):
            if not current_model_name:
                self.warning("No model selected and auto-routing is disabled.")
            elif self.models_data:
                found = False
                for model in self.models_data:
                    # Requesty uses 'id' for the model identifier (e.g., "google/gemini-pro")
                    if model.get('id') == current_model_name:
                        self.current_model_metadata = model
                        found = True
                        ASCIIColors.info(f"Found metadata for selected model: {current_model_name}")
                        break
                if not found:
                    self.warning(f"Selected model '{current_model_name}' not found in fetched list. Using default settings.")
            else:
                self.warning("Models list not available. Cannot verify selected model or set context size automatically.")

            # Set context size based on config and fetched data
            if self.binding_config.config.get("auto_set_ctx_size", True) and self.current_model_metadata:
                 detected_ctx = self.current_model_metadata.get("context_length")
                 if detected_ctx and isinstance(detected_ctx, int) and detected_ctx > 0:
                      effective_ctx_size = detected_ctx
                      ASCIIColors.success(f"Auto-detected context size: {effective_ctx_size}")
                 else:
                      ASCIIColors.warning(f"Could not auto-detect context size for {current_model_name}. Using manual/default: {effective_ctx_size}")
            else:
                 ASCIIColors.info(f"Using manually configured context size: {effective_ctx_size}")
        else:
            ASCIIColors.info("Auto-routing enabled. Context size determined by the routed model at runtime. Displayed context size is a placeholder.")
            # When auto-routing, context size isn't fixed. We use the manual/default as a placeholder for UI.
            effective_ctx_size = self.binding_config.config["ctx_size"]

        # Update effective context size in main config
        self.config.ctx_size = effective_ctx_size
        # Max n predict is always manual/config based
        self.config.max_n_predict = self.binding_config.config["max_n_predict"]

        # Determine Binding Type based on selected model (if not auto-routing) or assume TEXT_IMAGE if auto includes vision
        self.binding_type = BindingType.TEXT_ONLY # Default
        self.SAFE_STORE_SUPPORTED_FILE_EXTENSIONS=[]
        if self.binding_config.config.get("enable_auto_routing"):
             # Assume potential for vision if auto-routing is on
             self.binding_type = BindingType.TEXT_IMAGE
             self.SAFE_STORE_SUPPORTED_FILE_EXTENSIONS=['.png', '.jpg', '.jpeg', '.webp', '.gif']
             ASCIIColors.info("Auto-routing enabled, assuming potential for Vision capabilities.")
        elif self.current_model_metadata:
             architecture = self.current_model_metadata.get("architecture")
             modalities = architecture.get("input_modalities", [])
             if "image" in modalities:
                  self.binding_type = BindingType.TEXT_IMAGE
                  self.SAFE_STORE_SUPPORTED_FILE_EXTENSIONS=['.png', '.jpg', '.jpeg', '.webp', '.gif']
                  ASCIIColors.info(f"Model {current_model_name} supports vision.")
             else:
                  ASCIIColors.info(f"Model {current_model_name} is text-only.")

        ASCIIColors.success(f"Requesty binding built successfully. Model: {current_model_name or 'Auto-Routing'}. Context: {self.config.ctx_size}. Max Output: {self.config.max_n_predict}")
        return self

    def install(self):
        super().install()
        # Use pipmaster if available, otherwise use subprocess
        req_file = binding_path / "requirements.txt"
        if not req_file.exists():
             self.error("requirements.txt not found in binding directory.")
             return

        try:
            self.ShowBlockingMessage("Installing Requesty requirements (openai, requests)...")
            if 'pipmaster' in sys.modules:
                 import pipmaster as pm
                 if not pm.is_installed("openai>=1.0.0"): pm.install("openai>=1.0.0")
                 if not pm.is_installed("requests"): pm.install("requests")
            else:
                 subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "--no-cache-dir", "-r", str(req_file)], check=True)
            self.HideBlockingMessage()
            ASCIIColors.success("Installed successfully")
            ASCIIColors.info("----------------------")
            ASCIIColors.info("Attention:")
            ASCIIColors.info("----------------------")
            ASCIIColors.info("The Requesty binding uses the Requesty API.")
            ASCIIColors.info("1. Create an account at https://app.requesty.ai/")
            ASCIIColors.info("2. Generate an API key.")
            ASCIIColors.info("3. Provide the key in the binding settings or set the REQUESTY_API_KEY environment variable.")
        except subprocess.CalledProcessError as e:
             self.error(f"Installation failed: {e}")
             trace_exception(e)
             self.HideBlockingMessage()
        except Exception as e:
            self.error(f"An unexpected error occurred during installation: {e}")
            trace_exception(e)
            self.HideBlockingMessage()

    def tokenize(self, prompt: str) -> List[int]:
        """
        Tokenizes the given prompt.
        NOTE: Requesty uses different tokenizers depending on the model.
              Accurate client-side tokenization is not possible.
              This function returns an estimate based on character count / 4.

        Args:
            prompt: The text prompt to tokenize.

        Returns:
            A list of token IDs (estimated).
        """
        # ASCIIColors.warning("Requesty tokenization varies by model. Returning character count / 4 as a rough estimate.")
        # Simple estimate: average token length is around 4 chars
        return prompt.split(" ") # Return dummy range for length

    def detokenize(self, tokens_list: List[int]) -> str:
        """
        Detokenizes the given list of tokens.
        NOTE: As tokenization is approximate, detokenization is not supported.

        Args:
            tokens_list: A list of token IDs (estimated).

        Returns:
            An empty string.
        """
        return " ".join(tokens_list)

    def embed(self, text: Union[str, List[str]]) -> Optional[List[List[float]]]:
        """
        Computes text embeddings using an Requesty embedding model.

        Args:
            text: The text (str) or list of texts (List[str]) to embed.

        Returns:
            A list of embedding lists, or None if an error occurs.
        """
        if not self.openai_client:
            self.error("Requesty client not initialized. Cannot compute embeddings.")
            return None

        # Find a suitable embedding model from the fetched list
        # Prioritize known good ones like text-embedding-ada-002 if available via Requesty
        # Or let the user select an embedding model specifically?
        # For now, hardcode a common one often available via Requesty
        embedding_model_id = "openai/text-embedding-ada-002" # Check Requesty model list for alternatives
        found_embedding_model = False
        if self.models_data:
            for model in self.models_data:
                if model.get("id") == embedding_model_id:
                    found_embedding_model = True
                    break
        if not found_embedding_model:
             # Fallback or find another? Example: sentence-transformers/all-mpnet-base-v2
             alt_embedding_model = "sentence-transformers/all-mpnet-base-v2" # Example
             found_alt = False
             if self.models_data:
                  for model in self.models_data:
                     if model.get("id") == alt_embedding_model:
                         embedding_model_id = alt_embedding_model
                         found_alt = True
                         break
             if not found_alt:
                  self.error(f"Could not find a suitable default embedding model ({embedding_model_id} or {alt_embedding_model}) on Requesty. Cannot compute embeddings.")
                  return None


        try:
            input_texts = [text] if isinstance(text, str) else text
            if not isinstance(input_texts, list) or not all(isinstance(t, str) for t in input_texts):
                 self.error(f"Invalid input type for embedding: {type(text)}. Expected str or list[str].")
                 return None

            self.info(f"Computing embeddings using Requesty model: {embedding_model_id}")
            response = self.openai_client.embeddings.create(
                input=input_texts,
                model=embedding_model_id
                # Dimensions parameter might be supported by some OR models
            )

            if response.data:
                 embeddings_sorted = sorted(response.data, key=lambda e: e.index)
                 return [e.embedding for e in embeddings_sorted]
            else:
                 self.error("Embedding API returned no data.")
                 return None
        except openai.AuthenticationError:
             self.error("Authentication Error: Invalid Requesty API key for embeddings.")
             return None
        except openai.NotFoundError:
             self.error(f"Embedding model '{embedding_model_id}' not found or not accessible via your Requesty key.")
             return None
        except openai.APIError as api_ex:
             self.error(f"Requesty API Error during embedding: {api_ex}")
             trace_exception(api_ex)
             return None
        except Exception as e:
            self.error(f"Failed to compute embedding: {e}")
            trace_exception(e)
            return None


    def _prepare_single_turn_messages(self, prompt:str, images: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """ Helper to create the messages list for a single user turn with optional images. """
        content = []
        if prompt:
            content.append({"type": "text", "text": prompt})

        if images:
            processed_image_count = 0
            max_image_width = self.binding_config.config.get("max_image_width", -1)
            for image_path_str in images:
                valid_image_path = find_first_available_file_path([Path(image_path_str)])
                if not valid_image_path or not is_file_path(valid_image_path) or not valid_image_path.exists():
                     self.warning(f"Image path not found or invalid: {image_path_str}. Skipping.")
                     continue
                try:
                    encoded_image = encode_image(str(valid_image_path), max_image_width)
                    if encoded_image:
                        content.append({
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{encoded_image}"
                                # Requesty/OpenAI API doesn't typically use 'detail' here
                            }
                        })
                        processed_image_count += 1
                    else:
                         self.warning(f"Could not encode image: {valid_image_path}")
                except Exception as img_ex:
                     self.error(f"Error processing image {valid_image_path}: {img_ex}")
                     trace_exception(img_ex)

            if processed_image_count == 0 and not prompt:
                 self.error("Cannot generate response with empty prompt and no valid images.")
                 return [] # Return empty list to indicate failure

        return [{"role": "user", "content": content}]

    def _estimate_tokens(self, text: str) -> int:
        """ Rough token estimation (char count / 4). """
        if not text: return 0
        return max(1, int(len(text) / 4)) # Ensure at least 1 token if text exists

    def _update_costs(self, prompt_tokens: int, completion_tokens: int):
         """ Updates cost estimates based on token counts and model pricing. """
         if not self.binding_config.config.get("turn_on_cost_estimation"):
              return

         input_cost = 0.0
         output_cost = 0.0
         model_id = "auto" if self.binding_config.config.get("enable_auto_routing") else self.config.model_name

         if self.current_model_metadata and not self.binding_config.config.get("enable_auto_routing"):
              # Use specific model pricing if available and not auto-routing
              pricing = self.current_model_metadata.get("pricing")
              # Prices are per *million* tokens, convert to per token
              prompt_price_per_m = float(pricing.get("prompt", 0.0))
              completion_price_per_m = float(pricing.get("completion", 0.0))
              input_cost = prompt_tokens * (prompt_price_per_m / 1_000_000)
              output_cost = completion_tokens * (completion_price_per_m / 1_000_000)
              # TODO: Add image input cost if pricing info is available
         else:
              # Fallback or auto-routing: Use average or default pricing?
              # This is highly speculative. Let's use a very rough average if auto-routing.
              # For now, just log that cost estimation is less accurate for auto-routing.
              if self.binding_config.config.get("enable_auto_routing"):
                  self.warning("Cost estimation is less accurate with auto-routing enabled.")
              # Use zero cost if no pricing found or using fallback
              input_cost = 0.0
              output_cost = 0.0

         self.binding_config.config["total_input_tokens"] += prompt_tokens
         self.binding_config.config["total_output_tokens"] += completion_tokens
         self.binding_config.config["total_input_cost"] += input_cost
         self.binding_config.config["total_output_cost"] += output_cost
         self.binding_config.config["total_cost"] = self.binding_config.config["total_input_cost"] + self.binding_config.config["total_output_cost"]

         cost_info = f'Accumulated cost (estimate): ${self.binding_config.config["total_cost"]:.6f}'
         self.info(cost_info)
         self.binding_config.save() # Save updated costs


    def generate(self,
                 prompt: str,
                 n_predict: Optional[int] = None,
                 callback: Optional[Callable[[str, int], bool]] = None,
                 verbose: bool = False,
                 **generation_params) -> str:
        """
        Generates text using the Requesty API.

        Args:
            prompt: The text prompt.
            n_predict: Optional override for the maximum number of tokens to generate.
            callback: An optional callback function for streaming results.
            verbose: If True, prints more detailed information.
            **generation_params: Additional parameters for the API call.

        Returns:
            The generated text response.
        """
        # This method primarily handles text generation.
        # It will call generate_with_images if the selected model supports images,
        # but it's cleaner to have generate_with_images handle the image logic.
        # Let's simplify this to always call generate_with_images, passing images=None.
        return self.generate_with_images(prompt, images=None, n_predict=n_predict, callback=callback, verbose=verbose, **generation_params)


    def generate_with_images(self,
                             prompt: str,
                             images: Optional[List[str]] = None,
                             n_predict: Optional[int] = None,
                             callback: Optional[Callable[[str, int], bool]] = None,
                             verbose: bool = False,
                             **generation_params) -> str:
        """
        Generates text using the Requesty API, optionally including images.

        Args:
            prompt: The text prompt.
            images: A list of paths to image files (optional).
            n_predict: Optional override for the maximum number of tokens to generate.
            callback: An optional callback function for streaming results.
            verbose: If True, prints more detailed information.
            **generation_params: Additional parameters for the API call.

        Returns:
            The generated text response.
        """
        if not self.openai_client:
            self.error("Requesty client not initialized.")
            if callback: callback("Error: Requesty client not initialized.", MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_EXCEPTION)
            return ""

        # --- Parameter Preparation ---
        effective_max_n_predict = self.config.max_n_predict
        if n_predict is not None:
             if 0 < n_predict:
                 effective_max_n_predict = n_predict
                 # We don't cap here based on config.max_n_predict anymore,
                 # let the API handle potential errors if it exceeds model limits.
                 if verbose: ASCIIColors.verbose(f"Using user-provided n_predict: {effective_max_n_predict}")
             # else: n_predict <= 0 or invalid, use config default
        if verbose: ASCIIColors.verbose(f"Effective max_tokens for this generation: {effective_max_n_predict}")

        # Combine default binding config with runtime params for generation
        api_params: Dict[str, Any] = {
            "temperature": self.binding_config.config.get("temperature", DEFAULT_CONFIG["temperature"]),
            "top_p": self.binding_config.config.get("top_p", DEFAULT_CONFIG["top_p"]),
            "presence_penalty": self.binding_config.config.get("presence_penalty", DEFAULT_CONFIG["presence_penalty"]),
            "frequency_penalty": self.binding_config.config.get("frequency_penalty", DEFAULT_CONFIG["frequency_penalty"]),
            "seed": self.binding_config.config.get("seed", DEFAULT_CONFIG["seed"]),
            # Add other relevant params like stop sequences if needed from main config
            # 'stop': self.config.stop_sequences
        }
        # Override with any generation_params passed at runtime
        api_params.update(generation_params)

        # --- Prepare Messages ---
        messages = self._prepare_single_turn_messages(prompt, images)
        if not messages: # Error during message prep
             if callback: callback("Error preparing messages (no prompt or valid images).", MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_EXCEPTION)
             return ""

        # --- Determine Model for Payload ---
        payload_model: str
        payload_models_list: Optional[List[str]] = None
        if self.binding_config.config.get("enable_auto_routing", False):
            payload_model = "auto"
            route_models_str = self.binding_config.config.get('auto_route_models', '')
            payload_models_list = [m.strip() for m in route_models_str.split(',') if m.strip()]
            if not payload_models_list:
                 self.error("Auto-routing enabled, but no models specified in 'auto_route_models'. Aborting.")
                 if callback: callback("Error: Auto-routing enabled, but model list is empty.", MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_EXCEPTION)
                 return ""
            if verbose: ASCIIColors.verbose(f"Auto-routing enabled. Model='auto', routing list: {payload_models_list}")
        else:
            payload_model = self.config.model_name
            if not payload_model:
                 self.error("No model selected and auto-routing is disabled. Aborting.")
                 if callback: callback("Error: No model selected.", MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_EXCEPTION)
                 return ""
            if verbose: ASCIIColors.verbose(f"Using selected model: {payload_model}")


        # --- Construct Payload ---
        payload: Dict[str, Any] = {
            "model": payload_model,
            "messages": messages,
            "max_tokens": effective_max_n_predict,
            "stream": True, # Always stream if callback is possible
            # Add other params, converting types as needed
            "temperature": float(api_params["temperature"]),
            "top_p": float(api_params["top_p"]),
        }
        # Add optional parameters only if they differ from defaults or have meaningful values
        if float(api_params["presence_penalty"]) != 0.0: payload["presence_penalty"] = float(api_params["presence_penalty"])
        if float(api_params["frequency_penalty"]) != 0.0: payload["frequency_penalty"] = float(api_params["frequency_penalty"])
        if int(api_params["seed"]) != -1: payload["seed"] = int(api_params["seed"])
        if payload_models_list: payload["models"] = payload_models_list # For auto-routing

        # Add stop sequences if provided
        stop_sequences = api_params.get('stop')
        if stop_sequences:
            if isinstance(stop_sequences, str): stop_sequences = [stop_sequences]
            if isinstance(stop_sequences, list) and all(isinstance(s, str) for s in stop_sequences):
                 payload["stop"] = stop_sequences
            else:
                 self.warning(f"Invalid stop sequence format ignored: {stop_sequences}")

        # --- Cost Estimation (Input) ---
        estimated_prompt_tokens = self._estimate_tokens(prompt)
        # TODO: Add estimate for image tokens? Very difficult. Ignore for now.

        output = ""
        start_time = perf_counter()
        try:
            if verbose: ASCIIColors.verbose(f"Calling Requesty Chat Completions API. Payload: {json.dumps(payload, indent=2)}")

            chat_completion_stream = self.openai_client.chat.completions.create(**payload)

            stream_finished = False
            metadata = {}
            for chunk in chat_completion_stream:
                if verbose: ASCIIColors.verbose(f"Stream chunk received: {chunk}")
                chunk_text = chunk.choices[0].delta.content if chunk.choices and chunk.choices[0].delta else None
                finish_reason = chunk.choices[0].finish_reason

                if chunk_text:
                    output += chunk_text
                    if callback:
                        if not callback(chunk_text, MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_ADD_CHUNK):
                            self.info("Generation stopped by callback.")
                            stream_finished = True
                            break # Stop processing stream

                if finish_reason:
                    metadata["finish_reason"] = finish_reason
                    if verbose: ASCIIColors.verbose(f"Finish reason received: {finish_reason}")
                    stream_finished = True
                    # Usage stats are not typically in the stream for OpenAI protocol
                    break # End loop once finished

            if not stream_finished:
                 self.info("Stream ended without explicit finish reason.")
            if stream_finished and callback:
                 final_status = f"Generation finished: {metadata.get('finish_reason', 'Unknown')}"
                 self.info(final_status)


        # --- Exception Handling ---
        except openai.AuthenticationError as e: self.error(f"Authentication Error: {e}"); trace_exception(e); callback(f"Authentication Error: {e}", MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_EXCEPTION) if callback else None; return ""
        except openai.RateLimitError as e: self.error(f"Rate limit exceeded: {e}"); trace_exception(e); callback(f"Rate limit exceeded: {e}", MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_EXCEPTION) if callback else None; return ""
        except openai.BadRequestError as e: self.error(f"API Bad Request Error: {e}. Check model compatibility, parameters, or image format."); trace_exception(e); callback(f"API Bad Request: {e}", MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_EXCEPTION) if callback else None; return ""
        except openai.NotFoundError as e: self.error(f"Model not found or API endpoint error: {e}"); trace_exception(e); callback(f"API Error (NotFound): {e}", MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_EXCEPTION) if callback else None; return ""
        except openai.APIError as e: self.error(f'Requesty API Error: {e}'); trace_exception(e); callback(f"API Error: {e}", MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_EXCEPTION) if callback else None; return ""
        except Exception as e: self.error(f'Error during generation: {e}'); trace_exception(e); callback(f"Error: {e}", MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_EXCEPTION) if callback else None; return ""
        finally:
            generation_time = perf_counter() - start_time
            ASCIIColors.info(f"Generation process finished in {generation_time:.2f} seconds.")


        # --- Cost Estimation (Output) ---
        # Note: We don't get accurate token counts from the API stream easily.
        # We rely on our rough estimation.
        estimated_output_tokens = self._estimate_tokens(output)
        self._update_costs(estimated_prompt_tokens, estimated_output_tokens)


        return output


    def list_models(self) -> List[str]:
        """Lists the available models fetched from the API."""
        self._fetch_models_if_needed()
        if not self.models_data:
             self.error("Could not fetch or load models from Requesty.")
             return []
        # Return the 'id' field which Requesty uses
        return sorted([model.get('id', '') for model in self.models_data if model.get('id')])


    def get_available_models(self, app: Optional[LoLLMsCom] = None) -> List[dict]:
        """Gets the available models list formatted for the LoLLMs UI."""
        self._fetch_models_if_needed()
        if not self.models_data:
             self.error("Could not fetch or load models from Requesty for UI.")
             if self.lollmsCom: self.lollmsCom.InfoMessage("Requesty Error: Failed to fetch model list.")
             return []

        models_info: List[Dict[str, Any]] = []
        ui_path_prefix = f"/bindings/{binding_folder_name}/"
        default_icon = ui_path_prefix + "logo.png" # Assumes logo.png exists

        for model in self.models_data:
            model_id = model.get("id")
            if not model_id: continue # Skip entries without an ID

            name = model.get("name", model_id) # Use display name if available
            # Requesty's /v1/models uses 'context_window' (fallback to OpenAI-style 'context_length')
            ctx = model.get("context_window", model.get("context_length", 0)) or 0
            # Requesty's /v1/models does not expose per-token pricing; guard defensively.
            pricing = model.get("pricing") or {}
            prompt_cost = float(pricing.get("prompt", 0.0)) * 1_000_000 # Cost per million tokens
            completion_cost = float(pricing.get("completion", 0.0)) * 1_000_000
            # Requesty exposes capability flags (supports_vision, etc.) rather than an
            # 'architecture' object; build a modalities list from those flags defensively.
            architecture = model.get("architecture") or {}
            modalities = architecture.get("input_modalities", [])
            if not modalities and model.get("supports_vision"):
                modalities = ["image"]
            description = model.get("description", f"Requesty model: {name}")

            # Determine Category & Rank (simple heuristics)
            category = "text"
            rank = 2.0 # Default rank
            if "image" in modalities: category = "multimodal"; rank += 0.5
            if ctx >= 128000: rank += 1.5
            elif ctx >= 32000: rank += 1.0
            elif ctx >= 8000: rank += 0.5
            if "gpt-4" in model_id.lower(): rank += 1.0
            elif "claude-3" in model_id.lower(): rank += 0.9
            elif "gemini" in model_id.lower(): rank += 0.8
            elif "mistral" in model_id.lower() or "mixtral" in model_id.lower(): rank += 0.6
            elif "llama-3" in model_id.lower(): rank += 0.7
            # Adjust rank based on cost? Lower cost = slightly higher rank?
            avg_cost = (prompt_cost + completion_cost) / 2
            if avg_cost == 0: rank += 0.3 # Free models are good value
            elif avg_cost < 0.5: rank += 0.2 # Cheap models
            elif avg_cost < 2.0: rank += 0.1 # Moderate cost

            # --- Build Lollms Model Dictionary ---
            model_entry = {
                "id": model_id, # Add id for potential future use
                "name": model_id, # Use ID as the unique key for selection
                "display_name": name,
                "description": description,
                "ctx_size": ctx if ctx > 0 else -1, # Use -1 for unknown/0
                "category": category,
                "rank": rank,
                "icon": default_icon, # Use default icon for all
                "author": model_id.split('/')[0] if '/' in model_id else "Unknown", # Extract author from ID
                "license": "Proprietary/API", # General assumption
                "model_creator": model_id.split('/')[0] if '/' in model_id else "Unknown",
                "model_creator_link": "https://app.requesty.ai/models/"+model_id if '/' in model_id else "https://requesty.ai/",
                "type": "api",
                "binding_name": binding_name,
                # Variants can represent the model itself, including pricing info
                "variants": [{
                    "name": model_id, # Variant name is the model ID itself
                    "size": ctx, # Use context size as proxy for size
                    "prompt_cost_per_million": prompt_cost,
                    "completion_cost_per_million": completion_cost,
                }]
            }
            models_info.append(model_entry)

        # Sort models: by rank (desc), then by name (asc)
        models_info.sort(key=lambda x: (-x['rank'], x['name']))

        ASCIIColors.success(f"Formatted {len(models_info)} Requesty models for Lollms UI.")
        return models_info


# --- Main execution block for testing ---
if __name__ == "__main__":
    from lollms.paths import LollmsPaths
    from lollms.main_config import LOLLMSConfig
    from lollms.app import LollmsApplication
    from pathlib import Path
    import sys

    print("Initializing LoLLMs environment for testing...")
    lollms_paths = LollmsPaths.find_paths(force_local=True, tool_prefix="test_requesty_")
    config = LOLLMSConfig.autoload(lollms_paths)
    try:
        lollms_app = LollmsApplication("TestApp", config, lollms_paths, load_bindings=False, load_personalities=False, load_models=False)
        lollms_com = lollms_app.com
    except Exception as e:
        print(f"Couldn't instantiate LollmsApplication (might be normal in CI): {e}")
        lollms_com = None

    print("Creating Requesty binding instance...")
    orouter = Requesty(config, lollms_paths, installation_option=InstallOption.INSTALL_IF_NECESSARY, lollmsCom=lollms_com)

    # --- API Key Setup ---
    api_key_found = False
    if orouter._get_api_key():
        print("API Key found in config or environment.")
        api_key_found = True
    else:
        try:
            if sys.stdin.isatty(): # Check if running interactively
                key_input = input("Enter Requesty API Key for testing: ").strip()
                if key_input:
                    orouter.binding_config.config["requesty_key"] = key_input
                    # Don't save to permanent config during testing
                    print("API Key set for this session.")
                    api_key_found = True
                else:
                    print("No API key provided.")
            else:
                print("Running in non-interactive mode. Skipping API key input.")
                print("Ensure REQUESTY_API_KEY environment variable is set for tests.")
        except EOFError:
            print("No API key input detected.")

    if not api_key_found:
         print("API key not found. Skipping tests that require API access.")
         sys.exit(1) # Exit if no key for testing

    # --- Fetch models ---
    print("\nFetching models...")
    orouter._fetch_models_if_needed()
    available_models = orouter.list_models()

    if available_models:
        print(f"\nAvailable Requesty Models ({len(available_models)} found):")
        limit = 15
        if len(available_models) > limit:
            for m in available_models[:limit//2]: print(f"- {m}")
            print("  ...")
            for m in available_models[-limit//2:]: print(f"- {m}")
        else:
            for m in available_models: print(f"- {m}")

        # --- Test Setup ---
        # Select a specific model for some tests
        # Use a cheap/free one if possible
        test_model_specific = "mistralai/mistral-7b-instruct:free"
        if test_model_specific not in available_models:
            print(f"\nWarning: Preferred specific test model '{test_model_specific}' not found. Trying 'google/gemini-flash-1.5'.")
            test_model_specific = "google/gemini-flash-1.5"
            if test_model_specific not in available_models:
                 print(f"\nWarning: Model '{test_model_specific}' not found. Using first available model: {available_models[0] if available_models else 'None'}")
                 if available_models: test_model_specific = available_models[0]
                 else: test_model_specific = None

        # Define a callback function for testing
        def print_callback(chunk: str, msg_type: int, metadata: dict) -> bool:
            type_str = MSG_OPERATION_TYPE(msg_type).name if msg_type in MSG_OPERATION_TYPE.__members__.values() else f"UNKNOWN({msg_type})"
            if msg_type == MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_ADD_CHUNK:
                print(chunk, end="", flush=True)
            elif msg_type == MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_EXCEPTION:
                 print(f"\n## [{type_str}] EXCEPTION: {chunk} ##")
                 return False # Stop on error
            # You can add more handlers here if needed (e.g., for FULL_ANSWER, STEP_END)
            # else:
            #     print(f"\n--- [{type_str}] ---\n{chunk}\nMetadata: {metadata}\n--- End ---")
            return True

        if test_model_specific:
             # --- Test Case 1: Standard Chat (Specific Model) ---
             print("\n" + "="*20 + " Test 1: Standard Chat (Specific Model) " + "="*20)
             orouter.binding_config.config["enable_auto_routing"] = False # Disable auto-routing
             config.model_name = test_model_specific # Set in main config
             orouter.build_model() # Build for the specific model

             prompt1 = "Explain the concept of vector databases in two sentences."
             print(f"Using model: {test_model_specific}")
             print(f"Prompt: {prompt1}")
             print("Response Stream:")
             try:
                 response1 = orouter.generate(prompt1, n_predict=150, callback=print_callback, verbose=True)
                 print("\n-- Test 1 Complete --")
             except Exception as e: print(f"\nTest 1 failed: {e}"); trace_exception(e)

        else:
             print("\nSkipping Test 1 as no specific test model could be determined.")


        # --- Test Case 2: Auto-Routing Enabled ---
        print("\n" + "="*20 + " Test 2: Auto-Routing Enabled " + "="*20)
        orouter.binding_config.config["enable_auto_routing"] = True
        # Use the default auto_route_models or specify others
        # Example: orouter.binding_config.config["auto_route_models"] = "openai/gpt-4o-mini,google/gemini-flash-1.5"
        orouter.settings_updated() # Apply the change
        orouter.build_model() # Rebuild to reflect auto-routing status

        prompt2 = "What is the capital of France?"
        print(f"Using auto-routing. Models: [{orouter.binding_config.config['auto_route_models']}]")
        print(f"Prompt: {prompt2}")
        print("Response Stream:")
        try:
            # No need to set config.model_name when auto-routing
            response2 = orouter.generate(prompt2, n_predict=50, callback=print_callback, verbose=True)
            print("\n-- Test 2 Complete --")
        except Exception as e: print(f"\nTest 2 failed: {e}"); trace_exception(e)
        finally:
             orouter.binding_config.config["enable_auto_routing"] = False # Disable for next tests if any
             orouter.settings_updated()

        # --- Test Case 3: Vision Model (if available) ---
        print("\n" + "="*20 + " Test 3: Vision Input " + "="*20)
        # Find a vision model (e.g., gpt-4o, claude-3-haiku, gemini-pro-vision)
        vision_model_id = None
        potential_vision = ["openai/gpt-4o", "google/gemini-pro-vision", "anthropic/claude-3-haiku-20240307"]
        for vm in potential_vision:
            if vm in available_models:
                 # Double check modalities from fetched data
                 md = next((m for m in orouter.models_data if m.get('id') == vm), None)
                 if md and "image" in md.get("architecture").get("input_modalities",[]):
                     vision_model_id = vm
                     break

        if vision_model_id:
            orouter.binding_config.config["enable_auto_routing"] = False
            config.model_name = vision_model_id
            orouter.build_model()
            print(f"Using vision model: {vision_model_id}")

            # Create a dummy image file for testing
            dummy_image_path = lollms_paths.personal_outputs_path / "test_or_image.png"
            try:
                from PIL import Image, ImageDraw
                img = Image.new('RGB', (80, 40), color = 'cyan')
                d = ImageDraw.Draw(img)
                d.text((10,10), "OR Test", fill='black')
                img.save(dummy_image_path)
                print(f"Created dummy image: {dummy_image_path}")

                prompt3 = "Describe this image in detail."
                images3 = [str(dummy_image_path)]
                print(f"Prompt: {prompt3}")
                print(f"Image: {images3[0]}")
                print("Response Stream:")
                try:
                    response3 = orouter.generate_with_images(prompt3, images3, n_predict=100, callback=print_callback, verbose=True)
                    print("\n-- Test 3 Complete --")
                except Exception as e: print(f"\nTest 3 failed: {e}"); trace_exception(e)
                finally:
                    if dummy_image_path.exists(): dummy_image_path.unlink()

            except ImportError:
                print("PIL/Pillow not installed. Skipping image creation and vision test.")
            except Exception as e:
                 print(f"Error during image creation/test: {e}")
        else:
             print(f"-- Test 3 Skipped (No suitable vision model found among {potential_vision}) --")

        # --- Test Case 4: Cost Estimation Check ---
        print("\n" + "="*20 + " Test 4: Cost Estimation Check " + "="*20)
        orouter.binding_config.config["turn_on_cost_estimation"] = True
        # Use the specific model again for more predictable pricing (if available)
        if test_model_specific:
             orouter.binding_config.config["enable_auto_routing"] = False
             config.model_name = test_model_specific
             orouter.build_model()

             prompt4 = "Tell me a very short joke."
             print(f"Using model: {test_model_specific}")
             print(f"Prompt: {prompt4}")
             print("Generating...")
             try:
                 response4 = orouter.generate(prompt4, n_predict=50, callback=None, verbose=False) # Non-streaming, non-verbose
                 print("Response Received.")
                 print(f"Final Accumulated Cost (estimate): ${orouter.binding_config.config['total_cost']:.8f}")
                 print(f"Total Input Tokens (estimate): {orouter.binding_config.config['total_input_tokens']}")
                 print(f"Total Output Tokens (estimate): {orouter.binding_config.config['total_output_tokens']}")
                 print("\n-- Test 4 Complete --")
             except Exception as e: print(f"\nTest 4 failed: {e}"); trace_exception(e)
        else:
             print("-- Test 4 Skipped (No specific model available for cost test) --")
        # Disable cost estimation after test
        orouter.binding_config.config["turn_on_cost_estimation"] = False


    else:
        print("\nCould not retrieve model list from Requesty. Check API status or network connection.")
        print("Skipping tests.")

    print("\nScript finished.")