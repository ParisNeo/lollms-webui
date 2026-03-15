# -*- coding: utf-8 -*-
# Project name: LoLLMs Function Call Builder
# File path: lollms_core/lollms/functions/functions_zoo/development/build_lollms_function_call/function.py
# Author: ParisNeo
# Creation date: 2024-07-31
# Description: This file contains the FunctionCallBuilder class, a LoLLMs classic function
#              call designed to generate the 'config.yaml' and 'function.py' files for
#              new LoLLMs function calls based on user specifications. It includes a
#              "boost mode" for self-correction using LLM reflection.

import os
import datetime
from pathlib import Path
import re
import json
import unicodedata
from typing import List, Dict, Any, Optional, Union

# LoLLMs specific imports - VERY IMPORTANT - USE THESE EXACTLY
from lollms.function_call import FunctionCall, FunctionType
from lollms.app import LollmsApplication
from lollms.client_session import Client # Correct import for Client
from lollms.prompting import LollmsContextDetails # Correct import for ContextDetails
from lollms.config import TypedConfig, ConfigTemplate, BaseConfig # For static_parameters
from lollms.types import MSG_TYPE # If using self.personality.new_message with HTML

# Logging and Dependencies
import ascii_colors as logging # Standard LoLLMs logging
from ascii_colors import trace_exception # For detailed error logging
import pipmaster as pm # FOR MANAGING PYTHON PACKAGE DEPENDENCIES


# ==============================================================================
# Utility Functions (Copied from previous correct version)
# ==============================================================================
def sanitize_path_from_user_input(path_string: str, allow_slashes: bool = False) -> str:
    """
    Sanitizes a string to be safe for use as a path component.
    """
    if not isinstance(path_string, str):
        return ""
    normalized_string = unicodedata.normalize('NFKD', path_string).encode('ascii', 'ignore').decode('ascii')
    sanitized = normalized_string.lower()
    if allow_slashes:
        sanitized = re.sub(r'[^\w\s./\\-]', '_', sanitized)
        sanitized = re.sub(r'\s+', '_', sanitized)
    else:
        sanitized = re.sub(r'[^\w\s.-]', '_', sanitized)
        sanitized = re.sub(r'\s+', '_', sanitized)
    if not allow_slashes:
        sanitized = sanitized.strip('._ ')
        sanitized = re.sub(r'_+', '_', sanitized)
        if not sanitized:
            return "_generated_name_"
    sanitized = sanitized.replace('../', '_').replace('..\\', '_')
    max_len = 200
    if len(sanitized) > max_len:
        sanitized = sanitized[:max_len].rsplit('_', 1)[0]
        if not sanitized: # pragma: no cover
             sanitized = sanitized[:max_len]
    if not sanitized: # pragma: no cover
        return "_generated_component_" if not allow_slashes else "_" 
    reserved_names = ["con", "prn", "aux", "nul",
                      "com1", "com2", "com3", "com4", "com5", "com6", "com7", "com8", "com9",
                      "lpt1", "lpt2", "lpt3", "lpt4", "lpt5", "lpt6", "lpt7", "lpt8", "lpt9"]
    if not allow_slashes and sanitized.split('.')[0] in reserved_names: # pragma: no cover
        sanitized = f"_{sanitized}"
    return sanitized


def find_first_json_block(text: str) -> Optional[Union[Dict[str, Any], List[Any]]]:
    """
    Finds the first valid JSON object or array within a markdown-style JSON code block.
    """
    if not isinstance(text, str):
        return None
    match_block = re.search(r"```json\s*([\s\S]*?)\s*```", text, re.DOTALL)
    json_str_to_parse = None
    if match_block:
        json_str_to_parse = match_block.group(1).strip()
    else:
        stripped_text = text.strip()
        if (stripped_text.startswith("{") and stripped_text.endswith("}")) or \
           (stripped_text.startswith("[") and stripped_text.endswith("]")):
            json_str_to_parse = stripped_text
    if json_str_to_parse:
        try:
            return json.loads(json_str_to_parse)
        except json.JSONDecodeError: # pragma: no cover
            return None
    return None


def snake_to_camel(snake_str: str) -> str:
    """Converts a snake_case string to CamelCase."""
    if not snake_str:
        return ""
    components = snake_str.split('_')
    return "".join(x.title() for x in components)

# ==============================================================================
# FunctionCallBuilder Class
# ==============================================================================

class FunctionCallBuilder(FunctionCall):
    """
    A LoLLMs classic function call that generates the 'config.yaml' and 'function.py'
    files for new LoLLMs function calls based on user-provided specifications.
    It supports a "boost mode" for self-correction using LLM reflection.
    """
    def __init__(self, app: LollmsApplication, client: Client):
        """
        Initializes the FunctionCallBuilder.

        Args:
            app: The LollmsApplication instance.
            client: The Client session instance.
        """
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.logger.debug(f"Initializing {self.__class__.__name__}...")

        config_template = ConfigTemplate([
            {
                "name": "boost_mode_enabled", "type": "bool", "value": False,
                "help": "Enable self-correction loops for YAML and Python generation."
            },
            {
                "name": "max_correction_iterations", "type": "int", "value": 3,
                "help": "Maximum self-correction attempts if boost mode is enabled (e.g., 1-5)."
            }
        ])
        static_params_config = TypedConfig(config_template, BaseConfig(config={}))

        super().__init__(
            function_name="build_lollms_function_call",
            app=app,
            function_type=FunctionType.CLASSIC,
            client=client,
            static_parameters=static_params_config
        )
        self.settings_updated() # Load initial static parameter values
        self.logger.info(
            f"{self.function_name} initialization complete. "
            f"Boost mode: {self.boost_mode_enabled}, "
            f"Max iterations: {self.max_correction_iterations}"
        )

    def settings_updated(self):
        """
        Called by LoLLMs when user saves static settings in the UI or on initialization.
        Reloads static parameters for this function call.
        """
        self.logger.info(f"Reloading static parameters for {self.function_name}...")
        self.boost_mode_enabled = self.static_parameters.config.get("boost_mode_enabled", False)
        self.max_correction_iterations = self.static_parameters.config.get("max_correction_iterations", 3)
        self.logger.info(
            f"Settings loaded: Boost Mode={self.boost_mode_enabled}, "
            f"Max Iterations={self.max_correction_iterations}"
        )

    def _determine_function_type_with_llm(
            self, fn_desc: str, core_logic: str, user_preference: str
        ) -> str:
        """
        Uses the LLM to determine the most appropriate LoLLMs FunctionType.
        """
        self.personality.step_start("Determining optimal function type with LLM...")
        question = (
            f"Based on the following function description and core logic, what is the most appropriate LoLLMs FunctionType?\n"
            f"Description: '{fn_desc}'\n"
            f"Core Logic: '{core_logic}'\n"
            f"User's initial preference: '{user_preference}'\n"
            "Consider if the function primarily performs a discrete action returning a direct result (CLASSIC) "
            "or if it's meant to modify context before LLM generation or process output after (CONTEXT_UPDATE)."
        )
        possible_answers = ["CLASSIC", "CONTEXT_UPDATE"]
        
        try:
            choice_result = self.personality.multichoice_question(
                question=question,
                possible_answers=possible_answers,
                callback=self.personality.sink
            )

            chosen_index = -1
            if isinstance(choice_result, int):
                chosen_index = choice_result
            elif isinstance(choice_result, dict) and "index" in choice_result: # pragma: no cover
                chosen_index = choice_result["index"]

            if 0 <= chosen_index < len(possible_answers):
                llm_choice = possible_answers[chosen_index]
                self.personality.step_end(f"LLM suggested type: {llm_choice}", success=True)
                self.app.info(
                    f"LLM suggested function type: {llm_choice} (User preferred: {user_preference})",
                    client_id=self.client.client_id
                )
                return llm_choice
            else: # pragma: no cover
                self.personality.step_end("LLM type determination failed. Using user preference.", success=False)
                self.app.warning(
                    f"Could not determine function type via LLM. Defaulting to user preference: {user_preference}",
                    client_id=self.client.client_id
                )
                return user_preference
        except Exception as e: # pragma: no cover
            self.logger.error(f"Error in _determine_function_type_with_llm: {e}")
            trace_exception(e)
            self.personality.step_end("Error in LLM type determination. Using user preference.", success=False)
            return user_preference

    def _generate_function_py_prompt(
            self, new_fn_name: str, class_name:str, new_fn_type_str: str,
            new_fn_core_logic: str, new_fn_params_desc: Optional[str],
            new_fn_static_params_desc: Optional[str] = None, **kwargs
        ) -> str:
        """
        Generates the prompt for creating the function.py file with detailed instructions.
        """
        matplotlib_specific_hints = """
        # --- Matplotlib/Image Specific Considerations ---
        # If your function generates images (e.g., using Matplotlib):
        # 1. Dependencies: Ensure 'matplotlib' and 'numpy' are handled using 'pipmaster'.
        #    Place this block at the TOP LEVEL of the generated function.py, before class definition:
        #    ```python
        #    # import pipmaster as pm # Make sure pipmaster is imported
        #    # import ascii_colors as logging # Make sure logging is imported for this block
        #    # _plotting_dependencies_met = False # Define at module level
        #    # try:
        #    #     logging.info("Ensuring Matplotlib and NumPy are installed...") # Add logging
        #    #     pm.ensure_packages({"matplotlib":"", "numpy":""}) # Use dictionary format
        #    #     import matplotlib.pyplot as plt # Import AFTER ensure_packages
        #    #     import numpy as np # Import AFTER ensure_packages
        #    #     _plotting_dependencies_met = True
        #    #     logging.info("Matplotlib and NumPy are available.")
        #    # except ImportError: 
        #    #     logging.error("Matplotlib or NumPy could not be imported even after ensure_packages.")
        #    # except Exception as e: # pragma: no cover
        #    #     logging.error(f"Failed to install/ensure plotting dependencies: {{e}}")
        #    #     from ascii_colors import trace_exception # Local import if not global for this block
        #    #     trace_exception(e)
        #    ```
        #
        # 2. Saving the Image (inside execute method):
        #    # discussion_folder = self.client.discussion.discussion_folder 
        #    # if not discussion_folder or not discussion_folder.exists(): # pragma: no cover
        #    #     self.logger.error("Discussion folder is not available.")
        #    #     return "Error: Discussion folder not accessible to save plot."
        #    # image_filename = f"plot_{datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d_%H%M%S_%f')}.png"
        #    # image_path = discussion_folder / image_filename
        #    # plt.savefig(image_path)
        #    # plt.close() # CRUCIAL
        #
        # 3. Displaying the Image in UI (inside execute method):
        #    # image_url = f"/discussions/{self.client.discussion.discussion_id}/{image_filename}"
        #    # html_output = f"<p>Here is your plot:</p><img src='{image_url}' alt='Generated Plot' style='max-width:100%; height:auto;'>"
        #    # self.personality.set_message_html(html_output, client_id=self.client.client_id)
        #    # return f"Plot generated and displayed. Saved as {image_filename}"
        #
        # Check the _plotting_dependencies_met flag in your execute method.
        # In __init__, you might do: `self.plotting_ready = _plotting_dependencies_met` (if global)
        """

        mandatory_signature_instructions = f"""
        # --- CRITICAL: Method Signatures and Parameter Handling ---
        # Adhere STRICTLY to the following LoLLMs method signatures.
        # DO NOT add parameters directly to the method definitions below.
        # Parameters for 'execute' MUST be extracted from the 'kwargs' dictionary.

        # `__init__` method:
        # Signature MUST BE: def __init__(self, app: LollmsApplication, client: Client):

        # `execute` method (if FunctionType.CLASSIC):
        # Signature MUST BE: def execute(self, context: LollmsContextDetails, *args, **kwargs) -> str:
        #   - The 'context' parameter MUST be type-hinted as `LollmsContextDetails`.
        #   - Inside 'execute', access parameters using: `param_value = kwargs.get("param_name_from_config_yaml", default_value_if_any)`
        #   - Prefer simple data types (str, int, float, bool, list of simple types) for parameters. Avoid complex, schemaless dicts from LLM.

        # `update_context` method (if FunctionType.CONTEXT_UPDATE):
        # Signature MUST BE: def update_context(self, context: LollmsContextDetails, constructed_context: List[str]) -> List[str]:
        #   - The 'context' parameter MUST be type-hinted as `LollmsContextDetails`.

        # `process_output` method (OPTIONAL, if FunctionType.CONTEXT_UPDATE):
        # Signature MUST BE: def process_output(self, context: LollmsContextDetails, llm_output: str) -> str:
        #   - The 'context' parameter MUST be type-hinted as `LollmsContextDetails`.
        
        # `settings_updated` method (OPTIONAL, if function uses static_parameters):
        # Signature MUST BE: def settings_updated(self):
        #   - Access updated static parameters via `self.static_parameters.config.get("setting_name")`.
        # --- END CRITICAL INSTRUCTIONS ---
        """

        core_method_stub = ""
        if new_fn_type_str.upper() == "CLASSIC":
            param_handling_example_lines = [
                f"# User described dynamic parameters like: '{new_fn_params_desc}'" if new_fn_params_desc else "# No specific dynamic parameters were described by user, but always use kwargs.get() if any are expected by config.yaml.",
                f"# Example: `param_str = kwargs.get(\"string_param_from_config\", \"default_string\")`",
                f"# Example: `param_int = kwargs.get(\"integer_param_from_config\", 0)`",
                f"# Example: `param_list = kwargs.get(\"list_param_from_config\", [])` (ensure config.yaml type is 'list')",
                f"# ALWAYS use `kwargs.get(\"param_name_as_in_config_yaml\")` to retrieve parameters for execute."
            ]
            param_handling_example = "\n        ".join(param_handling_example_lines)
            core_method_stub = f"""
    # MANDATORY SIGNATURE: def execute(self, context: LollmsContextDetails, *args, **kwargs) -> str:
    def execute(self, context: LollmsContextDetails, *args, **kwargs) -> str: # DO NOT CHANGE THIS SIGNATURE
        self.logger.info(f"Executing {{self.function_name}} with kwargs: {{kwargs}}")
        
        # --- Parameter Extraction (MUST use kwargs.get for dynamic parameters) ---
        {param_handling_example}
        # --- End Parameter Extraction ---

        # --- User's Core Logic Description ---
        # {new_fn_core_logic}
        # --- End Core Logic Description ---
        
        # Example check for plotting dependencies (if _plotting_dependencies_met is a global in generated file)
        # if 'matplotlib' not in globals() or not _plotting_dependencies_met: # A way to check if imports succeeded
        #    msg = "Error: Plotting dependencies (matplotlib/numpy) are missing or failed to load. Check server logs."
        #    self.app.error(msg, client_id=self.client.client_id)
        #    return msg

        try:
            # Replace with actual implementation
            self.personality.warning("Function logic not fully implemented in generated function. Please complete.", client_id=self.client.client_id)
            return "Function logic not fully implemented. Please complete, ensuring parameters are fetched from kwargs."
        except Exception as e: # pragma: no cover
            self.logger.error(f"Error in {{self.function_name}}: {{e}}")
            trace_exception(e)
            self.app.error(f"Error executing function {{self.function_name}}: {{str(e)}}", client_id=self.client.client_id)
            return f"Error executing {{self.function_name}}: {{str(e)}}. Check server logs."
"""
        elif new_fn_type_str.upper() == "CONTEXT_UPDATE": # pragma: no cover
            core_method_stub = f"""
    # MANDATORY SIGNATURE: def update_context(self, context: LollmsContextDetails, constructed_context: List[str]) -> List[str]:
    def update_context(self, context: LollmsContextDetails, constructed_context: List[str]) -> List[str]: # DO NOT CHANGE
        self.logger.debug(f"Executing update_context for {{self.function_name}}.")
        # --- User's Core Logic Description ---
        # {new_fn_core_logic}
        # --- End Core Logic Description ---
        try:
            # TODO: Implement logic to modify 'constructed_context'.
            # Access static parameters (if any) via self.my_static_param_name (set in settings_updated or __init__).
            pass
        except Exception as e:
            self.logger.error(f"Error in {{self.function_name}} update_context: {{e}}")
            trace_exception(e)
        return constructed_context

    # OPTIONAL - MANDATORY SIGNATURE if implemented: def process_output(self, context: LollmsContextDetails, llm_output: str) -> str:
    # def process_output(self, context: LollmsContextDetails, llm_output: str) -> str: # DO NOT CHANGE IF IMPLEMENTED
    #     self.logger.debug(f"Executing process_output for {{self.function_name}}.")
    #     # --- User's Core Logic Description (for output processing) ---
    #     try:
    #         # TODO: Implement logic to modify 'llm_output'.
    #         pass
    #     except Exception as e: # pragma: no cover
    #         self.logger.error(f"Error in {{self.function_name}} process_output: {{e}}")
    #         trace_exception(e)
    #     return llm_output
"""
        else:  # pragma: no cover
            return "Error: Invalid function type specified for Python generation."

        static_param_setup_instructions = ""
        if new_fn_static_params_desc:
            static_param_setup_instructions = f"""
     # Static parameters were described: '{new_fn_static_params_desc}'
     # Define ConfigTemplate and TypedConfig for these static parameters here, BEFORE super().__init__
     config_template = ConfigTemplate([
         # TODO: Add static parameter definitions here based on user description.
         # Example: {{"name": "api_key", "type": "str", "value": "", "help": "Your API key"}},
         # Example: {{"name": "max_items", "type": "int", "value": 10, "help": "Max items to fetch"}},
     ])
     static_params_config = TypedConfig(config_template, BaseConfig(config={{}})) # Use empty BaseConfig initially
     # Call super().__init__ passing the static_params_config
     super().__init__(
         function_name="{new_fn_name}",
         app=app,
         function_type=FunctionType.{new_fn_type_str.upper()},
         client=client,
         static_parameters=static_params_config # Pass the TypedConfig object
     )
     # It's good practice to load initial values, LoLLMs might call settings_updated automatically,
     # but an explicit call ensures instance variables are set if needed immediately.
     self.settings_updated() 
"""
        else:
            static_param_setup_instructions = f"""
     # No static parameters were described by the user.
     super().__init__(
         function_name="{new_fn_name}",
         app=app,
         function_type=FunctionType.{new_fn_type_str.upper()},
         client=client
         # No static_parameters argument here
     )
"""
        settings_updated_stub = ""
        if new_fn_static_params_desc:
            settings_updated_stub = f"""
    # MANDATORY SIGNATURE if static_parameters are used: def settings_updated(self):
    def settings_updated(self): # DO NOT CHANGE THIS SIGNATURE
        '''Called by LoLLMs when user saves static settings or on init.'''
        self.logger.info(f"Reloading static parameters for {{self.function_name}}...")
        # Access loaded/updated values from self.static_parameters.config
        # TODO: Add lines here to load each static parameter described by the user
        # (e.g., '{new_fn_static_params_desc}') into instance variables.
        # Example: self.api_key = self.static_parameters.config.get("api_key", "") 
        # Example: self.max_items = self.static_parameters.config.get("max_items", 10)
        # self.logger.info(f"Settings loaded for {{self.function_name}} with new values.")
"""

        prompt = f"""
You are an expert LoLLMs Python developer. Generate 'function.py' content for a LoLLMs function call.
{mandatory_signature_instructions}

New function specifications:
- Function Name: {new_fn_name}
- Class Name: {class_name}
- Function Type: {new_fn_type_str.upper()}
- Core Logic: {new_fn_core_logic}
- Dynamic Parameters (for CLASSIC execute()): {new_fn_params_desc if new_fn_params_desc else "N/A"}
- Static Parameters (user-configurable settings): {new_fn_static_params_desc if new_fn_static_params_desc else "N/A"}

Structure for `function.py`:
1. **Mandatory Imports at the top of the file (these are essential for LoLLMs):**
   ```python
   # Standard Libraries (examples, add as needed by core logic)
   import json
   import datetime # Use datetime.datetime for objects, e.g. datetime.datetime.now()
   from pathlib import Path
   from typing import List, Dict, Any, Optional, Union # Be specific with types

   # LoLLMs specific imports - VERY IMPORTANT - USE THESE EXACTLY
   from lollms.function_call import FunctionCall, FunctionType
   from lollms.app import LollmsApplication
   from lollms.client_session import Client # ENSURE THIS IS lollms.client_session.Client
   from lollms.prompting import LollmsContextDetails # ENSURE THIS IS lollms.prompting.LollmsContextDetails
   from lollms.config import TypedConfig, ConfigTemplate, BaseConfig # For static_parameters
   from lollms.types import MSG_TYPE # If using self.personality.new_message with HTML

   # Logging and Dependencies
   import ascii_colors as logging # Standard LoLLMs logging
   from ascii_colors import trace_exception # For detailed error logging
   import pipmaster as pm # FOR MANAGING PYTHON PACKAGE DEPENDENCIES
   ```
   **Immediately after these imports, if the function needs external packages (like matplotlib, requests, etc.),
   add a `pipmaster.ensure_packages(...)` block as shown in the Matplotlib hints. This block should be at the MODULE LEVEL (outside any class or function).**

2. Class Definition: `class {class_name}(FunctionCall):`

3. `__init__` method: (STRICT Signature: `def __init__(self, app: LollmsApplication, client: Client):`)
   - `self.logger = logging.getLogger(f"{{__name__}}.{{self.__class__.__name__}}")` (Use f-string for logger name)
   - {static_param_setup_instructions}
   - Log initialization, e.g., `self.logger.info(f"{{self.function_name}} initialized.")`

4. Core Logic Method(s) (e.g., `execute`, `update_context`):
   STRICTLY follow the signatures mentioned in CRITICAL INSTRUCTIONS.
   For CLASSIC functions, ALL dynamic parameters MUST be extracted from `kwargs` using `kwargs.get("param_name_from_config")`.
   Ensure method parameters like 'context' are correctly type-hinted with `LollmsContextDetails`.

{settings_updated_stub}

{matplotlib_specific_hints if new_fn_type_str.upper() == 'CLASSIC' else ""}

Output *only* the complete Python code for 'function.py', enclosed in ```python ... ```.
""" + core_method_stub
        return prompt

    def _get_reflection_prompt(self, content_type: str, specs: dict, generated_content: str) -> str:
        """
        Generates the prompt for LLM reflection on generated YAML or Python content.
        """
        if content_type == "yaml":
            return f"""
You are a LoLLMs expert reviewing a 'config.yaml' file for a new function call.
Original specifications:
- Name: {specs['new_fn_name']}
- Class Name: {specs['class_name']}
- Description: {specs['new_fn_desc']}
- Intended Type: {specs['new_fn_type_str']}
- Parameter Description (dynamic): {specs.get('new_fn_params_desc', 'N/A')}
- Static Parameter Description: {specs.get('new_fn_static_params_desc', 'N/A')}
- Target Category: {specs['target_category']}

Generated config.yaml:
```yaml
{generated_content}
```
Review this YAML for correctness, completeness, and LoLLMs best practices.
Checklist:
1. `author`, `version`, `creation_date_time`, `last_update_date_time`: Present and correctly formatted?
2. `category`: Matches '{specs['target_category']}'?
3. `class_name`: Correct CamelCase of '{specs['new_fn_name']}'?
4. `name`: Matches '{specs['new_fn_name']}' (snake_case)?
5. `description`: Clear, reflects '{specs['new_fn_desc']}'?
6. `parameters` (if CLASSIC & params described): 
    - All present? Names snake_case? 
    - **Types**: Are types simple and clear (e.g., "str", "int", "float", "bool", "list")? If "list", is the item type implied or clear (e.g., list of strings)? 
    - Avoid complex "dict" types unless a clear schema was provided by user; prefer simpler structures for LLM generation.
    - Descriptions clear? `required`/`default` appropriate?
7. `returns`: Correct for type (CLASSIC: status.type str; CONTEXT_UPDATE: {{}})?
8. `static_parameters` (if described): All present? Names snake_case? Types valid? `value` (default) present? `help` clear? `options` if applicable?
9. Valid YAML syntax?

Output your review ONLY as a JSON object in a ```json ... ``` block:
```json
{{
    "review_summary": "Brief assessment.",
    "num_problems_detected": <integer>,
    "problem_details": [
        {{"field_path": "path.to.field", "issue": "Description.", "suggestion": "How to fix."}}
    ]
}}
```
"""
        elif content_type == "python": # pragma: no cover
            return f"""
You are a LoLLMs expert reviewing a 'function.py' file.
Original specifications:
- Function Name: {specs['new_fn_name']}
- Class Name: {specs['class_name']}
- Intended Type: {specs['new_fn_type_str']}
- Core Logic: {specs['new_fn_core_logic']}
- Parameter Description (dynamic, CLASSIC): {specs.get('new_fn_params_desc', 'N/A')}
- Static Parameter Description: {specs.get('new_fn_static_params_desc', 'N/A')}

Generated function.py:
```python
{generated_content}
```
Review this Python code for LoLLMs best practices and adherence to STRICT LoLLMs signatures and import patterns.
Checklist:
1.  **Imports:**
    *   **CRITICAL:** Is `from lollms.client_session import Client` used (NOT `lollms.client`)?
    *   **CRITICAL:** Is `from lollms.prompting import LollmsContextDetails` imported AND used as a type hint for the `context` parameter in `execute`, `update_context`, `process_output`?
    *   Are other LoLLMs base imports present (`FunctionCall`, `FunctionType`, `LollmsApplication`, etc.)?
    *   Is `import ascii_colors as logging` and `from ascii_colors import trace_exception` used?
    *   Is `import pipmaster as pm` present?
    *   **CRITICAL (if external libs needed, e.g., matplotlib):** Is there a `pm.ensure_packages(...)` block at the **MODULE LEVEL** (after imports, before class def)?
        *   It MUST use the dictionary format: `pm.ensure_packages({{"package_name": "version_specifier", ...}})` or list `pm.ensure_packages(["package1", "package2"])`.
        *   Imports of these external libraries (e.g., `import matplotlib.pyplot as plt`) MUST occur *inside the try block after* `pm.ensure_packages` or globally after the block if a flag like `_dependencies_met` is used.
2.  Class Definition: `class {specs['class_name']}(FunctionCall):` correct?
3.  `__init__`: STRICT Signature `__init__(self, app: LollmsApplication, client: Client)` used? `self.logger = logging.getLogger(f"{{__name__}}.{{self.__class__.__name__}}")` correct? Static param setup correct (if applicable, `ConfigTemplate` before `super`)?
4.  Core Method(s) (`execute`, `update_context`, `process_output`): 
    *   STRICT SIGNATURES used? 
    *   `execute` uses `kwargs.get("param_name")` for ALL dynamic parameters?
    *   **Parameter Handling in `execute`**: Are parameters fetched from `kwargs` using simple expected types (str, int, float, bool, list of simple types)? Does it avoid trying to parse overly complex dicts from `kwargs` unless explicitly and clearly defined by user?
5.  `settings_updated` (if static params described): STRICT Signature `settings_updated(self)` used? Accesses `self.static_parameters.config.get(...)`?
6.  Python syntax/logic good? Matplotlib/image hints (if applicable) followed, especially `plt.close()` and correct image URL for UI? Logger usage correct (e.g., `self.logger.info(f"message")`)?

Output your review ONLY as a JSON object in a ```json ... ``` block:
```json
{{
    "review_summary": "Brief assessment.",
    "num_problems_detected": <integer>,
    "problem_details": [
        {{"area": "e.g., Imports, LollmsContextDetails usage, pipmaster usage, execute signature, parameter types", "line_hint": <optional int>, "issue": "Description of the problem.", "suggestion": "How to fix it according to LoLLMs best practices."}}
    ]
}}
```
"""
        return "" # Should not happen

    def _get_correction_prompt(self, content_type: str, specs: dict, previous_content: str, problem_details_str: str, now_iso:str) -> str:
        """
        Generates the prompt for LLM correction of YAML or Python content.
        """
        if content_type == "yaml":
            return f"""
You are a LoLLMs expert correcting a 'config.yaml'.
Original specs: {specs}
Previous YAML attempt:
```yaml
{previous_content}
```
Identified problems:
{problem_details_str}

Generate a new, corrected 'config.yaml' addressing these problems.
For 'parameters', prefer simple types like "str", "int", "float", "bool", or "list" (of simple types). Avoid "dict" type for parameters unless absolutely necessary and the user provided a clear schema.
Output ONLY the complete YAML in a ```yaml ... ``` block.
Set 'creation_date_time' and 'last_update_date_time' to '{now_iso}'.
"""
        elif content_type == "python": # pragma: no cover
            return f"""
You are a LoLLMs expert correcting 'function.py'.
Original specs: {specs}
Core Logic to implement: "{specs['new_fn_core_logic']}"
Previous Python attempt:
```python
{previous_content}
```
Identified problems:
{problem_details_str}

Generate a new, corrected 'function.py' addressing these problems and implementing the core logic.
STRICTLY adhere to LoLLMs method signatures (e.g., `execute(self, context: LollmsContextDetails, *args, **kwargs)`, `__init__(self, app: LollmsApplication, client: Client)`).
For `execute`, parameters MUST be fetched using `kwargs.get("param_name")` and generally treated as simple types (str, int, float, bool, list of simple types) unless complex structure is unavoidable and well-defined.
Ensure correct imports: `from lollms.client_session import Client`, AND `from lollms.prompting import LollmsContextDetails`.
The `context` parameter in `execute`, `update_context`, `process_output` MUST be type-hinted as `LollmsContextDetails`.
If external libraries are needed, use `pipmaster.ensure_packages({{"package":"version"}})` at the module level, then import the library.
Output ONLY the complete Python code in a ```python ... ``` block.
"""
        return "" # Should not happen

    def _run_generation_loop(
            self, content_type: str, specs: dict,
            initial_generation_prompt_func, reflection_prompt_func, correction_prompt_func
        ) -> tuple[str, int, int]:
        """
        Manages the generation, reflection, and correction loop.
        Returns (best_content, total_iterations, final_problems_count)
        """
        self.personality.step_start(f"Boost Mode: Generating initial {content_type}...")
        current_content = self.personality.generate_code(
            prompt=initial_generation_prompt_func(**specs), 
            language=content_type, 
            code_tag_format="markdown",
            accept_all_if_no_code_tags_is_present=False,
            callback=self.personality.sink
        )
        if not current_content or not isinstance(current_content, str): # pragma: no cover
            self.personality.step_end(f"Initial {content_type} generation failed.", success=False)
            raise ValueError(f"LLM failed to generate initial {content_type} content.")
        
        self.personality.step_end(f"Initial {content_type} generated.", success=True)

        best_content = current_content
        min_problems = float('inf')
        iterations_done = 0

        for i in range(self.max_correction_iterations):
            iterations_done = i + 1
            self.personality.step_start(f"Boost ({content_type}): Reflection Iteration {iterations_done}/{self.max_correction_iterations}...")
            
            reflection_prompt = reflection_prompt_func(content_type=content_type, specs=specs, generated_content=current_content)
            reflection_json_str = self.personality.generate_code(
                prompt=reflection_prompt,
                language="json", 
                code_tag_format="markdown",
                accept_all_if_no_code_tags_is_present=True, 
                callback=self.personality.sink
            )

            reflection_data = None
            if reflection_json_str and isinstance(reflection_json_str, str):
                reflection_data = find_first_json_block(reflection_json_str)
                if not reflection_data: # pragma: no cover
                    try:
                        reflection_data = json.loads(reflection_json_str)
                    except json.JSONDecodeError as e:
                        self.logger.warning(f"Failed to parse reflection JSON for {content_type}: {e}. Raw: {reflection_json_str}")


            if not reflection_data or "num_problems_detected" not in reflection_data: # pragma: no cover
                self.logger.warning(f"Reflection data for {content_type} is malformed or incomplete. Iteration {i+1}.")
                self.personality.step_end(f"Reflection {i+1} data malformed.", success=False)
                if i == 0: min_problems = 0 
                break 


            num_problems = reflection_data.get("num_problems_detected", float('inf'))
            problem_details = reflection_data.get("problem_details", [])
            self.logger.info(f"Boost ({content_type}) Reflection {i+1}: {num_problems} problems detected. Details: {problem_details}")
            self.personality.step_end(f"Reflection {i+1}: {num_problems} problems. Summary: {reflection_data.get('review_summary', 'N/A')}", success=True)


            if num_problems < min_problems:
                min_problems = num_problems
                best_content = current_content
            
            if num_problems == 0:
                self.logger.info(f"Boost ({content_type}): No problems detected after {i+1} iterations.")
                break 

            if i == self.max_correction_iterations - 1: # Last iteration # pragma: no cover
                self.logger.info(f"Boost ({content_type}): Max iterations reached.")
                break 

            self.personality.step_start(f"Boost ({content_type}): Correction Iteration {i+1}...")
            problem_details_str = "\n".join([f"- Area/Field: {p.get('field_path', p.get('area', 'N/A'))}, Issue: {p.get('issue', 'N/A')}, Suggestion: {p.get('suggestion', 'N/A')}" for p in problem_details])
            
            now_iso_for_correction = datetime.datetime.now(datetime.timezone.utc).isoformat()
            correction_prompt = correction_prompt_func(content_type=content_type, specs=specs, previous_content=current_content, problem_details_str=problem_details_str, now_iso=now_iso_for_correction)
            
            corrected_content_str = self.personality.generate_code(
                prompt=correction_prompt,
                language=content_type,
                code_tag_format="markdown",
                accept_all_if_no_code_tags_is_present=False,
                callback=self.personality.sink
            )

            if not corrected_content_str or not isinstance(corrected_content_str, str): # pragma: no cover
                self.logger.warning(f"Boost ({content_type}): Correction attempt {i+1} failed to generate content.")
                self.personality.step_end(f"Correction {i+1} generation failed.", success=False)
                break 
            
            current_content = corrected_content_str
            self.personality.step_end(f"Correction {i+1} generated.", success=True)

        return best_content, iterations_done, min_problems

    def _generate_config_yaml_prompt(
            self, new_fn_name: str, class_name:str, new_fn_desc: str,
            new_fn_type_str: str, new_fn_params_desc: Optional[str],
            target_category:str, new_fn_static_params_desc: Optional[str] = None, **kwargs
        ) -> str:
        """
        Generates the prompt for creating the config.yaml file.
        """
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        
        static_params_instructions = ""
        if new_fn_static_params_desc:
            static_params_instructions = f"""
Static Parameters to define in 'static_parameters' list (user-configurable settings):
'{new_fn_static_params_desc}'
For each static parameter described, infer:
  - 'name' (snake_case)
  - 'type' ("str", "int", "float", "bool", "text")
  - 'value' (a sensible default)
  - 'help' (description for UI)
  - 'options' (list, if applicable for "str" type, e.g., ["choice1", "choice2"])
Example:
  - name: api_key
    type: str
    value: ""
    help: "The API key for the external service."
"""
        else: # pragma: no cover
            static_params_instructions = "Static parameters: None specified. Do not include 'static_parameters' section unless explicitly described above."

        parameter_type_guidance = """
Parameter Types Guidance:
For 'parameters' (dynamic inputs to `execute` method), strongly prefer simple data types:
- "str": For text, simple comma-separated values, or JSON strings if complex data must be passed as one argument.
- "int": For whole numbers.
- "float": For decimal numbers.
- "bool": For true/false values.
- "list": For lists of simple items (e.g., list of strings, list of numbers). Specify if possible (e.g. "list[str]").
Avoid using "dict" as a parameter type unless the user explicitly provided a clear, simple schema for the dictionary and it's absolutely necessary.
If a parameter seems complex, consider if it can be broken down into multiple simpler parameters or passed as a JSON string ("str" type) that the Python code will parse.
"""

        prompt = f"""
You are an expert LoLLMs function call developer. Generate 'config.yaml' content.
Follow LoLLMs documentation structure precisely.

New function specifications:
- Function Name (snake_case, for 'name' field): {new_fn_name}
- Class Name (CamelCase, for 'class_name' field): {class_name}
- Description (for 'description' field): {new_fn_desc}
- Function Type (conceptual): {new_fn_type_str}
- Category (for 'category' field): {target_category}
- Author: "AI Generated via FunctionCallBuilder"
- Version: "1.0.0"
- creation_date_time: '{now_iso}'
- last_update_date_time: '{now_iso}'

Parameters to define in 'parameters' list (dynamic inputs for CLASSIC function's 'execute' method):
'{new_fn_params_desc if new_fn_params_desc and new_fn_type_str == 'CLASSIC' else "No dynamic parameters needed."}'
If parameters are described for a CLASSIC function:
  - 'name' (snake_case)
  - 'type' (see Parameter Types Guidance below)
  - 'description' (clear explanation)
  - 'required' (bool, optional, defaults to false if not clear or if a default is given)
  - 'default' (optional, provide if a default value is clear from description)

{parameter_type_guidance}

'returns' section:
- If CLASSIC: returns: {{ status: {{ type: str, description: "The result of the function or an error message." }} }}
- If CONTEXT_UPDATE: returns: {{}}

{static_params_instructions}

Output *only* the complete YAML content for 'config.yaml', enclosed in ```yaml ... ```.
"""
        return prompt

    def execute(self, context: LollmsContextDetails, *args, **kwargs) -> str:
        """
        Main execution method for the FunctionCallBuilder.
        Generates function call files based on provided specifications.
        """
        self.personality.step_start("Starting Function Call Builder...")

        new_fn_name_orig = kwargs.get("new_function_name")
        new_fn_desc = kwargs.get("new_function_description")
        user_fn_type_pref = kwargs.get("new_function_type", "CLASSIC").upper()
        new_fn_params_desc = kwargs.get("new_function_parameters_description") 
        new_fn_static_params_desc = kwargs.get("new_function_static_parameters_description") 
        new_fn_core_logic = kwargs.get("new_function_core_logic")
        target_category_unsanitized = kwargs.get("target_category", "generated")

        if not all([new_fn_name_orig, new_fn_desc, new_fn_core_logic]):
            msg = "Build Failed: Missing one or more required parameters: new_function_name, new_function_description, new_function_core_logic."
            self.personality.step_end(msg, success=False)
            return f"Error: {msg}"

        if user_fn_type_pref not in ["CLASSIC", "CONTEXT_UPDATE"]: # pragma: no cover
            msg = f"Build Failed: Invalid user preferred function type '{user_fn_type_pref}'. Must be 'CLASSIC' or 'CONTEXT_UPDATE'."
            self.personality.step_end(msg, success=False)
            return f"Error: {msg}"

        new_fn_type_str = user_fn_type_pref
        if self.boost_mode_enabled:
            new_fn_type_str = self._determine_function_type_with_llm(new_fn_desc, new_fn_core_logic, user_fn_type_pref)

        safe_fn_name = sanitize_path_from_user_input(new_fn_name_orig.lower().replace(" ", "_"))
        safe_category = sanitize_path_from_user_input(target_category_unsanitized.lower().replace(" ", "_"))
        class_name = snake_to_camel(safe_fn_name)

        if not re.match(r'^[a-z0-9_]+$', safe_fn_name): # pragma: no cover
            msg = f"Build Failed: Invalid function name '{safe_fn_name}'. Must be snake_case (lowercase letters, numbers, underscores)."
            self.personality.step_end(msg, success=False)
            return f"Error: {msg}"

        self.logger.info(
            f"Building new function: {safe_fn_name} of type {new_fn_type_str} "
            f"(user pref: {user_fn_type_pref}) in category {safe_category}. Boost: {self.boost_mode_enabled}"
        )

        custom_functions_base_path = self.app.lollms_paths.custom_function_calls_path
        function_category_path = custom_functions_base_path / safe_category
        function_path = function_category_path / safe_fn_name

        if function_path.exists(): # pragma: no cover
            msg = f"Function '{safe_fn_name}' in category '{safe_category}' already exists. Choose a different name or category."
            self.personality.step_end(f"Build Failed: {msg}", success=False)
            self.app.warning(msg, client_id=self.client.client_id)
            return f"Error: {msg}"

        specs = {
            "new_fn_name": safe_fn_name, "class_name": class_name, "new_fn_desc": new_fn_desc,
            "new_fn_type_str": new_fn_type_str, 
            "new_fn_params_desc": new_fn_params_desc, 
            "new_fn_static_params_desc": new_fn_static_params_desc, 
            "target_category": safe_category, "new_fn_core_logic": new_fn_core_logic
        }
        
        generated_config_yaml = ""
        generated_function_py = ""
        yaml_iterations = 0
        yaml_problems = -1 
        py_iterations = 0
        py_problems = -1

        try:
            if self.boost_mode_enabled:
                self.personality.step_start(f"Boost Mode: Generating config.yaml for {safe_fn_name} with self-correction...")
                generated_config_yaml, yaml_iterations, yaml_problems = self._run_generation_loop(
                    content_type="yaml", specs=specs,
                    initial_generation_prompt_func=self._generate_config_yaml_prompt,
                    reflection_prompt_func=self._get_reflection_prompt,
                    correction_prompt_func=self._get_correction_prompt
                )
                self.personality.step_end(f"config.yaml generation (boosted) complete. Iterations: {yaml_iterations}, Final Problems: {yaml_problems}", success=True)
            else: 
                self.personality.step_start(f"Generating config.yaml for {safe_fn_name}...")
                generated_config_yaml = self.personality.generate_code(
                    prompt=self._generate_config_yaml_prompt(**specs), language="yaml",
                    code_tag_format="markdown", accept_all_if_no_code_tags_is_present=False,
                    callback=self.personality.sink
                )
                if not generated_config_yaml or not isinstance(generated_config_yaml, str): # pragma: no cover
                    raise ValueError("LLM failed to generate config.yaml content.")
                now_iso_val = datetime.datetime.now(datetime.timezone.utc).isoformat()
                generated_config_yaml = generated_config_yaml.replace('YYYY-MM-DDTHH:MM:SS.ffffff', now_iso_val) 
                generated_config_yaml = re.sub(r"creation_date_time: '.*?'", f"creation_date_time: '{now_iso_val}'", generated_config_yaml)
                generated_config_yaml = re.sub(r"last_update_date_time: '.*?'", f"last_update_date_time: '{now_iso_val}'", generated_config_yaml)
                self.personality.step_end(f"config.yaml generated.", success=True)


            if self.boost_mode_enabled:
                self.personality.step_start(f"Boost Mode: Generating function.py for {safe_fn_name} with self-correction...")
                generated_function_py, py_iterations, py_problems = self._run_generation_loop(
                    content_type="python", specs=specs,
                    initial_generation_prompt_func=self._generate_function_py_prompt,
                    reflection_prompt_func=self._get_reflection_prompt,
                    correction_prompt_func=self._get_correction_prompt
                )
                self.personality.step_end(f"function.py generation (boosted) complete. Iterations: {py_iterations}, Final Problems: {py_problems}", success=True)

            else: 
                self.personality.step_start(f"Generating function.py for {safe_fn_name}...")
                generated_function_py = self.personality.generate_code(
                    prompt=self._generate_function_py_prompt(**specs), language="python",
                    code_tag_format="markdown", accept_all_if_no_code_tags_is_present=False,
                    callback=self.personality.sink
                )
                if not generated_function_py or not isinstance(generated_function_py, str): # pragma: no cover
                    raise ValueError("LLM failed to generate function.py content.")
                self.personality.step_end(f"function.py generated.", success=True)

            self.personality.step_start(f"Saving files for {safe_fn_name}...")
            function_category_path.mkdir(parents=True, exist_ok=True)
            (function_category_path / "__init__.py").touch(exist_ok=True) 
            
            function_path.mkdir(parents=True, exist_ok=True)
            
            config_file_path = function_path / "config.yaml"
            function_file_path = function_path / "function.py"
            
            with open(config_file_path, "w", encoding="utf-8") as f_config:
                f_config.write(generated_config_yaml)
            self.logger.info(f"Saved config.yaml to {config_file_path}")

            with open(function_file_path, "w", encoding="utf-8") as f_py:
                f_py.write(generated_function_py)
            self.logger.info(f"Saved function.py to {function_file_path}")
            
            self.personality.step_end(f"Files saved successfully for {safe_fn_name}.", success=True)
            
            boost_details = ""
            if self.boost_mode_enabled:
                boost_details = (f"\nBoost Mode Report:\n"
                                 f"- YAML: {yaml_iterations} iterations, {yaml_problems if yaml_problems != float('inf') else 'N/A'} final problem(s).\n"
                                 f"- Python: {py_iterations} iterations, {py_problems if py_problems != float('inf') else 'N/A'} final problem(s).")

            success_message = (
                f"Successfully created function call '{safe_fn_name}' in category '{safe_category}'.\n"
                f"Files are located at: {function_path}\n"
                f"Type: {new_fn_type_str} (User pref: {user_fn_type_pref}).{boost_details}\n"
                "You may need to restart LoLLMs or use the 'Reload Functions Zoo' option in settings for it to be available.\n"
                "Please REVIEW the generated files, especially 'function.py', to implement the core logic and add any necessary dependencies using pipmaster."
            )
            self.app.success(f"Function call '{safe_fn_name}' created. Please review and test.{boost_details}", client_id=self.client.client_id)
            return success_message

        except Exception as e: # pragma: no cover
            self.logger.error(f"Error during function building for {safe_fn_name}: {e}")
            trace_exception(e)
            self.personality.step_end(f"Build Failed: {e}", success=False)
            self.app.error(f"Failed to build function {safe_fn_name}. Error: {e}", client_id=self.client.client_id)
            return f"Error: Could not build function {safe_fn_name}. Reason: {str(e)}"