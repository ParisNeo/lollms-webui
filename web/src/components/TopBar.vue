<template>
    <header v-if="isFullMode" class="top-0 shadow-lg navbar-container">
      <nav class="container flex flex-col lg:flex-row items-center gap-2 pb-0">
        <!-- LOGO -->
        <RouterLink :to="{ name: 'discussions' }" class="flex items-center space-x-2"> <!-- Added space-x-2 -->
          <div class="logo-container"> <!-- Removed mr-1 -->
            <img class="w-12 h-12 rounded-full object-cover logo-image" 
                :src="$store.state.config == null ? storeLogo : $store.state.config.app_custom_logo != '' ? '/user_infos/' + $store.state.config.app_custom_logo : storeLogo" 
                alt="Logo" title="LoLLMS WebUI">
          </div>
          <div class="flex flex-col justify-center">
            <div class="text-6xl md:text-2xl font-bold text-amber-500 mb-2"
                style="text-shadow: 2px 2px 0px white, -2px -2px 0px white, 2px -2px 0px white, -2px 2px 0px white;">
                L🌟LLMS
          </div>
            <p class="text-gray-400 text-sm">One tool to rule them all</p>
          </div>
        </RouterLink>
  
        <!-- SYSTEM STATUS -->
        <div class="flex gap-3 flex-1 items-center justify-end">
          <div v-if="isModelOK" title="Model is ok" class="text-green-500 dark:text-green-400 cursor-pointer transition-transform hover:scale-110">
            <svg class="w-8 h-8" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M9 12L11 14L15 10" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <div v-else title="Model is not ok" class="text-red-500 dark:text-red-400 cursor-pointer transition-transform hover:scale-110">
            <svg class="w-8 h-8" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M15 9L9 15" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M9 9L15 15" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <div v-if="!isGenerating" title="Text is not being generated. Ready to generate" class="text-green-500 dark:text-green-400 cursor-pointer transition-transform hover:scale-110">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 21v-4m0 0V5a2 2 0 012-2h6.5l1 1H21l-3 6 3 6h-8.5l-1-1H5a2 2 0 00-2 2zm9-13.5V9"></path>
            </svg>
          </div>
          <div v-else title="Generation in progress..." class="text-yellow-500 dark:text-yellow-400 cursor-pointer transition-transform hover:scale-110">
            <svg class="w-6 h-6 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
            </svg>
          </div>
          <div v-if="isConnected" title="Connection status: Connected" class="text-green-500 dark:text-green-400 cursor-pointer transition-transform hover:scale-110">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
            </svg>
          </div>
          <div v-else title="Connection status: Not connected" class="text-red-500 dark:text-red-400 cursor-pointer transition-transform hover:scale-110">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636"></path>
            </svg>
          </div>
        </div>
          <div class="flex items-center space-x-4">
            <ActionButton @click="restartProgram" icon="power" title="restart program" />
            <ActionButton @click="refreshPage" icon="refresh-ccw" title="refresh page" />
            <ActionButton href="/docs" icon="file-text" title="Fast API doc" />
          </div>

          <!-- SOCIALS -->
          <div class="flex items-center space-x-4">
            <SocialIcon href="https://github.com/ParisNeo/lollms-webui" icon="github" />
            <SocialIcon href="https://www.youtube.com/channel/UCJzrg0cyQV2Z30SQ1v2FdSQ" icon="youtube" />
            <SocialIcon href="https://x.com/ParisNeo_AI" icon="x" />
            <SocialIcon href="https://discord.com/channels/1092918764925882418" icon="discord" />
          </div>
  
          <div class="relative group" title="Lollms News">
            <div @click="showNews()" class="text-2xl w-8 h-8 cursor-pointer transition-colors duration-300 text-gray-600 hover:text-primary dark:text-gray-300 dark:hover:text-primary">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="w-full h-full">
                <path d="M19 20H5a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2v1m2 13a2 2 0 0 1-2-2V7m2 13a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z"></path>
              </svg>
            </div>
            <span class="absolute hidden group-hover:block bg-gray-800 text-white text-xs rounded py-1 px-2 top-full left-1/2 transform -translate-x-1/2 mt-2 whitespace-nowrap">
              Lollms News
            </span>
          </div>

          <div class="relative group">
              <div 
                v-if="is_fun_mode" 
                title="Fun mode is on, press to turn off" 
                class="w-8 h-8 cursor-pointer text-green-500 dark:text-green-400 hover:text-green-600 dark:hover:text-green-300 transition-colors duration-300"
                @click="fun_mode_off()"
              >
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="w-full h-full animate-bounce">
                  <circle cx="12" cy="12" r="10"></circle>
                  <path d="M8 14s1.5 2 4 2 4-2 4-2"></path>
                  <line x1="9" y1="9" x2="9.01" y2="9"></line>
                  <line x1="15" y1="9" x2="15.01" y2="9"></line>
                </svg>
              </div>
              <div 
                v-else 
                title="Fun mode is off, press to turn on" 
                class="w-8 h-8 cursor-pointer text-gray-500 dark:text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors duration-300"
                @click="fun_mode_on()"
              >
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="w-full h-full">
                  <circle cx="12" cy="12" r="10"></circle>
                  <line x1="8" y1="15" x2="16" y2="15"></line>
                  <line x1="9" y1="9" x2="9.01" y2="9"></line>
                  <line x1="15" y1="9" x2="15.01" y2="9"></line>
                </svg>
              </div>
              <span class="absolute hidden group-hover:block bg-gray-800 text-white text-xs rounded py-1 px-2 top-full left-1/2 transform -translate-x-1/2 mb-2 whitespace-nowrap">
                {{ is_fun_mode ? 'Turn off fun mode' : 'Turn on fun mode' }}
              </span>
            </div>          
          <div class="language-selector relative">
            <button @click="toggleLanguageMenu" class="bg-transparent text-black dark:text-white py-1 px-1 rounded font-bold uppercase transition-colors duration-300 hover:bg-blue-500">
              {{ $store.state.language.slice(0, 2) }}
            </button>
            <div v-if="isLanguageMenuVisible" ref="languageMenu" class="container language-menu absolute left-0 mt-1 bg-white dark:bg-bg-dark-tone rounded shadow-lg z-10 overflow-y-auto scrollbar-thin scrollbar-track-bg-light-tone scrollbar-thumb-bg-light-tone-panel hover:scrollbar-thumb-primary dark:scrollbar-track-bg-dark-tone dark:scrollbar-thumb-bg-dark-tone-panel dark:hover:scrollbar-thumb-primary active:scrollbar-thumb-secondary" style="position: absolute; top: 100%; width: 200px; max-height: 300px; overflow-y: auto;">
              <ul style="list-style-type: none; padding-left: 0; margin-left: 0;">
                <li v-for="language in languages" :key="language" class="relative flex items-center" style="padding-left: 0; margin-left: 0;">
                  <button @click="deleteLanguage(language)" class="mr-2 text-red-500 hover:text-white hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-opacity-50 rounded-full">✕</button>
                  <div @click="selectLanguage(language)" :class="{'cursor-pointer hover:bg-blue-500 hover:text-white py-2 px-4 block whitespace-no-wrap': true, 'bg-blue-500 text-white': language === $store.state.language, 'flex-grow': true}">
                    {{ language }}
                  </div>
                </li>
                <li class="cursor-pointer hover:text-white py-0 px-0 block whitespace-no-wrap">
                  <input type="text" v-model="customLanguage" @keyup.enter.prevent="addCustomLanguage" placeholder="Enter language..." class="bg-transparent border border-gray-300 rounded py-0 px-0 mx-0 my-1 w-full">
                </li>
              </ul>
            </div>
          </div>
          <div class="sun text-2xl w-6 hover:text-primary duration-150 cursor-pointer" title="Switch to Light theme" @click="themeSwitch()">
            <i data-feather="sun"></i>
          </div>
          <div class="moon text-2xl w-6 hover:text-primary duration-150 cursor-pointer" title="Switch to Dark theme" @click="themeSwitch()">
            <i data-feather="moon"></i>
          </div>
      </nav>
  
      <!-- NAVIGATION BUTTONS -->
      <Navigation />
      <Toast ref="toast" />
      <MessageBox ref="messageBox" />
      <div v-show="progress_visibility" role="status" class="fixed m-0 p-2 left-2 bottom-2 min-w-[24rem] max-w-[24rem] h-20 flex flex-col justify-center items-center pb-4 bg-blue-500 rounded-lg shadow-lg z-50 background-a">
        <ProgressBar ref="progress" :progress="progress_value" class="w-full h-4"></ProgressBar>
        <p class="text-2xl animate-pulse mt-2 text-white">{{ loading_infos }} ...</p>
      </div>     
      <UniversalForm ref="universalForm" class="z-20" />
      <YesNoDialog ref="yesNoDialog" class="z-20" />
      <PersonalityEditor ref="personality_editor" :config="currentPersonConfig" :personality="selectedPersonality"></PersonalityEditor>
      <div id="app">
        <PopupViewer ref="news"/>
      </div>
    </header>
</template>
  

<script setup>
import Toast from '@/components/Toast.vue'
import MessageBox from "@/components/MessageBox.vue";
import ProgressBar from "@/components/ProgressBar.vue";
import UniversalForm from '../components/UniversalForm.vue';
import YesNoDialog from './YesNoDialog.vue';
import PersonalityEditor from "@/components/PersonalityEditor.vue"
import PopupViewer from '@/components/PopupViewer.vue';
import ActionButton from '@/components/ActionButton.vue'
import SocialIcon from '@/components/SocialIcon.vue'

import FastAPI from '@/assets/fastapi.png';
import discord from '@/assets/discord.svg';
import { RouterLink } from 'vue-router'
import Navigation from './Navigation.vue'
import { nextTick } from 'vue'
import feather from 'feather-icons'

import static_info from "../assets/static_info.svg"
import animated_info from "../assets/animated_info.svg"
import { useRouter } from 'vue-router'
import storeLogo from '@/assets/logo.png'
import fun_mode from "../assets/fun_mode.svg"
import normal_mode from "../assets/normal_mode.svg"

import axios from 'axios';
import { store } from '../main';
</script>
<script>

export default {
    name: 'TopBar',
    computed:{
        isFullMode() {
          return this.$store.state.view_mode === 'full'; // Accessing the mode directly
        },      
        storeLogo(){
            if (this.$store.state.config){
                return storeLogo
            }
            return this.$store.state.config.app_custom_logo!=''?'/user_infos/'+this.$store.state.config.app_custom_logo:storeLogo
        },        
        languages: {
            get(){
                console.log("searching languages", this.$store.state.languages)
                return this.$store.state.languages
            }
        },
        language: {
            get(){
                console.log("searching language", this.$store.state.language)
                return this.$store.state.language
            }
        },
        currentPersonConfig (){
            try{
                return this.$store.state.currentPersonConfig
            }
            catch{
                console.log("Error finding current personality configuration")
                return undefined
            }
        },        
        selectedPersonality (){
            try{
                return this.$store.state.selectedPersonality
            }
            catch{
                console.log("Error finding current personality configuration")
                return undefined
            }
        },        
        
        loading_infos(){
            return this.$store.state.loading_infos;
        },
        is_fun_mode(){
            try{
                if (this.$store.state.config){
                    return this.$store.state.config.fun_mode;
                }
                else{
                    return false;
                }
            }
            catch(error){
                console.error("Oopsie! Looks like we hit a snag: ", error);
                return false;
            }
        },
        isModelOK(){
            return this.$store.state.isModelOk;
        },
        isGenerating(){
            return this.$store.state.isGenerating;
        },
        isConnected(){
            return this.$store.state.isConnected;
        }
    },
    components: {
        Toast,
        MessageBox,
        ProgressBar,
        UniversalForm,
        YesNoDialog,
        Navigation,
        PersonalityEditor,
        PopupViewer,
        ActionButton,
        SocialIcon
    },
    watch:{
        '$store.state.config.fun_mode': function(newVal, oldVal) {
            console.log(`Fun mode changed from ${oldVal} to ${newVal}! 🎉`);
        },        
        '$store.state.isConnected': function(newVal, oldVal) {
            if (!this.isConnected){
                this.$store.state.messageBox.showBlockingMessage("Server suddenly disconnected. Please reboot the server to recover the connection")
                this.is_first_connection = false
                console.log("this.is_first_connection set to false")
                console.log(this.is_first_connection)
                if(this.$store.state.config.activate_audio_infos)
                    this.connection_lost_audio.play()
            }
            else{
                console.log("this.is_first_connection")
                console.log(this.is_first_connection)
                if(!this.is_first_connection){
                    this.$store.state.messageBox.hideMessage()
                    this.$store.state.messageBox.showMessage("Server connected.")
                    if(this.$store.state.config.activate_audio_infos)
                        this.connection_recovered_audio.play()
                }
            }
            nextTick(() => {
                feather.replace()
            })
        }

    },
    data() {
        return {
            customLanguage: '', // Holds the value of the custom language input
            selectedLanguage: '',
            isLanguageMenuVisible: false,
            static_info: static_info,
            animated_info: animated_info,
            normal_mode:normal_mode,
            fun_mode:fun_mode,
            is_first_connection:true,
            discord:discord,
            FastAPI:FastAPI,
            rebooting_audio: new Audio("rebooting.wav"),            
            connection_lost_audio: new Audio("connection_lost.wav"),
            connection_recovered_audio: new Audio("connection_recovered.wav"),
            database_selectorDialogVisible:false,
            progress_visibility:false,
            progress_value:0,
            codeBlockStylesheet:'',
            sunIcon: document.querySelector(".sun"),
            moonIcon: document.querySelector(".moon"),
            userTheme: localStorage.getItem("theme"),
            systemTheme: window.matchMedia("prefers-color-scheme: dark").matches,
            posts_headers : {
                'accept': 'application/json',
                'Content-Type': 'application/json'
            }            
        }
    },
    async mounted() {
        this.$store.state.toast = this.$refs.toast
        this.$store.state.news = this.$refs.news
        this.$store.state.messageBox = this.$refs.messageBox
        this.$store.state.universalForm = this.$refs.universalForm
        this.$store.state.yesNoDialog = this.$refs.yesNoDialog
        this.$store.state.personality_editor = this.$refs.personality_editor

        
        this.sunIcon = document.querySelector(".sun");
        this.moonIcon = document.querySelector(".moon");
        this.userTheme = localStorage.getItem("theme");
        this.systemTheme = window.matchMedia("prefers-color-scheme: dark").matches;
        this.themeCheck()

        nextTick(() => {
            feather.replace()
        })

        window.addEventListener('resize', this.adjustMenuPosition);

    },
    beforeUnmount() {
        window.removeEventListener('resize', this.adjustMenuPosition);
    },
    created() {
        this.sunIcon = document.querySelector(".sun");
        this.moonIcon = document.querySelector(".moon");
        this.userTheme = localStorage.getItem("theme");
        this.systemTheme = window.matchMedia("prefers-color-scheme: dark").matches;
        if (!localStorage.getItem('lollms_webui_view_mode')) {
          localStorage.setItem('lollms_webui_view_mode', 'compact'); // Default to 'compact'
        }        
    },
    
    methods: {
        adjustMenuPosition() {
            const menu = this.$refs.languageMenu;
            if(menu){
                const rect = menu.getBoundingClientRect();
                const windowWidth = window.innerWidth;

                if (rect.right > windowWidth) {
                    menu.style.left = 'auto';
                    menu.style.right = '0';
                } else {
                    menu.style.left = '0';
                    menu.style.right = 'auto';
                }
            }
        },
        addCustomLanguage() {
            if (this.customLanguage.trim() !== '') {
            this.selectLanguage(this.customLanguage);
            this.customLanguage = ''; // Reset the input field after adding
            }
        },
        async selectLanguage(language) {
            await this.$store.dispatch('changeLanguage', language);
            this.toggleLanguageMenu(); // Fermer le menu après le changement de langue
            this.language = language
        },
        async deleteLanguage(language) {
            await this.$store.dispatch('deleteLanguage', language);
            this.toggleLanguageMenu(); // Fermer le menu après le changement de langue
            this.language = language
        },
        
        toggleLanguageMenu() {
            console.log("Toggling language ",this.isLanguageMenuVisible)
            this.isLanguageMenuVisible = !this.isLanguageMenuVisible;
        },        
        restartProgram(event) {
            event.preventDefault();
            this.$store.state.api_post_req('restart_program', this.$store.state.client_id)
            this.rebooting_audio.play()
            this.$store.state.toast.showToast("Rebooting the app. Please wait...", 410, false)
            //this.$store.state.toast.showToast("Rebooting the app. Please wait...", 50, true);
            console.log("this.$store.state.api_get_req",this.$store.state.api_get_req)
            setTimeout(()=>{
                window.close();
            },2000)
        },   
        refreshPage() {
            const hostnameParts = window.location.href.split('/');

            if(hostnameParts.length > 4){
                window.location.href='/'
            }
            else{
                window.location.reload(true);
            }
        },
        handleOk(inputText) {
            console.log("Input text:", inputText);
        },
        // codeBlockTheme(theme) {
        //     const styleDark = document.createElement('link');
        //     styleDark.type = "text/css";
        //     styleDark.href = 'highlight.js/styles/tokyo-night-dark.css';

        //     const styleLight = document.createElement('link');
        //     styleLight.type = "text/css";
        //     styleLight.href = 'highlight.js/styles/tomorrow-night-blue.css';
        //    if(theme=='dark'){

        //     document.head.appendChild(styleDark);
        //     document.head.removeChild(styleLight);
        //    }else{
        //     document.head.appendChild(styleLight);
        //     //document.head.removeChild(styleDark);
        //    }
            
        // },
        applyConfiguration() {
            this.isLoading = true;
            console.log(this.$store.state.config)
            axios.post('/apply_settings', {"client_id":this.$store.state.client_id, "config":this.$store.state.config}, {headers: this.posts_headers}).then((res) => {
                this.isLoading = false;
                //console.log('apply-res',res)
                if (res.data.status) {

                    this.$store.state.toast.showToast("Configuration changed successfully.", 4, true)
                    this.settingsChanged = false
                    //this.save_configuration()
                } else {

                    this.$store.state.toast.showToast("Configuration change failed.", 4, false)

                }
                nextTick(() => {
                    feather.replace()

                })
            })
        },
        fun_mode_on(){
            console.log("Turning on fun mode")
            this.$store.state.config.fun_mode=true;
            this.applyConfiguration()
        },
        fun_mode_off(){
            console.log("Turning off fun mode")
            this.$store.state.config.fun_mode=false;
            this.applyConfiguration()
        },
        showNews(){
            this.$store.state.news.show()
        },
        themeCheck() {

            if (this.userTheme == "dark" || (!this.userTheme && this.systemTheme)) {
                document.documentElement.classList.add("dark");
                this.moonIcon.classList.add("display-none");

                nextTick(()=>{
                    //import('highlight.js/styles/tokyo-night-dark.css');
                    import('highlight.js/styles/stackoverflow-dark.css');

                })

                return
            }

            nextTick(()=>{
                //import('highlight.js/styles/tomorrow-night-blue.css');
                import('highlight.js/styles/stackoverflow-light.css');
            })
            this.sunIcon.classList.add("display-none")

        },
        themeSwitch() {
            
            if (document.documentElement.classList.contains("dark")) {
                document.documentElement.classList.remove("dark");
                localStorage.setItem("theme", "light")
                this.userTheme == "light"
                this.iconToggle()
             
                return

            }
            import('highlight.js/styles/tokyo-night-dark.css');
            document.documentElement.classList.add("dark");
            localStorage.setItem("theme", "dark")
            this.userTheme == "dark"
            this.iconToggle()
            // Dispatch the themeChanged event
            window.dispatchEvent(new Event('themeChanged'));
        },
        iconToggle() {
            this.sunIcon.classList.toggle("display-none");
            this.moonIcon.classList.toggle("display-none");
        }
    },
}

</script>
  <style>
  .dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
  }

  .dot-green {
    background-color: green;
  }

  .dot-red {
    background-color: red;
  }

  .animate-pulse {
    animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
  }

  @keyframes pulse {
    0%, 100% {
      opacity: 1;
    }
    50% {
      opacity: .7;
    }
  }
  .logo-container {
    position: relative;
    width: 48px;
    height: 48px;
  }

  .logo-image {
    width: 100%;
    height: 100%;
    border-radius: 50%;
    object-fit: cover;
  }
  @keyframes bounce {
    0%, 100% {
      transform: translateY(-25%);
      animation-timing-function: cubic-bezier(0.8, 0, 1, 1);
    }
    50% {
      transform: translateY(0);
      animation-timing-function: cubic-bezier(0, 0, 0.2, 1);
    }
  }
  .animate-bounce {
    animation: bounce 1s infinite;
  }


  @keyframes roll-and-bounce {
    0%, 100% {
      transform: translateX(0) rotate(0deg);
    }
    45% {
      transform: translateX(100px) rotate(360deg);
    }
    50% {
      transform: translateX(90px) rotate(390deg);
    }
    55% {
      transform: translateX(100px) rotate(360deg);
    }
    95% {
      transform: translateX(0) rotate(0deg);
    }
  }

  @keyframes spin {
    0% {
      transform: rotate(0deg);
    }
    100% {
      transform: rotate(360deg);
    }
  }

  </style>