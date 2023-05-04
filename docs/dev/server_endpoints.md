# Server endpoints documentation

## Introduction:
This Flask server provides various endpoints to manage and interact with the chatbot. Here's a brief explanation of the endpoints available:

##  Endpoints:

"/list_backends": GET request endpoint to list all the available backends.
"/list_models": GET request endpoint to list all the available models.
"/list_personalities_languages": GET request endpoint to list all the available personality languages.
"/list_personalities_categories": GET request endpoint to list all the available personality categories.
"/list_personalities": GET request endpoint to list all the available personalities.
"/list_languages": GET request endpoint to list all the available languages.
"/list_discussions": GET request endpoint to list all the available discussions.
"/set_personality_language": GET request endpoint to set the personality language.
"/set_personality_category": GET request endpoint to set the personality category.
"/": GET request endpoint to display the index page.
"/path:filename": GET request endpoint to serve static files.
"/export_discussion": GET request endpoint to export the current discussion.
"/export": GET request endpoint to export the chatbot's data.
"/new_discussion": GET request endpoint to create a new discussion.
"/stop_gen": GET request endpoint to stop the chatbot from generating responses.
"/rename": POST request endpoint to rename a discussion.
"/edit_title": POST request endpoint to edit the title of a discussion.
"/load_discussion": POST request endpoint to load a discussion.
"/delete_discussion": POST request endpoint to delete a discussion.
"/update_message": GET request endpoint to update a message.
"/message_rank_up": GET request endpoint to rank up a message.
"/message_rank_down": GET request endpoint to rank down a message.
"/delete_message": GET request endpoint to delete a message.
"/set_backend": POST request endpoint to set the backend.
"/set_model": POST request endpoint to set the model.
"/update_model_params": POST request endpoint to update the model parameters.
"/get_config": GET request endpoint to get the chatbot's configuration.
"/extensions": GET request endpoint to list all the available extensions.
"/training": GET request endpoint to start the training process.
"/main": GET request endpoint to start the chatbot.
"/settings": GET request endpoint to display the settings page.
"/help": GET request endpoint to display the help page.

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
- `backend`: A string representing the backend to use for generating responses.

The save_settings function is used to save the updated settings to a configuratio


## How to use:

Call from client side.