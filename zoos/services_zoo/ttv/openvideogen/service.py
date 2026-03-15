import os
import time
from pathlib import Path
from typing import List, Optional
import subprocess
import sys
import torch
import pipmaster as pm


pm.install_if_missing("transformers")
pm.install_if_missing("accelerate")
pm.install_if_missing("imageio-ffmpeg")
pm.install_if_missing("sentencepiece")

if not(pm.is_version_exact("diffusers","0.32.2") or pm.is_version_higher("diffusers","0.32.2")):
    pm.install_or_update("git+https://github.com/huggingface/diffusers")

from lollms.app import LollmsApplication
from lollms.main_config import LOLLMSConfig
from lollms.config import TypedConfig, ConfigTemplate, BaseConfig
from lollms.utilities import find_next_available_filename
from lollms.ttv import LollmsTTV
from ascii_colors import ASCIIColors, trace_exception


from diffusers import CogVideoXPipeline, StableVideoDiffusionPipeline, MochiPipeline
from diffusers.utils import export_to_video

class LollmsOpenVideoGen(LollmsTTV):
    """
    LollmsOpenVideoGen is an implementation of LollmsTTV for text-to-video generation using multiple diffusion models.
    """
    
    def __init__(
            self,
            app: LollmsApplication,
            output_folder: str | Path = None
    ):
        # Define service configuration with more options
        service_config = TypedConfig(
            ConfigTemplate([
                {"name": "model_name", "type": "str", "value": "THUDM/CogVideoX-2b", "options": ["THUDM/CogVideoX-2b", "THUDM/CogVideoX-5b", "stabilityai/stable-video-diffusion-img2vid", "genmo/mochi-1-preview"], "help": "Model to use for video generation"},
                {"name": "model_type", "type": "str", "value": "cogvideox", "options": ["cogvideox", "stablevideo", "mochi"], "help": "Type of the model (cogvideox, stablevideo, mochi)"},
                {"name": "use_gpu", "type": "bool", "value": True, "help": "Use GPU if available"},
                {"name": "force_gpu", "type": "bool", "value": False, "help": "Force GPU usage (raises error if GPU not available)"},
                {"name": "dtype", "type": "str", "value": "float16", "options": ["float16", "bfloat16"], "help": "Data type for model precision"},
                {"name": "guidance_scale", "type": "float", "value": 6.0, "help": "Guidance scale for generation"},
                {"name": "num_inference_steps", "type": "int", "value": 50, "help": "Number of inference steps"},
                {"name": "nb_frames", "type": "int", "value": 49, "help": "Number of frames in the video"},
                {"name": "fps", "type": "int", "value": 8, "help": "Frames per second"},
                {"name": "height", "type": "int", "value": 480, "help": "Height of the video"},
                {"name": "width", "type": "int", "value": 720, "help": "Width of the video"},
            ]),
            BaseConfig(config={
                "model_name": "THUDM/CogVideoX-2b",
                "model_type": "cogvideox",
                "use_gpu": True,
                "force_gpu": False,
                "dtype": "float16",
                "guidance_scale": 6.0,
                "num_inference_steps": 50,
                "nb_frames": 49,
                "fps": 8,
                "height": 480,
                "width": 720,
            })
        )
        super().__init__("openvideogen", app, service_config, output_folder)

        # Initialize pipeline
        self.pipeline = None
        self.load_pipeline()

    def load_pipeline(self):
        """Loads or reloads the pipeline based on config."""
        try:
            if self.service_config.force_gpu and not torch.cuda.is_available():
                raise RuntimeError("force_gpu is set to True, but no GPU is available.")

            dtype = torch.float16 if self.service_config.dtype == "float16" else torch.bfloat16
            model_type = self.service_config.model_type

            if model_type == "cogvideox":
                self.pipeline = CogVideoXPipeline.from_pretrained(
                    self.service_config.model_name,
                    torch_dtype=dtype
                )
            elif model_type == "stablevideo":
                self.pipeline = StableVideoDiffusionPipeline.from_pretrained(
                    self.service_config.model_name,
                    torch_dtype=dtype
                )
            elif model_type == "mochi":
                self.pipeline = MochiPipeline.from_pretrained(
                    self.service_config.model_name,
                    torch_dtype=dtype
                )
                self.pipeline.enable_vae_tiling()  # Memory optimization for Mochi
            else:
                raise ValueError(f"Unsupported model type: {model_type}")

            if self.service_config.force_gpu or (self.service_config.use_gpu and torch.cuda.is_available()):
                self.pipeline.to("cuda")
                self.pipeline.enable_model_cpu_offload()  # Optimize VRAM usage
                ASCIIColors.success("Running on GPU with model CPU offloading enabled.")
            else:
                ASCIIColors.warning("GPU not available or disabled. Running on CPU (slower).")

            ASCIIColors.success(f"Loaded model: {self.service_config.model_name} ({model_type})")
        except Exception as e:
            trace_exception(e)
            self.app.error(f"Failed to load pipeline: {str(e)}")

    def settings_updated(self):
        """Reloads the pipeline if settings change."""
        self.load_pipeline()

    def generate_video(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        model_name: str = "",
        model_type: str = "",
        height: int = None,
        width: int = None,
        steps: int = None,
        guidance_scale: float = None,
        seed: int = -1,
        nb_frames: int = None,
        fps: int = None,
        output_folder: str | Path = None,
        output_file_name: str = None,
    ) -> str:
        """
        Generates a video from a text prompt using the selected model.

        Args:
            prompt (str): The text prompt describing the video content.
            negative_prompt (Optional[str]): Ignored (not supported by all models).
            model_name (str): Overrides config model if provided (optional).
            model_type (str): Overrides config model type if provided (optional).
            height (int): Desired height of the video (default from config).
            width (int): Desired width of the video (default from config).
            steps (int): Number of inference steps (default from config).
            guidance_scale (float): Guidance scale (default from config).
            seed (int): Random seed (default -1 for random).
            nb_frames (int): Number of frames (default from config).
            fps (int): Frames per second (default from config).
            output_folder (str | Path): Optional custom output directory.
            output_file_name (str): Optional custom output file name.

        Returns:
            str: Path to the generated video file.
        """
        output_path = Path(output_folder) if output_folder else self.output_folder
        output_path.mkdir(exist_ok=True, parents=True)

        # Update model if specified
        if model_name and model_name != self.service_config.model_name:
            ASCIIColors.warning(f"Overriding config model {self.service_config.model_name} with {model_name}")
            self.service_config.model_name = model_name
            self.load_pipeline()
        if model_type and model_type != self.service_config.model_type:
            ASCIIColors.warning(f"Overriding config model type {self.service_config.model_type} with {model_type}")
            self.service_config.model_type = model_type
            self.load_pipeline()

        # Use config defaults if parameters are not provided
        height = height if height is not None else self.service_config.height
        width = width if width is not None else self.service_config.width
        steps = steps if steps is not None else self.service_config.num_inference_steps
        guidance_scale = guidance_scale if guidance_scale is not None else self.service_config.guidance_scale
        nb_frames = nb_frames if nb_frames is not None else self.service_config.nb_frames
        fps = fps if fps is not None else self.service_config.fps

        # Handle unsupported parameters
        if negative_prompt:
            ASCIIColors.warning("Warning: Negative prompts are not supported by all models. Ignoring negative_prompt.")

        # Generation parameters
        gen_params = {
            "prompt": prompt,
            "num_frames": nb_frames,
            "num_inference_steps": steps,
            "guidance_scale": guidance_scale,
            "height": height,
            "width": width,
        }
        if seed != -1:
            device = "cuda" if (self.service_config.force_gpu or self.service_config.use_gpu) else "cpu"
            gen_params["generator"] = torch.Generator(device=device).manual_seed(seed)

        # Generate video
        try:
            ASCIIColors.info(f"Generating video with {self.service_config.model_name} ({self.service_config.model_type})...")
            start_time = time.time()

            # Special handling for Mochi model
            if self.service_config.model_type == "mochi" and (self.service_config.force_gpu or self.service_config.use_gpu):
                with torch.autocast("cuda", dtype=torch.bfloat16, cache_enabled=False):
                    video_frames = self.pipeline(**gen_params).frames[0]
            else:
                video_frames = self.pipeline(**gen_params).frames[0]

            # Determine output filename
            if output_file_name is None:
                output_filename = find_next_available_filename(output_path, "openvideogen_output_", ".mp4")
            else:
                output_filename = output_path / output_file_name

            export_to_video(video_frames, str(output_filename), fps=fps)
            elapsed_time = time.time() - start_time
            ASCIIColors.success(f"Video generated and saved to {output_filename} in {elapsed_time:.2f} seconds")
        except Exception as e:
            raise RuntimeError(f"Failed to generate video: {str(e)}")

        return str(output_filename)

    def generate_video_by_frames(
        self,
        prompts: List[str],
        frames: List[int],
        negative_prompt: str = None,
        fps: int = None,
        num_inference_steps: int = None,
        guidance_scale: float = None,
        seed: Optional[int] = None
    ) -> str:
        """
        Generates a video from a list of prompts. Concatenates prompts into a single description.

        Args:
            prompts (List[str]): List of prompts for each segment.
            frames (List[int]): Number of frames per segment (summed to total frames).
            negative_prompt (str): Ignored.
            fps (int): Frames per second (default from config).
            num_inference_steps (int): Inference steps (default from config).
            guidance_scale (float): Guidance scale (default from config).
            seed (Optional[int]): Random seed.

        Returns:
            str: Path to the generated video file.
        """
        if not prompts or not frames:
            raise ValueError("Prompts and frames lists cannot be empty.")
        
        # Combine prompts into a single narrative
        combined_prompt = " ".join(prompts)
        total_frames = sum(frames)
        
        return self.generate_video(
            prompt=combined_prompt,
            negative_prompt=negative_prompt,
            steps=num_inference_steps,
            guidance_scale=guidance_scale,
            seed=seed if seed is not None else -1,
            nb_frames=total_frames,
            fps=fps
        )

    def getModels(self):
        """Returns available models."""
        return [
            "THUDM/CogVideoX-2b",
            "THUDM/CogVideoX-5b",
            "stabilityai/stable-video-diffusion-img2vid",
            "genmo/mochi-1-preview"
        ]