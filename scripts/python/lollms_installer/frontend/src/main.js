import { createApp } from 'vue';
import { createRouter, createWebHistory } from 'vue-router';
import { createStore } from 'vuex'
import App from './App.vue';
import Install from './views/Install.vue';
import './style.css';
const routes = [
  {
    path: '/',
    name: 'Install',
    component: Install,
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});


// Create a new store instance.
export const store = createStore({
  state () {
    return {
      // count: 0,
      yesNoDialog:null,
      universalForm:null,
      toast:null,
      messageBox:null,
      api_get_req:null,
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
      mountedExtensions:[],
      bindingsZoo:[],
      modelsArr:[],
      selectedModel:null,
      personalities:[],
      diskUsage:null,
      ramUsage:null,
      vramUsage:null,
      modelsZoo:[],
      installedModels:[],
      currentModel:null,
      extensionsZoo:[],
      databases:[],
    }
  },
  mutations: {      
     
  },
  getters: {
  },
  actions: {
  }    
})

createApp(App).use(router).mount('#app');
