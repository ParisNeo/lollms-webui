# Lollms function call definition file
# File Name: download_youtube_transcript.py
# Author: ParisNeo
# Description: This function goes online to YouTube and downloads the transcript from any video

# Importing necessary libraries
from functools import partial
from typing import List
from lollms.utilities import PackageManager
from ascii_colors import trace_exception, ASCIIColors
from typing import Any

# Installing necessary packages
if not PackageManager.check_package_installed("youtube_transcript_api"):
    PackageManager.install_package("youtube-transcript-api")

# Importing the package after installation
from youtube_transcript_api import YouTubeTranscriptApi

def download_youtube_transcript(video_id: str, language_code: str = 'en') -> str:
    """
    This function downloads the transcript of a YouTube video given its video ID.
    
    Parameters:
    video_id (str): The ID of the YouTube video.
    languages (tuple): A list of languages to extract.
    
    Returns:
    str: The transcript of the video.
    """
    try:
        # Fetching the transcript
        transcript = YouTubeTranscriptApi.get_transcript(video_id, (language_code,))
        
        # Combining the transcript into a single string
        transcript_text = " ".join([entry['text'] for entry in transcript])
        ASCIIColors.magenta("---- Transcript ----")
        ASCIIColors.magenta(transcript_text)
        ASCIIColors.magenta("----")
        return transcript_text
    except Exception as e:
        return trace_exception(e)

def download_youtube_transcript_function():
    return {
        "function_name": "download_youtube_transcript",
        "function": download_youtube_transcript,
        "function_description": "This function goes online to YouTube and downloads the transcript from any video.",
        "function_parameters": [{"name": "video_id", "type": "str"},{"name": "language_code", "type": "str"}]
    }
