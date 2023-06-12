# Flask Backend API Documentation

This documentation provides an overview of the endpoints available in the Flask backend API.

## Introduction

The Flask backend API exposes various endpoints to interact with the application. Each endpoint performs a specific function and supports different HTTP methods. The following sections describe each endpoint along with their parameters and expected outputs.

## Endpoints

### Endpoint: /disk_usage (GET)

**Description**: Retrieves the disk usage of the system.

**Parameters**: None

**Output**: Returns the disk usage information.

---

### Endpoint: /ram_usage (GET)

**Description**: Retrieves the ram usage of the system.

**Parameters**: None

**Output**: Returns the ram usage information.

---

### Endpoint: /list_bindings (GET)

**Description**: Lists the available bindings.

**Parameters**: None

**Output**: Returns a list of available bindings.

---

### Endpoint: /list_models (GET)

**Description**: Lists the available models.

**Parameters**: None

**Output**: Returns a list of available models.

---

### Endpoint: /list_personalities_languages (GET)

**Description**: Lists the languages supported by personalities.

**Parameters**: None

**Output**: Returns a list of languages supported by personalities.

---

### Endpoint: /list_personalities_categories (GET)

**Description**: Lists the categories of personalities.

**Parameters**: None

**Output**: Returns a list of personality categories.

---

### Endpoint: /list_personalities (GET)

**Description**: Lists the available personalities.

**Parameters**: None

**Output**: Returns a list of available personalities.

---

### Endpoint: /list_languages (GET)

**Description**: Lists the available languages.

**Parameters**: None

**Output**: Returns a list of available languages.

---

### Endpoint: /list_discussions (GET)

**Description**: Lists the discussions.

**Parameters**: None

**Output**: Returns a list of discussions.

---

### Endpoint: /set_personality (GET)

**Description**: Sets the active personality.

**Parameters**: None

**Output**: Sets the active personality.

---

### Endpoint: /delete_personality (GET)

**Description**: Deletes a personality.

**Parameters**: None

**Output**: Deletes the specified personality.

---

### Endpoint: / (GET)

**Description**: Returns the index page.

**Parameters**: None

**Output**: Returns the index page.

---

### Endpoint: /<path:filename> (GET)

**Description**: Serves static files.

**Parameters**: `filename` - The path to the static file.

**Output**: Returns the requested static file.

---

### Endpoint: /personalities/<path:filename> (GET)

**Description**: Serves personality files.

**Parameters**: `filename` - The path to the personality file.

**Output**: Returns the requested personality file.

---

### Endpoint: /outputs/<path:filename> (GET)

**Description**: Serves output files.

**Parameters**: `filename` - The path to the output file.

**Output**: Returns the requested output file.

---

### Endpoint: /export_discussion (GET)

**Description**: Exports a discussion.

**Parameters**: None

**Output**: Exports the specified discussion.

---

### Endpoint: /export (GET)

**Description**: Exports data.

**Parameters**: None

**Output**: Exports the specified data.

---

### Endpoint: /new_discussion (GET)

**Description**: Creates a new discussion.

**Parameters**: None

**Output**: Creates a new discussion.

---

### Endpoint: /stop_gen (GET)

**Description**: Stops the generation process.

**Parameters**: None

**Output**: Stops the generation process.

---

### Endpoint: /rename (POST)

**Description**: Renames a resource.

**Parameters**: None

**Output**: Renames the specified resource.

---

### Endpoint: /edit_title (POST)

**Description**: Edits the title of a resource.

**Parameters**: None

**Output**: Edits the title of the specified resource.

---

### Endpoint: /load_discussion (POST)

**Description**: Loads a discussion.

**Parameters**: None

**Output**: Loads the specified discussion.

---

### Endpoint: /delete_discussion (POST)

**Description**: Deletes a discussion.

**Parameters**: None

**Output**: Deletes the specified discussion.

---

### Endpoint: /update_message (GET)

**Description**: Updates a message.

**Parameters**: None

**Output**: Updates the specified message.

---

### Endpoint: /message_rank_up (GET)

**Description**: Increases the rank of a message.

**Parameters**: None

**Output**: Increases the rank of the specified message.

---

### Endpoint: /message_rank_down (GET)

**Description**: Decreases the rank of a message.

**Parameters**: None

**Output**: Decreases the rank of the specified message.

---

### Endpoint: /delete_message (GET)

**Description**: Deletes a message.

**Parameters**: None

**Output**: Deletes the specified message.

---

### Endpoint: /set_binding (POST)

**Description**: Sets a binding.

**Parameters**: None

**Output**: Sets the specified binding.

---

### Endpoint: /set_model (POST)

**Description**: Sets a model.

**Parameters**: None

**Output**: Sets the specified model.

---

### Endpoint: /update_model_params (POST)

**Description**: Updates model parameters.

**Parameters**: None

**Output**: Updates the specified model parameters.

---

### Endpoint: /get_config (GET)

**Description**: Retrieves the configuration.

**Parameters**: None

**Output**: Returns the configuration.

---

### Endpoint: /get_available_models (GET)

**Description**: Retrieves the available models.

**Parameters**: None

**Output**: Returns a list of available models.

---

### Endpoint: /extensions (GET)

**Description**: Retrieves the extensions.

**Parameters**: None

**Output**: Returns the extensions.

---

### Endpoint: /training (GET)

**Description**: Performs training.

**Parameters**: None

**Output**: Performs the training process.

---

### Endpoint: /main (GET)

**Description**: Returns the main page.

**Parameters**: None

**Output**: Returns the main page.

---

### Endpoint: /settings (GET)

**Description**: Returns the settings page.

**Parameters**: None

**Output**: Returns the settings page.

---

### Endpoint: /help (GET)

**Description**: Returns the help page.

**Parameters**: None

**Output**: Returns the help page.

---

### Endpoint: /get_generation_status (GET)

**Description**: Retrieves the generation status.

**Parameters**: None

**Output**: Returns the generation status.

---

### Endpoint: /update_setting (POST)

**Description**: Updates a setting.

**Parameters**: None

**Output**: Updates the specified setting.

---

### Endpoint: /apply_settings (POST)

**Description**: Applies the settings.

**Parameters**: None

**Output**: Applies the specified settings.

---

### Endpoint: /save_settings (POST)

**Description**: Saves the settings.

**Parameters**: None

**Output**: Saves the specified settings.

---

### Endpoint: /get_current_personality (GET)

**Description**: Retrieves the current personality.

**Parameters**: None

**Output**: Returns the current personality.

---

### Endpoint: /get_all_personalities (GET)

**Description**: Retrieves all personalities.

**Parameters**: None

**Output**: Returns a list of all personalities.

---

### Endpoint: /get_personality (GET)

**Description**: Retrieves a specific personality.

**Parameters**: None

**Output**: Returns the specified personality.

---

### Endpoint: /reset (GET)

**Description**: Resets the system.

**Parameters**: None

**Output**: Resets the system.

---

### Endpoint: /export_multiple_discussions (POST)

**Description**: Exports multiple discussions.

**Parameters**: None

**Output**: Exports the specified discussions.

---

### Endpoint: /import_multiple_discussions (POST)

**Description**: Imports multiple discussions.

**Parameters**: None

**Output**: Imports the specified discussions.



## Active personalities manipulation endpoints

### Mount Personality

**Endpoint:** `/mount_personality`

**Method:** POST

**Parameters:**
- `language` (file): The language file associated with the personality.
- `category` (file): The category file associated with the personality.
- `name` (file): The name file associated with the personality.

**Description:**
This endpoint mounts a personality by adding it to the list of configured personalities and setting it as the active personality. The personality is specified by providing the language, category, and name files. The endpoint checks if the personality's configuration file exists and, if not, adds the personality to the configuration. After mounting the personality, the settings are applied.

**Returns:**
- If the personality is mounted successfully:
  - `status` (boolean): `True`
- If the personality is not found:
  - `status` (boolean): `False`
  - `error` (string): "Personality not found"

### Unmount Personality

**Endpoint:** `/unmount_personality`

**Method:** POST

**Parameters:**
- `language` (file): The language file associated with the personality.
- `category` (file): The category file associated with the personality.
- `name` (file): The name file associated with the personality.

**Description:**
This endpoint unmounts a personality by removing it from the list of configured personalities. The personality is specified by providing the language, category, and name files. If the active personality is removed, the active personality ID is reset to `0`. After unmounting the personality, the settings are applied.

**Returns:**
- If the personality is unmounted successfully:
  - `status` (boolean): `True`
- If the personality couldn't be unmounted:
  - `status` (boolean): `False`
  - `error` (string): "Couldn't unmount personality"

### Select Personality

**Endpoint:** `/select_personality`

**Method:** POST

**Parameters:**
- `id` (file): The ID of the personality to select.

**Description:**
This endpoint selects a personality from the list of configured personalities based on the provided ID. The ID represents the index of the personality in the list. After selecting the personality, the settings are applied.

**Returns:**
- If the personality is selected successfully:
  - `status` (boolean): `True`
- If the ID is invalid:
  - `status` (boolean): `False`
  - `error` (string): "Invalid ID"