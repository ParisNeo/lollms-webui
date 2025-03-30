<template>
    <div class="space-y-6 p-4 md:p-6 bg-white dark:bg-gray-800 rounded-lg shadow-md border border-gray-200 dark:border-gray-700">
        <!-- Header Section -->
        <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center border-b border-gray-200 dark:border-gray-700 pb-3 mb-4">
            <h2 class="text-xl font-semibold text-gray-800 dark:text-gray-200 mb-2 sm:mb-0">
                Models Zoo
            </h2>
            <!-- Current Model Display -->
             <div v-if="currentModelInfo" class="flex items-center gap-2 text-sm font-medium p-2 bg-primary-light dark:bg-primary-dark/20 rounded-md border border-primary-dark/30 shrink-0">
                 <img :src="currentModelInfo.icon" @error="imgPlaceholder" class="w-6 h-6 rounded-lg object-cover flex-shrink-0" alt="Current Model Icon">
                 <span>Active: <span class="font-semibold">{{ currentModelInfo.name }}</span></span>
                 <!-- Add settings/info button if applicable to models -->
            </div>
            <div v-else-if="!config.binding_name" class="text-sm font-medium text-orange-600 dark:text-orange-400 p-2 bg-orange-50 dark:bg-orange-900/20 rounded-md border border-orange-300 dark:border-orange-600 shrink-0">
                 Select a Binding first!
             </div>
            <div v-else class="text-sm font-medium text-red-600 dark:text-red-400 p-2 bg-red-50 dark:bg-red-900/20 rounded-md border border-red-300 dark:border-red-600 shrink-0">
                No model selected!
            </div>
        </div>

        <!-- Info and Warnings -->
        <p class="text-sm text-gray-500 dark:text-gray-400">
            Select a model compatible with your chosen binding (<span class="font-semibold">{{ currentBindingName || 'None Selected' }}</span>). Installed models are shown first.
        </p>
         <div v-if="!config.binding_name" class="p-3 text-center text-orange-600 dark:text-orange-400 bg-orange-50 dark:bg-orange-900/30 rounded-md border border-orange-200 dark:border-orange-700">
            Please select a Binding from the 'Bindings' section to see available models.
        </div>

        <!-- Controls: Search, Filters, Sort -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4 items-center">
            <!-- Search Input -->
            <div class="relative md:col-span-2">
                 <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                     <i data-feather="search" class="w-5 h-5 text-gray-400"></i>
                </div>
                 <input
                    type="search"
                    v-model="searchTerm"
                    placeholder="Search models by name, author, quantizer, description..."
                    class="input-field pl-10 w-full"
                    @input="debounceSearch"
                />
                 <div v-if="isSearching" class="absolute inset-y-0 right-0 pr-3 flex items-center">
                     <svg aria-hidden="true" class="w-5 h-5 text-gray-400 animate-spin dark:text-gray-500 fill-primary" viewBox="0 0 100 101" fill="none" xmlns="http://www.w3.org/2000/svg"> <path d="M100 50.5908C100 78.2051 77.6142 100.591 50 100.591C22.3858 100.591 0 78.2051 0 50.5908C0 22.9766 22.3858 0.59082 50 0.59082C77.6142 0.59082 100 22.9766 100 50.5908ZM9.08144 50.5908C9.08144 73.1895 27.4013 91.5094 50 91.5094C72.5987 91.5094 90.9186 73.1895 90.9186 50.5908C90.9186 27.9921 72.5987 9.67226 50 9.67226C27.4013 9.67226 9.08144 27.9921 9.08144 50.5908Z" fill="currentColor"/> <path d="M93.9676 39.0409C96.393 38.4038 97.8624 35.9116 97.0079 33.5539C95.2932 28.8227 92.871 24.3692 89.8167 20.348C85.8452 15.1192 80.8826 10.7238 75.2124 7.41289C69.5422 4.10194 63.2754 1.94025 56.7698 1.05124C51.7666 0.367541 46.6976 0.446843 41.7345 1.27873C39.2613 1.69328 37.813 4.19778 38.4501 6.62326C39.0873 9.04874 41.5694 10.4717 44.0505 10.1071C47.8511 9.54855 51.7191 9.52689 55.5402 10.0491C60.8642 10.7766 65.9928 12.5457 70.6331 15.2552C75.2735 17.9648 79.3347 21.5619 82.5849 25.841C84.9175 28.9121 86.7997 32.2913 88.1811 35.8758C89.083 38.2158 91.5421 39.6781 93.9676 39.0409Z" fill="currentFill"/> </svg>
                 </div>
            </div>
            <!-- Filters -->
            <div class="flex items-center space-x-2">
                 <label for="model-filter-installed" class="flex items-center space-x-1 cursor-pointer text-sm">
                    <input type="checkbox" id="model-filter-installed" v-model="showInstalledOnly" class="rounded text-primary focus:ring-primary-dark border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:focus:ring-offset-gray-800">
                     <span>Installed</span>
                 </label>
                 <!-- Add more filters if needed (e.g., by type, size) -->
            </div>
             <!-- Sort Select -->
            <div>
                 <label for="model-sort" class="sr-only">Sort models by</label>
                 <select id="model-sort" v-model="sortOption" class="input-field">
                     <option value="rank">Sort by Rank</option>
                     <option value="name">Sort by Name</option>
                     <option value="last_commit_time">Sort by Date</option>
                     <option value="quantizer">Sort by Quantizer</option>
                     <option value="license">Sort by License</option>
                 </select>
            </div>
        </div>

        <!-- Loading / Empty State -->
        <div v-if="isLoadingModels" class="flex justify-center items-center p-10 text-gray-500 dark:text-gray-400">
             <svg aria-hidden="true" class="w-8 h-8 mr-2 text-gray-300 animate-spin dark:text-gray-600 fill-primary" viewBox="0 0 100 101" fill="none" xmlns="http://www.w3.org/2000/svg"> <path d="M100 50.5908C100 78.2051 77.6142 100.591 50 100.591C22.3858 100.591 0 78.2051 0 50.5908C0 22.9766 22.3858 0.59082 50 0.59082C77.6142 0.59082 100 22.9766 100 50.5908ZM9.08144 50.5908C9.08144 73.1895 27.4013 91.5094 50 91.5094C72.5987 91.5094 90.9186 73.1895 90.9186 50.5908C90.9186 27.9921 72.5987 9.67226 50 9.67226C27.4013 9.67226 9.08144 27.9921 9.08144 50.5908Z" fill="currentColor"/> <path d="M93.9676 39.0409C96.393 38.4038 97.8624 35.9116 97.0079 33.5539C95.2932 28.8227 92.871 24.3692 89.8167 20.348C85.8452 15.1192 80.8826 10.7238 75.2124 7.41289C69.5422 4.10194 63.2754 1.94025 56.7698 1.05124C51.7666 0.367541 46.6976 0.446843 41.7345 1.27873C39.2613 1.69328 37.813 4.19778 38.4501 6.62326C39.0873 9.04874 41.5694 10.4717 44.0505 10.1071C47.8511 9.54855 51.7191 9.52689 55.5402 10.0491C60.8642 10.7766 65.9928 12.5457 70.6331 15.2552C75.2735 17.9648 79.3347 21.5619 82.5849 25.841C84.9175 28.9121 86.7997 32.2913 88.1811 35.8758C89.083 38.2158 91.5421 39.6781 93.9676 39.0409Z" fill="currentFill"/> </svg>
             <span>Loading models...</span>
        </div>
        <div v-else-if="pagedModels.length === 0 && models.length > 0" class="text-center text-gray-500 dark:text-gray-400 py-10">
             No models found matching filters{{ searchTerm ? ' and search "' + searchTerm + '"' : '' }}.
        </div>
        <div v-else-if="models.length === 0 && !isLoadingModels && config.binding_name" class="text-center text-gray-500 dark:text-gray-400 py-10">
             No models available for the selected binding. Try adding a reference below.
        </div>


        <!-- Models Grid - Lazy Loaded -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4" ref="scrollContainer">
             <ModelEntry
                 v-for="model in pagedModels"
                :key="model.id || model.name"
                :model="model"
                :is-selected="config.model_name === model.name"
                @select="handleSelect(model)"
                @install="handleInstall"
                 @uninstall="handleUninstall"
                 @cancel-install="handleCancelInstall"
                 @copy="handleCopy"
                @copy-link="handleCopyLink"
             />
        </div>

        <!-- Loading More Indicator / Trigger -->
        <div ref="loadMoreTrigger" class="h-10">
            <div v-if="hasMoreModelsToLoad && !isLoadingModels" class="text-center text-gray-500 dark:text-gray-400 py-4">
                Loading more models...
            </div>
        </div>


        <!-- Add Model / Reference Section -->
         <section class="pt-6 border-t border-gray-200 dark:border-gray-700 mt-6">
             <h3 class="text-lg font-medium text-gray-700 dark:text-gray-300 mb-3">Add Model</h3>
             <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                 <!-- Add Reference Path -->
                 <div>
                     <label for="reference_path" class="setting-label-inline">Add Reference to Local Model File/Folder</label>
                     <div class="flex">
                         <input type="text" id="reference_path" v-model="referencePath" class="input-field-sm rounded-r-none flex-grow" placeholder="Enter full path to model file or folder...">
                         <button @click="createReference" class="button-primary-sm rounded-l-none flex-shrink-0" title="Add Reference">Add</button>
                     </div>
                     <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">Creates a link without copying the model. Requires binding support.</p>
                 </div>
                 <!-- Download from URL / Hugging Face -->
                 <div>
                     <label for="model_url" class="setting-label-inline">Download Model from URL or Hugging Face ID</label>
                     <div class="flex">
                        <input type="text" id="model_url" v-model="modelUrl" class="input-field-sm rounded-r-none flex-grow" placeholder="Enter URL or HF ID (e.g., TheBloke/Llama-2-7B-GGUF)...">
                        <button @click="installFromInput" class="button-success-sm rounded-l-none flex-shrink-0" title="Download and Install" :disabled="isDownloading">
                             <i :data-feather="isDownloading ? 'loader' : 'download'" :class="['w-4 h-4', isDownloading ? 'animate-spin' : '']"></i>
                         </button>
                     </div>
                    <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">Downloads the model to the binding's models folder.</p>
                 </div>
             </div>
              <!-- Download Progress (Conditional) -->
             <div v-if="downloadProgress.visible" class="mt-4 p-3 bg-blue-50 dark:bg-blue-900/30 border border-blue-200 dark:border-blue-700 rounded-md">
                 <div class="flex justify-between items-center mb-1">
                     <span class="text-sm font-medium text-blue-700 dark:text-blue-300">Downloading: {{ downloadProgress.name }}</span>
                     <span class="text-xs font-medium text-blue-600 dark:text-blue-400">{{ downloadProgress.progress.toFixed(1) }}%</span>
                 </div>
                 <div class="w-full bg-blue-200 rounded-full h-1.5 dark:bg-blue-700">
                     <div class="bg-blue-600 h-1.5 rounded-full" :style="{ width: downloadProgress.progress + '%' }"></div>
                 </div>
                 <div class="flex justify-between items-center mt-1 text-xs text-blue-600 dark:text-blue-400">
                     <span>{{ downloadedSizeComputed }} / {{ totalSizeComputed }}</span>
                     <span>{{ speedComputed }}/s</span>
                 </div>
                 <button @click="handleCancelInstall(downloadProgress.details)" class="button-danger-sm mt-2 text-xs">Cancel Download</button>
             </div>
         </section>

         <!-- Variant Selection Dialog Placeholder -->
        <ChoiceDialog
            :show="variantSelectionDialog.visible"
            :title="variantSelectionDialog.title"
            :choices="variantSelectionDialog.choices"
            @choice-selected="handleVariantSelected"
            @choice-validated="handleVariantValidated"
            @close-dialog="closeVariantDialog"
        />

    </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick, reactive } from 'vue';
import feather from 'feather-icons';
import filesize from '@/plugins/filesize';
import ModelEntry from '@/components/ModelEntry.vue';
import ChoiceDialog from '@/components/ChoiceDialog.vue'; // Assuming component exists
import socket from '@/services/websocket.js';
import defaultModelIcon from "@/assets/default_model.png"; // Default icon

// Props
const props = defineProps({
    config: { type: Object, required: true },
    api_post_req: { type: Function, required: true },
    api_get_req: { type: Function, required: true },
    show_toast: { type: Function, required: true },
    show_yes_no_dialog: { type: Function, required: true },
    client_id: { type: String, required: true }
});

// Emits
const emit = defineEmits(['update:setting']);

// --- State ---
const allModels = ref([]); // Holds the full list fetched from backend
const filteredModels = ref([]); // Holds models after search/filter/sort
const pagedModels = ref([]); // Holds the currently rendered models (for pagination/lazy load)
const isLoadingModels = ref(false);
const isSearching = ref(false); // Indicate background search/filter is happening
const searchTerm = ref('');
const sortOption = ref('rank'); // Default sort: rank
const showInstalledOnly = ref(false);
const referencePath = ref('');
const modelUrl = ref(''); // For the download input field
const isDownloading = ref(false); // Tracks if *any* download is active

const itemsPerPage = ref(15); // How many models to load/show at a time
const currentPage = ref(1);

const searchDebounceTimer = ref(null);

const scrollContainer = ref(null); // Ref for the grid container
const loadMoreTrigger = ref(null); // Ref for the element triggering more loads

// Download Progress State
const downloadProgress = reactive({
    visible: false,
    name: '',
    progress: 0,
    speed: 0,
    total_size: 0,
    downloaded_size: 0,
    details: null // Store full model object or identifier
});

// Variant Selection Dialog State
const variantSelectionDialog = reactive({
    visible: false,
    title: "Select Model Variant",
    choices: [],
    modelToInstall: null,
    selectedVariant: null
});

// --- Computed ---

const currentBindingName = computed(() => {
    // Requires access to bindings list, potentially pass from parent or fetch here if needed
    // Placeholder logic:
    return props.config?.binding_name || 'None Selected';
});

const currentModelInfo = computed(() => {
    if (!props.config || !props.config.model_name || allModels.value.length === 0) {
        return null;
    }
    const current = allModels.value.find(m => m.name === props.config.model_name);
     // Fallback to finding in currently paged models if full list is huge and not fully processed?
     // const current = pagedModels.value.find(m => m.name === props.config.model_name) || allModels.value.find(m => m.name === props.config.model_name);
    return current ? { name: current.name, icon: current.icon || defaultModelIcon } : null;
});

const hasMoreModelsToLoad = computed(() => {
    return pagedModels.value.length < filteredModels.value.length;
});

// Computed properties for download progress display
const speedComputed = computed(() => filesize(downloadProgress.speed || 0));
const totalSizeComputed = computed(() => filesize(downloadProgress.total_size || 0));
const downloadedSizeComputed = computed(() => filesize(downloadProgress.downloaded_size || 0));

// --- Watchers ---
watch([searchTerm, sortOption, showInstalledOnly, () => props.config.binding_name], () => {
     // Reset pagination and re-apply filters when controls change or binding changes
    currentPage.value = 1;
    pagedModels.value = []; // Clear current page
    applyFiltersAndSort(); // This will update filteredModels
    loadMoreModels(); // Load the first page of the new filtered list
});

// Watch the master list changing (e.g., after fetching)
watch(allModels, () => {
    currentPage.value = 1;
    pagedModels.value = [];
    applyFiltersAndSort();
    loadMoreModels();
}, { deep: true }); // Use deep watch if model properties like 'installed' can change


// --- Methods ---

const fetchModels = async () => {
    if (!props.config.binding_name) {
        allModels.value = [];
        console.log("No binding selected, clearing models.");
        return;
    }
    isLoadingModels.value = true;
    console.log(`Fetching models for binding: ${props.config.binding_name}`);
    try {
        // 1. Get Zoo models (potentially large list)
        const zooModels = await props.api_get_req(`list_models?binding=${props.config.binding_name}`);

        // 2. Get Installed models (usually a smaller list)
        const installedModels = await props.api_get_req(`get_installed_models?binding=${props.config.binding_name}`);
        const installedSet = new Set(installedModels.map(m => m.name)); // Efficient lookup

        // 3. Combine and Mark Installed Status
        const combinedModels = (zooModels || []).map(model => ({
            ...model,
            isInstalled: installedSet.has(model.name),
            isProcessing: false, // For install/uninstall spinners
            // Add a unique ID if the backend provides one, otherwise rely on name/path
            id: model.id || `${model.name}-${model.quantizer || ''}`
        }));

        // 4. Add any installed models that weren't in the zoo list (custom references)
        installedModels.forEach(installedModel => {
             if (!combinedModels.some(m => m.name === installedModel.name)) {
                combinedModels.push({
                    ...installedModel, // Use data from get_installed_models
                    name: installedModel.name,
                    isInstalled: true,
                    isProcessing: false,
                    isCustomModel: true, // Flag it as potentially custom
                    icon: installedModel.icon || defaultModelIcon, // Use provided icon or default
                    id: installedModel.id || installedModel.name // Unique ID
                });
            }
        });


        allModels.value = combinedModels;
        console.log(`Fetched ${allModels.value.length} total models.`);

    } catch (error) {
        props.show_toast("Failed to load models.", 4, false);
        console.error("Error fetching models:", error);
        allModels.value = [];
    } finally {
        isLoadingModels.value = false;
        nextTick(feather.replace);
    }
};

const applyFiltersAndSort = () => {
    isSearching.value = true; // Indicate processing started
    console.time("FilterSortModels"); // Start timing

    let result = [...allModels.value];

    // 1. Filter by "Installed Only"
    if (showInstalledOnly.value) {
        result = result.filter(m => m.isInstalled);
    }

    // 2. Filter by Search Term (case-insensitive, check multiple fields)
    if (searchTerm.value) {
        const lowerSearch = searchTerm.value.toLowerCase();
        result = result.filter(m =>
            m.name?.toLowerCase().includes(lowerSearch) ||
            m.author?.toLowerCase().includes(lowerSearch) || // If author exists
            m.quantizer?.toLowerCase().includes(lowerSearch) || // If quantizer exists
            m.description?.toLowerCase().includes(lowerSearch) || // If description exists
            m.license?.toLowerCase().includes(lowerSearch) // If license exists
        );
    }

    // 3. Sort
    result.sort((a, b) => {
        // Always put installed models first regardless of other sort options
        if (a.isInstalled && !b.isInstalled) return -1;
        if (!a.isInstalled && b.isInstalled) return 1;

        // Then apply the selected sort option
        switch (sortOption.value) {
            case 'rank':
                return (b.rank ?? -Infinity) - (a.rank ?? -Infinity); // Higher rank first (handle missing rank)
            case 'name':
                return (a.name || '').localeCompare(b.name || '');
            case 'last_commit_time': {
                 // Handle potential null or invalid dates gracefully
                 const dateA = a.last_commit_time ? new Date(a.last_commit_time) : null;
                 const dateB = b.last_commit_time ? new Date(b.last_commit_time) : null;
                 if (dateA && dateB) return dateB - dateA; // Descending date (newest first)
                 if (dateA) return -1; // Put valid dates first
                 if (dateB) return 1;
                 return 0;
            }
            case 'quantizer':
                 return (a.quantizer || '').localeCompare(b.quantizer || '');
            case 'license':
                 return (a.license || '').localeCompare(b.license || '');
            default:
                return 0;
        }
    });

    filteredModels.value = result;
    console.timeEnd("FilterSortModels"); // End timing
    isSearching.value = false; // Indicate processing finished
    console.log(`Filtered/Sorted models: ${filteredModels.value.length}`);
};

const debounceSearch = () => {
    isSearching.value = true; // Show spinner immediately on input
    clearTimeout(searchDebounceTimer.value);
    searchDebounceTimer.value = setTimeout(() => {
        // Trigger the actual filter/sort which will set isSearching back to false
         currentPage.value = 1;
         pagedModels.value = [];
         applyFiltersAndSort();
         loadMoreModels();
    }, 500); // Adjust debounce delay (ms) as needed
};

const loadMoreModels = () => {
     if (isLoadingModels.value || isSearching.value) return; // Prevent loading during initial fetch or search debounce

     console.log(`Loading page ${currentPage.value}`);
     const start = (currentPage.value - 1) * itemsPerPage.value;
     const end = start + itemsPerPage.value;
     const nextPageItems = filteredModels.value.slice(start, end);

     pagedModels.value.push(...nextPageItems);
     currentPage.value++;
     nextTick(feather.replace); // Ensure icons render for new items
};

// --- Model Actions ---
const handleSelect = (model) => {
    if (!model.isInstalled) {
        props.show_toast(`Model "${model.name}" is not installed.`, 3, false);
        return;
    }
    if (props.config.model_name !== model.name) {
         // Set loading state specific to model selection if needed
        props.show_toast(`Selecting model: ${model.name}...`, 2, true);
        emit('update:setting', { key: 'model_name', value: model.name });
        // The parent watcher on config.model_name should handle backend updates/checks
    }
};

const handleInstall = (modelEntryData) => {
     const model = modelEntryData.model; // Extract the core model data
     console.log("Initiating install for:", model);

     // Check if variants exist
     if (model.variants && model.variants.length > 0) {
         variantSelectionDialog.choices = model.variants.map(v => ({
             ...v, // Spread variant properties like name, size, etc.
             id: v.name, // Use variant name as unique ID for ChoiceDialog
             label: `${v.name} (${filesize(v.size || 0)})` // Example label
         }));
         variantSelectionDialog.modelToInstall = model; // Store the main model info
         variantSelectionDialog.visible = true;
     } else {
         // No variants, proceed with direct install using the main model URL/path if available
         const path = model.path || `https://huggingface.co/${model.quantizer || 'Unknown'}/${model.name}/resolve/main/${model.filename || model.name}`; // Construct path if needed
        startDownload(model, path, model.filename || model.name);
     }
};

const handleVariantSelected = (choice) => {
    variantSelectionDialog.selectedVariant = choice;
};

const handleVariantValidated = (choice) => {
     if (!choice || !variantSelectionDialog.modelToInstall) {
        console.error("No variant selected or model info missing.");
        closeVariantDialog();
        return;
     }
     const model = variantSelectionDialog.modelToInstall;
     const variant = choice; // The validated choice object from ChoiceDialog
    const path = variant.path || `https://huggingface.co/${model.quantizer || 'Unknown'}/${model.name}/resolve/main/${variant.name}`; // Construct path

    startDownload(model, path, variant.name); // Pass variant name
    closeVariantDialog();
};

const closeVariantDialog = () => {
    variantSelectionDialog.visible = false;
    variantSelectionDialog.choices = [];
    variantSelectionDialog.modelToInstall = null;
    variantSelectionDialog.selectedVariant = null;
};

const startDownload = (model, path, variantName) => {
    console.log(`Starting download for: ${model.name}, Variant: ${variantName}, Path: ${path}`);
    if (isDownloading.value) {
        props.show_toast("Another download is already in progress.", 3, false);
        return;
    }
     setModelProcessing(model.id || model.name, true); // Use model ID or name as key
    isDownloading.value = true;
    downloadProgress.visible = true;
    downloadProgress.name = `${model.name}${variantName !== model.name ? ` (${variantName})` : ''}`;
    downloadProgress.progress = 0;
    downloadProgress.speed = 0;
    downloadProgress.total_size = 0;
    downloadProgress.downloaded_size = 0;
    downloadProgress.details = { // Store identifiers needed for cancellation
        model_name: model.name,
        binding_folder: props.config.binding_name, // Assuming current binding
        model_url: path,
        variant_name: variantName,
        model_id: model.id || model.name // Use the same key as setModelProcessing
        // patreon: model.patreon?model.patreon:"None" // If needed by backend cancel
    };

     // Emit install request via socket
    socket.emit('install_model', {
        path: path,
        name: model.name,
        variant_name: variantName,
        type: model.type || 'gguf', // Provide type if available
        binding: props.config.binding_name // Send current binding
    });
};

const handleUninstall = async (modelEntryData) => {
    const model = modelEntryData.model;
    const yes = await props.show_yes_no_dialog(`Are you sure you want to uninstall model "${model.name}"?`, 'Uninstall', 'Cancel');
    if (!yes) return;

    setModelProcessing(model.id || model.name, true);
    isDownloading.value = true; // Use this to prevent other actions
    downloadProgress.visible = true; // Show a generic "uninstalling" message
    downloadProgress.name = `Uninstalling ${model.name}...`;
    downloadProgress.progress = 50; // Indicate activity
    downloadProgress.details = { model_id: model.id || model.name }; // Store identifier

    try {
         // Backend needs to know which file(s) to delete based on model name/variant
         // This might require listing installed files first or passing enough info
        const response = await props.api_post_req('uninstall_model', {
            name: model.name,
             // variant: model.installed_variant // If backend tracks this
             binding: props.config.binding_name // Send current binding
        });

        if (response && response.status) {
             props.show_toast(`Model "${model.name}" uninstalled successfully.`, 4, true);
             // Update local state immediately
             const index = allModels.value.findIndex(m => (m.id || m.name) === (model.id || model.name));
             if (index !== -1) {
                 allModels.value[index].isInstalled = false;
                // Trigger reactivity for computed properties
                 allModels.value = [...allModels.value];
             }
             // No need to call fetchModels() if we update locally
        } else {
            props.show_toast(`Failed to uninstall model "${model.name}": ${response?.error || 'Unknown error'}`, 4, false);
        }
    } catch (error) {
        props.show_toast(`Error uninstalling model "${model.name}": ${error.message}`, 4, false);
        console.error(`Error uninstalling ${model.name}:`, error);
    } finally {
        setModelProcessing(model.id || model.name, false);
        downloadProgress.visible = false;
        isDownloading.value = false;
    }
};

const handleCancelInstall = (downloadDetails) => {
     if (!downloadDetails) return;
     console.log('Cancelling install for:', downloadDetails);
     socket.emit('cancel_install', {
         model_name: downloadDetails.model_name,
         binding_folder: downloadDetails.binding_folder,
         model_url: downloadDetails.model_url,
         variant_name: downloadDetails.variant_name
         // patreon: downloadDetails.patreon // If needed
     });
     // State reset is handled by the 'install_progress' listener receiving a cancel/fail status
};

const handleCopy = (modelEntryData) => {
     const model = modelEntryData.model;
    let content = `Model: ${model.name}\n`;
    if (model.quantizer) content += `Quantizer: ${model.quantizer}\n`;
    if (model.rank) content += `Rank: ${model.rank}\n`;
    if (model.license) content += `License: ${model.license}\n`;
    if (model.description) content += `Description: ${model.description}\n`;
    if (!model.isCustomModel) content += `Link: https://huggingface.co/${model.quantizer || 'Unknown'}/${model.name}\n`;

    navigator.clipboard.writeText(content.trim())
        .then(() => props.show_toast("Model info copied!", 3, true))
        .catch(err => props.show_toast("Failed to copy info.", 3, false));
};

const handleCopyLink = (modelEntryData) => {
     const model = modelEntryData.model;
    const link = model.isCustomModel ? model.name : `https://huggingface.co/${model.quantizer || 'Unknown'}/${model.name}`;
    navigator.clipboard.writeText(link)
        .then(() => props.show_toast("Link copied!", 3, true))
        .catch(err => props.show_toast("Failed to copy link.", 3, false));
};

const createReference = async () => {
    if (!referencePath.value) {
        props.show_toast("Please enter a path for the local model reference.", 3, false);
        return;
    }
    isLoadingModels.value = true; // Indicate activity
    try {
        const response = await props.api_post_req("add_reference_to_local_model", { path: referencePath.value });
        if (response.status) {
            props.show_toast("Reference created successfully.", 4, true);
            referencePath.value = ''; // Clear input
            await fetchModels(); // Refresh the model list
        } else {
            props.show_toast(`Couldn't create reference: ${response.error || 'Unknown error'}`, 4, false);
        }
    } catch (error) {
        props.show_toast(`Error creating reference: ${error.message}`, 4, false);
    } finally {
        isLoadingModels.value = false;
    }
};

const installFromInput = () => {
     if (!modelUrl.value) {
        props.show_toast("Please enter a Model URL or Hugging Face ID.", 3, false);
        return;
     }
     // Basic check if it looks like a HF ID (e.g., contains '/')
     let path = modelUrl.value;
     let modelNameGuess = modelUrl.value;
     let modelQuantizerGuess = 'Unknown';
     if (modelUrl.value.includes('/') && !modelUrl.value.startsWith('http')) {
         const parts = modelUrl.value.split('/');
         if (parts.length >= 2) {
            modelQuantizerGuess = parts[0];
            modelNameGuess = parts[1];
             // Attempt to construct a likely path, backend might need more robust handling
             path = `https://huggingface.co/${modelQuantizerGuess}/${modelNameGuess}`;
         }
     } else if (!modelUrl.value.startsWith('http')) {
         props.show_toast("Invalid Hugging Face ID format. Use 'User/Model'.", 4, false);
         return;
     }

     // Create a placeholder model object for the download process
     const placeholderModel = {
         name: modelNameGuess,
         quantizer: modelQuantizerGuess,
         type: 'gguf', // Assume GGUF or let backend determine
         id: modelNameGuess // Use name as temporary ID
     };

     // Currently doesn't support variant selection for direct URL/ID input
     startDownload(placeholderModel, path, modelNameGuess);
     modelUrl.value = ''; // Clear input after starting
};


const imgPlaceholder = (event) => {
    event.target.src = defaultModelIcon;
};

const setModelProcessing = (modelId, state) => {
    const index = allModels.value.findIndex(m => (m.id || m.name) === modelId);
    if (index !== -1) {
        allModels.value[index].isProcessing = state;
        // Also update pagedModels if the item exists there for immediate UI feedback
        const pagedIndex = pagedModels.value.findIndex(m => (m.id || m.name) === modelId);
        if (pagedIndex !== -1) {
            pagedModels.value[pagedIndex].isProcessing = state;
        }
    } else {
        console.warn("Couldn't find model to set processing state for ID:", modelId);
    }
};

// --- Socket Listeners ---
const installProgressListener = (response) => {
    console.log("Socket install_progress:", response);

     const modelId = response.model_id || response.model_name; // Use ID if available

     if (response.status === 'progress' || response.status === 'downloading') {
         downloadProgress.visible = true;
         downloadProgress.name = `${response.model_name}${response.variant_name !== response.model_name ? ` (${response.variant_name})` : ''}`;
         downloadProgress.progress = response.progress || 0;
         downloadProgress.speed = response.speed || 0;
         downloadProgress.total_size = response.total_size || 0;
         downloadProgress.downloaded_size = response.downloaded_size || 0;
         // Ensure the details object is populated if it wasn't already
         if (!downloadProgress.details || downloadProgress.details.model_id !== modelId) {
             downloadProgress.details = {
                 model_name: response.model_name,
                 binding_folder: response.binding_folder,
                 model_url: response.model_url,
                 variant_name: response.variant_name,
                 model_id: modelId
             };
         }
         // Update processing state on the actual model entry
         setModelProcessing(modelId, true);

     } else if (response.status === 'succeeded') {
         props.show_toast(`Model "${response.model_name}" installed successfully!`, 4, true);
         downloadProgress.visible = false;
         isDownloading.value = false;
         setModelProcessing(modelId, false);
         // Update installed status in the main list
         const index = allModels.value.findIndex(m => (m.id || m.name) === modelId);
         if (index !== -1) {
             allModels.value[index].isInstalled = true;
             allModels.value = [...allModels.value]; // Trigger reactivity
         }

     } else if (response.status === 'failed' || response.status === 'cancelled') {
         props.show_toast(`Model "${response.model_name}" installation ${response.status}: ${response.error || ''}`, 4, false);
         downloadProgress.visible = false;
         isDownloading.value = false;
         setModelProcessing(modelId, false);
     }
};

// --- Infinite Scroll ---
let observer = null;
const setupIntersectionObserver = () => {
     const options = {
         root: null, // Use the viewport
         rootMargin: '0px',
         threshold: 0.1 // Trigger when 10% of the trigger element is visible
     };

     observer = new IntersectionObserver((entries) => {
         entries.forEach(entry => {
             if (entry.isIntersecting && hasMoreModelsToLoad.value && !isLoadingModels.value && !isSearching.value) {
                 console.log("Intersection observer triggered: Loading more models.");
                 loadMoreModels();
             }
         });
     }, options);

     if (loadMoreTrigger.value) {
         observer.observe(loadMoreTrigger.value);
     } else {
         console.warn("Load more trigger element not found for IntersectionObserver.");
     }
};

// --- Lifecycle Hooks ---
onMounted(() => {
    fetchModels(); // Initial fetch
    socket.on('install_progress', installProgressListener);
    nextTick(() => {
        feather.replace();
         if (loadMoreTrigger.value) {
            setupIntersectionObserver();
        }
    });
});

onUnmounted(() => {
    socket.off('install_progress', installProgressListener);
     if (observer && loadMoreTrigger.value) {
        observer.unobserve(loadMoreTrigger.value);
     }
     if (observer) {
        observer.disconnect();
     }
     clearTimeout(searchDebounceTimer.value);
});

onUpdated(() => {
    nextTick(() => {
        feather.replace();
        // Ensure observer is attached if the trigger element becomes available after an update
        if (!observer && loadMoreTrigger.value) {
             setupIntersectionObserver();
        } else if (observer && loadMoreTrigger.value) {
             // Re-observe in case the element was replaced
            observer.disconnect();
            observer.observe(loadMoreTrigger.value);
        }
    });
});

</script>
<style scoped>
/* Shared styles */
.input-field {
     /* Standard focus, background, border */
     @apply block w-full px-3 py-2 text-sm bg-gray-50 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 focus:border-blue-500 dark:focus:ring-offset-gray-800 disabled:opacity-50;
}
.input-field-sm {
     /* Standard focus, background, border - smaller version */
     @apply block w-full px-2.5 py-1.5 text-xs bg-gray-50 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 focus:border-blue-500 dark:focus:ring-offset-gray-800 disabled:opacity-50;
}

/* Shared Button Styles (Tailwind) - Standardized */
.button-base-sm {
     @apply inline-flex items-center justify-center px-2.5 py-1.5 border border-transparent text-xs font-medium rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-offset-2 dark:focus:ring-offset-gray-800 disabled:opacity-50 transition-colors duration-150;
}

/* Use standard blue for primary, green for success etc. */
.button-primary-sm { @apply button-base-sm text-white bg-blue-600 hover:bg-blue-700 focus:ring-blue-500; }
.button-success-sm { @apply button-base-sm text-white bg-green-600 hover:bg-green-700 focus:ring-green-500; }
.button-danger-sm { @apply button-base-sm text-white bg-red-600 hover:bg-red-700 focus:ring-red-500; }

/* Specific styles */
/* Add transition group styles if needed */
.model-grid-enter-active,
.model-grid-leave-active {
  transition: all 0.5s ease;
}
.model-grid-enter-from,
.model-grid-leave-to {
  opacity: 0;
  transform: translateY(15px);
}
.model-grid-leave-active {
  /* Consider if position absolute is needed for your specific transition */
  /* position: absolute; */
}

/* Style for the currently active model display */
.bg-primary-light { /* Using a lighter blue for background */
    @apply bg-blue-100;
}
.dark .bg-primary-dark\/20 { /* Using blue with opacity in dark mode */
     @apply bg-blue-500/20;
}
.border-primary-dark\/30 { /* Using blue with opacity for border */
    @apply border-blue-500/30;
}
.dark .hover\:bg-primary-dark\/20:hover { /* Hover effect */
    @apply hover:bg-blue-500/30;
}
.hover\:bg-primary-dark\/20:hover { /* Hover effect */
    @apply hover:bg-blue-200;
}
</style>