# Gpt4All Web UI

![GitHub license](https://img.shields.io/github/license/nomic-ai/GPT4All-ui)
![GitHub issues](https://img.shields.io/github/issues/nomic-ai/GPT4All-ui)
![GitHub stars](https://img.shields.io/github/stars/nomic-ai/GPT4All-ui)
![GitHub forks](https://img.shields.io/github/forks/nomic-ai/GPT4All-ui)
[![Discord](https://img.shields.io/discord/1092918764925882418?color=7289da&label=Discord&logo=discord&logoColor=ffffff)](https://discord.gg/DZ4wsgg4)

This is a Flask web application that provides a chat UI for interacting with llamacpp based chatbots such as GPT4all, vicuna etc...

Follow us on our [Discord server](https://discord.gg/DZ4wsgg4).

## What is GPT4All ?

GPT4All is an exceptional language model, designed and developed by Nomic-AI, a proficient company dedicated to natural language processing. The app uses Nomic-AI's advanced library to communicate with the cutting-edge GPT4All model, which operates locally on the user's PC, ensuring seamless and efficient communication.

If you are interested in learning more about this groundbreaking project, visit their [Github repository](https://github.com/nomic-ai/gpt4all), where you can find comprehensive information regarding the app's functionalities and technical details. Moreover, you can delve deeper into the training process and database by going through their detailed Technical report, available for download at [Technical report](https://s3.amazonaws.com/static.nomic.ai/gpt4all/2023_GPT4All_Technical_Report.pdf).

One of the app's impressive features is that it allows users to send messages to the chatbot and receive instantaneous responses in real-time, ensuring a seamless user experience. Additionally, the app facilitates the exportation of the entire chat history in either text or JSON format, providing greater flexibility to the users.

It's worth noting that the model has recently been launched, and it's expected to evolve over time, enabling it to become even better in the future. This webui is designed to provide the community with easy and fully localized access to a chatbot that will continue to improve and adapt over time.

## UI screenshot
### MAIN page
![image](https://user-images.githubusercontent.com/827993/231911545-750c8293-58e4-4fac-8b34-f5c0d57a2f7d.png)
### Settings page
![image](https://user-images.githubusercontent.com/827993/231912018-4e69e0c3-cbef-4dc8-81b3-d977d96cc7de.png)
### Extensions page
The extensions interface is not yet ready but once it will be, any one may build its own plugins and share them with the community.
![image](https://user-images.githubusercontent.com/827993/231809762-0dd8127e-0cab-4310-9df3-d1cff89cf589.png)
### Training page
This page is not yet ready, but it will eventually be released to allow you to fine tune your own model and share it if you want
![image](https://user-images.githubusercontent.com/827993/231810125-b39c0672-f748-4311-9523-9b27b8a89dfe.png)
### Help
This page shows credits to the developers, How to use, few FAQ, and some examples to test.

## Installation

To install the app, follow these steps:

1.  Clone the GitHub repository:

```
git clone https://github.com/nomic-ai/gpt4all-ui
```

### Manual setup
Hint: Scroll down for docker-compose setup

1.  Navigate to the project directory:

```bash
cd gpt4all-ui
```

2.  Run the appropriate installation script for your platform:

On Windows :
```cmd
install.bat
```
- On Linux

```bash
bash ./install.sh
```

- On Mac os

```bash
bash ./install-macos.sh
```

On Linux/MacOS, if you have issues, refer more details are presented [here](docs/Linux_Osx_Install.md)
These scripts will create a Python virtual environment and install the required dependencies. It will also download the models and install them.

Now you're ready to work!

# Supported models
You can also refuse to download the model during the install procedure and download it manually.
For now we support any ggml model such as :
- [GPT4ALL 7B](https://huggingface.co/ParisNeo/GPT4All/resolve/main/gpt4all-lora-quantized-ggml.bin) 
- [Vicuna 7B](https://huggingface.co/eachadea/legacy-ggml-vicuna-7b-4bit/resolve/main/ggml-vicuna-7b-4bit.bin) NOTE:  Does not work out of the box
- [Vicuna 7B rev 1](https://huggingface.co/eachadea/legacy-ggml-vicuna-7b-4bit/resolve/main/ggml-vicuna-7b-4bit-rev1.bin)
- [Vicuna 13B q4 v0](https://huggingface.co/eachadea/ggml-vicuna-13b-1.1/resolve/main/ggml-vicuna-13b-1.1-q4_0.bin) NOTE:  Does not work out of the box
- [Vicuna 13B q4 v1](https://huggingface.co/eachadea/ggml-vicuna-13b-1.1/resolve/main/ggml-vicuna-13b-1.1-q4_1.bin) NOTE:  Does not work out of the box 
- [Vicuna 13B rev 1](https://huggingface.co/eachadea/ggml-vicuna-13b-4bit/resolve/main/ggml-vicuna-13b-4bit-rev1.bin)
- [ALPACA 7B](https://huggingface.co/Sosaka/Alpaca-native-4bit-ggml/blob/main/ggml-alpaca-7b-q4.bin) NOTE:  Does not work out of the box - Needs conversion

Just download the model into the models folder and start using the tool.
## Usage
For simple newbies on Windows:
```cmd
run.bat
```

For simple newbies on Linux/MacOsX:
```bash
bash run.sh
```

if you want more control on your launch, you can activate your environment:

On Windows:
```cmd
env/Scripts/activate.bat
```

On Linux/MacOs:
```cmd
source venv/bin/activate
```

Now you are ready to customize your Bot.

To run the Flask server, execute the following command:
```bash
python app.py [--config CONFIG] [--personality PERSONALITY] [--port PORT] [--host HOST] [--temp TEMP] [--n-predict N_PREDICT] [--top-k TOP_K] [--top-p TOP_P] [--repeat-penalty REPEAT_PENALTY] [--repeat-last-n REPEAT_LAST_N] [--ctx-size CTX_SIZE]
```

On Linux/MacOS more details are [here](docs/Linux_Osx_Usage.md)


## Options
*   `--config`: the configuration file to be used. It contains default configurations to be used. The script parameters will override the configurations inside the configuration file. It must be placed in configs folder (default: default.yaml)
*   `--personality`: the personality file name. It contains the definition of the pezrsonality of the chatbot. It should be placed in personalities folder. The default personality is `gpt4all_chatbot.yaml`
*   `--model`: the name of the model to be used. The model should be placed in models folder (default: gpt4all-lora-quantized.bin)
*   `--seed`: the random seed for reproductibility. If fixed, it is possible to reproduce the outputs exactly (default: random)
*   `--port`: the port on which to run the server (default: 9600)
*   `--host`: the host address on which to run the server (default: localhost)
*   `--temp`: the sampling temperature for the model (default: 0.1)
*   `--n-predict`: the number of tokens to predict at a time (default: 128)
*   `--top-k`: the number of top-k candidates to consider for sampling (default: 40)
*   `--top-p`: the cumulative probability threshold for top-p sampling (default: 0.90)
*   `--repeat-penalty`: the penalty to apply for repeated n-grams (default: 1.3)
*   `--repeat-last-n`: the number of tokens to use for detecting repeated n-grams (default: 64)
*   `--ctx-size`: the maximum context size to use for generating responses (default: 2048)

Note: All options are optional, and have default values.

Once the server is running, open your web browser and navigate to http://localhost:9600 (or http://your host name:your port number if you have selected different values for those) to access the chatbot UI. To use the app, open a web browser and navigate to this URL.

Make sure to adjust the default values and descriptions of the options to match your specific application.

### Docker Compose Setup
Make sure to have the `gpt4all-lora-quantized-ggml.bin` inside the `models` directory.
After that you can simply use docker-compose or podman-compose to build and start the application:

Build
```bash
docker-compose -f docker-compose.yml build
```

Start
```bash
docker-compose -f docker-compose.yml up
```

After that you can open the application in your browser on http://localhost:9600


## Update To latest version

On windows use:
```bash
update.bat
```
On linux or macos use:
```bash
bash update.sh
```


## Build custom personalities and share them

To build a new personality, create a new file with the name of the personality inside the personalities folder. You can look at `gpt4all_chatbot.yaml` file as an example. Then you can fill the fields with the description, the conditionning etc of your personality. Then save the file.

You can launch the application using the personality in two ways:
- Either you want to change it permanently by putting the name of the personality inside your configuration file
- Or just use the `--personality` or `-p` option to give the personality name to be used.

If you deem your personality worthy of sharing, you can share the personality by adding it to the [GPT4all personalities](https://github.com/ParisNeo/GPT4All_Personalities) repository. Just fork the repo, add your file and do a pull request.


## Features

- Chat with AI
- Create, edit, and share personality
- Audio in and audio out with many options for language and voices
- History of discussion with resume functionality
- Add new discussion, rename discussion, remove discussion
- Export database to json format
- Export discussion to text format

## Contribute

This is an open-source project by the community for the community. Our chatbot is a UI wrapper for Nomic AI's model, which enables natural language processing and machine learning capabilities.

We welcome contributions from anyone who is interested in improving our chatbot. Whether you want to report a bug, suggest a feature, or submit a pull request, we encourage you to get involved and help us make our chatbot even better.

Before contributing, please take a moment to review our [code of conduct](./CODE_OF_CONDUCT.md). We expect all contributors to abide by this code of conduct, which outlines our expectations for respectful communication, collaborative development, and innovative contributions.

### Reporting Bugs

If you find a bug or other issue with our chatbot, please report it by [opening an issue](https://github.com/your-username/your-chatbot/issues/new). Be sure to provide as much detail as possible, including steps to reproduce the issue and any relevant error messages.

### Suggesting Features

If you have an idea for a new feature or improvement to our chatbot, we encourage you to [open an issue](https://github.com/your-username/your-chatbot/issues/new) to discuss it. We welcome feedback and ideas from the community and will consider all suggestions that align with our project goals.

### Contributing Code

If you want to contribute code to our chatbot, please follow these steps:

1.  Fork the repository and create a new branch for your changes.
2.  Make your changes and ensure that they follow our coding conventions.
3.  Test your changes to ensure that they work as expected.
4.  Submit a pull request with a clear description of your changes and the problem they solve.

We will review your pull request as soon as possible and provide feedback on any necessary changes. We appreciate your contributions and look forward to working with you!

Please note that all contributions are subject to review and approval by our project maintainers. We reserve the right to reject any contribution that does not align with our project goals or standards.

## Future Plans

Here are some of the future plans for this project:

**Enhanced control of chatbot parameters:** We plan to improve the user interface (UI) of the chatbot to allow users to control the parameters of the chatbot such as temperature and other variables. This will give users more control over the chatbot's responses, and allow for a more customized experience.

**Extension system for plugins:** We are also working on an extension system that will allow developers to create plugins for the chatbot. These plugins will be able to add new features and capabilities to the chatbot, and allow for greater customization of the chatbot's behavior.

**Enhanced UI with themes and skins:** Additionally, we plan to enhance the user interface of the chatbot to allow for themes and skins. This will allow users to personalize the appearance of the chatbot, and make it more visually appealing.

We are excited about these future plans for the project and look forward to implementing them in the near future. Stay tuned for updates!

## License

This project is licensed under the Apache 2.0 License. See the [LICENSE](https://github.com/nomic-ai/GPT4All-ui/blob/main/LICENSE) file for details.
