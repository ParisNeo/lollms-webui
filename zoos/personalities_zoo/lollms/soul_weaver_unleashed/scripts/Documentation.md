APScript useful methods:
fast_gen:
    Fast way to gener       ate text from prompt
    
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