# UI development log, todo's and more

The new UI is build using Node.js VUE3 + Vite. It uses tailwindcss, feathericons, openfonts and flowbite-vue components.

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

