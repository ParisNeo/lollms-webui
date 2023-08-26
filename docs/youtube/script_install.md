Hi there. Today I finally make a presentation of the new alpha version of LOLLMS webui.
Join us as we dive into the features and functionalities of this new version.

First, I want to thank all of you for your support. We have reached 2.1k stars on github And I hope you continue spreading the word about this tool to give it more visibility.

If not done yet, and if you think this project is useful, please consider gifting a star to the project, that helps alot.

Before starting, let me tell you what this project is made for. This project is aimed to be a hub to all LLM models that people can use. You will be able to choose your preferred binding, your preferred model, and your preferred or needed personality then have it do what you need. Help you enhance your mails, help you write an essai, help you debug a code, help you organize your thoughts, help you find answers to your questions, search for you, organize your data, generate images for you, discuss with you about things. And much more.


This project is under Apache 2.0 licence which is an open source licence that can be used commercially, so people can built things from this and use it in their business. 

Also, please don't confuse the LoLLMs application built by Nomic AI which is an interesting more professional application that you can find on their website lollms.io. It has a great community and I encourage you to check it up. 

I have built this ui to explore new things and build on top of it. I am not building a company out of this, this is a side project. I just want to give back to the open source community and help make this technology available for all (hence the name).

I think all the contributors to this project and hope more people come and share their expertise. This help is vital to enhance the tool for all man kind.

Before installing this tool you need to install python 3.10 or higher as well as git. Make sure the python installation is in your path and you can call it from a terminal. To verify your python version, type python --version. If you get an error or the version is lower than 3.10, please install a newer version and try again. For those who use conda, you can create a conda virtual environment, install the requirements.txt content and just run the application using python app.py. Now we assume that you have a regular python installation and just want to use the tool.  



Now let's cut to the chace. Let's start by installing the tool.
First, go to the github repository page at github.com/ParisNeo/lollms-webui then press the latest release button. Depending on your platform download webui.bat for windows or webui.sh for linux.

We call this file, the application launcher. Make sure you install the launcher in a folder you choose. For example I'll put it in my ai folder at lollms-webui.

Now let's run the script.
You may encounter a warning from some antivirus or windows defender warining you about the script. It is a false positive caused by the reputation condition in some antiviruses. This means if a program is not used by enough users, some antiviruses consider it dangerous. This is true for this tool as it is new and not enough people as using it as of now so I have to wait for it to become more accepted.

You may notice that the installer does not prompt you to install the default model any more as we now do this in the ui which is way easier.

Now let's take a look at the new ui. As the previous one, you have a light mode and a dark mode. You also have direct access to the github repository.

On the left side, you have the discussions panel, and on the center side, you have the messages flow.

Before starting to use the tool, we need to download a model for a specific binding.
To do this, go to settings. Then open the models zoo tab.
You need to select a binding from the list. For example the llama-cpp-official. The first time you select a binding, you have to wait as it  is being installed. You can look it up in the console.

Once the installation is done, you should install a model by pressing install and waiting for it to finish.
This may take some time.

Once the model is installed, you can select it and press Apply changes.

Notice that applying modifications does not save the configuration, so You need to press the save button and confirm.

Now your model is selected and you are ready to start your first discussion.

Let's go back to discussions view. To create a new discussion, press the + button. You should see the personality welcome message. This is a predefined welcome message that you can find in the personality configuration file. by default, we use the LoLLMs personality which is conditioned to be a helpful personality. Let's ask it something. For example, who is Abraham Lincoln?

You can stop the generation at any time by pressing the Stop Generating button.

Now that the generation is done, we can see that it did a good job. In fact there is a little generation starting time at the beginning, but one it starts, you get around two words a second depending on your pc or mac configuration. As this is a discussion, we can follow up by asking to give more details.

You can see that the model did give a more detailed text about Abraham Lincoln. You can fact check the information on wikipedia, as those models may sometimes hallucinate or invent things that are not true. It depends on the quality of the data used to train the model and to fine tune it. Some models are better than others. You can test by yourself to choose the best model for your needs. This is one of the advantages of being able to test multiple bindings and multiple models.


Just as previous version, you can give the answer a thumb up or a thumb down, you can also edit the message, copy the message to the clip board, and remove the message. Notice that we removed the option to have the message read by the AI, but this feature should be added in the release version. I think of giving different voices to each personality and use a fullly local library as the previous version used a remote text to speach synthesizer. Our phylosophy is, your data should stay on your PC and never be sent out unless you explicitly do it yourself.


Now let's focus on the discussions sidebar. As we saw, we can create new discussion. When you create a new discussion, its name is always new discussion, but as soon as you put your initial prompt, the discussion title take the first message you typed as the title. You can edit the title at any time, or delete the discussion. All your discussions are stored in a local sqlite3 database on your databases/database.db file. You can change the database path in your configs/local_config.yaml file. We will make this possible from the UI in the release version.

In chat-GPT ui, one complaint I have is the difficulty to find out your discussion after days of discussions. So we have thought this up by adding a search button that allows you to search your discussions at any time. You can also delete multiple discussions or export them. Exporting messages may be interesting for training, but also for contributing to datalakes to help the community get more quality data. you can do any multi-discussions operation by pressing the check mode button. now you can select one or many discussions then you can export them or delete them.

In this tutorial we have seen how to install the new ui, how to select a binding, download and select a model, how to start a discussion and follow up with more details, how to manipulate discussions.
In the next tutorial we will take a look at the personalities zoo and all the 250 personalities that you can interact with.

Thank you very much for your attention. I hope you like this tool, test it, share your experience with it and report bugs. This is an amateur project, so don't be harsh on us as we do this in our free time.

Don't forget to hit like and subscribe and share the video if you want it to reach more people.

See ya