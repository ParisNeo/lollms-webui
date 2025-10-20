# Lollms function call definition file

# Import necessary modules
from pathlib import Path
from functools import partial
from typing import Union
from lollms.utilities import PackageManager
from lollms.personality import APScript
from lollms.tts import LollmsTTS
from ascii_colors import trace_exception

# Here is the core of the function to be built
def read_text(text: str, tts_module:LollmsTTS, llm:APScript) -> str:
    """
    This function takes a TTS module and a file path as input, reads the text from the file,
    and uses the TTS module to generate audio from the text.
    
    Parameters:
    tts_module: The text-to-speech module with a method tts_audio.
    text: The text to be read.

    Returns:
    str: The path to the generated audio file.
    """
    try:        
        # Generate audio from the text
        audio_file_path = tts_module.tts_audio(text)
        llm.add_chunk_to_message_content(text)
        llm.new_message("")
        
        # Return the path to the generated audio file
        return "Reading text:\n"+text
    except Exception as e:
        trace_exception(e)
        return str(e)
    

# Metadata function
def read_text_function(tts_module:LollmsTTS):
    return {
        "function_name": "read_text_from_file", # The function name in string
        "function": partial(read_text, tts_module=tts_module), # The function to be called
        "function_description": "Reads text from a file and uses a TTS module to generate audio from the text.", # Description of the function
        "function_parameters": [
            {"name":"text","type":"str","description":"Th text to generate the audio from"}
        ] # The set of parameters          
    }
