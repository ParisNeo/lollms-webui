# Lollms function call definition file
# File Name: download_channel_transcripts.py
# Author: ParisNeo
# Description: This function takes a YouTube channel name, scans all their videos using web scraping, and downloads the transcripts. Each transcript is saved in a folder as a text file.

# Importing necessary libraries
from functools import partial
from typing import List
from lollms.utilities import PackageManager
from ascii_colors import trace_exception
import pathlib
import requests
from bs4 import BeautifulSoup

# Installing necessary packages
if not PackageManager.check_package_installed("youtube_transcript_api"):
    PackageManager.install_package("youtube-transcript-api")

# Importing the package after installation
from youtube_transcript_api import YouTubeTranscriptApi

def download_channel_transcripts(channel_url: str, output_folder: str) -> str:
    """
    This function takes a YouTube channel URL, scans all their videos using web scraping, and downloads the transcripts.
    Each transcript is saved in a folder as a text file.
    
    Parameters:
    channel_url (str): The URL of the YouTube channel.
    output_folder (str): The folder where transcripts will be saved.
    
    Returns:
    str: A message indicating the status of the download process.
    """
    try:
        if output_folder=="":
            return "Please set the transcription output path in lollmz personality sdettings"
        # Create output folder if it doesn't exist
        output_folder_path = pathlib.Path(output_folder)
        output_folder_path.mkdir(parents=True, exist_ok=True)
        
        # Get channel page content
        response = requests.get(channel_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Find all video links
        video_links = soup.find_all("a", href=True)
        video_ids = [link['href'].split('v=')[1] for link in video_links if "watch?v=" in link['href']]
        
        # Remove duplicates
        video_ids = list(set(video_ids))
        
        # Download transcripts and save to files
        for video_id in video_ids:
            try:
                transcript = YouTubeTranscriptApi.get_transcript(video_id)
                transcript_text = " ".join([entry['text'] for entry in transcript])
                
                output_file_path = output_folder_path / f"{video_id}.txt"
                output_file_path.write_text(transcript_text, encoding='utf-8')
            except Exception as e:
                trace_exception(e)
        
        return "Transcripts downloaded successfully!"
    except Exception as e:
        return trace_exception(e)

def download_channel_transcripts_function(output_folder:str):
    return {
        "function_name": "download_channel_transcripts",
        "function": partial(download_channel_transcripts, output_folder=output_folder),
        "function_description": "This function takes a YouTube channel name, scans all their videos using web scraping, and downloads the transcripts. Each transcript is saved in a folder as a text file.",
        "function_parameters": [
            {"name": "channel_url", "type": "str"},
        ]
    }
