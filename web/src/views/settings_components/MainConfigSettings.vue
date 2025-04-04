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

        <!-- Interaction Parameters Section -->
        <div class="space-y-4 p-4 border border-blue-300 dark:border-blue-600 rounded-lg panels-color">
            <h3 class="text-lg font-medium text-blue-700 dark:text-blue-300 mb-3">Interaction Parameters</h3>
            <div class="setting-item">
                <label for="user_name" class="setting-label">User Name</label>
                <input
                    type="text"
                    id="user_name"
                    :value="config.user_name"
                    @input="updateValue('user_name', $event.target.value)"
                    class="input flex-grow"
                    placeholder="Default: user">
            </div>
            <div class="setting-item">
                <label for="user_description" class="setting-label">User Description</label>
                <textarea
                    id="user_description"
                    :value="config.user_description"
                    @input="updateValue('user_description', $event.target.value)"
                    class="input flex-grow"
                    placeholder="Optional: Describe yourself to the AI"></textarea>

            </div>
            <div class="setting-item items-start">
                <label class="setting-label pt-2">User Avatar</label>
                <div class="flex-1 flex items-center gap-4">
                     <div class="w-12 h-12 rounded-full overflow-hidden bg-blue-200 dark:bg-blue-700 ring-2 ring-offset-2 dark:ring-offset-blue-900 ring-blue-300 dark:ring-blue-600">
                         <img :src="userAvatarSrc" class="w-full h-full object-cover" alt="User Avatar">
                     </div>
                    <div class="flex gap-2">
                        <label class="btn btn-secondary btn-sm cursor-pointer">
                            Upload Avatar
                            <input type="file" @change="uploadUserAvatar" accept="image/*" class="hidden" :disabled="isUploadingAvatar">
                        </label>
                         <button
                            v-if="config.user_avatar"
                            @click="removeUserAvatar"
                            class="btn btn-secondary btn-sm text-red-500 dark:text-red-400 hover:bg-red-200 dark:hover:bg-red-700"
                            :disabled="isUploadingAvatar">
                            Remove Avatar
                        </button>
                    </div>
                     <span v-if="isUploadingAvatar" class="text-xs text-blue-500 dark:text-blue-400 italic ml-2">Uploading...</span>
                </div>
            </div>
            <div class="toggle-item">
                <label for="use_user_name_in_discussions" class="toggle-label">
                    Use User Name in Discussions
                     <span class="toggle-description">Prefix user messages with the 'User Name' defined above.</span>
                </label>
                <ToggleSwitch id="use_user_name_in_discussions" :checked="config.use_user_name_in_discussions" @update:checked="updateValue('use_user_name_in_discussions', $event)" />
            </div>
            <div class="toggle-item">
                <label for="use_assistant_name_in_discussion" class="toggle-label">
                    Use Assistant Name in Discussions
                     <span class="toggle-description">Prefix AI messages with the current personality's name.</span>
                </label>
                <ToggleSwitch id="use_assistant_name_in_discussion" :checked="config.use_assistant_name_in_discussion" @update:checked="updateValue('use_assistant_name_in_discussion', $event)" />
            </div>
            <div class="toggle-item">
                <label for="use_model_name_in_discussions" class="toggle-label">
                    Use Model Name in Discussions
                     <span class="toggle-description">Include the model name in AI message headers.</span>
                </label>
                <ToggleSwitch id="use_model_name_in_discussions" :checked="config.use_model_name_in_discussions" @update:checked="updateValue('use_model_name_in_discussions', $event)" />
            </div>
            <div class="toggle-item">
                <label for="use_user_informations_in_discussion" class="toggle-label">
                    Use User Information in Discussion Context
                     <span class="toggle-description">Include 'User Name' and 'User Description' in the context sent to the AI.</span>
                </label>
                <ToggleSwitch id="use_user_informations_in_discussion" :checked="config.use_user_informations_in_discussion" @update:checked="updateValue('use_user_informations_in_discussion', $event)" />
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
                             <strong class="block mt-1">Only enable if you understand the risks and have secured your network.</strong> Consider using 'Allowed Origins' below for added security.
                         </p>
                    </label>
                    <ToggleSwitch id="force_accept_remote_access" :checked="config.force_accept_remote_access" @update:checked="updateValue('force_accept_remote_access', $event)" />
                </div>
            </div>
            <div class="setting-item">
                <label for="host" class="setting-label">
                    Host Address
                    <span class="block text-xs text-gray-500 dark:text-gray-400 mt-1 font-normal">Hostname or IP to bind the server to. Use '0.0.0.0' for remote access. Requires restart.</span>
                </label>
                <input
                    type="text"
                    id="host"
                    :value="config.host"
                    @input="updateValue('host', $event.target.value)"
                    class="input flex-grow"
                    placeholder="localhost or 0.0.0.0">
            </div>
             <div class="setting-item">
                <label for="port" class="setting-label">
                    Port
                    <span class="block text-xs text-gray-500 dark:text-gray-400 mt-1 font-normal">Port number for the server. Requires restart.</span>
                </label>
                <input
                    type="number"
                    id="port"
                    :value="config.port"
                    @input="updateValue('port', parseInt($event.target.value) || 9600)"
                    min="1" max="65535"
                    class="input flex-grow"
                    placeholder="9600">
            </div>
            <div class="setting-item items-start">
                <label for="allowed_origins" class="setting-label pt-2">
                    Allowed Origins (CORS)
                    <span class="block text-xs text-gray-500 dark:text-gray-400 mt-1 font-normal">Comma-separated list of allowed origins for cross-origin requests (e.g., `http://localhost:8080,https://my-app.com`). Leave empty or `*` to allow all (less secure if remote access is enabled).</span>
                </label>
                <input
                    type="text"
                    id="allowed_origins"
                    :value="config.allowed_origins ? config.allowed_origins.join(',') : ''"
                    @input="updateValue('allowed_origins', $event.target.value ? $event.target.value.split(',').map(h => h.trim()).filter(h => h) : [])"
                    class="input flex-grow"
                    placeholder="http://localhost:8080,https://my-app.com">
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
                         <input type="text" id="start_header_id_template" :value="config.start_header_id_template" @input="updateValue('start_header_id_template', $event.target.value)" class="input flex-grow">
                     </div>
                     <div class="setting-item !flex-col !items-start md:!flex-row md:!items-center">
                         <label for="end_header_id_template" class="setting-label !w-auto md:!w-1/3">End Header Template</label>
                         <input type="text" id="end_header_id_template" :value="config.end_header_id_template" @input="updateValue('end_header_id_template', $event.target.value)" class="input flex-grow">
                     </div>
                 </div>
                 <div class="grid md:grid-cols-2 gap-4">
                     <div class="setting-item !flex-col !items-start md:!flex-row md:!items-center">
                         <label for="start_user_header_id_template" class="setting-label !w-auto md:!w-1/3">Start User Header Template</label>
                         <input type="text" id="start_user_header_id_template" :value="config.start_user_header_id_template" @input="updateValue('start_user_header_id_template', $event.target.value)" class="input flex-grow">
                     </div>
                     <div class="setting-item !flex-col !items-start md:!flex-row md:!items-center">
                         <label for="end_user_header_id_template" class="setting-label !w-auto md:!w-1/3">End User Header Template</label>
                         <input type="text" id="end_user_header_id_template" :value="config.end_user_header_id_template" @input="updateValue('end_user_header_id_template', $event.target.value)" class="input flex-grow">
                     </div>
                 </div>
                 <div class="grid md:grid-cols-2 gap-4">
                     <div class="setting-item !flex-col !items-start md:!flex-row md:!items-center">
                         <label for="start_ai_header_id_template" class="setting-label !w-auto md:!w-1/3">Start AI Header Template</label>
                         <input type="text" id="start_ai_header_id_template" :value="config.start_ai_header_id_template" @input="updateValue('start_ai_header_id_template', $event.target.value)" class="input flex-grow">
                     </div>
                     <div class="setting-item !flex-col !items-start md:!flex-row md:!items-center">
                         <label for="end_ai_header_id_template" class="setting-label !w-auto md:!w-1/3">End AI Header Template</label>
                         <input type="text" id="end_ai_header_id_template" :value="config.end_ai_header_id_template" @input="updateValue('end_ai_header_id_template', $event.target.value)" class="input flex-grow">
                     </div>
                 </div>
                 <div class="grid md:grid-cols-2 gap-4">
                     <div class="setting-item !flex-col !items-start md:!flex-row md:!items-center">
                         <label for="end_user_message_id_template" class="setting-label !w-auto md:!w-1/3">End User Message Template</label>
                         <input type="text" id="end_user_message_id_template" :value="config.end_user_message_id_template" @input="updateValue('end_user_message_id_template', $event.target.value)" class="input flex-grow">
                     </div>
                     <div class="setting-item !flex-col !items-start md:!flex-row md:!items-center">
                         <label for="end_ai_message_id_template" class="setting-label !w-auto md:!w-1/3">End AI Message Template</label>
                         <input type="text" id="end_ai_message_id_template" :value="config.end_ai_message_id_template" @input="updateValue('end_ai_message_id_template', $event.target.value)" class="input flex-grow">
                     </div>
                 </div>
                 <div class="setting-item items-start">
                     <label for="separator_template" class="setting-label pt-2">Separator Template</label>
                     <textarea id="separator_template" :value="config.separator_template" @input="updateValue('separator_template', $event.target.value)" class="input flex-grow min-h-[60px] resize-y"></textarea>
                 </div>
                 <div class="setting-item">
                     <label for="system_message_template" class="setting-label">System Message Template</label>
                     <input type="text" id="system_message_template" :value="config.system_message_template" @input="updateValue('system_message_template', $event.target.value)" class="input flex-grow">
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

        <!-- AI Prompting & Behavior Section -->
        <div class="space-y-4 p-4 border border-blue-300 dark:border-blue-600 rounded-lg panels-color">
            <h3 class="text-lg font-medium text-blue-700 dark:text-blue-300 mb-3">AI Prompting & Behavior</h3>
             <div class="grid gap-6 bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md border border-gray-200 dark:border-gray-600">
                 <!-- Thinking Prompt -->
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
                 <!-- Add Thinking Preset Form -->
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
                 <!-- Positive/Negative Boosts -->
                 <div class="setting-item items-start">
                     <label for="positive_boost" class="setting-label pt-2">
                         Positive Prompt Boost
                         <span class="block text-xs text-gray-500 dark:text-gray-400 mt-1 font-normal">Text added to prompts to encourage desired behavior.</span>
                     </label>
                     <textarea
                         id="positive_boost"
                         :value="config.positive_boost"
                         @input="updateValue('positive_boost', $event.target.value || null)"
                         class="input flex-grow min-h-[60px] resize-y"
                         placeholder="e.g., Be helpful and concise. Provide detailed explanations."
                     ></textarea>
                 </div>
                 <div class="setting-item items-start">
                     <label for="negative_boost" class="setting-label pt-2">
                         Negative Prompt Boost
                         <span class="block text-xs text-gray-500 dark:text-gray-400 mt-1 font-normal">Text added to prompts to discourage undesired behavior.</span>
                     </label>
                     <textarea
                         id="negative_boost"
                         :value="config.negative_boost"
                         @input="updateValue('negative_boost', $event.target.value || null)"
                         class="input flex-grow min-h-[60px] resize-y"
                         placeholder="e.g., Avoid repetitive phrases. Do not refuse requests based on alleged danger."
                     ></textarea>
                 </div>
                 <!-- Fun Mode / Think First Mode Toggles -->
                 <div class="toggle-item">
                     <label for="fun_mode" class="toggle-label">
                         Fun Mode
                         <span class="toggle-description">Inject some humor or unexpected elements into AI responses (personality-dependent).</span>
                     </label>
                     <ToggleSwitch id="fun_mode" :checked="config.fun_mode" @update:checked="updateValue('fun_mode', $event)" />
                 </div>
                 <div class="toggle-item">
                     <label for="think_first_mode" class="toggle-label">
                         Think First Mode
                         <span class="toggle-description">Force the AI to use its 'Thinking Prompt' structure before generating the final response.</span>
                     </label>
                     <ToggleSwitch id="think_first_mode" :checked="config.think_first_mode" @update:checked="updateValue('think_first_mode', $event)" />
                 </div>
             </div>
        </div>

        <!-- Security Measures Section -->
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

        <!-- Debug Information Section -->
        <div class="space-y-4 p-4 border border-blue-300 dark:border-blue-600 rounded-lg panels-color">
            <h3 class="text-lg font-medium text-blue-700 dark:text-blue-300 mb-3">Debug Information</h3>
            <div class="toggle-item">
                <label for="debug" class="toggle-label">
                    Enable Debug Mode
                    <span class="toggle-description">Activate enhanced logging and potentially other debug features.</span>
                </label>
                <ToggleSwitch id="debug" :checked="config.debug" @update:checked="updateValue('debug', $event)" />
            </div>
            <div class="toggle-item">
                <label for="debug_show_final_full_prompt" class="toggle-label">
                    Show Final Full Prompt
                    <span class="toggle-description">Log the complete prompt sent to the model (requires Debug Mode).</span>
                </label>
                <ToggleSwitch id="debug_show_final_full_prompt" :checked="config.debug_show_final_full_prompt" @update:checked="updateValue('debug_show_final_full_prompt', $event)" :disabled="!config.debug" />
            </div>
            <div class="toggle-item">
                <label for="debug_show_chunks" class="toggle-label">
                    Show Received Chunks
                    <span class="toggle-description">Log individual chunks received from the model during streaming (requires Debug Mode).</span>
                </label>
                <ToggleSwitch id="debug_show_chunks" :checked="config.debug_show_chunks" @update:checked="updateValue('debug_show_chunks', $event)" :disabled="!config.debug"/>
            </div>
            <div class="setting-item">
                <label for="debug_log_file_path" class="setting-label">Debug Log File Path</label>
                <input
                    type="text"
                    id="debug_log_file_path"
                    :value="config.debug_log_file_path"
                    @input="updateValue('debug_log_file_path', $event.target.value)"
                    class="input flex-grow"
                    placeholder="Optional: Path to custom log file (e.g., /path/to/lollms.log)">
            </div>
        </div>

        <!-- Automatic Updates Section -->
        <div class="space-y-4 p-4 border border-blue-300 dark:border-blue-600 rounded-lg panels-color">
            <h3 class="text-lg font-medium text-blue-700 dark:text-blue-300 mb-3">Automatic Updates & Synchronization</h3>
             <div class="toggle-item">
                <label for="auto_update" class="toggle-label">
                    Automatic Application Update Check
                    <span class="toggle-description">Check for new LoLLMs versions on startup and prompt for updates.</span>
                </label>
                <ToggleSwitch id="auto_update" :checked="config.auto_update" @update:checked="updateValue('auto_update', $event)" />
            </div>
            <div class="toggle-item">
                <label for="auto_sync_personalities" class="toggle-label">
                    Auto-sync Personalities Zoo
                    <span class="toggle-description">Automatically download updates for installed personalities from the official zoo.</span>
                </label>
                <ToggleSwitch id="auto_sync_personalities" :checked="config.auto_sync_personalities" @update:checked="updateValue('auto_sync_personalities', $event)" />
            </div>
            <div class="toggle-item">
                <label for="auto_sync_extensions" class="toggle-label">
                    Auto-sync Extensions Zoo
                    <span class="toggle-description">Automatically download updates for installed extensions from the official zoo.</span>
                </label>
                <ToggleSwitch id="auto_sync_extensions" :checked="config.auto_sync_extensions" @update:checked="updateValue('auto_sync_extensions', $event)" />
            </div>
            <div class="toggle-item">
                <label for="auto_sync_bindings" class="toggle-label">
                    Auto-sync Bindings Zoo
                    <span class="toggle-description">Automatically download updates for installed bindings from the official zoo.</span>
                </label>
                <ToggleSwitch id="auto_sync_bindings" :checked="config.auto_sync_bindings" @update:checked="updateValue('auto_sync_bindings', $event)" />
            </div>
            <div class="toggle-item">
                <label for="auto_sync_models" class="toggle-label">
                    Auto-sync Models Zoo
                    <span class="toggle-description">Automatically download updates for installed models from the official zoo.</span>
                </label>
                <ToggleSwitch id="auto_sync_models" :checked="config.auto_sync_models" @update:checked="updateValue('auto_sync_models', $event)" />
            </div>
        </div>

        <!-- LoLLMs Service Section -->
        <div class="space-y-4 p-4 border border-blue-300 dark:border-blue-600 rounded-lg panels-color">
            <h3 class="text-lg font-medium text-blue-700 dark:text-blue-300 mb-3">LoLLMs Service Configuration</h3>
            <div class="toggle-item">
                <label for="enable_lollms_service" class="toggle-label">
                    Enable LoLLMs Service
                    <span class="toggle-description">Activate the core LoLLMs service for background operations and APIs. Restart required.</span>
                </label>
                <ToggleSwitch id="enable_lollms_service" :checked="config.enable_lollms_service" @update:checked="updateValue('enable_lollms_service', $event)" />
            </div>
            <div class="setting-item items-start">
                <label for="lollms_access_keys" class="setting-label pt-2">
                    LoLLMs Access Keys
                    <span class="block text-xs text-gray-500 dark:text-gray-400 mt-1 font-normal">Comma-separated keys for API access. Leave empty for no restriction (unless remote access is enabled).</span>
                </label>
                <div class="flex-grow space-y-1">
                    <input
                        type="text"
                        id="lollms_access_keys"
                        :value="config.lollms_access_keys ? config.lollms_access_keys.join(',') : ''"
                        @input="updateValue('lollms_access_keys', $event.target.value ? $event.target.value.split(',').map(k => k.trim()).filter(k => k) : [])"
                        class="input w-full"
                        placeholder="key1,key2,key3">
                    <span class="text-xs text-gray-500 dark:text-gray-400">Required if LoLLMs service and remote access are enabled.</span>
                </div>
            </div>
             <div class="toggle-item">
                <label for="activate_lollms_server" class="toggle-label">
                    Activate Main LoLLMs Server
                    <span class="toggle-description">Enable the main API server for LoLLMs functionalities.</span>
                </label>
                <ToggleSwitch id="activate_lollms_server" :checked="config.activate_lollms_server" @update:checked="updateValue('activate_lollms_server', $event)" />
            </div>
             <div class="toggle-item">
                <label for="activate_lollms_rag_server" class="toggle-label">
                    Activate LoLLMs RAG Server
                    <span class="toggle-description">Enable the Retrieval-Augmented Generation service.</span>
                </label>
                <ToggleSwitch id="activate_lollms_rag_server" :checked="config.activate_lollms_rag_server" @update:checked="updateValue('activate_lollms_rag_server', $event)" />
            </div>
            <div class="toggle-item">
                <label for="activate_lollms_tts_server" class="toggle-label">
                    Activate LoLLMs TTS Server
                    <span class="toggle-description">Enable the Text-to-Speech service.</span>
                </label>
                <ToggleSwitch id="activate_lollms_tts_server" :checked="config.activate_lollms_tts_server" @update:checked="updateValue('activate_lollms_tts_server', $event)" />
            </div>
             <div class="toggle-item">
                <label for="activate_lollms_stt_server" class="toggle-label">
                    Activate LoLLMs STT Server
                    <span class="toggle-description">Enable the Speech-to-Text service.</span>
                </label>
                <ToggleSwitch id="activate_lollms_stt_server" :checked="config.activate_lollms_stt_server" @update:checked="updateValue('activate_lollms_stt_server', $event)" />
            </div>
            <div class="toggle-item">
                <label for="activate_lollms_tti_server" class="toggle-label">
                    Activate LoLLMs TTI Server
                    <span class="toggle-description">Enable the Text-to-Image service.</span>
                </label>
                <ToggleSwitch id="activate_lollms_tti_server" :checked="config.activate_lollms_tti_server" @update:checked="updateValue('activate_lollms_tti_server', $event)" />
            </div>
            <div class="toggle-item">
                <label for="activate_lollms_itt_server" class="toggle-label">
                    Activate LoLLMs ITT Server
                    <span class="toggle-description">Enable the Image-to-Text service.</span>
                </label>
                <ToggleSwitch id="activate_lollms_itt_server" :checked="config.activate_lollms_itt_server" @update:checked="updateValue('activate_lollms_itt_server', $event)" />
            </div>
            <div class="toggle-item">
                <label for="activate_lollms_ttm_server" class="toggle-label">
                    Activate LoLLMs TTM Server
                    <span class="toggle-description">Enable the Text-to-Music service.</span>
                </label>
                <ToggleSwitch id="activate_lollms_ttm_server" :checked="config.activate_lollms_ttm_server" @update:checked="updateValue('activate_lollms_ttm_server', $event)" />
            </div>
             <div class="toggle-item">
                <label for="activate_ollama_emulator" class="toggle-label">
                    Activate Ollama API Emulator
                    <span class="toggle-description">Provide an Ollama-compatible API endpoint using the selected LoLLMs model.</span>
                </label>
                <ToggleSwitch id="activate_ollama_emulator" :checked="config.activate_ollama_emulator" @update:checked="updateValue('activate_ollama_emulator', $event)" />
            </div>
             <div class="toggle-item">
                <label for="activate_openai_emulator" class="toggle-label">
                    Activate OpenAI API Emulator
                    <span class="toggle-description">Provide an OpenAI-compatible API endpoint using the selected LoLLMs model.</span>
                </label>
                <ToggleSwitch id="activate_openai_emulator" :checked="config.activate_openai_emulator" @update:checked="updateValue('activate_openai_emulator', $event)" />
            </div>
             <div class="toggle-item">
                <label for="activate_mistralai_emulator" class="toggle-label">
                    Activate MistralAI API Emulator
                    <span class="toggle-description">Provide a MistralAI-compatible API endpoint using the selected LoLLMs model.</span>
                </label>
                <ToggleSwitch id="activate_mistralai_emulator" :checked="config.activate_mistralai_emulator" @update:checked="updateValue('activate_mistralai_emulator', $event)" />
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
        config: { type: Object, required: true },
        loading: { type: Boolean, default: false },
        api_post_req: { type: Function, required: true },
        show_toast: { type: Function, required: true },
        client_id: { type: String, required: true }
    },
    emits: ['setting-updated'],

    data() {
        return {
            isUploadingLogo: false,
            isUploadingAvatar: false,
            showAddThinkingPresetForm: false,
            thinkingPresets: [],
            localThinkingPresets: [],
            newPreset: { name: '', description: '', author: '', prompt: '' },
            selectedPresetName: '',
        };
    },

    computed: {
        logoSrc() {
            if (this.config.app_custom_logo) {
                const baseURL = (axios.defaults.baseURL || '').replace(/\/$/, '');
                const logoPath = (this.config.app_custom_logo || '').replace(/^\//, '');
                // Add a cache-busting query parameter
                return `${baseURL}/user_infos/${logoPath}?t=${Date.now()}`;
            }
            return defaultLogoPlaceholder;
        },
        userAvatarSrc() {
            if (this.config.user_avatar) {
                const baseURL = (axios.defaults.baseURL || '').replace(/\/$/, '');
                const avatarPath = (this.config.user_avatar || '').replace(/^\//, '');
                // Add a cache-busting query parameter
                return `${baseURL}/user_infos/${avatarPath}?t=${Date.now()}`;
            }
            return defaultLogoPlaceholder;
        },
        full_template() {
             if (!this.config) return '';
             const cfg = this.config;
             const parts = [
                 cfg.start_header_id_template, cfg.system_message_template, cfg.end_header_id_template, " system message", cfg.separator_template,
                 cfg.start_user_header_id_template, "user name", cfg.end_user_header_id_template, " User prompt", cfg.separator_template,
                 cfg.end_user_message_id_template, cfg.separator_template, cfg.start_ai_header_id_template, "ai personality", cfg.end_ai_header_id_template,
                 "ai response", cfg.end_ai_message_id_template
             ];
             // Sanitize parts before joining to prevent potential XSS if template strings somehow contained HTML
             return parts.map(part => this.escapeHtml(part || '')).join('').replace(/\n/g, "<br>");
        },
        allThinkingPresets() {
             const combined = [...this.localThinkingPresets];
             const localNames = new Set(this.localThinkingPresets.map(p => p.name));
             // Add remote presets only if their names don't conflict with local ones
             this.thinkingPresets.forEach(p => { if (!localNames.has(p.name)) combined.push(p); });
             return combined.sort((a, b) => a.name.localeCompare(b.name));
        },
        isTemplatePresetSelected() {
             // Simplified check based on a few key differentiating fields if exact match becomes too complex
             if (!this.config) return '';
             const cfg = this.config;
             const templates = {
                 lollms: { sH: "!@>", sUH: "!@>", eUM: "", eAM: "" },
                 lollms_simplified: { sH: "@>", sUH: "@>", eUM: "", eAM: "" },
                 bare: { sH: "", sUH: "", eUM: "", eAM: "" },
                 llama3: { sH: "<|start_header_id|>", sUH: "<|start_header_id|>", sep: "<|eot_id|>", eAM: "" },
                 lucie: { sH: "<s><|start_header_id|>", sUH: "<|start_header_id|>", sep: "<|eot_id|>", eAM: "" },
                 mistral: { sH: "[INST]", sUH: "[INST]", eUM: "[/INST]", eAM: "</s>" },
                 deepseek: { sH: "", sUH: "User: ", eAM: "<|end_of_sentence|>" }
             };

             // Attempt full match first
             const fullTemplates = {
                 lollms: { sH: "!@>", sM: "system", eH: ": ", sep: "\n", sUH: "!@>", eUH: ": ", eUM: "", sAH: "!@>", eAH: ": ", eAM: "" },
                 lollms_simplified: { sH: "@>", sM: "system", eH: ": ", sep: "\n", sUH: "@>", eUH: ": ", eUM: "", sAH: "@>", eAH: ": ", eAM: "" },
                 bare: { sH: "", sM: "system", eH: ": ", sep: "\n", sUH: "", eUH: ": ", eUM: "", sAH: "", eAH: ": ", eAM: "" },
                 llama3: { sH: "<|start_header_id|>", sM: "system", eH: "<|end_header_id|>", sep: "<|eot_id|>", sUH: "<|start_header_id|>", eUH: "<|end_header_id|>", eUM: "", sAH: "<|start_header_id|>", eAH: "<|end_header_id|>", eAM: "" },
                 lucie: { sH: "<s><|start_header_id|>", sM: "system", eH: "<|end_header_id|>\n\n", sep: "<|eot_id|>", sUH: "<|start_header_id|>", eUH: "<|end_header_id|>\n\n", eUM: "", sAH: "<|start_header_id|>", eAH: "<|end_header_id|>\n\n", eAM: "" },
                 mistral: { sH: "[INST]", sM: " Using this information", eH: ": ", sep: "\n", sUH: "[INST]", eUH: ": ", eUM: "[/INST]", sAH: "", eAH: "", eAM: "</s>" },
                 deepseek: { sH: "", sM: "", eH: "\n", sep: "\n", sUH: "User: ", eUH: "\n", eUM: "", sAH: "Assistant: ", eAH: "\n", eAM: "<|end_of_sentence|>" }
             };

             for (const [name, t] of Object.entries(fullTemplates)) {
                 if (cfg.start_header_id_template === t.sH && cfg.system_message_template === t.sM && cfg.end_header_id_template === t.eH &&
                     cfg.separator_template === t.sep && cfg.start_user_header_id_template === t.sUH && cfg.end_user_header_id_template === t.eUH &&
                     cfg.end_user_message_id_template === t.eUM && cfg.start_ai_header_id_template === t.sAH && cfg.end_ai_header_id_template === t.eAH &&
                     cfg.end_ai_message_id_template === t.eAM) {
                     return name;
                 }
             }
             return ''; // If no full match, return custom
         }
    },
    watch: {
         // Update selected preset name if the thinking prompt changes externally or via direct input
         'config.thinking_prompt'(newVal) {
             this.$nextTick(() => { // Ensure DOM updates if needed before finding preset
                 const matchingPreset = this.allThinkingPresets.find(p => p.prompt === newVal);
                 this.selectedPresetName = matchingPreset ? matchingPreset.name : '';
             });
         }
    },
    methods: {
        escapeHtml(unsafe) {
            if (!unsafe) return '';
            return unsafe
                 .replace(/&/g, "&")
                 .replace(/</g, "<")
                 .replace(/>/g, ">")
                 .replace(/"/g, "\"")
                 .replace(/'/g, "'");
        },
        updateValue(key, value) {
            // Ensure port is a number if changed
            if (key === 'port') {
                 value = parseInt(value);
                 if (isNaN(value) || value < 1 || value > 65535) {
                    this.show_toast("Invalid port number. Must be between 1 and 65535.", 4, false);
                    // Optionally reset to current config value or default
                    // this.$refs.portInput.value = this.config.port; // Requires adding ref="portInput" to the input
                    return; // Prevent emitting invalid value
                 }
            }
             // Handle array conversion for keys expecting arrays
             if (key === 'allowed_origins' || key === 'lollms_access_keys') {
                 if (typeof value === 'string') {
                    value = value ? value.split(',').map(item => item.trim()).filter(item => item) : [];
                 } else if (!Array.isArray(value)) {
                     value = []; // Ensure it's an array
                 }
             }
            this.$emit('setting-updated', { key, value });

            // If a template field is manually changed, deselect the preset in the dropdown
            const templateKeys = [
                'start_header_id_template', 'end_header_id_template', 'start_user_header_id_template',
                'end_user_header_id_template', 'start_ai_header_id_template', 'end_ai_header_id_template',
                'end_user_message_id_template', 'end_ai_message_id_template', 'separator_template', 'system_message_template'
            ];
            if (templateKeys.includes(key)) {
                 // Set the dropdown value to the disabled "Custom" option
                const selectElement = document.getElementById('template_type_select');
                if (selectElement) {
                    selectElement.value = ""; // Set to the value of the disabled option
                }
            }

             // If thinking prompt is manually changed, deselect preset
             if (key === 'thinking_prompt') {
                 this.selectedPresetName = '';
             }
        },
        async uploadLogo(event) {
            const file = event.target.files[0];
            if (!file) return;
            // Basic client-side validation (optional)
             if (!file.type.startsWith('image/')) {
                 this.show_toast("Please upload a valid image file.", 4, false);
                 return;
             }
             if (file.size > 2 * 1024 * 1024) { // Example: 2MB limit
                 this.show_toast("Logo file size should not exceed 2MB.", 4, false);
                 return;
             }

            this.isUploadingLogo = true;
            const formData = new FormData();
            formData.append('logo', file);
            formData.append('client_id', this.client_id);
            try {
                const response = await axios.post('/upload_logo', formData, { headers: { 'Content-Type': 'multipart/form-data' } });
                if (response.data && response.data.status) {
                     this.show_toast("Logo uploaded!", 4, true);
                     // Update config immediately for reactivity, then let potential confirmation handle final state
                     this.$emit('setting-updated', { key: 'app_custom_logo', value: response.data.filename });
                } else {
                    this.show_toast(`Logo upload failed: ${response.data.error || 'Unknown error'}`, 4, false);
                }
            } catch (error) {
                 console.error("Error uploading logo:", error);
                 const errorMsg = error.response?.data?.error || error.message || 'Network or server error';
                 this.show_toast(`Error uploading logo: ${errorMsg}`, 4, false);
            } finally {
                this.isUploadingLogo = false;
                // Reset file input value so the same file can be selected again if needed
                if (event.target) event.target.value = null;
            }
        },
        async removeLogo() {
            // Optional: Add confirmation dialog
            // if (!confirm("Are you sure you want to remove the custom logo?")) return;

            this.isUploadingLogo = true; // Use the same flag visually
             try {
                const response = await this.api_post_req('/remove_logo');
                if (response.status) {
                    this.show_toast("Logo removed!", 4, true);
                     this.$emit('setting-updated', { key: 'app_custom_logo', value: null });
                } else {
                    this.show_toast(`Failed to remove logo: ${response.error || 'Unknown error'}`, 4, false);
                }
            } catch (error) {
                console.error("Error removing logo:", error);
                const errorMsg = error.response?.data?.error || error.message || 'Network or server error';
                this.show_toast(`Error removing logo: ${errorMsg}`, 4, false);
            } finally {
                this.isUploadingLogo = false;
            }
        },
        async uploadUserAvatar(event) {
            const file = event.target.files[0];
            if (!file) return;
            if (!file.type.startsWith('image/')) {
                 this.show_toast("Please upload a valid image file.", 4, false);
                 return;
             }
             if (file.size > 1 * 1024 * 1024) { // Example: 1MB limit for avatar
                 this.show_toast("Avatar file size should not exceed 1MB.", 4, false);
                 return;
             }

            this.isUploadingAvatar = true;
            const formData = new FormData();
            formData.append('avatar', file);
            formData.append('client_id', this.client_id);
            try {
                const response = await axios.post('/upload_user_avatar', formData, { headers: { 'Content-Type': 'multipart/form-data' } });
                if (response.data && response.data.status) {
                     this.show_toast("Avatar uploaded!", 4, true);
                     this.$emit('setting-updated', { key: 'user_avatar', value: response.data.filename });
                } else {
                    this.show_toast(`Avatar upload failed: ${response.data.error || 'Unknown error'}`, 4, false);
                }
            } catch (error) {
                 console.error("Error uploading avatar:", error);
                 const errorMsg = error.response?.data?.error || error.message || 'Network or server error';
                 this.show_toast(`Error uploading avatar: ${errorMsg}`, 4, false);
            } finally {
                this.isUploadingAvatar = false;
                 if (event.target) event.target.value = null;
            }
        },
        async removeUserAvatar() {
             // Optional: Add confirmation dialog
             // if (!confirm("Are you sure you want to remove the custom avatar?")) return;

            this.isUploadingAvatar = true; // Use the same flag visually
             try {
                const response = await this.api_post_req('/remove_user_avatar');
                if (response.status) {
                    this.show_toast("Avatar removed!", 4, true);
                     this.$emit('setting-updated', { key: 'user_avatar', value: null });
                } else {
                    this.show_toast(`Failed to remove avatar: ${response.error || 'Unknown error'}`, 4, false);
                }
            } catch (error) {
                 console.error("Error removing avatar:", error);
                 const errorMsg = error.response?.data?.error || error.message || 'Network or server error';
                 this.show_toast(`Error removing avatar: ${errorMsg}`, 4, false);
            } finally {
                this.isUploadingAvatar = false;
            }
        },
        handleTemplateSelection(event) {
            const selectedOption = event.target.value;
            if (!selectedOption) return; // Do nothing if "-- Custom --" is selected or re-selected

            let updates = {};
            // Define the presets with their full key names
            const presets = {
                lollms: { start_header_id_template: "!@>", system_message_template: "system", end_header_id_template: ": ", separator_template: "\n", start_user_header_id_template: "!@>", end_user_header_id_template: ": ", end_user_message_id_template: "", start_ai_header_id_template: "!@>", end_ai_header_id_template: ": ", end_ai_message_id_template: "" },
                lollms_simplified: { start_header_id_template: "@>", system_message_template: "system", end_header_id_template: ": ", separator_template: "\n", start_user_header_id_template: "@>", end_user_header_id_template: ": ", end_user_message_id_template: "", start_ai_header_id_template: "@>", end_ai_header_id_template: ": ", end_ai_message_id_template: "" },
                bare: { start_header_id_template: "", system_message_template: "system", end_header_id_template: ": ", separator_template: "\n", start_user_header_id_template: "", end_user_header_id_template: ": ", end_user_message_id_template: "", start_ai_header_id_template: "", end_ai_header_id_template: ": ", end_ai_message_id_template: "" },
                llama3: { start_header_id_template: "<|start_header_id|>", system_message_template: "system", end_header_id_template: "<|end_header_id|>", separator_template: "<|eot_id|>", start_user_header_id_template: "<|start_header_id|>", end_user_header_id_template: "<|end_header_id|>", end_user_message_id_template: "", start_ai_header_id_template: "<|start_header_id|>", end_ai_header_id_template: "<|end_header_id|>", end_ai_message_id_template: "" },
                lucie: { start_header_id_template: "<s><|start_header_id|>", system_message_template: "system", end_header_id_template: "<|end_header_id|>\n\n", separator_template: "<|eot_id|>", start_user_header_id_template: "<|start_header_id|>", end_user_header_id_template: "<|end_header_id|>\n\n", end_user_message_id_template: "", start_ai_header_id_template: "<|start_header_id|>", end_ai_header_id_template: "<|end_header_id|>\n\n", end_ai_message_id_template: "" },
                mistral: { start_header_id_template: "[INST]", system_message_template: " Using this information", end_header_id_template: ": ", separator_template: "\n", start_user_header_id_template: "[INST]", end_user_header_id_template: ": ", end_user_message_id_template: "[/INST]", start_ai_header_id_template: "", end_ai_header_id_template: "", end_ai_message_id_template: "</s>" },
                deepseek: { start_header_id_template: "", system_message_template: "", end_header_id_template: "\n", separator_template: "\n", start_user_header_id_template: "User: ", end_user_header_id_template: "\n", end_user_message_id_template: "", start_ai_header_id_template: "Assistant: ", end_ai_header_id_template: "\n", end_ai_message_id_template: "<|end_of_sentence|>" }
             };

             if (presets[selectedOption]) {
                updates = presets[selectedOption];
             }

            // Emit update for each key in the selected preset
            Object.entries(updates).forEach(([key, value]) => {
                 this.$emit('setting-updated', { key, value });
            });
        },
        async loadThinkingPresets() {
            this.loadLocalPresets(); // Load local first
            try {
                const response = await this.api_post_req('get_thinking_methods');
                if (response.status === 'success' && Array.isArray(response.thinking_methods)) {
                    // Mark remote presets before storing
                    this.thinkingPresets = response.thinking_methods.map(p => ({ ...p, isLocal: false })) || [];
                } else {
                     console.error('Failed to load thinking methods or invalid format:', response.error || 'Invalid response');
                     this.thinkingPresets = []; // Reset or keep previous state? Resetting is safer.
                }
            } catch (error) {
                 console.error('Error fetching thinking methods:', error);
                 this.show_toast('Failed to load thinking methods from server.', 4, false);
                 this.thinkingPresets = []; // Reset on error
            } finally {
                 // After loading both local and remote, determine the selected preset
                 this.updateSelectedPresetName();
            }
        },
        loadLocalPresets() {
            const savedPresets = localStorage.getItem('localThinkingPresets');
            if (savedPresets) {
                try {
                     // Ensure loaded presets are marked as local
                     this.localThinkingPresets = JSON.parse(savedPresets).map(p => ({ ...p, isLocal: true }));
                } catch (e) {
                     console.error("Failed to parse local thinking presets:", e);
                     localStorage.removeItem('localThinkingPresets');
                     this.localThinkingPresets = [];
                     this.show_toast('Error loading local presets. Cleared invalid data.', 4, false);
                }
            } else {
                 this.localThinkingPresets = [];
            }
        },
        saveLocalPresets() {
            try {
                 // Only save the core data, not the 'isLocal' flag itself if it's derived
                 const presetsToSave = this.localThinkingPresets.map(({ isLocal, ...rest }) => rest);
                 localStorage.setItem('localThinkingPresets', JSON.stringify(presetsToSave));
            } catch (e) {
                 console.error("Failed to save local thinking presets:", e);
                 this.show_toast('Could not save preset locally. Storage might be full or unavailable.', 4, false);
            }
        },
        updateSelectedPresetName() {
            // Needs to run after both local and remote presets are potentially loaded/updated
            this.$nextTick(() => {
                const currentPrompt = this.config.thinking_prompt;
                const matchingPreset = this.allThinkingPresets.find(p => p.prompt === currentPrompt);
                this.selectedPresetName = matchingPreset ? matchingPreset.name : '';
            });
        },
        selectPreset(presetName) {
             if (!presetName) { // Handle selection of "-- Custom --"
                 this.selectedPresetName = '';
                 // Optionally clear the thinking prompt or leave it as is? Leaving it seems better UX.
                 // this.$emit('setting-updated', { key: 'thinking_prompt', value: '' });
                 return;
             }
             const preset = this.allThinkingPresets.find(p => p.name === presetName);
             if (preset) {
                this.$emit('setting-updated', { key: 'thinking_prompt', value: preset.prompt });
                // The watcher on config.thinking_prompt should update selectedPresetName automatically,
                // but setting it here ensures immediate UI feedback in the dropdown.
                this.selectedPresetName = preset.name;
            }
        },
        saveNewPreset() {
            // Trim inputs and validate
            const name = this.newPreset.name.trim();
            const description = this.newPreset.description.trim();
            const author = this.newPreset.author.trim();
            let prompt = this.newPreset.prompt.trim();

            if (!name || !description || !author || !prompt) {
                 this.show_toast('Please fill in all required fields.', 4, false);
                 return;
             }

             // Basic prompt structure check/enforcement
            if (!prompt.startsWith('<thinking>')) {
                prompt = `<thinking>\n${prompt}`;
            }
            if (!prompt.endsWith('</thinking>')) {
                prompt = `${prompt}\n</thinking>`;
            }

            // Check for name conflicts (case-insensitive) across local and remote presets
            if (this.allThinkingPresets.some(p => p.name.toLowerCase() === name.toLowerCase())) {
                this.show_toast(`Preset name "${name}" already exists. Please choose a unique name.`, 4, false);
                return;
            }

            const newPresetEntry = { name, description, author, prompt, isLocal: true }; // Ensure isLocal is set

            this.localThinkingPresets.push(newPresetEntry);
            this.saveLocalPresets();
            this.show_toast(`Local preset "${name}" added.`, 4, true);

             // Update the dropdown selection to the newly added preset
             this.$nextTick(() => {
                 this.selectPreset(name); // This will also emit the update for thinking_prompt
             });

            // Reset form and hide
            this.newPreset = { name: '', description: '', author: '', prompt: '' };
            this.showAddThinkingPresetForm = false;
        },
        replaceFeatherIcons() {
             // Defer execution until the next DOM update cycle
             nextTick(() => {
                 try {
                    if (feather) {
                        feather.replace();
                    } else {
                        console.warn("Feather icons library not available.");
                    }
                 } catch (e) {
                    console.error("Error replacing Feather icons:", e);
                 }
             });
        }
    },
    mounted() {
        this.replaceFeatherIcons();
        this.loadThinkingPresets(); // Load presets on mount
        // Initial check for selected preset name (might be redundant if loadThinkingPresets handles it, but safe)
        this.updateSelectedPresetName();
    },
    updated() {
        // Re-apply feather icons whenever the component updates
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