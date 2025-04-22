<template>
    <div class="user-settings-panel space-y-6">
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

        <p class="text-sm text-blue-600 dark:text-blue-400">
             Select a model compatible with your chosen binding (<span class="font-semibold">{{ currentBindingNameComputed || 'None Selected' }}</span>). Installed models are shown first. Models may require specific variants (e.g., GGUF, GPTQ) depending on the binding.
        </p>
         <div v-if="!effectiveConfig.binding_name" class="p-3 text-center text-orange-600 dark:text-orange-400 bg-orange-100 dark:bg-orange-900/30 rounded-md border border-orange-300 dark:border-orange-600">
            Please select a Binding from the 'Bindings' section to see available models.
        </div>

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
                     <option value="provider">Sort by Quantizer</option>
                     <option value="license">Sort by License</option>
                 </select>
            </div>
        </div>

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

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4" ref="scrollContainer">
             <ModelEntry
                 v-for="model in pagedModels"
                :key="model.id"
                :model="model"
                :is-selected="config.model_name === model.name" 
                :is-installed="model.isInstalled"
                :is-processing="model.isProcessing"
                :progress="downloadProgress.details?.model_id === model.id ? downloadProgress.progress : 0"
                :speed="downloadProgress.details?.model_id === model.id ? downloadProgress.speed : 0"
                :total_size="downloadProgress.details?.model_id === model.id ? downloadProgress.total_size : 0"
                :downloaded_size="downloadProgress.details?.model_id === model.id ? downloadProgress.downloaded_size : 0"
                :progress-name="downloadProgress.details?.model_id === model.id ? downloadProgress.name : ''"
                @select="handleSelect"
                @install="handleInstall"
                @uninstall="handleUninstall"
                @cancel-install="handleCancelInstall"
                @copy="handleCopy"
                @copy-link="handleCopyLink"
             />
        </div>

        <div class="mt-6 text-center" v-if="hasMoreModelsToLoad">
            <button @click="loadMoreModels" :disabled="isLoadingModels || isSearching" class="btn btn-secondary">
                <span v-if="isLoadingModels || isSearching">
                    <svg aria-hidden="true" class="w-4 h-4 mr-1 inline animate-spin text-blue-400 dark:text-blue-500 fill-blue-600" viewBox="0 0 100 101" fill="none" xmlns="http://www.w3.org/2000/svg"> <path d="M100 50.5908C100 78.2051 77.6142 100.591 50 100.591C22.3858 100.591 0 78.2051 0 50.5908C0 22.9766 22.3858 0.59082 50 0.59082C77.6142 0.59082 100 22.9766 100 50.5908ZM9.08144 50.5908C9.08144 73.1895 27.4013 91.5094 50 91.5094C72.5987 91.5094 90.9186 73.1895 90.9186 50.5908C90.9186 27.9921 72.5987 9.67226 50 9.67226C27.4013 9.67226 9.08144 27.9921 9.08144 50.5908Z" fill="currentColor"/> <path d="M93.9676 39.0409C96.393 38.4038 97.8624 35.9116 97.0079 33.5539C95.2932 28.8227 92.871 24.3692 89.8167 20.348C85.8452 15.1192 80.8826 10.7238 75.2124 7.41289C69.5422 4.10194 63.2754 1.94025 56.7698 1.05124C51.7666 0.367541 46.6976 0.446843 41.7345 1.27873C39.2613 1.69328 37.813 4.19778 38.4501 6.62326C39.0873 9.04874 41.5694 10.4717 44.0505 10.1071C47.8511 9.54855 51.7191 9.52689 55.5402 10.0491C60.8642 10.7766 65.9928 12.5457 70.6331 15.2552C75.2735 17.9648 79.3347 21.5619 82.5849 25.841C84.9175 28.9121 86.7997 32.2913 88.1811 35.8758C89.083 38.2158 91.5421 39.6781 93.9676 39.0409Z" fill="currentFill"/> </svg>
                    Loading...
                </span>
                <span v-else>Load More Models ({{ filteredModels.length - pagedModels.length }} remaining)</span>
            </button>
        </div>

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
            :show="showVariantDialog"
            title="Select Your Model Variant"
            :items="modelVariants"
            itemDisplayField="name"  
            :canEdit="true"
            :canRemove="true"
            :canAdd="true"
            :choices="modelVariants"
            addInputPlaceholder="Enter new variant name..."
            :initialSelectedId="selectedVariantId"
            @item-selected="handleVariantSelected"
            @choice-validated="handleVariantValidated"
            @close-dialog="showVariantDialog = false"
            >
            <!-- Custom Rendering via Scoped Slot -->
            <template #choice-content="{ choice, isSelected }">
                <div class="flex items-center justify-between w-full">
                    <span
                        :class="{ 'font-semibold text-blue-600 dark:text-blue-400': isSelected }"
                        class="text-gray-800 dark:text-white truncate"
                        :title="choice.name"
                    >
                        {{ choice.name }}
                    </span>
                    <span v-if="choice.size !== undefined" class="text-xs text-gray-500 dark:text-gray-400 ml-2 flex-shrink-0">
                        ({{ formatFileSize(choice.size) }})
                    </span>
                </div>
            </template>
        </ChoiceDialog>
    </div>
</template>

<script>
import { nextTick } from 'vue';
import { useStore } from 'vuex';
import feather from 'feather-icons';
import filesize from '@/plugins/filesize';
import ModelEntry from '@/components/ModelEntry.vue';
import ChoiceDialog from '@/components/ChoiceDialog.vue';
import socket from '@/services/websocket.js';
import defaultModelIcon from "@/assets/default_model.png";

export default {
    name: 'ModelsZooSettings',
    components: {
        ModelEntry,
        ChoiceDialog
    },
    props: {
        config: { type: Object, required: true },
        loading: { type: Boolean, default: false },
        api_post_req: { type: Function, required: true },
        api_get_req: { type: Function, required: true },
        show_toast: { type: Function, required: true },
        show_yes_no_dialog: { type: Function, required: true },
        client_id: { type: String, required: true },
    },
    emits: ['setting-updated'],

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
            showDialog:false,
            downloadProgress: { visible: false, name: '', progress: 0, speed: 0, total_size: 0, downloaded_size: 0, details: null },
            showVariantDialog: false,
            selectedVariantId: null, // Store only the ID of the selected variant
            // Example data - Parent owns and manages this list
            modelVariants: [],        
            defaultIcon: defaultModelIcon,
            store: useStore() // Access store instance
        };
    },
    computed: {
        effectiveConfig() {
             return this.store.state.config || {};
        },
        storeModelsZoo() {
             return this.store.state.modelsZoo || [];
        },
        storeInstalledModelsArr() {
             return this.store.state.modelsArr || [];
        },
        storeBindingsZoo() {
            return this.store.state.bindingsZoo || [];
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
            return [ this.searchTerm, this.sortOption, this.showInstalledOnly, this.allModels ];
        }
    },
    watch: {
        '$store.state.config.binding_name': {
            async handler(newBinding, oldBinding) {
                if (newBinding !== oldBinding) {
                    this.isLoadingModels = true;
                    this.allModels = []; this.pagedModels = []; this.filteredModels = [];
                    this.searchTerm = ''; this.showInstalledOnly = false; this.currentPage = 1;

                    if (newBinding) {
                        // Data processing will be triggered by store watchers below
                    } else {
                        this.isLoadingModels = false;
                    }
                }
            },
        },
        '$store.state.modelsZoo': { handler() { this.processAndCombineModels(); }, deep: true },
        '$store.state.modelsArr': { handler() { this.processAndCombineModels(); }, deep: true },
        allModels: {
            handler(newModels, oldModels) {
                 if (JSON.stringify(newModels) !== JSON.stringify(oldModels)) {
                     this.currentPage = 1;
                     this.pagedModels = [];
                     this.applyFiltersAndSort();
                     this.$nextTick(() => {
                         this.loadMoreModels();
                     });
                 }
                 if (!this.isDownloading) {
                    this.isLoadingModels = false;
                 }
            },
        },
        watchSources: {
            handler(newVal, oldVal) {
                 if (newVal[0] !== oldVal[0] || newVal[1] !== oldVal[1] || newVal[2] !== oldVal[2]) {
                     this.currentPage = 1;
                     this.pagedModels = [];
                     this.applyFiltersAndSort();
                     this.$nextTick(() => {
                         this.loadMoreModels();
                     });
                 }
            },
        }
    },
    methods: {
        processAndCombineModels() {
            if (!this.effectiveConfig.binding_name) {
                this.allModels = [];
                this.isLoadingModels = false;
                return;
            }

            this.isLoadingModels = true;
            const zooModels = this.storeModelsZoo || [];
            const installedArray = this.storeInstalledModelsArr || [];
            const installedSet = new Set(installedArray);
            const currentProcessingModelId = this.downloadProgress.details?.model_id;
            console.log("zooModels")
            console.log(zooModels)

            const combined = zooModels.map(model => {
                const modelId = model.provider?model.provider+'/'+model.name:model.name;
                const isInstalledCheck = installedSet.has(model.name) || (model.variants && model.variants.some(v => installedSet.has(v.name)));
                return {
                    name: model.name,
                    author: model.author,
                    rank: model.rank ?? 9999, // Default rank if missing
                    provider: model.provider,
                    description: model.description,
                    license: model.license,
                    last_commit_time: model.last_commit_time,
                    variants: model.variants ? [...model.variants] : [],
                    filename: model.filename,
                    path: model.path,
                    type: model.type,
                    icon: model.icon || this.defaultIcon,
                    id: modelId,
                    isInstalled: isInstalledCheck,
                    isProcessing: (currentProcessingModelId === modelId && this.isDownloading) || false,
                    isCustomModel: false, // Mark models from the zoo
                };
            });

            const combinedNames = new Set(combined.map(m => m.name));
            combined.forEach(m => {
                 if (m.variants) m.variants.forEach(v => combinedNames.add(v.name));
            });


            installedArray.forEach(installedName => {
                if (!combinedNames.has(installedName)) {
                    const customModelId = "Local_Custom/"+installedName; // Use name for ID
                    combined.push({
                         name: installedName,
                         author: 'Local/Custom',
                         rank: -1, // Rank custom models high
                         provider: '',
                         description: 'Locally installed model reference.',
                         license: '',
                         last_commit_time: '',
                         variants: [],
                         filename: '',
                         path: '',
                         type: '',
                         icon: this.defaultIcon,
                         id: customModelId,
                         isInstalled: true,
                         isProcessing: (currentProcessingModelId === customModelId && this.isDownloading) || false,
                         isCustomModel: true,
                    });
                }
            });

            this.allModels = combined;
            // isLoadingModels will be set by the watcher or resetDownloadState
        },

        applyFiltersAndSort() {
             this.isSearching = true;
             let result = [...this.allModels];

             if (this.showInstalledOnly) {
                 result = result.filter(m => m.isInstalled);
             }

             if (this.searchTerm) {
                 const lowerSearch = this.searchTerm.toLowerCase();
                 result = result.filter(m =>
                     m.name?.toLowerCase().includes(lowerSearch) ||
                     m.author?.toLowerCase().includes(lowerSearch) ||
                     m.provider?.toLowerCase().includes(lowerSearch) ||
                     m.description?.toLowerCase().includes(lowerSearch) ||
                     m.license?.toLowerCase().includes(lowerSearch)
                 );
             }

            // Primary sort: Installed models first
            result.sort((a, b) => (b.isInstalled - a.isInstalled));

            // Secondary sort based on selection
             const sortOption = this.sortOption;
             result.sort((a, b) => {
                 // Keep installed status primary
                 const installedCompare = (b.isInstalled - a.isInstalled);
                 if (installedCompare !== 0) return installedCompare;

                 // Secondary sort logic
                 switch (sortOption) {
                    case 'rank':
                         // Lower rank is better. Handle potential nulls/undefineds
                         const rankA = a.rank ?? 9999;
                         const rankB = b.rank ?? 9999;
                         return rankA - rankB;
                    case 'name':
                         return (a.name || '').localeCompare(b.name || '');
                     case 'last_commit_time':
                          // Assuming ISO 8601 strings, newer first
                          const dateA = a.last_commit_time || '0';
                          const dateB = b.last_commit_time || '0';
                          return dateB.localeCompare(dateA); // Reversed for newer first
                     case 'provider':
                          return (a.provider || '').localeCompare(b.provider || '');
                     case 'license':
                          return (a.license || '').localeCompare(b.license || '');
                     default:
                          return 0; // Should not happen
                 }
             });

             this.filteredModels = result;
             this.isSearching = false;
        },

        debounceSearch() {
            this.isSearching = true; // Show spinner immediately
            clearTimeout(this.searchDebounceTimer);
            this.searchDebounceTimer = setTimeout(() => {
                // The watcher on `searchTerm` will trigger applyFiltersAndSort
                // We just need to turn off the spinner if the watcher doesn't run immediately
                // Or rely on applyFiltersAndSort to turn it off
                // For simplicity, let the applyFiltersAndSort in the watcher handle turning it off
            }, 300); // 300ms delay
        },

        loadMoreModels() {
            if (this.isLoadingModels || this.isSearching) return;

            const start = (this.currentPage - 1) * this.itemsPerPage;
            const end = start + this.itemsPerPage;
            const modelsToLoad = this.filteredModels.slice(start, end);

            if (modelsToLoad.length > 0) {
                 this.pagedModels.push(...modelsToLoad);
                 this.currentPage++;
            }
            this.replaceFeatherIcons();
        },

        handleSelect(payload) {
            const model = payload;
            if (this.isDownloading || this.isLoadingModels) {
                this.show_toast("Wait for current operation to finish.", 3, false);
                return;
            }
            if (!model.isInstalled) {
                this.show_toast(`Model "${model.name}" is not installed. Please install it first.`, 3, false);
                return;
            }
            if (this.config.model_name !== model.name) {
                 this.$emit('setting-updated', { key: 'model_name', value: model.name });
                 this.show_toast(`Selected model: ${model.name}. Remember to apply changes.`, 3, true);
            }
        },

        async handleInstall(payload) {
             const model = payload.model;
             if (this.isDownloading) { this.show_toast("Another operation is already in progress.", 3, false); return; }
             const currentBinding = this.effectiveConfig.binding_name;
             if (!currentBinding) { this.show_toast("No binding selected.", 4, false); return; }
             if (model.variants && model.variants.length > 0) {
                this.modelVariants=model.variants.map(v => ({ id: model.id + "::" + v.name, name: `${v.name} (${filesize(v.size || 0)})` }))
                this.showVariantDialog=true;
             } else {
                 const yes = await this.show_yes_no_dialog(`Install model "${model.name}"?`, 'Install', 'Cancel');
                 if (yes) {
                     this.startDownload(model.id); // Use path or name as identifier
                 }
             }
        },

        handleVariantSelected(choice) {
            this.variantSelectionDialog.selectedVariant = choice;
        },

        async handleVariantValidated(choice) {
            this.closeVariantDialog(); // Close dialog first

            const yes = await this.show_yes_no_dialog(`Install variant "${choice.id.split('::')[1]}" for model "${choice.id.split('::')[0]}"?`, 'Install', 'Cancel');
            if (yes) {
                // Pass variant info if needed, or just the name/path
                this.startDownload(choice.id);
            }
        },

        closeVariantDialog() {
            this.showVariantDialog = false;
        },

        startDownload(variant_id) {
            const model_id = variant_id.split("::")[0]
            this.setModelProcessing(variant_id, true);
            this.isDownloading = true;
            this.isLoadingModels = true; // Keep global loading indicator
            this.downloadProgress = {
                visible: true,
                name: `Installing ${model_id}...`,
                progress: 0,
                speed: 0,
                total_size: 0,
                downloaded_size: 0,
                details: { // Store details needed for cancellation/progress
                    model_id: model_id,
                    model_name: model_id, // Use the name being installed
                    path: model_id,
                    binding: this.effectiveConfig.binding_name,
                    client_id: this.client_id,
                 }
            };

            socket.emit('install_model', {
                 variant_id: variant_id
             });
        },

        async handleUninstall(payload) {
             const model = payload.model;
             const modelId = model.id ;
             if (this.isDownloading) {
                 this.show_toast("Another operation is in progress. Please wait.", 3, false);
                 return;
             }
             const yes = await this.show_yes_no_dialog(`Are you sure you want to uninstall the model "${model.name}"?`, 'Uninstall', 'Cancel');
             if (!yes) return;

             const currentBinding = this.effectiveConfig.binding_name;
             if (!currentBinding) {
                 this.show_toast("No binding selected. Cannot uninstall.", 4, false);
                 return;
             }

             this.setModelProcessing(modelId, true);
             this.isDownloading = true;
             this.isLoadingModels = true;
             this.downloadProgress = {
                 visible: true,
                 name: `Uninstalling ${model.name}...`,
                 progress: 0, // Indicate activity
                 speed: 0, total_size: 0, downloaded_size: 0,
                 details: { model_id: modelId, model_name: model.name } // Basic details for reset
             };

             socket.emit('uninstall_model', {
                 model_name: model.name, // Use the model name for backend identification
                 binding: currentBinding,
                 client_id: this.client_id,
                 model_id: modelId // Pass ID for frontend tracking
             });
        },

        handleCancelInstall(details) {
            console.log("received cancel request")
            if (!details || !this.isDownloading) return;
             // Send necessary info from 'details' for the backend to identify the process
             const payload = {
                 model_id: details.model_id, // ID used to start the install
                 model_path: details.path, // Path/ID sent to backend
                 binding: details.binding,
                 client_id: this.client_id
             };
            socket.emit('cancel_install', payload);
            this.show_toast(`Cancellation request sent for ${details.model_name}.`, 3, true);
            // Don't reset state immediately, wait for confirmation or timeout
        },

        handleCopy(payload) {
            navigator.clipboard.writeText(payload.text).then(() => {
                this.show_toast("Copied to clipboard!", 2, true);
            }).catch(err => {
                this.show_toast("Failed to copy text.", 4, false);
            });
        },

        handleCopyLink(payload) {
             navigator.clipboard.writeText(payload.link).then(() => {
                 this.show_toast("Model link copied!", 2, true);
             }).catch(err => {
                 this.show_toast("Failed to copy link.", 4, false);
             });
        },

        async createReference() {
             if (!this.referencePath) {
                 this.show_toast("Please enter a valid file or folder path.", 3, false);
                 return;
             }
             const currentBinding = this.effectiveConfig.binding_name;
             if (!currentBinding) {
                 this.show_toast("No binding selected. Cannot add reference.", 4, false);
                 return;
             }

             try {
                 this.isLoadingModels = true; // Indicate activity
                 const response = await this.api_post_req('add_reference', {
                     binding: currentBinding,
                     path: this.referencePath,
                     client_id: this.client_id
                 });
                 if (response && response.status === 'success') {
                     this.show_toast(response.message || "Reference added successfully.", 2, true);
                     this.referencePath = ''; // Clear input
                     // Manually trigger store refresh or wait for potential automatic updates
                     this.store.dispatch('refreshModels'); // Assuming such an action exists
                 } else {
                     this.show_toast(response.error || "Failed to add reference.", 4, false);
                 }
             } catch (error) {
                 this.show_toast(`Error adding reference: ${error.message || error}`, 4, false);
             } finally {
                 this.isLoadingModels = false; // Reset loading state
             }
        },

        installFromInput() {
            if (!this.modelUrl) {
                this.show_toast("Please enter a Model URL or Hugging Face ID.", 3, false);
                return;
            }
            if (this.isDownloading) {
                this.show_toast("Another operation is already in progress.", 3, false);
                return;
            }
            const currentBinding = this.effectiveConfig.binding_name;
            if (!currentBinding) {
                this.show_toast("No binding selected. Cannot download.", 4, false);
                return;
            }

             // Determine a placeholder name and ID
             const potentialName = this.modelUrl.split('/').pop() || this.modelUrl;
             const tempModelId = `download-${potentialName}-${Date.now()}`;

             this.isDownloading = true;
             this.isLoadingModels = true;
             this.setModelProcessing(tempModelId, true); // Use a temporary ID for processing state if needed
             this.downloadProgress = {
                 visible: true,
                 name: `Initiating install for ${potentialName}...`,
                 progress: 0, speed: 0, total_size: 0, downloaded_size: 0,
                 details: {
                     model_id: tempModelId, // Temporary ID
                     model_name: potentialName,
                     path: this.modelUrl, // The input URL/ID is the path here
                     binding: currentBinding,
                     client_id: this.client_id
                 }
             };

            socket.emit('install_model', {
                 model_path: this.modelUrl, // Send the URL/ID as the path
                 binding: currentBinding,
                 client_id: this.client_id,
                 model_id: tempModelId, // Pass temp ID for tracking
                 model_name: potentialName
             });
             this.modelUrl = ''; // Clear input after starting
        },

        imgPlaceholder(event) {
            event.target.src = this.defaultIcon;
        },

        setModelProcessing(variant_id, state) {
            // Update allModels immutably to trigger watchers properly
            const model_id = variant_id.split("::")[0]
            const indexAll = this.allModels.findIndex(m => m.id === model_id);
            if (indexAll !== -1) {
                 const updatedModel = { ...this.allModels[indexAll], isProcessing: state };
                 const newAllModels = [...this.allModels];
                 newAllModels[indexAll] = updatedModel;
                 this.allModels = newAllModels; // This triggers the watcher
            } else if (state) {
                 // Handle case where a temporary model (like from URL download) needs processing state
                 // This might require adding a temporary entry if not already done, or handling separately
            }

            // Update pagedModels directly for immediate UI feedback if visible
            const indexPaged = this.pagedModels.findIndex(m => m.id === model_id);
            if (indexPaged !== -1) {
                 // Avoid direct mutation if possible, but sometimes necessary for performance/simplicity
                 this.pagedModels[indexPaged].isProcessing = state;
            }
        },

        resetDownloadState(modelId = null, success = false) {
             const currentDetails = this.downloadProgress.details;
             if (modelId && currentDetails && currentDetails.model_id === modelId) {
                 this.setModelProcessing(modelId, false);
             }
             // Reset global state only if the completed/cancelled operation was the one being tracked
            if (!modelId || (currentDetails && currentDetails.model_id === modelId)) {
                 this.downloadProgress = { visible: false, name: '', progress: 0, speed: 0, total_size: 0, downloaded_size: 0, details: null };
                 this.isDownloading = false;
             }
             // Stop global loading only if no other download is active
             if (!this.isDownloading) {
                 this.isLoadingModels = false;
             }
             // Refresh lists if operation was successful
             if(success) {
                 this.store.dispatch('refreshModels'); // Assumes Vuex action exists
                 this.store.dispatch('refreshModelsZoo'); // Assumes Vuex action exists
             }
        },

        installProgressListener(response) {
            console.log("installProgressListener")
            console.log(response)
            const modelId = response.model_name; // ID sent back from backend
            const currentTrackedId = this.downloadProgress.details?.model_id;

            if (!modelId || modelId !== currentTrackedId) {
                // Progress update is not for the currently tracked operation, ignore or handle logging
                return;
            }

            if (response.status === 'progress') {
                this.downloadProgress.name = response.stage || `Processing ${response.model_name || 'model'}...`;
                this.downloadProgress.progress = response.progress || 0;
                this.downloadProgress.speed = response.speed || 0;
                this.downloadProgress.total_size = response.total_size || 0;
                this.downloadProgress.downloaded_size = response.downloaded_size || 0;
            } else if (response.status === 'cancelled') {
                this.show_toast(`Operation cancelled for ${this.downloadProgress.details?.model_name || 'model'}.`, 3, true);
                this.resetDownloadState(modelId, false);
            } else if (response.status === 'failed') {
                this.show_toast(response.error || `Operation failed for ${this.downloadProgress.details?.model_name || 'model'}.`, 4, false);
                this.resetDownloadState(modelId, false);
            } else if (response.status === 'success') {
                this.show_toast(response.message || `${this.downloadProgress.details?.model_name || 'Model'} operation successful.`, 2, true);
                this.resetDownloadState(modelId, true); // Mark as success for potential refresh
            } else if (response.status === 'processing') {
                 // Handle intermediate stages like 'extracting', 'verifying' etc.
                 this.downloadProgress.name = response.stage || `Processing ${response.model_name || 'model'}...`;
                 this.downloadProgress.progress = response.progress !== undefined ? response.progress : 100; // Show 100% if progress not specified but processing
            }
            this.replaceFeatherIcons();
        },

        replaceFeatherIcons() {
             nextTick(() => {
                 try {
                    feather.replace();
                 } catch (e) {
                    // Ignore errors if feather is not loaded or fails temporarily
                 }
             });
        }
    },
    mounted() {
        this.installProgressListener = this.installProgressListener.bind(this);
        socket.on('install_progress', this.installProgressListener);

        // Initial data processing if binding already exists
         if (this.effectiveConfig.binding_name) {
            this.processAndCombineModels();
         } else {
            this.isLoadingModels = false; // Not loading if no binding
         }
        this.replaceFeatherIcons();
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