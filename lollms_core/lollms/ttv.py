from abc import abstractmethod
from typing import List, Optional
from lollms.app import LollmsApplication
from lollms.main_config import LOLLMSConfig
from lollms.config import TypedConfig
from lollms.utilities import find_next_available_filename
from lollms.service import LollmsSERVICE
from pathlib import Path

class LollmsTTV(LollmsSERVICE):
    """
    LollmsTTI is a base class for implementing Text-to-Image (TTI) functionalities within the LollmsApplication.
    """
    
    def __init__(
                    self,
                    name:str,
                    app: LollmsApplication,
                    service_config: TypedConfig,
                    output_folder: str|Path=None
                    ):
        """
        Initializes the LollmsTTI class with the given parameters.

        Args:
            app (LollmsApplication): The instance of the main Lollms application.
            model (str, optional): The TTI model to be used for image generation. Defaults to an empty string.
            api_key (str, optional): API key for accessing external TTI services. Defaults to an empty string.
            output_path (Path or str, optional): Path where the output image files will be saved. Defaults to None.
        """
        super().__init__(name, app, service_config)
        if output_folder is not None:
            self.output_folder = Path(output_folder)
        else:
            self.output_folder = app.lollms_paths.personal_outputs_path/name
            self.output_folder.mkdir(exist_ok=True, parents=True)



    @abstractmethod
    def generate_video(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        model_name: str = "",
        height: int = 512,
        width: int = 512,
        steps: int = 20,
        seed: int = -1,
        nb_frames: int = None,
        fps: int = 8,
        output_folder: str | Path = None,
        output_file_name = None
    ) -> str:
        """
        Generates a video from a single text prompt.

        Args:
            prompt (str): The text prompt describing the video.
            negative_prompt (Optional[str]): Text describing elements to avoid in the video. Default is None.
            model_name (str): Name of the model to use. Default is empty string.
            height (int): Height of the video in pixels. Default is 512.
            width (int): Width of the video in pixels. Default is 512.
            steps (int): Number of inference steps. Default is 20.
            seed (int): Random seed for reproducibility. Default is -1.
            nb_frames (int): Number of frames in the video. Default is None.
            fps (int): Frames per second. Default is 8.
            output_folder (str | Path): Directory to save the video. Default is None.
            output_file_name: Name of the output file. Default is None.

        Returns:
            str: The path to the generated video.
        """
        pass

    @abstractmethod
    def generate_video_by_frames(self, prompts: List[str], frames: List[int], negative_prompt: str, fps: int = 8, 
                       num_inference_steps: int = 50, guidance_scale: float = 6.0, 
                       seed: Optional[int] = None) -> str:
        """
        Generates a video from a list of prompts and corresponding frames.

        Args:
            prompts (List[str]): List of text prompts for each frame.
            frames (List[int]): List of frame indices corresponding to each prompt.
            negative_prompt (str): Text describing elements to avoid in the video.
            fps (int): Frames per second. Default is 8.
            num_inference_steps (int): Number of steps for the model to infer. Default is 50.
            guidance_scale (float): Controls how closely the model adheres to the prompt. Default is 6.0.
            seed (Optional[int]): Random seed for reproducibility. Default is None.

        Returns:
            str: The path to the generated video.
        """
        pass

    def getModels(self):
        """
        Gets the list of models
        """
        return []