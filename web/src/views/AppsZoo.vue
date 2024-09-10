<template>
  <div class="app-zoo background-color w-full p-6 overflow-y-auto scrollbar-thin scrollbar-track-bg-light-tone scrollbar-thumb-bg-light-tone-panel hover:scrollbar-thumb-primary dark:scrollbar-track-bg-dark-tone dark:scrollbar-thumb-bg-dark-tone-panel dark:hover:scrollbar-thumb-primary active:scrollbar-thumb-secondary">
    <nav class="panels-color shadow-lg rounded-lg p-4 max-w-4xl mx-auto mb-50 pb-50">
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
          <input type="file" @change="onFileSelected" accept=".zip" ref="fileInput" style="display: none;">
          <button @click="triggerFileInput" :disabled="isUploading" class="btn-secondary text-green-500 hover:text-green-600 transition duration-300 ease-in-out" title="Upload App">
            {{ isUploading ? 'Uploading...' : 'Upload App' }}
          </button>
        </div>
        <p v-if="message">{{ message }}</p>
        <p v-if="error" class="error">{{ error }}</p>
        
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
        
        <div class="flex items-center space-x-4">
          <label for="category-select" class="font-semibold">Category:</label>
          <select 
            id="category-select" 
            v-model="selectedCategory" 
            class="border-2 border-gray-300 rounded-md px-2 py-1"
          >
            <option value="all">All Categories</option>
            <option v-for="category in categories" :key="category" :value="category">
              {{ category }}
            </option>
          </select>
        </div>
        <div class="flex items-center space-x-4">
          <label for="installed-only" class="font-semibold">
            <input 
              id="installed-only" 
              type="checkbox" 
              v-model="showOnlyInstalled"
              class="mr-2"
            >
            Show only installed apps
          </label>
        </div>        
        <div class="flex items-center space-x-4">
          <label for="sort-select" class="font-semibold">Sort by:</label>
          <select 
            id="sort-select" 
            v-model="sortBy" 
            class="border-2 border-gray-300 rounded-md px-2 py-1"
          >
            <option value="name">Name</option>
            <option value="author">Author</option>
            <option value="date">Creation Date</option>
            <option value="update">Last Update</option>
          </select>
          <button @click="toggleSortOrder" class="btn btn-secondary">
            {{ sortOrder === 'asc' ? '↑' : '↓' }}
          </button>
        </div>
      </div>
    </nav>  
    <div v-if="loading" class="flex justify-center items-center space-x-2 my-8" aria-live="polite">
      <div class="animate-spin rounded-full h-10 w-10 border-t-2 border-b-2 border-blue-500"></div>
      <span class="text-xl text-gray-700 font-semibold">Loading...</span>
    </div>
    <div v-else>
      <h2 class="text-2xl font-bold mb-4">Favorite Apps</h2>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mb-8">
        <app-card 
          v-for="app in favoriteApps" 
          :key="app.uid" 
          :app="app" 
          @toggle-favorite="toggleFavorite"
          @install="installApp"
          @uninstall="uninstallApp"
          @delete="deleteApp"
          @edit="editApp"
          @download="downloadApp"
          @view="handleAppClick"
          @open="openApp"
          @start-server="startServer"
        />
      </div>
      
      <h2 class="text-2xl font-bold mb-4">{{ currentCategoryName }} ({{ sortedAndFilteredApps.length }})</h2>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        <app-card 
          v-for="app in sortedAndFilteredApps" 
          :key="app.uid" 
          :app="app" 
          @toggle-favorite="toggleFavorite"
          @install="installApp"
          @uninstall="uninstallApp"
          @delete="deleteApp"
          @edit="editApp"
          @download="downloadApp"
          @view="handleAppClick"
          @open="openApp"
          @start-server="startServer"
        />

      </div>
    </div>

    <!-- App details modal -->
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

    <!-- Toast message -->
    <div v-if="message" class="fixed bottom-4 right-4 px-6 py-3 rounded-lg shadow-md" :class="{ 'bg-green-100 text-green-800': successMessage, 'bg-red-100 text-red-800': !successMessage }">
      {{ message }}
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import AppCard from '@/components/AppCard.vue'; // Create this component for individual app cards

export default {
  components: {
    AppCard,
  },
  data() {
    return {
      apps: [],
      githubApps: [],
      favorites: [],
      selectedCategory: 'all',
      selectedApp: null,
      appCode: '',
      loading: false,
      message: '',
      successMessage: true,
      searchQuery: '',
      selectedFile: null,
      isUploading: false,
      error: '',
      sortBy: 'update',
      sortOrder: 'desc',
      showOnlyInstalled: false,
    };
  },
  computed: {
    currentCategoryName() {
      return this.selectedCategory === 'all' ? 'All Apps': this.selectedCategory;
    },    
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
    categories() {
      return [...new Set(this.combinedApps.map(app => app.category))];
    },
    filteredApps() {
      return this.combinedApps.filter(app => {
        const matchesSearch = app.name.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
                              app.description.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
                              app.author.toLowerCase().includes(this.searchQuery.toLowerCase());
        const matchesCategory = this.selectedCategory === 'all' || app.category === this.selectedCategory;
        const matchesInstalled = !this.showOnlyInstalled || app.installed;
        return matchesSearch && matchesCategory && matchesInstalled;
      });
    },
    sortedAndFilteredApps() {
      return this.filteredApps.sort((a, b) => {
        let comparison = 0;
        switch (this.sortBy) {
          case 'name':
            comparison = a.name.localeCompare(b.name);
            break;
          case 'author':
            comparison = a.author.localeCompare(b.author);
            break;
          case 'date':
            comparison = new Date(a.creation_date) - new Date(b.creation_date);
            break;
          case 'update':
            comparison = new Date(a.last_update_date) - new Date(b.last_update_date);
            break;
        }
        return this.sortOrder === 'asc' ? comparison : -comparison;
      });
    },
    favoriteApps() {
      return this.combinedApps.filter(app => this.favorites.includes(app.uid));
    },
  },
  methods: {
    toggleSortOrder() {
      this.sortOrder = this.sortOrder === 'asc' ? 'desc' : 'asc';
    },
    toggleFavorite(appUid) {
      const index = this.favorites.indexOf(appUid);
      if (index === -1) {
        this.favorites.push(appUid);
      } else {
        this.favorites.splice(index, 1);
      }
      this.saveFavoritesToLocalStorage();
    },
    saveFavoritesToLocalStorage() {
      localStorage.setItem('appZooFavorites', JSON.stringify(this.favorites));
    },

    loadFavoritesFromLocalStorage() {
      const savedFavorites = localStorage.getItem('appZooFavorites');
      console.log("savedFavorites",savedFavorites)
      if (savedFavorites) {
        this.favorites = JSON.parse(savedFavorites);
      }
    },      
    startServer(appName) {
      const payload = {
        client_id: this.$store.state.client_id, // Assuming you have a clientId property in your component
        app_name: appName
      };

      this.$store.state.messageBox.showBlockingMessage("Loading server.\nThis may take some time the first time as some libraries need to be installed.")
      axios.post(`/apps/start_server`, payload)
        .then(response => {
          this.$store.state.messageBox.hideMessage()
          // Handle successful server start
          console.log('Server start initiated:', response.data.message);
          // You might want to show a notification to the user here
          this.$notify({
            type: 'success',
            title: 'Server Starting',
            text: response.data.message
          });
        })
        .catch(error => {
          this.$store.state.messageBox.hideMessage()
          // Handle error
          console.error('Error starting server:', error);
          // Show an error notification
          this.$notify({
            type: 'error',
            title: 'Server Start Failed',
            text: error.response?.data?.detail || 'An error occurred while starting the server'
          });
        });
    },
    triggerFileInput() {
      this.$refs.fileInput.click();
    },
    onFileSelected(event) {
      this.selectedFile = event.target.files[0];
      this.message = '';
      this.error = '';
      this.uploadApp();
    },
    async uploadApp() {
      if (!this.selectedFile) {
        this.error = 'Please select a file to upload.';
        return;
      }

      this.isUploading = true;
      this.message = '';
      this.error = '';

      const formData = new FormData();
      formData.append('file', this.selectedFile);
      formData.append('client_id', this.$store.state.client_id);

      try {
        const response = await axios.post('/upload_app', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        });

        this.message = response.data.message;
        this.$refs.fileInput.value = ''; // Reset file input
        this.selectedFile = null;
      } catch (error) {
        console.error('Error uploading app:', error);
        this.error = error.response?.data?.detail || 'Failed to upload the app. Please try again.';
      } finally {
        this.isUploading = false;
      }
    },    
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
      this.$store.state.messageBox.showBlockingMessage(`Installing app ${appName}`)

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
        this.$store.state.messageBox.hideMessage()
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
      this.isLoading = true;
      this.error = null;

      try {
        const response = await axios.post('/download_app', {
          client_id: this.$store.state.client_id,
          app_name: appName
        }, {
          responseType: 'arraybuffer'  // Important: request binary data
        });

        // Get the filename from the Content-Disposition header
        const contentDisposition = response.headers['content-disposition'];
        const filenameMatch = contentDisposition && contentDisposition.match(/filename="?(.+)"?/i);
        const filename = filenameMatch ? filenameMatch[1] : 'app.zip';

        // Create a Blob from the response data
        const blob = new Blob([response.data], { type: 'application/zip' });

        // Create a temporary URL for the Blob
        const url = window.URL.createObjectURL(blob);

        // Create a temporary anchor element and trigger the download
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();

        // Clean up
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);

      } catch (error) {
        console.error('Error downloading app:', error);
        this.error = 'Failed to download the app. Please try again.';
      } finally {
        this.isLoading = false;
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
    this.loadFavoritesFromLocalStorage();    
  },
};
</script>

