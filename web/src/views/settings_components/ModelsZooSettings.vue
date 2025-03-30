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
            <div v-else-if="!bindingNameFromStore" class="text-sm font-medium text-orange-600 dark:text-orange-400 p-2 bg-orange-50 dark:bg-orange-900/20 rounded-md border border-orange-300 dark:border-orange-600 shrink-0">
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
         <div v-if="!bindingNameFromStore" class="p-3 text-center text-orange-600 dark:text-orange-400 bg-orange-50 dark:bg-orange-900/30 rounded-md border border-orange-200 dark:border-orange-700">
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
        <div v-else-if="pagedModels.length === 0 && filteredModels.length > 0" class="text-center text-gray-500 dark:text-gray-400 py-10"> <!-- Check filteredModels here -->
             No models found matching filters{{ searchTerm ? ' and search "' + searchTerm + '"' : '' }}.
        </div>
        <div v-else-if="allModels.length === 0 && !isLoadingModels && bindingNameFromStore" class="text-center text-gray-500 dark:text-gray-400 py-10"> <!-- Check allModels here -->
             No models available for the selected binding. Try adding a reference below.
        </div>


        <!-- Models Grid - Lazy Loaded -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4" ref="scrollContainer">
             <ModelEntry
                 v-for="model in pagedModels"
                :key="model.id || model.name"
                :model="model"
                :is-selected="modelNameFromStore === model.name"
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

<script>
import feather from 'feather-icons';
import filesize from '@/plugins/filesize';
import ModelEntry from '@/components/ModelEntry.vue';
import ChoiceDialog from '@/components/ChoiceDialog.vue'; // Assuming component exists
import socket from '@/services/websocket.js';
import defaultModelIcon from "@/assets/default_model.png"; // Default icon

export default {
    name: 'ModelsZoo',
    components: {
        ModelEntry,
        ChoiceDialog
    },
    props: {
        // config prop removed - will use this.$store.state.config
        api_post_req: { type: Function, required: true },
        api_get_req: { type: Function, required: true },
        show_toast: { type: Function, required: true },
        show_yes_no_dialog: { type: Function, required: true },
        client_id: { type: String, required: true }
    },
    emits: ['update:setting'],
    data() {
        return {
            allModels: [], // Holds the full list fetched from backend
            filteredModels: [], // Holds models after search/filter/sort
            pagedModels: [], // Holds the currently rendered models (for pagination/lazy load)
            isLoadingModels: false,
            isSearching: false, // Indicate background search/filter is happening
            searchTerm: '',
            sortOption: 'rank', // Default sort: rank
            showInstalledOnly: false,
            referencePath: '',
            modelUrl: '', // For the download input field
            isDownloading: false, // Tracks if *any* download is active
            itemsPerPage: 15, // How many models to load/show at a time
            currentPage: 1,
            searchDebounceTimer: null,
            observer: null, // IntersectionObserver instance
            // Reactive objects remain similar
            downloadProgress: {
                visible: false,
                name: '',
                progress: 0,
                speed: 0,
                total_size: 0,
                downloaded_size: 0,
                details: null // Store full model object or identifier
            },
            variantSelectionDialog: {
                visible: false,
                title: "Select Model Variant",
                choices: [],
                modelToInstall: null,
                selectedVariant: null
            },
            defaultIcon: defaultModelIcon // Make the import accessible in the template/methods
        };
    },
    computed: {
        // Access store state using this.$store.state
        bindingNameFromStore() {
            return this.$store.state.config.binding_name;
        },
        modelNameFromStore() {
            return this.$store.state.config.model_name;
        },
        currentBindingName() {
            return this.bindingNameFromStore || 'None Selected';
        },
        currentModelInfo() {
            if (!this.modelNameFromStore || this.allModels.length === 0) {
                return null;
            }
            const current = this.allModels.find(m => m.name === this.modelNameFromStore);
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
        // Computed property to aggregate watch sources
        watchSources() {
            return [
                this.searchTerm,
                this.sortOption,
                this.showInstalledOnly,
                this.bindingNameFromStore // Watch binding name from store
            ];
        }
    },
    watch: {
        // Watch the computed property aggregating the sources
        watchSources() {
            console.log("Filter/Sort/Binding changed, resetting page and applying filters.");
            this.currentPage = 1;
            this.pagedModels = []; // Clear current page
            this.applyFiltersAndSort(); // This will update filteredModels
            this.loadMoreModels(); // Load the first page of the new filtered list
        },
        // Watch the master list changing (e.g., after fetching or local update)
        allModels: {
            handler() {
                console.log("allModels changed, resetting page and applying filters.");
                 // Don't reset page if only 'isInstalled' or 'isProcessing' changed?
                 // Maybe only reset if length changes significantly or items are removed/added.
                 // For simplicity now, we re-filter and reload the first page on any deep change.
                this.currentPage = 1;
                this.pagedModels = [];
                this.applyFiltersAndSort();
                this.loadMoreModels();
            },
            deep: true // Use deep watch as model properties like 'installed' can change
        },
         // Watch binding name specifically to trigger fetchModels
         bindingNameFromStore(newBinding, oldBinding) {
             if (newBinding !== oldBinding) {
                console.log(`Binding changed from ${oldBinding} to ${newBinding}, fetching new models.`);
                 this.fetchModels(); // Fetch models when binding changes
                 // The 'watchSources' watcher will handle filtering/sorting/reloading page 1
             }
         }
    },
    methods: {
        async fetchModels() {
            const currentBinding = this.bindingNameFromStore; // Use computed property
            if (!currentBinding) {
                this.allModels = [];
                this.filteredModels = []; // Reset filtered list too
                this.pagedModels = []; // Reset paged list
                console.log("No binding selected, clearing models.");
                return;
            }
            this.isLoadingModels = true;
            console.log(`Fetching models for binding: ${currentBinding}`);
            try {
                // 1. Get Zoo models
                const zooModels = await this.api_get_req(`list_models?binding=${currentBinding}`);

                // 2. Get Installed models
                const installedModels = await this.api_get_req(`get_installed_models?binding=${currentBinding}`);
                const installedSet = new Set(installedModels.map(m => m.name)); // Efficient lookup

                // 3. Combine and Mark Installed Status
                const combinedModels = (zooModels || []).map(model => ({
                    ...model,
                    isInstalled: installedSet.has(model.name),
                    isProcessing: false, // For install/uninstall spinners
                    icon: model.icon || this.defaultIcon, // Assign default icon here
                    id: model.id || `${model.name}-${model.quantizer || ''}-${model.filename || ''}` // Create a more unique ID
                }));

                // 4. Add any installed models that weren't in the zoo list (custom references)
                installedModels.forEach(installedModel => {
                    if (!combinedModels.some(m => m.name === installedModel.name)) {
                        combinedModels.push({
                            ...installedModel,
                            name: installedModel.name,
                            isInstalled: true,
                            isProcessing: false,
                            isCustomModel: true, // Flag it as potentially custom
                            icon: installedModel.icon || this.defaultIcon, // Use provided icon or default
                            id: installedModel.id || installedModel.name // Unique ID
                        });
                    }
                });

                this.allModels = combinedModels;
                 // Don't reset pagination here, let the watcher handle it
                // this.currentPage = 1;
                // this.pagedModels = [];
                // this.applyFiltersAndSort();
                // this.loadMoreModels();
                console.log(`Fetched ${this.allModels.length} total models.`);

            } catch (error) {
                this.show_toast("Failed to load models.", 4, false);
                console.error("Error fetching models:", error);
                this.allModels = [];
                this.filteredModels = []; // Reset on error
                this.pagedModels = []; // Reset on error
            } finally {
                this.isLoadingModels = false;
                 // This should be triggered by the allModels watcher now
                // this.$nextTick(feather.replace);
            }
        },

        applyFiltersAndSort() {
            this.isSearching = true; // Indicate processing started
            console.time("FilterSortModels");

            let result = [...this.allModels];

            // 1. Filter by "Installed Only"
            if (this.showInstalledOnly) {
                result = result.filter(m => m.isInstalled);
            }

            // 2. Filter by Search Term
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

            // 3. Sort
            result.sort((a, b) => {
                if (a.isInstalled && !b.isInstalled) return -1;
                if (!a.isInstalled && b.isInstalled) return 1;

                switch (this.sortOption) {
                    case 'rank':
                        return (b.rank ?? -Infinity) - (a.rank ?? -Infinity);
                    case 'name':
                        return (a.name || '').localeCompare(b.name || '');
                    case 'last_commit_time': {
                        const dateA = a.last_commit_time ? new Date(a.last_commit_time) : null;
                        const dateB = b.last_commit_time ? new Date(b.last_commit_time) : null;
                        if (dateA && dateB) return dateB - dateA;
                        if (dateA) return -1;
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

            this.filteredModels = result;
            console.timeEnd("FilterSortModels");
            this.isSearching = false; // Indicate processing finished
            console.log(`Filtered/Sorted models: ${this.filteredModels.length}`);
        },

        debounceSearch() {
            this.isSearching = true; // Show spinner immediately on input
            clearTimeout(this.searchDebounceTimer);
            this.searchDebounceTimer = setTimeout(() => {
                 // The watcher 'watchSources' will trigger the filter/sort/load
                 // No need to call explicitly here anymore
                 // this.currentPage = 1;
                 // this.pagedModels = [];
                 // this.applyFiltersAndSort();
                 // this.loadMoreModels();
            }, 500); // Adjust debounce delay (ms) as needed
        },

        loadMoreModels() {
             if (this.isLoadingModels || this.isSearching) return; // Prevent loading during initial fetch or search debounce

             console.log(`Loading page ${this.currentPage} for models`);
             const start = (this.currentPage - 1) * this.itemsPerPage;
             const end = start + this.itemsPerPage;
             const nextPageItems = this.filteredModels.slice(start, end);

             // Check if items already exist to prevent duplicates during rapid triggers
             const newItems = nextPageItems.filter(newItem =>
                 !this.pagedModels.some(existingItem => (existingItem.id || existingItem.name) === (newItem.id || newItem.name))
             );

            if (newItems.length > 0) {
                 this.pagedModels.push(...newItems);
                 this.currentPage++;
                this.$nextTick(feather.replace); // Ensure icons render for new items
            } else if (nextPageItems.length > 0) {
                console.log("Skipping loadMoreModels, items might already be loaded.");
            }
        },

        handleSelect(model) {
            if (!model.isInstalled) {
                this.show_toast(`Model "${model.name}" is not installed.`, 3, false);
                return;
            }
            if (this.modelNameFromStore !== model.name) {
                this.show_toast(`Selecting model: ${model.name}...`, 2, true);
                // Emit the event to the parent to handle the state update via its own logic
                this.$emit('update:setting', { key: 'model_name', value: model.name });
            }
        },

        handleInstall(modelEntryData) {
            const model = modelEntryData.model;
            console.log("Initiating install for:", model);

            if (model.variants && model.variants.length > 0) {
                this.variantSelectionDialog.choices = model.variants.map(v => ({
                    ...v,
                    id: v.name, // Use variant name as unique ID for ChoiceDialog
                    label: `${v.name} (${filesize(v.size || 0)})`
                }));
                this.variantSelectionDialog.modelToInstall = model;
                this.variantSelectionDialog.visible = true;
            } else {
                // Construct path carefully, using filename if available
                const filename = model.filename || model.name; // Fallback to model name if filename is missing
                const quantizer = model.quantizer || 'Unknown'; // Handle missing quantizer
                const path = model.path || `https://huggingface.co/${quantizer}/${model.name}/resolve/main/${filename}`;
                this.startDownload(model, path, filename); // Pass the determined filename as variantName here
            }
        },

        handleVariantSelected(choice) {
            this.variantSelectionDialog.selectedVariant = choice;
        },

        handleVariantValidated(choice) {
            if (!choice || !this.variantSelectionDialog.modelToInstall) {
                console.error("No variant selected or model info missing.");
                this.closeVariantDialog();
                return;
            }
            const model = this.variantSelectionDialog.modelToInstall;
            const variant = choice;
            const quantizer = model.quantizer || 'Unknown';
            // Use variant.path if provided, otherwise construct from model/variant info
            const path = variant.path || `https://huggingface.co/${quantizer}/${model.name}/resolve/main/${variant.name}`;

            this.startDownload(model, path, variant.name); // Pass variant name
            this.closeVariantDialog();
        },

        closeVariantDialog() {
            this.variantSelectionDialog.visible = false;
            this.variantSelectionDialog.choices = [];
            this.variantSelectionDialog.modelToInstall = null;
            this.variantSelectionDialog.selectedVariant = null;
        },

        startDownload(model, path, variantName) {
             const modelId = model.id || model.name; // Use consistent identifier
            console.log(`Starting download for: ${model.name}, Variant: ${variantName}, Path: ${path}, ID: ${modelId}`);
            if (this.isDownloading) {
                this.show_toast("Another download is already in progress.", 3, false);
                return;
            }
            this.setModelProcessing(modelId, true);
            this.isDownloading = true;
            this.downloadProgress.visible = true;
            this.downloadProgress.name = `${model.name}${variantName !== model.name ? ` (${variantName})` : ''}`;
            this.downloadProgress.progress = 0;
            this.downloadProgress.speed = 0;
            this.downloadProgress.total_size = 0;
            this.downloadProgress.downloaded_size = 0;
            this.downloadProgress.details = {
                model_name: model.name,
                binding_folder: this.bindingNameFromStore, // Use store value
                model_url: path,
                variant_name: variantName,
                model_id: modelId // Use the consistent ID
            };

            socket.emit('install_model', {
                path: path,
                name: model.name,
                variant_name: variantName,
                type: model.type || 'gguf',
                binding: this.bindingNameFromStore // Use store value
            });
        },

        async handleUninstall(modelEntryData) {
            const model = modelEntryData.model;
            const modelId = model.id || model.name;
            const yes = await this.show_yes_no_dialog(`Are you sure you want to uninstall model "${model.name}"?`, 'Uninstall', 'Cancel');
            if (!yes) return;

            this.setModelProcessing(modelId, true);
            this.isDownloading = true; // Reuse flag to block other actions
            this.downloadProgress.visible = true;
            this.downloadProgress.name = `Uninstalling ${model.name}...`;
            this.downloadProgress.progress = 50;
            this.downloadProgress.details = { model_id: modelId };

            try {
                const response = await this.api_post_req('uninstall_model', {
                    name: model.name,
                    binding: this.bindingNameFromStore // Use store value
                });

                if (response && response.status) {
                    this.show_toast(`Model "${model.name}" uninstalled successfully.`, 4, true);
                    // Update local state immediately
                    const index = this.allModels.findIndex(m => (m.id || m.name) === modelId);
                    if (index !== -1) {
                        // Modify the existing object for reactivity (Vue 3 handles this better)
                        this.allModels[index].isInstalled = false;
                         // Trigger the watcher by creating a new array reference
                        this.allModels = [...this.allModels];
                    }
                     // The allModels watcher will handle re-filtering and pagination update
                } else {
                    this.show_toast(`Failed to uninstall model "${model.name}": ${response?.error || 'Unknown error'}`, 4, false);
                }
            } catch (error) {
                this.show_toast(`Error uninstalling model "${model.name}": ${error.message}`, 4, false);
                console.error(`Error uninstalling ${model.name}:`, error);
            } finally {
                // Reset state even if it wasn't the primary model being uninstalled
                const finalIndex = this.allModels.findIndex(m => (m.id || m.name) === modelId);
                if (finalIndex !== -1) {
                    this.setModelProcessing(modelId, false); // Ensure processing state is reset
                } else {
                     console.warn("Model not found after uninstall to reset processing state:", modelId);
                }
                this.downloadProgress.visible = false;
                this.isDownloading = false;
            }
        },

        handleCancelInstall(downloadDetails) {
             if (!downloadDetails) return;
             console.log('Cancelling install for:', downloadDetails);
             // Ensure all necessary details are present for the backend
             if (!downloadDetails.model_name || !downloadDetails.binding_folder || !downloadDetails.model_url || !downloadDetails.variant_name) {
                console.error("Cannot cancel install: Missing details.", downloadDetails);
                this.show_toast("Cannot cancel install: information missing.", 3, false);
                // Reset local state anyway?
                this.downloadProgress.visible = false;
                this.isDownloading = false;
                if (downloadDetails.model_id) {
                    this.setModelProcessing(downloadDetails.model_id, false);
                }
                return;
             }
             socket.emit('cancel_install', {
                 model_name: downloadDetails.model_name,
                 binding_folder: downloadDetails.binding_folder,
                 model_url: downloadDetails.model_url,
                 variant_name: downloadDetails.variant_name
                 // Add patreon if needed: patreon: downloadDetails.patreon
             });
             // State reset is handled by the 'install_progress' listener receiving a cancel/fail status
        },

        handleCopy(modelEntryData) {
            const model = modelEntryData.model;
            let content = `Model: ${model.name}\n`;
            if (model.quantizer) content += `Quantizer: ${model.quantizer}\n`;
            if (model.rank) content += `Rank: ${model.rank}\n`;
            if (model.license) content += `License: ${model.license}\n`;
            if (model.description) content += `Description: ${model.description}\n`;
            if (!model.isCustomModel && model.quantizer && model.name) content += `Link: https://huggingface.co/${model.quantizer}/${model.name}\n`;

            navigator.clipboard.writeText(content.trim())
                .then(() => this.show_toast("Model info copied!", 3, true))
                .catch(err => this.show_toast("Failed to copy info.", 3, false));
        },

        handleCopyLink(modelEntryData) {
            const model = modelEntryData.model;
            const link = model.isCustomModel ? `Local reference: ${model.name}` : (model.quantizer && model.name ? `https://huggingface.co/${model.quantizer}/${model.name}` : model.name);
            navigator.clipboard.writeText(link)
                .then(() => this.show_toast("Link copied!", 3, true))
                .catch(err => this.show_toast("Failed to copy link.", 3, false));
        },

        async createReference() {
            if (!this.referencePath) {
                this.show_toast("Please enter a path for the local model reference.", 3, false);
                return;
            }
            this.isLoadingModels = true; // Indicate activity
            try {
                // Backend needs the binding context, include it
                const response = await this.api_post_req("add_reference_to_local_model", {
                     path: this.referencePath,
                     binding: this.bindingNameFromStore
                });
                if (response.status) {
                    this.show_toast("Reference created successfully.", 4, true);
                    this.referencePath = ''; // Clear input
                    await this.fetchModels(); // Refresh the model list
                } else {
                    this.show_toast(`Couldn't create reference: ${response.error || 'Unknown error'}`, 4, false);
                }
            } catch (error) {
                this.show_toast(`Error creating reference: ${error.message}`, 4, false);
            } finally {
                this.isLoadingModels = false;
            }
        },

        installFromInput() {
             if (!this.modelUrl) {
                this.show_toast("Please enter a Model URL or Hugging Face ID.", 3, false);
                return;
             }

             let path = this.modelUrl.trim();
             let modelNameGuess = path;
             let modelQuantizerGuess = 'Unknown';
             let filenameGuess = null; // Try to determine filename

             // Check for Hugging Face ID format (e.g., TheBloke/Llama-2-7B-Chat-GGUF)
             const hfIdRegex = /^([a-zA-Z0-9\-_.]+)\/([a-zA-Z0-9\-_.]+)(\/resolve\/main\/([a-zA-Z0-9\-_.]+))?$/;
             const hfIdMatchSimple = path.match(/^([a-zA-Z0-9\-_.]+)\/([a-zA-Z0-9\-_.]+)$/);

             if (hfIdMatchSimple && !path.startsWith('http')) {
                 modelQuantizerGuess = hfIdMatchSimple[1];
                 modelNameGuess = hfIdMatchSimple[2];
                 // Cannot reliably guess filename from simple ID, backend needs to handle this or list variants
                 filenameGuess = modelNameGuess; // Best guess
                 path = `https://huggingface.co/${modelQuantizerGuess}/${modelNameGuess}`; // Base path for repo
                 console.log(`Detected HF ID: ${modelQuantizerGuess}/${modelNameGuess}. Backend needs to resolve filename/variants.`);
                 // Consider triggering variant selection if possible, or show message.
                 // For now, proceed with a guess.
                 this.show_toast("Detected Hugging Face ID. Attempting download (may require specific file selection on backend).", 2, true);

             } else if (path.startsWith('http')) {
                 // Assume it's a direct URL
                 try {
                    const url = new URL(path);
                    // Try to guess name from path segments
                    const pathParts = url.pathname.split('/').filter(p => p);
                    if (pathParts.length > 0) {
                        filenameGuess = pathParts[pathParts.length - 1]; // Last part as filename guess
                         // Maybe try to get model name from earlier parts if HF URL structure
                        if (url.hostname === 'huggingface.co' && pathParts.length >= 2) {
                             modelQuantizerGuess = pathParts[0];
                             modelNameGuess = pathParts[1];
                        } else {
                             modelNameGuess = filenameGuess; // Fallback
                        }
                    } else {
                        modelNameGuess = url.hostname; // Fallback
                        filenameGuess = modelNameGuess;
                    }
                 } catch (e) {
                     this.show_toast("Invalid URL provided.", 4, false);
                     return;
                 }
             } else {
                 this.show_toast("Invalid input. Use a full URL or Hugging Face ID (e.g., User/Model).", 4, false);
                 return;
             }

             const placeholderModel = {
                 name: modelNameGuess,
                 quantizer: modelQuantizerGuess,
                 type: 'gguf', // Assume GGUF or let backend determine
                 id: modelNameGuess, // Use name as temporary ID
                 filename: filenameGuess // Pass the guessed filename
             };

             // Use filenameGuess as the variantName for startDownload
             this.startDownload(placeholderModel, path, filenameGuess || modelNameGuess);
             this.modelUrl = ''; // Clear input after starting
        },

        imgPlaceholder(event) {
            event.target.src = this.defaultIcon; // Use data property
        },

        setModelProcessing(modelId, state) {
            const index = this.allModels.findIndex(m => (m.id || m.name) === modelId);
            if (index !== -1) {
                // Directly modify the property. Vue 3's reactivity handles this well for objects in arrays.
                 if (this.allModels[index].isProcessing !== state) {
                    this.allModels[index].isProcessing = state;
                    // Don't need to create new array reference just for this in Vue 3 Options API usually
                 }
            }
            // Also update pagedModels if the item exists there for immediate UI feedback
            const pagedIndex = this.pagedModels.findIndex(m => (m.id || m.name) === modelId);
            if (pagedIndex !== -1) {
                if (this.pagedModels[pagedIndex].isProcessing !== state) {
                    this.pagedModels[pagedIndex].isProcessing = state;
                }
            }
             // No $forceUpdate or $set typically needed here in Vue 3
        },

        // Socket listener method
        installProgressListener(response) {
            console.log("Socket install_progress received:", response);

            // Use model_id if provided, otherwise fallback to name (ensure consistency)
            const modelId = response.model_id || response.model_name;
             if (!modelId) {
                 console.error("Install progress message missing model identifier:", response);
                 return;
             }

             if (response.status === 'progress' || response.status === 'downloading') {
                 this.downloadProgress.visible = true;
                 this.downloadProgress.name = `${response.model_name}${response.variant_name && response.variant_name !== response.model_name ? ` (${response.variant_name})` : ''}`;
                 this.downloadProgress.progress = response.progress || 0;
                 this.downloadProgress.speed = response.speed || 0;
                 this.downloadProgress.total_size = response.total_size || 0;
                 this.downloadProgress.downloaded_size = response.downloaded_size || 0;
                 // Ensure the details object is consistent, especially the model_id
                 if (!this.downloadProgress.details || this.downloadProgress.details.model_id !== modelId) {
                     this.downloadProgress.details = {
                         model_name: response.model_name,
                         binding_folder: response.binding_folder || this.bindingNameFromStore, // Use current binding if missing
                         model_url: response.model_url,
                         variant_name: response.variant_name,
                         model_id: modelId // Store the consistent ID
                     };
                 }
                 this.setModelProcessing(modelId, true); // Make sure the model itself shows processing

             } else if (response.status === 'succeeded') {
                 this.show_toast(`Model "${response.model_name}" installed successfully!`, 4, true);
                 this.downloadProgress.visible = false;
                 this.isDownloading = false;
                 this.setModelProcessing(modelId, false);
                 // Update installed status in the main list
                 const index = this.allModels.findIndex(m => (m.id || m.name) === modelId);
                 if (index !== -1) {
                     this.allModels[index].isInstalled = true;
                     // Trigger watcher by creating new array reference
                     this.allModels = [...this.allModels];
                 } else {
                     // Maybe the model wasn't in the list before (e.g., installed from URL) - fetch again
                     console.log(`Model ${modelId} installed successfully, refetching list.`);
                    this.fetchModels();
                 }

             } else if (response.status === 'failed' || response.status === 'cancelled') {
                 this.show_toast(`Model "${response.model_name}" installation ${response.status}: ${response.error || ''}`, 4, false);
                 this.downloadProgress.visible = false;
                 this.isDownloading = false;
                 this.setModelProcessing(modelId, false);
             }
        },

        // --- Intersection Observer Methods ---
        setupIntersectionObserver() {
            if (this.observer) return; // Already setup

             const options = {
                 root: null, // Use the viewport
                 rootMargin: '100px 0px', // Load a bit before it enters viewport
                 threshold: 0 // Trigger as soon as it starts entering margin
             };

             this.observer = new IntersectionObserver((entries) => {
                 entries.forEach(entry => {
                     if (entry.isIntersecting && this.hasMoreModelsToLoad && !this.isLoadingModels && !this.isSearching) {
                         console.log("Intersection observer triggered: Loading more models.");
                         this.loadMoreModels();
                     }
                 });
             }, options);

             if (this.$refs.loadMoreTrigger) {
                 this.observer.observe(this.$refs.loadMoreTrigger);
                 console.log("IntersectionObserver observing loadMoreTrigger.");
             } else {
                 console.warn("Load more trigger element not found for IntersectionObserver setup.");
             }
        },

        destroyIntersectionObserver() {
            if (this.observer) {
                if (this.$refs.loadMoreTrigger) {
                    this.observer.unobserve(this.$refs.loadMoreTrigger);
                }
                this.observer.disconnect();
                this.observer = null;
                console.log("IntersectionObserver destroyed.");
            }
        }
    },
    mounted() {
        this.fetchModels(); // Initial fetch
        socket.on('install_progress', this.installProgressListener); // Use the method defined in 'methods'
        this.$nextTick(() => {
            feather.replace();
             // Setup observer after initial render
            this.setupIntersectionObserver();
        });
    },
    unmounted() {
        socket.off('install_progress', this.installProgressListener); // Unbind the listener
        this.destroyIntersectionObserver(); // Clean up observer
        clearTimeout(this.searchDebounceTimer.value); // Clear any pending debounce timer
    },
    updated() {
        // This lifecycle hook is called after data changes and the DOM re-renders.
        this.$nextTick(() => {
             // Re-apply feather icons if new icons were added
            feather.replace();
             // Ensure observer is still attached, especially if v-if might remove/add the trigger
             if (this.$refs.loadMoreTrigger && !this.observer) {
                console.log("Re-setting up IntersectionObserver in updated hook.");
                this.setupIntersectionObserver();
             } else if (!this.$refs.loadMoreTrigger && this.observer) {
                console.log("Trigger element removed, destroying IntersectionObserver in updated hook.");
                 this.destroyIntersectionObserver();
             }
        });
    }
};
</script>

<style scoped>
/* Styles remain identical to the Composition API version */
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

/* Ensure feather icons align vertically if needed */
[data-feather].w-4 {
    @apply inline-block align-middle;
}
</style>