from lollms.function_call import FunctionCall, FunctionType
from lollms.app import LollmsApplication
from lollms.client_session import Client
from ascii_colors import trace_exception, ASCIIColors
import pipmaster as pm

# Check and install required package
if not pm.is_installed("youtube_transcript_api"):
    pm.install("youtube-transcript-api")

from youtube_transcript_api import YouTubeTranscriptApi

class DownloadYoutubeTranscript(FunctionCall):
    def __init__(self, app: LollmsApplication, client: Client):
        super().__init__("download_youtube_transcript",app,FunctionType.CLASSIC, client)

    def execute(self, *args, **kwargs):
        try:
            # Get parameters from kwargs
            video_id = kwargs.get("video_id", "")
            language_code = kwargs.get("language_code", "en")

            # Fetching the transcript
            try:
                transcript = YouTubeTranscriptApi.get_transcript(video_id, (language_code,))

                # Combining the transcript into a single string
                transcript_text = " ".join([entry['text'] for entry in transcript])

                ASCIIColors.magenta("---- Transcript ----")
                ASCIIColors.magenta(transcript_text)
                ASCIIColors.magenta("----")
            except :
                transcript = f"Couldn't recover the transcript of this video in the language {language_code}"
            return transcript_text

        except Exception as e:
            return str(trace_exception(e))
