# File: lollms_openaigptimage.py
# Title: LollmsOpenAIGPTImage
# Licence: Apache 2.0
# Author: Paris Neo based on provided documentation and examples

from pathlib import Path
import sys
from lollms.app import LollmsApplication
from lollms.paths import LollmsPaths
from lollms.config import TypedConfig, ConfigTemplate, BaseConfig
import time
import io
import requests
import os
import base64
import json
from PIL import Image # Not strictly needed for generation, but often useful in TTI context
from typing import List, Dict, Tuple, Any

from ascii_colors import ASCIIColors, trace_exception
from lollms.paths import LollmsPaths
from lollms.utilities import PackageManager, find_next_available_filename
from lollms.tti import LollmsTTI

if not PackageManager.check_package_installed("openai"):
    PackageManager.install_package("openai")
import openai

class LollmsOpenAIGPTImage(LollmsTTI):
    def __init__(self, 
                 app: LollmsApplication, 
                 output_folder: str|Path = None, 
                 config:dict=None, # Added for consistency with LollmsService init
                 shareable_config:dict=None # Added for consistency
                 ):
        """
        Initializes the LollmsOpenAIGPTImage binding.
        Args:
            app (LollmsApplication): The LollmsApplication instance.
            output_folder (Path|str): The output folder where to put the generated data.
            config (dict): A dictionary of configuration parameters.
            shareable_config (dict): A dictionary of shareable configuration parameters.
        """
        # Get the API key from environment variables if not provided
        api_key = os.getenv("OPENAI_API_KEY", "") # More common env var for OpenAI
        
        service_config_template = ConfigTemplate([
            {"name":"api_key", "type":"str", "value":api_key, "help":"A valid OpenAI API key."},
            {"name":"model", "type":"str", "value":"gpt-4o", "options":[ "gpt-4.1-mini", "GPT-4.1-nano", "o4-mini"], "help":"The model to be used for image generation via Responses API."},
            # Add other TTI specific settings if needed, though this API is simple
            {"name":"n_images", "type":"int", "value":1, "min":1, "max":1, "help":"Number of images to generate (Currently fixed to 1 by OpenAI Responses API for image_generation tool)."},
            {"name":"width", "type":"int", "value":1024, "help":"Desired image width (Note: Actual size may be model-dependent and not guaranteed)."},
            {"name":"height", "type":"int", "value":1024, "help":"Desired image height (Note: Actual size may be model-dependent and not guaranteed)."},
        ])
        service_config = BaseConfig(config={
            "api_key": api_key,
            "model": "gpt-4o", # Default to the latest powerful model
            "n_images": 1,
            "width": 1024,
            "height": 1024,
        })

        super().__init__("openaigptimage", app, TypedConfig(service_config_template, service_config), output_folder)
        self.settings_updated() # To initialize the client if api_key is present

    def settings_updated(self):
        """
        Called when the service settings are updated.
        Reinitializes the OpenAI client if the API key has changed.
        """
        if self.service_config.api_key:
            self.client = openai.OpenAI(api_key=self.service_config.api_key)
        else:
            self.client = None
        # Any other re-initialization logic can go here

    def paint(self, 
                positive_prompt: str,
                negative_prompt: str, # Not directly supported by this API method
                sampler_name: str = "Euler", # Not supported
                seed: int = None, # Not supported
                scale: float = None, # Not supported
                steps: int = None, # Not supported
                width: int = None, # Not directly controllable, but can hint in prompt
                height: int = None, # Not directly controllable, but can hint in prompt
                output_folder: str | Path = None,
                output_file_name: str = None
                ) -> Tuple[Path | None, Dict | None]:
        """
        Generates an image based on the given positive prompt using OpenAI's Responses API.
        Negative prompt, sampler, seed, scale, steps, width, and height are not directly supported.
        Width and height can be hinted at in the prompt, e.g., "A 16:9 aspect ratio image of..."

        Args:
            positive_prompt (str): The positive prompt describing the desired image.
            negative_prompt (str): The negative prompt (ignored by this API).
            sampler_name (str): The sampler name (ignored).
            seed (int): The seed (ignored).
            scale (float): The scale (ignored).
            steps (int): The number of steps (ignored).
            width (int): Desired width (hinted, not enforced).
            height (int): Desired height (hinted, not enforced).
            output_folder (str | Path, optional): Folder to save the image. Defaults to self.output_folder.
            output_file_name (str, optional): Name for the output file. Defaults to an auto-generated name.

        Returns:
            Tuple[Path | None, Dict | None]: Path to the saved image and metadata, or (None, error_dict) on failure.
        """
        if not self.client:
            ASCIIColors.error("OpenAI client not initialized. Please set the API key in the settings.")
            return None, {"error": "OpenAI client not initialized. API key missing."}

        if output_folder is None:
            output_folder = self.output_folder
        else:
            output_folder = Path(output_folder)
        
        output_folder.mkdir(parents=True, exist_ok=True)

        # Inform user about unsupported parameters
        unsupported_params = []
        if negative_prompt: unsupported_params.append("negative_prompt")
        if sampler_name != "Euler": unsupported_params.append("sampler_name") # Default is often ignored
        if seed is not None: unsupported_params.append("seed")
        if scale is not None: unsupported_params.append("scale")
        if steps is not None: unsupported_params.append("steps")
        
        # Construct a more descriptive prompt if width/height are provided
        # The API itself doesn't take w/h, but some models might interpret it from text.
        final_prompt = positive_prompt
        if width and height:
            # Try to hint aspect ratio or size. This is speculative.
            final_prompt += f" (Image dimensions: {width}x{height})"
            if width != self.service_config.width or height != self.service_config.height:
                 unsupported_params.append("width/height (Note: only passed as text hint, actual size model dependent)")
        elif self.service_config.width and self.service_config.height:
            # Use configured default width/height for the hint if not overridden
            final_prompt += f" (Image dimensions: {self.service_config.width}x{self.service_config.height})"


        if unsupported_params:
            self.app.InfoMessage(f"Warning: The following parameters are not directly supported by the OpenAI GPT Image generation (Responses API) and will be ignored or only used as text hints: {', '.join(unsupported_params)}")

        try:
            self.app.ShowBlockingMessage("Generating image with OpenAI GPT...")
            response = self.client.responses.create(
                model=self.service_config.model,
                input=final_prompt.strip(),
                tools=[{"type": "image_generation"}],
            )

            image_base64_data = None
            for output in response.output:
                if output.type == "image_generation_call":
                    image_base64_data = output.result
                    break
            
            self.app.HideBlockingMessage()

            if image_base64_data:
                if output_file_name:
                    if not output_file_name.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                        file_name = output_folder / f"{output_file_name}.png" # Default to PNG
                    else:
                        file_name = output_folder / output_file_name
                else:
                    file_name = output_folder / find_next_available_filename(output_folder, "openaigptimg_", extension="png")

                with open(file_name, "wb") as f:
                    f.write(base64.b64decode(image_base64_data))
                
                ASCIIColors.green(f"Image saved to {file_name}")
                return file_name, {"positive_prompt": positive_prompt, "model": self.service_config.model, "final_prompt_sent": final_prompt}
            else:
                ASCIIColors.error("No image data found in OpenAI response.")
                error_msg = "No image data found in OpenAI response."
                if response.output:
                    error_msg += f" Response output: {response.output}"
                return None, {"error": error_msg, "positive_prompt": positive_prompt}

        except openai.APIConnectionError as e:
            ASCIIColors.error(f"OpenAI API connection error: {e}")
            self.app.HideBlockingMessage()
            return None, {"error": f"APIConnectionError: {e}", "positive_prompt": positive_prompt}
        except openai.RateLimitError as e:
            ASCIIColors.error(f"OpenAI API rate limit exceeded: {e}")
            self.app.HideBlockingMessage()
            return None, {"error": f"RateLimitError: {e}", "positive_prompt": positive_prompt}
        except openai.APIStatusError as e:
            json_start = e.message.find('{')
            json_string = e.message[json_start:]
            msg = json.loads(json_string)
            error_message = f"OpenAI API status error: {e.status_code} - {e.response} - {msg}"
            ASCIIColors.error(error_message)
            self.app.HideBlockingMessage()
            self.app.InfoMessage(error_message)
            return None, {"error": f"APIStatusError: {e.status_code} - {e.response}", "positive_prompt": positive_prompt}
        except Exception as e:
            trace_exception(e)
            self.app.HideBlockingMessage()
            return None, {"error": str(e), "positive_prompt": positive_prompt}

    def paint_from_images(self, 
                            positive_prompt: str, 
                            images: List[str], 
                            negative_prompt: str = "",
                            # Add other LollmsTTI params if needed by base class signature
                            sampler_name="Euler",
                            seed=None,
                            scale=None,
                            steps=None,
                            width=None,
                            height=None,
                            output_folder=None,
                            output_file_name=None
                            ) -> Tuple[Path | None, Dict | None]:
        """
        Image-to-image generation is not directly supported by the OpenAI 'responses.create'
        API with the 'image_generation' tool in the way DALL-E 2's variations/edits work.
        This method will indicate that it's not implemented.
        """
        self.app.InfoMessage("Image-to-image generation (variations/edits) is not supported by this specific OpenAI GPT Image (Responses API) binding. Use the DALL-E binding for such features if available.")
        ASCIIColors.warning("paint_from_images called, but not implemented for LollmsOpenAIGPTImage using Responses API.")
        return None, {"error": "Image-to-image not supported by this OpenAI endpoint/model combination using Responses API."}

    @staticmethod
    def verify(app: LollmsApplication) -> bool:
        """
        Verifies if the TTI service is available.
        For OpenAI, this primarily means checking if the openai package is installed.
        API key validity is checked at runtime.
        """
        return PackageManager.check_package_installed("openai")

    @staticmethod
    def install(app: LollmsApplication) -> bool:
        """
        Installs the necessary components for the TTI service.
        For OpenAI, this means installing the openai package.
        """
        return PackageManager.install_package("openai")
    
    @staticmethod 
    def get(app: LollmsApplication, config:dict=None, shareable_config:dict=None) -> 'LollmsOpenAIGPTImage':
        """
        Returns an instance of the LollmsOpenAIGPTImage class.
        """
        return LollmsOpenAIGPTImage(app, config=config, shareable_config=shareable_config)


if __name__ == "__main__":
    # This is a basic test script, requires a LollmsApplication mock or instance
    # and an environment variable OPENAI_API_KEY to be set.
    
    # Mock LollmsApplication for testing
    class MockLollmsApplication:
        def __init__(self):
            self.lollms_paths = LollmsPaths() # Requires lollms_paths to be valid
            self.config = BaseConfig() # Mock config
            self.mounted_services = []

        def InfoMessage(self, msg):
            ASCIIColors.blue(f"App Info: {msg}")

        def ShowBlockingMessage(self, msg):
            ASCIIColors.yellow(f"App Blocking: {msg}")
        
        def HideBlockingMessage(self):
            ASCIIColors.yellow(f"App Unblocked")

    # Ensure OPENAI_API_KEY is set in your environment for this test
    if not os.getenv("OPENAI_API_KEY"):
        print("Please set the OPENAI_API_KEY environment variable to run this test.")
    else:
        app = MockLollmsApplication()
        # Create a temporary output folder for testing
        test_output_folder = Path(__file__).parent / "test_openaigptimage_output"
        test_output_folder.mkdir(exist_ok=True, parents=True)

        print(f"Attempting to initialize LollmsOpenAIGPTImage...")
        try:
            tti_service = LollmsOpenAIGPTImage(app, output_folder=test_output_folder)
            
            if tti_service.client:
                print("LollmsOpenAIGPTImage initialized successfully.")
                
                prompt = "A photorealistic image of a futuristic cityscape at sunset, with flying cars and neon lights."
                print(f"\nAttempting to generate image for prompt: '{prompt}'")
                
                file_path, metadata = tti_service.paint(
                    positive_prompt=prompt,
                    negative_prompt="ugly, blurry", # Will be ignored
                    width=1024, 
                    height=576 # Will be hinted
                )
                
                if file_path:
                    print(f"Image generation successful: {file_path}")
                    print(f"Metadata: {metadata}")
                else:
                    print(f"Image generation failed. Metadata: {metadata}")

                print("\nAttempting paint_from_images (expected to be not supported):")
                file_path_img2img, metadata_img2img = tti_service.paint_from_images(
                    positive_prompt="Make this cat wear a party hat",
                    images=["some_dummy_image_path.png"] # This path won't be used
                )
                if file_path_img2img is None:
                    print("paint_from_images correctly reported as not supported.")
                    print(f"Metadata: {metadata_img2img}")
                else:
                    print("paint_from_images unexpectedly produced an image (this shouldn't happen).")

            else:
                print("Failed to initialize LollmsOpenAIGPTImage client (likely API key issue).")

        except Exception as e:
            print(f"An error occurred during testing: {e}")
            trace_exception(e)
