Hi there, fellow creators! Today, I have something incredibly exciting to share with you. Get ready to unleash your artistic side and dive into the world of artbot. In this video, I'll guide you through the process of creating mesmerizing and unique art using the artbot persona of lollmz, an incredible tool that will ignite your creativity.

But wait, there's more! We won't stop at just creating art. We'll take it a step further and explore the world of NFTs (non-fungible tokens). Now, I know what you're thinking, 'NFTs? That sounds complicated!' Don't worry, I've got your back. We'll focus primarily on the art generation aspect using artbot, as the process of making NFTs has already been covered extensively in other videos.

By the end of this video, you'll have a stunning collection of art pieces ready to be shared with the world. And guess what? We won't just keep it to ourselves. We'll take our art to the next level by posting it to opensea, a popular platform on the Ethereum blockchain dedicated to showcasing and trading NFTs.

But here's the exciting part - our art collection will be available for a limited period of time. So, make sure you stick around till the end to witness the grand drop on opensea. Trust me, you won't want to miss this!

So, whether you're an aspiring artist or a seasoned creator looking to explore the world of NFTs, this video is for you. Get ready to create, captivate, and conquer the art world with artbot and opensea. Let's make your artistic dreams a reality!


Before we dive into the exciting world of artbot, let's take a moment to understand the terms of use. Artbot is an incredible AI-powered tool that utilizes an LLM (Large Language Model) to generate positive and negative prompts, which are then fed to an image generation model. Additionally, artbot has the ability to view your images and convert them into text descriptions using Blip, allowing the LLM to comprehend them better. What's fascinating is that artbot can also engage in conversations with you, enabling you to build upon vague ideas and transform them into something truly beautiful and original.
Now, it's essential to be transparent about the collaborative nature of working with AI. When presenting your artwork created with artbot, it's crucial to explicitly acknowledge the collaboration with AI and not claim it as your own manual production. The purpose of these tools is to inspire and assist you in thinking creatively, ultimately enhancing your artistic abilities. Transparency is key, as flooding the world with AI-generated content can lead to unfair competition with individuals who dedicate time and care to manual work. Manual work should be valued and appreciated in its own right.
Therefore, let's be honest and focus on valuing the ideas behind the artwork. When someone purchases your NFT, they should be aware that it is AI-generated, and the added value comes from your initiative and collaboration with artbot. By doing so, we ensure that the true worth of manual work is recognized, and the creative potential of AI is utilized responsibly.
Now that we've set the stage, let's unleash our imagination and embark on an artistic journey with artbot. Get ready to witness the incredible possibilities and showcase your unique artistic vision to the world through NFTs on opensea!








To start,we assume you have already installed lollmz. If not, please refer to the previous video on my channel. In this video, we will show you how to use Artbot v2.0 on lollmz v6.7. Upgrades are constantly being added to the tool, so new features may come over time.

To begin, let's go to the settings tab. Under the personalities section, select the category "Art". Now you can find Artbot. To mount it, simply press the menu and select "Mount". Great! Artbot is now mounted and selected. Let's head back to the discussions tab and press the "+" button to start a new discussion.

First, let's take a look at the configurations that we can modify on this personality. To show the configuration page, just press the personality icon. As you can see, there are many configurations here. For example, you can choose the type of images to generate, ranging from artworks to photos and even game assets and icons.

Next, we can select the engine. Up until this version, we support stable diffusion via the modified version of automatic1111's tool. We also support Dali2 via the OpenAI API. Please note that if you want to use Dali2, you will need to supply an OpenAI key.

But that's not all! We have many other configurations available. For instance, you can activate or deactivate AI imagination block controlled by the active LLM model. You can also activate or deactivate the image generation, which can come in handy if you only want to generate the prompt and perform the generation using the stable diffusion web UI for tasks like inpainting or other complex operations. Additionally, you can use Midjourney or Dali3 (which we will support natively as soon as they release their API). There are also options to control the resolution, scaling, number of images to generate, and sampler.

With these configurations, you have the power to customize your art generation experience and create truly unique and mesmerizing pieces. So what are you waiting for? Let your imagination run wild and let Artbot bring your artistic visions to life!

In the next part of the video, we will learn how to generate an image using Artbot without utilizing the imagination module. To begin, simply deactivate the "imagine" option and enter your prompt. The system expects one or two lines of text. If you provide only one line, it will be considered as the positive prompt. If you provide a second line, it will be considered as the negative prompt, and the generation model will try to avoid its content.

In this example, we will test a simple prompt with a positive prompt and my recipe negative prompt. Once you press enter, the system will start generating the images. We will generate six images, so please wait for them to be built. Once they are ready, you can select the image you like the most and save it.

Here we're going to make some Steampunk style artworks. As you can see, the artworks are good as we did use the default negative prompt which enhances the generated images. It is important to learn how to prompt the AI in this imaginationless mode as you are the one who needs to do the imagination and the prompting.

Now let's try to test a steampunk illustration in continuous mode. To activate this mode, just go to the settings of artbot and select continue_from_last_image. This means that the prompts will induce updates to last picture instead of starting from scratch. We can also fix the image to image denoising strength. A bigger value yields more changes to the generated image, and a smaller value yields less changes.

For example, here we ask to make a steampunk artwork of a white haired girl. Here I have activated imagine mode, so I don't need to be very specific. The AI will take care of imagining all the details and building the positive prompt as well as the negative prompt. You can also activate the make title option so that the AI builds a title to the artwork. All we have to do is wait. 

As you can see, the AI generated an image of a steampunk girl with white hair. We can click the image to view it in the new full screen mode. Notice here that this video took days to make and now we are using artbot version 2.2 with the new UI that offers more options than before. You can see that we have lots of metadata that we can use and export.

To make consistant changes to the artwork, I advice you to copy the seed number and set it as the default seed for the subsequent generations. This ensures that the noise used in the diffusion model stays the same allowing for more similar generations. Make sure you get it back to -1 if you want more randomness.

Using the metadata of the image allows you to have the full set of configurations to allow you to reproduce it.

Now let's try to change the hair of thegirl to be red instead of white.

It looks like the hair wasn't that changed. You can feel a hue but it is not as red as we may want. The thing is that the denoising strength that we did set was not enough to get any significant changes. Let's change that.


Now instead of starting the imagination process which will probably change the prompt again, we can just use the regenerate with last prompt command from the artbot commands menu. 

As you can see, the hair is now red. But you can notice that the AI has added a new element which is the glasses. Well, those glasses were introduced because we used the imagination mode between the first and second generations which triggers a whole new imagination. We could have avoided this by simply disabling the imagination mode, copy the prompt generated by the AI and then paste it and change the color in the text.


Ok, now let's do the same and build an image of a steampunk male with long moustache.

Here we have set the number of images to generate to three. This is interesting if you want to choose between multiple alternatives and build from it.

In the new version of artbot, we have a copy button that will copy the positive and negative prompts allowing us to use it in manual mode. Let's copy the prompt and paste it in the chatbox input. Let's select the second image then we can modify the prompt content. For example we can emphesize an aspect of the image by adding multiple braces around it. Let's inphesize the colorful nature of the image.

Now before generating, let's deactivate the imagination mode.
Also, let's copy the seed value from the image we want to build next images from, and activate the continuous mode.


Now let's generate the image.

As you can see, the image is basically the same but we get a little more color in the background. 

We can press the Variate button to generate more images. Here we generate a single image, but you can set the number of variations to generate in the settings in order to produce more variations and choose from.


Here is the original image. And here is the modified image. Finally, here is the variant we have produced from the modified image. You can see that the rainbow is now different.


Now let's reactivate the imagination part and talk to the AI about our artwork. Here I remind you that Artbot can also discuss with you  the aspects of the artwork. Let's ask it for some ideas to make out artwork a little more original.

As you can see, the AI proposed a set of ideas to make the artwork more original. I like the idea about the mechanical wings. Let's add this element to the artwork.

Remember, when you are in imagination mode, you need to explicitly ask the AI to generate an artwork, an icon or whatever you like or it will consider your prompt for discussion. In fact, the AI reads your prompt then decides whether you are asking for a generation or if you are just asking a question or discussing about the artwork. 


Here we have our colorful wings. We can press variate button to get more variants.

Be careful not to keep a fixed seed or you will just have an exact copy to your previous image.
To set a random seed, just set it to -1.


Let's also increase the value of denoising strength to make more changes.

As we can see, we have a new different image but with the same elements. Make sure to change the number of generated images to a higher value so that you can choose from the variants generated at once instead of generating them one by one.

This time we can see that multiple images have been generated. We can view them and select the best one. We can go on and on until we finish building the artwork that satisfies our needs.

It is important to note that the quality of the output is tightly linked to the model you are using. It is a good idea to install a more stylized model finetuned for the kind of art you are trying to make. You can find multiple models on https://civitai.com/. Make sure you only download safetensors models as this format was designed to prevent from putting malicious code in the model. Other file types especially those based on python's pickle may present a security risk as they can embed malicious code inside. 

Download the model to your lollms personal folder / shared / auto_sd / models / stable-diffusion. You can install as many models as you wish and thage them from the advanced automatic1111's web UI.

Now to select our model, go back to lollms, and press the artbot contextual menu and select Show Stable diffusion UI. This is a modofied version of Automatic 1111 Stable diffusion webui where you can perform exactly the same operations. It is uptodate to their main branch and you can use it to perform advanced upgrades by disabling the paint functionality in artbot and use it as a prompt generation tool. Here we are going to use it to select the model. If you don't see the model yet, just press the refresh button on the right of the models list. All you have to do is wait and when it is ready, we can go back to lollms and do some variations.

As you can see, the style has completely changed. We can see the manga like aspect of the generated images. You can try playing around with all those combinations, mixing models, your imagination, artbot imagination and your sense of beauty in order to produce even better images.


You can also use the Stable diffusion webui to do inpainting, image guidance using controlnet and so much more. You can find more tutorials on stable diffusion web UI on the internet as this video is only about Artbot parts.


