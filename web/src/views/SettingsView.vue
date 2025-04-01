<template>
    <!-- Apply base theme background and text color to the root element -->
    <div class="flex h-screen w-screen font-sans antialiased theme-bg-primary theme-text-primary">

        <!-- Sidebar -->
        <!-- Use theme classes for sidebar background and border -->
        <SettingsSidebar
            :sections="sections"
            :active-section="activeSection"
            @update:activeSection="setActiveSection"
            class="flex-shrink-0 w-64 border-r theme-border-primary theme-bg-secondary overflow-y-auto theme-scrollbar"
        />

        <!-- Main Content Area -->
        <div class="flex-1 flex flex-col overflow-hidden">
            <!-- Top Control Bar -->
            <!-- Use theme classes for the top bar background and add a bottom border for separation -->
            <div :class="['sticky top-0 z-20 flex items-center justify-between p-3 gap-3 shadow-md theme-bg-secondary theme-border-b theme-border-primary', isLoading ? 'opacity-50 pointer-events-none':'']">
                <div class="flex items-center gap-4 flex-1">
                    <!-- Save/Cancel Confirmation -->
                     <!-- Use a theme class for warning/highlight text -->
                     <div v-if="settingsChanged && !isLoading" class="flex items-center gap-2 theme-text-warning animate-pulse">
                        <!-- theme-text-warning: For attention-grabbing status text like unsaved changes -->
                        <i data-feather="alert-circle" class="w-5 h-5"></i>
                        <span class="text-sm font-medium">Settings have changed</span>
                    </div>

                    <!-- Save/Reset Actions -->
                    <!-- Base text color inherits, hover uses theme's secondary color -->
                    <div v-if="!settingsChanged && !isLoading" class="flex gap-3 items-center">
                         <button title="Reset configuration to default" class="icon-button theme-text-secondary hover:theme-text-primary" @click="reset_configuration()">
                            <!-- Use theme-text-secondary for icons, hover to theme-text-primary or theme-text-accent -->
                            <i data-feather="refresh-ccw"></i>
                         </button>
                         <button title="Restart program" class="icon-button theme-text-secondary hover:theme-text-primary" @click="restart_program()">
                            <i data-feather="power"></i>
                         </button>
                         <button title="Clear uploads folder" class="icon-button theme-text-secondary hover:theme-text-danger" @click="clear_uploads()">
                             <!-- Use theme-text-danger for destructive action hover -->
                             <i data-feather="trash-2"></i>
                         </button>
                         <button v-if="has_updates" title="Upgrade program" class="icon-button theme-text-success hover:theme-text-primary relative" @click="update_software()">
                             <!-- Use theme-text-success for positive status like updates -->
                             <i data-feather="arrow-up-circle"></i>
                             <!-- Ring color could also be themed if needed -->
                             <span class="absolute top-0 right-0 block h-2 w-2 rounded-full theme-bg-danger ring-2 theme-ring-bg"></span>
                             <!-- Assuming theme-ring-bg provides the appropriate background color for the ring outline -->
                         </button>
                    </div>
                </div>

                <!-- Apply/Cancel Buttons -->
                <!-- Use theme button classes -->
                <div v-if="settingsChanged && !isLoading" class="flex items-center gap-2">
                     <button class="flex items-center gap-2 px-3 py-1.5 rounded theme-button-success duration-150 active:scale-95"
                             title="Apply changes"
                             type="button"
                             @click.stop="applyConfiguration()">
                         <!--
                           - theme-button-success: Styles for success/apply actions (background, text color, hover).
                         -->
                         <span class="font-medium text-sm">Apply</span>
                         <i data-feather="check" class="w-4 h-4"></i>
                     </button>
                     <button class="flex items-center gap-2 px-3 py-1.5 rounded theme-button-danger duration-150 active:scale-95"
                             title="Cancel changes"
                             type="button"
                             @click.stop="cancelConfiguration()">
                          <!--
                           - theme-button-danger: Styles for danger/cancel actions (background, text color, hover).
                         -->
                         <span class="font-medium text-sm">Cancel</span>
                         <i data-feather="x" class="w-4 h-4"></i>
                     </button>
                </div>

                 <!-- Loading Indicator -->
                 <!-- Use theme text class for muted/secondary text -->
                 <div v-if="isLoading" class="flex items-center gap-2 text-sm theme-text-muted">
                     <span>{{ loading_text }}</span>
                     <!-- Spinner fill color already aligns with the concept of 'secondary' from App.vue -->
                     <svg aria-hidden="true"
                          class="w-5 h-5 animate-spin theme-spinner-color"
                          viewBox="0 0 100 101"
                          fill="none"
                          xmlns="http://www.w3.org/2000/svg">
                         <path d="M100 50.5908C100 78.2051 77.6142 100.591 50 100.591C22.3858 100.591 0 78.2051 0 50.5908C0 22.9766 22.3858 0.59082 50 0.59082C77.6142 0.59082 100 22.9766 100 50.5908ZM9.08144 50.5908C9.08144 73.1895 27.4013 91.5094 50 91.5094C72.5987 91.5094 90.9186 73.1895 90.9186 50.5908C90.9186 27.9921 72.5987 9.67226 50 9.67226C27.4013 9.67226 9.08144 27.9921 9.08144 50.5908Z"
                             fill="currentColor" />
                         <path d="M93.9676 39.0409C96.393 38.4038 97.8624 35.9116 97.0079 33.5539C95.2932 28.8227 92.871 24.3692 89.8167 20.348C85.8452 15.1192 80.8826 10.7238 75.2124 7.41289C69.5422 4.10194 63.2754 1.94025 56.7698 1.05124C51.7666 0.367541 46.6976 0.446843 41.7345 1.27873C39.2613 1.69328 37.813 4.19778 38.4501 6.62326C39.0873 9.04874 41.5694 10.4717 44.0505 10.1071C47.8511 9.54855 51.7191 9.52689 55.5402 10.0491C60.8642 10.7766 65.9928 12.5457 70.6331 15.2552C75.2735 17.9648 79.3347 21.5619 82.5849 25.841C84.9175 28.9121 86.7997 32.2913 88.1811 35.8758C89.083 38.2158 91.5421 39.6781 93.9676 39.0409Z"
                             fill="currentFill" /> <!-- Typically 'currentFill' works well for spinners -->
                     </svg>
                     <span class="sr-only">Loading...</span>
                 </div>
            </div>

            <!-- Content Area -->
            <!-- Apply themed scrollbar to the main content area -->
            <main class="flex-1 overflow-x-hidden overflow-y-auto theme-scrollbar p-6">
                 <!-- The component inside will inherit theme-bg-primary and theme-text-primary. -->
                 <!-- Ensure the components rendered here ALSO use theme classes for their internal elements (inputs, labels, cards, etc.) -->
                <component
                    :is="currentComponent"
                    v-if="$store.state.config"
                    :loading="isLoading"
                    :settings-changed="settingsChanged"
                    @settings-changed="handleSettingsChanged"
                    :api_get_req="api_get_req"
                    :api_post_req="api_post_req"
                    :refresh_config="refreshConfig"
                    :show_toast="(m,d,s)=> $store.state.toast.showToast(m,d,s)"
                    :show_yes_no_dialog="(q,y,n)=> $store.state.yesNoDialog.askQuestion(q,y,n)"
                    :show_message_box="(m)=> $store.state.messageBox.showMessage(m)"
                    :client_id="$store.state.client_id"
                    :show_universal_form="(f, t, y, n)=> $store.state.universalForm.showForm(f, t, y, n)"
                />
                 <div v-else class="flex justify-center items-center h-full theme-text-secondary">
                     <!-- Use theme text color for loading message -->
                     <p>Loading configuration...</p>
                 </div>
            </main>
        </div>

    </div>
</template>
<script>
import { nextTick } from 'vue';
import axios from 'axios';
import feather from 'feather-icons';
// import socket from '@/services/websocket.js'; // Uncomment if needed

// Import Components
import SettingsSidebar from '@/components/SettingsSidebar.vue';
// Child Setting Components
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
        SystemStatusSettings,
        SmartRoutingSettings,
        MainConfigSettings,
        DataManagementSettings,
        InternetSettings,
        ServicesZooSettings,
        BindingZooSettings,
        ModelsZooSettings,
        PersonalitiesZooSettings,
        FunctionCallsZooSettings,
        ModelConfigSettings,
    },
    data() {
        return {
            isLoading: false,
            settingsChanged: false,
            has_updates: false,
            activeSection: 'system_status', // Default section
            loading_text: "Loading settings...",
            sections: [ // Note: Component references are direct now
                { id: 'system_status', name: 'System Status', icon: 'activity', component: SystemStatusSettings },
                { id: 'main_config', name: 'Main Config', icon: 'sliders', component: MainConfigSettings },
                { id: 'smart_routing', name: 'Smart Routing', icon: 'git-branch', component: SmartRoutingSettings },
                { id: 'data_management', name: 'Data Management', icon: 'database', component: DataManagementSettings },
                { id: 'internet', name: 'Internet', icon: 'wifi', component: InternetSettings },
                { id: 'services_zoo', name: 'Services Zoo', icon: 'server', component: ServicesZooSettings },
                { id: 'model_config', name: 'Model Parameters', icon: 'cpu', component: ModelConfigSettings },
                { id: 'binding_zoo', name: 'Bindings', icon: 'link', component: BindingZooSettings },
                { id: 'models_zoo', name: 'Models', icon: 'package', component: ModelsZooSettings },
                { id: 'personalities_zoo', name: 'Personalities', icon: 'users', component: PersonalitiesZooSettings },
                { id: 'function_calls_zoo', name: 'Function Calls', icon: 'tool', component: FunctionCallsZooSettings },
            ]
        };
    },
    computed: {
        currentComponent() {
            const section = this.sections.find(s => s.id === this.activeSection);
            // In Options API, Vue automatically handles component registration if listed in `components`
            return section ? section.component : null;
        }
    },
    watch: {
    },
    methods: {
        setActiveSection(sectionId) {
            if (this.settingsChanged) {
                 this.$store.state.yesNoDialog.askQuestion(`You have unsaved changes in the current section. Do you want to discard them and switch?`, 'Discard Changes', 'Stay')
                    .then(yes => {
                        if (yes) {
                            this.cancelConfiguration(false); // Cancel without reloading config
                            this.activeSection = sectionId;
                        }
                    });
            } else {
                this.activeSection = sectionId;
            }
        },

        handleSettingUpdate(payload) {
            // Example: payload = { key: 'user_name', value: 'New Name' }
            const keys = payload.key.split('.');
            let current = this.$store.state.config; // Use this.configFile
            try {
                while (keys.length > 1) {
                    const k = keys.shift();
                    // Handle array indices like 'datalakes[0]'
                    const match = k.match(/(\w+)\[(\d+)\]/);
                    if (match) {
                        current = current[match[1]][parseInt(match[2])];
                    } else {
                        current = current[k];
                    }
                     if (current === undefined || current === null) {
                        console.error("Invalid key path segment:", k, "in", payload.key);
                        this.$store.state.toast.showToast(`Error updating setting: Invalid path ${payload.key}`, 4, false);
                        return; // Exit if path is invalid
                    }
                }
                const finalKey = keys[0];
                const finalMatch = finalKey.match(/(\w+)\[(\d+)\]/);
                 if (finalMatch) {
                      if (current[finalMatch[1]] === undefined || current[finalMatch[1]][parseInt(finalMatch[2])] === undefined){
                           console.error("Invalid final key path segment:", finalKey, "in", payload.key);
                            this.$store.state.toast.showToast(`Error updating setting: Invalid path ${payload.key}`, 4, false);
                            return; // Exit if final path segment is invalid
                      }
                      current[finalMatch[1]][parseInt(finalMatch[2])] = payload.value;
                  } else {
                      if (current[finalKey] === undefined){
                           console.error("Invalid final key path segment:", finalKey, "in", payload.key);
                            this.$store.state.toast.showToast(`Error updating setting: Invalid path ${payload.key}`, 4, false);
                            return; // Exit if final key is invalid
                      }
                       current[finalKey] = payload.value;
                  }
                console.log("Setting updated in parent:", payload.key, payload.value);
                 // Explicitly set settingsChanged to true AFTER successful update.
                 // The watcher might have already triggered, but this ensures it's set.
                 // Use nextTick if the watcher logic relies on the update being fully processed.
                 // nextTick(() => { this.settingsChanged = true; });
                 // However, simply setting it here is usually sufficient.
                 this.settingsChanged = true;

            } catch (error) {
                 console.error("Error processing setting update:", payload.key, error);
                 this.$store.state.toast.showToast(`Error updating setting ${payload.key}: ${error.message}`, 4, false);
            }

        },

        handleSettingsChanged() {
            console.log("settings changed")
            this.settingsChanged = true;
        },

        async refreshConfig() {
            this.isLoading = true;
            this.loading_text = "Refreshing configuration...";
            try {
                await this.$store.dispatch('refreshConfig');
                 // Create a deep copy for local editing to avoid direct mutation of store state
                this.settingsChanged = false; // Reset change status after refresh
            } catch (error) {
                console.error("Failed to refresh config:", error);
                this.$store.state.toast.showToast("Failed to load configuration.", 4, false);
            } finally {
                this.isLoading = false;
                nextTick(() => { feather.replace() }); // Ensure icons are rendered after potential DOM changes
            }
        },

        async applyConfiguration() {
            this.isLoading = true;
            this.loading_text = "Applying settings...";
            try {
                 // Send the local configFile copy
                const res = await axios.post('/apply_settings', { client_id: this.$store.state.client_id, config: this.$store.state.config }, { headers: posts_headers });
                if (res.data.status) {
                    this.$store.state.toast.showToast("Configuration applied successfully.", 4, true);
                     // Important: Refresh config from backend AFTER applying to get the potentially sanitized/validated version
                    await this.refreshConfig();
                    // refreshConfig already sets settingsChanged to false
                } else {
                    this.$store.state.toast.showToast(`Configuration apply failed: ${res.data.error || 'Unknown error'}`, 4, false);
                }
            } catch (error) {
                console.error("Error applying settings:", error);
                this.$store.state.toast.showToast(`Error applying settings: ${error.message || error}`, 4, false);
            } finally {
                this.isLoading = false;
            }
        },

        async cancelConfiguration(askRefresh = true) {
            if (askRefresh) {
                 // Reload data from the store/backend
                await this.refreshConfig();
            } else {
                this.settingsChanged = false;
            }
        },

        async saveConfiguration() {
             this.isLoading = true;
             this.loading_text = "Saving settings to disk...";
            try {
                const res = await axios.post('/save_settings', { client_id: this.$store.state.client_id }, { headers: posts_headers });
                if (res.data.status) {
                    this.$store.state.toast.showToast("Settings saved successfully.", 4, true);
                } else {
                    this.$store.state.messageBox.showMessage(`Error saving settings: ${res.data.error || 'Unknown error'}`);
                }
            } catch (error) {
                 console.error("Error saving settings:", error);
                 this.$store.state.messageBox.showMessage(`Error saving settings: ${error.message}`);
            } finally {
                this.isLoading = false;
            }
        },

        reset_configuration() {
            this.$store.state.yesNoDialog.askQuestion("Are you sure?\nThis will delete your current configuration file and revert to the default.", 'Reset Now', 'Cancel')
            .then(async (yes) => {
                if (yes) {
                    this.isLoading = true;
                    this.loading_text = "Resetting configuration...";
                    try {
                        const res = await axios.post('/reset_settings', { client_id: this.$store.state.client_id }, { headers: posts_headers });
                        if (res.data.status) {
                            this.$store.state.messageBox.showMessage("Settings reset successfully. The application will now reload.");
                            // Optional: Add a small delay before reload
                            setTimeout(() => window.location.reload(), 2000);
                        } else {
                            this.$store.state.messageBox.showMessage(`Couldn't reset settings: ${res.data.error || 'Unknown error'}`);
                             this.isLoading = false; // Only stop loading if there was an error before reload
                        }
                    } catch (error) {
                        console.error("Error resetting settings:", error);
                        this.$store.state.messageBox.showMessage(`Couldn't reset settings: ${error.message}`);
                         this.isLoading = false;
                    }
                     // isLoading might not be reset if page reloads successfully
                }
            });
        },

        async restart_program() {
            this.loading_text = "Restarting program...";
            this.isLoading = true;
            try {
                const res = await this.api_post_req('restart_program');
                if (res.status) {
                    this.$store.state.toast.showToast('Restarting LoLLMs.', 4, true);
                    // No need to set isLoading = false, as the page should become unresponsive/reload
                } else {
                    this.$store.state.toast.showToast(`Failed to restart: ${res.error || 'Unknown error'}`, 4, false);
                    this.isLoading = false;
                }
            } catch (error) {
                 // api_post_req already shows a toast on error
                 // this.$store.state.toast.showToast(`Failed to restart: ${error.message}`, 4, false);
                 this.isLoading = false;
            }
        },

        async clear_uploads() {
            this.loading_text = "Clearing uploads...";
            this.isLoading = true;
            try {
                const res = await this.api_get_req('clear_uploads'); // Assuming GET is correct
                if (res.status) {
                    this.$store.state.toast.showToast('Uploads folder cleared!', 4, true);
                } else {
                    this.$store.state.toast.showToast(`Failed to clear uploads: ${res.error || 'Unknown error'}`, 4, false);
                }
            } catch (error) {
                 // api_get_req already shows a toast on error
                 // this.$store.state.toast.showToast(`Failed to clear uploads: ${error.message}`, 4, false);
            } finally {
                this.isLoading = false;
            }
        },

        async update_software() {
            this.loading_text = "Updating software...";
            this.isLoading = true;
            try {
                const res = await this.api_post_req('update_software');
                 // Assume success or restart regardless of response status, show toast
                this.$store.state.toast.showToast('Update process initiated. LoLLMs might restart.', 4, true);
                 this.has_updates = false; // Optimistically assume update will occur or restart makes it irrelevant
                // No need to set isLoading = false if restart is expected
                if (!res.status) { // Optionally handle explicit failure message differently
                    this.$store.state.toast.showToast(`Update command sent, but server reported: ${res.error || 'Unknown issue'}`, 4, false);
                    this.isLoading = false; // Set false only if explicit failure allows continuation
                }
            } catch (error) {
                 // api_post_req shows toast
                 this.isLoading = false;
            }
        },

        async updateHasUpdates() {
            try {
                const res = await this.api_get_req("check_update");
                this.has_updates = res?.update_availability || false;
                console.log("Update available:", this.has_updates);
                nextTick(() => { feather.replace() }); // Update icons if update button appears/disappears
            } catch (error) {
                console.error("Failed to check for updates:", error);
                 // api_get_req shows toast
                this.has_updates = false;
            }
        },

        // --- API Request Helpers ---
        async api_get_req(endpoint) {
            try {
                const res = await axios.get(`/${endpoint}?client_id=${this.$store.state.client_id}`); // Pass client_id if needed by GET endpoint
                return res.data;
            } catch (error) {
                console.error(`API GET request failed for /${endpoint}:`, error);
                this.$store.state.toast.showToast(`Failed to fetch data from ${endpoint}. ${error.message}`, 4, false);
                throw error; // Re-throw error for caller handling
            }
        },

        async api_post_req(endpoint, data = {}) {
            try {
                const payload = { ...data, client_id: this.$store.state.client_id };
                const res = await axios.post(`/${endpoint}`, payload, { headers: posts_headers });
                return res.data;
            } catch (error) {
                console.error(`API POST request failed for /${endpoint}:`, error);
                 this.$store.state.toast.showToast(`Failed to post data to ${endpoint}. ${error.message}`, 4, false);
                throw error; // Re-throw error for caller handling
            }
        }
    },
    mounted() {
        this.refreshConfig(); // Load initial config
        this.updateHasUpdates();
        nextTick(() => {
            feather.replace();
        });
        // Example: Listen for socket events if needed
        // socket.on('some_event', (data) => { ... });
    },
    updated() {
        // Re-run feather icons replacement in case icons were added/changed dynamically
        nextTick(() => {
            feather.replace();
        });
    }
};
</script>

<style scoped>
/* Styles remain the same */
.icon-button {
    @apply p-1.5 rounded-full text-gray-600 dark:text-gray-400 duration-150 active:scale-90;
}
.icon-button:hover {
    @apply bg-gray-200 dark:bg-gray-700;
}

.panels-color {
  @apply bg-white dark:bg-gray-800;
}
</style>