import os
import tkinter as tk

import customtkinter as ctk
import torch
import torchaudio
import vlc
from tkVideoPlayer import TkinterVideo
from tortoise.api import TextToSpeech
from tortoise.utils.audio import load_voice
from transformers import AutoModelForCausalLM, AutoTokenizer

# Setup the app
app = tk.Tk()
app.geometry("600x550")
app.title("Rap God v2.0")
ctk.set_appearance_mode("dark")

promptFrame = tk.Frame()
promptFrame.pack(padx=10, pady=10)
buttonFrame = tk.Frame()
buttonFrame.pack()

prompt = ctk.CTkEntry(
    promptFrame, height=40, width=300, text_color="black", fg_color="white"
)
prompt.pack(side="left", padx=10)
lyrics = ctk.CTkEntry(None, height=240, width=500, text_color="black", fg_color="white")
lyrics.pack()


def generateText():
    model = AutoModelForCausalLM.from_pretrained("stormzy").to("cuda")
    tokenizer = AutoTokenizer.from_pretrained("distilgpt2", use_fast=True)
    tokens = tokenizer.encode(prompt.get(), return_tensors="pt")
    tokens = tokens.to("cuda")
    attn_mask = torch.ones_like(tokens)
    out = model.generate(
        tokens,
        attention_mask=attn_mask,
        num_beams=5,
        early_stopping=True,
        max_length=200,
        no_repeat_ngram_size=2,
    )
    rap = tokenizer.decode(out[0])
    lyrics.delete(0, tk.END)
    lyrics.insert(0, rap)


def generateAudio():
    voice_samples, conditioning_latents = load_voice(
        "stormzy", extra_voice_dirs=["stormzy_samples"]
    )
    tts = TextToSpeech()
    gen = tts.tts_with_preset(
        lyrics.get(),
        voice_samples=voice_samples,
        conditioning_latents=conditioning_latents,
        preset="ultra_fast",
    )
    torchaudio.save("generated.wav", gen.squeeze(0).cpu(), 24000)


def playAudio():
    if os.path.exists("generated.wav"):
        p = vlc.MediaPlayer("file:///generated.wav")
        p.play()


videoplayer = TkinterVideo(master=app, scaled=True, keep_aspect=True)


def generateVideo():
    os.system("xcopy /y generated.wav .\MakeItTalk\examples")
    os.system("cd MakeItTalk & python generate.py")

    if os.path.exists("generated.wav"):
        p = vlc.MediaPlayer("file:///generated.wav")
        p.play()

    videoplayer.load("MakeItTalk\examples\stormzy_pred_fls_generated_audio_embed.mp4")
    videoplayer.pack(fill="both", expand=True)
    videoplayer.play()


genTextButton = ctk.CTkButton(
    promptFrame,
    height=40,
    width=120,
    text_color="black",
    text="Generate",
    command=generateText,
)
genTextButton.pack(side="right")
genAudioButton = ctk.CTkButton(
    buttonFrame,
    height=40,
    width=120,
    text_color="black",
    text="Syn Audio",
    command=generateAudio,
)
genAudioButton.pack(side="left", padx=10)
playAudioButton = ctk.CTkButton(
    buttonFrame,
    height=40,
    width=120,
    text_color="black",
    text="Play Rap",
    command=playAudio,
)
playAudioButton.pack(side="left", padx=10)
genVideoButton = ctk.CTkButton(
    buttonFrame,
    height=40,
    width=120,
    text_color="black",
    text="Syn Video",
    command=generateVideo,
)
genVideoButton.pack(side="left", padx=10)

# Run the app
app.mainloop()
