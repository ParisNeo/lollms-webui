
<template>
  <div ref="topbar-container" :class="['topbar-container', {'h-0': !isPinned}]">
    <!-- Add a thin strip at the top that triggers the hover -->
    <div 
      class="hover-zone" 
      @mouseenter="show" 
      style="position: fixed; top: 0; left: 0; width: 100%; height: 10px; z-index: 50;"
    ></div>

    <div class="topbar" :class="{ 'topbar-hidden': !isVisible }" @mouseleave="hide">
      <!-- Rest of your topbar content -->
      <div class="topbar-content">
        <slot name="navigation"></slot>
        <button class="pin-button" @click="togglePin" :title="isPinned ? 'Unpin' : 'Pin'">
          <svg :fill="isPinned ? '#FF0000' : '#000000'" height="24px" width="24px" version="1.1" id="Capa_1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" 
            viewBox="0 0 490.125 490.125" xml:space="preserve">
              <g>
                <path d="M300.625,5.025c-6.7-6.7-17.6-6.7-24.3,0l-72.6,72.6c-6.7,6.7-6.7,17.6,0,24.3l16.3,16.3l-40.3,40.3l-63.5-7
                  c-3-0.3-6-0.5-8.9-0.5c-21.7,0-42.2,8.5-57.5,23.8l-20.8,20.8c-6.7,6.7-6.7,17.6,0,24.3l108.5,108.5l-132.4,132.4
                  c-6.7,6.7-6.7,17.6,0,24.3c3.3,3.3,7.7,5,12.1,5s8.8-1.7,12.1-5l132.5-132.5l108.5,108.5c3.3,3.3,7.7,5,12.1,5s8.8-1.7,12.1-5
                  l20.8-20.8c17.6-17.6,26.1-41.8,23.3-66.4l-7-63.5l40.3-40.3l16.2,16.2c6.7,6.7,17.6,6.7,24.3,0l72.6-72.6c3.2-3.2,5-7.6,5-12.1
                  s-1.8-8.9-5-12.1L300.625,5.025z M400.425,250.025l-16.2-16.3c-6.4-6.4-17.8-6.4-24.3,0l-58.2,58.3c-3.7,3.7-5.5,8.8-4.9,14
                  l7.9,71.6c1.6,14.3-3.3,28.3-13.5,38.4l-8.7,8.7l-217.1-217.1l8.7-8.6c10.1-10.1,24.2-15,38.4-13.5l71.7,7.9
                  c5.2,0.6,10.3-1.2,14-4.9l58.2-58.2c6.7-6.7,6.7-17.6,0-24.3l-16.3-16.3l48.3-48.3l160.3,160.3L400.425,250.025z"/>
              </g>
          </svg>
        </button>
        <Navigation></Navigation>
        <div class="toolbar-button" @mouseleave="hideInfosMenu">
            <div class="relative inline-block">
                <!-- Infos menu positioned above the button -->
                <div v-if="isInfosMenuVisible"  @mouseenter="showInfosMenu" class="absolute context-menu m-0 p-0 z-50 top-full right-0 transform rounded-md shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none transition-all duration-300 ease-out mb-2">
                    <div class="p-4 container flex flex-col lg:flex-row items-center gap-2">
                        <!-- SYSTEM STATUS -->
                        <div class="flex gap-3 flex-1 items-center justify-end">
                            <div v-if="isModelOK" title="Model is ok" class="btn-on cursor-pointer transition-transform hover:scale-110">
                            <svg class="w-8 h-8" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path d="M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                                <path d="M9 12L11 14L15 10" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                            </svg>
                            </div>
                            <div v-else title="Model is not ok" class="btn-off cursor-pointer transition-transform hover:scale-110">
                            <svg class="w-8 h-8" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path d="M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                                <path d="M15 9L9 15" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                                <path d="M9 9L15 15" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                            </svg>
                            </div>
                            <div v-if="!isGenerating" title="Text is not being generated. Ready to generate" class="btn-on cursor-pointer transition-transform hover:scale-110">
                            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 21v-4m0 0V5a2 2 0 012-2h6.5l1 1H21l-3 6 3 6h-8.5l-1-1H5a2 2 0 00-2 2zm9-13.5V9"></path>
                            </svg>
                            </div>
                            <div v-else title="Generation in progress..." class="svg-button cursor-pointer transition-transform hover:scale-110">
                            <svg class="w-6 h-6 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
                            </svg>
                            </div>
                            <div v-if="isConnected" title="Connection status: Connected" class="btn-on cursor-pointer transition-transform hover:scale-110">
                            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
                            </svg>
                            </div>
                            <div v-else title="Connection status: Not connected" class="btn-off cursor-pointer transition-transform hover:scale-110">
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
                        <SocialIcon href="https://github.com/ParisNeo/lollms-webui" icon="github" />
                        <SocialIcon href="https://www.youtube.com/channel/UCJzrg0cyQV2Z30SQ1v2FdSQ" icon="youtube" />
                        <SocialIcon href="https://x.com/ParisNeo_AI" icon="x" />
                        <SocialIcon href="https://discord.com/channels/1092918764925882418" icon="discord" />
                
                        <div class="relative group" title="Lollms News">
                            <div @click="showNews()" class="text-2xl w-8 h-8 cursor-pointer transition-colors duration-300 svg-button">
                            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="w-full h-full">
                                <path d="M19 20H5a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2v1m2 13a2 2 0 0 1-2-2V7m2 13a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z"></path>
                            </svg>
                            </div>
                            <span class="absolute hidden group-hover:block text-xs rounded py-1 px-2 top-full left-1/2 transform -translate-x-1/2 mt-2 whitespace-nowrap">
                            Lollms News
                            </span>
                        </div>
                    </div>
                </div>

                <!-- Info Button -->
                <div @mouseenter="showInfosMenu" class="infos-hover-area">
                    <button class="w-6 h-6">
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 25 25" class="w-full h-full">
                            <!-- Circle background -->
                            <circle cx="12.5" cy="12.5" r="11.25" fill="#3498db"/>
                            <!-- "i" stem -->
                            <rect x="11.25" y="10" width="2.5" height="8.75" fill="white"/>
                            <!-- "i" dot -->
                            <circle cx="12.5" cy="6.25" r="1.25" fill="white"/>
                        </svg>
                    </button>
                </div>
            </div>      
        </div>
        <div style="margin: 20px;">
          <a 
            href="https://github.com/ParisNeo/lollms-webui"
            target="_blank"
            rel="noopener noreferrer"
            class="inline-flex items-center gap-2 px-3 py-1.5 text-sm text-gray-700 hover:text-gray-900 bg-gray-100 hover:bg-gray-200 rounded-md transition-colors duration-200 my-4 mx-2"
          >
            <svg 
              class="w-5 h-5" 
              viewBox="0 0 16 16"
              fill="currentColor"
            >
              <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/>
            </svg>
            <span class="font-medium" v-if="starCount">{{ starCount }}</span>
          </a>
        </div>
        <div v-if="is_fun_mode" 
                title="Fun mode is on, press to turn off" 
                class="w-8 h-8 cursor-pointer btn-on transition-colors duration-300"
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
            class="w-8 h-8 cursor-pointer btn-off transition-colors duration-300"
            @click="fun_mode_on()"
        >
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="w-full h-full">
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="8" y1="15" x2="16" y2="15"></line>
                <line x1="9" y1="9" x2="9.01" y2="9"></line>
                <line x1="15" y1="9" x2="15.01" y2="9"></line>
                </svg>
            </div>
            <span class="absolute hidden group-hover:block text-xs rounded py-1 px-2 top-full left-1/2 transform -translate-x-1/2 mb-2 whitespace-nowrap">
                {{ is_fun_mode ? 'Turn off fun mode' : 'Turn on fun mode' }}
            </span>
        <div v-if="isDarkMode" class="text-2xl svg-button hover:text-primary duration-150 cursor-pointer  w-50 h-50 ml-2" title="Switch to Light theme" @click="themeSwitch()">
            <i data-feather="sun"></i>
        </div>
        <div v-else class="text-2xl svg-button hover:text-primary duration-150 cursor-pointer w-50 h-50  ml-2" title="Switch to Dark theme" @click="themeSwitch()">
            <i data-feather="moon"></i>
        </div>               
        <div class="relative ml-2">
          <button 
              @click="toggleLanguageMenu" 
              class="flex items-center gap-2 px-3 py-2 rounded-md hover:bg-gray-100 transition-colors"
              aria-haspopup="true"
              :aria-expanded="isLanguageMenuVisible"
          >
              <span class="font-medium">{{ $store.state.language.slice(0, 2) }}</span>
              <svg 
                  class="w-4 h-4 transition-transform" 
                  :class="{ 'rotate-180': isLanguageMenuVisible }"
                  viewBox="0 0 24 24"
              >
                  <path d="M7 10l5 5 5-5z" fill="currentColor" />
              </svg>
          </button>

          <Transition
              enter-active-class="transition duration-200 ease-out"
              enter-from-class="transform scale-95 opacity-0"
              enter-to-class="transform scale-100 opacity-100"
              leave-active-class="transition duration-150 ease-in"
              leave-from-class="transform scale-100 opacity-100"
              leave-to-class="transform scale-95 opacity-0"
          >
              <div 
                  v-if="isLanguageMenuVisible" 
                  ref="languageMenu" 
                  class="absolute left-0 mt-1 w-64 rounded-lg shadow-lg bg-white border border-gray-200 z-10"
                  role="menu"
              >
                  <ul class="py-2 max-h-72 overflow-y-auto">
                      <li 
                          v-for="language in languages" 
                          :key="language" 
                          class="group flex items-center px-3 py-2 hover:bg-gray-50"
                      >
                          <button 
                              @click="deleteLanguage(language)" 
                              class="p-1 rounded-full opacity-0 group-hover:opacity-100 transition-opacity text-gray-400 hover:text-red-500 hover:bg-red-50"
                              :aria-label="`Delete ${language}`"
                          >
                              <svg class="w-4 h-4" viewBox="0 0 24 24">
                                  <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z" fill="currentColor" />
                              </svg>
                          </button>
                          <div 
                              @click="selectLanguage(language)" 
                              class="flex-grow px-3 py-1 cursor-pointer rounded-md transition-colors"
                              :class="language === $store.state.language ? 'bg-blue-50 text-blue-600' : 'hover:bg-gray-100'"
                              role="menuitem"
                          >
                              {{ language }}
                          </div>
                      </li>
                      <li class="px-3 py-2 border-t border-gray-100">
                          <input 
                              type="text" 
                              v-model="customLanguage" 
                              @keyup.enter.prevent="addCustomLanguage"
                              placeholder="Add new language..." 
                              class="w-full px-3 py-2 rounded-md border border-gray-200 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none transition-all"
                          >
                      </li>
                  </ul>
              </div>
          </Transition>
      </div>

        <div class="relative inline-flex ml-2">
          <!-- Enhanced custom button -->
          <button 
            @click.stop="toggleThemeDropDown"
            class="inline-flex items-center justify-between w-40 px-4 py-2
                  bg-gradient-to-r from-blue-500/10 to-purple-500/10
                  dark:from-blue-400/20 dark:to-purple-400/20
                  border border-blue-200 dark:border-blue-700
                  rounded-lg shadow-sm
                  hover:from-blue-500/20 hover:to-purple-500/20
                  dark:hover:from-blue-400/30 dark:hover:to-purple-400/30
                  hover:border-blue-300 dark:hover:border-blue-600
                  hover:shadow-md
                  focus:outline-none focus:ring-2 focus:ring-blue-500/50
                  transition-all duration-300 ease-in-out
                  backdrop-blur-sm"
          >
            <div class="flex items-center space-x-2 overflow-hidden">
              <!-- Theme Icon -->
              <svg 
                class="w-5 h-5 flex-shrink-0"
                xmlns="http://www.w3.org/2000/svg" 
                fill="none" 
                viewBox="0 0 24 24" 
                stroke="currentColor"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                      d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01" />
              </svg>
              <span class="font-medium truncate">{{ currentTheme }}</span>
            </div>
            <svg 
              class="w-5 h-5 flex-shrink-0 text-blue-500 dark:text-blue-400 transition-transform duration-300"
              :class="{ 'rotate-180': themeDropdownOpen }"
              xmlns="http://www.w3.org/2000/svg" 
              viewBox="0 0 20 20" 
              fill="currentColor"
            >
              <path fill-rule="evenodd" 
                    d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" 
                    clip-rule="evenodd" />
            </svg>
          </button>

          <!-- Enhanced Dropdown menu with animations -->
          <transition
            enter-active-class="transition duration-200 ease-out"
            enter-from-class="transform scale-95 opacity-0"
            enter-to-class="transform scale-100 opacity-100"
            leave-active-class="transition duration-75 ease-in"
            leave-from-class="transform scale-100 opacity-100"
            leave-to-class="transform scale-95 opacity-0"
          >
            <div 
              v-if="themeDropdownOpen"
              class="absolute left-0 z-50 w-48 mt-2 
                    context-menu
                    overflow-hidden
                    bg-white dark:bg-gray-800 
                    border border-blue-200 dark:border-blue-700
                    rounded-lg shadow-lg"
            >
              <div class="max-h-60 overflow-y-auto scrollbar-thin scrollbar-thumb-blue-500 scrollbar-track-blue-100">
                <a
                  v-for="theme in availableThemes"
                  :key="theme"
                  @click="loadTheme(theme); currentTheme = theme; themeDropdownOpen = false"
                  class="flex items-center space-x-3 px-4 py-3
                        text-gray-700 dark:text-gray-200
                        hover:bg-gradient-to-r hover:from-blue-50 hover:to-purple-50
                        dark:hover:from-blue-900/30 dark:hover:to-purple-900/30
                        cursor-pointer
                        transition-colors duration-150
                        group"
                >
                  <div class="w-2 h-2 rounded-full bg-blue-400 group-hover:bg-blue-500 
                              transition-colors duration-150"></div>
                  <span class="font-medium truncate">{{ theme }}</span>
                </a>
              </div>
            </div>
          </transition>
        </div>    
        
      </div>
    </div>
  </div>
  <div v-show="progress_visibility" role="status" class="fixed m-0 p-2 left-2 bottom-2  min-w-[24rem] max-w-[24rem] h-20 flex flex-col justify-center items-center pb-4 bg-blue-500 rounded-lg shadow-lg z-50 background-a">
        <ProgressBar ref="progress" :progress="progress_value" class="w-full h-4"></ProgressBar>
        <p class="text-2xl animate-pulse mt-2 text-light-text-panel dark:text-dark-text-panel">{{ loading_infos }} ...</p>
  </div>
  <InputBox prompt-text="Enter the url to the page to use as discussion support" @ok="addWebpage" ref="web_url_input_box"></InputBox>   
  <Toast ref="toast" />
  <MessageBox ref="messageBox" />
  <YesNoDialog ref="yesNoDialog" class="z-20" />
  <UniversalForm ref="universalForm" class="z-20" />

</template>

<script>
import Navigation from '@/components/Navigation.vue';
import ActionButton from '@/components/ActionButton.vue'
import SocialIcon from '@/components/SocialIcon.vue'

import MessageBox from "@/components/MessageBox.vue";
import ProgressBar from "@/components/ProgressBar.vue";
import UniversalForm from '../components/UniversalForm.vue';
import Toast from '@/components/Toast.vue'
import YesNoDialog from '../components/YesNoDialog.vue';

import axios from 'axios'
import feather from 'feather-icons'
export default {
  name: 'TopBar',
  components: {
    Navigation,
    ActionButton,
    SocialIcon,
    Toast,
    MessageBox,
    ProgressBar,
    UniversalForm,
    YesNoDialog
   
  },
  data() {
    return {
      starCount:null,
      themeDropdownOpen: false,
      currentTheme: localStorage.getItem('preferred-theme') || 'default',
      availableThemes: [],
      isLoading: false,
      error: null,      
      isInfosMenuVisible: false,
      isVisible: false,
      isPinned: false,
      selectedLanguage: '',
      isLanguageMenuVisible: false,
      sunIcon: document.querySelector(".sun"),
      moonIcon: document.querySelector(".moon"),
      userTheme: localStorage.getItem("theme"),
      systemTheme: window.matchMedia("prefers-color-scheme: dark").matches,
      isDarkMode: false
    }
  },
  computed:{
    isModelOK(){
      return this.$store.state.isModelOk;
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
    isGenerating(){
        return this.$store.state.isGenerating;
    },
    isConnected(){
        return this.$store.state.isConnected;
    },     
  },
  async mounted() {
    try {
      this.$store.state.toast = this.$refs.toast
      this.$store.state.messageBox = this.$refs.messageBox
      this.$store.state.universalForm = this.$refs.universalForm
      this.$store.state.yesNoDialog = this.$refs.yesNoDialog
      document.addEventListener('click', this.handleClickOutside)
      // Load saved theme preference
      const savedTheme = localStorage.getItem('preferred-theme')
      if (savedTheme && this.availableThemes.includes(savedTheme)) {
        this.currentTheme = savedTheme
      }
      
      // Load the initial theme
      try {
        await this.loadTheme(this.currentTheme)
      } catch (err) {
        this.error = 'Failed to initialize theme system'
        console.error(err)
      }
      
    } catch (err) {
      this.error = 'Failed to initialize theme system'
      console.error(err)
    }

    try {
      const response = await fetch('https://api.github.com/repos/ParisNeo/lollms-webui')
      const data = await response.json()
      this.starCount = data.stargazers_count
    } catch (error) {
      console.error('Error fetching GitHub stars:', error)
    }
  },  
  beforeUnmount() {
    document.removeEventListener('click', this.handleClickOutside)
  },
  async created() {
    this.sunIcon = document.querySelector(".sun");
    this.moonIcon = document.querySelector(".moon");
    this.userTheme = localStorage.getItem("theme");
    console.log(this.userTheme)
    this.systemTheme = window.matchMedia("prefers-color-scheme: dark").matches;
    this.fetchThemes();    
    this.themeCheck()
    this.$nextTick(() => {
        feather.replace()
    })

  },
  methods: {
    async fetchThemes() {
      try {
        const response = await axios.get('/get_themes');
        this.availableThemes = response.data;
      } catch (error) {
        console.error('Error fetching themes:', error);
        // Optionally, you can set a default list of themes in case the API call fails
        this.availableThemes = ['default', 'strawberry_milkshake', 'red_dragon', 'matrix_reborn', 'borg', 'amber', 'sober_gray', 'strawberry'];
      }
    },    
    toggleThemeDropDown()
    {
      console.log("Toggling theme down:", this.themeDropdownOpen)
      this.themeDropdownOpen = !this.themeDropdownOpen;
      console.log("Toggled theme down:", this.themeDropdownOpen)
    },
    addCustomLanguage() {
        if (this.customLanguage.trim() !== '') {
        this.selectLanguage(this.customLanguage);
        this.customLanguage = ''; // Reset the input field after adding
        }
    },
    handleClickOutside(e) {
      const dropdown = this.$el
      if (!dropdown.contains(e.target)) {
        this.themeDropdownOpen = false
        console.log("Outside click detected")
      }
    },
    getSavedTheme() {
      try {
        return localStorage.getItem('preferred-theme')
      } catch (e) {
        console.warn('Failed to access localStorage:', e)
        return null
      }
    },

    // Safely save theme to localStorage
    saveTheme(themeName) {
      try {
        // Clear some space first
        this.clearOldStorageItems()
        localStorage.setItem('preferred-theme', themeName)
      } catch (e) {
        console.warn('Failed to save theme preference:', e)
        // Continue without saving to localStorage
      }
    },

    // Helper method to clear space in localStorage
    clearOldStorageItems() {
      try {
        // Remove old or unnecessary items
        const itemsToKeep = ['preferred-theme'] // Add other critical items here
        for (let i = 0; i < localStorage.length; i++) {
          const key = localStorage.key(i)
          if (!itemsToKeep.includes(key)) {
            localStorage.removeItem(key)
          }
        }
      } catch (e) {
        console.warn('Failed to clear localStorage:', e)
      }
    },

    async loadTheme(themeName) {
      this.isLoading = true
      this.error = null
      
      try {
        // Fetch and apply new theme CSS
        const response = await axios.get(`/themes/${themeName}.css`, {
          headers: {
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'Expires': '0',
          }
        });
        console.log(response)
        // Remove any existing theme style element
        const existingStyle = document.getElementById('theme-styles');
        if (existingStyle) {
          existingStyle.remove();
        }

        // Create and append new style element
        const styleElement = document.createElement('style');
        styleElement.id = 'theme-styles';
        styleElement.textContent = response.data;
        document.head.appendChild(styleElement);

        // Apply theme class to body
        // document.body.className = `theme-${themeName}`;

        // Safely save theme preference
        this.saveTheme(themeName);      
        
        // Update the main rapameters
        const styles = getComputedStyle(document.documentElement);
        const lollms_title = styles.getPropertyValue('--lollms-title').trim();
        const activate_dropping_animation = styles.getPropertyValue('--activate-dropping-animation').trim() === '1';
        const falling_object = styles.getPropertyValue('--falling-object').trim();
        const lollms_welcome_short_message = styles.getPropertyValue('--lollms-welcome-short-message').trim();
        const lollms_welcome_message = styles.getPropertyValue('--lollms-welcome-message').trim();
        
        
        let theme_vars = this.$store.state.theme_vars;
        if (lollms_title){
          theme_vars.lollms_title = lollms_title
        }
        if (activate_dropping_animation){
          theme_vars.activate_dropping_animation = activate_dropping_animation
        }
        if (falling_object){
          theme_vars.falling_object = falling_object
        }

        if (lollms_welcome_short_message){
          theme_vars.lollms_welcome_short_message = lollms_welcome_short_message
        }
        if (lollms_welcome_message){
          theme_vars.lollms_welcome_message = lollms_welcome_message
        }

        this.$store.commit('setThemeVars', theme_vars);
        this.isDarkMode =  document.documentElement.classList.contains("dark");

        this.$nextTick(() => {
            feather.replace()
        })
      } catch (error) {
        console.error(`Failed to load theme: ${themeName}`, error)
        this.error = `Failed to load theme: ${themeName}`
      } finally {
        this.isLoading = false
      }
    },

    reloadTheme() {
      return this.loadTheme(this.currentTheme)
    },
      
    themeSwitch() {
        
        if (document.documentElement.classList.contains("dark")) {
            document.documentElement.classList.remove("dark");
            localStorage.setItem("theme", "light")
            this.userTheme == "light"          
            return

        }
        import('highlight.js/styles/tokyo-night-dark.css');
        document.documentElement.classList.add("dark");
        localStorage.setItem("theme", "dark")
        this.userTheme == "dark"
        // Dispatch the themeChanged event
        window.dispatchEvent(new Event('themeChanged'));
        this.isDarkMode =  document.documentElement.classList.contains("dark");
        this.$nextTick(() => {
            feather.replace()
        })
    },
    async selectLanguage(language) {
        await this.$store.dispatch('changeLanguage', language);
        const current_personality_name = this.$store.state.config.personalities[this.$store.state.config.active_personality_id]
        let personality = this.$store.state.personalities.find(personality => personality.full_path === current_personality_name);
        console.log("personality", personality)
        console.log("this.$store.state.language", personality.language)
        console.log("personality.language", personality.language)
        
        if (this.$store.state.language != personality.language) {
            console.log("getting personality");
            const pers = await axios.get("/get_personality");
            console.log(pers);
            personality = pers.data;
            console.log(personality);
            
            // Appel de la mutation pour mettre à jour l'état
            this.$store.commit('updatePersonality', personality);
        }
        console.log("personality:", personality);
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

    showInfosMenu() {
        this.isInfosMenuVisible = true;
        this.$nextTick(() => {
            feather.replace()
        })
      },
    hideInfosMenu() {
        this.isInfosMenuVisible = false;
        this.$nextTick(() => {
                feather.replace()
            })
    },    
    show() {
      this.isVisible = true
    },
    hide() {
      if (!this.isPinned) {
        this.isVisible = false
      }
    },
    togglePin() {
      this.isPinned = !this.isPinned
      this.isVisible = this.isPinned
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
        this.$nextTick(() => {
            feather.replace()
        })
    },
    themeCheck() {

        if (this.userTheme == "dark" || (!this.userTheme && this.systemTheme)) {
            document.documentElement.classList.add("dark");
            this.moonIcon.classList.add("display-none");

            this.$nextTick(()=>{
                //import('highlight.js/styles/tokyo-night-dark.css');
                import('highlight.js/styles/stackoverflow-dark.css');

            })

            return
        }

        this.$nextTick(()=>{
            //import('highlight.js/styles/tomorrow-night-blue.css');
            import('highlight.js/styles/stackoverflow-light.css');
        })

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

  },
}
</script>

<style scoped>
.topbar-container {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
}

.topbar {
  background-color: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(5px);
  transition: transform 0.3s ease-in-out;
  display: flex;
  justify-content: center;
}

.topbar-hidden {
  transform: translateY(-100%);
}

.topbar-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1200px;
  width: 100%;
}

.pin-button {
  background-color: transparent;
  border: none;
  cursor: pointer;
  padding: 5px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.pin-button svg {
  width: 24px;
  height: 24px;
  transition: transform 0.3s ease;
}

.pin-button:hover svg {
  transform: scale(1.2);
}

.placeholder {
  height: 10px;
}



.topbar-container {
  position: relative;
  width: 100%;
}

.hover-zone {
  opacity: 0;
}


.error {
  color: red;
  margin-left: 1rem;
}
</style>
