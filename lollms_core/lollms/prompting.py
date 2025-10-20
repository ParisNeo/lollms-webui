from enum import Enum, auto
from typing import Dict, List, Optional
from ascii_colors import ASCIIColors
from lollms.templating import LollmsLLMTemplate
from lollms.function_call import FunctionCall, FunctionType
from lollms.client_session import Client


class LollmsContextDetails:
    """
    A class to manage context details for interactions with a Large Language Model (LLM).

    Attributes:
        client (str): Unique identifier for the client or user interacting with the LLM.
        conditionning (Optional[str]): Optional field to store conditioning information or context for the LLM.
        internet_search_infos (Optional[Dict]): Dictionary to store metadata or details about internet searches performed by the LLM.
        internet_search_results (Optional[List]): List to store the results of internet searches performed by the LLM.
        documentation (Optional[str]): Optional field to store documentation or reference material for the LLM.
        documentation_entries (Optional[List]): List to store individual entries or sections of documentation.
        user_description (Optional[str]): Optional field to store a description or profile of the user.
        discussion_messages (Optional[List]): List to store the history of messages in the current discussion or conversation.
        positive_boost (Optional[float]): Optional field to store a positive boost value for influencing LLM behavior.
        negative_boost (Optional[float]): Optional field to store a negative boost value for influencing LLM behavior.
        current_language (Optional[str]): Optional field to store the current language being used in the interaction.
        fun_mode (Optional[bool]): Optional boolean field to enable or disable "fun mode" for the LLM.
        think_first_mode (Optional[bool]): Optional boolean field to enable or disable "think first mode" for the LLM.
        ai_prefix (Optional[str]): Optional field to store a prefix or identifier for the AI in the conversation.
        extra (Optional[str]): Optional field to store additional custom or extra information.
        available_space (Optional[int]): Optional field to store the available space or capacity for the context.
        skills (Optional[Dict]): Dictionary to store skills or capabilities of the LLM.
        is_continue (Optional[bool]): Optional boolean field to indicate if the LLM is continuing from a previous chunk or context.
        previous_chunk (Optional[str]): Optional field to store the previous chunk of text or context.
        prompt (Optional[str]): Optional field to store the current prompt or input for the LLM.
        function_calls (Optional[List]): List to store function calls or actions performed by the LLM.
        debug (bool): Enable or disable debug mode.
        ctx_size (int): The maximum context size for the LLM.
        max_n_predict (Optional[int]): The maximum number of tokens to generate.
        model : The model (required to perform tokenization)
    """

    def __init__(
        self,
        client:Client,
        conditionning: Optional[str] = None,
        internet_search_infos: Optional[Dict] = None,
        internet_search_results: Optional[List] = None,
        documentation: Optional[str] = None,
        documentation_entries: Optional[List] = None,
        user_description: Optional[str] = None,
        discussion_messages: Optional[List] = None,
        positive_boost: Optional[float] = None,
        negative_boost: Optional[float] = None,
        current_language: Optional[str] = None,
        fun_mode: Optional[bool] = False,
        think_first_mode: Optional[bool] = False,
        ai_prefix: Optional[str] = None,
        extra: Optional[str] = "",
        available_space: Optional[int] = None,
        skills: Optional[Dict] = None,
        is_continue: Optional[bool] = False,
        previous_chunk: Optional[str] = None,
        prompt: Optional[str] = None,
        function_calls: Optional[List] = None,
        debug: bool = False,
        ctx_size: int = 2048,
        max_n_predict: Optional[int] = None,
        model = None
    ):
        """Initialize the LollmsContextDetails instance with the provided attributes."""
        self.client = client
        self.conditionning = conditionning
        self.internet_search_infos = internet_search_infos if internet_search_infos is not None else {}
        self.internet_search_results = internet_search_results if internet_search_results is not None else []
        self.documentation = documentation
        self.documentation_entries = documentation_entries if documentation_entries is not None else []
        self.user_description = user_description
        self.discussion_messages = discussion_messages if discussion_messages is not None else []
        self.positive_boost = positive_boost
        self.negative_boost = negative_boost
        self.current_language = current_language
        self.fun_mode = fun_mode
        self.think_first_mode = think_first_mode
        self.ai_prefix = ai_prefix
        self.extra = extra
        self.available_space = available_space
        self.skills = skills if skills is not None else {}
        self.is_continue = is_continue
        self.previous_chunk = previous_chunk
        self.prompt = prompt
        self.function_calls:List[dict] = function_calls if function_calls is not None else []
        self.debug = debug
        self.ctx_size = ctx_size
        self.max_n_predict = max_n_predict
        self.model = model
        self.ai_output = ""


    def transform_function_to_text(self, template, func):
        function_texts = []

        # Function header
        function_text = "## Function" + f'\nfunction_name: {func["name"]}\nfunction_description: {func["description"]}\n'

        # Parameters section
        function_text += "function_parameters:\n"
        for param in func["parameters"]:
            param_type = "string" if param["type"] == "str" else param["type"]
            param_description = param.get("description", "")
            function_text += f'  - {param["name"]} ({param_type}): {param_description}\n'


        function_texts.append(function_text.strip())
        return "\n\n".join(function_texts)

    def build_prompt(self, template: LollmsLLMTemplate, custom_entries: str = "", suppress: List[str] = [], ignore_function_calls:bool=False) -> str:
        """
        Builds a prompt from the context details using the integrated template system.

        Args:
            template (LollmsLLMTemplate): The template system to use for constructing the prompt.
            custom_entries (str): Additional custom entries to be included in the prompt.
            suppress (List[str]): A list of fields to exclude from the prompt.

        Returns:
            str: The constructed prompt.
        """
        full_context = []
        sacrifice_id = 0
        def extract_context_entry(field_name: str, header: Optional[str] = None, footer: Optional[str] = None):
            """
            Helper function to append context if the field is not suppressed.

            Args:
                field_name (str): The name of the field to append.
                header (Optional[str]): An optional header to prepend to the field content.
            """
            if getattr(self, field_name) and field_name not in suppress:
                content:str = getattr(self, field_name)
                entry = ""
                if header:
                    entry = header
                entry += content.strip()
                if footer:
                    entry += "\n"+footer
                return entry
            return ""
        
        def append_context(field_name: str, header: Optional[str] = None, footer: Optional[str] = None):
            """
            Helper function to append context if the field is not suppressed.

            Args:
                field_name (str): The name of the field to append.
                header (Optional[str]): An optional header to prepend to the field content.
            """
            if getattr(self, field_name) and field_name not in suppress:
                content:str = getattr(self, field_name)
                entry = ""
                if header:
                    entry = header
                entry += content.strip()
                if footer:
                    entry += "\n"+footer
                full_context.append(entry)
                nonlocal sacrifice_id
                sacrifice_id += 1

        # Append each field to the full context if it exists and is not suppressed
        append_context("conditionning", template.system_full_header)
        append_context("documentation", "# documentation:\n")
        append_context("internet_search_results", "# Internet search results:\n")
        append_context("user_description", "# user description:\n")
        append_context("positive_boost", "# positive_boost: ")
        append_context("negative_boost", "# negative_boost: ")
        append_context("current_language", "# current_language: ")
        append_context("fun_mode")
        append_context("think_first_mode")
        
        append_context("extra")

        discussion = extract_context_entry("discussion_messages", template.system_custom_header("discussion")+"\n")
       
        found_classic_function = False
        if not ignore_function_calls:
            for function_call in self.function_calls:
                fc:FunctionCall = function_call["class"]
                if fc.function_type == FunctionType.CONTEXT_UPDATE:
                    full_context = fc.update_context(self, full_context)
                elif fc.function_type == FunctionType.CLASSIC:
                    if not found_classic_function:
                        found_classic_function = True
                    full_context.append(self.transform_function_to_text(template,function_call))
                    full_context = fc.update_context(self, full_context)
                    
            if found_classic_function:
                full_context.append(
                    "# Function Calls instructions"+"\n" + "\n".join([
                        "You have access to functions presented to you in the available functions listed above.",
                        "If you need to call a function, use this exact syntax:",
                        "```function",
                        "{",
                        '  "function_name": "name_of_the_function_to_call",',
                        '  "function_parameters": {',
                        '    "parameter1": value1,',
                        '    "parameter2": value2',
                        "  }",
                        "}",
                        "```",
                        "Do not explain how the function call works, just call it with the parameters",
                        "Once you call the function, it will be executed and the output returned to the user.",
                        "It is mandatory to use the function markdown tag (not json) or it won't be executed."
                        "Important Notes:",
                        "- **Always** enclose the function call in a `function` markdown code block.",
                        "- Make sure the content of the function markdown code block is a valid json.",
                    ]
                )
                )


        full_context.append(discussion)
        # Add custom entries if provided
        if custom_entries:
            full_context+=custom_entries

        # Build the final prompt
        prompt = template.separator_template.join(full_context)

        # Debugging information
        if self.debug and self.model:
            nb_prompt_tokens = self.model.count_tokens(prompt)
            nb_tokens = min(
                self.ctx_size - nb_prompt_tokens,
                self.max_n_predict if self.max_n_predict else self.ctx_size - nb_prompt_tokens
            )
            print(f"Prompt size : {nb_prompt_tokens}")
            print(f"Requested generation max size : {nb_tokens}")

        return prompt
