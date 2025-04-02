Lollms Tutorial: Mastering Basic Usage

(Video Intro Music & Title Card)

Host: Hey everyone, and welcome back! In our previous video, we covered downloading and installing Lollms. Today, we're diving into how to actually use this powerful tool. We'll explore managing discussions, interacting with the AI in various ways, using advanced features like RAG and the Skills Library, and managing your chat messages. [1]Let's get started!

(Visual: Show the main Lollms interface)

Host: When you open Lollms, the first thing you'll notice is the interface, often featuring a light and dark mode option. [2]The main areas are the Discussions Panel on the left, and the main chat interaction area in the center.
[2][3]
Section 1: The Discussions Panel

(Visual: Focus zoom on the left panel)

Host: This left panel is your command center for managing conversations. Let's look at the toolbar at the top of this panel.

(Visual: Highlight the '+' icon)

Host: To start a new chat, simply click the Plus (+) icon. This creates a 'New discussion' entry in the list below, and you'll see a welcome message from the currently loaded AI personality in the main chat window.

(Visual: Highlight the 'check' icon, show checkboxes appearing next to discussion names)
[1]
Host: Need to manage multiple discussions? Click the Checkmark icon. This adds checkboxes next to each discussion. You can select individual chats, or use the 'Select All' toggle.
[1]
(Visual: With discussions selected, highlight Export options)

Host: Once you've selected discussions, you have options. [2][4][5]You can export them for backup or sharing. Lollms allows exporting as a JSON file (good for re-importing later), a Zip folder containing the data, or as Markdown files for easy reading.

(Visual: Show the search bar in the discussions panel)

Host: Looking for a specific chat? Use the search bar here to filter your discussions by name. Very handy when you have lots of conversations!

(Visual: Briefly point to the database name at the bottom of the panel)
[1]
Host: At the bottom, you see the name of your current discussion database. [1]Lollms stores discussions locally in a database file. [6]While you can manage multiple databases (switching, importing, deleting), we'll focus on managing discussions within a database today. You can import discussions from a previously exported JSON file using the import function in the toolbar.

Section 2: Interacting with the AI

(Visual: Shift focus to the main chat input area at the bottom)

Host: Now for the main event: talking to the AI. You type your prompts here, just like any chatbot.

(Visual: Highlight the 'Web Search' toggle/button near the input)

Host: Want the AI to access up-to-date information from the internet? Activate the 'Web Search' mode. Lollms will perform web searches based on your prompt to provide more current or contextually relevant answers. This is a form of Retrieval Augmented Generation, or RAG.
[7]
(Visual: Highlight the microphone icon)

Host: Prefer to talk? Click the microphone icon to use audio input. Speak your prompt, and Lollms will transcribe it. (Note: Audio output might also be available depending on configuration).

(Visual: Highlight the paperclip/attachment icon)

Host: Lollms excels at RAG using your own data. Click the attachment icon to send a file – like a PDF, text file, or document. The AI can then answer questions based on the content of that file. [8]This is incredibly useful for analyzing reports, summarizing documents, or getting specific information from your own materials.

(Visual: Highlight the webcam icon)

Host: You can even capture an image directly from your webcam to send to multimodal AI models if your selected personality supports it.

(Visual: Highlight a 'link' or similar icon, or demonstrate pasting a URL)

Host: Similar to file uploads, you can provide a web link. Lollms can fetch the content from that webpage and use it as context for its responses – another powerful RAG feature, great for summarizing articles or asking questions about specific online content. [Source 22 mentions pointing Lollms to a GitHub page as an example].

(Visual: Show the message input area, perhaps typing a prompt with Markdown)

Host: Want more control over your prompt's structure or need to include code? Lollms often supports Markdown formatting in the message input. You can use standard Markdown like backticks (`) for inline code, triple backticks (```) for code blocks, asterisks (*) for italics or bold (**), and hashes (#) for headings. This helps structure complex prompts clearly for the AI. [Sources 16, 21, 23, 24 confirm Markdown usage in chat interfaces].

(Visual: Show the 'Generate AI Response' button/feature, if visually distinct)

Host: Lollms also allows you to craft what looks like an AI response. [4]This is primarily useful for creating datasets for fine-tuning models, where you provide both the prompt and the desired answer.

(Visual: Demonstrate typing a specific instruction at the start of a prompt, e.g., "Start your answer with 'Based on the provided document...'")

Host: You can guide the AI's response style by giving it specific instructions. For instance, you can force it to start answering in a particular way to make it more aligned with your needs or the context.

Section 3: Managing Messages

(Visual: Hover over a user-sent message, show edit/copy icons)

Host: Made a typo or want to refine your prompt after sending? You can usually edit your own messages. You can also easily copy the content of any message – yours or the AI's – to your clipboard.

(Visual: Hover over an AI-generated message, show edit icon)

Host: Importantly, you can often edit the AI's response. This is another powerful feature for training or correction. If the AI makes a mistake or gives an answer you want to refine, you can directly modify its message content. This helps in creating accurate conversation logs or preparing data for fine-tuning. [Sources 3, 5, 6 mention editing AI messages].

(Visual: Highlight the thumbs-up/thumbs-down icons next to an AI message)

Host: Provide feedback on the AI's answers using the thumbs-up and thumbs-down icons. This feedback can sometimes be used by the model developers or for your own tracking of helpful responses. [Sources 2, 3, 5, 6, 19 confirm rating feature].

Section 4: The Skills Library (Long-Term Memory RAG)

(Visual: Go back to the Discussions Panel, highlight a specific discussion, show an 'Add to Skills Library' option)

Host: Lollms features a 'Skills Library', which acts as a long-term memory. [1][9]You can select a valuable discussion and add it to this library. Lollms processes the conversation, extracting key information and skills demonstrated. [1][Source 8 mentions Long-Term Memory acting as a skills library].

(Visual: Show a setting toggle related to 'Use Skills Library' or 'Activate RAG on Skills')

Host: To make the AI leverage this stored knowledge, you need to activate the Skills Library usage. [1]This enables RAG specifically on the content stored in your library. When you chat, the AI can then pull relevant information from past discussions you've saved, giving it a powerful memory and context that persists across new chats. [Source 8 implies RAG integration with this memory].

(Visual: Briefly show interaction where the AI might reference past 'learned' info)

Host: This allows the AI to build upon previous interactions and knowledge you've curated, making it progressively smarter and more helpful for your specific needs.

(Video Outro)

Host: And that covers the core usage of Lollms! We've looked at managing discussions, various ways to interact with the AI including web search, audio, and powerful RAG features using files and links, formatting prompts, managing messages, and leveraging the Skills Library for long-term memory.
[1]
Host: Lollms is incredibly versatile, so the best way to learn is to experiment. Try out different personalities, explore the settings, and see what you can create!

Host: If this tutorial was helpful, please give it a thumbs up, subscribe for more AI content, and let us know in the comments what you'd like to learn next! Thanks for watching!

(Outro Music & End Screen with links/subscribe button)