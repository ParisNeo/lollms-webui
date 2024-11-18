import { createApp, ref } from 'vue'
import { createStore } from 'vuex'
import axios from "axios";
import App from './App.vue'
import router from './router'

import './assets/tailwind.css'
//import './assets/tailwind_april_fool.css'

const app = createApp(App)

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
        theme_vars: {lollms_title:"LoLLMS", falling_object:"L", activate_dropping_animation:false, lollms_welcome_short_message:"Welcome to LoLLMS WebUI", lollms_welcome_message:"Embark on a journey through the realm of advanced AI with LoLLMS, your ultimate companion for intelligent conversations and multimodal interactions. Unleash the power of large language models and explore new frontiers in artificial intelligence."},
        personalities_ready: false,
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
        leftPanelCollapsed:  false, // Default value
        rightPanelCollapsed:  true, // Default value
        view_mode: localStorage.getItem('lollms_webui_view_mode') || 'compact', // Default value
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
      updatePersonality(state, newPersonality){
        const index = state.personalities.findIndex(p => p.full_path === newPersonality.full_path);
        if (index !== -1) {
            state.personalities[index]=newPersonality;
        }
        else{
          console.log("Can't uipdate personality beceause it was Not found:",newPersonality.full_path)
        }
      },
      setThemeVars(state, themeVars){
        state.theme_vars = themeVars;
      },
      setLeftPanelCollapsed(state, status) {
        state.leftPanelCollapsed = status;
        console.log(`Saving the status of left panel to ${status}`)
        localStorage.setItem('lollms_webui_left_panel_collapsed', status); // Sync with localStorage
      },
      setRightPanelCollapsed(state, status) {
        state.rightPanelCollapsed = status;
        console.log(`Saving the status of right panel to ${status}`)
        localStorage.setItem('lollms_webui_right_panel_collapsed', status); // Sync with localStorage
      },

      setViewMode(state, mode) {
        state.view_mode = mode;
        localStorage.setItem('lollms_webui_view_mode', mode); // Sync with localStorage
      },
      
      setpersonalitiesReady(state, personalities_ready) {
        state.personalities_ready = personalities_ready;
      },
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
      getThemeVars(state){
        return state.theme_vars;
      },
      getLeftPanelCollapsed(state) {
        return state.leftPanelCollapsed;
      },
      getRightPanelCollapsed(state) {
        return state.rightPanelCollapsed;
      },
      getViewMode(state){
        return state.view_mode;
      },
      
      getpersonalitiesReady(state){
        return state.personalities_ready;
      },
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
          }
  
        }
        catch{
          console.error("Coudln't get version")
        }
      },
      async refreshConfig({ commit }) {
        console.log("Fetching configuration");
        try {
          console.log("Fetching configuration with client id: ", this.state.client_id);
          const configFile = await api_post_req('get_config', this.state.client_id)
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
        const response = await axios.get(
                    '/is_rt_on'
                  );
            
        const is_rt_on = response.data.status;
        commit('setisRTOn', is_rt_on);
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
          await this.dispatch('refreshMountedPersonalities');

          console.log('Language changed successfully:', language);
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
              
          const languages = response.data;
          commit('setLanguages', languages);          
          response = await axios.post(
                      '/get_personality_language',
                      {client_id: this.state.client_id}
                    );
              
          const language = response.data;
          commit('setLanguage', language);
      },
      async refreshPersonalitiesZoo({ commit }) {
          let personalities = []
          const catdictionary = await api_get_req("get_all_personalities")
          const catkeys = Object.keys(catdictionary); // returns categories

          for (let j = 0; j < catkeys.length; j++) {
              const catkey = catkeys[j];
              const personalitiesArray = catdictionary[catkey];
              const modPersArr = personalitiesArray.map((item) => {
                  let isMounted = false;
                  for(const personality of this.state.config.personalities){
                    if(personality.includes(catkey + '/' + item.folder)){
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
        const indicesToRemove = [];
        for (let i = 0; i < this.state.config.personalities.length; i++) {
            const full_path_item = this.state.config.personalities[i]
            const index = this.state.personalities.findIndex(item => item.full_path == full_path_item)
            if(index>=0){
              let pers = copyObject(this.state.personalities[index])
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
          this.state.config.personalities.splice(indicesToRemove[i], 1);
          
          if(this.state.config.active_personality_id>indicesToRemove[i]){
            this.state.config.active_personality_id -= 1;
          }
        }

        commit('setMountedPersArr', mountedPersArr);
        const current_personality = this.state.personalities[this.state.personalities.findIndex(item => item.full_path == this.state.config.personalities[this.state.config.active_personality_id])]
        console.log("Setting current mounted personality: ",current_personality)
        this.state.mountedPers = current_personality
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
        const response = await axios.get('/get_available_models');
        const models_zoo = response.data;//.filter(model => model.variants &&  model.variants.length>0)
        commit('setModelsZoo', models_zoo)
      },
      async refreshModelStatus({ commit }) {
        let modelstatus = await api_get_req("get_model_status");
        commit('setIsModelOk',modelstatus["status"])
      },
      async refreshModels({ commit }) {
        let modelsArr = await api_get_req("list_models");
        let selectedModel = await api_get_req('get_active_model');
        if(selectedModel!=undefined){
          commit('setselectedModel',selectedModel["model"])
        }
        commit('setModelsArr',modelsArr)
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


let actionsExecuted = false;

app.mixin({
  async created() {
    if (!actionsExecuted) {
      this.$store.state.api_get_req = api_get_req
      this.$store.state.api_post_req = api_post_req
    }
  },
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

export{logObjectProperties, copyObject, flattenObject }
