// src/components/settings_components/DataManagementSettings.vue
<template>
    <div class="space-y-6 p-4 md:p-6 bg-white dark:bg-gray-800 rounded-lg shadow-md border border-gray-200 dark:border-gray-700">
        <h2 class="text-xl font-semibold text-gray-800 dark:text-gray-200 border-b border-gray-200 dark:border-gray-700 pb-2">
            Data Management
        </h2>

        <!-- Data Lakes Configuration -->
        <section class="space-y-4 p-4 border border-gray-200 dark:border-gray-600 rounded-lg">
            <h3 class="text-lg font-medium text-gray-700 dark:text-gray-300 mb-3">Data Lakes</h3>
             <p class="text-xs text-gray-500 dark:text-gray-400 mb-4">
                Configure data sources (vector databases) that LoLLMs can query for information retrieval (RAG).
            </p>

            <!-- Data Lakes List -->
            <div class="space-y-4">
                 <div v-if="!config.datalakes || config.datalakes.length === 0" class="text-center text-gray-500 dark:text-gray-400 py-4">
                    No Data Lakes configured.
                </div>
                <div v-for="(source, index) in config.datalakes" :key="`datalake-${index}`"
                    class="p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg shadow-sm border border-gray-200 dark:border-gray-600 space-y-4 relative group"
                >
                     <!-- Remove Button (Top Right) -->
                     <button
                        @click="removeDataLake(index)"
                        class="absolute top-2 right-2 p-1 rounded-full text-red-500 hover:bg-red-100 dark:hover:bg-red-900/50 opacity-0 group-hover:opacity-100 transition-opacity duration-200"
                        title="Remove Data Lake"
                    >
                        <i data-feather="x-circle" class="w-5 h-5"></i>
                    </button>

                    <!-- Main Controls Grid -->
                     <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <!-- Data Lake Alias -->
                        <div>
                             <label :for="`dl-alias-${index}`" class="setting-label-inline">Alias</label>
                             <input
                                type="text"
                                :id="`dl-alias-${index}`"
                                :value="source.alias"
                                @input="updateDataLake(index, 'alias', $event.target.value)"
                                class="input-field-sm w-full"
                                placeholder="Enter alias (e.g., 'Project Docs')"
                            >
                        </div>

                        <!-- Data Lake Type -->
                         <div>
                            <label :for="`dl-type-${index}`" class="setting-label-inline">Type</label>
                            <select
                                :id="`dl-type-${index}`"
                                required
                                :value="source.type"
                                @change="updateDataLake(index, 'type', $event.target.value)"
                                class="input-field-sm w-full"
                            >
                                <option value="lollmsvectordb">LoLLMs VectorDB</option>
                                <option value="lightrag">LightRAG</option>
                                <option value="elasticsearch">Elasticsearch</option>
                            </select>
                        </div>

                         <!-- Conditional URL/Path Input -->
                        <div class="md:col-span-2">
                             <label :for="`dl-pathurl-${index}`" class="setting-label-inline">
                                {{ source.type === 'lollmsvectordb' ? 'Database Path' : (source.type === 'lightrag' ? 'LightRAG URL' : 'Elasticsearch URL') }}
                            </label>
                            <input
                                type="text"
                                :id="`dl-pathurl-${index}`"
                                :value="source.type === 'lollmsvectordb' ? source.path : source.url"
                                @input="updateDataLake(index, source.type === 'lollmsvectordb' ? 'path' : 'url', $event.target.value)"
                                class="input-field-sm w-full"
                                :placeholder="source.type === 'lollmsvectordb' ? 'Path to database folder' : 'http://host:port/'"
                             >
                        </div>

                         <!-- API Key (conditional) -->
                        <div v-if="source.type === 'lightrag' || source.type === 'elasticsearch'" class="md:col-span-2">
                             <label :for="`dl-key-${index}`" class="setting-label-inline">API Key (Optional)</label>
                            <input
                                type="password"
                                :id="`dl-key-${index}`"
                                :value="source.key"
                                @input="updateDataLake(index, 'key', $event.target.value)"
                                class="input-field-sm w-full"
                                placeholder="Enter API key if required"
                            >
                        </div>
                    </div>

                    <!-- Actions Row -->
                    <div class="flex flex-wrap items-center justify-between gap-2 pt-3 border-t border-gray-300 dark:border-gray-600">
                         <!-- Mounted Toggle -->
                        <div class="flex items-center space-x-2">
                            <ToggleSwitch
                                :id="`dl-mounted-${index}`"
                                :checked="source.mounted"
                                @update:checked="updateDataLake(index, 'mounted', $event)"
                            />
                            <label :for="`dl-mounted-${index}`" class="text-sm font-medium text-gray-700 dark:text-gray-300 cursor-pointer">
                                Mounted
                            </label>
                        </div>


                         <!-- Type Specific Actions -->
                        <div class="flex flex-wrap gap-2">
                             <!-- Lollms VectorDB Actions -->
                            <template v-if="source.type === 'lollmsvectordb'">
                                <button @click="vectorizeFolder(index)" class="button-secondary-sm" title="Vectorize or re-vectorize the selected folder">
                                     <i data-feather="refresh-cw" class="w-4 h-4 mr-1"></i> Vectorize
                                 </button>
                                <button @click="selectLollmsVectordbFolder(index)" class="button-primary-sm" title="Select folder containing documents to vectorize">
                                    <i data-feather="folder-plus" class="w-4 h-4 mr-1"></i> Select Folder
                                </button>
                            </template>

                            <!-- LightRAG Actions -->
                             <template v-if="source.type === 'lightrag'">
                                 <button @click="triggerFileInput(index)" class="button-success-sm" title="Upload supported files (.txt, .md, .pdf, .docx, .pptx, .xlsx)">
                                     <i data-feather="upload" class="w-4 h-4 mr-1"></i> Upload Files
                                </button>
                                <input type="file" :ref="el => fileInputs[index] = el" @change="handleFileUpload($event, index)"
                                       accept=".txt,.md,.pdf,.docx,.pptx,.xlsx" class="hidden" multiple />
                                <!-- Add Check Status button later if needed -->
                             </template>
                         </div>
                    </div>
                </div>
            </div>

             <!-- Add New Data Lake Button -->
            <div class="pt-4">
                <button @click="addDataLake" class="button-primary w-full md:w-auto">
                    <i data-feather="plus-circle" class="w-5 h-5 mr-2"></i> Add New Data Lake
                </button>
            </div>
        </section>

        <!-- Database Servers Configuration -->
        <section class="space-y-4 p-4 border border-gray-200 dark:border-gray-600 rounded-lg">
            <h3 class="text-lg font-medium text-gray-700 dark:text-gray-300 mb-3">Self-Hosted RAG Servers</h3>
             <p class="text-xs text-gray-500 dark:text-gray-400 mb-4">
                 Configure and manage local RAG server instances (like LightRAG) running on your machine.
            </p>
             <!-- Servers List -->
            <div class="space-y-4">
                 <div v-if="!config.rag_local_services || config.rag_local_services.length === 0" class="text-center text-gray-500 dark:text-gray-400 py-4">
                    No RAG Servers configured.
                </div>
                <div v-for="(server, index) in config.rag_local_services" :key="`server-${index}`"
                    class="p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg shadow-sm border border-gray-200 dark:border-gray-600 space-y-4 relative group"
                >
                     <!-- Remove Button -->
                     <button
                        @click="removeDatabaseService(index)"
                        class="absolute top-2 right-2 p-1 rounded-full text-red-500 hover:bg-red-100 dark:hover:bg-red-900/50 opacity-0 group-hover:opacity-100 transition-opacity duration-200"
                        title="Remove Server"
                    >
                        <i data-feather="x-circle" class="w-5 h-5"></i>
                    </button>

                    <!-- Server Controls Grid -->
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                         <!-- Server Alias -->
                         <div>
                            <label :for="`srv-alias-${index}`" class="setting-label-inline">Alias</label>
                            <input type="text" :id="`srv-alias-${index}`" :value="server.alias" @input="updateServer(index, 'alias', $event.target.value)" class="input-field-sm w-full" placeholder="Server Alias">
                         </div>
                         <!-- Server Type -->
                         <div>
                            <label :for="`srv-type-${index}`" class="setting-label-inline">Type</label>
                             <select :id="`srv-type-${index}`" required :value="server.type" @change="updateServer(index, 'type', $event.target.value)" class="input-field-sm w-full">
                                <option value="lightrag">LightRAG</option>
                                <!-- <option value="elasticsearch">Elasticsearch</option> -->
                             </select>
                         </div>
                         <!-- Server URL -->
                         <div class="md:col-span-2">
                            <label :for="`srv-url-${index}`" class="setting-label-inline">Server URL</label>
                            <input type="text" :id="`srv-url-${index}`" :value="server.url" @input="updateServer(index, 'url', $event.target.value)" class="input-field-sm w-full" placeholder="http://localhost:port">
                         </div>
                         <!-- API Key -->
                         <div>
                             <label :for="`srv-key-${index}`" class="setting-label-inline">API Key (Optional)</label>
                            <input type="password" :id="`srv-key-${index}`" :value="server.key" @input="updateServer(index, 'key', $event.target.value)" class="input-field-sm w-full" placeholder="API Key if needed">
                         </div>
                        <!-- Start at Startup -->
                        <div class="flex items-end pb-1">
                             <div class="flex items-center space-x-2">
                                <ToggleSwitch :id="`srv-startup-${index}`" :checked="server.start_at_startup" @update:checked="updateServer(index, 'start_at_startup', $event)" />
                                <label :for="`srv-startup-${index}`" class="text-sm font-medium text-gray-700 dark:text-gray-300 cursor-pointer">Start at Startup</label>
                             </div>
                        </div>
                         <!-- Input Folder -->
                        <div>
                            <label :for="`srv-input-${index}`" class="setting-label-inline">Input Folder Path</label>
                            <div class="flex">
                                <input type="text" :id="`srv-input-${index}`" :value="server.input_path" @input="updateServer(index, 'input_path', $event.target.value)" class="input-field-sm w-full rounded-r-none" placeholder="Path to watch for new files">
                                <button @click="selectLightragFolder(index, 'input')" class="button-secondary-sm rounded-l-none flex-shrink-0" title="Select Input Folder"><i data-feather="folder" class="w-4 h-4"></i></button>
                            </div>
                         </div>
                         <!-- Working Folder -->
                         <div>
                            <label :for="`srv-work-${index}`" class="setting-label-inline">Working Folder Path</label>
                            <div class="flex">
                                <input type="text" :id="`srv-work-${index}`" :value="server.working_path" @input="updateServer(index, 'working_path', $event.target.value)" class="input-field-sm w-full rounded-r-none" placeholder="Path for database files">
                                <button @click="selectLightragFolder(index, 'output')" class="button-secondary-sm rounded-l-none flex-shrink-0" title="Select Working Folder"><i data-feather="folder" class="w-4 h-4"></i></button>
                            </div>
                         </div>
                    </div>

                     <!-- Server Actions & Status -->
                    <div class="flex flex-wrap items-center justify-between gap-2 pt-3 border-t border-gray-300 dark:border-gray-600">
                        <div class="flex items-center gap-2">
                             <span :class="['w-3 h-3 rounded-full', serverStatuses[index]?.dotClass || 'bg-gray-400']" :title="serverStatuses[index]?.title || 'Unknown'"></span>
                             <span class="text-xs font-medium text-gray-600 dark:text-gray-400">{{ serverStatuses[index]?.text || 'Status Unknown' }}</span>
                             <button @click="checkServerHealth(index)" class="button-secondary-sm p-1" title="Check Server Status" :disabled="serverStatuses[index]?.loading">
                                <i data-feather="refresh-cw" :class="['w-4 h-4', serverStatuses[index]?.loading ? 'animate-spin' : '']"></i>
                             </button>
                        </div>

                        <div class="flex flex-wrap gap-2">
                            <button @click="startRagServer(index)" class="button-success-sm" title="Start this RAG server instance">
                                <i data-feather="play" class="w-4 h-4 mr-1"></i> Start Server
                             </button>
                             <button v-if="server.type === 'lightrag' && serverStatuses[index]?.status === 'healthy'" @click="showLightRagWebUI(index)" class="button-primary-sm" title="Open LightRAG Web UI">
                                 <i data-feather="external-link" class="w-4 h-4 mr-1"></i> Show WebUI
                             </button>
                         </div>
                    </div>

                    <!-- Status Details (Example for LightRAG) -->
                     <div v-if="server.type === 'lightrag' && serverStatuses[index] && serverStatuses[index].status === 'healthy' && serverStatuses[index].details" class="text-xs text-gray-500 dark:text-gray-400 space-y-1 pt-2 border-t border-dashed border-gray-300 dark:border-gray-600 mt-2">
                         <div><b>Indexed Files:</b> {{ serverStatuses[index].details.indexed_files_count ?? 'N/A' }}</div>
                         <div><b>Model:</b> {{ serverStatuses[index].details.configuration?.llm_model || 'N/A' }}</div>
                         <div><b>Embedding:</b> {{ serverStatuses[index].details.configuration?.embedding_model || 'N/A' }}</div>
                         <!-- Add more details as needed -->
                     </div>
                </div>
            </div>

            <!-- Add New Server Button -->
             <div class="pt-4">
                <button @click="addDatabaseService" class="button-primary w-full md:w-auto">
                    <i data-feather="plus-circle" class="w-5 h-5 mr-2"></i> Add New RAG Server
                </button>
            </div>
        </section>

        <!-- LollmsVectordb General Configuration -->
        <section class="space-y-4 p-4 border border-gray-200 dark:border-gray-600 rounded-lg">
             <h3 class="text-lg font-medium text-gray-700 dark:text-gray-300 mb-3">LoLLMs VectorDB Settings</h3>

             <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                 <!-- RAG Vectorizer -->
                 <div>
                    <label for="rag_vectorizer" class="setting-label-inline">Vectorizer Engine</label>
                    <select id="rag_vectorizer" required :value="config.rag_vectorizer" @change="updateValue('rag_vectorizer', $event.target.value)" class="input-field-sm w-full">
                        <option value="semantic">Sentence Transformer (Recommended)</option>
                        <option value="tfidf">TF-IDF (Fast, Less Accurate)</option>
                        <option value="openai">OpenAI Ada</option>
                        <option value="ollama">Ollama Embedding</option>
                    </select>
                 </div>

                <!-- Execute Remote Code (for custom vectorizers maybe?) -->
                <div class="flex items-end pb-1">
                    <div class="flex items-center space-x-2">
                        <ToggleSwitch id="rag_vectorizer_execute_remote_code" :checked="config.rag_vectorizer_execute_remote_code" @update:checked="updateBoolean('rag_vectorizer_execute_remote_code', $event)" />
                        <label for="rag_vectorizer_execute_remote_code" class="text-sm font-medium text-gray-700 dark:text-gray-300 cursor-pointer">Allow Remote Code Execution</label>
                         <i data-feather="alert-triangle" class="w-4 h-4 text-red-500 ml-1" title="Security Risk: Only enable if using a trusted custom vectorizer source."></i>
                    </div>
                </div>

                <!-- RAG Vectorizer Model -->
                <div class="md:col-span-2">
                     <label for="rag_vectorizer_model" class="setting-label-inline">Vectorizer Model</label>
                     <select
                        id="rag_vectorizer_model"
                        :value="config.rag_vectorizer_model"
                        @change="updateValue('rag_vectorizer_model', $event.target.value)"
                        class="input-field-sm w-full mb-1"
                        :disabled="config.rag_vectorizer === 'tfidf'"
                    >
                         <!-- Options dynamically loaded or predefined -->
                          <option v-if="config.rag_vectorizer === 'tfidf'" disabled value="">N/A for TF-IDF</option>
                         <!-- Semantic Models -->
                         <optgroup v-if="config.rag_vectorizer === 'semantic'" label="Sentence Transformer Models">
                            <option value="BAAI/bge-m3">BAAI/bge-m3</option>
                            <option value="nvidia/NV-Embed-v2">nvidia/NV-Embed-v2</option>
                            <option value="sentence-transformers/all-MiniLM-L6-v2">all-MiniLM-L6-v2</option>
                            <option value="sentence-transformers/all-mpnet-base-v2">all-mpnet-base-v2</option>
                            <!-- Add more or fetch dynamically -->
                        </optgroup>
                        <!-- OpenAI Models -->
                        <optgroup v-if="config.rag_vectorizer === 'openai'" label="OpenAI Models">
                             <option value="text-embedding-3-large">text-embedding-3-large</option>
                             <option value="text-embedding-3-small">text-embedding-3-small</option>
                            <option value="text-embedding-ada-002">text-embedding-ada-002 (Legacy)</option>
                        </optgroup>
                         <!-- Ollama Models -->
                         <optgroup v-if="config.rag_vectorizer === 'ollama'" label="Ollama Embeddings">
                            <option value="mxbai-embed-large">mxbai-embed-large</option>
                            <option value="nomic-embed-text">nomic-embed-text</option>
                             <option value="all-minilm">all-minilm</option>
                             <option value="snowflake-arctic-embed">snowflake-arctic-embed</option>
                             <!-- Recommend users pull these via Ollama CLI -->
                        </optgroup>
                         <!-- Allow custom entry if needed -->
                     </select>
                     <!-- Custom model input (optional, shown if needed) -->
                    <input
                        type="text"
                        :value="config.rag_vectorizer_model"
                        @input="updateValue('rag_vectorizer_model', $event.target.value)"
                        class="input-field-sm w-full"
                        placeholder="Or enter custom model name/path"
                        :disabled="config.rag_vectorizer === 'tfidf'"
                    >
                </div>

                 <!-- RAG Service URL (Ollama/OpenAI) -->
                 <div v-if="config.rag_vectorizer === 'ollama' || config.rag_vectorizer === 'openai'" class="md:col-span-2">
                    <label for="rag_service_url" class="setting-label-inline">
                        {{ config.rag_vectorizer === 'ollama' ? 'Ollama Server URL' : 'OpenAI API Base URL' }}
                    </label>
                    <input
                        type="text"
                        id="rag_service_url"
                        :value="config.rag_service_url"
                        @input="updateValue('rag_service_url', $event.target.value)"
                        class="input-field-sm w-full"
                        :placeholder="config.rag_vectorizer === 'ollama' ? 'http://localhost:11434' : 'https://api.openai.com/v1'"
                    >
                 </div>
             </div>

            <!-- Chunk Size -->
            <div class="setting-item">
                <label for="rag_chunk_size" class="setting-label">Chunk Size</label>
                <div class="flex-1 flex items-center gap-4">
                    <input id="rag_chunk_size-range" :value="config.rag_chunk_size" @input="updateValue('rag_chunk_size', parseInt($event.target.value))" type="range" min="100" max="2000" step="50" class="range-input">
                    <input id="rag_chunk_size-number" :value="config.rag_chunk_size" @input="updateValue('rag_chunk_size', parseInt($event.target.value))" type="number" min="100" max="2000" step="50" class="input-field-sm w-24 text-center">
                </div>
            </div>

             <!-- Overlap Size -->
            <div class="setting-item">
                <label for="rag_overlap_size" class="setting-label">Overlap Size</label>
                 <div class="flex-1 flex items-center gap-4">
                    <input id="rag_overlap_size-range" :value="config.rag_overlap_size" @input="updateValue('rag_overlap_size', parseInt($event.target.value))" type="range" min="0" max="500" step="10" class="range-input">
                    <input id="rag_overlap_size-number" :value="config.rag_overlap_size" @input="updateValue('rag_overlap_size', parseInt($event.target.value))" type="number" min="0" max="500" step="10" class="input-field-sm w-24 text-center">
                </div>
            </div>

             <!-- Clean Chunks Toggle -->
            <div class="toggle-item !justify-start gap-4">
                 <ToggleSwitch id="rag_clean_chunks" :checked="config.rag_clean_chunks" @update:checked="updateBoolean('rag_clean_chunks', $event)" />
                <label for="rag_clean_chunks" class="toggle-label !flex-none">
                    Clean Chunks
                     <span class="toggle-description">Attempt to remove redundant whitespace and formatting from text chunks before vectorization.</span>
                </label>
            </div>

        </section>

         <!-- Data Vectorization Query Settings -->
        <section class="space-y-4 p-4 border border-gray-200 dark:border-gray-600 rounded-lg">
            <h3 class="text-lg font-medium text-gray-700 dark:text-gray-300 mb-3">RAG Query Settings</h3>

            <!-- Reformulate Prompt -->
             <div class="toggle-item">
                <label for="rag_build_keys_words" class="toggle-label">
                    Reformulate Query with Keywords
                     <span class="toggle-description">Let the AI extract keywords from your prompt to potentially improve database search relevance.</span>
                </label>
                <ToggleSwitch id="rag_build_keys_words" :checked="config.rag_build_keys_words" @update:checked="updateBoolean('rag_build_keys_words', $event)" />
            </div>

            <!-- Put Chunk Info -->
            <div class="toggle-item">
                <label for="rag_put_chunk_informations_into_context" class="toggle-label">
                    Include Chunk Source Info in Context
                     <span class="toggle-description">Prepend retrieved text chunks with source information (e.g., filename) when adding to the LLM context.</span>
                </label>
                <ToggleSwitch id="rag_put_chunk_informations_into_context" :checked="config.rag_put_chunk_informations_into_context" @update:checked="updateBoolean('rag_put_chunk_informations_into_context', $event)" />
            </div>

             <!-- Save DB -->
            <div class="toggle-item">
                <label for="data_vectorization_save_db" class="toggle-label">
                    Persist Vector Database
                     <span class="toggle-description">Save the vectorized data to disk. If disabled, the database is in-memory only and lost on restart. (Applies mainly to LoLLMs VectorDB).</span>
                </label>
                 <ToggleSwitch id="data_vectorization_save_db" :checked="config.data_vectorization_save_db" @update:checked="updateBoolean('data_vectorization_save_db', $event)" />
            </div>
        </section>

    </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick, defineProps, defineEmits } from 'vue';
import feather from 'feather-icons';
import axios from 'axios';
import ToggleSwitch from '@/components/ToggleSwitch.vue';
import socket from '@/services/websocket.js';


// Props definition
const props = defineProps({
    config: { type: Object, required: true },
    loading: { type: Boolean, default: false },
    api_post_req: { type: Function, required: true },
    api_get_req: { type: Function, required: true },
    show_toast: { type: Function, required: true },
    client_id: { type: String, required: true }
});

// Emits definition
const emit = defineEmits(['update:setting', 'settings-changed']);

// Reactive state for component-specific UI
const fileInputs = ref([]);
const serverStatuses = reactive({});

// --- Methods ---
const updateValue = (key, value) => {
    emit('update:setting', { key, value });
};

const updateBoolean = (key, value) => {
    emit('update:setting', { key: key, value: Boolean(value) });
};

// --- Data Lake Methods ---
const updateDataLake = (index, field, value) => {
    // Construct the correct key path for nested array update
    emit('update:setting', { key: `datalakes[${index}].${field}`, value });
};


const addDataLake = () => {
    const currentDatalakes = props.config.datalakes ? [...props.config.datalakes] : [];
    currentDatalakes.push({
        alias: "New DataLake",
        type: "lollmsvectordb",
        url: "",
        path: "",
        key: "",
        mounted: false
    });
    // Emit the entire updated array
    emit('update:setting', { key: 'datalakes', value: currentDatalakes });
    nextTick(() => feather.replace()); // Ensure icons render for new elements if any
};

const removeDataLake = (index) => {
    // Create a new array excluding the item at the index
    const currentDatalakes = props.config.datalakes.filter((_, i) => i !== index);
    emit('update:setting', { key: 'datalakes', value: currentDatalakes });
};


const vectorizeFolder = async (index) => {
     const lake = props.config.datalakes[index];
     if (!lake || lake.type !== 'lollmsvectordb' || !lake.path) {
         props.show_toast("Please ensure a valid path is set for the LoLLMs VectorDB.", 4, false);
         return;
     }
     props.show_toast(`Starting vectorization for: ${lake.alias}`, 5, true);
     try {
        await props.api_post_req('vectorize_folder', { rag_database: lake });
        // Success feedback might come via websockets or require manual status check
     } catch (error) {
        props.show_toast(`Vectorization failed for ${lake.alias}: ${error.message}`, 4, false);
     }
 };

 const selectLollmsVectordbFolder = async (index) => {
     try {
         const listener = (infos) => {
             if (infos && infos.path && infos.datalake_name) {
                 // Use updateDataLake for consistency
                 updateDataLake(index, 'path', infos.path);
                 updateDataLake(index, 'alias', infos.datalake_name);
                 props.show_toast(`Folder selected for Data Lake: ${infos.path}`, 4, true);
             } else {
                 props.show_toast("Folder selection failed or returned invalid data.", 4, false);
             }
             socket.off("lollmsvectordb_datalake_added", listener);
         };
         socket.on("lollmsvectordb_datalake_added", listener);
         await props.api_post_req('select_lollmsvectordb_input_folder');
     } catch (error) {
         props.show_toast(`Failed to initiate folder selection: ${error.message}`, 4, false);
         socket.off("lollmsvectordb_datalake_added");
     }
 };

 const triggerFileInput = (index) => {
     if (fileInputs.value[index]) {
        fileInputs.value[index].click();
     }
 };

 const handleFileUpload = async (event, index) => {
    const files = Array.from(event.target.files);
    const source = props.config.datalakes[index];
     if (!files.length || source.type !== 'lightrag') return;

    props.show_toast(`Uploading ${files.length} file(s) to ${source.alias}...`, files.length * 2, true);

     for (const file of files) {
        const formData = new FormData();
        formData.append('file', file);
         formData.append('client_id', props.client_id);

         const headers = { 'Content-Type': 'multipart/form-data' };
         if (source.key) {
             headers['X-API-Key'] = source.key;
         }

         try {
            const response = await axios.post(`${source.url.replace(/\/+$/, '')}/documents/upload`, formData, { headers });
             if (response.data && (response.status === 200 || response.status === 201)) {
                 props.show_toast(`${file.name} uploaded successfully to ${source.alias}`, 4, true);
            } else {
                 props.show_toast(`Failed to upload ${file.name}: ${response.data?.detail || 'Server error'}`, 4, false);
            }
        } catch (error) {
             console.error(`Error uploading ${file.name}:`, error);
             props.show_toast(`Error uploading ${file.name}: ${error.response?.data?.detail || error.message}`, 4, false);
        }
     }
     event.target.value = null;
 };


// --- Database Server Methods ---
const updateServer = (index, field, value) => {
     emit('update:setting', { key: `rag_local_services[${index}].${field}`, value });
};

const addDatabaseService = () => {
     const currentServers = props.config.rag_local_services ? [...props.config.rag_local_services] : [];
     currentServers.push({
         alias: "New RAG Server",
         type: "lightrag",
         url: "http://localhost:9621/",
         key: "",
         input_path: "",
         working_path: "",
         start_at_startup: false
     });
     emit('update:setting', { key: 'rag_local_services', value: currentServers });
     nextTick(() => feather.replace());
};

const removeDatabaseService = (index) => {
     const currentServers = props.config.rag_local_services.filter((_, i) => i !== index);
     emit('update:setting', { key: 'rag_local_services', value: currentServers });
 };

const startRagServer = async (index) => {
     const server = props.config.rag_local_services[index];
     props.show_toast(`Attempting to start server: ${server.alias}...`, 4, true);
     try {
        const response = await props.api_post_req('start_rag_server', { server_index: index });
        if (response.status) {
             props.show_toast(`Start command sent for ${server.alias}. Check status shortly.`, 4, true);
             setTimeout(() => checkServerHealth(index), 5000);
         } else {
            props.show_toast(`Failed to send start command for ${server.alias}: ${response.error || 'Unknown error'}`, 4, false);
         }
     } catch (error) {
        props.show_toast(`Error starting server ${server.alias}: ${error.message}`, 4, false);
     }
 };

 const checkServerHealth = async (index) => {
     const server = props.config.rag_local_services[index];
     if (!server || server.type !== 'lightrag') {
        serverStatuses[index] = { status: 'unknown', loading: false, details: null, dotClass: 'bg-gray-400', title: 'Unsupported', text: 'Unsupported Type' };
        return;
     }

    serverStatuses[index] = { status: 'loading', loading: true, details: null, dotClass: 'bg-yellow-400 animate-pulse', title: 'Checking...', text: 'Checking...' };

     try {
        const url = `${server.url.replace(/\/+$/, '')}/health`;
         const headers = {};
         if (server.key) headers['X-API-Key'] = server.key;
         const response = await fetch(url, { headers });
         if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
         const data = await response.json();
         serverStatuses[index] = { status: 'healthy', loading: false, details: data, dotClass: 'bg-green-500', title: 'Healthy', text: 'Healthy' };
         props.show_toast(`${server.alias} is healthy.`, 3, true);
     } catch (error) {
        console.error(`Health check failed for ${server.alias}:`, error);
        serverStatuses[index] = { status: 'unhealthy', loading: false, details: null, dotClass: 'bg-red-500', title: 'Unhealthy', text: 'Unhealthy' };
        props.show_toast(`${server.alias} health check failed: ${error.message}`, 4, false);
     }
 };

const showLightRagWebUI = (index) => {
     const server = props.config.rag_local_services[index];
     if (server && server.type === 'lightrag' && server.url) {
         const webuiUrl = `${server.url.replace(/\/+$/, '')}/webui`;
         window.open(webuiUrl, '_blank');
     } else {
         props.show_toast("Cannot open WebUI. Invalid server configuration.", 4, false);
     }
 };

 const selectLightragFolder = async (index, folderType) => {
    const endpoint = folderType === 'input' ? 'select_lightrag_input_folder' : 'select_lightrag_output_folder';
    const socketEvent = folderType === 'input' ? 'lightrag_input_folder_added' : 'lightrag_output_folder_added';
    const settingKey = folderType === 'input' ? 'input_path' : 'working_path';

    try {
        const listener = (infos) => {
            if (infos && infos.path) {
                updateServer(index, settingKey, infos.path);
                props.show_toast(`${folderType.charAt(0).toUpperCase() + folderType.slice(1)} folder selected: ${infos.path}`, 4, true);
            } else {
                props.show_toast(`Folder selection failed for ${folderType}.`, 4, false);
            }
             socket.off(socketEvent, listener);
        };
         socket.on(socketEvent, listener);
        await props.api_post_req(endpoint, { server_index: index });
     } catch (error) {
        props.show_toast(`Failed to initiate ${folderType} folder selection: ${error.message}`, 4, false);
         socket.off(socketEvent);
     }
 };


// Lifecycle Hooks
onMounted(() => {
    nextTick(() => {
        feather.replace();
    });
    // Initial health check for servers
    if (props.config.rag_local_services) {
         props.config.rag_local_services.forEach((_, index) => checkServerHealth(index));
     }
});

onUpdated(() => {
    nextTick(() => {
        feather.replace();
    });
});

</script>

<!-- Corrected Style Section -->
<style scoped>
.setting-item {
    @apply flex flex-col md:flex-row md:items-center gap-2 md:gap-4 py-2;
}
.setting-label {
    @apply block text-sm font-medium text-gray-700 dark:text-gray-300 w-full md:w-1/3 lg:w-1/4 flex-shrink-0;
}
.setting-label-inline {
    @apply block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1;
}

.input-field {
     /* Standard focus */
     @apply block w-full px-3 py-2 bg-gray-50 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 focus:border-blue-500 dark:focus:ring-offset-gray-800 sm:text-sm disabled:opacity-50;
}
.input-field-sm {
     /* Standard focus */
     @apply block w-full px-2.5 py-1.5 text-sm bg-gray-50 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 focus:border-blue-500 dark:focus:ring-offset-gray-800 disabled:opacity-50;
}
.range-input {
     /* Standard accent */
    @apply w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-600 accent-blue-600 disabled:opacity-50;
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

/* Shared Button Styles (Tailwind) - Standardized */
.button-base {
    @apply inline-flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-offset-2 dark:focus:ring-offset-gray-800 disabled:opacity-50 transition-colors duration-150;
}
.button-base-sm {
     @apply inline-flex items-center justify-center px-2.5 py-1.5 border border-transparent text-xs font-medium rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-offset-2 dark:focus:ring-offset-gray-800 disabled:opacity-50 transition-colors duration-150;
}

/* Use standard blue for primary, unless 'primary' is defined in config */
.button-primary { @apply button-base text-white bg-blue-600 hover:bg-blue-700 focus:ring-blue-500; }
.button-secondary { @apply button-base text-gray-700 dark:text-gray-200 bg-gray-200 dark:bg-gray-600 hover:bg-gray-300 dark:hover:bg-gray-500 focus:ring-gray-400; }
.button-success { @apply button-base text-white bg-green-600 hover:bg-green-700 focus:ring-green-500; }
.button-danger { @apply button-base text-white bg-red-600 hover:bg-red-700 focus:ring-red-500; }

.button-primary-sm { @apply button-base-sm text-white bg-blue-600 hover:bg-blue-700 focus:ring-blue-500; }
.button-secondary-sm { @apply button-base-sm text-gray-700 dark:text-gray-200 bg-gray-200 dark:bg-gray-600 hover:bg-gray-300 dark:hover:bg-gray-500 focus:ring-gray-400; }
.button-success-sm { @apply button-base-sm text-white bg-green-600 hover:bg-green-700 focus:ring-green-500; }

</style>