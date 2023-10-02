import { createApp, ref } from 'vue'
import { createStore } from 'vuex'
import axios from "axios";
import App from './App.vue'
import router from './router'

import './assets/tailwind.css'

const app = createApp(App)
console.log("Loaded main.js")

function copyObject(obj) {
  const copy = {};
  for (const key in obj) {
    if (obj.hasOwnProperty(key)) {
      copy[key] = obj[key];
    }
  }
  return copy;
}

// Create a new store instance.
export const store = createStore({
    state () {
      return {
        // count: 0,
        ready:false,
        version : "unknown",
        settingsChanged:false,
        isConnected: false, // Add the isConnected property
        config:null,
        mountedPers:null,
        mountedPersArr:null,
        bindingsArr:null,
        modelsArr:null,
        selectedModel:null,
        personalities:null,
        diskUsage:null,
        ramUsage:null,
        vramUsage:null,
        extensionsZoo:null,
        activeExtensions:null,
      }
    },
    mutations: {      
      setIsReady(state, ready) {
        state.ready = ready;
      },
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
      setselectedModel(state, selectedModel) {
        state.selectedModel = selectedModel;
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
      
      setActiveExtensions(state, activeExtensions) {
        state.activeExtensions = activeExtensions;
      },
      setExtensionsZoo(state, extensionsZoo) {
        state.extensionsZoo = extensionsZoo;
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
      
      getActiveExtensions(state) {
        return state.activeExtensions;
      },
      getExtensionsZoo(state) {
        return state.extensionsZoo;
      },
    },
    actions: {
      async getVersion(){
        let res = await axios.get('/get_lollms_webui_version', {});
        if (res) {
            this.state.version = res.data.version
        }
      },
      async refreshConfig({ commit }) {
        console.log("Fetching configuration");
        try {
          const configFile = await api_get_req('get_config')
          if(configFile.active_personality_id<0){
            configFile.active_personality_id=0;
          }
          let personality_path_infos = configFile.personalities[configFile.active_personality_id].split("/")
          //let personality_path_infos = await this.api_get_req("get_current_personality_path_infos")
          configFile.personality_category = personality_path_infos[0]
          configFile.personality_folder = personality_path_infos[1]
          console.log("Recovered config")
          console.log(configFile)
          console.log("Committing config");
          console.log(configFile)
          console.log(this.state.config)
          commit('setConfig', configFile);
        } catch (error) {
          console.log(error.message, 'refreshConfig');
          // Handle error
        }
      },
      async refreshPersonalitiesZoo({ commit }) {
          let personalities = []
          const catdictionary = await api_get_req("get_all_personalities")
          const catkeys = Object.keys(catdictionary); // returns categories
          console.log("Personalities recovered:"+this.state.config.personalities)

          for (let j = 0; j < catkeys.length; j++) {
              const catkey = catkeys[j];
              const personalitiesArray = catdictionary[catkey];
              const modPersArr = personalitiesArray.map((item) => {
                  let isMounted = false;

                  for(const personality of this.state.config.personalities){
                    if(personality.includes(catkey + '/' + item.folder)){
                      isMounted = true;
                      if(personality.includes(":")){
                        const parts = personality.split(':');
                        item.language = parts[1];
                      }
                    }
                  }
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
        if(this.state.config.active_personality_id<0){
          this.state.config.active_personality_id=0;
        }
        let mountedPersArr = []
        // console.log('perrs listo',this.state.personalities)
        const indicesToRemove = [];
        for (let i = 0; i < this.state.config.personalities.length; i++) {
            const full_path_item = this.state.config.personalities[i]
            const parts = full_path_item.split(':')
            const index = this.state.personalities.findIndex(item => item.full_path == full_path_item || item.full_path == parts[0])
            if(index>=0){
              let pers = copyObject(this.state.personalities[index])
              if(parts.length>0){
                pers.language = parts[1]
              }
              // console.log(`Personality : ${JSON.stringify(pers)}`)
              if (pers) {
                  mountedPersArr.push(pers)
              }
              else {
                  mountedPersArr.push(this.state.personalities[this.state.personalities.findIndex(item => item.full_path == "generic/lollms")])
              }
            }
            else{
              indicesToRemove.push(i)
              console.log("Couldn't load personality : ",full_path_item)
            }
        }
        // Remove the broken personalities using the collected indices
        for (let i = indicesToRemove.length - 1; i >= 0; i--) {
          console.log("Removing personality : ",this.state.config.personalities[indicesToRemove[i]])
          this.state.config.personalities.splice(indicesToRemove[i], 1);
          
          if(this.state.config.active_personality_id>indicesToRemove[i]){
            this.state.config.active_personality_id -= 1;
          }
        }

        commit('setMountedPersArr', mountedPersArr);
        
        this.state.mountedPers = this.state.personalities[this.state.personalities.findIndex(item => item.full_path == this.state.config.personalities[this.state.config.active_personality_id] || item.full_path+':'+item.language ==this.state.config.personalities[this.state.config.active_personality_id])]
        // console.log(`${this.state.config.personalities[this.state.config.active_personality_id]}`)
        // console.log(`Mounted personality: ${this.state.mountedPers}`)
      },
      async refreshBindings({ commit }) {
          let bindingsArr = await api_get_req("list_bindings")
          commit('setBindingsArr',bindingsArr)
      },
      async refreshModels({ commit }) {
          console.log("Fetching models")
          let modelsArr = await api_get_req("list_models");
          console.log(`Found ${modelsArr}`)
          let selectedModel = await api_get_req('get_active_model');
          if(selectedModel!=undefined){
            commit('setselectedModel',selectedModel["model"])
          }
            
          commit('setModelsArr',modelsArr)
      },
      async refreshExtensionsZoo({ commit }) {
          let extensions = []
          let catdictionary = await api_get_req("list_extensions")
          const catkeys = Object.keys(catdictionary); // returns categories
          console.log("Extensions recovered:"+this.state.config.extensions)

          for (let j = 0; j < catkeys.length; j++) {
              const catkey = catkeys[j];
              const extensionsArray = catdictionary[catkey];
              const modExtArr = extensionsArray.map((item) => {
                  let isMounted = false;

                  for(const extension of this.state.config.personalities){
                    if(extension.includes(catkey + '/' + item.folder)){
                      isMounted = true;
                    }
                  }
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


              if (extensions.length == 0) {
                  extensions = modExtArr
              } else {
                  extensions = extensions.concat(modExtArr)
              }
          }

          extensions.sort((a, b) => a.name.localeCompare(b.name))

          commit('setActiveExtensions', this.state.config.extensions);

          console.log("Done loading extensions")

          commit('setExtensionsZoo',extensions)
      },

      async refreshDiskUsage({ commit }) {
        this.state.diskUsage = await api_get_req("disk_usage")
      },
      async refreshRamUsage({ commit }) {
        this.state.ramUsage = await api_get_req("ram_usage")
      },      
      async refreshVramUsage({ commit }) {
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
  async created() {
    if (!actionsExecuted) {
      actionsExecuted = true;
      console.log("Calling")
      await this.$store.dispatch('refreshConfig');
      console.log("recovered config : ${}");
      await this.$store.dispatch('getVersion');
      console.log("recovered version");          
      await this.$store.dispatch('refreshBindings');

      await this.$store.dispatch('refreshDiskUsage');
      await this.$store.dispatch('refreshRamUsage');
      await this.$store.dispatch('refreshVramUsage');
      await this.$store.dispatch('refreshExtensionsZoo');
      await this.$store.dispatch('refreshModels');
      
      await this.$store.dispatch('refreshPersonalitiesZoo')
      await this.$store.dispatch('refreshMountedPersonalities');
      this.$store.state.ready = true;
      console.log("store status = ", this.$store.state.ready);
    console.log("done loading data")
    }

  },
  beforeMount() {
  }
})

function logObjectProperties(obj) {
  if (typeof obj !== 'object' || obj === null) {
    console.log('Invalid object');
    return;
  }

  let logString = "Object parameters and values:\n";
  
  for (const key in obj) {
    if (Object.prototype.hasOwnProperty.call(obj, key) && typeof obj[key] !== 'function') {
      logString += `${key}: ${obj[key]}\n`;
    }
  }

  console.log(logString);
}

function flattenObject(obj, parentKey = "") {
  let result = [];

  for (const key in obj) {
    if (obj.hasOwnProperty(key)) {
      const newKey = parentKey ? `${parentKey}/${key}` : key;

      if (typeof obj[key] === "object") {
        const nestedFields = flattenObject(obj[key], newKey);
        result = result.concat(nestedFields);
      } else {
        result.push(newKey);
      }
    }
  }

  return result;
}

app.use(router)
app.use(store)
app.mount('#app')

export{logObjectProperties, copyObject, flattenObject}