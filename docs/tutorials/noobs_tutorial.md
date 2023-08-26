# LOLLMS WebUI Tutorial

## Introduction
Welcome to the LOLLMS WebUI tutorial! In this tutorial, we will walk you through the steps to effectively use this powerful tool. LOLLMS WebUI is designed to provide access to a variety of language models (LLMs) and offers a range of functionalities to enhance your tasks.

## Installation
1. Ensure that you have Python 3.10 or a higher version, as well as Git, installed on your system. Confirm that the Python installation is in your system's path and can be accessed via the terminal. You can check your Python version by typing `python --version` in the terminal. If the version is lower than 3.10 or you encounter an error, please install a newer version.
2. If you are using Conda, you can create a Conda virtual environment, install the dependencies mentioned in the `requirements.txt` file, and run the application using `python app.py`. For regular Python installations, follow the next steps.

## Download and Launch the Tool
1. Visit the GitHub repository page at [github.com/ParisNeo/lollms-webui](https://github.com/ParisNeo/lollms-webui).
2. Click on the "Latest Release" button.
3. Depending on your platform, download either `webui.bat` for Windows or `webui.sh` for Linux.
4. Choose a folder on your system to install the application launcher. For example, you can create a folder named `lollms-webui` in your `ai` directory.
5. Run the downloaded script (application launcher). Note: Some antivirus programs or Windows Defender might display a warning due to the tool's reputation. This warning is a false positive caused by the tool being relatively new. You can ignore the warning and proceed with the installation.
6. The installer will no longer prompt you to install the default model. This step will be performed in the UI, making it easier for you.

## Exploring the User Interface
1. The UI provides both light mode and dark mode themes for your preference.
2. You can access the GitHub repository directly from the UI.
3. On the left side, you will find the discussions panel, and the center side displays the messages flow.

## Model Selection and Installation
1. To select and install a model for a specific binding, navigate to the "Settings" section.
2. Open the "Models Zoo" tab.
3. Choose a binding from the provided list. For example, select "llama-cpp-official".
4. The first time you select a binding, you need to wait as it gets installed. You can check the installation progress in the console.
5. After the installation is complete, click "Install" next to a model you want to use and wait for the installation process to finish.
6. Note that clicking "Apply Changes" does not save the configuration. To save the changes, click the "Save" button and confirm.

## Starting a Discussion
1. Return to the discussions view.
2. Click the "+" button to create a new discussion.
3. You will see a predefined welcome message based on the selected personality configuration. By default, the LoLLMs personality is used, which aims to be helpful.
4. Enter your query or prompt. For example, you can ask, "Who is Abraham Lincoln?"
5. You can stop the generation at any time by clicking the "Stop Generating" button.

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
