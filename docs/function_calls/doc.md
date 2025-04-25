# LoLLMs Function Calls: The Ultimate Guide to Extending Your AI Assistant

This comprehensive documentation provides a detailed guide on building custom function calls for the Lord of Large Language Models (LoLLMs) framework. Master function calls to extend the capabilities of your AI assistant beyond simple text generation by integrating external tools, APIs, custom logic, context manipulation, and providing robust logging.

**Table of Contents**

1.  [Introduction: What are Function Calls?](#1-introduction-what-are-function-calls)
2.  [Why Use Function Calls?](#2-why-use-function-calls)
3.  [Core Concepts](#3-core-concepts)
4.  [Function Call Types](#4-function-call-types)
    *   [CLASSIC Functions](#classic-functions)
    *   [CONTEXT_UPDATE Functions](#context_update-functions)
5.  [Building a Function Call: Step-by-Step](#5-building-a-function-call-step-by-step)
    *   [File Structure](#file-structure)
    *   [The `config.yaml` File](#the-configyaml-file)
    *   [The `function.py` File](#the-functionpy-file)
        *   [Imports and Dependency Checks](#imports-and-dependency-checks)
        *   [Class Definition](#class-definition)
        *   [The `__init__` Method (Mandatory Structure & Signature)](#the-__init__-method-mandatory-structure--signature)
        *   [Implementing Core Logic (`execute` or `update_context`/`process_output`)](#implementing-core-logic-execute-or-update_contextprocess_output)
        *   [Optional `settings_updated` Method](#optional-settings_updated-method)
6.  [Handling Dependencies (`pipmaster`)](#6-handling-dependencies-pipmaster)
7.  [Logging and Debugging with `ascii_colors`](#7-logging-and-debugging-with-ascii_colors)
    *   [Logging vs. Direct Printing](#logging-vs-direct-printing)
    *   [Getting a Logger Instance](#getting-a-logger-instance)
    *   [Logging Levels](#logging-levels)
    *   [Logging Messages](#logging-messages)
    *   [Tracing Exceptions](#tracing-exceptions)
    *   [Console Utilities (Use with Care)](#console-utilities-use-with-care)
8.  [Example 1: A CLASSIC Calculator Function](#8-example-1-a-classic-calculator-function)
9.  [Example 2: A CONTEXT_UPDATE Time Function](#9-example-2-a-context_update-time-function)
10. [Example 3: Function with Static Parameters](#10-example-3-function-with-static-parameters)
11. [Leveraging LoLLMs Helpers (`self.app`, `self.personality`)](#11-leveraging-lollms-helpers-selfapp-selfpersonality)
    *   [LLM Interaction Helpers (via `self.personality`)](#llm-interaction-helpers-via-selfpersonality)
    *   [Utility & Task Helpers (via `self.personality` or `TasksLibrary`)](#utility--task-helpers-via-selfpersonality-or-taskslibrary)
    *   [UI Feedback Helpers (via `self.personality` or `self.app`)](#ui-feedback-helpers-via-selfpersonality-or-selfapp)
    *   [Accessing Application State (via `self.app`)](#accessing-application-state-via-selfapp)
12. [Best Practices and Tips](#12-best-practices-and-tips)
13. [Registering and Using Function Calls](#13-registering-and-using-function-calls)
14. [Conclusion](#14-conclusion)

---

## 1. Introduction: What are Function Calls?

In LoLLMs, a "Function Call" refers to a mechanism that allows the Large Language Model (LLM) or a user (via specific commands or integrations) to trigger the execution of predefined Python code. This code can perform tasks like:

*   Fetching real-time data (e.g., weather, stock prices).
*   Interacting with external APIs (e.g., sending emails, controlling smart home devices like Philips Hue).
*   Performing complex calculations or data processing (e.g., using `sympy` or custom libraries).
*   Accessing local system resources (e.g., reading/writing files, running commands - **use with extreme caution!**).
*   Modifying the context sent to the LLM before generation (e.g., adding current time, summarizing previous turns, fetching relevant database entries).
*   Post-processing the LLM's output (e.g., cleaning up text, validating data, triggering follow-up actions).

Essentially, function calls bridge the gap between the generative capabilities of the LLM and the functional capabilities of traditional software and the wider digital world.

## 2. Why Use Function Calls?

*   **Extend Capabilities:** Overcome the LLM's limitations (e.g., lack of real-time data, inability to perform actions in the real world).
*   **Improve Accuracy & Reliability:** Fetch factual data from reliable sources instead of relying solely on the LLM's potentially outdated or hallucinated knowledge.
*   **Enable Automation:** Allow the AI to perform multi-step tasks and workflows by calling sequences of functions.
*   **Structured Interaction:** Define clear interfaces for tasks, making interactions more predictable and controllable.
*   **Context Management:** Dynamically add relevant, up-to-date information (like current time, sensor data, calendar events, or memory summaries) to the LLM's context window right before it generates a response.
*   **Output Processing:** Automatically clean up, format, validate, or even trigger further actions based on the LLM's generated text.
*   **Customization:** Tailor LoLLMs to specific needs and domains by integrating specialized tools, databases, or enterprise systems.
*   **Debugging & Monitoring:** Use structured logging within functions to understand their behavior and troubleshoot issues.

## 3. Core Concepts

Before diving into building, understand these key components:

*   **`FunctionCall` (Class):** The base class (`lollms.function_call.FunctionCall`) that all custom function calls **must** inherit from. It defines the essential structure and methods.
*   **`FunctionType` (Enum):** An enumeration (`lollms.function_call.FunctionType`) specifying the type of function call (`CLASSIC` or `CONTEXT_UPDATE`). This dictates how the function is triggered and how it interacts with the LLM's generation process.
*   **`LollmsApplication` (`self.app`):** The central application instance passed during initialization. It provides access to global configuration (`self.app.config`), paths (`self.app.lollms_paths`), the current model (`self.app.model`), mounted personalities, core functionalities like notifications (`self.app.notify`), and the logging system (`ascii_colors`).
*   **`AIPersonality` (`self.personality`):** The specific personality instance *associated with this function call*. This provides access to LLM interaction methods tailored for that personality's context (like `self.personality.fast_gen`, `self.personality.generate_code`) and UI feedback methods (`self.personality.step_start`, `self.personality.set_message_html`).
*   **`Client` (`self.client`):** Represents the user session interacting with LoLLMs. It provides access to the current discussion context (`self.client.discussion`), including discussion-specific folders (`self.client.discussion.discussion_folder`).
*   **`LollmsContextDetails`:** An object passed to certain methods (`update_context`, `process_output`, `execute`). It encapsulates various details about the current interaction state (discussion history, user info, attached files, etc.).
*   **`APScript`:** A helper class often part of an `AIPersonality` (accessed via `self.personality` if used). It provides utility methods for UI interaction (`step_start`, etc.) and common LLM tasks.
*   **`ascii_colors`:** The integrated logging and terminal coloring library. Use `import ascii_colors as logging` for a familiar interface, and `trace_exception` for detailed error reports.
*   **`pipmaster`:** A utility for ensuring Python package dependencies are installed (`pm.ensure_packages`).
*   **`config.yaml`:** The metadata file defining the function's name, description, parameters, etc.
*   **`function.py`:** The Python file containing the class implementation inheriting from `FunctionCall`.

## 4. Function Call Types

LoLLMs defines two primary types of function calls, each serving a different purpose:

### CLASSIC Functions

*   **Enum:** `FunctionType.CLASSIC`
*   **Purpose:** To perform a specific, discrete action and return a direct result (usually a string) back to the LLM or the system that invoked it. The LLM typically uses this result in its subsequent response generation. Think of these as tools the LLM can explicitly decide to use.
*   **Triggering:**
    *   Primarily invoked when the LLM generates a specific JSON structure within a ` ```function ... ``` ` markdown block. The JSON must contain a `"function_name"` key matching the function's registered name and a `"function_parameters"` key (can be a dictionary or list) with the necessary arguments.
    *   Can also be triggered programmatically.
*   **Key Method:** `execute(self, context: LollmsContextDetails, *args, **kwargs) -> str`
    *   Receives parameters defined in `config.yaml`'s `parameters` section via the `kwargs` dictionary.
    *   Contains the core logic. Use `ascii_colors` logging (`self.logger.info`, `self.logger.debug`) for internal state and `self.personality.step_start/end` for UI feedback.
    *   **Must return a string.** This string represents the function's output or status. It's often fed back into the LLM's context.

### CONTEXT_UPDATE Functions

*   **Enum:** `FunctionType.CONTEXT_UPDATE`
*   **Purpose:** To dynamically modify the context *before* it's sent to the LLM for generation, or to process the LLM's output *after* generation. These functions operate more implicitly. Ideal for injecting timely info (time, memory summaries) or post-processing responses.
*   **Triggering:** Automatically executed by LoLLMs core during prompt building and/or after generation, *if* the function call is mounted and currently *selected/enabled*.
*   **Key Methods:**
    *   `update_context(self, context: LollmsContextDetails, constructed_context: List[str]) -> List[str]`
        *   Called **before** LLM generation.
        *   Receives `LollmsContextDetails` and the `constructed_context` list.
        *   Modify the `constructed_context` list (add, remove, change entries).
        *   Use `ascii_colors` logging for debugging this stage.
        *   **Must return the modified `constructed_context` list.**
    *   `process_output(self, context: LollmsContextDetails, llm_output: str) -> str` (Optional)
        *   Called **after** LLM generation.
        *   Receives `LollmsContextDetails` and the raw `llm_output` string.
        *   Modify the `llm_output` (clean, format, validate, trigger side effects).
        *   Use `ascii_colors` logging for debugging.
        *   **Must return the (potentially modified) `llm_output` string.**

## 5. Building a Function Call: Step-by-Step

Creating a function call involves defining its interface (`config.yaml`) and implementing its logic (`function.py`) within a dedicated folder.

### File Structure

Organize your function calls logically within the LoLLMs functions zoo (`lollms_core/lollms/functions/functions_zoo/`) under a category folder, or in your personal custom functions folder (`personal_data/custom_function_calls/`).

```
# Example structure
lollms_core/lollms/functions/functions_zoo/
└── utility/
    └── get_weather/
        ├── config.yaml
        └── function.py
```

### The `config.yaml` File

This YAML file acts as the manifest for your function call, defining its metadata and how it can be invoked or configured.

**Key Fields:**

*   `author` (str): Your name or alias (e.g., "ParisNeo").
*   `version` (str): Semantic version number (e.g., "1.0.0").
*   `creation_date_time` (str): Timestamp when the function was created (ISO 8601 format recommended, e.g., '2024-05-25T14:30:00.123456'). *LoLLMs automatically adds/updates this if missing.*
*   `last_update_date_time` (str): Timestamp of the last modification. *LoLLMs automatically adds/updates this if missing.*
*   `category` (str): The category folder name where this function resides (e.g., "utility", "data_search", "custom").
*   `class_name` (str): **Crucial:** The exact name of your Python class in `function.py` that inherits from `FunctionCall`.
*   `name` (str): **Crucial:** The unique, snake_case identifier the LLM will use to refer to and call this function (e.g., `get_weather`, `summarize_youtube_video`). Keep it descriptive but concise.
*   `description` (str): A clear, informative description of what the function does. This is heavily used by the LLM (and users in the UI) to understand the function's purpose. Make it accurate and helpful.
*   `parameters` (list, optional): Defines the input parameters the function accepts. Primarily used by `CLASSIC` functions. Each item is a dictionary:
    *   `name` (str): The parameter name (used as a keyword argument key in the `execute` method).
    *   `type` (str): The expected Python data type as a string (e.g., `"str"`, `"int"`, `"float"`, `"bool"`, `"list"`, `"dict"`).
    *   `description` (str): A clear description of what this parameter represents, crucial for the LLM.
    *   `default` (any, optional): A default value used if the LLM doesn't provide this parameter.
    *   `required` (bool, optional): Defaults to `false`. Set to `true` if the parameter is mandatory for the function to execute.
*   `returns` (dict, optional): Describes the *expected* return value. Mainly for documentation and potential future type checking.
    *   `status` (dict): Describes the primary return (often a status message or the core result).
        *   `type` (str): Expected return type (usually `"str"` for `CLASSIC`).
        *   `description` (str): Description of what the function returns.
*   `static_parameters` (list, optional): Defines user-configurable settings accessible via the LoLLMs UI. See [Static Parameters](#10-static-parameters-user-configurable-settings) section for details. Each item is a dictionary:
    *   `name` (str): Setting identifier (snake_case).
    *   `type` (str): Data type ("str", "int", "float", "bool", "text").
    *   `value` (any): The default value for the setting.
    *   `help` (str): Tooltip/description shown to the user in the settings UI.
    *   `options` (list, optional): For `"str"` type, provides a list of predefined choices for a dropdown menu.

### The `function.py` File

This Python file contains the class that implements the function's logic.

#### Imports and Dependency Checks

Start by importing necessary standard libraries and LoLLMs components. Use `pipmaster` for external dependencies.

```python
# Standard libraries
import json, math, datetime, os, re, subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional, Union, Tuple, Callable # Be specific
from functools import partial

# Lollms specific imports
from lollms.function_call import FunctionCall, FunctionType # Base class and enum
from lollms.app import LollmsApplication # Main application instance
from lollms.client_session import Client # User session
from lollms.prompting import LollmsContextDetails # Context details object
from lollms.config import TypedConfig, ConfigTemplate, BaseConfig # For static params
from lollms.utilities import PackageManager # Or directly use pipmaster

# Logging and Dependencies
import ascii_colors as logging # Use alias for logging API
from ascii_colors import trace_exception # Specific import for exceptions
import pipmaster as pm

# --- Dependency Check Example ---
# required_packages = {"requests": ">=2.20.0"}
# try:
#     pm.ensure_packages(required_packages)
#     import requests # Now safe to import
# except Exception as e:
#     logging.getLogger(__name__).error(f"Failed to install dependencies: {e}")
```

#### Class Definition

Define your class, inheriting from `FunctionCall`. The class name **must** match `class_name` in `config.yaml`.

```python
class MyCustomFunction(FunctionCall): # Matches class_name
    # ... methods go here ...
```

#### The `__init__` Method (Mandatory Structure & Signature)

The constructor (`__init__`) is essential for setting up your function call and registering it correctly with LoLLMs. It **must** adhere to the following structure and signature:

**Mandatory Signature:**

```python
def __init__(self, app: LollmsApplication, client: Client):
```

**Implementation Steps:**

1.  **Initialize Logger (Recommended):** Get a logger instance for clear debugging specific to this function call.
    ```python
    self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    self.logger.debug(f"Initializing {self.__class__.__name__}...")
    ```

2.  **Define Static Parameters Setup (If Needed):** If your `config.yaml` defines `static_parameters`, create the corresponding `ConfigTemplate` and `TypedConfig` objects *before* calling `super().__init__()`.
    ```python
    # --- Define ConfigTemplate matching static_parameters in YAML ---
    config_template = ConfigTemplate([
        {"name": "api_key", "type": "str", "value": "", "help": "..."},
        # ... other static parameter definitions ...
    ])
    # --- Create TypedConfig instance ---
    static_params_config = TypedConfig(config_template, BaseConfig(config={}))
    ```

3.  **Call Parent Class Constructor (`super().__init__`) (MANDATORY):** This is the most critical step. It registers the function call with the LoLLMs framework and handles the loading of static parameter values from the user's configuration files.

    **Full Signature of `FunctionCall.__init__`:**
    ```python
    # Located in lollms/function_call.py
    def __init__(
        self,
        function_name: str,          # REQUIRED: Matches 'name' in config.yaml
        app: LollmsApplication,      # REQUIRED: The main app instance
        function_type: FunctionType, # REQUIRED: FunctionType.CLASSIC or FunctionType.CONTEXT_UPDATE
        client: Client,              # REQUIRED: The user client session instance
        static_parameters: Optional[TypedConfig] = None # OPTIONAL: Pass the TypedConfig object if you defined static params
    ):
        # ... internal initialization ...
        self.function_name = function_name
        self.app = app
        self.personality = app.personality # Gets the personality at the time of INIT
        self.function_type = function_type
        self.client = client
        self.description = "" # Often loaded from config later
        if static_parameters is not None:
            self.static_parameters = static_parameters
            self.sync_configuration() # Handles loading/saving config file
        # ... other internal setup ...
    ```

    **Your `super().__init__` Call (Example with static params):**
    ```python
    super().__init__(
        function_name="my_custom_function", # MUST match 'name' in config.yaml
        app=app,                            # Pass the app instance
        function_type=FunctionType.CLASSIC, # Choose CLASSIC or CONTEXT_UPDATE
        client=client,                      # Pass the client instance
        static_parameters=static_params_config # Pass your TypedConfig object IF you have static params
    )
    ```
    **Your `super().__init__` Call (Example without static params):**
    ```python
    super().__init__(
        function_name="my_simple_function", # Matches name in config.yaml
        app=app,
        function_type=FunctionType.CLASSIC, # Or CONTEXT_UPDATE
        client=client
        # No static_parameters argument here
    )
    ```

4.  **Access Loaded Static Parameters (AFTER `super().__init__`)**: If you defined static parameters, their user-configured (or default) values are now available in `self.static_parameters.config`. Use `.get()` for safe access.
    ```python
    # Example: Accessing the 'api_key' static parameter defined earlier
    self.api_key = self.static_parameters.config.get("api_key", "") # "" is the fallback default
    self.logger.debug(f"Loaded API Key: {'Set' if self.api_key else 'Not Set'}")
    ```

5.  **Initialize Other Instance Variables:** Perform any other necessary setup for your function (e.g., initializing API clients using the loaded `self.api_key`).
    ```python
    # Example: self.weather_client = WeatherAPI(api_key=self.api_key)
    self.logger.info(f"{self.function_name} initialization complete.")
    ```

#### Implementing Core Logic (`execute` or `update_context`/`process_output`)

Implement the method(s) corresponding to the `function_type` specified in `super().__init__`.

*   **`CLASSIC`:** `def execute(self, context: LollmsContextDetails, *args, **kwargs) -> str:`
*   **`CONTEXT_UPDATE`:** `def update_context(self, context: LollmsContextDetails, constructed_context: List[str]) -> List[str]:` and optionally `def process_output(self, context: LollmsContextDetails, llm_output: str) -> str:`

Use `self.logger` for logging and helpers from `self.personality` or `self.app` as needed (see Section 11).

#### Optional `settings_updated` Method

*   **Signature:** `def settings_updated(self):`
*   Implement this method if your function needs to re-initialize or reload configurations when the user saves changes to its static parameters in the UI. Access the new values via `self.static_parameters.config.get(...)`.

## 6. Handling Dependencies (`pipmaster`)

Function calls often require external Python libraries. Use `pipmaster` to manage these dependencies automatically.

**`pipmaster.ensure_packages(packages_dict: dict)`:**

Checks if packages meet version requirements and installs/upgrades if needed.

*   **Argument:** A dictionary mapping package names (str) to version specifiers (str).
    *   **Format:** `{"package-name": "version-specifier"}`
    *   **Examples:**
        *   `{"requests": ">=2.20.0"}` (Minimum version)
        *   `{"beautifulsoup4": ""}` (Latest version if missing)
        *   `{"phue": "==1.1"}` (Exact version)
        *   `{"numpy": ""}` (Latest)

**Placement:** Call `ensure_packages` at the **top level** of your `function.py` file, *before* importing the managed packages.

**Example:**

```python
# function.py
# ... (Lollms imports) ...
import pipmaster as pm
import ascii_colors as logging

logger = logging.getLogger(__name__)

# --- Dependency Management ---
logger.debug("Ensuring required packages for MyApiFunction...")
required_packages = {
    "requests": ">=2.20.0",
    "beautifulsoup4": "",
    "phue": "==1.1"
}
try:
    pm.ensure_packages(required_packages)
    # --- Dependencies are now ensured ---
    import requests # Safe to import now
    from bs4 import BeautifulSoup
    from phue import Bridge
    logger.debug("Required packages are available.")
    _dependencies_met = True
except Exception as e:
    logger.error(f"Failed to ensure/install required packages: {e}")
    trace_exception(e)
    _dependencies_met = False

# --- Class Definition ---
class MyApiFunction(FunctionCall):
    def __init__(self, app: LollmsApplication, client: Client):
        # ... (logger init) ...
        # ... (static params if needed) ...
        super().__init__("my_api_function", app, FunctionType.CLASSIC, client)
        # ... (access static params) ...
        self.dependencies_met = _dependencies_met # Use flag set during import check
        if not self.dependencies_met:
            self.logger.error("Initialization skipped due to missing dependencies.")
        # ... rest of init ...

    def execute(self, context: LollmsContextDetails, *args, **kwargs) -> str:
        if not self.dependencies_met:
            self.personality.step_start("Dependency Error")
            self.personality.step_end("Dependency Error", success=False)
            self.app.error("Required libraries missing for this function. Check server logs.", client_id=self.client.client_id)
            return "Error: Required libraries could not be installed or imported."
        # ... proceed with logic ...
```

## 7. Logging and Debugging with `ascii_colors`

LoLLMs uses `ascii_colors` for robust logging. Using it within your function calls is highly recommended for debugging and monitoring.

### Logging vs. Direct Printing

*   **Logging System:** Use `getLogger`, `logger.info`, `logger.error(..., exc_info=True)`, `trace_exception()`. **Recommended for function calls.** Sends structured messages via handlers (console, file). Filtered by levels. Provides persistent records.
*   **Direct Printing:** `ASCIIColors.red`, `ASCIIColors.print`. Prints directly to the *server console*. Bypasses logging. Use sparingly, mainly for server-side debugging or utilities like `execute_with_animation`.

### Getting a Logger Instance

In your `function.py` class `__init__`:
```python
import ascii_colors as logging

class MyFunction(FunctionCall):
    def __init__(self, app: LollmsApplication, client: Client):
        # ... super().__init__(...) ...
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
```

### Logging Levels

*   `DEBUG`: Detailed diagnostic info.
*   `INFO`: Routine operational messages.
*   `WARNING`: Potential issue or unexpected event.
*   `ERROR`: Function failed a task but might continue.
*   `CRITICAL`: Severe error, likely halting the function.

### Logging Messages

Log key events, parameters, results, and errors:
```python
self.logger.info(f"Processing request with params: {kwargs}")
# ... logic ...
if success:
    self.logger.info("Processing successful.")
else:
    self.logger.warning(f"Processing had minor issues for params: {kwargs}.")
```

### Tracing Exceptions

Use `trace_exception(e)` inside `except` blocks for full stack traces in logs:
```python
from ascii_colors import trace_exception

try:
    result = 1 / 0
except Exception as e:
    self.logger.error(f"Calculation failed: {e}")
    trace_exception(e) # Logs the full traceback at ERROR level
    return f"Error: Calculation failed. Check logs."
```

### Console Utilities (Use with Care)

*   **`ASCIIColors.execute_with_animation(text, function, *args, **kwargs)`:** Runs a *blocking* function with a spinner on the *server console*. Not for UI feedback.
*   Other direct prints (`highlight`, `multicolor`, etc.): Avoid in standard function call logging.

## 8. Example 1: A CLASSIC Calculator Function

**Folder:** `functions_zoo/utility/calculator/`

**`config.yaml`:**
```yaml
author: ParisNeo
category: utility
class_name: Calculator
creation_date_time: '2025-03-09T00:32:32.679228'
description: Evaluates a Python mathematical expression safely and returns the result as text. Supports standard math functions like sin, cos, sqrt, log, exp, pi, e.
last_update_date_time: '2025-03-09T00:32:32.679228'
name: calculator
parameters:
- description: The mathematical expression to evaluate (e.g., "2 * sin(pi/2)").
  name: expression
  type: str
  required: true
returns:
  status:
    description: The result of the calculation or an error message.
    type: str
version: 1.0.0
```

**`function.py`:**
```python
# Standard Libraries
import math
from typing import List, Dict, Any, Optional

# Lollms Imports
from lollms.function_call import FunctionCall, FunctionType
from lollms.app import LollmsApplication
from lollms.client_session import Client
from lollms.prompting import LollmsContextDetails

# Logging
import ascii_colors as logging # Use alias
from ascii_colors import trace_exception

class Calculator(FunctionCall): # Matches class_name
    def __init__(self, app: LollmsApplication, client: Client):
        # 1. Initialize logger
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.logger.debug("Initializing Calculator function.")

        # 2. No Static Parameters for this function

        # 3. Call Parent Constructor
        super().__init__(
            function_name="calculator", # Matches name in config.yaml
            app=app,
            function_type=FunctionType.CLASSIC,
            client=client
        )

        # 4/5. No other initialization needed
        self.logger.info("Calculator function initialized.")

    def execute(self, context: LollmsContextDetails, *args, **kwargs) -> str:
        """Evaluates a mathematical expression safely."""
        expression = kwargs.get("expression")
        self.logger.info(f"Executing calculator with expression: '{expression}'")

        if not expression:
            self.logger.warning("No expression provided to calculator.")
            return "Error: No expression provided."
        try:
            # Define allowed math functions and constants
            safe_dict = {k: v for k, v in math.__dict__.items() if not k.startswith("__")}
            safe_builtins = {"abs": abs, "round": round, "pow": pow}
            globals_env = {"__builtins__": safe_builtins}
            globals_env.update(safe_dict)
            locals_env = {}

            compiled_code = compile(expression, "<string>", "eval")
            result = eval(compiled_code, globals_env, locals_env)

            self.logger.info(f"Calculation result: {result}")
            return f"The result of '{expression}' is: {result}"
        except NameError as ne:
             self.logger.error(f"NameError evaluating: {expression} - {ne.name}", exc_info=False)
             return f"Error: Unknown name or function used: {ne.name}"
        except SyntaxError as se:
             self.logger.error(f"SyntaxError evaluating: {expression}", exc_info=False)
             return f"Error: Invalid expression syntax."
        except Exception as e:
            self.logger.error(f"Unexpected error evaluating expression: {expression}")
            trace_exception(e)
            return f"Error: Could not evaluate ({type(e).__name__}). Check logs."

    # No settings_updated needed
```

## 9. Example 2: A CONTEXT_UPDATE Time Function

**Folder:** `functions_zoo/context_updater/get_time/`

**`config.yaml`:**
```yaml
author: ParisNeo
category: context_updater
class_name: GetTimeFunction # Matches Python class
creation_date_time: '2025-02-09T23:05:21.407756'
description: Adds the current server date and time to the LLM context before generation.
last_update_date_time: '2025-02-09T23:05:21.407756'
name: get_time # Matches Python function_name
parameters: [] # CONTEXT_UPDATE usually doesn't need parameters here
returns: {} # Does not return directly to LLM
version: 1.0.0
```

**`function.py`:**
```python
# Standard Libraries
import datetime
from typing import List

# Lollms Imports
from lollms.function_call import FunctionCall, FunctionType
from lollms.app import LollmsApplication
from lollms.client_session import Client
from lollms.prompting import LollmsContextDetails

# Logging
import ascii_colors as logging
from ascii_colors import trace_exception

class GetTimeFunction (FunctionCall): # Matches class_name
    def __init__(self, app: LollmsApplication, client:Client):
        # 1. Initialize logger
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.logger.debug("Initializing GetTimeFunction.")

        # 2. No Static Parameters

        # 3. Call Parent Constructor
        super().__init__(
            function_name="get_time", # Matches name in config.yaml
            app=app,
            function_type=FunctionType.CONTEXT_UPDATE, # Important!
            client=client
        )

        # 4/5. No other initialization needed
        self.logger.info("GetTimeFunction initialized.")

    def update_context(self, context: LollmsContextDetails, constructed_context: List[str]) -> List[str]:
        """Adds the current time to the context list."""
        self.logger.debug("Executing update_context for GetTimeFunction.")
        try:
            now_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S %Z') # Include timezone
            time_entry = f"Current date and time: {now_str}"

            # Find insertion point (e.g., after system prompt)
            insertion_point = 1
            if constructed_context:
                system_header = self.app.template.system_full_header # Assumes LollmsLLMTemplate access
                try:
                    header_index = next(i for i, s in enumerate(constructed_context) if system_header in s)
                    insertion_point = header_index + 1
                except StopIteration:
                    self.logger.debug("System header not found, inserting time near beginning.")
                    insertion_point = 1

            insertion_point = min(insertion_point, len(constructed_context))
            constructed_context.insert(insertion_point, time_entry)
            self.logger.info(f"Added time to context at index {insertion_point}")

        except Exception as e:
            self.logger.error("Error adding time to context.")
            trace_exception(e)

        return constructed_context

    # No settings_updated or process_output needed
```

## 10. Example 3: Function with Static Parameters

**Folder:** `custom_function_calls/configurable_greeting/`

**`config.yaml`:** (Same as before)
```yaml
# ... metadata ...
name: configurable_greeting
description: Generates a greeting message using a configurable template and formality level.
parameters:
  - name: name_to_greet
    type: str
    description: The name of the person to greet.
    required: true
returns:
  status:
    type: str
    description: The generated greeting message.
static_parameters:
  - name: greeting_template
    type: str
    value: "Hello, {name}!"
    help: "Template for the greeting. Use {name} as a placeholder."
  - name: formality
    type: str
    value: "informal"
    options: ["informal", "formal", "casual"]
    help: "Select the formality level of the greeting."
  - name: add_timestamp
    type: bool
    value: false
    help: "If checked, add the current time to the greeting."
```

**`function.py`:**
```python
# Standard Libraries
import datetime
from typing import List, Dict, Any, Optional

# Lollms Imports
from lollms.function_call import FunctionCall, FunctionType
from lollms.app import LollmsApplication
from lollms.client_session import Client
from lollms.prompting import LollmsContextDetails
from lollms.config import TypedConfig, ConfigTemplate, BaseConfig # Import config classes

# Logging
import ascii_colors as logging
from ascii_colors import trace_exception

class ConfigurableGreeting(FunctionCall): # Matches class_name
    def __init__(self, app: LollmsApplication, client: Client):
        # 1. Initialize logger
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.logger.debug("Initializing ConfigurableGreeting.")

        # 2. Define ConfigTemplate matching static_parameters in YAML
        config_template = ConfigTemplate([
            {
                "name": "greeting_template", # Matches yaml
                "type": "str",
                "value": "Hello, {name}!",
                "help": "Template for the greeting. Use {name} as a placeholder."
            },
            {
                "name": "formality",
                "type": "str",
                "value": "informal",
                "options": ["informal", "formal", "casual"],
                "help": "Select the formality level of the greeting."
            },
            {
                "name": "add_timestamp",
                "type": "bool",
                "value": False,
                "help": "If checked, add the current time to the greeting."
            }
        ])
        # Create TypedConfig instance
        static_params_config = TypedConfig(config_template, BaseConfig(config={}))

        # 3. Call parent constructor, passing static_params_config
        super().__init__(
            function_name="configurable_greeting", # Matches name in config.yaml
            app=app,
            function_type=FunctionType.CLASSIC,
            client=client,
            static_parameters=static_params_config # Pass the object
        )

        # 4. Load initial settings via settings_updated (called after super)
        self.settings_updated()

        # 5. No other initialization needed here
        self.logger.info("ConfigurableGreeting initialized.")


    def settings_updated(self):
        """Called by LoLLMs when user saves settings in the UI or on init."""
        self.logger.info(f"Reloading static parameters for {self.function_name}...")
        # Access loaded/updated values from self.static_parameters.config
        self.template = self.static_parameters.config.get("greeting_template", "Hello, {name}!")
        self.formality_level = self.static_parameters.config.get("formality", "informal")
        self.include_time = self.static_parameters.config.get("add_timestamp", False)
        self.logger.info(f"Settings loaded: Template='{self.template}', Formality='{self.formality_level}', Timestamp={self.include_time}")

    def execute(self, context: LollmsContextDetails, *args, **kwargs) -> str:
        """Generates a greeting based on parameters and configured settings."""
        name_to_greet = kwargs.get("name_to_greet")
        if not name_to_greet:
            self.logger.warning("Parameter 'name_to_greet' is missing.")
            return "Error: Please provide the name of the person to greet."

        self.logger.info(f"Generating greeting for '{name_to_greet}' with formality '{self.formality_level}'.")

        try:
            # Use the template loaded from static parameters in self.template
            greeting = self.template.format(name=name_to_greet)

            # Add formality suffix (example logic)
            if self.formality_level == "formal":
                greeting += " It is a pleasure to make your acquaintance."
            elif self.formality_level == "casual":
                greeting += " What's up?"

            # Add timestamp if enabled
            if self.include_time:
                now_str = datetime.datetime.now().strftime('%H:%M:%S')
                greeting += f" (Current time: {now_str})"

            self.logger.info(f"Generated greeting: {greeting}")
            return greeting

        except KeyError as ke:
            self.logger.error(f"Template error: {ke}. Template in use: '{self.template}'")
            trace_exception(ke)
            return f"Error: Greeting template is invalid (missing '{{name}}'). Check function settings. Current template: '{self.template}'"
        except Exception as e:
            self.logger.error(f"Error generating greeting for {name_to_greet}")
            trace_exception(e)
            return f"Error generating greeting: {type(e).__name__}. Check logs."
```

## 11. Leveraging LoLLMs Helpers (`self.app`, `self.personality`)

Your function call instances have access to powerful helper methods via `self.app` (the global application) and `self.personality` (the associated personality, often containing an `APScript` instance).

### LLM Interaction Helpers (via `self.personality`)

These allow your function to use the LLM for internal tasks. **Remember the `callback=self.personality.sink` parameter to hide intermediate LLM outputs from the main chat UI.**

*   **`fast_gen(self, prompt: str, max_generation_size: Optional[int] = None, placeholders: dict = {}, sacrifice: List[str] = ["previous_discussion"], debug: bool = False, callback: Optional[Callable] = None, show_progress: bool = False, temperature: Optional[float] = None, top_k: Optional[int] = None, top_p: Optional[float] = None, repeat_penalty: Optional[float] = None, repeat_last_n: Optional[int] = None) -> str`**
    *   Quick text generation, handles context automatically.
    *   Returns: Generated text string.

*   **`generate_code(self, prompt: str, images: List[Any] = [], template: Optional[str] = None, language: str = "json", code_tag_format: str = "markdown", max_size: Optional[int] = None, temperature: Optional[float] = None, top_k: Optional[int] = None, top_p: Optional[float] = None, repeat_penalty: Optional[float] = None, repeat_last_n: Optional[int] = None, callback: Optional[Callable] = None, debug: Optional[bool] = None, return_full_generated_code: bool = False, accept_all_if_no_code_tags_is_present: bool = False, max_continues: int = 3, include_code_directives: bool = True) -> Union[Optional[str], Tuple[Optional[str], str]]`**
    *   Generates structured data or code, extracting from markdown/html blocks.
    *   Returns: Extracted code string or `(code_string, full_llm_response)`, or None.

*   **`generate(self, prompt: str, max_size: Optional[int] = None, temperature: Optional[float] = None, top_k: Optional[int] = None, top_p: Optional[float] = None, repeat_penalty: Optional[float] = None, repeat_last_n: Optional[int] = None, callback: Optional[Callable[[str, int, dict], bool]] = None, debug: bool = False, show_progress: bool = False) -> str`**
    *   Lower-level generation. Manage context size manually.
    *   Returns: Generated text string.

*   **`generate_with_images(self, prompt: str, images: List[Any], max_size: Optional[int] = None, temperature: Optional[float] = None, top_k: Optional[int] = None, top_p: Optional[float] = None, repeat_penalty: Optional[float] = None, repeat_last_n: Optional[int] = None, callback: Optional[Callable[[str, int, dict], bool]] = None, debug: bool = False, show_progress: bool = False) -> str`**
    *   Like `generate`, but for multimodal models.
    *   Returns: Generated text string.

### Utility & Task Helpers (via `self.personality` or `TasksLibrary`)

Leverage the LLM for specific analytical tasks. Access `TasksLibrary` via `self.app.tasks_library`.

*   **`yes_no(self, question: str, context: str = "", max_answer_length: Optional[int] = None, conditionning: str = "", return_explanation: bool = False, callback: Optional[Callable] = None) -> Union[bool, dict]`**
    *   Answers a Yes/No question based on context.
    *   Returns: Boolean or `{"answer": bool, "explanation": str}`.

*   **`multichoice_question(self, question: str, possible_answers: List[Any], context: str = "", max_answer_length: Optional[int] = None, conditionning: str = "", return_explanation: bool = False, callback: Optional[Callable] = None) -> Union[int, dict]`**
    *   Selects the single best option from a list.
    *   Returns: 0-based index or -1. Can return `{"index": int, "explanation": str}`.

*   **`multichoice_ranking(self, question: str, possible_answers: List[Any], context: str = "", max_answer_length: int = 512, conditionning: str = "", return_explanation: bool = False, callback: Optional[Callable] = None) -> dict`**
    *   Ranks a list of options from best to worst.
    *   Returns: `{"ranking": [idx1,...], "explanations": [...]}`.

*   **`sequential_summarize(self, text: str, chunk_processing_prompt: str, final_memory_processing_prompt: str, chunk_processing_output_format:str="markdown", final_output_format:str="markdown", ctx_size:Optional[int]=None, chunk_size:Optional[int]=None, bootstrap_chunk_size:Optional[int]=None, bootstrap_steps:Optional[int]=None, callback: Optional[Callable] = None, step_callback: Optional[Callable[[str, int, int, str], None]] = None, debug: bool = False) -> str`**
    *   Robustly summarizes very long text by processing in chunks.
    *   Returns: Final summary string.

*   **`summarize_text(self, text: str, summary_instruction: str = "summarize", doc_name: str = "chunk", answer_start: str = "", max_generation_size: int = 3000, max_summary_size: int = 512, callback: Optional[Callable] = None, chunk_summary_post_processing: Optional[Callable] = None, summary_mode=SUMMARY_MODE.SUMMARY_MODE_SEQUENCIAL) -> str`** (via `TasksLibrary`)
    *   Simpler interface for summarization.
    *   Returns: Summary string.

*   **`translate(self, text_chunk: str, output_language: str = "french", max_generation_size: int = 3000, ...) -> str`**
    *   Translates text using the LLM.
    *   Returns: Translated text string.

### UI Feedback Helpers (via `self.personality` or `self.app`)

Interact with the LoLLMs Web UI chat interface.

*   **`step_start(self, step_text: str, callback: Optional[Callable] = None)`:** Shows step start in UI.
*   **`step(self, step_text: str, callback: Optional[Callable] = None)`:** Shows intermediate step update.
*   **`step_end(self, step_text: str, success: bool = True, callback: Optional[Callable] = None)`:** Marks step completion.
*   **`set_message_html(self, html_ui: str, callback: Optional[Callable] = None, client_id: Optional[str] = None)`:** Replaces current AI message content with HTML.
*   **`new_message(self, message_text: str, message_type: MSG_OPERATION_TYPE = ..., metadata: List = [], callback: Optional[Callable] = None)`:** Creates a *new* message bubble.
*   **`add_chunk_to_message_content(self, text_chunk: str, callback: Optional[Callable] = None)`:** Appends text to the current AI message bubble.
*   **`finished_message(self, message_text: str = "", callback: Optional[Callable] = None)`:** Signals the end of a message stream.
*   **`InfoMessage(self, content: str, client_id: Optional[str] = None, verbose: Optional[bool] = None)`:** Shows a modal dialog box (blocking).
*   **`ShowBlockingMessage(self, content: str, client_id: Optional[str] = None, verbose: Optional[bool] = None)`:** Shows a non-interactive overlay message.
*   **`HideBlockingMessage(self, client_id: Optional[str] = None, verbose: Optional[bool] = None)`:** Hides the blocking message.
*   **`info/warning/error/success(self, content: str, duration: int = 4, client_id: Optional[str] = None, verbose: Optional[bool] = None)`:** Shows toast notifications.
*   **`notify(self, content: str, notification_type: NotificationType = ..., duration: int = 4, client_id: Optional[str] = None, display_type: NotificationDisplayType = ..., verbose: Optional[bool] = None)`:** Generic notification method.

### Accessing Application State (via `self.app`)

*   **`self.app.config`:** Global `LOLLMSConfig`.
*   **`self.app.model` / `self.app.binding`:** Current LLM model/binding.
*   **`self.app.tti`/`tts`/`stt`/`ttm`/`ttv`:** Active multimodal services (check for `None`).
*   **`self.app.lollms_paths`:** System path configurations.
*   **`self.app.session`:** User session manager.
*   **`self.app.tasks_library`:** Access to task helpers.

## 12. Best Practices and Tips

*   **Clear Descriptions:** Crucial for LLM understanding (`config.yaml`).
*   **Error Handling:** Use `try...except`, return informative strings, use `trace_exception` and `self.logger.error(..., exc_info=True)`.
*   **Security:** Sanitize paths (`lollms.security.sanitize_path`), avoid `eval`/`exec`/`subprocess.shell=True` on untrusted input, protect API keys (static params/env vars).
*   **User Feedback:** Use UI helpers (`step_start/end`, `set_message_html`, notifications) for tasks > 1-2 seconds.
*   **Logging:** Log key steps, parameters, results, and errors using `self.logger`. Use appropriate levels (`DEBUG`, `INFO`, `WARNING`, `ERROR`).
*   **Dependencies:** Use `pipmaster.ensure_packages` with the format `{"package-name": "version-specifier"}` at the top of `function.py`.
*   **Return Values (`CLASSIC`):** Keep return strings concise for the LLM. Use `set_message_html` for rich *user* output *before* returning.
*   **Context (`CONTEXT_UPDATE`):** Manage context size. Summarize or select relevant data. `process_output` can clean the final LLM reply.
*   **Modularity:** Smaller, focused functions are better.
*   **Configuration:** Use static parameters for user-tunable settings.
*   **`__init__` Structure:** Follow the mandatory `__init__` structure precisely, especially the order of static param definition and the `super().__init__` call.

## 13. Registering and Using Function Calls

1.  **Placement:** Put your function folder in the zoo (`functions_zoo/<category>/`) or custom folder (`custom_function_calls/`).
2.  **Discovery:** LoLLMs finds them automatically.
3.  **Management (UI):** Use `Settings` -> `Function Calls` to Mount/Unmount, Select/Deselect, and Configure (static params).
4.  **Invocation:**
    *   `CLASSIC`: Triggered by LLM generating ` ```function ... ``` ` block if function is *selected*.
    *   `CONTEXT_UPDATE`: Runs automatically before/after LLM generation if function is *selected*.

## 14. Conclusion

LoLLMs Function Calls transform your AI assistant from a text generator into a capable agent. By mastering the different types, utilizing the provided helper methods for LLM interaction, UI feedback, logging, and dependency management, and adhering to best practices, you can build powerful, reliable, and user-friendly extensions for your LoLLMs assistant.