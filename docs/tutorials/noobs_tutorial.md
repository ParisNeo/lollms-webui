# LOLLMS WebUI Tutorial

## Introduction
Welcome to the LOLLMS WebUI tutorial! In this tutorial, we will walk you through the steps to effectively use this powerful tool. LOLLMS WebUI is designed to provide access to a variety of language models (LLMs) and offers a range of functionalities to enhance your tasks.

## Installation
1. Ensure that you have Python 3.10 or a higher version, as well as Git, installed on your system. Confirm that the Python installation is in your system's path and can be accessed via the terminal. You can check your Python version by typing `python --version` in the terminal. If the version is lower than 3.10 or you encounter an error, please install a newer version.
2. If you are using Conda, you can create a Conda virtual environment, install the dependencies mentioned in the `requirements.txt` file, and run the application using `python app.py`. For regular Python installations, follow the next steps.

## Download and Launch the Tool
1. Visit the GitHub repository page at [github.com/ParisNeo/lollms-webui](https://github.com/ParisNeo/lollms-webui).
2. Click on the "Latest Release" button.
3. Depending on your platform, download either `win_install.bat` for Windows or `linux_install.sh` for Linux or `macos_install.sh` for MacOS.
4. Choose a folder on your system to install the application launcher. For example, you can create a folder named `lollms-webui` in your `ai` directory.
5. Run the downloaded script. Note: Some antivirus programs or Windows Defender might display a warning due to the tool's reputation. This warning is a false positive caused by the tool being relatively new. You can ignore the warning and proceed with the installation.
6. The installer will prompt you to choose either to install using CPU or one of the GPU options.
7. The installer will no longer prompt you to install the default model. This step will be performed in the UI, making it easier for you.

## Exploring the User Interface
1. The UI provides both light mode and dark mode themes for your preference.
2. On the top, under the application logo and slogan, you can find the tabs. Each tab allows you to access a specific functionality.
3. You can access the GitHub repository directly from the UI.
4. You can also access all ParisNeo socials to find videos and tutorials on LoLLMs use on the top right of the page.
5. On the left side, you will find the discussions panel, and the center side displays the messages flow.

## Main settings
LoLLMs main configuration section offers many options to control the discussion behavior.

### Main Configuration Page - General
The general section of the main configuration page offers several settings to control the LoLLMs server and client behavior. Notice that the database is stored on the client side.

#### Host
- Description: The host address of the LoLLMs server.
- Type: Text
- Required: Yes
- Default Value: None
- Example: `localhost`

#### Port
- Description: The port number to connect to the LoLLMs server.
- Type: Number
- Required: Yes
- Default Value: None
- Example: `8080`

#### Database Path
- Description: The path to the database file on the client side.
- Type: Text
- Required: Yes
- Default Value: None
- Example: `/path/to/database.db`

#### Auto Show Browser
- Description: Automatically show the browser when the LoLLMs server is started.
- Type: Checkbox
- Required: Yes
- Default Value: None
- Example: Checked or Unchecked

#### Enable GPU
- Description: Enable the use of GPU for processing.
- Type: Checkbox
- Required: Yes
- Default Value: None
- Example: Checked or Unchecked
- Note: If GPU is enabled, the "Upgrade from CPU to GPU" button will be displayed.

#### Auto Save
- Description: Automatically save changes made in the LoLLMs application.
- Type: Checkbox
- Required: Yes
- Default Value: None
- Example: Checked or Unchecked

#### Auto Update
- Description: Automatically update the LoLLMs application.
- Type: Checkbox
- Required: Yes
- Default Value: None
- Example: Checked or Unchecked

### User Configuration Page
The user section of the main configuration page allows you to customize your user information and preferences.

#### User Name
- Description: Your user name.
- Type: Text
- Required: Yes
- Default Value: None
- Example: "JohnDoe"

#### User Description
- Description: A description or biography about yourself.
- Type: Text
- Required: Yes
- Default Value: None
- Example: "I am a research engineer with a passion for artificial intelligence."

#### Use User Description in Discussion
- Description: Whether to use your user description in discussions.
- Type: Checkbox
- Required: Yes
- Default Value: None
- Example: Checked or Unchecked

#### User Avatar
- Description: Your user avatar or profile picture.
- Type: File
- Required: No
- Default Value: None
- Example: [Upload Avatar]

#### Use User Name in Discussions
- Description: Whether to use your user name in discussions.
- Type: Checkbox
- Required: Yes
- Default Value: None
- Example: Checked or Unchecked

### Main Configuration Page - Data Vectorization
The data vectorization section is used to configure various settings related to data vectorization. Here is a breakdown of the available options:

1. **Activate files support**: This option allows you to enable or disable support for files in the data vectorization process. When enabled, the system will include files in the vectorization process.

2. **Activate discussion vectorization**: This option enables or disables the vectorization of discussions. When enabled, discussions will be included in the vectorization process.

3. **Show vectorized data**: This option determines whether the vectorized data will be displayed or not.

4. **Activate data Vectorization**: This option enables or disables data vectorization. When enabled, data vectorization will be performed.

5. **Build keywords when querying the vectorized database**: This option determines whether keywords should be built when querying the vectorized database.

6. **Data vectorization method**: This option allows you to select the data vectorization method. The available options are `tfidf Vectorizer` and `Model Embedding`.

7. **Data visualization method**: This option allows you to select the data visualization method. The available options are `PCA` and `TSNE`.

8. **Save the new files to the database**: This option determines whether the new files should be saved to the database. 

9. **Data vectorization chunk size(tokens)**: This option allows you to set the size of each chunk used for data vectorization.

10. **Data vectorization overlap size(tokens)**: This option allows you to set the overlap size between each chunk used for data vectorization.

11. **Number of chunks to use for each message**: This option allows you to specify the number of chunks to use for each message.

### Main Configuration Page - Audio
The audio section is used to configure various settings related to audio. Here is a breakdown of the available options:

1. **Send audio input automatically**: This option allows you to enable or disable automatic sending of audio input. When enabled, the system will automatically send audio input.
2. **Enable auto speak**: This option enables or disables the auto speak feature. When enabled, the system will automatically speak the responses.
3. **Audio pitch**: This option allows you to set the pitch of the audio.
4. **Audio in silence timer (ms)**: This option allows you to set the duration of silence in milliseconds before the audio input is considered complete.
5. **Input Audio Language**: This option allows you to choose the language for the input audio.
6. **Output Audio Voice**: This option allows you to choose the voice for the output audio.


## Binding Selection and Installation
1. To select and install a binding, navigate to the "Settings" tab.
2. Open the "Bindings Zoo" section.
3. Choose a binding from the provided list. For example, select "gpt4all".
4. If the binding was not already installed, please press install button and wait. You can check the installation progress in the console.
5. After the installation is complete, you can select the model by pressing the model card.

## Model Selection and Installation
1. To select and install a model for a specific binding, navigate to the "Settings" tab.
2. Open the "Models Zoo" tab.
3. You should find multiple models, if the one you are seeking does not exist, make sure you download it first by pressing the menue in the model card and selecting Download. You will be prompted to select a version of the model (in general it is just a quantization level for GGML/GGUF models and a single model.safetensor option for the others).
4. Once installed, you can select the model by checking the selection checkbox.
5. Depending on your main configuration settings, clicking "Apply Changes" may not save the configuration automatically. Make sure you check the autosave option in the main configurations sub section if you don't want to press save for each step. Since v 6.5, this is enabled by default.
6. If the auto save is not selected, to save the changes, click the "Save" button and confirm.

## Personality Selection and Installation
1. To select and mount a personality, navigate to the "Settings" tab.
2. Open the "Personalities Zoo" tab.
3. Either search for a personality by typing in the search text box, or just select a category.
4. To mount a personality, in the personality card, you can find a menu button. Click it and press mount.
5. If the personality needs installation, first press install, then, once installed, you can press mount.
6. You can mount any number of personalities to be used in your discussions


## Starting a Discussion
1. Return to the discussions view.
2. Click the "+" button to create a new discussion.
3. You will see a predefined welcome message based on the selected personality configuration. By default, the LoLLMs personality is used, which aims to be helpful.
4. Enter your query or prompt. For example, you can ask, "Who is Abraham Lincoln?"
5. You can stop the generation at any time by clicking the "Stop Generating" button.
6. You can view the current model and the current personality in the chatbox on the left
7. You can switch model by hovering on top of current model which causes the apearance of the other models as icons, then you can select the model you want
8. You can switch personality by hivering on top of the current personality which causes the apearance of the other mounted personalities as icons, then you can select the personality you want.
9. In a discussion, you can use multiple personas.
10. There is always a lead persona for the current discussion which is the one that shows its welcome message. So if you want a new discussion with a different persona, just select it and then press + to start a new discussion.


## Interacting with the Model
1. Once the generation is complete, you will see the generated response from the model.
2. You can fact-check the information provided by referring to reliable sources like Wikipedia, as models may sometimes generate inaccurate or fictional content.
3. You can give a thumbs-up or thumbs-down to the answer, edit the message, copy it to the clipboard, or remove it.
4. Note: The feature to have the message read by the AI will be added in the release version, using a locally stored library instead of a remote text-to-speech synthesizer.

## Managing Discussions
1. The discussions sidebar allows you to create, edit, and delete discussions.
2. When creating a new discussion, its initial name is "New Discussion." Once you enter your first message, the discussion title will be updated accordingly. You can edit the title or delete the discussion as needed.
3. All your discussions are stored in a local SQLite3 database located at `databases/database.db`. You can modify the database path in the `configs/local_config.yaml` file.
4. To facilitate finding specific discussions, a search button is provided. You can search for discussions using keywords.
5. When in check mode, you can select multiple discussions for exporting or deletion. Exporting messages can be useful for training purposes or contributing to data lakes.
6. Note: In the release version, it will be possible to change the database path directly from the UI.

## Conclusion
Congratulations! You have learned how to install and use LOLLMS WebUI effectively. Experiment with different bindings, models, and personalities to find the best fit for your needs. Remember to report any bugs or issues you encounter, as this project is developed by volunteers in their free time. Please support the project by liking, subscribing, and sharing this video to help it reach more people.

See you in the next tutorial!
