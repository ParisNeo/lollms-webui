# GPT4ALL-UI Web interface VUE3 development log, todo's and more

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
> To run the developmen environment you need to create copy of the `.env` file and name it either `.env.development` or if that dont work then `.env.dev`. Set `VITE_GPT4ALL_API_BASEURL = /api/ ` in the `.env.development`. 
> Run your gpt backend by launching `webui.bat` or bash `webui.sh`.

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

- Add ability to select multiple discussions to export or delete [WIP]
- Add toast messages for errors and successes
- Populate settings with settings controls [WIP]
- Connect Settings to backend, ability to save changes
- Add DB switcher (im thinking in the settings view)
- Make the UI work good on mobile
- Scroll to bottom
- Scroll to top
- Need to fix colors for `<input />` fields
- Create status bar for backend to display if something is generating on the backend
- Create stop generating button
- Fix the generated message formatting - add line breaks, also for user input messages.
- Add ability for users to style the whole UI, either changing Hue or changing every color manually.
- Maybe try to set the chatbox to float to the bottom (always on the bottom of the screen)
- Create a panel in the Settings tab to create new personalities
- Need to fix when user inputs message it shows up in the discussion array and then add new message for bot that is typing.
- Need to investigate performance of websocket when message is being streamed back to the UI
- On first launch of the UI force users to create "User" personality, to be used as "User" for any or all input messages.
- Connect delete / export discussions to backend functions.
- Need to fix when deleting multiple discussions to not loose loading animation for each discussion when list gets updated
- Need to add loading feedback for when a new discussion is being created

## Done

- Fix discussion list width so that it stays static and dont resize depending on message contents [DONE]
- Add chat input field [DONE]
- Make search filter work [DONE]
- Add clear filter button to search input field [DONE]
- Add modal to ask user if you sure about to delete [DONE but in different way]
- Fix up the discussion array to filter out the messages by type not by count. (conditionner and )[DONE]
- Add title of current discussion to page [DONE]