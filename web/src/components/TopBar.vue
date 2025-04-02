<template>
  <div
    v-if="!isPinned"
    class="fixed top-0 left-0 w-full h-3 z-[51] cursor-pointer"
    @mouseenter="show"
    @mouseleave="hideUnlessEnteringTopbar"
  ></div>

  <div
    ref="topbarContainer"
    :class="[
      'fixed top-0 left-0 right-0 z-50 h-14',
      'toolbar-color',
      'shadow-lg',
      'transition-transform duration-300 ease-in-out',
      { '-translate-y-full': !isEffectivelyVisible, 'translate-y-0': isEffectivelyVisible }
    ]"
    @mouseenter="clearHideTimeout"
    @mouseleave="hide"
  >
    <div class="flex justify-center h-full">
      <div class="flex justify-between items-center w-full max-w-7xl px-2 sm:px-4 py-1 h-full">
         <div class="flex-shrink-0">
            <slot name="navigation">
               <Navigation></Navigation>
            </slot>
          </div>

          <div class="flex-grow"></div>

          <div class="flex items-center gap-1 sm:gap-2">
              <a
                  v-if="starCount !== null"
                  :href="githubRepoUrl"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="btn btn-secondary btn-sm hidden md:inline-flex items-center gap-1.5"
                  :title="`Star us on GitHub! (${starCount} stars)`"
              >
                  <i data-feather="github" class="w-4 h-4"></i>
                  <span class="font-medium text-xs">{{ formattedStarCount }}</span>
              </a>

             <div class="relative">
                <button @click.stop="toggleThemeDropDown" class="btn btn-secondary btn-sm w-28 sm:w-36" title="Select Theme">
                    <div class="flex items-center justify-between w-full">
                        <div class="flex items-center space-x-1.5 overflow-hidden">
                            <i data-feather="layout" class="w-4 h-4 flex-shrink-0"></i>
                            <span class="font-medium truncate text-xs">{{ currentTheme }}</span>
                        </div>
                        <i data-feather="chevron-down" :class="['w-4 h-4 flex-shrink-0 transition-transform duration-300', { 'rotate-180': themeDropdownOpen }]"></i>
                    </div>
                </button>
                 <transition name="context-menu-transition">
                     <div v-if="themeDropdownOpen" ref="themeMenu" class="context-menu theme-dropdown" role="menu">
                         <div class="max-h-60 overflow-y-auto scrollbar">
                             <a v-for="theme in availableThemes" :key="theme" @click="selectTheme(theme)" class="context-menu-item group" role="menuitem">
                                 <i data-feather="droplet" class="w-3.5 h-3.5 context-menu-item-icon group-hover:animate-pulse"></i>
                                 <span class="truncate">{{ theme }}</span>
                             </a>
                         </div>
                     </div>
                 </transition>
             </div>

             <div class="relative">
                <button @click.stop="toggleLanguageMenu" class="btn btn-secondary btn-sm inline-flex items-center" title="Select Language" aria-haspopup="true" :aria-expanded="isLanguageMenuVisible">
                    <span class="font-medium text-xs">{{ currentLanguageDisplay }}</span>
                    <i data-feather="chevron-down" :class="['w-4 h-4 ml-1 transition-transform duration-300', { 'rotate-180': isLanguageMenuVisible }]"></i>
                </button>
                 <Transition name="context-menu-transition">
                    <div v-if="isLanguageMenuVisible" ref="languageMenu" class="context-menu language-dropdown" role="menu">
                        <ul class="max-h-72 overflow-y-auto scrollbar py-1">
                            <li v-for="lang in languages" :key="lang" class="context-menu-item flex items-center group pr-2">
                                <button v-if="lang !== 'English'" @click.stop="deleteLanguage(lang)" class="svg-button p-0.5 rounded-full opacity-0 group-hover:opacity-100 transition-opacity text-red-500 hover:bg-red-100 dark:hover:bg-red-900/50 mr-2" :aria-label="`Delete ${lang}`" title="Delete Language">
                                    <i data-feather="x" class="w-3 h-3"></i>
                                </button>
                                <div @click="selectLanguage(lang)" :class="['flex-grow pl-2 pr-1 py-0.5 cursor-pointer rounded text-xs transition-colors', lang === language ? 'bg-blue-100 dark:bg-blue-700 text-blue-700 dark:text-blue-100 font-semibold' : 'hover:bg-blue-50 dark:hover:bg-blue-800', { 'ml-[calc(0.75rem+0.5rem)]': lang === 'English' }]" role="menuitem">
                                    {{ lang }}
                                </div>
                            </li>
                            <li class="px-3 pt-2 pb-1 border-t border-blue-200 dark:border-blue-700 mt-1">
                                <input type="text" v-model="customLanguage" @keyup.enter.prevent="addCustomLanguage" placeholder="Add new language..." class="input input-sm w-full">
                            </li>
                        </ul>
                    </div>
                 </Transition>
             </div>

             <button @click="themeSwitch()" :title="isDarkMode ? 'Switch to Light theme' : 'Switch to Dark theme'" class="svg-button text-xl p-1.5">
                 <i :data-feather="isDarkMode ? 'sun' : 'moon'" class="w-4 h-4"></i>
             </button>

             <button class="svg-button p-1.5 transition-transform hover:scale-110 focus:outline-none" @click="togglePin" :title="isPinned ? 'Unpin Top Bar' : 'Pin Top Bar'">
                 <svg class="w-4 h-4" :class="isPinned ? 'text-red-500 dark:text-red-400' : 'text-blue-600 dark:text-blue-400'" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
                     <path d="M16 12V4H17V2H7V4H8V12L6 14V16H11.5V22H12.5V16H18V14L16 12Z M8.8 14L10 12.8V4H14V12.8L15.2 14H8.8Z"/>
                 </svg>
             </button>

             <div class="relative" @mouseleave="hideInfosMenu">
                <button @mouseenter="showInfosMenu" class="svg-button p-1.5" title="Status & Info">
                    <i data-feather="info" class="w-5 h-5"></i>
                </button>
                 <transition name="context-menu-transition">
                     <div v-if="isInfosMenuVisible" @mouseenter="showInfosMenu" @mouseleave="hideInfosMenu" class="context-menu info-dropdown" role="menu">
                         <div class="p-3 space-y-3">
                             <div class="flex justify-between items-center gap-2 border-b border-blue-200 dark:border-blue-700 pb-2">
                                 <h4 class="text-sm font-semibold text-blue-700 dark:text-blue-300">System Status</h4>
                                 <div class="flex gap-2 items-center">
                                     <div :title="isModelOK ? 'Model OK' : 'Model Error'" :class="['p-1 rounded-full transition-transform hover:scale-110', isModelOK ? 'text-green-500 dark:text-green-400' : 'text-red-500 dark:text-red-400']">
                                         <i :data-feather="isModelOK ? 'check-circle' : 'x-octagon'" class="w-5 h-5"></i>
                                     </div>
                                     <div :title="!isGenerating ? 'Ready' : 'Generating...'" class="p-1 rounded-full transition-transform hover:scale-110" :class="[!isGenerating ? 'text-green-500 dark:text-green-400' : 'text-yellow-500 dark:text-yellow-400']">
                                         <i :data-feather="!isGenerating ? 'zap' : 'loader'" :class="['w-5 h-5', {'animate-spin': isGenerating}]"></i>
                                     </div>
                                     <div :title="isConnected ? 'Connected' : 'Disconnected'" class="p-1 rounded-full transition-transform hover:scale-110" :class="[isConnected ? 'text-green-500 dark:text-green-400' : 'text-red-500 dark:text-red-400']">
                                         <i :data-feather="isConnected ? 'wifi' : 'wifi-off'" class="w-5 h-5"></i>
                                     </div>
                                 </div>
                             </div>

                             <div class="flex flex-wrap gap-2 justify-center">
                                 <ActionButton @click="restartProgram" icon="power" title="Restart LoLLMs" class="btn-secondary btn-sm flex-1 min-w-[100px] justify-center"/>
                                 <ActionButton @click="refreshPage" icon="refresh-ccw" title="Refresh Page" class="btn-secondary btn-sm flex-1 min-w-[100px] justify-center"/>
                                 <ActionButton href="/docs" icon="file-text" title="API Docs" class="btn-secondary btn-sm flex-1 min-w-[100px] justify-center" target="_blank"/>
                                 <button @click="showNews()" class="btn btn-secondary btn-sm flex-1 min-w-[100px] justify-center">
                                     <i data-feather="bell" class="w-4 h-4 mr-1.5"></i> News
                                 </button>
                             </div>

                             <div class="flex justify-center items-center gap-3 pt-2 border-t border-blue-200 dark:border-blue-700">
                                 <SocialIcon :href="githubRepoUrl" icon="github" title="GitHub" class="w-5 h-5"/>
                                 <SocialIcon href="https://www.youtube.com/channel/UCJzrg0cyQV2Z30SQ1v2FdSQ" icon="youtube" title="YouTube" class="w-5 h-5"/>
                                 <SocialIcon href="https://x.com/ParisNeo_AI" icon="x" title="Twitter/X" class="w-5 h-5"/>
                                 <SocialIcon href="https://discord.com/channels/1092918764925882418" icon="discord" title="Discord" class="w-5 h-5"/>
                             </div>
                         </div>
                     </div>
                 </transition>
             </div>
          </div>
      </div>
    </div>
  </div>

  <InputBox prompt-text="Enter the URL to the page to use as discussion support" @ok="handleWebUrlOk" ref="web_url_input_box"></InputBox>
  <Toast ref="toast" />
  <MessageBox ref="messageBox" />
  <YesNoDialog ref="yesNoDialog" class="z-[60]" />
  <UniversalForm ref="universalForm" class="z-[60]" />
   <div v-show="progress_visibility" role="status" class="fixed m-0 p-2 left-2 bottom-2 min-w-[24rem] max-w-[24rem] h-auto flex flex-col justify-center items-center rounded-lg shadow-lg z-[60] panels-color">
       <ProgressBar ref="progress" :progress="progress_value" class="w-full h-3"></ProgressBar>
       <p class="text-sm text-blue-800 dark:text-blue-100 animate-pulse mt-1">{{ loading_infos }} ...</p>
   </div>
</template>

<script>
import { useStore } from 'vuex'; // Keep useStore for mapping purposes if preferred, or use this.$store directly
import feather from 'feather-icons';
import axios from 'axios';
import hljs from 'highlight.js'; // Keep hljs import

import Navigation from '@/components/Navigation.vue';
import ActionButton from '@/components/ActionButton.vue';
import SocialIcon from '@/components/SocialIcon.vue';
import Toast from '@/components/Toast.vue';
import MessageBox from "@/components/MessageBox.vue";
import ProgressBar from "@/components/ProgressBar.vue";
import InputBox from "@/components/input_box.vue";
import UniversalForm from '../components/UniversalForm.vue';
import YesNoDialog from '../components/YesNoDialog.vue';

export default {
  name: 'TopBar',
  components: {
    Navigation, ActionButton, SocialIcon, Toast, MessageBox,
    ProgressBar, InputBox, UniversalForm, YesNoDialog
  },
  emits: ['update:pinned', 'update:occupyingSpace'],
  data() {
    return {
      isVisible: false,
      isPinned: JSON.parse(localStorage.getItem('isPinned') || 'false'),
      hideTimeout: null,
      themeDropdownOpen: false,
      isLanguageMenuVisible: false,
      isInfosMenuVisible: false,
      infoMenuHover: false,
      starCount: null,
      currentTheme: localStorage.getItem('preferred-theme') || 'default',
      availableThemes: [],
      customLanguage: '',
      githubRepoUrl: "https://github.com/ParisNeo/lollms-webui",
      // No need for template refs in data
      // Variables for system theme listener management
      darkModeMediaQuery: null,
      handleSystemThemeChangeFunc: null,
    };
  },
  computed: {
    // Map state from Vuex store
    progress_visibility() { return this.$store.state.progress_visibility; },
    progress_value() { return this.$store.state.progress_value; },
    loading_infos() { return this.$store.state.loading_infos; },
    isModelOK() { return this.$store.state.isModelOk; },
    isGenerating() { return this.$store.state.isGenerating; },
    isConnected() { return this.$store.state.isConnected; },
    languages() { return this.$store.state.languages || ['English']; },
    language() { return this.$store.state.language || 'English'; },

    // Local computed properties
    isDarkMode() {
      return document.documentElement.classList.contains('dark');
    },
    isEffectivelyVisible() {
      return this.isPinned || this.isVisible;
    },
    formattedStarCount() {
      if (this.starCount === null || this.starCount === 'N/A') return '?';
      const num = Number(this.starCount);
      return num >= 1000 ? `${(num / 1000).toFixed(1)}k` : num.toString();
    },
    currentLanguageDisplay() {
        const lang = this.language;
        if (lang?.length === 2) return lang.toUpperCase();
        if (lang?.toLowerCase().startsWith('en')) return 'EN';
        if (lang?.toLowerCase().startsWith('fr')) return 'FR';
        if (lang?.toLowerCase().startsWith('de')) return 'DE';
        if (lang?.toLowerCase().startsWith('es')) return 'ES';
        return lang ? lang.slice(0, 2).toUpperCase() : '??';
    }
  },
  watch: {
    isEffectivelyVisible(newValue) {
      this.$emit('update:occupyingSpace', newValue);
      this.$nextTick(() => feather.replace());
    },
    // Watch store state directly (ensure $store is reactive)
    '$store.state.isTopBarPinned'(newVal) {
      if (this.isPinned !== newVal) {
        this.isPinned = newVal;
        localStorage.setItem('isPinned', JSON.stringify(newVal));
        this.isVisible = true; // Show when pinning state changes via store
      }
    },
    '$store.state.config': {
      handler() {
        this.$nextTick(() => feather.replace());
      },
      deep: true
    }
  },
  methods: {
    // Methods corresponding to functions in setup
    show() {
      clearTimeout(this.hideTimeout);
      this.isVisible = true;
    },
    hide() {
      if (!this.isPinned) {
        this.hideTimeout = setTimeout(() => {
            // Check if the mouse is actually outside the container
            if (!this.$refs.topbarContainer?.matches(':hover')) {
                 this.isVisible = false;
            }
        }, 150);
      }
    },
    hideUnlessEnteringTopbar() {
      this.hideTimeout = setTimeout(() => {
        this.isVisible = false;
      }, 300);
    },
    clearHideTimeout() {
        clearTimeout(this.hideTimeout);
        // If mouse enters topbar container directly, ensure it's visible
        if (!this.isVisible && !this.isPinned) {
             this.isVisible = true;
        }
    },
    togglePin() {
      const newState = !this.isPinned;
      this.isPinned = newState;
      localStorage.setItem('isPinned', JSON.stringify(newState));
      this.isVisible = true; // Ensure visible when pinning/unpinning
      this.$store.commit('setTopBarPinned', newState);
      this.$emit('update:pinned', newState); // Keep emitting prop update if parent uses it
      this.$nextTick(() => feather.replace());
    },
    async fetchThemes() {
        try {
            const response = await axios.get('/get_themes');
            this.availableThemes = response.data.sort();
            // Ensure 'default' exists if it's the current or needed fallback
            if (this.currentTheme === 'default' && !this.availableThemes.includes('default')) {
                 this.availableThemes.unshift('default');
            }
            // If current theme isn't available, reset to default
            if (!this.availableThemes.includes(this.currentTheme)) {
                await this.selectTheme('default'); // Use await if selectTheme becomes async
            }
         } catch (error) {
            console.error('Error fetching themes:', error);
            this.availableThemes = ['default']; // Fallback
            if (this.currentTheme !== 'default') {
                 await this.selectTheme('default');
            }
        }
    },
    async selectTheme(themeName) { // Make async if loadTheme is async
        await this.loadTheme(themeName);
        this.themeDropdownOpen = false;
    },
    async loadTheme(themeName) {
         console.log(`Attempting to load theme: ${themeName}`);
         try {
             const timestamp = new Date().getTime();
             const response = await axios.get(`/themes/${themeName}.css?v=${timestamp}`);

             // Remove existing theme style if present
             const existingStyle = document.getElementById('theme-styles');
             if (existingStyle) existingStyle.remove();

             // Add new theme style
             const styleElement = document.createElement('style');
             styleElement.id = 'theme-styles';
             styleElement.textContent = response.data;
             document.head.appendChild(styleElement);

             // Update local storage and state
             localStorage.setItem('preferred-theme', themeName);
             this.currentTheme = themeName;

             // Wait for DOM update and check dark mode
             await this.$nextTick();
             this.checkAndUpdateDarkMode(); // This now checks and potentially loads hljs style

             // Update theme variables in store
             const styles = getComputedStyle(document.documentElement);
             const theme_vars = {
                 lollms_title: styles.getPropertyValue('--lollms-title').trim() || 'LoLLMS',
                 activate_dropping_animation: styles.getPropertyValue('--activate-dropping-animation').trim() === '1',
                 falling_object: styles.getPropertyValue('--falling-object').trim(),
                 lollms_welcome_short_message: styles.getPropertyValue('--lollms-welcome-short-message').trim() || 'Welcome',
                 lollms_welcome_message: styles.getPropertyValue('--lollms-welcome-message').trim() || 'Welcome to LoLLMS',
             };
             this.$store.commit('setThemeVars', theme_vars);

             this.$nextTick(() => feather.replace()); // Replace icons after theme change

         } catch (error) {
             console.error(`Failed to load theme: ${themeName}`, error);
             this.$refs.toast?.showToast(`Error loading theme: ${themeName}`, 5, false);
             // Attempt to load default theme if the selected one failed and isn't already default
             if (this.currentTheme !== 'default') {
                 await this.loadTheme('default');
             }
         }
     },
     checkAndUpdateDarkMode() {
        const wasDarkMode = this.isDarkMode; // Check based on class before potential changes
        const currentIsDark = document.documentElement.classList.contains('dark');

        if (wasDarkMode !== currentIsDark || !document.getElementById('highlight-js-style')) {
             console.log("Dark mode status potentially changed, isDark:", currentIsDark);
             this.loadHighlightJsStyle(currentIsDark);
        }
         this.$nextTick(() => feather.replace()); // Ensure icons are updated after mode change
    },
     loadHighlightJsStyle(isDark) {
        const styleId = 'highlight-js-style';
        const existingStyle = document.getElementById(styleId);
        if (existingStyle) existingStyle.remove();

        const link = document.createElement('link');
        link.id = styleId;
        link.rel = 'stylesheet';
        if (isDark) {
             link.href = 'https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/tokyo-night-dark.min.css';
        } else {
             link.href = 'https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/stackoverflow-light.min.css';
        }
        document.head.appendChild(link);
        console.log(`Loaded highlight.js style: ${isDark ? 'Dark' : 'Light'}`);
     },
     themeSwitch() {
         if (document.documentElement.classList.contains("dark")) {
             document.documentElement.classList.remove("dark");
             localStorage.setItem("theme-mode", "light");
         } else {
             document.documentElement.classList.add("dark");
             localStorage.setItem("theme-mode", "dark");
         }
         this.checkAndUpdateDarkMode(); // Update hljs style and icons
     },
     async selectLanguage(selectedLang) {
        await this.$store.dispatch('changeLanguage', selectedLang);
        this.isLanguageMenuVisible = false;
        this.$nextTick(() => feather.replace());
     },
     async deleteLanguage(langToDelete) {
         this.$refs.yesNoDialog?.show(`Are you sure you want to delete the language "${langToDelete}"?`, async () => {
             try {
                 await this.$store.dispatch('deleteLanguage', langToDelete);
             } catch (error) {
                 console.error("Error deleting language:", error);
                 this.$refs.toast?.showToast(`Failed to delete language: ${error.message || error}`, 4, false);
             }
         });
     },
     addCustomLanguage() {
        const newLang = this.customLanguage.trim();
         if (newLang) {
            if (this.languages.map(l => l.toLowerCase()).includes(newLang.toLowerCase())) {
                 this.$refs.toast?.showToast(`Language "${newLang}" already exists.`, 4, false);
            } else {
                 this.selectLanguage(newLang); // selectLanguage is now async
                 this.customLanguage = '';
            }
         }
     },
     toggleThemeDropDown() {
        this.themeDropdownOpen = !this.themeDropdownOpen;
        // Close other menus
        this.isLanguageMenuVisible = false;
        this.isInfosMenuVisible = false;
     },
     toggleLanguageMenu() {
        this.isLanguageMenuVisible = !this.isLanguageMenuVisible;
        // Close other menus
        this.themeDropdownOpen = false;
        this.isInfosMenuVisible = false;
     },
    showInfosMenu() {
      this.infoMenuHover = true;
      if (!this.isInfosMenuVisible) {
        this.isInfosMenuVisible = true;
        // Close other menus
        this.themeDropdownOpen = false;
        this.isLanguageMenuVisible = false;
        this.$nextTick(() => feather.replace()); // Replace icons if menu content changes
      }
    },
    hideInfosMenu() {
      this.infoMenuHover = false;
      setTimeout(() => {
        if (!this.infoMenuHover) {
          this.isInfosMenuVisible = false;
        }
      }, 150); // Small delay to allow moving mouse into the menu
    },
    showNews() {
        this.$store.state.news?.show();
    },
    refreshPage() {
        window.location.reload();
    },
    restartProgram() {
        this.$store.state.yesNoDialog?.show("Are you sure you want to restart LoLLMs?", ()=>{
             axios.get('/restart_program').then(()=>{
                 this.$store.state.toast?.showToast("Restarting server...", 4, true);
             }).catch(error => {
                 console.error("Error restarting server:", error);
                 this.$store.state.toast?.showToast(`Failed to send restart command: ${error.response?.data?.error || error.message}`, 5, false);
             });
         });
     },
    async fetchGitHubStars() {
         try {
            // Use axios or fetch, fetch shown here for variety
            const response = await fetch(this.githubRepoUrl.replace('github.com', 'api.github.com/repos'), {
                 headers: { 'Accept': 'application/vnd.github.v3+json' }
            });
            if (!response.ok) {
                const rateLimitRemaining = response.headers.get('X-RateLimit-Remaining');
                const rateLimitReset = response.headers.get('X-RateLimit-Reset');
                let errorMsg = `HTTP error! status: ${response.status}`;
                if (rateLimitRemaining === '0') {
                    const resetTime = new Date(parseInt(rateLimitReset) * 1000);
                    errorMsg += ` (GitHub API rate limit exceeded. Resets at ${resetTime.toLocaleTimeString()})`;
                }
                 throw new Error(errorMsg);
            }
            const data = await response.json();
            this.starCount = data.stargazers_count;
         } catch (error) {
            console.error('Error fetching GitHub stars:', error);
            this.starCount = 'N/A'; // Indicate error fetching stars
         }
    },
    handleWebUrlOk(url) {
        console.log("Web URL submitted:", url);
        this.$store.dispatch('processWebUrl', url);
    },
    // Click outside handler for dropdowns
    handleClickOutside(event) {
      const themeButton = event.target.closest('button[title="Select Theme"]');
      if (this.$refs.themeMenu && !this.$refs.themeMenu.contains(event.target) && !themeButton) {
        this.themeDropdownOpen = false;
      }
      const langButton = event.target.closest('button[title="Select Language"]');
      if (this.$refs.languageMenu && !this.$refs.languageMenu.contains(event.target) && !langButton) {
        this.isLanguageMenuVisible = false;
      }
      // Info menu hides on mouseleave primarily, but can add outside click too if needed
    },
    // Initial theme check based on storage and system preference
    themeCheckInitial() {
        const storedMode = localStorage.getItem("theme-mode");
        const systemPrefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;

        if (storedMode === "dark" || (!storedMode && systemPrefersDark)) {
            if (!document.documentElement.classList.contains('dark')) {
                document.documentElement.classList.add("dark");
            }
        } else {
             if (document.documentElement.classList.contains('dark')) {
                document.documentElement.classList.remove("dark");
            }
        }
         // Call this AFTER setting the class initially
         this.checkAndUpdateDarkMode();
    },
    // Listener for system theme changes
    handleSystemThemeChange(e) {
        // Only apply system theme if no explicit theme-mode is stored
        if (!localStorage.getItem("theme-mode")) {
          if (e.matches) { // System prefers dark
            if (!document.documentElement.classList.contains('dark')) {
              document.documentElement.classList.add('dark');
              this.checkAndUpdateDarkMode(); // Update styles and icons
            }
          } else { // System prefers light
             if (document.documentElement.classList.contains('dark')) {
               document.documentElement.classList.remove('dark');
               this.checkAndUpdateDarkMode(); // Update styles and icons
            }
          }
        }
    }
  },
  async mounted() {
    // Assign refs to store AFTER component is mounted
    this.$store.state.toast = this.$refs.toast;
    this.$store.state.messageBox = this.$refs.messageBox;
    this.$store.state.universalForm = this.$refs.universalForm;
    this.$store.state.yesNoDialog = this.$refs.yesNoDialog;
    // No need to assign web_url_input_box to store unless globally needed

    // Add global click listener
    document.addEventListener('click', this.handleClickOutside, true);

    // Fetch initial data and setup
    await this.fetchThemes();
    await this.loadTheme(this.currentTheme); // Load theme after fetching list
    this.themeCheckInitial(); // Set initial dark/light mode
    this.fetchGitHubStars();

    // Sync isPinned with store if necessary (initial value already set in data)
    const initialPinState = JSON.parse(localStorage.getItem('isPinned') || 'false');
    if (this.$store.state.isTopBarPinned === null) { // Initialize store if not set
         this.$store.commit('setTopBarPinned', initialPinState);
    }
    // Make sure local state matches store state if store was already set
    this.isPinned = this.$store.state.isTopBarPinned;
    this.isVisible = this.isPinned; // Initial visibility based on pinned state

    // Initial feather icon replacement
    this.$nextTick(() => feather.replace());

    // Setup system theme listener
    this.darkModeMediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    // Store the bound function to remove it later
    this.handleSystemThemeChangeFunc = this.handleSystemThemeChange.bind(this);
    this.darkModeMediaQuery.addEventListener('change', this.handleSystemThemeChangeFunc);

    // Emit initial space occupation state
    this.$emit('update:occupyingSpace', this.isEffectivelyVisible);
  },
  beforeUnmount() {
    // Clean up listeners and timeouts
    document.removeEventListener('click', this.handleClickOutside, true);
    if (this.darkModeMediaQuery && this.handleSystemThemeChangeFunc) {
        this.darkModeMediaQuery.removeEventListener('change', this.handleSystemThemeChangeFunc);
    }
    clearTimeout(this.hideTimeout);
  }
}
</script>

<style scoped>
/* Styles remain the same */
.theme-dropdown {
    @apply absolute right-0 mt-1 w-48 z-[52] overflow-hidden;
}
.language-dropdown {
    @apply absolute right-0 mt-1 w-64 z-[52] overflow-hidden;
}
.info-dropdown {
     @apply absolute right-0 mt-1 z-[52] w-auto min-w-[300px] max-w-md;
}
.context-menu-transition-enter-active { @apply transition duration-200 ease-out; }
.context-menu-transition-enter-from { @apply transform scale-95 opacity-0 -translate-y-2; }
.context-menu-transition-enter-to { @apply transform scale-100 opacity-100 translate-y-0; }
.context-menu-transition-leave-active { @apply transition duration-150 ease-in; }
.context-menu-transition-leave-from { @apply transform scale-100 opacity-100 translate-y-0; }
.context-menu-transition-leave-to { @apply transform scale-95 opacity-0 -translate-y-2; }
.context-menu {
  @apply bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-md shadow-lg;
}
.context-menu-item {
  @apply px-3 py-1.5 text-sm text-gray-700 dark:text-gray-200 hover:bg-blue-50 dark:hover:bg-blue-900 cursor-pointer transition-colors duration-150 flex items-center;
}
.context-menu-item-icon {
  @apply mr-2 text-blue-500 dark:text-blue-400 w-3.5 h-3.5;
}
.scrollbar {
  scrollbar-width: thin;
  scrollbar-color: theme('colors.blue.300') theme('colors.blue.100');
}
.scrollbar::-webkit-scrollbar { width: 6px; height: 6px; }
.scrollbar::-webkit-scrollbar-track { @apply bg-blue-100 dark:bg-gray-700 rounded; }
.scrollbar::-webkit-scrollbar-thumb { @apply bg-blue-400 dark:bg-blue-600 rounded; }
.scrollbar::-webkit-scrollbar-thumb:hover { @apply bg-blue-500 dark:bg-blue-500; }
</style>