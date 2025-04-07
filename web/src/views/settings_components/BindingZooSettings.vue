<template>
    <div class="user-settings-panel space-y-6 p-4 md:p-6">
        <!-- Header -->
        <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center border-b border-blue-300 dark:border-blue-600 pb-3 mb-4">
            <h2 class="text-xl font-semibold text-blue-800 dark:text-blue-200 mb-2 sm:mb-0">
                Binding Zoo
            </h2>
            <div v-if="currentBindingInfo" class="flex items-center gap-2 text-sm font-medium p-2 bg-blue-100 dark:bg-blue-900/50 rounded-md border border-blue-300 dark:border-blue-700 text-blue-700 dark:text-blue-200">
                <img :src="getIconPath(currentBindingInfo.icon)" @error="imgPlaceholder" class="w-6 h-6 rounded-full object-cover flex-shrink-0" alt="Current Binding Icon">
                <span>Active: <span class="font-semibold">{{ currentBindingInfo.name }}</span></span>

                <button @click="handleSettings(effectiveConfig.binding_name)" :disabled="isLoadingAction || loading || hasPendingChanges" class="svg-button ml-2 disabled:opacity-50 disabled:cursor-not-allowed" title="Configure Active Binding">
                    <i data-feather="settings" class="w-4 h-4"></i>
                </button>
                 <button @click="handleReload(effectiveConfig.binding_name)" :disabled="isLoadingAction || loading || hasPendingChanges" class="svg-button ml-1 disabled:opacity-50 disabled:cursor-not-allowed" title="Reload Active Binding">
                    <i data-feather="refresh-cw" class="w-4 h-4"></i>
                </button>
            </div>
            <div v-else class="text-sm font-medium text-red-600 dark:text-red-400 p-2 bg-red-100 dark:bg-red-900/30 rounded-md border border-red-300 dark:border-red-600">
                No binding selected!
            </div>
        </div>

        <p class="text-sm text-blue-600 dark:text-blue-400">
            Bindings are the engines that run the AI models. Select an installed binding to enable model selection and generation.
        </p>
         <div v-if="hasPendingChanges" class="p-3 bg-yellow-100 dark:bg-yellow-900/30 border border-yellow-300 dark:border-yellow-700 rounded-lg text-center text-sm text-yellow-700 dark:text-yellow-300">
             <i data-feather="alert-circle" class="inline-block w-4 h-4 mr-1 align-middle"></i>
             Apply main settings changes to use binding actions (settings, reload).
        </div>

        <!-- Search and Sort Controls -->
        <div class="flex flex-col sm:flex-row gap-4 mb-4">
            <div class="relative flex-grow">
                <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <i data-feather="search" class="w-5 h-5 text-blue-400 dark:text-blue-500"></i>
                </div>
                <input
                    type="search"
                    v-model="searchTerm"
                    placeholder="Search bindings..."
                    class="input search-input pl-10 w-full"
                    aria-label="Search bindings"
                    :disabled="isLoadingBindings || loading"
                />
            </div>
            <div class="flex-shrink-0">
                 <label for="binding-sort" class="sr-only">Sort bindings by</label>
                 <select id="binding-sort" v-model="sortOption" class="input w-full sm:w-auto" aria-label="Sort bindings by" :disabled="isLoadingBindings || loading">
                     <option value="name">Sort by Name</option>
                     <option value="author">Sort by Author</option>
                     <option value="status">Sort by Status</option>
                </select>
            </div>
        </div>

        <!-- Bindings Grid -->
        <div v-if="isLoadingBindings" class="flex justify-center items-center p-10">
             <svg aria-hidden="true" role="status" class="w-8 h-8 text-blue-300 animate-spin dark:text-blue-600 fill-blue-600 dark:fill-blue-400" viewBox="0 0 100 101" fill="none" xmlns="http://www.w3.org/2000/svg">
                 <path d="M100 50.5908C100 78.2051 77.6142 100.591 50 100.591C22.3858 100.591 0 78.2051 0 50.5908C0 22.9766 22.3858 0.59082 50 0.59082C77.6142 0.59082 100 22.9766 100 50.5908ZM9.08144 50.5908C9.08144 73.1895 27.4013 91.5094 50 91.5094C72.5987 91.5094 90.9186 73.1895 90.9186 50.5908C90.9186 27.9921 72.5987 9.67226 50 9.67226C27.4013 9.67226 9.08144 27.9921 9.08144 50.5908Z" fill="currentColor"/>
                 <path d="M93.9676 39.0409C96.393 38.4038 97.8624 35.9116 97.0079 33.5539C95.2932 28.8227 92.871 24.3692 89.8167 20.348C85.8452 15.1192 80.8826 10.7238 75.2124 7.41289C69.5422 4.10194 63.2754 1.94025 56.7698 1.05124C51.7666 0.367541 46.6976 0.446843 41.7345 1.27873C39.2613 1.69328 37.813 4.19778 38.4501 6.62326C39.0873 9.04874 41.5694 10.4717 44.0505 10.1071C47.8511 9.54855 51.7191 9.52689 55.5402 10.0491C60.8642 10.7766 65.9928 12.5457 70.6331 15.2552C75.2735 17.9648 79.3347 21.5619 82.5849 25.841C84.9175 28.9121 86.7997 32.2913 88.1811 35.8758C89.083 38.2158 91.5421 39.6781 93.9676 39.0409Z" fill="currentFill"/>
             </svg>
            <span class="ml-2 text-loading">Loading bindings...</span>
        </div>
        <div v-else-if="sortedBindings.length === 0" class="text-center text-blue-500 dark:text-blue-400 py-10">
            No bindings found{{ searchTerm ? ' matching "' + searchTerm + '"' : '' }}.
        </div>
        <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 scrollbar">
            <BindingEntry
                v-for="binding_item in sortedBindings"
                :key="binding_item.folder"
                :binding="binding_item"
                :selected="isBindingSelected(binding_item)"
                :is-processing="binding_item.isProcessing"
                @select="handleSelect"
                @install="handleInstall"
                @uninstall="handleUninstall"
                @reinstall="handleReinstall"
                @settings="handleSettingsFromEntry"
                @reload-binding="handleReloadFromEntry"
            />
        </div>
    </div>
</template>

<script>
import { nextTick } from 'vue';
import feather from 'feather-icons';
import BindingEntry from '@/components/BindingEntry.vue';
import defaultBindingIcon from "@/assets/default_binding.png";

export default {
    name: 'BindingZooSettings',
    components: {
        BindingEntry
    },
    props: {
        config: { type: Object, required: true }, // The editable config from parent
        loading: { type: Boolean, default: false },
        api_get_req: { type: Function, required: true },
        api_post_req: { type: Function, required: true },
        show_toast: { type: Function, required: true },
        show_yes_no_dialog: { type: Function, required: true },
        show_universal_form: { type: Function, required: true },
        client_id: { type: String, required: true },
    },
    emits: ['setting-updated'], // Emits updates for parent

    data() {
        return {
            bindings: [], // Local cache of binding list from store/API
            isLoadingBindings: false,
            isLoadingAction: false,
            sortOption: 'name',
            searchTerm: '',
        };
    },

    computed: {
        // Use store state for applied config checks
        effectiveConfig() {
            return this.$store.state.config || {};
        },
        hasPendingChanges() {
            return this.$store.state.settingsChanged;
        },

        // Find the current binding info based on the APPLIED config
        currentBindingInfo() {
            if (!this.effectiveConfig.binding_name || this.bindings.length === 0) return null;
            return this.bindings.find(b => b.folder === this.effectiveConfig.binding_name);
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
                    b.folder?.toLowerCase().includes(lowerSearch)
                );
            }

            // Sort
            filtered.sort((a, b) => {
                // --- Primary Sorting Rule: Active binding first ---
                const isASelected = a.folder === this.effectiveConfig.binding_name;
                const isBSelected = b.folder === this.effectiveConfig.binding_name;

                if (isASelected && !isBSelected) return -1; // a comes first
                if (!isASelected && isBSelected) return 1;  // b comes first
                // If both are selected or neither are selected, proceed to secondary sort

                // --- Secondary Sorting Rules ---
                switch (this.sortOption) {
                    case 'status':
                        // Sort by installed status secondarily
                        if (a.installed && !b.installed) return -1;
                        if (!a.installed && b.installed) return 1;
                        // If status is the same, sort by name
                        return (a.name || '').localeCompare(b.name || '');
                    case 'author':
                        // Sort by author secondarily
                        return (a.author || '').localeCompare(b.author || '');
                    case 'name':
                    default:
                        // Default sort by name secondarily
                        return (a.name || '').localeCompare(b.name || '');
                }
            });

            return filtered;
        }
    },

    watch: {
         // Watch store changes for bindings (if managed by store)
         // This assumes bindings might be updated externally
         '$store.state.bindingsZoo': {
             handler(newBindings) {
                 if (newBindings) {
                     this.bindings = (newBindings || []).map(b => ({
                         ...b,
                         // Preserve existing processing state if possible
                         isProcessing: this.bindings.find(ob => ob.folder === b.folder)?.isProcessing || false
                     }));
                     this.replaceFeatherIcons();
                 }
             },
             deep: true,
             immediate: true // Also run on component load if store might already have data
         }
    },

    methods: {
        // Check selection based on the EDITABLE config prop
        isBindingSelected(binding) {
            return binding.folder === this.config.binding_name;
        },
        getIconPath(iconRelativePath) {
            if (!iconRelativePath) return defaultBindingIcon;
            if (iconRelativePath.startsWith('http')) return iconRelativePath;
            // Assuming icons are served relative to the base URL or root
             const icon = iconRelativePath.startsWith('/') ? iconRelativePath : `/${iconRelativePath}`;
             return icon.replace(/\\/g, '/'); // Normalize path separators
        },
        imgPlaceholder(event) {
            event.target.src = defaultBindingIcon;
        },
        async fetchBindings() {
            this.isLoadingBindings = true;
            try {
                const response = await this.api_get_req('list_bindings');
                // Update local state, potentially overwriting store-watched state if fetch is primary source
                this.bindings = (response || []).map(b => ({ ...b, isProcessing: false }));
                // Or commit to store if store is the source of truth:
                // this.$store.commit('setBindingsZoo', (response || []).map(b => ({ ...b, isProcessing: false })));
            } catch (error) { this.bindings = []; } finally { this.isLoadingBindings = false; this.replaceFeatherIcons(); }
        },
        setBindingProcessing(folder, state) {
            const index = this.bindings.findIndex(b => b.folder === folder);
            if (index !== -1) this.bindings[index].isProcessing = state;
        },
        handleSelect(binding) {
            if (!binding?.installed) { this.show_toast(`Binding "${binding.name}" is not installed.`, 3, false); return; }
            if (this.config.binding_name !== binding.folder) {
                 this.$emit('setting-updated', { key: 'binding_name', value: binding.folder });
                 this.store.dispatch('refreshModels');
                 this.show_toast(`Selected binding: ${binding.name}. Apply changes.`, 3, true);
            }
        },
        async handleInstall(binding) {
             let proceed = true;
             if (binding.disclaimer) {
                proceed = await this.show_yes_no_dialog(`Disclaimer for ${binding.name}:\n${binding.disclaimer}\nProceed?`, 'Proceed', 'Cancel');
             }
             if (!proceed) return;
             this.setBindingProcessing(binding.folder, true); this.isLoadingAction = true;
             try {
                 const response = await this.api_post_req('install_binding', { name: binding.folder });
                 if (response?.status) {
                     this.show_toast(`"${binding.name}" installed! Reload recommended.`, 5, true);
                     await this.fetchBindings();
                 } else { this.show_toast(`Install failed: ${response?.error || 'Error'}`, 4, false); }
             } catch (error) { /* Handled */ }
             finally { this.setBindingProcessing(binding.folder, false); this.isLoadingAction = false; this.replaceFeatherIcons(); }
        },
        async handleUninstall(binding) {
             const yes = await this.show_yes_no_dialog(`Uninstall "${binding.name}"?`, 'Uninstall', 'Cancel');
             if (!yes) return;
             this.setBindingProcessing(binding.folder, true); this.isLoadingAction = true;
             try {
                 const response = await this.api_post_req('uninstall_binding', { name: binding.folder });
                 if (response?.status) {
                     this.show_toast(`"${binding.name}" uninstalled.`, 4, true);
                     await this.fetchBindings();
                     if (this.config.binding_name === binding.folder) {
                          this.$emit('setting-updated', { key: 'binding_name', value: null });
                          this.$emit('setting-updated', { key: 'model_name', value: null });
                     }
                 } else { this.show_toast(`Uninstall failed: ${response?.error || 'Error'}`, 4, false); }
             } catch (error) { /* Handled */ }
             finally { this.setBindingProcessing(binding.folder, false); this.isLoadingAction = false; this.replaceFeatherIcons(); }
        },
        async handleReinstall(binding) {
             const yes = await this.show_yes_no_dialog(`Reinstall "${binding.name}"?`, 'Reinstall', 'Cancel');
             if (!yes) return;
             this.setBindingProcessing(binding.folder, true); this.isLoadingAction = true;
             try {
                 const response = await this.api_post_req('reinstall_binding', { name: binding.folder });
                 if (response?.status) {
                     this.show_toast(`"${binding.name}" reinstalled! Reload recommended.`, 5, true);
                     await this.fetchBindings();
                 } else { this.show_toast(`Reinstall failed: ${response?.error || 'Error'}`, 4, false); }
             } catch (error) { /* Handled */ }
             finally { this.setBindingProcessing(binding.folder, false); this.isLoadingAction = false; this.replaceFeatherIcons(); }
        },
        handleSettingsFromEntry(binding) { this.handleSettings(binding.folder); },
        handleReloadFromEntry(binding) { this.handleReload(binding.folder); },
        async handleSettings(bindingFolder) {
            if (!bindingFolder) { this.show_toast("No binding specified.", 3, false); return; }
            if (this.hasPendingChanges) { this.show_toast(`Apply settings changes first.`, 3, false); return; }
            const targetBinding = this.bindings.find(b => b.folder === bindingFolder);
            if (!targetBinding?.installed) { this.show_toast(`Binding "${targetBinding?.name || bindingFolder}" not installed.`, 3, false); return; }
            if (bindingFolder !== this.effectiveConfig.binding_name) { this.show_toast(`Select and Apply "${targetBinding.name}" first.`, 4, false); return; }

            this.isLoadingAction = true;
            try {
                 const settingsData = await this.api_post_req('get_active_binding_settings');
                 if (settingsData && Object.keys(settingsData).length > 0) {
                     const result = await this.show_universal_form(settingsData, `Settings - ${targetBinding.name}`, "Save", "Cancel");
                     if (result !== null && result !== undefined) {
                         const setResponse = await this.api_post_req('set_active_binding_settings', { settings: result });
                         if (setResponse?.status) {
                             this.show_toast(`Settings updated for "${targetBinding.name}". Reloading...`, 4, true);
                             await this.api_post_req('update_binding_settings');
                             this.show_toast(`Binding "${targetBinding.name}" reloaded.`, 4, true);
                         } else { this.show_toast(`Update failed: ${setResponse?.error || 'Error'}`, 4, false); }
                     } else { this.show_toast(`Settings update cancelled.`, 3, false); }
                 } else if (settingsData) { this.show_toast(`"${targetBinding.name}" has no settings.`, 3, false);
                 } else { this.show_toast(`Could not get settings.`, 4, false); }
            } catch (error) { /* Handled */ }
            finally { this.isLoadingAction = false; this.replaceFeatherIcons(); }
        },
        async handleReload(bindingFolder) {
             if (!bindingFolder) { this.show_toast("No binding specified.", 3, false); return; }
             if (this.hasPendingChanges) { this.show_toast(`Apply settings changes first.`, 3, false); return; }
             const targetBinding = this.bindings.find(b => b.folder === bindingFolder);
             if (!targetBinding?.installed) { this.show_toast(`Binding "${targetBinding?.name || bindingFolder}" not installed.`, 3, false); return; }
             if (bindingFolder !== this.effectiveConfig.binding_name) { this.show_toast(`"${targetBinding.name}" is not the active binding.`, 3, false); return; }

            this.isLoadingAction = true; this.show_toast(`Reloading "${targetBinding.name}"...`, 3, true);
            try {
                const response = await this.api_post_req('reload_binding', { name: bindingFolder });
                if (response?.status) { this.show_toast(`"${targetBinding.name}" reloaded.`, 4, true); }
                else { this.show_toast(`Reload failed: ${response?.error || 'Error'}`, 4, false); }
            } catch (error) { /* Handled */ }
            finally { this.isLoadingAction = false; this.replaceFeatherIcons(); }
        },
        replaceFeatherIcons() {
             nextTick(() => { try { feather.replace(); } catch (e) {} });
        }
    },
    mounted() {
        // Fetch initial list or rely on watcher if store is primary source
        this.fetchBindings();
        this.replaceFeatherIcons();
    },
    updated() {
        this.replaceFeatherIcons();
    }
};
</script>

<style scoped>
.user-settings-panel { @apply bg-white dark:bg-gray-800 rounded-lg shadow; }
.svg-button { @apply p-1 rounded-full text-blue-600 dark:text-blue-400 hover:bg-blue-100 dark:hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-1 dark:focus:ring-offset-gray-800 transition-colors duration-150; }
.input { @apply block w-full px-3 py-2 bg-gray-50 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 focus:border-blue-500 dark:focus:ring-offset-gray-900 sm:text-sm disabled:opacity-50 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500; }
.search-input { /* Inherits .input */ }
.text-loading { @apply text-blue-600 dark:text-blue-300; }
.scrollbar::-webkit-scrollbar { width: 8px; height: 8px; }
.scrollbar::-webkit-scrollbar-track { @apply bg-gray-100 dark:bg-gray-700 rounded-lg; }
.scrollbar::-webkit-scrollbar-thumb { @apply bg-gray-300 dark:bg-gray-500 rounded-lg; }
.scrollbar::-webkit-scrollbar-thumb:hover { @apply bg-gray-400 dark:bg-gray-400; }
</style>