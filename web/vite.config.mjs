import { fileURLToPath, URL } from 'node:url'

import { defineConfig,loadEnv  } from 'vite'
import vue from '@vitejs/plugin-vue'


// https://vitejs.dev/config/
export default async ({ mode }) => {
  async function getFlaskServerURL() {
    try {
      console.log("Loading")
      const response = await fetch('/get_server_address'); // Replace with the actual endpoint on your Flask server
      const serverAddress = await response.text();
      if(serverAddress.includes('<') || !serverAddress.startsWith("http")){
        console.log(`Server address not found`)
        return process.env.VITE_LOLLMS_API
        
      }
      console.log(`Server address: ${serverAddress}`)
      return `${serverAddress}`; // Construct the full server address dynamically
    } catch (error) {
      // console.error('Error fetching server address:', error);
      // Handle error if necessary
      return process.env.VITE_LOLLMS_API
    }
  }
  let serverURL = undefined;
  try{
    serverURL = await getFlaskServerURL() 
    console.log(serverURL)
  }catch{
    serverURL = process.env.VITE_LOLLMS_API
    console.log(`Server address: ${serverAddress}`)
  }
  // Load app-level env vars to node-level env vars.
  process.env = {...process.env, ...loadEnv(mode, process.cwd())};
  
  return defineConfig({
      
  plugins: [
    vue()
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    proxy: {
      "/api/": {
        target:  serverURL,//process.env.VITE_LOLLMS_API,//process.env.VITE_LOLLMS_API,//getFlaskServerURL(),// process.env.VITE_LOLLMS_API,
        changeOrigin: process.env.VITE_LOLLMS_API_CHANGE_ORIGIN,
        secure: process.env.VITE_LOLLMS_API_SECURE,
        rewrite: (path) => path.replace(/^\/api/, ""),
      },
      // "/": {
      //    target: process.env.VITE_LOLLMS_API,
      //    changeOrigin: process.env.VITE_LOLLMS_API_CHANGE_ORIGIN,
      //    secure: process.env.VITE_LOLLMS_API_SECURE,
        
      // },

    },
  }
})}
