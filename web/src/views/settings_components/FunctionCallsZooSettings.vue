<template>
    <div class="space-y-6 p-4 md:p-6 bg-white dark:bg-gray-800 rounded-lg shadow-md border border-gray-200 dark:border-gray-700">
        <!-- Header Section -->
        <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center border-b border-gray-200 dark:border-gray-700 pb-3 mb-4">
            <h2 class="text-xl font-semibold text-gray-800 dark:text-gray-200 mb-2 sm:mb-0">
                Function Calls Zoo
            </h2>
            <!-- Mounted Functions Display -->
            <div class="flex flex-col items-end">
                 <div class="flex items-center flex-wrap gap-2 text-sm font-medium mb-1">
                     <span class="text-gray-600 dark:text-gray-400">Mounted:</span>
                     <div v-if="mountedFunctions.length === 0" class="text-gray-500 dark:text-gray-500 italic text-xs">None</div>
                    <div v-else class="flex -space-x-3 items-center">
                         <!-- Limited display of mounted icons -->
                         <div v-for="(func, index) in displayedMountedFunctions" :key="`mounted-${func.full_path || index}`" class="relative group">
                            <img :src="getFunctionIcon(func.icon)" @error="imgPlaceholder"
                                class="w-7 h-7 rounded-full object-cover ring-2 ring-white dark:ring-gray-800 cursor-pointer hover:ring-primary transition-all"
                                :title="`${func.name} (${func.category})`"
                                @click="scrollToFunction(func)"> <!-- Click scrolls to the function in the list -->
                            <button @click.stop="handleUnmount(func)"
                                class="absolute -top-1 -right-1 p-0.5 rounded-full bg-red-600 text-white opacity-0 group-hover:opacity-100 transition-opacity duration-150 hover:bg-red-700"
                                title="Unmount">
                                <i data-feather="x" class="w-3 h-3"></i>
                            </button>
                         </div>
                         <div v-if="mountedFunctions.length > maxDisplayedMountedFunc"
                             class="w-7 h-7 rounded-full bg-gray-200 dark:bg-gray-600 ring-2 ring-white dark:ring-gray-800 flex items-center justify-center text-xs font-semibold text-gray-600 dark:text-gray-300"
                             :title="`${mountedFunctions.length - maxDisplayedMountedFunc} more mounted`">
                            +{{ mountedFunctions.length - maxDisplayedMountedFunc }}
                         </div>
                     </div>
                 </div>
                 <button v-if="mountedFunctions.length > 0" @click="unmountAll" class="button-danger-sm text-xs mt-1">
                     <i data-feather="x-octagon" class="w-3 h-3 mr-1"></i>Unmount All
                </button>
            </div>
        </div>

         <p class="text-sm text-gray-500 dark:text-gray-400">
             Mount functions to grant the AI specific capabilities and tools it can use during conversations. Requires a model trained for function calling.
        </p>

        <!-- Controls: Search, Category, Sort -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4 items-center">
             <!-- Search Input -->
            <div class="relative md:col-span-1">
                 <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                     <i data-feather="search" class="w-5 h-5 text-gray-400"></i>
                </div>
                 <input
                    type="search"
                    v-model="searchTermFunc"
                    placeholder="Search functions..."
                    class="input-field pl-10 w-full"
                    @input="debounceSearchFunc"
                />
                 <div v-if="isSearchingFunc" class="absolute inset-y-0 right-0 pr-3 flex items-center">
                    <svg aria-hidden="true" class="w-5 h-5 text-gray-400 animate-spin dark:text-gray-500 fill-primary" viewBox="0 0 100 101" fill="none" xmlns="http://www.w3.org/2000/svg"> <path d="M100 50.5908C100 78.2051 77.6142 100.591 50 100.591C22.3858 100.591 0 78.2051 0 50.5908C0 22.9766 22.3858 0.59082 50 0.59082C77.6142 0.59082 100 22.9766 100 50.5908ZM9.08144 50.5908C9.08144 73.1895 27.4013 91.5094 50 91.5094C72.5987 91.5094 90.9186 73.1895 90.9186 50.5908C90.9186 27.9921 72.5987 9.67226 50 9.67226C27.4013 9.67226 9.08144 27.9921 9.08144 50.5908Z" fill="currentColor"/> <path d="M93.9676 39.0409C96.393 38.4038 97.8624 35.9116 97.0079 33.5539C95.2932 28.8227 92.871 24.3692 89.8167 20.348C85.8452 15.1192 80.8826 10.7238 75.2124 7.41289C69.5422 4.10194 63.2754 1.94025 56.7698 1.05124C51.7666 0.367541 46.6976 0.446843 41.7345 1.27873C39.2613 1.69328 37.813 4.19778 38.4501 6.62326C39.0873 9.04874 41.5694 10.4717 44.0505 10.1071C47.8511 9.54855 51.7191 9.52689 55.5402 10.0491C60.8642 10.7766 65.9928 12.5457 70.6331 15.2552C75.2735 17.9648 79.3347 21.5619 82.5849 25.841C84.9175 28.9121 86.7997 32.2913 88.1811 35.8758C89.083 38.2158 91.5421 39.6781 93.9676 39.0409Z" fill="currentFill"/> </svg>
                 </div>
            </div>
            <!-- Category Filter -->
            <div class="md:col-span-1">
                <label for="func-category" class="sr-only">Filter by Category</label>
                 <select id="func-category" v-model="selectedCategoryFunc" class="input-field">
                    <option value="">All Categories</option>
                     <option v-for="cat in categoriesFunc" :key="cat" :value="cat">{{ cat }}</option>
                </select>
            </div>
            <!-- Sort Select -->
            <div class="md:col-span-1">
                 <label for="func-sort" class="sr-only">Sort functions by</label>
                 <select id="func-sort" v-model="sortOptionFunc" class="input-field">
                    <option value="name">Sort by Name</option>
                    <option value="author">Sort by Author</option>
                     <option value="category">Sort by Category</option>
                 </select>
             </div>
        </div>

         <!-- Loading / Empty State -->
         <div v-if="isLoadingFunctions" class="flex justify-center items-center p-10 text-gray-500 dark:text-gray-400">
            <svg aria-hidden="true" class="w-8 h-8 mr-2 text-gray-300 animate-spin dark:text-gray-600 fill-primary" viewBox="0 0 100 101" fill="none" xmlns="http://www.w3.org/2000/svg"> <path d="M100 50.5908C100 78.2051 77.6142 100.591 50 100.591C22.3858 100.591 0 78.2051 0 50.5908C0 22.9766 22.3858 0.59082 50 0.59082C77.6142 0.59082 100 22.9766 100 50.5908ZM9.08144 50.5908C9.08144 73.1895 27.4013 91.5094 50 91.5094C72.5987 91.5094 90.9186 73.1895 90.9186 50.5908C90.9186 27.9921 72.5987 9.67226 50 9.67226C27.4013 9.67226 9.08144 27.9921 9.08144 50.5908Z" fill="currentColor"/> <path d="M93.9676 39.0409C96.393 38.4038 97.8624 35.9116 97.0079 33.5539C95.2932 28.8227 92.871 24.3692 89.8167 20.348C85.8452 15.1192 80.8826 10.7238 75.2124 7.41289C69.5422 4.10194 63.2754 1.94025 56.7698 1.05124C51.7666 0.367541 46.6976 0.446843 41.7345 1.27873C39.2613 1.69328 37.813 4.19778 38.4501 6.62326C39.0873 9.04874 41.5694 10.4717 44.0505 10.1071C47.8511 9.54855 51.7191 9.52689 55.5402 10.0491C60.8642 10.7766 65.9928 12.5457 70.6331 15.2552C75.2735 17.9648 79.3347 21.5619 82.5849 25.841C84.9175 28.9121 86.7997 32.2913 88.1811 35.8758C89.083 38.2158 91.5421 39.6781 93.9676 39.0409Z" fill="currentFill"/> </svg>
             <span>Loading functions...</span>
        </div>
         <div v-else-if="pagedFunctions.length === 0" class="text-center text-gray-500 dark:text-gray-400 py-10">
            No functions found{{ searchTermFunc ? ' matching "' + searchTermFunc + '"' : '' }}{{ selectedCategoryFunc ? ' in category "' + selectedCategoryFunc + '"' : '' }}.
         </div>

        <!-- Functions Grid - Lazy Loaded -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4" ref="scrollContainerFunc">
             <FunctionEntry
                v-for="func in pagedFunctions"
                :key="func.id || func.full_path"
                :ref="el => functionEntryRefs[func.id || func.full_path] = el"
                :function_call="func"
                :is-mounted="func.isMounted"
                @mount="handleMount(func)"
                @unmount="handleUnmount(func)"
                @remount="handleRemount(func)"
                @settings="handleSettings(func)"
                @edit="handleEdit(func)"
                 @copy-to-custom="handleCopyToCustom(func)"
                 @copy-name="handleCopyName(func)"
                @open-folder="handleOpenFolder(func)"
            />
        </div>

        <!-- Loading More Indicator / Trigger -->
        <div ref="loadMoreTriggerFunc" class="h-10">
            <div v-if="hasMoreFunctionsToLoad && !isLoadingFunctions" class="text-center text-gray-500 dark:text-gray-400 py-4">
                Loading more functions...
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick, reactive, onUpdated } from 'vue';
import feather from 'feather-icons';
import FunctionEntry from '@/components/FunctionEntry.vue'; // Assuming this component exists
import defaultFunctionIcon from "@/assets/default_function.png"; // Default icon

const axios = require('axios'); // Use if needed

// Props
const props = defineProps({
    config: { type: Object, required: true },
    api_post_req: { type: Function, required: true },
    api_get_req: { type: Function, required: true },
    show_toast: { type: Function, required: true },
    show_yes_no_dialog: { type: Function, required: true },
    show_universal_form: { type: Function, required: true },
     show_message_box: { type: Function, required: true },
    client_id: { type: String, required: true }
});

// Emits
const emit = defineEmits(['update:setting']);

// --- State ---
const allFunctions = ref([]); // Master list: [{...functionData, full_path: string, isMounted: boolean, id: string, isProcessing: boolean}]
const categoriesFunc = ref([]);
const filteredFunctions = ref([]);
const pagedFunctions = ref([]);
const mountedFunctions = ref([]); // Derived from config

const isLoadingFunctions = ref(false);
const isSearchingFunc = ref(false);
const searchTermFunc = ref('');
const selectedCategoryFunc = ref('');
const sortOptionFunc = ref('name'); // 'name', 'author', 'category'

const itemsPerPageFunc = ref(15);
const currentPageFunc = ref(1);
const searchDebounceTimerFunc = ref(null);

const scrollContainerFunc = ref(null);
const loadMoreTriggerFunc = ref(null);
const maxDisplayedMountedFunc = ref(7); // Adjust as needed
const functionEntryRefs = reactive({}); // For scrolling to entries


// --- Computed ---
const hasMoreFunctionsToLoad = computed(() => {
    return pagedFunctions.value.length < filteredFunctions.value.length;
});

const displayedMountedFunctions = computed(() => {
    return mountedFunctions.value.slice(0, maxDisplayedMountedFunc.value);
});


// --- Watchers ---
watch(() => props.config.mounted_functions, (newVal) => {
    updateMountedFuncList(newVal);
}, { immediate: true, deep: true });

watch([searchTermFunc, selectedCategoryFunc, sortOptionFunc], () => {
    debounceSearchFunc();
});

watch(allFunctions, () => {
    currentPageFunc.value = 1;
    pagedFunctions.value = [];
    applyFiltersAndSortFunc();
    loadMoreFunctions();
}, { deep: true });

// --- Methods ---

const getFunctionIcon = (iconPath) => {
    if (!iconPath) return defaultFunctionIcon;
    // Assuming iconPath is relative
    return `${axios.defaults.baseURL}${iconPath.startsWith('/') ? '' : '/'}${iconPath}`;
};

const imgPlaceholder = (event) => {
    event.target.src = defaultFunctionIcon;
};

const fetchFunctionsAndCategories = async () => {
    isLoadingFunctions.value = true;
    console.log("Fetching functions and categories...");
    try {
        // Fetch all function calls (assuming endpoint returns { function_calls: [...] })
        const response = await props.api_get_req("list_function_calls");
        const allFuncsRaw = response?.function_calls || [];

        // Extract unique categories
        const cats = new Set(allFuncsRaw.map(func => func.category));
        categoriesFunc.value = Array.from(cats).sort();

        const mountedSet = new Set(props.config.mounted_functions || []);

        // Process into the desired format
        allFunctions.value = allFuncsRaw.map(func => {
             const full_path = `${func.category}/${func.name}`; // Assuming 'name' is the unique identifier within category
             const uniqueId = func.id || full_path; // Use backend ID if provided
             return {
                 ...func,
                 full_path: full_path,
                 isMounted: mountedSet.has(full_path),
                 id: uniqueId,
                 isProcessing: false
             };
         });

        console.log(`Fetched ${allFunctions.value.length} total functions.`);
        updateMountedFuncList(props.config.mounted_functions); // Sync mounted list

    } catch (error) {
        props.show_toast("Failed to load functions.", 4, false);
        console.error("Error fetching functions:", error);
        allFunctions.value = [];
        categoriesFunc.value = [];
    } finally {
        isLoadingFunctions.value = false;
        nextTick(feather.replace);
    }
};

const applyFiltersAndSortFunc = () => {
    isSearchingFunc.value = true;
    console.time("FilterSortFunctions");

    let result = [...allFunctions.value];

    // 1. Filter by Category
    if (selectedCategoryFunc.value) {
        result = result.filter(f => f.category === selectedCategoryFunc.value);
    }

    // 2. Filter by Search Term (Improved: Clearer field checks)
    if (searchTermFunc.value) {
        const lowerSearch = searchTermFunc.value.toLowerCase();
        result = result.filter(f => {
            const nameMatch = f.name?.toLowerCase().includes(lowerSearch);
            const authorMatch = f.author?.toLowerCase().includes(lowerSearch);
            const descMatch = f.description?.toLowerCase().includes(lowerSearch);
            const catMatch = f.category?.toLowerCase().includes(lowerSearch);
            const pathMatch = f.full_path?.toLowerCase().includes(lowerSearch);
            // Add more fields to search if necessary (e.g., keywords)
             const keywordsMatch = Array.isArray(f.keywords) ? f.keywords.some(k => k.toLowerCase().includes(lowerSearch)) : false;

            return nameMatch || authorMatch || descMatch || catMatch || pathMatch || keywordsMatch;
        });
    }

    // 3. Sort
    result.sort((a, b) => {
        // Mounted first
        if (a.isMounted && !b.isMounted) return -1;
        if (!a.isMounted && b.isMounted) return 1;

        // Secondary sort
        switch (sortOptionFunc.value) {
            case 'name': return (a.name || '').localeCompare(b.name || '');
            case 'author': return (a.author || '').localeCompare(b.author || '');
            case 'category': return (a.category || '').localeCompare(b.category || '');
            default: return 0;
        }
    });

    filteredFunctions.value = result;
    console.timeEnd("FilterSortFunctions");
    isSearchingFunc.value = false;
    console.log(`Filtered/Sorted functions: ${filteredFunctions.value.length}`);
};

const debounceSearchFunc = () => {
    isSearchingFunc.value = true;
    clearTimeout(searchDebounceTimerFunc.value);
    searchDebounceTimerFunc.value = setTimeout(() => {
        currentPageFunc.value = 1;
        pagedFunctions.value = [];
        applyFiltersAndSortFunc();
        loadMoreFunctions();
    }, 300);
};

const loadMoreFunctions = () => {
    if (isLoadingFunctions.value || isSearchingFunc.value) return;

    const start = (currentPageFunc.value - 1) * itemsPerPageFunc.value;
    const end = start + itemsPerPageFunc.value;
    const nextPageItems = filteredFunctions.value.slice(start, end);

    pagedFunctions.value.push(...nextPageItems);
    currentPageFunc.value++;
    nextTick(feather.replace);
};

const updateMountedFuncList = (mountedPathsArray) => {
    const mountedSet = new Set(mountedPathsArray || []);
    mountedFunctions.value = allFunctions.value.filter(f => mountedSet.has(f.full_path));
    // Update isMounted status on the main list
    allFunctions.value.forEach(f => {
        f.isMounted = mountedSet.has(f.full_path);
    });
    // applyFiltersAndSortFunc(); // Re-sort/filter if needed
    console.log("Updated mounted function list:", mountedFunctions.value.length);
};

const setFunctionProcessing = (funcId, state) => {
     const index = allFunctions.value.findIndex(f => (f.id || f.full_path) === funcId);
     if (index !== -1) {
         allFunctions.value[index].isProcessing = state;
         const pagedIndex = pagedFunctions.value.findIndex(f => (f.id || f.full_path) === funcId);
         if (pagedIndex !== -1) pagedFunctions.value[pagedIndex].isProcessing = state;
     }
};


// --- Function Actions ---

const handleMount = async (func) => {
     if (func.isMounted) return;
     const funcId = func.id || func.full_path;
     setFunctionProcessing(funcId, true);
     props.show_toast(`Mounting ${func.name}...`, 3, true);
     try {
         const response = await props.api_post_req('mount_function_call', {
             function_category: func.category,
             function_name: func.name // Assuming 'name' is the identifier within category
         });
         if (response && response.status) {
             props.show_toast(`${func.name} mounted successfully.`, 4, true);
             // Update config
             const newMountedList = [...(props.config.mounted_functions || []), func.full_path];
             emit('update:setting', { key: 'mounted_functions', value: newMountedList });
             // Update local state (watcher will also catch config change)
             const index = allFunctions.value.findIndex(f => (f.id || f.full_path) === funcId);
             if (index !== -1) {
                allFunctions.value[index].isMounted = true;
                allFunctions.value = [...allFunctions.value];
             }
         } else {
             props.show_toast(`Failed to mount ${func.name}: ${response?.error || 'Error'}`, 4, false);
         }
     } catch (error) {
         props.show_toast(`Error mounting ${func.name}: ${error.message}`, 4, false);
     } finally {
         setFunctionProcessing(funcId, false);
     }
};

const handleUnmount = async (func) => {
    if (!func.isMounted) return;
    const funcId = func.id || func.full_path;
    setFunctionProcessing(funcId, true);
     props.show_toast(`Unmounting ${func.name}...`, 3, true);
    try {
        const response = await props.api_post_req('unmount_function_call', {
            function_name: func.name // Assuming backend identifies by name
        });
         if (response && response.status) {
            props.show_toast(`${func.name} unmounted.`, 4, true);
            // Update config
            const newMountedList = (props.config.mounted_functions || []).filter(p => p !== func.full_path);
            emit('update:setting', { key: 'mounted_functions', value: newMountedList });
             // Update local state
             const index = allFunctions.value.findIndex(f => (f.id || f.full_path) === funcId);
             if (index !== -1) {
                 allFunctions.value[index].isMounted = false;
                 allFunctions.value = [...allFunctions.value];
             }
        } else {
            props.show_toast(`Failed to unmount ${func.name}: ${response?.error || 'Error'}`, 4, false);
        }
    } catch (error) {
        props.show_toast(`Error unmounting ${func.name}: ${error.message}`, 4, false);
    } finally {
        setFunctionProcessing(funcId, false);
    }
};

const unmountAll = async () => {
     const yes = await props.show_yes_no_dialog(`Unmount all functions?`, 'Unmount All', 'Cancel');
     if (!yes) return;
     props.show_toast(`Unmounting all functions...`, 3, true);
    try {
        const response = await props.api_post_req('unmount_all_functions');
        if (response && response.status) {
            props.show_toast('All functions unmounted.', 4, true);
            emit('update:setting', { key: 'mounted_functions', value: [] });
            // Update local state
            allFunctions.value.forEach(f => f.isMounted = false);
            allFunctions.value = [...allFunctions.value];
        } else {
             props.show_toast(`Failed to unmount all: ${response?.error || 'Error'}`, 4, false);
        }
    } catch (error) {
        props.show_toast(`Error unmounting all: ${error.message}`, 4, false);
    }
};

const handleRemount = async (func) => {
    const funcId = func.id || func.full_path;
    setFunctionProcessing(funcId, true);
    props.show_toast(`Remounting ${func.name}...`, 3, true);
    try {
        if (func.isMounted) await handleUnmount(func); // Unmount first if mounted
        await handleMount(func); // Then mount
    } catch (e) { /* Errors handled in sub-functions */ }
     finally { setFunctionProcessing(funcId, false); }
};

const handleSettings = async (func) => {
     const funcId = func.id || func.full_path;
     setFunctionProcessing(funcId, true);
    try {
        const settingsData = await props.api_post_req('get_function_call_settings', {
            category: func.category,
            name: func.name
        });
         if (settingsData && Object.keys(settingsData).length > 0) {
            const result = await props.show_universal_form(settingsData, `Function Settings - ${func.name}`, "Save", "Cancel");
            const setResponse = await props.api_post_req('set_function_call_settings', {
                category: func.category,
                name: func.name,
                settings: result
            });
            if (setResponse && setResponse.status) {
                 props.show_toast(`Settings for ${func.name} updated.`, 4, true);
            } else {
                 props.show_toast(`Failed to update settings for ${func.name}: ${setResponse?.error || 'Error'}`, 4, false);
            }
         } else {
             props.show_toast(`Function "${func.name}" has no configurable settings.`, 4, false);
         }
     } catch (error) {
         props.show_toast(`Error accessing settings for ${func.name}: ${error.message}`, 4, false);
     } finally {
         setFunctionProcessing(funcId, false);
     }
};

const handleEdit = async (func) => {
    props.show_toast(`Editing ${func.name} requires opening its folder.`, 3, true);
    await handleOpenFolder(func);
};

const handleCopyToCustom = async (func) => {
     const yes = await props.show_yes_no_dialog(`Copy "${func.name}" to your 'custom_functions' folder?`, 'Copy', 'Cancel');
     if (!yes) return;
     const funcId = func.id || func.full_path;
     setFunctionProcessing(funcId, true);
    try {
        const response = await props.api_post_req('copy_to_custom_functions', { // Endpoint might differ
            category: func.category,
            name: func.name
        });
        if (response && response.status) {
            props.show_message_box(`Function "${func.name}" copied to 'custom_functions'.`);
            await fetchFunctionsAndCategories(); // Refresh list
        } else {
             props.show_toast(`Failed to copy ${func.name}: ${response?.error || 'Already exists?'}`, 4, false);
        }
    } catch (error) {
        props.show_toast(`Error copying ${func.name}: ${error.message}`, 4, false);
    } finally {
        setFunctionProcessing(funcId, false);
    }
};

const handleCopyName = (func) => {
     navigator.clipboard.writeText(func.name)
        .then(() => props.show_toast(`Copied name: ${func.name}`, 3, true))
        .catch(() => props.show_toast("Failed to copy name.", 3, false));
};

const handleOpenFolder = async (func) => {
     try {
        // Assuming backend uses category/name
        await props.api_post_req("open_function_folder", { category: func.category, name: func.name });
     } catch (error) {
        props.show_toast(`Error opening folder for ${func.name}: ${error.message}`, 4, false);
     }
};

const scrollToFunction = (func) => {
    const funcId = func.id || func.full_path;
    const elementRef = functionEntryRefs[funcId];
    if (elementRef && elementRef.$el) {
         elementRef.$el.scrollIntoView({ behavior: 'smooth', block: 'center' });
         // Optional: Add a temporary highlight effect
         elementRef.$el.classList.add('ring-2', 'ring-primary', 'ring-offset-2', 'dark:ring-offset-gray-800', 'transition-all', 'duration-1000');
         setTimeout(() => {
             elementRef.$el.classList.remove('ring-2', 'ring-primary', 'ring-offset-2', 'dark:ring-offset-gray-800', 'transition-all', 'duration-1000');
         }, 1500);
     } else {
        console.warn(`Could not find ref to scroll to for function ID: ${funcId}`);
        // Potentially load more pages until the function is found? Could be complex.
     }
};

// --- Infinite Scroll ---
let observerFunc = null;
const setupIntersectionObserverFunc = () => {
    const options = { root: null, rootMargin: '0px', threshold: 0.1 };
    observerFunc = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting && hasMoreFunctionsToLoad.value && !isLoadingFunctions.value && !isSearchingFunc.value) {
                loadMoreFunctions();
            }
        });
    }, options);
    if (loadMoreTriggerFunc.value) observerFunc.observe(loadMoreTriggerFunc.value);
};

// --- Lifecycle ---
onMounted(() => {
    fetchFunctionsAndCategories();
    nextTick(() => {
        feather.replace();
        if (loadMoreTriggerFunc.value) setupIntersectionObserverFunc();
    });
});

onUnmounted(() => {
    if (observerFunc && loadMoreTriggerFunc.value) observerFunc.unobserve(loadMoreTriggerFunc.value);
    if (observerFunc) observerFunc.disconnect();
    clearTimeout(searchDebounceTimerFunc.value);
});

onUpdated(() => {
    nextTick(() => {
        feather.replace();
        if (!observerFunc && loadMoreTriggerFunc.value) setupIntersectionObserverFunc();
        else if (observerFunc && loadMoreTriggerFunc.value) {
            observerFunc.disconnect();
            observerFunc.observe(loadMoreTriggerFunc.value);
        }
    });
});

</script>

<style scoped>
/* Shared styles */
.input-field {
     @apply block w-full px-3 py-2 text-sm bg-gray-50 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-primary focus:border-primary disabled:opacity-50;
}
.button-base-sm {
     @apply inline-flex items-center justify-center px-2.5 py-1.5 border border-transparent text-xs font-medium rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 transition-colors duration-150;
}
.button-danger-sm { @apply button-base-sm text-white bg-red-600 hover:bg-red-700 focus:ring-red-500; }

/* Add transition group styles if needed */
</style>