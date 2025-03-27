# LoLLMs (Lord of Large Language Multimodal Systems) Web UI
<div align="center">
  <img src="https://github.com/ParisNeo/lollms-webui/blob/main/assets/logo.png" alt="Logo" width="200" height="200">
</div>

## Latest video
[Here is a tutorial on how to use function calls in lollms](https://youtu.be/0ft6PyOvSqI?si=3bFtOzQ-J2Y53JaY)

![GitHub license](https://img.shields.io/github/license/ParisNeo/lollms-webui)
![GitHub issues](https://img.shields.io/github/issues/ParisNeo/lollms-webui)
![GitHub stars](https://img.shields.io/github/stars/ParisNeo/lollms-webui)
![GitHub forks](https://img.shields.io/github/forks/ParisNeo/lollms-webui)
[![Discord](https://img.shields.io/discord/1092918764925882418?color=7289da&label=Discord&logo=discord&logoColor=ffffff)](https://discord.gg/4rR282WJb6)
[![Follow me on X](https://img.shields.io/twitter/follow/ParisNeo_AI?style=social)](https://twitter.com/ParisNeo_AI)
[![Follow Me on YouTube](https://img.shields.io/badge/Follow%20Me%20on-YouTube-red?style=flat&logo=youtube)](https://www.youtube.com/user/Parisneo)

## LoLLMs core library download statistics
[![Downloads](https://static.pepy.tech/badge/lollms)](https://pepy.tech/project/lollms)
[![Downloads](https://static.pepy.tech/badge/lollms/month)](https://pepy.tech/project/lollms)
[![Downloads](https://static.pepy.tech/badge/lollms/week)](https://pepy.tech/project/lollms)

## LoLLMs webui download statistics
[![Downloads](https://img.shields.io/github/downloads/ParisNeo/lollms-webui/total?style=flat-square)](https://github.com/ParisNeo/lollms-webui/releases)
[![Downloads](https://img.shields.io/github/downloads/ParisNeo/lollms-webui/latest/total?style=flat-square)](https://github.com/ParisNeo/lollms-webui/releases)


Welcome to LoLLMS WebUI (Lord of Large Language Multimodal Systems: One tool to rule them all), the hub for LLM (Large Language Models) and multimodal intelligence systems. This project aims to provide a user-friendly interface to access and utilize various LLM and other AI models for a wide range of tasks. Whether you need help with writing, coding, organizing data, analyzing images, generating images, generating music or seeking answers to your questions, LoLLMS WebUI has got you covered.

As an all-encompassing tool with access to over 500 AI expert conditioning across diverse domains and more than 2500 fine tuned models over multiple domains, you now have an immediate resource for any problem. Whether your car needs repair or if you need coding assistance in Python, C++ or JavaScript; feeling down about life decisions that were made wrongly yet unable to see how? Ask Lollms. Need guidance on what lies ahead healthwise based on current symptoms presented, our medical assistance AI can help you get a potential diagnosis and guide you to seek the right medical care. If stuck with legal matters such contract interpretation feel free to reach out to Lawyer personality, to get some insight at hand -all without leaving comfort home. Not only does it aid students struggling through those lengthy lectors but provides them extra support during assessments too, so they are able grasp concepts properly rather then just reading along lines which could leave many confused afterward. Want some entertainment? Then engage Laughter Botand let yourself go enjoy hysterical laughs until tears roll from eyes while playing Dungeons&Dragonsor make up crazy stories together thanks to Creative Story Generator. Need illustration work done? No worries, Artbot got us covered there! And last but definitely not least LordOfMusic is here for music generation according to individual specifications. So essentially say goodbye boring nights alone because everything possible can be achieved within one single platform called Lollms...

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
- Support for image generation based on stable diffusion/flux/comfyui/open ai dall-e/Midjourney/Novita ai services
- Support for video generation based lumalabs/cogvideo_x/runwayml/stable_diffusion/Novita ai services
- Support for music generation based on musicgen
- Support for multi generation peer to peer network through Lollms Nodes and Petals.
- Support for Docker, conda, and manual virtual environment setups
- Support for LLMs using multiple bindings:
  - Hugging face local models
  - GGUF/GGML local models
  - EXLLama v2 local models (EXT/AWQ/GPTQ)
  - Ollama service
  - vllm service
  - Openai service
  - Anthropic service
  - Open-router service
  - Novita-ai service
- Support for prompt Routing to various models depending on the complexity of the task

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

### Automatic installation (Console)
Download the installation script from scripts folder and run it.
The installation scripts are:
- `lollms_installer.bat` for Windows.
- `lollms_installer.sh`for Linux.
- `lollms_installer_macos.sh`for Mac.

### Manual install:
Since v 10.14, manual installation is back:

1. First ensure Python 3.11 is installed
You can check your Python version with:
```bash
python --version
```

If you need to install Python 3.11, download it from:
[https://www.python.org/downloads/release/python-3118/](https://www.python.org/downloads/release/python-3118/)

2. Clone the repository with submodules
```bash
git clone --recursive https://github.com/ParisNeo/lollms-webui.git
cd lollms-webui
git submodule update --init --recursive
```

3. Create and activate a virtual environment (recommended)
```bash
python -m venv venv
```
### On Windows:
```cmd
.\venv\Scripts\activate
```
### On Linux/Mac:
```bash
source venv/bin/activate
```
4. Install requirements
```bash
pip install -r requirements.txt
```

5. Create global_paths_cfg.yaml
```bash
cat > global_paths_cfg.yaml << EOL
lollms_path: $(pwd)/lollms_core/lollms
lollms_personal_path: $(pwd)/personal_data
EOL
```

6. Install desired bindings
You can set environment variables to select which bindings to install
For example, to install ollama binding:
```bash
python zoos/bindings_zoo/ollama/__init__.py
```

List of available bindings and their installation commands:
elf:           python zoos/bindings_zoo/elf/__init__.py
openrouter:    python zoos/bindings_zoo/openrouter/__init__.py
openai:        python zoos/bindings_zoo/openai/__init__.py
groq:          python zoos/bindings_zoo/groq/__init__.py
mistralai:     python zoos/bindings_zoo/mistralai/__init__.py
ollama:        python zoos/bindings_zoo/ollama/__init__.py
vllm:          python zoos/bindings_zoo/vllm/__init__.py
litellm:       python zoos/bindings_zoo/litellm/__init__.py
exllamav2:     python zoos/bindings_zoo/exllamav2/__init__.py
python_llama_cpp: python zoos/bindings_zoo/python_llama_cpp/__init__.py
huggingface:   python zoos/bindings_zoo/huggingface/__init__.py
remote_lollms: python zoos/bindings_zoo/remote_lollms/__init__.py
xAI:           python zoos/bindings_zoo/xAI/__init__.py
gemini:        python zoos/bindings_zoo/gemini/__init__.py
novita_ai:     python zoos/bindings_zoo/novita_ai/__init__.py
7. Run the server
```bash
python app.py
```


now you are ready to run lolmms: `python app.py` 
## Smart Routing: Optimizing for Money and Speed

Lollms' Smart Routing feature goes beyond just selecting the right model for accuracy. It empowers you to optimize your text generation process for two key factors: **money** and **speed**.

**Optimizing for Money:**

Imagine you're using multiple text generation services with varying price points. Some models might be exceptionally powerful but come with a hefty price tag, while others offer a more budget-friendly option with slightly less capability. Smart Routing lets you leverage this price difference to your advantage:

* **Cost-Effective Selection:** By defining a hierarchy of models based on their cost, Smart Routing can automatically choose the most economical model for your prompt. This ensures you're only paying for the power you need, minimizing unnecessary expenses.
* **Dynamic Price Adjustment:**  As your prompt complexity changes, Smart Routing can dynamically switch between models, ensuring you're always using the most cost-effective option for the task at hand.

**Optimizing for Speed:**

Speed is another critical factor in text generation, especially when dealing with large volumes of content or time-sensitive tasks. Smart Routing allows you to prioritize speed by:

* **Prioritizing Smaller Models:** By placing faster, less resource-intensive models higher in the hierarchy, Smart Routing can prioritize speed for simple prompts. This ensures quick responses and efficient processing.
* **Dynamic Speed Adjustment:**  For more complex prompts requiring the power of larger models, Smart Routing can seamlessly switch to those models while maintaining a balance between speed and accuracy.

**Example Use Cases:**

* **Content Marketing:**  Use Smart Routing to select the most cost-effective model for generating large volumes of blog posts or social media content.
* **Customer Support:**  Prioritize speed by using smaller models for quick responses to frequently asked questions, while leveraging more powerful models for complex inquiries.
* **Research and Development:**  Optimize for both money and speed by using a tiered model hierarchy, ensuring you can quickly generate initial drafts while using more powerful models for in-depth analysis.

**Conclusion:**

Smart Routing is a versatile tool that empowers you to optimize your text generation process for both cost and speed. By leveraging a hierarchy of models and dynamically adjusting your selection based on prompt complexity, you can achieve the perfect balance between efficiency, accuracy, and cost-effectiveness.


# Code of conduct

By using this tool, users agree to follow these guidelines :
- This tool is not meant to be used for building and spreading fakenews / misinformation.
- You are responsible for what you generate by using this tool. The creators will take no responsibility for anything created via this lollms.
- You can use lollms in your own project free of charge if you agree to respect the Apache 2.0 licenseterms. Please refer to https://www.apache.org/licenses/LICENSE-2.0 .
- You are not allowed to use lollms to harm others directly or indirectly. This tool is meant for peaceful purposes and should be used for good never for bad.
- Users must comply with local laws when accessing content provided by third parties like OpenAI API etc., including copyright restrictions where applicable.

# ⚠️ Security Warning

Please be aware that LoLLMs WebUI does not have built-in user authentication and is primarily designed for local use. Exposing the WebUI to external access without proper security measures could lead to potential vulnerabilities.

If you require remote access to LoLLMs, it is strongly recommended to follow these security guidelines:

1. **Activate Headless Mode**: Enabling headless mode will expose only the generation API while turning off other potentially vulnerable endpoints. This helps to minimize the attack surface.

2. **Set Up a Secure Tunnel**: Establish a secure tunnel between the localhost running LoLLMs and the remote PC that needs access. This ensures that the communication between the two devices is encrypted and protected.

3. **Modify Configuration Settings**: After setting up the secure tunnel, edit the `/configs/local_config.yaml` file and adjust the following settings:
   ```yaml
   host: 0.0.0.0  # Allow remote connections
   port: 9600  # Change the port number if desired (default is 9600)
   force_accept_remote_access: true  # Force accepting remote connections
   headless_server_mode: true  # Set to true for API-only access, or false if the WebUI is needed
   ```

By following these security practices, you can help protect your LoLLMs instance and its users from potential security risks when enabling remote access.

Remember, it is crucial to prioritize security and take necessary precautions to safeguard your system and sensitive information. If you have any further questions or concerns regarding the security of LoLLMs, please consult the documentation or reach out to the community for assistance.

Stay safe and enjoy using LoLLMs responsibly!


# Docker status
Since v18, lollms can be run using Docker.
Just build the image. Assuming you are in lollms-webui folder :
```bash
docker build -t lollms-webui-app .
```
Then run ot using:
```bash
docker run -d -p 9600:9600 --name lollms-webui-container lollms-webui-app 
```
When lollms is first run, you can use
# Disclaimer
Large Language Models are amazing tools that can be used for diverse purposes. Lollms was built to harness this power to help the user enhance its productivity. But you need to keep in mind that these models have their limitations and should not replace human intelligence or creativity, but rather augment it by providing suggestions based on patterns found within large amounts of data. It is up to each individual how they choose to use them responsibly!

The performance of the system varies depending on the used model, its size and the dataset on whichit has been trained. The larger a language model's training set (the more examples), generally speaking - better results will follow when using such systems as opposed those with smaller ones. But there is still no guarantee that the output generated from any given prompt would always be perfect and it may contain errors due various reasons. So please make sure you do not use it for serious matters like choosing medications or making financial decisions without consulting an expert first hand! 

# license
This repository uses code under ApacheLicense Version 2.0 , see [license](https://github.com/ParisNeo/lollms-webui/blob/main/LICENSE) file for details about rights granted with respect to usage & distribution

# Copyright:
ParisNeo 2023


