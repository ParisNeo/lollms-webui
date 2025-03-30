<template>
    <div class="space-y-6 p-4 md:p-6 bg-white dark:bg-gray-800 rounded-lg shadow-md border border-gray-200 dark:border-gray-700">
        <!-- Header -->
        <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center border-b border-gray-200 dark:border-gray-700 pb-3 mb-4">
            <h2 class="text-xl font-semibold text-gray-800 dark:text-gray-200 mb-2 sm:mb-0">
                Binding Zoo
            </h2>
            <!-- Current Binding Display -->
            <!-- Use props.config directly -->
            <div v-if="currentBindingInfo" class="flex items-center gap-2 text-sm font-medium p-2 bg-primary-light dark:bg-primary-dark/20 rounded-md border border-primary-dark/30">
                <img :src="getIconPath(currentBindingInfo.icon)" @error="imgPlaceholder" class="w-6 h-6 rounded-full object-cover flex-shrink-0" alt="Current Binding Icon">
                <span>Active: <span class="font-semibold">{{ currentBindingInfo.name }}</span></span>

                <button @click="handleSettings($store.state.config.binding_name)" :disabled="isLoadingAction || loading" class="ml-2 p-1 rounded-full hover:bg-primary-dark/20 focus:outline-none focus:ring-2 focus:ring-primary-dark/50 disabled:opacity-50 disabled:cursor-not-allowed" title="Configure Active Binding">
                    <i data-feather="settings" class="w-4 h-4"></i>
                </button>
                 <button @click="handleReload($store.state.config.binding_name)" :disabled="isLoadingAction || loading" class="ml-1 p-1 rounded-full hover:bg-primary-dark/20 focus:outline-none focus:ring-2 focus:ring-primary-dark/50 disabled:opacity-50 disabled:cursor-not-allowed" title="Reload Active Binding">
                    <i data-feather="refresh-cw" class="w-4 h-4"></i>
                </button>
            </div>
            <div v-else class="text-sm font-medium text-red-600 dark:text-red-400 p-2 bg-red-50 dark:bg-red-900/20 rounded-md border border-red-300 dark:border-red-600">
                No binding selected!
            </div>
        </div>

        <p class="text-sm text-gray-500 dark:text-gray-400">
            Bindings are the engines that run the AI models. Select an installed binding to enable model selection and generation.
        </p>

        <!-- Search and Sort Controls -->
        <div class="flex flex-col sm:flex-row gap-4 mb-4">
            <!-- Search Input -->
            <div class="relative flex-grow">
                <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <i data-feather="search" class="w-5 h-5 text-gray-400"></i>
                </div>
                <input
                    type="search"
                    v-model="searchTerm"
                    placeholder="Search bindings by name or author..."
                    class="input-field pl-10 w-full"
                    aria-label="Search bindings"
                    :disabled="isLoadingBindings || loading"
                />
            </div>
            <!-- Sort Select -->
            <div class="flex-shrink-0">
                 <label for="binding-sort" class="sr-only">Sort bindings by</label>
                 <select id="binding-sort" v-model="sortOption" class="input-field" aria-label="Sort bindings by" :disabled="isLoadingBindings || loading">
                     <option value="name">Sort by Name</option>
                     <option value="author">Sort by Author</option>
                     <option value="status">Sort by Status</option>
                </select>
            </div>
        </div>

        <!-- Bindings Grid -->
        <div v-if="isLoadingBindings" class="flex justify-center items-center p-10">
             <!-- Spinner SVG -->
             <svg aria-hidden="true" role="status" class="w-8 h-8 text-gray-300 animate-spin dark:text-gray-600 fill-primary" viewBox="0 0 100 101" fill="none" xmlns="http://www.w3.org/2000/svg"> <path d="M100 50.5908C100 78.2051 77.6142 100.591 50 100.591C22.3858 100.591 0 78.2051 0 50.5908C0 22.9766 22.3858 0.59082 50 0.59082C77.6142 0.59082 100 22.9766 100 50.5908ZM9.08144 50.5908C9.08144 73.1895 27.4013 91.5094 50 91.5094C72.5987 91.5094 90.9186 73.1895 90.9186 50.5908C90.9186 27.9921 72.5987 9.67226 50 9.67226C27.4013 9.67226 9.08144 27.9921 9.08144 50.5908Z" fill="currentColor"/> <path d="M93.9676 39.0409C96.393 38.4038 97.8624 35.9116 97.0079 33.5539C95.2932 28.8227 92.871 24.3692 89.8167 20.348C85.8452 15.1192 80.8826 10.7238 75.2124 7.41289C69.5422 4.10194 63.2754 1.94025 56.7698 1.05124C51.7666 0.367541 46.6976 0.446843 41.7345 1.27873C39.2613 1.69328 37.813 4.19778 38.4501 6.62326C39.0873 9.04874 41.5694 10.4717 44.0505 10.1071C47.8511 9.54855 51.7191 9.52689 55.5402 10.0491C60.8642 10.7766 65.9928 12.5457 70.6331 15.2552C75.2735 17.9648 79.3347 21.5619 82.5849 25.841C84.9175 28.9121 86.7997 32.2913 88.1811 35.8758C89.083 38.2158 91.5421 39.6781 93.9676 39.0409Z" fill="currentFill"/> </svg>
            <span class="ml-2 text-gray-500 dark:text-gray-400">Loading bindings...</span>
        </div>
        <div v-else-if="sortedBindings.length === 0" class="text-center text-gray-500 dark:text-gray-400 py-10">
            No bindings found{{ searchTerm ? ' matching "' + searchTerm + '"' : '' }}.
        </div>
        <!-- Grid rendering -->
        <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <BindingEntry
                v-for="binding_item in sortedBindings"  
                :key="binding_item.folder"              
                :binding="binding_item"               
                :selected="config?.binding_name === binding_item.folder" 
                :is-processing="binding_item.isProcessing" 
                @select="handleSelect"        
                @install="handleInstall"       
                @uninstall="handleUninstall"   
                @reinstall="handleReinstall"   
                @settings="handleSettingsFromEntry" 
                @reload-binding="handleReloadFromEntry" 
            />
        </div>
         <!-- Save/Cancel Footer REMOVED - Parent handles this -->
    </div>
</template>

<script>
import { nextTick } from 'vue';
import feather from 'feather-icons';
import BindingEntry from '@/components/BindingEntry.vue'; // Ensure this path is correct
import defaultBindingIcon from "@/assets/default_binding.png"; // Ensure this path is correct

export default {
    name: 'BindingZooSettings', // Changed name to avoid conflict if used elsewhere
    components: {
        BindingEntry
    },
    props: {
        loading: { type: Boolean, default: false }, // Parent loading state
        // settings-changed prop removed as it's handled by emits now
        api_get_req: { type: Function, required: true },
        api_post_req: { type: Function, required: true },
        refresh_config: { type: Function, required: true },
        show_toast: { type: Function, required: true },
        show_yes_no_dialog: { type: Function, required: true },
        show_message_box: { type: Function, required: true }, // Added based on parent call
        client_id: { type: String, required: true },
        show_universal_form: { type: Function, required: true },
    },
    emits: ['update:setting', 'settings-changed'], // Declare emitted events

    data() {
        return {
            bindings: [], // Holds the list of binding objects
            isLoadingBindings: false, // Loading state specifically for fetching bindings
            isLoadingAction: false, // Loading state for actions like install, uninstall, settings, reload
            sortOption: 'name', // Default sort option
            searchTerm: '', // Search term input
        };
    },

    computed: {
        currentBindingInfo() {
            // Use prop config
            if (!this.$store.state.config || !this.$store.state.config.binding_name || this.bindings.length === 0) {
                return null;
            }
            const current = this.bindings.find(b => b.folder === this.$store.state.config.binding_name);
            return current;
        },

        sortedBindings() {
            if (!this.bindings) return [];

            let filtered = [...this.bindings];

            // Filter by search term
            if (this.searchTerm) {
                const lowerSearch = this.searchTerm.toLowerCase();
                filtered = filtered.filter(b =>
                    b.name?.toLowerCase().includes(lowerSearch) ||
                    b.author?.toLowerCase().includes(lowerSearch) ||
                    b.description?.toLowerCase().includes(lowerSearch) ||
                    b.folder?.toLowerCase().includes(lowerSearch)
                );
            }

            // Sort
            filtered.sort((a, b) => {
                switch (this.sortOption) {
                    case 'status':
                        if (a.installed && !b.installed) return -1;
                        if (!a.installed && b.installed) return 1;
                        return (a.name || '').localeCompare(b.name || '');
                    case 'author':
                        return (a.author || '').localeCompare(b.author || '');
                    case 'name':
                    default:
                        return (a.name || '').localeCompare(b.name || '');
                }
            });

            return filtered;
        }
    },

    methods: {
        // Helper to construct full icon path
        getIconPath(iconRelativePath) {
            console.log(`iconRelativePath: ${iconRelativePath}`)
            if (!iconRelativePath) return defaultBindingIcon;
            // Ensure bUrl is correctly prepended only if needed (check if iconRelativePath already has http)
            if (iconRelativePath.startsWith('http')) {
                return iconRelativePath;
            }
            const icon = "/"+iconRelativePath.replace(/\\/g, '/');
            console.log(`icon: ${icon}`)
            return icon;
        },

        // Method for the image error handler
        imgPlaceholder(event) {
            event.target.src = defaultBindingIcon;
        },

        // Use prop function for API GET requests
        async internal_api_get_req(endpoint, params = {}) {
            try {
                 // Add client_id if not present, assuming the prop function doesn't do it automatically
                 const fullParams = { client_id: this.client_id, ...params };
                 // Await the promise returned by the prop function
                 return await this.api_get_req(endpoint, fullParams);
            } catch (error) {
                console.error(`API GET error for ${endpoint}:`, error);
                 this.show_toast(`API Error: ${error.message || 'Failed to fetch data'}`, 4, false);
                throw error; // Re-throw to allow caller handling if needed
            }
        },

        // Use prop function for API POST requests
        async internal_api_post_req(endpoint, data = {}) {
            try {
                // Add client_id if not present, assuming the prop function doesn't do it automatically
                const fullData = { client_id: this.client_id, ...data };
                // Await the promise returned by the prop function
                 return await this.api_post_req(endpoint, fullData);
            } catch (error) {
                console.error(`API POST error for ${endpoint}:`, error);
                 this.show_toast(`API Error: ${error.message || 'Action failed'}`, 4, false);
                throw error; // Re-throw to allow caller handling if needed
            }
        },

        async fetchBindings() {
            this.isLoadingBindings = true;
            try {
                // Use internal wrapper which uses the prop function
                const response = await this.internal_api_get_req('list_bindings');
                // Assume response is the array directly now
                this.bindings = (response || []).map(b => ({ ...b, isProcessing: false }));
            } catch (error) {
                // Error already shown by internal_api_get_req
                this.bindings = [];
            } finally {
                this.isLoadingBindings = false;
                nextTick(feather.replace);
            }
        },

        setBindingProcessing(folder, state) {
            const index = this.bindings.findIndex(b => b.folder === folder);
            if (index !== -1) {
                // Vue 2 reactivity might need $set, Vue 3 handles this automatically
                 this.bindings[index].isProcessing = state;
            }
        },

        handleSelect(binding) {
            console.log("received selection of binding")
            console.log(binding)
            if (!binding || !binding.folder) {
                 console.error("Invalid binding data received in handleSelect:", binding);
                 this.show_toast("Internal error: Invalid binding data.", 4, false);
                 return;
            }
            if (!binding.installed) {
                this.show_toast(`Binding "${binding.name}" is not installed.`, 3, false);
                return;
            }
            // Use prop config
            if (this.$store.state.config.binding_name !== binding.name) {
                this.$store.state.config.binding_name = binding.name
                this.$store.state.config.model_name = null
                // Emit events for parent to handle state update
                this.$emit('settings-changed', true); // Inform parent about the change
                this.show_toast(`Selected binding: ${binding.name}`, 3, true);
            }
        },

        async handleInstall(binding) {
             if (!binding || !binding.folder) {
                 console.error("Invalid binding data received in handleInstall:", binding);
                 this.show_toast("Internal error: Invalid binding data.", 4, false);
                 return;
            }
            let proceed = true;
            if (binding.disclaimer) {
                // Use prop function
                proceed = await this.show_yes_no_dialog(`Disclaimer for ${binding.name}:\n\n${binding.disclaimer}\n\nProceed with installation?`, 'Proceed', 'Cancel');
            }
            if (!proceed) return;

            this.setBindingProcessing(binding.folder, true);
            this.isLoadingAction = true;
            try {
                // Use internal wrapper
                const response = await this.internal_api_post_req('install_binding', { name: binding.folder });
                if (response && response.status) {
                    // Use prop function
                    this.show_toast(`Binding "${binding.name}" installed successfully! Reload recommended.`, 5, true);
                    await this.fetchBindings(); // Refresh internal list
                } else {
                     this.show_toast(`Failed to install "${binding.name}": ${response?.error || 'Unknown error'}`, 4, false);
                }
            } catch (error) {
                 // Error handled by internal_api_post_req
            } finally {
                this.setBindingProcessing(binding.folder, false);
                this.isLoadingAction = false;
                nextTick(feather.replace);
            }
        },

        async handleUninstall(binding) {
             if (!binding || !binding.folder) {
                 console.error("Invalid binding data received in handleUninstall:", binding);
                 this.show_toast("Internal error: Invalid binding data.", 4, false);
                 return;
            }
            // Use prop function
            const yes = await this.show_yes_no_dialog(`Uninstall "${binding.name}"?\nThis removes its files.`, 'Uninstall', 'Cancel');
            if (!yes) return;

            this.setBindingProcessing(binding.folder, true);
            this.isLoadingAction = true;
            try {
                 // Use internal wrapper - ensure correct endpoint name
                const response = await this.internal_api_post_req('uninstall_binding', { name: binding.folder });
                if (response && response.status) {
                    this.show_toast(`Binding "${binding.name}" uninstalled successfully!`, 4, true);
                    await this.fetchBindings(); // Refresh internal list
                    // If active binding was uninstalled, inform parent
                    if (this.$store.state.config.binding_name === binding.folder) {
                        this.$store.state.config.binding_name = null
                        this.$store.state.config.model_name = null
                        this.$emit('settings-changed', true);
                        this.refresh_config(); // Trigger parent refresh
                    }
                } else {
                     this.show_toast(`Failed to uninstall "${binding.name}": ${response?.error || 'Unknown error'}`, 4, false);
                }
            } catch (error) {
                 // Error handled by internal_api_post_req
            } finally {
                this.setBindingProcessing(binding.folder, false);
                this.isLoadingAction = false;
                nextTick(feather.replace);
            }
        },

        async handleReinstall(binding) {
              if (!binding || !binding.folder) {
                 console.error("Invalid binding data received in handleReinstall:", binding);
                 this.show_toast("Internal error: Invalid binding data.", 4, false);
                 return;
            }
             // Use prop function
            const yes = await this.show_yes_no_dialog(`Reinstall "${binding.name}"?\nThis overwrites files.`, 'Reinstall', 'Cancel');
            if (!yes) return;

            this.setBindingProcessing(binding.folder, true);
            this.isLoadingAction = true;
            try {
                 // Use internal wrapper
                const response = await this.internal_api_post_req('reinstall_binding', { name: binding.folder });
                if (response && response.status) {
                    this.show_toast(`Binding "${binding.name}" reinstalled successfully! Reload recommended.`, 5, true);
                    await this.fetchBindings(); // Refresh internal list
                } else {
                     this.show_toast(`Failed to reinstall "${binding.name}": ${response?.error || 'Unknown error'}`, 4, false);
                }
            } catch (error) {
                 // Error handled by internal_api_post_req
            } finally {
                this.setBindingProcessing(binding.folder, false);
                this.isLoadingAction = false;
                nextTick(feather.replace);
            }
        },

        handleSettingsFromEntry(binding) {
              if (!binding || !binding.folder) {
                 console.error("Invalid binding data in handleSettingsFromEntry:", binding);
                 this.show_toast("Internal error: Invalid binding data.", 4, false);
                 return;
             }
            this.handleSettings(binding.folder);
        },

        async handleSettings(bindingFolder) {
             if (!bindingFolder) {
                this.show_toast("No binding specified.", 3, false);
                return;
            }
            const targetBinding = this.bindings.find(b => b.folder === bindingFolder);
            if (!targetBinding) {
                this.show_toast(`Binding "${bindingFolder}" not found.`, 4, false);
                return;
            }
            if (!targetBinding.installed) {
                 this.show_toast(`"${targetBinding.name}" is not installed.`, 3, false);
                 return;
            }
            // Use prop config
            if (bindingFolder !== this.$store.state.config.binding_name) {
                this.show_toast(`Select "${targetBinding.name}" first to configure it.`, 4, false);
                return;
            }

            this.isLoadingAction = true;
            try {
                // Use internal wrapper
                const settingsData = await this.internal_api_post_req('get_active_binding_settings');

                if (settingsData && Object.keys(settingsData).length > 0) {
                    const bindingName = targetBinding.name || bindingFolder;
                    // Use prop function for form
                    const result = await this.show_universal_form(settingsData, `Settings - ${bindingName}`, "Save", "Cancel");

                    if (result !== null && result !== undefined) { // Form submitted
                        // Use internal wrapper
                        const setResponse = await this.internal_api_post_req('set_active_binding_settings', { settings: result });
                        if (setResponse && setResponse.status) {
                            this.show_toast(`Settings for "${bindingName}" updated. Reloading...`, 4, true);
                            // Use internal wrapper
                            await this.internal_api_post_req('update_binding_settings');
                            this.show_toast(`Binding "${bindingName}" reloaded with new settings.`, 4, true);
                            // No need to emit 'settings-changed' here as parent likely handles config persistence globally
                            this.$emit('settings-changed', true);
                            this.refresh_config(); // Tell parent to refresh state
                        } else {
                             this.show_toast(`Failed to update settings for "${bindingName}": ${setResponse?.error || 'Unknown error'}`, 4, false);
                        }
                    } else { // Form cancelled
                        this.show_toast(`Settings update for "${bindingName}" cancelled.`, 3, false);
                    }
                } else if (settingsData && Object.keys(settingsData).length === 0) {
                     this.show_toast(`"${targetBinding.name}" has no settings.`, 4, false);
                } else {
                     this.show_toast(`Could not get settings for "${targetBinding.name}".`, 4, false);
                }
            } catch (error) {
                 // Error handled by internal_api_post_req or show_universal_form
            } finally {
                this.isLoadingAction = false;
                nextTick(feather.replace);
            }
        },

        handleReloadFromEntry(binding) {
             if (!binding || !binding.folder) {
                 console.error("Invalid binding data in handleReloadFromEntry:", binding);
                 this.show_toast("Internal error: Invalid binding data.", 4, false);
                 return;
             }
             this.handleReload(binding.folder);
        },

        async handleReload(bindingFolder) {
             if (!bindingFolder) {
                 this.show_toast("No binding specified.", 3, false);
                 return;
             }
             const targetBinding = this.bindings.find(b => b.folder === bindingFolder);
             if (!targetBinding) {
                 this.show_toast(`Binding "${bindingFolder}" not found.`, 4, false);
                 return;
             }
              if (!targetBinding.installed) {
                 this.show_toast(`"${targetBinding.name}" is not installed.`, 3, false);
                 return;
             }
             // Use prop config
            if (bindingFolder !== this.$store.state.config.binding_name) {
                this.show_toast(`"${targetBinding.name}" is not active. Select it first.`, 3, false);
                return;
            }

            this.isLoadingAction = true;
            this.show_toast(`Reloading "${targetBinding.name}"...`, 3, true);
            try {
                 // Use internal wrapper
                const response = await this.internal_api_post_req('reload_binding', { name: bindingFolder });
                if (response && response.status) {
                    this.show_toast(`Binding "${targetBinding.name}" reloaded.`, 4, true);
                    this.refresh_config(); // Refresh parent state
                } else {
                     this.show_toast(`Failed to reload "${targetBinding.name}": ${response?.error || 'Unknown error'}`, 4, false);
                }
            } catch (error) {
                 // Error handled by internal_api_post_req
            } finally {
                this.isLoadingAction = false;
                nextTick(feather.replace);
            }
        }
    },

    mounted() {
        this.fetchBindings(); // Fetch data on mount
        nextTick(() => {
            feather.replace();
        });
    },

    // Watch for external config changes if needed, though parent should handle consistency
    // watch: {
    //     config: {
    //         handler(newConfig, oldConfig) {
    //             // Optional: Handle external changes if necessary, e.g., refresh bindings if binding_name changes externally
    //             console.log("BindingZoo detected config change from parent");
    //         },
    //         deep: true // Be careful with deep watchers
    //     }
    // },

    updated() {
        nextTick(() => {
            feather.replace(); // Ensure icons are updated on subsequent renders
        });
    }
};
</script>

<style scoped>
/* Styles from the original component */
.input-field {
    @apply block w-full px-3 py-2 text-sm bg-gray-50 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500 dark:text-gray-200 dark:placeholder-gray-400 disabled:opacity-50;
}

.binding-entry-processing {
    opacity: 0.7;
    pointer-events: none;
}

/* Example Primary Color Definitions (adjust as needed) */
.bg-primary-light {
     background-color: #e0f2fe; /* Tailwind sky-100 */
}
.dark .bg-primary-dark\/20 {
     background-color: rgba(59, 130, 246, 0.2); /* Tailwind blue-500 with 20% opacity */
}
.border-primary-dark\/30 {
    border-color: rgba(37, 99, 235, 0.3); /* Tailwind blue-700 with 30% opacity */
}
.focus\:ring-primary-dark\/50:focus {
    --tw-ring-color: rgba(37, 99, 235, 0.5); /* Tailwind blue-700 with 50% opacity */
}
.dark .fill-primary {
    fill: #3b82f6; /* Tailwind blue-500 */
}
.fill-primary {
    fill: #2563eb; /* Tailwind blue-600 */
}
</style>