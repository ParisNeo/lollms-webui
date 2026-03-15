#!/bin/bash

PATH="$HOME/miniconda3/bin:$PATH"
export PATH
echo "Initializing conda"
$HOME/miniconda3/bin/conda init --all
echo "Initializing vllm with:"
echo "model :$1"
echo "host :$2"
echo "port :$3"
echo "max_model_len :$4"
echo "gpu_memory_utilization :$5"
source activate vllm && python -m vllm.entrypoints.openai.api_server --model "$1" --host "$2" --port "$3" --max-model-len "$4" --gpu-memory-utilization "$5" --max-num-seqs "$6"

# Wait for all background processes to finish
wait