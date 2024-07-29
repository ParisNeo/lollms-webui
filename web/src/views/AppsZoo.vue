<template>
  <div class="app-zoo w-full p-4 overflow-y-auto scrollbar-thin scrollbar-track-bg-light-tone scrollbar-thumb-bg-light-tone-panel hover:scrollbar-thumb-primary dark:scrollbar-track-bg-dark-tone dark:scrollbar-thumb-bg-dark-tone-panel dark:hover:scrollbar-thumb-primary active:scrollbar-thumb-secondary">
    <div class="mb-6 flex flex-wrap justify-between items-center gap-4">
      <button 
        @click="fetchGithubApps" 
        class="bg-green-500 hover:bg-green-600 focus:ring-2 focus:ring-green-300 text-white font-semibold px-6 py-2 rounded-lg transition duration-300 ease-in-out shadow-md"
        aria-label="Refresh apps from GitHub"
      >
        <span class="flex items-center">
          <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
          </svg>
          Refresh apps
        </span>
      </button>
      
      <button 
        @click="openAppsFolder" 
        class="bg-blue-500 hover:bg-blue-600 focus:ring-2 focus:ring-blue-300 text-white font-semibold px-6 py-2 rounded-lg transition duration-300 ease-in-out shadow-md"
        aria-label="Open apps folder"
      >
        <span class="flex items-center">
          <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 19a2 2 0 01-2-2V7a2 2 0 012-2h4l2 2h4a2 2 0 012 2v1M5 19h14a2 2 0 002-2v-5a2 2 0 00-2-2H9a2 2 0 00-2 2v5a2 2 0 01-2 2z"></path>
          </svg>
          Open applications folder
        </span>
      </button>
      
      <div class="relative flex-grow max-w-md">
        <input 
          v-model="searchQuery" 
          placeholder="Search apps..." 
          class="w-full border border-gray-300 rounded-lg px-4 py-2 pl-10 focus:outline-none focus:ring-2 focus:ring-blue-300 transition duration-300 ease-in-out"
          aria-label="Search apps"
        >
        <svg class="w-5 h-5 text-gray-400 absolute left-3 top-1/2 transform -translate-y-1/2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
        </svg>
      </div>
    </div>    
    <div v-if="loading" class="flex justify-center items-center space-x-2 my-8" aria-live="polite">
      <div class="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-blue-500"></div>
      <span class="text-xl text-gray-700 font-semibold">Loading...</span>
    </div>    
    <div v-for="category in categories" :key="category" class="mb-8">
      <h2 class="text-2xl font-bold mb-4">{{ category }}</h2>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div
          v-for="app in filteredApps.filter(a => a.category === category)"
          :key="app.uid"
          class="app-card bg-white border rounded-lg shadow-lg p-6 hover:shadow-xl transition w-full"
        >
          <div class="flex items-center mb-4">
            <img :src="app.icon" alt="App Icon" class="w-16 h-16 rounded-full border border-gray-300 mr-4" />
            <div>
              <h3 class="font-semibold text-lg">{{ app.name }}</h3>
              <p class="text-sm text-gray-600">Author: {{ app.author }}</p>
              <p class="text-sm text-gray-600">Version: {{ app.version }}</p>
            </div>
          </div>
          
          <div class="mb-4">
            <h4 class="font-semibold mb-1">Description:</h4>
            <p class="text-sm text-gray-600 h-20 overflow-y-auto">{{ app.description }}</p>
          </div>
          
          <p class="text-sm text-gray-600 mb-2">AI Model: {{ app.model_name }}</p>
          
          <div v-if="app.disclaimer && app.disclaimer.trim() !== ''" class="mb-4">
            <h4 class="font-semibold mb-1">Disclaimer:</h4>
            <p class="text-xs text-gray-500 italic h-16 overflow-y-auto">{{ app.disclaimer }}</p>
          </div>          
          <div class="flex flex-wrap gap-2">
            <button v-if="app.installed" @click="uninstallApp(app.name)" class="bg-red-500 hover:bg-red-600 text-white px-2 py-1 rounded text-sm">
              Uninstall
            </button>
            <button v-else-if="app.existsInFolder" @click="deleteApp(app.name)" class="bg-yellow-500 hover:bg-yellow-600 text-white px-2 py-1 rounded text-sm">
              Delete
            </button>
            <button v-else @click="installApp(app.name)" class="bg-blue-500 hover:bg-blue-600 text-white px-2 py-1 rounded text-sm">
              Install
            </button>
            <button v-if="app.installed" @click="editApp(app)" class="bg-purple-500 hover:bg-purple-600 text-white px-2 py-1 rounded text-sm">
              Edit
            </button>
            <button @click="downloadApp(app.name)" class="bg-green-500 hover:bg-green-600 text-white px-2 py-1 rounded text-sm">
              Download
            </button>
            <button @click="handleAppClick(app)" class="bg-gray-500 hover:bg-gray-600 text-white px-2 py-1 rounded text-sm">
              View
            </button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="selectedApp" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 w-11/12 h-5/6 flex flex-col">
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-2xl font-bold">{{ selectedApp.name }}</h2>
          <button @click="backToZoo" class="bg-gray-300 hover:bg-gray-400 px-2 py-1 rounded">Close</button>
        </div>
        <iframe v-if="appCode" :srcdoc="appCode" class="flex-grow border-none"></iframe>
        <p v-else class="text-center text-red-500">Please install this app to view its code.</p>
      </div>
    </div>

    <div v-if="message" class="fixed bottom-4 right-4 px-4 py-2 rounded" :class="{ 'bg-green-100 text-green-800': successMessage, 'bg-red-100 text-red-800': !successMessage }">
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
        this.showMessage('Failed to refresh GitHub apps.', false);
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
        const response = await axios.post(`/apps/${app.folder_name}/code`, {
          client_id: this.$store.state.client_id,
        });
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
/* You can add any additional styles here if needed */
</style>