import datetime
from lollms.app import LollmsApplication
from lollms.personality import AIPersonality
from lollms.function_call import FunctionCall, FunctionType
from lollms.prompting import LollmsContextDetails
from datetime import datetime
from typing import List, Optional, Dict, Any
from lollms.utilities import discussion_path_to_url
from lollms.client_session import Client
from lollms.personality import APScript
from ascii_colors import trace_exception
from lollms.config import TypedConfig, ConfigTemplate, BaseConfig


def build_negative_prompt(image_generation_prompt: str, llm: LollmsApplication):
    start_header_id_template    = llm.config.start_header_id_template
    end_header_id_template      = llm.config.end_header_id_template
    system_message_template     = llm.config.system_message_template        

    return "\n".join([
                    f"{start_header_id_template}{system_message_template}{end_header_id_template}",
                    f"{llm.config.negative_prompt_generation_prompt}",
                    f"{start_header_id_template}image_generation_prompt{end_header_id_template}",
                    f"{image_generation_prompt}",
                    f"{start_header_id_template}negative_prompt{end_header_id_template}",
                ])    

def build_video(
    app: LollmsApplication,
    prompts: List[Dict[str, Any]] | str,  # Accept either a list of prompts or a single string
    negative_prompt: str = "",
    width: int = 512,
    height: int = 512,
    personality: AIPersonality = None,
    client: Client = None,
    output_file_name: str = None
) -> str:
    try:
        personality = app.personality
        if app.ttv is not None:
            personality.step_start("Generating video (this can take a while, be patient please ...)")

            # Handle single prompt case by converting to list format
            if isinstance(prompts, str):
                prompts = [{"prompt": prompts, "frames": 8}]  # Default to 8 frames for single prompt

            file = app.ttv.generate_video_by_frames(
                prompts=prompts,
                negative_prompt=negative_prompt,
                width=width,
                height=height,
                output_folder=client.discussion.discussion_folder,
                output_file_name=output_file_name
            )
            
            if file is None:
                personality.step_end("Generating video (this can take a while, be patient please ...)", False)
                return "Failed to generate the video. Make sure you have enough balance"

            personality.step_end("Generating video (this can take a while, be patient please ...)")
            url = discussion_path_to_url(file)
            
            app.personality.set_message_html(f"""<div style="width: 100%; max-width: 800px; margin: 0 auto;">
  <video controls style="width: 100%; height: auto;">
    <source src="{url}" type="video/mp4">
    Your browser does not support the video tag.
  </video>
</div>
""")
            return f"Generated video saved to: {file}"
        else:
            return "Text to video module not loaded"

    except Exception as ex:
        trace_exception(ex)
        return f"Error generating video: {str(ex)}"


class VideoGen(FunctionCall):
    def __init__(self, app: LollmsApplication, client: Client):
        super().__init__("video_gen", app, FunctionType.CLASSIC, client)

    def execute(self, context, *args, **kwargs):
        # Accept either a single prompt or a list of prompts
        prompt = kwargs.get("prompt", "")
        prompts = kwargs.get("prompts", None)  # Optional list of {"prompt": str, "frames": int}
        negative_prompt = kwargs.get("negative_prompt", "")
        width = kwargs.get("width", 1024)
        height = kwargs.get("height", 512)
        output_file_name = kwargs.get("output_file_name", None)

        # If 'prompts' is provided, use it; otherwise, fall back to single 'prompt'
        if prompts is not None:
            if not isinstance(prompts, list):
                return "Error: 'prompts' must be a list of dictionaries with 'prompt' and 'frames' keys"
        else:
            prompts = prompt  # Use single prompt if no prompts list is provided

        return build_video(
            self.app,
            prompts,
            negative_prompt,
            width,
            height,
            self.personality,
            self.client,
            output_file_name=output_file_name
        )