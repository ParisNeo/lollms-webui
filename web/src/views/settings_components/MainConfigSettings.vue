<template>
    <div class="user-settings-panel space-y-6">
        <h2 class="text-xl font-semibold text-blue-800 dark:text-blue-100 border-b border-blue-300 dark:border-blue-600 pb-2">
            Main Configuration
        </h2>

        <!-- Application Branding Section -->
        <div class="space-y-4 p-4 border border-blue-300 dark:border-blue-600 rounded-lg panels-color">
            <h3 class="text-lg font-medium text-blue-700 dark:text-blue-300 mb-3">Application Branding</h3>

            <div class="setting-item">
                <label for="app_custom_name" class="setting-label">Application Name</label>
                <input
                    type="text"
                    id="app_custom_name"
                    :value="config.app_custom_name"
                    @input="updateValue('app_custom_name', $event.target.value)"
                    class="input flex-grow"
                    placeholder="Default: LoLLMs"
                >
            </div>

            <div class="setting-item">
                <label for="app_custom_slogan" class="setting-label">Application Slogan</label>
                <input
                    type="text"
                    id="app_custom_slogan"
                    :value="config.app_custom_slogan"
                    @input="updateValue('app_custom_slogan', $event.target.value)"
                    class="input flex-grow"
                    placeholder="Default: Lord of Large Language Models"
                >
            </div>

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
                            v-if="config.app_custom_logo"
                            @click="removeLogo"
                            class="btn btn-secondary btn-sm text-red-500 dark:text-red-400 hover:bg-red-200 dark:hover:bg-red-700"
                            :disabled="isUploadingLogo">
                            Remove Logo
                        </button>
                    </div>
                     <span v-if="isUploadingLogo" class="text-xs text-blue-500 dark:text-blue-400 italic ml-2">Uploading...</span>
                </div>
            </div>

             <div class="setting-item items-start">
                 <label for="app_custom_welcome_message" class="setting-label pt-2">Custom Welcome Message</label>
                 <textarea
                    id="app_custom_welcome_message"
                    :value="config.app_custom_welcome_message"
                    @input="updateValue('app_custom_welcome_message', $event.target.value)"
                    class="input flex-grow min-h-[80px] resize-y"
                    placeholder="Enter a custom welcome message shown on the main page (leave blank for default)."
                 ></textarea>
             </div>
        </div>

        <!-- UI Behavior Section -->
         <div class="space-y-4 p-4 border border-blue-300 dark:border-blue-600 rounded-lg panels-color">
            <h3 class="text-lg font-medium text-blue-700 dark:text-blue-300 mb-3">UI & Behavior</h3>

            <div class="toggle-item">
                <label for="auto_title" class="toggle-label">
                    Automatic Discussion Naming
                     <span class="toggle-description">Let AI name your discussions automatically based on the first message.</span>
                </label>
                <ToggleSwitch id="auto_title" :checked="config.auto_title" @update:checked="updateValue('auto_title', $event)" />
            </div>

            <div class="toggle-item">
                <label for="auto_show_browser" class="toggle-label">
                    Auto-launch Browser
                     <span class="toggle-description">Open the default web browser automatically when LoLLMs starts.</span>
                </label>
                <ToggleSwitch id="auto_show_browser" :checked="config.auto_show_browser" @update:checked="updateValue('auto_show_browser', $event)" />
            </div>

             <div class="toggle-item">
                <label for="app_show_changelogs" class="toggle-label">
                    Show Startup Changelog
                     <span class="toggle-description">Display the changelog modal window when the application starts after an update.</span>
                </label>
                <ToggleSwitch id="app_show_changelogs" :checked="config.app_show_changelogs" @update:checked="updateValue('app_show_changelogs', $event)" />
            </div>

             <div class="toggle-item">
                <label for="app_show_fun_facts" class="toggle-label">
                    Show Fun Facts
                     <span class="toggle-description">Display fun facts related to AI and LLMs while loading or waiting.</span>
                </label>
                <ToggleSwitch id="app_show_fun_facts" :checked="config.app_show_fun_facts" @update:checked="updateValue('app_show_fun_facts', $event)" />
            </div>

             <div class="toggle-item">
                <label for="copy_to_clipboard_add_all_details" class="toggle-label">
                    Enhanced Message Copy
                     <span class="toggle-description">Include metadata (sender, model, etc.) when copying messages from discussions.</span>
                </label>
                 <ToggleSwitch id="copy_to_clipboard_add_all_details" :checked="config.copy_to_clipboard_add_all_details" @update:checked="updateValue('copy_to_clipboard_add_all_details', $event)" />
            </div>
        </div>

        <!-- Server & Access Section -->
        <div class="space-y-4 p-4 border border-blue-300 dark:border-blue-600 rounded-lg panels-color">
             <h3 class="text-lg font-medium text-blue-700 dark:text-blue-300 mb-3">Server & Access</h3>

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
                    <ToggleSwitch id="force_accept_remote_access" :checked="config.force_accept_remote_access" @update:checked="updateValue('force_accept_remote_access', $event)" />
                </div>
            </div>

            <div class="toggle-item">
                <label for="headless_server_mode" class="toggle-label">
                    Headless Server Mode
                     <span class="toggle-description">Run LoLLMs without the Web UI. Useful for server deployments or API-only usage. This setting requires a restart.</span>
                </label>
                 <ToggleSwitch id="headless_server_mode" :checked="config.headless_server_mode" @update:checked="updateValue('headless_server_mode', $event)" />
            </div>
        </div>

        <!-- Model Template Section -->
        <div class="space-y-4 p-4 border border-blue-300 dark:border-blue-600 rounded-lg panels-color">
            <h3 class="text-lg font-medium text-blue-700 dark:text-blue-300 mb-3">Model Template Configuration</h3>
             <div class="grid gap-6 bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md border border-gray-200 dark:border-gray-600">
                 <div class="setting-item">
                     <label for="template_type_select" class="setting-label">Template Type</label>
                     <select id="template_type_select" @change="handleTemplateSelection"
                             class="input form-select flex-grow">
                         <option value="" disabled :selected="!isTemplatePresetSelected">-- Custom --</option>
                         <option value="lollms" :selected="isTemplatePresetSelected === 'lollms'">Lollms communication template</option>
                         <option value="lollms_simplified" :selected="isTemplatePresetSelected === 'lollms_simplified'">Lollms simplified communication template</option>
                         <option value="bare" :selected="isTemplatePresetSelected === 'bare'">Bare, useful when in chat mode</option>
                         <option value="llama3" :selected="isTemplatePresetSelected === 'llama3'">LLama3 communication template</option>
                         <option value="lucie" :selected="isTemplatePresetSelected === 'lucie'">Lucie communication template</option>
                         <option value="mistral" :selected="isTemplatePresetSelected === 'mistral'">Mistral communication template</option>
                         <option value="deepseek" :selected="isTemplatePresetSelected === 'deepseek'">DeepSeek communication template</option>
                     </select>
                 </div>

                 <div class="grid md:grid-cols-2 gap-4">
                     <div class="setting-item !flex-col !items-start md:!flex-row md:!items-center">
                         <label for="start_header_id_template" class="setting-label !w-auto md:!w-1/3">Start Header Template</label>
                         <input type="text" id="start_header_id_template"
                            :value="config.start_header_id_template"
                            @input="updateValue('start_header_id_template', $event.target.value)"
                            class="input flex-grow">
                     </div>
                     <div class="setting-item !flex-col !items-start md:!flex-row md:!items-center">
                         <label for="end_header_id_template" class="setting-label !w-auto md:!w-1/3">End Header Template</label>
                         <input type="text" id="end_header_id_template"
                            :value="config.end_header_id_template"
                            @input="updateValue('end_header_id_template', $event.target.value)"
                            class="input flex-grow">
                     </div>
                 </div>

                 <div class="grid md:grid-cols-2 gap-4">
                     <div class="setting-item !flex-col !items-start md:!flex-row md:!items-center">
                         <label for="start_user_header_id_template" class="setting-label !w-auto md:!w-1/3">Start User Header Template</label>
                         <input type="text" id="start_user_header_id_template"
                            :value="config.start_user_header_id_template"
                            @input="updateValue('start_user_header_id_template', $event.target.value)"
                            class="input flex-grow">
                     </div>
                     <div class="setting-item !flex-col !items-start md:!flex-row md:!items-center">
                         <label for="end_user_header_id_template" class="setting-label !w-auto md:!w-1/3">End User Header Template</label>
                         <input type="text" id="end_user_header_id_template"
                            :value="config.end_user_header_id_template"
                            @input="updateValue('end_user_header_id_template', $event.target.value)"
                            class="input flex-grow">
                     </div>
                 </div>

                 <div class="grid md:grid-cols-2 gap-4">
                     <div class="setting-item !flex-col !items-start md:!flex-row md:!items-center">
                         <label for="start_ai_header_id_template" class="setting-label !w-auto md:!w-1/3">Start AI Header Template</label>
                         <input type="text" id="start_ai_header_id_template"
                            :value="config.start_ai_header_id_template"
                            @input="updateValue('start_ai_header_id_template', $event.target.value)"
                            class="input flex-grow">
                     </div>
                     <div class="setting-item !flex-col !items-start md:!flex-row md:!items-center">
                         <label for="end_ai_header_id_template" class="setting-label !w-auto md:!w-1/3">End AI Header Template</label>
                         <input type="text" id="end_ai_header_id_template"
                            :value="config.end_ai_header_id_template"
                            @input="updateValue('end_ai_header_id_template', $event.target.value)"
                            class="input flex-grow">
                     </div>
                 </div>

                 <div class="grid md:grid-cols-2 gap-4">
                     <div class="setting-item !flex-col !items-start md:!flex-row md:!items-center">
                         <label for="end_user_message_id_template" class="setting-label !w-auto md:!w-1/3">End User Message Template</label>
                         <input type="text" id="end_user_message_id_template"
                            :value="config.end_user_message_id_template"
                            @input="updateValue('end_user_message_id_template', $event.target.value)"
                            class="input flex-grow">
                     </div>
                     <div class="setting-item !flex-col !items-start md:!flex-row md:!items-center">
                         <label for="end_ai_message_id_template" class="setting-label !w-auto md:!w-1/3">End AI Message Template</label>
                         <input type="text" id="end_ai_message_id_template"
                            :value="config.end_ai_message_id_template"
                            @input="updateValue('end_ai_message_id_template', $event.target.value)"
                            class="input flex-grow">
                     </div>
                 </div>

                 <div class="setting-item items-start">
                     <label for="separator_template" class="setting-label pt-2">Separator Template</label>
                     <textarea id="separator_template"
                            :value="config.separator_template"
                            @input="updateValue('separator_template', $event.target.value)"
                            class="input flex-grow min-h-[60px] resize-y">
                     </textarea>
                 </div>

                 <div class="setting-item">
                     <label for="system_message_template" class="setting-label">System Message Template</label>
                     <input type="text" id="system_message_template"
                        :value="config.system_message_template"
                        @input="updateValue('system_message_template', $event.target.value)"
                        class="input flex-grow">
                 </div>

                 <div class="setting-item items-start">
                     <label class="setting-label pt-2">Full Template Preview</label>
                     <div class="p-4 bg-gray-100 dark:bg-gray-900 rounded-md flex-grow border border-gray-200 dark:border-gray-700 overflow-x-auto text-sm">
                         <div v-html="full_template" class="whitespace-pre-wrap break-words"></div>
                     </div>
                 </div>

                 <div class="toggle-item">
                    <label for="use_continue_message" class="toggle-label">
                        Use Continue Message
                        <span class="toggle-description">If supported by the model, use a specific token or phrase to indicate the AI should continue its response.</span>
                    </label>
                    <ToggleSwitch id="use_continue_message" :checked="config.use_continue_message" @update:checked="updateValue('use_continue_message', $event)" />
                </div>
             </div>
        </div>

<!-- Security Measures Section (New) -->
<div class="space-y-4 p-4 border border-blue-300 dark:border-blue-600 rounded-lg panels-color">
            <h3 class="text-lg font-medium text-blue-700 dark:text-blue-300 mb-3">Security Measures</h3>
            <div class="toggle-item">
                <label for="turn_on_setting_update_validation" class="toggle-label">
                    Validate Setting Updates
                    <span class="toggle-description">Enable validation for changes to configuration settings to prevent unauthorized or invalid updates.</span>
                </label>
                <ToggleSwitch id="turn_on_setting_update_validation" :checked="config.turn_on_setting_update_validation" @update:checked="updateValue('turn_on_setting_update_validation', $event)" />
            </div>
            <div class="toggle-item">
                <label for="turn_on_code_execution" class="toggle-label">
                    Allow Code Execution
                    <span class="toggle-description">Permit the execution of code snippets within the application (use with caution).</span>
                </label>
                <ToggleSwitch id="turn_on_code_execution" :checked="config.turn_on_code_execution" @update:checked="updateValue('turn_on_code_execution', $event)" />
            </div>
            <div class="toggle-item">
                <label for="turn_on_code_validation" class="toggle-label">
                    Validate Executed Code
                    <span class="toggle-description">Enable validation of code before execution to ensure safety and correctness.</span>
                </label>
                <ToggleSwitch id="turn_on_code_validation" :checked="config.turn_on_code_validation" @update:checked="updateValue('turn_on_code_validation', $event)" />
            </div>
            <div class="toggle-item">
                <label for="turn_on_open_file_validation" class="toggle-label">
                    Validate File Opening
                    <span class="toggle-description">Check files before opening to prevent access to unauthorized or harmful content.</span>
                </label>
                <ToggleSwitch id="turn_on_open_file_validation" :checked="config.turn_on_open_file_validation" @update:checked="updateValue('turn_on_open_file_validation', $event)" />
            </div>
            <div class="toggle-item">
                <label for="turn_on_send_file_validation" class="toggle-label">
                    Validate File Sending
                    <span class="toggle-description">Validate files before sending to ensure they meet security and format requirements.</span>
                </label>
                <ToggleSwitch id="turn_on_send_file_validation" :checked="config.turn_on_send_file_validation" @update:checked="updateValue('turn_on_send_file_validation', $event)" />
            </div>
            <div class="toggle-item">
                <label for="turn_on_language_validation" class="toggle-label">
                    Validate Language Inputs
                    <span class="toggle-description">Ensure language inputs are valid and safe before processing.</span>
                </label>
                <ToggleSwitch id="turn_on_language_validation" :checked="config.turn_on_language_validation" @update:checked="updateValue('turn_on_language_validation', $event)" />
            </div>
        </div>
        <!-- Thinking Methods Section -->
        <div class="space-y-4 p-4 border border-blue-300 dark:border-blue-600 rounded-lg panels-color">
            <h3 class="text-lg font-medium text-blue-700 dark:text-blue-300 mb-3">Thinking Methods</h3>
             <div class="grid gap-6 bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md border border-gray-200 dark:border-gray-600">
                 <div class="space-y-4">
                     <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 mb-2">
                         <label for="thinking_prompt_textarea" class="setting-label !w-auto sm:!w-1/3">
                             Thinking Prompt
                             <span class="block text-xs text-gray-500 dark:text-gray-400 mt-1 font-normal">Prompt used by the AI to structure its thought process. Use `thinking` tags.</span>
                         </label>
                         <div class="flex items-center gap-2 flex-wrap">
                             <select id="thinking_preset_select" v-model="selectedPresetName" @change="selectPreset($event.target.value)" class="input form-select flex-grow min-w-[150px]">
                                 <option value="">-- Custom --</option>
                                 <option v-for="preset in allThinkingPresets" :key="preset.name" :value="preset.name">
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
                         :value="config.thinking_prompt"
                         @input="updateValue('thinking_prompt', $event.target.value)"
                         class="input w-full p-4 bg-gray-100 dark:bg-gray-900 rounded-md text-sm min-h-[150px] resize-y font-mono border border-gray-200 dark:border-gray-700"
                         placeholder="<thinking>...</thinking>"
                     ></textarea>
                 </div>

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
        config: { type: Object, required: true }, // Receive editable config copy
        loading: { type: Boolean, default: false },
        api_post_req: { type: Function, required: true },
        show_toast: { type: Function, required: true },
        client_id: { type: String, required: true }
    },
    emits: ['setting-updated'], // Declare the event used to notify parent

    data() {
        return {
            isUploadingLogo: false,
            showAddThinkingPresetForm: false,
            thinkingPresets: [],
            localThinkingPresets: [],
            newPreset: { name: '', description: '', author: '', prompt: '' },
            selectedPresetName: '',
        };
    },

    computed: {
        logoSrc() {
            // Reads from the config prop
            if (this.config.app_custom_logo) {
                const baseURL = (axios.defaults.baseURL || '').replace(/\/$/, '');
                const logoPath = (this.config.app_custom_logo || '').replace(/^\//, '');
                return `${baseURL}/user_infos/${logoPath}`;
            }
            return defaultLogoPlaceholder;
        },
        full_template() {
             // Reads from the config prop
             if (!this.config) return '';
             const cfg = this.config;
             const parts = [
                 cfg.start_header_id_template, cfg.system_message_template, cfg.end_header_id_template, " system message", cfg.separator_template,
                 cfg.start_user_header_id_template, "user name", cfg.end_user_header_id_template, " User prompt", cfg.separator_template,
                 cfg.end_user_message_id_template, cfg.separator_template, cfg.start_ai_header_id_template, "ai personality", cfg.end_ai_header_id_template,
                 "ai response", cfg.end_ai_message_id_template
             ];
             return parts.map(part => part || '').join('').replace(/\n/g, "<br>");
        },
        allThinkingPresets() {
             const combined = [...this.localThinkingPresets];
             const localNames = new Set(this.localThinkingPresets.map(p => p.name));
             this.thinkingPresets.forEach(p => { if (!localNames.has(p.name)) combined.push(p); });
             return combined.sort((a, b) => a.name.localeCompare(b.name));
        },
        isTemplatePresetSelected() {
             // Determine if the current template settings match a known preset
             const cfg = this.config;
             if (!cfg) return ''; // Return empty if config is not loaded

             const templates = {
                 lollms: { sH: "!@>", sM: "system", eH: ": ", sep: "\n", sUH: "!@>", eUH: ": ", eUM: "", sAH: "!@>", eAH: ": ", eAM: "" },
                 lollms_simplified: { sH: "@>", sM: "system", eH: ": ", sep: "\n", sUH: "@>", eUH: ": ", eUM: "", sAH: "@>", eAH: ": ", eAM: "" },
                 bare: { sH: "", sM: "system", eH: ": ", sep: "\n", sUH: "", eUH: ": ", eUM: "", sAH: "", eAH: ": ", eAM: "" },
                 llama3: { sH: "<|start_header_id|>", sM: "system", eH: "<|end_header_id|>", sep: "<|eot_id|>", sUH: "<|start_header_id|>", eUH: "<|end_header_id|>", eUM: "", sAH: "<|start_header_id|>", eAH: "<|end_header_id|>", eAM: "" },
                 lucie: { sH: "<s><|start_header_id|>", sM: "system", eH: "<|end_header_id|>\n\n", sep: "<|eot_id|>", sUH: "<|start_header_id|>", eUH: "<|end_header_id|>\n\n", eUM: "", sAH: "<|start_header_id|>", eAH: "<|end_header_id|>\n\n", eAM: "" },
                 mistral: { sH: "[INST]", sM: " Using this information", eH: ": ", sep: "\n", sUH: "[INST]", eUH: ": ", eUM: "[/INST]", sAH: "", eAH: "", eAM: "</s>" },
                 deepseek: { sH: "", sM: "", eH: "\n", sep: "\n", sUH: "User: ", eUH: "\n", eUM: "", sAH: "Assistant: ", eAH: "\n", eAM: "<|end_of_sentence|>" }
             };

             for (const [name, t] of Object.entries(templates)) {
                 if (cfg.start_header_id_template === t.sH && cfg.system_message_template === t.sM && cfg.end_header_id_template === t.eH &&
                     cfg.separator_template === t.sep && cfg.start_user_header_id_template === t.sUH && cfg.end_user_header_id_template === t.eUH &&
                     cfg.end_user_message_id_template === t.eUM && cfg.start_ai_header_id_template === t.sAH && cfg.end_ai_header_id_template === t.eAH &&
                     cfg.end_ai_message_id_template === t.eAM) {
                     return name;
                 }
             }
             return ''; // Return empty string if no preset matches (custom)
         }
    },
    watch: {
         // Watch the config prop to update local state if needed (e.g., selected preset name)
         'config.thinking_prompt'(newVal) {
             const matchingPreset = this.allThinkingPresets.find(p => p.prompt === newVal);
             this.selectedPresetName = matchingPreset ? matchingPreset.name : '';
         }
    },
    methods: {
        updateValue(key, value) {
            // Emit event for parent to handle update in its local copy
            this.$emit('setting-updated', { key, value });
             // If thinking prompt is manually changed, deselect preset in dropdown
             if (key === 'thinking_prompt') {
                 this.selectedPresetName = '';
             }
        },
        async uploadLogo(event) {
            const file = event.target.files[0];
            if (!file) return;
            this.isUploadingLogo = true;
            const formData = new FormData();
            formData.append('logo', file);
            formData.append('client_id', this.client_id);
            try {
                const response = await axios.post('/upload_logo', formData, { headers: { 'Content-Type': 'multipart/form-data' } });
                if (response.data && response.data.status) {
                     this.show_toast("Logo uploaded!", 4, true);
                     // Emit update for the logo setting
                     this.$emit('setting-updated', { key: 'app_custom_logo', value: response.data.filename });
                } else {
                    this.show_toast(`Logo upload failed: ${response.data.error || 'Error'}`, 4, false);
                }
            } catch (error) {
                this.show_toast(`Error uploading logo: ${error.response?.data?.error || error.message || 'Error'}`, 4, false);
            } finally {
                this.isUploadingLogo = false;
                if (event.target) event.target.value = null;
            }
        },
        async removeLogo() {
            this.isUploadingLogo = true;
             try {
                 // Use prop function for API call
                const response = await this.api_post_req('/remove_logo');
                if (response.status) {
                    this.show_toast("Logo removed!", 4, true);
                     // Emit update for the logo setting
                     this.$emit('setting-updated', { key: 'app_custom_logo', value: null });
                } else {
                    this.show_toast(`Failed to remove logo: ${response.error || 'Error'}`, 4, false);
                }
            } catch (error) {
                this.show_toast(`Error removing logo: ${error.response?.data?.error || error.message || 'Error'}`, 4, false);
            } finally {
                this.isUploadingLogo = false;
            }
        },
        handleTemplateSelection(event) {
            const selectedOption = event.target.value;
            let updates = {};
             if (selectedOption === 'lollms') {
                 updates = { sH: "!@>", sM: "system", eH: ": ", sep: "\n", sUH: "!@>", eUH: ": ", eUM: "", sAH: "!@>", eAH: ": ", eAM: "" };
             } else if (selectedOption === 'lollms_simplified') {
                 updates = { sH: "@>", sM: "system", eH: ": ", sep: "\n", sUH: "@>", eUH: ": ", eUM: "", sAH: "@>", eAH: ": ", eAM: "" };
             } else if (selectedOption === 'bare') {
                 updates = { sH: "", sM: "system", eH: ": ", sep: "\n", sUH: "", eUH: ": ", eUM: "", sAH: "", eAH: ": ", eAM: "" };
             } else if (selectedOption === 'llama3') {
                 updates = { sH: "<|start_header_id|>", sM: "system", eH: "<|end_header_id|>", sep: "<|eot_id|>", sUH: "<|start_header_id|>", eUH: "<|end_header_id|>", eUM: "", sAH: "<|start_header_id|>", eAH: "<|end_header_id|>", eAM: "" };
             } else if (selectedOption === 'lucie') {
                 updates = { sH: "<s><|start_header_id|>", sM: "system", eH: "<|end_header_id|>\n\n", sep: "<|eot_id|>", sUH: "<|start_header_id|>", eUH: "<|end_header_id|>\n\n", eUM: "", sAH: "<|start_header_id|>", eAH: "<|end_header_id|>\n\n", eAM: "" };
             } else if (selectedOption === 'mistral') {
                 updates = { sH: "[INST]", sM: " Using this information", eH: ": ", sep: "\n", sUH: "[INST]", eUH: ": ", eUM: "[/INST]", sAH: "", eAH: "", eAM: "</s>" };
             } else if (selectedOption === 'deepseek') {
                 updates = { sH: "", sM: "", eH: "\n", sep: "\n", sUH: "User: ", eUH: "\n", eUM: "", sAH: "Assistant: ", eAH: "\n", eAM: "<|end_of_sentence|>" };
             }

             // Map shorthand keys to full config keys
            const keyMap = { sH: 'start_header_id_template', sM: 'system_message_template', eH: 'end_header_id_template', sep: 'separator_template', sUH: 'start_user_header_id_template', eUH: 'end_user_header_id_template', eUM: 'end_user_message_id_template', sAH: 'start_ai_header_id_template', eAH: 'end_ai_header_id_template', eAM: 'end_ai_message_id_template' };

             // Emit updates for all affected keys
            Object.entries(updates).forEach(([shortKey, value]) => {
                 const fullKey = keyMap[shortKey];
                 if (fullKey) {
                    this.$emit('setting-updated', { key: fullKey, value });
                 }
            });
        },
        async loadThinkingPresets() {
            this.loadLocalPresets();
            try {
                // Use prop function
                const response = await this.api_post_req('get_thinking_methods');
                if (response.status === 'success') {
                    this.thinkingPresets = response.thinking_methods || [];
                     // Set initial selectedPresetName based on current prop value
                     const currentPrompt = this.config.thinking_prompt;
                     const matchingPreset = this.allThinkingPresets.find(p => p.prompt === currentPrompt);
                     this.selectedPresetName = matchingPreset ? matchingPreset.name : '';
                } else {
                     console.error('Failed to load thinking methods:', response.error);
                }
            } catch (error) {
                this.show_toast('Failed to load thinking methods from server.', 4, false);
            }
        },
        loadLocalPresets() {
            const savedPresets = localStorage.getItem('localThinkingPresets');
            if (savedPresets) {
                try { this.localThinkingPresets = JSON.parse(savedPresets); } catch (e) { localStorage.removeItem('localThinkingPresets'); this.localThinkingPresets = []; }
            } else { this.localThinkingPresets = []; }
        },
        saveLocalPresets() {
            try { localStorage.setItem('localThinkingPresets', JSON.stringify(this.localThinkingPresets)); } catch (e) { this.show_toast('Could not save preset locally.', 4, false); }
        },
        selectPreset(presetName) {
             if (!presetName) { // Handle "-- Custom --" selection
                 // Do not change the prompt if custom is selected, user might be editing
                 // Only update the dropdown display state
                 this.selectedPresetName = '';
                 return;
             }
             const preset = this.allThinkingPresets.find(p => p.name === presetName);
             if (preset) {
                 // Emit the update for the thinking prompt
                this.$emit('setting-updated', { key: 'thinking_prompt', value: preset.prompt });
                this.selectedPresetName = preset.name; // Sync dropdown visual state
            }
        },
        saveNewPreset() {
            if (!this.newPreset.name || !this.newPreset.description || !this.newPreset.author || !this.newPreset.prompt) {
                 this.show_toast('Please fill in all fields.', 4, false); return;
             }
            let promptToSave = this.newPreset.prompt.trim();
            if (!promptToSave.startsWith('<thinking>')) promptToSave = `<thinking>\n${promptToSave}`;
            if (!promptToSave.endsWith('</thinking>')) promptToSave = `${promptToSave}\n</thinking>`;

            const newPresetEntry = { name: this.newPreset.name.trim(), description: this.newPreset.description.trim(), author: this.newPreset.author.trim(), prompt: promptToSave, isLocal: true };
            if (this.allThinkingPresets.some(p => p.name.toLowerCase() === newPresetEntry.name.toLowerCase())) {
                this.show_toast('Preset name already exists.', 4, false); return;
            }
            this.localThinkingPresets.push(newPresetEntry);
            this.saveLocalPresets();
            this.show_toast('New preset added.', 4, true);
             // Select the new preset and emit the update
             this.$nextTick(() => { this.selectPreset(newPresetEntry.name); });
            this.newPreset = { name: '', description: '', author: '', prompt: '' };
            this.showAddThinkingPresetForm = false;
        },
        replaceFeatherIcons() {
             nextTick(() => { try { feather.replace(); } catch (e) {} });
        }
    },
    mounted() {
        this.replaceFeatherIcons();
        this.loadThinkingPresets();
         // Set initial dropdown state based on the initial config prop value
        const currentPrompt = this.config.thinking_prompt;
        const matchingPreset = this.allThinkingPresets.find(p => p.prompt === currentPrompt);
        this.selectedPresetName = matchingPreset ? matchingPreset.name : '';
    },
    updated() {
        this.replaceFeatherIcons();
    }
};
</script>

<style scoped>
.setting-item { @apply flex flex-col md:flex-row md:items-center gap-2 md:gap-4 py-2; }
.setting-label { @apply block text-sm font-medium text-gray-700 dark:text-gray-300 w-full md:w-1/3 lg:w-1/4 flex-shrink-0; }
.input { @apply block w-full px-3 py-2 bg-gray-50 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 focus:border-blue-500 dark:focus:ring-offset-gray-900 sm:text-sm disabled:opacity-50 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500; }
.panels-color { @apply bg-white dark:bg-gray-800; }
.toggle-item { @apply flex items-center justify-between p-3 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors; }
.toggle-label { @apply text-sm font-medium text-gray-700 dark:text-gray-300 cursor-pointer flex-1 mr-4; }
.toggle-description { @apply block text-xs text-gray-500 dark:text-gray-400 mt-1 font-normal; }
.btn { @apply inline-flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-offset-2 dark:focus:ring-offset-gray-900 disabled:opacity-50 transition-colors duration-150 whitespace-nowrap; }
.btn-sm { @apply px-3 py-1.5 text-xs; }
.btn-primary { @apply text-white bg-blue-600 hover:bg-blue-700 focus:ring-blue-500 ; }
.btn-secondary { @apply text-gray-700 dark:text-gray-200 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 focus:ring-blue-500 border-gray-300 dark:border-gray-500; }
.form-select { @apply block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md dark:bg-gray-700 dark:border-gray-600 dark:text-gray-300; }
.panels-color > .grid { @apply border-none shadow-none p-0; }
</style>