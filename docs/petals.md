Thank you very much. I actually managed only to make it run on linux.
On windows, there is a dependency that is making this very very difficult: uvloop. This dependency explicitly rejects any attempt to install it on windows. There is active work to make it windows friendly, but the pull requests are not yet accepted and they don't seem to be fully working .

This means that my best shot at doing this is to use WSL.

It works like charm with WSL with cuda and everything:

![image](https://github.com/TheSCInitiative/bounties/assets/827993/aecc7e0e-2afa-4506-bbae-02bb12a355d2)
![image](https://github.com/TheSCInitiative/bounties/assets/827993/07f49df5-81e7-4391-9ddc-228b03a3c4d2)
![image](https://github.com/TheSCInitiative/bounties/assets/827993/6c30b8f8-b567-4311-a516-23416f2c3e47)
![image](https://github.com/TheSCInitiative/bounties/assets/827993/9bf4ff43-a4a7-4fc9-bc42-c49ec0bab2f5)
![image](https://github.com/TheSCInitiative/bounties/assets/827993/07f663da-6426-4fd1-b237-ee3d71903f01)
![image](https://github.com/TheSCInitiative/bounties/assets/827993/cb59498f-fde3-4e97-bcb0-187cb1422927)
![image](https://github.com/TheSCInitiative/bounties/assets/827993/ea9fb44a-f754-4346-8e26-edd30d9ef09f)
The node is visible from the [https://health.petals.dev/](https://health.petals.dev/) site. So everything is running fine.

To sum up, I've built a simple .bat file that installs an ubuntu WSL system, installs python and pip, then installs petals and runs the server.

But that won't be acceptable if I understand the rules of this challenge. So I am integrating the installation directly in the lollms binding installation procedure. Usually, if you are using linux, I install the binding and run the node from python with the right models.  So for windows I'll make a test and use the wsl instead.

![image](https://github.com/TheSCInitiative/bounties/assets/827993/dd005337-ee66-46c6-ae0d-73881eb34676)

Now with this, when you run lollms it starts the node but I need to code a bridge so that it is usable for text generation. I may go with a client that uses socketio to communicate with lollms.

The other solution is to literally install lollms in wsl, which will solve all bridging needs. I think I'll go with that other solution, that would save me some time.

I'll make a version of lollms that runs on wsl and is using petals by default.

DONE!

Now lollms can be installed with wsl support
Works!
![image](https://github.com/TheSCInitiative/bounties/assets/827993/a94e2a03-bc74-45d3-86f3-1f5f9eb2da09)
Now Install petals
![image](https://github.com/TheSCInitiative/bounties/assets/827993/a818eb40-387d-4fc5-8c88-5b8912648b20)

It automatically installs cuda and stuff:
![image](https://github.com/TheSCInitiative/bounties/assets/827993/4e3c7f1a-a99a-4083-8df7-6ff0065f9cf5)

Now it is using petals
![image](https://github.com/TheSCInitiative/bounties/assets/827993/6400deb6-255a-48b0-bfc3-1a26c01b15a2)

To finish, I create an exe installer:
![image](https://github.com/TheSCInitiative/bounties/assets/827993/873fa7d2-5688-4f6f-a5dd-a3743eb9df92)

One installed you will have three new icons
![image](https://github.com/TheSCInitiative/bounties/assets/827993/e10cc42a-b7af-4e1e-9750-aed1fd55880a)
The lollms with petals launches lollms with petals support
the petals server runs a petals-team/StableBeluga2 server
the ubuntu is a terminal to interact with the wsl image that is running lollms.

OK, now I finished making the installer. I'll make a video on how to do the install.
You can find all the scripts to build the installer in the lollms repository:
[https://github.com/ParisNeo/lollms-webui/tree/main/scripts/wsl](https://github.com/ParisNeo/lollms-webui/tree/main/scripts/wsl)

The installer is built using innosetup tool (free to download from the internet)

Steps:
- Download the installer (make sure your antivirus don't block the download because the installer is new and sometimes the antiviruses consider that its reputation is not high enough for it to be safe)
- Run the installer and accept licence and press next next next as any install.

![image](https://github.com/TheSCInitiative/bounties/assets/827993/4aaab953-75ce-4f63-86e6-1f273c0796ae)


- After copying files, a console window wil appear. If you don't have wsl, it will install it and install an ubuntu distribution, It will ask you for a user name and password to be used for the ubuntu distribution. Otherwize, it may load a terminal. Just type exit to go on.
- After that another script is executed, this script requires sudo privileges, so make sure you type the password you have created when installed the ubuntu wsl. This script will update all files, install cuda and add it to the path and setups the environment variables, configures the whole system, install miniconda, clone lollms-webui repository, install all required files. 
- Now you have finished the install, you will be asked if you want to run lollms, you can accept.
- Notice that there will be three new shortcuts on the desktop:

![image](https://github.com/TheSCInitiative/bounties/assets/827993/1250872c-a720-4656-a373-d4d43f125433)

- The first one is a simple ubuntu terminal, useful for debug and manual execution of petals
- The second one is for running lollms to do inference with petals or any other binding
- The third one is for running a petals server to give part of your PC to the community (you'll be prompted for a model hugging face path. if you press enter it will use petals-team/StableBeluga2)

You need to run lollms to install petals binding. When it is loaded it opens a browser. If it doesn't open a browser and navigate to localhost:9600.
Go to settings -> Bindings zoo -> petals and press install. You can monitor the install by looking at the console output.

Once ready, open the models zoo and select a model you want to use for petals. Wait for it to load. If no model is showing up, just reload the localhost:9600 page and then go to settings and the models zoo should have models in it.

![image](https://github.com/TheSCInitiative/bounties/assets/827993/d1981e83-ea36-4df4-be99-ca21cb8ed168)

You can run the petals server by double clicking the petals server icon on the desktop. This will use your machine as part of the hive mind:
![image](https://github.com/TheSCInitiative/bounties/assets/827993/1176c8f5-5e64-4df1-baf1-d8ada8d49b47)


And after all, in the discussion view it works like charm. We can see here that it is using the bs_petals which is the codename for the petals binding (i can't use the same name as the module to avoid import issues): 

![image](https://github.com/TheSCInitiative/bounties/assets/827993/8c453a88-240a-4836-9d69-8e9fd1273508)

Now this is all in my lollms hugging face repository.
You can find the code for wsl install of everything in here:
[https://github.com/ParisNeo/lollms-webui/tree/main/scripts/wsl](https://github.com/ParisNeo/lollms-webui/tree/main/scripts/wsl)

You can modify the code to adapt any aspect to your needs then use innosetup to generate an installer.

I also provide an executable installer on my release page of lollms, just select the petals version:
https://github.com/ParisNeo/lollms-webui/releases/tag/v6.5.0

The one with wsl and petals support is [lollms-with-petals.exe](https://github.com/ParisNeo/lollms-webui/releases/download/v6.5.0/lollms-with-petals.exe)

I will probably make a video explaining exactly how to install this tool.


I hope you like this. Tell me if you have questions or notice a bug or something.
Here is my free discord: https://discord.gg/vHRwSxb5
My twitter: https://twitter.com/SpaceNerduino

Best regards 







