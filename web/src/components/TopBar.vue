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
import { ref, computed, onMounted, onBeforeUnmount, nextTick, watch } from 'vue';
import { useStore } from 'vuex';
import feather from 'feather-icons';
import axios from 'axios';
import hljs from 'highlight.js';

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
  setup(_, { emit }) {
    const store = useStore();

    const toast = ref(null);
    const messageBox = ref(null);
    const universalForm = ref(null);
    const yesNoDialog = ref(null);
    const web_url_input_box = ref(null);
    const topbarContainer = ref(null);
    const themeMenu = ref(null);
    const languageMenu = ref(null);

    const isVisible = ref(false);
    const isPinned = ref(JSON.parse(localStorage.getItem('isPinned') || 'false'));
    const hideTimeout = ref(null);
    const themeDropdownOpen = ref(false);
    const isLanguageMenuVisible = ref(false);
    const isInfosMenuVisible = ref(false);
    const infoMenuHover = ref(false);
    const starCount = ref(null);
    const currentTheme = ref(localStorage.getItem('preferred-theme') || 'default');
    const availableThemes = ref([]);
    const customLanguage = ref('');
    const githubRepoUrl = "https://github.com/ParisNeo/lollms-webui";

    const progress_visibility = computed(() => store.state.progress_visibility);
    const progress_value = computed(() => store.state.progress_value);
    const loading_infos = computed(() => store.state.loading_infos);
    const isModelOK = computed(() => store.state.isModelOk);
    const isGenerating = computed(() => store.state.isGenerating);
    const isConnected = computed(() => store.state.isConnected);
    const languages = computed(() => store.state.languages || ['English']);
    const language = computed(() => store.state.language || 'English');

    const isDarkMode = computed(() => document.documentElement.classList.contains('dark'));
    const isEffectivelyVisible = computed(() => isPinned.value || isVisible.value);
    const formattedStarCount = computed(() => {
      if (starCount.value === null || starCount.value === 'N/A') return '?';
      const num = Number(starCount.value);
      return num >= 1000 ? `${(num / 1000).toFixed(1)}k` : num.toString();
    });
     const currentLanguageDisplay = computed(() => {
        const lang = language.value;
        if (lang?.length === 2) return lang.toUpperCase();
        if (lang?.toLowerCase().startsWith('en')) return 'EN';
        if (lang?.toLowerCase().startsWith('fr')) return 'FR';
        if (lang?.toLowerCase().startsWith('de')) return 'DE';
        if (lang?.toLowerCase().startsWith('es')) return 'ES';
        return lang ? lang.slice(0, 2).toUpperCase() : '??';
     });

    const show = () => {
      clearTimeout(hideTimeout.value);
      isVisible.value = true;
    };

    const hide = () => {
      if (!isPinned.value) {
        hideTimeout.value = setTimeout(() => {
           if (!topbarContainer.value?.matches(':hover')) {
               isVisible.value = false;
           }
        }, 150);
      }
    };

    const hideUnlessEnteringTopbar = () => {
        hideTimeout.value = setTimeout(() => {
            isVisible.value = false;
        }, 300);
    };

    const clearHideTimeout = () => {
        clearTimeout(hideTimeout.value);
        if (!isVisible.value && !isPinned.value) {
             isVisible.value = true;
        }
    };

    const togglePin = () => {
      const newState = !isPinned.value;
      isPinned.value = newState;
      localStorage.setItem('isPinned', JSON.stringify(newState));
      isVisible.value = true;
      store.commit('setTopBarPinned', newState);
      emit('update:pinned', newState);
      nextTick(feather.replace);
    };

     const fetchThemes = async () => {
        try {
            const response = await axios.get('/get_themes');
            availableThemes.value = response.data.sort();
            if (currentTheme.value === 'default' && !availableThemes.value.includes('default')) {
                 availableThemes.value.unshift('default');
            }
            if (!availableThemes.value.includes(currentTheme.value)) {
                selectTheme('default');
            }
         } catch (error) {
            console.error('Error fetching themes:', error);
            availableThemes.value = ['default'];
            if (currentTheme.value !== 'default') {
                selectTheme('default');
            }
        }
    };
    const selectTheme = (themeName) => {
        loadTheme(themeName);
        themeDropdownOpen.value = false;
    };
    const loadTheme = async (themeName) => {
         console.log(`Attempting to load theme: ${themeName}`);
         try {
             const timestamp = new Date().getTime();
             const response = await axios.get(`/themes/${themeName}.css?v=${timestamp}`);

             const existingStyle = document.getElementById('theme-styles');
             if (existingStyle) existingStyle.remove();

             const styleElement = document.createElement('style');
             styleElement.id = 'theme-styles';
             styleElement.textContent = response.data;
             document.head.appendChild(styleElement);

             localStorage.setItem('preferred-theme', themeName);
             currentTheme.value = themeName;

             await nextTick();
             checkAndUpdateDarkMode();

             const styles = getComputedStyle(document.documentElement);
             const theme_vars = {
                 lollms_title: styles.getPropertyValue('--lollms-title').trim() || 'LoLLMS',
                 activate_dropping_animation: styles.getPropertyValue('--activate-dropping-animation').trim() === '1',
                 falling_object: styles.getPropertyValue('--falling-object').trim(),
                 lollms_welcome_short_message: styles.getPropertyValue('--lollms-welcome-short-message').trim() || 'Welcome',
                 lollms_welcome_message: styles.getPropertyValue('--lollms-welcome-message').trim() || 'Welcome to LoLLMS',
             };
             store.commit('setThemeVars', theme_vars);

             nextTick(feather.replace);

         } catch (error) {
             console.error(`Failed to load theme: ${themeName}`, error);
             toast.value?.showToast(`Error loading theme: ${themeName}`, 5, false);
              if (currentTheme.value !== 'default') {
                 await loadTheme('default');
              }
         }
     };
     const checkAndUpdateDarkMode = () => {
        const wasDarkMode = isDarkMode.value;
        const currentIsDark = document.documentElement.classList.contains('dark');

        if (wasDarkMode !== currentIsDark) {
             console.log("Dark mode status changed, isDark:", currentIsDark);
             loadHighlightJsStyle(currentIsDark);
        }
         nextTick(feather.replace);
    };

     const loadHighlightJsStyle = (isDark) => {
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
     };
    const themeSwitch = () => {
         if (document.documentElement.classList.contains("dark")) {
             document.documentElement.classList.remove("dark");
             localStorage.setItem("theme-mode", "light");
         } else {
             document.documentElement.classList.add("dark");
             localStorage.setItem("theme-mode", "dark");
         }
         checkAndUpdateDarkMode();
     };

     const selectLanguage = async (selectedLang) => {
        await store.dispatch('changeLanguage', selectedLang);
        isLanguageMenuVisible.value = false;
        nextTick(feather.replace);
     };
     const deleteLanguage = async (langToDelete) => {
         yesNoDialog.value?.show(`Are you sure you want to delete the language "${langToDelete}"?`, async () => {
             try {
                 await store.dispatch('deleteLanguage', langToDelete);
             } catch (error) {
                 console.error("Error deleting language:", error);
                 toast.value?.showToast(`Failed to delete language: ${error.message || error}`, 4, false);
             }
         });
     };
     const addCustomLanguage = () => {
        const newLang = customLanguage.value.trim();
         if (newLang) {
            if (languages.value.map(l => l.toLowerCase()).includes(newLang.toLowerCase())) {
                 toast.value?.showToast(`Language "${newLang}" already exists.`, 4, false);
            } else {
                 selectLanguage(newLang);
                 customLanguage.value = '';
            }
         }
     };
     const toggleThemeDropDown = () => {
        themeDropdownOpen.value = !themeDropdownOpen.value;
        isLanguageMenuVisible.value = false;
        isInfosMenuVisible.value = false;
     };
     const toggleLanguageMenu = () => {
        isLanguageMenuVisible.value = !isLanguageMenuVisible.value;
        themeDropdownOpen.value = false;
        isInfosMenuVisible.value = false;
     };

    const showInfosMenu = () => {
      infoMenuHover.value = true;
      if (!isInfosMenuVisible.value) {
        isInfosMenuVisible.value = true;
        themeDropdownOpen.value = false;
        isLanguageMenuVisible.value = false;
        nextTick(feather.replace);
      }
    };
    const hideInfosMenu = () => {
      infoMenuHover.value = false;
      setTimeout(() => {
        if (!infoMenuHover.value) {
          isInfosMenuVisible.value = false;
        }
      }, 150);
    };

    const showNews = () => { store.state.news?.show(); };
    const refreshPage = () => { window.location.reload(); };
    const restartProgram = () => {
        store.state.yesNoDialog?.show("Are you sure you want to restart LoLLMs?", ()=>{
             axios.get('/restart_program').then(()=>{
                 store.state.toast?.showToast("Restarting server...", 4, true);
             }).catch(error => {
                 console.error("Error restarting server:", error);
                 store.state.toast?.showToast(`Failed to send restart command: ${error.response?.data?.error || error.message}`, 5, false);
             });
         });
     };
    const fetchGitHubStars = async () => {
         try {
            const response = await fetch(githubRepoUrl.replace('github.com', 'api.github.com/repos'), {
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
            starCount.value = data.stargazers_count;
         } catch (error) {
            console.error('Error fetching GitHub stars:', error);
            starCount.value = 'N/A';
         }
    };
    const handleWebUrlOk = (url) => {
        console.log("Web URL submitted:", url);
        store.dispatch('processWebUrl', url);
    };

    const handleClickOutside = (event) => {
      const themeButton = event.target.closest('button[title="Select Theme"]');
      if (themeMenu.value && !themeMenu.value.contains(event.target) && !themeButton) {
        themeDropdownOpen.value = false;
      }
      const langButton = event.target.closest('button[title="Select Language"]');
      if (languageMenu.value && !languageMenu.value.contains(event.target) && !langButton) {
        isLanguageMenuVisible.value = false;
      }
    };

    const themeCheckInitial = () => {
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
         checkAndUpdateDarkMode();
    };

    onMounted(async () => {
       store.commit('setToastRef', toast.value);
       store.commit('setMessageBoxRef', messageBox.value);
       store.commit('setUniversalFormRef', universalForm.value);
       store.commit('setYesNoDialogRef', yesNoDialog.value);
       store.commit('setWebUrlInputBoxRef', web_url_input_box.value);

      document.addEventListener('click', handleClickOutside, true);

      await fetchThemes();
      await loadTheme(currentTheme.value);
      themeCheckInitial();
      fetchGitHubStars();

      const initialPinState = JSON.parse(localStorage.getItem('isPinned') || 'false');
      if (store.state.isTopBarPinned === null) {
           store.commit('setTopBarPinned', initialPinState);
      }
      isPinned.value = store.state.isTopBarPinned;
      isVisible.value = isPinned.value;

      nextTick(feather.replace);

      const darkModeMediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
      const handleSystemThemeChange = (e) => {
        if (!localStorage.getItem("theme-mode")) {
          if (e.matches) {
            if (!document.documentElement.classList.contains('dark')) {
              document.documentElement.classList.add('dark');
               checkAndUpdateDarkMode();
            }
          } else {
             if (document.documentElement.classList.contains('dark')) {
               document.documentElement.classList.remove('dark');
               checkAndUpdateDarkMode();
            }
          }
        }
      };
      darkModeMediaQuery.addEventListener('change', handleSystemThemeChange);

      onBeforeUnmount(() => {
        document.removeEventListener('click', handleClickOutside, true);
        darkModeMediaQuery.removeEventListener('change', handleSystemThemeChange);
        clearTimeout(hideTimeout.value);
      });

        emit('update:occupyingSpace', isEffectivelyVisible.value);
    });

     watch(isEffectivelyVisible, (newValue) => {
         emit('update:occupyingSpace', newValue);
         nextTick(feather.replace);
     });

     watch(() => store.state.isTopBarPinned, (newVal) => {
         if (isPinned.value !== newVal) {
             isPinned.value = newVal;
             localStorage.setItem('isPinned', JSON.stringify(newVal));
             isVisible.value = true;
         }
     });

      watch(() => store.state.config, () => {
          nextTick(() => feather.replace());
      }, { deep: true });


    return {
      toast, messageBox, universalForm, yesNoDialog, web_url_input_box,
      topbarContainer, themeMenu, languageMenu,
      isVisible, isPinned, themeDropdownOpen, isLanguageMenuVisible, isInfosMenuVisible,
      starCount, currentTheme, availableThemes, customLanguage, githubRepoUrl,
      progress_visibility, progress_value, loading_infos, isModelOK, isGenerating, isConnected,
      languages, language, isDarkMode, isEffectivelyVisible, formattedStarCount, currentLanguageDisplay,
      show, hide, hideUnlessEnteringTopbar, clearHideTimeout, togglePin,
      fetchThemes, selectTheme, loadTheme, themeSwitch, checkAndUpdateDarkMode,
      selectLanguage, deleteLanguage, addCustomLanguage, toggleThemeDropDown, toggleLanguageMenu,
      showInfosMenu, hideInfosMenu,
      showNews, refreshPage, restartProgram, fetchGitHubStars, handleWebUrlOk,
    };
  }
}
</script>

<style scoped>
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