<template>
    <div class="user-settings-panel space-y-6 p-4 md:p-6 rounded-lg shadow-md bg-white dark:bg-gray-800">
        <!-- Header Section -->
        <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center border-b border-blue-300 dark:border-blue-600 pb-3 mb-4">
            <h2 class="text-2xl font-semibold text-blue-800 dark:text-blue-100 mb-2 sm:mb-0">
                Function Calls Zoo
            </h2>
            <!-- Mounted Functions Display -->
            <div class="flex flex-col items-end">
                 <div class="flex items-center flex-wrap gap-2 text-sm font-medium mb-1">
                     <span class="text-blue-600 dark:text-blue-400">Mounted:</span>
                     <!-- Use the computed property 'mountedFunctions' directly -->
                     <div v-if="mountedFunctions.length === 0" class="text-blue-500 dark:text-blue-500 italic text-xs">None</div>
                    <div v-else class="flex -space-x-3 items-center">
                         <!-- Limited display of mounted icons -->
                         <!-- Iterate over the computed 'displayedMountedFunctions' -->
                         <div v-for="(func, index) in displayedMountedFunctions" :key="`mounted-${func.id || func.full_path || index}`" class="relative group">
                            <img :src="getFunctionIcon(func.icon)" @error="imgPlaceholder"
                                class="w-7 h-7 rounded-full object-cover ring-2 ring-white dark:ring-gray-700 cursor-pointer hover:ring-blue-500 dark:hover:ring-blue-400 transition-all"
                                :title="`${func.name} (${func.category})`"
                                @click="scrollToFunction(func)"> <!-- Click scrolls to the function in the list -->
                            <button @click.stop="handleUnmount(func)"
                                class="absolute -top-1 -right-1 p-0.5 rounded-full bg-red-600 text-white opacity-0 group-hover:opacity-100 transition-opacity duration-150 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-1 dark:focus:ring-offset-gray-900"
                                title="Unmount">
                                <i data-feather="x" class="w-3 h-3 stroke-current"></i>
                            </button>
                         </div>
                         <div v-if="mountedFunctions.length > maxDisplayedMountedFunc"
                             class="w-7 h-7 rounded-full bg-blue-200 dark:bg-blue-700 ring-2 ring-white dark:ring-gray-700 flex items-center justify-center text-xs font-semibold text-blue-600 dark:text-blue-300"
                             :title="`${mountedFunctions.length - maxDisplayedMountedFunc} more mounted`">
                            +{{ mountedFunctions.length - maxDisplayedMountedFunc }}
                         </div>
                     </div>
                 </div>
                 <button v-if="mountedFunctions.length > 0" @click="unmountAll" class="btn btn-sm bg-red-600 hover:bg-red-700 text-white text-xs mt-1 focus:ring-red-300 dark:focus:ring-red-600">
                     <i data-feather="x-octagon" class="w-3 h-3 mr-1 stroke-current"></i>Unmount All
                </button>
            </div>
        </div>

         <p class="text-sm text-blue-600 dark:text-blue-400">
             Mount functions to grant the AI specific capabilities and tools it can use during conversations. Requires a model trained for function calling.
        </p>

        <!-- Controls: Search, Category, Sort -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4 items-center">
             <!-- Search Input -->
            <div class="relative md:col-span-1">
                 <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                     <i data-feather="search" class="w-5 h-5 text-blue-400 dark:text-blue-500"></i>
                </div>
                 <input
                    type="search"
                    v-model="searchTermFunc"
                    placeholder="Search functions..."
                    class="input pl-10 w-full placeholder:text-blue-400 dark:placeholder:text-blue-500"
                    @input="debounceSearchFunc"
                />
                 <div v-if="isSearchingFunc" class="absolute inset-y-0 right-0 pr-3 flex items-center">
                    <svg aria-hidden="true" class="w-5 h-5 text-blue-400 dark:text-blue-500 animate-spin fill-blue-500 dark:fill-blue-400" viewBox="0 0 100 101" fill="none" xmlns="http://www.w3.org/2000/svg"> <path d="M100 50.5908C100 78.2051 77.6142 100.591 50 100.591C22.3858 100.591 0 78.2051 0 50.5908C0 22.9766 22.3858 0.59082 50 0.59082C77.6142 0.59082 100 22.9766 100 50.5908ZM9.08144 50.5908C9.08144 73.1895 27.4013 91.5094 50 91.5094C72.5987 91.5094 90.9186 73.1895 90.9186 50.5908C90.9186 27.9921 72.5987 9.67226 50 9.67226C27.4013 9.67226 9.08144 27.9921 9.08144 50.5908Z" fill="currentColor"/> <path d="M93.9676 39.0409C96.393 38.4038 97.8624 35.9116 97.0079 33.5539C95.2932 28.8227 92.871 24.3692 89.8167 20.348C85.8452 15.1192 80.8826 10.7238 75.2124 7.41289C69.5422 4.10194 63.2754 1.94025 56.7698 1.05124C51.7666 0.367541 46.6976 0.446843 41.7345 1.27873C39.2613 1.69328 37.813 4.19778 38.4501 6.62326C39.0873 9.04874 41.5694 10.4717 44.0505 10.1071C47.8511 9.54855 51.7191 9.52689 55.5402 10.0491C60.8642 10.7766 65.9928 12.5457 70.6331 15.2552C75.2735 17.9648 79.3347 21.5619 82.5849 25.841C84.9175 28.9121 86.7997 32.2913 88.1811 35.8758C89.083 38.2158 91.5421 39.6781 93.9676 39.0409Z" fill="currentFill"/> </svg>
                 </div>
            </div>
            <!-- Category Filter -->
            <div class="md:col-span-1">
                <label for="func-category" class="sr-only">Filter by Category</label>
                 <select id="func-category" v-model="selectedCategoryFunc" class="input w-full">
                    <option value="">All Categories</option>
                     <option v-for="cat in categoriesFunc" :key="cat" :value="cat">{{ cat }}</option>
                </select>
            </div>
            <!-- Sort Select -->
            <div class="md:col-span-1">
                 <label for="func-sort" class="sr-only">Sort functions by</label>
                 <select id="func-sort" v-model="sortOptionFunc" class="input w-full">
                    <option value="mounted">Sort by Mounted</option> <!-- Added mounted sort -->
                    <option value="name">Sort by Name</option>
                    <option value="author">Sort by Author</option>
                     <option value="category">Sort by Category</option>
                 </select>
             </div>
        </div>

         <!-- Loading / Empty State -->
         <div v-if="isLoadingFunctions" class="flex justify-center items-center p-10 text-blue-500 dark:text-blue-400">
            <svg aria-hidden="true" class="w-8 h-8 mr-2 text-blue-300 dark:text-blue-600 animate-spin fill-blue-500 dark:fill-blue-400" viewBox="0 0 100 101" fill="none" xmlns="http://www.w3.org/2000/svg"> <path d="M100 50.5908C100 78.2051 77.6142 100.591 50 100.591C22.3858 100.591 0 78.2051 0 50.5908C0 22.9766 22.3858 0.59082 50 0.59082C77.6142 0.59082 100 22.9766 100 50.5908ZM9.08144 50.5908C9.08144 73.1895 27.4013 91.5094 50 91.5094C72.5987 91.5094 90.9186 73.1895 90.9186 50.5908C90.9186 27.9921 72.5987 9.67226 50 9.67226C27.4013 9.67226 9.08144 27.9921 9.08144 50.5908Z" fill="currentColor"/> <path d="M93.9676 39.0409C96.393 38.4038 97.8624 35.9116 97.0079 33.5539C95.2932 28.8227 92.871 24.3692 89.8167 20.348C85.8452 15.1192 80.8826 10.7238 75.2124 7.41289C69.5422 4.10194 63.2754 1.94025 56.7698 1.05124C51.7666 0.367541 46.6976 0.446843 41.7345 1.27873C39.2613 1.69328 37.813 4.19778 38.4501 6.62326C39.0873 9.04874 41.5694 10.4717 44.0505 10.1071C47.8511 9.54855 51.7191 9.52689 55.5402 10.0491C60.8642 10.7766 65.9928 12.5457 70.6331 15.2552C75.2735 17.9648 79.3347 21.5619 82.5849 25.841C84.9175 28.9121 86.7997 32.2913 88.1811 35.8758C89.083 38.2158 91.5421 39.6781 93.9676 39.0409Z" fill="currentFill"/> </svg>
             <span>Loading functions...</span>
        </div>
         <div v-else-if="pagedFunctions.length === 0 && filteredFunctions.length === 0" class="text-center text-blue-500 dark:text-blue-400 py-10">
            No functions found{{ searchTermFunc ? ' matching "' + searchTermFunc + '"' : '' }}{{ selectedCategoryFunc ? ' in category "' + selectedCategoryFunc + '"' : '' }}.
         </div>

        <!-- Functions Grid - Lazy Loaded -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 scrollbar-thin scrollbar-thumb-blue-300 scrollbar-track-blue-100 dark:scrollbar-thumb-blue-700 dark:scrollbar-track-blue-900" ref="scrollContainerFunc">
             <FunctionEntry
                v-for="func in pagedFunctions"
                :key="func.id || func.full_path"
                :ref="el => setFunctionRef(func.id || func.full_path, el)"
                :function_call="func"
                :is-mounted="func.isMounted"
                :is-processing="func.isProcessing"
                :get-icon-url="getFunctionIcon"
                :on-img-error="imgPlaceholder"
                @mount="handleMount(func)"
                @unmount="handleUnmount(func)"
                @remount="handleRemount(func)"
                @show-settings="handleSettings(func)"
                @edit="handleEdit(func)"
                 @copy-to-custom="handleCopyToCustom(func)"
                 @copy-name="handleCopyName(func)"
                @open-folder="handleOpenFolder(func)"
            />
        </div>

        <!-- Loading More Indicator / Trigger -->
        <div ref="loadMoreTriggerFunc" class="h-10">
            <div v-if="hasMoreFunctionsToLoad && !isLoadingFunctions && !isSearchingFunc" class="flex justify-center items-center text-center text-blue-500 dark:text-blue-400 py-4">
                 <svg aria-hidden="true" class="w-5 h-5 mr-2 text-blue-300 dark:text-blue-600 animate-spin fill-blue-500 dark:fill-blue-400" viewBox="0 0 100 101" fill="none" xmlns="http://www.w3.org/2000/svg"> <path d="M100 50.5908C100 78.2051 77.6142 100.591 50 100.591C22.3858 100.591 0 78.2051 0 50.5908C0 22.9766 22.3858 0.59082 50 0.59082C77.6142 0.59082 100 22.9766 100 50.5908ZM9.08144 50.5908C9.08144 73.1895 27.4013 91.5094 50 91.5094C72.5987 91.5094 90.9186 73.1895 90.9186 50.5908C90.9186 27.9921 72.5987 9.67226 50 9.67226C27.4013 9.67226 9.08144 27.9921 9.08144 50.5908Z" fill="currentColor"/> <path d="M93.9676 39.0409C96.393 38.4038 97.8624 35.9116 97.0079 33.5539C95.2932 28.8227 92.871 24.3692 89.8167 20.348C85.8452 15.1192 80.8826 10.7238 75.2124 7.41289C69.5422 4.10194 63.2754 1.94025 56.7698 1.05124C51.7666 0.367541 46.6976 0.446843 41.7345 1.27873C39.2613 1.69328 37.813 4.19778 38.4501 6.62326C39.0873 9.04874 41.5694 10.4717 44.0505 10.1071C47.8511 9.54855 51.7191 9.52689 55.5402 10.0491C60.8642 10.7766 65.9928 12.5457 70.6331 15.2552C75.2735 17.9648 79.3347 21.5619 82.5849 25.841C84.9175 28.9121 86.7997 32.2913 88.1811 35.8758C89.083 38.2158 91.5421 39.6781 93.9676 39.0409Z" fill="currentFill"/> </svg>
                <span>Loading more...</span>
            </div>
        </div>
    </div>
</template>
<script>
import { nextTick } from 'vue';
import feather from 'feather-icons';
import FunctionEntry from '@/components/FunctionEntry.vue';
import defaultFunctionIcon from "@/assets/default_function.png";
import axios from 'axios'; // Assuming axios is configured globally or imported

// Helper for debounce
function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func.apply(this, args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}


export default {
    name: 'FunctionCallsZoo',
    components: {
        FunctionEntry
    },
    props: {
        config: { type: Object, required: true },
        api_post_req: { type: Function, required: true },
        api_get_req: { type: Function, required: true },
        show_toast: { type: Function, required: true },
        show_yes_no_dialog: { type: Function, required: true },
        show_universal_form: { type: Function, required: true },
        show_message_box: { type: Function, required: true },
        client_id: { type: String, required: true } // Assuming client_id is needed for API calls
    },
    emits: ['update:setting'], // Emits updates to parent config

    data() {
        return {
            allFunctions: [], // Master list: [{...functionData, full_path: string, isMounted: boolean, id: string, isProcessing: boolean}]
            categoriesFunc: [],
            filteredFunctions: [], // Result of filtering/sorting allFunctions
            pagedFunctions: [], // Subset of filteredFunctions for display

            isLoadingFunctions: false,
            isSearchingFunc: false,
            searchTermFunc: '',
            selectedCategoryFunc: '',
            sortOptionFunc: 'mounted', // Default sort: 'mounted', 'name', 'author', 'category'

            itemsPerPageFunc: 15,
            currentPageFunc: 1,
            // searchDebounceTimerFunc: null, // Replaced with imported debounce

            maxDisplayedMountedFunc: 7,
            functionEntryRefs: {},
            observerFunc: null,
            defaultIcon: defaultFunctionIcon,
            axiosBaseUrl: axios.defaults.baseURL || '' // Store base URL if set globally
        };
    },

    computed: {
        // Use a Set for efficient lookups of mounted paths
        mountedFunctionPathsSet() {
            return new Set(this.config?.mounted_functions || []);
        },

        // **Key Change**: Derive the list of mounted function *objects* directly
        // from the master list (`allFunctions`) based on the config prop.
        // This replaces the old `updateMountedFuncList` method.
        mountedFunctions() {
            return this.allFunctions.filter(func =>
                this.mountedFunctionPathsSet.has(func.full_path)
            );
        },

        // List for the header display (limited number)
        displayedMountedFunctions() {
            // Sort mounted functions alphabetically for consistent header display
            const sortedMounted = [...this.mountedFunctions].sort((a, b) => (a.name || '').localeCompare(b.name || ''));
            return sortedMounted.slice(0, this.maxDisplayedMountedFunc);
        },

        // Flag indicating if more items can be loaded via infinite scroll
        hasMoreFunctionsToLoad() {
            return this.pagedFunctions.length < this.filteredFunctions.length;
        }
    },

    watch: {
        // **Key Change**: Watch the config prop directly.
        // When it changes, update the `isMounted` flag on the `allFunctions` items.
        // This ensures the internal state reflects the external config.
        'config.mounted_functions': {
            handler(newPathsArray) {
                console.log("Watcher: config.mounted_functions changed", newPathsArray);
                const newMountedSet = new Set(newPathsArray || []);
                let listNeedsResort = false;

                this.allFunctions.forEach(func => {
                    const shouldBeMounted = newMountedSet.has(func.full_path);
                    if (func.isMounted !== shouldBeMounted) {
                        func.isMounted = shouldBeMounted;
                        // If mounted status changes, sorting order might change
                        listNeedsResort = true;
                    }
                });

                // If the mounted status of any item changed, we must re-apply
                // sorting and filtering to maintain the correct display order.
                if (listNeedsResort) {
                    console.log("Watcher: Re-applying filters and sort due to mounted status change.");
                    this.resetAndReloadFunctions(); // Re-run the filter/sort/paginate process
                }

                // The computed 'mountedFunctions' automatically updates the header.
                 this.featherReplace(); // Ensure icons update in header too
            },
            // immediate: true, // Let initial fetch populate first, then watcher updates
            deep: true // Usually needed for arrays/objects
        },

        // Watchers for filter/sort options - trigger a debounced reload
        searchTermFunc() { this.debouncedResetAndReload(); },
        selectedCategoryFunc() { this.debouncedResetAndReload(); },
        sortOptionFunc() { this.debouncedResetAndReload(); },

        // Watcher for the master list itself (e.g., after fetch or copy)
        // Triggers the initial filtering and loading sequence.
        allFunctions: {
           handler() {
               console.log("Watcher: allFunctions list changed. Triggering initial load.");
               this.resetAndReloadFunctions();
           },
           // No deep needed if only the array reference changes (e.g., on fetch)
        }
    },

    methods: {
        // --- Utility & Display ---
        getFunctionIcon(iconPath) {
            if (!iconPath) return this.defaultIcon;
            // Handle potential absolute vs relative paths better
            if (iconPath.startsWith('http://') || iconPath.startsWith('https://') || iconPath.startsWith('/')) {
                 // Assume absolute or root-relative path that works as is, or needs base URL prepended if root-relative
                 return iconPath.startsWith('/') ? `${this.axiosBaseUrl}${iconPath}` : iconPath;
            } else {
                 // Assume relative path needing base URL
                 return `${this.axiosBaseUrl}/${iconPath}`;
            }
        },
        imgPlaceholder(event) {
            event.target.src = this.defaultIcon;
        },
        featherReplace() {
            this.$nextTick(() => {
                try {
                    feather.replace();
                } catch (e) {
                    console.error("Feather replace error:", e);
                }
            });
        },
        setFunctionRef(key, el) {
            if (el) {
                this.functionEntryRefs[key] = el;
            }
        },

        // --- Data Fetching & Processing ---
        async fetchFunctionsAndCategories() {
            if (this.isLoadingFunctions) return; // Prevent concurrent fetches
            this.isLoadingFunctions = true;
            console.log("Fetching functions and categories...");
            try {
                const response = await this.api_get_req("list_function_calls");
                const allFuncsRaw = response?.function_calls || [];

                const cats = new Set(allFuncsRaw.map(func => func.category).filter(Boolean)); // Filter out null/empty categories
                this.categoriesFunc = Array.from(cats).sort();

                // Map raw data. Crucially, DO NOT set isMounted here.
                // The watcher for 'config.mounted_functions' will handle setting isMounted
                // once 'allFunctions' is populated.
                this.allFunctions = allFuncsRaw.map(func => {
                    const full_path = `${func.category}/${func.name}`; // Ensure consistent path format
                    const uniqueId = func.id || full_path; // Use id if available, else path
                    return {
                        ...func,
                        full_path: full_path,
                        isMounted: false, // Initialize as false, watcher will correct this
                        id: uniqueId,
                        isProcessing: false
                    };
                });
                console.log(`Fetched ${this.allFunctions.length} total functions.`);
                // Initial filter/sort/load is triggered by the 'allFunctions' watcher

                 // Explicitly trigger the config watcher after fetch in case config loaded before fetch finished
                 this.$nextTick(() => {
                    if (this.config?.mounted_functions) {
                        this.watch['config.mounted_functions'].handler.call(this, this.config.mounted_functions);
                    }
                 });


            } catch (error) {
                this.show_toast("Failed to load functions list.", 4, false);
                console.error("Error fetching functions:", error);
                this.allFunctions = []; // Reset on error
                this.categoriesFunc = [];
            } finally {
                this.isLoadingFunctions = false;
                 // No need to call featherReplace here, watcher/loadMore will handle it
            }
        },

        // Combined filter and sort logic
        applyFiltersAndSortFunc() {
            console.time("FilterSortFunctions");
            let result = [...this.allFunctions];

            // 1. Filter by Category
            if (this.selectedCategoryFunc) {
                result = result.filter(f => f.category === this.selectedCategoryFunc);
            }

            // 2. Filter by Search Term
            if (this.searchTermFunc) {
                const lowerSearch = this.searchTermFunc.toLowerCase();
                result = result.filter(f => {
                    const nameMatch = f.name?.toLowerCase().includes(lowerSearch);
                    const authorMatch = f.author?.toLowerCase().includes(lowerSearch);
                    const descMatch = f.description?.toLowerCase().includes(lowerSearch);
                    const catMatch = f.category?.toLowerCase().includes(lowerSearch);
                    const pathMatch = f.full_path?.toLowerCase().includes(lowerSearch);
                    const keywordsMatch = Array.isArray(f.keywords) ? f.keywords.some(k => k.toLowerCase().includes(lowerSearch)) : false;
                    return nameMatch || authorMatch || descMatch || catMatch || pathMatch || keywordsMatch;
                });
            }

            // 3. Sort
            result.sort((a, b) => {
                 // Primary sort by mounted status if selected
                 if (this.sortOptionFunc === 'mounted') {
                    if (a.isMounted && !b.isMounted) return -1;
                    if (!a.isMounted && b.isMounted) return 1;
                 }

                 // Secondary sort based on selected option or default to name
                const option = (this.sortOptionFunc !== 'mounted') ? this.sortOptionFunc : 'name';
                switch (option) {
                    case 'name': return (a.name || '').localeCompare(b.name || '');
                    case 'author': return (a.author || '').localeCompare(b.author || '');
                    case 'category': return (a.category || '').localeCompare(b.category || '');
                    default: return 0;
                }
            });

            this.filteredFunctions = result;
            console.timeEnd("FilterSortFunctions");
            console.log(`Filtered/Sorted functions: ${this.filteredFunctions.length}`);
        },

        // Resets pagination and applies filters/sort, then loads the first page
        resetAndReloadFunctions() {
            this.currentPageFunc = 1;
            this.pagedFunctions = []; // Clear current pages
            this.applyFiltersAndSortFunc(); // Apply current filters/sort
            this.$nextTick(() => { // Ensure DOM is ready for potential scroll updates
                 this.loadMoreFunctions(); // Load the first page
            });
        },

        // Debounced version of resetAndReloadFunctions for user input
        debouncedResetAndReload: debounce(function() {
            this.isSearchingFunc = true; // Show spinner
            this.resetAndReloadFunctions();
            // Hide spinner after a short delay to allow rendering
            setTimeout(() => { this.isSearchingFunc = false; }, 100);
        }, 300), // 300ms debounce delay


        // Loads the next page of functions
        loadMoreFunctions() {
            if (this.isLoadingFunctions || this.isSearchingFunc || !this.hasMoreFunctionsToLoad) {
                return;
            }
            console.log(`Loading page ${this.currentPageFunc}`);

            const start = (this.currentPageFunc - 1) * this.itemsPerPageFunc;
            const end = start + this.itemsPerPageFunc;
            const nextPageItems = this.filteredFunctions.slice(start, end);

            // Prevent duplicates if called rapidly (though less likely with observer)
            const existingIds = new Set(this.pagedFunctions.map(p => p.id || p.full_path));
            const uniqueNewItems = nextPageItems.filter(item => !existingIds.has(item.id || item.full_path));

            if (uniqueNewItems.length > 0) {
                this.pagedFunctions.push(...uniqueNewItems);
                this.currentPageFunc++;
                 this.featherReplace(); // Replace icons after adding new items
            } else if (nextPageItems.length > 0) {
                console.log("Load more triggered but items already seem to be loaded.");
            }
        },

        // Helper to update the processing state visually
        setFunctionProcessing(funcIdOrPath, state) {
             const updateItem = (item) => { if (item) item.isProcessing = state; };

             const indexAll = this.allFunctions.findIndex(f => (f.id || f.full_path) === funcIdOrPath);
             updateItem(this.allFunctions[indexAll]);

             const indexPaged = this.pagedFunctions.findIndex(f => (f.id || f.full_path) === funcIdOrPath);
             updateItem(this.pagedFunctions[indexPaged]);
        },

        // --- Function Actions (Mount, Unmount, etc.) ---
        // These methods now just focus on the API call and emitting the event.
        // The watcher on `config.mounted_functions` handles the UI update.

        async handleMount(func) {
            if (func.isMounted || func.isProcessing) return;
            const funcId = func.id || func.full_path;
            this.setFunctionProcessing(funcId, true);
            this.show_toast(`Mounting ${func.name}...`, 3, true);
            try {
                // API uses category and name
                const response = await this.api_post_req('mount_function_call', {
                    client_id: this.client_id, // Add client_id if required by API
                    function_category: func.category,
                    function_name: func.name
                });
                if (response && response.status) {
                    this.show_toast(`${func.name} mounted successfully.`, 4, true);
                    // Emit the *new complete list* of mounted paths
                    const newMountedList = [...this.mountedFunctionPathsSet, func.full_path];
                    this.$emit('update:setting', { key: 'mounted_functions', value: newMountedList });
                    // Watcher will update internal 'isMounted' flags and UI
                } else {
                    this.show_toast(`Failed to mount ${func.name}: ${response?.error || 'Error'}`, 4, false);
                }
            } catch (error) {
                this.show_toast(`Error mounting ${func.name}: ${error.message || error}`, 4, false);
                console.error("Mount error:", error);
            } finally {
                this.setFunctionProcessing(funcId, false);
            }
        },

        async handleUnmount(func) {
            if (!func.isMounted || func.isProcessing) return;
            const funcId = func.id || func.full_path;
            this.setFunctionProcessing(funcId, true);
            this.show_toast(`Unmounting ${func.name}...`, 3, true);
            try {
                // API might just use name, or category/name
                const response = await this.api_post_req('unmount_function_call', {
                    client_id: this.client_id, // Add client_id if required by API
                    function_category: func.category, // Include if needed
                    function_name: func.name
                });
                if (response && response.status) {
                    this.show_toast(`${func.name} unmounted.`, 4, true);
                    // Emit the *new complete list* of mounted paths
                    const newMountedList = (this.config?.mounted_functions || []).filter(p => p !== func.full_path);
                    this.$emit('update:setting', { key: 'mounted_functions', value: newMountedList });
                     // Watcher will update internal 'isMounted' flags and UI
                } else {
                    this.show_toast(`Failed to unmount ${func.name}: ${response?.error || 'Error'}`, 4, false);
                }
            } catch (error) {
                this.show_toast(`Error unmounting ${func.name}: ${error.message || error}`, 4, false);
                console.error("Unmount error:", error);
            } finally {
                this.setFunctionProcessing(funcId, false);
            }
        },

        async unmountAll() {
            if (this.mountedFunctions.length === 0) return; // Nothing to unmount
            const yes = await this.show_yes_no_dialog(`Unmount all ${this.mountedFunctions.length} functions?`, 'Unmount All', 'Cancel');
            if (!yes) return;

            this.show_toast(`Unmounting all functions...`, 3, true);
            // Visually mark all mounted as processing (optional)
             this.mountedFunctions.forEach(func => this.setFunctionProcessing(func.id || func.full_path, true));

            try {
                const response = await this.api_post_req('unmount_all_functions', { client_id: this.client_id }); // Add client_id
                if (response && response.status) {
                    this.show_toast('All functions unmounted.', 4, true);
                    this.$emit('update:setting', { key: 'mounted_functions', value: [] }); // Emit empty list
                     // Watcher will update UI
                } else {
                    this.show_toast(`Failed to unmount all: ${response?.error || 'Error'}`, 4, false);
                     // Reset processing state on error if needed
                     this.mountedFunctions.forEach(func => this.setFunctionProcessing(func.id || func.full_path, false));
                }
            } catch (error) {
                this.show_toast(`Error unmounting all: ${error.message || error}`, 4, false);
                console.error("Unmount all error:", error);
                 // Reset processing state on error
                 this.mountedFunctions.forEach(func => this.setFunctionProcessing(func.id || func.full_path, false));
            }
            // No finally needed here, watcher handles resetting processing via 'isMounted' update
        },

         async handleRemount(func) {
             const funcId = func.id || func.full_path;
             if (func.isProcessing) return;
             this.setFunctionProcessing(funcId, true);
             this.show_toast(`Remounting ${func.name}...`, 3, true);

             try {
                 let currentMountedPaths = [...(this.config.mounted_functions || [])];
                 const isCurrentlyMounted = currentMountedPaths.includes(func.full_path);

                 // 1. Unmount if currently mounted
                 if (isCurrentlyMounted) {
                     const unmountResponse = await this.api_post_req('unmount_function_call', { client_id: this.client_id, function_category: func.category, function_name: func.name });
                     if (!unmountResponse || !unmountResponse.status) {
                         this.show_toast(`Failed to unmount ${func.name} during remount. Aborting.`, 4, false);
                         this.setFunctionProcessing(funcId, false);
                         return; // Stop if unmount fails
                     }
                     // Emit the unmounted state
                     currentMountedPaths = currentMountedPaths.filter(p => p !== func.full_path);
                     this.$emit('update:setting', { key: 'mounted_functions', value: currentMountedPaths });
                     await nextTick(); // Give watcher time to process the unmount
                     console.log("Remount Step 1: Unmounted and emitted.")
                 }

                 // 2. Mount (or re-mount)
                 const mountResponse = await this.api_post_req('mount_function_call', { client_id: this.client_id, function_category: func.category, function_name: func.name });
                 if (mountResponse && mountResponse.status) {
                     this.show_toast(`${func.name} remounted successfully.`, 4, true);
                     // Emit the mounted state (add if not already present)
                     if (!currentMountedPaths.includes(func.full_path)) {
                         currentMountedPaths.push(func.full_path);
                     }
                     this.$emit('update:setting', { key: 'mounted_functions', value: currentMountedPaths });
                     console.log("Remount Step 2: Mounted and emitted.")
                      // Watcher updates UI state based on the final emitted list
                 } else {
                     this.show_toast(`Failed to mount ${func.name} during remount: ${mountResponse?.error || 'Error'}`, 4, false);
                     // If mount failed after a successful unmount, the config prop state is already correct (unmounted).
                     // The watcher should have already handled the UI update for the unmount step.
                 }
             } catch (error) {
                 this.show_toast(`Error remounting ${func.name}: ${error.message || error}`, 4, false);
                 console.error("Remount error:", error);
             } finally {
                  // Reset processing state regardless of success/failure
                  // The watcher triggered by the last emit will ensure 'isMounted' is correct.
                 this.setFunctionProcessing(funcId, false);
             }
         },

        async handleSettings(func) {
            if (func.isProcessing) return;
            const funcId = func.id || func.full_path;
            this.setFunctionProcessing(funcId, true);
            try {
                // API uses category and name
                const settingsData = await this.api_post_req('get_function_call_settings', {
                    client_id: this.client_id, // Add client_id
                    category: func.category,
                    name: func.name
                });
                // Check if settingsData is a non-empty object
                if (settingsData && typeof settingsData === 'object' && Object.keys(settingsData).length > 0) {
                     // show_universal_form should return the result or null if cancelled
                    const result = await this.show_universal_form(settingsData, `Function Settings - ${func.name}`, "Save", "Cancel");

                    if(result !== null && result !== undefined){ // User clicked Save
                        const setResponse = await this.api_post_req('set_function_call_settings', {
                            client_id: this.client_id, // Add client_id
                            category: func.category,
                            name: func.name,
                            settings: result // Send back the modified settings
                        });
                        if (setResponse && setResponse.status) {
                            this.show_toast(`Settings for ${func.name} updated.`, 4, true);
                        } else {
                            this.show_toast(`Failed to update settings for ${func.name}: ${setResponse?.error || 'Error'}`, 4, false);
                        }
                    } else {
                         // User clicked Cancel or closed the form
                         this.show_toast(`Settings update for ${func.name} cancelled.`, 3, true);
                    }
                } else if (settingsData && typeof settingsData === 'object' && Object.keys(settingsData).length === 0) {
                     // Function exists but has no settings
                     this.show_message_box(`Function "${func.name}" has no configurable settings.`);
                 } else {
                     // Error retrieving settings or invalid format
                     this.show_toast(`Could not retrieve settings for ${func.name}: ${settingsData?.error || 'Invalid response'}`, 4, false);
                 }
            } catch (error) {
                this.show_toast(`Error accessing settings for ${func.name}: ${error.message || error}`, 4, false);
                console.error("Settings error:", error);
            } finally {
                this.setFunctionProcessing(funcId, false);
            }
        },

        async handleEdit(func) {
            this.show_toast(`Opening folder containing "${func.name}" for editing...`, 3, true);
            await this.handleOpenFolder(func); // Re-use open folder logic
        },

        async handleCopyToCustom(func) {
            const yes = await this.show_yes_no_dialog(`Copy "${func.name}" from "${func.category}" to your 'custom_functions' folder?`, 'Copy', 'Cancel');
            if (!yes) return;
            if (func.isProcessing) return;
            const funcId = func.id || func.full_path;
            this.setFunctionProcessing(funcId, true);
            try {
                const response = await this.api_post_req('copy_to_custom_functions', {
                    client_id: this.client_id, // Add client_id
                    category: func.category,
                    name: func.name
                });
                if (response && response.status) {
                    this.show_message_box(`Function "${func.name}" copied to 'custom_functions'. The list will refresh shortly.`);
                    // Re-fetch the entire list to include the new custom function
                    await this.fetchFunctionsAndCategories();
                } else {
                    // Handle specific errors like already exists if provided by API
                    this.show_toast(`Failed to copy ${func.name}: ${response?.error || 'Already exists in custom?'}`, 4, false);
                }
            } catch (error) {
                this.show_toast(`Error copying ${func.name}: ${error.message || error}`, 4, false);
                console.error("Copy to custom error:", error);
            } finally {
                this.setFunctionProcessing(funcId, false);
            }
        },

        handleCopyName(func) {
            navigator.clipboard.writeText(func.name)
                .then(() => this.show_toast(`Copied name: ${func.name}`, 3, true))
                .catch(err => {
                    this.show_toast("Failed to copy name to clipboard.", 3, false);
                    console.error("Clipboard copy failed:", err);
                });
        },

        async handleOpenFolder(func) {
            try {
                await this.api_post_req("open_function_folder", {
                     client_id: this.client_id, // Add client_id
                     category: func.category,
                     name: func.name
                });
                 // No success toast needed, OS should open the folder
            } catch (error) {
                this.show_toast(`Error opening folder for ${func.name}: ${error.message || error}`, 4, false);
                console.error("Open folder error:", error);
            }
        },

        scrollToFunction(func) {
            const funcId = func.id || func.full_path;
            const elementComponent = this.functionEntryRefs[funcId];

            if (elementComponent && elementComponent.$el) {
                const element = elementComponent.$el;
                element.scrollIntoView({ behavior: 'smooth', block: 'center' });
                // Highlight effect
                element.classList.add('ring-2', 'ring-offset-2', 'ring-blue-500', 'dark:ring-offset-gray-800', 'transition-all', 'duration-1000', 'ease-out');
                setTimeout(() => {
                    element.classList.remove('ring-2', 'ring-offset-2', 'ring-blue-500', 'dark:ring-offset-gray-800', 'transition-all', 'duration-1000', 'ease-out');
                }, 1500);
            } else {
                console.warn(`Could not find ref $el to scroll to for function ID: ${funcId}. Is it loaded?`);
                // Attempt to load more if the function isn't visible and more exist
                if (this.hasMoreFunctionsToLoad && !this.pagedFunctions.some(f => (f.id || f.full_path) === funcId)) {
                    this.show_toast(`Function ${func.name} not visible, attempting to load more...`, 3, true);
                    // TODO: Implement a more robust load-until-found or jump-to-page logic if needed.
                    // For now, just trigger one load cycle.
                    this.loadMoreFunctions();
                    // Try scrolling again after a delay
                    setTimeout(() => this.scrollToFunction(func), 500);
                } else {
                    this.show_toast(`Could not scroll to ${func.name}.`, 3, false);
                }
            }
        },

        // --- Infinite Scroll ---
        setupIntersectionObserverFunc() {
             // Disconnect previous observer if exists
             this.disconnectIntersectionObserver();

             const options = { root: null, rootMargin: '100px', threshold: 0.1 }; // Load slightly before visible
            this.observerFunc = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting && this.hasMoreFunctionsToLoad) {
                        this.loadMoreFunctions();
                    }
                });
            }, options);

            const triggerElement = this.$refs.loadMoreTriggerFunc;
            if (triggerElement) {
                 this.observerFunc.observe(triggerElement);
                 console.log("IntersectionObserver setup complete.");
            } else {
                 // This might happen during initial render, try again next tick
                 this.$nextTick(() => {
                    const trigger = this.$refs.loadMoreTriggerFunc;
                    if(trigger) {
                        this.observerFunc.observe(trigger);
                         console.log("IntersectionObserver setup complete (nextTick).");
                    } else {
                        console.error("Load more trigger element not found for IntersectionObserver setup.");
                    }
                 });
            }
        },
        disconnectIntersectionObserver() {
            if (this.observerFunc) {
                 console.log("Disconnecting IntersectionObserver.");
                 // Find the element to unobserve safely
                 const triggerElement = this.$refs.loadMoreTriggerFunc;
                 if (triggerElement) {
                    try {
                        this.observerFunc.unobserve(triggerElement);
                    } catch (e) { console.warn("Error unobserving trigger:", e); }
                 }
                this.observerFunc.disconnect();
                this.observerFunc = null;
            }
        }
    },

    // --- Lifecycle Hooks ---
    mounted() {
        console.log("FunctionCallsZoo Mounted.");
        this.fetchFunctionsAndCategories(); // Initial data fetch
        this.featherReplace();
        // Setup observer after initial fetch and DOM render attempt
        this.$nextTick(() => {
            this.setupIntersectionObserverFunc();
        });
    },

    beforeUpdate() {
        // Clear refs before update to prevent memory leaks if items are removed
        this.functionEntryRefs = {};
    },

    updated() {
        // Re-apply feather icons after any DOM update
        this.featherReplace();
        // Ensure observer is attached (e.g., if trigger element re-rendered)
        // Check if observer exists and if the trigger element is still observed
        this.$nextTick(() => {
             const triggerElement = this.$refs.loadMoreTriggerFunc;
             if (triggerElement && this.observerFunc && !this.observerFunc.takeRecords().some(entry => entry.target === triggerElement)) {
                console.warn("IntersectionObserver detached from trigger, re-observing.");
                try{ this.observerFunc.unobserve(triggerElement); } catch(e){} // Safely unobserve first
                this.observerFunc.observe(triggerElement);
            } else if (triggerElement && !this.observerFunc) {
                 console.warn("IntersectionObserver lost, re-setting up.");
                 this.setupIntersectionObserverFunc(); // Re-setup if observer was lost
            }
        });
    },

    unmounted() {
        console.log("FunctionCallsZoo Unmounted.");
        // Cleanup observer and timers
        this.disconnectIntersectionObserver();
        // Clear any pending debounce timers if necessary (though component destruction usually handles this)
        // clearTimeout(this.searchDebounceTimerFunc); // No longer needed with imported debounce
    }
}
</script>

<style scoped>
/* Reuse input style from your project or define here */
.input {
     @apply block w-full px-3 py-2 text-sm bg-gray-100 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50 dark:text-gray-100;
}
.btn {
    @apply inline-flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 transition-colors duration-150 dark:focus:ring-offset-gray-800;
}
.btn-sm {
    @apply px-2.5 py-1.5 text-xs; /* Adjust padding and text size for smaller buttons */
}

/* Basic scrollbar styling */
.scrollbar-thin {
  scrollbar-width: thin;
  scrollbar-color: var(--scrollbar-thumb) var(--scrollbar-track);
}
.scrollbar-thin::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}
.scrollbar-thin::-webkit-scrollbar-track {
  background: var(--scrollbar-track);
  border-radius: 4px;
}
.scrollbar-thin::-webkit-scrollbar-thumb {
  background-color: var(--scrollbar-thumb);
  border-radius: 4px;
  border: 2px solid var(--scrollbar-track); /* Creates padding around thumb */
}

/* Define scrollbar colors (Tailwind doesn't have scrollbar color utilities by default) */
:root {
  --scrollbar-thumb: #cbd5e1; /* gray-300 */
  --scrollbar-track: #f1f5f9; /* gray-100 */
}
.dark:root {
  --scrollbar-thumb: #4b5563; /* gray-600 */
  --scrollbar-track: #1f2937; /* gray-800 */
}

/* Style for scrollbar using the CSS variables (applied on the element with scrollbar-thin) */
.scrollbar-thumb-blue-300 { --scrollbar-thumb: #93c5fd; } /* Light mode blue */
.scrollbar-track-blue-100 { --scrollbar-track: #dbeafe; } /* Light mode blue */
.dark .dark\:scrollbar-thumb-blue-700 { --scrollbar-thumb: #1d4ed8; } /* Dark mode blue */
.dark .dark\:scrollbar-track-blue-900 { --scrollbar-track: #1e3a8a; } /* Dark mode blue */

</style>