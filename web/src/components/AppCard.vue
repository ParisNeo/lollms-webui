<template>
    <div class="app-card bg-white border rounded-xl shadow-lg p-6 hover:shadow-xl transition duration-300 ease-in-out flex flex-col h-full">
      <div class="flex-grow">
        <div class="flex items-center mb-4">
          <img :src="app.icon" alt="App Icon" class="w-16 h-16 rounded-full border border-gray-300 mr-4" />
          <div>
            <h3 class="font-bold text-xl text-gray-800">{{ app.name }}</h3>
            <p class="text-sm text-gray-600">Author: {{ app.author }}</p>
            <p class="text-sm text-gray-600">Version: {{ app.version }}</p>
            <p class="text-sm text-gray-600">Category: {{ app.category }}</p>
            <p class="text-sm text-gray-600">Creation date: {{ formatDate(app.creation_date) }}</p>
            <p class="text-sm text-gray-600">Last update: {{ formatDate(app.last_update_date) }}</p>
            <p class="text-sm" :class="app.is_public ? 'text-green-600' : 'text-orange-600'">
              {{ app.is_public ? 'Public App' : 'Local App' }}
            </p>
          </div>
        </div>
        
        <div class="mb-4">
          <h4 class="font-semibold mb-1 text-gray-700">Description:</h4>
          <p class="text-sm text-gray-600 h-20 overflow-y-auto">{{ app.description }}</p>
        </div>
        
        <p class="text-sm text-gray-600 mb-2">AI Model: {{ app.model_name }}</p>
        
        <div v-if="app.disclaimer && app.disclaimer.trim() !== ''" class="mb-4">
          <h4 class="font-semibold mb-1 text-gray-700">Disclaimer:</h4>
          <p class="text-xs text-gray-500 italic h-16 overflow-y-auto">{{ app.disclaimer }}</p>
        </div>
      </div>
      
      <div class="mt-auto pt-4 border-t">
        <div class="flex justify-between items-center flex-wrap">
          <button @click.stop="$emit('toggle-favorite', app.uid)" class="text-yellow-500 hover:text-yellow-600 transition duration-300 ease-in-out" :title="isFavorite ? 'Remove from favorites' : 'Add to favorites'">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" :fill="isFavorite ? 'currentColor' : 'none'" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
            </svg>
          </button>
          <button v-if="app.installed" @click.stop="$emit('uninstall', app.folder_name)" class="text-red-500 hover:text-red-600 transition duration-300 ease-in-out" title="Uninstall">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </button>
          <button v-else-if="app.existsInFolder" @click.stop="$emit('delete', app.name)" class="text-yellow-500 hover:text-yellow-600 transition duration-300 ease-in-out" title="Delete">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </button>
          <button v-else @click.stop="$emit('install', app.folder_name)" class="text-blue-500 hover:text-blue-600 transition duration-300 ease-in-out" title="Install">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
          </button>
          <button v-if="app.installed" @click.stop="$emit('edit', app)" class="text-purple-500 hover:text-purple-600 transition duration-300 ease-in-out" title="Edit">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
          </button>
          <button @click.stop="$emit('download', app.folder_name)" class="text-green-500 hover:text-green-600 transition duration-300 ease-in-out" title="Download">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
          </button>
          <button @click.stop="$emit('view', app)" class="text-gray-500 hover:text-gray-600 transition duration-300 ease-in-out" title="View">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
            </svg>
          </button>
          <button v-if="app.installed" @click.stop="$emit('open', app)" class="text-indigo-500 hover:text-indigo-600 transition duration-300 ease-in-out" title="Open">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
            </svg>
          </button>
          <button v-if="app.has_server && app.installed" @click.stop="$emit('start-server', app.folder_name)" class="text-teal-500 hover:text-teal-600 transition duration-300 ease-in-out" title="Start Server">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 12h14M12 5l7 7-7 7" />
            </svg>
          </button>
          <button v-if="app.has_update" @click.stop="$emit('install', app.folder_name)" class="relative text-yellow-500 hover:text-yellow-600 transition duration-300 ease-in-out animate-pulse" title="Update Available">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            <span class="absolute top-0 right-0 inline-flex items-center justify-center px-2 py-1 text-xs font-bold leading-none text-red-100 transform translate-x-1/2 -translate-y-1/2 bg-red-600 rounded-full">!</span>
          </button>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    name: 'AppCard',
    props: {
      app: {
        type: Object,
        required: true
      },
      isFavorite: {
        type: Boolean,
        default: false
      }
    },
    methods: {
      formatDate(dateString) {
        const options = { year: 'numeric', month: 'short', day: 'numeric' };
        return new Date(dateString).toLocaleDateString(undefined, options);
      }
    }
  }
  </script>
  
  <style scoped>
  /* Add any additional styles here */
  </style>
  