<template>
    <div class="space-y-6 p-4 md:p-6 bg-white dark:bg-gray-800 rounded-lg shadow-md border border-gray-200 dark:border-gray-700">
        <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center border-b border-gray-200 dark:border-gray-700 pb-3 mb-4">
            <h2 class="text-xl font-semibold text-gray-800 dark:text-gray-200 mb-2 sm:mb-0">
                Binding Zoo
            </h2>
             <!-- Current Binding Display -->
            <div v-if="currentBindingInfo" class="flex items-center gap-2 text-sm font-medium p-2 bg-primary-light dark:bg-primary-dark/20 rounded-md border border-primary-dark/30">
                <img :src="currentBindingInfo.icon" @error="imgPlaceholder" class="w-6 h-6 rounded-full object-cover flex-shrink-0" alt="Current Binding Icon">
                <span>Active: <span class="font-semibold">{{ currentBindingInfo.name }}</span></span>
                <button @click="handleSettings(config.binding_name)" class="ml-2 p-1 rounded-full hover:bg-primary-dark/20" title="Configure Active Binding">
                     <i data-feather="settings" class="w-4 h-4"></i>
                </button>
                 <button @click="handleReload(config.binding_name)" class="ml-1 p-1 rounded-full hover:bg-primary-dark/20" title="Reload Active Binding">
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
                />
            </div>
             <!-- Sort Select -->
            <div class="flex-shrink-0">
                 <label for="binding-sort" class="sr-only">Sort bindings by</label>
                 <select id="binding-sort" v-model="sortOption" class="input-field">
                     <option value="name">Sort by Name</option>
                     <option value="author">Sort by Author</option>
                     <!-- Add more options if needed, e.g., popularity, last updated -->
                </select>
            </div>
        </div>

        <!-- Bindings Grid -->
        <div v-if="isLoadingBindings" class="flex justify-center items-center p-10">
             <svg aria-hidden="true" class="w-8 h-8 text-gray-300 animate-spin dark:text-gray-600 fill-primary" viewBox="0 0 100 101" fill="none" xmlns="http://www.w3.org/2000/svg"> <path d="M100 50.5908C100 78.2051 77.6142 100.591 50 100.591C22.3858 100.591 0 78.2051 0 50.5908C0 22.9766 22.3858 0.59082 50 0.59082C77.6142 0.59082 100 22.9766 100 50.5908ZM9.08144 50.5908C9.08144 73.1895 27.4013 91.5094 50 91.5094C72.5987 91.5094 90.9186 73.1895 90.9186 50.5908C90.9186 27.9921 72.5987 9.67226 50 9.67226C27.4013 9.67226 9.08144 27.9921 9.08144 50.5908Z" fill="currentColor"/> <path d="M93.9676 39.0409C96.393 38.4038 97.8624 35.9116 97.0079 33.5539C95.2932 28.8227 92.871 24.3692 89.8167 20.348C85.8452 15.1192 80.8826 10.7238 75.2124 7.41289C69.5422 4.10194 63.2754 1.94025 56.7698 1.05124C51.7666 0.367541 46.6976 0.446843 41.7345 1.27873C39.2613 1.69328 37.813 4.19778 38.4501 6.62326C39.0873 9.04874 41.5694 10.4717 44.0505 10.1071C47.8511 9.54855 51.7191 9.52689 55.5402 10.0491C60.8642 10.7766 65.9928 12.5457 70.6331 15.2552C75.2735 17.9648 79.3347 21.5619 82.5849 25.841C84.9175 28.9121 86.7997 32.2913 88.1811 35.8758C89.083 38.2158 91.5421 39.6781 93.9676 39.0409Z" fill="currentFill"/> </svg>
            <span class="ml-2 text-gray-500 dark:text-gray-400">Loading bindings...</span>
        </div>
         <div v-else-if="sortedBindings.length === 0" class="text-center text-gray-500 dark:text-gray-400 py-10">
            No bindings found{{ searchTerm ? ' matching "' + searchTerm + '"' : '' }}.
        </div>
        <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
             <BindingEntry
                v-for="binding in sortedBindings"
                :key="binding.folder"
                :binding="binding"
                :is-selected="config.binding_name === binding.folder"
                @select="handleSelect(binding)"
                @install="handleInstall(binding)"
                @uninstall="handleUninstall(binding)"
                @reinstall="handleReinstall(binding)"
                @settings="handleSettings(binding.folder)"
                @reload="handleReload(binding.folder)"
            />
        </div>
    </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick, defineProps, defineEmits, watch } from 'vue';
import feather from 'feather-icons';
import BindingEntry from '@/components/BindingEntry.vue'; // Assuming this component exists
import defaultBindingIcon from "@/assets/default_binding.png"; // Path to your default icon

// Props
const props = defineProps({
    config: { type: Object, required: true },
    loading: { type: Boolean, default: false }, // Parent loading state
    api_post_req: { type: Function, required: true },
    api_get_req: { type: Function, required: true },
    show_toast: { type: Function, required: true },
    show_yes_no_dialog: { type: Function, required: true },
    show_universal_form: { type: Function, required: true },
    refresh_config: { type: Function, required: true }, // Function to trigger parent config refresh
    client_id: { type: String, required: true }
});

// Emits
const emit = defineEmits(['update:setting', 'settings-changed']); // Emit settings-changed if needed locally

// State
const bindings = ref([]);
const isLoadingBindings = ref(false);
const isLoadingAction = ref(false); // For specific actions like install/uninstall
const sortOption = ref('name'); // 'name' or 'author'
const searchTerm = ref('');

// --- Computed ---
const currentBindingInfo = computed(() => {
    if (!props.config || !props.config.binding_name || bindings.value.length === 0) {
        return null;
    }
    const current = bindings.value.find(b => b.folder === props.config.binding_name);
    return current ? { name: current.name, icon: current.icon || defaultBindingIcon } : null;
});

const sortedBindings = computed(() => {
    if (!bindings.value) return [];

    let filtered = [...bindings.value];

    // Filter by search term
    if (searchTerm.value) {
        const lowerSearch = searchTerm.value.toLowerCase();
        filtered = filtered.filter(b =>
            b.name?.toLowerCase().includes(lowerSearch) ||
            b.author?.toLowerCase().includes(lowerSearch) ||
            b.description?.toLowerCase().includes(lowerSearch) ||
            b.folder?.toLowerCase().includes(lowerSearch)
        );
    }

    // Sort
    filtered.sort((a, b) => {
        // 1. Installed first
        if (a.installed && !b.installed) return -1;
        if (!a.installed && b.installed) return 1;

        // 2. Secondary sort option
        if (sortOption.value === 'name') {
            return (a.name || '').localeCompare(b.name || '');
        } else if (sortOption.value === 'author') {
            return (a.author || '').localeCompare(b.author || '');
        }
        // Add more sort options here if needed

        return 0; // Keep original order if secondary sort doesn't apply
    });

    return filtered;
});

// --- Methods ---
const fetchBindings = async () => {
    isLoadingBindings.value = true;
    try {
        const response = await props.api_get_req('list_bindings');
        // Add isProcessing state to each binding for install/uninstall UI feedback
        bindings.value = response.map(b => ({ ...b, isProcessing: false })) || [];
    } catch (error) {
        props.show_toast("Failed to load bindings.", 4, false);
        console.error("Error fetching bindings:", error);
        bindings.value = [];
    } finally {
        isLoadingBindings.value = false;
        nextTick(feather.replace);
    }
};

const setBindingProcessing = (folder, state) => {
    const index = bindings.value.findIndex(b => b.folder === folder);
    if (index !== -1) {
        bindings.value[index].isProcessing = state;
    }
};

const handleSelect = (binding) => {
    if (!binding.installed) {
        props.show_toast(`Binding "${binding.name}" is not installed.`, 3, false);
        return;
    }
    if (props.config.binding_name !== binding.folder) {
        emit('update:setting', { key: 'binding_name', value: binding.folder });
        // Optionally reset model name here or let parent handle it
        emit('update:setting', { key: 'model_name', value: null });
        props.show_toast(`Selected binding: ${binding.name}`, 3, true);
    }
};

const handleInstall = async (binding) => {
    let proceed = true;
    if (binding.disclaimer) {
        proceed = await props.show_yes_no_dialog(`Disclaimer for ${binding.name}:\n\n${binding.disclaimer}\n\nDo you want to proceed with installation?`, 'Proceed', 'Cancel');
    }

    if (!proceed) return;

    setBindingProcessing(binding.folder, true);
    isLoadingAction.value = true; // Maybe use a global loading indicator from parent?
    try {
        const response = await props.api_post_req('install_binding', { name: binding.folder });
        if (response && response.status) {
            props.show_toast(`Binding "${binding.name}" installed successfully! Restart recommended.`, 5, true);
            // Refresh bindings list to show installed status
            await fetchBindings();
            // Optionally prompt for restart or reload page
            // props.show_message_box("It is advised to reboot the application after installing a binding.\nPage will refresh in 5s.")
            // setTimeout(()=>{window.location.href = "/"},5000) ;
        } else {
            props.show_toast(`Failed to install binding "${binding.name}": ${response?.error || 'Unknown error'}`, 4, false);
        }
    } catch (error) {
        props.show_toast(`Error installing binding "${binding.name}": ${error.message}`, 4, false);
        console.error(`Error installing ${binding.folder}:`, error);
    } finally {
        setBindingProcessing(binding.folder, false);
        isLoadingAction.value = false;
    }
};

const handleUninstall = async (binding) => {
     const yes = await props.show_yes_no_dialog(`Are you sure you want to uninstall the binding "${binding.name}"?\nThis will remove its files.`, 'Uninstall', 'Cancel');
     if (!yes) return;

    setBindingProcessing(binding.folder, true);
    isLoadingAction.value = true;
    try {
        const response = await props.api_post_req('unInstall_binding', { name: binding.folder });
        if (response && response.status) {
            props.show_toast(`Binding "${binding.name}" uninstalled successfully!`, 4, true);
            await fetchBindings(); // Refresh list
            // If the uninstalled binding was selected, clear it
            if (props.config.binding_name === binding.folder) {
                 emit('update:setting', { key: 'binding_name', value: null });
                 emit('update:setting', { key: 'model_name', value: null });
            }
        } else {
            props.show_toast(`Failed to uninstall binding "${binding.name}": ${response?.error || 'Unknown error'}`, 4, false);
        }
    } catch (error) {
        props.show_toast(`Error uninstalling binding "${binding.name}": ${error.message}`, 4, false);
        console.error(`Error uninstalling ${binding.folder}:`, error);
    } finally {
        setBindingProcessing(binding.folder, false);
        isLoadingAction.value = false;
    }
};

const handleReinstall = async (binding) => {
     const yes = await props.show_yes_no_dialog(`Are you sure you want to reinstall the binding "${binding.name}"?\nThis will overwrite existing files.`, 'Reinstall', 'Cancel');
     if (!yes) return;

    setBindingProcessing(binding.folder, true);
    isLoadingAction.value = true;
    try {
        const response = await props.api_post_req('reinstall_binding', { name: binding.folder });
        if (response && response.status) {
            props.show_toast(`Binding "${binding.name}" reinstalled successfully! Restart recommended.`, 5, true);
            await fetchBindings(); // Refresh list (status might not change visually immediately)
        } else {
            props.show_toast(`Failed to reinstall binding "${binding.name}": ${response?.error || 'Unknown error'}`, 4, false);
        }
    } catch (error) {
        props.show_toast(`Error reinstalling binding "${binding.name}": ${error.message}`, 4, false);
        console.error(`Error reinstalling ${binding.folder}:`, error);
    } finally {
        setBindingProcessing(binding.folder, false);
        isLoadingAction.value = false;
    }
};

const handleSettings = async (bindingFolder) => {
    if (!bindingFolder) return;
    // Needs to fetch settings specifically for the *active* binding,
    // even if clicking the settings button on an *inactive* but selected binding in the list.
    // The backend endpoint usually gets settings for the currently loaded one.
    // We might need a way to get settings for *any* installed binding if required.
    // Assuming '/get_active_binding_settings' gets settings for props.config.binding_name
     if (bindingFolder !== props.config.binding_name) {
        props.show_toast(`Please select the binding "${bindingFolder}" first to configure its active settings.`, 4, false);
        return; // Or try to fetch settings for the specific folder if backend supports it
     }

    isLoadingAction.value = true;
    try {
        const settingsData = await props.api_post_req('get_active_binding_settings');
         if (settingsData && Object.keys(settingsData).length > 0) {
            const bindingName = bindings.value.find(b => b.folder === bindingFolder)?.name || bindingFolder;
            const result = await props.show_universal_form(settingsData, `Binding Settings - ${bindingName}`, "Save", "Cancel");

            // If form was submitted (not cancelled)
            const setResponse = await props.api_post_req('set_active_binding_settings', { settings: result });
             if (setResponse && setResponse.status) {
                 props.show_toast(`Settings for "${bindingName}" updated. Reloading binding...`, 4, true);
                 // Attempt to apply the settings by reloading the binding
                 await props.api_post_req('update_binding_settings'); // Tell backend to commit potentially cached settings
                // Optional: Force page reload or more graceful update
                // await props.refresh_config(); // Refresh config may revert visual changes until saved/applied
                props.show_toast(`Binding "${bindingName}" reloaded with new settings.`, 4, true);
                 // window.location.href = "/"; // Force reload if necessary
             } else {
                 props.show_toast(`Failed to update settings for "${bindingName}": ${setResponse?.error || 'Unknown error'}`, 4, false);
            }
         } else {
            props.show_toast(`Binding "${bindingFolder}" has no configurable settings.`, 4, false);
        }
    } catch (error) {
        props.show_toast(`Error accessing settings for "${bindingFolder}": ${error.message}`, 4, false);
        console.error(`Error getting/setting settings for ${bindingFolder}:`, error);
    } finally {
        isLoadingAction.value = false;
    }
};

const handleReload = async (bindingFolder) => {
    if (!bindingFolder || bindingFolder !== props.config.binding_name) {
        props.show_toast(`Binding "${bindingFolder}" is not currently active.`, 3, false);
        return;
    }
    isLoadingAction.value = true;
    props.show_toast(`Reloading binding "${bindingFolder}"...`, 3, true);
    try {
        const response = await props.api_post_req('reload_binding', { name: bindingFolder }); // Assuming name = folder
        if (response && response.status) {
            props.show_toast(`Binding "${bindingFolder}" reloaded successfully.`, 4, true);
            // Might need to refresh models list if reload affects available models
        } else {
            props.show_toast(`Failed to reload binding "${bindingFolder}": ${response?.error || 'Unknown error'}`, 4, false);
        }
    } catch (error) {
        props.show_toast(`Error reloading binding "${bindingFolder}": ${error.message}`, 4, false);
        console.error(`Error reloading ${bindingFolder}:`, error);
    } finally {
        isLoadingAction.value = false;
    }
};

const imgPlaceholder = (event) => {
    event.target.src = defaultBindingIcon;
};


// Lifecycle Hooks
onMounted(() => {
    fetchBindings();
});

onUpdated(() => {
     // Use this cautiously
     nextTick(() => {
        feather.replace();
     });
});

</script>

<style scoped>
/* Using shared styles */
.input-field {
     @apply block w-full px-3 py-2 text-sm bg-gray-50 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:focus:ring-offset-gray-800 disabled:opacity-50; /* Corrected focus */
}

/* Updated Button Styles in BindingZoo */
.button-primary-sm {
    /* Assuming 'primary' is blue-600 */
    @apply button-base-sm text-white bg-blue-600 hover:bg-blue-700 focus:ring-blue-500;
}
.button-secondary-sm {
    @apply button-base-sm text-gray-700 dark:text-gray-200 bg-gray-200 dark:bg-gray-600 hover:bg-gray-300 dark:hover:bg-gray-500 focus:ring-gray-400;
}
.button-success-sm {
    @apply button-base-sm text-white bg-green-600 hover:bg-green-700 focus:ring-green-500;
}

/* Base definitions if not global */
.button-base-sm {
     @apply inline-flex items-center justify-center px-2.5 py-1.5 border border-transparent text-xs font-medium rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-offset-2 dark:focus:ring-offset-gray-800 disabled:opacity-50 transition-colors duration-150;
}
.dark .button-secondary-sm {
     @apply focus:ring-offset-gray-800;
}

/* Add specific styles if needed */
.binding-grid-enter-active,
.binding-grid-leave-active {
  transition: all 0.5s ease;
}
.binding-grid-enter-from,
.binding-grid-leave-to {
  opacity: 0;
  transform: translateY(20px);
}
.binding-grid-leave-active {
  position: absolute; /* Optional: for smoother leave transitions */
}
</style>