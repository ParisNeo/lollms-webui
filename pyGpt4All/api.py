######
# Project       : GPT4ALL-UI
# File          : api.py
# Author        : ParisNeo with the help of the community
# Supported by Nomic-AI
# Licence       : Apache 2.0
# Description   : 
# A simple api to communicate with gpt4all-ui and its models.
######
import gc
import sys
from queue import Queue
from datetime import datetime
from pyGpt4All.db import DiscussionsDB
from pyGpt4All.backends import BACKENDS_LIST
__author__ = "parisneo"
__github__ = "https://github.com/nomic-ai/gpt4all-ui"
__copyright__ = "Copyright 2023, "
__license__ = "Apache 2.0"

class GPT4AllAPI():
    def __init__(self, config:dict, personality:dict, config_file_path:str) -> None:
        self.config = config
        self.personality = personality
        self.config_file_path = config_file_path

        # This is the queue used to stream text to the ui as the bot spits out its response
        self.text_queue = Queue(0)

        # Keeping track of current discussion and message
        self.current_discussion = None
        self.current_message_id = 0

        self.db_path = config["db_path"]

        # Create database object
        self.db = DiscussionsDB(self.db_path)

        # If the database is empty, populate it with tables
        self.db.populate()

        # This is used to keep track of messages 
        self.full_message_list = []

        # Select backend
        self.backend = BACKENDS_LIST[self.config["backend"]]

        # Build chatbot
        self.chatbot_bindings = self.create_chatbot()
        print("Chatbot created successfully")

        # tests the model
        """
        self.prepare_reception()
        self.discussion_messages = "Instruction: Act as gpt4all. A kind and helpful AI bot built to help users solve problems.\nuser: how to build a water rocket?\ngpt4all:"
        self.chatbot_bindings.generate(
            self.discussion_messages,
            new_text_callback=self.new_text_callback,
            n_predict=372,
            temp=self.config['temp'],
            top_k=self.config['top_k'],
            top_p=self.config['top_p'],
            repeat_penalty=self.config['repeat_penalty'],
            repeat_last_n = self.config['repeat_last_n'],
            #seed=self.config['seed'],
            n_threads=self.config['n_threads']
        )        
        
        """

        # generation status
        self.generating=False

    def create_chatbot(self):
        try:
            return self.backend(self.config)
        except Exception as ex:
            print(f"Exception {ex}")
            return None
    
    def condition_chatbot(self, conditionning_message):
        if self.current_discussion is None:
            self.current_discussion = self.db.load_last_discussion()
        
        message_id = self.current_discussion.add_message(
            "conditionner", 
            conditionning_message, 
            DiscussionsDB.MSG_TYPE_CONDITIONNING,
            0,
            0
        )
        self.current_message_id = message_id
        if self.personality["welcome_message"]!="":
            message_id = self.current_discussion.add_message(
                self.personality["name"], self.personality["welcome_message"], 
                DiscussionsDB.MSG_TYPE_NORMAL,
                0,
                self.current_message_id
            )
        
            self.current_message_id = message_id
        return message_id

    def prepare_reception(self):
        self.bot_says = ""
        self.full_text = ""
        self.is_bot_text_started = False
        #self.current_message = message

    def create_new_discussion(self, title):
        self.current_discussion = self.db.create_discussion(title)
        # Get the current timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Chatbot conditionning
        self.condition_chatbot(self.personality["personality_conditionning"])
        return timestamp

    def prepare_query(self, message_id=-1):
        messages = self.current_discussion.get_messages()
        self.full_message_list = []
        for message in messages:
            if message["id"]<= message_id or message_id==-1: 
                if message["type"]!=self.db.MSG_TYPE_CONDITIONNING:
                    if message["sender"]==self.personality["name"]:
                        self.full_message_list.append(self.personality["ai_message_prefix"]+message["content"])
                    else:
                        self.full_message_list.append(self.personality["user_message_prefix"] + message["content"])

        link_text = self.personality["link_text"]

        if len(self.full_message_list) > self.config["nb_messages_to_remember"]:
            discussion_messages = self.personality["personality_conditionning"]+ link_text.join(self.full_message_list[-self.config["nb_messages_to_remember"]:])
        else:
            discussion_messages = self.personality["personality_conditionning"]+ link_text.join(self.full_message_list)
        
        discussion_messages += link_text + self.personality["ai_message_prefix"]
        return discussion_messages # Removes the last return

    def get_discussion_to(self, message_id=-1):
        messages = self.current_discussion.get_messages()
        self.full_message_list = []
        for message in messages:
            if message["id"]<= message_id or message_id==-1: 
                if message["type"]!=self.db.MSG_TYPE_CONDITIONNING:
                    if message["sender"]==self.personality["name"]:
                        self.full_message_list.append(self.personality["ai_message_prefix"]+message["content"])
                    else:
                        self.full_message_list.append(self.personality["user_message_prefix"] + message["content"])

        link_text = self.personality["link_text"]

        if len(self.full_message_list) > self.config["nb_messages_to_remember"]:
            discussion_messages = self.personality["personality_conditionning"]+ link_text.join(self.full_message_list[-self.config["nb_messages_to_remember"]:])
        else:
            discussion_messages = self.personality["personality_conditionning"]+ link_text.join(self.full_message_list)
        
        return discussion_messages # Removes the last return

    def new_text_callback(self, text: str):
        print(text, end="")
        sys.stdout.flush()
        self.full_text += text
        if self.is_bot_text_started:
            self.bot_says += text
            self.text_queue.put(text)
            
        #if self.current_message in self.full_text:
        if len(self.discussion_messages) < len(self.full_text):
            self.is_bot_text_started = True
        
    def generate_message(self):
        self.generating=True
        self.text_queue=Queue()
        gc.collect()
        total_n_predict = len(self.discussion_messages)+self.config['n_predict']
        self.chatbot_bindings.generate(
            self.discussion_messages,
            new_text_callback=self.new_text_callback,
            n_predict=total_n_predict,
            temp=self.config['temp'],
            top_k=self.config['top_k'],
            top_p=self.config['top_p'],
            repeat_penalty=self.config['repeat_penalty'],
            repeat_last_n = self.config['repeat_last_n'],
            #seed=self.config['seed'],
            n_threads=self.config['n_threads']
        )
        self.generating=False
