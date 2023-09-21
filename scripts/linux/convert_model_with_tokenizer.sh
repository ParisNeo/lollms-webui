#!/bin/bash
## untested Linux shell script
#
FILENAME="../models/$1"
NEWNAME="../models/$1.original"

#echo %modelPath%
echo Converting the model to the new format...
#if not exist tmp\llama.cpp git clone https://github.com/ggerganov/llama.cpp.git tmp\llama.cpp
if [! -e tmp\llama.cpp]; then $(git clone https://github.com/ggerganov/llama.cpp.git tmp\llama.cpp)
cd tmp\llama.cpp
cd ../..
#move /y "%filename%" "%newname%"
mv -f $FILENAME $NEWNAME
echo Converting ...
python -c tmp\llama.cpp\convert.py \"$NEWNAME\" --outfile \"$FILENAME\" --vocab-dir $2