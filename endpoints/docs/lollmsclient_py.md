Lollms client allows the user to interact with lollms using LollmsClient and TasksLibrary.
To build an instance from lc and tl:
lc = LollmsClient(lollms_address, ctx_size=ctx_size)
tl = TasksLibrary(self.lc)
default ctx_size is 4096, but can be changed for big models like gpt4o (128000) and claude sonnet (200000)
Use the following information to construct applications for the user
MSG_TYPE is an enum that can be found in lollms_client.lollms_types
personality is an integer that is set to -1 by default
host_address can be set once at the beginning then the lc will use that one for all command.
Lollms by default uses http://localhost:9600 as default host_address

LollmsClient methods
```yaml
- name: LollmsClient
  methods:
  - 'def __init__(self, host_address=None, model_name=None, ctx_size=4096, personality=UnaryOp(op=USub(),
    operand=Constant(value=1)), n_predict=1024, min_n_predict=512=1024, temperature=0.1,
    top_k=50, top_p=0.95, repeat_penalty=0.8, repeat_last_n=40, seed=None, n_threads=8,
    service_key='''': str, tokenizer=None, default_generation_mode=Attribute(value=Name(id=''ELF_GENERATION_FORMAT'',
    ctx=Load()), attr=''LOLLMS'', ctx=Load()))'
  - 'def tokenize(self, prompt: str)'
  - 'def detokenize(self, tokens_list: list)'
  - 'def generate_with_images(self, prompt, images:List[str], n_predict=None, stream=False,
    temperature=0.1, top_k=50, top_p=0.95, repeat_penalty=0.8, repeat_last_n=40, seed=None,
    n_threads=8, service_key='''': str, stream=Falseing_callback)'
  - 'def generate(self, prompt, n_predict=None, stream=False, temperature=0.1, top_k=50,
    top_p=0.95, repeat_penalty=0.8, repeat_last_n=40, seed=None, n_threads=8, service_key='''':
    str, stream=Falseing_callback)'
  - 'def generate_text(self, prompt, host_address=None, model_name=None, personality=None,
    n_predict=None, stream=False, temperature=0.1, top_k=50, top_p=0.95, repeat_penalty=0.8,
    repeat_last_n=40, seed=None, n_threads=8, service_key='''': str, stream=Falseing_callback)'
  - 'def lollms_generate(self, prompt, host_address=None, model_name=None, personality=None,
    n_predict=None, stream=False, temperature=0.1, top_k=50, top_p=0.95, repeat_penalty=0.8,
    repeat_last_n=40, seed=None, n_threads=8, service_key='''': str, stream=Falseing_callback)'
  - 'def lollms_generate_with_images(self, prompt, images, host_address=None, model_name=None,
    personality=None, n_predict=None, stream=False, temperature=0.1, top_k=50, top_p=0.95,
    repeat_penalty=0.8, repeat_last_n=40, seed=None, n_threads=8, service_key='''':
    str, stream=Falseing_callback)'
  - 'def openai_generate(self, prompt, host_address=None, model_name=None, personality=None,
    n_predict=None, stream=False, temperature=0.1, top_k=50, top_p=0.95, repeat_penalty=0.8,
    repeat_last_n=40, seed=None, n_threads=8, completion_format=Attribute(value=Name(id=''ELF_COMPLETION_FORMAT'',
    ctx=Load()), attr=''Instruct'', ctx=Load()): ELF_COMPLETION_FORMAT, service_key='''':
    str, stream=Falseing_callback)'
  - 'def ollama_generate(self, prompt, host_address=None, model_name=None, personality=None,
    n_predict=None, stream=False, temperature=0.1, top_k=50, top_p=0.95, repeat_penalty=0.8,
    repeat_last_n=40, seed=None, n_threads=8, completion_format=Attribute(value=Name(id=''ELF_COMPLETION_FORMAT'',
    ctx=Load()), attr=''Instruct'', ctx=Load()): ELF_COMPLETION_FORMAT, service_key='''':
    str, stream=Falseing_callback)'
  - 'def litellm_generate(self, prompt, host_address=None, model_name=None, personality=None,
    n_predict=None, stream=False, temperature=0.1, top_k=50, top_p=0.95, repeat_penalty=0.8,
    repeat_last_n=40, seed=None, n_threads=8, completion_format=Attribute(value=Name(id=''ELF_COMPLETION_FORMAT'',
    ctx=Load()), attr=''Instruct'', ctx=Load()): ELF_COMPLETION_FORMAT, service_key='''':
    str, stream=Falseing_callback)'
  - 'def listMountedPersonalities(self, host_address=None: str)'
  - 'def listModels(self, host_address=None: str)'
```

Tasks library allows the user to do extra operations like summarizing text and extracting code blocks:
To extract codes from code tags we can use this code snippet
```python
response = lc.generate(prompt)
codes = tl.extract_code_blocks(response)
codes is a list of dicts, each entry has 'content' which is the extracted code text
```
codes is a list of dicts each one has the following entries:
  - 'index' (int): The index of the code block in the text.
  - 'file_name' (str): An empty string. This field is not used in the current implementation.
  - 'content' (str): The content of the code block.
  - 'type' (str): The type of the code block. If the code block starts with a language specifier (like 'python' or 'java'), this field will contain that specifier. Otherwise, it will be set to 'language-specific'.




Tasks library methods
```yaml
- name: TasksLibrary
  methods:
  - 'def __init__(self, lollms: LollmsClient)'
  - def print_prompt(self, title, prompt)
  - 'def setCallback(self, callback: Callable[None])'
  - 'def process(self, text: str, message_type: MSG_TYPE, callback, show_progress)'
  - def generate(self, prompt, max_size, temperature, top_k, top_p, repeat_penalty,
    repeat_last_n, callback, debug, show_progress, stream)
  - 'def fast_gen(self, prompt: str, max_generation_size: int, placeholders: dict,
    sacrifice: list, debug: bool, callback, show_progress, temperature, top_k, top_p,
    repeat_penalty, repeat_last_n) -> str'
  - def generate_with_images(self, prompt, images, max_size, temperature, top_k, top_p,
    repeat_penalty, repeat_last_n, callback, debug, show_progress, stream)
  - 'def fast_gen_with_images(self, prompt: str, images: list, max_generation_size:
    int, placeholders: dict, sacrifice: list, debug: bool, callback, show_progress)
    -> str'
  - def sink(self, s, i, d)
  - 'def build_prompt(self, prompt_parts: List[str], sacrifice_id: int, context_size:
    int, minimum_spare_context_size: int)'
  - 'def translate_text_chunk(self, text_chunk, output_language: str, host_address:
    str, model_name: str, temperature, max_generation_size)'
  - 'def extract_code_blocks(self, text: str) -> List[dict]'
  - 'def yes_no(self, question: str, context: str, max_answer_length: int, conditionning)
    -> bool'
  - 'def multichoice_question(self, question: str, possible_answers: list, context:
    str, max_answer_length: int, conditionning) -> int'
  - def summerize_text(self, text, summary_instruction, doc_name, answer_start, max_generation_size,
    max_summary_size, callback, chunk_summary_post_processing, summary_mode)
  - def smart_data_extraction(self, text, data_extraction_instruction, final_task_instruction,
    doc_name, answer_start, max_generation_size, max_summary_size, callback, chunk_summary_post_processing,
    summary_mode)
  - def summerize_chunks(self, chunks, summary_instruction, doc_name, answer_start,
    max_generation_size, callback, chunk_summary_post_processing, summary_mode)
  - 'def _upgrade_prompt_with_function_info(self, prompt: str, functions: List[Dict[None]])
    -> str'
  - 'def extract_function_calls_as_json(self, text: str) -> List[Dict[None]]'
  - 'def execute_function_calls(self, function_calls: List[Dict[None]], function_definitions:
    List[Dict[None]]) -> List[Any]'
  - 'def generate_with_function_calls(self, prompt: str, functions: List[Dict[None]],
    max_answer_length: Optional[int], callback: Callable[None]) -> List[Dict[None]]'
  - 'def generate_with_function_calls_and_images(self, prompt: str, images: list,
    functions: List[Dict[None]], max_answer_length: Optional[int], callback: Callable[None])
    -> List[Dict[None]]'
```
```yaml
- name: ELF_GENERATION_FORMAT
  members:
  - LOLLMS
  - OPENAI
  - OLLAMA
  - LITELLM
- name: ELF_COMPLETION_FORMAT
  members:
  - Instruct
  - Chat
```
