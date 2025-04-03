<template>
    <div class="user-settings-panel space-y-6">
        <!-- Header Section -->
        <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center border-b border-blue-300 dark:border-blue-600 pb-3 mb-4">
            <h2 class="text-xl font-semibold text-blue-800 dark:text-blue-100 mb-2 sm:mb-0">
                Models Zoo
            </h2>
            <div v-if="currentModelInfoComputed" class="flex items-center gap-2 text-sm font-medium p-2 bg-blue-100 dark:bg-blue-800/50 rounded-md border border-blue-300 dark:border-blue-600 shrink-0 text-blue-700 dark:text-blue-200">
                 <img :src="currentModelInfoComputed.icon" @error="imgPlaceholder" class="w-6 h-6 rounded-lg object-cover flex-shrink-0" alt="Current Model Icon">
                 <span>Active: <span class="font-semibold">{{ currentModelInfoComputed.name }}</span></span>
            </div>
            <div v-else-if="!effectiveConfig.binding_name" class="text-sm font-medium text-orange-600 dark:text-orange-400 p-2 bg-orange-100 dark:bg-orange-900/30 rounded-md border border-orange-300 dark:border-orange-600 shrink-0">
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
         <div v-if="!effectiveConfig.binding_name" class="p-3 text-center text-orange-600 dark:text-orange-400 bg-orange-100 dark:bg-orange-900/30 rounded-md border border-orange-300 dark:border-orange-600">
            Please select a Binding from the 'Bindings' section to see available models.
        </div>

        <!-- Controls: Search, Filters, Sort -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4 items-center">
            <div class="relative md:col-span-2">
                 <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <i data-feather="search" class="w-5 h-5 text-blue-400 dark:text-blue-500"></i>
                </div>
                 <input
                    type="search"
                    v-model="searchTerm"
                    placeholder="Search models..."
                    class="input search-input pl-10 w-full"
                    @input="debounceSearch"
                />
                 <div v-if="isSearching" class="absolute inset-y-0 right-0 pr-3 flex items-center">
                     <svg aria-hidden="true" class="w-5 h-5 text-blue-400 animate-spin dark:text-blue-500 fill-blue-600" viewBox="0 0 100 101" fill="none" xmlns="http://www.w3.org/2000/svg"> <path d="M100 50.5908C100 78.2051 77.6142 100.591 50 100.591C22.3858 100.591 0 78.2051 0 50.5908C0 22.9766 22.3858 0.59082 50 0.59082C77.6142 0.59082 100 22.9766 100 50.5908ZM9.08144 50.5908C9.08144 73.1895 27.4013 91.5094 50 91.5094C72.5987 91.5094 90.9186 73.1895 90.9186 50.5908C90.9186 27.9921 72.5987 9.67226 50 9.67226C27.4013 9.67226 9.08144 27.9921 9.08144 50.5908Z" fill="currentColor"/> <path d="M93.9676 39.0409C96.393 38.4038 97.8624 35.9116 97.0079 33.5539C95.2932 28.8227 92.871 24.3692 89.8167 20.348C85.8452 15.1192 80.8826 10.7238 75.2124 7.41289C69.5422 4.10194 63.2754 1.94025 56.7698 1.05124C51.7666 0.367541 46.6976 0.446843 41.7345 1.27873C39.2613 1.69328 37.813 4.19778 38.4501 6.62326C39.0873 9.04874 41.5694 10.4717 44.0505 10.1071C47.8511 9.54855 51.7191 9.52689 55.5402 10.0491C60.8642 10.7766 65.9928 12.5457 70.6331 15.2552C75.2735 17.9648 79.3347 21.5619 82.5849 25.841C84.9175 28.9121 86.7997 32.2913 88.1811 35.8758C89.083 38.2158 91.5421 39.6781 93.9676 39.0409Z" fill="currentFill"/> </svg>
                 </div>
            </div>
            <div class="flex items-center space-x-2">
                 <label for="model-filter-installed" class="flex items-center space-x-1 cursor-pointer text-sm label">
                    <input type="checkbox" id="model-filter-installed" v-model="showInstalledOnly" class="rounded text-blue-600 focus:ring-blue-500 border-blue-300 dark:border-blue-600 bg-blue-100 dark:bg-blue-700 focus:ring-offset-blue-100 dark:focus:ring-offset-blue-800">
                     <span>Installed Only</span>
                 </label>
            </div>
            <div>
                 <label for="model-sort" class="sr-only">Sort models by</label>
                 <select id="model-sort" v-model="sortOption" class="input">
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
        <div v-else-if="allModels.length === 0 && !isLoadingModels && effectiveConfig.binding_name" class="text-center text-blue-500 dark:text-blue-400 py-10">
             No models available for the selected binding. Try adding a reference or downloading below.
        </div>

        <!-- Models Grid -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4" ref="scrollContainer">
             <ModelEntry
                 v-for="model in pagedModels"
                :key="model.id || model.name"
                :model="model"
                :is-selected="config.model_name === model.name" 
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

        <!-- Load More Button -->
        <div class="mt-6 text-center" v-if="hasMoreModelsToLoad">
            <button @click="loadMoreModels" :disabled="isLoadingModels || isSearching" class="btn btn-secondary">
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
                 <div>
                     <label for="reference_path" class="label mb-1">Add Reference to Local Model File/Folder</label>
                     <div class="flex">
                         <input type="text" id="reference_path" v-model="referencePath" class="input input-sm rounded-r-none flex-grow" placeholder="Enter full path...">
                         <button @click="createReference" class="btn btn-primary btn-sm rounded-l-none flex-shrink-0" title="Add Reference">Add</button>
                     </div>
                     <p class="text-xs text-blue-500 dark:text-blue-400 mt-1">Creates a link without copying the model.</p>
                 </div>
                 <div>
                     <label for="model_url" class="label mb-1">Download Model from URL or Hugging Face ID</label>
                     <div class="flex">
                        <input type="text" id="model_url" v-model="modelUrl" class="input input-sm rounded-r-none flex-grow" placeholder="Enter URL or HF ID...">
                        <button @click="installFromInput" class="btn btn-success btn-sm rounded-l-none flex-shrink-0" title="Download and Install" :disabled="isDownloading">
                             <i :data-feather="isDownloading ? 'loader' : 'download'" :class="['w-4 h-4', isDownloading ? 'animate-spin' : '']"></i>
                         </button>
                     </div>
                    <p class="text-xs text-blue-500 dark:text-blue-400 mt-1">Downloads the model to the binding's models folder.</p>
                 </div>
             </div>
             <div v-if="downloadProgress.visible" class="mt-4 p-3 bg-blue-100 dark:bg-blue-900/30 border border-blue-200 dark:border-blue-700 rounded-md">
                 <div class="flex justify-between items-center mb-1">
                     <span class="text-sm font-medium text-blue-700 dark:text-blue-300"> {{ downloadProgress.name }}</span>
                     <span class="text-xs font-medium text-progress">{{ downloadProgress.progress.toFixed(1) }}%</span>
                 </div>
                 <div class="animated-progressbar-bg h-1.5">
                    <div class="animated-progressbar-fg h-1.5 rounded-full" :style="{ width: downloadProgress.progress + '%' }"></div>
                 </div>
                 <div class="flex justify-between items-center mt-1 text-xs text-progress">
                     <span>{{ downloadedSizeComputed }} / {{ totalSizeComputed }}</span>
                     <span>{{ speedComputed }}/s</span>
                 </div>
                 <button @click="handleCancelInstall(downloadProgress.details)" class="btn btn-secondary btn-sm mt-2 text-xs text-red-500 dark:text-red-400 hover:bg-red-200 dark:hover:bg-red-700">Cancel Operation</button>
             </div>
         </section>

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
import { useStore } from 'vuex'; // Import useStore
import feather from 'feather-icons';
import filesize from '@/plugins/filesize';
import ModelEntry from '@/components/ModelEntry.vue';
import ChoiceDialog from '@/components/ChoiceDialog.vue';
import socket from '@/services/websocket.js';
import defaultModelIcon from "@/assets/default_model.png";

export default {
    name: 'ModelsZooSettings', // Changed name
    components: {
        ModelEntry,
        ChoiceDialog
    },
    props: {
        config: { type: Object, required: true }, // The editable config from parent
        loading: { type: Boolean, default: false },
        api_post_req: { type: Function, required: true },
        api_get_req: { type: Function, required: true },
        show_toast: { type: Function, required: true },
        show_yes_no_dialog: { type: Function, required: true },
        client_id: { type: String, required: true },
    },
    emits: ['setting-updated'], // Emits updates for parent

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
            downloadProgress: { visible: false, name: '', progress: 0, speed: 0, total_size: 0, downloaded_size: 0, details: null },
            variantSelectionDialog: { visible: false, title: "Select Model Variant", choices: [], modelToInstall: null, selectedVariant: null },
            defaultIcon: defaultModelIcon
        };
    },
    setup(props) {
         // Cannot use setup with Options API's data/computed/methods/etc.
         // We will use Options API structure fully.
    },
    computed: {
        // Use store state for applied config checks and data
        effectiveConfig() {
             return this.$store.state.config || {};
        },
        storeModelsZoo() {
             return this.$store.state.modelsZoo || [];
        },
        storeInstalledModelsArr() {
             return this.$store.state.modelsArr || [];
        },
        storeBindingsZoo() {
            return this.$store.state.bindingsZoo || [];
        },

        currentBindingNameComputed() {
            const currentBindingFolder = this.effectiveConfig.binding_name;
            if (!currentBindingFolder) return 'None Selected';
            const binding = this.storeBindingsZoo.find(b => b.folder === currentBindingFolder);
            return binding ? binding.name : currentBindingFolder;
        },

        currentModelInfoComputed() {
            const currentModelName = this.effectiveConfig.model_name;
            if (!currentModelName || this.allModels.length === 0) return null;
            const current = this.allModels.find(m => m.name === currentModelName);
            return current ? { name: current.name, icon: current.icon || this.defaultIcon } : null;
        },

        hasMoreModelsToLoad() {
            return this.pagedModels.length < this.filteredModels.length;
        },
        speedComputed() { return filesize(this.downloadProgress.speed || 0); },
        totalSizeComputed() { return filesize(this.downloadProgress.total_size || 0); },
        downloadedSizeComputed() { return filesize(this.downloadProgress.downloaded_size || 0); },

        watchSources() {
            // Watch local filters and the main processed list
            return [ this.searchTerm, this.sortOption, this.showInstalledOnly, this.allModels ];
        }
    },
    watch: {
        // Watch the *applied* binding name from the store
        '$store.state.config.binding_name': {
            async handler(newBinding, oldBinding) {
                if (newBinding !== oldBinding) {
                    this.isLoadingModels = true;
                    this.allModels = []; this.pagedModels = []; this.filteredModels = [];
                    this.searchTerm = ''; this.showInstalledOnly = false; this.currentPage = 1;

                    if (newBinding) {
                         // Rely on parent to have triggered store refreshes
                         // We just need to wait for those to complete, which the watchers below handle.
                         // This watcher mainly resets local state for the UI.
                         console.log(`Binding watcher: Binding changed to ${newBinding}, resetting local state.`);
                    } else {
                        this.isLoadingModels = false; // No binding, no loading needed
                    }
                }
            },
            // immediate: true // Run on load if necessary
        },
        // Watch the store's model lists
        '$store.state.modelsZoo': { handler() { this.processAndCombineModels(); }, deep: true },
        '$store.state.modelsArr': { handler() { this.processAndCombineModels(); }, deep: true },

        // Watch combined/processed list
        allModels: {
            handler(newModels, oldModels) {
                // Only apply filters if the array content actually changes
                // Avoid infinite loops if processAndCombineModels triggers this watcher unnecessarily
                 if (JSON.stringify(newModels) !== JSON.stringify(oldModels)) {
                     console.log("Processed allModels changed, applying filters/sort.");
                     this.currentPage = 1;
                     this.pagedModels = [];
                     this.applyFiltersAndSort(); // This populates filteredModels
                     this.loadMoreModels();     // This populates pagedModels from filteredModels
                 }
                 // Ensure loading stops once models are processed (unless downloading)
                 if (this.allModels.length > 0 && !this.isDownloading) {
                     this.isLoadingModels = false;
                 }
            },
             // deep: true // Deep watcher might be too expensive here, rely on reference change
        },
        // Watch local filters
        watchSources: {
            handler(newVal, oldVal) {
                 // Check if filters actually changed (excluding allModels check handled above)
                 if (newVal[0] !== oldVal[0] || newVal[1] !== oldVal[1] || newVal[2] !== oldVal[2]) {
                     console.log("Filters changed, resetting page and applying.");
                     this.currentPage = 1;
                     this.pagedModels = [];
                     this.applyFiltersAndSort();
                     this.loadMoreModels();
                 }
            },
             // deep: false // No need for deep here as we watch the array ref
        }
    },
    methods: {
        processAndCombineModels() {
            if (!this.effectiveConfig.binding_name) {
                this.allModels = []; // Clear if no binding
                this.isLoadingModels = false;
                return;
            }

            console.log("Reprocessing models list...");
            this.isLoadingModels = true; // Set loading true during processing
            const zooModels = this.storeModelsZoo;
            const installedSet = new Set(this.storeInstalledModelsArr);
            const createModelId = (model) => { /* ... same ID logic ... */ };
            const currentProcessingModelId = this.downloadProgress.details?.model_id;

            const combined = (zooModels || []).map(model => {
                const modelId = createModelId(model);
                const isInstalledCheck = installedSet.has(model.name) || (model.variants && model.variants.some(v => installedSet.has(v.name)));
                return {
                    /* ... model properties ... */
                    name: model.name, author: model.author, rank: model.rank, quantizer: model.quantizer,
                    description: model.description, license: model.license, last_commit_time: model.last_commit_time,
                    variants: model.variants ? [...model.variants] : [], filename: model.filename, path: model.path,
                    type: model.type, icon: model.icon || this.defaultIcon, id: modelId,
                    isInstalled: isInstalledCheck,
                    isProcessing: (currentProcessingModelId === modelId && this.isDownloading) || false,
                };
            });

            this.storeInstalledModelsArr.forEach(installedName => {
                const isInZoo = combined.some(m => m.name === installedName || (m.variants && m.variants.some(v => v.name === installedName)));
                if (!isInZoo) {
                    const customModelId = installedName;
                    combined.push({
                        /* ... custom model properties ... */
                         name: installedName, isInstalled: true, isCustomModel: true, icon: this.defaultIcon,
                         id: customModelId, rank: -1, author: 'Local',
                         isProcessing: (currentProcessingModelId === customModelId && this.isDownloading) || false,
                    });
                }
            });

            // Update the data property, this will trigger the allModels watcher
            this.allModels = combined;

            // isLoadingModels will be set to false by the watcher or install listener
            console.log(`Finished processing ${this.allModels.length} models.`);
        },

        applyFiltersAndSort() {
             this.isSearching = true; // Indicate filtering/sorting is happening
             console.time("FilterSortModels");
             let result = [...this.allModels]; // Start with the processed list
             if (this.showInstalledOnly) result = result.filter(m => m.isInstalled);
             if (this.searchTerm) {
                 const lowerSearch = this.searchTerm.toLowerCase();
                 result = result.filter(m =>
                     m.name?.toLowerCase().includes(lowerSearch) || m.author?.toLowerCase().includes(lowerSearch) ||
                     m.quantizer?.toLowerCase().includes(lowerSearch) || m.description?.toLowerCase().includes(lowerSearch) ||
                     m.license?.toLowerCase().includes(lowerSearch)
                 );
             }
             result.sort((a, b) => { /* ... same sorting logic ... */ });
             this.filteredModels = result; // Update the filtered list
             console.timeEnd("FilterSortModels");
             this.isSearching = false; // Done filtering/sorting
             console.log(`Filtered/Sorted models: ${this.filteredModels.length}`);
        },

        debounceSearch() { /* ... same logic ... */ },
        loadMoreModels() { /* ... same logic ... */ },

        handleSelect(model) {
            if (this.isDownloading || this.isLoadingModels) { this.show_toast("Wait for current operation.", 3, false); return; }
            if (!model.isInstalled) { this.show_toast(`Model "${model.name}" not installed.`, 3, false); return; }
            // Only emit if different from the *editable* config
            if (this.config.model_name !== model.name) {
                 this.$emit('setting-updated', { key: 'model_name', value: model.name });
                 this.show_toast(`Selected model: ${model.name}. Apply changes.`, 3, true);
            }
        },
        handleInstall(payload) { /* ... unchanged, uses props/local state ... */ },
        handleVariantSelected(choice) { /* ... unchanged ... */ },
        handleVariantValidated(choice) { /* ... unchanged ... */ },
        closeVariantDialog() { /* ... unchanged ... */ },
        startDownload(model, path, variantName) { /* ... unchanged, uses props/local state/socket ... */ },
        async handleUninstall(payload) {
             const model = payload.model; const modelId = model.id || model.name;
             if (this.isDownloading) { this.show_toast("Operation in progress.", 3, false); return; }
             const yes = await this.show_yes_no_dialog(`Uninstall "${model.name}"?`, 'Uninstall', 'Cancel');
             if (!yes) return;
             const currentBinding = this.effectiveConfig.binding_name; // Use applied binding
             if (!currentBinding) { this.show_toast("No binding selected.", 4, false); return; }

             this.setModelProcessing(modelId, true); this.isDownloading = true; this.isLoadingModels = true;
             this.downloadProgress = { /* ... progress state ... */ };

             socket.emit('uninstall_model', { /* ... payload ... */ });
        },
        handleCancelInstall(payload) { /* ... unchanged, uses props/local state/socket ... */ },
        handleCopy(payload) { navigator.clipboard.writeText(payload.text); this.show_toast("Copied", 3, true); },
        handleCopyLink(payload) { navigator.clipboard.writeText(payload.link); this.show_toast("Link copied", 3, true); },
        async createReference() { /* ... unchanged, uses props/local state ... */ },
        installFromInput() { /* ... unchanged, uses props/local state ... */ },
        imgPlaceholder(event) { /* ... unchanged ... */ },

        setModelProcessing(modelId, state) {
             const indexAll = this.allModels.findIndex(m => (m.id || m.name) === modelId);
             if (indexAll !== -1 && this.allModels[indexAll].isProcessing !== state) {
                 // Update the item in the array immutably to trigger watcher
                 const newAllModels = [...this.allModels];
                 newAllModels[indexAll] = { ...newAllModels[indexAll], isProcessing: state };
                 this.allModels = newAllModels; // This triggers the 'allModels' watcher
             }
             // Update pagedModels directly for immediate UI feedback if the item is visible
             const indexPaged = this.pagedModels.findIndex(m => (m.id || m.name) === modelId);
             if (indexPaged !== -1 && this.pagedModels[indexPaged].isProcessing !== state) {
                  this.pagedModels[indexPaged].isProcessing = state;
             }
        },

        resetDownloadState(modelId = null, success = false) {
             if (!modelId || (this.downloadProgress.details && this.downloadProgress.details.model_id === modelId)) {
                 this.downloadProgress.visible = false; this.downloadProgress.details = null; this.isDownloading = false;
             }
             if (modelId) this.setModelProcessing(modelId, false);
             // Only stop global loading if no longer downloading AND models are processed/available
             if (!this.isDownloading && (!this.effectiveConfig.binding_name || this.allModels.length > 0)) {
                 this.isLoadingModels = false;
             }
        },

        installProgressListener(response) { /* ... same logic ... */ },

        replaceFeatherIcons() {
             nextTick(() => { try { feather.replace(); } catch (e) {} });
        }
    },
    mounted() {
        // Fetch initial lists from store or API - rely on watchers now
        // this.processAndCombineModels(); // Initial processing if store has data
        this.installProgressListener = this.installProgressListener.bind(this); // Ensure correct 'this'
        socket.on('install_progress', this.installProgressListener);
        this.replaceFeatherIcons();
        // Trigger initial model processing if binding already exists
         if (this.effectiveConfig.binding_name) {
            this.processAndCombineModels();
         }
    },
    unmounted() {
        socket.off('install_progress', this.installProgressListener);
        clearTimeout(this.searchDebounceTimer);
    },
    updated() {
        this.replaceFeatherIcons();
    }
};
</script>

<style scoped>
/* Styles remain the same */
.input { @apply block w-full px-3 py-2 bg-gray-50 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 focus:border-blue-500 dark:focus:ring-offset-gray-900 sm:text-sm disabled:opacity-50 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500; }
.input-sm { @apply block w-full px-2.5 py-1.5 text-sm bg-gray-50 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 focus:border-blue-500 dark:focus:ring-offset-gray-900 sm:text-sm disabled:opacity-50 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500; }
.label { @apply block text-sm font-medium text-gray-700 dark:text-gray-300; }
.btn { @apply inline-flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-offset-2 dark:focus:ring-offset-gray-900 disabled:opacity-50 transition-colors duration-150 whitespace-nowrap; }
.btn-sm { @apply px-2.5 py-1.5 text-xs; }
.btn-primary { @apply text-white bg-blue-600 hover:bg-blue-700 focus:ring-blue-500 ; }
.btn-secondary { @apply text-gray-700 dark:text-gray-200 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 focus:ring-blue-500 border-gray-300 dark:border-gray-500; }
.btn-success { @apply text-white bg-green-600 hover:bg-green-700 focus:ring-green-500 ; }
.text-progress { @apply text-blue-600 dark:text-blue-400; }
.animated-progressbar-bg { @apply w-full bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden; }
.animated-progressbar-fg { @apply bg-blue-600 dark:bg-blue-500 transition-all duration-300 ease-linear; }
.text-loading { @apply text-blue-600 dark:text-blue-300; }
.search-input { /* inherits .input */ }
.scrollbar::-webkit-scrollbar { width: 8px; height: 8px; }
.scrollbar::-webkit-scrollbar-track { @apply bg-gray-100 dark:bg-gray-700 rounded-lg; }
.scrollbar::-webkit-scrollbar-thumb { @apply bg-gray-300 dark:bg-gray-500 rounded-lg; }
.scrollbar::-webkit-scrollbar-thumb:hover { @apply bg-gray-400 dark:bg-gray-400; }
</style>