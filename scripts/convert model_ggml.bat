@echo off
REM put the model to ../models/alpaca as well as the tokenizer
set filename=../models/alpaca
set tokenizer=../models/alpaca/alpaca_tokenizer.model
echo %modelPath%
echo Converting the model to the new format...
if not exist tmp\llama.cpp git clone https://github.com/ggerganov/llama.cpp.git tmp\llama.cpp
cd tmp\llama.cpp
git checkout 6c248707f51c8a50f7792e7f7787ec481881db88
cd ../..
echo Converting ...
python tmp\llama.cpp\convert-lollms-to-ggml.py "%filename%" "%tokenizer%"