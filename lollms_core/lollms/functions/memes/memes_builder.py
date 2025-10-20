# Lollms function call definition file
# File Name: drake_meme_generator.py
# Author: ParisNeo
# Description: This function generates a Drake meme by overlaying positive and negative text onto a predefined image template.

from functools import partial
from typing import Dict
from lollms.utilities import PackageManager, discussion_path_to_url
from lollms.client_session import Client
from ascii_colors import trace_exception
from pathlib import Path

# Ensure required libraries are installed
if not PackageManager.check_package_installed("PIL"):
    PackageManager.install_package("Pillow")

from pathlib import Path
import requests
from PIL import Image
from io import BytesIO

# Now we can import the library
from PIL import Image, ImageDraw, ImageFont

import textwrap

def load_image_from_url(url: str) -> Image.Image:
    """
    Load an image from a given URL.

    Args:
        url (str): The URL of the image to load.

    Returns:
        Image.Image: The loaded image.
    """
    response = requests.get(url)
    response.raise_for_status()  # Ensure we notice bad responses
    image = Image.open(BytesIO(response.content))
    return image

def draw_text_with_outline(draw: ImageDraw.Draw, text: str, position: tuple, font: ImageFont.FreeTypeFont, outline_width: int = 2, fill: str = "white", outline_fill: str = "black"):
    """
    Draw text with an outline, perfect for meme-worthy captions.

    Args:
        draw (ImageDraw.Draw): The drawing context.
        text (str): The text to draw.
        position (tuple): The position to draw the text (x, y).
        font (ImageFont.FreeTypeFont): The font to use.
        outline_width (int): The width of the outline.
        fill (str): Color to fill the text with (default is white).
        outline_fill (str): Color to fill the outline with (default is black).
    """
    x, y = position
    # Draw outline
    for dx in range(-outline_width, outline_width + 1):
        for dy in range(-outline_width, outline_width + 1):
            if dx != 0 or dy != 0:
                draw.text((x + dx, y + dy), text, font=font, fill=outline_fill)
    # Draw text
    draw.text(position, text, font=font, fill=fill)


def draw_text_within_box(draw: ImageDraw.Draw, text: str, box_coords: tuple, font_path: Path, initial_font_size: int, fill: str = "white", outline_fill: str = "black"):
    """
    Draw text within a specified box, adjusting font size and wrapping text as needed, and center it within the box.

    Args:
        draw (ImageDraw.Draw): The drawing context.
        text (str): The text to draw.
        box_coords (tuple): The coordinates of the box (top_left_x, top_left_y, bottom_right_x, bottom_right_y).
        font_path (Path): Path to the font file.
        initial_font_size (int): Initial font size to start with.
        fill (str): Color to fill the text with.
        outline_fill (str): Color to fill the outline with.
    """
    top_left_x, top_left_y, bottom_right_x, bottom_right_y = box_coords
    box_width = bottom_right_x - top_left_x
    box_height = bottom_right_y - top_left_y
    font_size = initial_font_size
    font = ImageFont.truetype(str(font_path), font_size)

    # Ensure box width is positive
    if box_width <= 0:
        raise ValueError("Box width must be greater than 0")
    
    # Wrap text to fit within the box width
    wrapped_text = textwrap.fill(text, width=box_width // font.getbbox('A')[2])
    
    # Adjust font size to fit within the box height
    while font.getbbox(wrapped_text)[3] > box_height and font_size > 1:
        font_size -= 1
        font = ImageFont.truetype(str(font_path), font_size)
        wrapped_text = textwrap.fill(text, width=box_width // font.getbbox('A')[2])
    
    # Calculate text size and position to center it
    text_left, text_top, text_width, text_height = font.getbbox(wrapped_text)
    text_x = top_left_x + (box_width - text_width) / 2
    text_y = top_left_y + (box_height - text_height) / 2
    
    # Draw the text with outline
    draw_text_with_outline(draw, wrapped_text, (text_x, text_y), font, outline_width=2, fill=fill, outline_fill=outline_fill)

def drake_meme_generator(positive_text: str, negative_text: str, client:Client) -> str:
    """
    Generates a Drake meme using the provided positive and negative text.

    Args:
        positive_text (str): Text to be placed in the second box (Drake approving).
        negative_text (str): Text to be placed in the first box (Drake disapproving).

    Returns:
        str: HTML string containing the path to the generated meme image.
    """
    try:
        # Load the Drake meme template image
        template_url = "https://i.pinimg.com/originals/0e/90/91/0e9091993fc0289656646088f0ea93f7.jpg"
        image = load_image_from_url(template_url)

        # Define positions for text boxes
        first_box_coords = (627, 129, 1173, 407)
        second_box_coords = (627, 763, 1173, 1046)

        # Initialize drawing context
        draw = ImageDraw.Draw(image)
        font_path = Path("arial.ttf")  # Ensure you have a suitable font file

        # Add text to the image
        draw_text_within_box(draw, negative_text, first_box_coords, font_path, initial_font_size=40, fill="white")
        draw_text_within_box(draw, positive_text, second_box_coords, font_path, initial_font_size=40, fill="white")

        # Save the modified image
        output_path = client.discussion_path/"drake_meme_output.jpg"
        image.save(output_path)

        # Return HTML string with the image path
        return f'<img src="{discussion_path_to_url(output_path)}" alt="Drake Meme">'
    except Exception as e:
        return trace_exception(e)

def drake_meme_generator_function(client:Client) -> Dict:
    return {
        "function_name": "drake_meme_generator",
        "function": partial(drake_meme_generator, client=client),
        "function_description": "Generates a Drake meme using the provided positive and negative text.",
        "function_parameters": [
            {"name": "positive_text", "type": "str"},
            {"name": "negative_text", "type": "str"}
        ]
    }

def two_paths_meme_generator(good_text: str, bad_text: str, person_text: str, client: Client) -> str:
    """
    Generates a Two Paths meme using the provided text for the good path, bad path, and the person.

    Args:
        good_text (str): Text to be placed on the path towards the good castle.
        bad_text (str): Text to be placed on the path towards the bad castle.
        person_text (str): Text to be placed on the person.

    Returns:
        str: HTML string containing the path to the generated meme image.
    """
    try:
        # Load the Two Paths meme template image
        template_url = "https://i.imgflip.com/54d9lj.png?a477528"
        image = load_image_from_url(template_url)

        # Define positions for text boxes
        good_path_coords = (0, 0, 196, 148)
        bad_path_coords = (197, 0, 414, 148)
        person_coords = (130, 306, 282, 416)

        # Initialize drawing context
        draw = ImageDraw.Draw(image)
        font_path = Path("arial.ttf")  # Ensure you have a suitable font file

        # Add text to the image
        draw_text_within_box(draw, good_text, good_path_coords, font_path, initial_font_size=20)
        draw_text_within_box(draw, bad_text, bad_path_coords, font_path, initial_font_size=20)
        draw_text_within_box(draw, person_text, person_coords, font_path, initial_font_size=20)

        # Save the modified image
        output_path = client.discussion_path / "two_paths_meme_output.jpg"
        image.save(output_path)

        # Return HTML string with the image path
        return f'<img src="{discussion_path_to_url(output_path)}" alt="Two Paths Meme">'
    except Exception as e:
        return trace_exception(e)

def two_paths_meme_generator_function(client: Client) -> Dict:
    return {
        "function_name": "two_paths_meme_generator",
        "function": partial(two_paths_meme_generator, client=client),
        "function_description": "Generates a Two Paths meme using the provided text for the good path, bad path, and the person.",
        "function_parameters": [
            {"name": "good_text", "type": "str"},
            {"name": "bad_text", "type": "str"},
            {"name": "person_text", "type": "str"}
        ]
    }



from lollms.utilities import PackageManager, find_first_available_file_index, discussion_path_to_url
from lollms.client_session import Client
from lollms.personality import APScript
from ascii_colors import trace_exception
from functools import partial
from PIL import Image, ImageDraw, ImageFont

def build_negative_prompt(image_generation_prompt, llm):
    start_header_id_template = llm.config.start_header_id_template
    end_header_id_template = llm.config.end_header_id_template
    system_message_template = llm.config.system_message_template        

    return "\n".join([
        f"{start_header_id_template}{system_message_template}{end_header_id_template}",
        f"{llm.config.negative_prompt_generation_prompt}",
        f"{start_header_id_template}image_generation_prompt{end_header_id_template}",
        f"{image_generation_prompt}",
        f"{start_header_id_template}negative_prompt{end_header_id_template}",
    ])    

def add_text_overlay(image_path, text, output_path):
    # Open the original image
    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)

    # Define the font and size
    font_size = 36
    font = ImageFont.load_default()  # You can specify a TTF font file if needed

    # Define text position and color
    text_position = (10, 10)  # Top-left corner
    text_color = (255, 255, 255)  # White color

    # Add text overlay
    draw.text(text_position, text, fill=text_color, font=font)

    # Save the new image with overlay
    image.save(output_path)

def build_meme_image_with_text_overlay(prompt, negative_prompt, width, height, text: str, processor: APScript, client: Client):
    try:
        if processor.personality.config.active_tti_service == "diffusers":
            if not processor.personality.app.tti:
                from lollms.services.tti.diffusers.lollms_diffusers import LollmsDiffusers
                processor.step_start("Loading ParisNeo's fork of AUTOMATIC1111's stable diffusion service")
                processor.personality.app.tti = LollmsDiffusers(processor.personality.app, processor.personality.name)
                processor.personality.app.sd = processor.personality.app.tti
                processor.step_end("Loading ParisNeo's fork of AUTOMATIC1111's stable diffusion service")
            file, infos = processor.personality.app.tti.paint(
                prompt, 
                negative_prompt,
                width=width,
                height=height,
                output_path=client.discussion.discussion_folder
            )
        elif processor.personality.config.active_tti_service == "autosd":
            if not processor.personality.app.tti:
                from lollms.services.tti.sd.lollms_sd import LollmsSD
                processor.step_start("Loading ParisNeo's fork of AUTOMATIC1111's stable diffusion service")
                processor.personality.app.tti = LollmsSD(processor.personality.app, processor.personality.name, max_retries=-1, auto_sd_base_url=processor.personality.config.sd_base_url)
                processor.personality.app.sd = processor.personality.app.tti
                processor.step_end("Loading ParisNeo's fork of AUTOMATIC1111's stable diffusion service")
            file, infos = processor.personality.app.tti.paint(
                prompt, 
                negative_prompt,
                width=width,
                height=height,
                output_path=client.discussion.discussion_folder
            )
        elif processor.personality.config.active_tti_service == "dall-e":
            if not processor.personality.app.tti:
                from lollms.services.tti.dalle.lollms_dalle import LollmsDalle
                processor.step_start("Loading dalle service")
                processor.personality.app.tti = LollmsDalle(processor.personality.app, processor.personality.config.dall_e_key, processor.personality.config.dall_e_generation_engine)
                processor.personality.app.dalle = processor.personality.app.tti
                processor.step_end("Loading dalle service")
            processor.step_start("Painting")
            file = processor.personality.app.tti.paint(
                prompt,
                negative_prompt,
                width=width,
                height=height,
                output_path=client.discussion.discussion_folder
            )
            processor.step_end("Painting")
        elif processor.personality.config.active_tti_service == "comfyui":
            if not processor.personality.app.tti:
                from lollms.services.tti.comfyui.lollms_comfyui import LollmsComfyUI
                processor.step_start("Loading comfyui service")
                processor.personality.app.tti = LollmsComfyUI(
                    processor.personality.app,
                    comfyui_base_url=processor.config.comfyui_base_url
                )
                processor.personality.app.dalle = processor.personality.app.tti
                processor.step_end("Loading comfyui service")
            processor.step_start("Painting")
            file = processor.personality.app.tti.paint(
                prompt,
                negative_prompt,
                width=width,
                height=height,
                output_path=client.discussion.discussion_folder
            )
            processor.step_end("Painting")

        file = str(file)
        escaped_url = discussion_path_to_url(file)

        # Add text overlay to the generated image
        output_image_path = f"{client.discussion.discussion_folder}/output_with_text.png"
        add_text_overlay(file, text, output_image_path)

        escaped_output_url = discussion_path_to_url(output_image_path)
        return f'\nRespond with this link in markdown format:\n![]({escaped_output_url})'
    except Exception as ex:
        trace_exception(ex)
        return f"Couldn't generate image. Make sure {processor.personality.config.active_tti_service} service is installed"


def build_meme_image_with_text_overlay_function(processor, client):
    if processor.config.use_negative_prompt:
        if processor.config.use_ai_generated_negative_prompt:
            return {
                    "function_name": "build_image",
                    "function": partial(build_meme_image_with_text_overlay, processor=processor, client=client),
                    "function_description": "Builds and shows a meme image from a prompt and width and height parameters then overlays a text on the center. A square 1024x1024, a portrait woudl be 1024x1820 or landscape 1820x1024. Width and height have to be divisible by 8.",
                    "function_parameters": [{"name": "prompt", "type": "str"}, {"name": "negative_prompt", "type": "str"}, {"name": "width", "type": "int"}, {"name": "height", "type": "int"}, {"name": "text", "type": "str"}]                
                }
        else:
            return {
                    "function_name": "build_image",
                    "function": partial(build_meme_image_with_text_overlay, processor=processor, client=client, negative_prompt=processor.config.default_negative_prompt),
                    "function_description": "Builds and shows a meme image from a prompt and width and height parameters then overlays a text on the center. A square 1024x1024, a portrait woudl be 1024x1820 or landscape 1820x1024. Width and height have to be divisible by 8.",
                    "function_parameters": [{"name": "prompt", "type": "str"}, {"name": "width", "type": "int"}, {"name": "height", "type": "int"}, {"name": "text", "type": "str"}]                
                }
    else:
        return {
                "function_name": "build_image",
                "function": partial(build_meme_image_with_text_overlay, processor=processor, client=client, negative_prompt=""),
                "function_description": "Builds and shows a meme image from a prompt and width and height parameters then overlays a text on the center. A square 1024x1024, a portrait woudl be 1024x1820 or landscape 1820x1024. Width and height have to be divisible by 8.",
                "function_parameters": [{"name": "prompt", "type": "str"}, {"name": "width", "type": "int"}, {"name": "height", "type": "int"}, {"name": "text", "type": "str"}]                
            }



