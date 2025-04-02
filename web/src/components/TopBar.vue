<template>
  <div ref="topbar-wrapper" :class="['fixed top-0 left-0 right-0 z-50 transition-transform duration-300 ease-in-out', { 'pb-14': isPinned }]">
    <!-- Hover zone to trigger visibility when not pinned -->
    <div
      v-if="!isPinned"
      class="fixed top-0 left-0 w-full h-3 z-[51] cursor-pointer"
      @mouseenter="show"
    ></div>

    <!-- The actual top bar -->
    <div
      ref="topbar-container"
      :class="[
        'fixed top-0 left-0 right-0 z-50',
        'toolbar-color', // Theme background
        'shadow-lg',
        'transition-transform duration-300 ease-in-out',
        { '-translate-y-full': !isVisible && !isPinned, 'translate-y-0': isVisible || isPinned }
      ]"
      @mouseleave="hide"
    >
      <div class="flex justify-center">
        <div class="flex justify-between items-center w-full max-w-7xl px-2 sm:px-4 py-1">
          <!-- Left Slot (e.g., for Navigation) -->
          <div class="flex-shrink-0">
            <slot name="navigation">
              <!-- Default Navigation can be placed here if needed -->
               <Navigation></Navigation>
            </slot>
          </div>

          <!-- Center Spacer -->
          <div class="flex-grow"></div>

          <!-- Right Side Controls -->
          <div class="flex items-center gap-1 sm:gap-2">
            <!-- GitHub Stars -->
            <a
              v-if="starCount !== null"
              href="https://github.com/ParisNeo/lollms-webui"
              target="_blank"
              rel="noopener noreferrer"
              class="btn btn-secondary btn-sm hidden md:inline-flex items-center gap-1.5"
              title="Star us on GitHub!"
            >
              <svg class="w-4 h-4" viewBox="0 0 16 16" fill="currentColor">
                <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/>
              </svg>
              <span class="font-medium text-xs">{{ starCount }}</span>
            </a>

            <!-- Theme Switcher -->
            <div class="relative">
              <button
                @click.stop="toggleThemeDropDown"
                class="btn btn-secondary btn-sm inline-flex items-center justify-between w-28 sm:w-36"
                title="Select Theme"
              >
                <div class="flex items-center space-x-1.5 overflow-hidden">
                  <i data-feather="layout" class="w-4 h-4 flex-shrink-0"></i>
                  <span class="font-medium truncate text-xs">{{ currentTheme }}</span>
                </div>
                <i data-feather="chevron-down" :class="['w-4 h-4 flex-shrink-0 transition-transform duration-300', { 'rotate-180': themeDropdownOpen }]"></i>
              </button>
              <transition
                enter-active-class="transition duration-200 ease-out"
                enter-from-class="transform scale-95 opacity-0 -translate-y-2"
                enter-to-class="transform scale-100 opacity-100 translate-y-0"
                leave-active-class="transition duration-150 ease-in"
                leave-from-class="transform scale-100 opacity-100 translate-y-0"
                leave-to-class="transform scale-95 opacity-0 -translate-y-2"
              >
                <div
                  v-if="themeDropdownOpen"
                  ref="themeMenu"
                  class="context-menu absolute right-0 mt-1 w-48 z-[52] overflow-hidden"
                  role="menu"
                >
                  <div class="max-h-60 overflow-y-auto scrollbar">
                    <a
                      v-for="theme in availableThemes"
                      :key="theme"
                      @click="loadTheme(theme); currentTheme = theme; themeDropdownOpen = false"
                      class="context-menu-item flex items-center space-x-2 group"
                      role="menuitem"
                    >
                       <i data-feather="droplet" class="w-3.5 h-3.5 context-menu-item-icon group-hover:animate-pulse"></i>
                      <span class="truncate">{{ theme }}</span>
                    </a>
                  </div>
                </div>
              </transition>
            </div>

            <!-- Language Switcher -->
            <div class="relative">
                <button
                    @click="toggleLanguageMenu"
                    class="btn btn-secondary btn-sm inline-flex items-center"
                    title="Select Language"
                    aria-haspopup="true"
                    :aria-expanded="isLanguageMenuVisible"
                >
                    <span class="font-medium text-xs">{{ $store.state.language.slice(0, 2).toUpperCase() }}</span>
                    <i data-feather="chevron-down" :class="['w-4 h-4 ml-1 transition-transform duration-300', { 'rotate-180': isLanguageMenuVisible }]"></i>
                </button>
                <Transition
                    enter-active-class="transition duration-200 ease-out"
                    enter-from-class="transform scale-95 opacity-0 -translate-y-2"
                    enter-to-class="transform scale-100 opacity-100 translate-y-0"
                    leave-active-class="transition duration-150 ease-in"
                    leave-from-class="transform scale-100 opacity-100 translate-y-0"
                    leave-to-class="transform scale-95 opacity-0 -translate-y-2"
                >
                    <div
                        v-if="isLanguageMenuVisible"
                        ref="languageMenu"
                        class="context-menu absolute right-0 mt-1 w-64 z-[52] overflow-hidden"
                        role="menu"
                    >
                        <ul class="max-h-72 overflow-y-auto scrollbar py-1">
                            <li
                                v-for="language in languages"
                                :key="language"
                                class="context-menu-item flex items-center group pr-2"
                            >
                                <button
                                    @click.stop="deleteLanguage(language)"
                                    :class="['svg-button p-0.5 rounded-full opacity-0 group-hover:opacity-100 transition-opacity text-red-500 hover:bg-red-100 dark:hover:bg-red-900/50 mr-2', {'hidden': language === 'English'}]"
                                    :aria-label="`Delete ${language}`"
                                    title="Delete Language"
                                >
                                    <i data-feather="x" class="w-3 h-3"></i>
                                </button>
                                <div
                                    @click="selectLanguage(language)"
                                    :class="['flex-grow px-2 py-0.5 cursor-pointer rounded text-xs transition-colors', language === $store.state.language ? 'bg-blue-100 dark:bg-blue-700 text-blue-700 dark:text-blue-100 font-semibold' : 'hover:bg-blue-50 dark:hover:bg-blue-800']"
                                    role="menuitem"
                                >
                                    {{ language }}
                                </div>
                            </li>
                            <li class="px-3 pt-2 pb-1 border-t border-blue-200 dark:border-blue-700 mt-1">
                                <input
                                    type="text"
                                    v-model="customLanguage"
                                    @keyup.enter.prevent="addCustomLanguage"
                                    placeholder="Add new language..."
                                    class="input input-sm w-full"
                                >
                            </li>
                        </ul>
                    </div>
                </Transition>
            </div>

            <!-- Dark Mode Toggle -->
            <button
              @click="themeSwitch()"
              :title="isDarkMode ? 'Switch to Light theme' : 'Switch to Dark theme'"
              class="svg-button text-xl p-1.5"
            >
              <i :data-feather="isDarkMode ? 'sun' : 'moon'" class="w-4 h-4"></i>
            </button>

            <!-- Pin Button -->
            <button
              class="svg-button p-1.5 transition-transform hover:scale-110 focus:outline-none"
              @click="togglePin"
              :title="isPinned ? 'Unpin Top Bar' : 'Pin Top Bar'"
            >
              <svg class="w-4 h-4" :class="isPinned ? 'text-red-500 dark:text-red-400' : 'text-blue-600 dark:text-blue-400'" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
                  <path d="M16 12V4H17V2H7V4H8V12L6 14V16H11.5V22H12.5V16H18V14L16 12Z M8.8 14L10 12.8V4H14V12.8L15.2 14H8.8Z"/>
              </svg>
            </button>

            <!-- Info Button & Menu -->
            <div class="relative" @mouseleave="hideInfosMenu">
              <button
                @mouseenter="showInfosMenu"
                class="svg-button p-1.5"
                title="Status & Info"
              >
                 <i data-feather="info" class="w-5 h-5"></i>
              </button>

              <transition
                enter-active-class="transition duration-200 ease-out"
                enter-from-class="transform scale-95 opacity-0 -translate-y-2"
                enter-to-class="transform scale-100 opacity-100 translate-y-0"
                leave-active-class="transition duration-150 ease-in"
                leave-from-class="transform scale-100 opacity-100 translate-y-0"
                leave-to-class="transform scale-95 opacity-0 -translate-y-2"
              >
                <div
                  v-if="isInfosMenuVisible"
                  @mouseenter="showInfosMenu"
                  class="context-menu absolute right-0 mt-1 z-[52] w-auto min-w-[300px] max-w-md"
                  role="menu"
                >
                  <div class="p-3 space-y-3">
                    <!-- System Status -->
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

                    <!-- Actions -->
                    <div class="flex flex-wrap gap-2 justify-center">
                        <ActionButton @click="restartProgram" icon="power" title="Restart LoLLMs" class="btn-secondary btn-sm flex-1 min-w-[100px] justify-center"/>
                        <ActionButton @click="refreshPage" icon="refresh-ccw" title="Refresh Page" class="btn-secondary btn-sm flex-1 min-w-[100px] justify-center"/>
                        <ActionButton href="/docs" icon="file-text" title="API Docs" class="btn-secondary btn-sm flex-1 min-w-[100px] justify-center" target="_blank"/>
                        <button @click="showNews()" class="btn btn-secondary btn-sm flex-1 min-w-[100px] justify-center">
                            <i data-feather="bell" class="w-4 h-4 mr-1.5"></i> News
                        </button>
                    </div>

                    <!-- Socials -->
                    <div class="flex justify-center items-center gap-3 pt-2 border-t border-blue-200 dark:border-blue-700">
                        <SocialIcon href="https://github.com/ParisNeo/lollms-webui" icon="github" title="GitHub" class="w-5 h-5"/>
                        <SocialIcon href="https://www.youtube.com/channel/UCJzrg0cyQV2Z30SQ1v2FdSQ" icon="youtube" title="YouTube" class="w-5 h-5"/>
                        <SocialIcon href="https://x.com/ParisNeo_AI" icon="x" title="Twitter/X" class="w-5 h-5"/>
                        <SocialIcon href="https://discord.com/channels/1092918764925882418" icon="discord" title="Discord" class="w-5 h-5"/>
                    </div>
                  </div>
                </div>
              </transition>
            </div> <!-- End Info Button & Menu -->
          </div> <!-- End Right Side Controls -->
        </div>
      </div>
    </div> <!-- End Top Bar -->
  </div> <!-- End Wrapper -->

  <!-- Progress Bar Area -->
  <div v-show="progress_visibility" role="status" class="fixed m-0 p-2 left-2 bottom-2 min-w-[24rem] max-w-[24rem] h-auto flex flex-col justify-center items-center rounded-lg shadow-lg z-50 panels-color">
      <ProgressBar ref="progress" :progress="progress_value" class="w-full h-3"></ProgressBar>
      <p class="text-sm text-blue-800 dark:text-blue-100 animate-pulse mt-1">{{ loading_infos }} ...</p>
  </div>

  <!-- Utility Components -->
  <InputBox prompt-text="Enter the URL to the page to use as discussion support" @ok="addWebpage" ref="web_url_input_box"></InputBox>
  <Toast ref="toast" />
  <MessageBox ref="messageBox" />
  <YesNoDialog ref="yesNoDialog" class="z-[60]" />
  <UniversalForm ref="universalForm" class="z-[60]" />
</template>

<script>
import { ref, onMounted, onBeforeUnmount, computed, nextTick, watch } from 'vue';
import { useStore } from 'vuex';
import Navigation from '@/components/Navigation.vue';
import ActionButton from '@/components/ActionButton.vue';
import SocialIcon from '@/components/SocialIcon.vue';
import MessageBox from "@/components/MessageBox.vue";
import ProgressBar from "@/components/ProgressBar.vue";
import UniversalForm from '../components/UniversalForm.vue';
import Toast from '@/components/Toast.vue';
import YesNoDialog from '../components/YesNoDialog.vue';
import InputBox from "@/components/input_box.vue";
import axios from 'axios';
import feather from 'feather-icons';
import hljs from 'highlight.js';
// Import necessary highlight.js styles dynamically later based on theme

export default {
  name: 'TopBar',
  components: {
    Navigation,
    ActionButton,
    SocialIcon,
    Toast,
    MessageBox,
    ProgressBar,
    InputBox,
    UniversalForm,
    YesNoDialog
  },
  setup() {
    const store = useStore();
    const toast = ref(null);
    const messageBox = ref(null);
    const universalForm = ref(null);
    const yesNoDialog = ref(null);
    const web_url_input_box = ref(null);
    const themeMenu = ref(null); // Ref for theme dropdown
    const languageMenu = ref(null); // Ref for language dropdown

    const starCount = ref(null);
    const themeDropdownOpen = ref(false);
    const currentTheme = ref(localStorage.getItem('preferred-theme') || 'default');
    const availableThemes = ref([]);
    const isInfosMenuVisible = ref(false);
    const isVisible = ref(false); // Controls hover/show state
    const isPinned = ref(JSON.parse(localStorage.getItem('isPinned') || 'false'));
    const isLanguageMenuVisible = ref(false);
    const customLanguage = ref('');
    const isDarkMode = ref(false); // Reactive dark mode state

    const posts_headers = {
      'accept': 'application/json',
      'Content-Type': 'application/json'
    };

    // Computed properties
    const progress_visibility = computed(() => store.state.progress_visibility);
    const progress_value = computed(() => store.state.progress_value);
    const loading_infos = computed(() => store.state.loading_infos);
    const isModelOK = computed(() => store.state.isModelOk);
    const isGenerating = computed(() => store.state.isGenerating);
    const isConnected = computed(() => store.state.isConnected);
    const languages = computed(() => store.state.languages);
    const language = computed(() => store.state.language);


    // Methods
    const fetchThemes = async () => {
      try {
        const response = await axios.get('/get_themes');
        availableThemes.value = response.data;
        // Ensure current theme exists, reset if not
        if (!availableThemes.value.includes(currentTheme.value)) {
            currentTheme.value = 'default';
            localStorage.setItem('preferred-theme', 'default');
            loadTheme(currentTheme.value); // Load default if saved theme is invalid
        }
      } catch (error) {
        console.error('Error fetching themes:', error);
        availableThemes.value = ['default', 'Soft Bluish Theme']; // Basic fallback
      }
    };

    const toggleThemeDropDown = () => {
      themeDropdownOpen.value = !themeDropdownOpen.value;
      isLanguageMenuVisible.value = false; // Close other dropdown
      isInfosMenuVisible.value = false; // Close other dropdown
    };

    const addCustomLanguage = () => {
        if (customLanguage.value.trim() !== '') {
            selectLanguage(customLanguage.value.trim());
            customLanguage.value = '';
        }
    };

    const handleClickOutside = (event) => {
        if (themeMenu.value && !themeMenu.value.contains(event.target) && !event.target.closest('.btn')) {
            themeDropdownOpen.value = false;
        }
        if (languageMenu.value && !languageMenu.value.contains(event.target) && !event.target.closest('.btn')) {
            isLanguageMenuVisible.value = false;
        }
         // Close info menu if clicking outside - adjust selector if needed
        if (isInfosMenuVisible.value && !event.target.closest('.relative[title="Lollms News"]') && !event.target.closest('.context-menu')) {
           // hideInfosMenu(); // Need to define this if using setup() or adapt logic
        }
    };

    const saveTheme = (themeName) => {
        try {
            localStorage.setItem('preferred-theme', themeName);
        } catch (e) {
            console.warn('Failed to save theme preference:', e);
        }
    };

    const loadTheme = async (themeName) => {
      console.log(`Attempting to load theme: ${themeName}`);
      try {
        const response = await axios.get(`/themes/${themeName}.css`, {
          headers: { 'Cache-Control': 'no-cache', 'Pragma': 'no-cache', 'Expires': '0' }
        });

        const existingStyle = document.getElementById('theme-styles');
        if (existingStyle) existingStyle.remove();

        const styleElement = document.createElement('style');
        styleElement.id = 'theme-styles';
        styleElement.textContent = response.data;
        document.head.appendChild(styleElement);

        saveTheme(themeName);
        currentTheme.value = themeName; // Update reactive ref

        // Give the browser a moment to apply styles, then check dark mode
        await nextTick();
        checkAndUpdateDarkMode(); // Check dark mode based on new theme

        // Update theme variables in store
        const styles = getComputedStyle(document.documentElement);
        const theme_vars = {
            lollms_title: styles.getPropertyValue('--lollms-title').trim() || 'LoLLMS',
            activate_dropping_animation: styles.getPropertyValue('--activate-dropping-animation').trim() === '1',
            falling_object: styles.getPropertyValue('--falling-object').trim(),
            lollms_welcome_short_message: styles.getPropertyValue('--lollms-welcome-short-message').trim() || 'Welcome',
            lollms_welcome_message: styles.getPropertyValue('--lollms-welcome-message').trim() || 'Welcome to LoLLMS',
        };
        store.commit('setThemeVars', theme_vars);

        // Re-render Feather icons if needed
        nextTick(() => feather.replace());

      } catch (error) {
        console.error(`Failed to load theme: ${themeName}`, error);
        // Optionally revert to default or show error
      }
    };

    const checkAndUpdateDarkMode = () => {
        const wasDarkMode = isDarkMode.value;
        isDarkMode.value = document.documentElement.classList.contains('dark');
        console.log("Dark mode checked, isDark:", isDarkMode.value);

        // If dark mode status changed, potentially reload highlight.js theme
        if (wasDarkMode !== isDarkMode.value) {
            loadHighlightJsStyle(isDarkMode.value);
        }
         nextTick(() => feather.replace()); // Ensure icons are updated
    };

    // Function to load highlight.js styles
    const loadHighlightJsStyle = (isDark) => {
        const styleId = 'highlight-js-style';
        const existingStyle = document.getElementById(styleId);
        if (existingStyle) existingStyle.remove();

        const link = document.createElement('link');
        link.id = styleId;
        link.rel = 'stylesheet';
        if (isDark) {
            link.href = 'https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/tokyo-night-dark.min.css'; // Or your preferred dark style
        } else {
            link.href = 'https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/stackoverflow-light.min.css'; // Or your preferred light style
        }
        document.head.appendChild(link);
        console.log(`Loaded highlight.js style: ${isDark ? 'Dark' : 'Light'}`);
    };

    const themeSwitch = () => {
      if (document.documentElement.classList.contains("dark")) {
        document.documentElement.classList.remove("dark");
        localStorage.setItem("theme-mode", "light"); // Use a different key than theme name
      } else {
        document.documentElement.classList.add("dark");
        localStorage.setItem("theme-mode", "dark");
      }
      checkAndUpdateDarkMode(); // Update internal state and potentially hljs style
    };

    const selectLanguage = async (selectedLang) => {
        await store.dispatch('changeLanguage', selectedLang);
        // Logic to potentially update personality based on language (keep if needed)
        // ... existing logic ...
        isLanguageMenuVisible.value = false;
    };

    const deleteLanguage = async (langToDelete) => {
        if (langToDelete !== 'English') { // Prevent deleting English
             await store.dispatch('deleteLanguage', langToDelete);
             if (store.state.language === langToDelete) {
                 // If the deleted language was the active one, switch to English
                 await selectLanguage('English');
             }
        } else {
            toast.value.showToast("Cannot delete the default English language.", 4, false);
        }
        // Do not close the menu automatically on delete
    };

    const toggleLanguageMenu = () => {
        isLanguageMenuVisible.value = !isLanguageMenuVisible.value;
        themeDropdownOpen.value = false; // Close other dropdown
        isInfosMenuVisible.value = false; // Close other dropdown
    };

    const showInfosMenu = () => {
        if (!isInfosMenuVisible.value) {
            isInfosMenuVisible.value = true;
            themeDropdownOpen.value = false; // Close other dropdown
            isLanguageMenuVisible.value = false; // Close other dropdown
            nextTick(() => feather.replace());
        }
    };

    const hideInfosMenu = () => {
        // Use a small delay to allow moving mouse into the menu
        setTimeout(() => {
             // Check if the mouse is still over the button or the menu itself
             // This requires refs to the button and menu, or a more complex hover state management
             // For simplicity, we might just rely on mouseleave from the parent container
             isInfosMenuVisible.value = false;
         }, 100);

    };

    const show = () => { isVisible.value = true; };
    const hide = () => { if (!isPinned.value) isVisible.value = false; };

    const togglePin = () => {
        isPinned.value = !isPinned.value;
        isVisible.value = true; // Ensure it's visible when pinning
        localStorage.setItem('isPinned', JSON.stringify(isPinned.value));
        nextTick(() => feather.replace()); // Update icons if needed
    };

    const showNews = () => { store.state.news.show(); };

    const themeCheckInitial = () => {
        const storedMode = localStorage.getItem("theme-mode");
        const systemPrefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;

        if (storedMode === "dark" || (!storedMode && systemPrefersDark)) {
            document.documentElement.classList.add("dark");
        } else {
            document.documentElement.classList.remove("dark");
        }
        checkAndUpdateDarkMode(); // Sync internal state and load initial hljs style
    };

    const refreshPage = () => { window.location.reload(); };
    const restartProgram = () => { axios.get('/restart_program'); }; // Assuming endpoint exists

    const fetchGitHubStars = async () => {
        try {
            const response = await fetch('https://api.github.com/repos/ParisNeo/lollms-webui');
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            const data = await response.json();
            starCount.value = data.stargazers_count;
        } catch (error) {
            console.error('Error fetching GitHub stars:', error);
            starCount.value = 'N/A'; // Indicate failure
        }
    };

    // Lifecycle Hooks
    onMounted(async () => {
        // Assign refs to store
        store.state.toast = toast.value;
        store.state.messageBox = messageBox.value;
        store.state.universalForm = universalForm.value;
        store.state.yesNoDialog = yesNoDialog.value;
        store.state.web_url_input_box = web_url_input_box.value;

        document.addEventListener('click', handleClickOutside);

        await fetchThemes(); // Fetch themes first
        await loadTheme(currentTheme.value); // Load initial or saved theme
        themeCheckInitial(); // Check and apply dark/light mode preference

        fetchGitHubStars(); // Fetch stars

        isVisible.value = isPinned.value; // Initial visibility based on pin state

        nextTick(() => {
            feather.replace();
        });

         // Watch for changes in system preference
        const darkModeMediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
        const handleSystemThemeChange = (e) => {
            if (!localStorage.getItem("theme-mode")) { // Only react if no explicit mode is set
                if (e.matches) {
                    document.documentElement.classList.add('dark');
                } else {
                    document.documentElement.classList.remove('dark');
                }
                 checkAndUpdateDarkMode(); // Update state and hljs style
            }
        };
        darkModeMediaQuery.addEventListener('change', handleSystemThemeChange);

        // Cleanup listener on unmount
        onBeforeUnmount(() => {
            darkModeMediaQuery.removeEventListener('change', handleSystemThemeChange);
        });
    });

    onBeforeUnmount(() => {
        document.removeEventListener('click', handleClickOutside);
    });

    // Watchers
    watch(isPinned, (newVal) => {
        // When unpinned, ensure visibility matches hover state (might need refinement)
        if (!newVal) {
           // isVisible.value = false; // Or check hover state explicitly
        } else {
            isVisible.value = true; // Always visible when pinned
        }
    });

     watch(() => store.state.config, () => {
         nextTick(() => feather.replace());
     }, { deep: true });


    return {
      toast,
      messageBox,
      universalForm,
      yesNoDialog,
      web_url_input_box,
      themeMenu,
      languageMenu,
      starCount,
      themeDropdownOpen,
      currentTheme,
      availableThemes,
      isInfosMenuVisible,
      isVisible,
      isPinned,
      isLanguageMenuVisible,
      customLanguage,
      isDarkMode,
      progress_visibility,
      progress_value,
      loading_infos,
      isModelOK,
      isGenerating,
      isConnected,
      languages,
      language,
      fetchThemes,
      toggleThemeDropDown,
      addCustomLanguage,
      loadTheme,
      themeSwitch,
      selectLanguage,
      deleteLanguage,
      toggleLanguageMenu,
      showInfosMenu,
      hideInfosMenu,
      show,
      hide,
      togglePin,
      showNews,
      refreshPage,
      restartProgram,
      addWebpage: (url) => web_url_input_box.value.ok(url), // Example of calling child method
    };
  }
}
</script>

<style scoped>
/* Keep minimal specific styles, rely on theme CSS */
.topbar-wrapper { /* Wrapper to reserve space when pinned */
  height: 0; /* Default height */
}
.topbar-wrapper.pb-14 { /* Adjust based on actual topbar height */
  /* Placeholder height applied via padding-bottom */
}

/* Ensure feather icons inherit text color */
[data-feather] {
  width: 1em; /* Default size */
  height: 1em;
  stroke: currentColor;
  stroke-width: 2;
  stroke-linecap: round;
  stroke-linejoin: round;
  fill: none;
}
.svg-button [data-feather], .btn [data-feather] {
     /* width/height might be overridden by btn/svg-button classes */
}
</style>