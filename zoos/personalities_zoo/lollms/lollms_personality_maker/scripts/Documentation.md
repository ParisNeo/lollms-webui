# LoLLMs Personality Development Documentation

## Table of Contents

- [LoLLMs Personality Development Documentation](#lollms-personality-development-documentation)
  - [Table of Contents](#table-of-contents)
  - [1. Introduction ](#1-introduction-)
  - [2. Personality Types ](#2-personality-types-)
  - [3. Personality Structure ](#3-personality-structure-)
  - [4. Scripted Personalities ](#4-scripted-personalities-)
    - [4.1 Processor Class ](#41-processor-class-)
    - [4.2 Key Methods ](#42-key-methods-)
    - [4.3 Workflow Execution ](#43-workflow-execution-)
    - [4.4 User Interaction ](#44-user-interaction-)
    - [4.5 AI Querying ](#45-ai-querying-)
    - [4.6 Asset Management ](#46-asset-management-)
    - [4.7 Text Processing ](#47-text-processing-)
    - [4.8 Code Handling ](#48-code-handling-)
  - [5. Advanced Features ](#5-advanced-features-)
    - [5.1 Text-to-Image Generation ](#51-text-to-image-generation-)
    - [5.2 Settings System ](#52-settings-system-)
  - [6. Generate code](#6-generate-code)
  - [7. Best Practices ](#7-best-practices-)
  - [7. Conclusion ](#7-conclusion-)

## 1. Introduction <a name="introduction"></a>

LoLLMs (Lord of Large Language Multimodal Systems) is a powerful framework for creating AI personalities with advanced capabilities. This documentation focuses on developing scripted personalities, which offer more complex and interactive functionalities compared to standard personalities.

## 2. Personality Types <a name="personality-types"></a>

LoLLMs supports two types of personalities:

1. **Standard Personalities**: Controlled primarily by a system prompt.
2. **Scripted Personalities**: Utilize both a system prompt and a Python script for complex interactions and workflows.

## 3. Personality Structure <a name="personality-structure"></a>

Personalities in LoLLMs are organized within the personalities zoo. Each personality resides in its own folder within a category folder. The structure is as follows:

```
personalities_zoo/
├── category_1/
│   ├── personality_1/
│   │   ├── config.yaml
│   │   ├── assets/
│   │   │   └── logo.png
│   │   ├── files/ (optional)
│   │   ├── audio/ (optional)
│   │   └── scripts/
│   │       └── processor.py
│   └── personality_2/
└── category_2/
    └── ...
```

Key components:
- `config.yaml`: Contains metadata about the personality (name, author, description, etc.)
- `assets/logo.png`: The personality's logo
- `files/`: Optional folder for augmented personalities (used by the inner RAG system)
- `audio/`: Optional folder for prerecorded audio
- `scripts/processor.py`: Main script for scripted personalities

## 4. Scripted Personalities <a name="scripted-personalities"></a>

Scripted personalities offer advanced control and functionality through Python code. The main component is the `Processor` class in `processor.py`.

### 4.1 Processor Class <a name="processor-class"></a>

The `Processor` class inherits from `APScript` and defines the behavior of the personality:

```python
from lollms.personality import APScript, AIPersonality
from lollms.client_session import Client
from lollms.types import MSG_OPERATION_TYPE

class Processor(APScript): # The class must be called Processor and enherit from APScript
    def __init__(self, personality: AIPersonality, callback: Callable = None) -> None:
        # Initialize configuration and states
        personality_config_template = ConfigTemplate([
            # Configuration entries in this format:
            {"name":"the_name_of_the_parameter_with_no_space","type":"the type: str, int, float, options","value":"the default value of the setting", "help":"A  help text"},
        ])

        personality_config_vals = BaseConfig.from_template(personality_config_template)
        personality_config = TypedConfig(personality_config_template, personality_config_vals)
        
        super().__init__(
            personality,
            personality_config,
            states_list=[
                {
                    "name": "idle",
                    "commands": {
                        "help": self.help, # Here we can add more commands that will be shown as menues
                    },
                    "default": None
                },
            ],
            callback=callback
        )

        # The settings may be read like this:
        self.personality_config.setting_name
```

### 4.2 Key Methods <a name="key-methods"></a>

- `mounted()`: Triggered when the personality is mounted
- `selected()`: Triggered when the personality is selected
- `install()`: Sets up necessary dependencies
- `help(prompt="", full_context="")`: Provides help information
- `run_workflow(context_details, client, callback)`: Main method for executing the personality's workflow

### 4.3 Workflow Execution <a name="workflow-execution"></a>

The `run_workflow` method is the core of a scripted personality. It handles user input and orchestrates the personality's response:

```python
def run_workflow(self,  context_details:dict=None, client:Client=None,  callback: Callable[[str | list | None, MSG_OPERATION_TYPE, str, AIPersonality| None], bool]=None):
    self.callback = callback
    # to build the full prompt from context:
    full_prompt = self.build_prompt_from_context_details(context_details)
    # You can also use the context_details content directly
    # To generate text without too much configurations, just use
    out = self.fast_gen(full_prompt)
    # To show the message to the user:
    self.set_message_content(out)
```

context_details contains alot of information that can be used by the AI:
```python
    context_details = {
        "client_id":the id of the client using the service,
        "conditionning":the doncitioning text,
        "internet_search_infos":internet search infos (empty if internet is off),
        "internet_search_results":internet search results (empty if internet is off),
        "documentation":documentation (empty if no documentation is used),
        "documentation_entries":the documentation separated by type as there is datalakes, discussion documents, skills library... (empty if no documentation is used),
        "user_description":the user description (empty if deactivated),
        "discussion_messages":the full descussion until current time,
        "positive_boost":a text to boost ai positively (empty if deactivated),
        "negative_boost":a text to boost ai negatively (empty if deactivated),
        "current_language":The language the ai must use to answer,
        "fun_mode":if this moide is on, then the AI must respond in fally way (empty if deactivated),
        "ai_prefix":the prefix of AI ,
        "extra":"",
        "available_space":how much context space left,
        "skills":information about skills the AI must remember(empty if deactivated),
        "is_continue":true if this is a conotinue from previous message,
        "previous_chunk":previous_chunk,
        "prompt":The user last prompt
    } 
```


### 4.4 User Interaction <a name="user-interaction"></a>

Scripted personalities can interact with users through various methods:

- `set_message_content(text)`: Sets the current AI message output
- `add_chunk_to_message_content(text)`: Adds a new chunk to the current message
- `step_start(step_text)` and `step_end(step_text)`: Show workflow execution steps
- `json(dict)`: Display JSON data
- `ui(ui_string)`: Send complete UI with HTML/CSS/JavaScript

Example:
```python
self.step_start("Processing user input")
result = self.process_input(prompt)
self.step_end("Input processed successfully")

self.json({"result": result})
```

### 4.5 AI Querying <a name="ai-querying"></a>

Scripted personalities can query the AI for decision-making:

- `yes_no(question, context="", max_answer_length=50, conditioning="")->bool`: Ask yes/no questions to the LLM
- `multichoice_question(question, possible_answers, context="", max_answer_length=50, conditioning="")->int`: Ask multiple-choice questions to LLM

Example:
```python
if self.yes_no("Does the user want to generate an image?", context=prompt):
    self.generate_image()
```

### 4.6 Asset Management <a name="asset-management"></a>

Access personality and discussion assets:

- Personality assets:
  - `self.personality.text_files`
  - `self.personality.image_files`
  - `self.personality.audio_files`

- Discussion assets:
  - `client.discussion.text_files`
  - `client.discussion.image_files`
  - `client.discussion.audio_files`

### 4.7 Text Processing <a name="text-processing"></a>

Use the summarization feature for processing large texts:

```python
summary = self.summarize_text(
    text,
    summary_instruction="Summarize the key points",
    max_summary_size=512,
    summary_mode=SUMMARY_MODE.SUMMARY_MODE_HIERARCHICAL
)
```

### 4.8 Code Handling <a name="code-handling"></a>

Extract and process code blocks from AI responses:

```python
code_blocks = self.extract_code_blocks(ai_response)
for block in code_blocks:
    print(f"File: {block['file_name']}, Type: {block['type']}")
    print(block['content'])
```

## 5. Advanced Features <a name="advanced-features"></a>

### 5.1 Text-to-Image Generation <a name="text-to-image-generation"></a>

Generate images using the built-in text-to-image service:

```python
file, infos = self.tti.paint(
    positive_prompt,
    negative_prompt,
    self.personality_config.sampler_name,
    self.personality_config.seed,
    self.personality_config.scale,
    self.personality_config.steps,
    self.personality_config.img2img_denoising_strength,
    width=self.personality_config.width,
    height=self.personality_config.height,
    output_path=client.discussion.discussion_folder
)

escaped_url = discussion_path_to_url(file)
self.set_message_content(f"Generated image: {escaped_url}")
```

### 5.2 Settings System <a name="settings-system"></a>

Implement customizable settings for your personality:

```python
personality_config_template = ConfigTemplate([
    {"name": "image_size", "type": "int", "value": 512, "help": "Size of generated images"},
    {"name": "style", "type": "string", "options": ["realistic", "cartoon", "abstract"], "value": "realistic", "help": "Image generation style"}
])
```

Access settings in your code:
```python
image_size = self.personality_config.image_size
style = self.personality_config.style
```
## 6. Generate code
Use this method:
```python
    def generate_code(self, prompt, images=[], max_size = None,  temperature = None, top_k = None, top_p=None, repeat_penalty=None, repeat_last_n=None, callback=None, debug=False ):
```
This method generates a code from the prompt. all the other parameters are optional.

## 7. Best Practices <a name="best-practices"></a>

1. Use AI querying when decision making is needed.
2. Use the step system to provide clear progress indicators to users.
3. Implement error handling and provide informative error messages.
4. Use the settings system to make your personality customizable.
5. Leverage the AI querying methods for dynamic decision-making.
6. Utilize assets and discussion files for context-aware responses.
7. Implement the `help` method thoroughly to guide users.




## 7. Conclusion <a name="conclusion"></a>

Scripted personalities in LoLLMs offer powerful capabilities for creating advanced AI interactions. By leveraging the provided methods and features, developers can create rich, interactive, and context-aware AI personalities that can perform complex tasks and provide engaging user experiences.

Remember to test your personality thoroughly and consider edge cases in user interactions. The flexibility of the scripted approach allows for continuous improvement and expansion of your AI personality's capabilities.

