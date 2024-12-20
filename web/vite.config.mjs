import { fileURLToPath, URL } from 'node:url'

import { defineConfig, loadEnv  } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'
// https://vitejs.dev/config/
export default async ({ mode }) => {
  // Load app-level env vars to node-level env vars.
  process.env = {...process.env, ...loadEnv(mode, process.cwd())};
  
  return defineConfig({
      
  plugins: [
    vue()
  ],
  optimizeDeps: {
    include: ['monaco-editor/esm/vs/editor/editor.main.js']
  },
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    proxy: {
      "/api/": {
        target: process.env.VITE_LOLLMS_API,//serverURL,
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
