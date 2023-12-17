Hi there,

In this short I'm going to show you how to install lollms in GPU mode and use the hugging face binding to run inference.

The steps to aceive this are simple:
download the installer from the github of the project to an empty folder with a path that does not contain spaces.
double click the installer and validate.
select the install mode (Cuda, rocm or cpu)
wait
Run the app
Choose the personal data folder
Install a binding then Reboot the app
Select the binding
Install a model
Select a model

And now you are ready to rock

Let me show you how I do it:

Start by opening the lollms web user interface link that you can find in the description. Then go to the latest release page and download the installer suited for your platform. Make sure you put it into a path with no spaces and inside an empty folder as it will fill out the folder with the install files.

Now execute the installer. As it says, make sure the path you are using is not very long and without spaces as conda may have bugs with paths that contains spaces.

Now press enter to continue.

Select the right configuration. if you have an nvisia gpu, select option a. if you have a Rocm compatible GPU like AMD GPUs press B. If you have no GPU or want to use remote generation, then select C.

Now just wait

Once the installation is done, close the installation script and go back to the install folder.
run the win_run.bat file and wait for the program to run for the first time.
Some additional libraries may need to be installed the first time you run it.


The first time you run the app, you will need to specify a folder where to put your personal data. Make sure the disk containing this folder is big enough as it will hold your models as well as the personas outputs and your discussion databases. The default folder is a folder called lollms under your documents folder. Just press enter if it is ok or type another path then press enter.

Now lollms is installed, but there is no binding installed nor a model. To do this, go to settings tab, select binding s zoo and install a binding depending on your preferences. Here I am using a GPU and want local generation, so I will select Hugging face to use full sized models, GPTQ quantized models or AWQ quantized models. The installation may take some while, you can look at the install details in the console window.

