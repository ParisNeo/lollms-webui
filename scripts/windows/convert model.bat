@echo off
@echo off
set filename=../models/%1
set newname=../models/%1.original

echo %modelPath%
echo Converting the model to the new format...
if not exist tmp\llama.cpp git clone https://github.com/ggerganov/llama.cpp.git tmp\llama.cpp
cd tmp\llama.cpp
cd ../..
move /y "%filename%" "%newname%"
echo Converting ...
python tmp\llama.cpp\convert.py "%newname%" --outfile "%filename%"