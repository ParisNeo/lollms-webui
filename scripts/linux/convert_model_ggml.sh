#!/bin/bash
## Untested Linux shell script
#
FILENAME="../models/alpaca"
TOKENIZER="../models/alpaca/alpaca_tokenizer.model"
# echo %modelPath%
echo Converting the model to the new format...
if [! -e tmp\llama.cpp]; then $(git clone https://github.com/ggerganov/llama.cpp.git tmp\llama.cpp)
cd tmp\llama.cpp
$(git checkout 6c248707f51c8a50f7792e7f7787ec481881db88)
cd ../..
echo Converting ...
python -c tmp\llama.cpp\convert-lollms-to-ggml.py \"$FILENAME\" \"$TOKENIZER\"