import os
from typing import List
from discussions.discussion import Discussion

class DiscussionDatabase:
    """
    Class representing a discussion database.
    """

    def __init__(self, name, root_folder):
        """
        Initializes a new DiscussionDatabase object.

        Args:
            name (str): The name of the discussion database.
            root_folder (str): The root folder of the discussion database.
        """
        self.name = name
        self.root_folder = root_folder
        self.discussions:List[Discussion] = {}

    def load_discussions(self):
        """
        Loads the discussions from the discussion database.
        """
        for discussion_folder in os.listdir(self.root_folder):
            discussion = Discussion(discussion_folder)
            discussion.load_messages()
            self.discussions[discussion_folder] = discussion

    def save_discussions(self):
        """
        Saves the discussions to the discussion database.
        """
        for discussion in self.discussions.values():
            discussion.save_messages()

    def remove_discussion(self, discussion_name):
        """
        Removes a discussion from the discussion database.

        Args:
            discussion_name (str): The name of the discussion to remove.
        """
        del self.discussions[discussion_name]
        os.rmdir(f'{self.root_folder}/{discussion_name}')
        
    def list_discussions(self):
        """
        Lists all the discussions in the discussion database.

        Returns:
            List[str]: A list of discussion names.
        """
        return list(self.discussions.keys())

    def new_discussion(self, discussion_name):
        """
        Creates a new discussion in the discussion database.

        Args:
            discussion_name (str): The name of the new discussion.
        """
        discussion = Discussion(discussion_name)
        self.discussions[discussion_name] = discussion
        os.mkdir(f'{self.root_folder}/{discussion_name}')