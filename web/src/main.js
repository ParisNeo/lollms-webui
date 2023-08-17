import { createApp, ref } from 'vue'
import { createStore } from 'vuex'
import axios from "axios";
import App from './App.vue'
import router from './router'

import './assets/tailwind.css'

const app = createApp(App)
console.log("Loaded main.js")

// Create a new store instance.
export const store = createStore({
    state () {
      return {
        // count: 0,
        ready:false,
        settingsChanged:false,
        isConnected: false, // Add the isConnected property
        config:null,
        mountedPers:null,
        mountedPersArr:null,
        bindingsArr:null,
        modelsArr:null,
        models_zoo:null,
        personalities:null,
        diskUsage:null,
        ramUsage:null,
        vramUsage:null,
        extensionsZoo:null,
      }
    },
    mutations: {
      setIsConnected(state, isConnected) {
        state.isConnected = isConnected;
      },
      setConfig(state, config) {
        state.config = config;
      },
      setPersonalities(state, personalities) {
        state.personalities = personalities;
      },
      setMountedPers(state, mountedPers) {
        state.mountedPers = mountedPers;
      },
      setMountedPersArr(state, mountedPersArr) {
        state.mountedPersArr = mountedPersArr;
      },
      setBindingsArr(state, bindingsArr) {
        state.bindingsArr = bindingsArr;
      },
      setModelsArr(state, modelsArr) {
        state.modelsArr = modelsArr;
      },
      setDiskUsage(state, diskUsage) {
        state.diskUsage = diskUsage;
      },
      setRamUsage(state, ramUsage) {
        state.ramUsage = ramUsage;
      },
      setVramUsage(state, vramUsage) {
        state.vramUsage = vramUsage;
      },
      
      setExtensionsZoo(state, extensionsZoo) {
        state.extensionsZoo = extensionsZoo;
      },
      setModelsZoo(state, modelsZoo) {
        state.models_zoo = modelsZoo;
      },
      // increment (state) {
      //   state.count++
      // }    
    },
    getters: {
      getIsConnected(state) {
        return state.isConnected
      },
      getConfig(state) {
        return state.config
      },
      getPersonalities(state) {
        return state.personalities;
      },
      getMountedPersArr(state) {
        return state.mountedPersArr;
      },
      getMountedPers(state) {
        return state.mountedPers;
      },
      getbindingsArr(state) {
        return state.bindingsArr;
      },
      getModelsArr(state) {
        return state.modelsArr;
      },
      getDiskUsage(state) {
        return state.diskUsage;
      },
      getRamUsage(state) {
        return state.ramUsage;
      },
      getVramUsage(state) {
        return state.vramUsage;
      },
      getModelsZoo(state) {
        return state.models_zoo;
      },
      getExtensionsZoo(state) {
        return state.extensionsZoo;
      },
    },
    actions: {

      async refreshConfig({ commit }) {
        console.log("Fetching configuration");
        try {
          const configFile = await api_get_req('get_config')
          let personality_path_infos = configFile.personalities[configFile.active_personality_id].split("/")
          //let personality_path_infos = await this.api_get_req("get_current_personality_path_infos")
          configFile.personality_category = personality_path_infos[0]
          configFile.personality_folder = personality_path_infos[1]

          commit('setConfig', configFile);
        } catch (error) {
          console.log(error.message, 'refreshConfig');
          // Handle error
        }
      },
      async refreshPersonalitiesArr({ commit }) {
          let personalities = []
          const catdictionary = await api_get_req("get_all_personalities")
          const catkeys = Object.keys(catdictionary); // returns categories

          for (let j = 0; j < catkeys.length; j++) {
              const catkey = catkeys[j];
              const personalitiesArray = catdictionary[catkey];
              const modPersArr = personalitiesArray.map((item) => {

                  const isMounted = this.state.config.personalities.includes(catkey + '/' + item.folder)
                  // if (isMounted) {
                  //     console.log(item)
                  // }
                  let newItem = {}
                  newItem = item
                  newItem.category = catkey // add new props to items
                  newItem.full_path = catkey + '/' + item.folder // add new props to items
                  newItem.isMounted = isMounted // add new props to items
                  return newItem
              })


              if (personalities.length == 0) {
                  personalities = modPersArr
              } else {
                  personalities = personalities.concat(modPersArr)
              }
          }

          personalities.sort((a, b) => a.name.localeCompare(b.name))

          commit('setPersonalities', personalities);

          console.log("Done loading personalities")
      },
      refreshMountedPersonalities({ commit }) {
          let mountedPersArr = []
          // console.log('perrs listo',this.state.personalities)
          for (let i = 0; i < this.state.config.personalities.length; i++) {
              const full_path_item = this.state.config.personalities[i]
              const index = this.state.personalities.findIndex(item => item.full_path == full_path_item)

              const pers = this.state.personalities[index]
              if (pers) {
                  mountedPersArr.push(pers)
              }
              else {
                  mountedPersArr.push(this.state.personalities[this.state.personalities.findIndex(item => item.full_path == "english/generic/lollms")])
              }
          }
          console.log("Personalities list",this.state.personalities)
          commit('setMountedPersArr', mountedPersArr);
          
          console.log("active_personality_id",this.state.config.active_personality_id)
          console.log("selected pers",this.state.config.personalities[this.state.config.active_personality_id])
          this.state.mountedPers = this.state.personalities[this.state.personalities.findIndex(item => item.full_path == this.state.config.personalities[this.state.config.active_personality_id])]
          console.log("selected pers",this.state.mountedPers)

      },
      async refreshBindings({ commit }) {
          let bindingsArr = await api_get_req("list_bindings")
          commit('setBindingsArr',bindingsArr)
      },
      async refreshModels({ commit }) {
          let modelsArr = await api_get_req("list_models")
          commit('setModelsArr',modelsArr)
      },
      async refreshExtensionsZoo({ commit }) {
          let extensionsZoo = await api_get_req("list_extensions")
          commit('setExtensionsZoo',extensionsZoo)
      },

      async refreshDiskUsage({ commit }) {
        this.state.diskUsage = await api_get_req("disk_usage")
      },
      async refreshRamUsage({ commit }) {
        this.state.ramUsage = await api_get_req("ram_usage")
      },      
      async refreshVramUsage({ commit }) {
        console.log("getting gpu data")
        const resp = await api_get_req("vram_usage")
        // {
        //   "gpu_0_total_vram": 11811160064,
        //   "gpu_0_used_vram": 3177185280,
        //   "nb_gpus": 1
        // }

        const gpuArr = []

        if (resp.nb_gpus > 0) {
            // Get keys
            const keys = Object.keys(resp)
            // for each gpu
            for (let i = 0; i < resp.nb_gpus; i++) {




                const total_vram = resp[`gpu_${i}_total_vram`];
                const used_vram = resp[`gpu_${i}_used_vram`];
                const model = resp[`gpu_${i}_model`];
                const percentage = (used_vram / total_vram) * 100
                const available_space = total_vram - used_vram



                gpuArr.push({
                    total_vram: total_vram,
                    used_vram: used_vram,
                    gpu_index: i,
                    gpu_model: model,
                    percentage: percentage.toFixed(2),
                    available_space: available_space
                });

            }
            const result = {

                "nb_gpus": resp.nb_gpus,
                "gpus": gpuArr
            }
            console.log('gpu usage: ',result)
            this.state.vramUsage = result

        }
        else{
            const result = {
            "nb_gpus": 0,
            "gpus": []
            }
            console.log('gpu usage: ',result)
            this.state.vramUsage = result

        }

      },
      async refreshModelsZoo({ commit }) {
        console.log("Refreshing models zoo")
        axios.get('/get_available_models')
        .then(response => {
            console.log("found models")
            let models_zoo = response.data
            models_zoo.sort((a, b) => a.title.localeCompare(b.title))

            // Returns array of model filenames which are = to title of models zoo entry
            for (let i = 0; i < this.state.modelsArr.length; i++) {
              const customModel = this.state.modelsArr[i]
              const index = models_zoo.findIndex(x => x.title == customModel)

              if (index == -1) {
                  let newModelEntry = {}
                  newModelEntry.title = customModel
                  newModelEntry.path = customModel
                  newModelEntry.icon = ""
                  newModelEntry.isCustomModel = true
                  newModelEntry.isInstalled = true
                  models_zoo.push(newModelEntry)
              }
            }
            models_zoo.sort((a, b) => {
                if (a.isInstalled && !b.isInstalled) {
                    return -1; // a is installed, b is not installed, so a comes first
                } else if (!a.isInstalled && b.isInstalled) {
                    return 1; // b is installed, a is not installed, so b comes first
                } else {
                    return 0; // both models are either installed or not installed, maintain their original order
                }
            });
            
            models_zoo.forEach(model => {
                if (model.title == this.state.config["model_name"]) {
                    model.selected = true;
                }
                else{
                  model.selected = false; 
                }
            });            
            commit('setModelsZoo', models_zoo)
            console.log("Models zoo loaded successfully")

        })
        .catch(error => {
            console.log(error.message, 'fetchModels');
        });        
      },
      fetchCustomModels({ commit }) {
          axios.get('/list_models')
              .then(response => {



              })
              .catch(error => {
                  console.log(error.message, 'fetchCustomModels');
              });
      },      
    }    
})
async function api_get_req(endpoint) {
  try {
    const res = await axios.get('/' + endpoint);

    if (res) {
      return res.data;
    }
  } catch (error) {
    console.log(error.message, 'api_get_req');
    throw error;
  }
}

let actionsExecuted = false;

app.mixin({
  created() {
    if (!actionsExecuted) {
      actionsExecuted = true;
      console.log("Calling")
      this.$store.dispatch('refreshConfig').then(() => {
          console.log("recovered config")
          this.$store.dispatch('refreshPersonalitiesArr').then(() => {
          this.$store.dispatch('refreshMountedPersonalities');
          this.$store.dispatch('refreshBindings');
          this.$store.dispatch('refreshModels');
    
          this.$store.dispatch('refreshDiskUsage');
          this.$store.dispatch('refreshRamUsage');
          this.$store.dispatch('refreshVramUsage');
          this.$store.dispatch('refreshModelsZoo');
          this.$store.dispatch('refreshExtensionsZoo');
          
          
          this.$store.state.ready = true
          console.log("done loading data")
  
        });
      });
    }

  },
  beforeMount() {
  }
})
app.use(router)
app.use(store)
app.mount('#app')

