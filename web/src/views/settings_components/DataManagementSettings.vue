<template>
    <div class="user-settings-panel space-y-6">
        <!-- Main Title -->
        <h2 class="text-2xl font-semibold text-blue-700 dark:text-blue-200 border-b border-blue-300 dark:border-blue-600 pb-2">
            Data Management
        </h2>

        <!-- Data Lakes Configuration Section -->
        <section class="space-y-4 p-4 border border-blue-300 dark:border-blue-600 rounded-lg bg-blue-50 dark:bg-blue-900/50">
            <h3 class="text-xl font-medium text-blue-600 dark:text-blue-300 mb-2">Data Lakes</h3>
             <p class="text-sm text-blue-500 dark:text-blue-400 mb-4">
                Configure data sources (vector databases) that LoLLMs can query for information retrieval (RAG).
            </p>

            <!-- Data Lakes List -->
            <div class="space-y-4">
                 <div v-if="!$store.state.config.datalakes || $store.state.config.datalakes.length === 0" class="text-center text-blue-500 dark:text-blue-400 py-4">
                    No Data Lakes configured.
                </div>
                <!-- Data Lake Item -->
                <div v-for="(source, index) in $store.state.config.datalakes" :key="`datalake-${index}`"
                    class="p-4 bg-blue-100 dark:bg-blue-800/60 border border-blue-200 dark:border-blue-700 rounded-lg shadow-sm space-y-4 relative group"
                >
                     <!-- Remove Button (Top Right) -->
                     <button
                        @click="removeDataLake(index)"
                        class="absolute top-2 right-2 p-1 rounded-full text-red-500 hover:bg-red-100 dark:hover:bg-red-800 opacity-0 group-hover:opacity-100 transition-opacity duration-200 svg-button"
                        title="Remove Data Lake"
                    >
                        <i data-feather="x-circle" class="w-5 h-5"></i>
                    </button>

                    <!-- Main Controls Grid -->
                     <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <!-- Data Lake Alias -->
                        <div>
                             <label :for="`dl-alias-${index}`" class="label mb-1">Alias</label>
                             <input
                                type="text"
                                :id="`dl-alias-${index}`"
                                :value="source.alias"
                                @input="updateDataLake(index, 'alias', $event.target.value)"
                                class="input input-sm w-full"
                                placeholder="Enter alias (e.g., 'Project Docs')"
                            >
                        </div>

                        <!-- Data Lake Type -->
                         <div>
                            <label :for="`dl-type-${index}`" class="label mb-1">Type</label>
                            <select
                                :id="`dl-type-${index}`"
                                required
                                :value="source.type"
                                @change="updateDataLake(index, 'type', $event.target.value)"
                                class="input input-sm w-full"
                            >
                                <option value="lollmsvectordb">LoLLMs VectorDB</option>
                                <option value="lightrag">LightRAG</option>
                                <option value="elasticsearch">Elasticsearch</option>
                            </select>
                        </div>

                         <!-- Conditional URL/Path Input -->
                        <div class="md:col-span-2">
                             <label :for="`dl-pathurl-${index}`" class="label mb-1">
                                {{ source.type === 'lollmsvectordb' ? 'Database Path' : (source.type === 'lightrag' ? 'LightRAG URL' : 'Elasticsearch URL') }}
                            </label>
                            <input
                                type="text"
                                :id="`dl-pathurl-${index}`"
                                :value="source.type === 'lollmsvectordb' ? source.path : source.url"
                                @input="updateDataLake(index, source.type === 'lollmsvectordb' ? 'path' : 'url', $event.target.value)"
                                class="input input-sm w-full"
                                :placeholder="source.type === 'lollmsvectordb' ? 'Path to database folder' : 'http://host:port/'"
                             >
                        </div>

                         <!-- API Key (conditional) -->
                        <div v-if="source.type === 'lightrag' || source.type === 'elasticsearch'" class="md:col-span-2">
                             <label :for="`dl-key-${index}`" class="label mb-1">API Key (Optional)</label>
                            <input
                                type="password"
                                :id="`dl-key-${index}`"
                                :value="source.key"
                                @input="updateDataLake(index, 'key', $event.target.value)"
                                class="input input-sm w-full"
                                placeholder="Enter API key if required"
                            >
                        </div>
                    </div>

                    <!-- Actions Row -->
                    <div class="flex flex-wrap items-center justify-between gap-2 pt-3 border-t border-blue-300 dark:border-blue-600">
                         <!-- Mounted Toggle -->
                        <div class="flex items-center space-x-2">
                            <ToggleSwitch
                                :id="`dl-mounted-${index}`"
                                :checked="source.mounted"
                                @update:checked="updateDataLake(index, 'mounted', $event)"
                            />
                            <label :for="`dl-mounted-${index}`" class="label !mb-0 text-sm cursor-pointer">
                                Mounted
                            </label>
                        </div>


                         <!-- Type Specific Actions -->
                        <div class="flex flex-wrap gap-2">
                             <!-- Lollms VectorDB Actions -->
                            <template v-if="source.type === 'lollmsvectordb'">
                                <button @click="vectorizeFolder(index)" class="btn btn-secondary btn-sm" title="Vectorize or re-vectorize the selected folder">
                                     <i data-feather="refresh-cw" class="w-4 h-4 mr-1"></i> Vectorize
                                 </button>
                                <button @click="selectLollmsVectordbFolder(index)" class="btn btn-primary btn-sm" title="Select folder containing documents to vectorize">
                                    <i data-feather="folder-plus" class="w-4 h-4 mr-1"></i> Select Folder
                                </button>
                            </template>

                            <!-- LightRAG Actions -->
                             <template v-if="source.type === 'lightrag'">
                                 <button @click="triggerFileInput(index)" class="btn btn-success btn-sm" title="Upload supported files (.txt, .md, .pdf, .docx, .pptx, .xlsx)">
                                     <i data-feather="upload" class="w-4 h-4 mr-1"></i> Upload Files
                                </button>
                                <input type="file" :ref="el => { if (el) fileInputs[index] = el }" @change="handleFileUpload($event, index)"
                                       accept=".txt,.md,.pdf,.docx,.pptx,.xlsx" class="hidden" multiple />
                             </template>
                         </div>
                    </div>
                </div>
            </div>

             <!-- Add New Data Lake Button -->
            <div class="pt-4">
                <button @click="addDataLake" class="btn btn-primary w-full md:w-auto">
                    <i data-feather="plus-circle" class="w-5 h-5 mr-2"></i> Add New Data Lake
                </button>
            </div>
        </section>

        <!-- Database Servers Configuration Section -->
        <section class="space-y-4 p-4 border border-blue-300 dark:border-blue-600 rounded-lg bg-blue-50 dark:bg-blue-900/50">
            <h3 class="text-xl font-medium text-blue-600 dark:text-blue-300 mb-2">Self-Hosted RAG Servers</h3>
             <p class="text-sm text-blue-500 dark:text-blue-400 mb-4">
                 Configure and manage local RAG server instances (like LightRAG) running on your machine.
            </p>
             <!-- Servers List -->
            <div class="space-y-4">
                 <div v-if="!$store.state.config.rag_local_services || $store.state.config.rag_local_services.length === 0" class="text-center text-blue-500 dark:text-blue-400 py-4">
                    No RAG Servers configured.
                </div>
                <!-- Server Item -->
                <div v-for="(server, index) in $store.state.config.rag_local_services" :key="`server-${index}`"
                    class="p-4 bg-blue-100 dark:bg-blue-800/60 border border-blue-200 dark:border-blue-700 rounded-lg shadow-sm space-y-4 relative group"
                >
                     <!-- Remove Button -->
                     <button
                        @click="removeDatabaseService(index)"
                        class="absolute top-2 right-2 p-1 rounded-full text-red-500 hover:bg-red-100 dark:hover:bg-red-800 opacity-0 group-hover:opacity-100 transition-opacity duration-200 svg-button"
                        title="Remove Server"
                    >
                        <i data-feather="x-circle" class="w-5 h-5"></i>
                    </button>

                    <!-- Server Controls Grid -->
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                         <!-- Server Alias -->
                         <div>
                            <label :for="`srv-alias-${index}`" class="label mb-1">Alias</label>
                            <input type="text" :id="`srv-alias-${index}`" :value="server.alias" @input="updateServer(index, 'alias', $event.target.value)" class="input input-sm w-full" placeholder="Server Alias">
                         </div>
                         <!-- Server Type -->
                         <div>
                            <label :for="`srv-type-${index}`" class="label mb-1">Type</label>
                             <select :id="`srv-type-${index}`" required :value="server.type" @change="updateServer(index, 'type', $event.target.value)" class="input input-sm w-full">
                                <option value="lightrag">LightRAG</option>
                                <!-- <option value="elasticsearch">Elasticsearch</option> -->
                             </select>
                         </div>
                         <!-- Server URL -->
                         <div class="md:col-span-2">
                            <label :for="`srv-url-${index}`" class="label mb-1">Server URL</label>
                            <input type="text" :id="`srv-url-${index}`" :value="server.url" @input="updateServer(index, 'url', $event.target.value)" class="input input-sm w-full" placeholder="http://localhost:port">
                         </div>
                         <!-- API Key -->
                         <div>
                             <label :for="`srv-key-${index}`" class="label mb-1">API Key (Optional)</label>
                            <input type="password" :id="`srv-key-${index}`" :value="server.key" @input="updateServer(index, 'key', $event.target.value)" class="input input-sm w-full" placeholder="API Key if needed">
                         </div>
                        <!-- Start at Startup -->
                        <div class="flex items-end pb-1">
                             <div class="flex items-center space-x-2">
                                <ToggleSwitch :id="`srv-startup-${index}`" :checked="server.start_at_startup" @update:checked="updateServer(index, 'start_at_startup', $event)" />
                                <label :for="`srv-startup-${index}`" class="label !mb-0 text-sm cursor-pointer">Start at Startup</label>
                             </div>
                        </div>
                         <!-- Input Folder -->
                        <div>
                            <label :for="`srv-input-${index}`" class="label mb-1">Input Folder Path</label>
                            <div class="flex">
                                <input type="text" :id="`srv-input-${index}`" :value="server.input_path" @input="updateServer(index, 'input_path', $event.target.value)" class="input input-sm w-full rounded-r-none" placeholder="Path to watch for new files">
                                <button @click="selectLightragFolder(index, 'input')" class="btn btn-secondary btn-sm rounded-l-none flex-shrink-0" title="Select Input Folder"><i data-feather="folder" class="w-4 h-4"></i></button>
                            </div>
                         </div>
                         <!-- Working Folder -->
                         <div>
                            <label :for="`srv-work-${index}`" class="label mb-1">Working Folder Path</label>
                            <div class="flex">
                                <input type="text" :id="`srv-work-${index}`" :value="server.working_path" @input="updateServer(index, 'working_path', $event.target.value)" class="input input-sm w-full rounded-r-none" placeholder="Path for database files">
                                <button @click="selectLightragFolder(index, 'output')" class="btn btn-secondary btn-sm rounded-l-none flex-shrink-0" title="Select Working Folder"><i data-feather="folder" class="w-4 h-4"></i></button>
                            </div>
                         </div>
                    </div>

                     <!-- Server Actions & Status -->
                    <div class="flex flex-wrap items-center justify-between gap-2 pt-3 border-t border-blue-300 dark:border-blue-600">
                        <div class="flex items-center gap-2">
                             <span :class="['w-3 h-3 rounded-full', serverStatuses[index]?.dotClass || 'bg-status-unknown']" :title="serverStatuses[index]?.title || 'Unknown'"></span>
                             <span class="text-xs font-medium text-blue-600 dark:text-blue-400">{{ serverStatuses[index]?.text || 'Status Unknown' }}</span>
                             <button @click="checkServerHealth(index)" class="btn btn-secondary btn-sm !p-1" title="Check Server Status" :disabled="serverStatuses[index]?.loading">
                                <i data-feather="refresh-cw" :class="['w-4 h-4', serverStatuses[index]?.loading ? 'animate-spin' : '']"></i>
                             </button>
                        </div>

                        <div class="flex flex-wrap gap-2">
                            <button @click="startRagServer(index)" class="btn btn-success btn-sm" title="Start this RAG server instance">
                                <i data-feather="play" class="w-4 h-4 mr-1"></i> Start Server
                             </button>
                             <button v-if="server.type === 'lightrag' && serverStatuses[index]?.status === 'healthy'" @click="showLightRagWebUI(index)" class="btn btn-primary btn-sm" title="Open LightRAG Web UI">
                                 <i data-feather="external-link" class="w-4 h-4 mr-1"></i> Show WebUI
                             </button>
                         </div>
                    </div>

                    <!-- Status Details (Example for LightRAG) -->
                     <div v-if="server.type === 'lightrag' && serverStatuses[index] && serverStatuses[index].status === 'healthy' && serverStatuses[index].details" class="text-xs text-blue-500 dark:text-blue-400 space-y-1 pt-2 border-t border-dashed border-blue-300 dark:border-blue-600 mt-2">
                         <div><b class="text-blue-600 dark:text-blue-300">Indexed Files:</b> {{ serverStatuses[index].details.indexed_files_count ?? 'N/A' }}</div>
                         <div><b class="text-blue-600 dark:text-blue-300">Model:</b> {{ serverStatuses[index].details.configuration?.llm_model || 'N/A' }}</div>
                         <div><b class="text-blue-600 dark:text-blue-300">Embedding:</b> {{ serverStatuses[index].details.configuration?.embedding_model || 'N/A' }}</div>
                     </div>
                </div>
            </div>

            <!-- Add New Server Button -->
             <div class="pt-4">
                <button @click="addDatabaseService" class="btn btn-primary w-full md:w-auto">
                    <i data-feather="plus-circle" class="w-5 h-5 mr-2"></i> Add New RAG Server
                </button>
            </div>
        </section>

        <!-- LollmsVectordb General Configuration Section -->
        <section class="space-y-4 p-4 border border-blue-300 dark:border-blue-600 rounded-lg bg-blue-50 dark:bg-blue-900/50">
             <h3 class="text-xl font-medium text-blue-600 dark:text-blue-300 mb-3">LoLLMs VectorDB Settings</h3>

             <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                 <!-- RAG Vectorizer -->
                 <div>
                    <label for="rag_vectorizer" class="label mb-1">Vectorizer Engine</label>
                    <select id="rag_vectorizer" required :value="$store.state.config.rag_vectorizer" @change="$store.state.config.rag_vectorizer = $event.target.value" class="input input-sm w-full">
                        <option value="semantic">Sentence Transformer (Recommended)</option>
                        <option value="tfidf">TF-IDF (Fast, Less Accurate)</option>
                        <option value="openai">OpenAI Ada</option>
                        <option value="ollama">Ollama Embedding</option>
                    </select>
                 </div>

                <!-- Execute Remote Code -->
                <div class="flex items-end pb-1">
                    <div class="flex items-center space-x-2">
                        <ToggleSwitch id="rag_vectorizer_execute_remote_code" :checked="$store.state.config.rag_vectorizer_execute_remote_code" @update:checked="$store.state.config.rag_vectorizer_execute_remote_code = Boolean($event)" />
                        <label for="rag_vectorizer_execute_remote_code" class="label !mb-0 text-sm cursor-pointer">Allow Remote Code Execution</label>
                         <i data-feather="alert-triangle" class="w-4 h-4 text-red-500 dark:text-red-400 ml-1" title="Security Risk: Only enable if using a trusted custom vectorizer source."></i>
                    </div>
                </div>

                <!-- RAG Vectorizer Model -->
                <div class="md:col-span-2">
                     <label for="rag_vectorizer_model" class="label mb-1">Vectorizer Model</label>
                     <select
                        id="rag_vectorizer_model"
                        :value="$store.state.config.rag_vectorizer_model"
                        @change="$store.state.config.rag_vectorizer_model = $event.target.value"
                        class="input input-sm w-full mb-1"
                        :disabled="$store.state.config.rag_vectorizer === 'tfidf'"
                    >
                         <option v-if="$store.state.config.rag_vectorizer === 'tfidf'" disabled value="">N/A for TF-IDF</option>
                         <optgroup v-if="$store.state.config.rag_vectorizer === 'semantic'" label="Sentence Transformer Models">
                            <option value="BAAI/bge-m3">BAAI/bge-m3</option>
                            <option value="nvidia/NV-Embed-v2">nvidia/NV-Embed-v2</option>
                            <option value="sentence-transformers/all-MiniLM-L6-v2">all-MiniLM-L6-v2</option>
                            <option value="sentence-transformers/all-mpnet-base-v2">all-mpnet-base-v2</option>
                        </optgroup>
                        <optgroup v-if="$store.state.config.rag_vectorizer === 'openai'" label="OpenAI Models">
                             <option value="text-embedding-3-large">text-embedding-3-large</option>
                             <option value="text-embedding-3-small">text-embedding-3-small</option>
                            <option value="text-embedding-ada-002">text-embedding-ada-002 (Legacy)</option>
                        </optgroup>
                         <optgroup v-if="$store.state.config.rag_vectorizer === 'ollama'" label="Ollama Embeddings">
                            <option value="mxbai-embed-large">mxbai-embed-large</option>
                            <option value="nomic-embed-text">nomic-embed-text</option>
                             <option value="all-minilm">all-minilm</option>
                             <option value="snowflake-arctic-embed">snowflake-arctic-embed</option>
                        </optgroup>
                     </select>
                    <input
                        type="text"
                        :value="$store.state.config.rag_vectorizer_model"
                        @input="$store.state.config.rag_vectorizer_model = $event.target.value"
                        class="input input-sm w-full"
                        placeholder="Or enter custom model name/path"
                        :disabled="$store.state.config.rag_vectorizer === 'tfidf'"
                    >
                </div>

                 <!-- RAG Service URL (Ollama/OpenAI) -->
                 <div v-if="$store.state.config.rag_vectorizer === 'ollama' || $store.state.config.rag_vectorizer === 'openai'" class="md:col-span-2">
                    <label for="rag_service_url" class="label mb-1">
                        {{ $store.state.config.rag_vectorizer === 'ollama' ? 'Ollama Server URL' : 'OpenAI API Base URL' }}
                    </label>
                    <input
                        type="text"
                        id="rag_service_url"
                        :value="$store.state.config.rag_service_url"
                        @input="$store.state.config.rag_service_url = $event.target.value"
                        class="input input-sm w-full"
                        :placeholder="$store.state.config.rag_vectorizer === 'ollama' ? 'http://localhost:11434' : 'https://api.openai.com/v1'"
                    >
                 </div>
             </div>

            <!-- Chunk Size -->
            <div class="setting-item border-t border-blue-200 dark:border-blue-700 pt-3 mt-3">
                <label for="rag_chunk_size-range" class="setting-label">Chunk Size</label>
                <div class="flex-1 flex items-center gap-4">
                    <input id="rag_chunk_size-range" :value="$store.state.config.rag_chunk_size" @input="$store.state.config.rag_chunk_size = parseInt($event.target.value)" type="range" min="100" max="2000" step="50" class="range-input flex-grow">
                    <input id="rag_chunk_size-number" :value="$store.state.config.rag_chunk_size" @input="$store.state.config.rag_chunk_size = parseInt($event.target.value)" type="number" min="100" max="2000" step="50" class="input input-sm w-24 text-center">
                </div>
            </div>

             <!-- Overlap Size -->
            <div class="setting-item">
                <label for="rag_overlap_size-range" class="setting-label">Overlap Size</label>
                 <div class="flex-1 flex items-center gap-4">
                    <input id="rag_overlap_size-range" :value="$store.state.config.rag_overlap_size" @input="$store.state.config.rag_overlap_size = parseInt($event.target.value)" type="range" min="0" max="500" step="10" class="range-input flex-grow">
                    <input id="rag_overlap_size-number" :value="$store.state.config.rag_overlap_size" @input="$store.state.config.rag_overlap_size = parseInt($event.target.value)" type="number" min="0" max="500" step="10" class="input input-sm w-24 text-center">
                </div>
            </div>

             <!-- Clean Chunks Toggle -->
            <div class="toggle-item !justify-start gap-4 !border-t-0 !pt-0 !mt-0">
                 <ToggleSwitch id="rag_clean_chunks" :checked="$store.state.config.rag_clean_chunks" @update:checked="$store.state.config.rag_clean_chunks = Boolean($event)" />
                <label for="rag_clean_chunks" class="toggle-label !flex-none">
                    Clean Chunks
                     <span class="toggle-description">Attempt to remove redundant whitespace and formatting from text chunks before vectorization.</span>
                </label>
            </div>

        </section>

         <!-- Data Vectorization Query Settings Section -->
        <section class="space-y-4 p-4 border border-blue-300 dark:border-blue-600 rounded-lg bg-blue-50 dark:bg-blue-900/50">
            <h3 class="text-xl font-medium text-blue-600 dark:text-blue-300 mb-3">RAG Query Settings</h3>

            <!-- Reformulate Prompt -->
             <div class="toggle-item">
                <label for="rag_build_keys_words" class="toggle-label">
                    Reformulate Query with Keywords
                     <span class="toggle-description">Let the AI extract keywords from your prompt to potentially improve database search relevance.</span>
                </label>
                <ToggleSwitch id="rag_build_keys_words" :checked="$store.state.config.rag_build_keys_words" @update:checked="$store.state.config.rag_build_keys_words = Boolean($event)" />
            </div>

            <!-- Put Chunk Info -->
            <div class="toggle-item">
                <label for="rag_put_chunk_informations_into_context" class="toggle-label">
                    Include Chunk Source Info in Context
                     <span class="toggle-description">Prepend retrieved text chunks with source information (e.g., filename) when adding to the LLM context.</span>
                </label>
                <ToggleSwitch id="rag_put_chunk_informations_into_context" :checked="$store.state.config.rag_put_chunk_informations_into_context" @update:checked="$store.state.config.rag_put_chunk_informations_into_context = Boolean($event)" />
            </div>

             <!-- Save DB -->
            <div class="toggle-item">
                <label for="data_vectorization_save_db" class="toggle-label">
                    Persist Vector Database
                     <span class="toggle-description">Save the vectorized data to disk. If disabled, the database is in-memory only and lost on restart. (Applies mainly to LoLLMs VectorDB).</span>
                </label>
                 <ToggleSwitch id="data_vectorization_save_db" :checked="$store.state.config.data_vectorization_save_db" @update:checked="$store.state.config.data_vectorization_save_db = Boolean($event)" />
            </div>
        </section>

    </div>
</template>

<script>
import { reactive, nextTick } from 'vue'; // Import reactive and nextTick
import feather from 'feather-icons';
import axios from 'axios';
import ToggleSwitch from '@/components/ToggleSwitch.vue';
import socket from '@/services/websocket.js';

export default {
    name: 'DataManagementSettings',
    components: {
        ToggleSwitch
    },
    props: {
        loading: { type: Boolean, default: false },
        api_post_req: { type: Function, required: true },
        api_get_req: { type: Function, required: true },
        show_toast: { type: Function, required: true },
        client_id: { type: String, required: true }
    },
    emits: ['settings-changed'], // Use standard emits option
    data() {
        return {
            fileInputs: [], // Array to hold file input DOM elements
            serverStatuses: reactive({}) // Use reactive for nested reactivity
        };
    },
    methods: {
        // --- Data Lake Methods ---
        updateDataLake(index, field, value) {
            // Construct the correct key path for nested array update
            // Note: Vue 3's reactivity handles deep updates, but emitting the path is good for clarity/tracking
            const currentDatalakes = JSON.parse(JSON.stringify(this.$store.state.config.datalakes || []));
            if (currentDatalakes[index]) {
                currentDatalakes[index][field] = value;
                // Handle type change potentially swapping between path/url
                if(field === 'type') {
                    if(value === 'lollmsvectordb') {
                        currentDatalakes[index].url = ""; // Clear URL if switching to path-based
                    } else {
                        currentDatalakes[index].path = ""; // Clear path if switching to URL-based
                    }
                }
                this.$store.state.config.datalakes = currentDatalakes
            } else {
                 console.error("Attempted to update non-existent datalake at index:", index);
            }
        },

        addDataLake() {
            const currentDatalakes = this.$store.state.config.datalakes ? [...this.$store.state.config.datalakes] : [];
            currentDatalakes.push({
                alias: "New DataLake",
                type: "lollmsvectordb",
                url: "",
                path: "",
                key: "",
                mounted: false
            });
            // Emit the entire updated array
            this.$store.state.config.datalakes = currentDatalakes
            nextTick(() => feather.replace()); // Use Vue's nextTick
        },

        removeDataLake(index) {
            // Create a new array excluding the item at the index
            const currentDatalakes = this.$store.state.config.datalakes.filter((_, i) => i !== index);
            this.$store.state.config.datalakes = currentDatalakes
        },

        async vectorizeFolder(index) {
             const lake = this.$store.state.config.datalakes[index];
             if (!lake || lake.type !== 'lollmsvectordb' || !lake.path) {
                 this.show_toast("Please ensure a valid path is set for the LoLLMs VectorDB.", 4, false);
                 return;
             }
             this.show_toast(`Starting vectorization for: ${lake.alias}`, 5, true);
             try {
                await this.api_post_req('vectorize_folder', { rag_database: lake });
                // Success feedback might come via websockets or require manual status check
             } catch (error) {
                this.show_toast(`Vectorization failed for ${lake.alias}: ${error.message || error}`, 4, false);
             }
        },

         async selectLollmsVectordbFolder(index) {
             try {
                 // Use arrow function to preserve `this` context
                 const listener = (infos) => {
                     if (infos && infos.path && infos.datalake_name) {
                         // Use updateDataLake for consistency - need to emit the whole array for data() model
                         const currentDatalakes = JSON.parse(JSON.stringify(this.$store.state.config.datalakes || []));
                         if(currentDatalakes[index]){
                            currentDatalakes[index].path = infos.path;
                            currentDatalakes[index].alias = infos.datalake_name;
                            this.$store.state.config.datalakes = currentDatalakes
                            this.show_toast(`Folder selected for Data Lake: ${infos.path}`, 4, true);
                         }
                     } else {
                         this.show_toast("Folder selection failed or returned invalid data.", 4, false);
                     }
                     socket.off("lollmsvectordb_datalake_added", listener);
                 };
                 socket.on("lollmsvectordb_datalake_added", listener);
                 await this.api_post_req('select_lollmsvectordb_input_folder');
             } catch (error) {
                 this.show_toast(`Failed to initiate folder selection: ${error.message || error}`, 4, false);
                 socket.off("lollmsvectordb_datalake_added"); // Ensure listener is removed on error
             }
        },

        triggerFileInput(index) {
             if (this.fileInputs[index]) {
                this.fileInputs[index].click();
             } else {
                 console.warn("File input ref not found for index:", index);
             }
        },

        async handleFileUpload(event, index) {
            const files = Array.from(event.target.files);
            const source = this.$store.state.config.datalakes[index];
             if (!files.length || source.type !== 'lightrag') return;

            this.show_toast(`Uploading ${files.length} file(s) to ${source.alias}...`, files.length * 2, true);

             for (const file of files) {
                const formData = new FormData();
                formData.append('file', file);
                formData.append('client_id', this.client_id); // Use this.client_id

                const headers = { 'Content-Type': 'multipart/form-data' };
                if (source.key) {
                     headers['X-API-Key'] = source.key;
                }

                try {
                    const response = await axios.post(`${source.url.replace(/\/+$/, '')}/documents/upload`, formData, { headers });
                     if (response.data && (response.status === 200 || response.status === 201)) {
                         this.show_toast(`${file.name} uploaded successfully to ${source.alias}`, 4, true);
                    } else {
                         this.show_toast(`Failed to upload ${file.name}: ${response.data?.detail || 'Server error'}`, 4, false);
                    }
                } catch (error) {
                     console.error(`Error uploading ${file.name}:`, error);
                     this.show_toast(`Error uploading ${file.name}: ${error.response?.data?.detail || error.message || error}`, 4, false);
                }
             }
             // Reset file input value to allow uploading the same file again
             if(event.target) event.target.value = null;
        },

        // --- Database Server Methods ---
        updateServer(index, field, value) {
             // Similar to updateDataLake, emit the whole array or handle specific path update
             const currentServers = JSON.parse(JSON.stringify(this.$store.state.config.rag_local_services || []));
             if (currentServers[index]) {
                 currentServers[index][field] = value;
                 this.$store.state.config.rag_local_services = currentServers
             } else {
                console.error("Attempted to update non-existent server at index:", index);
             }
        },

        addDatabaseService() {
             const currentServers = this.$store.state.config.rag_local_services ? [...this.$store.state.config.rag_local_services] : [];
             currentServers.push({
                 alias: "New RAG Server",
                 type: "lightrag",
                 url: "http://localhost:9621/",
                 key: "",
                 input_path: "",
                 working_path: "",
                 start_at_startup: false
             });
             this.$store.state.config.rag_local_services = currentServers
             nextTick(() => feather.replace()); // Use Vue's nextTick
        },

        removeDatabaseService(index) {
             const currentServers = this.$store.state.config.rag_local_services.filter((_, i) => i !== index);
             this.$store.state.config.rag_local_services = currentServers
        },

        async startRagServer(index) {
             const server = this.$store.state.config.rag_local_services[index];
             this.show_toast(`Attempting to start server: ${server.alias}...`, 4, true);
             try {
                const response = await this.api_post_req('start_rag_server', { server_index: index });
                if (response.status) {
                     this.show_toast(`Start command sent for ${server.alias}. Check status shortly.`, 4, true);
                     // Use setTimeout with `this` context if needed, arrow function preserves it
                     setTimeout(() => this.checkServerHealth(index), 5000);
                 } else {
                    this.show_toast(`Failed to send start command for ${server.alias}: ${response.error || 'Unknown error'}`, 4, false);
                 }
             } catch (error) {
                this.show_toast(`Error starting server ${server.alias}: ${error.message || error}`, 4, false);
             }
        },

        async checkServerHealth(index) {
            // Ensure server exists in config before proceeding
            if (!this.$store.state.config.rag_local_services || !this.$store.state.config.rag_local_services[index]) {
                 console.warn(`Tried to check health for non-existent server index: ${index}`);
                 return;
            }
             const server = this.$store.state.config.rag_local_services[index];
             if (!server || server.type !== 'lightrag') {
                // Use Vue.set or direct assignment for reactive objects in Options API
                this.serverStatuses[index] = { status: 'unknown', loading: false, details: null, dotClass: 'bg-gray-400', title: 'Unsupported', text: 'Unsupported Type' };
                return;
             }

             // Set loading state
            this.serverStatuses[index] = { status: 'loading', loading: true, details: null, dotClass: 'bg-yellow-400 animate-pulse', title: 'Checking...', text: 'Checking...' };

             try {
                const url = `${server.url.replace(/\/+$/, '')}/health`;
                const headers = {};
                if (server.key) headers['X-API-Key'] = server.key;

                // Use fetch API
                const response = await fetch(url, { headers });
                if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
                const data = await response.json();

                // Update status to healthy
                this.serverStatuses[index] = { status: 'healthy', loading: false, details: data, dotClass: 'bg-green-500', title: 'Healthy', text: 'Healthy' };
                this.show_toast(`${server.alias} is healthy.`, 3, true);

             } catch (error) {
                console.error(`Health check failed for ${server.alias}:`, error);
                // Update status to unhealthy
                this.serverStatuses[index] = { status: 'unhealthy', loading: false, details: null, dotClass: 'bg-red-500', title: 'Unhealthy', text: 'Unhealthy' };
                this.show_toast(`${server.alias} health check failed: ${error.message || error}`, 4, false);
             }
        },

        showLightRagWebUI(index) {
             const server = this.$store.state.config.rag_local_services[index];
             if (server && server.type === 'lightrag' && server.url) {
                 const webuiUrl = `${server.url.replace(/\/+$/, '')}/webui`;
                 window.open(webuiUrl, '_blank');
             } else {
                 this.show_toast("Cannot open WebUI. Invalid server configuration.", 4, false);
             }
        },

         async selectLightragFolder(index, folderType) {
            const endpoint = folderType === 'input' ? 'select_lightrag_input_folder' : 'select_lightrag_output_folder';
            const socketEvent = folderType === 'input' ? 'lightrag_input_folder_added' : 'lightrag_output_folder_added';
            const settingKey = folderType === 'input' ? 'input_path' : 'working_path';

            try {
                 // Use arrow function to preserve `this`
                 const listener = (infos) => {
                    if (infos && infos.path) {
                        // Need to update the whole array for data model reactivity
                        const currentServers = JSON.parse(JSON.stringify(this.$store.state.config.rag_local_services || []));
                        if (currentServers[index]) {
                            currentServers[index][settingKey] = infos.path;
                            this.$store.state.config.rag_local_services = currentServers
                            this.show_toast(`${folderType.charAt(0).toUpperCase() + folderType.slice(1)} folder selected: ${infos.path}`, 4, true);
                        }
                    } else {
                         this.show_toast(`Folder selection failed for ${folderType}.`, 4, false);
                    }
                     socket.off(socketEvent, listener); // Remove listener after execution
                 };
                 socket.on(socketEvent, listener);
                 await this.api_post_req(endpoint, { server_index: index });
             } catch (error) {
                 this.show_toast(`Failed to initiate ${folderType} folder selection: ${error.message || error}`, 4, false);
                 // Ensure listener is removed on error
                 socket.off(socketEvent); // Remove potentially dangling listener
             }
        },

        // Helper to refresh icons
        refreshFeatherIcons() {
            nextTick(() => {
                feather.replace();
            });
        }
    },
    mounted() {
        this.refreshFeatherIcons();
        // Initial health check for servers
        if (this.$store.state.config.rag_local_services) {
             this.$store.state.config.rag_local_services.forEach((_, index) => this.checkServerHealth(index));
        }
        // Initialize fileInputs array based on current datalakes
        if(this.$store.state.config.datalakes) {
            this.fileInputs = new Array(this.$store.state.config.datalakes.length).fill(null);
        }
    },
    updated() {
        // Refresh icons whenever the component updates
        this.refreshFeatherIcons();
         // Ensure fileInputs array size matches datalakes list
        if(this.$store.state.config.datalakes && this.fileInputs.length !== this.$store.state.config.datalakes.length) {
            const newLength = this.$store.state.config.datalakes.length;
            const oldLength = this.fileInputs.length;
            if (newLength > oldLength) {
                this.fileInputs.push(...new Array(newLength - oldLength).fill(null));
            } else {
                this.fileInputs.splice(newLength);
            }
        }
    },
    watch: {
        // Watch for changes in config.datalakes length to update fileInputs array size if needed
        'config.datalakes.length'(newLength, oldLength) {
            if (newLength > oldLength) {
                this.fileInputs.push(...new Array(newLength - oldLength).fill(null));
            } else if (newLength < oldLength) {
                 this.fileInputs.splice(newLength);
            }
        }
    }
}
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