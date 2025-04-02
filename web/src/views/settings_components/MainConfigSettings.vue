<template>
    <div class="user-settings-panel space-y-6">
        <h2 class="text-xl font-semibold text-blue-800 dark:text-blue-100 border-b border-blue-300 dark:border-blue-600 pb-2">
            Main Configuration
        </h2>

        <!-- Application Branding Section -->
        <div class="space-y-4 p-4 border border-blue-300 dark:border-blue-600 rounded-lg panels-color">
            <h3 class="text-lg font-medium text-blue-700 dark:text-blue-300 mb-3">Application Branding</h3>

            <!-- App Name -->
            <div class="setting-item">
                <label for="app_custom_name" class="setting-label">Application Name</label>
                <input
                    type="text"
                    id="app_custom_name"
                    :value="$store.state.config.app_custom_name"
                    @input="updateValue('app_custom_name', $event.target.value)"
                    class="input flex-grow"
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
                    class="input flex-grow"
                    placeholder="Default: Lord of Large Language Models"
                >
            </div>

            <!-- App Logo -->
            <div class="setting-item items-start">
                <label class="setting-label pt-2">Application Logo</label>
                <div class="flex-1 flex items-center gap-4">
                     <div class="w-12 h-12 rounded-full overflow-hidden bg-blue-200 dark:bg-blue-700 ring-2 ring-offset-2 dark:ring-offset-blue-900 ring-blue-300 dark:ring-blue-600">
                         <img :src="logoSrc" class="w-full h-full object-cover" alt="App Logo">
                     </div>
                    <div class="flex gap-2">
                        <label class="btn btn-secondary btn-sm cursor-pointer">
                            Upload Logo
                            <input type="file" @change="uploadLogo" accept="image/*" class="hidden" :disabled="isUploadingLogo">
                        </label>
                         <button
                            v-if="$store.state.config.app_custom_logo"
                            @click="removeLogo"
                            class="btn btn-secondary btn-sm text-red-500 dark:text-red-400 hover:bg-red-200 dark:hover:bg-red-700"
                            :disabled="isUploadingLogo">
                            Remove Logo
                        </button>
                    </div>
                     <span v-if="isUploadingLogo" class="text-xs text-blue-500 dark:text-blue-400 italic ml-2">Uploading...</span>
                </div>
            </div>

             <!-- Welcome Message -->
             <div class="setting-item items-start">
                 <label for="app_custom_welcome_message" class="setting-label pt-2">Custom Welcome Message</label>
                 <textarea
                    id="app_custom_welcome_message"
                    :value="$store.state.config.app_custom_welcome_message"
                    @input="updateValue('app_custom_welcome_message', $event.target.value)"
                    class="input flex-grow min-h-[80px] resize-y"
                    placeholder="Enter a custom welcome message shown on the main page (leave blank for default)."
                 ></textarea>
             </div>
        </div>

        <!-- UI Behavior Section -->
         <div class="space-y-4 p-4 border border-blue-300 dark:border-blue-600 rounded-lg panels-color">
            <h3 class="text-lg font-medium text-blue-700 dark:text-blue-300 mb-3">UI & Behavior</h3>

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
        <div class="space-y-4 p-4 border border-blue-300 dark:border-blue-600 rounded-lg panels-color">
             <h3 class="text-lg font-medium text-blue-700 dark:text-blue-300 mb-3">Server & Access</h3>

            <!-- Remote Access Warning & Toggle -->
             <div class="setting-item items-start p-4 bg-red-100 dark:bg-red-900/30 rounded-lg border border-red-300 dark:border-red-700">
                <div class="flex justify-between items-start w-full">
                    <label for="force_accept_remote_access" class="flex-1 mr-4">
                        <span class="font-bold text-sm text-red-700 dark:text-red-400 flex items-center gap-2">
                             <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="w-5 h-5 feather feather-alert-triangle"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>
                             Enable Remote Access (Security Risk)
                         </span>
                         <p class="mt-2 text-xs text-red-600 dark:text-red-500/90">
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

        <!-- Model Template Section -->
        <div class="space-y-4 p-4 border border-blue-300 dark:border-blue-600 rounded-lg panels-color">
            <h3 class="text-lg font-medium text-blue-700 dark:text-blue-300 mb-3">Model Template Configuration</h3>
             <div class="grid gap-6 bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md border border-gray-200 dark:border-gray-600">
                 <!-- Template Selection -->
                 <div class="setting-item">
                     <label for="template_type_select" class="setting-label">Template Type</label>
                     <select id="template_type_select" @change="handleTemplateSelection"
                             class="input form-select flex-grow">
                         <option value="lollms">Lollms communication template</option>
                         <option value="lollms_simplified">Lollms simplified communication template</option>
                         <option value="bare">Bare, useful when in chat mode</option>
                         <option value="llama3">LLama3 communication template</option>
                         <option value="lucie">Lucie communication template</option>
                         <option value="mistral">Mistral communication template</option>
                         <option value="deepseek">DeepSeek communication template</option>
                     </select>
                 </div>

                 <!-- Header Templates -->
                 <div class="grid md:grid-cols-2 gap-4">
                     <div class="setting-item !flex-col !items-start md:!flex-row md:!items-center">
                         <label for="start_header_id_template" class="setting-label !w-auto md:!w-1/3">Start Header Template</label>
                         <input type="text" id="start_header_id_template"
                            :value="$store.state.config.start_header_id_template"
                            @input="updateValue('start_header_id_template', $event.target.value)"
                            class="input flex-grow">
                     </div>
                     <div class="setting-item !flex-col !items-start md:!flex-row md:!items-center">
                         <label for="end_header_id_template" class="setting-label !w-auto md:!w-1/3">End Header Template</label>
                         <input type="text" id="end_header_id_template"
                            :value="$store.state.config.end_header_id_template"
                            @input="updateValue('end_header_id_template', $event.target.value)"
                            class="input flex-grow">
                     </div>
                 </div>

                 <!-- User Templates -->
                 <div class="grid md:grid-cols-2 gap-4">
                     <div class="setting-item !flex-col !items-start md:!flex-row md:!items-center">
                         <label for="start_user_header_id_template" class="setting-label !w-auto md:!w-1/3">Start User Header Template</label>
                         <input type="text" id="start_user_header_id_template"
                            :value="$store.state.config.start_user_header_id_template"
                            @input="updateValue('start_user_header_id_template', $event.target.value)"
                            class="input flex-grow">
                     </div>
                     <div class="setting-item !flex-col !items-start md:!flex-row md:!items-center">
                         <label for="end_user_header_id_template" class="setting-label !w-auto md:!w-1/3">End User Header Template</label>
                         <input type="text" id="end_user_header_id_template"
                            :value="$store.state.config.end_user_header_id_template"
                            @input="updateValue('end_user_header_id_template', $event.target.value)"
                            class="input flex-grow">
                     </div>
                 </div>

                 <!-- AI Templates -->
                 <div class="grid md:grid-cols-2 gap-4">
                     <div class="setting-item !flex-col !items-start md:!flex-row md:!items-center">
                         <label for="start_ai_header_id_template" class="setting-label !w-auto md:!w-1/3">Start AI Header Template</label>
                         <input type="text" id="start_ai_header_id_template"
                            :value="$store.state.config.start_ai_header_id_template"
                            @input="updateValue('start_ai_header_id_template', $event.target.value)"
                            class="input flex-grow">
                     </div>
                     <div class="setting-item !flex-col !items-start md:!flex-row md:!items-center">
                         <label for="end_ai_header_id_template" class="setting-label !w-auto md:!w-1/3">End AI Header Template</label>
                         <input type="text" id="end_ai_header_id_template"
                            :value="$store.state.config.end_ai_header_id_template"
                            @input="updateValue('end_ai_header_id_template', $event.target.value)"
                            class="input flex-grow">
                     </div>
                 </div>

                 <!-- Message End Templates -->
                 <div class="grid md:grid-cols-2 gap-4">
                     <div class="setting-item !flex-col !items-start md:!flex-row md:!items-center">
                         <label for="end_user_message_id_template" class="setting-label !w-auto md:!w-1/3">End User Message Template</label>
                         <input type="text" id="end_user_message_id_template"
                            :value="$store.state.config.end_user_message_id_template"
                            @input="updateValue('end_user_message_id_template', $event.target.value)"
                            class="input flex-grow">
                     </div>
                     <div class="setting-item !flex-col !items-start md:!flex-row md:!items-center">
                         <label for="end_ai_message_id_template" class="setting-label !w-auto md:!w-1/3">End AI Message Template</label>
                         <input type="text" id="end_ai_message_id_template"
                            :value="$store.state.config.end_ai_message_id_template"
                            @input="updateValue('end_ai_message_id_template', $event.target.value)"
                            class="input flex-grow">
                     </div>
                 </div>

                 <!-- Separator and System Templates -->
                 <div class="setting-item items-start">
                     <label for="separator_template" class="setting-label pt-2">Separator Template</label>
                     <textarea id="separator_template"
                            :value="$store.state.config.separator_template"
                            @input="updateValue('separator_template', $event.target.value)"
                            class="input flex-grow min-h-[60px] resize-y">
                     </textarea>
                 </div>

                 <div class="setting-item">
                     <label for="system_message_template" class="setting-label">System Message Template</label>
                     <input type="text" id="system_message_template"
                        :value="$store.state.config.system_message_template"
                        @input="updateValue('system_message_template', $event.target.value)"
                        class="input flex-grow">
                 </div>

                 <!-- Full Template Preview -->
                 <div class="setting-item items-start">
                     <label class="setting-label pt-2">Full Template Preview</label>
                     <div class="p-4 bg-gray-100 dark:bg-gray-900 rounded-md flex-grow border border-gray-200 dark:border-gray-700 overflow-x-auto text-sm">
                         <div v-html="full_template" class="whitespace-pre-wrap break-words"></div>
                     </div>
                 </div>

                 <!-- Continue Message Toggle -->
                 <div class="toggle-item">
                    <label for="use_continue_message" class="toggle-label">
                        Use Continue Message
                        <span class="toggle-description">If supported by the model, use a specific token or phrase to indicate the AI should continue its response.</span>
                    </label>
                    <ToggleSwitch id="use_continue_message" :checked="$store.state.config.use_continue_message" @update:checked="updateBoolean('use_continue_message', $event)" />
                </div>
             </div>
        </div>


        <!-- Thinking Methods Section -->
        <div class="space-y-4 p-4 border border-blue-300 dark:border-blue-600 rounded-lg panels-color">
            <h3 class="text-lg font-medium text-blue-700 dark:text-blue-300 mb-3">Thinking Methods</h3>
             <div class="grid gap-6 bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md border border-gray-200 dark:border-gray-600">
                 <!-- Thinking Prompt and Preset Selection -->
                 <div class="space-y-4">
                     <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 mb-2">
                         <label for="thinking_prompt_textarea" class="setting-label !w-auto sm:!w-1/3">
                             Thinking Prompt
                             <span class="block text-xs text-gray-500 dark:text-gray-400 mt-1 font-normal">Prompt used by the AI to structure its thought process. Use `thinking` tags.</span>
                         </label>
                         <div class="flex items-center gap-2 flex-wrap">
                             <select id="thinking_preset_select" @change="selectPreset($event.target.value)" class="input form-select flex-grow min-w-[150px]">
                                 <option value="" disabled :selected="!selectedPresetName">-- Select Preset --</option>
                                 <option v-for="preset in allThinkingPresets" :key="preset.name" :value="preset.name" :selected="preset.name === selectedPresetName">
                                     {{ preset.name }} {{ preset.isLocal ? '(Local)' : '' }}
                                 </option>
                             </select>
                             <button @click="showAddThinkingPresetForm = !showAddThinkingPresetForm" class="btn btn-secondary btn-sm whitespace-nowrap">
                                 {{ showAddThinkingPresetForm ? 'Cancel Add' : 'Add New Preset' }}
                             </button>
                         </div>
                     </div>
                     <textarea
                         id="thinking_prompt_textarea"
                         :value="$store.state.config.thinking_prompt"
                         @input="updateValue('thinking_prompt', $event.target.value)"
                         class="input w-full p-4 bg-gray-100 dark:bg-gray-900 rounded-md text-sm min-h-[150px] resize-y font-mono border border-gray-200 dark:border-gray-700"
                         placeholder="<thinking>...</thinking>"
                     ></textarea>
                 </div>

                 <!-- Add New Thinking Preset Form (Inline, Collapsible) -->
                 <div v-if="showAddThinkingPresetForm" class="mt-4 p-4 border border-gray-300 dark:border-gray-600 rounded-lg bg-gray-50 dark:bg-gray-700 space-y-4">
                    <h4 class="text-md font-semibold text-gray-800 dark:text-gray-200">Add New Local Preset</h4>
                     <form @submit.prevent="saveNewPreset" class="space-y-4">
                         <div class="setting-item !py-0">
                             <label for="new_preset_name" class="setting-label">Name <span class="text-red-500">*</span></label>
                             <input id="new_preset_name" v-model="newPreset.name" class="input flex-grow" required>
                         </div>
                         <div class="setting-item !py-0">
                             <label for="new_preset_desc" class="setting-label">Description <span class="text-red-500">*</span></label>
                             <input id="new_preset_desc" v-model="newPreset.description" class="input flex-grow" required>
                         </div>
                         <div class="setting-item !py-0">
                             <label for="new_preset_author" class="setting-label">Author <span class="text-red-500">*</span></label>
                             <input id="new_preset_author" v-model="newPreset.author" class="input flex-grow" required>
                         </div>
                         <div class="setting-item !py-0 items-start">
                             <label for="new_preset_prompt" class="setting-label pt-2">Thinking Prompt <span class="text-red-500">*</span></label>
                             <textarea
                                 id="new_preset_prompt"
                                 v-model="newPreset.prompt"
                                 class="input w-full min-h-[100px] resize-y font-mono flex-grow"
                                 required
                                 placeholder="Enter the thinking prompt. Use <thinking>...</thinking> tags."
                             ></textarea>
                         </div>
                         <div class="flex justify-end space-x-2">
                             <button type="submit" class="btn btn-primary btn-sm">Save Preset</button>
                         </div>
                     </form>
                 </div>
             </div>
        </div>

    </div>
</template>

<script>
import axios from 'axios';
import feather from 'feather-icons';
import { nextTick } from 'vue';
import ToggleSwitch from '@/components/ToggleSwitch.vue';
import defaultLogoPlaceholder from "@/assets/logo.png";

export default {
    name: 'MainConfigSettings',
    components: {
        ToggleSwitch,
    },
    props: {
        loading: { type: Boolean, default: false },
        settingsChanged: { type: Boolean, default: false },
        api_post_req: { type: Function, required: true },
        show_toast: { type: Function, required: true },
        client_id: { type: String, required: true }
    },
    emits: ['update:setting', 'settings-changed'],

    data() {
        return {
            isUploadingLogo: false,
            showAddThinkingPresetForm: false, // To toggle the inline form
            thinkingPresets: [], // Combined list of backend + local
            localThinkingPresets: [], // User-created presets stored locally
            newPreset: {
                name: '',
                description: '',
                author: '',
                prompt: ''
            },
            selectedPresetName: '', // To manage the select dropdown value
        };
    },

    computed: {
        logoSrc() {
            if (this.$store.state.config.app_custom_logo) {
                const baseURL = (axios.defaults.baseURL || '').replace(/\/$/, '');
                const logoPath = (this.$store.state.config.app_custom_logo || '').replace(/^\//, '');
                return `${baseURL}/user_infos/${logoPath}`;
            }
            return defaultLogoPlaceholder;
        },
        full_template() {
             if (!this.$store.state.config) return '';
             const config = this.$store.state.config;
             const parts = [
                 config.start_header_id_template,
                 config.system_message_template,
                 config.end_header_id_template,
                 " system message",
                 config.separator_template,
                 config.start_user_header_id_template,
                 "user name",
                 config.end_user_header_id_template,
                 " User prompt",
                 config.separator_template,
                 config.end_user_message_id_template,
                 config.separator_template,
                 config.start_ai_header_id_template,
                 "ai personality",
                 config.end_ai_header_id_template,
                 "ai response",
                 config.end_ai_message_id_template
             ];
             return parts.map(part => part || '').join('').replace(/\n/g, "<br>");
        },
        allThinkingPresets() {
             // Combine backend and local presets, ensure no duplicates by name (local takes precedence)
             const combined = [...this.localThinkingPresets];
             const localNames = new Set(this.localThinkingPresets.map(p => p.name));
             this.thinkingPresets.forEach(p => {
                 if (!localNames.has(p.name)) {
                     combined.push(p);
                 }
             });
             // Sort alphabetically for the dropdown
             return combined.sort((a, b) => a.name.localeCompare(b.name));
        }
    },

    methods: {
        updateValue(key, value) {
            this.$emit('update:setting', { key, value });
            this.$emit('settings-changed', true);
             // If thinking prompt is manually changed, deselect preset in dropdown
             if (key === 'thinking_prompt') {
                 this.selectedPresetName = '';
             }
        },

        updateBoolean(key, value) {
            this.$emit('update:setting', { key: key, value: Boolean(value) });
            this.$emit('settings-changed', true);
        },

        async uploadLogo(event) {
            const file = event.target.files[0];
            if (!file) return;

            this.isUploadingLogo = true;
            const formData = new FormData();
            formData.append('logo', file);
            formData.append('client_id', this.client_id);

            try {
                const response = await axios.post('/upload_logo', formData, {
                     headers: { 'Content-Type': 'multipart/form-data' }
                });

                if (response.data && response.data.status) {
                     this.show_toast("Logo uploaded successfully!", 4, true);
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
                if (event.target) {
                    event.target.value = null;
                }
            }
        },

        async removeLogo() {
            this.isUploadingLogo = true;
             try {
                const response = await this.api_post_req('/remove_logo',{client_id: this.client_id});
                if (response.status) {
                    this.show_toast("Logo removed successfully!", 4, true);
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

        handleTemplateSelection(event) {
            const selectedOption = event.target.value;
            let updates = {};

             if (selectedOption === 'lollms') {
                updates = {
                    start_header_id_template: "!@>", system_message_template: "system", end_header_id_template: ": ", separator_template: "\n",
                    start_user_header_id_template: "!@>", end_user_header_id_template: ": ", end_user_message_id_template: "",
                    start_ai_header_id_template: "!@>", end_ai_header_id_template: ": ", end_ai_message_id_template: ""
                };
            } else if (selectedOption === 'lollms_simplified') {
                 updates = {
                    start_header_id_template: "@>", system_message_template: "system", end_header_id_template: ": ", separator_template: "\n",
                    start_user_header_id_template: "@>", end_user_header_id_template: ": ", end_user_message_id_template: "",
                    start_ai_header_id_template: "@>", end_ai_header_id_template: ": ", end_ai_message_id_template: ""
                 };
            } else if (selectedOption === 'bare') {
                 updates = {
                    start_header_id_template: "", system_message_template: "system", end_header_id_template: ": ", separator_template: "\n",
                    start_user_header_id_template: "", end_user_header_id_template: ": ", end_user_message_id_template: "",
                    start_ai_header_id_template: "", end_ai_header_id_template: ": ", end_ai_message_id_template: ""
                 };
            } else if (selectedOption === 'llama3') {
                 updates = {
                    start_header_id_template: "<|start_header_id|>", system_message_template: "system", end_header_id_template: "<|end_header_id|>", separator_template: "<|eot_id|>",
                    start_user_header_id_template: "<|start_header_id|>", end_user_header_id_template: "<|end_header_id|>", end_user_message_id_template: "",
                    start_ai_header_id_template: "<|start_header_id|>", end_ai_header_id_template: "<|end_header_id|>", end_ai_message_id_template: ""
                 };
            } else if (selectedOption === 'lucie') {
                 updates = {
                    start_header_id_template: "<s><|start_header_id|>", system_message_template: "system", end_header_id_template: "<|end_header_id|>\n\n", separator_template: "<|eot_id|>",
                    start_user_header_id_template: "<|start_header_id|>", end_user_header_id_template: "<|end_header_id|>\n\n", end_user_message_id_template: "",
                    start_ai_header_id_template: "<|start_header_id|>", end_ai_header_id_template: "<|end_header_id|>\n\n", end_ai_message_id_template: ""
                 };
            } else if (selectedOption === 'mistral') {
                 updates = {
                    start_header_id_template: "[INST]", system_message_template: " Using this information", end_header_id_template: ": ", separator_template: "\n",
                    start_user_header_id_template: "[INST]", end_user_header_id_template: ": ", end_user_message_id_template: "[/INST]",
                    start_ai_header_id_template: "", end_ai_header_id_template: "", end_ai_message_id_template: "</s>" // Common Mistral end token
                 };
            } else if (selectedOption === 'deepseek') {
                 updates = {
                    start_header_id_template: "", system_message_template: "", end_header_id_template: "\n", separator_template: "\n", // Separator might need adjustment
                    start_user_header_id_template: "User: ", end_user_header_id_template: "\n", end_user_message_id_template: "",
                    start_ai_header_id_template: "Assistant: ", end_ai_header_id_template: "\n", end_ai_message_id_template: "<|end_of_sentence|>"
                 };
            }

            Object.entries(updates).forEach(([key, value]) => {
                 this.$emit('update:setting', { key, value });
            });
            this.$emit('settings-changed', true);
        },

        async loadThinkingPresets() {
            this.loadLocalPresets();
            try {
                const response = await axios.post('/get_thinking_methods', {
                    client_id: this.client_id
                });
                if (response.data.status === 'success') {
                    this.thinkingPresets = response.data.thinking_methods;
                     // Set the selectedPresetName based on the current config value
                     const currentPrompt = this.$store.state.config.thinking_prompt;
                     const matchingPreset = this.allThinkingPresets.find(p => p.prompt === currentPrompt);
                     this.selectedPresetName = matchingPreset ? matchingPreset.name : '';
                } else {
                     console.error('Failed to load thinking methods from backend:', response.data.error);
                }
            } catch (error) {
                console.error('Error loading thinking methods:', error);
                 this.show_toast('Failed to load thinking methods from server.', 4, false);
            }
        },

        loadLocalPresets() {
            const savedPresets = localStorage.getItem('localThinkingPresets');
            if (savedPresets) {
                try {
                    this.localThinkingPresets = JSON.parse(savedPresets);
                } catch (e) {
                    console.error("Failed to parse local thinking presets:", e);
                    localStorage.removeItem('localThinkingPresets');
                    this.localThinkingPresets = [];
                }
            } else {
                this.localThinkingPresets = [];
            }
        },

        saveLocalPresets() {
            try {
                localStorage.setItem('localThinkingPresets', JSON.stringify(this.localThinkingPresets));
            } catch (e) {
                console.error("Failed to save local thinking presets:", e);
                this.show_toast('Could not save the new preset locally.', 4, false);
            }
        },

        selectPreset(presetName) {
             if (!presetName) return; // Handle the "-- Select Preset --" case

             const preset = this.allThinkingPresets.find(p => p.name === presetName);
             if (preset) {
                this.$emit('update:setting', { key: 'thinking_prompt', value: preset.prompt });
                this.selectedPresetName = preset.name; // Update dropdown selection state
                this.$emit('settings-changed', true);
            }
        },

        saveNewPreset() {
            if (!this.newPreset.name || !this.newPreset.description || !this.newPreset.author || !this.newPreset.prompt) {
                 this.show_toast('Please fill in all fields for the new preset.', 4, false);
                 return;
             }

            let promptToSave = this.newPreset.prompt.trim();
            if (!promptToSave.startsWith('<thinking>')) {
                promptToSave = `<thinking>\n${promptToSave}`;
            }
            if (!promptToSave.endsWith('</thinking>')) {
                promptToSave = `${promptToSave}\n</thinking>`;
            }

            const newPresetEntry = {
                name: this.newPreset.name.trim(),
                description: this.newPreset.description.trim(),
                author: this.newPreset.author.trim(),
                prompt: promptToSave,
                isLocal: true
            };

            const existingPreset = this.allThinkingPresets.find(p => p.name.toLowerCase() === newPresetEntry.name.toLowerCase());
            if (existingPreset) {
                this.show_toast('A preset with this name already exists. Please choose a different name.', 4, false);
                return;
            }

            this.localThinkingPresets.push(newPresetEntry);
            this.saveLocalPresets();

            this.show_toast('New thinking preset added successfully.', 4, true);
             // Automatically select the newly added preset
             this.$nextTick(() => {
                 this.selectPreset(newPresetEntry.name);
             });

             // Reset form and hide it
            this.newPreset = { name: '', description: '', author: '', prompt: '' };
            this.showAddThinkingPresetForm = false;
            this.$emit('settings-changed', true);
        },

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
        this.loadThinkingPresets();
    },

    updated() {
        this.replaceFeatherIcons();
    }
};
</script>

<style scoped>
.setting-item {
    @apply flex flex-col md:flex-row md:items-center gap-2 md:gap-4 py-2;
}

.setting-label {
    @apply block text-sm font-medium text-gray-700 dark:text-gray-300 w-full md:w-1/3 lg:w-1/4 flex-shrink-0;
}

.input {
     @apply block w-full px-3 py-2 bg-gray-50 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 focus:border-blue-500 dark:focus:ring-offset-gray-900 sm:text-sm disabled:opacity-50 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500;
}
.panels-color {
     @apply bg-white dark:bg-gray-800;
}

.toggle-item {
    @apply flex items-center justify-between p-3 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors;
}

.toggle-label {
    @apply text-sm font-medium text-gray-700 dark:text-gray-300 cursor-pointer flex-1 mr-4;
}
.toggle-description {
     @apply block text-xs text-gray-500 dark:text-gray-400 mt-1 font-normal;
}

/* Simplified Button Styles based on btn classes */
.btn {
  @apply inline-flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-offset-2 dark:focus:ring-offset-gray-900 disabled:opacity-50 transition-colors duration-150 whitespace-nowrap;
}
.btn-sm {
  @apply px-3 py-1.5 text-xs;
}
.btn-primary {
  @apply text-white bg-blue-600 hover:bg-blue-700 focus:ring-blue-500 ;
}
.btn-secondary {
  @apply text-gray-700 dark:text-gray-200 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 focus:ring-blue-500 border-gray-300 dark:border-gray-500;
}
.btn-positive {
  @apply text-white bg-green-600 hover:bg-green-700 focus:ring-green-500 ;
}

/* Form select styling */
.form-select {
    @apply block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md dark:bg-gray-700 dark:border-gray-600 dark:text-gray-300;
}

/* Ensure consistent padding and borders for nested sections */
.panels-color > .grid {
    @apply border-none shadow-none p-0; /* Remove duplicate styling if Card component is not used */
}
</style>