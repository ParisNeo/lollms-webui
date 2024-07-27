<template>
  <div class="app-zoo">
    <h1 class="text-3xl font-bold mb-4">Apps Zoo</h1>
    <button @click="fetchGithubApps" class="bg-green-500 text-white px-4 py-2 rounded mb-4">Fetch GitHub Apps</button>
    <div class="app-list grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      <div
        v-for="app in apps"
        :key="app.uid"
        class="app-card border rounded-lg shadow-lg p-4 cursor-pointer hover:shadow-xl transition"
        @click="selectApp(app)"
      >
        <img :src="app.icon" alt="App Icon" class="w-16 h-16 mx-auto mb-2" />
        <p class="text-center font-semibold">{{ app.name }}</p>
        <p class="text-center text-sm text-gray-600">Author: {{ app.author }}</p>
        <p class="text-center text-sm text-gray-600">Version: {{ app.version }}</p>
        <label class="text-center text-sm text-gray-600" for="app-description">Description:</label>
        <p id="app-description" class="text-center text-sm text-gray-600">{{ app.description }}</p>
        <p class="text-center text-sm text-gray-600">AI Model: {{ app.aiModel }}</p>
        <p class="text-center text-sm text-gray-600 italic">Disclaimer: {{ app.disclaimer }}</p>
        <div class="flex justify-between mt-2">
          <button @click.stop="installApp(app.name)" class="bg-blue-500 text-white px-2 py-1 rounded">Install</button>
          <button @click.stop="uninstallApp(app.name)" class="bg-red-500 text-white px-2 py-1 rounded">Uninstall</button>
        </div>

      </div>
    </div>
    <div v-if="selectedApp" class="app-render fixed inset-0 bg-white z-50 flex flex-col items-center justify-center">
      <button @click="backToZoo" class="absolute top-4 right-4 bg-gray-300 px-2 py-1 rounded">Back</button>
      <h2 class="text-2xl font-bold mb-4">Rendering: {{ selectedApp.name }}</h2>
      <iframe :srcdoc="appCode" class="app-frame w-full h-full border-none"></iframe>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      apps: [],
      selectedApp: null,
      appCode: '',
    };
  },
  methods: {
    async fetchApps() {
      const response = await axios.get('/apps');
      this.apps = response.data;
    },
    async fetchGithubApps() {
      await axios.get('/github/apps');
      this.fetchApps(); // Refresh the app list after fetching GitHub apps
    },
    async selectApp(app) {
      this.selectedApp = app;
      const response = await axios.post(`/apps/${app.name}/code`, {
        client_id: this.$store.state.client_id,
      });
      this.appCode = response.data;
    },
    backToZoo() {
      this.selectedApp = null;
      this.appCode = '';
    },
    async installApp(appName) {
      await axios.post(`/install/${appName}`, {
        client_id: this.$store.state.client_id,
      });
      this.fetchApps(); // Refresh the app list
    },
    async uninstallApp(appName) {
      await axios.post(`/uninstall/${appName}`, {
        client_id: this.$store.state.client_id,
      });
      this.fetchApps(); // Refresh the app list
    },
  },
  mounted() {
    this.fetchApps();
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
}
.app-frame {
  width: 100%;
  height: 100%;
  border: none;
}
</style>
