<template>
  <div class="app-zoo background-color w-full p-6 pt-12 min-h-screen overflow-y-auto text-blue-900 dark:text-blue-100">
    <!-- Navigation and Filters Bar -->
    <nav class="panels-color shadow-lg rounded-lg p-4 max-w-6xl mx-auto mb-8">
      <div class="flex flex-wrap items-center justify-between gap-4">
        <!-- Action Buttons -->
        <div class="flex items-center space-x-2 flex-wrap gap-2">
          <button
            @click="fetchGithubApps"
            class="btn btn-primary btn-sm"
            aria-label="Refresh apps from GitHub"
          >
            <i data-feather="refresh-cw" class="w-4 h-4 mr-1"></i>
            Refresh
          </button>

          <button
            @click="openAppsFolder"
            class="btn btn-secondary btn-sm"
            aria-label="Open apps folder"
          >
            <i data-feather="folder" class="w-4 h-4 mr-1"></i>
            Open Folder
          </button>

          <input type="file" @change="onFileSelected" accept=".zip" ref="fileInput" class="display-none">
          <button @click="triggerFileInput" :disabled="isUploading" class="btn btn-success btn-sm" title="Upload App">
            <i v-if="!isUploading" data-feather="upload" class="w-4 h-4 mr-1"></i>
            <span v-if="isUploading" class="animate-spin inline-block w-4 h-4 border-2 border-current border-t-transparent rounded-full mr-1" role="status" aria-hidden="true"></span>
            {{ isUploading ? 'Uploading...' : 'Upload App' }}
          </button>
        </div>

        <!-- Search Input -->
        <div class="relative flex-grow max-w-xs sm:max-w-sm md:max-w-md">
           <label for="app-search" class="sr-only">Search Apps</label>
           <div class="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
                <i data-feather="search" class="w-5 h-5 text-blue-400 dark:text-blue-500"></i>
           </div>
           <input
            id="app-search"
            v-model="searchQuery"
            placeholder="Search apps..."
            class="search-input w-full py-2 px-4 pl-10 text-sm"
            aria-label="Search apps"
           />
        </div>

        <!-- Filters and Sorting -->
        <div class="flex items-center space-x-4 flex-wrap gap-x-4 gap-y-2">
           <!-- Category Filter -->
            <div class="flex items-center space-x-2">
              <label for="category-select" class="label !mb-0">Category:</label> 
              <select
                id="category-select"
                v-model="selectedCategory"
                class="input input-sm py-1"
              >
                <option value="all">All Categories</option>
                <option v-for="category in categories" :key="category" :value="category">
                  {{ category }}
                </option>
              </select>
            </div>

            <!-- Installation Status Filters -->
            <div class="flex items-center space-x-3">
               <label for="installed-only" class="label !mb-0 flex items-center cursor-pointer">
                <input
                  id="installed-only"
                  type="checkbox"
                  v-model="showOnlyInstalled"
                  class="mr-1.5 h-4 w-4 rounded border-blue-300 dark:border-blue-600 text-blue-600 focus:ring-blue-500 dark:focus:ring-blue-400 dark:bg-blue-700 dark:text-blue-500"
                >
                Installed
              </label>
              <label for="uninstalled-only" class="label !mb-0 flex items-center cursor-pointer">
                <input
                  id="uninstalled-only"
                  type="checkbox"
                  v-model="showOnlyUnInstalled"
                  class="mr-1.5 h-4 w-4 rounded border-blue-300 dark:border-blue-600 text-blue-600 focus:ring-blue-500 dark:focus:ring-blue-400 dark:bg-blue-700 dark:text-blue-500"
                >
                Not Installed
              </label>
            </div>

            <!-- Sorting -->
            <div class="flex items-center space-x-2">
              <label for="sort-select" class="label !mb-0">Sort by:</label>
              <select
                id="sort-select"
                v-model="sortBy"
                class="input input-sm py-1" 
              >
                <option value="name">Name</option>
                <option value="author">Author</option>
                <option value="date">Creation Date</option>
                <option value="update">Last Update</option>
              </select>
              <button @click="toggleSortOrder" class="btn btn-secondary btn-sm" aria-label="Toggle sort order">
                <i v-if="sortOrder === 'asc'" data-feather="arrow-up" class="w-4 h-4"></i>
                <i v-else data-feather="arrow-down" class="w-4 h-4"></i>
              </button>
            </div>
        </div>
      </div>
    </nav>

    <!-- Loading Indicator -->
    <div v-if="loading" class="flex justify-center items-center space-x-2 my-12" aria-live="polite">
      <div class="animate-spin rounded-full h-10 w-10 border-t-2 border-b-2 border-blue-500 dark:border-blue-400"></div>
      <span class="text-xl text-loading font-semibold">Loading...</span> 
    </div>

    <!-- App Grids -->
    <div v-else class="pb-20">
       <!-- Favorite Apps Section -->
       <div v-if="favoriteApps.length > 0" class="mb-10">
        <h2 class="h2 text-2xl font-bold mb-4">Favorite Apps</h2> 
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          <app-card
            v-for="app in favoriteApps"
            :key="app.appName"
            :app="app"
            @toggle-favorite="toggleFavorite"
            @install="installApp"
            @uninstall="uninstallApp"
            @delete="deleteApp"
            @edit="editApp"
            @download="downloadApp"
            @help="handleAppClick"
            @open="openApp"
            @start-server="startServer"
          />
        </div>
      </div>

      <!-- All Apps Section (Filtered/Sorted) -->
      <h2 class="h2 text-2xl font-bold mb-4">{{ currentCategoryName }} ({{ sortedAndFilteredApps.length }})</h2>
       <div v-if="sortedAndFilteredApps.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        <app-card
          v-for="app in sortedAndFilteredApps"
          :key="app.name"
          :app="app"
          @toggle-favorite="toggleFavorite"
          @install="installApp"
          @uninstall="uninstallApp"
          @delete="deleteApp"
          @edit="editApp"
          @download="downloadApp"
          @help="handleAppClick"
          @open="openApp"
          @start-server="startServer"
        />
      </div>
      <p v-else class="text-center text-blue-500 dark:text-blue-400 py-10">
        No apps found in this category or matching your filters.
      </p>
    </div>

    <!-- App details modal -->
    <div v-if="selectedApp" class="fixed inset-0 bg-black bg-opacity-70 flex items-center justify-center z-50 p-4">
       <!-- Applied card class -->
      <div class="card w-11/12 max-w-4xl h-5/6 flex flex-col text-blue-900 dark:text-blue-100">
        <div class="flex justify-between items-center mb-4 pb-2 border-b border-blue-300 dark:border-blue-600">
          <h2 class="h3 !mb-0">{{ selectedApp.name }}</h2>
          <button @click="backToZoo" class="btn btn-secondary btn-sm">Close</button>
        </div>
        <iframe v-if="appCode" :srcdoc="appCode" class="flex-grow border border-blue-200 dark:border-blue-700 rounded-md bg-white dark:bg-blue-900"></iframe> <!-- Styled iframe -->
        <p v-else class="text-center text-red-600 dark:text-red-400 py-10">Please install this app to view its code.</p>
      </div>
    </div>

    <!-- Toast message -->
    <div v-if="message" class="fixed bottom-4 right-4 px-6 py-3 rounded-lg shadow-lg z-[100]" :class="{ 'bg-green-200 text-green-800 dark:bg-green-700 dark:text-green-100': successMessage, 'bg-red-200 text-red-800 dark:bg-red-800 dark:text-red-100': !successMessage }">
      {{ message }}
    </div>
  </div>
</template>



<script>
import axios from 'axios';
import AppCard from './apps_components/AppCard.vue'; // Create this component for individual app cards
import { marked } from 'marked';

import { mapState, mapGetters, mapActions } from 'vuex';

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
      showOnlyUnInstalled: false,
    };
  },
  computed: {
    currentCategoryName() {
      return this.selectedCategory === 'all' ? 'All Apps': this.selectedCategory;
    },    
    combinedApps() {
      //const installedAppNames = this.apps.map(app => app.name);
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

        // Adjusting the installed logic to account for both showOnlyInstalled and showOnlyUnInstalled
        const matchesInstalled = (this.showOnlyInstalled && app.installed) || 
                                (this.showOnlyUnInstalled && !app.installed) || 
                                (!this.showOnlyInstalled && !this.showOnlyUnInstalled);

        return matchesSearch && matchesCategory && matchesInstalled;
      });
    },
    sortedAndFilteredApps() {
      return [...this.filteredApps].sort((a, b) => {
        let comparison = 0;
        switch (this.sortBy) {
          case 'name':
            comparison = a.name.localeCompare(b.name);
            break;
          case 'author':
            comparison = a.author.localeCompare(b.author);
            break;
          case 'date':
            comparison = this.getDateValue(a.creation_date) - this.getDateValue(b.creation_date);
            break;
          case 'update':
            comparison = this.getDateValue(a.last_update_date) - this.getDateValue(b.last_update_date);
            break;
        }
        return this.sortOrder === 'asc' ? comparison : -comparison;
      });
    },

    favoriteApps() {
      return this.combinedApps.filter(app => this.favorites.includes(app.appName));
    },
  },
  methods: {
    ...mapActions(['refreshConfig', 'refreshDatabase', 'refreshBindings', 'refreshPersonalitiesZoo', 'refreshMountedPersonalities', 'refreshModelsZoo', 'refreshModels', 'fetchLanguages', 'fetchLanguage', 'fetchIsRtOn', 'toggleStarPersonality', 'toggleStarDiscussion', 'toggleStarApp', 'applyConfiguration', 'saveConfiguration', 'refreshModelStatus']),

    ...mapState([
            'ready', 'loading_infos', 'loading_progress', 'version', 'config',
            'databases', 'isConnected', 'isGenerating', 'client_id', 'leftPanelCollapsed',
            'rightPanelCollapsed', 'theme_vars', 'selectedPersonality',
            'currentPersonConfig', 'personalities', 'personalities_ready',
            'starredDiscussions', 'starredApps' // Make sure this is in mapState or mapGetters
        ]),
        ...mapGetters([
            'getIsReady', 'getVersion', 'getConfig', 'getClientId', 'getDatabases',
            'getIsConnected', 'getIsGenerating', 'getLeftPanelCollapsed',
            'getRightPanelCollapsed', 'getStarredDiscussions', 'getStarredApps' // Use getter if defined
        ]),
    getDateValue(dateString) {
        if (!dateString) return 0; // Gère les valeurs manquantes
        const date = new Date(dateString);
        return isNaN(date.getTime()) ? 0 : date.getTime();
    },

    toggleSortOrder() {
      this.sortOrder = this.sortOrder === 'asc' ? 'desc' : 'asc';
    },
    toggleFavorite(appName) {
      console.log("Toggling favorite")
      console.log(appName)
      this.toggleStarApp()

      const index = this.favorites.indexOf(appName);
      if (index === -1) {
        this.favorites.push(appName);
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
        console.log(response)
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
        const response = await axios.get(`/apps/${app.folder_name}/README.md`);
        this.appCode = marked(response.data);
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
        await axios.post(`/install_app/${appName}`, {
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
        await axios.post(`/uninstall_app/${appName}`, {
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

