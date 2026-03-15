import datetime
from lollms.app import LollmsApplication
from lollms.personality import AIPersonality
from lollms.function_call import FunctionCall, FunctionType
from lollms.prompting import LollmsContextDetails
from datetime import datetime
from typing import List
from lollms.utilities import discussion_path_to_url
from lollms.client_session import Client
from lollms.personality import APScript
from ascii_colors import trace_exception
from functools import partial
from lollms.functions.prompting.image_gen_prompts import get_image_gen_prompt, get_random_image_gen_prompt
import pipmaster as pm
pm.install_if_missing("pillow")
from PIL import Image

def build_image(prompt, negative_prompt, width, height, output_file_name, personality:AIPersonality, client:Client, return_format="markdown", transparency_key=None):
    """
    Generates an image based on the given prompt and optionally makes a specific color transparent.

    Args:
        prompt (str): The prompt for generating the image.
        negative_prompt (str): The negative prompt for generating the image.
        width (int): The width of the image.
        height (int): The height of the image.
        output_file_name (str): The name of the output file.
        personality (AIPersonality): The AI personality instance.
        client (Client): The client instance.
        return_format (str): The format in which to return the image (markdown, url, path, url_and_path).
        transparency_key (tuple): The RGB color to make transparent (e.g., (255, 0, 0) for red).

    Returns:
        str or dict: The generated image in the specified format.
    """
    try:
        if personality.app.tti is not None:
            personality.step_start("Painting")
            file, infos = personality.app.tti.paint(
                prompt,
                negative_prompt,
                width=width,
                height=height,
                output_folder=client.discussion.discussion_folder,
                output_file_name=output_file_name
            )
            personality.step_end("Painting")

        if file:
            file = str(file)
            if transparency_key:
                # Open the image and convert it to RGBA
                img = Image.open(file).convert("RGBA")
                datas = img.getdata()

                new_data = []
                for item in datas:
                    # Change all pixels that match the transparency_key to transparent
                    if item[:3] == transparency_key:
                        new_data.append((255, 255, 255, 0))
                    else:
                        new_data.append(item)

                img.putdata(new_data)
                img.save(file, "PNG")

            escaped_url = discussion_path_to_url(file)

            if return_format == "markdown":
                return f'\n![]({escaped_url})'
            elif return_format == "url":
                return escaped_url
            elif return_format == "path":
                return file
            elif return_format == "url_and_path":
                return {"url": escaped_url, "path": file}
            else:
                return f"Invalid return_format: {return_format}. Supported formats are 'markdown', 'url', 'path', and 'url_and_path'."
        else:
            return f"Could not generate the image."

    except Exception as ex:
        trace_exception(ex)
        if return_format == "markdown":
            return f"\nCouldn't generate image. Make sure {personality.config.active_tti_service} service is installed"
        elif return_format == "url":
            return None
        elif return_format == "path":
            return None
        elif return_format == "url_and_path":
            return {"url": None, "path": None, "error": ex}
        else:
            return f"Couldn't generate image. Make sure {personality.config.active_tti_service} service is installed"


class ImageGen (FunctionCall):
    def __init__(self, app: LollmsApplication, client: Client):
        super().__init__("image_gen", app, FunctionType.CLASSIC, client)

    def execute(self, context, *args, **kwargs):
        prompt = kwargs.get("prompt","")
        negative_prompt = kwargs.get("negative_prompt","")
        output_file_name = kwargs.get("output_file_name",None)
        width = kwargs.get("width",1024)
        height = kwargs.get("height",512)
        transparency_key = kwargs.get("transparency_color",[255,0,255])
        
        return build_image(prompt, negative_prompt,width, height, output_file_name, self.personality, self.client, transparency_key=transparency_key)
    
        
