# -*- coding: utf-8 -*-
# File: lollms_openvideogen.py
# Author: ParisNeo
# Description: LoLLMs binding for the OpenVideoGen API (v0.5.0+ compatible)
# Date: 10/04/2025

import requests
import time
from typing import List, Optional, Dict, Any
from pathlib import Path
import base64 # To potentially send image data if needed, though path is preferred
import io

from lollms.app import LollmsApplication
from lollms.main_config import LOLLMSConfig
from lollms.config import TypedConfig, ConfigTemplate, BaseConfig
from lollms.utilities import find_next_available_filename
from lollms.ttv import LollmsTTV # Keep inheriting for type hinting and structure
from ascii_colors import ASCIIColors, trace_exception
import json # For parsing JSON responses

class LollmsOpenVideoGenClient(LollmsTTV):
    """
    Lollms binding for the OpenVideoGen API (v0.5.0+).
    Supports Text-to-Video and Image-to-Video generation with job polling
    and status updates reflecting model loading and resource waiting states.
    """

    def __init__(
            self,
            app: LollmsApplication,
            output_folder: str | Path = None,
            config: TypedConfig = None, # Allow passing config for advanced use cases
            **kwargs # Accept arbitrary keyword arguments
    ):
        # Define service configuration template
        config_template = ConfigTemplate([
            {"name": "api_url", "type": "str", "value": "http://localhost:8088", "help": "URL of the OpenVideoGen FastAPI server"},
            {"name": "t2v_model_name", "type": "str", "value": "", "options": [], "help": "Default Text-to-Video model (fetched dynamically)"},
            {"name": "i2v_model_name", "type": "str", "value": "", "options": [], "help": "Default Image-to-Video model (fetched dynamically)"},
            {"name": "timeout", "type": "int", "value": 1200, "help": "Timeout for API requests in seconds (increased for potential loading/waiting)"}, # Increased timeout
            {"name": "poll_interval", "type": "int", "value": 3, "help": "Interval in seconds to poll job status"}, # Slightly faster polling
        ])

        # Set default values
        base_config_defaults = {
            "api_url": "http://localhost:8088",
            "t2v_model_name": "", # Will be set after fetching models
            "i2v_model_name": "", # Will be set after fetching models
            "timeout": 1200,
            "poll_interval": 3,
        }

        # Initialize the TypedConfig
        # If a config is passed, use it, otherwise create a new one
        service_config = config if config else TypedConfig(
            config_template,
            BaseConfig(config=base_config_defaults)
        )

        super().__init__("openvideogen", app, service_config, output_folder)

        # Fetch available models and separate them
        self.all_models_info: List[Dict[str, Any]] = []
        self.available_t2v_models: List[str] = []
        self.available_i2v_models: List[str] = []
        self.fetch_and_update_models() # Initial fetch

    def fetch_and_update_models(self):
        """Fetches model info from the server and updates local lists and config options."""
        ASCIIColors.info("Fetching available models from OpenVideoGen server...")
        try:
            response = requests.get(f"{self.service_config.api_url}/models", timeout=15) # Moderate timeout
            response.raise_for_status()
            data = response.json()
            self.all_models_info = data.get("models", [])

            self.available_t2v_models = [m["id"] for m in self.all_models_info if m.get("task") == "Text-to-Video"]
            self.available_i2v_models = [m["id"] for m in self.all_models_info if m.get("task") == "Image-to-Video"]

            # Update config template options
            self.service_config.config_template["t2v_model_name"]["options"] = self.available_t2v_models
            self.service_config.config_template["i2v_model_name"]["options"] = self.available_i2v_models

            # Set default if current selection is invalid or empty
            if not self.service_config.t2v_model_name or self.service_config.t2v_model_name not in self.available_t2v_models:
                if self.available_t2v_models:
                    self.service_config.t2v_model_name = self.available_t2v_models[0]
                    ASCIIColors.warning(f"Default T2V model reset to {self.service_config.t2v_model_name}")
                else:
                    self.service_config.t2v_model_name = "" # No models available
                    ASCIIColors.warning("No Text-to-Video models available from the server.")

            if not self.service_config.i2v_model_name or self.service_config.i2v_model_name not in self.available_i2v_models:
                if self.available_i2v_models:
                    self.service_config.i2v_model_name = self.available_i2v_models[0]
                    ASCIIColors.warning(f"Default I2V model reset to {self.service_config.i2v_model_name}")
                else:
                    self.service_config.i2v_model_name = "" # No models available
                    ASCIIColors.warning("No Image-to-Video models available from the server.")

            ASCIIColors.success(f"Found {len(self.available_t2v_models)} T2V and {len(self.available_i2v_models)} I2V models.")

        except requests.exceptions.RequestException as e:
            ASCIIColors.error(f"Failed to connect or fetch models from OpenVideoGen server at {self.service_config.api_url}: {e}")
            self.all_models_info = []
            self.available_t2v_models = []
            self.available_i2v_models = []
        except Exception as e:
            trace_exception(e)
            ASCIIColors.error(f"An error occurred while processing models: {e}")
            self.all_models_info = []
            self.available_t2v_models = []
            self.available_i2v_models = []

    def settings_updated(self):
        """Called when settings are updated. Refetch models."""
        self.fetch_and_update_models()

    def _wait_for_job_completion(self, job_id: str, output_folder: Path, output_file_name: Optional[str] = None) -> str:
        """Polls the job status until completion and downloads the video."""
        output_path = Path(output_folder) if output_folder else self.output_folder
        output_path.mkdir(exist_ok=True, parents=True)
        last_reported_status = None

        while True:
            try:
                status_response = requests.get(
                    f"{self.service_config.api_url}/status/{job_id}",
                    timeout=self.service_config.timeout # Use longer timeout for status check too
                )
                status_response.raise_for_status()
                status_data = status_response.json()

                job_status = status_data.get("status")
                progress = status_data.get("progress", 0)
                message = status_data.get("message", "")

                # Report status change distinctly
                if job_status != last_reported_status:
                    ASCIIColors.info(f"Job {job_id} status updated: {job_status} - {message}")
                    last_reported_status = job_status
                elif job_status == "processing": # Report progress if processing
                    ASCIIColors.info(f"Job {job_id} status: {job_status}, Progress: {progress}% - {message}")
                # else: # Reduce noise for other statuses like waiting
                #     ASCIIColors.debug(f"Job {job_id} status: {job_status}, Progress: {progress}% - {message}")


                if job_status == "completed":
                    ASCIIColors.info(f"Job {job_id} completed. Downloading video...")
                    download_url = f"{self.service_config.api_url}/download/{job_id}"
                    video_response = requests.get(download_url, timeout=self.service_config.timeout)
                    video_response.raise_for_status()

                    if output_file_name:
                        output_filename = output_path / output_file_name
                    else:
                        # Use a safe name based on job ID initially
                        safe_filename = f"video_{job_id}.mp4"
                        output_filename = find_next_available_filename(output_path, safe_filename)

                    with open(output_filename, "wb") as f:
                        f.write(video_response.content)
                    ASCIIColors.success(f"Video downloaded successfully to {output_filename}")
                    return str(output_filename)

                elif job_status == "failed":
                    ASCIIColors.error(f"Job {job_id} failed: {message}")
                    raise RuntimeError(f"Job {job_id} failed: {message}")

                # Continue polling if pending, waiting, loading, or processing
                time.sleep(self.service_config.poll_interval)

            except requests.exceptions.Timeout:
                ASCIIColors.warning(f"Polling job {job_id} timed out. Retrying...")
                time.sleep(self.service_config.poll_interval * 2) # Wait longer after timeout
            except requests.exceptions.RequestException as e:
                ASCIIColors.error(f"Connection error while polling job {job_id}: {str(e)}")
                raise RuntimeError(f"Connection error polling job {job_id}: {e}")
            except Exception as e:
                ASCIIColors.error(f"Unexpected error while polling job {job_id}: {str(e)}")
                raise

    def generate_video(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        model_name: Optional[str] = None, # Allow override
        height: Optional[int] = None, # Use None for default
        width: Optional[int] = None,
        steps: Optional[int] = None,
        guidance_scale: Optional[float] = None,
        seed: int = -1,
        nb_frames: Optional[int] = None,
        fps: Optional[int] = None,
        output_folder: Optional[str | Path] = None,
        output_file_name: Optional[str] = None,
    ) -> str:
        """
        Submits a Text-to-Video generation job and waits for completion.

        Args:
            prompt (str): The text prompt.
            negative_prompt (Optional[str]): Negative prompt.
            model_name (Optional[str]): Specific T2V model to use. Defaults to config.
            height (Optional[int]): Video height. Uses API default if None.
            width (Optional[int]): Video width. Uses API default if None.
            steps (Optional[int]): Inference steps. Uses API default if None.
            guidance_scale (Optional[float]): Guidance scale. Uses API default if None.
            seed (int): Random seed (-1 for random).
            nb_frames (Optional[int]): Number of frames. Uses API default if None.
            fps (Optional[int]): Frames per second. Uses API default if None.
            output_folder (Optional[str | Path]): Output directory.
            output_file_name (Optional[str]): Output filename.

        Returns:
            str: Path to the generated video file.

        Raises:
            ValueError: If no T2V model is selected or available.
            RuntimeError: If the generation job fails.
        """
        final_output_folder = Path(output_folder) if output_folder else self.output_folder
        selected_model = model_name if model_name else self.service_config.t2v_model_name

        if not selected_model:
            raise ValueError("No Text-to-Video model selected or available in configuration.")
        if selected_model not in self.available_t2v_models:
             # Check if it's maybe an I2V model requested by mistake
             if selected_model in self.available_i2v_models:
                 raise ValueError(f"Model '{selected_model}' is an Image-to-Video model. Use generate_video_from_image for it.")
             else:
                 raise ValueError(f"Selected Text-to-Video model '{selected_model}' is not available on the server.")

        # Prepare the request payload, omitting None values so API uses defaults
        payload = {
            "prompt": prompt,
            "seed": seed, # Always include seed
            "model_name": selected_model,
        }
        if negative_prompt is not None: payload["negative_prompt"] = negative_prompt
        if height is not None: payload["height"] = height
        if width is not None: payload["width"] = width
        if steps is not None: payload["steps"] = steps
        if guidance_scale is not None: payload["guidance_scale"] = guidance_scale
        if nb_frames is not None: payload["nb_frames"] = nb_frames
        if fps is not None: payload["fps"] = fps

        # Submit the job
        try:
            ASCIIColors.info(f"Submitting T2V job with model {selected_model}...")
            ASCIIColors.debug(f"Payload: {json.dumps(payload)}") # Log payload
            response = requests.post(
                f"{self.service_config.api_url}/submit",
                json=payload,
                timeout=self.service_config.timeout
            )
            response.raise_for_status()
            result = response.json()
            job_id = result.get("job_id")
            if not job_id:
                raise ValueError("No job ID returned from the server.")
            ASCIIColors.success(f"T2V Job submitted successfully: {job_id}")

            # Wait for completion and download
            return self._wait_for_job_completion(job_id, final_output_folder, output_file_name)

        except requests.exceptions.RequestException as e:
            ASCIIColors.error(f"Failed to submit T2V job: {str(e)}")
            raise RuntimeError(f"Failed to submit T2V job: {e}")
        except Exception as e:
            ASCIIColors.error(f"Failed during T2V generation: {str(e)}")
            raise # Re-raise other exceptions like ValueError or RuntimeError

    def generate_video_from_image(
        self,
        image_path: str | Path,
        model_name: Optional[str] = None, # Allow override
        height: Optional[int] = None,
        width: Optional[int] = None,
        fps: Optional[int] = None,
        motion_bucket_id: Optional[int] = None,
        noise_aug_strength: Optional[float] = None,
        seed: int = -1,
        num_inference_steps: Optional[int] = None, # Corresponds to 'steps' in some UIs
        prompt: Optional[str] = None, # Optional conditioning prompt
        output_folder: Optional[str | Path] = None,
        output_file_name: Optional[str] = None,
    ) -> str:
        """
        Submits an Image-to-Video generation job and waits for completion.

        Args:
            image_path (str | Path): Path to the input image file.
            model_name (Optional[str]): Specific I2V model to use. Defaults to config.
            height (Optional[int]): Video height. Uses API default if None.
            width (Optional[int]): Video width. Uses API default if None.
            fps (Optional[int]): Frames per second. Uses API default if None.
            motion_bucket_id (Optional[int]): SVD motion amount. Uses API default if None.
            noise_aug_strength (Optional[float]): SVD noise augmentation. Uses API default if None.
            seed (int): Random seed (-1 for random).
            num_inference_steps (Optional[int]): Inference steps. Uses API default if None.
            prompt (Optional[str]): Optional text prompt for conditioning.
            output_folder (Optional[str | Path]): Output directory.
            output_file_name (Optional[str]): Output filename.

        Returns:
            str: Path to the generated video file.

        Raises:
            FileNotFoundError: If the image path is invalid.
            ValueError: If no I2V model is selected or available.
            RuntimeError: If the generation job fails.
        """
        final_output_folder = Path(output_folder) if output_folder else self.output_folder
        selected_model = model_name if model_name else self.service_config.i2v_model_name

        if not selected_model:
            raise ValueError("No Image-to-Video model selected or available in configuration.")
        if selected_model not in self.available_i2v_models:
             if selected_model in self.available_t2v_models:
                 raise ValueError(f"Model '{selected_model}' is a Text-to-Video model. Use generate_video for it.")
             else:
                raise ValueError(f"Selected Image-to-Video model '{selected_model}' is not available on the server.")

        image_path = Path(image_path)
        if not image_path.is_file():
            raise FileNotFoundError(f"Input image not found at: {image_path}")

        # Prepare form data payload (key-value pairs, excluding the file itself)
        form_data = {
            "seed": seed, # Always include seed
            "model_name": selected_model,
        }
        if height is not None: form_data["height"] = height
        if width is not None: form_data["width"] = width
        if fps is not None: form_data["fps"] = fps
        if motion_bucket_id is not None: form_data["motion_bucket_id"] = motion_bucket_id
        if noise_aug_strength is not None: form_data["noise_aug_strength"] = noise_aug_strength
        if num_inference_steps is not None: form_data["num_inference_steps"] = num_inference_steps
        if prompt is not None: form_data["prompt"] = prompt
        # decode_chunk_size is usually handled by the API default

        # Prepare files dictionary for the image upload
        try:
            with open(image_path, 'rb') as f:
                files = {'image': (image_path.name, f.read(), File_InfosLoader.get_mime_type(str(image_path)))}
                ASCIIColors.info(f"Submitting I2V job with model {selected_model} and image {image_path.name}...")
                ASCIIColors.debug(f"Form data: {json.dumps({k: v for k, v in form_data.items()})} ") # Log form data

                # Submit the job using multipart/form-data
                response = requests.post(
                    f"{self.service_config.api_url}/submit_image_video",
                    data=form_data, # Form fields go in 'data'
                    files=files,    # File upload goes in 'files'
                    timeout=self.service_config.timeout
                )
                response.raise_for_status()
                result = response.json()
                job_id = result.get("job_id")
                if not job_id:
                    raise ValueError("No job ID returned from the server.")
                ASCIIColors.success(f"I2V Job submitted successfully: {job_id}")

                # Wait for completion and download
                return self._wait_for_job_completion(job_id, final_output_folder, output_file_name)

        except FileNotFoundError: # Already checked, but as safeguard
             raise
        except requests.exceptions.RequestException as e:
            ASCIIColors.error(f"Failed to submit I2V job: {str(e)}")
            raise RuntimeError(f"Failed to submit I2V job: {e}")
        except Exception as e:
            ASCIIColors.error(f"Failed during I2V generation: {str(e)}")
            raise # Re-raise other exceptions

    def generate_video_by_frames(
        self,
        prompts: List[str],
        frames: List[int],
        model_name: Optional[str] = None, # Allow override
        negative_prompt: Optional[str] = None,
        height: Optional[int] = None,
        width: Optional[int] = None,
        fps: Optional[int] = None,
        num_inference_steps: Optional[int] = None,
        guidance_scale: Optional[float] = None,
        seed: Optional[int] = None,
        output_folder: Optional[str | Path] = None,
        output_file_name: Optional[str] = None,
    ) -> str:
        """
        Submits a multi-prompt T2V job and waits for completion.

        Args:
            prompts (List[str]): List of prompts.
            frames (List[int]): Frames per prompt.
            model_name (Optional[str]): Specific T2V model. Defaults to config.
            negative_prompt (Optional[str]): Negative prompt.
            height (Optional[int]): Video height. Uses API default if None.
            width (Optional[int]): Video width. Uses API default if None.
            fps (Optional[int]): Frames per second. Uses API default if None.
            num_inference_steps (Optional[int]): Steps. Uses API default if None.
            guidance_scale (Optional[float]): Guidance. Uses API default if None.
            seed (Optional[int]): Random seed.
            output_folder (Optional[str | Path]): Output directory.
            output_file_name (Optional[str]): Output filename.

        Returns:
            str: Path to the generated video file.
        """
        final_output_folder = Path(output_folder) if output_folder else self.output_folder
        selected_model = model_name if model_name else self.service_config.t2v_model_name

        if not selected_model:
            raise ValueError("No Text-to-Video model selected/available for multi-prompt.")
        if selected_model not in self.available_t2v_models:
             if selected_model in self.available_i2v_models:
                 raise ValueError(f"Model '{selected_model}' is I2V. Multi-prompt endpoint only supports T2V.")
             else:
                 raise ValueError(f"Selected T2V model '{selected_model}' not available.")
        if not prompts or not frames or len(prompts) != len(frames):
            raise ValueError("Prompts and frames lists must be non-empty and equal length.")

        # Prepare payload, omitting None values
        payload = {
            "prompts": prompts,
            "frames": frames,
            "model_name": selected_model,
        }
        if negative_prompt is not None: payload["negative_prompt"] = negative_prompt
        if height is not None: payload["height"] = height
        if width is not None: payload["width"] = width
        if fps is not None: payload["fps"] = fps
        if num_inference_steps is not None: payload["num_inference_steps"] = num_inference_steps
        if guidance_scale is not None: payload["guidance_scale"] = guidance_scale
        if seed is not None: payload["seed"] = seed # Send seed if provided

        # Submit the multi-prompt job
        try:
            ASCIIColors.info(f"Submitting multi-prompt T2V job with model {selected_model}...")
            ASCIIColors.debug(f"Payload: {json.dumps(payload)}")
            response = requests.post(
                f"{self.service_config.api_url}/submit_multi",
                json=payload,
                timeout=self.service_config.timeout
            )
            response.raise_for_status()
            result = response.json()
            job_id = result.get("job_id")
            if not job_id: raise ValueError("No job ID returned from server.")
            ASCIIColors.success(f"Multi-prompt job submitted: {job_id}")

            # Wait for completion
            return self._wait_for_job_completion(job_id, final_output_folder, output_file_name)

        except requests.exceptions.RequestException as e:
            ASCIIColors.error(f"Failed to submit multi-prompt job: {str(e)}")
            raise RuntimeError(f"Failed to submit multi-prompt job: {e}")
        except Exception as e:
            ASCIIColors.error(f"Failed during multi-prompt generation: {str(e)}")
            raise

    def getModels(self, force_fetch: bool = False) -> List[str]:
        """Returns the list of all available model IDs."""
        if force_fetch or not self.all_models_info:
            self.fetch_and_update_models()
        return [m["id"] for m in self.all_models_info]

    def getT2VModels(self, force_fetch: bool = False) -> List[str]:
        """Returns the list of available Text-to-Video model IDs."""
        if force_fetch or not self.available_t2v_models:
             self.fetch_and_update_models()
        return self.available_t2v_models

    def getI2VModels(self, force_fetch: bool = False) -> List[str]:
        """Returns the list of available Image-to-Video model IDs."""
        if force_fetch or not self.available_i2v_models:
             self.fetch_and_update_models()
        return self.available_i2v_models