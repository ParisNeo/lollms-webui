Hi there. In this video, we are going to talk about the personalities and what you can do with them.

The LoLLMs webui uses my PyAIPersonality library under the hood. I have buit this library to create a standard way to define AI simulations and integrate the AI personality with other tools, applications and data. Before starting, I want to explain some concepts to make it easy for you to understand the inner workings of these tools. Let's dive right in.

Large Language Models (LLMs) are powerful text processing models based on machine learning techniques. As their name suggests, these models are characterized by their substantial size and versatility in handling various text-based tasks. In the context of this work, we focus specifically on text generation models.

To generate text, we first need a hardware layer, which is simply the physical machine running the code that executes the model. The hardware has at least a CPU and some memory to store the data while processing the text but can also have a GPU to accelerate some calculations.

On top of the hardware there is a software that is running the model. The model can be seen as a giant function with many parameters. chatGPT for example has around 175 billion parameters while a typical LLama based small model has around 7 billion parameters. There are also models with 13 Billion parameters, 30 billion parameters and 64 billion parameters.

To reduce the size of those model we use some optimization techniques like quantization and pruning.
Quantization reduces the precision of numerical values in a neural network to lower bit widths, improving computational efficiency and reducing memory usage.
Pruning removes unnecessary connections or weights from a neural network, making it sparser and reducing computational complexity, while often requiring fine-tuning to maintain performance.

Let's do a quick refresher to remind how the model works.

In the initial step of text processing, a sequence of text undergoes tokenization, which involves converting it from plain text into a series of integers that correspond to the text's position within a comprehensive vocabulary. As mentioned in a previous video, a token can represent individual letters, complete words, word combinations, or even parts of words, such as "automobile" being represented by two tokens: "auto" and "mobile." This intelligent approach efficiently represents text. On average, a token corresponds to approximately 0.7 words.

The model itself determines a distribution probability of the next token given the current state of the context. Basically, given the previous text. The distribution probability of the next token refers to the probability distribution over the vocabulary of possible tokens at a given step in a sequence generation task. It represents the model's estimation of the likelihood of each token being the correct or appropriate choice for the next position in the sequence.

During the training step, the model looks at chunks of text and tryes to update its weight to give a better prediction of the next token. It learns the statistical relationships between the input tokens list and the next token which leads to the ability to generate coherant text.


To illustrate this concept, let's consider an example. Suppose we start with the word "I." At this point, there are numerous possible next words that could follow. However, by leveraging the knowledge and patterns learned from extensive training on a vast corpus of text, we can rank these potential next words based on their likelihood in the given context.

For instance, if we determine that the most probable next word after "I" is "am," we update our context to "I am." As a result, the likelihood of "am" being repeated as the next word diminishes significantly, and other words like "happy" or "hungry" become more probable in this new context.

The dynamic nature of the likelihood distribution for the next tokens is a fundamental aspect of language modeling. As more context is provided, the distribution of probable next words undergoes constant adjustments. This adaptability is precisely what the training step aims to enhance. By leveraging advanced techniques like the attention mechanism, the model learns the intricate relationships between words and becomes better at predicting the next token with greater accuracy.

For a more comprehensive understanding of these mechanisms, I recommend referring to the "Attention is all you need" paper by Google, which delves into the details of the attention mechanism and its role in improving language modeling capabilities.

One may ask, if we always select the most likely next word, how are these model capable of generating different outputs from the same input?

As we discussed earlier, the language model determines the probability distribution of the next token. However, when it comes to selecting the next word, we rely on additional algorithms. While choosing the most likely word leads to a deterministic output, modern models employ various techniques such as sampling, top-k sampling, top-p (nucleus) sampling, and even apply repetition penalty to enhance the generated text.

Sampling introduces an element of randomness during token selection. It involves stochastically drawing a token from the probability distribution based on a temperature parameter. A higher temperature (e.g., 1.0) increases randomness, resulting in diverse outputs. Conversely, a lower temperature (e.g., 0.5) makes the distribution sharper, favoring more probable tokens and yielding more focused outputs.

Top-k sampling restricts the selection to the top-k most likely tokens, where k is a predefined value. Instead of considering the entire distribution, it narrows down the choices to a smaller set, maintaining a balance between randomness and coherence.

Top-p (nucleus) sampling, also known as "soft" or "weighted" sampling, takes into account a cumulative probability threshold, usually referred to as p. It selects from the smallest possible set of tokens whose cumulative probability exceeds p. This approach allows for dynamic selection of the token set, ensuring a varied yet controlled generation process.

Moreover, repetition penalty is a technique used to discourage repetitive outputs. It assigns lower probabilities to tokens that have been recently generated, reducing the likelihood of repetition and promoting more diverse and coherent text.

By combining these techniques, language models can generate text that exhibits controlled randomness, avoids repetitiveness, and strikes a balance between exploration and coherence.

Now that we have our next token, all we need to do is detokenize it and add it to our context.

In our text generation process, we repeat this procedure until we encounter either the model predicting an end-of-sentence (EOS) token or reaching the maximum number of allowed tokens, which we refer to as the "N predict" parameter in our tool.

This iterative approach ensures that the generated text remains within predefined length constraints and aligns with natural sentence boundaries. By incorporating the EOS token as a stopping criterion, we signify the completion of a coherent sentence or text snippet.

The "N predict" parameter in our tool enables users to control the generated text's length, avoiding excessive length or truncation while maintaining desired content and brevity.

Now you understand each one of the parameters that you can control in our UI. Let's take a look at these. First go to the settings tab and scroll down to model configuration section.

As you observe, the parameters we discussed are integral to our system. By default, these parameters are not customizable, as our personalized system ensures the appropriate configuration for each personality. We recognize that different personalities may require varying levels of creativity or determinism, and this responsibility lies with the personality settings.

However, we provide an override checkbox option that empowers you to modify and override the default personality settings, granting you the flexibility to adjust the parameters according to your specific needs and preferences. This checkbox serves as a means to deviate from the predefined settings, giving you greater control over the generated output.

Let's get back to our diagram. Now we have an AI that has the possibility to generate text sequentially based on its experience acquired during the training process. But how can this seamingly dump process lead to a tool that can solve complex tasks like generating stories and do some basic reasoning?!

At the heart of this process lies the simulation layer, a meta layer comprising the text itself. The ingenious trick is to leverage the power of text to condition subsequent generations, infusing them with contextual relevance. This is achieved through an initial text, known as the model conditioning, which establishes the foundation for the generation process and sets the plot.

By employing the model conditioning, we enable the generation process to align with specific contexts, facilitating coherent and tailored outputs. This dynamic approach harnesses the rich potential of text to shape subsequent generations, ultimately enhancing the overall quality and relevance of the generated content.


Allow me to provide you with an illustrative example. Suppose I present the model with a math question and instruct it to solve the problem. I would provide the math problem, followed by specific instructions such as "solve this problem," and then proceed to include the prefix, "solution:", before feeding the text to the AI.

The AI, leveraging its prior knowledge acquired during training and utilizing the given context, will determine the appropriate response. The generated answer is generally coherent, although it may occasionally contain errors or take the form of a disclaimer, such as "I am a machine learning program and cannot solve math problems." This outcome depends on the training process and the alignment phase of the model, which may influence the model's readiness or inclination to perform certain tasks.

While we won't delve into the intricacies of the alignment phase in this video, it is a crucial step that aligns the model to the specific task we desire it to perform. Through this alignment phase, the model can learn to recognize the scope and limitations of its abilities, leading to informed decisions regarding task completion.

By combining the context provided and the model's training, we can explore the model's capabilities in generating responses to math questions or other tasks, while being mindful of the alignment process that shapes its behavior and responses.

In PY AI Personalities library, the generation text is composed of a fixed Condutionning text, and an incremental discussion messages text. The discussion messages text in our application is in the form of a multi turns discussion. Each time we add a user prefix text such as, "### User:", followed by the user prompt, a link text (generally, a simple return to the line character), followed by the AI prefix, such as "### AI:". Then we feed this to the model that generates the AI text.

At the end, we add the messages to the previous messages text and we continue as the user interacts with the AI.

It's important to acknowledge that the AI has the potential to continue generating predictions for the rest of the discussion, including anticipating the user's future requests. This phenomenon is known as hallucination. To address this issue, we have implemented a hallucination suppression system designed to detect instances where the model predicts the user's next prompt and intervene to prevent it from persisting further.

By employing this suppression system, we aim to ensure that the AI remains within the desired boundaries and avoids venturing into speculative or inaccurate territory. This protective mechanism helps maintain a more controlled and focused conversation, preventing the AI from generating misleading or unrelated information based on its own projections.

The implementation of the hallucination suppression system enables a more reliable and coherent interaction, allowing users to have meaningful and productive exchanges with the AI while mitigating the risks associated with unfettered generation.

Finally, the personality system is a structure that allows the definition of all the parameters of the AI agent you are talking too: The conditioning text, the user prefix text, the link text, the ai prefix text, the antiprompts text used by the hallucination suppression system as well as all the generation parameters that control the model.

All of this is stored inside a yaml file called config.yaml stored in the personality folder. Notice that we also ahev extra folders, such as assets folder that contains the personality logo and will eventually be used to store more assets such as personality voice or personality 3D character that can be used for a future meta integration of language models.


We also have a scripts folder where we can put custom code to execute instead of following the default generation workflow that we have shown at the beginning of this video. 


Let's take a closer look at the GPT for art personality and its structure. It's a bit more complex because it's not just about answering prompts—it has its own customized workflow.

In the assets folder, you'll find the personality's cool logo, which it actually generated itself.

Now, in the scripts folder, there are two files. The first one is install.py, which runs when you select the personality for the first time. This file handles all the custom installation steps. For example, in this case, it installs extra libraries, downloads the stable diffusion project, and gets a diffusion model to work with. We keep a list of those extra libraries in requirements.txt. Once everything's installed, you're good to go with this personality.

The second file, processor.py, is where the personality's magic happens. It's got a class called Processor that inherits from PAPScript and does some important stuff. The star of the show is the run_workflow method. It takes the current prompt, the accumulated messages so far, and a callback function that's triggered at each step of the workflow.

In this art personality, we've set it up to generate an image description based on the user's prompt. Then it uses the stable diffusion generator to bring that description to life as an actual image. Finally, it prepares and sends the image as a cool markdown text to the UI.

Alright, let's get started with this cool personality! First, open up the UI and head over to the settings tab. Now, look for the section called "Personalities Zoo." It's where all the personalities are organized by language and category.

By default, the personality is set to "GPT for All," but we're going to change that. Find the "Art" category, and within it, select the "GPT for Art" personality. Give it a moment to sink in.

Now, this is important—click on "Apply Changes" to make sure the new settings take effect. Since this is the first time we're running this personality, it might take a bit longer. It needs to install some stuff, like the stable diffusion system and the model itself. So, just hang tight and be patient while everything gets set up.

Once the installation is complete, you'll be all set to explore the artistic wonders of this personality.

Just a heads up, if you decide to reboot the application now, all the updates to your settings will be lost. So, make sure you save those changes before you go ahead.


Alright, let's head back to the discussions tab and start a fresh discussion. This is where we can really put the tool to the test!

To challenge its creative abilities, let's ask it to imagine something cool without providing too much information. We want to see how it can come up with an image all on its own. Give it some freedom to work its magic and let's see what it creates.

Here is the output generated by our artbot. We can see the description of the artwork as well as the artwork itself.

Since this is a discussion, we can go on and ask for changes. For example let's ask it to change this to a day vew.

As we can see, the model did the requested changes. 


Keep in mind that this tool is still in its early stages of development, and there's plenty of room for improvement. One way to enhance its performance is by adjusting the default sampler to an Euler sampler, which can potentially yield even better results. Additionally, you have the flexibility to explore a wide range of models available on Hugging Face repositories. With thousands of models at your disposal, you can experiment and choose the one that aligns best with your specific needs and preferences. By making these adjustments, you can take this tool to new heights and unlock its full potential.

Please note that all the generated images bear a watermark with the LoLLMs signature, serving as a clear indication that they were created by AI using the stable diffusion WatermarkEncoder. This step is crucial to promote responsible AI usage and ensure that each generated work is properly identified as an AI creation.

It's important to emphasize that this tool is intended for appreciating art, fostering creative exploration, and sparking new ideas. It is not meant for malicious purposes or spreading misinformation. We firmly stand against such misuse.

By incorporating the watermark and setting these ethical guidelines, we aim to promote transparency and accountability in AI-generated content, while encouraging the responsible and respectful use of this tool. Let's embrace the power of AI to ignite imagination and appreciate the beauty of art in a responsible manner.

Now, let's dive into the structure of the personality folder once it's installed. Take a peek at what's inside, and you'll notice a couple of new files that have appeared.

First up, we have the .install file. It's a simple empty file that serves as a marker to indicate that the personality has been successfully installed. Whenever the personality is loaded, the install script checks for the presence of this file. If it's missing, the script knows that the personality needs to be installed again. So, if you ever remove this file, don't worry! The next time you use this personality, it will reinstall itself automatically.

Next on the list is the config_local.yaml file. This nifty little file holds all the local configuration settings. You have the power to customize various aspects such as the maximum size of the generated image description text. Just tinker with the settings to your liking. Additionally, you can specify the model you want to use. Simply download a stable diffusion model and place it in the project's root directory under "shared/sd_models." Then, reference the model's name in the config_local.yaml file. Cool, right?

Oh, and let's not forget! You can even set the number of images to generate for each prompt. Fancy playing around with multiple images? This is your chance. And if you want consistency, you can set a specific seed value for the sampling noise generation. A seed value of -1 means randomness, while any other value ensures that all generated images will be the same for each prompt.

Feel free to explore and make tweaks according to your preferences. It's your playground now!

Now, let's delve into another fascinating personality: the Tree of Thoughts personality. This particular personality has gained quite a reputation and is highly sought after. Its main goal is to explore a technique for enhancing AI reasoning.

The Tree of Thoughts technique takes an innovative approach by breaking down an answer into multiple thoughts. Here's how it works: the AI generates a number of thoughts related to the question or prompt. Then, it evaluates and assesses these thoughts, ultimately selecting the best one. This chosen thought is then incorporated into the AI's previous context, prompting it to generate another thought. This iterative process repeats multiple times.

By the end of this dynamic thought generation process, the AI accumulates a collection of the best thoughts it has generated. These thoughts are then synthesized into a comprehensive summary, which is presented to the user as a result. It's a remarkable way to tackle complex subjects and generate creative solutions.

Now, let's put this Tree of Thoughts personality to the test with a challenging topic: finding solutions to the climate change problem. Brace yourself for an engaging and thought-provoking exploration of ideas and potential strategies.

Here is the final synthesis of the AI's thoughts. The text appears to be correct and coherent, aligning precisely with the number of thoughts we set in the configuration. It's important to note that this response is the result of a thorough tree search process, which takes more time compared to a simple response. However, this technique allows for a more thoughtful and well-considered output, exceeding the expectations we might have had from the model alone.


If we observe the console, we can see that the personality initiated the process by posing a question to itself. It then generated three distinct thoughts and proceeded to select the most suitable one. Following this, it asked itself, "Given that I've chosen this initial thought, what would be the subsequent thought?" Generating three more thoughts, it once again selected the most optimal choice. This cycle repeated once more, resulting in a final selection of the best thought. Finally, the personality synthesized its ultimate conclusion by combining the top three thoughts derived from this thoughtful tree-based approach.

Just a quick reminder: the quality of the answers primarily relies on the model you're using. It's all about size here – the bigger the model, the better the results. In our case, we're using the Wizard LM 7B model, which has 7 billion parameters. But if you're looking for even more impressive outcomes, you can't go wrong with super-sized models like Open Assistant or chat GPT.

Now, let's dive into another crowd-favorite personality: GPT 4 Internet. This personality comes packed with an impressive feature – it can browse the internet to fetch answers for user questions. Whenever you ask a query, the AI cleverly sends a search request to an engine, retrieves the results, and crafts a response based on the information it finds. The best part? It even provides you with the sources it used, adding an extra layer of credibility to its answers. With this nifty functionality, you can trust that GPT 4 Internet has got your back when it comes to delivering well-informed responses.

Let's put GPT 4 Internet to the test with a current affairs question: Who is the newly appointed CEO of Twitter? By leveraging its internet-searching capabilities, this personality will scour the web to find the most up-to-date information and promptly deliver the answer you seek.

As you can observe, the personality performed its intended function flawlessly. It intelligently crafted a well-tailored query, conducted the search seamlessly behind the scenes, and swiftly presented the desired information along with proper source attribution. This showcases the power of leveraging the internet to enhance the AI's capabilities and provide you with accurate and reliable answers.

Finally, to install the personalities, go to the root of your lollms webui application and open a terminal. Then type installation/add_personality.bat or add_personality.sh depending on your operating system. you'll be prompted to choose a language, then a category, and finally the personality you want to install. Once installed, your personality will apear in the zoo.

Alright, let's wrap up here to keep the video concise. With over 250 personalities to explore, we've only scratched the surface of what GPT 4 All has to offer. While not all personalities have been fully adapted to the new format, a majority of them are already functional and ready for testing.

Throughout this video, we've delved into the various layers of LLM-based chatbots, grasped the fundamentals of text generation, and gained insights into the essential parameters that govern the generation process. Additionally, we've discovered the intriguing concept of personalities, witnessing some of them in action.

I hope you found this video informative and engaging. If you enjoyed it, please show your support by liking, starring the project on GitHub, sharing, and subscribing to stay updated on future content. Producing this video was a labor of love, dedicating an entire weekend to its creation, and I sincerely hope it proves valuable to you.

Thank you for watching, and until next time!

See ya