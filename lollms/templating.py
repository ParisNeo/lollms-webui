class LollmsLLMTemplate:
    """
    A template class for managing LLM (Large Language Model) headers, separators, and message templates.
    This class provides properties and methods to generate headers and templates for system, user, and AI messages.
    """

    def __init__(self, config, personality):
        """
        Initialize the LollmsLLMTemplate class.

        Parameters:
        config (object): A configuration object containing template-related settings.
        personality (object): A personality object containing AI-specific settings (e.g., AI name).
        """
        self.config = config
        self.personality = personality

    # Properties ===============================================

    @property
    def start_header_id_template(self) -> str:
        """Get the start_header_id_template."""
        return self.config.start_header_id_template

    @property
    def end_header_id_template(self) -> str:
        """Get the end_header_id_template."""
        return self.config.end_header_id_template

    @property
    def system_message_template(self) -> str:
        """Get the system_message_template."""
        return self.config.system_message_template

    @property
    def separator_template(self) -> str:
        """Get the separator template."""
        return self.config.separator_template

    @property
    def start_user_header_id_template(self) -> str:
        """Get the start_user_header_id_template."""
        return self.config.start_user_header_id_template

    @property
    def end_user_header_id_template(self) -> str:
        """Get the end_user_header_id_template."""
        return self.config.end_user_header_id_template

    @property
    def end_user_message_id_template(self) -> str:
        """Get the end_user_message_id_template."""
        return self.config.end_user_message_id_template

    @property
    def start_ai_header_id_template(self) -> str:
        """Get the start_ai_header_id_template."""
        return self.config.start_ai_header_id_template

    @property
    def end_ai_header_id_template(self) -> str:
        """Get the end_ai_header_id_template."""
        return self.config.end_ai_header_id_template

    @property
    def end_ai_message_id_template(self) -> str:
        """Get the end_ai_message_id_template."""
        return self.config.end_ai_message_id_template

    @property
    def system_full_header(self) -> str:
        """Generate the full system header."""
        return f"{self.start_header_id_template}{self.system_message_template}{self.end_header_id_template}"

    @property
    def user_full_header(self) -> str:
        """Generate the full user header."""
        return f"{self.start_user_header_id_template}{self.config.user_name}{self.end_user_header_id_template}"

    @property
    def ai_full_header(self) -> str:
        """Generate the full AI header."""
        return f"{self.start_ai_header_id_template}{self.personality.name}{self.end_ai_header_id_template}"

    # Methods ===============================================

    def system_custom_header(self, ai_name: str) -> str:
        """
        Generate a custom system header with the specified AI name.

        Parameters:
        ai_name (str): The name of the AI to include in the header.

        Returns:
        str: The custom system header.
        """
        return f"{self.start_header_id_template}{ai_name}{self.end_user_header_id_template}"

    def user_custom_header(self, ai_name: str) -> str:
        """
        Generate a custom user header with the specified AI name.

        Parameters:
        ai_name (str): The name of the AI to include in the header.

        Returns:
        str: The custom user header.
        """
        return f"{self.start_user_header_id_template}{ai_name}{self.end_user_header_id_template}"

    def ai_custom_header(self, ai_name: str) -> str:
        """
        Generate a custom AI header with the specified AI name.

        Parameters:
        ai_name (str): The name of the AI to include in the header.

        Returns:
        str: The custom AI header.
        """
        return f"{self.start_ai_header_id_template}{ai_name}{self.end_ai_header_id_template}"