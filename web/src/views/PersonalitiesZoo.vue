<template>
  <div class="app-zoo mb-100 pb-100 background-color w-full p-6 overflow-y-auto h-screen scrollbar-thin scrollbar-track-bg-light-tone scrollbar-thumb-bg-light-tone-panel hover:scrollbar-thumb-primary dark:scrollbar-track-bg-dark-tone dark:scrollbar-thumb-bg-dark-tone-panel dark:hover:scrollbar-thumb-primary active:scrollbar-thumb-secondary">
    <nav class="panels-color shadow-lg rounded-lg p-4 max-w-4xl mx-auto mb-8">
      <div class="flex flex-wrap items-center justify-between gap-4">
        <p v-if="message">{{ message }}</p>
        <p v-if="error" class="error">{{ error }}</p>
        
        <div class="relative flex-grow max-w-md">
          <input 
            v-model="searchQuery" 
            placeholder="Search personalities..." 
            class="w-full border-b-2 border-gray-300 px-4 py-2 pl-10 focus:outline-none focus:border-blue-500 transition duration-300 ease-in-out"
            aria-label="Search personalities"
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
        <!-- Favorite Apps Section -->
        <div v-if="favoriteApps.length > 0 && !searchQuery">
          <h2 class="text-2xl font-bold my-8">Favorite Apps</h2>
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8 mb-12">
            <personality-entry
              ref="personalitiesZoo"
              v-for="pers in favoriteApps"
              :key="pers.uid"
              :personality="pers"
              :select_language="true"
              :full_path="pers.full_path"
              :selected="configFile.active_personality_id == configFile.personalities.findIndex(item => item === pers.full_path || item === pers.full_path+':'+pers.language)"
              :on-selected="onPersonalitySelected"
              :on-mount="mountPersonality"
              :on-un-mount="unmountPersonality"
              :on-remount="remountPersonality"
              :on-edit="editPersonality"
              :on-copy-to-custom="copyToCustom"
              :on-reinstall="onPersonalityReinstall"
              :on-settings="onSettingsPersonality"
              :on-copy-personality-name="onCopyPersonalityName"
              :on-copy-to_custom="onCopyToCustom"
              :on-open-folder="handleOpenFolder"
              :on-toggle-favorite="toggleFavorite"
            />
          </div>
        </div>
      </div>
      <div class="container mx-auto px-4 flex flex-column pb-20">
        <!-- Current Category Section -->
        <h2 class="text-2xl font-bold my-8">{{ currentCategoryName }} ({{ sortedAndFilteredApps.length }})</h2>
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8 mb-12">
          <personality-entry
            ref="personalitiesZoo"
            v-for="pers in sortedAndFilteredApps"
            :key="pers.uid"
            :personality="pers"
            :select_language="true"
            :full_path="pers.full_path"
            :selected="configFile.active_personality_id == configFile.personalities.findIndex(item => item === pers.full_path || item === pers.full_path+':'+pers.language)"
            :on-selected="onPersonalitySelected"
            :on-mount="mountPersonality"
            :on-un-mount="unmountPersonality"
            :on-remount="remountPersonality"
            :on-edit="editPersonality"
            :on-copy-to-custom="copyToCustom"
            :on-reinstall="onPersonalityReinstall"
            :on-settings="onSettingsPersonality"
            :on-copy-personality-name="onCopyPersonalityName"
            :on-copy-to_custom="onCopyToCustom"
            :on-open-folder="handleOpenFolder"
            :toggle-favorite="toggleFavorite"
          />
        </div>
      </div>
    </div>

    <!-- App details modal -->
    <div v-if="selectedApp" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 overflow-y-auto">
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

    <!-- Extra padding at the bottom -->
    <div class="h-20"></div>
  </div>
</template>


<script>
import axios from 'axios';
import PersonalityEntry from '@/components/PersonalityEntry.vue'; // Create this component for individual app cards
import { nextTick } from 'vue';

export default {
  components: {
    PersonalityEntry,
  },
  data() {
    return {
      personalities: [],
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
      sortBy: 'name',
      sortOrder: 'asc',
    };
  },
  computed: {
    currentCategoryName() {
      return this.selectedCategory=='all'?'All Personalities':this.selectedCategory;
    },           
    configFile: {
        get() {
            return this.$store.state.config;
        },
        set(value) {
            this.$store.commit('setConfig', value);
        },
    }, 
    combinedApps() {
      const installedAppNames = this.personalities.map(app => app.name);
      const localAppsMap = new Map(this.personalities.map(app => [app.name, { ...app, installed: true, existsInFolder: true }]));
      
      this.githubApps.forEach(app => {
        if (!localAppsMap.has(app.name)) {
          localAppsMap.set(app.name, { ...app, installed: false, existsInFolder: false });
        }
      });

      return Array.from(localAppsMap.values());
    },
    categories() {
      return [...new Set(this.combinedApps.map(app => app.category))]
        .sort((a, b) => a.localeCompare(b));
    },
    filteredApps() {
      return this.combinedApps.filter(app => {
        const matchesSearch = app.name.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
                              app.author.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
                              app.description.toLowerCase().includes(this.searchQuery.toLowerCase());
        const matchesCategory = this.selectedCategory === 'all' || app.category === this.selectedCategory;
        return matchesSearch && matchesCategory;
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

    async onPersonalitySelected(pers) {
            console.log('on pers', pers)
            // eslint-disable-next-line no-unused-vars
            if (this.isLoading) {
                this.$store.state.toast.showToast("Loading... please wait", 4, false)
            }
            this.isLoading = true
            console.log('selecting ', pers)
            if (pers) {

                if (pers.selected) {
                    this.$store.state.toast.showToast("Personality already selected", 4, true)
                    this.isLoading = false
                    return
                }


                //this.settingsChanged = true
                let pth = pers.language==null?pers.full_path:pers.full_path+":"+pers.language
                console.log("pth",pth)
                if (pers.isMounted && this.configFile.personalities.includes(pth)) {

                    const res = await this.select_personality(pers)
                    console.log('pers is mounted', res)
                    if (res && res.status && res.active_personality_id > -1) {
                        this.$store.state.toast.showToast("Selected personality:\n" + pers.name, 4, true)

                    } else {
                        this.$store.state.toast.showToast("Error on select personality:\n" + pers.name, 4, false)
                    }
                    this.isLoading = false

                } else {
                    console.log('mounting pers')
                    this.mountPersonality(pers)

                }


                nextTick(() => {
                    feather.replace()

                })

            }

    },

    onModelSelected(model_object) {
        // eslint-disable-next-line no-unused-vars
        if (this.isLoading) {
            this.$store.state.toast.showToast("Loading... please wait", 4, false)
            return
        }
        if (model_object) {
            if (model_object.isInstalled) {
                
                this.update_model(model_object.model.name).then((res)=>{
                    console.log("update_model",res)
                    this.configFile.model_name = model_object.model.name
                    if(res.status){
                        this.$store.state.toast.showToast("Selected model:\n" + model_object.name, 4, true)
                        nextTick(() => {
                            feather.replace()
                            this.is_loading_zoo = false
                        })
                        this.updateModelsZoo()
                        this.api_get_req("get_model_status").then((res)=>{
                            this.$store.commit('setIsModelOk', res);
                        })
                    }else{
                        this.$store.state.toast.showToast("Couldn't select model:\n" + model_object.name, 4, false)
                        nextTick(() => {
                            feather.replace()
                        })
                    }
                    this.settingsChanged = true
                    this.isModelSelected = true
                });

            } else {
                this.$store.state.toast.showToast("Model:\n" + model_object.model.name + "\nis not installed", 4, false)
            }

            nextTick(() => {
                feather.replace()

            })
        }

    },    
    toggleSortOrder() {
      this.sortOrder = this.sortOrder === 'asc' ? 'desc' : 'asc';
    },
    toggleFavorite(appUid) {
      console.log("Toggling favorite")
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
      axios.post(`/personalities/start_server`, payload)
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
    async mount_personality(pers) {
        this.$store.state.messageBox.showMessage("Loading personality")
          
          if (!pers) { return { 'status': false, 'error': 'no personality - mount_personality' } }

          try {
              const obj = {
                  client_id: this.$store.state.client_id,
                  language: pers.language?pers.language:"",
                  category: pers.category?pers.category:"",
                  folder: pers.folder?pers.folder:"",
              }
              const res = await axios.post('/mount_personality', obj, {headers: this.posts_headers});

              if (res) {

                  return res.data

              }
          } catch (error) {
              console.log(error.message, 'mount_personality - settings')
              return
          }
          this.$store.state.messageBox.hideMessage()

        },

        async select_personality(pers) {
            if (!pers) { return { 'status': false, 'error': 'no personality - select_personality' } }
            let pth = pers.language==null?pers.full_path:pers.full_path+":"+pers.language
            console.log("pth",pth)
            const id = this.configFile.personalities.findIndex(item => item === pth)

            const obj = {
                client_id: this.$store.state.client_id,
                id: id
            }


            try {
                const res = await axios.post('/select_personality', obj, {headers: this.posts_headers});

                if (res) {

                    this.$store.dispatch('refreshConfig').then(() => {
                        this.$store.dispatch('refreshPersonalitiesZoo').then(() => {
                        this.$store.dispatch('refreshMountedPersonalities');                
                        });
                    });
                    return res.data

                }
            } catch (error) {
                console.log(error.message, 'select_personality - settings')
                return
            }

        },
      async mountPersonality(pers) {
          this.isLoading = true
          console.log('mount pers', pers)

          if(pers.personality.disclaimer!=""){
              this.$store.state.messageBox.showMessage(pers.personality.disclaimer)
          }

          if (!pers) { return }

          if (this.configFile.personalities.includes(pers.personality.full_path)) {
              this.isLoading = false
              this.$store.state.toast.showToast("Personality already mounted", 4, false)

              return
          }

          const res = await this.mount_personality(pers.personality)
          console.log('mount_personality res', res)

          if (res && res.status && res.active_personality_id > -1 && res.personalities.includes(pers.personality.full_path)) {
              this.configFile.personalities = res.personalities
              this.$store.state.toast.showToast("Personality mounted", 4, true)
              pers.isMounted = true

              const res2 = await this.select_personality(pers.personality)
              if (res2.status) {
                  this.$store.state.toast.showToast("Selected personality:\n" + pers.personality.name, 4, true)

              }
              this.$store.dispatch('refreshMountedPersonalities');
              const hostnameParts = window.location.href.split('/');

              if(hostnameParts.length > 4){
                  window.location.href='/'
              }
              else{
                  window.location.reload(true);
              }
          } else {
              pers.isMounted = false
              this.$store.state.toast.showToast("Could not mount personality\nError: " + res.error + "\nResponse:\n" + res, 4, false)
          }
          this.isLoading = false

      },
      async unmountAll(){
          await axios.post('/unmount_all_personalities', {client_id: this.$store.state.client_id,}, {headers: this.posts_headers});
          this.$store.dispatch('refreshMountedPersonalities');
          this.$store.dispatch('refreshConfig');
          this.$store.state.toast.showToast("All personas unmounted", 4, true)
      },
      async unmount_personality(pers) {
          if (!pers) { return { 'status': false, 'error': 'no personality - unmount_personality' } }

          const obj = {
              client_id: this.$store.state.client_id,
              language: pers.language,
              category: pers.category,
              folder: pers.folder
          }


          try {
              const res = await axios.post('/unmount_personality', obj, {headers: this.posts_headers});

              if (res) {
                  return res.data

              }
          } catch (error) {
              console.log(error.message, 'unmount_personality - settings')
              return
          }

      },      
      async unmountPersonality(pers) {
          this.isLoading = true
          if (!pers) { return }

          const res = await this.unmount_personality(pers.personality || pers)


          if (res.status) {
              this.configFile.personalities = res.personalities
              this.$store.state.toast.showToast("Personality unmounted", 4, true)
              const persId = this.$store.state.personalities.findIndex(item => item.full_path == pers.full_path)
              const persFilteredId = this.personalitiesFiltered.findIndex(item => item.full_path == pers.full_path)
              const persIdZoo = this.$refs.personalitiesZoo.findIndex(item => item.full_path == pers.full_path)
              console.log('ppp', this.$store.state.personalities[persId])

              this.$store.state.personalities[persId].isMounted = false

              if (persFilteredId > -1) {
                  this.personalitiesFiltered[persFilteredId].isMounted = false

              }

              if (persIdZoo > -1) {
                  this.$refs.personalitiesZoo[persIdZoo].isMounted = false

              }


              //pers.isMounted = false
              this.$store.dispatch('refreshMountedPersonalities');
              // Select some other personality
              const lastPers = this.mountedPersArr[this.mountedPersArr.length - 1]

              console.log(lastPers, this.mountedPersArr.length)
              // const res2 = await this.select_personality(lastPers.personality)
              const res2 = await this.select_personality(pers.personality)
              if (res2.status) {
                  this.$store.state.toast.showToast("Selected personality:\n" + lastPers.name, 4, true)

              }


          } else {
              this.$store.state.toast.showToast("Could not unmount personality\nError: " + res.error, 4, false)
          }

          this.isLoading = false
      },
      editPersonality(pers) {
          pers=pers.personality;
          // Make a POST request to the '/get_personality_config' endpoint using Axios
          axios.post('/get_personality_config', {
              client_id:this.$store.state.client_id,
              category: pers.category,
              name: pers.folder,
          })
          .then(response => {
          const data = response.data;
          console.log("Done")
          if (data.status) {
              // Update the currentPersonConfig with the received data
              this.$store.state.currentPersonConfig = data.config;
              this.$store.state.showPersonalityEditor = true;
              this.$store.state.personality_editor.showPanel()
              this.$store.state.selectedPersonality = pers
          } else {
              // Handle the error
              console.error(data.error);
          }
          })
          .catch(error => {
          // Handle the error
          console.error(error);
          });
      },
      copyToCustom(pers) {
          pers=pers.personality;
          // Make a POST request to the '/get_personality_config' endpoint using Axios
          axios.post('/copy_to_custom_personas', {
              category: pers.category,
              name: pers.folder,
          })
          .then(response => {
              if (response.status){
                  this.$store.state.messageBox.showMessage(
                      "Personality copied to the custom personalities folder:\n"+
                      "Now it's up to you to modify it, enhance it, and maybe even share it.\n"+
                      "Feel free to add your name as an author, but please remember to keep the original creator's name as well.\n"+
                      "You have the freedom to give, sell, or keep the personas you create for yourself.\n"+
                      "The possibilities are endless, they are now yours to mold and customize as you see fit."
                  
                  )

                  this.$store.dispatch('refreshPersonalitiesZoo')
              }
              else{
                  this.$store.state.toast.showToast("Personality couldn't be copied to the custom personalities folder:\nVerify that the personality is not already copied there.", 4, false)
              }
          })
          .catch(error => {
          // Handle the error
              this.$store.state.toast.showToast("Personality couldn't be copied to the custom personalities folder:\n", 4, false)
              console.error(error);
          });
      },
      async remountPersonality(pers){
          await this.unmountPersonality(pers);
          await this.mountPersonality(pers);
      },

    onPersonalityReinstall(persItem){
        console.log('on reinstall ', persItem)
        this.isLoading = true
        console.log("Personality path:",persItem.personality.path)
        axios.post('/reinstall_personality', { client_id:this.$store.state.client_id, name: persItem.personality.path }, {headers: this.posts_headers}).then((res) => {

            if (res) {
                this.isLoading = false
                console.log('reinstall_personality', res)
                if (res.data.status) {
                    this.$store.state.toast.showToast("Personality reinstalled successfully!", 4, true)
                } else {
                    this.$store.state.toast.showToast("Could not reinstall personality", 4, false)
                }
                return res.data;
            }
            this.isLoading = false
        })
            // eslint-disable-next-line no-unused-vars

            .catch(error => {
                this.isLoading = false
                this.$store.state.toast.showToast("Could not reinstall personality\n" + error.message, 4, false)
                return { 'status': false }
            });
    },
    async handleOpenFolder(pers){
        await axios.post("/open_personality_folder",{client_id:this.$store.state.client_id, personality_folder: pers.personality.folder})
    },

    showMessage(msg, success) {
      this.message = msg;
      this.successMessage = success;
      setTimeout(() => {
        this.message = '';
      }, 3000);
    },
    loadPersonalities() {
      this.loading = true;
      // Simulate an API call or data fetching
      setTimeout(() => {
        this.personalities = this.$store.state.personalities;
        this.loading = false;
      }, 500);
    },
  },
  mounted() {
    this.loadFavoritesFromLocalStorage();
    this.loading = true
    setTimeout(() => {
      this.personalities = this.$store.state.personalities;
      this.loading = false
    }, 500);
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