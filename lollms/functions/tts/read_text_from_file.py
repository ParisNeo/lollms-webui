# Lollms function call definition file

# Import necessary modules
from pathlib import Path
from functools import partial
from typing import Union
from lollms.utilities import PackageManager
from lollms.personality import APScript
from lollms.tts import LollmsTTS
from safe_store import parse_document
from ascii_colors import trace_exception

# Here is the core of the function to be built
def read_text_from_file(file_path: Union[Path, str], tts_module:LollmsTTS, llm:APScript) -> str:
    """
    This function takes a TTS module and a file path as input, reads the text from the file,
    and uses the TTS module to generate audio from the text.
    
    Parameters:
    tts_module: The text-to-speech module with a method tts_audio.
    file_path: The path to the text file containing the text to be read.

    Returns:
    str: The path to the generated audio file.
    """
    try:
        # Ensure file_path is of type Path
        file_path = Path(file_path)
        
        # Read the text from the file
        text = parse_document(file_path)
        
        # Generate audio from the text
        audio_file_path = tts_module.tts_audio(text,use_threading=True)
        llm.set_message_content(text)
        
        # Return the path to the generated audio file
        return str(audio_file_path)
    except Exception as e:
        return trace_exception(e)
    

# Metadata function
def read_text_from_file_function(file_path:str,tts_module:LollmsTTS, llm:APScript):
    return {
        "function_name": "read_text_from_file", # The function name in string
        "function": partial(read_text_from_file, file_path=file_path, tts_module=tts_module, llm=llm), # The function to be called
        "function_description": "Reads text from the current file and uses a TTS module to generate audio from the text.", # Description of the function
        "function_parameters": [] # The set of parameters          
    }
