import { createApp } from 'vue'
import { createStore } from 'vuex'
import axios from "axios";
import App from './App.vue'
import router from './router'

import './assets/tailwind.css'

const app = createApp(App)
const STARRED_LOCAL_STORAGE_KEY = 'lollms_starred_personalities';
const STARRED_FUNCTIONS_LOCAL_STORAGE_KEY = 'lollms_starred_functions';
const STARRED_DISCUSSIONS_LOCAL_STORAGE_KEY = 'lollms_starred_discussions';
const STARRED_APPS_LOCAL_STORAGE_KEY = 'lollms_starred_apps';

function copyObject(obj) {
  if (obj === null || typeof obj !== 'object') {
    return obj;
  }
  if (obj instanceof Date) {
    return new Date(obj.getTime());
  }
  if (Array.isArray(obj)) {
    const arrCopy = [];
    for (let i = 0; i < obj.length; i++) {
      arrCopy[i] = copyObject(obj[i]);
    }
    return arrCopy;
  }
  const objCopy = {};
  for (const key in obj) {
    if (Object.prototype.hasOwnProperty.call(obj, key)) {
      objCopy[key] = copyObject(obj[key]);
    }
  }
  return objCopy;
}

function loadStarredFromLocalStorage(key, description) {
    try {
        const stored = localStorage.getItem(key);
        return stored ? JSON.parse(stored) : [];
    } catch (e) {
        console.error(`Failed to load starred ${description} from localStorage:`, e);
        saveStarredToLocalStorage(key,[], description);
        return [];
    }
}

function saveStarredToLocalStorage(key, starredItems, description) {
    try {
        localStorage.setItem(key, JSON.stringify(starredItems));
    } catch (e) {
        console.error(`Failed to save starred ${description} to localStorage:`, e);
    }
}

export const store = createStore({
    state () {
      return {
        theme_vars: {lollms_title:"LoLLMS", falling_object:"L", activate_dropping_animation:false, lollms_welcome_short_message:"Welcome to LoLLMS WebUI", lollms_welcome_message:"Embark on a journey through the realm of advanced AI with LoLLMS, your ultimate companion for intelligent conversations and multimodal interactions. Unleash the power of large language models and explore new frontiers in artificial intelligence."},
        personalities_ready: false,
        is_rt_on:false,
        topBarPinned:false,
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
        leftPanelCollapsed: localStorage.getItem('lollms_webui_left_panel_collapsed') === 'true',
        rightPanelCollapsed: localStorage.getItem('lollms_webui_right_panel_collapsed') !== 'false', // Default to true if not set or false
        view_mode: localStorage.getItem('lollms_webui_view_mode') || 'compact',
        yesNoDialog:null,
        universalForm:null,
        saveConfiguration:null,
        toast:null,
        news:null,
        messageBox:null,
        api_get_req:null,
        api_post_req:null,
        startSpeechRecognition:null,
        ready:false,
        loading_infos: "",
        loading_progress: 0,
        progress_value:0,
        version : "unknown",
        settingsChanged:false,
        isConnected: false,
        isModelOk: false,
        isGenerating: false,
        config:null,
        mountedPers:null,
        mountedPersArr:[],
        bindingsZoo:[],
        modelsArr:[],
        selectedModel:null,
        personalities:[],
        functions:[], // Added state for functions if managed globally
        starredPersonalities: loadStarredFromLocalStorage(STARRED_LOCAL_STORAGE_KEY, 'personalities'),
        starredFunctions: loadStarredFromLocalStorage(STARRED_FUNCTIONS_LOCAL_STORAGE_KEY, 'functions'),
        starredDiscussions: loadStarredFromLocalStorage(STARRED_DISCUSSIONS_LOCAL_STORAGE_KEY, 'discussions'),
        starredApps: loadStarredFromLocalStorage(STARRED_APPS_LOCAL_STORAGE_KEY, 'apps'),
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
      setThemeVars(state, themeVars){ state.theme_vars = themeVars; },
      setPersonalitiesReady(state, personalities_ready) { state.personalities_ready = personalities_ready; },
      setIsRtOn(state, is_rt_on) { state.is_rt_on = is_rt_on; },
      setTopBarPinned(state, topBarPinned) { state.topBarPinned = topBarPinned; },
      setLanguage(state, language) { state.language = language; },
      setLanguages(state, languages) { state.languages = languages; },
      setCurrentTheme(state, theme) { state.currentTheme = theme; },
      setPersonalityEditor(state, editor) { state.personality_editor = editor; },
      setShowPersonalityEditor(state, show) { state.showPersonalityEditor = show; },
      setSelectedPersonality(state, personality) { state.selectedPersonality = personality; },
      setCurrentPersonConfig(state, config) { state.currentPersonConfig = config; },
      setPostsHeaders(state, headers) { state.posts_headers = headers; },
      setClientId(state, id) { state.client_id = id; },
      setLeftPanelCollapsed(state, status) {
        state.leftPanelCollapsed = status;
        localStorage.setItem('lollms_webui_left_panel_collapsed', status);
      },
      setRightPanelCollapsed(state, status) {
        state.rightPanelCollapsed = status;
        localStorage.setItem('lollms_webui_right_panel_collapsed', status);
      },
      setViewMode(state, mode) {
        state.view_mode = mode;
        localStorage.setItem('lollms_webui_view_mode', mode);
      },
      setFunctions(state, functions) { state.functions = functions; },
      setStarredFunctions(state, starredPaths) {
          state.starredFunctions = starredPaths;
          saveStarredToLocalStorage(STARRED_FUNCTIONS_LOCAL_STORAGE_KEY, starredPaths, 'functions');
      },
      setStarredDiscussions(state, starredIds) {
          state.starredDiscussions = starredIds;
          saveStarredToLocalStorage(STARRED_DISCUSSIONS_LOCAL_STORAGE_KEY, starredIds, 'discussions');
      },
      setStarredApps(state, starredApps) {
          state.starredApps = starredApps;
          saveStarredToLocalStorage(STARRED_APPS_LOCAL_STORAGE_KEY, starredApps, 'apps');
      },
    
      setYesNoDialog(state, dialog) { state.yesNoDialog = dialog; },
      setUniversalForm(state, form) { state.universalForm = form; },
      setSaveConfiguration(state, saveFn) { state.saveConfiguration = saveFn; },
      setToast(state, toast) { state.toast = toast; },
      setNews(state, news) { state.news = news; },
      setMessageBox(state, box) { state.messageBox = box; },
      setApiGetReq(state, fn) { state.api_get_req = fn; },
      setApiPostReq(state, fn) { state.api_post_req = fn; },
      setStartSpeechRecognition(state, fn) { state.startSpeechRecognition = fn; },
      setIsReady(state, ready) { state.ready = ready; },
      setLoadingInfos(state, infos) { state.loading_infos = infos; },
      setLoadingProgress(state, progress) { state.loading_progress = progress; },
      setProgressValue(state, progress_value) { state.progress_value = progress_value; },
      setVersion(state, version) { state.version = version; },
      setSettingsChanged(state, changed) { state.settingsChanged = changed; },
      setIsConnected(state, isConnected) { state.isConnected = isConnected; },
      setIsModelOk(state, isModelOk) { state.isModelOk = isModelOk; },
      setIsGenerating(state, isGenerating) { state.isGenerating = isGenerating; },
      setConfig(state, config) { state.config = config; },
      setMountedPers(state, mountedPers) { state.mountedPers = mountedPers; },
      setMountedPersArr(state, mountedPersArr) { state.mountedPersArr = mountedPersArr; },
      setBindingsZoo(state, bindingsZoo) { state.bindingsZoo = bindingsZoo; },
      setModelsArr(state, modelsArr) { state.modelsArr = modelsArr; },
      setSelectedModel(state, selectedModel) { state.selectedModel = selectedModel; },
      setPersonalities(state, personalities) { state.personalities = personalities; },
      setStarredPersonalities(state, starredPaths) {
        state.starredPersonalities = starredPaths;
        saveStarredToLocalStorage(STARRED_LOCAL_STORAGE_KEY, starredPaths, 'personalities');
      },
      addStarredPersonality(state, personalityPath) {
        if (!state.starredPersonalities.includes(personalityPath)) {
            state.starredPersonalities.push(personalityPath);
            saveStarredToLocalStorage(STARRED_LOCAL_STORAGE_KEY, state.starredPersonalities, 'personalities');
        }
      },
      removeStarredPersonality(state, personalityPath) {
          const index = state.starredPersonalities.indexOf(personalityPath);
          if (index > -1) {
              state.starredPersonalities.splice(index, 1);
              saveStarredToLocalStorage(STARRED_LOCAL_STORAGE_KEY, state.starredPersonalities, 'personalities');
          }
      },
      addStarredFunction(state, functionPath) {
          if (!state.starredFunctions.includes(functionPath)) {
              state.starredFunctions.push(functionPath);
              saveStarredToLocalStorage(STARRED_FUNCTIONS_LOCAL_STORAGE_KEY, state.starredFunctions, 'functions');
          }
      },
      removeStarredFunction(state, functionPath) {
          const index = state.starredFunctions.indexOf(functionPath);
          if (index > -1) {
              state.starredFunctions.splice(index, 1);
              saveStarredToLocalStorage(STARRED_FUNCTIONS_LOCAL_STORAGE_KEY, state.starredFunctions, 'functions');
          }
      },
      addStarredDiscussion(state, discussionId) {
          if (!state.starredDiscussions.includes(discussionId)) {
              state.starredDiscussions.push(discussionId);
              saveStarredToLocalStorage(STARRED_DISCUSSIONS_LOCAL_STORAGE_KEY, state.starredDiscussions, 'discussions');
          }
      },
      removeStarredDiscussion(state, discussionId) {
          const index = state.starredDiscussions.indexOf(discussionId);
          if (index > -1) {
              state.starredDiscussions.splice(index, 1);
              saveStarredToLocalStorage(STARRED_DISCUSSIONS_LOCAL_STORAGE_KEY, state.starredDiscussions, 'discussions');
          }
      },
      addStarredApp(state, starredApp) {
          if (!state.starredApps.includes(starredApp)) {
              state.starredDiscussions.push(starredApp);
              saveStarredToLocalStorage(STARRED_APPS_LOCAL_STORAGE_KEY, state.starredDiscussions, 'apps');
          }
      },
    
      removeStarredApp(state, appPath) {
          const index = state.starredApps.indexOf(appPath);
          if (index > -1) {
              state.starredApps.splice(index, 1);
              saveStarredToLocalStorage(STARRED_APPS_LOCAL_STORAGE_KEY, state.starredApps, 'apps');
          }
      },
      setDiskUsage(state, diskUsage) { state.diskUsage = diskUsage; },
      setRamUsage(state, ramUsage) { state.ramUsage = ramUsage; },
      setVramUsage(state, vramUsage) { state.vramUsage = vramUsage; },
      setModelsZoo(state, modelsZoo) { state.modelsZoo = modelsZoo; },
      setInstalledModels(state, installedModels){ state.installedModels = installedModels; },
      setInstalledBindings(state, installedBindings){ state.installedBindings = installedBindings; },
      setCurrentModel(state, currentModel) { state.currentModel = currentModel; },
      setCurrentBinding(state, currentBinding){ state.currentBinding = currentBinding; },
      setDatabases(state, databases) { state.databases = databases; },
      updateFunction(state, newFunctionData){
          const index = state.functions.findIndex(f => (f.id || f.full_path) === (newFunctionData.id || newFunctionData.full_path));
          if (index !== -1) {
              const updatedFunc = { ...state.functions[index], ...newFunctionData };
              state.functions.splice(index, 1, updatedFunc);
          } else {
            console.warn("Couldn't update function (not found):", newFunctionData.full_path);
          }
      },
      updatePersonality(state, newPersonality){
        const index = state.personalities.findIndex(p => (p.id || p.full_path) === (newPersonality.id || newPersonality.full_path));
        if (index !== -1) {
            const updatedPers = { ...state.personalities[index], ...newPersonality };
            state.personalities.splice(index, 1, updatedPers);
        } else {
          console.warn("Couldn't update personality (not found):", newPersonality.full_path);
        }

        const mountedIndex = state.mountedPersArr.findIndex(p => (p.id || p.full_path) === (newPersonality.id || newPersonality.full_path));
        if (mountedIndex !== -1) {
            const updatedMountedPers = { ...state.mountedPersArr[mountedIndex], ...newPersonality };
            state.mountedPersArr.splice(mountedIndex, 1, updatedMountedPers);
        }

        if (state.selectedPersonality && (state.selectedPersonality.id || state.selectedPersonality.full_path) === (newPersonality.id || newPersonality.full_path)) {
            state.selectedPersonality = { ...state.selectedPersonality, ...newPersonality };
        }

        if (state.mountedPers && (state.mountedPers.id || state.mountedPers.full_path) === (newPersonality.id || newPersonality.full_path)) {
            state.mountedPers = { ...state.mountedPers, ...newPersonality };
        }
      },
    },
    getters: {
      getThemeVars: state => state.theme_vars,
      getPersonalitiesReady: state => state.personalities_ready,
      getIsRtOn: state => state.is_rt_on,
      getTopBarPinned: state => state.topBarPinned,
      getLanguage: state => state.language,
      getLanguages: state => state.languages,
      getCurrentTheme: state => state.currentTheme,
      getPersonalityEditor: state => state.personality_editor,
      getShowPersonalityEditor: state => state.showPersonalityEditor,
      getSelectedPersonality: state => state.selectedPersonality,
      getCurrentPersonConfig: state => state.currentPersonConfig,
      getPostsHeaders: state => state.posts_headers,
      getClientId: state => state.client_id,
      getLeftPanelCollapsed: state => state.leftPanelCollapsed,
      getRightPanelCollapsed: state => state.rightPanelCollapsed,
      getViewMode: state => state.view_mode,
      getYesNoDialog: state => state.yesNoDialog,
      getUniversalForm: state => state.universalForm,
      getSaveConfiguration: state => state.saveConfiguration,
      getToast: state => state.toast,
      getNews: state => state.news,
      getMessageBox: state => state.messageBox,
      getApiGetReq: state => state.api_get_req,
      getApiPostReq: state => state.api_post_req,
      getStartSpeechRecognition: state => state.startSpeechRecognition,
      getIsReady: state => state.ready,
      getLoadingInfos: state => state.loading_infos,
      getLoadingProgress: state => state.loading_progress,
      getProgressValue: state => state.progress_value,
      getVersion: state => state.version,
      getSettingsChanged: state => state.settingsChanged,
      getIsConnected: state => state.isConnected,
      getIsModelOk: state => state.isModelOk,
      getIsGenerating: state => state.isGenerating,
      getConfig: state => state.config,
      getMountedPers: state => state.mountedPers,
      getMountedPersArr: state => state.mountedPersArr,
      getBindingsZoo: state => state.bindingsZoo,
      getModelsArr: state => state.modelsArr,
      getSelectedModel: state => state.selectedModel,
      getPersonalities: state => state.personalities,
      getStarredPersonalities: state => state.starredPersonalities,
      getDiskUsage: state => state.diskUsage,
      getRamUsage: state => state.ramUsage,
      getVramUsage: state => state.vramUsage,
      getModelsZoo: state => state.modelsZoo,
      getInstalledModels: state => state.installedModels,
      getInstalledBindings: state => state.installedBindings,
      getCurrentModel: state => state.currentModel,
      getCurrentBinding: state => state.currentBinding,
      getDatabases: state => state.databases,
      getFunctions: state => state.functions,
      getStarredFunctions: state => state.starredFunctions,
      getStarredDiscussions: state => state.starredDiscussions,
      setStarredApps: state => state.starredApps
    },
    actions: {
      async fetchIsRtOn({ commit }) {
        try {
          const response = await axios.get('/is_rt_on');
          commit('setIsRtOn', response?.data?.status || false);
        } catch(error) {
            console.error("Error fetching RT status:", error);
            commit('setIsRtOn', false);
        }
      },
      async getVersion({ commit }){
        try{
          let res = await axios.get('/get_lollms_webui_version', {});
          if (res && res.data) {
            const data = res.data;
            let versionString = "";
            if(data.version_type && data.version_type !== ""){
              versionString = `${data.version_main}.${data.version_secondary} ${data.version_type} (${data.version_codename})`;
            } else {
              versionString = `${data.version_main}.${data.version_secondary} (${data.version_codename})`;
            }
            commit('setVersion', versionString);
          }
        }
        catch(error) {
          console.error("Couldn't get version:", error);
          commit('setVersion', 'unknown (error)');
        }
      },
        toggleStarFunction({ commit, state }, func) {
          if (!func || !func.full_path) {
              console.warn("Attempted to toggle star on invalid function:", func);
              return;
          }
          const functionPath = func.full_path;
          const isCurrentlyStarred = state.starredFunctions.includes(functionPath);

          if (isCurrentlyStarred) {
              commit('removeStarredFunction', functionPath);
          } else {
              commit('addStarredFunction', functionPath);
          }
      },
      toggleStarPersonality({ commit, state, dispatch }, personality) {
          if (!personality || !personality.full_path) {
              console.warn("Attempted to toggle star on invalid personality:", personality);
              return;
          }
          const personalityPath = personality.full_path;
          const isCurrentlyStarred = state.starredPersonalities.includes(personalityPath);

          if (isCurrentlyStarred) {
              commit('removeStarredPersonality', personalityPath);
          } else {
              commit('addStarredPersonality', personalityPath);
          }
          dispatch('updatePersonalityStarredStatus', { personalityPath, isStarred: !isCurrentlyStarred });
      },
      toggleStarDiscussion({ commit, state }, discussion) {
        if (!discussion || typeof discussion.id === 'undefined') {
            console.warn("Attempted to toggle star on invalid discussion:", discussion);
            return;
        }
        const discussionId = discussion.id;
        const isCurrentlyStarred = state.starredDiscussions.includes(discussionId);

        if (isCurrentlyStarred) {
            commit('removeStarredDiscussion', discussionId);
        } else {
            commit('addStarredDiscussion', discussionId);
        }
        // No global discussion list update action needed unless discussions are managed in Vuex state
    },
    toggleStarApp({ commit, state }, app) {
      if (!app || typeof app.id === 'undefined') {
          console.warn("Attempted to toggle star on invalid app:", app);
          return;
      }
      const appId = app.id;
      const isCurrentlyStarred = state.starredDiscussions.includes(appId);

      if (isCurrentlyStarred) {
          commit('removeStarredApp', appId);
      } else {
          commit('addStarredApp', appId);
      }
      // No global discussion list update action needed unless discussions are managed in Vuex state
  },    
      // eslint-disable-next-line no-unused-vars
      async refreshConfig({ commit, state }) {
        console.log("Fetching configuration");
        try {
          const configData = await api_post_req('get_config');

          if (!configData) {
             throw new Error("Received null or undefined config file");
          }
          let configFile = copyObject(configData);

          if (!configFile.personalities || configFile.personalities.length === 0) {
              configFile.personalities = ["generic/lollms"];
              configFile.active_personality_id = 0;
          } else if(configFile.active_personality_id < 0 || configFile.active_personality_id >= configFile.personalities.length) {
              configFile.active_personality_id = 0;
          }

          const activePersonalityPath = configFile.personalities[configFile.active_personality_id];
          if (activePersonalityPath && typeof activePersonalityPath === 'string') {
              const personality_path_infos = activePersonalityPath.split('/');
              if (personality_path_infos.length >= 2) {
                   configFile.personality_category = personality_path_infos[0];
                   configFile.personality_folder = personality_path_infos[1].split(':')[0];
              } else {
                   configFile.personality_category = "unknown";
                   configFile.personality_folder = "unknown";
              }
          } else {
               configFile.personality_category = "unknown";
               configFile.personality_folder = "unknown";
          }

          commit('setConfig', configFile);
          commit('setSettingsChanged', false);
        } catch (error) {
          console.error('Error during refreshConfig:', error);
          commit('setSettingsChanged', false);
        }
      },

      async refreshDatabase({ commit }) {
        try {
          let databases = await api_get_req("list_databases");
          commit('setDatabases', databases || []);
        } catch(error) {
            console.error("Error refreshing databases:", error);
            commit('setDatabases', []);
        }
      },
      async fetchLanguages({ commit, state }) {
        try {
          const response = await axios.post('/get_personality_languages_list', { client_id: state.client_id });
          commit('setLanguages', response?.data || []);
        } catch(error) {
            console.error("Error fetching languages list:", error);
            commit('setLanguages', []);
        }
      },

      async fetchLanguage({ commit, state }) {
        try {
          const response = await axios.post('/get_personality_language', { client_id: state.client_id });
          commit('setLanguage', response?.data || 'english');
        } catch (error) {
            console.error("Error fetching current language:", error);
            commit('setLanguage', 'english');
        }
      },

      async changeLanguage({ dispatch, state }, new_language) {
        try {
          let response = await api_post_req('set_personality_language', { language: new_language });

          if(response?.status){
              await dispatch('fetchLanguage');
              await dispatch('fetchLanguages');
              await dispatch('refreshMountedPersonalities');
          } else {
              console.error("Failed to set language:", response?.error);
              state.toast?.showToast(`Failed to set language: ${response?.error || 'Unknown error'}`, 4, false);
          }
        } catch (error) {
            console.error("Error changing language:", error);
        }
      },

      async deleteLanguage({ dispatch, state }, language_to_delete) {
        try {
          let response = await api_post_req('/del_personality_language', { language: language_to_delete });
          if(response?.status){
              await dispatch('fetchLanguage');
              await dispatch('fetchLanguages');
              await dispatch('refreshMountedPersonalities');
          } else {
              console.error("Failed to delete language:", response?.error);
              state.toast?.showToast(`Failed to delete language: ${response?.error || 'Unknown error'}`, 4, false);
          }
        } catch (error) {
            console.error("Error deleting language:", error);
        }
      },

      async refreshPersonalitiesZoo({ commit, state }) {
          try {
              let personalities = [];
              const catdictionary = await api_get_req("get_all_personalities");
              const mountedSet = new Set(state.config?.personalities || []);
              const starredSet = new Set(state.starredPersonalities || []);

              if (!catdictionary) {
                   commit('setPersonalities', []);
                   commit('setPersonalitiesReady', false);
                   return;
              }
              const catkeys = Object.keys(catdictionary);

              for (let j = 0; j < catkeys.length; j++) {
                  const catkey = catkeys[j];
                  const personalitiesArray = catdictionary[catkey];
                  if (!Array.isArray(personalitiesArray)) continue;

                  const modPersArr = personalitiesArray.map((item) => {
                      if (!item || typeof item !== 'object' || !item.folder) return null;
                      const full_path = `${catkey}/${item.folder}`;
                      const langPaths = Array.isArray(item.languages) ? item.languages.map(lang => `${full_path}:${lang}`) : [];
                      const isMounted = mountedSet.has(full_path) || langPaths.some(lp => mountedSet.has(lp));
                      const isStarred = starredSet.has(full_path);

                      return {
                          ...item,
                          category: catkey,
                          full_path: full_path,
                          id: item.id || full_path,
                          isMounted: isMounted,
                          isStarred: isStarred,
                          isProcessing: false,
                      };
                  }).filter(item => item !== null);
                  personalities = personalities.concat(modPersArr);
              }

              personalities.sort((a, b) => (a.name || '').localeCompare(b.name || ''));
              commit('setPersonalities', personalities);
              commit('setPersonalitiesReady', true);

          } catch (error) {
              console.error("Error refreshing personalities zoo:", error);
              commit('setPersonalities', []);
              commit('setPersonalitiesReady', false);
          }
      },

      refreshMountedPersonalities({ commit, state }) {
        if (!state.config || !state.config.personalities || !state.personalities) {
            commit('setMountedPersArr', []);
            commit('setMountedPers', null);
            return;
        }

        let currentConfig = copyObject(state.config);
        let mountedPersArr = [];
        const indicesToRemove = [];
        const personalitiesMap = new Map(state.personalities.map(p => [p.full_path, p]));
        const starredSet = new Set(state.starredPersonalities || []);

        for (let i = 0; i < currentConfig.personalities.length; i++) {
            const full_path_item = currentConfig.personalities[i];
            const basePath = typeof full_path_item === 'string' ? full_path_item.split(':')[0] : null;

            if (basePath && personalitiesMap.has(basePath)) {
                let pers = copyObject(personalitiesMap.get(basePath));
                pers.language = typeof full_path_item === 'string' && full_path_item.includes(':') ? full_path_item.split(':')[1] : '';
                pers.isMounted = true;
                pers.isStarred = starredSet.has(basePath);
                mountedPersArr.push(pers);
            } else {
                indicesToRemove.push(i);
            }
        }

        for (let i = indicesToRemove.length - 1; i >= 0; i--) {
            const removedIndex = indicesToRemove[i];
            currentConfig.personalities.splice(removedIndex, 1);
            if (currentConfig.active_personality_id >= removedIndex) {
                if (currentConfig.active_personality_id === removedIndex) {
                     currentConfig.active_personality_id = currentConfig.personalities.length > 0 ? 0 : -1;
                } else {
                    currentConfig.active_personality_id -= 1;
                }
            }
        }
         if (currentConfig.active_personality_id < 0 && currentConfig.personalities.length > 0) {
            currentConfig.active_personality_id = 0;
         } else if (currentConfig.personalities.length === 0) {
             currentConfig.active_personality_id = -1;
         }


        commit('setMountedPersArr', mountedPersArr);

        if (currentConfig.active_personality_id >= 0 && currentConfig.active_personality_id < mountedPersArr.length) {
            commit('setMountedPers', mountedPersArr[currentConfig.active_personality_id]);
        } else {
            commit('setMountedPers', null);
        }

        if (indicesToRemove.length > 0) {
            commit('setConfig', currentConfig);
        }
      },

      async refreshBindings({ commit, state }) {
        try {
            let bindingsZoo = await api_get_req("list_bindings");
            if (!Array.isArray(bindingsZoo)) bindingsZoo = [];

            const installedBindings = bindingsZoo.filter(item => item && item.installed);
            commit('setInstalledBindings', installedBindings);
            commit('setBindingsZoo', bindingsZoo);

            const currentBindingName = state.config?.binding_name;
            if (currentBindingName) {
                const currentBinding = bindingsZoo.find(item => item && item.name === currentBindingName);
                commit('setCurrentBinding', currentBinding || null);
            } else {
                 commit('setCurrentBinding', null);
            }
        } catch (error) {
            console.error("Error refreshing bindings zoo:", error);
            commit('setBindingsZoo', []);
            commit('setInstalledBindings', []);
            commit('setCurrentBinding', null);
        }
      },

      async refreshModelStatus({ commit }) {
        try {
          let modelstatus = await api_get_req("get_model_status");
          commit('setIsModelOk', modelstatus?.status || false);
        } catch(error) {
            console.error("Error refreshing model status:", error);
            commit('setIsModelOk', false);
        }
      },

      async refreshModelsZoo({ commit }) {
        try {
          const response = await axios.get('/get_available_models');
           if (!Array.isArray(response?.data)) {
               commit('setModelsZoo', []);
           } else {
               commit('setModelsZoo', response.data);
           }
        } catch (error) {
            console.error("Error refreshing models zoo:", error);
            commit('setModelsZoo', []);
        }
      },

      async refreshModels({ commit, state }) {
          try {
              let modelsArr = await api_get_req("list_models");
              if (!Array.isArray(modelsArr)) modelsArr = [];
              commit('setModelsArr', modelsArr);

              let selectedModelInfo = await api_get_req('get_active_model');
              const selectedModelName = selectedModelInfo?.model || state.config?.model_name;
              commit('setSelectedModel', selectedModelName || null);

              const modelsZoo = state.modelsZoo || [];
              const modelsArrSet = new Set(modelsArr);
              modelsZoo.forEach(item => {
                   if (item && item.name) item.isInstalled = modelsArrSet.has(item.name);
              });
              commit('setModelsZoo', [...modelsZoo]);

              let installedModels = modelsZoo.filter(item => item && item.isInstalled);
              const zooModelNames = new Set(modelsZoo.map(item => item?.name).filter(Boolean));
              const customModelNames = modelsArr.filter(modelName => !zooModelNames.has(modelName));

              const imgBinding = state.currentBinding?.icon || '/bindings/default_binding.png';
              const installedCustomModels = customModelNames.map(modelName => ({
                  name: modelName, icon: imgBinding, isCustomModel: true, isInstalled: true,
              }));

              installedModels = [...installedModels, ...installedCustomModels];
              commit('setInstalledModels', installedModels);

              const currentModel = modelsZoo.find(item => item && item.name === selectedModelName);
               if (currentModel) {
                   commit('setCurrentModel', currentModel);
               } else if (selectedModelName) {
                    const customModelEntry = installedCustomModels.find(m => m.name === selectedModelName);
                    commit('setCurrentModel', customModelEntry || null);
               } else {
                   commit('setCurrentModel', null);
               }
          } catch (error) {
              console.error("Error refreshing models:", error);
              commit('setModelsArr', []);
              commit('setSelectedModel', null);
              commit('setInstalledModels', []);
              commit('setCurrentModel', null);
          }
      },

      async refreshDiskUsage({ commit }) {
        try {
          let usage = await api_get_req("disk_usage");
          commit('setDiskUsage', usage);
        } catch (error) {
            console.error("Error refreshing disk usage:", error);
            commit('setDiskUsage', null);
        }
      },

      async refreshRamUsage({ commit }) {
        try {
          let usage = await api_get_req("ram_usage");
          commit('setRamUsage', usage);
        } catch (error) {
            console.error("Error refreshing RAM usage:", error);
            commit('setRamUsage', null);
        }
      },

      async refreshVramUsage({ commit }) {
        try {
            const resp = await api_get_req("vram_usage");
            const gpuArr = [];
            let result = { nb_gpus: 0, gpus: [] };

            if (resp && resp.nb_gpus > 0) {
                result.nb_gpus = resp.nb_gpus;
                for (let i = 0; i < resp.nb_gpus; i++) {
                    const total_vram = resp[`gpu_${i}_total_vram`] || 0;
                    const used_vram = resp[`gpu_${i}_used_vram`] || 0;
                    const model = resp[`gpu_${i}_model`] || 'N/A';
                    const percentage = total_vram > 0 ? ((used_vram / total_vram) * 100).toFixed(2) : 0;
                    const available_space = total_vram - used_vram;

                    gpuArr.push({
                        total_vram: total_vram, used_vram: used_vram, gpu_index: i, gpu_model: model,
                        percentage: percentage, available_space: available_space
                    });
                }
                 result.gpus = gpuArr;
            }
            commit('setVramUsage', result);
        } catch (error) {
             console.error("Error refreshing VRAM usage:", error);
             commit('setVramUsage', { nb_gpus: 0, gpus: [] });
        }
      },

      updatePersonalityStarredStatus({ commit, state }, { personalityPath, isStarred }) {
         const personality = state.personalities.find(p => p.full_path === personalityPath);
         if (personality) {
             commit('updatePersonality', { ...personality, isStarred: isStarred });
         } else {
            console.warn("Could not find personality in main list to update starred status:", personalityPath);
         }
      },

      // eslint-disable-next-line no-unused-vars
      async applyConfiguration({ commit, state, dispatch }) {
          try {
              const res = await axios.post('/apply_settings', { client_id:state.client_id, config: state.config }, { headers: state.posts_headers });
              if (res.data.status) {
                 state.toast.showToast("Settings applied. Refreshing...", 4, true);
                  // Assuming refreshConfigInView exists in the component context where this action is called
                  // If not, need to call refreshConfig directly or handle UI refresh differently
                  // await this.refreshConfigInView(); // This line might cause issues if 'this' is not the component instance
                  await dispatch('refreshConfig'); // Refresh store config state
              } else {
                 state.toast.showToast(`Apply failed: ${res.data.error || 'Error'}`, 4, false);
              }
          } catch (error) {
             state.toast.showToast(`Error applying settings: ${error.message || error}`, 4, false);
          }
      },
      async saveConfiguration({ state }) {
            // Typically isLoading and loading_text are component-local state, not Vuex state
            // We'll assume the component calling this action handles its own loading state
          try {
              const res = await axios.post('/save_settings', { client_id:state.client_id }, { headers: state.posts_headers });
              if (res.data.status) state.toast.showToast("Settings saved successfully.", 4, true);
              else state.messageBox.showMessage(`Error saving settings: ${res.data.error || 'Error'}`);
          } catch (error) {state.messageBox.showMessage(`Error saving settings: ${error.message}`);
          }
      },
    }
})

async function api_get_req(endpoint) {
  try {
    const res = await axios.get(`/${endpoint}`);
    return res?.data;
  } catch (error) {
    console.error(`API GET request error for /${endpoint}:`, error.message);
    store.state.toast?.showToast(`API Error (GET ${endpoint}): ${error.message}`, 4, false);
    throw error;
  }
}

async function api_post_req(endpoint, data = {}) {
  try {
      const payload = { ...data, client_id: store.state.client_id };
      const res = await axios.post(`/${endpoint}`, payload, { headers: store.state.posts_headers });
      return res?.data;
  } catch (error) {
      console.error(`API POST request error for /${endpoint}:`, error.message);
      store.state.toast?.showToast(`API Error (POST ${endpoint}): ${error.message}`, 4, false);
      throw error;
  }
}

app.mixin({
  created() {
    if (!this.$store.state.api_get_req) {
        this.$store.commit('setApiGetReq', api_get_req);
    }
    if (!this.$store.state.api_post_req) {
        this.$store.commit('setApiPostReq', api_post_req);
    }
  },
})

function logObjectProperties(obj) {
  if (typeof obj !== 'object' || obj === null) {
    return;
  }
  let logString = "Object properties:\n";
  for (const key in obj) {
    if (Object.prototype.hasOwnProperty.call(obj, key) && typeof obj[key] !== 'function') {
      logString += `${key}: ${JSON.stringify(obj[key])}\n`;
    }
  }
  console.log(logString);
}


function flattenObject(obj, parentKey = "", separator = "/") {
  let result = [];
  for (const key in obj) {
    if (Object.prototype.hasOwnProperty.call(obj, key)) {
      const newKey = parentKey ? `${parentKey}${separator}${key}` : key;
      const value = obj[key];
      if (typeof value === "object" && value !== null && !Array.isArray(value)) {
        const nestedFields = flattenObject(value, newKey, separator);
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

export { logObjectProperties, copyObject, flattenObject }