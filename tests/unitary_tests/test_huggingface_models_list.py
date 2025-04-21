#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import time
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Set, Dict, Any
import types
import pprint
import traceback

# --- Dependencies Check ---
try:
    from huggingface_hub import HfApi
except ImportError:
    print("ERROR: huggingface_hub library not found.")
    print("Please install it: pip install huggingface_hub")
    sys.exit(1)

# --- Constants and Mock Definitions ---

# Simulate constants/globals from the original environment
HF_LOCAL_MODELS_DIR = "hf"  # Directory inside personal_models_path for HF models
binding_folder_name = "hf_binding" # Example binding folder name
binding_name = "hf_binding" # Example binding name

# Mock LoLLMsCom methods (logging) - Can be enhanced if needed
class MockLoLLMsCom:
    def info(self, msg: str):
        print(f"INFO: {msg}")

    def warning(self, msg: str):
        print(f"WARN: {msg}")

    def error(self, msg: str):
        print(f"ERROR: {msg}")

# Mock LoLLMsPaths
class MockLoLLMsPaths:
    def __init__(self, temp_dir: Path):
        # Simulate the path where models are stored
        self.personal_models_path = Path(temp_dir)

# Mock BindingConfig
class MockBindingConfig:
    def __init__(self, config_dict: Optional[Dict[str, Any]] = None):
        self.config = config_dict or {}
        # Provide defaults similar to the original code's usage
        self.config.setdefault("hub_fetch_limit", 50) # Smaller limit for testing
        self.config.setdefault("model_sorting", "trending_score") # or 'downloads', 'lastModified'

# Mock trace_exception (simple version)
def trace_exception(e: Exception):
    print(f"TRACE: An exception occurred: {type(e).__name__}: {e}")
    # traceback.print_exc() # Uncomment for full traceback

# Mock ASCIIColors (simple version)
class MockASCIIColors:
    @staticmethod
    def success(msg: str):
        print(f"SUCCESS: {msg}")

    @staticmethod
    def warning(msg: str):
        print(f"WARNING: {msg}")

    @staticmethod
    def error(msg: str):
        print(f"ERROR: {msg}")

ASCIIColors = MockASCIIColors() # Use the mock

# --- The Class Containing the Method to Test ---

class TestHFBinding:
    """
    A test class mimicking the structure where get_available_models lives.
    """
    def __init__(self, lollms_paths: MockLoLLMsPaths, binding_config: MockBindingConfig, local_models: List[str]):
        self.lollms_paths = lollms_paths
        self.binding_config = binding_config
        self._local_models = set(local_models) # Store simulated local models

        # Add mock logging methods directly to the instance
        mock_logger = MockLoLLMsCom()
        self.info = mock_logger.info
        self.warning = mock_logger.warning
        self.error = mock_logger.error

    def list_models(self) -> List[str]:
        """ Returns the list of simulated local models. """
        self.info(f"Simulating list_models(), returning: {self._local_models}")
        # We return the list passed during init, actual file presence is checked later
        return list(self._local_models)

    # --- PASTE THE get_available_models METHOD HERE ---
    def get_available_models(self, app: Optional[MockLoLLMsCom] = None) -> List[dict]:
        """ Gets available models: local + fetched from Hub. """
        # If app is provided, use its loggers, otherwise use self's loggers
        info = app.info if app else self.info
        warning = app.warning if app else self.warning
        error = app.error if app else self.error

        lollms_models = []
        local_model_names = set(self.list_models())
        local_hf_root = self.lollms_paths.personal_models_path / HF_LOCAL_MODELS_DIR
        binding_folder = binding_folder_name if binding_folder_name else binding_name
        default_icon = f"/bindings/{binding_folder.lower()}/logo.png" # Corrected path separator

        # Add Local Models
        info(f"Checking for local models in: {local_hf_root}")
        for model_name in sorted(list(local_model_names)):
            entry = {"category": "local", "datasets": "Unknown", "icon": default_icon, "last_commit_time": None,
                     "license": "Unknown", "model_creator": None, "name": model_name, "provider": None,
                     "rank": 5.0, "type": "model", "variants": [{"name": model_name + " (Local)", "size": -1}],
                     "model_creator_link": f"https://huggingface.co/{model_name.split('/')[0]}" if '/' in model_name else "https://huggingface.co/"}
            model_path = local_hf_root / model_name
            try:
                if model_path.exists(): # Check if path actually exists for stat
                    entry["last_commit_time"] = datetime.fromtimestamp(model_path.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                    info(f"Found local model '{model_name}' with mtime: {entry['last_commit_time']}")
                else:
                    warning(f"Local model '{model_name}' listed but not found at {model_path}. Cannot get timestamp.")
            except Exception as e:
                warning(f"Could not get timestamp for local model {model_name}: {e}")
            lollms_models.append(entry)

        # Fetch Models from Hub
        filtered_hub_count = 0
        try:
            info("Fetching models from Hugging Face Hub...")
            api = HfApi(); limit = self.binding_config.config.get("hub_fetch_limit", 100)
            model_iterator = api.list_models(filter=["text-generation-inference"], sort=self.binding_config.config.get("model_sorting", "trending_score"), direction=-1, limit=limit)
            hub_models_list = list(model_iterator)
            info(f"Fetched {len(hub_models_list)} models from Hub (before filtering).")

            for model in hub_models_list:
                model_id = model.modelId
                if model_id in local_model_names:
                    info(f"Skipping Hub model '{model_id}' because it's present locally.")
                    continue # Skip if already local

                # Filtering logic from the original code
                skip_keywords = ["gguf", "gptq", "awq", "ggml", "-onnx"]
                if any(kw in model_id.lower() for kw in skip_keywords):
                    # info(f"Skipping Hub model '{model_id}' due to keyword filter.") # Verbose
                    continue
                format_tags = {'gguf', 'gptq', 'awq', 'ggml'}; model_tags = set(model.tags or [])
                if format_tags.intersection(model_tags) and not {'transformers', 'pytorch'}.intersection(model_tags):
                    # info(f"Skipping Hub model '{model_id}' due to tag filter (format tag without transformer/pytorch).") # Verbose
                    continue

                # Determine category and description
                category = "hub_vision" if "image-to-text" in (model.pipeline_tag or "") else "hub_text"
                description = f"Downloads: {model.downloads or 'N/A'}" + (f", Updated: {model.lastModified.split('T')[0]}" if model.lastModified else "")

                entry = {"category": category, "datasets": "Check card", "icon": default_icon, "last_commit_time": model.lastModified,
                         "license": "Check card", "model_creator": model.author or None, "name": model_id, "provider": None,
                         "rank": 1.0 + (model.downloads / 1e7 if model.downloads else 0), "type": "downloadable", "description": description,
                         "link": f"https://huggingface.co/{model_id}", "variants": [{"name": model_id + " (Hub)", "size": -1}],
                         "model_creator_link": f"https://huggingface.co/{model.author}" if model.author else "https://huggingface.co/"}
                lollms_models.append(entry); filtered_hub_count += 1
            info(f"Added {filtered_hub_count} Hub models after filtering.")

        except ImportError: error("huggingface_hub not found.") # Should not happen due to check at start
        except Exception as e: error(f"Failed fetch Hub models: {e}"); trace_exception(e)

        # Add fallbacks if Hub fetch failed/yielded few results
        if filtered_hub_count == 0:
             warning("Hub fetch yielded zero results after filtering. Adding fallback models.")
             fallback_models = [
                 {"category": "hub_text", "name": "google/gemma-1.1-2b-it", "description":"(Fallback) Google Gemma 2B IT", "icon": default_icon, "rank": 1.5, "type":"downloadable", "variants":[{"name":"gemma-1.1-2b-it (Hub)", "size":-1}], "license": "Check card", "model_creator": "google", "model_creator_link":"https://huggingface.co/google", "last_commit_time":None},
                 {"category": "hub_text", "name": "meta-llama/Meta-Llama-3-8B-Instruct", "description":"(Fallback) Meta Llama 3 8B Instruct", "icon": default_icon, "rank": 1.4, "type":"downloadable", "variants":[{"name":"Meta-Llama-3-8B-Instruct (Hub)", "size":-1}], "license": "Check card", "model_creator": "meta-llama", "model_creator_link":"https://huggingface.co/meta-llama", "last_commit_time":None},
                 {"category": "hub_vision", "name": "google/gemma-2-9b-it", "description":"(Fallback) Google Gemma 2 9B Vision IT", "icon": default_icon, "rank": 1.6, "type":"downloadable", "variants":[{"name":"gemma-2-9b-it (Hub)", "size":-1}], "license": "Check card", "model_creator": "google", "model_creator_link":"https://huggingface.co/google", "last_commit_time":None}, # Updated fallback
                 {"category": "hub_vision", "name": "Salesforce/blip-image-captioning-large", "description":"(Fallback) Salesforce BLIP Captioning", "icon": default_icon, "rank": 1.2, "type":"downloadable", "variants":[{"name":"blip-image-captioning-large (Hub)", "size":-1}], "license": "Check card", "model_creator": "Salesforce", "model_creator_link":"https://huggingface.co/Salesforce", "last_commit_time":None},
             ]
             added_fb_count = 0
             for fm in fallback_models:
                 # Add missing default fields to fallback models for consistency
                 fm.setdefault("provider", None)
                 fm.setdefault("datasets", "Check card")
                 fm.setdefault("link", f"https://huggingface.co/{fm['name']}")

                 if fm["name"] not in local_model_names:
                    # Check if this fallback model name is already added from Hub (unlikely if count is 0, but good practice)
                    if not any(m['name'] == fm['name'] for m in lollms_models):
                        lollms_models.append(fm)
                        added_fb_count += 1

             if added_fb_count > 0: warning(f"Hub fetch failed/sparse. Added {added_fb_count} fallback examples.")

        # Sort models: local first, then rank (desc), then name (asc)
        lollms_models.sort(key=lambda x: (x.get('category') != 'local', -x.get('rank', 1.0), x['name']))
        ASCIIColors.success(f"Formatted {len(lollms_models)} models for Lollms UI.")
        return lollms_models

# --- Test Execution ---

if __name__ == "__main__":
    # 1. Configuration
    simulated_local_models = [
        "username/local-model-1",
        "another-org/local-model-2-variant",
        "microsoft/phi-3-mini-4k-instruct" # Example of a model that might also be on Hub
    ]
    test_config = {
        "hub_fetch_limit": 200, # Fetch more to test filtering
        "model_sorting": "downloads" # Try sorting by downloads
    }

    # 2. Setup Temporary Environment
    with tempfile.TemporaryDirectory() as tmpdir:
        temp_dir_path = Path(tmpdir)
        hf_models_path = temp_dir_path / HF_LOCAL_MODELS_DIR
        hf_models_path.mkdir(parents=True, exist_ok=True)
        print(f"Created temporary directory for models: {hf_models_path}")

        # Create dummy files/dirs for simulated local models to get timestamps
        for model_name in simulated_local_models:
            # HF models can be just directories containing files
            model_path = hf_models_path / model_name
            model_path.mkdir(parents=True, exist_ok=True)
            # Create a dummy file inside to give the dir a mod time
            dummy_file = model_path / "config.json"
            dummy_file.touch()
            print(f"  - Created dummy structure for local model: {model_name}")
            # Optional: sleep slightly to ensure different timestamps
            time.sleep(0.01)


        # 3. Instantiate Mocks and Test Class
        mock_paths = MockLoLLMsPaths(temp_dir_path)
        mock_config = MockBindingConfig(test_config)
        test_binding = TestHFBinding(mock_paths, mock_config, simulated_local_models)

        # Instantiate the optional app logger (or pass None)
        mock_app = MockLoLLMsCom() # Separate logger instance if needed

        print("\n--- Starting get_available_models() ---")
        # 4. Run the Method
        start_time = time.time()
        available_models = test_binding.get_available_models(app=mock_app) # Pass mock app logger
        end_time = time.time()
        print(f"--- get_available_models() finished in {end_time - start_time:.2f} seconds ---")

        # 5. Print Results
        print(f"\nTotal models retrieved: {len(available_models)}")
        print("First 5 models found:")
        pprint.pprint(available_models[:5])

        print("\nLast 5 models found:")
        pprint.pprint(available_models[-5:])

        # Example: Check if local models are present and have timestamps
        print("\nChecking local models in results:")
        local_count = 0
        for model in available_models:
            if model['category'] == 'local':
                local_count += 1
                print(f"  - Local: {model['name']}, Timestamp: {model.get('last_commit_time', 'N/A')}")
        print(f"Found {local_count} local models in the final list.")

        # Example: Check if fallback models were added (if applicable)
        if any("(Fallback)" in m.get("description", "") for m in available_models):
            print("\nFallback models were included in the list.")


    print("\n--- Test Script Finished ---")
    # Temporary directory is automatically cleaned up upon exiting the 'with' block