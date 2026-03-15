#!/bin/bash

PATH="$HOME/miniconda3/bin:$PATH"
export PATH
conda activate vllm && python -m vllm.entrypoints.openai.api_server --model_name "$1" --node_name "$2" --device "$3"

# Wait for all background processes to finish
wait