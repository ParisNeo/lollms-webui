# GPT4ALL-UI Web interface VUE3

## Todo's

- Fix discussion list width so that it stays static and dont resize depending on message contents [DONE]
- Add chat input field [DONE]
- Add ability to select multiple discussions to export or delete
- Add modal to ask user if you sure about to delete
- Add toast messages for errors and successes
- Populate settings with settings controls [WIP]
- Make search filter work [DONE]
- Add clear filter button to search input field [DONE]
- Add DB switcher (im thinking in the settings view)
- Make the UI work good on mobile
- Scroll to bottom
- Scroll to top
- Need to fix colors for `<input />` fields

## Dependencies for development

You mus have [Node.js](https://nodejs.org/en) installed on your computer. 

```
git clone repo_URL
cd into-this-repo-dir
npm install
```

After that to run development server locally and test the web page at http://localhost:5173/:

```
npm run dev
```

To connect to GPT4ALL-UI API server you need to enter its URL in the `.env` or make a copy of `.env` file and name it `.env.local`. This .env.local is added to `.gitignore`. 
All http requests made to GPT4ALL-UI api has to have /api/ prefix. This prefix gets rewritten in the vite.config.js file.
Make changes to your usecase in the `.env.local` file.

Once UI id done you can build static files for serving.
```
npm run build
```

This will create /dist/ folder with all the files. Also the build will show you if there are errors or not in your vue code.
> Make sure you test the static files too, because sometimes the builder dont catch all the errors, and if a component is not refernced it might not load in the built version, but it loads fine in development environment
### Overview of used dependencies and development

- Nodejs
- vue
- feather-icons
- axios

```
npm init vue@latest
```
```
cd gpt4all-ui-vue
npm install
npm run format
npm install axios dotenv
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
npm install feather-icons --save
```

### Running dev environment and building commands

To lint: (not very used)
```
npm run lint
```

To run test:
```
npm run dev
```

To build static files
```
npm run build
```
