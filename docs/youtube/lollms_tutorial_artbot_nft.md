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

To use artbot as a prompt generator, then use the advanced webui to perform more complex modifications, we can deactivate the paint option in artbot settings and start over. Now we can ask the AI to generate a prompt and then copy it and paste it in the stable diffusion web UI.

We can change the batch size to increase the number of generated images.


Now we can select a different model and regenerate using the same prompt.
As you can see, the output has changed significantly. In fact, here we are using specialized models that tend to force the style to a specific value. Some models are more generic but they tend to be less interesting compared to the special ones.
We can also notice that the quality of the output may vary significantly from model to model. So make sure you experiment with multiple models to get the best of your AI.

You can also use the Stable diffusion webui to do inpainting, image guidance using controlnet and so much more. You can find more tutorials on stable diffusion web UI on the internet as this video is only about Artbot parts.


Now that we know how to build interesting AI generated artworks, let's take a look at how to create an NFT for our artwork.
As I said earlier, NFTs, or Non-Fungible Tokens, are unique digital assets that are stored on the blockchain. Unlike cryptocurrencies such as Bitcoin or Ethereum, which are fungible and can be exchanged on a one-to-one basis, NFTs cannot be modified or replicated. They are one-of-a-kind and have their own distinct value.
Now, here's where it gets interesting. NFTs are governed by smart contracts, which are essentially sets of rules that dictate how these digital assets can be bought, sold, and traded. These contracts provide a level of security and trust, allowing NFTs to be traded even though they exist in a digital form that can be easily copied.

Unlike traditional assets like stocks or real estate, the value of an NFT is not solely determined by its scarcity or physical attributes. Instead, it's the underlying factors that contribute to its value. Here are a few key elements:

Authenticity: NFTs are unique and verifiable on the blockchain, ensuring their authenticity. This scarcity and proof of ownership can significantly increase their value.

Reputation: The reputation of the creator or artist behind an NFT plays a crucial role in determining its value. Established artists or well-known creators often command higher prices for their NFTs due to their track record and fan base.

Rarity: Just like in the physical world, rarity can drive up the value of an NFT. If there are only a limited number of copies or editions available, the demand for that particular NFT can increase its value.

Utility and Functionality: Some NFTs have additional utility or functionality beyond their visual appeal. For example, an NFT could grant access to exclusive content, virtual experiences, or even real-world perks. This added utility can enhance its value in the eyes of collectors and enthusiasts.

Market Demand: Ultimately, the value of an NFT is determined by the market. If there is high demand and competition for a particular NFT, its value can skyrocket. Factors such as current trends, popular themes, and cultural relevance can all influence market demand.

Now that we understand the vague idea about NFTs, here is how to generate one using opensea.

First, you need a crypto wallet as NFTs require what we call gas fee to generate and trade. On opensea, we use etherium as the cryptocurrency.

So you need to create a wallet then to link it to opensea.

When you load opensea, you can press login and sign with your current wallet. I use metamask, but there are multiple optiions out there.

To begin, you have two options: creating a single NFT or dropping a collection. Let's take a closer look at each one.
Option 1: Create a Single NFT
If you have a specific piece of digital art, music, or any other digital asset that you want to turn into an NFT, this option is for you.
Option 2: Drop a Collection
If you have multiple pieces of digital content that you want to release as a collection, this option is perfect for you. Creating a collection allows you to showcase your work as a series or theme.

When creating an NFT or a collection, it's important to consider the gas fees associated with the blockchain you choose to use. Gas fees are transaction fees that are required to be paid in order to execute operations on the blockchain, such as minting an NFT.

If you choose to use a well-known blockchain like Ethereum, the gas fees tend to be higher. However, Ethereum is a stable and established blockchain with a strong track record. This means that your NFT will be secured on a reliable and widely recognized platform.

On the other hand, there are newer blockchains that offer lower gas fees. While this may be more cost-effective in the short term, there may be less certainty about the future of these blockchains. It's important to weigh the pros and cons and consider the trade-offs between cost and long-term stability when choosing a blockchain for your NFTs.

Ultimately, the choice of blockchain and the associated gas fees will depend on your specific needs and priorities as a creator or collector. Make sure to do your research and consider all factors before making a decision.

Now we are ready to personalize our collection before dropping it. The collection will be proposed for minting which means that collectors will mint one or many items from this collection and they won't be able to see which element they won until the grand reveal. 

Minting is the process of creating and issuing a new Non-Fungible Token (NFT) on the blockchain. It is similar to the concept of printing money, but in the digital realm. When you mint an NFT, you are essentially turning a digital asset, such as artwork, music, or collectibles, into a unique and verifiable token that can be bought, sold, and owned.

During the minting process, you provide the necessary details and metadata for your NFT, including its title, description, and any additional information that adds value or context to the asset. Once the minting process is complete, your NFT is assigned a unique identifier and becomes part of the blockchain, ensuring its authenticity and immutability.

Minting is a crucial step in the NFT creation process, as it establishes the ownership and provenance of the digital asset. It gives creators the ability to monetize their work, collectors the opportunity to own exclusive digital pieces, and the entire NFT ecosystem the foundation for secure and transparent transactions.

So, if you're ready to bring your digital creations to life and join the exciting world of NFTs, get ready to mint your very own tokens and unleash their potential!


Now let's get back to our collection. In the opensea collection editor, we can specify the collection name. You can provide a brief description, some tags and the block chain to drop the collection on. Here we choose art as tag and since we have already selected the etherium blockchain, we can't change that. You can also specify the payment token. Here I have set three token types that people can buy the NFTs with. You can also set the collection format and select collaborators if the collection was built by multiple artists.

Before publishing our artworks, we're going to add some descriptions to each one. Since we have 35 unique elements, we're gonna use our NFT reshaper personality on lollms to automatically build the entire metadata information set. You can find it in art category in lollms.


First set the path to the folder containing our collection in the personality settings.

Then type start and wait for the magic to happen.


The AI starts looking at the images one by one and builds the metadata file. You can look at the files individually and read their descriptions. It will add those descriptions to the csv file. These will be the files that you'll find in the collecvtion.

You can find some of the artworks we have generated during this video there but when we drop the collection for minting, the collectors can't know beforehand which artwork they are minting. All they can know is that the artwork is one of those I have shown here. I myself don't even know which artwork you can get. The real value is in the entire collection. Minting multiple artworks allows you to maximize your chance to have the art work you really like. 


If you didn't get the artwork you like, you can still buy it from another collector if they propose it for sale. But if an artwork was never minted, it will not be minted and so, no one will ever be able to buy it unless I put it in another collection.

You should only create NFTs of photos for which you have the legal rights and ownership. If you are the photographer or artist and hold the copyright to the image, or if you have explicit permission from the copyright holder, then you can proceed. Using someone else's copyrighted photo without permission is not only unethical but also illegal. Also, since NFT value is tightly linked to the original artist, it can't have the same value. It is like buying an artwork copy of mona lisa. That artwork would not have the same price than the real thing, because the owner is not the real artist.

Now Here are the 35 items in our collection.


Now, let's Add our images and the generated metadata to the collection then press upload. once uploaded we can press continue and wait for the data to be processed. This may take a long time so let's move on.

Once the importing is done, you can preview the items of the collection and see their description.  If you have done multiple uploads, sometimes the image descriptions get mingled. Don't worry, it is just a bug in their system that should be fixed. So try not to do multiple uploads to prevent this from happening.

Now in settings page, we select a limited edition and set the items number to 35 which means each one of our images will be unique. We can also set the start of the minting and we define the public mint stage. There we fix the price of each element, the minting duration, and per-wallet mint limit which should forbid the collection from being owned by a single entity. Let's deactivate that. You can also set a pre-reveal image and description so that the people who mint the items have some idea about the artworks shared.

Now we are ready to publish the drop. Press publish the drop and sign the transaction. Make sure you verify the fees on the block chain. For example, here the fees are very high. I advice you to wait till the fees are low enough before validating. You can literally have a factor of three between fees, so why the rush, just wait till you get a good low price.

After waiting for a while we started to have some reasonable prices. We can wait even more but I need to publish this video so I'll stick with the 18$ price so  that I can show you how. Now we sign and validate. This will remove an amount of etherium from my wallet and perform the drop.

Congratulations folks, We successfully published our Artbot Steampunk collection. We can share it on social media if we want. Let's go to the collection and mint some items.

Here I'll mint two items from the collection and I'll leave the rest to you, if you are interested. You can pay in crypto or using a card. I'll just use my crypto wallet to buy the two items. As any transaction, there will be fees to the network here we pay the equivalent of 6$ for a total of 30$ purshace. You can wait to get better prices, but I'll just go along since my main objective is to show you how it works. For this collection, I did set a low price compared to the fees, but you can set any price you want. I want this collection to be collected so a lower price should help.

Once you have minted the items, they're yours, but they are not revealed yet until the last day of the drop or until I decide that I want to stop the minting duration because all items are already sold out. In this collection, I have set the duration to 15 days starting from november second.

You can see that I have already minted the colorful cyber bot and the colorful moustache steam bot. All the other items are still available as of now. You can list the items for sale with higher price or just keep them as collectables that you can show to your friends. These are like pokémon card or baseball cards. They may become more valuable in the future.

To list for sale, just select the item, and press List for sale. You can set multiple parameters. For example, you can set a fixed price, or sell to the highest bidder. You can set a sale duration and multiple other settings. Be aware that opensees charge fees for those transactions. Also, you can tip the original creator by offering up to 10% of the selling price. You can select a lower value if you want, but the creator earnings ensure that an NFT that suddenly becomes very pricy, can give back to its original creator in one way or another.

Once again, there is always the network gas fee. Here it is around 2.78$. I'm not selling this item, I'm just showing you, but if you want to sell, just sign the transaction and your item is on sail.

Be aware that transactions require fees. And we are on Etherium blokchain which has pretty high fees. The sale of the collection elements should compensate the price, the network fees and the opensea fees or it would be a loss especially that non minted items are out of the final collection. Here between all fees, I spent around 40$ to build the collection which is decent considering that we are on etherium blockchain. I could have spent less if I automated the minting process, but maybe some day I'll build a lollms personality that can optimize the transactions process to minimize fees.  

In this video, we have learned about Artbot and the different ways we can use it to build stunning artworks and evolve our ideas. We also learned about NFTs, how to build them, how to share them, and how to use NFT Reshaper to prepare the NFT metadata for us. We have also learned how to create and drop a collection and how to mint a collection, and sell our NFTs. 

The collection we have created in this video is available in the description, If you liked the video and think the items are valuable, you can mint them before the end of the mint time. If the items are minted by someone else, you will be able to buy them after that if their owners want to sell them but it will probably be more expensive than the initial price as they gain interest and value over time. Note that if no one buyes an Item it wil not be minted on the blockchain which means it is not tradable and no one will be able to own it.

Any way, If you liked this video, and don't want to buy NFTs, just leave a thumb up, subscribe to the channel for more videos about LoLLMs and its amazing tools and consider sharing the video with people. That helps alot.

This video took me more than a week to make. You can tell by the advancement of lollms ui over the course of the week. It is a long process even with the help of AI, as I am building the tool while making the videos. I hope you liked this.

Thanks for watching. 
See ya