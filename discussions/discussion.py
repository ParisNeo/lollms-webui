import yaml
from typing import List
from discussions.message import Message

class Discussion:
    """
    Class representing a discussion.
    """

    def __init__(self, name):
        """
        Initializes a new Discussion object.

        Args:
            name (str): The name of the discussion.
        """
        self.name = name
        self.messages:List[Message] = []

    def load_messages(self):
        """
        Loads the messages of the discussion from the discussion.yaml file.
        """
        with open(f'{self.name}/discussion.yaml', 'r') as file:
            self.messages = yaml.load(file)

    def save_messages(self):
        """
        Saves the messages of the discussion to the discussion.yaml file.
        """
        with open(f'{self.name}/discussion.yaml', 'w') as file:
            yaml.dump(self.messages, file)

    def remove_message(self, message_index):
        """
        Removes a message from the discussion.

        Args:
            message_index (int): The index of the message to remove.
        """
        self.messages.pop(message_index)
        self.save_messages()

    def add_message(self, message: Message):
        """
        Adds a new message to the discussion.

        Args:
            message (Message): The message to add.
        """
        self.messages.append(message)
        self.save_messages()