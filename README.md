# LoLLMS Web UI

![GitHub license](https://img.shields.io/github/license/ParisNeo/lollms-webui)
![GitHub issues](https://img.shields.io/github/issues/ParisNeo/lollms-webui)
![GitHub stars](https://img.shields.io/github/stars/ParisNeo/lollms-webui)
![GitHub forks](https://img.shields.io/github/forks/ParisNeo/lollms-webui)
[![Discord](https://img.shields.io/discord/1092918764925882418?color=7289da&label=Discord&logo=discord&logoColor=ffffff)](https://discord.gg/4rR282WJb6)
[![Follow me on Twitter](https://img.shields.io/twitter/follow/SpaceNerduino?style=social)](https://twitter.com/SpaceNerduino)
[![Follow Me on YouTube](https://img.shields.io/badge/Follow%20Me%20on-YouTube-red?style=flat&logo=youtube)](https://www.youtube.com/user/Parisneo)
[![pages-build-deployment](https://github.com/ParisNeo/lollms-webui/actions/workflows/pages/pages-build-deployment/badge.svg)](https://github.com/ParisNeo/lollms-webui/actions/workflows/pages/pages-build-deployment)


Welcome to LoLLMS WebUI (Lord of Large Language Models: One tool to rule them all), the hub for LLM (Large Language Model) models. This project aims to provide a user-friendly interface to access and utilize various LLM models for a wide range of tasks. Whether you need help with writing, coding, organizing data, generating images, or seeking answers to your questions, LoLLMS WebUI has got you covered.

[Click here for my youtube video on how to use the tool](https://youtu.be/ds_U0TDzbzI)
## Features

- Choose your preferred binding, model, and personality for your tasks
- Enhance your emails, essays, code debugging, thought organization, and more
- Explore a wide range of functionalities, such as searching, data organization, and image generation
- Easy-to-use UI with light and dark mode options
- Integration with GitHub repository for easy access
- Support for different personalities with predefined welcome messages
- Thumb up/down rating for generated answers
- Copy, edit, and remove messages
- Local database storage for your discussions
- Search, export, and delete multiple discussions
- Support for Docker, conda, and manual virtual environment setups

## Installation

### Prerequisites

Before installing LoLLMS WebUI, make sure you have the following dependencies installed:

- [Python 3.10 or higher](https://www.python.org/downloads/release/python-3100/)
- Pip - installation depends on OS, but make sure you have it installed.
- [Git (for cloning the repository)](https://git-scm.com/downloads)
- [Visual Studio Community](https://visualstudio.microsoft.com/vs/community/) with c++ build tools (for CUDA [nvidia GPU's]) - optional for windows
- Build essentials (for CUDA [nvidia GPU's]) - optional for linux
- [Nvidia CUDA toolkit 11.7 or higher](https://developer.nvidia.com/cuda-downloads) (for CUDA [nvidia GPU's]) - optional
- [Miniconda3](https://docs.conda.io/en/latest/miniconda.html) - optional (more stable than python)

Ensure that the Python installation is in your system's PATH, and you can call it from the terminal. To verify your Python version, run the following command:

Windows:
```bash
python --version
```

Linux:
```bash
python3 --version
```

If you receive an error or the version is lower than 3.10, please install a newer version and try again.

### Installation steps

For detailed installation steps please refer to these documents:

- [Windows 10/11](./docs/usage/AdvancedInstallInstructions.md#windows-10-and-11)
- [Linux (tested on ubuntu)](./docs/usage/AdvancedInstallInstructions.md#linux)
#### Easy install

- Download the appropriate application launcher based on your platform:
    For Windows: `webui.bat`
    For Linux: `webui.sh`
    For Linux: `c_webui.sh` - using miniconda3
- Place the downloaded launcher in a folder of your choice, for example:
    Windows: `C:\ai\LoLLMS-webui`
    Linux: `/home/user/ai/LoLLMS-webui`
- Run the launcher script. Note that you might encounter warnings from antivirus or Windows Defender due to the tool's newness and limited usage. These warnings are false positives caused by reputation conditions in some antivirus software. You can safely proceed with running the script.
Once the installation is complete, the LoLLMS WebUI will launch automatically.

#### Using Conda
If you use conda, you can create a virtual environment and install the required packages using the provided `requirements.txt` file. Here's an example of how to set it up:
First clone the project or download the zip file and unzip it:

```bash
git clone https://github.com/ParisNeo/lollms-webui.git
cd lollms-webui
```
Now create a new conda environment, activate it and install requirements

```bash
conda create --prefix ./env python=3.10
conda activate ./env
pip install -r requirements.txt
```
#### Using Docker
Alternatively, you can use Docker to set up the LoLLMS WebUI. Please refer to the Docker documentation for installation instructions specific to your operating system.

## Usage

You can launch the app from the webui.sh or webui.bat launcher. It will automatically perform updates if any are present. If you don't prefer this method, you can also activate the virtual environment and launch the application using python app.py from the root of the project.
Once the app is running, you can go to the application front link displayed in the console (by default localhost:9600 but can change if you change configuration) 
### Selecting a Model and Binding
- Open the LoLLMS WebUI and navigate to the Settings page.
- In the Models Zoo tab, select a binding from the list (e.g., llama-cpp-official).
- Wait for the installation process to finish. You can monitor the progress in the console.
- Once the installation is complete, click the Install button next to the desired model.
- After the model installation finishes, select the model and press Apply changes.
- Remember to press the Save button to save the configuration.

### Starting a Discussion
- Go to the Discussions view.
- Click the + button to create a new discussion.
- You will see a predefined welcome message based on the selected personality (by default, LoLLMS).
- Ask a question or provide an initial prompt to start the discussion.
- You can stop the generation process at any time by pressing the Stop Generating button.

### Managing Discussions
- To edit a discussion title, simply type a new title or modify the existing one.
- To delete a discussion, click the Delete button.
- To search for specific discussions, use the search button and enter relevant keywords.
- To perform batch operations (exporting or deleting multiple discussions), enable Check Mode, select the discussions, and choose the desired action.

# Contributing
Contributions to LoLLMS WebUI are welcome! If you encounter any issues, have ideas for improvements, or want to contribute code, please open an issue or submit a pull request on the GitHub repository.

# License
This project is licensed under the Apache 2.0 License. You are free to use this software commercially, build upon it, and integrate it into your own projects. See the [LICENSE](https://github.com/ParisNeo/lollms-webui/blob/main/LICENSE) file for details.

# Acknowledgements
Please note that LoLLMS WebUI is not affiliated with the LoLLMS application developed by Nomic AI. The latter is a separate professional application available at LoLLMS.io, which has its own unique features and community.

We express our gratitude to all the contributors who have made this project possible and welcome additional contributions to further enhance the tool for the benefit of all users.

# Contact

For any questions or inquiries, feel free to reach out via our discord server: https://discord.gg/4rR282WJb6

Thank you for your interest and support!

If you find this tool useful, don't forget to give it a star on GitHub, share your experience, and help us spread the word. Your feedback and bug reports are valuable to us as we continue developing and improving LoLLMS WebUI.

If you enjoyed this tutorial, consider subscribing to our YouTube channel for more updates, tutorials, and exciting content.

Happy exploring with LoLLMS WebUI!
