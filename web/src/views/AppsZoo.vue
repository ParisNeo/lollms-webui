<template>
  <div class="app-zoo w-full p-6 overflow-y-auto scrollbar-thin scrollbar-track-bg-light-tone scrollbar-thumb-bg-light-tone-panel hover:scrollbar-thumb-primary dark:scrollbar-track-bg-dark-tone dark:scrollbar-thumb-bg-dark-tone-panel dark:hover:scrollbar-thumb-primary active:scrollbar-thumb-secondary">
    <nav class="bg-white shadow-lg rounded-lg p-4 max-w-4xl mx-auto">
      <div class="flex flex-wrap items-center justify-between gap-4">
        <div class="flex items-center space-x-4">
          <button 
            @click="fetchGithubApps" 
            class="btn btn-primary"
            aria-label="Refresh apps from GitHub"
          >
            <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
            </svg>
            Refresh
          </button>
          
          <button 
            @click="openAppsFolder" 
            class="btn btn-secondary"
            aria-label="Open apps folder"
          >
            <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 19a2 2 0 01-2-2V7a2 2 0 012-2h4l2 2h4a2 2 0 012 2v1M5 19h14a2 2 0 002-2v-5a2 2 0 00-2-2H9a2 2 0 00-2 2v5a2 2 0 01-2 2z"></path>
            </svg>
            Open Folder
          </button>
        </div>
        
        <div class="relative flex-grow max-w-md">
          <input 
            v-model="searchQuery" 
            placeholder="Search apps..." 
            class="w-full border-b-2 border-gray-300 px-4 py-2 pl-10 focus:outline-none focus:border-blue-500 transition duration-300 ease-in-out"
            aria-label="Search apps"
          >
          <svg class="w-5 h-5 text-gray-400 absolute left-3 top-1/2 transform -translate-y-1/2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
          </svg>
        </div>
      </div>
    </nav>    
    <div v-if="loading" class="flex justify-center items-center space-x-2 my-8" aria-live="polite">
      <div class="animate-spin rounded-full h-10 w-10 border-t-2 border-b-2 border-blue-500"></div>
      <span class="text-xl text-gray-700 font-semibold">Loading...</span>
    </div>    
    <div v-for="category in categories" :key="category" class="mb-12">
      <h2 class="text-3xl font-bold mb-6 text-gray-800">{{ category }}</h2>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        <div
          v-for="app in filteredApps.filter(a => a.category === category)"
          :key="app.uid"
          class="app-card bg-white border rounded-xl shadow-lg p-6 hover:shadow-xl transition duration-300 ease-in-out flex flex-col h-full"
        >
          <div class="flex-grow">
            <div class="flex items-center mb-4">
              <img :src="app.icon" alt="App Icon" class="w-16 h-16 rounded-full border border-gray-300 mr-4" />
              <div>
                <h3 class="font-bold text-xl text-gray-800">{{ app.name }}</h3>
                <p class="text-sm text-gray-600">Author: {{ app.author }}</p>
                <p class="text-sm text-gray-600">Version: {{ app.version }}</p>
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
            <div class="flex justify-between">
              <button v-if="app.installed" @click="uninstallApp(app.folder_name)" class="text-red-500 hover:text-red-600 transition duration-300 ease-in-out" title="Uninstall">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
              <button v-else-if="app.existsInFolder" @click="deleteApp(app.name)" class="text-yellow-500 hover:text-yellow-600 transition duration-300 ease-in-out" title="Delete">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
              <button v-else @click="installApp(app.folder_name)" class="text-blue-500 hover:text-blue-600 transition duration-300 ease-in-out" title="Install">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                </svg>
              </button>
              <button v-if="app.installed" @click="editApp(app)" class="text-purple-500 hover:text-purple-600 transition duration-300 ease-in-out" title="Edit">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
              </button>
              <button @click="downloadApp(app.name)" class="text-green-500 hover:text-green-600 transition duration-300 ease-in-out" title="Download">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                </svg>
              </button>
              <button @click="handleAppClick(app)" class="text-gray-500 hover:text-gray-600 transition duration-300 ease-in-out" title="View">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
              </button>
              <button @click="openApp(app)" class="text-indigo-500 hover:text-indigo-600 transition duration-300 ease-in-out" title="Open">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="selectedApp" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 w-11/12 h-5/6 flex flex-col">
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-2xl font-bold">{{ selectedApp.name }}</h2>
          <button @click="backToZoo" class="bg-gray-300 hover:bg-gray-400 px-4 py-2 rounded-lg transition duration-300 ease-in-out">Close</button>
        </div>
        <iframe v-if="appCode" :srcdoc="appCode" class="flex-grow border-none"></iframe>
        <p v-else class="text-center text-red-500">Please install this app to view its code.</p>
      </div>
    </div>

    <div v-if="message" class="fixed bottom-4 right-4 px-6 py-3 rounded-lg shadow-md" :class="{ 'bg-green-100 text-green-800': successMessage, 'bg-red-100 text-red-800': !successMessage }">
      {{ message }}
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      apps: [],
      githubApps: [],
      selectedApp: null,
      appCode: '',
      loading: false,
      message: '',
      successMessage: true,
      searchQuery: '',
    };
  },
  computed: {
    combinedApps() {
      const installedAppNames = this.apps.map(app => app.name);
      const localAppsMap = new Map(this.apps.map(app => [app.name, { ...app, installed: true, existsInFolder: true }]));
      
      this.githubApps.forEach(app => {
        if (!localAppsMap.has(app.name)) {
          localAppsMap.set(app.name, { ...app, installed: false, existsInFolder: false });
        }
      });

      return Array.from(localAppsMap.values());
    },
    filteredApps() {
      return this.combinedApps.filter(app => 
        app.name.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
        app.description.toLowerCase().includes(this.searchQuery.toLowerCase())
      );
    },
    categories() {
      return [...new Set(this.combinedApps.map(app => app.category))];
    }
  },
  methods: {
    async fetchApps() {
      this.loading = true;
      try {
        const response = await axios.get('/apps');
        this.apps = response.data;
        this.showMessage('Refresh successful!', true);
      } catch (error) {
        this.showMessage('Failed to refresh apps.', false);
      } finally {
        this.loading = false;
      }
    },    
    async openAppsFolder() {
      this.loading = true;
      try {
        console.log("opening apps folder")
        const response = await axios.post(`/show_apps_folder`, {
          client_id: this.$store.state.client_id
        });
      } catch (error) {
        this.showMessage('Failed to open apps folder.', false);
      } finally {
        this.loading = false;
      }
    },
    async fetchGithubApps() {
      this.loading = true;
      try {
        const response = await axios.get('/github/apps');
        this.githubApps = response.data.apps;
        await this.fetchApps();
      } catch (error) {
        this.showMessage('Failed to refresh GitHub apps.', false);
      } finally {
        this.loading = false;
      }
    },
    async handleAppClick(app) {
      if (app.installed) {
        this.selectedApp = app;
        const response = await axios.get(`/apps/${app.folder_name}/index.html`);
        this.appCode = response.data;
      } else {
        this.showMessage(`Please install ${app.folder_name} to view its code.`, false);
      }
    },
    backToZoo() {
      this.selectedApp = null;
      this.appCode = '';
    },
    async installApp(appName) {
      this.loading = true;
      try {
        await axios.post(`/install/${appName}`, {
          client_id: this.$store.state.client_id,
        });
        this.showMessage('Installation succeeded!', true);
      } catch (error) {
        this.showMessage('Installation failed.', false);
      } finally {
        this.loading = false;
        this.fetchApps();
        this.fetchGithubApps();
      }
    },
    async uninstallApp(appName) {
      this.loading = true;
      try {
        await axios.post(`/uninstall/${appName}`, {
          client_id: this.$store.state.client_id,
        });
        this.showMessage('Uninstallation succeeded!', true);
      } catch (error) {
        this.showMessage('Uninstallation failed.', false);
      } finally {
        this.loading = false;
        this.fetchApps();
      }
    },
    async deleteApp(appName) {
      this.loading = true;
      try {
        await axios.post(`/delete/${appName}`, {
          client_id: this.$store.state.client_id,
        });
        this.showMessage('Deletion succeeded!', true);
      } catch (error) {
        this.showMessage('Deletion failed.', false);
      } finally {
        this.loading = false;
        this.fetchApps();
      }
    },
    async editApp(app) {
      this.loading = true;
      try {
        const response = await axios.post('/open_app_in_vscode', {
          client_id: this.$store.state.client_id,
          app_name: app.folder_name,
        });
        this.showMessage(response.data.message, true);
      } catch (error) {
        this.showMessage('Failed to open folder in VSCode.', false);
      } finally {
        this.loading = false;
      }
    },
    async downloadApp(appName) {
      try {
        const response = await axios.get(`/download/${appName}`, {
          responseType: 'blob',
        });
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', `${appName}.zip`);
        document.body.appendChild(link);
        link.click();
        link.remove();
        this.showMessage('Download started!', true);
      } catch (error) {
        this.showMessage('Download failed.', false);
      }
    },
    openApp(app) {
      if (app.installed) {
        window.open(`/apps/${app.folder_name}/index.html?client_id=${this.$store.state.client_id}`, '_blank');
      } else {
        this.showMessage(`Please install ${app.name} before opening.`, false);
      }
    },
    showMessage(msg, success) {
      this.message = msg;
      this.successMessage = success;
      setTimeout(() => {
        this.message = '';
      }, 3000);
    }
  },
  mounted() {
    this.fetchGithubApps();
  },
};
</script>

<style scoped>
.app-card {
  transition: all 0.3s ease;
}

.app-card:hover {
  transform: translateY(-5px);
}

button {
  transition: all 0.3s ease;
}

button:hover {
  transform: translateY(-2px);
}

.scrollbar-thin::-webkit-scrollbar {
  width: 6px;
}

.scrollbar-thin::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.scrollbar-thin::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 3px;
}

.scrollbar-thin::-webkit-scrollbar-thumb:hover {
  background: #555;
}
.btn {
  font-weight: 600;
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  transition: all 0.3s ease-in-out;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
  display: flex;
  align-items: center;
}
.btn-primary {
  background-color: #3b82f6;
  color: white;
}
.btn-primary:hover {
  background-color: #2563eb;
}
.btn-primary:focus {
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.5);
}
.btn-secondary {
  background-color: #e5e7eb;
  color: #374151;
}
.btn-secondary:hover {
  background-color: #d1d5db;
}
.btn-secondary:focus {
  box-shadow: 0 0 0 3px rgba(107, 114, 128, 0.5);
}
.search-input {
  width: 100%;
  border-bottom: 2px solid #e5e7eb;
  padding: 0.5rem 1rem 0.5rem 2.5rem;
  transition: border-color 0.3s ease-in-out;
}
.search-input:focus {
  outline: none;
  border-color: #3b82f6;
}
</style>