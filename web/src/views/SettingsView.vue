<template>
    <div class="flex h-screen w-screen font-sans antialiased theme-bg-primary theme-text-primary">
        <SettingsSidebar
            :sections="sections"
            :active-section="activeSection"
            @update:activeSection="setActiveSection"
            class="flex-shrink-0 w-64 border-r theme-border-primary theme-bg-secondary overflow-y-auto theme-scrollbar"
        />

        <div class="flex-1 flex flex-col overflow-hidden">
            <div :class="['sticky top-0 z-20 flex items-center justify-between p-3 gap-3 shadow-md theme-bg-secondary theme-border-b theme-border-primary', isLoading ? 'opacity-50 pointer-events-none':'']">
                <div class="flex items-center gap-4 flex-1">
                     <div v-if="settingsChanged && !isLoading" class="flex items-center gap-2 theme-text-warning animate-pulse">
                        <i data-feather="alert-circle" class="w-5 h-5"></i>
                        <span class="text-sm font-medium">Settings have changed</span>
                    </div>
                    <div v-if="!settingsChanged && !isLoading" class="flex gap-3 items-center">
                         <button title="Reset configuration to default" class="icon-button theme-text-secondary hover:theme-text-primary" @click="reset_configuration()">
                            <i data-feather="refresh-ccw"></i>
                         </button>
                         <button title="Restart program" class="icon-button theme-text-secondary hover:theme-text-primary" @click="restart_program()">
                            <i data-feather="power"></i>
                         </button>
                         <button title="Clear uploads folder" class="icon-button theme-text-secondary hover:theme-text-danger" @click="clear_uploads()">
                             <i data-feather="trash-2"></i>
                         </button>
                         <button v-if="has_updates" title="Upgrade program" class="icon-button theme-text-success hover:theme-text-primary relative" @click="update_software()">
                             <i data-feather="arrow-up-circle"></i>
                             <span class="absolute top-0 right-0 block h-2 w-2 rounded-full theme-bg-danger ring-2 theme-ring-bg"></span>
                         </button>
                    </div>
                </div>
                <div v-if="settingsChanged && !isLoading" class="flex items-center gap-2">
                     <button class="flex items-center gap-2 px-3 py-1.5 rounded theme-button-success duration-150 active:scale-95"
                             title="Apply changes"
                             type="button"
                             @click.stop="applyConfiguration()">
                         <span class="font-medium text-sm">Apply</span>
                         <i data-feather="check" class="w-4 h-4"></i>
                     </button>
                     <button class="flex items-center gap-2 px-3 py-1.5 rounded theme-button-danger duration-150 active:scale-95"
                             title="Cancel changes"
                             type="button"
                             @click.stop="cancelConfiguration()">
                         <span class="font-medium text-sm">Cancel</span>
                         <i data-feather="x" class="w-4 h-4"></i>
                     </button>
                </div>
                 <div v-if="isLoading" class="flex items-center gap-2 text-sm theme-text-muted">
                     <span>{{ loading_text }}</span>
                     <svg aria-hidden="true"
                          class="w-5 h-5 animate-spin theme-spinner-color"
                          viewBox="0 0 100 101"
                          fill="none"
                          xmlns="http://www.w3.org/2000/svg">
                         <path d="M100 50.5908C100 78.2051 77.6142 100.591 50 100.591C22.3858 100.591 0 78.2051 0 50.5908C0 22.9766 22.3858 0.59082 50 0.59082C77.6142 0.59082 100 22.9766 100 50.5908ZM9.08144 50.5908C9.08144 73.1895 27.4013 91.5094 50 91.5094C72.5987 91.5094 90.9186 73.1895 90.9186 50.5908C90.9186 27.9921 72.5987 9.67226 50 9.67226C27.4013 9.67226 9.08144 27.9921 9.08144 50.5908Z"
                             fill="currentColor" />
                         <path d="M93.9676 39.0409C96.393 38.4038 97.8624 35.9116 97.0079 33.5539C95.2932 28.8227 92.871 24.3692 89.8167 20.348C85.8452 15.1192 80.8826 10.7238 75.2124 7.41289C69.5422 4.10194 63.2754 1.94025 56.7698 1.05124C51.7666 0.367541 46.6976 0.446843 41.7345 1.27873C39.2613 1.69328 37.813 4.19778 38.4501 6.62326C39.0873 9.04874 41.5694 10.4717 44.0505 10.1071C47.8511 9.54855 51.7191 9.52689 55.5402 10.0491C60.8642 10.7766 65.9928 12.5457 70.6331 15.2552C75.2735 17.9648 79.3347 21.5619 82.5849 25.841C84.9175 28.9121 86.7997 32.2913 88.1811 35.8758C89.083 38.2158 91.5421 39.6781 93.9676 39.0409Z"
                             fill="currentFill" />
                     </svg>
                     <span class="sr-only">Loading...</span>
                 </div>
            </div>
            <main class="flex-1 overflow-x-hidden overflow-y-auto theme-scrollbar p-6">
                <component
                    :is="currentComponent"
                    v-if="configToEdit"
                    :config="configToEdit"
                    :loading="isLoading"
                    @setting-updated="handleSettingUpdated"
                    :api_get_req="api_get_req"
                    :api_post_req="api_post_req"
                    :show_toast="this.$store.state.toast.showToast"
                    :show_yes_no_dialog="this.$store.state.yesNoDialog.askQuestion"
                    :show_message_box="this.$store.state.messageBox.showMessage"
                    :client_id="$store.state.client_id"
                    :show_universal_form="this.$store.state.universalForm.showForm"
                />
                 <div v-else class="flex justify-center items-center h-full theme-text-secondary">
                     <p>Loading configuration...</p>
                 </div>
            </main>
        </div>

    </div>
</template>
<script>
import { nextTick, markRaw } from 'vue'; // Import markRaw
import axios from 'axios';
import feather from 'feather-icons';
import SettingsSidebar from '@/components/SettingsSidebar.vue';
import SystemStatusSettings from './settings_components/SystemStatusSettings.vue';
import SmartRoutingSettings from './settings_components/SmartRoutingSettings.vue';
import MainConfigSettings from './settings_components/MainConfigSettings.vue';
import DataManagementSettings from './settings_components/DataManagementSettings.vue';
import InternetSettings from './settings_components/InternetSettings.vue';
import ServicesZooSettings from './settings_components/ServicesZooSettings.vue';
import BindingZooSettings from './settings_components/BindingZooSettings.vue';
import ModelsZooSettings from './settings_components/ModelsZooSettings.vue';
import PersonalitiesZooSettings from './settings_components/PersonalitiesZooSettings.vue';
import FunctionCallsZooSettings from './settings_components/FunctionCallsZooSettings.vue';
import ModelConfigSettings from './settings_components/ModelConfigSettings.vue';

axios.defaults.baseURL = import.meta.env.VITE_LOLLMS_API_BASEURL;

const posts_headers = {
    'accept': 'application/json',
    'Content-Type': 'application/json'
};

export default {
    name: 'SettingsView',
    components: {
        SettingsSidebar,
        // Child components are automatically registered, no need to list them here again
        // if they are used in the 'sections' data and rendered via <component :is="...">
    },
    data() {
        return {
            isLoading: false,
            settingsChanged: false,
            has_updates: false,
            activeSection: 'system_status',
            loading_text: "Loading settings...",
            editableConfig: null,
            // Mark component definitions as raw to prevent reactivity issues
            sections: [
                { id: 'system_status', name: 'System Status', icon: 'activity', component: markRaw(SystemStatusSettings) },
                { id: 'main_config', name: 'Main Config', icon: 'sliders', component: markRaw(MainConfigSettings) },
                { id: 'model_config', name: 'Model Parameters', icon: 'cpu', component: markRaw(ModelConfigSettings) },
                { id: 'smart_routing', name: 'Smart Routing', icon: 'git-branch', component: markRaw(SmartRoutingSettings) },
                { id: 'data_management', name: 'Data Management', icon: 'database', component: markRaw(DataManagementSettings) },
                { id: 'internet', name: 'Internet', icon: 'wifi', component: markRaw(InternetSettings) },
                { id: 'services_zoo', name: 'Services Zoo', icon: 'server', component: markRaw(ServicesZooSettings) },
                { id: 'binding_zoo', name: 'Bindings Zoo', icon: 'link', component: markRaw(BindingZooSettings) },
                { id: 'models_zoo', name: 'Models Zoo', icon: 'package', component: markRaw(ModelsZooSettings) },
                { id: 'personalities_zoo', name: 'Personalities Zoo', icon: 'users', component: markRaw(PersonalitiesZooSettings) },
                { id: 'function_calls_zoo', name: 'Function Calls Zoo', icon: 'tool', component: markRaw(FunctionCallsZooSettings) },
            ]
        };
    },
    computed: {
        configToEdit() {
            return this.editableConfig ?? this.$store.state.config;
        },
        currentComponent() {
            const section = this.sections.find(s => s.id === this.activeSection);
            return section ? section.component : null; // Returns the (now raw) component definition
        }
    },
    methods: {
        deepClone(obj) {
            if (obj === null || typeof obj !== 'object') return obj;
            if (obj instanceof Date) return new Date(obj.getTime());
            if (Array.isArray(obj)) {
                const arrCopy = [];
                for (let i = 0; i < obj.length; i++) arrCopy[i] = this.deepClone(obj[i]);
                return arrCopy;
            }
            const objCopy = {};
            for (const key in obj) {
                if (Object.prototype.hasOwnProperty.call(obj, key)) objCopy[key] = this.deepClone(obj[key]);
            }
            return objCopy;
        },
        setActiveSection(sectionId) {
            if (this.settingsChanged) {
                 this.$store.state.yesNoDialog.askQuestion(`Discard unsaved changes in the current section?`, 'Discard', 'Stay')
                    .then(yes => {
                        if (yes) {
                            this.cancelConfiguration(false);
                            this.activeSection = sectionId;
                        }
                    });
            } else {
                this.activeSection = sectionId;
            }
        },
        handleSettingUpdated(payload) {
            if (!this.editableConfig) {
                 this.editableConfig = this.deepClone(this.$store.state.config);
            }
            const keys = payload.key.split('.');
            let current = this.editableConfig;
            try {
                while (keys.length > 1) {
                    const k = keys.shift();
                    const arrayMatch = k.match(/^(\w+)\[(\d+)\]$/);
                    let targetKey = k, index = -1;
                    if (arrayMatch) { targetKey = arrayMatch[1]; index = parseInt(arrayMatch[2], 10); }
                    if (!current || typeof current !== 'object' || !current.hasOwnProperty(targetKey)) throw new Error(`Invalid path segment: ${targetKey}`);
                    if (index !== -1) {
                         if (!Array.isArray(current[targetKey]) || index >= current[targetKey].length) throw new Error(`Invalid array index: ${index} for key ${targetKey}`);
                         current = current[targetKey][index];
                    } else { current = current[targetKey]; }
                }
                const finalKey = keys[0];
                const finalArrayMatch = finalKey.match(/^(\w+)\[(\d+)\]$/);
                let finalTargetKey = finalKey, finalIndex = -1;
                if (finalArrayMatch) { finalTargetKey = finalArrayMatch[1]; finalIndex = parseInt(finalArrayMatch[2], 10); }
                if (typeof current !== 'object' || current === null) throw new Error(`Cannot set property on non-object: ${finalKey}`);
                 if (finalIndex !== -1) {
                     if (!current.hasOwnProperty(finalTargetKey) || !Array.isArray(current[finalTargetKey]) || finalIndex >= current[finalTargetKey].length) throw new Error(`Invalid final array index: ${finalIndex} for key ${finalTargetKey}`);
                     current[finalTargetKey][finalIndex] = payload.value;
                 } else { current[finalTargetKey] = payload.value; }
                this.settingsChanged = true;
            } catch (error) {
                 this.$store.state.toast.showToast(`Error updating setting ${payload.key}: ${error.message}`, 4, false);
            }
        },
        async refreshConfigInView() {
            this.isLoading = true;
            this.loading_text = "Refreshing config...";
            try {
                // 1. Refresh the main configuration (gets the new binding_name)
                await this.$store.dispatch('refreshConfig');

                // 2. **** ADD THIS ****: Explicitly refresh model lists based on the NEW config
                //    (Assuming your store has actions named 'refreshModelsZoo' and 'refreshModelsArr'
                //     that fetch models based on the current store.state.config.binding_name)
                
                await this.$store.dispatch('refreshModels');
                await this.$store.dispatch('refreshModelsZoo');

                // 3. Reset local editable state
                this.editableConfig = null;
                this.settingsChanged = false;

                this.$store.state.toast.showToast("Configuration refreshed.", 2, true); // Optional feedback

            } catch (error) {
                this.$store.state.toast.showToast("Failed to load configuration.", 4, false);
                console.error("Error refreshing config or model lists:", error);
                this.editableConfig = null; // Discard edits even on failure for safety
                this.settingsChanged = false;
            } finally {
                this.isLoading = false;
                nextTick(() => { feather.replace() });
            }
        },
        async applyConfiguration() {
            if (!this.settingsChanged || !this.editableConfig) {
                this.$store.state.toast.showToast("No changes to apply.", 3, false); return;
            }
            this.isLoading = true;
            this.loading_text = "Applying settings...";
            let success = false;
            try {
                 const res = await axios.post('/apply_settings', { client_id: this.$store.state.client_id, config: this.editableConfig }, { headers: posts_headers });
                if (res.data.status) {
                    this.$store.state.toast.showToast("Settings applied. Refreshing...", 4, true);
                    success = true;
                    await this.refreshConfigInView(); // Refreshes store, resets local state
                } else {
                    this.$store.state.toast.showToast(`Apply failed: ${res.data.error || 'Error'}`, 4, false);
                }
            } catch (error) {
                this.$store.state.toast.showToast(`Error applying settings: ${error.message || error}`, 4, false);
            } finally {
                // Only set loading to false if apply failed. If successful, refreshConfigInView handles it.
                 if (!success) {
                    this.isLoading = false;
                 }
            }
        },
        cancelConfiguration(askRefresh = true) {
            this.editableConfig = null;
            this.settingsChanged = false;
        },
        async saveConfiguration() {
            this.isLoading = true;
            this.loading_text = "Saving configuration...";
            try {
                const res = await axios.post('/save_settings', { client_id: this.$store.state.client_id }, { headers: posts_headers });
                if (res.data.status) this.$store.state.toast.showToast("Settings saved successfully.", 4, true);
                else this.$store.state.messageBox.showMessage(`Error saving settings: ${res.data.error || 'Error'}`);
            } catch (error) { this.$store.state.messageBox.showMessage(`Error saving settings: ${error.message}`);
            } finally { this.isLoading = false; 
                this.$store.commit('refreshBindings')
                this.$store.commit('refreshModelsZoo')
            }
        },
        reset_configuration() {
            this.$store.state.yesNoDialog.askQuestion("Reset config to default? This deletes current settings.", 'Reset', 'Cancel')
            .then(async (yes) => {
                if (yes) {
                    this.isLoading = true; this.loading_text = "Resetting..."; let success = false;
                    try {
                        const res = await axios.post('/reset_settings', { client_id: this.$store.state.client_id }, { headers: posts_headers });
                        if (res.data.status) {
                            this.$store.state.messageBox.showMessage("Settings reset. Reloading...");
                            success = true;
                            setTimeout(() => window.location.reload(), 2000);
                        } else { this.$store.state.messageBox.showMessage(`Reset failed: ${res.data.error || 'Error'}`); }
                    } catch (error) { this.$store.state.messageBox.showMessage(`Reset failed: ${error.message}`);
                    } finally { if (!success) this.isLoading = false; }
                }
            });
        },
        async restart_program() {
            this.loading_text = "Restarting..."; this.isLoading = true; let success = false;
            try {
                const res = await this.api_post_req('restart_program');
                if (res.status) {
                    this.$store.state.toast.showToast('Restarting LoLLMs...', 4, true); success = true;
                    // Assume restart happens, don't unset loading
                } else { this.$store.state.toast.showToast(`Restart command failed: ${res.error || 'Error'}`, 4, false); }
            } catch (error) { /* Handled by api_post_req toast */
            } finally { if (!success) this.isLoading = false; }
        },
        async clear_uploads() {
            this.loading_text = "Clearing uploads..."; this.isLoading = true;
            try {
                const res = await this.api_get_req('clear_uploads');
                if (res.status) this.$store.state.toast.showToast('Uploads folder cleared!', 4, true);
                else this.$store.state.toast.showToast(`Clear failed: ${res.error || 'Error'}`, 4, false);
            } catch (error) { /* Handled by api_get_req toast */ } finally { this.isLoading = false; }
        },
        async update_software() {
            this.loading_text = "Updating..."; this.isLoading = true; let success = false;
            try {
                const res = await this.api_post_req('update_software');
                this.$store.state.toast.showToast('Update initiated. LoLLMs might restart.', 4, true);
                this.has_updates = false; success = true; // Assume restart happens or is attempted
                if (!res.status) { this.$store.state.toast.showToast(`Update command sent, server reported issue: ${res.error || 'Unknown'}`, 4, false); }
                 // Don't unset loading if restart is expected
            } catch (error) { /* Handled by api_post_req toast */
            } finally { if (!success) this.isLoading = false; }
        },
        async updateHasUpdates() {
            try {
                const res = await this.api_get_req("check_update");
                this.has_updates = res?.update_availability || false;
                nextTick(() => { feather.replace() });
            } catch (error) { this.has_updates = false; /* Handled by api_get_req toast */ }
        },
        async api_get_req(endpoint) {
             // Use store's version if injected, otherwise fallback to local axios call
             if (this.$store.state.api_get_req) return this.$store.state.api_get_req(endpoint);
             try {
                 const res = await axios.get(`/${endpoint}?client_id=${this.$store.state.client_id}`);
                 return res.data;
             } catch (error) { this.$store.state.toast.showToast(`GET Error: ${error.message}`, 4, false); throw error; }
        },
        async api_post_req(endpoint, data = {}) {
             // Use store's version if injected
             if (this.$store.state.api_post_req) return this.$store.state.api_post_req(endpoint, data);
             try {
                 const payload = { ...data, client_id: this.$store.state.client_id };
                 const res = await axios.post(`/${endpoint}`, payload, { headers: posts_headers });
                 return res.data;
             } catch (error) { this.$store.state.toast.showToast(`POST Error: ${error.message}`, 4, false); throw error; }
        }
    },
    mounted() {
        this.refreshConfigInView();
        this.updateHasUpdates();
        nextTick(() => { feather.replace(); });
    },
    updated() {
        nextTick(() => { feather.replace(); });
    }
};
</script>

<style scoped>
.icon-button { @apply p-1.5 rounded-full text-gray-600 dark:text-gray-400 duration-150 active:scale-90; }
.icon-button:hover { @apply bg-gray-200 dark:bg-gray-700; }
.panels-color { @apply bg-white dark:bg-gray-800; }
.theme-button-success { @apply bg-green-600 hover:bg-green-700 text-white focus:ring-2 focus:ring-offset-2 focus:ring-green-500 dark:focus:ring-offset-gray-900; }
.theme-button-danger { @apply bg-red-600 hover:bg-red-700 text-white focus:ring-2 focus:ring-offset-2 focus:ring-red-500 dark:focus:ring-offset-gray-900; }
.theme-text-primary { @apply text-gray-900 dark:text-gray-100; }
.theme-text-secondary { @apply text-gray-600 dark:text-gray-400; }
.theme-text-muted { @apply text-gray-500 dark:text-gray-500; }
.theme-text-warning { @apply text-yellow-600 dark:text-yellow-400; }
.theme-text-danger { @apply text-red-600 dark:text-red-400; }
.theme-text-success { @apply text-green-600 dark:text-green-400; }
.theme-bg-primary { @apply bg-gray-100 dark:bg-gray-900; }
.theme-bg-secondary { @apply bg-white dark:bg-gray-800; }
.theme-border-primary { @apply border-gray-200 dark:border-gray-700; }
.theme-border-b { @apply border-b; }
.theme-scrollbar::-webkit-scrollbar { width: 8px; height: 8px; }
.theme-scrollbar::-webkit-scrollbar-track { @apply bg-gray-100 dark:bg-gray-700 rounded-lg; }
.theme-scrollbar::-webkit-scrollbar-thumb { @apply bg-gray-300 dark:bg-gray-500 rounded-lg; }
.theme-scrollbar::-webkit-scrollbar-thumb:hover { @apply bg-gray-400 dark:bg-gray-400; }
.theme-ring-bg { @apply ring-white dark:ring-gray-800; } /* Example ring bg */
.theme-bg-danger { @apply bg-red-500; }
.theme-spinner-color { @apply text-blue-600 dark:text-blue-400 fill-blue-200 dark:fill-blue-700; }
</style>