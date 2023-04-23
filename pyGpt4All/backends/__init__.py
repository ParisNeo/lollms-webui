from pyGpt4All.backends.llama_cpp import LLAMACPP
from pyGpt4All.backends.gpt_j import GPT_J
from pyGpt4All.backends.transformers import Transformers

BACKENDS_LIST={
    "llama_cpp":LLAMACPP,
    "gpt_j":GPT_J,
    "transformers":Transformers
}
