import { createApp, ref } from 'vue'
import { createStore } from 'vuex'
import axios from "axios";
import App from './App.vue'
import router from './router'

import './assets/tailwind.css'
//import './assets/tailwind_april_fool.css'

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
        is_rt_on:false,
        language: "english",
        languages: [],
        currentTheme: '',
        personality_editor:null,
        showPersonalityEditor: false,
        selectedPersonality:null,
        currentPersonConfig: {
          ai_name: '',
          ai_author: '',
          ai_category: '',
          ai_language: '',
          ai_description: '',
          ai_conditionning: '',
          ai_disclaimer: '',
          ai_icon: null,
        },
        posts_headers : {
          'accept': 'application/json',
          'Content-Type': 'application/json'
        },   
        client_id:"",    
        // count: 0,
        yesNoDialog:null,
        universalForm:null,
        toast:null,
        news:null,
        messageBox:null,
        api_get_req:null,
        api_post_req:null,
        startSpeechRecognition:null,
        ready:false,
        loading_infos: "",
        loading_progress: 0,
        version : "unknown",
        settingsChanged:false,
        isConnected: false, // Add the isConnected property
        isModelOk: false,
        isGenerating: false,
        config:null,
        mountedPers:null,
        mountedPersArr:[],
        bindingsZoo:[],
        modelsArr:[],
        selectedModel:null,
        personalities:[],
        diskUsage:null,
        ramUsage:null,
        vramUsage:null,
        modelsZoo:[],
        installedModels:[],
        installedBindings:[],
        currentModel:null,
        currentBinding:null,
        databases:[],
      }
    },
    mutations: {    
      
      setisRTOn(state, is_rt_on) {
        state.is_rt_on = is_rt_on;
      },

      setLanguages(state, languages) {
        state.languages = languages;
      },
      setLanguage(state, language) {
        state.language = language;
      },
      
        
      setIsReady(state, ready) {
        state.ready = ready;
      },
      setIsConnected(state, isConnected) {
        state.isConnected = isConnected;
      },
      setIsModelOk(state, isModelOk) {
        state.isModelOk = isModelOk;
      },
      setIsGenerating(state, isGenerating) {
        state.isGenerating = isGenerating;
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
      setbindingsZoo(state, bindingsZoo) {
        state.bindingsZoo = bindingsZoo;
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
      setModelsZoo(state, modelsZoo) {
        state.modelsZoo = modelsZoo;
      },   
      setCurrentBinding(state, currentBinding){
        state.currentBinding = currentBinding
      },
      setCurrentModel(state, currentModel) {
        state.currentModel = currentModel;
      },   
         
      setDatabases(state, databases) {
        state.databases = databases;
      },
      
      // increment (state) {
      //   state.count++
      // }
      setTheme(theme) {
        this.currentTheme = theme;
      }      
    },
    getters: {
      
      getisRTOn(state) {
        return state.is_rt_on;
      },      
      getLanguages(state) {
        return state.languages;
      },      
      getLanguage(state) {
        return state.language;
      },      
      getIsConnected(state) {
        return state.isConnected
      },
      getIsModelOk(state) {
        return state.isModelOk;
      },
      getIsGenerating(state) {
        return state.isGenerating
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
      getbindingsZoo(state) {
        return state.bindingsZoo;
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
      
      getDatabasesList(state){
        return state.databases;
      },
      getModelsZoo(state) {
        return state.modelsZoo;
      },
      getCyrrentBinding(state){
        return state.currentBinding
      },
      getCurrentModel(state) {
        return state.currentModel;
      },
    },
    actions: {
      async getVersion(){
        try{
          let res = await axios.get('/get_lollms_webui_version', {});
          if (res) {
              this.state.version = res.data
              console.log("version res:", res)
              console.log("version :", this.state.version)
          }
  
        }
        catch{
          console.log("Coudln't get version")
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
      async refreshDatabase({ commit }) {
        let databases = await api_get_req("list_databases")
        console.log("databases:",databases)
        commit('setDatabases', databases);
      },
      async fetchisRTOn({ commit }) {
        console.log("is_rt_on", this.state.client_id)
        const response = await axios.get(
                    '/is_rt_on'
                  );
            
        console.log("response", response)
        const is_rt_on = response.data.status;
        console.log("is_rt_on", is_rt_on)
        commit('setRTOn', is_rt_on);
      },
      async fetchLanguages({ commit }) {
        console.log("get_personality_languages_list", this.state.client_id)
        const response = await axios.post(
                    '/get_personality_languages_list',
                    {client_id: this.state.client_id}
                  );
            
        console.log("response", response)
        const languages = response.data;
        console.log("languages", languages)
        commit('setLanguages', languages);
      },
      async fetchLanguage({ commit }) {
        console.log("get_personality_language", this.state.client_id)
        const response = await axios.post(
                    '/get_personality_language',
                    {client_id: this.state.client_id}
                  );
            
        console.log("response", response)
        const language = response.data;
        console.log("language", language)
        commit('setLanguage', language);
      },
      
      async changeLanguage({ commit }, new_language) {
        console.log("Changing language to ", new_language)
          let response = await axios.post('/set_personality_language', {
            client_id: this.state.client_id,
              language: new_language,
          })
          console.log("get_personality_languages_list", this.state.client_id)
          response = await axios.post(
                      '/get_personality_languages_list',
                      {client_id: this.state.client_id}
                    );
              
          console.log("response", response)
          const languages = response.data;
          console.log("languages", languages)
          commit('setLanguages', languages);          
          response = await axios.post(
                      '/get_personality_language',
                      {client_id: this.state.client_id}
                    );
              
          console.log("response", response)
          const language = response.data;
          console.log("language", language)
          commit('setLanguage', language);

          console.log('Language changed successfully:', response.data.message);
      },
      async deleteLanguage({ commit }, new_language) {
        console.log("Deleting ", new_language)
          let response = await axios.post('/del_personality_language', {
            client_id: this.state.client_id,
              language: new_language,
          })
          console.log("get_personality_languages_list", this.state.client_id)
          response = await axios.post(
                      '/get_personality_languages_list',
                      {client_id: this.state.client_id}
                    );
              
          console.log("response", response)
          const languages = response.data;
          console.log("languages", languages)
          commit('setLanguages', languages);          
          response = await axios.post(
                      '/get_personality_language',
                      {client_id: this.state.client_id}
                    );
              
          console.log("response", response)
          const language = response.data;
          console.log("language", language)
          commit('setLanguage', language);

          console.log('Language changed successfully:', response.data.message);
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
                      else{
                        item.language = null
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
              if(parts.length>1){
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
          let bindingsZoo = await api_get_req("list_bindings")
          console.log("Loaded bindings zoo :",bindingsZoo)
          this.state.installedBindings = bindingsZoo.filter(item=> item.installed)
          console.log("Loaded bindings zoo ", this.state.installedBindings)
          commit('setbindingsZoo',bindingsZoo)
          const index = bindingsZoo.findIndex(item=>item.name == this.state.config.binding_name)
          if (index!=-1){
            commit('setCurrentBinding',bindingsZoo[index])
          }
  
      },
      async refreshModelsZoo({ commit }) {
        console.log("Fetching models")
        const response = await axios.get('/get_available_models');
        const models_zoo = response.data.filter(model => model.variants &&  model.variants.length>0)
        console.log(`get_available_models: ${models_zoo}`)
        commit('setModelsZoo', models_zoo)
      },
      async refreshModelStatus({ commit }) {
        let modelstatus = await api_get_req("get_model_status");
        commit('setIsModelOk',modelstatus["status"])
      },
      async refreshModels({ commit }) {
        console.log("Fetching models")
        let modelsArr = await api_get_req("list_models");
        console.log(`Found ${modelsArr}`)
        let selectedModel = await api_get_req('get_active_model');
        console.log("Selected model ", selectedModel);
        if(selectedModel!=undefined){
          commit('setselectedModel',selectedModel["model"])
        }
        commit('setModelsArr',modelsArr)
        console.log("setModelsArr",modelsArr)
        console.log("this.state.modelsZoo",this.state.modelsZoo)
        this.state.modelsZoo.map((item)=>{
          item.isInstalled=modelsArr.includes(item.name)
        })
        this.state.installedModels = this.state.modelsZoo.filter(item=> item.isInstalled)
        const index = this.state.modelsZoo.findIndex(item=>item.name == this.state.config.model_name)
        if (index!=-1){
          commit('setCurrentModel',this.state.modelsZoo[index])
        }
    },
      async refreshDiskUsage({ commit }) {
        this.state.diskUsage = await api_get_req("disk_usage")
      },
      async refreshRamUsage({ commit }) {
        this.state.ramUsage = await api_get_req("ram_usage")
      },      
      async refreshVramUsage({ commit }) {
        const resp = await api_get_req("vram_usage")
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

async function api_post_req(endpoint, client_id) {
  try {
      const res = await axios.post("/" + endpoint, {client_id: client_id});

      if (res) {

          return res.data

      }
  } catch (error) {
      console.log(error.message, 'api_post_req - settings')
      return
  }

}

async function refreshHardwareUsage(store) {
  await store.dispatch('refreshDiskUsage');
  await store.dispatch('refreshRamUsage');
  await store.dispatch('refreshVramUsage');
}
let actionsExecuted = false;

app.mixin({
  async created() {
    if (!actionsExecuted) {
      this.$store.state.api_get_req = api_get_req
      this.$store.state.api_post_req = api_post_req

      actionsExecuted = true;
      console.log("Calling")
      
      try{
        this.$store.state.loading_infos = "Getting version"
        this.$store.state.loading_progress = 30
        await this.$store.dispatch('getVersion');
      }
      catch (ex){
        console.log("Error cought:", ex)
      }


      try{
        this.$store.state.loading_infos = "Loading Configuration"
        this.$store.state.loading_progress = 10
        await this.$store.dispatch('refreshConfig');
        console.log("Config ready")
      }
      catch (ex){
        console.log("Error cought:", ex)
      }
      try{
        this.$store.state.loading_infos = "Loading Database"
        this.$store.state.loading_progress = 20
        await this.$store.dispatch('refreshDatabase');
      }
      catch (ex){
        console.log("Error cought:", ex)
      }

      try{
        this.$store.state.loading_infos = "Getting Bindings list"
        this.$store.state.loading_progress = 40
        await this.$store.dispatch('refreshBindings');
      }
      catch (ex){
        console.log("Error cought:", ex)
      }
      try{
        this.$store.state.loading_infos = "Getting Hardware usage"
        await refreshHardwareUsage(this.$store);
      }
      catch (ex){
        console.log("Error cought:", ex)
      }
   
      try{
        this.$store.state.loading_infos = "Getting personalities zoo"
        this.$store.state.loading_progress = 70
        await this.$store.dispatch('refreshPersonalitiesZoo')
      }
      catch (ex){
        console.log("Error cought:", ex)
      }
      try{
        this.$store.state.loading_infos = "Getting mounted personalities"
        this.$store.state.loading_progress = 80
        await this.$store.dispatch('refreshMountedPersonalities');
      }
      catch (ex){
        console.log("Error cought:", ex)
      }

      try{
        this.$store.state.loading_infos = "Getting models zoo"
        this.$store.state.loading_progress = 90
        await this.$store.dispatch('refreshModelsZoo');
      }
      catch (ex){
        console.log("Error cought:", ex)
      }
      try{
        this.$store.state.loading_infos = "Getting active models"
        this.$store.state.loading_progress = 100
        await this.$store.dispatch('refreshModels');
        await this.$store.dispatch('refreshModelStatus');
      }
      catch (ex){
        console.log("Error cought:", ex)
      }
    
      try{
        await this.$store.dispatch('fetchLanguages');
        await this.$store.dispatch('fetchLanguage');
      }
      catch (ex){
        console.log("Error cought:", ex)
      }
      try{
        await this.$store.dispatch('fetchisRTOn');
      }
      catch (ex){
        console.log("Error cought:", ex)
      }

      
      this.$store.state.ready = true;
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

export{logObjectProperties, copyObject, flattenObject, refreshHardwareUsage }
