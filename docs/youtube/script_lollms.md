Hi Every one.
This is a new video about Lord of Large language models, formally known as LoLLMs webui.

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
The first time you run this application, you are prompted to select the binding. bindings are bridge modules that allows lollms to talk to different libraries that can run language models. If you are using a mac, I would recommend using lollms binding. If you have a powerful GPU and want to use as many models as possible then you go with ctransformers. The fastest for llama models is the official llama cpp binding. The Pyllamacpp is a tiny stable binding that runs with only llama models but can run on any pc seamlessly. As of today, GPTQ binding can run but it is still in experimental stage. Maybe use it in few weeks. I have a GPU, and want to test many models, so I'll go with CTransformers.
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

Few days have passed and now the personality system has been enhanced. Let's start by mounting personalities to use in a multipersonalities conversation.


Let's talk to empror Napoleon Bonaparte and ask it about his plans after conquering Egypt.Now, as you can see, you have a new module in the ui that shows the current personality icon. When we press the + button, we can select the personality to talk to.

With this, we can make personalities talk to each other by selecting next personality and pressing the regenerate answer button. This will be refined in the future. It is still a work in progress but the feature is pretty much usable right now. You can explore impossible discussions between personalities that never lived in the same era, never spoken the same language and sometimes the discussions get really interesting. Be aware that the quality of the discussions depend heavily on the model you use. You can view which model was used to generate each message as well as time needed to generate the answer. Feel free to explore these things and share your findings on internet.

Now let me show you this new binding made for those who have a network with a powerful pc or server and many low grade PCs or terminals. We can use this new binding to create a text generation service for all those little PCs which is really interesting if you have a company and want to keep your data local while investing in only a handful of nodes, servers or high end PCs and give the text generation service to all your workers. This can also be done at home where you may have a PC with GPU and few laptops or raspberry pi that can benefit from the text generation service on your PC. I personally do that and it is a great trade off allowing for mutualization of resources.

First we need to install the lollms library and run the lollms server. go to the console and type:
pip install --upgrade lollms
This will install the library along with the server, a console generation tool and a settings tool.
Once the installation is done, just run lollms-server and follow the instruction. The first time you use it, it will ask for the path to your personal data folder. You can use the same folder as the webui if you want to mutualize your models and settings. The server bindings and model names are exclusive to each application. This is logical as if you want to use the lollms remote nodes for the client, you would use another binding for the server. In fact the server configuration file has a prefix lollms_server. 

Now we need to come back to our web-ui and configure the servers we want to use. Here we used a local server, so we just use its name as http://localhost:9601 but you can run the server on a different PC. Just make sure you run the lollms-server with the option --host 0.0.0.0 which will expose the server on all ip adresses of your PC. You can also specify the IP address. You can run multiple servers on the same node by changing the port number using --port parameter of the lollms-server. You can also add multiple server paths in the configuration by separating them using a comma. Make sure this parameter is a list of strings put inside brackets just as in python. 

You can view in the console what servers are active at the moment. You can  choose to completely remove the inactive servers from the list for the current session or to continue trying to connect to them whenever a new generation is attempted.

Now that our remote service is up, we can use it as we use any local binding.
Let's ask Carl sagan what is cosmos.

If we look at the Lollms console, we can see that it got the prompt and is generating the words.

As you can see, generative AI has a huge potential to help us enhance our productivity. This tool is a little glimpse of what AI models especially generative models are capable of. AI is a tool, it can be used for good, as for bad. I hope you use this tool wizely and bare in mind that the future of humanity may depend on how we use these technologies. It is now impossible to stop AI development but we should tame it and make sure that its goals are aligned with ours. It can lead us to a bright future where we fix urgent problems like climate change and resource depletion, where we aceive great science discoveries, like building a better physics theory that can fuse quantum physics and general relativity. Or it can lead us to a dark world where AI empowers a handful of ritch people and enslaves the rest. I personally think that open source is the way to ensure fair access to every one to those tools.

I hope that you have liked this video. If you did, please consider leaving a thumb up, a sub to the channel and a comment. Thank you for watching. C ya