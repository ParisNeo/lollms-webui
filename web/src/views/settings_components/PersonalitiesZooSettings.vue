<template>
    <!-- Main container for the Personalities Zoo section -->
    <div class="user-settings-panel flex flex-col mb-2 rounded-lg shadow-lg p-4">

        <!-- Top Bar: Title, Active Personality, Mounted Personalities -->
        <div class="flex flex-row justify-between items-center mb-4 flex-wrap gap-y-2">
            <!-- Left Side: Title and Active Personality -->
            <div class="flex items-center flex-wrap">
                <p class="text-xl font-semibold cursor-default select-none mr-3 text-blue-800 dark:text-blue-100">
                    Personalities Zoo
                </p>
                <!-- Display Active Personality Name -->
                <div v-if="active_personality_name" class="flex items-center mr-2 text-lg text-blue-600 dark:text-blue-300">
                    <span class="mx-2 text-blue-400 dark:text-blue-500">|</span>
                    <span class="font-bold line-clamp-1" :title="`Active: ${active_personality_name}`">
                        {{ active_personality_name }}
                    </span>
                </div>
            </div>

            <!-- Right Side: Mounted Personalities -->
            <div class="flex items-center space-x-3 shrink-0">
                <!-- Display Mounted Personalities Icons -->
                <div v-if="mountedPersArr.length > 0" class="text-base font-semibold cursor-pointer select-none items-center flex flex-row">
                     <div class="flex -space-x-4 items-center">
                        <div class="relative hover:-translate-y-1 duration-300 hover:z-10 shrink-0"
                             v-for="(item, index) in displayedMountedPersonalities"
                             :key="index + '-' + item.name"
                             ref="mountedPersonalitiesRefs">
                             <div class="group items-center flex flex-row">
                                <button @click.stop="onPersonalitySelected({ personality: item, isMounted: true })"
                                        :title="`Select: ${item.name}`">
                                    <img :src="getPersonalityIconUrl(item.avatar)" @error="personalityImgPlaceholder"
                                         class="w-8 h-8 rounded-full object-cover border-2 active:scale-90 group-hover:border-blue-500 dark:group-hover:border-blue-400"
                                         :class="isActivePersonality(item) ? 'border-blue-500 dark:border-blue-400' : 'border-blue-300 dark:border-blue-600'">
                                </button>
                                <button @click.stop="unmountPersonality({ personality: item })"
                                        class="absolute -top-1 -right-1 opacity-0 group-hover:opacity-100 transition-opacity duration-150"
                                        title="Unmount personality">
                                    <span class="bg-red-500 hover:bg-red-600 text-white rounded-full p-0.5 flex items-center justify-center shadow-md">
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

                <!-- Unmount All Button -->
                <button v-if="mountedPersArr.length > 0" @click.stop="unmountAll()"
                        class="p-1 bg-red-100 hover:bg-red-200 dark:bg-red-900 dark:hover:bg-red-800 rounded-full border border-red-300 dark:border-red-700 active:scale-90"
                        title="Unmount All Personalities">
                    <i data-feather="x-octagon" class="w-4 h-4 text-red-600 dark:text-red-400 stroke-current"></i>
                </button>
            </div>
        </div>

        <!-- Filters and Search Area -->
        <div class="flex flex-col sm:flex-row gap-4 mb-4">
            <!-- SEARCH BAR -->
            <div class="flex-grow">
                <label for="personality-search" class="sr-only">Search</label>
                <div class="relative">
                    <div class="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
                        <i v-if="!searchPersonalityInProgress" data-feather="search" class="w-5 h-5 text-blue-400 dark:text-blue-500"></i>
                        <!-- SPINNER -->
                        <div v-else role="status">
                            <svg aria-hidden="true" class="w-5 h-5 text-blue-400 animate-spin dark:text-blue-500 fill-blue-500" viewBox="0 0 100 101" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path d="M100 50.5908C100 78.2051 77.6142 100.591 50 100.591C22.3858 100.591 0 78.2051 0 50.5908C0 22.9766 22.3858 0.59082 50 0.59082C77.6142 0.59082 100 22.9766 100 50.5908ZM9.08144 50.5908C9.08144 73.1895 27.4013 91.5094 50 91.5094C72.5987 91.5094 90.9186 73.1895 90.9186 50.5908C90.9186 27.9921 72.5987 9.67226 50 9.67226C27.4013 9.67226 9.08144 27.9921 9.08144 50.5908Z" fill="currentColor" />
                                <path d="M93.9676 39.0409C96.393 38.4038 97.8624 35.9116 97.0079 33.5539C95.2932 28.8227 92.871 24.3692 89.8167 20.348C85.8452 15.1192 80.8826 10.7238 75.2124 7.41289C69.5422 4.10194 63.2754 1.94025 56.7698 1.05124C51.7666 0.367541 46.6976 0.446843 41.7345 1.27873C39.2613 1.69328 37.813 4.19778 38.4501 6.62326C39.0873 9.04874 41.5694 10.4717 44.0505 10.1071C47.8511 9.54855 51.7191 9.52689 55.5402 10.0491C60.8642 10.7766 65.9928 12.5457 70.6331 15.2552C75.2735 17.9648 79.3347 21.5619 82.5849 25.841C84.9175 28.9121 86.7997 32.2913 88.1811 35.8758C89.083 38.2158 91.5421 39.6781 93.9676 39.0409Z" fill="currentFill" />
                            </svg>
                        </div>
                    </div>
                    <input type="search" id="personality-search"
                           class="block w-full p-3 pl-10 text-sm input text-blue-900 dark:text-blue-100"
                           placeholder="Search name, author, description..." required v-model="searchPersonality"
                           @input="searchPersonality_func">
                    <button v-if="searchPersonality" @click.stop="clearSearch" type="button"
                            class="text-white absolute right-2.5 bottom-1.5 bg-blue-600 hover:bg-blue-700 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-lg text-xs px-3 py-1.5 dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800">
                        Clear
                    </button>
                </div>
            </div>

            <!-- CATEGORY DROPDOWN -->
            <div class="flex-shrink-0 sm:w-64">
                <label for="persCat" class="sr-only">Category</label>
                <select id="persCat"
                        v-model="selectedCategory"
                        @change="applyFiltersAndSort"
                        class="block w-full p-3 text-sm input text-blue-900 dark:text-blue-100">
                     <option value="">All Categories ({{ allPersonalities.length }})</option>
                     <option v-if="starredPaths.length > 0" value="Starred">⭐ Starred ({{ starredPaths.length }})</option>
                     <!-- Add a separator visually if needed -->
                      <option disabled v-if="starredPaths.length > 0 && persCatgArr.length > 0" class="text-blue-400 dark:text-blue-600">──────────</option>
                     <option v-for="(item, index) in persCatgArr" :key="index" :value="item">
                        {{ item }} ({{ getCategoryCount(item) }})
                    </option>
                </select>
            </div>
        </div>

        <!-- Loading State -->
        <div v-if="isLoading && allPersonalities.length === 0" class="flex justify-center items-center p-10 text-blue-500 dark:text-blue-400">
            <svg aria-hidden="true" class="w-8 h-8 mr-2 text-blue-300 animate-spin dark:text-blue-600 fill-blue-500" viewBox="0 0 100 101" fill="none" xmlns="http://www.w3.org/2000/svg"> <path d="M100 50.5908C100 78.2051 77.6142 100.591 50 100.591C22.3858 100.591 0 78.2051 0 50.5908C0 22.9766 22.3858 0.59082 50 0.59082C77.6142 0.59082 100 22.9766 100 50.5908ZM9.08144 50.5908C9.08144 73.1895 27.4013 91.5094 50 91.5094C72.5987 91.5094 90.9186 73.1895 90.9186 50.5908C90.9186 27.9921 72.5987 9.67226 50 9.67226C27.4013 9.67226 9.08144 27.9921 9.08144 50.5908Z" fill="currentColor"/> <path d="M93.9676 39.0409C96.393 38.4038 97.8624 35.9116 97.0079 33.5539C95.2932 28.8227 92.871 24.3692 89.8167 20.348C85.8452 15.1192 80.8826 10.7238 75.2124 7.41289C69.5422 4.10194 63.2754 1.94025 56.7698 1.05124C51.7666 0.367541 46.6976 0.446843 41.7345 1.27873C39.2613 1.69328 37.813 4.19778 38.4501 6.62326C39.0873 9.04874 41.5694 10.4717 44.0505 10.1071C47.8511 9.54855 51.7191 9.52689 55.5402 10.0491C60.8642 10.7766 65.9928 12.5457 70.6331 15.2552C75.2735 17.9648 79.3347 21.5619 82.5849 25.841C84.9175 28.9121 86.7997 32.2913 88.1811 35.8758C89.083 38.2158 91.5421 39.6781 93.9676 39.0409Z" fill="currentFill"/> </svg>
            <span>Loading personalities...</span>
        </div>

        <!-- Empty State -->
        <div v-else-if="fullyFilteredPersonalities.length === 0" class="text-center text-blue-500 dark:text-blue-400 py-10">
            No personalities found{{ searchPersonality ? ' matching "' + searchPersonality + '"' : '' }}{{ selectedCategory && selectedCategory !== 'Starred' ? ' in category "' + selectedCategory + '"' : '' }}{{ selectedCategory === 'Starred' ? ' in Starred' : '' }}.
         </div>

        <!-- PERSONALITIES GRID (Lazy Loaded) -->
        <div v-else class="overflow-y-auto flex-grow personalities-grid-container scrollbar scrollbar-thin" style="max-height: calc(100vh - 300px);"> <!-- Added scrollbar styling -->
            <label class="label block ml-2 mb-2"> <!-- Used label class -->
                 {{ getResultLabel() }}: ({{ fullyFilteredPersonalities.length }})
            </label>
             <!-- Added key to the div for better conditional rendering updates -->
             <div :key="selectedCategory + '-' + searchPersonality"
                  class="p-2 pb-0 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                <transition-group name="list">
                    <PersonalityEntry
                        v-for="(pers, index) in renderedPersonalities"
                        :key="'pers-' + (pers.id || `${pers.category}-${pers.folder}-${index}`)"
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
            <!-- Intersection Observer Sentinel -->
            <div ref="sentinel" class="h-10">
                 <div v-if="isLoading && renderedPersonalities.length > 0 && renderedPersonalities.length < fullyFilteredPersonalities.length" class="flex justify-center items-center p-4 text-blue-500 dark:text-blue-400">
                     <svg aria-hidden="true" class="w-6 h-6 mr-2 text-blue-300 animate-spin dark:text-blue-600 fill-blue-500" viewBox="0 0 100 101" fill="none" xmlns="http://www.w3.org/2000/svg"> <path d="M100 50.5908C100 78.2051 77.6142 100.591 50 100.591C22.3858 100.591 0 78.2051 0 50.5908C0 22.9766 22.3858 0.59082 50 0.59082C77.6142 0.59082 100 22.9766 100 50.5908ZM9.08144 50.5908C9.08144 73.1895 27.4013 91.5094 50 91.5094C72.5987 91.5094 90.9186 73.1895 90.9186 50.5908C90.9186 27.9921 72.5987 9.67226 50 9.67226C27.4013 9.67226 9.08144 27.9921 9.08144 50.5908Z" fill="currentColor"/> <path d="M93.9676 39.0409C96.393 38.4038 97.8624 35.9116 97.0079 33.5539C95.2932 28.8227 92.871 24.3692 89.8167 20.348C85.8452 15.1192 80.8826 10.7238 75.2124 7.41289C69.5422 4.10194 63.2754 1.94025 56.7698 1.05124C51.7666 0.367541 46.6976 0.446843 41.7345 1.27873C39.2613 1.69328 37.813 4.19778 38.4501 6.62326C39.0873 9.04874 41.5694 10.4717 44.0505 10.1071C47.8511 9.54855 51.7191 9.52689 55.5402 10.0491C60.8642 10.7766 65.9928 12.5457 70.6331 15.2552C75.2735 17.9648 79.3347 21.5619 82.5849 25.841C84.9175 28.9121 86.7997 32.2913 88.1811 35.8758C89.083 38.2158 91.5421 39.6781 93.9676 39.0409Z" fill="currentFill"/> </svg>
                     <span>Loading more...</span>
                 </div>
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
// Use mapState, mapActions, etc. if preferred, or access $store directly

const bUrl = import.meta.env.VITE_LOLLMS_API_BASEURL || '';
const STARRED_LOCAL_STORAGE_KEY = 'lollms_starred_personalities';

export default {
    name: 'PersonalitiesZoo',
    components: {
        PersonalityEntry,
    },
    emits: ['settings-changed'],
    data() {
        return {
            allPersonalities: [],
            persCatgArr: [],
            selectedCategory: '', // Will be initialized based on store in mounted()
            searchPersonality: '',
            searchPersonalityInProgress: false,
            searchDebounceTimer: null,
            searchDebounceDelay: 350,
            isLoading: false,
            bUrl: bUrl, // Expose bUrl to the template if needed directly or for props
            defaultPersonalityIcon_: defaultPersonalityIcon, // Expose for template usage
            maxDisplayedMounted: 5,
            starredPaths: [], // Store full_path of starred personalities

            // Lazy Loading state
            displayedCount: 24, // Initial number of items to display
            loadBatchSize: 24,  // Number of items to load each time
            observer: null,     // Intersection observer instance
        };
    },
    computed: {
        // Access store state
        configFile() {
            return this.$store.state.config || { personalities: [], active_personality_id: -1, personality_category: '' };
        },

        mountedPersArr() {
            if (!this.configFile.personalities || this.allPersonalities.length === 0) {
                return [];
            }
            const mountedSet = new Set(this.configFile.personalities);
            return this.allPersonalities.filter(p => {
                const basePath = p.full_path;
                const langPaths = Array.isArray(p.languages) ? p.languages.map(lang => `${basePath}:${lang}`) : [];
                return mountedSet.has(basePath) || langPaths.some(lp => mountedSet.has(lp));
            });
        },

        active_personality_name() {
            if (this.configFile.active_personality_id < 0 || !this.configFile.personalities || this.configFile.active_personality_id >= this.configFile.personalities.length) {
                return null;
            }
            const activePathWithOptionalLang = this.configFile.personalities[this.configFile.active_personality_id];
            const activePath = activePathWithOptionalLang ? activePathWithOptionalLang.split(':')[0] : null; // Get path without language
            const activePers = this.allPersonalities.find(p => p.full_path === activePath);
            return activePers ? activePers.name : null;
        },

        displayedMountedPersonalities() {
            return this.mountedPersArr.slice(0, this.maxDisplayedMounted);
        },

        // Core filtering logic (before slicing for lazy loading)
        fullyFilteredPersonalities() {
             let result = [...this.allPersonalities];

             // Filter by Starred
             if (this.selectedCategory === 'Starred') {
                 const starredSet = new Set(this.starredPaths);
                 result = result.filter(p => starredSet.has(p.full_path));
             }
             // Filter by Category (if not Starred)
             else if (this.selectedCategory) {
                 result = result.filter(p => p.category === this.selectedCategory);
             }

             // Filter by Search Term
             if (this.searchPersonality) {
                 const searchTerm = this.searchPersonality.toLowerCase();
                 result = result.filter((item) => {
                     try {
                         return (item.name && item.name.toLowerCase().includes(searchTerm)) ||
                                (item.author && item.author.toLowerCase().includes(searchTerm)) ||
                                (item.description && item.description.toLowerCase().includes(searchTerm)) ||
                                (item.full_path && item.full_path.toLowerCase().includes(searchTerm));
                     } catch { return false; }
                 });
             }

             // Sort: Mounted first, then by name
             result.sort((a, b) => {
                 if (a.isMounted && !b.isMounted) return -1;
                 if (!a.isMounted && b.isMounted) return 1;
                 return (a.name || '').localeCompare(b.name || '');
             });

             return result;
         },

         // Slice the filtered list for rendering based on lazy loading
         renderedPersonalities() {
             return this.fullyFilteredPersonalities.slice(0, this.displayedCount);
         },
    },
    watch: {
        // Watch store config for changes in mounted personalities
        'configFile.personalities': {
            handler() {
                this.syncLocalMountedFlags();
            },
            deep: true // Necessary for arrays
        },
        // Watch store config for category changes
        'configFile.personality_category': {
            handler(newVal) {
                const currentVal = newVal || '';
                 // Only update local state if it differs AND is a valid category
                 if (this.selectedCategory !== currentVal && (this.persCatgArr.includes(currentVal) || currentVal === '' || currentVal === 'Starred')) {
                    this.selectedCategory = currentVal;
                    this.applyFiltersAndSort(); // Re-filter list
                }
            }
        },
        // Watch local selectedCategory to update store and potentially emit changes
        selectedCategory(newVal) {
             const storeVal = this.$store.state.config.personality_category || '';
             if (storeVal !== newVal) {
                 this.$store.state.config.personality_category = newVal;
                 this.$emit('settings-changed');
             }
             // Filter/sort is handled by the @change event on the select element
             // and the applyFiltersAndSort method. No need to call it here directly.
        },
        // Watch starred paths for changes
        starredPaths: {
            handler() {
                // Refetch categories to potentially add/remove the "Starred" option
                this.fetchCategories();
                // Re-apply filters if the starred list changes and "Starred" is selected
                if (this.selectedCategory === 'Starred') {
                    this.applyFiltersAndSort();
                }
                // Mark the `isStarred` flag on the main list
                this.markStarredInAllPersonalities();
            },
            deep: true // Necessary for arrays
        }
    },
    methods: {
        // --- API Helpers ---
        async api_get_req(endpoint) {
            try {
                const res = await axios.get(`${endpoint.startsWith('/') ? '' : '/'}${endpoint}`);
                if (res) { return res.data; }
            } catch (error) {
                this.$store.state.toast.showToast(`API GET Error (${endpoint}): ${error.message}`, 4, false);
                console.error(`API GET Error (${endpoint}):`, error);
                return null;
            }
        },
        async api_post_req(endpoint, data = {}) {
             const payload = { ...data, client_id: this.$store.state.client_id };
             try {
                 const res = await axios.post(`${endpoint.startsWith('/') ? '' : '/'}${endpoint}`, payload);
                  if (typeof res.data === 'object' && res.data !== null && 'status' in res.data) {
                      return res.data;
                  } else {
                      console.warn(`API POST response for ${endpoint} has unexpected structure:`, res.data);
                      return { status: false, error: 'Unexpected response structure', data: res.data };
                  }
             } catch (error) {
                 this.$store.state.toast.showToast(`API POST Error (${endpoint}): ${error.message}`, 4, false);
                 console.error(`API POST Error (${endpoint}):`, error);
                 return { status: false, error: error.message };
             }
        },

        // --- Data Fetching & Processing ---
        async getPersonalitiesArr() {
            this.isLoading = true;
            try {
                const dictionary = await this.api_get_req("get_all_personalities");
                const config = this.configFile; // Use computed property

                console.log("Processing get_all_personalities response");
                let combined = [];
                const mountedSet = new Set(config.personalities || []);
                const starredSet = new Set(this.starredPaths); // Use current starred paths

                if (dictionary) {
                    for (const category in dictionary) {
                        const personalitiesInCategory = dictionary[category];
                        if (Array.isArray(personalitiesInCategory)) {
                            personalitiesInCategory.forEach((item) => {
                                const full_path = `${category}/${item.folder}`;
                                const uniqueId = item.id || full_path;
                                // Determine if *any* language variant is mounted
                                const langPaths = Array.isArray(item.languages) ? item.languages.map(lang => `${full_path}:${lang}`) : [];
                                const isAnyVariantMounted = mountedSet.has(full_path) || langPaths.some(lp => mountedSet.has(lp));

                                combined.push({
                                    ...item,
                                    category: category,
                                    language: "", // Base entry has no specific language set here
                                    full_path: full_path,
                                    isMounted: isAnyVariantMounted,
                                    isStarred: starredSet.has(full_path), // Set starred flag
                                    id: uniqueId,
                                    isProcessing: false
                                });
                            });
                        }
                    }
                }
                this.allPersonalities = combined;
                this.applyFiltersAndSort(); // Apply initial filter/sort/slice
                console.log(`Fetched ${this.allPersonalities.length} total personalities.`);

            } finally {
                 this.isLoading = false; // Set loading false *after* processing
                 nextTick(feather.replace);
            }
        },
        async fetchCategories() {
            this.isLoading = true; // Consider if separate loading state is needed here
            try {
                const cats = await this.api_get_req("list_personalities_categories");
                this.persCatgArr = cats ? cats.sort() : [];
                 // Initialize selectedCategory based on store config *after* categories are fetched
                const storedCat = this.configFile.personality_category;
                const isValidStoredCat = storedCat && (this.persCatgArr.includes(storedCat) || storedCat === 'Starred');
                this.selectedCategory = isValidStoredCat ? storedCat : ''; // Initialize here
            } finally {
                this.isLoading = false;
                nextTick(feather.replace); // Might need icon updates if categories change dynamically
            }
        },
        async fetchPersonalitiesAndCategories() {
             await this.fetchCategories(); // Fetch categories first
             await this.getPersonalitiesArr(); // Then fetch personalities
        },

        // --- Filtering, Sorting, Searching ---
        applyFiltersAndSort() {
            // Reset displayed count when filters change
            this.displayedCount = this.loadBatchSize;
            this.searchPersonalityInProgress = false; // Ensure spinner stops

            // Computed properties `fullyFilteredPersonalities` and `renderedPersonalities`
            // will automatically update based on `selectedCategory`, `searchPersonality`,
            // `allPersonalities`, and `displayedCount`.

            nextTick(() => {
                 feather.replace();
                 // Reset scroll position to top when filters change
                 const gridContainer = this.$el.querySelector('.personalities-grid-container'); // Use $el
                 if (gridContainer) {
                     gridContainer.scrollTop = 0;
                 }
                 // Re-observe after potential list changes
                 this.setupObserver();
            });
        },
        searchPersonality_func() {
            this.searchPersonalityInProgress = true;
            clearTimeout(this.searchDebounceTimer);
            this.searchDebounceTimer = setTimeout(() => {
                this.applyFiltersAndSort();
            }, this.searchDebounceDelay);
        },
        clearSearch() {
            this.searchPersonality = '';
            this.applyFiltersAndSort();
        },

        // --- Starred Functionality ---
        loadStarred() {
            try {
                const stored = localStorage.getItem(STARRED_LOCAL_STORAGE_KEY);
                this.starredPaths = stored ? JSON.parse(stored) : [];
            } catch (e) {
                console.error("Failed to load starred personalities:", e);
                this.starredPaths = [];
            }
            this.markStarredInAllPersonalities(); // Mark initially
        },
        saveStarred() {
            try {
                localStorage.setItem(STARRED_LOCAL_STORAGE_KEY, JSON.stringify(this.starredPaths));
            } catch (e) {
                console.error("Failed to save starred personalities:", e);
            }
        },
        markStarredInAllPersonalities() {
            const starredSet = new Set(this.starredPaths);
            this.allPersonalities.forEach(p => {
                p.isStarred = starredSet.has(p.full_path);
            });
            // Force update if needed, although changing array item properties should be reactive
            // this.allPersonalities = [...this.allPersonalities];
            // Filtering/sorting will happen naturally when applyFiltersAndSort is called
        },
        toggleStar(persEntry) {
            const path = persEntry.personality.full_path;
            const index = this.starredPaths.indexOf(path);
            if (index > -1) {
                this.starredPaths.splice(index, 1); // Unstar
            } else {
                this.starredPaths.push(path); // Star
            }
            // Find the personality in the *master* list and update its flag directly
            const masterPers = this.allPersonalities.find(p => p.full_path === path);
            if (masterPers) {
                masterPers.isStarred = index === -1; // True if it was just added
            }
            this.saveStarred(); // Persist change

            // Small toast notification
             this.$store.state.toast.showToast(
                `${persEntry.personality.name} ${index > -1 ? 'unstarred' : 'starred'}`,
                 2, true
             );
            nextTick(feather.replace);
        },

        // --- UI & State Helpers ---
        syncLocalMountedFlags() {
            const mountedSet = new Set(this.configFile.personalities || []);
            let changed = false;
            this.allPersonalities.forEach(p => {
                 const pathToCheck = p.full_path;
                 const langPathsToCheck = Array.isArray(p.languages) ? p.languages.map(lang => `${pathToCheck}:${lang}`) : [];
                 const shouldBeMounted = mountedSet.has(pathToCheck) || langPathsToCheck.some(lp => mountedSet.has(lp));

                 if (p.isMounted !== shouldBeMounted) {
                     p.isMounted = shouldBeMounted;
                     changed = true;
                 }
             });
             if(changed){
                  this.applyFiltersAndSort(); // Re-filter/sort if mounted status changed
             }
             nextTick(feather.replace);
        },
        personalityImgPlaceholder(event) { event.target.src = this.defaultPersonalityIcon_; },
        getPersonalityIconUrl(avatarPath) {
             if (!avatarPath) return this.defaultPersonalityIcon_;
             const path = avatarPath.startsWith('/') ? avatarPath : `/${avatarPath}`;
             const separator = this.bUrl.endsWith('/') || path.startsWith('/') ? '' : '/';
             let finalPath = path.startsWith('/') ? path.substring(1) : path; // Remove leading slash if present
             finalPath = finalPath === '/' ? '' : finalPath; // Handle root path case
             // Construct the final URL using the exposed bUrl data property
            return `${this.bUrl}${separator}${finalPath}`;
        },
        isActivePersonality(pers) {
             if (!this.configFile || this.configFile.active_personality_id < 0 || !this.configFile.personalities) return false;
             const activePathWithOptionalLang = this.configFile.personalities[this.configFile.active_personality_id];
             const activePath = activePathWithOptionalLang ? activePathWithOptionalLang.split(':')[0] : null;
             return pers.full_path === activePath;
        },
        setPersonalityProcessing(persEntry, state) {
             const id = persEntry.personality.id || persEntry.personality.full_path;
             const findAndUpdate = (list) => {
                 const pers = list.find(p => (p.id || p.full_path) === id);
                 if (pers) pers.isProcessing = state;
             };
             findAndUpdate(this.allPersonalities); // Update master list
             // Vue's reactivity should handle updates in computed props automatically
             nextTick(feather.replace); // Update icons if needed
        },
        getCategoryCount(category) {
            return this.allPersonalities.filter(p => p.category === category).length;
        },
        getResultLabel() {
             if (this.searchPersonality) return 'Search results';
             if (this.selectedCategory === 'Starred') return 'Starred Personalities';
             if (this.selectedCategory) return `Personalities in "${this.selectedCategory}"`;
             return 'All Personalities';
        },

        // --- Action Handlers ---
        async onPersonalitySelected(persEntry) {
             const pers = persEntry.personality;
             if (this.isLoading) { this.$store.state.toast.showToast("Loading...", 4, false); return; }
             if (!pers.isMounted) { this.$store.state.toast.showToast(`Mount "${pers.name}" first.`, 3, false); return; }
             if (this.isActivePersonality(pers)) { this.$store.state.toast.showToast(`"${pers.name}" is already active.`, 3, false); return; }

             this.setPersonalityProcessing(persEntry, true);
             this.$store.state.toast.showToast(`Selecting ${pers.name}...`, 2, true);

             const res = await this.select_personality(pers);

             if (res && res.status) {
                  this.$emit('settings-changed');
                  this.$store.state.toast.showToast(`Selected personality: ${pers.name}`, 4, true);
             } else {
                  this.$store.state.toast.showToast(`Failed to select ${pers.name}: ${res?.error || 'Unknown error'}`, 4, false);
             }
             this.setPersonalityProcessing(persEntry, false);
             nextTick(feather.replace);
        },
        async select_personality(pers) {
             if (!pers) { return { 'status': false, 'error': 'no personality - select_personality' } }
             let pth = pers.language ? `${pers.full_path}:${pers.language}` : pers.full_path;
             // Find index in the *current* store config personalities array
             const id = this.$store.state.config.personalities.findIndex(item => item === pth || item === pers.full_path);

             if (id === -1) {
                 const baseId = this.$store.state.config.personalities.findIndex(item => item === pers.full_path);
                 if (baseId === -1) {
                     console.error("Personality path not found in store config:", pth, pers.full_path);
                     return { 'status': false, 'error': 'Personality path not found in current config' };
                 }
                 pth = pers.full_path; // Use base path if found
             }

             const finalId = this.$store.state.config.personalities.findIndex(item => item === pth);
              if (finalId === -1) {
                   console.error("Consistency Error: Personality path disappeared after check:", pth);
                   return { 'status': false, 'error': 'Internal error finding personality ID' };
              }

             const obj = { client_id: this.$store.state.client_id, id: finalId };
             try {
                 const res = await axios.post(`/select_personality`, obj, {headers: { 'Content-Type': 'application/json' }});
                 if (res && res.data) {
                      await this.$store.dispatch('refreshConfig'); // Refresh store config
                     return res.data;
                 } else {
                     return { status: false, error: 'No response data from select_personality' };
                 }
             } catch (error) {
                 console.error("Error in select_personality API call:", error);
                 return { status: false, error: error.message };
             }
        },
        async mountPersonality(persEntry) {
             const pers = persEntry.personality;
             if (pers.isMounted) { this.$store.state.toast.showToast(`${pers.name} is already mounted.`, 3, false); return; }
             if (pers.disclaimer && pers.disclaimer.trim() !== "") {
                 const yes = await this.$store.state.yesNoDialog.askQuestion(`Disclaimer for ${pers.name}:\n\n${pers.disclaimer}\n\nMount this personality?`, 'Mount', 'Cancel');
                 if (!yes) return;
             }

             this.setPersonalityProcessing(persEntry, true);
             this.$store.state.toast.showToast(`Mounting ${pers.name}...`, 3, true);

             const res = await this.mount_personality(pers);

             if (res && res.status && res.active_personality_id > -1 && res.personalities) {
                 // Directly update store state (or dispatch an action)
                 this.$store.state.config.personalities = res.personalities;
                 this.$store.state.config.active_personality_id = res.active_personality_id;
                 this.$emit('settings-changed');
                 this.$store.state.toast.showToast("Personality mounted and selected", 4, true);
                 // syncLocalMountedFlags will be called by the watcher on configFile.personalities
             } else {
                 this.$store.state.toast.showToast(`Could not mount personality\nError: ${res?.error || 'Unknown error'}`, 4, false);
                 this.syncLocalMountedFlags(); // Resync on error too
             }
             this.setPersonalityProcessing(persEntry, false);
             nextTick(feather.replace);
        },
        async mount_personality(pers) {
            if (!pers) { return { 'status': false, 'error': 'no personality - mount_personality' } }
              try {
                  const obj = {
                      client_id: this.$store.state.client_id,
                      language: pers.language || "",
                      category: pers.category || "",
                      folder: pers.folder || "",
                  };
                  const res = await this.api_post_req('/mount_personality', obj);
                  return res;
              } catch (error) {
                  console.error("Error in mount_personality helper:", error);
                  return { status: false, error: error.message };
              }
        },
        async unmountPersonality(persEntry) {
            const pers = persEntry.personality;
             if (!pers.isMounted) { this.$store.state.toast.showToast(`${pers.name} is not mounted.`, 3, false); return; }
             const yes = await this.$store.state.yesNoDialog.askQuestion(`Unmount personality "${pers.name}"?`, 'Unmount', 'Cancel');
             if (!yes) return;

            this.setPersonalityProcessing(persEntry, true);
            this.$store.state.toast.showToast(`Unmounting ${pers.name}...`, 3, true);

            const res = await this.unmount_personality(pers);

            if (res && res.status) {
                 // Directly update store state (or dispatch an action)
                 this.$store.state.config.personalities = res.personalities;
                 this.$store.state.config.active_personality_id = res.active_personality_id;
                 this.$emit('settings-changed');
                 this.$store.state.toast.showToast("Personality unmounted", 4, true);
                 // syncLocalMountedFlags will be called by the watcher on configFile.personalities
            } else {
                this.$store.state.toast.showToast(`Could not unmount personality\nError: ${res?.error || 'Unknown error'}`, 4, false);
                this.syncLocalMountedFlags(); // Resync on error
            }
            this.setPersonalityProcessing(persEntry, false);
            nextTick(feather.replace);
        },
        async unmount_personality(pers) {
             if (!pers) { return { 'status': false, 'error': 'no personality - unmount_personality' } }
             const obj = {
                 client_id: this.$store.state.client_id,
                 language: pers.language || "",
                 category: pers.category || "",
                 folder: pers.folder || ""
             };
             try {
                  const res = await this.api_post_req('/unmount_personality', obj);
                  return res;
             } catch (error) {
                 console.error("Error in unmount_personality helper:", error);
                 return { status: false, error: error.message };
             }
        },
        async unmountAll() {
            const yes = await this.$store.state.yesNoDialog.askQuestion(`Unmount all personalities?`, 'Unmount All', 'Cancel');
            if (!yes) return;

            this.$store.state.toast.showToast(`Unmounting all...`, 3, true);
            this.isLoading = true; // Use global loading state

            const res = await this.api_post_req('/unmount_all_personalities');

            if (res && res.status) {
                this.$store.state.config.personalities = [];
                this.$store.state.config.active_personality_id = -1;
                this.$emit('settings-changed');
                this.$store.state.toast.showToast(`All personalities unmounted.`, 4, true);
                 // syncLocalMountedFlags will be called by the watcher
            } else {
                this.$store.state.toast.showToast(`Failed to unmount all: ${res?.error || 'Unknown error'}`, 4, false);
            }
            this.isLoading = false;
            nextTick(feather.replace);
        },
        async remountPersonality(persEntry) {
            const pers = persEntry.personality;
            this.setPersonalityProcessing(persEntry, true);
            this.$store.state.toast.showToast(`Remounting ${pers.name}...`, 3, true);
            try {
                await this.unmount_personality(pers);
                await new Promise(resolve => setTimeout(resolve, 150)); // Small delay
                const res = await this.mount_personality(pers);

                if (res && res.status) {
                    this.$store.state.config.personalities = res.personalities;
                    this.$store.state.config.active_personality_id = res.active_personality_id;
                    this.$emit('settings-changed');
                    this.$store.state.toast.showToast(`${pers.name} remounted successfully.`, 4, true);
                    // Watcher will trigger syncLocalMountedFlags
                } else {
                    this.$store.state.toast.showToast(`Failed to remount ${pers.name}: ${res?.error || 'Mount failed'}`, 4, false);
                    await this.fetchPersonalitiesAndCategories(); // Fetch again to resync state fully
                    // syncLocalMountedFlags called implicitly
                }
            } catch (error) {
                this.$store.state.toast.showToast(`Error remounting ${pers.name}: ${error.message}`, 4, false);
                await this.fetchPersonalitiesAndCategories();
                 // syncLocalMountedFlags called implicitly
            } finally {
                this.setPersonalityProcessing(persEntry, false);
            }
        },
        async editPersonality(persEntry) {
            const pers = persEntry.personality;
            this.isLoading = true;
            try {
                const res = await axios.post(`/get_personality_config`, {
                    client_id: this.$store.state.client_id,
                    category: pers.category,
                    name: pers.folder, // Use folder name here
                });
                const data = res.data;
                if (data.status) {
                    this.$store.state.currentPersonConfig = data.config;
                    this.$store.state.showPersonalityEditor = true;
                    if (this.$store.state.personality_editor?.showPanel) {
                        this.$store.state.personality_editor.showPanel();
                    }
                    this.$store.state.selectedPersonality = pers;
                } else {
                    console.error(data.error);
                    this.$store.state.toast.showToast(`Failed to load config for ${pers.name}: ${data.error}`, 4, false);
                }
            } catch (error) {
                console.error("Error fetching personality config:", error);
                this.$store.state.toast.showToast(`Error loading config for ${pers.name}`, 4, false);
            } finally {
                this.isLoading = false;
            }
        },
        async onCopyToCustom(persEntry) {
            const pers = persEntry.personality;
            const yes = await this.$store.state.yesNoDialog.askQuestion(`Copy "${pers.name}" to 'custom_personalities'?`, 'Copy', 'Cancel');
            if (!yes) return;

            this.setPersonalityProcessing(persEntry, true);
            const res = await this.api_post_req('copy_to_custom_personas', {
                category: pers.category,
                name: pers.folder // Assuming original intent was folder name
            });

            if (res && res.status) {
                this.$store.state.messageBox.showMessage(
                    `"${pers.name}" copied to 'custom_personalities'. Refreshing list...`
                );
                await new Promise(resolve => setTimeout(resolve, 500));
                await this.fetchPersonalitiesAndCategories(); // Refetch everything
                // syncLocalMountedFlags called implicitly
            } else {
                this.$store.state.toast.showToast(`Failed to copy ${pers.name}: ${res?.error || 'Already exists?'}`, 4, false);
            }
            this.setPersonalityProcessing(persEntry, false);
        },
        async onPersonalityReinstall(persEntry) {
             const pers = persEntry.personality;
             const yes = await this.$store.state.yesNoDialog.askQuestion(`Reinstall "${pers.name}"? This overwrites local changes.`, 'Reinstall', 'Cancel');
             if (!yes) return;

            this.setPersonalityProcessing(persEntry, true);
            this.$store.state.toast.showToast(`Reinstalling ${pers.name}...`, 3, true);
             const res = await this.api_post_req('reinstall_personality', { name: pers.full_path });

             if (res && res.status) {
                 this.$store.state.toast.showToast(`${pers.name} reinstalled successfully.`, 4, true);
                 // Maybe refetch or remount if needed
             } else {
                 this.$store.state.toast.showToast(`Failed to reinstall ${pers.name}: ${res?.error || 'Not found?'}`, 4, false);
             }
             this.setPersonalityProcessing(persEntry, false);
        },
        async onSettingsPersonality(persEntry) {
            const pers = persEntry.personality;
             if (!this.isActivePersonality(pers)) {
                 this.$store.state.toast.showToast(`Select and activate "${pers.name}" first to configure its settings.`, 4, false);
                 return;
             }

            this.setPersonalityProcessing(persEntry, true);
             try {
                  const res = await axios.get(`/get_active_personality_settings`);
                  const settingsSchema = res.data;

                  if (settingsSchema && typeof settingsSchema === 'object' && Object.keys(settingsSchema).length > 0) {
                       const result = await this.$store.state.universalForm.showForm(settingsSchema, `Settings - ${pers.name}`, "Save", "Cancel");

                       if (result !== null) {
                            const setResponse = await axios.post(`/set_active_personality_settings`, result);

                            if (setResponse?.data?.status) {
                                this.$store.state.toast.showToast(`Settings for ${pers.name} updated.`, 4, true);
                            } else {
                                this.$store.state.toast.showToast(`Failed to update settings: ${setResponse?.data?.error || 'Unknown error'}`, 4, false);
                            }
                       }
                  } else if (settingsSchema && typeof settingsSchema === 'object') {
                       this.$store.state.toast.showToast(`"${pers.name}" has no configurable settings.`, 4, false);
                  } else {
                        this.$store.state.toast.showToast(`Could not get settings for ${pers.name}.`, 4, false);
                  }
             } catch (error) {
                  console.error("Error getting/setting personality settings:", error);
                  this.$store.state.toast.showToast(`Error accessing settings: ${error.message}`, 4, false);
             } finally {
                 this.setPersonalityProcessing(persEntry, false);
             }
        },
        onCopyPersonalityName(persEntry) {
            const pers = persEntry.personality;
             navigator.clipboard.writeText(pers.name)
                 .then(() => this.$store.state.toast.showToast(`Copied name: ${pers.name}`, 3, true))
                 .catch(() => this.$store.state.toast.showToast("Failed to copy name.", 3, false));
        },
        async handleOpenFolder(persEntry) {
             const pers = persEntry.personality;
             await this.api_post_req("open_personality_folder", { category: pers.category, name: pers.folder });
        },

        // --- Lazy Loading ---
        loadMore() {
            if (this.isLoading) return; // Don't load more if already loading something else
            if (this.displayedCount >= this.fullyFilteredPersonalities.length) return; // All loaded

            console.log("Loading more personalities...");
            this.displayedCount += this.loadBatchSize;
            nextTick(feather.replace); // Update icons for newly added items
        },
        setupObserver() {
            // Disconnect previous observer if exists
            if (this.observer) {
                this.observer.disconnect();
            }
             // Use this.$refs which is available after mount
            const sentinel = this.$refs.sentinel;
            if (!sentinel) {
                 //console.warn("Sentinel element not found for Intersection Observer.");
                 return; // Exit if sentinel isn't rendered yet
            }

            const options = {
                root: null, // Use the viewport
                rootMargin: '0px',
                threshold: 0.1 // Trigger when 10% of the sentinel is visible
            };

            this.observer = new IntersectionObserver((entries) => {
                if (entries[0].isIntersecting) {
                    this.loadMore();
                }
            }, options);

            this.observer.observe(sentinel);
        },
    },
    // --- Lifecycle Hooks ---
    async mounted() {
        console.log("PersonalitiesZoo mounted (Options API). Initializing...");
        this.isLoading = true; // Set loading true at the start
        this.loadStarred(); // Load starred before fetching
        await this.fetchPersonalitiesAndCategories(); // Fetch data
        // Initial category sync from store happens within fetchCategories now
        nextTick(() => {
            feather.replace();
            this.setupObserver(); // Setup observer after initial render and data fetch
        });
        this.isLoading = false; // Set loading false after initialization
        console.log("PersonalitiesZoo initialization complete.");
    },
    beforeUnmount() {
        // Clean up observer
        if (this.observer) {
            this.observer.disconnect();
            this.observer = null;
        }
        // Clear debounce timer
        clearTimeout(this.searchDebounceTimer);
    },
     updated() {
         // This can be useful for ensuring Feather icons are replaced after any reactive update
         // However, calling it within specific methods using nextTick is often more targeted.
         nextTick(() => {
             feather.replace();
         });
     },
}
</script>

