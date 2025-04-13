## LoLLMs Personality Documentation

This documentation explains the structure and process for creating personalities for the LoLLMs framework.

### 1. Introduction: What is a LoLLMs Personality?

A LoLLMs personality defines how the AI interacts, its specific knowledge, capabilities, and potentially custom workflows. It encapsulates:

*   **Identity:** Name, author, description, welcome message.
*   **Conditioning:** Instructions that guide the Large Language Model (LLM) on how to behave and respond (the `personality_conditioning` in `config.yaml`).
*   **Configuration:** Default LLM parameters (temperature, top_k, etc.) and personality-specific settings.
*   **Behavior (Optional but Powerful):** Custom Python code that allows for complex logic, interaction with external tools, state management, and customized input/output processing.

There are two main types:

1.  **Simple Personalities:** Defined solely by a `config.yaml` file. They rely entirely on the LLM's capabilities guided by the conditioning prompt. Good for straightforward conversational agents or role-playing.
2.  **Scripted Personalities:** Include a `config.yaml` *and* a `scripts/processor.py` file containing a `Processor` class inheriting from `APScript`. This allows for:
    *   Custom installation steps (installing Python packages, downloading models).
    *   Loading and managing personality-specific configurations.
    *   Intercepting and modifying user input before sending it to the LLM.
    *   Processing the LLM's output before sending it to the user.
    *   Executing complex workflows involving multiple steps, API calls, file manipulation, etc.
    *   Defining and handling custom commands.
    *   Interacting with the LoLLMs UI beyond simple text (e.g., showing images, buttons, custom HTML).
    *   Managing internal state across interactions.

This documentation primarily focuses on **Scripted Personalities**.

### 2. Core Components

*   **`AIPersonality` Class (`lollms/personality.py`):**
    *   The core class representing *any* personality (simple or scripted).
    *   Loads the `config.yaml`.
    *   Loads the `Processor` from `scripts/processor.py` if it exists.
    *   Provides access to the main `LOLLMSConfig`, `LollmsPaths`, and the loaded `LLMBinding` (the language model).
    *   Holds basic personality attributes (name, author, etc.).
    *   Offers fundamental methods for text generation (`generate`, `generate_with_images`, `fast_gen`), file handling (`add_file`), and prompt building.
    *   You typically interact with this class *through* your `Processor` instance via `self.personality`.

*   **`config.yaml` (Personality Root Folder):**
    *   Defines the static aspects of the personality.
    *   Contains metadata (author, name, version, description, category).
    *   Specifies conditioning prompts (`personality_conditioning`, `user_message_prefix`, `ai_message_prefix`).
    *   Sets default model parameters (`model_temperature`, `model_top_k`, etc.).
    *   Lists dependencies (`dependencies`) if any (though `requirements.txt` is preferred for scripted personalities).
    *   Defines custom commands (`commands`) available to the user.
    *   Includes help text (`help`) and disclaimers (`disclaimer`).
    *   Crucially for scripted personalities, the `processor_cfg` section can control aspects of the `APScript` execution (see Artbot example: `custom_workflow: true`).

*   **`APScript` Class (`lollms/personality.py`):**
    *   The base class for all personality processors (`Processor`).
    *   Provides a rich set of helper methods for interacting with the LLM, the LoLLMs UI, the file system, external services, and managing state.
    *   Handles the loading and saving of the *dynamic* personality configuration (usually stored in `lollms_personal_path/personal_config/personalities/<personality_name>/config.yaml`).
    *   Implements a basic `StateMachine` for command handling.

*   **`Processor` Class (`scripts/processor.py`):**
    *   **This is the class you create.**
    *   Must be named exactly `Processor`.
    *   Must inherit from `APScript`.
    *   Contains your custom Python logic.

### 3. Building a Scripted Personality (`Processor` Class)

#### 3.1. File Structure

A typical scripted personality has the following structure:

```
<personality_name>/
├── config.yaml             # Static configuration
├── assets/                 # Optional: Images, CSS, JS, HTML templates
│   └── logo.png            # Optional: Personality logo
│   └── ...
├── scripts/
│   └── processor.py        # Your custom logic
├── requirements.txt        # Optional: Python package dependencies
└── ...                     # Optional: Other data files, language folders, etc.
```

#### 3.2. The `Processor` Class Definition

Your `scripts/processor.py` must contain a class named `Processor` that inherits from `APScript`.

```python
# <personality_name>/scripts/processor.py
import subprocess
from pathlib import Path
from lollms.helpers import ASCIIColors
from lollms.config import TypedConfig, BaseConfig, ConfigTemplate # For dynamic config
from lollms.types import MSG_OPERATION_TYPE
from lollms.personality import APScript, AIPersonality
from lollms.utilities import PromptReshaper, discussion_path_to_url
# ... potentially other imports ...
from lollms.client_session import Client # Important for interacting with client state
from lollms.prompting import LollmsContextDetails # To get detailed context

class Processor(APScript):
    """
    Your custom personality processor documentation.
    Explain what this personality does.
    """
    def __init__(
                 self,
                 personality: AIPersonality, # An instance of the AIPersonality class
                 callback: Callable | None = None, # Optional callback function for UI updates
                ) -> None:
        """
        Initializes the Processor instance.

        Args:
            personality (AIPersonality): The AIPersonality instance containing
                                         configuration and shared resources.
            callback (Callable | None): Optional function to send messages
                                        back to the UI.
        """
        # --- Dynamic Configuration Setup (Example from Artbot) ---
        # 1. Define the structure and defaults of your dynamic config
        personality_config_template = ConfigTemplate(
            [
                # {"name":"setting_name", "type":"str/int/float/bool", "value":default_value, "help":"Description"},
                {"name":"activate_discussion_mode","type":"bool","value":True,"help":"Description..."},
                {"name":"sd_model_name","type":"str","value":"default_model", "options":["default_model", "other_model"], "help":"Description..."},
                {"name":"steps","type":"int","value":40, "min":10, "max":1024},
                # ... more settings ...
            ]
        )
        # 2. Create a BaseConfig instance from the template
        personality_config_vals = BaseConfig.from_template(personality_config_template)

        # 3. Create the TypedConfig object, linking the template and values
        personality_config = TypedConfig(
            personality_config_template,
            personality_config_vals
        )

        # 4. Call the parent APScript.__init__
        #    This handles loading the dynamic config file or creating it
        #    if it doesn't exist, and runs the install() method if needed.
        super().__init__(
                            personality,    # Pass the AIPersonality instance
                            personality_config, # Pass your TypedConfig object
                            states_list={}, # Optional: Define states for StateMachine (see advanced usage)
                            callback=callback   # Pass the callback for UI updates
                        )
        # --- End Dynamic Configuration Setup ---

        # --- Your Custom Initialization ---
        # Access configurations:
        # self.personality             # The AIPersonality instance
        # self.config                  # The main LOLLMSConfig instance
        # self.personality_config      # Your TypedConfig instance (access values like self.personality_config.steps)
        # self.personality.app         # Access to the LoLLMsCom application object (for notifications etc.)
        # self.personality.model       # Access to the LLM binding

        # Example: Load resources, initialize variables
        # self.my_tool = MyTool()
        # self.current_state_variable = None
        # ...

    # --- Override APScript Methods as Needed ---
    # (See section 3.3 below)

    # --- Define Your Custom Methods ---
    # def my_custom_logic(self, input_data):
    #     # ...
    #     pass

    # def _internal_helper(self):
    #     # ...
    #     pass

```

**Key points about `__init__`:**

1.  **Signature:** It *must* accept `personality: AIPersonality` and `callback: Callable | None = None`.
2.  **Dynamic Configuration:** The `ConfigTemplate`, `BaseConfig`, `TypedConfig` setup is the standard way to manage settings that the *user can change* through the personality's settings UI. These settings are saved separately from the main `config.yaml`.
3.  **`super().__init__`:** This call is crucial. It initializes the `APScript` base class, loads the dynamic configuration (`self.personality_config`), handles installation via the `install()` method if necessary, and sets up the callback.
4.  **Accessing Resources:** Inside your `Processor`, you can access:
    *   `self.personality`: The `AIPersonality` instance.
    *   `self.personality_config`: Your dynamic `TypedConfig` object (e.g., `self.personality_config.steps`).
    *   `self.config`: The main LoLLMs application config (`LOLLMSConfig`).
    *   `self.personality.model`: The loaded LLM binding (`LLMBinding`).
    *   `self.personality.app`: The main `LoLLMsCom` application instance (useful for `self.personality.app.notify`, `self.personality.app.tti`, etc.).
    *   `self.personality.lollms_paths`: Access to various LoLLMs paths.

#### 3.3. Key `APScript` Methods to Override or Use

You will primarily interact with the LoLLMs framework by overriding specific methods from `APScript` or calling its helper methods.

**Methods to Override (Lifecycle & Core Logic):**

*   **`install(self)`:**
    *   **Purpose:** Executed the first time the personality is loaded or if `InstallOption.FORCE_INSTALL` is used. Ideal for installing Python dependencies, downloading models, or setting up required resources.
    *   **Example (Artbot):** Installs packages from `requirements.txt`.
    *   **Note:** Use `PackageManager.install_package("package_name")` or `subprocess.run(["pip", "install", ...])`. Use `self.personality.lollms_paths` to find personality folders.
    ```python
    def install(self):
        super().install() # Recommended to call parent install first
        self.personality.app.ShowBlockingMessage("Installing Artbot dependencies...")
        requirements_file = self.personality.personality_package_path / "requirements.txt"
        if requirements_file.exists():
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "-r", str(requirements_file)], check=True)
                self.personality.app.HideBlockingMessage()
            except subprocess.CalledProcessError as ex:
                self.personality.app.HideBlockingMessage()
                self.error(f"Failed to install requirements: {ex}")
                # Handle installation failure appropriately
        else:
            self.personality.app.HideBlockingMessage()
            self.info("No requirements.txt file found.")
        # You might also download models here using requests or other libraries
    ```

*   **`uninstall(self)`:**
    *   **Purpose:** Called when the personality is explicitly uninstalled. Use this to clean up any resources created during installation (e.g., remove downloaded models, although be cautious not to remove user data).

*   **`run_workflow(self, context_details:LollmsContextDetails, client:Client, callback: Callable)`:**
    *   **Purpose:** This is the **main entry point** for processing a user's prompt when `processor_cfg.custom_workflow` is `true` in `config.yaml`. It receives the full context and should orchestrate the personality's response generation.
    *   **Parameters:**
        *   `context_details` (`LollmsContextDetails`): An object containing detailed context like `prompt`, `conditionning`, `discussion_messages`, `image_files`, `is_continue`, etc. Access fields like `context_details.prompt`.
        *   `client` (`Client`): Represents the specific client connection, useful for client-specific state or accessing discussion metadata (`client.discussion.get_metadata()`).
        *   `callback` (`Callable`): The function to send updates back to the UI (same as `self.callback`).
    *   **Implementation:** Typically, you'll extract the user's prompt, potentially process it, call generation methods (`self.fast_gen`, `self.generate_with_function_calls`, etc.), format the output, and send it back using `self.set_message_content` or other UI methods.
    *   **Return Value:** The final generated text string (or potentially other data if handled differently by the UI).
    *   **Example (Conceptual based on Artbot's `main_process`):**
    ```python
    def run_workflow(self, context_details:LollmsContextDetails, client:Client=None, callback: Callable=None):
        prompt = context_details.prompt
        full_context = context_details.get_discussion_to() # Get discussion history as string
        self.callback = callback # Store callback if needed elsewhere

        # --- Your custom logic ---
        # 1. Analyze prompt (e.g., is it a command, a generation request?)
        if prompt.startswith("help"):
             self.help(prompt, full_context, client)
             return "" # Return empty if handled

        # 2. Prepare context for LLM (maybe summarize, add specific instructions)
        prepared_prompt = self.build_prompt([
            self.personality.personality_conditioning, # Base conditioning
            "Instructions: Focus on visual details...",
            full_context,
            prompt,
            context_details.ai_prefix # Use the correct AI prefix
        ], sacrifice_id=2) # Sacrifice discussion if too long

        # 3. Call LLM generation
        self.step_start("Generating response...")
        generated_text = self.fast_gen(prepared_prompt, callback=self.sink) # Use sink for progress dots
        self.step_end("Generating response...")

        # 4. Process LLM output (e.g., extract code, call functions)
        if "```python" in generated_text:
             codes = self.extract_code_blocks(generated_text)
             # ... execute code ...
             processed_output = "Executed code..."
        else:
             processed_output = generated_text

        # 5. Format and send output to UI
        self.set_message_content(processed_output) # Send final text to UI

        return processed_output # Return the final text
    ```

*   **`execute_command(self, command: str, parameters:list=[], client:Client=None)`:**
    *   **Purpose:** Handles custom commands defined in the `commands` section of `config.yaml`. `APScript` provides a basic state machine implementation. You can define command handlers directly in the `states_list` passed to `super().__init__` or override this method for more complex command routing.
    *   **See Artbot:** Artbot defines commands like `help`, `new_image`, `regenerate` in its `states_list`.

*   **`handle_request(self, data: dict, client:Client=None) -> Dict[str, Any]`:**
    *   **Purpose:** Handles asynchronous requests sent from custom JavaScript in your UI elements (e.g., button clicks).
    *   **Parameters:**
        *   `data` (`dict`): The JSON data sent from the JavaScript `fetch` call.
        *   `client` (`Client`): The client instance.
    *   **Return Value:** A dictionary, typically containing `{"status": True/False, "message": "optional message"}`.
    *   **Example (Artbot):** Handles clicks on generated images for variation or setting as img2img source.

*   **`settings_updated(self)`:**
    *   **Purpose:** Called automatically when the user saves changes to the personality's dynamic configuration (`self.personality_config`) in the UI. Use this to react to setting changes (e.g., reload a model, change internal variables).

*   **`mounted(self)` / `selected(self)`:**
    *   **Purpose:** Lifecycle hooks called when the personality is loaded/selected in the UI. Useful for initial setup that needs to happen *after* installation and config loading.

*   **`get_welcome(self, welcome_message:str, client:Client)`:**
    *   **Purpose:** Allows you to dynamically modify the welcome message (defined in `config.yaml`) when a new discussion starts.
    *   **Return Value:** The potentially modified welcome message string.

#### 3.4. Using `APScript` Helper Methods

`APScript` provides numerous methods to simplify common tasks. Access them via `self.*`. Here's a categorized overview (refer to `lollms/personality.py` for full signatures):

**UI Interaction & Messaging:**

*   `self.new_message(text, msg_type, metadata)`: Starts a *new* message bubble in the UI.
*   `self.set_message_content(text)`: Sets the entire content of the *current* message bubble.
*   `self.add_chunk_to_message_content(chunk)`: Appends text to the *current* message bubble (streaming).
*   `self.set_message_html(html_content)`: Replaces the *current* message content with raw HTML.
*   `self.step_start(message)`: Displays a "step started" message in the UI's progress area.
*   `self.step_end(message, status=True)`: Displays a "step ended" message (success/failure).
*   `self.step(message)`: Displays an intermediate step message.
*   `self.step_progress(message, progress_percentage)`: Updates a progress bar associated with a step.
*   `self.info(message)`, `self.warning(message)`, `self.error(message)`, `self.success(message)`: Send simple notifications (usually toasts).
*   `self.InfoMessage(message)`: Shows a blocking modal message box.
*   `self.ShowBlockingMessage(message)`, `self.HideBlockingMessage()`: Show/hide a persistent blocking overlay.
*   `self.json(title, data_dict)`: Displays formatted JSON data in the UI.
*   `self.build_*_message(text)`: Helpers to build styled message elements (success, error, warning, info, progress, thinking).
*   `self.add_collapsible_entry(title, content, ...)`: Adds a collapsible UI element.
*   `self.build_a_folder_link(path, client, text)`, `self.build_a_file_link(...)`: Creates links that trigger backend actions to open folders/files.

**LLM Generation:**

*   `self.generate(prompt, max_size, ...)`: Standard text generation.
*   `self.generate_with_images(prompt, images, ...)`: Text generation with image context (for multimodal models).
*   `self.fast_gen(prompt, max_size, ...)`: A wrapper around `generate` that often includes prompt reshaping for context management.
*   `self.fast_gen_with_images(...)`: Wrapper for `generate_with_images`.
*   `self.generate_code(prompt, language, template, ...)`: Generates code, often expecting it within markdown blocks. Handles continuation.
*   `self.generate_codes(...)`: Generates multiple code blocks.
*   `self.generate_text(prompt, template, ...)`: Similar to `generate_code` but for plain text within markdown.
*   `self.generate_structured_content(prompt, template, output_format, ...)`: Generates structured data (JSON/YAML) based on a template.
*   `self.generate_with_function_calls(context_details, functions, ...)`: Generates text and attempts to extract function calls based on provided definitions.
*   `self.interact(context_details, ...)`: A high-level method often used for simple conversational turns.
*   `self.interact_with_function_call(...)`: Orchestrates generation, function execution, and potential follow-up generation.
*   `self.mix_it_up(prompt, models, master_model, ...)`: Experimental multi-model generation.

**Text & Data Processing:**

*   `self.summarize_text(text, instruction, ...)`: Summarizes text, handling chunking if necessary.
*   `self.sequential_summarize(...)`: Summarizes long text chunk by chunk, maintaining memory.
*   `self.summarize_chunks(...)`: Summarizes a list of text chunks.
*   `self.extract_code_blocks(text, return_remaining_text)`: Extracts code from markdown ``` blocks. Returns a list of dicts with content, type, filename etc.
*   `self.extract_text_from_tag(text, tag_name)`: Extracts text between custom `<tag>` and `</tag>`.
*   `self.remove_backticks(text)`: Removes leading/trailing markdown code backticks.
*   `self.update_code_with_best_match(original_content, original_code, new_code)`: Uses `difflib` to replace a code snippet within larger content.
*   `self.parse_code_replacement(text)`: Parses a specific `# REPLACE`/`# ORIGINAL`/`# SET` format.
*   `self.compress_js(code)`, `self.compress_python(code)`, `self.compress_html(code)`: Basic code compression/minification.
*   `self.make_title(prompt, ...)`: Generates a short title based on a prompt.

**File Handling & System Interaction:**

*   `self.add_file(path, client, process=True)`: Adds a file to the personality's context (potentially vectorizing it).
*   `self.remove_file(path)`: Removes a file from the context.
*   `self.execute_python(code, code_folder, code_file_name)`: Executes Python code in a subprocess. **Use with extreme caution due to security risks.**
*   `self.compile_latex(file_path, ...)`: Compiles a LaTeX file using `pdflatex`.

**External Services & Utilities:**

*   `self.search_duckduckgo(query, ...)`: Performs a web search using DuckDuckGo.
*   `self.internet_search_with_vectorization(query, ...)`: Performs web search, retrieves pages, vectorizes content, and returns relevant chunks.
*   `self.vectorize_and_query(title, url, text, query, ...)`: Vectorizes given text and performs a similarity search.
*   `self.yes_no(question, context, ...)`: Asks the LLM a yes/no question based on context.
*   `self.multichoice_question(question, options, ...)`: Asks the LLM to choose one option from a list.
*   `self.multichoice_ranking(question, options, ...)`: Asks the LLM to rank options.
*   `self.plan(request, actions_list, ...)`: Asks the LLM to create a plan using predefined `LoLLMsAction` objects.
*   `self.path2url(file_path)`: Converts a local file path in the `outputs` folder to a web-accessible URL.

**Function Calling Specific:**

*   `self.execute_function(code, function_definitions)`: Executes a single function call JSON string.
*   `self.execute_function_calls(calls_list, function_definitions)`: Executes a list of function call dictionaries.
*   `self.transform_functions_to_text(functions)`: Formats function definitions into a text block for the LLM prompt.
*   `self.transform_functions(functions)`: Formats function definitions into OpenAI-compatible tool format.
*   `self._upgrade_prompt_with_function_info(...)`: Internal helper to add function info to a prompt.
*   `self.extract_function_calls_as_json(text)`: Extracts function call JSON from markdown blocks.

**Configuration:**

*   `self.load_config_file(path, default_config)`: Loads a generic YAML file.
*   `self.save_config_file(path, data)`: Saves data to a generic YAML file.
*   `self.load_personality_config()`: Loads the dynamic personality config (called by `__init__`).

**Prompt Building:**

*   `self.build_prompt(parts_list, sacrifice_id, ...)`: Intelligently combines prompt parts, potentially truncating one part (`sacrifice_id`) to fit the context window.

#### 3.5. State Management (Optional)

`APScript` inherits from `StateMachine`. You can define states and command handlers within those states by passing a `states_list` dictionary to `super().__init__`.

```python
# In __init__
states = [
    {
        "name": "idle",
        "commands": {
            "generate": self.handle_generation,
            "summarize": self.handle_summarization,
        },
        "default": self.handle_chat # Fallback for non-command input
    },
    {
        "name": "summarizing",
        "commands": {
            "cancel": self.cancel_summarization,
        },
        "default": self.reject_while_summarizing
    }
]
super().__init__(personality, personality_config, states_list=states, callback=callback)

# Methods referenced in states_list
def handle_generation(self, command, full_context, client):
    # ... logic ...
    self.goto_state("idle") # Or stay in the same state

def handle_summarization(self, command, full_context, client):
    self.goto_state("summarizing")
    # ... start summarization ...

def cancel_summarization(self, command, full_context, client):
    # ... cleanup ...
    self.goto_state("idle")

# ... other handlers ...
```

You can then use `self.goto_state("state_name")` to transition between states. When input arrives, `APScript` (via `execute_command` or `run_workflow` if you call `self.process_state` within it) will look for the command in the current state's `commands` dictionary or call the `default` handler for that state.

### 4. The `config.yaml` File in Detail

This file defines the static properties and default settings.

```yaml
# Metadata
ai_message_prefix: 'artbot'  # How the AI signs its messages
author: ParisNeo
name: Artbot             # The personality's display name
version: 4.0.0
category: art             # Helps organize personalities in the UI
personality_description: | # Multi-line description shown in UI
  An art and illustration generation AI...
dependencies: []          # List of other personalities this one depends on (rarely used)
disclaimer: ''            # Optional disclaimer message shown on selection

# Conversation Flow
language: english         # Default language (can be overridden)
user_message_prefix: 'user' # Prefix for user messages in the prompt context
user_name: user           # Default user name
ai_message_prefix: 'artbot' # Prefix for AI messages in the prompt context (redundant with top one?)
link_text: '\n'          # Separator used between messages (rarely change)
personality_conditioning: '' # IMPORTANT: Base instructions for the LLM. Empty here as Artbot uses run_workflow
include_welcome_message_in_discussion: False # Whether the welcome message is part of the context history
welcome_message: |        # Multi-line welcome message for new discussions
  Welcome to Artbot 4...
help: |                   # Help text shown to the user
  Artbot uses auto1111's stable diffusion...

# Custom Commands (for UI buttons and potentially chat commands)
commands:
  - name: Send File       # Button Label / Command Name
    value: send_file      # The actual command string sent to execute_command
    icon: 'feather:file-plus' # Icon for the button (Feather icons)
    is_file: true         # Indicates this command triggers a file upload dialog
    file_types: .png,.jpg,.bmp # Allowed file extensions
    help: sends a file... # Tooltip for the button
  - name: New Image
    value: new_image
    icon: 'feather:file'
    help: start
  # ... more commands

# Hallucination Control
anti_prompts: []          # List of strings. If the LLM outputs any of these, generation stops.

# Default Model Parameters (can be overridden by main settings or dynamic config)
model_temperature: 0.9
model_n_predicts: 1024 # Max tokens to generate per turn
model_top_k: 50
model_top_p: 0.50
model_repeat_penalty: 1.9
model_repeat_last_n: 30

# Processor Configuration (Specific to APScript)
processor_cfg:
  custom_workflow: true     # If true, run_workflow is called. If false, standard prompt building happens.
  process_model_input: false # If true, allows Processor to modify prompt before sending to LLM (rarely needed with custom_workflow)
  process_model_output: false # If true, allows Processor to modify LLM output (rarely needed with custom_workflow)

# Example Prompts (Optional, can be used by the personality itself)
prompts_list:
  - "Surreal landscape..."
  - "Abstract geometric..."
```

### 5. Putting It Together: Artbot Example

1.  **`config.yaml`:** Defines the name "Artbot", category "art", welcome message, help text, and commands (`send_file`, `new_image`, `regenerate`, `show_settings`). Crucially, `processor_cfg.custom_workflow: true` tells LoLLMs to call `Artbot/scripts/processor.py:Processor.run_workflow`.
2.  **`scripts/processor.py`:**
    *   `__init__`: Sets up the dynamic `TypedConfig` for Stable Diffusion settings (model, sampler, steps, width, height, etc.). Calls `super().__init__` which loads these settings or installs dependencies (`requirements.txt`) if needed.
    *   `install()`: Runs `pip install -r requirements.txt`.
    *   `run_workflow()`: This is the main entry point. It calls `self.main_process`.
    *   `main_process()`: Contains the core logic.
        *   Checks `self.personality_config.activate_discussion_mode`. If active and the prompt isn't a generation request, it performs a simple chat turn using `self.generate`.
        *   If generating:
            *   Optionally determines resolution (`self.get_resolution`) and style (`self.get_styles`) using LLM calls (`self.generate`).
            *   Constructs a detailed prompt for the *positive* SD prompt using `self.build_prompt` and `self.generate`. It might include examples (`get_random_image_gen_prompt`).
            *   Constructs or uses a fixed *negative* SD prompt.
            *   Optionally generates a title (`self.generate`).
            *   Calls `self.paint()` to interact with the Stable Diffusion service (via `self.personality.app.tti`).
            *   Uses UI helpers like `self.step_start`, `self.set_message_content`, `self.set_message_html`, `self.make_selectable_photo` to show progress and results.
    *   `add_file()`: Overrides the base method to handle image uploads, optionally captioning them using `self.personality.model.interrogate_blip` and displaying them.
    *   `execute_command()` handlers (`help`, `new_image`, `regenerate`, `show_settings`): Implement the logic for the commands defined in `config.yaml`.
    *   `handle_request()`: Handles clicks on generated images (sent from JavaScript embedded in the HTML generated by `make_selectable_photo`).

### 6. Best Practices

*   **Modularity:** Break down complex logic in `run_workflow` or `main_process` into smaller, reusable methods within your `Processor` class.
*   **Configuration:** Use `TypedConfig` for settings the user should be able to change easily. Keep static settings in `config.yaml`.
*   **Dependencies:** List Python dependencies in `requirements.txt` for `install()` to handle.
*   **UI Feedback:** Use `step_start`, `step_end`, `step`, `info`, `warning`, `error`, `ShowBlockingMessage` generously to keep the user informed about what the personality is doing, especially during long operations.
*   **Error Handling:** Wrap potentially failing operations (API calls, file operations, subprocesses) in `try...except` blocks and report errors using `self.error()` or `self.exception()`.
*   **Security:** Be extremely cautious when using methods like `execute_python`. Avoid executing code directly from LLM output without strict validation and sandboxing if absolutely necessary.
*   **Context Management:** Use `self.build_prompt` with `sacrifice_id` or manual truncation to avoid exceeding the LLM's context limit.
*   **Clarity:** Document your `Processor` class and its methods clearly with docstrings.
