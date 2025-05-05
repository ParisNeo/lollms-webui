## LoLLMs Personality & Scripting Documentation

### Introduction

LoLLMs (Lord of Large Language Models) utilizes a powerful personality system that allows developers to customize the behavior, knowledge, and interaction style of the AI. This system is built around two core classes:

1.  **`AIPersonality`**: This is the foundational class for any personality. It handles loading configuration (`config.yaml`), managing assets, defining core attributes (like name, description, conditioning prompts), and providing basic interaction methods with the LLM binding (`generate`, `tokenize`, etc.). You generally don't inherit directly from this unless creating a fundamentally new *type* of personality structure.
2.  **`APScript`**: This class is designed specifically for **scripted personalities**. Developers inherit from `APScript` to implement custom logic, workflows, state management, tool usage (function calling), and complex interactions. `APScript` provides a rich set of helper methods to simplify common tasks like text generation, UI updates, file handling, data processing, and more. It also inherits from `StateMachine`, enabling stateful interactions.

Think of `AIPersonality` as the container and basic engine, and `APScript` as the customizable driver or brain that you implement.

### `AIPersonality` - The Foundation

This class manages the core definition and state of a personality loaded from its package folder.

**Initialization (`__init__`)**

```python
def __init__(
    self,
    personality_package_path: str|Path, # Path to the personality folder (e.g., "generic/lollms_personality")
    lollms_paths: LollmsPaths,          # LoLLMs paths configuration object
    config: LOLLMSConfig,               # Global LoLLMs configuration object
    model: LLMBinding = None,           # The loaded LLM binding instance
    app: LoLLMsCom = None,              # The main LoLLMs communication application instance
    run_scripts=True,                   # Whether to load and run the processor.py script (APScript)
    selected_language=None,             # Optional: force a specific language
    ignore_discussion_documents_rag=False, # Optional: Ignore discussion context for RAG
    is_relative_path=True,              # Is the package_path relative to the zoo or absolute?
    installation_option: InstallOption = InstallOption.INSTALL_IF_NECESSARY, # Installation behavior
    callback: Callable[[str | list | None, MSG_OPERATION_TYPE, str, Any | None], bool] = None # Default message callback
):
    # ... initialization logic ...
```

-   Loads `config.yaml` from the `personality_package_path`.
-   Sets up paths to assets, scripts, data, etc. within the personality package.
-   Initializes attributes based on `config.yaml`.
-   Optionally loads and initializes the `processor.py` (your `APScript` instance) if `run_scripts` is True.

**Key Attributes (Examples, mostly from `config.yaml`)**

*   `name`: Personality's display name.
*   `author`: Creator of the personality.
*   `personality_description`: A brief description.
*   `personality_conditioning`: The core system prompt or conditioning text.
*   `welcome_message`: The initial message shown when a new discussion starts.
*   `user_message_prefix`: Prefix for user messages in the prompt (e.g., "user:").
*   `ai_message_prefix`: Prefix for AI messages in the prompt (e.g., "assistant:").
*   `dependencies`: List of Python packages required by the personality.
*   `model_temperature`, `model_top_k`, etc.: Default generation parameters.
*   `processor_cfg`: Configuration specific to the `APScript` (loaded/saved via `APScript` helpers).
*   `logo`: PIL Image object if `assets/logo.png` exists.
*   `personality_package_path`: Path object to the personality's folder.
*   `assets_path`, `scripts_path`, `data_path`: Paths to subfolders.
*   `text_files`, `image_files`: Lists of files added to the current discussion context.
*   `vectorizer`: The vector database instance for the current discussion's RAG.

**Important Methods (Accessible via `self.personality` in `APScript`)**

*   **Generation:**
    *   `generate(prompt, max_size, ...)`: Basic text generation.
    *   `generate_with_images(prompt, images, max_size, ...)`: Text generation with image context (if model supports it).
    *   `fast_gen(prompt, max_generation_size, ...)`: Generation with automatic context reshaping based on available space. Highly recommended.
    *   `fast_gen_with_images(prompt, images, max_generation_size, ...)`: `fast_gen` with image support.
    *   `generate_code(prompt, language, template, ...)`: Generates code, expecting it within markdown code blocks. Handles continuations.
    *   `generate_text(prompt, template, ...)`: Generates text expected inside a `plaintext` markdown block.
    *   `generate_structured_content(prompt, template, output_format, ...)`: Generates structured data (JSON/YAML/XML) based on a template.
    *   `generate_text_with_tag(prompt, tag_name)`: Generates text wrapped in a specific XML-like tag. Useful for isolating specific outputs.
*   **RAG & Search:**
    *   `internet_search_with_vectorization(query, ...)`: Performs a web search, vectorizes results, and returns relevant chunks.
    *   `vectorize_and_query(title, url, text, query, ...)`: Vectorizes given text and searches within it.
*   **Decision Making:**
    *   `yes_no(question, context, ...)`: Asks the LLM a yes/no question about the context. Returns `True` or `False`.
    *   `multichoice_question(question, possible_answers, context, ...)`: Asks the LLM to choose one option from a list. Returns the index.
    *   `multichoice_ranking(question, possible_answers, context, ...)`: Asks the LLM to rank options. Returns a list of indices.
*   **File Handling:**
    *   `add_file(path, client, ...)`: Adds a file (text, image, audio) to the discussion context. Handles vectorization for text/audio transcription.
    *   `remove_file(file_name, ...)`: Removes a file from the context.
    *   `remove_all_files(...)`: Clears all added files.
*   **Text Processing:**
    *   `extract_code_blocks(text, return_remaining_text=False)`: Extracts code blocks (``` ```) from text, returning a list of dicts with content, type, filename, etc. Optionally returns text outside blocks.
    *   `extract_thinking_blocks(text)`: Extracts content from `<thinking>` or `<think>` blocks.
    *   `remove_thinking_blocks(text)`: Removes thinking blocks and their content.
    *   `extract_text_from_tag(tagged_text, tag_name)`: Extracts text from within a specific XML-like tag.
*   **UI Feedback (Low-level):** Methods like `InfoMessage`, `ShowBlockingMessage`, `HideBlockingMessage`, `notify`, `info`, `warning`, `success`, `error` are proxied from the `app` object for basic notifications. `APScript` provides more structured UI helpers.
*   **Progress Reporting (Low-level):** `step_start`, `step_end`, `step`. `APScript` wraps these.
*   **Prompt Building:**
    *   `build_prompt(prompt_parts, sacrifice_id, ...)`: Manually builds a prompt string, potentially sacrificing parts if the context is too large.
    *   `build_context(context_details, is_continue, ...)`: Builds the final prompt string from `LollmsContextDetails`.
*   **Utility:**
    *   `compute_n_predict(tokens)`: Calculates a reasonable `max_tokens` prediction length.
    *   `load_personality()`: Reloads the personality configuration.
    *   `save_personality()`: Saves the current state back to `config.yaml` (rarely needed directly).
    *   `as_dict()`: Returns the personality's configuration as a dictionary.

**Properties (Getters/Setters)**

Provide access to the attributes loaded from `config.yaml` (e.g., `self.personality.name`, `self.personality.model_temperature`). Also includes prompt template parts derived from the global config (e.g., `self.personality.system_full_header`, `self.personality.user_full_header`, `self.personality.ai_full_header`, `self.personality.separator_template`).

---

### `APScript` - The Scripting Engine

Inherit from this class in your `scripts/processor.py` file to create a scripted personality.

**Initialization (`__init__`)**

```python
class MyProcessor(APScript):
    def __init__(
        self,
        personality: AIPersonality,         # The owner AIPersonality instance
        personality_config: TypedConfig,  # Configuration object for this specific script
                                          # (Define fields using Pydantic models in your TypedConfig)
        states_list: dict = {},           # Optional: Initial states for the StateMachine
        callback = None                   # Optional: Default message callback
    ) -> None:
        # Recommended: Define your personality_config structure
        # Example:
        # personality_config_template = BaseConfigTemplate([
        #     {"name":"your_setting_name", "type":"str", "value":"", "help":"Help text"},
        #     {"name":"your_bool_setting", "type":"bool", "value":True, "help":"Another help text"},
        # ])
        # personality_config = TypedConfig(
        #     personality_config_template,
        #     BaseConfig(config={}) # Start with empty or default config
        # )

        super().__init__(personality, personality_config, states_list, callback)

        # Custom initialization here
        # Load configuration: self.personality_config.load_config() or rely on auto-load
        # Access settings: self.personality_config.your_setting_name
```

-   Receives the parent `AIPersonality` instance.
-   Receives a `TypedConfig` object. **This is crucial for defining custom settings** for your personality script that users can configure in the UI. You define the structure using `BaseConfigTemplate` and `TypedConfig`.
-   The script automatically tries to load saved settings from `personal_configuration_path/personalities/<personality_folder_name>/config.yaml`.
-   If the config file doesn't exist or `installation_option` forces it, `self.install()` is called automatically during initialization.

**Core Lifecycle/Callback Methods (Implement These)**

*   `install(self)`: Called automatically if the script's config file is missing or installation is forced. Use this to:
    *   Install dependencies listed in `AIPersonality.dependencies` using `self.personality.app.ShowBlockingMessage` and `subprocess.check_call(['pip', 'install', ...])`.
    *   Download necessary models or data files.
    *   Set up initial configuration values in `self.personality_config`.
    *   **Crucially:** Call `self.personality_config.save_config()` at the end if you modify settings.
*   `uninstall(self)`: (Optional) Implement cleanup logic if needed when the personality is removed.
*   `run_workflow(self, context_details: LollmsContextDetails, client: Client, callback: Callable)`: **The main entry point for your personality's logic.**
    *   This is called whenever the user sends a message and expects a reply.
    *   `context_details`: A `LollmsContextDetails` object containing the full conversation history, conditioning, RAG data, user prompt, etc. Use `context_details.build_prompt(self.personality.app.template)` to get the prompt string or use `self.fast_gen`.
    *   `client`: The `Client` object representing the user connection.
    *   `callback`: The function to send messages back to the UI (use the helper methods below instead of calling this directly).
    *   Inside this method, you'll typically:
        *   Analyze the user prompt (`context_details.prompt`).
        *   Fetch RAG data if needed (`context_details.rag_content`).
        *   Call LLM generation methods (`self.fast_gen`, `self.generate_code`, etc.).
        *   Use function calling (`self.generate_with_function_calls`, `self.execute_function_calls`).
        *   Use planning (`self.plan`).
        *   Update the UI (`self.add_chunk_to_message_content`, `self.set_message_html`, `self.step`, etc.).
        *   Manage state if using the `StateMachine` features.
    *   Return `None` or any relevant result (though output is usually sent via callbacks).
*   `get_welcome(self, welcome_message: str, client: Client)`: (Optional) Override to customize the welcome message dynamically when a new discussion starts. Return the desired welcome string.
*   `settings_updated(self)`: (Optional) Called when the user changes settings for this personality script in the UI. Use this to react to changes (e.g., reload resources).
*   `mounted(self)`: (Optional) Called once when the personality is first loaded by the server.
*   `selected(self)`: (Optional) Called when this personality is selected by a user in the UI.
*   `handle_request(self, data: dict, client: Client)`: (Optional) Implement to handle custom API requests sent to `/execute_personality_command/<personality_name>/<your_endpoint>`. Useful for interactive UI elements. Return a JSON response.

**Helper Methods (Call These in Your Script)**

These simplify interaction with the LLM, UI, and system.

*   **Generation:**
    *   `generate(prompt, max_size, ...)`: Proxies to `self.personality.generate`.
    *   `generate_with_images(prompt, images, max_size, ...)`: Proxies to `self.personality.generate_with_images`.
    *   `fast_gen(prompt, max_generation_size, ...)`: Proxies to `self.personality.fast_gen`. **Recommended**.
    *   `fast_gen_with_images(prompt, images, max_generation_size, ...)`: Proxies to `self.personality.fast_gen_with_images`. **Recommended**.
    *   `generate_code(prompt, language, template, ...)`: Proxies to `self.personality.generate_code`.
    *   `generate_codes(prompt, ...)`: Similar to `generate_code` but may return multiple blocks.
    *   `generate_text(prompt, template, ...)`: Proxies to `self.personality.generate_text`.
    *   `generate_structured_content(prompt, template, output_format, ...)`: Proxies to `self.personality.generate_structured_content`.
    *   `generate_text_with_tag(prompt, tag_name)`: Proxies to `self.personality.generate_text_with_tag`.
    *   `mix_it_up(prompt, models, master_model, ...)`: Experimental multi-model generation.
    *   `answer(context_details, ...)`: A convenient wrapper around `fast_gen` using `context_details`.
*   **Function Calling / Tool Use:**
    *   `function_definitions`: **Attribute (List[Dict])**. Define your available tools/functions here in the specified format (see example in `APScript` source). Each entry needs `function_name`, `function_description`, `function_parameters` (list of dicts with `name`, `type`, `description`), and `function` (the actual callable Python function).
    *   `generate_with_function_calls(context_details, functions, ...)`: Generates text and attempts to extract function calls based on the provided `functions` list. Returns `(generated_text, function_calls, text_without_code)`.
    *   `generate_with_function_calls_and_images(...)`: Same as above but with image support.
    *   `execute_function_calls(function_calls, function_definitions)`: Executes a list of parsed function calls using the callables from `function_definitions`. Returns a list of results.
    *   `interact_with_function_call(context_details, function_definitions, ...)`: A high-level wrapper that handles generation, function call extraction, execution, and potentially re-prompting with results. Returns the final textual output.
*   **Action Planning:**
    *   `plan(request, actions_list, context, ...)`: Asks the LLM to generate a sequence of actions (from `actions_list`) to fulfill the `request`. Uses `LoLLMsAction` objects. Returns `(list_of_LoLLMsAction_instances, raw_json_output)`.
*   **UI Interaction / Feedback:**
    *   `step_start(step_text, callback=None)`: Shows a "step started" indicator in the UI.
    *   `step_end(step_text, status=True, callback=None)`: Shows a "step ended" indicator (success/failure).
    *   `step(step_text, callback=None)`: Shows an intermediate step message.
    *   `step_progress(step_text, progress, callback=None)`: Shows a step with a progress percentage (0.0 to 1.0).
    *   `info(info_text, callback=None)`: Sends simple informational text to the current message block.
    *   `warning(warning_text, callback=None)`: Sends a warning message.
    *   `error(error_text, callback=None)`: Sends an error message.
    *   `exception(ex, callback=None)`: Sends an exception message.
    *   `json(title, json_infos, callback=None, indent=4)`: Displays formatted JSON data in the UI.
    *   `set_message_html(html_ui, callback=None)`: Replaces the *entire* current message block with the provided HTML.
    *   `ui_in_iframe(html_ui, callback=None)`: Displays the provided HTML inside an iframe within the message block. Useful for complex UIs or isolating styles.
    *   `code(code_text, callback=None)`: Sends text formatted as code (likely uses markdown).
    *   `add_chunk_to_message_content(chunk, callback=None)`: Appends text to the current message block (streaming). **Use this for generation callbacks.**
    *   `set_message_content(full_text, callback=None)`: Replaces the content of the current message block with `full_text`.
    *   `set_message_content_invisible_to_ai(full_text, callback=None)`: Sends text to the UI, but it won't be included in future prompts to the AI.
    *   `set_message_content_invisible_to_user(full_text, callback=None)`: Includes text in the context for the AI, but it's not displayed in the UI.
    *   `new_message(message_text, message_type, metadata, callback=None)`: Starts a *new* message block in the discussion UI.
    *   `finished_message(message_text, callback=None)`: Signals that the *current* message generation is fully complete.
    *   `InfoMessage(content, client_id, ...)`: Shows a modal message box (proxied from `self.personality.app`).
    *   `build_message_element(...)`, `build_success_message(...)`, etc.: Helpers to create styled HTML snippets for use with `set_message_html`.
    *   `build_a_document_block(title, link, content)`: Creates a styled HTML block for displaying document snippets.
    *   `build_a_folder_link(folder_path, client, link_text)`: Creates an HTML link that, when clicked, asks the LoLLMs server to open the specified folder on the server machine.
    *   `build_a_file_link(file_path, client, link_text)`: Creates an HTML link to open a specific file on the server.
*   **File Handling:**
    *   `add_file(path, client, ...)`: Proxies to `self.personality.add_file`.
    *   `remove_file(path)`: Removes a file added via `add_file`.
*   **Data Processing / Summarization:**
    *   `summarize_text(text, summary_instruction, ...)`: Summarizes text, automatically handling chunking if it's too long.
    *   `smart_data_extraction(text, data_extraction_instruction, final_task_instruction, ...)`: Similar to `summarize_text` but designed for extracting specific information and potentially reformulating it.
    *   `summarize_chunks(chunks, summary_instruction, ...)`: Summarizes a pre-chunked list of text. Supports sequential (memory-based) or parallel summarization.
    *   `sequential_summarize(text, chunk_processing_prompt, final_memory_processing_prompt, ...)`: A detailed sequential summarization method with explicit prompts for chunk processing and final output generation.
*   **Code Execution / Handling:**
    *   `execute_python(code, code_folder, code_file_name)`: Executes Python code in a subprocess and returns stdout/stderr.
    *   `build_python_code(prompt, ...)`: Asks the LLM to generate Python code based on a prompt.
    *   `extract_code_blocks(text, return_remaining_text=False)`: Proxies to `self.personality.extract_code_blocks`.
    *   `update_code_with_best_match(original_content, original_code, new_code)`: Uses `difflib` to find `original_code` within `original_content` and replaces it with `new_code`, preserving indentation.
    *   `parse_code_replacement(input_text)`: Parses a specific text format (`# ORIGINAL ... # SET ...`) to extract old and new code snippets for replacement tasks.
*   **Web/Search:**
    *   `internet_search_with_vectorization(query, ...)`: Proxies to `self.personality.internet_search_with_vectorization`.
    *   `search_duckduckgo(query, max_results, ...)`: Performs a direct DuckDuckGo search.
*   **RAG/Vectorization:**
    *   `vectorize_and_query(title, url, text, query, ...)`: Proxies to `self.personality.vectorize_and_query`.
    *   `verify_rag_entry(query, rag_entry)`: Asks the LLM (using `yes_no`) if a RAG chunk is relevant to the query.
*   **Decision Making / Parsing:**
    *   `yes_no(question, context, ...)`: Proxies to `self.personality.yes_no`.
    *   `multichoice_question(question, possible_answers, ...)`: Proxies to `self.personality.multichoice_question`.
    *   `multichoice_ranking(question, possible_answers, ...)`: Proxies to `self.personality.multichoice_ranking`.
*   **Utility:**
    *   `print_prompt(title, prompt)`: Prints a formatted prompt to the console (useful for debugging).
    *   `make_title(prompt, max_title_length)`: Asks the LLM to generate a concise title for a prompt.
    *   `translate(text_chunk, output_language, ...)`: Asks the LLM to translate text.
    *   `compress_js(code)`, `compress_python(code)`, `compress_html(code)`: Basic code compression/minification utilities.
    *   `parse_directory_structure(structure)`: Parses a text-based tree structure into a list of paths.
    *   `compile_latex(file_path, pdf_latex_path)`: Compiles a `.tex` file to PDF using `pdflatex`.
    *   `find_numeric_value(text)`: Extracts the first numeric value from text using regex.
    *   `remove_backticks(text)`: Removes markdown code block backticks from the start/end of a string.
    *   `extract_text_from_tag(tagged_text, tag_name)`: Proxies to `self.personality.extract_text_from_tag`.
*   **Configuration:**
    *   `load_personality_config()`: Loads the script's specific config (`personal_configuration_path/.../<personality>/config.yaml`).
    *   `load_config_file(path, default_config)`: Loads an arbitrary YAML file.
    *   `save_config_file(path, data)`: Saves data to an arbitrary YAML file. (Use `self.personality_config.save_config()` for the script's main config).
*   **Model Selection:**
    *   `select_model(binding_name, model_name)`: Tells the LoLLMs server to switch the active model.
*   **Prompt Building:**
    *   `build_prompt(prompt_parts, sacrifice_id, ...)`: Proxies to `self.personality.build_prompt`.
    *   Access prompt template parts via `self.start_header_id_template`, `self.separator_template`, `self.system_full_header`, `self.user_full_header`, `self.ai_full_header`, etc.

**State Machine Integration**

Since `APScript` inherits from `StateMachine`, you can define states and transitions.

*   **Define States:** Pass a `states_list` dictionary to the `super().__init__()`. The structure is:
    ```python
    states_list = [
        {
            "name": "state_name_1",
            "commands": { # Commands specific to this state
                "!command1": self.handle_command1,
                "!command2": self.handle_command2,
            },
            "default": self.handle_default_state1 # Function called if no specific command matches
        },
        {
            "name": "state_name_2",
            "commands": { ... },
            "default": self.handle_default_state2
        }
    ]
    ```
*   **Process Input:** In `run_workflow` or command handlers, call `self.process_state(command_text, full_context, callback, context_state, client)` to execute the appropriate function based on the current state.
*   **Change State:** Call `self.goto_state("state_name_2")` or `self.goto_state(1)` to transition to another state.

**Configuration (`self.personality_config`)**

*   Define your script's settings using `BaseConfigTemplate` and `TypedConfig`.
*   Access settings like attributes: `self.personality_config.my_setting`.
*   Load settings: `self.personality_config.load_config()` (often done automatically).
*   Save settings: `self.personality_config.save_config()` (essential after changes, especially in `install`).

### Helper Classes

*   **`StateMachine`**: Base class for state management used by `APScript`.
*   **`LoLLMsActionParameters`**: Defines a parameter for a `LoLLMsAction`.
*   **`LoLLMsAction`**: Defines an action (name, parameters, callback) that the `plan` method can use.

### Simple Example (`scripts/processor.py`)

```python
from lollms.personality import APScript, AIPersonality
from lollms.types import MSG_OPERATION_TYPE
from lollms.config import TypedConfig, BaseConfig, ConfigTemplate
from lollms.prompting import LollmsContextDetails
from lollms.client_session import Client
from typing import Callable

# Define configuration structure
cfg_template = ConfigTemplate([
    {"name":"greeting", "type":"str", "value":"Hello!", "help":"The greeting message to use."},
    {"name":"use_name", "type":"bool", "value":True, "help":"Whether to include the personality name in the response."},
])
cfg_schema = BaseConfig() # You can derive from BaseConfig for validation

class Processor(APScript):
    def __init__(
                 self,
                 personality: AIPersonality,
                 personality_config: TypedConfig = None,
                 states_list:dict = {}, # For state machine
                 callback: Callable[[str, int, dict], bool] = None,
                ) -> None:
        # Ensure personality_config is properly setup
        if personality_config is None:
            personality_config = TypedConfig(cfg_template, cfg_schema)

        super().__init__(personality, personality_config, states_list, callback)

    def install(self):
        super().install()
        # No specific installation needed for this simple example
        self.personality_config.save_config() # Save default config if installing
        self.info("Simple Greeter installed.")

    def run_workflow(self, context_details: LollmsContextDetails, client: Client, callback: Callable):
        """
        Main entry point for processing user input.
        """
        user_prompt = context_details.prompt
        self.info(f"Received prompt: {user_prompt}") # Send info to UI

        # Simple response generation
        prompt = f"User asks: {user_prompt}. Respond simply."

        # Use fast_gen for context management
        full_prompt = context_details.build_prompt(
            self.personality.app.template,
            [
                self.personality.system_full_header + self.personality.personality_conditioning,
                self.personality.user_full_header + user_prompt,
                self.personality.ai_full_header
            ]
        )

        self.step_start("Generating response...")
        # Stream the response using fast_gen and add_chunk_to_message_content
        response = self.fast_gen(full_prompt, callback=self.add_chunk_to_message_content)
        self.step_end("Generating response...")

        # Example of using config
        greeting = self.personality_config.greeting
        if self.personality_config.use_name:
            final_text = f"{greeting} I am {self.personality.name}. You asked about: '{user_prompt}'. The AI said: {response}"
        else:
            final_text = f"{greeting} You asked about: '{user_prompt}'. The AI said: {response}"

        # Send the final composed message (or could have streamed directly)
        # self.set_message_content(final_text) # Use this if not streaming

        self.finished_message() # Signal completion of the current message block

        # Example: Adding an HTML element
        html_content = self.build_success_message("Response generated successfully!")
        # Start a new message block for the HTML
        self.new_message("", MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_UI)
        self.set_message_html(html_content)
        self.finished_message()


    def get_welcome(self, welcome_message: str, client: Client) -> str:
        # Customize welcome message using config
        return f"{self.personality_config.greeting} Welcome to the {self.personality.name} personality!"

    def settings_updated(self):
        self.info("Settings have been updated!")
        # Potentially reload resources based on new settings
```

### Conclusion

By inheriting from `APScript` and utilizing its extensive helper methods, developers can create sophisticated, interactive, and tool-using personalities within the LoLLMs ecosystem. Remember to define your custom settings using `TypedConfig` and implement the necessary lifecycle methods, especially `run_workflow`.