@echo off
@echo off
set filename=../models/ggml-alpaca-7b-q4.bin
set newname=../models/ggml-alpaca-7b-q4.bin.original

echo %modelPath%
echo Converting the model to the new format...
if not exist tmp\llama.cpp git clone https://github.com/ggerganov/llama.cpp.git tmp\llama.cpp
cd tmp\llama.cpp
git checkout 0f07cacb05f49704d35a39aa27cfd4b419eb6f8d
move /y "%filename%" "%filename%.original"
python tmp\llama.cpp\migrate-ggml-2023-03-30-pr613.py "%filename%.original" "%filename%"