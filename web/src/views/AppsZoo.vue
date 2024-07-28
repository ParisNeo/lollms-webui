<template>
  <div class="app-zoo w-full">
    <button @click="fetchGithubApps" class="bg-green-500 text-white px-4 py-2 rounded mb-4">Refresh apps from GitHub</button>
    <div v-if="loading" class="loading-animation">Loading...</div>
    <div class="app-list grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 w-full">
      <div
        v-for="app in combinedApps"
        :key="app.uid"
        class="app-card border rounded-lg shadow-lg p-4 cursor-pointer hover:shadow-xl transition"
        @click="handleAppClick(app)"
      >
        <img :src="app.icon" alt="App Icon" class="app-icon w-16 h-16 mx-auto mb-2 rounded-full border border-gray-300" />
        <p class="text-center font-semibold">{{ app.name }}</p>
        <p class="text-center text-sm text-gray-600">Author: {{ app.author }}</p>
        <p class="text-center text-sm text-gray-600">Version: {{ app.version }}</p>
        <label class="text-center text-sm text-gray-600" for="app-description">Description:</label>
        <p id="app-description" class="text-center text-sm text-gray-600">{{ app.description }}</p>
        <p class="text-center text-sm text-gray-600">AI Model: {{ app.model_name }}</p>
        <p class="text-center text-sm text-gray-600 italic">Disclaimer: {{ app.disclaimer }}</p>
        <div class="flex justify-between mt-2">
          <button v-if="!app.installed" @click.stop="installApp(app.name)" class="bg-blue-500 text-white px-2 py-1 rounded">Install</button>
          <button v-if="app.installed" @click.stop="uninstallApp(app.name)" class="bg-red-500 text-white px-2 py-1 rounded">Uninstall</button>
        </div>
      </div>
    </div>
    <div v-if="selectedApp" class="app-render fixed inset-0 bg-white z-50 flex flex-col items-center justify-center">
      <button @click="backToZoo" class="absolute top-4 right-4 bg-gray-300 px-2 py-1 rounded">Back</button>
      <h2 class="text-2xl font-bold mb-4">Rendering: {{ selectedApp.name }}</h2>
      <iframe v-if="appCode" :srcdoc="appCode" class="app-frame w-full h-full border-none"></iframe>
      <p v-else class="text-center text-red-500">Please install this app to view its code.</p>
    </div>
    <div v-if="message" class="message" :class="{ success: successMessage, error: !successMessage }">{{ message }}</div>
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
    };
  },
  computed: {
    combinedApps() {
      const installedAppNames = this.apps.map(app => app.name);
      const localAppsMap = new Map(this.apps.map(app => [app.name, { ...app, installed: true }]));
      
      this.githubApps.forEach(app => {
        if (!localAppsMap.has(app.name)) {
          localAppsMap.set(app.name, { ...app, installed: false });
        }
      });

      return Array.from(localAppsMap.values());
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
    async fetchGithubApps() {
      this.loading = true;
      try {
        const response = await axios.get('/github/apps');
        this.githubApps = response.data.apps;
        await this.fetchApps(); // Refresh the app list after fetching GitHub apps
      } catch (error) {
        this.showMessage('Failed to refresh GitHub apps.', false);
      } finally {
        this.loading = false;
      }
    },
    async handleAppClick(app) {
      if (app.installed) {
        this.selectedApp = app;
        const response = await axios.post(`/apps/${app.name}/code`, {
          client_id: this.$store.state.client_id,
        });
        this.appCode = response.data;
      } else {
        alert(`Please install ${app.name} to view its code.`);
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
        this.fetchApps(); // Refresh the app list
        this.fetchGithubApps(); // Refresh GitHub apps
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
        this.fetchApps(); // Refresh the app list
      }
    },
    showMessage(msg, success) {
      this.message = msg;
      this.successMessage = success;
      setTimeout(() => {
        this.message = '';
      }, 3000); // Clear message after 3 seconds
    }
  },
  mounted() {
    this.fetchGithubApps(); // Fetch GitHub apps when the component is mounted
    this.fetchApps(); // Also fetch local apps
  },
};
</script>

<style scoped>
.app-zoo {
  display: flex;
  flex-direction: column;
  align-items: center;
}
.app-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
  width: 100%;
}
.app-icon {
  border-radius: 50%; /* Rounded edges */
  border: 2px solid #d1d5db; /* Light gray border */
}
.app-frame {
  width: 100%;
  height: 100%;
  border: none;
}
.loading-animation {
  animation: fadeIn 1s ease-in-out;
  margin: 20px;
  font-size: 1.5rem;
  color: #4a5568; /* Gray color */
}
.message {
  margin-top: 20px;
  padding: 10px;
  border-radius: 5px;
  transition: opacity 0.5s ease;
}
.message.success {
  background-color: #c6f6d5; /* Green background */
  color: #2f855a; /* Dark green text */
}
.message.error {
  background-color: #fed7d7; /* Red background */
  color: #c53030; /* Dark red text */
}
@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}
</style>
