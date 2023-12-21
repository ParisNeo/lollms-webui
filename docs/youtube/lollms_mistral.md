Hi there,

Let me show you how you can use the new web RAG (Retreival Augmented Generation) proposed on lollms to allow your persona to use a path to a website to learn how to do some new stuff.

Here I'll point it to my FaceAnalyzer library that you can find on my github page then ask it to make an application for detecting my facial landmarks in realtime and show them in green.

The AI will use the content of my github readme in order to accomplish my request. You can also add multiple paths if you have a more complex request that requires more than one library.

We will be using the new MistralAI medium model through MistralAI API. To use this binding you need to create a mistralAI account and get a key that you should put in settings.

Let's start by going to the github of the FaceAnalyzer application then copy its path. Now in lollms, press the globe button and paste the path.

Select Mistral AI binding and  the Mistral Medium model from the models zoo.

Now let's ask it to make the code.

As you can see, the code seems correct, it does use the FaceAnalyzer library as it should. Let's execute it.

As you can see, the application works. We didn't need to do multiple turn discussions, the model was good enough to accomplish the task just as I asked.

Combining Lollms, its personas, and its Rag with the power of mistral AI allows you to be more productive.

Thanks for watching
See ya

