# Lord of Large Language Models (LoLLMs) Documentation

LoLLMs (Lord of Large Language Models) is a powerful text generation framework that leverages distributed or centralized architecture with multiple service nodes. It enables users to generate text using various models and personalities. This documentation will guide you through the installation, setup, and usage of LoLLMs.

## Prerequisites

Before installing LoLLMs, ensure that you have the following prerequisites:

- Python 3.10: LoLLMs requires Python 3.10 or later. If you don't have Python installed, you can download it from the official Python website: [python.org](https://www.python.org/downloads/).

- pip: The Python package installer (`pip`) is required to install LoLLMs and its dependencies. pip usually comes pre-installed with Python. However, if you don't have pip installed or need to upgrade it, refer to the [pip installation guide](https://pip.pypa.io/en/stable/installing/) for instructions.

- Build Tools (optional): Some bindings used by LoLLMs may require build tools to be installed. Build tools are used to compile native code during the installation process. If you encounter any issues during installation related to missing build tools, you may need to install them. Refer to the documentation of your operating system or package manager for instructions on installing build tools.

- CUDA (optional, for GPU support): If you want to enable GPU support for certain bindings, you need to have CUDA installed. CUDA is a parallel computing platform and programming model developed by NVIDIA. GPU support can significantly improve the performance of LoLLMs for certain tasks. To install CUDA, follow the instructions provided in the [NVIDIA CUDA Toolkit documentation](https://docs.nvidia.com/cuda/).

## Installation

To install LoLLMs and its dependencies, follow these steps:

1. Open your terminal or command prompt.

2. Run the following command to install LoLLMs using pip:

   ```shell
   pip install lollms
   ```

   If you encounter any permission issues, you may need to use `sudo` or run the command in an elevated prompt.

3. Wait for the installation process to complete. It may take some time depending on your internet connection and the system's configuration.

## Setup

After installing LoLLMs, you need to set it up before using it. Follow the steps below:

1. Open your terminal or command prompt.

2. Run the following command to access the LoLLMs settings:

   ```shell
   lollms-settings
   ```

3. In the settings prompt, select the desired binding, such as `ctransformer`, from the available options.

4. Choose a model from the provided options.

5. Optionally, select one of the preconditioned personalities. There are 260 personalities available.

6. Save the settings.

## Starting the LoLLMs Server

To start the LoLLMs server, follow these steps:

1. Open your terminal or command prompt.

2. Run the following command:

   ```shell
   lollms-server
   ```

3. This will start a local server on `localhost:9600`.

You can also run multiple LoLLMs servers on different hosts and ports. To specify a different host and port, use the following command:

```shell
lollms-server --host <hostname> --port <port>
```

Replace `<hostname>` with the desired hostname and `<port>` with the desired port number.

## Using the LoLLMs Playground

LoLLMs provides a user-friendly playground for generating text. You can use the pre-built playground or create your own code to interact with the LoLLMs server.

To use the LoLLMs playground:

1. Clone the [

LoLLMs Playground repository](https://github.com/ParisNeo/lollms-playground) from GitHub.

2. Open the playground in your web browser.

## Using the LoLLMs Console App

LoLLMs also provides a console app that allows direct text generation from a console interface. To start the console app, follow these steps:

1. After installing LoLLMs, open your terminal or command prompt.

2. Run the following command to start the LoLLMs console:

   ```shell
   lollms-console
   ```

3. The console app will load the same binding and personalities that are active on the server.

4. You can type `exit` to stop the application.

5. Typing `help` will display help information.

6. Typing `menu` will display a menu where you can select entries by typing their number. The menu may have submenus for selecting binding, model, personality, and installing models from the internet or a local file.

Please note that the console app provides a convenient way to generate text directly from the console interface.

## Disclaimer

Text generation using LoLLMs is a powerful tool that can enhance productivity and stimulate creativity. However, it is important to use this tool responsibly and ethically. LoLLMs should not be used for any malicious purposes or to generate harmful or misleading content. The generated text should be carefully reviewed and validated before being used in any public or critical contexts.

Always consider the implications and potential biases associated with text generation. Use LoLLMs as a tool to explore ideas, aid in writing, or expand your imagination. Respect copyright laws, privacy, and the rights of others when using LoLLMs for any purpose.

## Conclusion

Congratulations! You have successfully installed, set up, and used LoLLMs. Ensure that you have Python 3.10 or later, pip, and any necessary build tools installed. If you want to enable GPU support, consider installing CUDA. You can now generate text using the provided interface, the playground, or the console app. Explore the capabilities of LoLLMs and enjoy generating text with large language models!
