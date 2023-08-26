# lollms-webui Web interface VUE3 development log, todo's and more

## Installation for development

You must have [Node.js](https://nodejs.org/en) installed on your computer. 

```
cd  /web/
npm install
```
## Testing, running, debugging

After that to run development server locally and test the web page at http://localhost:5173/:

```
npm run dev
```

> Note
> To run the developmen environment you need to create copy of the `.env` file and name it either `.env.development` or if that dont work then `.env.dev`. Set `VITE_LoLLMs_API_BASEURL = /api/ ` in the `.env.development`. 
> Run your gpt binding by launching `webui.bat` or bash `webui.sh`.

## Building frontend - UI

```
npm run build
```

This will update `/dist/` folder with all the files. Also the build will show you if there are errors or not in your vue code.

> Note
> Make sure you test the built files too, because sometimes the builder dont catch all the errors, and if a component is not refernced it might not load in the built version, but it loads fine in development environment

# UI development log, todo's and more

Here we keep track of things to implement and stuff we need to do.
## Todo's

- Add ability to select multiple discussions to export [WIP]
- Add toast messages for errors and successes
- Add DB switcher (im thinking in the settings view)
- Make the UI work good on mobile
- Need to fix colors for `<input />` fields
- Create status bar for binding to display if something is generating on the binding
- Add ability for users to style the whole UI, either changing Hue or changing every color manually.
- Create a panel in the Settings tab to create new personalities
- Need to investigate performance of websocket when message is being streamed back to the UI
- On first launch of the UI force users to create "User" personality, to be used as "User" for any or all input messages.
- Add drag n drop files into messages, images gets parsed as images, ability to load images from messages from DB.
- Send files to binding - images, other files for parsing data.
- Ability to reorder Discussions, add tags, categories
- Export whole DB
- Reset whole DB
- Add text to speech to messages and chatbox
- Add indicator to messages when non-comercial model was used. 
- Ability to export messages that are for commercial use or open source model messages Only.
- Ability to hide non commercial model messages.
- Feature - bot council where you add multiple bots to discussion, give them a topic and maybe max message count or something and they ponder about the topic then summerize it all.
- Feature voice chat with bot and voice output from bot - whisper + bard?
- Feature under selected discussion show more options to select and add more bots, select model per discussion or per bot, tweak settings per bot or per model.
- Easy share personality via export to a file, then drag and drop on to the webui and youre done.

## Done

- Fix discussion list width so that it stays static and dont resize depending on message contents [DONE]
- Add chat input field [DONE]
- Make search filter work [DONE]
- Add clear filter button to search input field [DONE]
- Add modal to ask user if you sure about to delete [DONE but in different way]
- Fix up the discussion array to filter out the messages by type not by count. (conditionner and )[DONE]
- Add title of current discussion to page [DONE]
- Populate settings with settings controls [DONE]
- Connect Settings to binding, ability to save changes [DONE]
- Scroll to bottom [SCROLLBAR]
- Scroll to top [SCROLLBAR]
- Create stop generating button [DONE]
- Fix the generated message formatting - add line breaks, also for user input messages. [DONE]
- Maybe try to set the chatbox to float to the bottom (always on the bottom of the screen) [DONE]
- Need to fix when user inputs message it shows up in the discussion array and then add new message for bot that is typing. [DONE]
- Connect delete / export discussions to binding functions.[DONE]
- Need to fix when deleting multiple discussions to not loose loading animation for each discussion when list gets updated [DONE]
- Need to add loading feedback for when a new discussion is being created [DONE]
- Add ability to select multiple discussions to delete [DONE]