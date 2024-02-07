import datetime
import json
import yaml
from enum import Enum

__project__ = "lollms-webui"
__author__ = "ParisNeo"
__description__ = ""


class Role(Enum):
    SYSTEM = "system"
    AI = "ai"
    USER = "user"



class Message:
    """
    Class representing a message in a discussion.
    """

    def __init__(self, sender, role:Role, model:str, content:str, sending_date=None, rank=0):
        """
        Initializes a new Message object.

        Args:
            sender (str): The name of the sender.
            role (str): The role of the sender (system, ai, user).
            model (str): The model name or "human".
            content (str): The content of the message.
            sending_date (datetime.datetime, optional): The sending date and time. Defaults to the current date and time.
            rank (int, optional): The rank of the message. Defaults to 0.
        """
        self.sender = sender
        self.role = role
        self.model = model
        self.content = content
        self.sending_date = sending_date or datetime.datetime.now()
        self.rank = rank

    def rank_up(self):
        """
        Increases the rank of the message by 1.
        """
        self.rank += 1

    def rank_down(self):
        """
        Decreases the rank of the message by 1.
        """
        if self.rank > 0:
            self.rank -= 1

    def to_json(self):
        """
        Converts the message object to JSON format.

        Returns:
            str: The message object in JSON format.
        """
        return json.dumps(self.__dict__)

    def to_yaml(self):
        """
        Converts the message object to YAML format.

        Returns:
            str: The message object in YAML format.
        """
        return yaml.dump(self.__dict__)