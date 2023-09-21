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
the ubuntu is a terminal to interact with wsl


You can learn more about lollms in my youtube videos:
https://www.youtube.com/results?search_query=lollms
Or directly from the github:
https://github.com/ParisNeo/lollms-webui

It is a multi bindings UI for text generation that provides personalities to chat with, a playground for experimenting with text generation tasks along with multiple presets gfor many applications. It also support image and video generation as well as music generation. All in one :)

