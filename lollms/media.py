"""
Project: LoLLMs
Author: ParisNeo
Description: Media classes:
    - WebcamImageSender: is a captures images from the webcam and sends them to a SocketIO client.
    - MusicPlayer: is a MusicPlayer class that allows you to play music using pygame library.
License: Apache 2.0
"""
import pipmaster as pm
from lollms.com import LoLLMsCom
from lollms.utilities import trace_exception, run_async
from lollms.types import MSG_OPERATION_TYPE, SENDER_TYPES
from lollms.client_session import Session
from ascii_colors import ASCIIColors
import platform
from functools import partial
import subprocess
from collections import deque
from scipy.signal import butter, lfilter
import pipmaster as pm

import os
import threading
import re

pm.ensure_packages({
    "opencv-python":"",
    "scipy":"",
    "matplotlib":"",
    "sounddevice":"",
    "wave":""
    })

import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')



import socketio
from lollms.com import LoLLMsCom
try:
    import sounddevice as sd
    import wave
except:
    ASCIIColors.error("Couldn't load sound tools")

import time
import base64
import socketio
from matplotlib import pyplot as plt
import numpy as np
from scipy.signal import spectrogram
from pathlib import Path

from lollms.app import LollmsApplication
from lollms.tasks import TasksLibrary
from lollms.tts import LollmsTTS
from lollms.personality import AIPersonality
from lollms.function_call import FunctionCalling_Library
from lollms.client_session import Client
from datetime import datetime

import sys

def update_progress_bar(silence_counter, max_silence):
    bar_length = 40  # Length of the progress bar
    progress = silence_counter / max_silence
    block = int(round(bar_length * progress))
    
    # Determine the color based on progress
    if progress < 0.5:
        color = ASCIIColors.color_bright_green
    else:
        color = ASCIIColors.color_bright_red
    
    bar = "#" * block + "-" * (bar_length - block)
    
    sys.stdout.write("\r")
    ASCIIColors.print(f"silence_counter: {silence_counter} |{bar}| {round(progress * 100, 2)}%", color=color, end="")
    sys.stdout.flush()

# Step 1: Define your high-pass and low-pass filters (they’re like the bouncers for your audio club)
def butter_bandpass(lowcut, highcut, fs, order=5):
    nyquist = 0.5 * fs
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = butter(order, [low, high], btype='band')
    return b, a

def bandpass_filter(data, lowcut, highcut, fs, order=5):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = lfilter(b, a, data)
    return y

class RTCom:
    def __init__(
                        self, 
                        lc:LollmsApplication, 
                        sio:socketio.Client,  
                        personality:AIPersonality,
                        client:Client,
                        threshold=1000, 
                        silence_duration=2, 
                        sound_threshold_percentage=10, 
                        gain=1.0, 
                        rate=44100, 
                        channels=1, 
                        buffer_size=10, 
                        snd_input_device=None,
                        snd_output_device=None,
                        logs_folder="logs", 
                        block_while_talking=True,
                        use_keyword_audio=False,
                        keyword_audio_path=None
                    ):
        self.sio = sio
        self.lc = lc
        self.client = client
        self.block_listening = False
        self.personality = personality
        self.rate = rate
        self.channels = channels
        self.threshold = threshold
        self.silence_duration = silence_duration
        self.buffer_size = buffer_size
        self.gain = gain
        self.sound_threshold_percentage = sound_threshold_percentage
        self.block_while_talking = block_while_talking
        self.image_shot = None
        self.use_keyword_audio=use_keyword_audio,
        self.keyword_audio_path=keyword_audio_path
        self.summoned = False
        self.sample_mfccs = None
        if self.use_keyword_audio and self.keyword_audio_path:
            self.sample_features = self.load_and_extract_features(self.keyword_audio_path)



        if snd_input_device is None:
            devices = sd.query_devices()
            snd_input_device = [device['name'] for device in devices  if device["max_input_channels"]>0][0]
        if snd_output_device is None:
            devices = sd.query_devices()
            snd_output_device = [device['name'] for device in devices  if device["max_output_channels"]>0][0]

        self.snd_input_device = snd_input_device
        self.snd_output_device = snd_output_device
        self.logs_folder = Path(logs_folder)

        self.logs_folder.mkdir(exist_ok=True, parents=True)

        self.frames = []
        self.silence_counter = 0
        self.current_silence_duration = 0
        self.longest_silence_duration = 0
        self.sound_frames = 0
        self.audio_values = []

        self.max_audio_value = 0
        self.min_audio_value = 0
        self.total_frames = 0  # Initialize total_frames

        self.file_index = 0
        self.recording = False
        self.stop_flag = False

        self.buffer = deque(maxlen=buffer_size)
        self.transcribed_files = deque()
        self.buffer_lock = threading.Condition()
        self.transcribed_lock = threading.Condition()

    def load_and_extract_features(self, file_path):

        
        if not pm.is_installed("librosa"):
            pm.install("librosa")
        import librosa
        y, sr = librosa.load(file_path, sr=None)
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        return np.mean(mfccs.T, axis=0)

    def extract_features(self, frames):
        pm.ensure_packages({"librosa":""})
        
        filename = f"recording_{self.file_index}.wav"
        self.file_index += 1

        amplified_frames = self._apply_gain(frames)
        trimmed_frames = self._trim_silence([amplified_frames])
        logs_file = Path(self.logs_folder)/filename
        logs_file.parent.mkdir(exist_ok=True, parents=True)

        wf = wave.open(str(logs_file), 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(2)
        wf.setframerate(self.rate)
        wf.writeframes(trimmed_frames)
        wf.close()

        import librosa
        y, sr = librosa.load(logs_file, sr=self.rate)
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)

        return np.mean(mfccs.T, axis=0)
    
    def compare_voices(self, sample_features, realtime_features, th = 20):
        pm.ensure_packages({"scipy":""})
        from scipy.spatial.distance import euclidean
        # Calculate the Euclidean distance between the features
        distance = euclidean(sample_features, realtime_features)
        
        # If the distance is smaller than the threshold, we have a match!
        if distance < th:
            print(f"Voice match found! (distance: {distance}) 🎉🤡")
            return True
        else:
            print(f"No match found. (distance: {distance}) 😢🤡")
            return False
        

    def start_recording(self):
        self.recording = True
        self.stop_flag = False

        self.recording_thread = threading.Thread(target=self._record)
        self.transcription_thread = threading.Thread(target=self._process_files)
        self.recording_thread.start()
        self.transcription_thread.start()

    def stop_recording(self):
        self.recording = False
        self.stop_flag = True
        ASCIIColors.green("<<RTCOM off>>")

    def _record(self):
        with sd.InputStream(channels=self.channels, device=self.snd_input_device, samplerate=self.rate, callback=self.callback, dtype='int16'):
            while not self.stop_flag:
                time.sleep(1)
        self.recording = False

        # self._save_histogram(self.audio_values)

    def callback(self, indata, frames, time, status):
        max_scilence = int((self.rate / frames) * self.silence_duration)
        if not self.block_listening:
            # Transform the buffer into a numpy array (like turning a frog into a prince)
            audio_data = np.frombuffer(indata, dtype=np.int16)
            # Apply the bandpass filter to the incoming audio data
            audio_data = bandpass_filter(audio_data, lowcut=300, highcut=3000, fs=self.rate)
            max_value = np.max(audio_data)
            min_value = np.min(audio_data)

            if max_value > self.max_audio_value:
                self.max_audio_value = max_value
            if min_value < self.min_audio_value:
                self.min_audio_value = min_value

            self.audio_values.extend(audio_data)

            self.total_frames += frames
            ASCIIColors.red(f" max_value: {max_value}", end="")
            if max_value < self.threshold:
                self.silence_counter += 1
                self.current_silence_duration += frames
            else:
                self.silence_counter = 0
                self.current_silence_duration = 0
                self.sound_frames += frames

            if self.current_silence_duration > self.longest_silence_duration:
                self.longest_silence_duration = self.current_silence_duration

            if self.silence_counter > max_scilence:
                trimmed_frames = self._trim_silence(self.frames)
                ASCIIColors.yellow(f"\nsound duration: {len(trimmed_frames)/self.rate}")
                sound_percentage = self._calculate_sound_percentage(trimmed_frames)
                if sound_percentage >= self.sound_threshold_percentage:
                    ASCIIColors.red(f"Sound percentage {sound_percentage}")
                    ASCIIColors.red("\nSilence counter reached threshold")

                    if self.use_keyword_audio and self.keyword_audio_path and self.summoned == False:
                        features = self.extract_features(self.frames)
                        if self.compare_voices(self.sample_features, features):
                            self.summoned = True
                    else:
                        self._save_wav(self.frames)
                        self.summoned = False
                self.frames = []
                self.silence_counter = 0
                self.total_frames = 0
                self.sound_frames = 0
            else:
                update_progress_bar(self.silence_counter, max_scilence)
                self.frames.append(indata.copy())
        else:
            self.frames = []
            self.silence_counter = 0
            self.current_silence_duration = 0
            self.longest_silence_duration = 0
            self.sound_frames = 0
            self.audio_values = []

            self.max_audio_value = 0
            self.min_audio_value = 0
            self.total_frames = 0  # Initialize total_frames

    def _apply_gain(self, frames):
        audio_data = np.frombuffer(b''.join(frames), dtype=np.int16)
        audio_data = audio_data * self.gain
        audio_data = np.clip(audio_data, -32768, 32767)
        return audio_data.astype(np.int16).tobytes()

    def _trim_silence(self, frames):
        audio_data = np.frombuffer(b''.join(frames), dtype=np.int16)
        non_silent_indices = np.where(np.abs(audio_data) >= self.threshold)[0]

        if non_silent_indices.size:
            start_index = max(non_silent_indices[0] - self.rate, 0)
            end_index = min(non_silent_indices[-1] + self.rate, len(audio_data))
            trimmed_data = audio_data[start_index:end_index]
        else:
            trimmed_data = np.array([], dtype=np.int16)

        return trimmed_data.tobytes()

    def _calculate_sound_percentage(self, frames):
        audio_data = np.frombuffer(frames, dtype=np.int16)
        num_bins = len(audio_data) // self.rate
        sound_count = 0

        for i in range(num_bins):
            bin_data = audio_data[i * self.rate: (i + 1) * self.rate]
            if np.max(bin_data) >= self.threshold:
                sound_count += 1

        sound_percentage = (sound_count / num_bins) * 100 if num_bins > 0 else 0
        return sound_percentage

    def contains_unwanted_special_characters(self, s):
        # Define a regex pattern to match any character that is not a Unicode letter, digit, punctuation, or whitespace
        pattern = re.compile(r'[^a-zA-Z0-9\s.,!?;:()\'"“”‘’—\-\u00C0-\u017F\u0400-\u04FF\u0600-\u06FF\u3040-\u30FF\u4E00-\u9FFF]', re.UNICODE)
        # Search for the pattern in the string
        if pattern.search(s):
            return True
        return False

    def remove_special_characters(self, s:str)->str:
        # Define a regex pattern to match any character that is not a Unicode letter, digit, punctuation, or whitespace
        pattern = re.compile(r'[^a-zA-Z0-9\s.,!?;:()\'"“”‘’—\-\u00C0-\u017F\u0400-\u04FF\u0600-\u06FF\u3040-\u30FF\u4E00-\u9FFF]', re.UNICODE)
        # Substitute the matched characters with an empty string
        cleaned_string = pattern.sub('', s)
        return cleaned_string

    def _save_wav(self, frames):
        ASCIIColors.green("<<SEGMENT_RECOVERED>>")
        # Todo annouce
        # self.transcription_signal.update_status.emit("Segment detected and saved")
        filename = f"recording_{self.file_index}.wav"
        self.file_index += 1

        amplified_frames = self._apply_gain(frames)
        trimmed_frames = self._trim_silence([amplified_frames])
        logs_file = Path(self.logs_folder)/filename
        logs_file.parent.mkdir(exist_ok=True, parents=True)

        wf = wave.open(str(logs_file), 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(2)
        wf.setframerate(self.rate)
        wf.writeframes(trimmed_frames)
        wf.close()

        with self.buffer_lock:
            while len(self.buffer) >= self.buffer.maxlen:
                self.buffer_lock.wait()
            self.buffer.append(filename)
            self.buffer_lock.notify()

    def _save_histogram(self, audio_values):
        plt.hist(audio_values, bins=50, edgecolor='black')
        plt.title('Histogram of Audio Values')
        plt.xlabel('Audio Value')
        plt.ylabel('Frequency')
        plt.savefig('audio_values_histogram.png')
        plt.close()

    def fix_string_for_xtts(self, input_string):
        # Remove excessive exclamation marks
        fixed_string = input_string.rstrip('!')
        
        return fixed_string
    
    def _process_files(self):
        while not self.stop_flag:
            with self.buffer_lock:
                while not self.buffer and not self.stop_flag:
                    self.buffer_lock.wait()
                if self.buffer:
                    filename = self.buffer.popleft()
                    self.buffer_lock.notify()
            if self.block_while_talking:
                self.block_listening = True
            try:
                if filename:
                    self.lc.info("Transcribing")
                    ASCIIColors.green("<<TRANSCRIBING>>")
                    wav_file_path = str(Path(self.logs_folder)/filename)
                    ASCIIColors.cyan(f"Logging to : {wav_file_path}")
                    transcription = self.lc.stt.transcribe(wav_file_path)
                    transcription = self.remove_special_characters(transcription).strip()
                    if len(transcription)>0:
                        transcription_fn = str(Path(self.logs_folder)/filename) + ".txt"
                        with open(transcription_fn, "w", encoding="utf-8") as f:
                            f.write(transcription)

                        with self.transcribed_lock:
                            self.transcribed_files.append((filename, transcription))
                            self.transcribed_lock.notify()

                        current_prompt = transcription
                        self.lc.new_block(client_id=self.client.client_id,sender=self.lc.config.user_name, content=current_prompt)
                        ASCIIColors.green("<<RESPONDING>>")
                        self.lc.info("Responding")
                        self.lc.handle_generate_msg(self.client.client_id, {"prompt": current_prompt})
                        while self.lc.busy:
                            time.sleep(0.01)
                        lollms_text = self.fix_string_for_xtts(self.client.generated_text)
                        ASCIIColors.red(" -------------- LOLLMS answer -------------------")
                        ASCIIColors.yellow(lollms_text)
                        ASCIIColors.red(" -------------------------------------------------")
                        self.lc.info("Talking")
                        ASCIIColors.green("<<TALKING>>")
                        self.lc.tts.tts_audio(lollms_text, file_name_or_path=str(Path(self.logs_folder)/filename)+"_answer.wav", use_threading=True)
            except Exception as ex:
                trace_exception(ex)
            self.block_listening = False
            ASCIIColors.green("<<LISTENING>>")
            self.lc.info(f"Listening.\nYou can talk to {self.personality.name}")
            # TODO : send the output
            #self.transcription_signal.update_status.emit("Listening")

    def get_voices(self):
        if self.lc.tts and self.lc.tts.ready:
            voices = self.lc.tts.get_voices()  # Assuming the response is in JSON format
            return voices
        return []
from pathlib import Path
import sounddevice as sd
import threading
import datetime
import wave
import numpy as np

class AudioNinja:
    def __init__(self, lc, logs_folder='logs', device=None):
        """
        Initialize the AudioNinja with a LollmsApplication object,
        a log folder, and an optional recording device.

        Args:
            lc (LollmsApplication): The LollmsApplication object for communication.
            logs_folder (str): The folder to save recordings. Default is 'logs'.
            device (int or str): The recording device index or name. Default is None.
        """
        self.lc = lc
        self.logs_folder = Path(logs_folder)
        self.device = device
        self.recording_thread = None
        self.is_recording = False
        self.frames = []
        self.sample_rate = 44100  # Default sample rate
        self.channels = 1  # Default to mono recording

        # Ensure the logs folder exists
        self.logs_folder.mkdir(parents=True, exist_ok=True)
        self.lc.info(f"AudioNinja is ready to strike from the shadows! Logging to '{self.logs_folder}' with device '{self.device}'")

    def _record_audio(self):
        """
        Internal method to handle audio recording callback.
        """
        def callback(indata, frames, time, status):
            if status:
                self.lc.warning(f"Status: {status}")
            if self.is_recording:
                self.frames.append(indata.copy())
    
        with sd.InputStream(callback=callback, device=self.device, channels=self.channels, samplerate=self.sample_rate):
            while self.is_recording:
                sd.sleep(100)

    def start_recording(self):
        """
        Start the audio recording.
        """
        if not self.is_recording:
            self.is_recording = True
            self.frames = []
            self.recording_thread = threading.Thread(target=self._record_audio)
            self.recording_thread.start()
            self.lc.info("Ninja recording started! 🥷🔴")

    def stop_recording(self):
        """
        Stop the audio recording.
        """
        if self.is_recording:
            self.is_recording = False
            self.recording_thread.join()
            filename = self._save_recording()
            self.lc.info("Ninja recording stopped! 🥷⚪️")
            return filename

    def _save_recording(self):
        """
        Save the recorded audio to a .wav file.
        """
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.logs_folder / f"recording_{timestamp}.wav"
        
        audio_data = np.concatenate(self.frames, axis=0)
        
        # Normalize float32 data to the range [-1, 1]
        audio_data = np.clip(audio_data, -1, 1)
        
        # Convert to int16
        audio_data = (audio_data * 32767).astype(np.int16)

        with wave.open(str(filename), 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(2)  # 2 bytes for int16
            wf.setframerate(self.sample_rate)
            wf.writeframes(audio_data.tobytes())
        
        self.lc.info(f"Ninja stored the audio file at '{filename}'! 🥷📂")
        return filename



class WebcamImageSender:
    """
    Class for capturing images from the webcam and sending them to a SocketIO client.
    """

    def __init__(self, sio:socketio, lollmsCom:LoLLMsCom=None):
        """
        Initializes the WebcamImageSender class.

        Args:
            socketio (socketio.Client): The SocketIO client object.
        """
        self.sio = sio
        self.last_image = None
        self.last_change_time = None
        self.capture_thread = None
        self.is_running = False
        self.lollmsCom = lollmsCom

    def start_capture(self):
        """
        Starts capturing images from the webcam in a separate thread.
        """
        self.is_running = True
        self.capture_thread = threading.Thread(target=self.capture_image)
        self.capture_thread.start()

    def stop_capture(self):
        """
        Stops capturing images from the webcam.
        """
        self.is_running = False
        self.capture_thread.join()

    def capture_image(self):
        """
        Captures images from the webcam, checks if the image content has changed, and sends the image to the client if it remains the same for 3 seconds.
        """
        try:
            cap = cv2.VideoCapture(0)

            while self.is_running:
                ret, frame = cap.read()
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                if self.last_image is None or self.image_difference(gray) > 2:
                    self.last_image = gray
                    self.last_change_time = time.time()

                _, buffer = cv2.imencode('.jpg', frame)
                image_base64 = base64.b64encode(buffer)
                if self.sio:
                    run_async(partial(self.sio.emit,"video_stream_image", image_base64.decode('utf-8')))

            cap.release()
        except Exception as ex:
            self.lollmsCom.error("Couldn't start webcam")
            trace_exception(ex)

    def image_difference(self, image):
        """
        Calculates the difference between two images using the absolute difference method.

        Args:
            image (numpy.ndarray): The current image.

        Returns:
            int: The sum of pixel intensities representing the difference between the current image and the last image.
        """
        if self.last_image is None:
            return 0

        diff = cv2.absdiff(image, self.last_image)
        diff_sum = diff.sum()

        return diff_sum

class MusicPlayer(threading.Thread):
    """
    MusicPlayer class for playing music using pygame library.

    Attributes:
    - file_path (str): The path of the music file to be played.
    - paused (bool): Flag to indicate if the music is paused.
    - stopped (bool): Flag to indicate if the music is stopped.
    """

    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path
        self.paused = False
        self.stopped = False

    def run(self):
        """
        The main function that runs in a separate thread to play the music.
        """
        pm.ensure_packages({"pygame":""})
        import pygame

        pygame.mixer.init()
        pygame.mixer.music.load(self.file_path)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy() and not self.stopped:
            if self.paused:
                pygame.mixer.music.pause()
            else:
                pygame.mixer.music.unpause()

    def pause(self):
        """
        Pauses the music.
        """
        self.paused = True

    def resume(self):
        """
        Resumes the paused music.
        """
        self.paused = False

    def stop(self):
        """
        Stops the music.
        """
        import pygame
        self.stopped = True
        pygame.mixer.music.stop()


class RealTimeTranscription:
    def __init__(self, callback):

        # Set up PyAudio
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=1024)

        # Set the callback
        self.callback = callback

    def start(self):
        import torch
        # Start the stream
        self.stream.start_stream()

        try:
            while True:
                # Read a chunk of audio data
                data = self.stream.read(1024)

                # Convert bytes to numpy array
                data_np = np.frombuffer(data, dtype=np.int16)
                # Convert numpy array to float tensor
                data_tensor = torch.tensor(data_np).float()
                # Send the chunk to Whisper for transcription
                result = self.whisper.transcribe(data_tensor)
                
                # If the result is not empty, call the callback
                if result:
                    self.callback(transcription)
        except KeyboardInterrupt:
            # If the user hits Ctrl+C, stop the stream
            self.stop()

    def stop(self):
        # Stop the stream and clean up
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()
