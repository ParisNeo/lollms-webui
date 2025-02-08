# Information for personality.py

self is of type APScript

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