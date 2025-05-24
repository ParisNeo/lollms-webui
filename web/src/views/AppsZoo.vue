<template>
  <div class="app-zoo background-color w-full p-6 pt-12 min-h-screen overflow-y-auto text-blue-900 dark:text-blue-100">
    <!-- Navigation and Filters Bar -->
    <nav class="panels-color shadow-lg rounded-lg p-4 max-w-7xl mx-auto mb-8 sticky top-4 z-40">
      <div class="flex flex-wrap items-center justify-between gap-4">
        <!-- Action Buttons -->
        <div class="flex items-center space-x-2 flex-wrap gap-2">
          <button
            @click="refreshAllApps"
            class="btn btn-primary btn-sm"
            aria-label="Refresh apps from GitHub and local"
            title="Refresh all app listings"
          >
            <i data-feather="refresh-cw" class="w-4 h-4 mr-1"></i>
            Refresh All
          </button>

          <button
            @click="openAppsFolder"
            class="btn btn-secondary btn-sm"
            aria-label="Open apps folder"
            title="Open local apps folder"
          >
            <i data-feather="folder" class="w-4 h-4 mr-1"></i>
            Apps Folder
          </button>

          <input type="file" @change="onFileSelected" accept=".zip" ref="fileInput" class="hidden" aria-hidden="true">
          <button @click="triggerFileInput" :disabled="isUploading" class="btn btn-success btn-sm" title="Upload a new App (ZIP)">
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
            placeholder="Search apps by name, author, description..."
            class="search-input w-full py-2 px-4 pl-10 text-sm"
            aria-label="Search apps"
           />
        </div>

        <!-- Filters and Sorting -->
        <div class="flex items-center space-x-4 flex-wrap gap-x-4 gap-y-2">
            <div class="flex items-center space-x-2">
              <label for="category-select" class="label !mb-0 text-sm">Category:</label> 
              <select
                id="category-select"
                v-model="selectedCategory"
                class="input input-sm py-1 text-sm"
              >
                <option value="all">All Categories</option>
                <option v-for="category in categories" :key="category" :value="category">
                  {{ category }}
                </option>
              </select>
            </div>

            <div class="flex items-center space-x-3">
               <label for="installed-only" class="label !mb-0 flex items-center cursor-pointer text-sm">
                <input
                  id="installed-only"
                  type="checkbox"
                  v-model="showOnlyInstalled"
                  class="mr-1.5 h-4 w-4 rounded border-blue-300 dark:border-blue-600 text-blue-600 focus:ring-blue-500 dark:focus:ring-blue-400 dark:bg-blue-700 dark:text-blue-500"
                >
                Installed
              </label>
              <label for="uninstalled-only" class="label !mb-0 flex items-center cursor-pointer text-sm">
                <input
                  id="uninstalled-only"
                  type="checkbox"
                  v-model="showOnlyUnInstalled"
                  class="mr-1.5 h-4 w-4 rounded border-blue-300 dark:border-blue-600 text-blue-600 focus:ring-blue-500 dark:focus:ring-blue-400 dark:bg-blue-700 dark:text-blue-500"
                >
                Not Installed
              </label>
            </div>

            <div class="flex items-center space-x-2">
              <label for="sort-select" class="label !mb-0 text-sm">Sort by:</label>
              <select
                id="sort-select"
                v-model="sortBy"
                class="input input-sm py-1 text-sm" 
              >
                <option value="name">Name</option>
                <option value="author">Author</option>
                <option value="creation_date">Creation Date</option>
                <option value="last_update_date">Last Update</option>
              </select>
              <button @click="toggleSortOrder" class="btn btn-secondary btn-sm" aria-label="Toggle sort order" title="Toggle sort order">
                <i v-if="sortOrder === 'asc'" data-feather="arrow-up" class="w-4 h-4"></i>
                <i v-else data-feather="arrow-down" class="w-4 h-4"></i>
              </button>
            </div>
        </div>
      </div>
    </nav>

    <!-- Loading Indicator -->
    <div v-if="loading" class="flex flex-col justify-center items-center space-y-2 my-12" aria-live="polite">
      <div class="animate-spin rounded-full h-12 w-12 border-t-4 border-b-4 border-blue-500 dark:border-blue-400"></div>
      <span class="text-xl text-loading font-semibold">Loading Apps...</span> 
    </div>

    <!-- App Grids -->
    <div v-else class="pb-20 max-w-7xl mx-auto">
       <!-- Favorite Apps Section -->
       <div v-if="favoriteAppsToDisplay.length > 0" class="mb-10">
        <h2 class="h2 text-2xl font-bold mb-4 text-gray-800 dark:text-gray-100">
            <i data-feather="star" class="w-6 h-6 inline-block mr-2 text-yellow-500 fill-current"></i>Favorite Apps
        </h2> 
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          <app-card
            v-for="app in favoriteAppsToDisplay"
            :key="app.folder_name"
            :app="app"
            :is-favorite="true"
            @toggle-favorite="handleToggleFavorite"
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

      <!-- All Other Apps Section (Filtered/Sorted) -->
      <h2 class="h2 text-2xl font-bold mb-4 text-gray-800 dark:text-gray-100">
        {{ currentCategoryName }} ({{ nonFavoriteAppsToDisplay.length }})
      </h2>
       <div v-if="nonFavoriteAppsToDisplay.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        <app-card
          v-for="app in nonFavoriteAppsToDisplay"
          :key="app.folder_name"
          :app="app"
          :is-favorite="getStarredApps.includes(app.folder_name)"
          @toggle-favorite="handleToggleFavorite"
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
      <p v-else-if="!loading && combinedApps.length > 0" class="text-center text-gray-500 dark:text-gray-400 py-10 text-lg">
        No apps match your current filters in this category. Try adjusting your search or filter settings.
      </p>
      <p v-else-if="!loading && combinedApps.length === 0" class="text-center text-gray-500 dark:text-gray-400 py-10 text-lg">
        No apps available. Try refreshing or uploading an app.
      </p>
    </div>

    <!-- App details modal -->
    <div v-if="selectedApp" class="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-[60] p-4" @click.self="backToZoo">
      <div class="card w-11/12 max-w-4xl h-5/6 flex flex-col text-blue-900 dark:text-blue-100 shadow-2xl">
        <div class="flex justify-between items-center mb-4 pb-2 border-b border-blue-300 dark:border-blue-600 p-4">
          <h2 class="h3 !mb-0 text-xl font-semibold">{{ selectedApp.name }} - README</h2>
          <button @click="backToZoo" class="btn btn-secondary btn-sm p-2" title="Close README">
            <i data-feather="x" class="w-5 h-5"></i>
          </button>
        </div>
        <div v-if="appCode" class="flex-grow border border-blue-200 dark:border-blue-700 rounded-md bg-white dark:bg-gray-900 overflow-y-auto p-4 prose dark:prose-invert max-w-none" v-html="appCode"></div>
        <div v-else-if="readmeLoading" class="flex justify-center items-center h-full">
            <div class="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-blue-500"></div>
            <p class="ml-2">Loading README...</p>
        </div>
        <p v-else class="text-center text-red-600 dark:text-red-400 py-10">README content not available or app not installed properly.</p>
      </div>
    </div>

    <!-- Toast message -->
    <div v-if="message" :class="['fixed bottom-4 right-4 px-6 py-3 rounded-lg shadow-lg z-[100] text-sm transition-opacity duration-300', successMessage ? 'bg-green-600 text-white dark:bg-green-700' : 'bg-red-600 text-white dark:bg-red-700', messageVisible ? 'opacity-100' : 'opacity-0']">
      {{ message }}
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import AppCard from './apps_components/AppCard.vue';
import { marked } from 'marked';
import feather from 'feather-icons';
import { mapGetters, mapActions } from 'vuex';
import { nextTick } from 'vue';

const APPS_ZOO_SETTINGS_KEY = 'lollms_apps_zoo_settings';

export default {
  components: {
    AppCard,
  },
  data() {
    return {
      apps: [], // Local apps
      githubApps: [], // Apps from GitHub
      selectedApp: null,
      appCode: '',
      readmeLoading: false,
      loading: false,
      message: '',
      successMessage: true,
      messageVisible: false,
      searchQuery: '',
      selectedFile: null,
      isUploading: false,
      error: '', // General error messages for UI
      // Filter and sort states - defaults will be overridden by localStorage
      selectedCategory: 'all',
      sortBy: 'last_update_date', // Default sort
      sortOrder: 'desc', // Default sort order
      showOnlyInstalled: false,
      showOnlyUnInstalled: false,
    };
  },
  computed: {
    ...mapGetters(['getClientId', 'getStarredApps', 'getToast', 'getMessageBox']), // Assuming getToast and getMessageBox are used for notifications
    
    currentCategoryName() {
      if (this.selectedCategory === 'all') return 'All Apps';
      const cat = this.categories.find(c => c === this.selectedCategory);
      return cat ? cat : 'Unknown Category';
    },    
    combinedApps() {
      const localAppsMap = new Map();
      // Prioritize local app data if an app exists both locally and on GitHub
      this.apps.forEach(app => {
        if (app.folder_name) { // Ensure folder_name exists
            localAppsMap.set(app.folder_name, { ...app, installed: true, existsInFolder: true, is_public: app.is_public !== undefined ? app.is_public : false });
        }
      });

      this.githubApps.forEach(app => {
        if (app.folder_name) { // Ensure folder_name exists
            if (!localAppsMap.has(app.folder_name)) {
                localAppsMap.set(app.folder_name, { ...app, installed: false, existsInFolder: false, is_public: true });
            } else {
                // If it exists locally, merge GitHub info like description, version if newer, etc.
                // For now, just mark it as public if GitHub says so and update version if GH is newer
                const localApp = localAppsMap.get(app.folder_name);
                localApp.is_public = true; // If it's on GH, it's public
                localApp.description = localApp.description || app.description; // Prefer local description if available
                localApp.author = localApp.author || app.author;
                // Potentially add version comparison here for 'has_update' logic
                // localApp.has_update = compareVersions(localApp.version, app.version) < 0;
            }
        }
      });
      return Array.from(localAppsMap.values());
    },
    categories() {
      // Ensure default 'General' category if none provided or handle gracefully
      const cats = [...new Set(this.combinedApps.map(app => app.category || 'General'))];
      return cats.sort();
    },
    filteredApps() {
      return this.combinedApps.filter(app => {
        if (!app || !app.name) return false; // Skip invalid app objects
        const appName = app.name || "";
        const appDescription = app.description || "";
        const appAuthor = app.author || "";

        const matchesSearch = appName.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
                              appDescription.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
                              appAuthor.toLowerCase().includes(this.searchQuery.toLowerCase());
        
        const appCategory = app.category || 'General';
        const matchesCategory = this.selectedCategory === 'all' || appCategory === this.selectedCategory;

        const matchesInstalled = (this.showOnlyInstalled && app.installed) || 
                                (this.showOnlyUnInstalled && !app.installed) || 
                                (!this.showOnlyInstalled && !this.showOnlyUnInstalled);

        return matchesSearch && matchesCategory && matchesInstalled;
      });
    },
    
    _sortedBase() { // Internal computed for sorting logic
        return [...this.filteredApps].sort((a, b) => {
            let comparison = 0;
            const valA = (this.sortBy === 'name' || this.sortBy === 'author') ? (a[this.sortBy] || '').toLowerCase() : this.getDateValue(a[this.sortBy]);
            const valB = (this.sortBy === 'name' || this.sortBy === 'author') ? (b[this.sortBy] || '').toLowerCase() : this.getDateValue(b[this.sortBy]);

            if (valA < valB) {
                comparison = -1;
            } else if (valA > valB) {
                comparison = 1;
            }
            return this.sortOrder === 'asc' ? comparison : -comparison;
        });
    },

    favoriteAppsToDisplay() {
        if (!this.getStarredApps) return [];
        const starredSet = new Set(this.getStarredApps);
        return this._sortedBase.filter(app => app.folder_name && starredSet.has(app.folder_name));
    },

    nonFavoriteAppsToDisplay() {
        if (!this.getStarredApps) return this._sortedBase;
        const starredSet = new Set(this.getStarredApps);
        return this._sortedBase.filter(app => !app.folder_name || !starredSet.has(app.folder_name));
    },
  },
  watch: {
    searchQuery() { this.saveSettingsToLocalStorage(); },
    selectedCategory() { this.saveSettingsToLocalStorage(); },
    sortBy() { this.saveSettingsToLocalStorage(); },
    sortOrder() { this.saveSettingsToLocalStorage(); },
    showOnlyInstalled() { this.saveSettingsToLocalStorage(); },
    showOnlyUnInstalled() { this.saveSettingsToLocalStorage(); },
    combinedApps: {
      handler() {
        this.triggerFeatherReplacement();
      },
      deep: true
    }
  },
  methods: {
    ...mapActions(['toggleStarApp']), // Add other actions if needed

    triggerFeatherReplacement() {
        nextTick(() => {
            feather.replace();
        });
    },
    loadSettingsFromLocalStorage() {
      const savedSettings = localStorage.getItem(APPS_ZOO_SETTINGS_KEY);
      if (savedSettings) {
        try {
          const settings = JSON.parse(savedSettings);
          this.searchQuery = settings.searchQuery || '';
          this.selectedCategory = settings.selectedCategory || 'all';
          this.sortBy = settings.sortBy || 'last_update_date';
          this.sortOrder = settings.sortOrder || 'desc';
          this.showOnlyInstalled = settings.showOnlyInstalled || false;
          this.showOnlyUnInstalled = settings.showOnlyUnInstalled || false;
        } catch (e) {
          console.error("Error loading AppsZoo settings from localStorage:", e);
          // Use defaults if parsing fails
        }
      }
    },
    saveSettingsToLocalStorage() {
      const settings = {
        searchQuery: this.searchQuery,
        selectedCategory: this.selectedCategory,
        sortBy: this.sortBy,
        sortOrder: this.sortOrder,
        showOnlyInstalled: this.showOnlyInstalled,
        showOnlyUnInstalled: this.showOnlyUnInstalled,
      };
      localStorage.setItem(APPS_ZOO_SETTINGS_KEY, JSON.stringify(settings));
    },
    getDateValue(dateString) {
        if (!dateString) return this.sortOrder === 'asc' ? Infinity : -Infinity; // Push undefined dates to the end
        const date = new Date(dateString);
        return isNaN(date.getTime()) ? (this.sortOrder === 'asc' ? Infinity : -Infinity) : date.getTime();
    },
    toggleSortOrder() {
      this.sortOrder = this.sortOrder === 'asc' ? 'desc' : 'asc';
      this.triggerFeatherReplacement(); // Icons in sort button might change
    },
    handleToggleFavorite(appFolderName) {
      const app = this.combinedApps.find(a => a.folder_name === appFolderName);
      if (app) {
        this.$store.dispatch('toggleStarApp', app); // Dispatch action with the app object
      } else {
        console.warn("App not found for toggling favorite:", appFolderName);
        this.showMessage(`Error: App '${appFolderName}' not found.`, false);
      }
    },   
    async refreshAllApps() {
        this.loading = true;
        this.showMessage("Refreshing app lists...", true, 10000); // Longer duration for refresh
        try {
            await this.fetchGithubApps(); // This will also call fetchApps
            this.showMessage('App lists refreshed successfully!', true);
        } catch(e) {
            this.showMessage('Failed to refresh all apps.', false);
        } finally {
            this.loading = false;
            this.triggerFeatherReplacement();
        }
    },
    startServer(appName) {
      const payload = {
        client_id: this.getClientId,
        app_name: appName
      };
      this.getMessageBox.showBlockingMessage("Loading server.\nThis may take some time the first time as some libraries need to be installed.");
      axios.post(`/apps/start_server`, payload)
        .then(response => {
          this.getMessageBox.hideMessage();
          this.getToast.showToast(response.data.message || 'Server start initiated.', 4, true);
        })
        .catch(error => {
          this.getMessageBox.hideMessage();
          this.getToast.showToast(error.response?.data?.detail || 'Error starting server.', 4, false);
        });
    },
    triggerFileInput() {
      this.$refs.fileInput.click();
    },
    onFileSelected(event) {
      this.selectedFile = event.target.files[0];
      if (this.selectedFile) {
        this.uploadApp();
      }
    },
    async uploadApp() {
      if (!this.selectedFile) {
        this.showMessage('Please select a file to upload.', false);
        return;
      }
      this.isUploading = true;
      const formData = new FormData();
      formData.append('file', this.selectedFile);
      formData.append('client_id', this.getClientId);

      try {
        const response = await axios.post('/upload_app', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });
        this.showMessage(response.data.message || "App uploaded successfully!", true);
        this.$refs.fileInput.value = ''; 
        this.selectedFile = null;
        await this.fetchApps(); // Refresh local apps list
      } catch (error) {
        console.error('Error uploading app:', error);
        this.showMessage(error.response?.data?.detail || 'Failed to upload the app.', false);
      } finally {
        this.isUploading = false;
        this.triggerFeatherReplacement();
      }
    },    
    async fetchApps() { // Fetches locally available apps
      this.loading = true;
      try {
        const response = await axios.get('/apps');
        this.apps = Array.isArray(response.data) ? response.data : [];
      } catch (error) {
        this.showMessage('Failed to fetch local apps.', false);
        this.apps = []; // Ensure apps is an array on error
      } finally {
        // Loading will be set to false by fetchGithubApps or refreshAllApps
        this.triggerFeatherReplacement();
      }
    },    
    async openAppsFolder() {
      try {
        await axios.post(`/show_apps_folder`, { client_id: this.getClientId });
      } catch (error) {
        this.showMessage('Failed to request opening apps folder.', false);
      }
    },
    async fetchGithubApps() {
      this.loading = true;
      try {
        const response = await axios.get('/github/apps');
        this.githubApps = Array.isArray(response.data.apps) ? response.data.apps : [];
        await this.fetchApps(); // Refresh local apps after getting GitHub list for proper merging
      } catch (error) {
        this.showMessage('Failed to fetch GitHub apps list.', false);
        this.githubApps = []; // Ensure githubApps is an array on error
      } finally {
        this.loading = false;
        this.triggerFeatherReplacement();
      }
    },
    async handleAppClick(app) { // For README
      if (app.installed) {
        this.selectedApp = app;
        this.appCode = ''; // Clear previous code
        this.readmeLoading = true;
        this.triggerFeatherReplacement(); // For modal icons
        try {
            const response = await axios.get(`/apps/${app.folder_name}/README.md`);
            this.appCode = marked(response.data);
        } catch (e) {
            console.error("Error fetching README:", e);
            this.appCode = "<p>Could not load README.md. It might not exist or the app is not properly installed.</p>";
        } finally {
            this.readmeLoading = false;
            this.triggerFeatherReplacement();
        }
      } else {
        this.showMessage(`Please install '${app.name}' to view its README.`, false);
      }
    },
    backToZoo() {
      this.selectedApp = null;
      this.appCode = '';
    },
    async _appAction(actionType, appName, successMsg, failureMsg, endpoint, method = 'post') {
        this.loading = true; // General loading for the page might be too much, consider card-specific loading
        let blockingMessage = `${actionType.charAt(0).toUpperCase() + actionType.slice(1)} app '${appName}'...`;
        if (actionType === 'install') {
            blockingMessage = `Installing app '${appName}'. This may take a while for downloads and setup...`;
        }
        this.getMessageBox.showBlockingMessage(blockingMessage);

        try {
            const payload = { client_id: this.getClientId };
            if (method === 'post') {
                await axios.post(`/${endpoint}/${appName}`, payload);
            } else {
                await axios.get(`/${endpoint}/${appName}`, payload); // Assuming some actions might be GET
            }
            this.showMessage(successMsg, true);
            // Refresh relevant data
            await this.fetchApps(); // Always refresh local apps
            if (actionType === 'install' || actionType === 'uninstall' || actionType === 'delete') {
                 // Potentially refresh github apps too if installation status affects combined view
                 await this.fetchGithubApps();
            }
        } catch (error) {
            console.error(`Error ${actionType} app ${appName}:`, error);
            this.showMessage(error.response?.data?.detail || `${failureMsg} Error: ${error.message}`, false);
        } finally {
            this.loading = false;
            this.getMessageBox.hideMessage();
            this.triggerFeatherReplacement();
        }
    },
    installApp(appName) { this._appAction('install', appName, 'Installation successful!', 'Installation failed.', 'install_app'); },
    uninstallApp(appName) { this._appAction('uninstall', appName, 'Uninstallation successful!', 'Uninstallation failed.', 'uninstall_app'); },
    deleteApp(appName) { this._appAction('delete', appName, 'Deletion successful!', 'Deletion failed.', 'delete_app_folder'); }, // Assuming endpoint is delete_app_folder

    async editApp(app) {
      try {
        const response = await axios.post('/open_app_in_vscode', {
          client_id: this.getClientId,
          app_name: app.folder_name,
        });
        this.showMessage(response.data.message || "Request to open in VSCode sent.", true);
      } catch (error) {
        this.showMessage(error.response?.data?.detail || 'Failed to open folder in VSCode.', false);
      }
    },
    async downloadApp(appName) {
      this.showMessage(`Preparing download for ${appName}...`, true);
      try {
        const response = await axios.post('/download_app', {
          client_id: this.getClientId,
          app_name: appName
        }, { responseType: 'arraybuffer' });

        const contentDisposition = response.headers['content-disposition'];
        const filenameMatch = contentDisposition && contentDisposition.match(/filename="?(.+)"?/i);
        const filename = filenameMatch ? filenameMatch[1] : `${appName}.zip`;
        const blob = new Blob([response.data], { type: 'application/zip' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        this.showMessage(`Download started for ${filename}.`, true);
      } catch (error) {
        console.error('Error downloading app:', error);
        this.showMessage(error.response?.data?.detail || 'Failed to download the app.', false);
      }
    },
    openApp(app) {
      if (app.installed) {
        window.open(`/apps/${app.folder_name}/index.html?client_id=${this.getClientId}`, '_blank');
      } else {
        this.showMessage(`Please install '${app.name}' before opening.`, false);
      }
    },
    showMessage(msg, success, duration = 3000) {
      this.message = msg;
      this.successMessage = success;
      this.messageVisible = true;
      if (this.messageTimeout) clearTimeout(this.messageTimeout);
      this.messageTimeout = setTimeout(() => {
        this.messageVisible = false;
        // Optionally clear message after fade out: setTimeout(() => { this.message = ''; }, 300);
      }, duration);
    }
  },
  mounted() {
    this.loadSettingsFromLocalStorage();
    this.refreshAllApps(); // Initial fetch of all apps
    this.messageTimeout = null;
    nextTick(() => {
        feather.replace();
    });
  },
  updated() {
    // This is a general catch-all. Be cautious if it causes performance issues.
    // Specific nextTick calls after data changes are often better.
    nextTick(() => {
        feather.replace();
    });
  },
  beforeUnmount() {
    if (this.messageTimeout) clearTimeout(this.messageTimeout);
  }
};
</script>

<style scoped>
/* Add any additional specific styles for AppsZoo.vue if needed */
.prose :where(code):not(:where([class~="not-prose"] *))::before,
.prose :where(code):not(:where([class~="not-prose"] *))::after {
    content: ""; /* Disable prose backticks for inline code */
}
.search-input {
    /* Ensure styles are inherited or explicitly set for consistency */
    /* Example: border-color: var(--border-color); */
}
.sticky {
  position: -webkit-sticky; /* For Safari */
  position: sticky;
}

/* Thin scrollbar for modal content if needed, AppCard already has its own */
.prose {
  scrollbar-width: thin;
  scrollbar-color: var(--scrollbar-thumb-color, #a0aec0) var(--scrollbar-track-color, #edf2f7);
}
.prose::-webkit-scrollbar {
  width: 8px;
}
.prose::-webkit-scrollbar-track {
  background: var(--scrollbar-track-color, #edf2f7);
}
.prose::-webkit-scrollbar-thumb {
  background-color: var(--scrollbar-thumb-color, #a0aec0);
  border-radius: 4px;
  border: 2px solid var(--scrollbar-track-color, #edf2f7);
}
.dark .prose {
  scrollbar-color: var(--dark-scrollbar-thumb-color, #4a5568) var(--dark-scrollbar-track-color, #2d3748);
}
.dark .prose::-webkit-scrollbar-track {
  background: var(--dark-scrollbar-track-color, #2d3748);
}
.dark .prose::-webkit-scrollbar-thumb {
  background-color: var(--dark-scrollbar-thumb-color, #4a5568);
  border: 2px solid var(--dark-scrollbar-track-color, #2d3748);
}
</style>