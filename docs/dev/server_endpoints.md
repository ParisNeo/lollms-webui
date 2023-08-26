# Server endpoints documentation

## Introduction:
This Flask server provides various endpoints to manage and interact with the chatbot. Here's a brief explanation of the endpoints available:

##  Endpoints:

- "/list_bindings": GET request endpoint to list all the available bindings.
```
[
  "llama_cpp"
]
```

- "/list_models": GET request endpoint to list all the available models.
```
[
  "ggml-alpaca-7b-q4.bin",
  "ggml-vicuna-13b-1.1-q4_0.bin",
  "ggml-vicuna-13b-1.1-q4_1.bin",
  "ggml-vicuna-13b-4bit-rev1.bin",
  "ggml-vicuna-7b-4bit-rev1.bin",
  "ggml-vicuna-7b-4bit.bin",
  "lollms-lora-quantized-ggml.bin",
  "lollms-lora-quantized.bin",
  "lollms-lora-unfiltered-quantized.bin"
]
```
- "/list_personalities_languages": GET request endpoint to list all the available personality languages.
```
[
  "english",
  "french"
]
```

- "/list_personalities_categories": GET request endpoint to list all the available personality categories.
```
[
  "art",
  "creativity",
  "funny_learning",
  "general",
  "tools"
]
```

- "/list_personalities": GET request endpoint to list all the available personalities.
```
[
  "Computing advisor"
]
```

- "/list_languages": GET request endpoint to list all the available languages.
```
[
  {
    "label": "English",
    "value": "en-US"
  },
  {
    "label": "Fran\u00e7ais",
    "value": "fr-FR"
  },
  {
    "label": "\u0627\u0644\u0639\u0631\u0628\u064a\u0629",
    "value": "ar-AR"
  },
  {
    "label": "Italiano",
    "value": "it-IT"
  },
  {
    "label": "Deutsch",
    "value": "de-DE"
  },
  {
    "label": "Dutch",
    "value": "nl-XX"
  },
  {
    "label": "\u4e2d\u570b\u4eba",
    "value": "zh-CN"
  }
]
```

- "/list_discussions": GET request endpoint to list all the available discussions.
```
[
  {
    "id": 9,
    "title": "is dog a god?"
  },
  {
    "id": 10,
    "title": "untitled"
  }
]
```

- "/set_personality_language": GET request endpoint to set the personality language.
- "/set_personality_category": GET request endpoint to set the personality category.
- "/": GET request endpoint to display the index page.
- "/path:filename": GET request endpoint to serve static files.
- "/export_discussion": GET request endpoint to export the current discussion.
- "/export": GET request endpoint to export the chatbot's data.
- "/new_discussion": GET request endpoint to create a new discussion.
- "/stop_gen": GET request endpoint to stop the chatbot from generating responses.
```
{
  "status": True
}
```

- "/rename": POST request endpoint to rename a discussion.
- "/edit_title": POST request endpoint to edit the title of a discussion.
- "/load_discussion": POST request endpoint to load a discussion.
```
[
  {
    "content": "##Instructions:\\nLoLLMs is a smart and helpful Assistant built by Nomic-AI. It can discuss with humans and assist them.\n",
    "id": 23,
    "parent": 0,
    "rank": 0,
    "sender": "conditionner",
    "type": 1
  },
  {
    "content": "Welcome! I am LoLLMs A free and open assistant. What can I do for you today?",
    "id": 24,
    "parent": 23,
    "rank": 0,
    "sender": "lollms",
    "type": 0
  },
  {
    "content": "is dog a god?",
    "id": 25,
    "parent": 24,
    "rank": 0,
    "sender": "user",
    "type": 0
  },
  {
    "content": "That depends on your definition of 'God'. In some religions, dogs are considered sacred and divine creatures. But in others, they may not be seen as gods or deities at all.",
    "id": 26,
    "parent": 25,
    "rank": 0,
    "sender": "lollms",
    "type": 0
  }
]
```

- "/delete_discussion": POST request endpoint to delete a discussion.
- "/update_message": GET request endpoint to update a message.
- "/message_rank_up": GET request endpoint to rank up a message.
- "/message_rank_down": GET request endpoint to rank down a message.
- "/delete_message": GET request endpoint to delete a message.
- "/set_binding": POST request endpoint to set the binding.
- "/set_model": POST request endpoint to set the model.
- "/update_model_params": POST request endpoint to update the model parameters.
- "/get_config": GET request endpoint to get the chatbot's configuration.
```
{
  "auto_read": false,
  "binding": "llama_cpp",
  "config": "local_config.yaml",
  "ctx_size": 2048,
  "db_path": "databases/database.db",
  "debug": false,
  "host": "localhost",
  "language": "en-US",
  "model": "lollms-lora-quantized-ggml.bin",
  "n_predict": 1024,
  "n_threads": 8,
  "nb_messages_to_remember": 5,
  "override_personality_model_parameters": false,
  "personality": "Computing advisor",
  "personality_category": "Helpers",
  "port": 9600,
  "repeat_last_n": 40,
  "repeat_penalty": 1.2,
  "seed": 0,
  "temperature": 0.9,
  "top_k": 50,
  "top_p": 0.95,
  "use_avx2": true,
  "use_gpu": false,
  "use_new_ui": true,
  "version": 3,
  "voice": ""
}
```

- "/get_current_personality": GET request endpoint to get all information about current personality
```
{
  "personality": {
    "ai_message_prefix": "###lollms:\n",
    "anti_prompts": [
      "###user",
      "### user",
      "###lollms",
      "### lollms"
    ],
    "assets_list": [
      "personalities\\english\\generic\\lollms\\assets\\logo.png"
    ],
    "author": "ParisNeo",
    "category": "General",
    "dependencies": [],
    "disclaimer": "",
    "language": "en_XX",
    "link_text": "\n",
    "model_n_predicts": 1024,
    "model_repeat_last_n": 40,
    "model_repeat_penalty": 1.0,
    "model_temperature": 0.6,
    "model_top_k": 50,
    "model_top_p": 0.9,
    "name": "lollms",
    "personality_conditioning": "## Information:\nAssistant's name is lollms\nToday's date is {{date}}\n## Instructions:\nYour mission is to assist user to perform various tasks and answer his questions\n",
    "personality_description": "This personality is a helpful and Kind AI ready to help you solve your problems \n",
    "user_message_prefix": "###user:\n",
    "user_name": "user",
    "version": "1.0.0",
    "welcome_message": "Welcome! My name is lollms.\nHow can I help you today?\n"
  }
}
```

- "/extensions": GET request endpoint to list all the available extensions.
- "/training": GET request endpoint to start the training process.
- "/main": GET request endpoint to start the chatbot.
- "/settings": GET request endpoint to display the settings page.
- "/help": GET request endpoint to display the help page.
- "/get_all_personalities": GET request endpoint to get all personalities array
- "/get_personality": GET request endpoint to get speciffic data based on request
- "/disk_usage": GET request endpoint to retrieve the available space in the current folder's drive.
    Method: GET
    Description: Retrieves the available space in bytes for the current folder's drive.
    Response:
    Content-Type: application/json
    Body: JSON object with a single entry 'available_space' containing the available space in bytes.
    Example Response:
    ```json
    {
        "total_space":1000000000000,
        "available_space":515358106014,
        "percent_usage":51.53,
        "binding_models_usage": 3900000000
    }
    ```
    Example Usage:
    Request: GET /disk_space
    Response: 200 OK

##  TODO Endpoints:

Here we list needed endpoints on th ebinding to make UI work as expected.


# Socketio endpoints
These are the WebSocket server endpoints that are used to handle real-time communication between the client and server using the SocketIO library.

The first decorator `@socketio.on('connect')` listens for a connection event and calls the `connect()` function when a client connects to the server. Similarly, the second decorator `@socketio.on('disconnect')` listens for a disconnection event and calls the `disconnect()` function when a client disconnects from the server.

The third decorator `@socketio.on('generate_msg')` is used to handle the event of generating a message. It takes the data sent by the client and adds a new message to the current discussion with the user as the sender and the message content as the prompt. It then starts a new thread to parse the prompt into a prompt stream.

The fourth decorator `@socketio.on('generate_msg_from')` is used to handle the event of generating a message from a specific message ID. It takes the data sent by the client which includes the message ID and message prompt and starts a new thread to parse the prompt into a prompt stream.

The fifth decorator `@socketio.on('update_setting')`, listens for updates to the chatbot's configuration settings. The listener takes in a JSON object that contains the name of the setting being updated (setting_name) and the new value for the setting (setting_value). The function then updates the corresponding value in the chatbot's configuration dictionary based on the setting_name. The updated setting is then sent to the client with a status flag indicating whether the update was successful.

The sixth decorator `@socketio.on('save_settings')`, listens for a request from the client to save the current chatbot settings to a file. When triggered, the save_settings function writes the current configuration dictionary to a file specified by self.config_file_path. Once the file has been written, the function sends a status flag indicating whether the save was successful to the client.

The available settings are:

- `temperature`: A floating-point value that determines the creativity of the chatbot's responses. Higher values will result in more diverse and unpredictable responses, while lower values will result in more conservative and predictable responses.
- `top_k`: An integer that determines the number of most likely tokens to consider at each step of generating a response. Smaller values will result in more conservative and predictable responses, while larger values will result in more diverse and unpredictable responses.
- `top_p`: A floating-point value between 0 and 1 that determines the probability mass threshold for including the next token in the generated response. Smaller values will result in more conservative and predictable responses, while larger values will result in more diverse and unpredictable responses.
- `n_predict`: An integer that determines the number of responses the chatbot generates for a given prompt.
- `n_threads`: An integer that determines the number of threads to use for generating responses.
- `ctx_size`: An integer that determines the maximum number of tokens to include in the context for generating responses.
- `repeat_penalty`: A floating-point value that determines the penalty for repeating the same token or sequence of tokens in a generated response. Higher values will result in the chatbot being less likely to repeat itself.
- `repeat_last_n`: An integer that determines the number of previous generated tokens to consider for the repeat_penalty calculation.
- `language`: A string representing the language for audio input.
- `personality_language`: A string representing the language to use for generating personality traits.
- `personality_category`: A string representing the category of personality traits to use for generating responses.
- `personality`: A string representing the name of a specific personality traits to use for generating responses.
- `model`: A string representing the model to use for generating responses.
- `binding`: A string representing the binding to use for generating responses.

The save_settings function is used to save the updated settings to a configuratio


## How to use:

Call from client side.