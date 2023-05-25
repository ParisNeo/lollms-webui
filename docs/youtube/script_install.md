[INTRO]

Hi there. Today I finally make a presentation of the new alpha version of GPT4ALL webui.
Join us as we dive into the features and functionalities of this new version.

First, I want to thank all of you for your support. We have reached 2.1k stars on github And I hope you continue spreading the word about this tool to give it more visibility.

If not done yet, and if you think this project is useful, please consider gifting a star to the project, that helps alot.

Before starting, let me tell you what this project is made for. This project is aimed to be a hub to all LLM models that people can use. You will be able to choose your preferred binding, your preferred model, and your preferred or needed personality then have it do what you need. Help you enhance your mails, help you write an essai, help you debug a code, help you organize your thoughts, help you find answers to your questions, search for you, organize your data, generate images for you, discuss with you about things. And much more.


This project is under Apache 2.0 licence which is an open source licence that can be used commercially, so people can built things from this and use it in their business. 

Also, please don't confuse the GPT4All application built by Nomic AI which is an interesting more professional application that you can find on their website gpt4all.io. It has a great community and I encourage you to check it up. 

I have built this ui to explore new things and build on top of it. I am not building a company out of this, this is a side project. I just want to give back to the open source community and help make this technology available for all (hence the name).

I think all the contributors to this project and hope more people come and share their expertise. This help is vital to enhance the tool for all man kind.

Now let's cut to the chace. Let's start by installing the tool.
First, go to the github repository page at github.com/ParisNeo/gpt4all-ui then press the latest release button. Depending on your platform download webui.bat for windows or webui.sh for linux.

We call this file, the application launcher. Make sure you install the launcher in a folder you choose. For example I'll put it in my ai folder at gpt4all-webui.

Now let's run the script.
You may encounter a warning from some antivirus or windows defender warining you about the script. It is a false positive caused by the reputation condition in some antiviruses. This means if a program is not used by enough users, some antiviruses consider it dangerous. This is true for this tool as it is new and not enough people as using it as of now so I have to wait for it to become more accepted.

You may notice that the installer does not prompt you to install the default model any more as we now do this in the ui which is way easier.

Now let's take a look at the new ui. As the previous one, you have a light mode and a dark mode. You also have direct access to the github repository.

On the right side, you have the discussions panel, and on the center side, you have the messages flow.

Before starting to use the tool, we need to download a model for a specific binding.
To do this, go to settings. Then open the models zoo tab.
You need to select a binding from the list. For example the llama-cpp-official. The first time you select a binding, you have to wait as it  is being installed. You can look it up in the console.

Once the installation is done, you should install a model by pressing install and waiting for it to finish.

Once the model is installed, you can select it and press Apply modifications.

Notice that applying modifications does not save the configuration, so You need to press the save button and confirm.

Now your model is selected and you are ready to start your first discussion.

