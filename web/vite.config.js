import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

require('dotenv').config()
require('dotenv').config({ path: `.env.local`, override: true });

// https://vitejs.dev/config/
export default defineConfig({
  
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
        target: process.env.VITE_GPT4ALL_API,
        changeOrigin: process.env.VITE_GPT4ALL_API_CHANGE_ORIGIN,
        secure: process.env.VITE_GPT4ALL_API_SECURE,
        rewrite: (path) => path.replace(/^\/api/, ""),
      },
    },
  },

})
