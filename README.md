# LoLLMS Web UI
<div align="center">
  <img src="https://github.com/ParisNeo/lollms/blob/main/lollms/assets/logo.png" alt="Logo" width="200" height="200">
</div>

![GitHub license](https://img.shields.io/github/license/ParisNeo/lollms-webui)
![GitHub issues](https://img.shields.io/github/issues/ParisNeo/lollms-webui)
![GitHub stars](https://img.shields.io/github/stars/ParisNeo/lollms-webui)
![GitHub forks](https://img.shields.io/github/forks/ParisNeo/lollms-webui)
[![Discord](https://img.shields.io/discord/1092918764925882418?color=7289da&label=Discord&logo=discord&logoColor=ffffff)](https://discord.gg/4rR282WJb6)
[![Follow me on Twitter](https://img.shields.io/twitter/follow/SpaceNerduino?style=social)](https://twitter.com/SpaceNerduino)
[![Follow Me on YouTube](https://img.shields.io/badge/Follow%20Me%20on-YouTube-red?style=flat&logo=youtube)](https://www.youtube.com/user/Parisneo)
[![pages-build-deployment](https://github.com/ParisNeo/lollms-webui/actions/workflows/pages/pages-build-deployment/badge.svg)](https://github.com/ParisNeo/lollms-webui/actions/workflows/pages/pages-build-deployment)

Welcome to LoLLMS WebUI (Lord of Large Language Models: One tool to rule them all), the hub for LLM (Large Language Model) models. This project aims to provide a user-friendly interface to access and utilize various LLM models for a wide range of tasks. Whether you need help with writing, coding, organizing data, generating images, generating music or seeking answers to your questions, LoLLMS WebUI has got you covered.

## Features

- Choose your preferred binding, model, and personality for your tasks
- Enhance your emails, essays, code debugging, thought organization, and more
- Explore a wide range of functionalities, such as searching, data organization, image generation, and music generation
- Easy-to-use UI with light and dark mode options
- Integration with GitHub repository for easy access
- Support for different personalities with predefined welcome messages
- Thumb up/down rating for generated answers
- Copy, edit, and remove messages
- Local database storage for your discussions
- Search, export, and delete multiple discussions
- Support for Docker, conda, and manual virtual environment setups


## Installation
### Automatic installation (UI)
If you are using Windows, just visit the release page, download the windows installer and install it.

### Automatic installation (Console)
Download the installation script from scripts folder and run it.
The installation scripts are:
- `win_install.bat` for Windows.
- `linux_install.sh`for Linux.
- `mac_install.sh`for Mac.

### Manual install with Anaconda/Miniconda:
If you don't have anaconda or miniconda installed, please install it:
[Install miniconda](https://docs.conda.io/projects/miniconda/en/latest/miniconda-install.html)
Make sure to add it to your path so that you can run it easily from a terminal.
If you don't have git installed, please install it:
[Install git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
Make sure to add it to your path so that you can run it easily from a terminal.
- Run a terminal and create a new environment called `lollms` with python 3.10:
```bash
conda create --name lollms python=3.10
```
- Activate the environment
```bash
conda activate lollms
```
- Clone the project
```bash
git clone https://github.com/ParisNeo/lollms-webui.git
```
- enter the lollms-webui folder
```bash
cd lollms-webui
```
- install dependancies
```bash
pip install --upgrade -r requirements.txt
```
- run the application
```bash
python app.py
```
### Manual install with virtual env:
Make sure you install python 3.10, and git:
[Install python](https://www.python.org/downloads/release/python-31013/)
Make sure to add it to your path so that you can run it easily from a terminal.
If you don't have git installed, please install it:
[Install git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
Make sure to add it to your path so that you can run it easily from a terminal.
- Run a terminal and install pip:
```bash
python -m ensurepip --upgrade
```
- Install virtual environment:
```bash
pip install venv
```
- Clone the project
```bash
git clone https://github.com/ParisNeo/lollms-webui.git
```
- enter the lollms-webui folder
```bash
cd lollms-webui
```
- Create a virtual environment
```bash
python -m venv ./env
```
- Activate the virtual environment:
- On windows: `./env/Scripts/activate`
- On linux: `./env/bin/activate`
- On macos: `./env/bin/activate`
- install dependancies
```bash
pip install --upgrade -r requirements.txt
```
- run the application
```bash
python app.py
```

Once installed, you need to activate the environment then run the app.
## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=ParisNeo/lollms,ParisNeo/lollms-webui,ParisNeo/lollms_cpp_client,ParisNeo/lollms_bindings_zoo,ParisNeo/lollms_personalities_zoo&type=Date)](https://star-history.com/#ParisNeo/lollms&ParisNeo/lollms-webui&ParisNeo/lollms_cpp_client&ParisNeo/lollms_bindings_zoo&ParisNeo/lollms_personalities_zoo&Date)
