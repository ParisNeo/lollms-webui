The personality class inherits from APScript that can be imported using
`from lollms.personality import APScript`
APScript has access to personality object via self.personality

Here is a typical example of APScript class

```python
class Processor(APScript):
    """
    Defines the behavior of a personality in a programmatic manner, inheriting from APScript.
    
    Attributes:
        callback (Callable): Optional function to call after processing.
    """
    
    def __init__(
                 self, 
                 personality: AIPersonality,
                 callback: Callable = None,
                ) -> None:
        """
        Initializes the Processor class with a personality and an optional callback.

        Parameters:
            personality (AIPersonality): The personality instance.
            callback (Callable, optional): A function to call after processing. Defaults to None.
        """

    def mounted(self):
        """
        triggered when mounted
        """
        pass


    def selected(self):
        """
        triggered when selected
        """
        pass
        # self.play_mp3(Path(__file__).parent.parent/"assets"/"borg_threat.mp3")


    # Note: Remember to add command implementations and additional states as needed.

    def install(self):
        """
        Install the necessary dependencies for the personality.

        This method is responsible for setting up any dependencies or environment requirements
        that the personality needs to operate correctly. It can involve installing packages from
        a requirements.txt file, setting up virtual environments, or performing initial setup tasks.
        
        The method demonstrates how to print a success message using the ASCIIColors helper class
        upon successful installation of dependencies. This step can be expanded to include error
        handling and logging for more robust installation processes.

        Example Usage:
            processor = Processor(personality)
            processor.install()
        
        Returns:
            None
        """        

    def help(self, prompt="", full_context=""):
        """
        Displays help information about the personality and its available commands.

        This method provides users with guidance on how to interact with the personality,
        detailing the commands that can be executed and any additional help text associated
        with those commands. It's an essential feature for enhancing user experience and
        ensuring users can effectively utilize the personality's capabilities.

        Args:
            prompt (str, optional): A specific prompt or command for which help is requested.
                                    If empty, general help for the personality is provided.
            full_context (str, optional): Additional context information that might influence
                                          the help response. This can include user preferences,
                                          historical interaction data, or any other relevant context.

        Example Usage:
            processor = Processor(personality)
            processor.help("How do I use the 'add_file' command?")
        
        Returns:
            None
        """


    def run_workflow(self, prompt:str, previous_discussion_text:str="", callback: Callable[[str | list | None, MSG_OPERATION_TYPE, str, AIPersonality| None], bool]=None, context_details:dict=None, client:Client=None):
        """
        This function generates code based on the given parameters.

        Args:
            full_prompt (str): The full discussion since the beginning.
            prompt (str): The last message given by the user inside the discussion.
            context_details (dict): A dictionary containing the following context details for code generation:
                - conditionning (str): The conditioning information.
                - documentation (str): The documentation information.
                - knowledge (str): The knowledge information.
                - user_description (str): The user description information.
                - discussion_messages (str): The discussion messages information.
                - positive_boost (str): The positive boost information.
                - negative_boost (str): The negative boost information.
                - current_language (str): The force language information.
                - fun_mode (str): The fun mode conditionning text
                - ai_prefix (str): The AI prefix information.
            n_predict (int): The number of predictions to generate.
            client_id: The client ID for code generation.
            callback (function, optional): The callback function for code generation.

        Returns:
            None
        """
```


Here is the list of APScript useful methods usable in run_workflow:
fast_gen:
    Fast way to generate text from prompt
    
    This method takes in a prompt, maximum generation size, optional placeholders, sacrifice list, and debug flag.
    It reshapes the context before performing text generation by adjusting and cropping the number of tokens.
    
    Parameters:
    - prompt (str): The input prompt for text generation.
    - max_generation_size (int): The maximum number of tokens to generate.
    - placeholders (dict, optional): A dictionary of placeholders to be replaced in the prompt. Defaults to an empty dictionary.
    - sacrifice (list, optional): A list of placeholders to sacrifice if the window is bigger than the context size minus the number of tokens to generate. Defaults to ["previous_discussion"].
    - debug (bool, optional): Flag to enable/disable debug mode. Defaults to False.
    
    Returns:
    - str: The generated text after removing special tokens ("<s>" and "</s>") and stripping any leading/trailing whitespace.

step_start:
    This triggers a step start for multi steps actions

    Args:
        step_text (str): The step text

    if not callback and self.callback:
        callback = self.callback

    if callback:
        callback(step_text, MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_STEP_START)

step_end:
        This triggers a step end

        Args:
            step_text (str): The step text must be the same ass the one used for start

full:
        full_text:str
        This sends full text to front end

        Args:
            full_text (str): The text to send to the ui for the user
            callback (callable, optional): A callable with this signature (str, MSG_TYPE) to send the text to. Defaults to None.

yes_no(self, question: str, context:str="", max_answer_length: int = 50) -> bool:

        Analyzes the user prompt and answers whether it is asking to generate an image.

        Args:
            question (str): The user's message.
            max_answer_length (int, optional): The maximum length of the generated answer. Defaults to 50.

        Returns:
            bool: True if the user prompt is asking to generate an image, False otherwise.

yes_no(self, question: str, context:str="", max_answer_length: int = 50) -> bool:

        Analyzes the user prompt and answers whether it is asking to generate an image.

        Args:
            question (str): The user's message.
            max_answer_length (int, optional): The maximum length of the generated answer. Defaults to 50.

        Returns:
            bool: True if the user prompt is asking to generate an image, False otherwise.

def multichoice_question(self, question: str, possible_answers: list, context: str = "", max_answer_length: int = 50, conditionning="") -> int:
    """
    Interprets a multi-choice question from a user's response. Expects one correct choice; returns -1 if none are correct.

    Args:
        question (str): The multi-choice question.
        possible_answers (List[Any]): List of valid options. Each item can be 'True', 'False', None, or a callable for truth testing.
        context (str, optional): Additional context for the question. Defaults to "".
        max_answer_length (int, optional): Max length of user response. Defaults to 50.
        conditionning (str, optional): System message at the beginning of the prompt. Defaults to "".

    Returns:
        int: Index of the selected option in possible_answers, or -1 if no match.
    """