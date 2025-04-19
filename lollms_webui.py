"""
File: lollms_web_ui.py
Author: ParisNeo
Description: Singleton class for the LoLLMS web UI.

This class provides a singleton instance of the LoLLMS web UI, allowing access to its functionality and data across multiple endpoints.
"""

import asyncio
import ctypes
import gc
import json
import os
import re
import shutil
import string
import sys
import threading
import time
import traceback
from datetime import datetime
from functools import partial
from pathlib import Path
from typing import Any, Callable, List, Tuple

import git
import numpy as np
import requests
from lollms.app import LollmsApplication
from lollms.binding import (BindingBuilder, BindingType, LLMBinding,
                            LOLLMSConfig, ModelBuilder)
from lollms.function_call import FunctionCall, FunctionType
from lollms.client_session import Client
from lollms.com import LoLLMsCom, NotificationDisplayType, NotificationType
from lollms.config import InstallOption
from lollms.databases.discussions_database import Discussion, DiscussionsDB
from lollms.generation import (RECEPTION_MANAGER, ROLE_CHANGE_DECISION,
                               ROLE_CHANGE_OURTPUT)
from lollms.helpers import ASCIIColors, trace_exception
from lollms.paths import LollmsPaths
from lollms.personality import AIPersonality, PersonalityBuilder
from lollms.server.elf_server import LOLLMSElfServer
from lollms.types import (CONTENT_OPERATION_TYPES, MSG_OPERATION_TYPE,
                          MSG_TYPE, SENDER_TYPES)
from lollms.utilities import (File64BitsManager, PackageManager,
                              PromptReshaper, convert_language_name,
                              find_first_available_file_index,
                              is_asyncio_loop_running, process_ai_output,
                              run_async, yes_or_no_input)
from tqdm import tqdm

if not PackageManager.check_package_installed("requests"):
    PackageManager.install_package("requests")
if not PackageManager.check_package_installed("bs4"):
    PackageManager.install_package("beautifulsoup4")
import requests


def terminate_thread(thread):
    if thread:
        if not thread.is_alive():
            ASCIIColors.yellow("Thread not alive")
            return

        thread_id = thread.ident
        exc = ctypes.py_object(SystemExit)
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, exc)
        if res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, None)
            del thread
            gc.collect()
            raise SystemError("Failed to terminate the thread.")
        else:
            ASCIIColors.yellow(
                "Canceled successfully"
            )  # The current version of the webui


lollms_webui_version = {
    "version_main":"19",
    "version_secondary":"22.42",
    "version_type":"Alpha",
    "version_codename":"Twins"
}




class LOLLMSWebUI(LOLLMSElfServer):
    __instance = None

    @staticmethod
    def build_instance(
        config: LOLLMSConfig,
        lollms_paths: LollmsPaths,
        load_binding=True,
        load_model=True,
        load_voice_service=True,
        load_sd_service=True,
        try_select_binding=False,
        try_select_model=False,
        callback=None,
        args=None,
        sio=None,
    ):
        if LOLLMSWebUI.__instance is None:
            LOLLMSWebUI(
                config,
                lollms_paths,
                load_binding=load_binding,
                load_model=load_model,
                load_sd_service=load_sd_service,
                load_voice_service=load_voice_service,
                try_select_binding=try_select_binding,
                try_select_model=try_select_model,
                callback=callback,
                args=args,
                sio=sio,
            )
        return LOLLMSWebUI.__instance

    def __init__(
        self,
        config: LOLLMSConfig,
        lollms_paths: LollmsPaths,
        load_binding=True,
        load_model=True,
        load_voice_service=True,
        load_sd_service=True,
        try_select_binding=False,
        try_select_model=False,
        callback=None,
        args=None,
        sio=None,
    ) -> None:
        super().__init__(
            config,
            lollms_paths,
            load_binding=load_binding,
            load_model=load_model,
            try_select_binding=try_select_binding,
            try_select_model=try_select_model,
            callback=callback,
            sio=sio,
        )
        self.app_name: str = "LOLLMSWebUI"
        self.version: str = lollms_webui_version
        self.args = args

        self.busy = False
        self.nb_received_tokens = 0

        self.config_file_path = config.file_path
        self.cancel_gen = False

        if self.config.auto_update:
            if self.check_update_():
                ASCIIColors.info("New version found. Updating!")
                self.run_update_script()

        # migrate old databases to new ones:
        databases_path = self.lollms_paths.personal_path / "databases"
        
        if config["discussion_db_name"].endswith(".db"):
            config["discussion_db_name"] = config["discussion_db_name"].replace(
                ".db", ""
            )
            config.save_config()

        self.discussion_db_name = config["discussion_db_name"]

        # Create database object
        self.db = DiscussionsDB(self, self.lollms_paths, self.discussion_db_name)

        # If the database is empty, populate it with tables
        ASCIIColors.info("Checking discussions database... ", end="")
        self.db.create_tables()
        self.db.add_missing_columns()
        ASCIIColors.success("ok")

        # This is used to keep track of messages
        self.download_infos = {}

        # Define a WebSocket event handler
        @sio.event
        async def connect(sid, environ):
            self.session.add_client(sid, sid, self.db.load_last_discussion(), self.db)
            await self.sio.emit("connected", to=sid)
            ASCIIColors.success(f"Client {sid} connected")

        @sio.event
        def disconnect(sid):
            try:
                self.session.add_client(
                    sid, sid, self.db.load_last_discussion(), self.db
                )
                if self.session.get_client(sid).processing:
                    self.session.get_client(sid).schedule_for_deletion = True
                else:
                    # Clients are now kept forever
                    pass  # self.session.remove_client(sid, sid)
            except Exception as ex:
                pass

            ASCIIColors.error(f"Client {sid} disconnected")

        # generation status
        self.generating = False
        ASCIIColors.blue(f"Your personal data is stored here :", end="")
        ASCIIColors.green(f"{self.lollms_paths.personal_path}")

        self.start_servers()

    def get_uploads_path(self, client_id):
        return self.session.get_client(
            client_id
        ).discussion_path  # self.db.discussion_db_path/f'{["discussion"].discussion_id}'

    # Other methods and properties of the LoLLMSWebUI singleton class
    def check_module_update_(self, repo_path, branch_name="main"):
        try:
            # Open the repository
            ASCIIColors.yellow(f"Checking for updates from {repo_path}")
            repo = git.Repo(repo_path)

            # Fetch updates from the remote for the specified branch
            repo.remotes.origin.fetch(
                refspec=f"refs/heads/{branch_name}:refs/remotes/origin/{branch_name}"
            )

            # Compare the local and remote commit IDs for the specified branch
            local_commit = repo.head.commit
            remote_commit = repo.remotes.origin.refs[branch_name].commit

            # Check if the local branch is behind the remote branch
            is_behind = (
                repo.is_ancestor(local_commit, remote_commit)
                and local_commit != remote_commit
            )

            ASCIIColors.yellow(f"update availability: {is_behind}")

            # Return True if the local branch is behind the remote branch
            return is_behind
        except Exception as e:
            # Handle any errors that may occur during the fetch process
            # trace_exception(e)
            return False

    def check_update_(self, branch_name="main"):
        try:
            # Open the repository
            repo_path = str(Path(__file__).parent / "lollms_core")
            if self.check_module_update_(repo_path, branch_name):
                return True
            repo_path = str(Path(__file__).parent)
            if self.check_module_update_(repo_path, branch_name):
                return True
            return False
        except Exception as e:
            # Handle any errors that may occur during the fetch process
            # trace_exception(e)
            return False

    def run_update_script(self, args=None):
        # deactivate trust store for github and pip package install
        if "REQUESTS_CA_BUNDLE" in os.environ:
            del os.environ["REQUESTS_CA_BUNDLE"]
        update_script = Path(__file__).parent / "update_script.py"

        # Convert Namespace object to a dictionary
        if args:
            args_dict = vars(args)
        else:
            args_dict = {}
        # Filter out any key-value pairs where the value is None
        valid_args = {
            key: value for key, value in args_dict.items() if value is not None
        }

        # Save the arguments to a temporary file
        temp_file = Path(__file__).parent / "temp_args.txt"
        with open(temp_file, "w") as file:
            # Convert the valid_args dictionary to a string in the format "key1 value1 key2 value2 ..."
            arg_string = " ".join(
                [f"--{key} {value}" for key, value in valid_args.items()]
            )
            file.write(arg_string)

        os.system(f"python {update_script}")
        sys.exit(0)

    def run_restart_script(self, args):
        restart_script = Path(__file__).parent / "restart_script.py"

        # Convert Namespace object to a dictionary
        args_dict = vars(args)

        # Filter out any key-value pairs where the value is None
        valid_args = {
            key: value for key, value in args_dict.items() if value is not None
        }

        # Save the arguments to a temporary file
        temp_file = Path(__file__).parent / "temp_args.txt"
        with open(temp_file, "w") as file:
            # Convert the valid_args dictionary to a string in the format "key1 value1 key2 value2 ..."
            arg_string = " ".join(
                [f"--{key} {value}" for key, value in valid_args.items()]
            )
            file.write(arg_string)

        os.system(f"python {restart_script}")
        sys.exit(0)

    def audio_callback(self, text):

        if self.summoned:
            client_id = 0
            self.cancel_gen = False
            client = self.session.get_client(client_id)
            client.generated_text = ""
            client.cancel_generation = False
            client.continuing = False
            client.first_chunk = True

            if not self.model:
                ASCIIColors.error("Model not selected. Please select a model")
                self.error(
                    "Model not selected. Please select a model", client_id=client_id
                )
                return

            if not self.busy:
                if client.discussion is None:
                    if self.db.does_last_discussion_have_messages():
                        client.discussion = self.db.create_discussion()
                    else:
                        client.discussion = self.db.load_last_discussion()

                prompt = text
                try:
                    nb_tokens = self.model.count_tokens(prompt)
                except:
                    nb_tokens = None
                message = client.discussion.add_message(
                    message_type=MSG_TYPE.MSG_TYPE_CONTENT.value,
                    sender_type=SENDER_TYPES.SENDER_TYPES_USER.value,
                    sender=(
                        self.config.user_name.strip()
                        if self.config.use_user_name_in_discussions
                        else self.config.user_name
                    ),
                    content=prompt,
                    metadata=None,
                    parent_message_id=self.message_id,
                    nb_tokens=nb_tokens,
                )

                ASCIIColors.green(
                    "Starting message generation by " + self.personality.name
                )
                client.generation_thread = threading.Thread(
                    target=self.start_message_generation,
                    args=(message, message.id, client_id),
                )
                client.generation_thread.start()

                self.sio.sleep(0.01)
                self.busy = True
                # tpe = threading.Thread(target=self.start_message_generation, args=(message, message_id, client_id))
                # tpe.start()
            else:
                self.error("I am busy. Come back later.", client_id=client_id)
        else:
            if "lollms" in text.lower():
                self.summoned = True

    # def scrape_and_save(self, url, file_path):
    #     # Send a GET request to the URL
    #     response = requests.get(url)

    #     # Parse the HTML content using BeautifulSoup
    #     soup = BeautifulSoup(response.content, 'html.parser')

    #     # Find all the text content in the webpage
    #     text_content = soup.get_text()

    #     # Remove extra returns and spaces
    #     text_content = ' '.join(text_content.split())

    #     # Save the text content as a text file
    #     with open(file_path, 'w', encoding="utf-8") as file:
    #         file.write(text_content)

    #     self.info(f"Webpage content saved to {file_path}")


    # ================================== LOLLMSApp


    def download_file(self, url, installation_path, callback=None):
        """
        Downloads a file from a URL, reports the download progress using a callback function, and displays a progress bar.

        Args:
            url (str): The URL of the file to download.
            installation_path (str): The path where the file should be saved.
            callback (function, optional): A callback function to be called during the download
                with the progress percentage as an argument. Defaults to None.
        """
        try:
            response = requests.get(url, stream=True)

            # Get the file size from the response headers
            total_size = int(response.headers.get("content-length", 0))

            with open(installation_path, "wb") as file:
                downloaded_size = 0
                with tqdm(
                    total=total_size, unit="B", unit_scale=True, ncols=80
                ) as progress_bar:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            file.write(chunk)
                            downloaded_size += len(chunk)
                            if callback is not None:
                                callback(downloaded_size, total_size)
                            progress_bar.update(len(chunk))

            if callback is not None:
                callback(total_size, total_size)

            print("File downloaded successfully")
        except Exception as e:
            print("Couldn't download file:", str(e))

    def clean_string(self, input_string):
        # Remove extra spaces by replacing multiple spaces with a single space
        # cleaned_string = re.sub(r'\s+', ' ', input_string)

        # Remove extra line breaks by replacing multiple consecutive line breaks with a single line break
        cleaned_string = re.sub(r"\n\s*\n", "\n", input_string)
        # Create a string containing all punctuation characters
        punctuation_chars = string.punctuation
        # Define a regular expression pattern to match and remove non-alphanumeric characters
        # pattern = f'[^a-zA-Z0-9\s{re.escape(punctuation_chars)}]'  # This pattern matches any character that is not a letter, digit, space, or punctuation
        pattern = f"[^a-zA-Z0-9\u00C0-\u017F\s{re.escape(punctuation_chars)}]"
        # Use re.sub to replace the matched characters with an empty string
        cleaned_string = re.sub(pattern, "", cleaned_string)
        return cleaned_string


    def get_discussion_to(self, client_id, message_id=-1):
        messages = self.session.get_client(client_id).discussion.get_messages()
        full_message_list = []
        ump = f"{self.start_header_id_template}{self.config.user_name.strip()if self.config.use_user_name_in_discussions else self.personality.user_message_prefix}{self.end_header_id_template}"

        for message in messages:
            if message["id"] <= message_id or message_id == -1:
                if (
                    message["type"]
                    != MSG_OPERATION_TYPE.MSG_OPERATION_TYPE_SET_CONTENT_INVISIBLE_TO_USER
                ):
                    if message["sender"] == self.personality.name:
                        full_message_list.append(
                            self.config.discussion_prompt_separator
                            + self.personality.ai_message_prefix
                            + message["content"]
                        )
                    else:
                        full_message_list.append(ump + message["content"])

        link_text = "\n"  # self.personality.link_text

        if len(full_message_list) > self.config["nb_messages_to_remember"]:
            discussion_messages = (
                self.config.discussion_prompt_separator
                + self.personality.personality_conditioning
                + link_text.join(
                    full_message_list[-self.config["nb_messages_to_remember"] :]
                )
            )
        else:
            discussion_messages = (
                self.config.discussion_prompt_separator
                + self.personality.personality_conditioning
                + link_text.join(full_message_list)
            )

        return discussion_messages  # Removes the last return
