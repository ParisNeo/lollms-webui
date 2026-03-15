from lollms.function_call import FunctionCall, FunctionType
from lollms.app import LollmsApplication
from lollms.client_session import Client
from lollms.prompting import LollmsContextDetails
from ascii_colors import ASCIIColors, trace_exception
from lollms.config import TypedConfig, ConfigTemplate, BaseConfig
from typing import List
import json

# Check and install youtube_transcript_api if not present
import pipmaster as pm
if not pm.is_installed("youtube_transcript_api"):
    pm.install("youtube_transcript_api")

from youtube_transcript_api import YouTubeTranscriptApi

class YoutubeTranscriptSummarizer(FunctionCall):
    def __init__(self, app: LollmsApplication, client: Client):
        static_parameters = TypedConfig(
            ConfigTemplate([
                {
                    "name": "language_code",
                    "type": "str",
                    "value": "en",
                    "help": "ISO language code"
                },
            ]),
            BaseConfig(config={
            })
        )
        super().__init__("youtube_transcript_summarizer", app, FunctionType.CONTEXT_UPDATE, client, static_parameters)

    def extract_video_id(self, prompt: str) -> str:
        # Use AI to extract video ID
        extraction_prompt = f"""
        Extract the YouTube video ID from the following text. The video ID could be in these formats:
        - Full URL: https://www.youtube.com/watch?v=XXXXXXXXXXX
        - Short URL: https://youtu.be/XXXXXXXXXXX
        - Just the ID: XXXXXXXXXXX (11 characters)

        Text: {prompt}

        Output the result in this JSON format:
        {{
            "video_id": "the_extracted_id_or_null_if_not_found",
            "found": true_or_false
        }}
        """

        try:
            json_result = self.personality.generate_code(
                prompt=extraction_prompt,
                language="json",
                template='{"video_id": "", "found": false}'
            )
            result = json.loads(json_result)
            return result.get("video_id") if result.get("found") else None
        except Exception as e:
            print(f"Error extracting video ID: {str(e)}")
            return None

    def update_context(self, context: LollmsContextDetails, constructed_context: List[str]):
        try:
            # First, check if the user wants to summarize a YouTube video
            is_youtube_summary = self.personality.yes_no(
                question="Is the user asking to recover and summarize a YouTube video transcript?",
                context=context.prompt,
                callback=self.personality.sink
            )

            if not is_youtube_summary:
                return constructed_context

            # Extract video ID using AI
            video_id = self.extract_video_id(context.prompt)

            if not video_id:
                constructed_context.append("Error: Could not find a valid YouTube video ID in the prompt.")
                return constructed_context

            # Get the transcript
            try:
                transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[self.static_parameters.language_code])

                # Convert transcript to text
                full_text = " ".join([entry['text'] for entry in transcript])

                # Add instructions for the AI
                constructed_context.append("I have retrieved the following YouTube video transcript. Please provide a comprehensive summary:")
                constructed_context.append(full_text)
                constructed_context.append("\nPlease analyze the transcript and create a detailed summary covering the main points and key insights from the video.")

            except Exception as e:
                constructed_context.append(f"Error: Could not retrieve the transcript. Error message: {str(e)}")

        except Exception as e:
            trace_exception(e)
            constructed_context.append(f"An error occurred: {str(e)}")

        return constructed_context

    def process_output(self, context: LollmsContextDetails, llm_output: str):
        return llm_output
