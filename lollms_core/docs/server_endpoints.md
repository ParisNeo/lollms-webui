# Lord Of Large Language Models Socket.io Endpoints Documentation

<img src="https://github.com/ParisNeo/lollms/blob/main/lollms/assets/logo.png?raw=true" alt="Logo" width="200" height="200">

The server provides several Socket.io endpoints that clients can use to interact with the server. The default URL for the server is `http://localhost:9601`, but it can be changed using the configuration file or launch parameters.

## Endpoints

### `connect`
- Event: `'connect'`
- Description: This event is triggered when a client connects to the server.
- Actions:
  - Adds the client to the list of connected clients with a unique session ID.
  - Prints a message indicating the client's session ID.

### `disconnect`
- Event: `'disconnect'`
- Description: This event is triggered when a client disconnects from the server.
- Actions:
  - Removes the client from the list of connected clients, if it exists.
  - Prints a message indicating the client's session ID.

#### `list_available_bindings`
- Event: `'list_available_bindings'`
- Description: This event is triggered when a client requests a list of available bindings.
- Parameters: None
- Actions:
  - Initializes an empty list `binding_infs` to store information about each binding.
  - Iterates over the files and directories in the `self.bindings_path` directory.
  - For each directory in `self.bindings_path`:
    - Reads the content of the `binding_card.yaml` file, which contains information about the binding card.
    - Reads the content of the `models.yaml` file, which contains information about the models associated with the binding.
    - Creates an entry dictionary that includes the binding's name, card information, and model information.
    - Appends the entry to the `binding_infs` list.
  - Emits a response event `'bindings_list'` to the client containing the list of available bindings and their information (`bindings`) as well as a `success` parameter that is `False` when not successful.

Events generated:
- `'bindings_list'`: Sent to the client as a response to the `'list_available_bindings'` request. It contains the list of available bindings along with their associated information (`binding_infs`).


#### `list_available_personalities`
- Event: `'list_available_personalities'`
- Description: This event is triggered when a client requests a list of available personalities.
- Parameters: None
- Actions:
  - Retrieves the path to the personalities folder from the server (`self.personalities_path`).
  - Initializes an empty dictionary to store the available personalities.
  - Iterates over each category folder within the language folder.
    - Checks if the current item is a directory.
    - Initializes an empty list to store the personalities within the category.
    - Iterates over each personality folder within the category folder.
      - Checks if the current item is a directory.
      - Tries to load personality information from the config file (`config.yaml`) within the personality folder.
        - Retrieves the name, description, author, and version from the config data.
      - Checks if the `scripts` folder exists within the personality folder to determine if the personality has scripts.
      - Checks for the existence of logo files named `logo.gif` or `logo.webp` or `logo.png` or `logo.jpg` or `logo.jpeg` or `logo.bmp` within the `assets` folder to determine if the personality has a logo.
      - Sets the `avatar` field of the personality info based on the available logo file.
      - Appends the personality info to the list of personalities within the category.
    - Adds the list of personalities to the dictionary of the current category within the language.
  - Sends a response to the client containing the dictionary of available personalities.

Events generated:
- `'personalities_list'`: Emits an event to the client with the list of available personalities, categorized by language and category. The event data includes the personality information such as name, description, author, version, presence of scripts, and avatar image file path.


#### `list_available_models`
- Event: `'list_available_models'`
- Description: This event is triggered when a client requests a list of available models.
- Parameters: None (except `self` which refers to the class instance)
- Actions:
  - Checks if a binding class is selected. If not, emits an event `'available_models_list'` with a failure response indicating that no binding is selected.
  - Retrieves the list of available models using the binding class.
  - Processes each model in the list to extract relevant information such as filename, server, image URL, license, owner, owner link, filesize, description, model type, etc.
  - Constructs a dictionary representation for each model with the extracted information.
  - Appends each model dictionary to the `models` list.
  - Emits an event `'available_models_list'` with a success response containing the list of available models to the client.

Events generated:
- `'available_models_list'`: This event is emitted as a response to the client requesting a list of available models. It contains the success status and a list of available models with their details, such as title, icon, license, owner, owner link, description, installation status, file path, filesize, and model type.



#### `list_available_personalities_categories`
- Event: `'list_available_personalities_categories'`
- Description: This event is triggered when a client requests a list of available personality categories based on a specified language.
- Parameters:
  - `data`: An empty dictionary:

- Actions:
  - Attempts to retrieve the available personality categories.
  - Emits an event `'available_personalities_categories_list'` to the client.
    - If successful, sends a response with a list of available personality categories in the `'available_personalities_categories'` field of the event data.
    - If an error occurs, sends a response with an error message in the `'error'` field of the event data.

Events:
- Event: `'available_personalities_categories_list'`
  - Description: This event is emitted in response to the `list_available_personalities_categories` event.
  - Data:
    - If successful:
      - `'success'` (boolean): Indicates whether the retrieval of available personality categories was successful.
      - `'available_personalities_categories'` (list): A list of available personality categories.
    - If an error occurs:
      - `'success'` (boolean): Indicates whether an error occurred during the retrieval of available personality categories.
      - `'error'` (string): The error message describing the encountered error.


#### `list_available_personalities_names`
- Event: `'list_available_personalities_names'`
- Description: This event is triggered when a client requests a list of available personality names based on the specified language and category.
- Parameters:
  - `language` (string): The language for which the available personality names are requested.
  - `category` (string): The category for which the available personality names are requested.
- Actions:
  - Extracts the `language` and `category` parameters from the request data.
  - Retrieves the list of available personalities by iterating over the directory specified by the `language` and `category` parameters.
  - Sends a response to the client containing the list of available personality names.
- Event Generated: `'list_available_personalities_names_list'`
  - Description: This event is emitted as a response to the `list_available_personalities_names` request, providing the list of available personality names.
  - Parameters:
    - `success` (bool): Indicates the success or failure of the request.
    - `list_available_personalities_names` (list): The list of available personality names.
    - `error` (string, optional): If the request fails, this parameter contains the error message.



#### `select_binding`
- Event: `'select_binding'`
- Description: This event is triggered when a client selects a binding.
- Parameters:
  - `data['binding_name']`: The name of the binding selected by the client.

Actions:
- Creates a deep copy of the `self.config` dictionary and assigns it to `self.cp_config` variable.
- Updates the `"binding_name"` value in `self.cp_config` with the selected binding name obtained from `data['binding_name']`.
- Attempts to build a binding instance using the `self.bindings_path` and `self.cp_config`.
- If successful, updates `self.binding` with the created binding instance and updates `self.config` with `self.cp_config`.
- Sends a response to the client indicating the success of the binding selection along with the selected binding name.
- If an exception occurs during the binding creation process, the exception is printed and a response is sent to the client indicating the failure of the binding selection along with the selected binding name and the error message.

Events generated:
- `'select_binding'`: This event is emitted to the client to provide a response regarding the binding selection. It contains the following data:
  - `'success'`: A boolean value indicating the success or failure of the binding selection.
  - `'binding_name'`: The name of the selected binding.
  - If the binding selection fails, it also includes:
    - `'error'`: An error message explaining the reason for the failure.


#### `select_model`
- Event: `'select_model'`
- Description: This event is triggered when a client requests to select a model.
- Parameters:
  - `data['model_name']` (string): The name of the model to select.
- Actions:
  - Extracts the model name from the request data.
  - Checks if a binding class is available (`self.binding`).
    - If no binding class is available, emits a `'select_model'` event with a failure response, indicating that a binding needs to be selected first.
    - Returns and exits the function.
  - Creates a deep copy of the configuration (`self.config`) and assigns it to `self.cp_config`.
  - Sets the `"model_name"` property of `self.cp_config` to the selected model name.
  - Tries to create an instance of the binding class (`self.binding`) with `self.cp_config`.
    - If successful, assigns the created binding instance to `self.model`.
    - Emits a `'select_model'` event with a success response, indicating that the model selection was successful.
    - Returns and exits the function.
  - If an exception occurs during model creation, prints the exception and emits a `'select_model'` event with a failure response, indicating that a binding needs to be selected first.

Events generated:
- `'select_model'` (success response):
  - Emits to the client a success response indicating that the model selection was successful.
  - Parameters:
    - `'success'` (boolean): `True` to indicate success.
    - `'model_name'` (string): The selected model name.
- `'select_model'` (failure response):
  - Emits to the client a failure response indicating that a binding needs to be selected first or an error occurred during model creation.
  - Parameters:
    - `'success'` (boolean): `False` to indicate failure.
    - `'model_name'` (string): The selected model name.
    - `'error'` (string): An error message providing additional details.


#### `add_personality`
- Event: `'add_personality'`
- Description: This event is triggered when a client requests to add a new personality.
- Parameters:
  - `data`: A dictionary containing the following key-value pairs:
    - `'path'`: The path to the personality file.
- Actions:
  - Extracts the personality path from the `data` dictionary.
  - Attempts to create a new `AIPersonality` instance with the provided path.
  - Appends the created personality to the `self.personalities` list.
  - Appends the personality path to the `self.config["personalities"]` list.
  - Saves the updated configuration using `self.config.save_config()`.
  - Sends a response to the client indicating the success of the personality addition along with the name and ID of the added personality.
- Events Generated:
  - `'personality_added'`: This event is emitted to the client to indicate the successful addition of the personality. The emitted data is a dictionary with the following key-value pairs:
    - `'success'`: `True` to indicate success.
    - `'name'`: The name of the added personality.
    - `'id'`: The ID of the added personality in the `self.personalities` list.
  - `'personality_add_failed'`: This event is emitted to the client if an exception occurs during the personality addition. The emitted data is a dictionary with the following key-value pairs:
    - `'success'`: `False` to indicate failure.
    - `'error'`: A string containing the error message explaining the cause of the failure.


#### `activate_personality`
- Event: `'activate_personality'`
- Description: This event is triggered when a client requests to activate a personality.
- Actions:
  - Extracts the personality ID from the request data.
  - Checks if the personality ID is valid (within the range of `self.personalities`).
  - Sets the `self.active_personality` to the selected personality.
  - Sends a response to the client indicating the success of the personality activation along with the name and ID of the activated personality.
  - Updates the default personality ID in `self.config["active_personality_id"]`.
  - Saves the updated configuration using `self.config.save_config()`.
- Event Generated:
  - `'activate_personality'`: Emits the event to the client with the following data:
    - `'success'`: Indicates whether the personality activation was successful (`True` or `False`).
    - `'name'`: The name of the activated personality.
    - `'id'`: The ID (index) of the activated personality in the `self.personalities` list.

#### `list_active_personalities`
- Event: `'list_active_personalities'`
- Description: This event is triggered when a client requests a list of active personalities.
- Parameters: None
- Actions:
  - Retrieves the names of all the active personalities from the `self.personalities` list.
  - Sends a response to the client containing the list of active personality names.
- Event Generated: `'active_personalities_list'`
- Event Data:
  - `'success'`: A boolean value indicating the success of the operation.
  - `'personalities'`: A list of strings representing the names of the active personalities.

Please note that the `'list_active_personalities'` event does not require any parameters when triggering the endpoint. It simply returns the list of active personalities to the client.

#### `activate_personality`
- Event: `'activate_personality'`
- Description: This event is triggered when a client requests to activate a personality.
- Parameters:
  - `data['id']` (integer): The ID of the personality to activate.
- Actions:
  - Extracts the personality ID from the request data.
  - Checks if the personality ID is valid by comparing it with the length of the `self.personalities` list.
  - If the personality ID is valid:
    - Sets the `self.active_personality` to the personality at the specified ID.
    - Sends a response to the client indicating the success of the personality activation, along with the name and ID of the activated personality.
    - Updates the `active_personality_id` in the `self.config` object with the activated personality's ID.
    - Saves the updated configuration.
  - If the personality ID is not valid:
    - Sends a response to the client indicating the failure of the personality activation, along with an error message.

Generated Events:
- `'activate_personality'`: This event is emitted to the client after successfully activating a personality.
  - Parameters:
    - `{'success': True, 'name': self.active_personality, 'id': len(self.personalities) - 1}`:
      - `'success'` (boolean): Indicates whether the personality activation was successful.
      - `'name'` (string): The name of the activated personality.
      - `'id'` (integer): The ID of the activated personality.
- `'personality_add_failed'`: This event is emitted to the client if the personality ID provided is not valid.
  - Parameters:
    - `{'success': False, 'error': 'Personality ID not valid'}`:
      - `'success'` (boolean): Indicates whether the personality activation failed.
      - `'error'` (string): The error message indicating the reason for the failure.


#### `generate_text`
- Event: `'generate_text'`
- Description: This event is triggered when a client requests text generation.
- Parameters:
  - `data`: A dictionary containing the following fields:
    - `prompt` (string): The text prompt for text generation.
    - `personality` (integer): The index of the selected personality for conditioning the text generation. If it is -1 then no personality is used and the text is assumed to be raw.
- Actions:
  - Retrieves the selected model and client ID from the server.
  - Extracts the prompt and selected personality index from the request data.
  - Initializes an empty answer list for text chunks.
  - Retrieves the full discussion blocks from the client's data.
  - Defines a callback function to handle generated text chunks.
  - Preprocesses the prompt based on the selected personality's configuration, if applicable.
  - Constructs the full discussion text by combining the personality's conditioning, prompt, and AI message prefix.
  - Prints the input prompt for debugging purposes.
  - If a personality processor is available and has a custom workflow, runs the processor's workflow with the prompt and full discussion text, providing the callback function for text chunk emission.
  - If no custom workflow is available, generates text using the selected model with the full discussion text, specifying the number of predictions.
  - Appends the generated text to the full discussion blocks.
  - Prints a success message for debugging purposes.
  - Emits the generated text to the client through the `'text_generated'` event.

Events generated:
- `'buzzy'`: when the server is buzzy and can't process the request, it sends this event and returns. This event have parameter `message` containing a string.
- `'text_chunk'`: Generated text chunks are emitted to the client through this event during the text generation process. The event has two parameters `chunk` and `type`.
- `'text_generated'`: Once the text generation process is complete, the final generated text is emitted to the client through this event. The event has one parameter `text` containing the full generated text.
- `'generation_canceled'`: Answer to `cancel_generation` endpoint call
