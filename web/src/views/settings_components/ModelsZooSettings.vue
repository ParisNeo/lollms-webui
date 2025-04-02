<template>
    <div class="user-settings-panel space-y-6">
        <!-- Header Section -->
        <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center border-b border-blue-300 dark:border-blue-600 pb-3 mb-4">
            <h2 class="text-xl font-semibold text-blue-800 dark:text-blue-100 mb-2 sm:mb-0">
                Models Zoo
            </h2>
            <!-- Current Model Display -->
             <div v-if="currentModelInfoComputed" class="flex items-center gap-2 text-sm font-medium p-2 bg-blue-100 dark:bg-blue-800/50 rounded-md border border-blue-300 dark:border-blue-600 shrink-0 text-blue-700 dark:text-blue-200">
                 <img :src="currentModelInfoComputed.icon" @error="imgPlaceholder" class="w-6 h-6 rounded-lg object-cover flex-shrink-0" alt="Current Model Icon">
                 <span>Active: <span class="font-semibold">{{ currentModelInfoComputed.name }}</span></span>
            </div>
             <!-- Directly access store state for binding -->
            <div v-else-if="!$store.state.config.binding_name" class="text-sm font-medium text-orange-600 dark:text-orange-400 p-2 bg-orange-100 dark:bg-orange-900/30 rounded-md border border-orange-300 dark:border-orange-600 shrink-0">
                 Select a Binding first!
             </div>
            <div v-else class="text-sm font-medium text-red-600 dark:text-red-400 p-2 bg-red-100 dark:bg-red-900/30 rounded-md border border-red-300 dark:border-red-600 shrink-0">
                No model selected!
            </div>
        </div>

        <!-- Info and Warnings -->
        <p class="text-sm text-blue-600 dark:text-blue-400">
             Select a model compatible with your chosen binding (<span class="font-semibold">{{ currentBindingNameComputed || 'None Selected' }}</span>). Installed models are shown first. Models may require specific variants (e.g., GGUF, GPTQ) depending on the binding.
        </p>
         <!-- Directly access store state for binding -->
         <div v-if="!$store.state.config.binding_name" class="p-3 text-center text-orange-600 dark:text-orange-400 bg-orange-100 dark:bg-orange-900/30 rounded-md border border-orange-300 dark:border-orange-600">
            Please select a Binding from the 'Bindings' section to see available models.
        </div>

        <!-- Controls: Search, Filters, Sort -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4 items-center">
            <!-- Search Input -->
            <div class="relative md:col-span-2">
                 <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                     <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="w-5 h-5 text-blue-400 dark:text-blue-500 feather feather-search"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
                </div>
                 <input
                    type="search"
                    v-model="searchTerm"
                    placeholder="Search models by name, author, quantizer, description..."
                    class="input search-input pl-10 w-full"
                    @input="debounceSearch"
                />
                 <div v-if="isSearching" class="absolute inset-y-0 right-0 pr-3 flex items-center">
                     <svg aria-hidden="true" class="w-5 h-5 text-blue-400 animate-spin dark:text-blue-500 fill-blue-600" viewBox="0 0 100 101" fill="none" xmlns="http://www.w3.org/2000/svg"> <path d="M100 50.5908C100 78.2051 77.6142 100.591 50 100.591C22.3858 100.591 0 78.2051 0 50.5908C0 22.9766 22.3858 0.59082 50 0.59082C77.6142 0.59082 100 22.9766 100 50.5908ZM9.08144 50.5908C9.08144 73.1895 27.4013 91.5094 50 91.5094C72.5987 91.5094 90.9186 73.1895 90.9186 50.5908C90.9186 27.9921 72.5987 9.67226 50 9.67226C27.4013 9.67226 9.08144 27.9921 9.08144 50.5908Z" fill="currentColor"/> <path d="M93.9676 39.0409C96.393 38.4038 97.8624 35.9116 97.0079 33.5539C95.2932 28.8227 92.871 24.3692 89.8167 20.348C85.8452 15.1192 80.8826 10.7238 75.2124 7.41289C69.5422 4.10194 63.2754 1.94025 56.7698 1.05124C51.7666 0.367541 46.6976 0.446843 41.7345 1.27873C39.2613 1.69328 37.813 4.19778 38.4501 6.62326C39.0873 9.04874 41.5694 10.4717 44.0505 10.1071C47.8511 9.54855 51.7191 9.52689 55.5402 10.0491C60.8642 10.7766 65.9928 12.5457 70.6331 15.2552C75.2735 17.9648 79.3347 21.5619 82.5849 25.841C84.9175 28.9121 86.7997 32.2913 88.1811 35.8758C89.083 38.2158 91.5421 39.6781 93.9676 39.0409Z" fill="currentFill"/> </svg>
                 </div>
            </div>
            <!-- Filters -->
            <div class="flex items-center space-x-2">
                 <label for="model-filter-installed" class="flex items-center space-x-1 cursor-pointer text-sm label"> <!-- Applied label class -->
                    <input type="checkbox" id="model-filter-installed" v-model="showInstalledOnly" class="rounded text-blue-600 focus:ring-blue-500 border-blue-300 dark:border-blue-600 bg-blue-100 dark:bg-blue-700 focus:ring-offset-blue-100 dark:focus:ring-offset-blue-800"> <!-- Added bg colors -->
                     <span>Installed Only</span>
                 </label>
                 <!-- Add more filters if needed -->
            </div>
             <!-- Sort Select -->
            <div>
                 <label for="model-sort" class="sr-only">Sort models by</label>
                 <select id="model-sort" v-model="sortOption" class="input"> <!-- Applied input class -->
                     <option value="rank">Sort by Rank</option>
                     <option value="name">Sort by Name</option>
                     <option value="last_commit_time">Sort by Date</option>
                     <option value="quantizer">Sort by Quantizer</option>
                     <option value="license">Sort by License</option>
                 </select>
            </div>
        </div>

        <!-- Loading / Empty State -->
        <div v-if="isLoadingModels" class="flex justify-center items-center p-10 text-loading">
             <svg aria-hidden="true" class="w-8 h-8 mr-2 text-blue-300 animate-spin dark:text-blue-600 fill-blue-600" viewBox="0 0 100 101" fill="none" xmlns="http://www.w3.org/2000/svg"> <path d="M100 50.5908C100 78.2051 77.6142 100.591 50 100.591C22.3858 100.591 0 78.2051 0 50.5908C0 22.9766 22.3858 0.59082 50 0.59082C77.6142 0.59082 100 22.9766 100 50.5908ZM9.08144 50.5908C9.08144 73.1895 27.4013 91.5094 50 91.5094C72.5987 91.5094 90.9186 73.1895 90.9186 50.5908C90.9186 27.9921 72.5987 9.67226 50 9.67226C27.4013 9.67226 9.08144 27.9921 9.08144 50.5908Z" fill="currentColor"/> <path d="M93.9676 39.0409C96.393 38.4038 97.8624 35.9116 97.0079 33.5539C95.2932 28.8227 92.871 24.3692 89.8167 20.348C85.8452 15.1192 80.8826 10.7238 75.2124 7.41289C69.5422 4.10194 63.2754 1.94025 56.7698 1.05124C51.7666 0.367541 46.6976 0.446843 41.7345 1.27873C39.2613 1.69328 37.813 4.19778 38.4501 6.62326C39.0873 9.04874 41.5694 10.4717 44.0505 10.1071C47.8511 9.54855 51.7191 9.52689 55.5402 10.0491C60.8642 10.7766 65.9928 12.5457 70.6331 15.2552C75.2735 17.9648 79.3347 21.5619 82.5849 25.841C84.9175 28.9121 86.7997 32.2913 88.1811 35.8758C89.083 38.2158 91.5421 39.6781 93.9676 39.0409Z" fill="currentFill"/> </svg>
             <span>Loading models...</span>
        </div>
        <div v-else-if="pagedModels.length === 0 && filteredModels.length > 0" class="text-center text-blue-500 dark:text-blue-400 py-10">
             No models found matching filters{{ searchTerm ? ' and search "' + searchTerm + '"' : '' }}.
        </div>
         <!-- Directly access store state for binding -->
        <div v-else-if="allModels.length === 0 && !isLoadingModels && $store.state.config.binding_name" class="text-center text-blue-500 dark:text-blue-400 py-10">
             No models available for the selected binding. Try adding a reference or downloading below.
        </div>


        <!-- Models Grid - Lazy Loaded -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4" ref="scrollContainer">
             <!-- Ensure the key is stable and unique -->
             <ModelEntry
                 v-for="model in pagedModels"
                :key="model.id || model.name"
                :model="model"
                :is-selected="$store.state.config.model_name === model.name"
                :is-installed="model.isInstalled"
                :is-processing="model.isProcessing"
                :progress="downloadProgress.details?.model_id === (model.id || model.name) ? downloadProgress.progress : 0"
                :speed="downloadProgress.details?.model_id === (model.id || model.name) ? downloadProgress.speed : 0"
                :total_size="downloadProgress.details?.model_id === (model.id || model.name) ? downloadProgress.total_size : 0"
                :downloaded_size="downloadProgress.details?.model_id === (model.id || model.name) ? downloadProgress.downloaded_size : 0"
                :progress-name="downloadProgress.details?.model_id === (model.id || model.name) ? downloadProgress.name : ''"
                @select="handleSelect"
                @install="handleInstall"
                @uninstall="handleUninstall"
                @cancel-install="handleCancelInstall"
                @copy="handleCopy"
                @copy-link="handleCopyLink"
             />
        </div>

        <!-- NEW: Load More Button -->
        <div class="mt-6 text-center" v-if="hasMoreModelsToLoad">
            <button
                @click="loadMoreModels"
                :disabled="isLoadingModels || isSearching"
                class="btn btn-secondary"
            >
                <span v-if="isLoadingModels || isSearching">
                    <svg aria-hidden="true" class="w-4 h-4 mr-1 inline animate-spin text-blue-400 dark:text-blue-500 fill-blue-600" viewBox="0 0 100 101" fill="none" xmlns="http://www.w3.org/2000/svg"> <path d="M100 50.5908C100 78.2051 77.6142 100.591 50 100.591C22.3858 100.591 0 78.2051 0 50.5908C0 22.9766 22.3858 0.59082 50 0.59082C77.6142 0.59082 100 22.9766 100 50.5908ZM9.08144 50.5908C9.08144 73.1895 27.4013 91.5094 50 91.5094C72.5987 91.5094 90.9186 73.1895 90.9186 50.5908C90.9186 27.9921 72.5987 9.67226 50 9.67226C27.4013 9.67226 9.08144 27.9921 9.08144 50.5908Z" fill="currentColor"/> <path d="M93.9676 39.0409C96.393 38.4038 97.8624 35.9116 97.0079 33.5539C95.2932 28.8227 92.871 24.3692 89.8167 20.348C85.8452 15.1192 80.8826 10.7238 75.2124 7.41289C69.5422 4.10194 63.2754 1.94025 56.7698 1.05124C51.7666 0.367541 46.6976 0.446843 41.7345 1.27873C39.2613 1.69328 37.813 4.19778 38.4501 6.62326C39.0873 9.04874 41.5694 10.4717 44.0505 10.1071C47.8511 9.54855 51.7191 9.52689 55.5402 10.0491C60.8642 10.7766 65.9928 12.5457 70.6331 15.2552C75.2735 17.9648 79.3347 21.5619 82.5849 25.841C84.9175 28.9121 86.7997 32.2913 88.1811 35.8758C89.083 38.2158 91.5421 39.6781 93.9676 39.0409Z" fill="currentFill"/> </svg>
                    Loading...
                </span>
                <span v-else>Load More Models ({{ filteredModels.length - pagedModels.length }} remaining)</span>
            </button>
        </div>

        <!-- Add Model / Reference Section -->
         <section class="pt-6 border-t border-blue-200 dark:border-blue-700 mt-6">
             <h3 class="text-lg font-medium text-blue-700 dark:text-blue-300 mb-3">Add Model</h3>
             <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                 <!-- Add Reference Path -->
                 <div>
                     <label for="reference_path" class="label mb-1">Add Reference to Local Model File/Folder</label> <!-- Use label class -->
                     <div class="flex">
                         <input type="text" id="reference_path" v-model="referencePath" class="input input-sm rounded-r-none flex-grow" placeholder="Enter full path to model file or folder..."> <!-- Use input-sm -->
                         <button @click="createReference" class="btn btn-primary btn-sm rounded-l-none flex-shrink-0" title="Add Reference">Add</button>
                     </div>
                     <p class="text-xs text-blue-500 dark:text-blue-400 mt-1">Creates a link without copying the model. Binding must support references.</p>
                 </div>
                 <!-- Download from URL / Hugging Face -->
                 <div>
                     <label for="model_url" class="label mb-1">Download Model from URL or Hugging Face ID</label> <!-- Use label class -->
                     <div class="flex">
                        <input type="text" id="model_url" v-model="modelUrl" class="input input-sm rounded-r-none flex-grow" placeholder="Enter URL or HF ID (e.g., TheBloke/Llama-2-7B-GGUF)..."> <!-- Use input-sm -->
                        <button @click="installFromInput" class="btn btn-success btn-sm rounded-l-none flex-shrink-0" title="Download and Install" :disabled="isDownloading">
                             <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" :class="['w-4 h-4', isDownloading ? 'animate-spin feather feather-loader' : 'feather feather-download']"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line><line x1="12" y1="2" x2="12" y2="6"></line><line x1="12" y1="18" x2="12" y2="22"></line><line x1="4.93" y1="4.93" x2="7.76" y2="7.76"></line><line x1="16.24" y1="16.24" x2="19.07" y2="19.07"></line><line x1="2" y1="12" x2="6" y2="12"></line><line x1="18" y1="12" x2="22" y2="12"></line><line x1="4.93" y1="19.07" x2="7.76" y2="16.24"></line><line x1="16.24" y1="7.76" x2="19.07" y2="4.93"></line></svg>
                         </button>
                     </div>
                    <p class="text-xs text-blue-500 dark:text-blue-400 mt-1">Downloads the model to the binding's models folder.</p>
                 </div>
             </div>
              <!-- Download Progress (Conditional) -->
             <div v-if="downloadProgress.visible" class="mt-4 p-3 bg-blue-100 dark:bg-blue-900/30 border border-blue-200 dark:border-blue-700 rounded-md">
                 <div class="flex justify-between items-center mb-1">
                     <span class="text-sm font-medium text-blue-700 dark:text-blue-300"> {{ downloadProgress.name }}</span>
                     <span class="text-xs font-medium text-progress">{{ downloadProgress.progress.toFixed(1) }}%</span> <!-- Use text-progress -->
                 </div>
                 <!-- Use animated progress bar classes -->
                 <div class="animated-progressbar-bg h-1.5">
                    <div class="animated-progressbar-fg h-1.5 rounded-full" :style="{ width: downloadProgress.progress + '%' }"></div>
                 </div>
                 <div class="flex justify-between items-center mt-1 text-xs text-progress"> <!-- Use text-progress -->
                     <span>{{ downloadedSizeComputed }} / {{ totalSizeComputed }}</span>
                     <span>{{ speedComputed }}/s</span>
                 </div>
                 <button @click="handleCancelInstall(downloadProgress.details)" class="btn btn-secondary btn-sm mt-2 text-xs text-red-500 dark:text-red-400 hover:bg-red-200 dark:hover:bg-red-700">Cancel Operation</button> <!-- Use secondary button with red text -->
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

<script>
import { nextTick } from 'vue';
import feather from 'feather-icons';
import filesize from '@/plugins/filesize';
import ModelEntry from '@/components/ModelEntry.vue';
import ChoiceDialog from '@/components/ChoiceDialog.vue';
import socket from '@/services/websocket.js';
import defaultModelIcon from "@/assets/default_model.png";

export default {
    name: 'ModelsZoo',
    components: {
        ModelEntry,
        ChoiceDialog
    },
    props: {
        api_post_req: { type: Function, required: true },
        api_get_req: { type: Function, required: true },
        show_toast: { type: Function, required: true },
        show_yes_no_dialog: { type: Function, required: true },
        client_id: { type: String, required: true }
    },
    emits: ['settings-changed'], // To notify parent about model selection change
    data() {
        return {
            allModels: [],
            filteredModels: [],
            pagedModels: [],
            isLoadingModels: false,
            isSearching: false,
            searchTerm: '',
            sortOption: 'rank',
            showInstalledOnly: false,
            referencePath: '',
            modelUrl: '',
            isDownloading: false,
            itemsPerPage: 15,
            currentPage: 1,
            searchDebounceTimer: null,
            downloadProgress: {
                visible: false, name: '', progress: 0, speed: 0, total_size: 0, downloaded_size: 0, details: null
            },
            variantSelectionDialog: {
                visible: false, title: "Select Model Variant", choices: [], modelToInstall: null, selectedVariant: null
            },
            defaultIcon: defaultModelIcon
        };
    },
    computed: {
        // --- Retained Computed Properties ---
        // These depend on other store parts or local state and should be fine.

        // Computed property to derive the binding name for display purposes
        currentBindingNameComputed() {
            const currentBindingFolder = this.$store.state.config.binding_name;
            if (!currentBindingFolder) return 'None Selected';
            const binding = (this.$store.state.bindingsZoo || []).find(b => b.folder === currentBindingFolder);
            return binding ? binding.name : currentBindingFolder; // Fallback to folder name if not found in zoo
        },

        // Computed property to derive the current model info for display
        currentModelInfoComputed() {
            const currentModelName = this.$store.state.config.model_name;
            if (!currentModelName || this.allModels.length === 0) {
                return null;
            }
            // Find model in the locally processed 'allModels' list
            const current = this.allModels.find(m => m.name === currentModelName);
            // Use computed here for cleaner template access
            return current ? { name: current.name, icon: current.icon || this.defaultIcon } : null;
        },

        hasMoreModelsToLoad() {
            return this.pagedModels.length < this.filteredModels.length;
        },
        speedComputed() {
            return filesize(this.downloadProgress.speed || 0);
        },
        totalSizeComputed() {
            return filesize(this.downloadProgress.total_size || 0);
        },
        downloadedSizeComputed() {
            return filesize(this.downloadProgress.downloaded_size || 0);
        },
        // Watch source aggregation (remains the same)
        watchSources() {
            return [
                this.searchTerm,
                this.sortOption,
                this.showInstalledOnly,
                this.allModels // Watch the result of processAndCombineModels
            ];
        }
    },
    watch: {
        // Watch store values directly if needed for complex logic outside templates/methods
        // Using a function allows watching nested properties reactively
        '$store.state.config.binding_name': {
            handler(newBinding, oldBinding) {
                console.log("Binding name changed")
                if (newBinding !== oldBinding) { // Only react if it actually changed
                    console.log(`Binding changed via watcher from ${oldBinding} to ${newBinding}.`);

                    // Reset local state immediately
                    this.isLoadingModels = true;
                    this.allModels = []; // Clear the main source array first
                    this.searchTerm = '';
                    this.showInstalledOnly = false;
                    this.currentPage = 1; // Reset pagination
                    this.pagedModels = []; // Clear visible models

                    if (newBinding) {
                        console.log(`Triggering store refresh actions for binding: ${newBinding}`);
                        // Assuming store actions handle the async loading and update
                        // which will then trigger their respective watchers below.
                         Promise.all([
                             this.$store.dispatch('refreshModelsZoo'),
                             this.$store.dispatch('refreshModels')
                         ]).then(() => {
                            console.log(`Store refresh dispatches initiated for ${newBinding}. Waiting for store watchers.`);
                            // The watchers below will call processAndCombineModels -> sets isLoadingModels = false.
                        }).catch(error => {
                            console.error(`Error dispatching store refresh for binding ${newBinding}:`, error);
                            this.show_toast(`Failed to load models for binding ${newBinding}.`, 5, false);
                            this.isLoadingModels = false; // Ensure loading stops on error
                        });
                    } else {
                        console.log("Binding removed, local models cleared.");
                        this.isLoadingModels = false; // No loading needed if no binding
                    }
                }
            },
             // immediate: true // Optionally run on component mount if needed
        },
        '$store.state.modelsArr': {
            handler() {
                console.log("Store installedModels changed, reprocessing.");
                this.processAndCombineModels();
            },
            deep: false
        },
        allModels: {
            handler(newModels, oldModels) {
                if (newModels !== oldModels && newModels.length > 0) {
                    console.log("Processed allModels changed, applying filters and reloading page 1.");
                    this.currentPage = 1;
                    this.pagedModels = [];
                    this.applyFiltersAndSort();
                    this.loadMoreModels();
                } else if (newModels.length === 0 && oldModels.length > 0){
                    console.log("Processed allModels cleared, resetting filters and paged models.");
                    this.filteredModels = [];
                    this.pagedModels = [];
                    this.currentPage = 1;
                 } else if (newModels === oldModels && newModels.length > 0) {
                     // Handle cases where internal properties might change (like isProcessing)
                     // but the array reference itself didn't. Re-filter/sort.
                     console.log("allModels reference same, but potentially updated internal state. Re-applying filters.");
                     this.currentPage = 1; // Reset to page 1 as filters might change order/content
                     this.pagedModels = [];
                     this.applyFiltersAndSort();
                     this.loadMoreModels();
                 }
            },
            deep: true // Important for detecting changes within model objects (like isProcessing)
        },
        watchSources(newVal, oldVal) {
             // Compare individual elements to avoid unnecessary triggers if allModels reference changes but other filters don't
            if (newVal[0] !== oldVal[0] || newVal[1] !== oldVal[1] || newVal[2] !== oldVal[2]) {
                 console.log("Filter/Sort/Search changed, resetting page and applying filters.");
                 this.currentPage = 1;
                 this.pagedModels = [];
                 this.applyFiltersAndSort();
                 this.loadMoreModels();
            }
             // Note: Changes to allModels are handled by the dedicated 'allModels' watcher now.
        },
    },
    methods: {

        // --- Core Logic Methods (mostly unchanged) ---
        async processAndCombineModels() {
            this.isLoadingModels = true; // Start loading
            console.log("Processing models from store...");
            const zooModels = this.$store.state.modelsZoo; // Use computed property here
            const installedSet = new Set(this.$store.state.modelsArr);

             const createModelId = (model) => {
                 // Improved ID creation for stability
                 let base = model.id || model.name || model.filename || 'unknown';
                 if (model.quantizer) base += `-${model.quantizer}`;
                 if (model.variants && model.variants.length > 0 && model.variants[0].name) base += `-${model.variants[0].name}`;
                 else if (model.filename) base += `-${model.filename}`;
                 return base;
            };

             // Get the current operation's model ID *before* mapping, if any
             const currentProcessingModelId = this.downloadProgress.details?.model_id;

            const combinedModels = (zooModels || []).map(model => {
                const modelId = createModelId(model);
                return {
                    name: model.name,
                    author: model.author,
                    rank: model.rank,
                    quantizer: model.quantizer,
                    description: model.description,
                    license: model.license,
                    last_commit_time: model.last_commit_time,
                    variants: model.variants ? [...model.variants] : [],
                    filename: model.filename,
                    path: model.path,
                    type: model.type,
                    icon: model.icon || this.defaultIcon,
                    isInstalled: installedSet.has(model.name) || (model.variants && model.variants.some(v => installedSet.has(v.name))),
                     // Ensure isProcessing state persists across re-renders
                    isProcessing: (currentProcessingModelId === modelId && this.isDownloading) || false,
                    id: modelId
                };
            });

            this.$store.state.modelsArr.forEach(installedName => {
                const isInZoo = combinedModels.some(m =>
                    m.name === installedName || (m.variants && m.variants.some(v => v.name === installedName))
                );
                if (!isInZoo) {
                    const customModelId = installedName; // Use name as ID for local-only
                    combinedModels.push({
                        name: installedName,
                        isInstalled: true,
                        isProcessing: (currentProcessingModelId === customModelId && this.isDownloading) || false,
                        isCustomModel: true,
                        icon: this.defaultIcon,
                        id: customModelId,
                        rank: -1,
                        author: 'Local',
                    });
                }
            });

             this.allModels = combinedModels; // This assignment triggers the 'allModels' watcher

             // Setting loading false is now handled carefully within watchers and async operations
             // We set it false here only if no binding is selected initially or after clearing.
             // Otherwise, the end of async operations (like store refresh or install) should set it.
             if (!this.$store.state.config.binding_name) {
                this.isLoadingModels = false;
             }
             // If a binding IS selected, isLoadingModels will be set false by the installProgressListener
             // or the .then/.catch block in the binding watcher after store refreshes complete (via processAndCombineModels).
             // Add a final check here in case no operation is running and store is already populated.
             else if (!this.isDownloading && this.allModels.length > 0) {
                 // If we have models and aren't downloading, processing is done.
                  this.isLoadingModels = false;
             }

            console.log(`Processed ${this.allModels.length} total models. Loading state: ${this.isLoadingModels}`);
        },

        applyFiltersAndSort() {
            this.isSearching = true;
            console.time("FilterSortModels");
            let result = [...this.allModels];

            if (this.showInstalledOnly) {
                result = result.filter(m => m.isInstalled);
            }

            if (this.searchTerm) {
                const lowerSearch = this.searchTerm.toLowerCase();
                result = result.filter(m =>
                    m.name?.toLowerCase().includes(lowerSearch) ||
                    m.author?.toLowerCase().includes(lowerSearch) ||
                    m.quantizer?.toLowerCase().includes(lowerSearch) ||
                    m.description?.toLowerCase().includes(lowerSearch) ||
                    m.license?.toLowerCase().includes(lowerSearch)
                );
            }

            result.sort((a, b) => {
                if (a.isInstalled && !b.isInstalled) return -1;
                if (!a.isInstalled && b.isInstalled) return 1;
                switch (this.sortOption) {
                    case 'rank': return (b.rank ?? -Infinity) - (a.rank ?? -Infinity);
                    case 'name': return (a.name || '').localeCompare(b.name || '');
                    case 'last_commit_time': {
                        const dateA = a.last_commit_time ? new Date(a.last_commit_time) : null;
                        const dateB = b.last_commit_time ? new Date(b.last_commit_time) : null;
                        if (dateA && dateB) return dateB - dateA;
                        if (dateA) return -1; if (dateB) return 1; return 0;
                    }
                    case 'quantizer': return (a.quantizer || '').localeCompare(b.quantizer || '');
                    case 'license': return (a.license || '').localeCompare(b.license || '');
                    default: return 0;
                }
            });

            this.filteredModels = result;
            console.timeEnd("FilterSortModels");
            this.isSearching = false; // Filtering/sorting done
            console.log(`Filtered/Sorted models: ${this.filteredModels.length}`);
        },

        debounceSearch() {
            this.isSearching = true; // Indicate searching started
            clearTimeout(this.searchDebounceTimer);
            this.searchDebounceTimer = setTimeout(() => {
                 // The watcher for 'watchSources' will trigger applyFiltersAndSort
                 // No need to call it directly here.
                 // isSearching will be set to false within applyFiltersAndSort
            }, 500);
        },

        loadMoreModels() {
             // Prevent loading more if explicitly disabled or no more models exist
             if (this.isLoadingModels || this.isSearching || !this.hasMoreModelsToLoad) return;

             this.isLoadingModels = true; // Set loading state BEFORE potentially heavy operation
             console.log(`Loading page ${this.currentPage} for models`);

             // Use nextTick to allow the loading state to potentially update UI
             // before the potentially blocking push/render cycle starts
            nextTick(() => {
                const start = (this.currentPage - 1) * this.itemsPerPage;
                const end = start + this.itemsPerPage;
                const nextPageItems = this.filteredModels.slice(start, end);

                // Prevent adding duplicates if loadMore is triggered rapidly (unlikely with button)
                const newItems = nextPageItems.filter(newItem =>
                    !this.pagedModels.some(existingItem => (existingItem.id || existingItem.name) === (newItem.id || newItem.name))
                );

                if (newItems.length > 0) {
                    this.pagedModels.push(...newItems);
                    this.currentPage++;
                    nextTick(() => {
                        feather.replace(); // Replace icons after new items are rendered
                        this.isLoadingModels = false; // Reset loading state AFTER rendering cycle (approximately)
                    });
                } else {
                    // No new items were added, reset loading state
                    this.isLoadingModels = false;
                    if (nextPageItems.length === 0 && this.hasMoreModelsToLoad){
                        console.warn("Load more triggered but no new items found in slice.");
                    }
                }
             });
        },

        // --- Actions ---

        handleSelect(model) {
            console.log("Model selected in child:", model.name);
            if (this.isDownloading || this.isLoadingModels) {
                this.show_toast("Please wait for the current operation to finish.", 3, false); return;
            }
            if (!model.isInstalled) {
                this.show_toast(`Model "${model.name}" is not installed.`, 3, false); return;
            }
            // Directly compare with store state
            if (this.$store.state.config.model_name !== model.name) {
                this.$store.state.config.model_name = model.name
                this.show_toast(`Selecting model: ${model.name}...`, 2, true);
                this.isLoadingModels = true; // Show indicator during selection

                // IMPORTANT: Emit event for parent to update the store config
                // Do NOT mutate store directly (this.$store.state.config.model_name = model.name)
                this.$emit('settings-changed');

                // Simulate waiting for parent confirmation (remove in real app if parent updates quickly)
                // Check the store state *after* emitting to see if it changed
                setTimeout(() => {
                     // isLoadingModels should ideally be reset when the store change is confirmed
                     // or by the parent component. For now, reset it here.
                     this.isLoadingModels = false;
                     if (this.$store.state.config.model_name === model.name) {
                         console.log("Model selection confirmed in store.");
                         nextTick(feather.replace);
                     } else {
                         console.warn("Model selection change not reflected in store after emit and delay.");
                         // Optionally show error toast
                         // this.show_toast(`Failed to select ${model.name}.`, 4, false);
                     }
                 }, 500); // Adjust delay or remove if parent confirmation is faster
            }
        },

        handleInstall(payload) {
            const model = payload.model;
            console.log("Install requested for:", model.name);
            const variants = model.variants || [];

             if (model.isInstalled) {
                 this.show_toast(`Model "${model.name}" is already installed.`, 3, false); return;
             }
             if (this.isDownloading) {
                 this.show_toast("Another operation is already in progress.", 3, false); return;
             }

            if (variants.length > 0) {
                 // Ensure variant name exists and is unique for ID
                 this.variantSelectionDialog.choices = variants.map(v => ({
                     ...v,
                     id: v.name || `variant-${Math.random().toString(36).substring(7)}`, // Fallback ID
                     label: `${v.name || 'Unknown Variant'} (${filesize(v.size || 0)})`
                 }));
                 this.variantSelectionDialog.modelToInstall = model;
                 this.variantSelectionDialog.title = `Select variant for ${model.name}`;
                 this.variantSelectionDialog.visible = true;
            } else {
                 const filename = model.filename || model.name;
                 const quantizer = model.quantizer || 'Unknown';
                 const path = model.path || `https://huggingface.co/${model.author || quantizer}/${model.name}/resolve/main/${filename}`; // Use author if available
                this.startDownload(model, path, filename);
            }
        },

        handleVariantSelected(choice) {
            this.variantSelectionDialog.selectedVariant = choice;
        },

        handleVariantValidated(choice) {
            if (!choice || !this.variantSelectionDialog.modelToInstall) {
                this.closeVariantDialog(); return;
            }
            const model = this.variantSelectionDialog.modelToInstall;
            const variant = choice;
            const quantizer = model.quantizer || 'Unknown';
            // Construct path using variant details if available, otherwise assume HF structure
            const path = variant.path || `https://huggingface.co/${model.author || quantizer}/${model.name}/resolve/main/${variant.name}`;

            this.startDownload(model, path, variant.name);
            this.closeVariantDialog();
        },

        closeVariantDialog() {
            this.variantSelectionDialog.visible = false;
            this.variantSelectionDialog.choices = [];
            this.variantSelectionDialog.modelToInstall = null;
            this.variantSelectionDialog.selectedVariant = null;
        },

        startDownload(model, path, variantName) {
             const modelId = model.id || model.name; // Use the pre-calculated ID
            console.log(`Starting download: ${model.name}, Variant: ${variantName}, Path: ${path}, ID: ${modelId}`);

             if (this.isDownloading) {
                 this.show_toast("Another operation is in progress.", 3, false); return;
             }

             const currentBinding = this.$store.state.config.binding_name;
             if (!currentBinding) {
                 this.show_toast("No binding selected. Cannot install model.", 4, false); return;
             }

            this.setModelProcessing(modelId, true); // Update local state first
            this.isDownloading = true;
            this.isLoadingModels = true; // Show global loading
            this.downloadProgress = {
                visible: true,
                name: `Downloading ${model.name}${variantName !== model.name ? ` (${variantName})` : ''}`,
                progress: 0, speed: 0, total_size: 0, downloaded_size: 0,
                details: {
                    model_name: model.name,
                    binding_folder: currentBinding, // Use direct store access
                    model_url: path,
                    variant_name: variantName,
                    model_id: modelId, // Use the consistent ID
                    type: model.type || 'gguf'
                }
            };

            socket.emit('install_model', {
                path: path,
                name: model.name,
                variant_name: variantName,
                type: model.type || 'gguf',
                binding: currentBinding, // Use direct store access
                model_id: modelId // Pass the consistent ID
            });
            console.log("Install command sent via socket.");
        },

        async handleUninstall(payload) {
            const model = payload.model;
            const modelId = model.id || model.name;

            if (this.isDownloading) {
                 this.show_toast("Another operation is in progress.", 3, false); return;
             }

            const yes = await this.show_yes_no_dialog(`Uninstall model "${model.name}"?`, 'Uninstall', 'Cancel');
            if (!yes) return;

             const currentBinding = this.$store.state.config.binding_name;
             if (!currentBinding) {
                 this.show_toast("No binding selected. Cannot uninstall model.", 4, false); return;
             }

            console.log(`Starting uninstall for: ${model.name}, ID: ${modelId}`);
            this.setModelProcessing(modelId, true);
            this.isDownloading = true;
            this.isLoadingModels = true; // Show global loading
            this.downloadProgress = {
                 visible: true,
                 name: `Uninstalling ${model.name}...`,
                 progress: 50, // Indicate activity
                 speed: 0, total_size: 0, downloaded_size: 0,
                 details: { model_id: modelId, model_name: model.name, operation: 'uninstall', binding_folder: currentBinding }
            };

            socket.emit('uninstall_model', {
                name: model.name,
                type: model.type || 'gguf',
                binding: currentBinding, // Use direct store access
                model_id: modelId
            });
             console.log("Uninstall command sent via socket.");
        },

        handleCancelInstall(payload) {
             const details = payload?.model ? { // Try direct payload if from button click
                 model_name: payload.model.name,
                 binding_folder: this.$store.state.config.binding_name, // Use current binding
                 model_url: payload.model.path || 'unknown',
                 variant_name: payload.model.filename || payload.model.name,
                 model_id: payload.model.id || payload.model.name
             } : (this.downloadProgress.details || payload); // Fallback to global progress or direct details if passed

            if (!details || !details.model_id) {
                console.warn("Cancel requested but no details found or missing ID.");
                if (this.downloadProgress.visible) {
                    this.resetDownloadState(null, false); // Reset global state if visible
                }
                return;
            }
            console.log('Cancelling operation for:', details);

             // Ensure binding folder is present
             const bindingFolder = details.binding_folder || this.$store.state.config.binding_name;
             if (!bindingFolder) {
                 console.error("Cannot cancel, binding folder unknown.");
                 this.show_toast("Cannot cancel operation: Binding context missing.", 4, false);
                 return;
             }

             socket.emit('cancel_install', {
                 model_name: details.model_name,
                 binding_folder: bindingFolder,
                 model_url: details.model_url,
                 variant_name: details.variant_name,
                 model_id: details.model_id
             });
             // UI state reset is handled by the installProgressListener on failure/cancel message
        },

        handleCopy(payload) { /* ... unchanged ... */ },
        handleCopyLink(payload) { /* ... unchanged ... */ },

        async createReference() {
             if (!this.referencePath) {
                this.show_toast("Please enter a path.", 3, false); return;
             }
             if (this.isDownloading) {
                 this.show_toast("Another operation is in progress.", 3, false); return;
             }
             const currentBinding = this.$store.state.config.binding_name;
             if (!currentBinding) {
                 this.show_toast("No binding selected. Cannot add reference.", 4, false); return;
             }
            this.isLoadingModels = true; // Indicate activity
            try {
                const response = await this.api_post_req("add_reference_to_local_model", {
                     path: this.referencePath,
                     binding: currentBinding // Use direct store access
                });
                if (response.status) {
                    this.show_toast("Reference created.", 4, true);
                    this.referencePath = '';
                    this.$store.dispatch('refreshModels', { binding: currentBinding }); // Refresh installed list for the current binding
                } else {
                    this.show_toast(`Couldn't create reference: ${response.error || 'Unknown'}`, 4, false);
                     this.isLoadingModels = false; // Stop loading on handled error
                }
                 // processAndCombineModels triggered by watcher will set isLoadingModels = false on success
            } catch (error) {
                this.show_toast(`Error: ${error.message}`, 4, false);
                 this.isLoadingModels = false; // Stop loading on exception
            }
            // No finally block for isLoadingModels = false, let watchers handle it
        },

        installFromInput() {
             if (!this.modelUrl) {
                this.show_toast("Enter URL or HF ID.", 3, false); return;
             }
             if (this.isDownloading) {
                 this.show_toast("Another operation is in progress.", 3, false); return;
             }
             const currentBinding = this.$store.state.config.binding_name;
             if (!currentBinding) {
                 this.show_toast("No binding selected. Cannot install model.", 4, false); return;
             }

             let path = this.modelUrl.trim();
             let modelNameGuess = 'unknown_model';
             let variantNameGuess = 'unknown_variant';
             let typeGuess = 'gguf';
             let authorGuess = 'Unknown'; // Changed from quantizerGuess
             let modelId = path; // Temporary ID

             const hfIdRegex = /^([a-zA-Z0-9\-_.]+)\/([a-zA-Z0-9\-_.]+)(\/resolve\/main\/)?([a-zA-Z0-9\-_.]+\.(gguf|bin|safetensors))?$/;
             const hfIdMatch = path.match(hfIdRegex);
             const hfIdSimpleRegex = /^([a-zA-Z0-9\-_.]+)\/([a-zA-Z0-9\-_.]+)$/; // For repo only
             const hfIdSimpleMatch = path.match(hfIdSimpleRegex);


             if (hfIdMatch) { // Full HF path or partial path with file
                 authorGuess = hfIdMatch[1];
                 modelNameGuess = hfIdMatch[2];
                 variantNameGuess = hfIdMatch[4] || modelNameGuess; // Use filename if present, else model name
                 modelId = `${authorGuess}/${modelNameGuess}`; // Repo ID
                 if (!path.startsWith('http')) { // Ensure it's a full URL if needed by backend
                     path = `https://huggingface.co/${authorGuess}/${modelNameGuess}` + (hfIdMatch[3] ? hfIdMatch[3] : '/resolve/main/') + variantNameGuess;
                 }
                 typeGuess = hfIdMatch[5] || 'gguf'; // Extract type from extension
                 this.show_toast(`Detected HF Model: ${modelId}, File: ${variantNameGuess}`, 2, true);
             } else if (hfIdSimpleMatch && !path.startsWith('http')) { // Repo ID only
                 authorGuess = hfIdSimpleMatch[1];
                 modelNameGuess = hfIdSimpleMatch[2];
                 variantNameGuess = modelNameGuess; // Best guess
                 modelId = `${authorGuess}/${modelNameGuess}`;
                 path = `https://huggingface.co/${authorGuess}/${modelNameGuess}`; // Backend needs to handle repo download
                 this.show_toast(`Detected HF Repo ID: ${modelId}. Attempting download (may require variant selection).`, 2, true);
                 // Note: Backend might need to list files first if only repo ID is given
             } else if (path.startsWith('http')) {
                 try {
                    const url = new URL(path);
                    const pathParts = url.pathname.split('/').filter(p => p);
                    if (pathParts.length > 0) {
                        variantNameGuess = pathParts[pathParts.length - 1];
                        modelNameGuess = variantNameGuess.split('.')[0];
                        if (url.hostname === 'huggingface.co' && pathParts.length >= 2) {
                             authorGuess = pathParts[0]; // Assume author
                             modelNameGuess = pathParts[1]; // Assume model repo name
                             modelId = `${authorGuess}/${modelNameGuess}`;
                         } else { modelId = modelNameGuess; }
                         if (variantNameGuess.toLowerCase().endsWith('.safetensors')) typeGuess = 'safetensors';
                         else if (variantNameGuess.toLowerCase().endsWith('.bin')) typeGuess = 'bin'; // Add other types
                    } else { modelNameGuess = url.hostname; variantNameGuess = modelNameGuess; modelId = modelNameGuess; }
                 } catch (e) { this.show_toast("Invalid URL.", 4, false); return; }
             } else { this.show_toast("Invalid input. Use URL or HF ID (e.g., TheBloke/Llama-2-7B-GGUF).", 4, false); return; }

             const placeholderModel = {
                 name: modelNameGuess,
                 author: authorGuess,
                 type: typeGuess,
                 id: modelId, // Use the derived ID
                 filename: variantNameGuess, // Pass filename guess
                 path: path // Pass the original or constructed path
             };

             this.startDownload(placeholderModel, path, variantNameGuess);
             this.modelUrl = '';
        },

        imgPlaceholder(event) {
            event.target.src = this.defaultIcon;
        },

         setModelProcessing(modelId, state) {
             const indexAll = this.allModels.findIndex(m => (m.id || m.name) === modelId);
             if (indexAll !== -1) {
                 // Avoid direct mutation, create new object/array for reactivity
                 // Check if state actually needs changing
                 if (this.allModels[indexAll].isProcessing !== state) {
                     const updatedModel = { ...this.allModels[indexAll], isProcessing: state };
                     const newAllModels = [...this.allModels]; // Create new array reference
                     newAllModels[indexAll] = updatedModel;
                     this.allModels = newAllModels; // Trigger 'allModels' watcher
                     console.log(`Set processing ${state} for ${modelId}`);
                 }
             } else {
                 console.warn(`setModelProcessing: Model with ID ${modelId} not found in allModels.`);
             }
              // The allModels watcher handles updating filtered/paged models
         },

         resetDownloadState(modelId = null, success = false) {
             // Reset global progress bar
             if (!modelId || (this.downloadProgress.details && this.downloadProgress.details.model_id === modelId)) {
                 this.downloadProgress.visible = false;
                 this.downloadProgress.details = null; // Clear details
                 this.isDownloading = false; // Release global lock
             }
             // Update processing state for the specific model if ID provided
             if (modelId) {
                 this.setModelProcessing(modelId, false);
             }
             // Only set global loading false if not still loading other data
             if (!this.isDownloading && (!this.$store.state.config.binding_name || this.allModels.length > 0)) {
                this.isLoadingModels = false;
             }
             console.log(`Reset download state. Global loading: ${this.isLoadingModels}`);
         },

        installProgressListener(response) {
            console.log("Socket install_progress received:", response);
            const modelId = response.model_id || response.model_name; // Prefer model_id if available
            if (!modelId) { console.error("Progress msg missing ID:", response); return; }

            const currentOpModelId = this.downloadProgress.details?.model_id;

             // Ignore progress if it's not for the currently tracked operation
             if (this.isDownloading && modelId !== currentOpModelId) {
                 console.log(`Ignoring progress for ${modelId}, currently processing ${currentOpModelId}`);
                 return;
             }

             // Make sure we are tracking an operation
             if (!this.isDownloading && (response.status === 'progress' || response.status === 'downloading')) {
                 console.warn(`Received progress for ${modelId} but not in downloading state.`);
                 // Optionally try to recover state if details match, otherwise ignore
                 // return;
             }

             switch (response.status) {
                 case 'progress':
                 case 'downloading':
                     this.isLoadingModels = true; // Ensure global loading is active
                     if (!this.downloadProgress.visible) this.downloadProgress.visible = true; // Ensure visible
                     if (!this.downloadProgress.details) this.downloadProgress.details = { model_id: modelId }; // Ensure details exist
                     this.downloadProgress.name = response.message || `Processing ${response.model_name || modelId}...`;
                     this.downloadProgress.progress = response.progress || 0;
                     this.downloadProgress.speed = response.speed || 0;
                     this.downloadProgress.total_size = response.total_size || 0;
                     this.downloadProgress.downloaded_size = response.downloaded_size || 0;
                     // Ensure the model in the list shows processing
                     this.setModelProcessing(modelId, true);
                     break;
                 case 'succeeded': {
                     const operation = response.operation || (this.downloadProgress.details?.operation === 'uninstall' ? 'uninstall' : 'install');
                     this.show_toast(`"${response.model_name || modelId}" ${operation} succeeded!`, 4, true);
                     this.resetDownloadState(modelId, true); // Reset state on success
                     // Refresh the list of installed models
                     this.$store.dispatch('refreshModels', { binding: this.$store.state.config.binding_name });
                     // processAndCombineModels (via watcher) will update the view and set isLoadingModels = false
                     break;
                 }
                 case 'failed':
                 case 'cancelled': {
                     const operation = response.operation || this.downloadProgress.details?.operation || 'operation';
                     this.show_toast(`"${response.model_name || modelId}" ${operation} ${response.status}: ${response.error || 'Unknown reason'}`, 5, false);
                     this.resetDownloadState(modelId, false); // Reset state on failure/cancel
                      // No need to refresh store here, model state didn't change successfully
                     break;
                 }
                 default:
                     console.warn("Unknown progress status:", response.status);
             }
        },
    },
    async mounted() {
        console.log("updated")
        await this.$store.dispatch('refreshModelsZoo'),
        await this.$store.dispatch('refreshModels')        
        this.processAndCombineModels(); // Initial processing
        socket.on('install_progress', this.installProgressListener);
        nextTick(() => {
            feather.replace();
        });
        // If binding changes *before* mount, the watcher might need 'immediate: true'
        // or call the refresh logic here based on initial store state.
        if(this.$store.state.config.binding_name && this.allModels.length === 0 && !this.isLoadingModels){
             console.log("Mounted with binding but no models, triggering initial load check.");
             this.isLoadingModels = true; // Assume loading starts
             Promise.all([
                 this.$store.dispatch('refreshModelsZoo', { binding: this.$store.state.config.binding_name }),
                 this.$store.dispatch('refreshModels', { binding: this.$store.state.config.binding_name })
             ]).catch(error => {
                 console.error(`Error dispatching initial store refresh:`, error);
                 this.show_toast(`Failed initial load for ${this.$store.state.config.binding_name}.`, 5, false);
                 this.isLoadingModels = false;
             });
        }
    },
    unmounted() {
        socket.off('install_progress', this.installProgressListener);
        this.destroyIntersectionObserver();
        clearTimeout(this.searchDebounceTimer);
    },
    async updated() {        
        nextTick(() => {
            feather.replace();
        });
    }
};
</script>

<style scoped>
/* Styles remain identical */
.input-field {
     @apply block w-full px-3 py-2 text-sm bg-gray-50 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 focus:border-blue-500 dark:focus:ring-offset-gray-800 disabled:opacity-50;
}
.input-field-sm {
     @apply block w-full px-2.5 py-1.5 text-xs bg-gray-50 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 focus:border-blue-500 dark:focus:ring-offset-gray-800 disabled:opacity-50;
}
.setting-label-inline {
     @apply block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1;
}
.button-base-sm {
     @apply inline-flex items-center justify-center px-2.5 py-1.5 border border-transparent text-xs font-medium rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-offset-2 dark:focus:ring-offset-gray-800 disabled:opacity-50 transition-colors duration-150;
}
.button-primary-sm { @apply button-base-sm text-white bg-blue-600 hover:bg-blue-700 focus:ring-blue-500; }
.button-success-sm { @apply button-base-sm text-white bg-green-600 hover:bg-green-700 focus:ring-green-500; }
.button-danger-sm { @apply button-base-sm text-white bg-red-600 hover:bg-red-700 focus:ring-red-500; }

.model-grid-enter-active,
.model-grid-leave-active {
  transition: all 0.5s ease;
}
.model-grid-enter-from,
.model-grid-leave-to {
  opacity: 0;
  transform: translateY(15px);
}
.bg-primary-light { @apply bg-blue-100; }
.dark .bg-primary-dark\/20 { @apply dark:bg-blue-500/20; }
.border-primary-dark\/30 { @apply border-blue-500/30; }

[data-feather].w-4 { @apply inline-block align-middle; }
[data-feather].animate-spin { animation: spin 1s linear infinite; }
@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
</style>