- After copying files, a console window wil appear. If you don't have wsl, it will install it and install an ubuntu distribution, It will ask you for a user name and password to be used for the ubuntu distribution. Otherwize, it may load a terminal. Just type exit to go on.
- After that, another script is executed, this script requires sudo privileges, so make sure you type the password you have created when installed the ubuntu wsl. This script will update all files, install cuda, add it to the path and setup the environment variables, configure the whole system, install miniconda, clone lollms-webui repository, install all required files. 
- Now you have finished the install, you will be asked if you want to run lollms, you can accept.
- Notice that there will be three new shortcuts on the desktop as stated before:
- The first one is a simple ubuntu terminal, useful for debug and manual execution of petals
- The second one is for running lollms to do inference with petals or any other binding
- The third one is for running a petals server to give part of your PC to the community (you'll be prompted for a model hugging face path. if you press enter it will use petals-team/StableBeluga2)

You need to run lollms to install petals binding. When it is loaded it opens a browser. If it doesn't open a browser and navigate to localhost:9600.
Go to settings -> Bindings zoo -> petals and press install. You can monitor the install by looking at the console output.

Once ready, open the models zoo and select a model you want to use for petals. Wait for it to load. If no model is showing up, just reload the localhost:9600 page and then go to settings and the models zoo should have models in it.

You can run the petals server by double clicking the petals server icon on the desktop. This will use your machine as part of the hive mind:
