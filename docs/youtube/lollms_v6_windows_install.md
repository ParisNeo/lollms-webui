Hi there. Today I'll show you how to install and use lollms v6 on windows using the executable installer.
First go to the github page shown below and download lollms_v6_cpu.exe.
Then, run the downloaded file.
Sometimes, windows may warn you as the executable is not signed and not yet massively used. You can simply ignore the warning and procede with the installation.
You will be presented with a classic installer, accept the license and read the code of conduct, then the installer will install the tool on your PC.
Optionally, you can add a shortcut to your desktop for fast and easy access.
The install may take a while, so let's fast forward.
After the install, you may get this error if you did run the installer as regular user. It is windows trying to forbid the installer from creating the start menu element. Don't bother, you can just press ok and finish the installation.
Now you can run the application.
With this install procedure, you get a complete fully functional and self-contained version of the tool in cpu mode. This version is fixed so when I release a new version, you can do the same install and it will update the entire tool with the new version of the code.
You won't have access to realtime updates I do regularly on the gitbub, But I'll show you how to do that manually.
Press the link to load the ui on the browser.
This tool is delivered with all bindings code, but without models as they are heavy and can make the installer very big. So the first thing to do is to install a model. By default, you are using cpu mode and the selected binding is c_transformers.
Go to settings page, then to the models zoo and download a model.
You can use the search bar to search for a model by name.
Find the model you want, press install, select a quantization level and validate.
Now wait for the model to be downloaded.
Once downloaded, the model card change, and now you have an uninstall button instead of the install button. Click anywhere on the card to select the model.
Now you can configure your user name and avatar.
Don't forget to apply changes, otherwize they will not be committed to the backend. Also, by default apply change saves the settings permanently. You can change this behavior by unchecking auto save checkbox.
You can also set up other settings like document vectorization options and audio settings.
Now let's go to discussion tab and start a new discussion. Let's ask lollms to write a poem about himself.
The first time you may have to waite a bit depending on your PC computing power, then the generation will happen token by token at a speed that depends on your CPU speed, the size of the model and the amount of memory you have.
Here for example we get around 1 token per second which is slow compared to what you can get if you use GPU.
Let's fast forward.
You can find extra information at the bottom of the message, like the binding and model that were used as well as the time it took to generate the text.
Now let's take a rapid look at the playground. Go to playground app.
This app is basically a text completion app. You just put some text and press the stylus button to start generating. You can stop the generation at any time, make adjustments, then generate etc. You can control all generation parameters, select the model to test and you can also find presets that I have wrote to build new tasks like text translation, coding and other things. You can also create your own presets. I will cover this in a future video.

Now using CPU is ok for small models like 7B or even 13B as we did here, but you get much faster output if you use GPU.
The next section will talk about installing GPU support 
You can view your configuration in the settings where you can see how much memory are you pulling as well as remaining diskk space.
Start by going to the main settings and check enable gpu.
Don't forget to apply changes.
Now we are ready to install GPU support.
In the settings page, you can view your hardware status to verify how much disk or memory you still have. This is important if you want to use multimodal personalities that require extra memory when loaded.
I have built an all in one procedure that allows you to automatically install cuda and pytorch by a single click of a button.
Go to main configuration section and press the Update from CPU to GPU button.
You will need to take a look at the console as it will ask you for confirmation when installing cuda toolkit.
Press y to accept the install procedure and wait till install is finished.
When all installs are done, the settings page clears up.
Now we can either reinstall C transformers binding and it will automatically get into the GPU mode, or install the GPTQ binding or another binding. Here let's install autoGPTQ binding.
Go to the bindings zoo and press install in the auto gptq binding card.
You can view the install in the console.
If ever it hangs for a long time, just press enter in the console window and wait.
Now we are ready to install a model. Let's try the new WizardLM's Wizard-Coder-python-13B.
Once installed, select it.
In the console, you can see the model being loaded.
Once loaded, you can view many information about the model, its structure, and its parameters.
Now let's head back to the UI
Apply changes then go to the discussions view.
Here, the autosave is activated, so there is no need for manually saving.
Let's ask the same question and monitor the generation speed enhancement.
As you can see, the speed is higher with GPU than it was on CPU.
The speed will depend on many things, including your hardware power, the model size, and weather or not you need to split it between CPU and GPU.
Now it is your turn to play around with lollms. You have fast access to models and personalities. You can also send files to talk about, you can use audio in and audio out and many more.
I hope you liked this tutorial.
Don't forget to share, like and subscribe.

See ya.

