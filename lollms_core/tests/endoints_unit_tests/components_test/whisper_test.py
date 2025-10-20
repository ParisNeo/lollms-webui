# Title LollmsWhisper
# Licence: MIT
# Author : Paris Neo
# 

from pathlib import Path
import whisper


if __name__ == "__main__":
    # Create a mock LollmsApplication instance
    w = whisper.load_model("small")
    # Example usage
    audio_file_path = Path(r"E:\lollms\custom_voices\ParisNeo_Original_voice.wav")
    
    if audio_file_path.exists():
        transcription = w.transcribe(str(audio_file_path))
        print("Transcription:")
        print(transcription)
    else:
        print(f"Audio file not found: {audio_file_path}")
