import torch
import requests
from PIL import Image
from transformers import BlipProcessor, BlipForQuestionAnswering

class BlipInterrogatorStorer():
    def __init__(self, vqa_model_name="Salesforce/blip-vqa-base"):
        self.vqa_model_name = vqa_model_name
        self.processor = BlipProcessor.from_pretrained(vqa_model_name)
        self.model = BlipForQuestionAnswering.from_pretrained(vqa_model_name, torch_dtype=torch.float16).to("cuda")

    def interrogate(self, raw_image:Image, question:str, max_length:int=256):
        inputs = self.processor(raw_image, question, return_tensors="pt").to("cuda", torch.float16)
        out = self.model.generate(**inputs, max_length=max_length)
        return self.processor.decode(out[0], skip_special_tokens=True)            

