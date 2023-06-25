Hi Every one.
This is a new video about Lord of Large language models, formally known as GPT4All webui.

In this video, we start by presenting the tool, its phylosophy and it's main goals. Then, we discuss how to install and use it, we dive deep into its different use cases and how you can harness the power of Large language models in one tool. We will also do some interesting tests and comparisons of models and bindings, and we'll finish by some thoughts about AI, its benefits and dangers.

To start, I have changed the name of the tool to confirm its identity as a separate free project that aims at supporting all those open source libraries for large language models.

The slogan is: One tool to rule them all. This tool uses multiple opensource libraries built by various developers from all around the world and creates a unique interface to talk to all of them in three different ways:
First, you can use lollms as a library in a python project
Second, you can use the socket-io API to trigger text generation from any program capable of talking to socket-io services. This covers a very large number of languages such as javascript, c#, c++ etc.
The third use is by directly using out web-ui to interact with the language models.
The web-ui has multiple functionalities and allow you to handle many tasks.

Now let's install the application.
To install the application, you need to have already installed git and python 3.10 with its pip package manager. You can optionally have anaconda or miniconda installed if you want to use that option. To use the GPU, you also need to install Cuda toolkit v 11.7 or higher or use the conda installation script that will automatically install conda build tools. Make sure git, python and cuda are added to your path environment variable and let's begin.
As usual, go to the github repository then to the release page. Now you have many options depending on your system and your preference. for windows, you can use webui.bat or c_webui.bat, for linux, you can use webui.sh or c-webui.sh. C stands for conda, so if you havn't installed conda, don't use that file.

Download the file to a folder where you want to install the application. 

Once it is downloaded, go to the folder and double click the script to run it.
Now just follow the instructions.
The tool start by cloning the project into a subfolder called lollms-webui.
If you don't have conda, this will ask you if you want to install it. I already have conda, so it will just create a conda environment in the lollms-webui/env folder and will install every thing in there. This is to ensure that your system is not polluted with useless libraries if ever you want to delete this tool.
When you are asked to install cuda, the answer depends on your system. If you have an nvidea GPU accept, otherwize refuse.
You will be asked to select a personal folder. This folder will contain:
- the bindings zoo
- the installed models
- the personalities zoo
- the configurations
- the data files
- the outputs of the models which can be text, images, or even executable code etc
- the configuration files
- the discussion database
Make sure to put this folder to a partition that has enough space as models may be heavy sometimes. 
Here I just press enter to choose the default location which is my documents folder.
