<template>
    <div class="space-y-6 p-4 md:p-6 bg-white dark:bg-gray-800 rounded-lg shadow-md border border-gray-200 dark:border-gray-700">
        <!-- Header Section -->
        <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center border-b border-gray-200 dark:border-gray-700 pb-3 mb-4">
            <h2 class="text-xl font-semibold text-gray-800 dark:text-gray-200 mb-2 sm:mb-0">
                Personalities Zoo
            </h2>
            <!-- Mounted Personalities Display -->
            <div class="flex flex-col items-end">
                 <div class="flex items-center flex-wrap gap-2 text-sm font-medium mb-1">
                     <span class="text-gray-600 dark:text-gray-400">Mounted:</span>
                     <div v-if="mountedPersonalities.length === 0" class="text-gray-500 dark:text-gray-500 italic text-xs">None</div>
                    <div v-else class="flex -space-x-3 items-center">
                         <!-- Limited display of mounted icons -->
                         <div v-for="(pers, index) in displayedMountedPersonalities" :key="`mounted-${pers.full_path || index}`" class="relative group">
                            <img :src="getPersonalityIcon(pers.avatar)" @error="imgPlaceholder"
                                class="w-7 h-7 rounded-full object-cover ring-2 ring-white dark:ring-gray-800 cursor-pointer hover:ring-primary transition-all"
                                :class="{ 'ring-primary dark:ring-primary': isActivePersonality(pers) }"
                                :title="`${pers.name} (${pers.category}) ${isActivePersonality(pers) ? '- Active' : ''}`"
                                @click="handleSelect(pers)">
                            <button @click.stop="handleUnmount(pers)"
                                class="absolute -top-1 -right-1 p-0.5 rounded-full bg-red-600 text-white opacity-0 group-hover:opacity-100 transition-opacity duration-150 hover:bg-red-700"
                                title="Unmount">
                                <i data-feather="x" class="w-3 h-3"></i>
                            </button>
                         </div>
                         <div v-if="mountedPersonalities.length > maxDisplayedMounted"
                             class="w-7 h-7 rounded-full bg-gray-200 dark:bg-gray-600 ring-2 ring-white dark:ring-gray-800 flex items-center justify-center text-xs font-semibold text-gray-600 dark:text-gray-300"
                             :title="`${mountedPersonalities.length - maxDisplayedMounted} more mounted`">
                            +{{ mountedPersonalities.length - maxDisplayedMounted }}
                         </div>
                     </div>
                 </div>
                 <button v-if="mountedPersonalities.length > 0" @click="unmountAll" class="button-danger-sm text-xs mt-1">
                     <i data-feather="x-octagon" class="w-3 h-3 mr-1"></i>Unmount All
                </button>
            </div>
        </div>

         <p class="text-sm text-gray-500 dark:text-gray-400">
             Mount personalities to make them available for selection in discussions. The active personality determines the AI's behavior and persona.
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
                    v-model="searchTerm"
                    placeholder="Search personalities..."
                    class="input-field pl-10 w-full"
                    @input="debounceSearch"
                />
                 <div v-if="isSearching" class="absolute inset-y-0 right-0 pr-3 flex items-center">
                    <svg aria-hidden="true" class="w-5 h-5 text-gray-400 animate-spin dark:text-gray-500 fill-primary" viewBox="0 0 100 101" fill="none" xmlns="http://www.w3.org/2000/svg"> <path d="M100 50.5908C100 78.2051 77.6142 100.591 50 100.591C22.3858 100.591 0 78.2051 0 50.5908C0 22.9766 22.3858 0.59082 50 0.59082C77.6142 0.59082 100 22.9766 100 50.5908ZM9.08144 50.5908C9.08144 73.1895 27.4013 91.5094 50 91.5094C72.5987 91.5094 90.9186 73.1895 90.9186 50.5908C90.9186 27.9921 72.5987 9.67226 50 9.67226C27.4013 9.67226 9.08144 27.9921 9.08144 50.5908Z" fill="currentColor"/> <path d="M93.9676 39.0409C96.393 38.4038 97.8624 35.9116 97.0079 33.5539C95.2932 28.8227 92.871 24.3692 89.8167 20.348C85.8452 15.1192 80.8826 10.7238 75.2124 7.41289C69.5422 4.10194 63.2754 1.94025 56.7698 1.05124C51.7666 0.367541 46.6976 0.446843 41.7345 1.27873C39.2613 1.69328 37.813 4.19778 38.4501 6.62326C39.0873 9.04874 41.5694 10.4717 44.0505 10.1071C47.8511 9.54855 51.7191 9.52689 55.5402 10.0491C60.8642 10.7766 65.9928 12.5457 70.6331 15.2552C75.2735 17.9648 79.3347 21.5619 82.5849 25.841C84.9175 28.9121 86.7997 32.2913 88.1811 35.8758C89.083 38.2158 91.5421 39.6781 93.9676 39.0409Z" fill="currentFill"/> </svg>
                 </div>
            </div>
            <!-- Category Filter -->
            <div class="md:col-span-1">
                <label for="pers-category" class="sr-only">Filter by Category</label>
                 <select id="pers-category" v-model="selectedCategory" class="input-field">
                    <option value="">All Categories</option>
                     <option v-for="cat in categories" :key="cat" :value="cat">{{ cat }}</option>
                </select>
            </div>
            <!-- Sort Select -->
            <div class="md:col-span-1">
                 <label for="pers-sort" class="sr-only">Sort personalities by</label>
                 <select id="pers-sort" v-model="sortOption" class="input-field">
                    <option value="name">Sort by Name</option>
                    <option value="author">Sort by Author</option>
                     <option value="category">Sort by Category</option>
                    <!-- Add more options: popularity, date added? -->
                 </select>
             </div>
        </div>

         <!-- Loading / Empty State -->
         <div v-if="isLoadingPersonalities" class="flex justify-center items-center p-10 text-gray-500 dark:text-gray-400">
            <svg aria-hidden="true" class="w-8 h-8 mr-2 text-gray-300 animate-spin dark:text-gray-600 fill-primary" viewBox="0 0 100 101" fill="none" xmlns="http://www.w3.org/2000/svg"> <path d="M100 50.5908C100 78.2051 77.6142 100.591 50 100.591C22.3858 100.591 0 78.2051 0 50.5908C0 22.9766 22.3858 0.59082 50 0.59082C77.6142 0.59082 100 22.9766 100 50.5908ZM9.08144 50.5908C9.08144 73.1895 27.4013 91.5094 50 91.5094C72.5987 91.5094 90.9186 73.1895 90.9186 50.5908C90.9186 27.9921 72.5987 9.67226 50 9.67226C27.4013 9.67226 9.08144 27.9921 9.08144 50.5908Z" fill="currentColor"/> <path d="M93.9676 39.0409C96.393 38.4038 97.8624 35.9116 97.0079 33.5539C95.2932 28.8227 92.871 24.3692 89.8167 20.348C85.8452 15.1192 80.8826 10.7238 75.2124 7.41289C69.5422 4.10194 63.2754 1.94025 56.7698 1.05124C51.7666 0.367541 46.6976 0.446843 41.7345 1.27873C39.2613 1.69328 37.813 4.19778 38.4501 6.62326C39.0873 9.04874 41.5694 10.4717 44.0505 10.1071C47.8511 9.54855 51.7191 9.52689 55.5402 10.0491C60.8642 10.7766 65.9928 12.5457 70.6331 15.2552C75.2735 17.9648 79.3347 21.5619 82.5849 25.841C84.9175 28.9121 86.7997 32.2913 88.1811 35.8758C89.083 38.2158 91.5421 39.6781 93.9676 39.0409Z" fill="currentFill"/> </svg>
             <span>Loading personalities...</span>
        </div>
         <div v-else-if="pagedPersonalities.length === 0" class="text-center text-gray-500 dark:text-gray-400 py-10">
             No personalities found{{ searchTerm ? ' matching "' + searchTerm + '"' : '' }}{{ selectedCategory ? ' in category "' + selectedCategory + '"' : '' }}.
        </div>

        <!-- Personalities Grid - Lazy Loaded -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4" ref="scrollContainerPers">
             <PersonalityEntry
                v-for="pers in pagedPersonalities"
                :key="pers.id || pers.full_path"
                :personality="pers"
                :is-mounted="pers.isMounted"
                :is-active="isActivePersonality(pers)"
                :select_language="true"
                @select="handleSelect(pers)"
                @mount="handleMount(pers)"
                @unmount="handleUnmount(pers)"
                @remount="handleRemount(pers)"
                @edit="handleEdit(pers)"
                @copy-to-custom="handleCopyToCustom(pers)"
                @reinstall="handleReinstall(pers)"
                @settings="handleSettings(pers)"
                 @copy-personality-name="handleCopyName(pers)"
                 @open-folder="handleOpenFolder(pers)"
            />
        </div>

        <!-- Loading More Indicator / Trigger -->
        <div ref="loadMoreTriggerPers" class="h-10">
            <div v-if="hasMorePersonalitiesToLoad && !isLoadingPersonalities" class="text-center text-gray-500 dark:text-gray-400 py-4">
                Loading more personalities...
            </div>
        </div>

    </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick, onUpdated } from 'vue';
import feather from 'feather-icons';
import PersonalityEntry from '@/components/PersonalityEntry.vue'; // Assuming this component exists
import defaultPersonalityIcon from "@/assets/logo.png"; // Default icon for personalities

const axios = require('axios'); // If needed directly, though api_post_req is preferred

// Props
const props = defineProps({
    config: { type: Object, required: true },
    api_post_req: { type: Function, required: true },
    api_get_req: { type: Function, required: true },
    show_toast: { type: Function, required: true },
    show_yes_no_dialog: { type: Function, required: true },
    show_message_box: { type: Function, required: true }, // Added for copy to custom message
    client_id: { type: String, required: true },
    refresh_config: { type: Function, required: true }, // Function to trigger parent config refresh
});

// Emits
const emit = defineEmits(['update:setting']);

// --- State ---
const allPersonalities = ref([]); // Holds the full list [{...personalityData, full_path: string, isMounted: boolean, id: string, isProcessing: boolean}]
const categories = ref([]); // List of unique category names
const filteredPersonalities = ref([]);
const pagedPersonalities = ref([]);
const mountedPersonalities = ref([]); // Derived from config for display

const isLoadingPersonalities = ref(false);
const isSearching = ref(false);
const searchTerm = ref('');
const selectedCategory = ref(''); // Holds the selected category filter
const sortOption = ref('name'); // 'name', 'author', 'category'

const itemsPerPagePers = ref(15);
const currentPagePers = ref(1);
const searchDebounceTimerPers = ref(null);

const scrollContainerPers = ref(null);
const loadMoreTriggerPers = ref(null);
const maxDisplayedMounted = ref(5); // Max mounted icons to show before '+N'

// --- Computed ---
const hasMorePersonalitiesToLoad = computed(() => {
    return pagedPersonalities.value.length < filteredPersonalities.value.length;
});

const displayedMountedPersonalities = computed(() => {
    // Slice the array for display limit
    return mountedPersonalities.value.slice(0, maxDisplayedMounted.value);
});


// --- Watchers ---
watch(() => props.config.personalities, (newVal) => {
    updateMountedList(newVal);
}, { immediate: true, deep: true });

watch([searchTerm, selectedCategory, sortOption], () => {
    debounceSearch(); // Use debounce for all filter/sort changes
});

// Watch the master list changing
watch(allPersonalities, () => {
    currentPagePers.value = 1;
    pagedPersonalities.value = [];
    applyFiltersAndSortPers();
    loadMorePersonalities();
}, { deep: true });

// --- Methods ---

const getPersonalityIcon = (avatarPath) => {
    if (!avatarPath) return defaultPersonalityIcon;
    // Assuming avatarPath is relative like 'personalities/category/name/assets/logo.png'
    // Adjust baseURL as needed if it doesn't include the leading slash
    return `${axios.defaults.baseURL}${avatarPath.startsWith('/') ? '' : '/'}${avatarPath}`;
};

const imgPlaceholder = (event) => {
    event.target.src = defaultPersonalityIcon;
};

const fetchPersonalitiesAndCategories = async () => {
    isLoadingPersonalities.value = true;
    console.log("Fetching personalities and categories...");
    try {
        const [cats, allPersDict] = await Promise.all([
            props.api_get_req("list_personalities_categories"),
            props.api_get_req("get_all_personalities") // Assumes this returns { category: [persObj1, persObj2] }
        ]);

        categories.value = cats || [];
        categories.value.sort(); // Sort categories alphabetically

        let combined = [];
        const mountedSet = new Set(props.config.personalities || []); // Set of mounted "category/folder" strings

        if (allPersDict) {
            for (const category in allPersDict) {
                const personalitiesInCategory = allPersDict[category];
                if (Array.isArray(personalitiesInCategory)) {
                    personalitiesInCategory.forEach(pers => {
                        const full_path = `${category}/${pers.folder}`;
                        // Determine unique ID - prefer pers.id, fallback to full_path
                        const uniqueId = pers.id || full_path;
                        combined.push({
                            ...pers,
                            category: category, // Ensure category is stored
                            full_path: full_path,
                            isMounted: mountedSet.has(full_path),
                            id: uniqueId,
                            isProcessing: false // For mount/unmount spinners
                        });
                    });
                }
            }
        }

        allPersonalities.value = combined;
        console.log(`Fetched ${allPersonalities.value.length} total personalities.`);
        updateMountedList(props.config.personalities); // Ensure mounted list is synced initially

    } catch (error) {
        props.show_toast("Failed to load personalities.", 4, false);
        console.error("Error fetching personalities:", error);
        allPersonalities.value = [];
        categories.value = [];
    } finally {
        isLoadingPersonalities.value = false;
        nextTick(feather.replace);
    }
};

const applyFiltersAndSortPers = () => {
    isSearching.value = true;
    console.time("FilterSortPersonalities");

    let result = [...allPersonalities.value];

    // 1. Filter by Category
    if (selectedCategory.value) {
        result = result.filter(p => p.category === selectedCategory.value);
    }

    // 2. Filter by Search Term
    if (searchTerm.value) {
        const lowerSearch = searchTerm.value.toLowerCase();
        result = result.filter(p =>
            p.name?.toLowerCase().includes(lowerSearch) ||
            p.author?.toLowerCase().includes(lowerSearch) ||
            p.description?.toLowerCase().includes(lowerSearch) ||
            p.category?.toLowerCase().includes(lowerSearch) ||
            p.folder?.toLowerCase().includes(lowerSearch)
        );
    }

    // 3. Sort
    result.sort((a, b) => {
        // Always put mounted personalities first
        if (a.isMounted && !b.isMounted) return -1;
        if (!a.isMounted && b.isMounted) return 1;

        // Then apply the selected sort option
        switch (sortOption.value) {
            case 'name':
                return (a.name || '').localeCompare(b.name || '');
            case 'author':
                return (a.author || '').localeCompare(b.author || '');
            case 'category':
                return (a.category || '').localeCompare(b.category || '');
            default:
                return 0;
        }
    });

    filteredPersonalities.value = result;
    console.timeEnd("FilterSortPersonalities");
    isSearching.value = false;
    console.log(`Filtered/Sorted personalities: ${filteredPersonalities.value.length}`);
};

const debounceSearch = () => {
    isSearching.value = true;
    clearTimeout(searchDebounceTimerPers.value);
    searchDebounceTimerPers.value = setTimeout(() => {
        currentPagePers.value = 1;
        pagedPersonalities.value = [];
        applyFiltersAndSortPers();
        loadMorePersonalities();
    }, 300); // Shorter delay might be ok for personalities
};

const loadMorePersonalities = () => {
    if (isLoadingPersonalities.value || isSearching.value) return;

    const start = (currentPagePers.value - 1) * itemsPerPagePers.value;
    const end = start + itemsPerPagePers.value;
    const nextPageItems = filteredPersonalities.value.slice(start, end);

    pagedPersonalities.value.push(...nextPageItems);
    currentPagePers.value++;
    nextTick(feather.replace);
};

const updateMountedList = (mountedPathsArray) => {
    const mountedSet = new Set(mountedPathsArray || []);
    mountedPersonalities.value = allPersonalities.value.filter(p => mountedSet.has(p.full_path));
     // Also update the isMounted flag on the main list for consistency in the grid display
     allPersonalities.value.forEach(p => {
         p.isMounted = mountedSet.has(p.full_path);
     });
     // Trigger re-sort/filter if needed (e.g., if sort depends on mounted status)
     // applyFiltersAndSortPers(); // This might cause loops if not careful, maybe trigger selectively
     console.log("Updated mounted list:", mountedPersonalities.value.length);
};

const isActivePersonality = (pers) => {
     // The active personality is identified by its index in the config's personalities array
     const activeIndex = props.config.active_personality_id;
     if (activeIndex === undefined || activeIndex < 0 || !props.config.personalities) {
         return false;
     }
     // Check if the personality's full_path matches the one at the active index
     return props.config.personalities[activeIndex] === pers.full_path;
};


const setPersonalityProcessing = (persId, state) => {
     const index = allPersonalities.value.findIndex(p => (p.id || p.full_path) === persId);
     if (index !== -1) {
         allPersonalities.value[index].isProcessing = state;
         // Update paged list as well
         const pagedIndex = pagedPersonalities.value.findIndex(p => (p.id || p.full_path) === persId);
         if (pagedIndex !== -1) {
             pagedPersonalities.value[pagedIndex].isProcessing = state;
         }
     }
};

// --- Personality Actions ---

const handleSelect = async (pers) => {
     if (!pers.isMounted) {
         props.show_toast(`Personality "${pers.name}" is not mounted. Mount it first.`, 3, false);
         return;
     }
     const persId = pers.id || pers.full_path;
     setPersonalityProcessing(persId, true);
     props.show_toast(`Selecting ${pers.name}...`, 2, true);

     // Find the index of this personality in the *config's* mounted list
     const indexInConfig = (props.config.personalities || []).findIndex(p => p === pers.full_path);

     if (indexInConfig === -1) {
         props.show_toast(`Error: ${pers.name} is marked as mounted but not found in config list.`, 4, false);
         setPersonalityProcessing(persId, false);
         return;
     }

     try {
        const response = await props.api_post_req('select_personality', { id: indexInConfig });
        if (response && response.status) {
             props.show_toast(`Selected personality: ${pers.name}`, 4, true);
             // Parent config should update via its refresh mechanism or direct emit
             emit('update:setting', { key: 'active_personality_id', value: indexInConfig });
             // We might need to refresh the whole config to be safe if backend changes other things
             // await props.refresh_config();
        } else {
            props.show_toast(`Failed to select ${pers.name}: ${response?.error || 'Unknown error'}`, 4, false);
        }
     } catch (error) {
        props.show_toast(`Error selecting ${pers.name}: ${error.message}`, 4, false);
     } finally {
         setPersonalityProcessing(persId, false);
         // Manually trigger reactivity for the isActive computed property if needed
         // This might require forcing an update if props.config change isn't detected quickly enough
         // Example: allPersonalities.value = [...allPersonalities.value];
     }
};

const handleMount = async (pers) => {
    if (pers.isMounted) {
        props.show_toast(`${pers.name} is already mounted.`, 3, false);
        return;
    }
     if (pers.disclaimer) {
        const yes = await props.show_yes_no_dialog(`Disclaimer for ${pers.name}:\n\n${pers.disclaimer}\n\nMount this personality?`, 'Mount', 'Cancel');
        if (!yes) return;
    }

    const persId = pers.id || pers.full_path;
    setPersonalityProcessing(persId, true);
    props.show_toast(`Mounting ${pers.name}...`, 3, true);

    try {
        // Request to mount
        const mountResponse = await props.api_post_req('mount_personality', {
            category: pers.category,
            folder: pers.folder,
            language: pers.language // Include if relevant
        });

        if (mountResponse && mountResponse.status) {
             props.show_toast(`${pers.name} mounted successfully.`, 4, true);
             // Update local state & config
             const newMountedList = [...(props.config.personalities || []), pers.full_path];
            emit('update:setting', { key: 'personalities', value: newMountedList });
            // Mark as mounted in the main list
            const index = allPersonalities.value.findIndex(p => (p.id || p.full_path) === persId);
            if (index !== -1) {
                 allPersonalities.value[index].isMounted = true;
                allPersonalities.value = [...allPersonalities.value]; // Trigger reactivity
            }
             // Optionally select it immediately after mounting
             // Need the new index from the updated config list
            const newIndexInConfig = newMountedList.length - 1; // It's the last one added
            emit('update:setting', { key: 'active_personality_id', value: newIndexInConfig });


        } else {
            props.show_toast(`Failed to mount ${pers.name}: ${mountResponse?.error || 'Unknown error'}`, 4, false);
        }
    } catch (error) {
        props.show_toast(`Error mounting ${pers.name}: ${error.message}`, 4, false);
    } finally {
        setPersonalityProcessing(persId, false);
    }
};

const handleUnmount = async (pers) => {
     if (!pers.isMounted) return;
     const yes = await props.show_yes_no_dialog(`Unmount personality "${pers.name}"?`, 'Unmount', 'Cancel');
     if (!yes) return;

     const persId = pers.id || pers.full_path;
     setPersonalityProcessing(persId, true);
     props.show_toast(`Unmounting ${pers.name}...`, 3, true);

     try {
        const response = await props.api_post_req('unmount_personality', {
            category: pers.category,
            folder: pers.folder,
            language: pers.language
        });
        if (response && response.status) {
             props.show_toast(`${pers.name} unmounted.`, 4, true);
             // Update local state & config
            const currentMountedList = (props.config.personalities || []);
            const newMountedList = currentMountedList.filter(p => p !== pers.full_path);
            emit('update:setting', { key: 'personalities', value: newMountedList });

             // If the unmounted one was active, select the last remaining one or none
             if (isActivePersonality(pers)) {
                 const newActiveId = newMountedList.length > 0 ? newMountedList.length - 1 : -1;
                 emit('update:setting', { key: 'active_personality_id', value: newActiveId });
             } else {
                 // Adjust active_personality_id if items before it were removed (more complex)
                 // A full config refresh might be safer here, or recalculate index based on new list.
                 // For simplicity, let's assume parent handles index adjustment or user re-selects.
             }

             // Mark as unmounted in the main list
             const index = allPersonalities.value.findIndex(p => (p.id || p.full_path) === persId);
             if (index !== -1) {
                 allPersonalities.value[index].isMounted = false;
                 allPersonalities.value = [...allPersonalities.value]; // Trigger reactivity
             }

        } else {
            props.show_toast(`Failed to unmount ${pers.name}: ${response?.error || 'Unknown error'}`, 4, false);
        }
     } catch (error) {
        props.show_toast(`Error unmounting ${pers.name}: ${error.message}`, 4, false);
     } finally {
        setPersonalityProcessing(persId, false);
     }
};

const unmountAll = async () => {
     const yes = await props.show_yes_no_dialog(`Unmount all personalities?`, 'Unmount All', 'Cancel');
     if (!yes) return;

     props.show_toast(`Unmounting all...`, 3, true);
     try {
         const response = await props.api_post_req('unmount_all_personalities');
         if (response && response.status) {
             props.show_toast(`All personalities unmounted.`, 4, true);
             emit('update:setting', { key: 'personalities', value: [] });
             emit('update:setting', { key: 'active_personality_id', value: -1 });
             // Update local state
            allPersonalities.value.forEach(p => p.isMounted = false);
            allPersonalities.value = [...allPersonalities.value];
         } else {
             props.show_toast(`Failed to unmount all: ${response?.error || 'Unknown error'}`, 4, false);
         }
     } catch (error) {
         props.show_toast(`Error unmounting all: ${error.message}`, 4, false);
     }
};


const handleRemount = async (pers) => {
     const persId = pers.id || pers.full_path;
     setPersonalityProcessing(persId, true);
     props.show_toast(`Remounting ${pers.name}...`, 3, true);
    // Simplified: Call unmount then mount logic
    try {
        await handleUnmount(pers); // Attempt unmount first
        await handleMount(pers); // Then attempt mount
    } catch(e){/* Errors handled in sub-functions */}
    finally {
        setPersonalityProcessing(persId, false); // Ensure processing is reset
    }

};

const handleEdit = async (pers) => {
     props.show_toast(`Editing ${pers.name} requires opening its folder. Opening now...`, 4, true);
     await handleOpenFolder(pers); // Use the existing open folder logic
     // Consider navigating to a dedicated editor view if one exists in the future
     // Or opening a specific file (e.g., config.yaml) if the backend supports it
};

const handleCopyToCustom = async (pers) => {
     const yes = await props.show_yes_no_dialog(`Copy "${pers.name}" from "${pers.category}" to your 'custom_personalities' folder?`, 'Copy', 'Cancel');
     if (!yes) return;

     const persId = pers.id || pers.full_path;
     setPersonalityProcessing(persId, true);
     try {
        const response = await props.api_post_req('copy_to_custom_personas', {
             category: pers.category,
             name: pers.folder // Assuming 'name' in API maps to 'folder' from personality object
         });
        if (response && response.status) {
             props.show_message_box( // Use message box for longer text
                 `Personality "${pers.name}" copied to 'custom_personalities'.\nYou can now find and edit it under the 'custom_personalities' category.`
            );
             await fetchPersonalitiesAndCategories(); // Refresh list to show the new copy
         } else {
             props.show_toast(`Failed to copy ${pers.name}: ${response?.error || 'Already exists?'}`, 4, false);
         }
     } catch (error) {
         props.show_toast(`Error copying ${pers.name}: ${error.message}`, 4, false);
     } finally {
        setPersonalityProcessing(persId, false);
     }
};

const handleReinstall = async (pers) => {
    const yes = await props.show_yes_no_dialog(`Reinstall "${pers.name}" from its source?\nThis will overwrite any local changes.`, 'Reinstall', 'Cancel');
    if (!yes) return;

     const persId = pers.id || pers.full_path;
     setPersonalityProcessing(persId, true);
     props.show_toast(`Reinstalling ${pers.name}...`, 3, true);

     try {
         // Assuming backend uses the full path or category/name combo
         const response = await props.api_post_req('reinstall_personality', { name: pers.full_path });
        if (response && response.status) {
             props.show_toast(`${pers.name} reinstalled successfully.`, 4, true);
             // Might need to refresh config or specific personality data if content changed
         } else {
             props.show_toast(`Failed to reinstall ${pers.name}: ${response?.error || 'Not found?'}`, 4, false);
         }
     } catch (error) {
         props.show_toast(`Error reinstalling ${pers.name}: ${error.message}`, 4, false);
     } finally {
         setPersonalityProcessing(persId, false);
     }
};

const handleSettings = async (pers) => {
    // Similar to binding settings, usually fetches settings for the *active* personality
    const activePersPath = props.config.personalities ? props.config.personalities[props.config.active_personality_id] : null;
     if (!activePersPath || activePersPath !== pers.full_path) {
        props.show_toast(`Select "${pers.name}" first to configure its active settings.`, 4, false);
        return; // Or implement fetching settings by path if backend supports it
    }

    const persId = pers.id || pers.full_path;
    setPersonalityProcessing(persId, true);
     try {
         const settingsData = await props.api_get_req('get_active_personality_settings'); // Endpoint fetches for the active one
         if (settingsData && Object.keys(settingsData).length > 0) {
             const result = await props.show_universal_form(settingsData, `Personality Settings - ${pers.name}`, "Save", "Cancel");
            // If form submitted
            const setResponse = await props.api_post_req('set_active_personality_settings', { settings: result });
            if (setResponse && setResponse.status) {
                 props.show_toast(`Settings for ${pers.name} updated.`, 4, true);
                 // Changes applied automatically if backend modifies the active personality's config in memory.
                 // May need a remount/reload if changes require it.
             } else {
                props.show_toast(`Failed to update settings for ${pers.name}: ${setResponse?.error || 'Unknown error'}`, 4, false);
             }
         } else {
            props.show_toast(`Personality "${pers.name}" has no configurable settings.`, 4, false);
        }
     } catch (error) {
        props.show_toast(`Error accessing settings for ${pers.name}: ${error.message}`, 4, false);
     } finally {
        setPersonalityProcessing(persId, false);
     }
};

const handleCopyName = (pers) => {
     navigator.clipboard.writeText(pers.name)
        .then(() => props.show_toast(`Copied name: ${pers.name}`, 3, true))
        .catch(() => props.show_toast("Failed to copy name.", 3, false));
};

const handleOpenFolder = async (pers) => {
     try {
        await props.api_post_req("open_personality_folder", { category: pers.category, name: pers.folder });
        // No toast needed, action happens on backend/OS
     } catch (error) {
        props.show_toast(`Error opening folder for ${pers.name}: ${error.message}`, 4, false);
     }
};

// --- Infinite Scroll ---
let observerPers = null;
const setupIntersectionObserverPers = () => {
     const options = { root: null, rootMargin: '0px', threshold: 0.1 };
     observerPers = new IntersectionObserver((entries) => {
         entries.forEach(entry => {
             if (entry.isIntersecting && hasMorePersonalitiesToLoad.value && !isLoadingPersonalities.value && !isSearching.value) {
                 loadMorePersonalities();
             }
         });
     }, options);
     if (loadMoreTriggerPers.value) observerPers.observe(loadMoreTriggerPers.value);
};

// --- Lifecycle Hooks ---
onMounted(() => {
    fetchPersonalitiesAndCategories();
    nextTick(() => {
        feather.replace();
         if (loadMoreTriggerPers.value) setupIntersectionObserverPers();
    });
});

onUnmounted(() => {
     if (observerPers && loadMoreTriggerPers.value) observerPers.unobserve(loadMoreTriggerPers.value);
     if (observerPers) observerPers.disconnect();
     clearTimeout(searchDebounceTimerPers.value);
});

onUpdated(() => {
    nextTick(() => {
        feather.replace();
        if (!observerPers && loadMoreTriggerPers.value) setupIntersectionObserverPers();
        else if (observerPers && loadMoreTriggerPers.value) { // Re-observe if trigger element changed
            observerPers.disconnect();
            observerPers.observe(loadMoreTriggerPers.value);
        }
    });
});

</script>

<style scoped>
/* Using shared styles */
.input-field {
     @apply block w-full px-3 py-2 text-sm bg-gray-50 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-primary focus:border-primary disabled:opacity-50;
}
.button-base-sm {
     @apply inline-flex items-center justify-center px-2.5 py-1.5 border border-transparent text-xs font-medium rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 transition-colors duration-150;
}
.button-danger-sm { @apply button-base-sm text-white bg-red-600 hover:bg-red-700 focus:ring-red-500; }

/* Add transition group styles if needed */
.pers-grid-enter-active,
.pers-grid-leave-active {
  transition: all 0.5s ease;
}
.pers-grid-enter-from,
.pers-grid-leave-to {
  opacity: 0;
  transform: translateY(15px);
}
/* .pers-grid-leave-active { position: absolute; } */ /* Be careful with absolute positioning */
</style>