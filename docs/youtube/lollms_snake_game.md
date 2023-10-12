Hi there. In this video, we will demonstrate how to code, debug, test, and deploy a game by interacting with lollms. We will be using the open-ai binding and the gpt3.5-turbo model. While gpt4 is an option, it is not necessary for this demonstration. Before starting, remember to activate the open-ai binding, set your key in the binding settings, select the model, and apply the changes.

Feel free to use any other binding and model combination, but keep in mind that most models are slower and less powerful than GPT. So, to showcase the possibilities, we will be using GPT3.5-turbo.

We sill be using the Python specialist as ourt lollms persona. It conditions the model to act as a specialist in python which makes the AI more focused on its task.

Let's begin by setting the initial prompt: "Let's make a snake game using pygame as the graphic engine and let's make the snake red and the food green.
Please comment your code and use docstring, typing and fstrings for text rendering."

Before we proceed, the AI asks if we have installed pygame. I have already installed it in the conda environment of lollms before starting the test. Make sure to do the same if you want to replicate the experiment.

Next, the Python expert explains how to build the game and provides some code. Now, let's ask the AI to put it all together.

With the code written, we can now execute it directly from lollms.

As we can see, the game is working, but there is an alignment issue. Let's ask the AI to make the game grid-based to ensure everything aligns properly.

The Python expert showed us what changes to make. Since we are coding inside lollms, let's ask the expert to put it all together for us.

Now, let's execute the code again.

As we can see, the code works, and the snake and the food are now aligned. Great job, Little AI!

I am definitely not good at it, the game is too fast for me. No worries, let's ask Python specialist to slow it down.

There we go, that's much better!
As you can see, the game is playable and enjoyable, allowing you to chase food endlessly. However, to add more excitement and challenge to the game, I decided to introduce fire walls. These walls will serve as obstacles that the snake must avoid. If the snake touches any of these fire walls, it will result in an instant game over.

The Python specialist provided some suggestions for modifying the game, but I realized that I need to provide further clarification.  We can see that It did add a wall, but didn't cover the whole boundaries.  Also, it looks like if you touch the walls you die and the game ends. I want the game to have a lives system. The player should start with 3 lives, and if the snake touches a fire wall, it will lose one life. Once the player loses all three lives, the game will end.

I asked Python specialist to write the complete code incorporating these changes. However, due to the limited context size of the AI, it may stop in the middle of the text. Not to worry though, as Lollms has a sliding context feature. Simply press the continue button, and the AI will continue writing the code seamlessly.

After executing the code, I noticed a couple of issues. Firstly, the fire walls were too thick, making it difficult for the snake to navigate through them. Additionally, sometimes the food was generated inside the walls, rendering it impossible for the snake to reach. I asked the AI to fix these problems.

Upon execution, I encountered a simple indentation error, which I manually corrected.

Now, the game runs as expected with the fire walls properly aligned along the boundaries. I also verified that if the player dies three times, the game ends.

However, there was one more issue to address. The score and the remaining lives were not displayed during gameplay. I asked the Python specialist to modify the code to include these information. 

During the execution, I encountered another error where the AI tried to load a PNG file to represent hearts. I requested the AI to use ASCII characters instead.

I had to change the ASCII hearts written by the AI with just the letter H to avoid all encoding problems

After executing the modified code, we can see that the game now displays the score and remaining lives exactly as we requested.

To improve the visual appeal, I made a minor adjustment to the positioning of the text.

And there you have it! A fully functional snake game built entirely by conversing in plain English with the Python expert personality on Lollms. The game can be executed directly within the platform.

To give the game a name that reflects its AI-generated nature, the AI proposed "Lollms' GPT3.5-turbo Snake Game." 

To make the game accessible to a wider audience, we created a GitHub repository with the same name. You can find the repository link in the description. The game is open source, so feel free to play with it or make modifications.

I asked the AI to build a README.md text with badges and even a screen shot.

Once built we add it to github and we commit.

Finally, we create the source code file on github.

We can copy the code using the built in copy button.

And voilà, we have built a full game, documented it and shared it on github using lollms Python specialist personality.
This is just one  of 300 more personalities ready to be used for multiple applications.

Thank you for watching this tutorial, and we hope you found it interesting. Don't forget to like, share, subscribe, and leave a comment to support our channel!