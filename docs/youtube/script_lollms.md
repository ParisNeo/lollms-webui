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
The first time you run this application, you are prompted to select the binding. bindings are bridge modules that allows lollms to talk to different libraries that can run language models. If you are using a mac, I would recommend using gpt4all binding. If you have a powerful GPU and want to use as many models as possible then you go with ctransformers. The fastest for llama models is the official llama cpp binding. The Pyllamacpp is a tiny stable binding that runs with only llama models but can run on any pc seamlessly. As of today, GPTQ binding can run but it is still in experimental stage. Maybe use it in few weeks. I have a GPU, and want to test many models, so I'll go with CTransformers.
This may take few minutes to complete as it should install many modules.
Let's fastforward.
Once the binding is installed, you need to select a first model. You have the choice between installing a model from the internet or link to a local model file. This allows you tu mutualize models with other tools like Gpt4all or oobbabooga's text generation webui.
Let's choose to install a model from internet.
I advise you to checkout TheBlokes's hugging face space as he has a huge library of quantized models that you can download and use. Let's select a small model.
C Transformers is compatible with GGML models. So make sure you select a GGML one. Let's go with a very tiny orca mini 3B model quantized to 4 bits.
Copy and paste the model link to the console then press enter.
Downloading the model takes some time, so let's fast forward.
Once the model is downloaded, you can select it.
Now open your browser at the shown address. The default one is localhost:9600. You can change the address or port in the configuration file that you can find in your personal folder / configs / local_config.yaml. if you put 0.0.0.0 all your ip addresses will expose the ui. Make sure you use this in trustworthy networks as people may have access to your discussions. To stay safe, just use localhost to force a local use. The remote use may be useful if you want to use the app on your phone or another low power terminal. I will show you later how you can use multi servers / clients with secure access while keeping your data private without exposing them.
Now to start a conversation, just press + and start typing your prompt to the ai in the input area. you validate either by pressing enter, or by pressing the validation button. You can make a multiline prompt by holding shift key and pressing enter.
Let's ask it to make a short love story.
As you can see, the ai did come up with something. This model is very very small, so don't expect it to have a high peformance.
Now let's install a littble bit bigger model like the Falcon 7B.
To do this, we go to settings tab.
There are many changes since last time. Now you can monitor disk usage as well as both ram and v-ram usages if you have a cuda enabled GPU.
You can also install more bindings and select them as well as updating their configuration from the ui.
Check out the new models zoo. There are many many models out there. Feel free to try some of them to find which one fits you better.
Now let's find our falcon 7B model. For now the search option is not yet implemented but it is going to be implemented next week, so stay tuned.

Let's select a 4 bits quantization which is a good ratio between size and performance.
Press install and wait for it to download the model. You can install multiple models simultaniously. Make sure you have enough disk space as some of those models are very big.
Now let's take a look at the new personalities system.
The new system allows us to mount multiple personalities in the same session. This means that we can create a multipersonalities discussion.
There are many categories for english language. I will probably create more languages in the future and translate those personality files.
There are in total over 260 personalities in different fields and sorts. You can checkout the Job category where you cvan find multiple personalities.
We can activate personalities like shoping in a mall. Those personalities will be loaded at startup and will be easily accessible in the mounted personalities list.
Most personalities just have a yaml conditioning file and a logo in the assets folder. But some other personalities are more advanted with behavior and configuration parameters. Here we are going to show simple conversational personalities.
You can either use the personalities category organization or the search bar.
Once you finish mounting personalities, you can start a conversation. Here we talk to Einstein.
Let's ask it to teach us relativity.
To select another personality to interact with Einstein, just go to the settings page and select the personality you want to use. We are developing fast access to personalities in the main discussion page, it should be out in few days from now. 
Let's select Jack Sparrow.
To trigger generation, just press the refresh button from previous message and the tool will use your active personality to generate the next mesasge. you can go on doing this and exploring possible interactions between AI-s.

Now let's take a look in
