<template>
    <div class="user-settings-panel flex flex-col mb-2 rounded-lg shadow-lg p-4 bg-white dark:bg-gray-800">

        <div class="flex flex-row justify-between items-center mb-4 flex-wrap gap-y-2">
            <div class="flex items-center flex-wrap">
                <p class="text-xl font-semibold cursor-default select-none mr-3 text-blue-800 dark:text-blue-100">
                    Personalities Zoo
                </p>
                <div v-if="active_personality_name" class="flex items-center mr-2 text-lg text-blue-600 dark:text-blue-300">
                    <span class="mx-2 text-blue-400 dark:text-blue-500">|</span>
                    <span class="font-bold line-clamp-1" :title="`Active: ${active_personality_name}`">
                        {{ active_personality_name }}
                    </span>
                </div>
            </div>

            <div class="flex items-center space-x-3 shrink-0">
                <div v-if="mountedPersArr.length > 0" class="text-base font-semibold cursor-default select-none items-center flex flex-row">
                     <div class="flex -space-x-4 items-center">
                        <div class="relative hover:-translate-y-1 duration-300 hover:z-10 shrink-0"
                             v-for="(item, index) in displayedMountedPersonalities"
                             :key="item.id || item.full_path + '-' + index"
                             ref="mountedPersonalitiesRefs">
                             <div class="group/mounted items-center flex flex-row">
                                <button @click.stop="onPersonalitySelected({ personality: item, isMounted: true })"
                                        :title="`Select: ${item.name}`"
                                        class="transition-transform duration-150 ease-in-out active:scale-90">
                                    <img :src="getPersonalityIconUrl(item.avatar)" @error="personalityImgPlaceholder"
                                         class="w-8 h-8 rounded-full object-cover border-2 transition-colors duration-200 group-hover/mounted:border-blue-500 dark:group-hover/mounted:border-blue-400"
                                         :class="isActivePersonality(item) ? 'border-blue-500 dark:border-blue-400' : 'border-blue-300 dark:border-blue-600'">
                                </button>
                                <button @click.stop="unmountPersonality({ personality: item })"
                                        class="absolute -top-1 -right-1 opacity-0 group-hover/mounted:opacity-100 transition-all duration-150 ease-in-out hover:scale-110"
                                        title="Unmount personality">
                                    <span class="bg-red-500 hover:bg-red-600 text-white rounded-full p-0.5 flex items-center justify-center shadow-md transition-colors duration-150">
                                        <i data-feather="x" class="w-3 h-3 stroke-current"></i>
                                    </span>
                                </button>
                            </div>
                        </div>
                        <div v-if="mountedPersArr.length > maxDisplayedMounted"
                             class="w-8 h-8 rounded-full bg-blue-200 dark:bg-blue-700 border-2 border-blue-300 dark:border-blue-600 flex items-center justify-center text-xs font-semibold text-blue-600 dark:text-blue-300 cursor-default"
                             :title="`${mountedPersArr.length - maxDisplayedMounted} more mounted`">
                            +{{ mountedPersArr.length - maxDisplayedMounted }}
                        </div>
                    </div>
                </div>

                <button v-if="mountedPersArr.length > 0" @click.stop="unmountAll()"
                        class="p-1 bg-red-100 hover:bg-red-200 dark:bg-red-900 dark:hover:bg-red-800 rounded-full border border-red-300 dark:border-red-700 active:scale-90 transition-all duration-150"
                        title="Unmount All Personalities">
                    <i data-feather="x-octagon" class="w-4 h-4 text-red-600 dark:text-red-400 stroke-current"></i>
                </button>
            </div>
        </div>

        <div class="flex flex-col sm:flex-row gap-4 mb-4">
            <div class="flex-grow">
                <label for="personality-search" class="sr-only">Search</label>
                <div class="relative">
                    <div class="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
                       <i data-feather="search" class="w-5 h-5 text-blue-400 dark:text-blue-500"></i>
                    </div>
                    <input type="search" id="personality-search"
                           class="input search-input block w-full p-3 pl-10 text-sm text-blue-900 dark:text-blue-100 placeholder-blue-500 dark:placeholder-blue-400 pr-24"
                           placeholder="Search name, author, description..."
                           v-model="searchTermInput"
                           @keyup.enter="applySearch">
                    <div class="absolute right-1.5 bottom-1.5 flex space-x-1">
                        <button v-if="searchTermInput" @click.stop="clearSearch" type="button"
                                class="btn btn-secondary btn-sm text-xs px-3 py-1.5">
                            Clear
                        </button>
                         <button @click.stop="applySearch" type="button"
                                class="btn btn-primary btn-sm text-xs px-3 py-1.5">
                            Search
                        </button>
                    </div>
                </div>
            </div>

            <div class="flex-shrink-0 sm:w-64">
                <label for="persCat" class="sr-only">Category</label>
                <select id="persCat"
                        v-model="selectedCategory"
                        @change="handleCategoryChange"
                        class="input block w-full p-3 text-sm text-blue-900 dark:text-blue-100">
                     <option value="">All Categories ({{ allPersonalities.length }})</option>
                     <option value="Mounted">⬆️ Mounted ({{ mountedPersArr.length }})</option>
                     <option v-if="starredPersonalitiesPaths.length > 0" value="Starred">⭐ Starred ({{ getStarredCount() }})</option>
                      <option disabled v-if="(starredPersonalitiesPaths.length > 0 || mountedPersArr.length > 0) && persCatgArr.length > 0" class="text-blue-400 dark:text-blue-600">──────────</option>
                     <option v-for="(item, index) in persCatgArr" :key="index" :value="item">
                        {{ item }} ({{ getCategoryCount(item) }})
                    </option>
                </select>
            </div>
        </div>

        <div v-if="isLoading && allPersonalities.length === 0" class="flex justify-center items-center p-10 text-loading text-blue-600 dark:text-blue-300">
            <svg aria-hidden="true" class="w-8 h-8 mr-2 text-blue-400 animate-spin dark:text-blue-500 fill-blue-600 dark:fill-blue-300" viewBox="0 0 100 101" fill="none" xmlns="http://www.w3.org/2000/svg"> <path d="M100 50.5908C100 78.2051 77.6142 100.591 50 100.591C22.3858 100.591 0 78.2051 0 50.5908C0 22.9766 22.3858 0.59082 50 0.59082C77.6142 0.59082 100 22.9766 100 50.5908ZM9.08144 50.5908C9.08144 73.1895 27.4013 91.5094 50 91.5094C72.5987 91.5094 90.9186 73.1895 90.9186 50.5908C90.9186 27.9921 72.5987 9.67226 50 9.67226C27.4013 9.67226 9.08144 27.9921 9.08144 50.5908Z" fill="currentColor"/> <path d="M93.9676 39.0409C96.393 38.4038 97.8624 35.9116 97.0079 33.5539C95.2932 28.8227 92.871 24.3692 89.8167 20.348C85.8452 15.1192 80.8826 10.7238 75.2124 7.41289C69.5422 4.10194 63.2754 1.94025 56.7698 1.05124C51.7666 0.367541 46.6976 0.446843 41.7345 1.27873C39.2613 1.69328 37.813 4.19778 38.4501 6.62326C39.0873 9.04874 41.5694 10.4717 44.0505 10.1071C47.8511 9.54855 51.7191 9.52689 55.5402 10.0491C60.8642 10.7766 65.9928 12.5457 70.6331 15.2552C75.2735 17.9648 79.3347 21.5619 82.5849 25.841C84.9175 28.9121 86.7997 32.2913 88.1811 35.8758C89.083 38.2158 91.5421 39.6781 93.9676 39.0409Z" fill="currentFill"/> </svg>
            <span>Loading personalities...</span>
        </div>

        <div v-else-if="!isLoading && filteredPersonalities.length === 0" class="text-center text-blue-500 dark:text-blue-400 py-10">
             No personalities found{{ activeSearchTerm ? ' matching "' + activeSearchTerm + '"' : '' }}{{ getResultMessageQualifier() }}.
         </div>

        <div v-else class="overflow-y-auto flex-grow personalities-grid-container scrollbar" style="max-height: calc(100vh - 300px);" ref="gridContainer">
            <label class="label block ml-2 mb-2 text-blue-700 dark:text-blue-300">
                 {{ getResultLabel() }}: ({{ filteredPersonalities.length }})
            </label>
             <div :key="selectedCategory + '-' + activeSearchTerm"
                  class="p-2 pb-0 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 bg-blue-100/50 dark:bg-blue-800/30 rounded-md">
                <transition-group name="list">
                    <PersonalityEntry
                        v-for="pers in filteredPersonalities"
                        :key="pers.id || pers.full_path"
                        :personality="pers"
                        :select_language="true"
                        :full_path="pers.full_path"
                        :is-mounted="pers.isMounted"
                        :is-active="isActivePersonality(pers)"
                        :is-processing="pers.isProcessing"
                        :is-starred="pers.isStarred"
                        :base-url="bUrl"
                        @select="onPersonalitySelected"
                        @mount="mountPersonality"
                        @unmount="unmountPersonality"
                        @remount="remountPersonality"
                        @edit="editPersonality"
                        @toggle-star="toggleStar"
                        @copy-to-custom="onCopyToCustom"
                        @reinstall="onPersonalityReinstall"
                        @settings="onSettingsPersonality"
                        @copy-personality-name="onCopyPersonalityName"
                        @open-folder="handleOpenFolder"
                        @error="personalityImgPlaceholder"
                        />
                </transition-group>
            </div>
        </div>
    </div>
</template>

<script>
import axios from 'axios';
import feather from 'feather-icons';
import { nextTick } from 'vue';
import PersonalityEntry from "@/components/PersonalityEntry.vue";
import defaultPersonalityIcon from "@/assets/logo.png";

const bUrl = import.meta.env.VITE_LOLLMS_API_BASEURL || '';

export default {
    name: 'PersonalitiesZoo',
    components: {
        PersonalityEntry,
    },
    props: {
        config: Object, // Receive current config state (including category)
        api_get_req: Function,
        api_post_req: Function,
        show_toast: Function,
        show_yes_no_dialog: Function,
        show_message_box: Function,
        client_id: String,
        show_universal_form: Function,
    },
    emits: ['setting-updated'], // Declare the event
    data() {
        return {
            allPersonalities: [], // Now sourced fully from store getter indirectly
            persCatgArr: [],
            selectedCategory: '', // Local view state, initialized from prop/store
            searchTermInput: '',
            activeSearchTerm: '',
            isLoading: false,
            bUrl: bUrl,
            defaultPersonalityIcon_: defaultPersonalityIcon,
            maxDisplayedMounted: 5,
        };
    },
    computed: {
        allStorePersonalities() {
            // Use store getter for the base list
            return this.$store.getters.getPersonalities || [];
        },
        starredPersonalitiesPaths() {
            // Get starred paths directly from store getter
            return this.$store.getters.getStarredPersonalities || [];
        },
        mountedPersArr() {
            // Filter the store's list based on mounted status
            if (!this.$store.state.config?.personalities || this.allStorePersonalities.length === 0) {
                return [];
            }
            const mountedSet = new Set(this.$store.state.config.personalities);
            return this.allStorePersonalities.filter(p => {
                 const basePath = p.full_path;
                 const langPaths = Array.isArray(p.languages) ? p.languages.map(lang => `${basePath}:${lang}`) : [];
                 // Check both base path and specific language variants
                 return mountedSet.has(basePath) || langPaths.some(lp => mountedSet.has(lp));
            }).sort((a, b) => (a.name || '').localeCompare(b.name || ''));
        },
        active_personality_name() {
            const config = this.$store.state.config;
            if (!config || config.active_personality_id < 0 || !config.personalities || config.active_personality_id >= config.personalities.length) {
                return null;
            }
            const activePathWithOptionalLang = config.personalities[config.active_personality_id];
            const activePath = activePathWithOptionalLang ? activePathWithOptionalLang.split(':')[0] : null;
            // Find in the store's list
            const activePers = this.allStorePersonalities.find(p => p.full_path === activePath);
            return activePers ? activePers.name : null;
        },
        displayedMountedPersonalities() {
            return this.mountedPersArr.slice(0, this.maxDisplayedMounted);
        },
        filteredPersonalities() {
             // Start with the full list from the store
             let result = [...this.allStorePersonalities];
             const starredSet = new Set(this.starredPersonalitiesPaths);

             // Apply filters
             if (this.selectedCategory === 'Mounted') {
                 result = result.filter(p => p.isMounted);
             } else if (this.selectedCategory === 'Starred') {
                 result = result.filter(p => starredSet.has(p.full_path));
             } else if (this.selectedCategory) {
                 result = result.filter(p => p.category === this.selectedCategory);
             }

             if (this.activeSearchTerm) {
                 const searchTerm = this.activeSearchTerm.toLowerCase().trim();
                 if (searchTerm) {
                     result = result.filter((item) => {
                         return (item.name && item.name.toLowerCase().includes(searchTerm)) ||
                                (item.author && item.author.toLowerCase().includes(searchTerm)) ||
                                (item.description && item.description.toLowerCase().includes(searchTerm)) ||
                                (item.full_path && item.full_path.toLowerCase().includes(searchTerm));
                     });
                 }
             }

             // Sort results
             result.sort((a, b) => {
                 const starredA = starredSet.has(a.full_path);
                 const starredB = starredSet.has(b.full_path);
                 if (starredA && !starredB) return -1;
                 if (!starredA && starredB) return 1;
                 if (a.isMounted && !b.isMounted) return -1;
                 if (!a.isMounted && b.isMounted) return 1;
                 const nameA = a.name || '';
                 const nameB = b.name || '';
                 return nameA.localeCompare(nameB);
             });

             return result;
         },
    },
    watch: {
        // Watch the config prop for changes from the parent (SettingsView)
        'config.personality_category': {
             handler(newVal) {
                 const currentVal = newVal || '';
                 const validCategories = ['', 'Mounted', 'Starred', ...this.persCatgArr];
                 // Update local selectedCategory if the prop changes and is valid
                 if (this.selectedCategory !== currentVal && validCategories.includes(currentVal)) {
                     this.selectedCategory = currentVal;
                 }
             },
              immediate: true // Check immediately on component load/prop availability
        },
        selectedCategory(newVal) {
             // When the user changes the dropdown, emit the update event to the parent
             this.activeSearchTerm = ''; // Reset search on category change
             this.searchTermInput = '';
             nextTick(() => this.resetScroll());
        },
         // Watch the store's personalities list to update local data if needed
         '$store.state.personalities': {
             handler(newVal) {
                 // If the store list changes significantly, update local derived data
                 // Note: computed properties should handle most updates reactively
                 // this.allPersonalities = newVal || []; // Not needed if using computed allStorePersonalities
                 this.syncLocalMountedFlags(); // Still useful to ensure flags are synced
             },
             deep: true,
             immediate: false
         },
    },
    methods: {
        async fetchCategories() {
            try {
                const cats = await this.api_get_req("list_personalities_categories");
                this.persCatgArr = cats ? cats.sort() : [];
                // Initial category selection is handled by watching the config prop
            } catch (error) {
                console.error("Error fetching categories:", error)
            }
        },
        async fetchInitialData() {
             this.isLoading = true;
             try {
                 await this.fetchCategories();
                 // Fetching personalities is now handled by the store action elsewhere
                 // We just need to ensure the store has been populated before this component mounts
                 // or rely on watchers/computed properties reacting to store changes.
                 // If direct fetch is needed here: await this.$store.dispatch('refreshPersonalitiesZoo');
                 this.syncLocalMountedFlags(); // Sync flags based on current store state
             } catch (error) {
                 console.error("Error fetching initial data:", error);
                 this.show_toast(`Error loading data: ${error.message}`, 4, false);
             } finally {
                 this.isLoading = false;
                 nextTick(() => {
                     feather.replace();
                     this.resetScroll();
                 });
             }
        },
        handleCategoryChange() {
            // The watcher for selectedCategory handles emitting the update
            nextTick(() => this.resetScroll());
        },
        applySearch() {
             this.activeSearchTerm = this.searchTermInput;
             nextTick(() => this.resetScroll());
        },
        clearSearch() {
            this.searchTermInput = '';
            this.activeSearchTerm = '';
             nextTick(() => this.resetScroll());
        },
        toggleStar(payload) {
            // Dispatch the action to the store
            this.$store.dispatch('toggleStarPersonality', payload.personality);
            // UI updates (like the star icon itself) will react to store changes via computed/props
        },
        resetScroll() {
            const container = this.$refs.gridContainer;
            if (container) {
                container.scrollTop = 0;
            }
        },
        syncLocalMountedFlags() {
            // This ensures the isMounted flag used by PersonalityEntry is correct
            const mountedSet = new Set(this.$store.state.config?.personalities || []);
            this.allStorePersonalities.forEach(p => { // Iterate store's list
                 const basePath = p.full_path;
                 const langPaths = Array.isArray(p.languages) ? p.languages.map(lang => `${basePath}:${lang}`) : [];
                 const shouldBeMounted = mountedSet.has(basePath) || langPaths.some(lp => mountedSet.has(lp));
                 if (p.isMounted !== shouldBeMounted) {
                     // Update the personality object in the store for reactivity
                      this.$store.commit('updatePersonality', { ...p, isMounted: shouldBeMounted });
                 }
             });
        },
        personalityImgPlaceholder(event) { event.target.src = this.defaultPersonalityIcon_; },
        getPersonalityIconUrl(avatarPath) {
             if (!avatarPath) return this.defaultPersonalityIcon_;
             const path = avatarPath.startsWith('/') ? avatarPath.substring(1) : avatarPath;
             const separator = this.bUrl.endsWith('/') || path.startsWith('/') ? '' : '/';
             let finalPath = path === '/' ? '' : path;
            return `${this.bUrl}${separator}${finalPath}`;
        },
        isActivePersonality(pers) {
             const config = this.$store.state.config;
             if (!config || config.active_personality_id < 0 || !config.personalities) return false;
             const activePathWithOptionalLang = config.personalities[config.active_personality_id];
             const activePath = activePathWithOptionalLang ? activePathWithOptionalLang.split(':')[0] : null;
             return pers.full_path === activePath;
        },
        setPersonalityProcessing(persEntry, state) {
             // Update processing state in the store's personality list
             const idToFind = persEntry.personality.id || persEntry.personality.full_path;
             const persInStore = this.allStorePersonalities.find(p => (p.id || p.full_path) === idToFind);
              if (persInStore) {
                   this.$store.commit('updatePersonality', { ...persInStore, isProcessing: state });
              } else {
                    console.warn("Cannot find personality in store to set processing state:", idToFind);
              }
        },
        getCategoryCount(category) {
            return this.allStorePersonalities.filter(p => p.category === category).length;
        },
         getStarredCount() {
            const starredSet = new Set(this.starredPersonalitiesPaths);
            return this.allStorePersonalities.filter(p => starredSet.has(p.full_path)).length;
         },
        getResultLabel() {
             if (this.selectedCategory === 'Mounted') return 'Mounted Personalities';
             if (this.selectedCategory === 'Starred') return 'Starred Personalities';
             if (this.selectedCategory) return `Personalities in "${this.selectedCategory}"`;
             return 'All Personalities';
        },
         getResultMessageQualifier() {
            if (this.selectedCategory === 'Mounted') return ' in Mounted';
            if (this.selectedCategory === 'Starred') return ' in Starred';
            if (this.selectedCategory) return ` in category "${this.selectedCategory}"`;
            return '';
        },
        async onPersonalitySelected(persEntry) {
             const pers = persEntry.personality;
             if (this.isLoading || pers.isProcessing) { this.show_toast("Loading...", 4, false); return; }
             if (!pers.isMounted) { this.show_toast(`Mount "${pers.name}" first.`, 3, false); return; }
             if (this.isActivePersonality(pers)) { this.show_toast(`"${pers.name}" is already active.`, 3, false); return; }

             this.setPersonalityProcessing(persEntry, true);
             this.show_toast(`Selecting ${pers.name}...`, 2, true);

             const res = await this.select_personality(pers);

             if (res && res.status) {
                  this.show_toast(`Selected personality: ${pers.name}`, 4, true);
                  await this.$store.dispatch('refreshConfig');
                  await this.$store.dispatch('refreshMountedPersonalities');
             } else {
                  this.show_toast(`Failed to select ${pers.name}: ${res?.error || 'Unknown error'}`, 4, false);
             }
             this.setPersonalityProcessing(persEntry, false);
        },
        async select_personality(pers) {
             if (!pers) return { status: false, error: 'no personality provided' };
             const mountedPaths = this.$store.state.config?.personalities || [];
             const langPath = pers.language ? `${pers.full_path}:${pers.language}` : null;
             let mountedPathToSelect = null;
             if (langPath && mountedPaths.includes(langPath)) {
                 mountedPathToSelect = langPath;
             } else if (mountedPaths.includes(pers.full_path)) {
                 mountedPathToSelect = pers.full_path;
             }
             if (!mountedPathToSelect) return { status: false, error: 'Personality variant not found in mounted list' };
             const finalId = mountedPaths.findIndex(item => item === mountedPathToSelect);
             if (finalId === -1) return { status: false, error: 'Internal error finding personality ID' };
             const obj = { id: finalId };
             try {
                 // Use api_post_req prop
                 const res = await this.api_post_req(`/select_personality`, obj);
                 return res; // Assuming res already contains {status, ...}
             } catch (error) {
                 return { status: false, error: error.message };
             }
        },
        async mountPersonality(persEntry) {
             const pers = persEntry.personality;
             if (pers.isMounted || pers.isProcessing) return;
             if (pers.disclaimer && pers.disclaimer.trim() !== "") {
                 const yes = await this.show_yes_no_dialog(`Disclaimer for ${pers.name}:\n\n${pers.disclaimer}\n\nMount this personality?`, 'Mount', 'Cancel');
                 if (!yes) return;
             }
             this.setPersonalityProcessing(persEntry, true);
             this.show_toast(`Mounting ${pers.name}...`, 3, true);
             const res = await this.mount_personality(pers);
             if (res && res.status) {
                 await this.$store.dispatch('refreshConfig');
                 await this.$store.dispatch('refreshMountedPersonalities'); // This updates mountedPersArr and mountedPers
                 // syncLocalMountedFlags will be triggered by store change or called explicitly if needed
                 this.show_toast(`Personality "${pers.name}" mounted`, 4, true);
                 const newConfig = this.$store.state.config; // Check updated config
                 if (newConfig?.active_personality_id > -1) {
                     const newlyMountedPath = pers.language ? `${pers.full_path}:${pers.language}` : pers.full_path;
                     const activePath = newConfig.personalities[newConfig.active_personality_id];
                     if(newlyMountedPath === activePath) {
                          this.show_toast(`${pers.name} mounted and selected`, 4, true);
                     }
                 }
             } else {
                 this.show_toast(`Could not mount personality\nError: ${res?.error || 'Unknown error'}`, 4, false);
             }
             this.setPersonalityProcessing(persEntry, false);
        },
        async mount_personality(pers) {
            if (!pers) return { status: false, error: 'no personality provided' };
              try {
                  const obj = {
                      language: pers.language || "",
                      category: pers.category || "",
                      folder: pers.folder || "",
                  };
                  const res = await this.api_post_req('/mount_personality', obj);
                  return res;
              } catch (error) {
                  return { status: false, error: error.message };
              }
        },
        async unmountPersonality(persEntry) {
            const pers = persEntry.personality;
             if (!pers.isMounted || pers.isProcessing) return;
             const yes = await this.show_yes_no_dialog(`Unmount personality "${pers.name}"?`, 'Unmount', 'Cancel');
             if (!yes) return;
            this.setPersonalityProcessing(persEntry, true);
            this.show_toast(`Unmounting ${pers.name}...`, 3, true);
            const res = await this.unmount_personality(pers);
            if (res && res.status) {
                 await this.$store.dispatch('refreshConfig');
                 await this.$store.dispatch('refreshMountedPersonalities');
                 this.show_toast("Personality unmounted", 4, true);
            } else {
                this.show_toast(`Could not unmount personality\nError: ${res?.error || 'Unknown error'}`, 4, false);
            }
            this.setPersonalityProcessing(persEntry, false);
        },
        async unmount_personality(pers) {
             if (!pers) return { status: false, error: 'no personality provided' };
             const mountedPaths = this.$store.state.config?.personalities || [];
             let path_to_unmount = null;
             const langPath = pers.language ? `${pers.full_path}:${pers.language}` : null;
             if (langPath && mountedPaths.includes(langPath)) {
                 path_to_unmount = langPath;
             } else if (mountedPaths.includes(pers.full_path)) {
                 path_to_unmount = pers.full_path;
             } else {
                 path_to_unmount = pers.full_path;
             }
             const obj = { path: path_to_unmount };
             try {
                  const res = await this.api_post_req('/unmount_personality', obj);
                  return res;
             } catch (error) {
                 return { status: false, error: error.message };
             }
        },
        async unmountAll() {
            const yes = await this.show_yes_no_dialog(`Unmount all ${this.mountedPersArr.length} personalities?`, 'Unmount All', 'Cancel');
            if (!yes) return;
            this.show_toast(`Unmounting all...`, 3, true);
            this.isLoading = true; // Use component loading state for this global action
            const res = await this.api_post_req('/unmount_all_personalities');
            if (res && res.status) {
                 await this.$store.dispatch('refreshConfig');
                 await this.$store.dispatch('refreshMountedPersonalities');
                this.show_toast(`All personalities unmounted.`, 4, true);
            } else {
                this.show_toast(`Failed to unmount all: ${res?.error || 'Unknown error'}`, 4, false);
            }
            this.isLoading = false;
        },
        async remountPersonality(persEntry) {
            const pers = persEntry.personality;
             if (!pers.isMounted || pers.isProcessing) return;
            this.setPersonalityProcessing(persEntry, true);
            this.show_toast(`Remounting ${pers.name}...`, 3, true);
            try {
                const unmountRes = await this.unmount_personality(pers);
                if (!unmountRes || !unmountRes.status) throw new Error(`Unmount failed: ${unmountRes?.error || 'Unknown error'}`);

                await this.$store.dispatch('refreshConfig'); // Refresh state after unmount
                await this.$store.dispatch('refreshMountedPersonalities');
                await new Promise(resolve => setTimeout(resolve, 200)); // Small delay

                const mountRes = await this.mount_personality(pers);
                 if (!mountRes || !mountRes.status) throw new Error(`Mount failed: ${mountRes?.error || 'Unknown error'}`);

                 await this.$store.dispatch('refreshConfig'); // Refresh state after mount
                 await this.$store.dispatch('refreshMountedPersonalities');
                 this.show_toast(`${pers.name} remounted successfully.`, 4, true);

            } catch (error) {
                this.show_toast(`Error remounting ${pers.name}: ${error.message}`, 4, false);
                 // Attempt to refresh state even on error to reflect reality
                 await this.$store.dispatch('refreshConfig');
                 await this.$store.dispatch('refreshMountedPersonalities');
            } finally {
                this.setPersonalityProcessing(persEntry, false);
            }
        },
        async editPersonality(persEntry) {
            const pers = persEntry.personality;
            if (pers.isProcessing) return;
             this.setPersonalityProcessing(persEntry, true);
            try {
                const res = await this.api_post_req(`/get_personality_config`, {
                    category: pers.category, name: pers.folder,
                });
                if (res.status && res.config) {
                    this.$store.commit('setCurrentPersonConfig', res.config);
                    this.$store.commit('setShowPersonalityEditor', true);
                    this.$store.commit('setSelectedPersonality', pers);
                     if (this.$store.state.personality_editor?.showPanel) {
                         this.$store.state.personality_editor.showPanel();
                     }
                } else {
                    this.show_toast(`Failed to load config for ${pers.name}: ${res.error || 'Not found/error'}`, 4, false);
                }
            } catch (error) {
                this.show_toast(`Error loading config for ${pers.name}: ${error.message}`, 4, false);
            } finally {
                 this.setPersonalityProcessing(persEntry, false);
            }
        },
        async onCopyToCustom(persEntry) {
            const pers = persEntry.personality;
            if (pers.isProcessing) return;
            const yes = await this.show_yes_no_dialog(`Copy "${pers.name}" to 'custom_personalities'?`, 'Copy', 'Cancel');
            if (!yes) return;
            this.setPersonalityProcessing(persEntry, true);
            const res = await this.api_post_req('copy_to_custom_personas', {
                category: pers.category, name: pers.folder
            });
            if (res && res.status) {
                this.show_message_box(`"${pers.name}" copied. Refreshing list...`);
                await new Promise(resolve => setTimeout(resolve, 500));
                await this.$store.dispatch('refreshPersonalitiesZoo'); // Refresh store list
                await this.$store.dispatch('refreshMountedPersonalities'); // Refresh mounted status
            } else {
                this.show_toast(`Failed to copy ${pers.name}: ${res?.error || 'Error'}`, 4, false);
            }
            this.setPersonalityProcessing(persEntry, false);
        },
        async onPersonalityReinstall(persEntry) {
             const pers = persEntry.personality;
             if (pers.isProcessing) return;
             const yes = await this.show_yes_no_dialog(`Reinstall "${pers.name}"? This overwrites local changes.`, 'Reinstall', 'Cancel');
             if (!yes) return;
            this.setPersonalityProcessing(persEntry, true);
            this.show_toast(`Reinstalling ${pers.name}...`, 3, true);
             const res = await this.api_post_req('reinstall_personality', { name: pers.full_path });
             if (res && res.status) {
                 this.show_toast(`${pers.name} reinstalled. Remount if active.`, 4, true);
                  // Optionally refresh the specific personality data if needed
                  // await this.$store.dispatch('refreshSpecificPersonality', pers.full_path);
             } else {
                 this.show_toast(`Failed to reinstall ${pers.name}: ${res?.error || 'Error'}`, 4, false);
             }
             this.setPersonalityProcessing(persEntry, false);
        },
        async onSettingsPersonality(persEntry) {
            const pers = persEntry.personality;
             if (!this.isActivePersonality(pers) || pers.isProcessing) return;
             if (!this.isActivePersonality(pers)) {
                  this.show_toast(`Activate "${pers.name}" first to configure settings.`, 4, false);
                  return;
             }
            this.setPersonalityProcessing(persEntry, true);
             try {
                  const settingsSchema = await this.api_get_req(`/get_active_personality_settings`);
                  if (settingsSchema && typeof settingsSchema === 'object' && Object.keys(settingsSchema).length > 0) {
                       const result = await this.show_universal_form(settingsSchema, `Settings - ${pers.name}`, "Save", "Cancel");
                       if (result !== null && result !== undefined) {
                           this.setPersonalityProcessing(persEntry, true); // Keep processing
                            const setResponse = await this.api_post_req(`/set_active_personality_settings`, result);
                            if (setResponse?.status) {
                                this.show_toast(`Settings for ${pers.name} updated.`, 4, true);
                            } else {
                                this.show_toast(`Failed to update settings: ${setResponse?.error || 'Error'}`, 4, false);
                            }
                       }
                  } else if (settingsSchema && typeof settingsSchema === 'object') {
                       this.show_toast(`"${pers.name}" has no configurable settings.`, 3, true);
                  } else {
                       this.show_toast(`Could not retrieve settings structure.`, 4, false);
                  }
             } catch (error) {
                  this.show_toast(`Error accessing settings: ${error.message}`, 4, false);
             } finally {
                 this.setPersonalityProcessing(persEntry, false);
             }
        },
        onCopyPersonalityName(persEntry) {
            const pers = persEntry.personality;
             navigator.clipboard.writeText(pers.name)
                 .then(() => this.show_toast(`Copied name: ${pers.name}`, 3, true))
                 .catch((err) => this.show_toast("Failed to copy name.", 3, false));
        },
        async handleOpenFolder(persEntry) {
             const pers = persEntry.personality;
             const res = await this.api_post_req("open_personality_folder", { category: pers.category, name: pers.folder });
             if (!res || !res.status) {
                 this.show_toast(`Could not open folder: ${res?.error || 'Error'}`, 4, false);
             }
        },
    },
    async mounted() {
        // Initial data fetch actions are likely called by the parent or app initialization
        // This component now primarily reacts to store state changes.
        // We still fetch categories specific to this view.
        await this.fetchInitialData();
        // Initialize local selectedCategory from the config prop
        this.selectedCategory = this.config?.personality_category || '';
    },
    updated() {
         nextTick(() => {
             feather.replace();
         });
     },
}
</script>

<style scoped>
.list-enter-active,
.list-leave-active {
  transition: all 0.3s ease;
}
.list-enter-from,
.list-leave-to {
  opacity: 0;
  transform: translateY(10px);
}

.scrollbar::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

.scrollbar::-webkit-scrollbar-track {
  @apply bg-blue-100 dark:bg-gray-700 rounded-lg;
}

.scrollbar::-webkit-scrollbar-thumb {
  @apply bg-blue-300 dark:bg-gray-500 rounded-lg;
}

.scrollbar::-webkit-scrollbar-thumb:hover {
  @apply bg-blue-400 dark:bg-gray-400;
}

.input {
     @apply bg-white dark:bg-gray-700 border border-blue-300 dark:border-gray-600 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:focus:ring-blue-500 dark:focus:border-blue-500;
}
.search-input {
     @apply placeholder-blue-500 dark:placeholder-blue-400 text-blue-900 dark:text-blue-100;
}
.text-loading {
     @apply text-blue-600 dark:text-blue-300;
}

#personality-search + div {
    display: flex;
    align-items: center;
    height: 100%;
    top: 0;
    bottom: 0;
    margin-top: auto;
    margin-bottom: auto;
}
.search-input{
    padding-right: 8rem;
}
.btn {
     @apply px-3 py-1 rounded-md text-sm font-medium shadow-sm focus:outline-none focus:ring-2 focus:ring-offset-2 dark:focus:ring-offset-gray-800 transition-colors duration-150 disabled:opacity-50;
 }

 .btn-sm {
     @apply px-2.5 py-0.5 text-xs rounded;
 }

 .btn-primary {
    @apply bg-blue-600 hover:bg-blue-700 text-white focus:ring-blue-500;
 }
 .btn-secondary {
    @apply bg-gray-200 hover:bg-gray-300 text-gray-700 dark:bg-gray-600 dark:hover:bg-gray-500 dark:text-gray-100 focus:ring-indigo-500;
 }
</style>