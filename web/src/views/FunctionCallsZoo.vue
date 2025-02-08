<template>
    <div class="app-zoo mb-100 pb-100 pt-12 background-color w-full p-6 overflow-y-auto h-screen scrollbar-thin scrollbar-track-bg-light-tone scrollbar-thumb-bg-light-tone-panel hover:scrollbar-thumb-primary dark:scrollbar-track-bg-dark-tone dark:scrollbar-thumb-bg-dark-tone-panel dark:hover:scrollbar-thumb-primary active:scrollbar-thumb-secondary">
      <nav class="panels-color shadow-lg rounded-lg p-4 max-w-4xl mx-auto mb-8">
        <div class="flex flex-wrap items-center justify-between gap-4">
          <p v-if="message">{{ message }}</p>
          <p v-if="error" class="error">{{ error }}</p>
          
          <div class="relative flex-grow max-w-md">
            <input 
              v-model="searchQuery" 
              placeholder="Search functions..." 
              class="w-full border-b-2 border-gray-300 px-4 py-2 pl-10 focus:outline-none focus:border-blue-500 transition duration-300 ease-in-out"
              aria-label="Search functions"
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
        <div class="container mx-auto px-4 flex flex-column pb-20">
          <!-- Favorite Functions Section -->
          <div v-if="favoriteFunctions.length > 0 && !searchQuery">
            <h2 class="text-2xl font-bold my-8">Favorite Functions</h2>
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8 mb-12">
              <function-entry
                ref="functionsZoo"
                v-for="func in favoriteFunctions"
                :key="func.uid"
                :function="func"
                :on-mount="mountFunction"
                :on-unmount="unmountFunction"
                :on-remount="remountFunction"
                :on-edit="editFunction"
                :on-copy-to-custom="copyToCustom"
                :on-reinstall="onFunctionReinstall"
                :on-settings="onSettingsFunction"
                :on-toggle-favorite="toggleFavorite"
              />
            </div>
          </div>
        </div>
        <div class="container mx-auto px-4 flex flex-column pb-20">
          <!-- Current Category Section -->
          <h2 class="text-2xl font-bold my-8">{{ currentCategoryName }} ({{ sortedAndFilteredFunctions.length }})</h2>
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8 mb-12">
            <function-entry
              ref="functionsZoo"
              v-for="func in sortedAndFilteredFunctions"
              :key="func.uid"
              :function="func"
              :on-mount="mountFunction"
              :on-unmount="unmountFunction"
              :on-remount="remountFunction"
              :on-edit="editFunction"
              :on-copy-to-custom="copyToCustom"
              :on-reinstall="onFunctionReinstall"
              :on-settings="onSettingsFunction"
              :on-toggle-favorite="toggleFavorite"
            />
          </div>
        </div>
      </div>
  
      <!-- Function details modal -->
      <div v-if="selectedFunction" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 overflow-y-auto">
        <div class="bg-white rounded-lg p-6 w-11/12 h-5/6 flex flex-col">
          <div class="flex justify-between items-center mb-4">
            <h2 class="text-2xl font-bold">{{ selectedFunction.name }}</h2>
            <button @click="backToZoo" class="bg-gray-300 hover:bg-gray-400 px-4 py-2 rounded-lg transition duration-300 ease-in-out">Close</button>
          </div>
          <div class="flex-grow overflow-y-auto">
            <pre>{{ selectedFunctionDetails }}</pre>
          </div>
        </div>
      </div>
      <!-- Toast message -->
      <div v-if="message" class="fixed bottom-4 right-4 px-6 py-3 rounded-lg shadow-md" :class="{ 'bg-green-100 text-green-800': successMessage, 'bg-red-100 text-red-800': !successMessage }">
        {{ message }}
      </div>
  
      <!-- Extra padding at the bottom -->
      <div class="h-20"></div>
    </div>
  </template>
  <script>
  import axios from 'axios';
  import FunctionEntry from '@/components/FunctionEntry.vue'; // Create this component for individual function cards
  import { nextTick } from 'vue';
  
  export default {
    components: {
      FunctionEntry,
    },
    data() {
      return {
        functions: [],
        githubFunctions: [],
        favorites: [],
        selectedCategory: 'all',
        selectedFunction: null,
        loading: false,
        message: '',
        successMessage: true,
        searchQuery: '',
        selectedFile: null,
        isUploading: false,
        error: '',
        sortBy: 'name',
        sortOrder: 'asc',
      };
    },
    computed: {
      currentCategoryName() {
        return this.selectedCategory === 'all' ? 'All Functions' : this.selectedCategory;
      },
      configFile: {
        get() {
          return this.$store.state.config;
        },
        set(value) {
          this.$store.commit('setConfig', value);
        },
      },
      combinedFunctions() {
        const installedFunctionNames = this.functions.map(func => func.name);
        const localFunctionsMap = new Map(this.functions.map(func => [func.name, { ...func, installed: true, existsInFolder: true }]));
        
        this.githubFunctions.forEach(func => {
          if (!localFunctionsMap.has(func.name)) {
            localFunctionsMap.set(func.name, { ...func, installed: false, existsInFolder: false });
          }
        });
  
        return Array.from(localFunctionsMap.values());
      },
      categories() {
        return [...new Set(this.combinedFunctions.map(func => func.category))]
          .sort((a, b) => a.localeCompare(b));
      },
      filteredFunctions() {
        return this.combinedFunctions.filter(func => {
          const matchesSearch = func.name.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
                                func.author.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
                                func.description.toLowerCase().includes(this.searchQuery.toLowerCase());
          const matchesCategory = this.selectedCategory === 'all' || func.category === this.selectedCategory;
          return matchesSearch && matchesCategory;
        });
      },
      sortedAndFilteredFunctions() {
        return [...this.filteredFunctions].sort((a, b) => {
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
      favoriteFunctions() {
        return this.combinedFunctions.filter(func => this.favorites.includes(func.uid));
      },
      selectedFunctionDetails() {
        if (!this.selectedFunction) return '';
        return JSON.stringify(this.selectedFunction, null, 2);
      }
    },
    methods: {
      getDateValue(dateString) {
        if (!dateString) return 0;
        const date = new Date(dateString);
        return isNaN(date.getTime()) ? 0 : date.getTime();
      },
      toggleSortOrder() {
        this.sortOrder = this.sortOrder === 'asc' ? 'desc' : 'asc';
      },
      toggleFavorite(funcUid) {
        const index = this.favorites.indexOf(funcUid);
        if (index === -1) {
          this.favorites.push(funcUid);
        } else {
          this.favorites.splice(index, 1);
        }
        this.saveFavoritesToLocalStorage();
      },
      saveFavoritesToLocalStorage() {
        localStorage.setItem('functionZooFavorites', JSON.stringify(this.favorites));
      },
      loadFavoritesFromLocalStorage() {
        const savedFavorites = localStorage.getItem('functionZooFavorites');
        if (savedFavorites) {
          this.favorites = JSON.parse(savedFavorites);
        }
      },
      async mountFunction(func) {
        try {
          const response = await axios.post('/mount_function', {
            client_id: this.$store.state.client_id,
            function_name: func.name,
          });
          if (response.data.status) {
            this.showMessage('Function mounted successfully', true);
            this.$store.dispatch('refreshMountedFunctions');
          } else {
            this.showMessage('Failed to mount function', false);
          }
        } catch (error) {
          this.showMessage('Error mounting function', false);
          console.error(error);
        }
      },
      async unmountFunction(func) {
        try {
          const response = await axios.post('/unmount_function', {
            client_id: this.$store.state.client_id,
            function_name: func.name,
          });
          if (response.data.status) {
            this.showMessage('Function unmounted successfully', true);
            this.$store.dispatch('refreshMountedFunctions');
          } else {
            this.showMessage('Failed to unmount function', false);
          }
        } catch (error) {
          this.showMessage('Error unmounting function', false);
          console.error(error);
        }
      },
      async remountFunction(func) {
        await this.unmountFunction(func);
        await this.mountFunction(func);
      },
      editFunction(func) {
        this.selectedFunction = func;
      },
      async onFunctionReinstall(func) {
        try {
          const response = await axios.post('/reinstall_function', {
            client_id: this.$store.state.client_id,
            function_name: func.name,
          });
          if (response.data.status) {
            this.showMessage('Function reinstalled successfully', true);
          } else {
            this.showMessage('Failed to reinstall function', false);
          }
        } catch (error) {
          this.showMessage('Error reinstalling function', false);
          console.error(error);
        }
      },
      onSettingsFunction(func) {
        this.selectedFunction = func;
      },
      showMessage(msg, success) {
        this.message = msg;
        this.successMessage = success;
        setTimeout(() => {
          this.message = '';
        }, 3000);
      },
      loadFunctions() {
        this.loading = true;
        axios.get('/list_function_calls')
          .then(response => {
            this.functions = response.data.functions;
            this.loading = false;
          })
          .catch(error => {
            console.error(error);
            this.loading = false;
          });
      },
    },
    mounted() {
      this.loadFavoritesFromLocalStorage();
      this.loadFunctions();
    },
  };
  </script>
  
  <style scoped>
  .loading-indicator {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100px;
    font-size: 1.2em;
    color: #666;
  }
  </style>