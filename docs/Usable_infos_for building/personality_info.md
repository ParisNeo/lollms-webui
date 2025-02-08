# Information for personality.py

## Classes

### AIPersonality

```python
class AIPersonality:
    def __init__(self, personality_package_path: str | Path, lollms_paths: LollmsPaths, config: LOLLMSConfig, model: LLMBinding = None, app: LoLLMsCom = None, run_scripts = True, selected_language = None, ignore_discussion_documents_rag = False, is_relative_path = True, installation_option: InstallOption = InstallOption.INSTALL_IF_NECESSARY, callback: Callable[([str, MSG_TYPE, dict, list], bool)] = None) -> Any
    def InfoMessage(self, content, duration: int = 4, client_id = None, verbose: bool = True) -> Any
    def ShowBlockingMessage(self, content, client_id = None, verbose: bool = True) -> Any
    def HideBlockingMessage(self, client_id = None, verbose: bool = True) -> Any
    def info(self, content, duration: int = 4, client_id = None, verbose: bool = True) -> Any
    def warning(self, content, duration: int = 4, client_id = None, verbose: bool = True) -> Any
    def success(self, content, duration: int = 4, client_id = None, verbose: bool = True) -> Any
    def error(self, content, duration: int = 4, client_id = None, verbose: bool = True) -> Any
    def notify(self, content, notification_type: NotificationType = NotificationType.NOTIF_SUCCESS, duration: int = 4, client_id = None, display_type: NotificationDisplayType = NotificationDisplayType.TOAST, verbose = True) -> Any
    def new_message(self, message_text: str, message_type: MSG_TYPE = MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_SET_CONTENT, metadata = [], callback: Callable[([str, int, dict, list, Any], bool)] = None) -> Any
    def set_message_content(self, full_text: str, callback: Callable[([str, MSG_TYPE, dict, list], bool)] = None) -> Any
    def set_message_html(self, ui_text: str, callback: Callable[([str, MSG_TYPE, dict, list], bool)] = None) -> Any
    def set_message_content_invisible_to_ai(self, full_text: str, callback: Callable[([str, MSG_TYPE, dict, list], bool)] = None) -> Any
    def set_message_content_invisible_to_user(self, full_text: str, callback: Callable[([str, MSG_TYPE, dict, list], bool)] = None) -> Any
    def build_prompt(self, prompt_parts: List[str], sacrifice_id: int = -1, context_size: int = None, minimum_spare_context_size: int = None) -> Any
    def add_collapsible_entry(self, title, content) -> Any
    def internet_search_with_vectorization(self, query, quick_search: bool = False, asses_using_llm = True) -> Any
    def sink(self, s = None, i = None, d = None) -> Any
    def yes_no(self, question: str, context: str = '', max_answer_length: int = 50, conditionning = '') -> bool
    def multichoice_question(self, question: str, possible_answers: list, context: str = '', max_answer_length: int = 50, conditionning = '') -> int
    def multichoice_ranking(self, question: str, possible_answers: list, context: str = '', max_answer_length: int = 50, conditionning = '') -> int
    def step_start(self, step_text, callback: Callable[([str, MSG_TYPE, dict, list], bool)] = None) -> Any
    def step_end(self, step_text, status = True, callback: Callable[([str, int, dict, list], bool)] = None) -> Any
    def step(self, step_text, callback: Callable[([str, MSG_TYPE, dict, list], bool)] = None) -> Any
    def print_prompt(self, title, prompt) -> Any
    def fast_gen_with_images(self, prompt: str, images: list, max_generation_size: int = None, placeholders: dict = {}, sacrifice: list = ['previous_discussion'], debug: bool = False, callback = None, show_progress = False) -> str
    def fast_gen(self, prompt: str, max_generation_size: int = None, placeholders: dict = {}, sacrifice: list = ['previous_discussion'], debug: bool = False, callback = None, show_progress = False, temperature = None, top_k = None, top_p = None, repeat_penalty = None, repeat_last_n = None) -> str
    def process(self, text: str, message_type: MSG_TYPE, callback = None, show_progress = False) -> Any
    def generate_with_images(self, prompt, images, max_size, temperature = None, top_k = None, top_p = None, repeat_penalty = None, repeat_last_n = None, callback = None, debug = False, show_progress = False) -> Any
    def generate(self, prompt, max_size = None, temperature = None, top_k = None, top_p = None, repeat_penalty = None, repeat_last_n = None, callback = None, debug = False, show_progress = False) -> Any
    def setCallback(self, callback: Callable[([str, MSG_TYPE, dict, list], bool)]) -> Any
    def __str__(self) -> Any
    def load_personality(self, package_path = None) -> Any
    def remove_file(self, file_name, callback = None) -> Any
    def remove_all_files(self, callback = None) -> Any
    def add_file(self, path, client: Client, callback = None, process = True) -> Any
    def save_personality(self, package_path = None) -> Any
    def as_dict(self) -> Any
    def conditionning_commands(self) -> Any
    def logo(self) -> Any
    def version(self) -> Any
    def version(self, value) -> Any
    def author(self) -> Any
    def author(self, value) -> Any
    def name(self) -> str
    def name(self, value: str) -> Any
    def user_name(self) -> str
    def user_name(self, value: str) -> Any
    def language(self) -> str
    def category(self) -> str
    def category_desc(self) -> str
    def language(self, value: str) -> Any
    def category(self, value: str) -> Any
    def category_desc(self, value: str) -> Any
    def supported_languages(self) -> str
    def supported_languages(self, value: str) -> Any
    def selected_language(self) -> str
    def selected_language(self, value: str) -> Any
    def ignore_discussion_documents_rag(self) -> str
    def ignore_discussion_documents_rag(self, value: str) -> Any
    def personality_description(self) -> str
    def personality_description(self, description: str) -> Any
    def personality_conditioning(self) -> str
    def personality_conditioning(self, conditioning: str) -> Any
    def prompts_list(self) -> str
    def prompts_list(self, prompts: str) -> Any
    def welcome_message(self) -> str
    def welcome_message(self, message: str) -> Any
    def include_welcome_message_in_discussion(self) -> bool
    def include_welcome_message_in_discussion(self, message: bool) -> Any
    def user_message_prefix(self) -> str
    def user_message_prefix(self, prefix: str) -> Any
    def link_text(self) -> str
    def link_text(self, text: str) -> Any
    def ai_message_prefix(self) -> Any
    def ai_message_prefix(self, prefix) -> Any
    def dependencies(self) -> List[str]
    def dependencies(self, dependencies: List[str]) -> Any
    def disclaimer(self) -> str
    def disclaimer(self, disclaimer: str) -> Any
    def help(self) -> str
    def help(self, help: str) -> Any
    def commands(self) -> str
    def commands(self, commands: str) -> Any
    def model_temperature(self) -> float
    def model_temperature(self, value: float) -> Any
    def model_top_k(self) -> int
    def model_top_k(self, value: int) -> Any
    def model_top_p(self) -> float
    def model_top_p(self, value: float) -> Any
    def model_repeat_penalty(self) -> float
    def model_repeat_penalty(self, value: float) -> Any
    def model_repeat_last_n(self) -> int
    def model_repeat_last_n(self, value: int) -> Any
    def assets_list(self) -> list
    def assets_list(self, value: list) -> Any
    def processor(self) -> APScript
    def processor(self, value: APScript) -> Any
    def processor_cfg(self) -> list
    def processor_cfg(self, value: dict) -> Any
    def start_header_id_template(self) -> str
    def end_header_id_template(self) -> str
    def system_message_template(self) -> str
    def separator_template(self) -> str
    def start_user_header_id_template(self) -> str
    def end_user_header_id_template(self) -> str
    def end_user_message_id_template(self) -> str
    def start_ai_header_id_template(self) -> str
    def end_ai_header_id_template(self) -> str
    def end_ai_message_id_template(self) -> str
    def system_full_header(self) -> str
    def user_full_header(self) -> str
    def ai_full_header(self) -> str
    def system_custom_header(self, ai_name) -> str
    def ai_custom_header(self, ai_name) -> str
    def detect_antiprompt(self, text: str) -> bool
    def replace_keys(input_string, replacements) -> Any
    def verify_rag_entry(self, query, rag_entry) -> Any
    def translate(self, text_chunk, output_language = 'french', max_generation_size = 3000) -> Any
    def summarize_text(self, text, summary_instruction = 'summarize', doc_name = 'chunk', answer_start = '', max_generation_size = 3000, max_summary_size = 512, callback = None, chunk_summary_post_processing = None, summary_mode = SUMMARY_MODE.SUMMARY_MODE_SEQUENCIAL) -> Any
    def smart_data_extraction(self, text, data_extraction_instruction = f'summarize the current chunk.', final_task_instruction = 'reformulate with better wording', doc_name = 'chunk', answer_start = '', max_generation_size = 3000, max_summary_size = 512, callback = None, chunk_summary_post_processing = None, summary_mode = SUMMARY_MODE.SUMMARY_MODE_SEQUENCIAL) -> Any
    def summarize_chunks(self, chunks, summary_instruction = f'summarize the current chunk.', doc_name = 'chunk', answer_start = '', max_generation_size = 3000, callback = None, chunk_summary_post_processing = None, summary_mode = SUMMARY_MODE.SUMMARY_MODE_SEQUENCIAL) -> Any
    def sequencial_chunks_summary(self, chunks, summary_instruction = 'summarize', doc_name = 'chunk', answer_start = '', max_generation_size = 3000, callback = None, chunk_summary_post_processing = None) -> Any
```

### StateMachine

```python
class StateMachine:
    def __init__(self, states_list) -> Any
    def goto_state(self, state) -> Any
    def process_state(self, command, full_context, callback: Callable[([str, MSG_TYPE, dict, list], bool)] = None, context_state: dict = None, client: Client = None) -> Any
```

### LoLLMsActionParameters

```python
class LoLLMsActionParameters:
    def __init__(self, name: str, parameter_type: Type, range: Optional[List] = None, options: Optional[List] = None, value: Any = None) -> None
    def __str__(self) -> str
    def from_str(string: str) -> LoLLMsActionParameters
    def from_dict(parameter_dict: dict) -> LoLLMsActionParameters
```

### LoLLMsActionParametersEncoder

```python
class LoLLMsActionParametersEncoder:
    def default(self, obj) -> Any
```

### LoLLMsAction

```python
class LoLLMsAction:
    def __init__(self, name, parameters: List[LoLLMsActionParameters], callback: Callable, description: str = '') -> None
    def __str__(self) -> str
    def from_str(string: str) -> LoLLMsAction
    def from_dict(action_dict: dict) -> LoLLMsAction
    def run(self) -> None
```

### APScript

```python
class APScript:
    def __init__(self, personality: AIPersonality, personality_config: TypedConfig, states_list: dict = {}, callback = None) -> None
    def sink(self, s = None, i = None, d = None) -> Any
    def settings_updated(self) -> Any
    def mounted(self) -> Any
    def get_welcome(self, welcome_message: str, client: Client) -> Any
    def selected(self) -> Any
    def execute_command(self, command: str, parameters: list = [], client: Client = None) -> Any
    def load_personality_config(self) -> Any
    def install(self) -> Any
    def uninstall(self) -> Any
    def add_file(self, path, client: Client, callback = None, process = True) -> Any
    def remove_file(self, path) -> Any
    def load_config_file(self, path, default_config = None) -> Any
    def save_config_file(self, path, data) -> Any
    def generate_with_images(self, prompt, images, max_size = None, temperature = None, top_k = None, top_p = None, repeat_penalty = None, repeat_last_n = None, callback = None, debug = False) -> Any
    def generate(self, prompt, max_size = None, temperature = None, top_k = None, top_p = None, repeat_penalty = None, repeat_last_n = None, callback = None, debug = False) -> Any
    def run_workflow(self, prompt: str, previous_discussion_text: str = '', callback: Callable[([str, MSG_TYPE, dict, list], bool)] = None, context_details: dict = None, client: Client = None) -> Any
    def compile_latex(self, file_path, pdf_latex_path = None) -> Any
    def find_numeric_value(self, text) -> Any
    def remove_backticks(self, text) -> Any
    def search_duckduckgo(self, query: str, max_results: int = 10, instant_answers: bool = True, regular_search_queries: bool = True, get_webpage_content: bool = False) -> List[Dict[(str, Union[str, None])]]
    def translate(self, text_chunk, output_language = 'french', max_generation_size = 3000) -> Any
    def summarize_text(self, text, summary_instruction = 'summarize', doc_name = 'chunk', answer_start = '', max_generation_size = 3000, max_summary_size = 512, callback = None, chunk_summary_post_processing = None, summary_mode = SUMMARY_MODE.SUMMARY_MODE_SEQUENCIAL) -> Any
    def smart_data_extraction(self, text, data_extraction_instruction = 'summarize', final_task_instruction = 'reformulate with better wording', doc_name = 'chunk', answer_start = '', max_generation_size = 3000, max_summary_size = 512, callback = None, chunk_summary_post_processing = None, summary_mode = SUMMARY_MODE.SUMMARY_MODE_SEQUENCIAL) -> Any
    def summarize_chunks(self, chunks, summary_instruction = 'summarize', doc_name = 'chunk', answer_start = '', max_generation_size = 3000, callback = None, chunk_summary_post_processing = None, summary_mode = SUMMARY_MODE.SUMMARY_MODE_SEQUENCIAL) -> Any
    def sequencial_chunks_summary(self, chunks, summary_instruction = 'summarize', doc_name = 'chunk', answer_start = '', max_generation_size = 3000, callback = None, chunk_summary_post_processing = None) -> Any
    def build_prompt_from_context_details(self, context_details: dict, custom_entries = '', suppress = []) -> Any
    def build_prompt(self, prompt_parts: List[str], sacrifice_id: int = -1, context_size: int = None, minimum_spare_context_size: int = None) -> Any
    def add_collapsible_entry(self, title, content, subtitle = '') -> Any
    def internet_search_with_vectorization(self, query, quick_search: bool = False) -> Any
    def vectorize_and_query(self, title, url, text, query, max_chunk_size = 512, overlap_size = 20, internet_vectorization_nb_chunks = 3) -> Any
    def step_start(self, step_text, callback: Callable[([str, MSG_TYPE, dict, list], bool)] = None) -> Any
    def step_end(self, step_text, status = True, callback: Callable[([str, int, dict, list], bool)] = None) -> Any
    def step(self, step_text, callback: Callable[([str, MSG_TYPE, dict, list], bool)] = None) -> Any
    def exception(self, ex, callback: Callable[([str, MSG_TYPE, dict, list], bool)] = None) -> Any
    def warning(self, warning: str, callback: Callable[([str, MSG_TYPE, dict, list], bool)] = None) -> Any
    def json(self, title: str, json_infos: dict, callback: Callable[([str, int, dict, list], bool)] = None, indent = 4) -> Any
    def set_message_html(self, html_ui: str, callback: Callable[([str, MSG_TYPE, dict, list], bool)] = None) -> Any
    def ui_in_iframe(self, html_ui: str, callback: Callable[([str, MSG_TYPE, dict, list], bool)] = None) -> Any
    def code(self, code: str, callback: Callable[([str, MSG_TYPE, dict, list], bool)] = None) -> Any
    def add_chunk_to_message_content(self, full_text: str, callback: Callable[([str, MSG_TYPE, dict, list], bool)] = None) -> Any
    def set_message_content(self, full_text: str, callback: Callable[([str, MSG_TYPE, dict, list], bool)] = None, msg_type: MSG_TYPE = MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_SET_CONTENT) -> Any
    def set_message_content_invisible_to_ai(self, full_text: str, callback: Callable[([str, MSG_TYPE, dict, list], bool)] = None) -> Any
    def set_message_content_invisible_to_user(self, full_text: str, callback: Callable[([str, MSG_TYPE, dict, list], bool)] = None) -> Any
    def execute_python(self, code, code_folder = None, code_file_name = None) -> Any
    def build_python_code(self, prompt, max_title_length = 4096) -> Any
    def make_title(self, prompt, max_title_length: int = 50) -> Any
    def plan_with_images(self, request: str, images: list, actions_list: list = [LoLLMsAction], context: str = '', max_answer_length: int = 512) -> List[LoLLMsAction]
    def plan(self, request: str, actions_list: list = [LoLLMsAction], context: str = '', max_answer_length: int = 512) -> List[LoLLMsAction]
    def parse_directory_structure(self, structure) -> Any
    def extract_code_blocks(self, text: str) -> List[dict]
    def build_and_execute_python_code(self, context, instructions, execution_function_signature, extra_imports = '') -> Any
    def yes_no(self, question: str, context: str = '', max_answer_length: int = 50, conditionning = '') -> bool
    def multichoice_question(self, question: str, possible_answers: list, context: str = '', max_answer_length: int = 50, conditionning = '') -> int
    def multichoice_ranking(self, question: str, possible_answers: list, context: str = '', max_answer_length: int = 50, conditionning = '') -> int
    def build_html5_integration(self, html, ifram_name = 'unnamed') -> Any
    def InfoMessage(self, content, client_id = None, verbose: bool = None) -> Any
    def info(self, info_text: str, callback: Callable[([str, MSG_TYPE, dict, list], bool)] = None) -> Any
    def step_progress(self, step_text: str, progress: float, callback: Callable[([str, MSG_TYPE, dict, list, AIPersonality], bool)] = None) -> Any
    def new_message(self, message_text: str, message_type: MSG_TYPE = MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_SET_CONTENT, metadata = [], callback: Callable[([str, int, dict, list, AIPersonality], bool)] = None) -> Any
    def finished_message(self, message_text: str = '', callback: Callable[([str, MSG_TYPE, dict, list], bool)] = None) -> Any
    def print_prompt(self, title, prompt) -> Any
    def fast_gen_with_images(self, prompt: str, images: list, max_generation_size: int = None, placeholders: dict = {}, sacrifice: list = ['previous_discussion'], debug: bool = False, callback = None, show_progress = False) -> str
    def fast_gen(self, prompt: str, max_generation_size: int = None, placeholders: dict = {}, sacrifice: list = ['previous_discussion'], debug: bool = False, callback = None, show_progress = False) -> str
    def mix_it_up(self, prompt: str, models, master_model, nb_rounds = 2, max_generation_size: int = None, placeholders: dict = {}, sacrifice: list = ['previous_discussion'], debug: bool = False, callback = None, show_progress = False) -> dict
    def generate_with_function_calls(self, context_details: dict, functions: List[Dict[(str, Any)]], max_answer_length: Optional[int] = None, callback = None) -> List[Dict[(str, Any)]]
    def generate_with_function_calls_and_images(self, context_details: dict, images: list, functions: List[Dict[(str, Any)]], max_answer_length: Optional[int] = None, callback = None) -> List[Dict[(str, Any)]]
    def execute_function(self, code, function_definitions = None) -> Any
    def execute_function_calls(self, function_calls: List[Dict[(str, Any)]], function_definitions: List[Dict[(str, Any)]]) -> List[Any]
    def transform_functions_to_text(self, functions) -> Any
    def transform_functions(self, functions) -> Any
    def _upgrade_prompt_with_function_info(self, context_details: dict, functions: List[Dict[(str, Any)]]) -> str
    def extract_function_calls_as_json(self, text: str) -> List[Dict[(str, Any)]]
    def interact(self, context_details, callback = None) -> Any
    def interact_with_function_call(self, context_details, function_definitions, prompt_after_execution = True, callback = None, hide_function_call = False, separate_output = False, max_nested_function_calls = 10) -> Any
    def path2url(file) -> Any
    def build_a_document_block(self, title = 'Title', link = '', content = 'content') -> Any
    def build_a_folder_link(self, folder_path, link_text = 'Open Folder') -> Any
    def build_a_file_link(self, file_path, link_text = 'Open Folder') -> Any
    def compress_js(self, code) -> Any
    def compress_python(self, code) -> Any
    def compress_html(self, code) -> Any
    def select_model(self, binding_name, model_name) -> Any
    def verify_rag_entry(self, query, rag_entry) -> Any
    def start_header_id_template(self) -> str
    def end_header_id_template(self) -> str
    def system_message_template(self) -> str
    def separator_template(self) -> str
    def start_user_header_id_template(self) -> str
    def end_user_header_id_template(self) -> str
    def end_user_message_id_template(self) -> str
    def start_ai_header_id_template(self) -> str
    def end_ai_header_id_template(self) -> str
    def end_ai_message_id_template(self) -> str
    def system_full_header(self) -> str
    def user_full_header(self) -> str
    def ai_full_header(self) -> str
    def system_custom_header(self, ai_name) -> str
    def ai_custom_header(self, ai_name) -> str
```

### AIPersonalityInstaller

```python
class AIPersonalityInstaller:
    def __init__(self, personality: AIPersonality) -> None
```

### PersonalityBuilder

```python
class PersonalityBuilder:
    def __init__(self, lollms_paths: LollmsPaths, config: LOLLMSConfig, model: LLMBinding, app = None, installation_option: InstallOption = InstallOption.INSTALL_IF_NECESSARY, callback = None) -> Any
    def build_personality(self, id: int = None) -> Any
    def get_personality(self) -> Any
    def extract_function_call(self, query) -> Any
```

## Functions

### get_element_id

```python
def get_element_id(url, text) -> Any
```

### craft_a_tag_to_specific_text

```python
def craft_a_tag_to_specific_text(url, text, caption) -> Any
```

### is_package_installed

```python
def is_package_installed(package_name) -> Any
```

### install_package

```python
def install_package(package_name) -> Any
```

### fix_json

```python
def fix_json(json_text) -> Any
```

### generate_actions

```python
def generate_actions(potential_actions: List[LoLLMsAction], parsed_text: dict) -> List[LoLLMsAction]
```

### __init__

```python
def __init__(self, personality_package_path: str | Path, lollms_paths: LollmsPaths, config: LOLLMSConfig, model: LLMBinding = None, app: LoLLMsCom = None, run_scripts = True, selected_language = None, ignore_discussion_documents_rag = False, is_relative_path = True, installation_option: InstallOption = InstallOption.INSTALL_IF_NECESSARY, callback: Callable[([str, MSG_TYPE, dict, list], bool)] = None) -> Any
```

### InfoMessage

```python
def InfoMessage(self, content, duration: int = 4, client_id = None, verbose: bool = True) -> Any
```

### ShowBlockingMessage

```python
def ShowBlockingMessage(self, content, client_id = None, verbose: bool = True) -> Any
```

### HideBlockingMessage

```python
def HideBlockingMessage(self, client_id = None, verbose: bool = True) -> Any
```

### info

```python
def info(self, content, duration: int = 4, client_id = None, verbose: bool = True) -> Any
```

### warning

```python
def warning(self, content, duration: int = 4, client_id = None, verbose: bool = True) -> Any
```

### success

```python
def success(self, content, duration: int = 4, client_id = None, verbose: bool = True) -> Any
```

### error

```python
def error(self, content, duration: int = 4, client_id = None, verbose: bool = True) -> Any
```

### notify

```python
def notify(self, content, notification_type: NotificationType = NotificationType.NOTIF_SUCCESS, duration: int = 4, client_id = None, display_type: NotificationDisplayType = NotificationDisplayType.TOAST, verbose = True) -> Any
```

### new_message

```python
def new_message(self, message_text: str, message_type: MSG_TYPE = MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_SET_CONTENT, metadata = [], callback: Callable[([str, int, dict, list, Any], bool)] = None) -> Any
```

### full

```python
def set_message_content(self, full_text: str, callback: Callable[([str, MSG_TYPE, dict, list], bool)] = None) -> Any
```

### ui

```python
def set_message_html(self, ui_text: str, callback: Callable[([str, MSG_TYPE, dict, list], bool)] = None) -> Any
```

### full_invisible_to_ai

```python
def set_message_content_invisible_to_ai(self, full_text: str, callback: Callable[([str, MSG_TYPE, dict, list], bool)] = None) -> Any
```

### full_invisible_to_user

```python
def set_message_content_invisible_to_user(self, full_text: str, callback: Callable[([str, MSG_TYPE, dict, list], bool)] = None) -> Any
```

### build_prompt

```python
def build_prompt(self, prompt_parts: List[str], sacrifice_id: int = -1, context_size: int = None, minimum_spare_context_size: int = None) -> Any
```

### add_collapsible_entry

```python
def add_collapsible_entry(self, title, content) -> Any
```

### internet_search_with_vectorization

```python
def internet_search_with_vectorization(self, query, quick_search: bool = False, asses_using_llm = True) -> Any
```

### sink

```python
def sink(self, s = None, i = None, d = None) -> Any
```

### yes_no

```python
def yes_no(self, question: str, context: str = '', max_answer_length: int = 50, conditionning = '') -> bool
```

### multichoice_question

```python
def multichoice_question(self, question: str, possible_answers: list, context: str = '', max_answer_length: int = 50, conditionning = '') -> int
```

### multichoice_ranking

```python
def multichoice_ranking(self, question: str, possible_answers: list, context: str = '', max_answer_length: int = 50, conditionning = '') -> int
```

### step_start

```python
def step_start(self, step_text, callback: Callable[([str, MSG_TYPE, dict, list], bool)] = None) -> Any
```

### step_end

```python
def step_end(self, step_text, status = True, callback: Callable[([str, int, dict, list], bool)] = None) -> Any
```

### step

```python
def step(self, step_text, callback: Callable[([str, MSG_TYPE, dict, list], bool)] = None) -> Any
```

### print_prompt

```python
def print_prompt(self, title, prompt) -> Any
```

### fast_gen_with_images

```python
def fast_gen_with_images(self, prompt: str, images: list, max_generation_size: int = None, placeholders: dict = {}, sacrifice: list = ['previous_discussion'], debug: bool = False, callback = None, show_progress = False) -> str
```

### fast_gen

```python
def fast_gen(self, prompt: str, max_generation_size: int = None, placeholders: dict = {}, sacrifice: list = ['previous_discussion'], debug: bool = False, callback = None, show_progress = False, temperature = None, top_k = None, top_p = None, repeat_penalty = None, repeat_last_n = None) -> str
```

### process

```python
def process(self, text: str, message_type: MSG_TYPE, callback = None, show_progress = False) -> Any
```

### generate_with_images

```python
def generate_with_images(self, prompt, images, max_size, temperature = None, top_k = None, top_p = None, repeat_penalty = None, repeat_last_n = None, callback = None, debug = False, show_progress = False) -> Any
```

### generate

```python
def generate(self, prompt, max_size = None, temperature = None, top_k = None, top_p = None, repeat_penalty = None, repeat_last_n = None, callback = None, debug = False, show_progress = False) -> Any
```

### setCallback

```python
def setCallback(self, callback: Callable[([str, MSG_TYPE, dict, list], bool)]) -> Any
```

### __str__

```python
def __str__(self) -> Any
```

### load_personality

```python
def load_personality(self, package_path = None) -> Any
```

### remove_file

```python
def remove_file(self, file_name, callback = None) -> Any
```

### remove_all_files

```python
def remove_all_files(self, callback = None) -> Any
```

### add_file

```python
def add_file(self, path, client: Client, callback = None, process = True) -> Any
```

### save_personality

```python
def save_personality(self, package_path = None) -> Any
```

### as_dict

```python
def as_dict(self) -> Any
```

### conditionning_commands

```python
def conditionning_commands(self) -> Any
```

### logo

```python
def logo(self) -> Any
```

### version

```python
def version(self) -> Any
```

### version

```python
def version(self, value) -> Any
```

### author

```python
def author(self) -> Any
```

### author

```python
def author(self, value) -> Any
```

### name

```python
def name(self) -> str
```

### name

```python
def name(self, value: str) -> Any
```

### user_name

```python
def user_name(self) -> str
```

### user_name

```python
def user_name(self, value: str) -> Any
```

### language

```python
def language(self) -> str
```

### category

```python
def category(self) -> str
```

### category_desc

```python
def category_desc(self) -> str
```

### language

```python
def language(self, value: str) -> Any
```

### category

```python
def category(self, value: str) -> Any
```

### category_desc

```python
def category_desc(self, value: str) -> Any
```

### supported_languages

```python
def supported_languages(self) -> str
```

### supported_languages

```python
def supported_languages(self, value: str) -> Any
```

### selected_language

```python
def selected_language(self) -> str
```

### selected_language

```python
def selected_language(self, value: str) -> Any
```

### ignore_discussion_documents_rag

```python
def ignore_discussion_documents_rag(self) -> str
```

### ignore_discussion_documents_rag

```python
def ignore_discussion_documents_rag(self, value: str) -> Any
```

### personality_description

```python
def personality_description(self) -> str
```

### personality_description

```python
def personality_description(self, description: str) -> Any
```

### personality_conditioning

```python
def personality_conditioning(self) -> str
```

### personality_conditioning

```python
def personality_conditioning(self, conditioning: str) -> Any
```

### prompts_list

```python
def prompts_list(self) -> str
```

### prompts_list

```python
def prompts_list(self, prompts: str) -> Any
```

### welcome_message

```python
def welcome_message(self) -> str
```

### welcome_message

```python
def welcome_message(self, message: str) -> Any
```

### include_welcome_message_in_discussion

```python
def include_welcome_message_in_discussion(self) -> bool
```

### include_welcome_message_in_discussion

```python
def include_welcome_message_in_discussion(self, message: bool) -> Any
```

### user_message_prefix

```python
def user_message_prefix(self) -> str
```

### user_message_prefix

```python
def user_message_prefix(self, prefix: str) -> Any
```

### link_text

```python
def link_text(self) -> str
```

### link_text

```python
def link_text(self, text: str) -> Any
```

### ai_message_prefix

```python
def ai_message_prefix(self) -> Any
```

### ai_message_prefix

```python
def ai_message_prefix(self, prefix) -> Any
```

### dependencies

```python
def dependencies(self) -> List[str]
```

### dependencies

```python
def dependencies(self, dependencies: List[str]) -> Any
```

### disclaimer

```python
def disclaimer(self) -> str
```

### disclaimer

```python
def disclaimer(self, disclaimer: str) -> Any
```

### help

```python
def help(self) -> str
```

### help

```python
def help(self, help: str) -> Any
```

### commands

```python
def commands(self) -> str
```

### commands

```python
def commands(self, commands: str) -> Any
```

### model_temperature

```python
def model_temperature(self) -> float
```

### model_temperature

```python
def model_temperature(self, value: float) -> Any
```

### model_top_k

```python
def model_top_k(self) -> int
```

### model_top_k

```python
def model_top_k(self, value: int) -> Any
```

### model_top_p

```python
def model_top_p(self) -> float
```

### model_top_p

```python
def model_top_p(self, value: float) -> Any
```

### model_repeat_penalty

```python
def model_repeat_penalty(self) -> float
```

### model_repeat_penalty

```python
def model_repeat_penalty(self, value: float) -> Any
```

### model_repeat_last_n

```python
def model_repeat_last_n(self) -> int
```

### model_repeat_last_n

```python
def model_repeat_last_n(self, value: int) -> Any
```

### assets_list

```python
def assets_list(self) -> list
```

### assets_list

```python
def assets_list(self, value: list) -> Any
```

### processor

```python
def processor(self) -> APScript
```

### processor

```python
def processor(self, value: APScript) -> Any
```

### processor_cfg

```python
def processor_cfg(self) -> list
```

### processor_cfg

```python
def processor_cfg(self, value: dict) -> Any
```

### start_header_id_template

```python
def start_header_id_template(self) -> str
```

### end_header_id_template

```python
def end_header_id_template(self) -> str
```

### system_message_template

```python
def system_message_template(self) -> str
```

### separator_template

```python
def separator_template(self) -> str
```

### start_user_header_id_template

```python
def start_user_header_id_template(self) -> str
```

### end_user_header_id_template

```python
def end_user_header_id_template(self) -> str
```

### end_user_message_id_template

```python
def end_user_message_id_template(self) -> str
```

### start_ai_header_id_template

```python
def start_ai_header_id_template(self) -> str
```

### end_ai_header_id_template

```python
def end_ai_header_id_template(self) -> str
```

### end_ai_message_id_template

```python
def end_ai_message_id_template(self) -> str
```

### system_full_header

```python
def system_full_header(self) -> str
```

### user_full_header

```python
def user_full_header(self) -> str
```

### ai_full_header

```python
def ai_full_header(self) -> str
```

### system_custom_header

```python
def system_custom_header(self, ai_name) -> str
```

### ai_custom_header

```python
def ai_custom_header(self, ai_name) -> str
```

### detect_antiprompt

```python
def detect_antiprompt(self, text: str) -> bool
```

### replace_keys

```python
def replace_keys(input_string, replacements) -> Any
```

### verify_rag_entry

```python
def verify_rag_entry(self, query, rag_entry) -> Any
```

### translate

```python
def translate(self, text_chunk, output_language = 'french', max_generation_size = 3000) -> Any
```

### summarize_text

```python
def summarize_text(self, text, summary_instruction = 'summarize', doc_name = 'chunk', answer_start = '', max_generation_size = 3000, max_summary_size = 512, callback = None, chunk_summary_post_processing = None, summary_mode = SUMMARY_MODE.SUMMARY_MODE_SEQUENCIAL) -> Any
```

### smart_data_extraction

```python
def smart_data_extraction(self, text, data_extraction_instruction = f'summarize the current chunk.', final_task_instruction = 'reformulate with better wording', doc_name = 'chunk', answer_start = '', max_generation_size = 3000, max_summary_size = 512, callback = None, chunk_summary_post_processing = None, summary_mode = SUMMARY_MODE.SUMMARY_MODE_SEQUENCIAL) -> Any
```

### summarize_chunks

```python
def summarize_chunks(self, chunks, summary_instruction = f'summarize the current chunk.', doc_name = 'chunk', answer_start = '', max_generation_size = 3000, callback = None, chunk_summary_post_processing = None, summary_mode = SUMMARY_MODE.SUMMARY_MODE_SEQUENCIAL) -> Any
```

### sequencial_chunks_summary

```python
def sequencial_chunks_summary(self, chunks, summary_instruction = 'summarize', doc_name = 'chunk', answer_start = '', max_generation_size = 3000, callback = None, chunk_summary_post_processing = None) -> Any
```

### __init__

```python
def __init__(self, states_list) -> Any
```

### goto_state

```python
def goto_state(self, state) -> Any
```

### process_state

```python
def process_state(self, command, full_context, callback: Callable[([str, MSG_TYPE, dict, list], bool)] = None, context_state: dict = None, client: Client = None) -> Any
```

### __init__

```python
def __init__(self, name: str, parameter_type: Type, range: Optional[List] = None, options: Optional[List] = None, value: Any = None) -> None
```

### __str__

```python
def __str__(self) -> str
```

### from_str

```python
def from_str(string: str) -> LoLLMsActionParameters
```

### from_dict

```python
def from_dict(parameter_dict: dict) -> LoLLMsActionParameters
```

### default

```python
def default(self, obj) -> Any
```

### __init__

```python
def __init__(self, name, parameters: List[LoLLMsActionParameters], callback: Callable, description: str = '') -> None
```

### __str__

```python
def __str__(self) -> str
```

### from_str

```python
def from_str(string: str) -> LoLLMsAction
```

### from_dict

```python
def from_dict(action_dict: dict) -> LoLLMsAction
```

### run

```python
def run(self) -> None
```

### __init__

```python
def __init__(self, personality: AIPersonality, personality_config: TypedConfig, states_list: dict = {}, callback = None) -> None
```

### sink

```python
def sink(self, s = None, i = None, d = None) -> Any
```

### settings_updated

```python
def settings_updated(self) -> Any
```

### mounted

```python
def mounted(self) -> Any
```

### get_welcome

```python
def get_welcome(self, welcome_message: str, client: Client) -> Any
```

### selected

```python
def selected(self) -> Any
```

### execute_command

```python
def execute_command(self, command: str, parameters: list = [], client: Client = None) -> Any
```

### load_personality_config

```python
def load_personality_config(self) -> Any
```

### install

```python
def install(self) -> Any
```

### uninstall

```python
def uninstall(self) -> Any
```

### add_file

```python
def add_file(self, path, client: Client, callback = None, process = True) -> Any
```

### remove_file

```python
def remove_file(self, path) -> Any
```

### load_config_file

```python
def load_config_file(self, path, default_config = None) -> Any
```

### save_config_file

```python
def save_config_file(self, path, data) -> Any
```

### generate_with_images

```python
def generate_with_images(self, prompt, images, max_size = None, temperature = None, top_k = None, top_p = None, repeat_penalty = None, repeat_last_n = None, callback = None, debug = False) -> Any
```

### generate

```python
def generate(self, prompt, max_size = None, temperature = None, top_k = None, top_p = None, repeat_penalty = None, repeat_last_n = None, callback = None, debug = False) -> Any
```

### run_workflow

```python
def run_workflow(self, prompt: str, previous_discussion_text: str = '', callback: Callable[([str, MSG_TYPE, dict, list], bool)] = None, context_details: dict = None, client: Client = None) -> Any
```

### compile_latex

```python
def compile_latex(self, file_path, pdf_latex_path = None) -> Any
```

### find_numeric_value

```python
def find_numeric_value(self, text) -> Any
```

### remove_backticks

```python
def remove_backticks(self, text) -> Any
```

### search_duckduckgo

```python
def search_duckduckgo(self, query: str, max_results: int = 10, instant_answers: bool = True, regular_search_queries: bool = True, get_webpage_content: bool = False) -> List[Dict[(str, Union[str, None])]]
```

### translate

```python
def translate(self, text_chunk, output_language = 'french', max_generation_size = 3000) -> Any
```

### summarize_text

```python
def summarize_text(self, text, summary_instruction = 'summarize', doc_name = 'chunk', answer_start = '', max_generation_size = 3000, max_summary_size = 512, callback = None, chunk_summary_post_processing = None, summary_mode = SUMMARY_MODE.SUMMARY_MODE_SEQUENCIAL) -> Any
```

### smart_data_extraction

```python
def smart_data_extraction(self, text, data_extraction_instruction = 'summarize', final_task_instruction = 'reformulate with better wording', doc_name = 'chunk', answer_start = '', max_generation_size = 3000, max_summary_size = 512, callback = None, chunk_summary_post_processing = None, summary_mode = SUMMARY_MODE.SUMMARY_MODE_SEQUENCIAL) -> Any
```

### summarize_chunks

```python
def summarize_chunks(self, chunks, summary_instruction = 'summarize', doc_name = 'chunk', answer_start = '', max_generation_size = 3000, callback = None, chunk_summary_post_processing = None, summary_mode = SUMMARY_MODE.SUMMARY_MODE_SEQUENCIAL) -> Any
```

### sequencial_chunks_summary

```python
def sequencial_chunks_summary(self, chunks, summary_instruction = 'summarize', doc_name = 'chunk', answer_start = '', max_generation_size = 3000, callback = None, chunk_summary_post_processing = None) -> Any
```

### build_prompt_from_context_details

```python
def build_prompt_from_context_details(self, context_details: dict, custom_entries = '', suppress = []) -> Any
```

### build_prompt

```python
def build_prompt(self, prompt_parts: List[str], sacrifice_id: int = -1, context_size: int = None, minimum_spare_context_size: int = None) -> Any
```

### add_collapsible_entry

```python
def add_collapsible_entry(self, title, content, subtitle = '') -> Any
```

### internet_search_with_vectorization

```python
def internet_search_with_vectorization(self, query, quick_search: bool = False) -> Any
```

### vectorize_and_query

```python
def vectorize_and_query(self, title, url, text, query, max_chunk_size = 512, overlap_size = 20, internet_vectorization_nb_chunks = 3) -> Any
```

### step_start

```python
def step_start(self, step_text, callback: Callable[([str, MSG_TYPE, dict, list], bool)] = None) -> Any
```

### step_end

```python
def step_end(self, step_text, status = True, callback: Callable[([str, int, dict, list], bool)] = None) -> Any
```

### step

```python
def step(self, step_text, callback: Callable[([str, MSG_TYPE, dict, list], bool)] = None) -> Any
```

### exception

```python
def exception(self, ex, callback: Callable[([str, MSG_TYPE, dict, list], bool)] = None) -> Any
```

### warning

```python
def warning(self, warning: str, callback: Callable[([str, MSG_TYPE, dict, list], bool)] = None) -> Any
```

### json

```python
def json(self, title: str, json_infos: dict, callback: Callable[([str, int, dict, list], bool)] = None, indent = 4) -> Any
```

### ui

```python
def set_message_html(self, html_ui: str, callback: Callable[([str, MSG_TYPE, dict, list], bool)] = None) -> Any
```

### ui_in_iframe

```python
def ui_in_iframe(self, html_ui: str, callback: Callable[([str, MSG_TYPE, dict, list], bool)] = None) -> Any
```

### code

```python
def code(self, code: str, callback: Callable[([str, MSG_TYPE, dict, list], bool)] = None) -> Any
```

### chunk

```python
def add_chunk_to_message_content(self, full_text: str, callback: Callable[([str, MSG_TYPE, dict, list], bool)] = None) -> Any
```

### full

```python
def set_message_content(self, full_text: str, callback: Callable[([str, MSG_TYPE, dict, list], bool)] = None, msg_type: MSG_TYPE = MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_SET_CONTENT) -> Any
```

### full_invisible_to_ai

```python
def set_message_content_invisible_to_ai(self, full_text: str, callback: Callable[([str, MSG_TYPE, dict, list], bool)] = None) -> Any
```

### full_invisible_to_user

```python
def set_message_content_invisible_to_user(self, full_text: str, callback: Callable[([str, MSG_TYPE, dict, list], bool)] = None) -> Any
```

### execute_python

```python
def execute_python(self, code, code_folder = None, code_file_name = None) -> Any
```

### build_python_code

```python
def build_python_code(self, prompt, max_title_length = 4096) -> Any
```

### make_title

```python
def make_title(self, prompt, max_title_length: int = 50) -> Any
```

### plan_with_images

```python
def plan_with_images(self, request: str, images: list, actions_list: list = [LoLLMsAction], context: str = '', max_answer_length: int = 512) -> List[LoLLMsAction]
```

### plan

```python
def plan(self, request: str, actions_list: list = [LoLLMsAction], context: str = '', max_answer_length: int = 512) -> List[LoLLMsAction]
```

### parse_directory_structure

```python
def parse_directory_structure(self, structure) -> Any
```

### extract_code_blocks

```python
def extract_code_blocks(self, text: str) -> List[dict]
```

### build_and_execute_python_code

```python
def build_and_execute_python_code(self, context, instructions, execution_function_signature, extra_imports = '') -> Any
```

### yes_no

```python
def yes_no(self, question: str, context: str = '', max_answer_length: int = 50, conditionning = '') -> bool
```

### multichoice_question

```python
def multichoice_question(self, question: str, possible_answers: list, context: str = '', max_answer_length: int = 50, conditionning = '') -> int
```

### multichoice_ranking

```python
def multichoice_ranking(self, question: str, possible_answers: list, context: str = '', max_answer_length: int = 50, conditionning = '') -> int
```

### build_html5_integration

```python
def build_html5_integration(self, html, ifram_name = 'unnamed') -> Any
```

### InfoMessage

```python
def InfoMessage(self, content, client_id = None, verbose: bool = None) -> Any
```

### info

```python
def info(self, info_text: str, callback: Callable[([str, MSG_TYPE, dict, list], bool)] = None) -> Any
```

### step_progress

```python
def step_progress(self, step_text: str, progress: float, callback: Callable[([str, MSG_TYPE, dict, list, AIPersonality], bool)] = None) -> Any
```

### new_message

```python
def new_message(self, message_text: str, message_type: MSG_TYPE = MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_SET_CONTENT, metadata = [], callback: Callable[([str, int, dict, list, AIPersonality], bool)] = None) -> Any
```

### finished_message

```python
def finished_message(self, message_text: str = '', callback: Callable[([str, MSG_TYPE, dict, list], bool)] = None) -> Any
```

### print_prompt

```python
def print_prompt(self, title, prompt) -> Any
```

### fast_gen_with_images

```python
def fast_gen_with_images(self, prompt: str, images: list, max_generation_size: int = None, placeholders: dict = {}, sacrifice: list = ['previous_discussion'], debug: bool = False, callback = None, show_progress = False) -> str
```

### fast_gen

```python
def fast_gen(self, prompt: str, max_generation_size: int = None, placeholders: dict = {}, sacrifice: list = ['previous_discussion'], debug: bool = False, callback = None, show_progress = False) -> str
```

### mix_it_up

```python
def mix_it_up(self, prompt: str, models, master_model, nb_rounds = 2, max_generation_size: int = None, placeholders: dict = {}, sacrifice: list = ['previous_discussion'], debug: bool = False, callback = None, show_progress = False) -> dict
```

### generate_with_function_calls

```python
def generate_with_function_calls(self, context_details: dict, functions: List[Dict[(str, Any)]], max_answer_length: Optional[int] = None, callback = None) -> List[Dict[(str, Any)]]
```

### generate_with_function_calls_and_images

```python
def generate_with_function_calls_and_images(self, context_details: dict, images: list, functions: List[Dict[(str, Any)]], max_answer_length: Optional[int] = None, callback = None) -> List[Dict[(str, Any)]]
```

### execute_function

```python
def execute_function(self, code, function_definitions = None) -> Any
```

### execute_function_calls

```python
def execute_function_calls(self, function_calls: List[Dict[(str, Any)]], function_definitions: List[Dict[(str, Any)]]) -> List[Any]
```

### transform_functions_to_text

```python
def transform_functions_to_text(self, functions) -> Any
```

### transform_functions

```python
def transform_functions(self, functions) -> Any
```

### _upgrade_prompt_with_function_info

```python
def _upgrade_prompt_with_function_info(self, context_details: dict, functions: List[Dict[(str, Any)]]) -> str
```

### extract_function_calls_as_json

```python
def extract_function_calls_as_json(self, text: str) -> List[Dict[(str, Any)]]
```

### interact

```python
def interact(self, context_details, callback = None) -> Any
```

### interact_with_function_call

```python
def interact_with_function_call(self, context_details, function_definitions, prompt_after_execution = True, callback = None, hide_function_call = False, separate_output = False, max_nested_function_calls = 10) -> Any
```

### path2url

```python
def path2url(file) -> Any
```

### build_a_document_block

```python
def build_a_document_block(self, title = 'Title', link = '', content = 'content') -> Any
```

### build_a_folder_link

```python
def build_a_folder_link(self, folder_path, link_text = 'Open Folder') -> Any
```

### build_a_file_link

```python
def build_a_file_link(self, file_path, link_text = 'Open Folder') -> Any
```

### compress_js

```python
def compress_js(self, code) -> Any
```

### compress_python

```python
def compress_python(self, code) -> Any
```

### compress_html

```python
def compress_html(self, code) -> Any
```

### select_model

```python
def select_model(self, binding_name, model_name) -> Any
```

### verify_rag_entry

```python
def verify_rag_entry(self, query, rag_entry) -> Any
```

### start_header_id_template

```python
def start_header_id_template(self) -> str
```

### end_header_id_template

```python
def end_header_id_template(self) -> str
```

### system_message_template

```python
def system_message_template(self) -> str
```

### separator_template

```python
def separator_template(self) -> str
```

### start_user_header_id_template

```python
def start_user_header_id_template(self) -> str
```

### end_user_header_id_template

```python
def end_user_header_id_template(self) -> str
```

### end_user_message_id_template

```python
def end_user_message_id_template(self) -> str
```

### start_ai_header_id_template

```python
def start_ai_header_id_template(self) -> str
```

### end_ai_header_id_template

```python
def end_ai_header_id_template(self) -> str
```

### end_ai_message_id_template

```python
def end_ai_message_id_template(self) -> str
```

### system_full_header

```python
def system_full_header(self) -> str
```

### user_full_header

```python
def user_full_header(self) -> str
```

### ai_full_header

```python
def ai_full_header(self) -> str
```

### system_custom_header

```python
def system_custom_header(self, ai_name) -> str
```

### ai_custom_header

```python
def ai_custom_header(self, ai_name) -> str
```

### __init__

```python
def __init__(self, personality: AIPersonality) -> None
```

### __init__

```python
def __init__(self, lollms_paths: LollmsPaths, config: LOLLMSConfig, model: LLMBinding, app = None, installation_option: InstallOption = InstallOption.INSTALL_IF_NECESSARY, callback = None) -> Any
```

### build_personality

```python
def build_personality(self, id: int = None) -> Any
```

### get_personality

```python
def get_personality(self) -> Any
```

### extract_function_call

```python
def extract_function_call(self, query) -> Any
```

### replace

```python
def replace(match) -> Any
```

