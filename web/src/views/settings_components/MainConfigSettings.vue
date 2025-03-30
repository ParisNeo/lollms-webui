// src/components/settings_components/MainConfigSettings.vue
<template>
    <div class="space-y-6 p-4 md:p-6 bg-white dark:bg-gray-800 rounded-lg shadow-md border border-gray-200 dark:border-gray-700">
        <h2 class="text-xl font-semibold text-gray-800 dark:text-gray-200 border-b border-gray-200 dark:border-gray-700 pb-2">
            Main Configuration
        </h2>

        <!-- Application Branding Section -->
        <div class="space-y-4 p-4 border border-gray-200 dark:border-gray-600 rounded-lg">
            <h3 class="text-lg font-medium text-gray-700 dark:text-gray-300 mb-3">Application Branding</h3>

            <!-- App Name -->
            <div class="setting-item">
                <label for="app_custom_name" class="setting-label">Application Name</label>
                <input
                    type="text"
                    id="app_custom_name"
                    :value="$store.state.config.app_custom_name"
                    @input="updateValue('app_custom_name', $event.target.value)"
                    class="input-field"
                    placeholder="Default: LoLLMs"
                >
            </div>

            <!-- App Slogan -->
            <div class="setting-item">
                <label for="app_custom_slogan" class="setting-label">Application Slogan</label>
                <input
                    type="text"
                    id="app_custom_slogan"
                    :value="$store.state.config.app_custom_slogan"
                    @input="updateValue('app_custom_slogan', $event.target.value)"
                    class="input-field"
                    placeholder="Default: Lord of Large Language Models"
                >
            </div>

            <!-- App Logo -->
            <div class="setting-item items-start">
                <label class="setting-label pt-2">Application Logo</label>
                <div class="flex-1 flex items-center gap-4">
                     <div class="w-12 h-12 rounded-full overflow-hidden bg-gray-200 dark:bg-gray-700 ring-2 ring-offset-2 dark:ring-offset-gray-800 ring-gray-300 dark:ring-gray-600">
                         <img :src="logoSrc" class="w-full h-full object-cover" alt="App Logo">
                     </div>
                    <div class="flex gap-2">
                        <label class="button-primary text-sm cursor-pointer">
                            Upload Logo
                            <input type="file" @change="uploadLogo" accept="image/*" class="hidden" :disabled="isUploadingLogo">
                        </label>
                         <button
                            v-if="$store.state.config.app_custom_logo"
                            @click="removeLogo"
                            class="button-danger text-sm"
                            :disabled="isUploadingLogo">
                            Remove Logo
                        </button>
                    </div>
                     <span v-if="isUploadingLogo" class="text-xs text-gray-500 dark:text-gray-400 italic ml-2">Uploading...</span>
                </div>
            </div>

             <!-- Welcome Message -->
             <div class="setting-item items-start">
                 <label for="app_custom_welcome_message" class="setting-label pt-2">Custom Welcome Message</label>
                 <textarea
                    id="app_custom_welcome_message"
                    :value="$store.state.config.app_custom_welcome_message"
                    @input="updateValue('app_custom_welcome_message', $event.target.value)"
                    class="input-field min-h-[80px] resize-y"
                    placeholder="Enter a custom welcome message shown on the main page (leave blank for default)."
                 ></textarea>
             </div>
        </div>

        <!-- UI Behavior Section -->
         <div class="space-y-4 p-4 border border-gray-200 dark:border-gray-600 rounded-lg">
            <h3 class="text-lg font-medium text-gray-700 dark:text-gray-300 mb-3">UI & Behavior</h3>

            <!-- Auto Title -->
            <div class="toggle-item">
                <label for="auto_title" class="toggle-label">
                    Automatic Discussion Naming
                     <span class="toggle-description">Let AI name your discussions automatically based on the first message.</span>
                </label>
                <ToggleSwitch id="auto_title" :checked="$store.state.config.auto_title" @update:checked="updateBoolean('auto_title', $event)" />
            </div>

            <!-- Show Browser -->
            <div class="toggle-item">
                <label for="auto_show_browser" class="toggle-label">
                    Auto-launch Browser
                     <span class="toggle-description">Open the default web browser automatically when LoLLMs starts.</span>
                </label>
                <ToggleSwitch id="auto_show_browser" :checked="$store.state.config.auto_show_browser" @update:checked="updateBoolean('auto_show_browser', $event)" />
            </div>

             <!-- Show Change Log -->
            <div class="toggle-item">
                <label for="app_show_changelogs" class="toggle-label">
                    Show Startup Changelog
                     <span class="toggle-description">Display the changelog modal window when the application starts after an update.</span>
                </label>
                <ToggleSwitch id="app_show_changelogs" :checked="$store.state.config.app_show_changelogs" @update:checked="updateBoolean('app_show_changelogs', $event)" />
            </div>

             <!-- Show Fun Facts -->
            <div class="toggle-item">
                <label for="app_show_fun_facts" class="toggle-label">
                    Show Fun Facts
                     <span class="toggle-description">Display fun facts related to AI and LLMs while loading or waiting.</span>
                </label>
                <ToggleSwitch id="app_show_fun_facts" :checked="$store.state.config.app_show_fun_facts" @update:checked="updateBoolean('app_show_fun_facts', $event)" />
            </div>

             <!-- Enhanced Copy -->
            <div class="toggle-item">
                <label for="copy_to_clipboard_add_all_details" class="toggle-label">
                    Enhanced Message Copy
                     <span class="toggle-description">Include metadata (sender, model, etc.) when copying messages from discussions.</span>
                </label>
                 <ToggleSwitch id="copy_to_clipboard_add_all_details" :checked="$store.state.config.copy_to_clipboard_add_all_details" @update:checked="updateBoolean('copy_to_clipboard_add_all_details', $event)" />
            </div>
        </div>

        <!-- Server & Access Section -->
        <div class="space-y-4 p-4 border border-gray-200 dark:border-gray-600 rounded-lg">
             <h3 class="text-lg font-medium text-gray-700 dark:text-gray-300 mb-3">Server & Access</h3>

            <!-- Remote Access Warning & Toggle -->
             <div class="setting-item items-start p-4 bg-red-50 dark:bg-red-900/20 rounded-lg border border-red-200 dark:border-red-700">
                <div class="flex justify-between items-start w-full">
                    <label for="force_accept_remote_access" class="flex-1 mr-4">
                        <span class="font-bold text-sm text-red-700 dark:text-red-400 flex items-center gap-2">
                             <i data-feather="alert-triangle" class="w-5 h-5"></i> Enable Remote Access (Security Risk)
                         </span>
                         <p class="mt-2 text-xs text-red-600 dark:text-red-400/90">
                             <strong>Warning:</strong> Enabling this allows connections from any device on your network (or potentially the internet if port-forwarded).
                             <strong class="block mt-1">Only enable if you understand the risks and have secured your network.</strong>
                         </p>
                    </label>
                    <ToggleSwitch id="force_accept_remote_access" :checked="$store.state.config.force_accept_remote_access" @update:checked="updateBoolean('force_accept_remote_access', $event)" />
                </div>
            </div>

            <!-- Headless Mode -->
            <div class="toggle-item">
                <label for="headless_server_mode" class="toggle-label">
                    Headless Server Mode
                     <span class="toggle-description">Run LoLLMs without the Web UI. Useful for server deployments or API-only usage. This setting requires a restart.</span>
                </label>
                 <ToggleSwitch id="headless_server_mode" :checked="$store.state.config.headless_server_mode" @update:checked="updateBoolean('headless_server_mode', $event)" />
            </div>
        </div>

    </div>
</template>

<script>
import axios from 'axios';
import feather from 'feather-icons';
import { nextTick } from 'vue';
import ToggleSwitch from '@/components/ToggleSwitch.vue';
import defaultLogoPlaceholder from "@/assets/logo.png"; // Your default logo

export default {
    name: 'MainConfigSettings',
    components: {
        ToggleSwitch
    },
    props: {
        loading: { type: Boolean, default: false }, // Note: loading prop is defined but not used in the template/script
        settingsChanged: { type: Boolean, default: false }, // Note: settingsChanged prop is defined but not used in the template/script
        api_post_req: { type: Function, required: true },
        show_toast: { type: Function, required: true },
        client_id: { type: String, required: true }
    },
    emits: ['update:setting', 'settings-changed'], // settings-changed is emitted but not explicitly triggered here, maybe in parent?

    data() {
        return {
            isUploadingLogo: false,
            // defaultLogoPlaceholder is used directly in computed, no need for data property unless it changes
        };
    },

    computed: {
        logoSrc() {
            if (this.$store.state.config.app_custom_logo) {
                // Assuming axios.defaults.baseURL is configured globally
                return `${axios.defaults.baseURL}/user_infos/${this.$store.state.config.app_custom_logo}`;
            }
            return defaultLogoPlaceholder;
        }
    },

    methods: {
        updateValue(key, value) {
            this.$emit('update:setting', { key, value });
            this.$emit('settings-changed', true); // Optionally emit settings-changed on any update
        },

        updateBoolean(key, value) {
            this.$emit('update:setting', { key: key, value: Boolean(value) });
             this.$emit('settings-changed', true); // Optionally emit settings-changed on any update
        },

        async uploadLogo(event) {
            const file = event.target.files[0];
            if (!file) return;

            this.isUploadingLogo = true;
            const formData = new FormData();
            formData.append('logo', file);
            formData.append('client_id', this.client_id); // Include client_id if required by backend

            try {
                const response = await axios.post('/upload_logo', formData, {
                     headers: { 'Content-Type': 'multipart/form-data' }
                });

                if (response.data && response.data.status) {
                     this.show_toast("Logo uploaded successfully!", 4, true);
                     // Emit update for the parent to handle config change
                     this.$emit('update:setting', { key: 'app_custom_logo', value: response.data.filename });
                     this.$emit('settings-changed', true);
                } else {
                    this.show_toast(`Logo upload failed: ${response.data.error || 'Unknown error'}`, 4, false);
                }
            } catch (error) {
                console.error('Error uploading logo:', error);
                this.show_toast(`Error uploading logo: ${error.response?.data?.error || error.message || 'Unknown error'}`, 4, false);
            } finally {
                this.isUploadingLogo = false;
                // Reset file input for potential re-upload of the same file
                if (event.target) {
                    event.target.value = null;
                }
            }
        },

        async removeLogo() {
            this.isUploadingLogo = true; // Prevent actions during removal
             try {
                // Use the provided api_post_req function prop for consistency
                const response = await this.api_post_req('/remove_logo',{client_id: this.client_id}); // Send client_id if needed
                if (response.status) {
                    this.show_toast("Logo removed successfully!", 4, true);
                    // Emit update for the parent to handle config change
                     this.$emit('update:setting', { key: 'app_custom_logo', value: null });
                     this.$emit('settings-changed', true);
                } else {
                    this.show_toast(`Failed to remove logo: ${response.error || 'Unknown error'}`, 4, false);
                }
            } catch (error) {
                console.error('Error removing logo:', error);
                this.show_toast(`Error removing logo: ${error.response?.data?.error || error.message || 'Unknown error'}`, 4, false);
            } finally {
                this.isUploadingLogo = false;
            }
        },
        // Helper to ensure Feather icons are rendered after DOM updates
        replaceFeatherIcons() {
             nextTick(() => {
                 try {
                    feather.replace();
                 } catch (e) {
                    console.error("Feather icons replacement failed:", e);
                 }
            });
        }
    },

    mounted() {
        this.replaceFeatherIcons();
    },

    updated() {
        // Re-run feather replace if the component updates (e.g., v-if changes)
        this.replaceFeatherIcons();
    }
};
</script>

<style scoped>
/* Styles remain the same */
.setting-item {
    @apply flex flex-col md:flex-row md:items-center gap-2 md:gap-4 py-2;
}

.setting-label {
    @apply block text-sm font-medium text-gray-700 dark:text-gray-300 w-full md:w-1/3 lg:w-1/4 flex-shrink-0;
}

.input-field {
     @apply block w-full px-3 py-2 bg-gray-50 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 focus:border-blue-500 dark:focus:ring-offset-gray-800 sm:text-sm disabled:opacity-50;
}

.toggle-item {
    @apply flex items-center justify-between p-3 hover:bg-gray-50 dark:hover:bg-gray-700 rounded-lg transition-colors;
}

.toggle-label {
    @apply text-sm font-medium text-gray-700 dark:text-gray-300 cursor-pointer flex-1 mr-4;
}
.toggle-description {
     @apply block text-xs text-gray-500 dark:text-gray-400 mt-1 font-normal;
}

/* Updated Button Styles */
.button-primary {
    /* Assuming 'primary' is defined as blue-600 in config or default */
    @apply px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md shadow-sm transition duration-150 ease-in-out cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed;
}
.button-danger {
    @apply px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-md shadow-sm transition duration-150 ease-in-out cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed;
}
</style>