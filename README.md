# LoLLMs (Lord of Large Language Multimodal Systems) Web UI
<div align="center">
  <img src="https://github.com/ParisNeo/lollms/blob/main/lollms/assets/logo.png" alt="Logo" width="200" height="200">
</div>

![GitHub license](https://img.shields.io/github/license/ParisNeo/lollms-webui)
![GitHub issues](https://img.shields.io/github/issues/ParisNeo/lollms-webui)
![GitHub stars](https://img.shields.io/github/stars/ParisNeo/lollms-webui)
![GitHub forks](https://img.shields.io/github/forks/ParisNeo/lollms-webui)
[![Discord](https://img.shields.io/discord/1092918764925882418?color=7289da&label=Discord&logo=discord&logoColor=ffffff)](https://discord.gg/4rR282WJb6)
[![Follow me on X](https://img.shields.io/twitter/follow/SpaceNerduino?style=social)](https://twitter.com/ParisNeo_AI)
[![Follow Me on YouTube](https://img.shields.io/badge/Follow%20Me%20on-YouTube-red?style=flat&logo=youtube)](https://www.youtube.com/user/Parisneo)

## LoLLMs core library download statistics
[![Downloads](https://static.pepy.tech/badge/lollms)](https://pepy.tech/project/lollms)
[![Downloads](https://static.pepy.tech/badge/lollms/month)](https://pepy.tech/project/lollms)
[![Downloads](https://static.pepy.tech/badge/lollms/week)](https://pepy.tech/project/lollms)

## LoLLMs webui download statistics
[![Downloads](https://img.shields.io/github/downloads/ParisNeo/lollms-webui/total?style=flat-square)](https://github.com/ParisNeo/lollms-webui/releases)
[![Downloads](https://img.shields.io/github/downloads/ParisNeo/lollms-webui/latest/total?style=flat-square)](https://github.com/ParisNeo/lollms-webui/releases)


Welcome to LoLLMS WebUI (Lord of Large Language Multimodal Systems: One tool to rule them all), the hub for LLM (Large Language Models) and multimodal intelligence systems. This project aims to provide a user-friendly interface to access and utilize various LLM and other AI models for a wide range of tasks. Whether you need help with writing, coding, organizing data, analyzing images, generating images, generating music or seeking answers to your questions, LoLLMS WebUI has got you covered.

As an all-encompassing tool with access to over 500 AI expert conditionning across diverse domains and more than 2500 fine tuned models over multiple domains, you now have an immediate resource for any problem. Whether your car needs repair or if you need coding assistance in Python, C++ or JavaScript; feeling down about life decisions that were made wrongly yet unable see how? Ask Lollms. Need guidance on what lies ahead healthwise based on current symptoms presented, our medical assistance AI can help you get a potential diagnosis and guide you to seek the right medical care. If stuck with legal matters such contract interpretation feel free reach out to Lawyer personality, to get some insight at hand -all without leaving comfort home. Not only does it aid students struggling through those lengthy lectors but provides them extra support during assessments too, so they are able grasp concepts properly rather then just reading along lines which could leave many confused afterward. Want some entertainment? Then engage Laughter Botand let yourself go enjoy hysterical laughs until tears roll from eyes while playing Dungeons&Dragonsor make up crazy stories together thanks to Creative Story Generator. Need illustration work done? No worries, Artbot got us covered there! And last but definitely not least LordOfMusic here for music generation according to individual specifications. So essentially say goodbye boring nights alone because everything possible can be achieved within one single platform called Lollms...

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
- Support for image/video generation based on stable diffusion
- Support for music generation based on musicgen
- Support for multi generation peer to peer network through Lollms Nodes and Petals.
- Support for Docker, conda, and manual virtual environment setups
- Support for LM Studio as a backend 

## Star History

<a href="https://star-history.com/#ParisNeo/lollms-webui&ParisNeo/lollms&ParisNeo/lollms_cpp_client&ParisNeo/lollms_bindings_zoo&ParisNeo/lollms_personalities_zoo&Date">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=ParisNeo/lollms-webui,ParisNeo/lollms,ParisNeo/lollms_cpp_client,ParisNeo/lollms_bindings_zoo,ParisNeo/lollms_personalities_zoo&type=Date&theme=dark" />
    <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=ParisNeo/lollms-webui,ParisNeo/lollms,ParisNeo/lollms_cpp_client,ParisNeo/lollms_bindings_zoo,ParisNeo/lollms_personalities_zoo&type=Date" />
    <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=ParisNeo/lollms-webui,ParisNeo/lollms,ParisNeo/lollms_cpp_client,ParisNeo/lollms_bindings_zoo,ParisNeo/lollms_personalities_zoo&type=Date" />
  </picture>
</a>

Thank you for all users who tested this tool and helped making it more user friendly.

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
- Run a terminal and create a new environment called `lollms` with python 3.11:
```bash
conda create --name lollms python=3.11
```
- Activate the environment
```bash
conda activate lollms
```
- If you want to use an nVidia GPU, install cuda toolkit 12.1
```bash
conda install -c "nvidia/label/cuda-12.1.1" cuda-toolkit
```
- Clone the project
```bash
git clone https://github.com/ParisNeo/lollms-webui.git
```
- enter the lollms-webui folder
```bash
cd lollms-webui
```
- download submodules (lollms_core, zoos and safe_store library)
```bash
git submodule init
git submodule update
cd zoos/bindings_zoo
git checkout main
cd ../personalities_zoo
git checkout main
cd ../extensions_zoo
git checkout main
cd ../models_zoo
git checkout main
cd ../../lollms_core
git checkout main
pip install -e .
cd ../utilities/safe_store
git checkout main
pip install -e .
cd ../..
```
- install dependencies
```bash
pip install --upgrade -r requirements.txt
```
- run the application
```bash
python app.py
```
### Manual install with virtual env:
Make sure you install python 3.11, and git:
[Install python](https://www.python.org/downloads/release/python-31103/)
Make sure to add it to your path so that you can run it easily from a terminal.
If you don't have git installed, please install it:
[Install git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
Make sure to add it to your path so that you can run it easily from a terminal.
- To use your GPU, you may need to install [nVidia cuda toolkit](https://developer.nvidia.com/cuda-toolkit)
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
- On linux: `source ./env/bin/activate`
- On macos: `./env/bin/activate`
- download submodules (lollms_core, zoos and safe_store library)
```bash
git submodule init
git submodule update
cd zoos/bindings_zoo
git checkout main
cd ../personalities_zoo
git checkout main
cd ../extensions_zoo
git checkout main
cd ../models_zoo
git checkout main
cd ../../lollms_core
git checkout main
pip install -e .
cd ../../utilities/safe_store
git checkout main
pip install -e .
cd ../..
```
- install dependencies
```bash
pip install --upgrade -r requirements.txt
```
- run the application
```bash
python app.py
```

Once installed, you need to activate the environment then run the app.

# Code of conduct

By using this tool, users agree to follow these guidelines :
- This tool is not meant to be used for building and spreading fakenews / misinformation.
- You are responsible for what you generate by using this tool. The creators will take no responsibility for anything created via this lollms.
- You can use lollms in your own project free of charge if you agree to respect the Apache 2.0 licenseterms. Please refer to https://www.apache.org/licenses/LICENSE-2.0 .
- You are not allowed to use lollms to harm others directly or indirectly. This tool is meant for peacefull purposes and should be used for good never for bad.
- Users must comply with local laws when accessing content provided by third parties like OpenAI API etc., including copyright restrictions where applicable.

# Disclaimer
Large Language Models are amazing tools that can be used for diverse purposes. Lollms was built to harness this power to help the user inhance its productivity. But you need to keep in mind that these models have their limitations and should not replace human intelligence or creativity, but rather augment it by providing suggestions based on patterns found within large amounts of data. It is up to each individual how they choose use them responsibly!

The performance of the system varies depending on the used model, its size and the dataset on whichit has been trained. The larger a language model's training set (the more examples), generally speaking - better results will follow when using such systems as opposed those with smaller ones. But there is still no garantee that the output generated from any given prompt would always be perfect and it may contain errors due various reasons. So please make sure you do not use it for serious matters like choosing medications or making financial decisions without consultating an expert first hand ! 

# license
This repository uses code under ApacheLicense Version 2.0 , see [license](https://github.com/ParisNeo/lollms-webui/blob/main/LICENSE) file for details about rights granted with respect to usage & distribution

# Copyright:
ParisNeo 2023


