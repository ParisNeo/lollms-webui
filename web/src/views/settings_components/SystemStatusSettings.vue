<template>
    <!-- Root container: Applied soft bluish theme panel styling -->
    <div class="user-settings-panel"> <!-- user-settings-panel defined in theme css -->

        <!-- Header Section: Styled with theme colors and border -->
        <div class="flex justify-between items-center border-b border-blue-300 dark:border-blue-600 pb-2 mb-4">
            <!-- Using h2 style from theme -->
            <h2 class="h2"> <!-- Applied theme h2 class -->
                System Status
            </h2>
             <!-- Using svg-button style from theme -->
             <button @click="refreshHardwareUsage" title="Refresh Status" class="svg-button">
                <i data-feather="refresh-cw" class="w-4 h-4"></i>
            </button>
        </div>

        <!-- Hardware Usage Summary -->
        <!-- Grid layout for summary items -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 text-sm">
            <!-- VRAM Usage -->
             <!-- Summary item container: Used a contrasting background -->
             <div v-if="vramUsage && vramUsage.gpus && vramUsage.gpus.length > 0" class="flex items-center space-x-2 p-3 panels-color rounded-md shadow"> <!-- Used panels-color for background -->
                 <img :src="SVGGPU" width="25" height="25" class="flex-shrink-0" alt="GPU Icon">
                 <div v-if="vramUsage.gpus.length === 1" class="flex-1">
                     <!-- Used theme text colors -->
                     <div class="font-medium text-blue-800 dark:text-blue-100">GPU VRAM</div>
                     <div class="text-blue-600 dark:text-blue-300">{{ computedFileSize(vramUsage.gpus[0].used_vram) }} / {{ computedFileSize(vramUsage.gpus[0].total_vram) }} ({{ vramUsage.gpus[0].percentage }}%)</div>
                 </div>
                 <div v-else class="flex-1">
                      <div class="font-medium text-blue-800 dark:text-blue-100">{{ vramUsage.gpus.length }}x GPUs</div>
                      <!-- Used muted theme text color -->
                      <div class="text-xs text-blue-500 dark:text-blue-400">Total: {{ computedFileSize(totalVramUsed) }} / {{ computedFileSize(totalVram) }} ({{ avgVramPercentage }}%)</div>
                 </div>
            </div>
             <!-- Fallback item: Muted text and styling -->
             <div v-else class="flex items-center space-x-2 p-3 panels-color rounded-md text-blue-500 dark:text-blue-400 shadow"> <!-- Used panels-color and muted text -->
                 <i data-feather="alert-circle" class="w-5 h-5"></i>
                 <div class="flex-1 font-medium">No GPU Detected</div>
             </div>

            <!-- RAM Usage -->
            <div v-if="ramUsage" class="flex items-center space-x-2 p-3 panels-color rounded-md shadow"> <!-- Used panels-color -->
                 <i data-feather="cpu" class="w-5 h-5 text-blue-500 dark:text-blue-400 flex-shrink-0"></i> <!-- Used theme accent color -->
                 <div class="flex-1">
                     <div class="font-medium text-blue-800 dark:text-blue-100">CPU RAM</div>
                     <div class="text-blue-600 dark:text-blue-300">{{ computedFileSize(ramUsage.ram_usage) }} / {{ computedFileSize(ramUsage.total_space) }} ({{ ramUsage.percent_usage }}%)</div>
                 </div>
            </div>
             <div v-else class="flex items-center space-x-2 p-3 panels-color rounded-md text-blue-500 dark:text-blue-400 shadow"> <!-- Used panels-color and muted text -->
                 <i data-feather="cpu" class="w-5 h-5"></i>
                 <div class="flex-1 font-medium">RAM N/A</div>
             </div>

            <!-- Disk Usage -->
            <div v-if="diskUsage" class="flex items-center space-x-2 p-3 panels-color rounded-md shadow"> <!-- Used panels-color -->
                 <i data-feather="hard-drive" class="w-5 h-5 text-green-500 dark:text-green-400 flex-shrink-0"></i> <!-- Kept green color as per original intention -->
                 <div class="flex-1">
                     <div class="font-medium text-blue-800 dark:text-blue-100">Disk (Models/DB)</div>
                     <div class="text-blue-600 dark:text-blue-300">{{ computedFileSize(diskUsage.binding_models_usage) }} / {{ computedFileSize(diskUsage.total_space) }} ({{ diskUsage.percent_usage }}%)</div>
                 </div>
            </div>
             <div v-else class="flex items-center space-x-2 p-3 panels-color rounded-md text-blue-500 dark:text-blue-400 shadow"> <!-- Used panels-color and muted text -->
                  <i data-feather="hard-drive" class="w-5 h-5"></i>
                  <div class="flex-1 font-medium">Disk N/A</div>
             </div>
        </div>

        <!-- Detailed Hardware Usage -->
        <div class="space-y-4">
            <!-- RAM Details -->
             <!-- Detail card: Applied theme border and background -->
             <div v-if="ramUsage" class="p-4 border border-blue-300 dark:border-blue-600 rounded-md chatbox-color"> <!-- Used chatbox-color for background -->
                <!-- Label: Using 'label' class styling, theme accent for icon -->
                <label class="label flex items-center gap-1 mb-2"> <!-- Applied theme label class -->
                     <i data-feather="cpu" class="w-4 h-4 text-blue-500 dark:text-blue-400"></i>
                     CPU RAM Usage Details
                 </label>
                 <!-- Detail text: Secondary/muted theme text -->
                 <div class="text-xs space-y-1 mb-2 text-blue-600 dark:text-blue-300">
                     <div><b>Available: </b>{{ computedFileSize(ramUsage.available_space) }}</div>
                     <div><b>Usage: </b> {{ computedFileSize(ramUsage.ram_usage) }} / {{ computedFileSize(ramUsage.total_space) }} ({{ ramUsage.percent_usage }}%)</div>
                 </div>
                 <!-- Progress Bar: Use animated theme background and foreground classes -->
                 <div class="animated-progressbar-bg h-2.5">
                     <div class="animated-progressbar-fg h-2.5 rounded-full" :style="{ width: ramUsage.percent_usage + '%' }"></div>
                 </div>
             </div>

            <!-- Disk Details -->
             <div v-if="diskUsage" class="p-4 border border-blue-300 dark:border-blue-600 rounded-md chatbox-color"> <!-- Used chatbox-color -->
                <label class="label flex items-center gap-1 mb-2"> <!-- Applied theme label class -->
                     <i data-feather="hard-drive" class="w-4 h-4 text-green-500 dark:text-green-400"></i> <!-- Kept green -->
                     Disk Usage Details
                 </label>
                 <div class="text-xs space-y-1 mb-2 text-blue-600 dark:text-blue-300">
                     <div><b>Available: </b>{{ computedFileSize(diskUsage.available_space) }}</div>
                     <div><b>Usage (Models/DB): </b> {{ computedFileSize(diskUsage.binding_models_usage) }} / {{ computedFileSize(diskUsage.total_space) }} ({{ diskUsage.percent_usage }}%)</div>
                 </div>
                 <div class="animated-progressbar-bg h-2.5">
                     <div class="animated-progressbar-fg h-2.5 rounded-full" :style="{ width: diskUsage.percent_usage + '%' }"></div>
                 </div>
             </div>

            <!-- GPU Details -->
            <div v-if="vramUsage && vramUsage.gpus && vramUsage.gpus.length > 0">
                 <div v-for="(item, index) in vramUsage.gpus" :key="index" class="p-4 border border-blue-300 dark:border-blue-600 rounded-md mb-4 chatbox-color"> <!-- Used chatbox-color -->
                    <label class="label flex items-center gap-1 mb-2"> <!-- Applied theme label class -->
                        <img :src="SVGGPU" width="20" height="20" class="flex-shrink-0" alt="GPU Icon">
                        GPU {{ index + 1 }} Usage Details
                    </label>
                    <div class="text-xs space-y-1 mb-2 text-blue-600 dark:text-blue-300">
                        <div><b>Model: </b>{{ item.gpu_model }}</div>
                        <div><b>Available VRAM: </b>{{ computedFileSize(item.available_space) }}</div>
                        <div><b>Usage: </b> {{ computedFileSize(item.used_vram) }} / {{ computedFileSize(item.total_vram) }} ({{ item.percentage }}%)</div>
                    </div>
                     <div class="animated-progressbar-bg h-2.5">
                         <div class="animated-progressbar-fg h-2.5 rounded-full" :style="{ width: item.percentage + '%' }"></div>
                     </div>
                 </div>
            </div>
             <!-- Fallback: Use theme border and muted text -->
             <div v-else class="p-4 border border-dashed border-blue-300 dark:border-blue-600 rounded-md text-center text-blue-500 dark:text-blue-400 chatbox-color"> <!-- Used chatbox-color -->
                 No GPU detected or VRAM information unavailable.
             </div>
        </div>

        <!-- Folders Section -->
        <!-- Separator: Use theme border -->
        <div class="pt-4 border-t border-blue-300 dark:border-blue-600">
             <!-- Using h3 style from theme -->
             <h3 class="h3">Common Folders</h3> <!-- Applied theme h3 class -->
             <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
                <!-- Using dedicated folder item classes from the theme -->
                <!-- Custom Personalities Folder -->
                <div
                    class="folder-item-base folder-item-personalities group"
                    @click="handleFolderClick('custom-personalities')"
                    title="Open Custom Personalities folder"
                >
                    <i data-feather="users" class="folder-item-icon folder-item-icon-personalities"></i> <!-- Applied icon classes -->
                    <span class="folder-item-label">Custom Personalities</span> <!-- Applied label class -->
                </div>

                <!-- Custom Function Calls Folder -->
                <div
                    class="folder-item-base folder-item-functions group"
                    @click="handleFolderClick('custom-function-calls')"
                     title="Open Custom Function Calls folder"
               >
                     <i data-feather="tool" class="folder-item-icon folder-item-icon-functions"></i> <!-- Applied icon classes -->
                    <span class="folder-item-label">Custom Functions</span> <!-- Applied label class -->
                </div>

                <!-- Configurations Folder -->
                 <div
                    class="folder-item-base folder-item-configs group"
                    @click="handleFolderClick('configurations')"
                     title="Open Configurations folder"
               >
                      <i data-feather="settings" class="folder-item-icon folder-item-icon-configs"></i> <!-- Applied icon classes -->
                     <span class="folder-item-label">Configurations</span> <!-- Applied label class -->
                 </div>

                <!-- AI Outputs Folder -->
                 <div
                    class="folder-item-base folder-item-outputs group"
                    @click="handleFolderClick('ai-outputs')"
                     title="Open AI Outputs folder"
               >
                      <i data-feather="gift" class="folder-item-icon folder-item-icon-outputs"></i> <!-- Applied icon classes -->
                     <span class="folder-item-label">AI Outputs</span> <!-- Applied label class -->
                 </div>

                <!-- Discussions Folder -->
                 <div
                    class="folder-item-base folder-item-discussions group"
                    @click="handleFolderClick('discussions')"
                     title="Open Discussions folder"
               >
                     <i data-feather="message-square" class="folder-item-icon folder-item-icon-discussions"></i> <!-- Applied icon classes -->
                    <span class="folder-item-label">Discussions</span> <!-- Applied label class -->
                 </div>
            </div>
        </div>
    </div>
</template>

<script>
import feather from 'feather-icons';
import filesize from '@/plugins/filesize'; // Make sure this path is correct
import SVGGPU from '@/assets/gpu.svg'; // Import SVG for template use
import axios from 'axios';

// --- Configuration (defined outside component export) ---
const REFRESH_INTERVAL_MS = 15000; // Refresh stats every 15 seconds
const VITE_LOLLMS_API_BASEURL = import.meta.env.VITE_LOLLMS_API_BASEURL || 'http://localhost:9600'; // Default API URL

// --- API Setup (defined outside component export) ---
axios.defaults.baseURL = VITE_LOLLMS_API_BASEURL;
const posts_headers = {
    'accept': 'application/json',
    'Content-Type': 'application/json'
};

export default {
    name: 'SystemStatusPanel',
    // No components: {} needed as it has no child components

    data() {
        return {
            diskUsage: null,
            ramUsage: null,
            vramUsage: null,
            refreshTimer: null,
            SVGGPU: SVGGPU // Expose imported SVG to the template
        };
    },

    computed: {
        totalVram() {
            if (!this.vramUsage || !this.vramUsage.gpus) return 0;
            return this.vramUsage.gpus.reduce((sum, gpu) => sum + gpu.total_vram, 0);
        },

        totalVramUsed() {
            console.log("this.vramUsage")
            console.log(this.vramUsage)
            if (!this.vramUsage || !this.vramUsage.gpus) return 0;
            return this.vramUsage.gpus.reduce((sum, gpu) => sum + gpu.used_vram, 0);
        },

        avgVramPercentage() {
            console.log("this.vramUsage")
            console.log(this.vramUsage)
            if (!this.vramUsage || !this.vramUsage.gpus || this.vramUsage.gpus.length === 0) return '0.00';
            const totalPercentage = this.vramUsage.gpus.reduce((sum, gpu) => sum + gpu.percentage, 0);
            return (totalPercentage / this.vramUsage.gpus.length).toFixed(2);
        }
    },

    methods: {
        async api_get_req(endpoint) {
            try {
                const res = await axios.get(`/${endpoint}`);
                return res.data;
            } catch (error) {
                console.error(`API GET Error (${endpoint}):`, error.message);
                return null; // Return null to indicate failure
            }
        },

        async api_post_req(endpoint, data = {}) {
            try {
                const payload = { ...data, client_id: this.$store.state.client_id }; // Use this.clientId
                const res = await axios.post(`/${endpoint}`, payload, { headers: posts_headers });
                return res.data;
            } catch (error) {
                console.error(`API POST Error (${endpoint}):`, error.message);
                return { status: false, error: error.message }; // Return error status
            }
        },

        computedFileSize(size) {
            if (size === null || size === undefined || isNaN(size)) return 'N/A';
            try {
                // filesize is imported globally, no 'this' needed
                return filesize(size);
            } catch (e) {
                console.warn("Filesize calculation error:", e);
                return 'Error';
            }
        },

        async refreshHardwareUsage() {
            console.log("Refreshing hardware usage...");
            // Fetch data concurrently
            const [diskData, ramData, vramData] = await Promise.all([
                this.api_get_req("disk_usage"),
                this.api_get_req("ram_usage"),
                this.api_get_req("vram_usage")
            ]);
            console.log("vramData")
            console.log(this.vramUsage)

            // Update data properties using 'this'
            this.diskUsage = diskData;
            this.ramUsage = ramData;
            this.vramUsage = vramData;

            // Ensure Feather icons are re-rendered after data update
            this.$nextTick(() => { // Use this.$nextTick
                feather.replace();
            });
        },

        async handleFolderClick(folderType) {
            if (!this.clientId) {
                console.error("Client ID not available for handleFolderClick");
                // Maybe show a toast here
                return;
            }
            const payload = {
                folder: folderType,
                // client_id is added automatically by api_post_req using this.clientId
            };
            try {
                // Call method using 'this'
                const response = await this.api_post_req('open_personal_folder', payload);
                if (response.status) {
                    console.log(`Successfully opened folder: ${folderType}`);
                    console.info(`Opened ${folderType.replace('-', ' ')} folder`);
                } else {
                    console.error(`Failed to open folder: ${folderType}`, response.error);
                    console.error(`Failed to open folder: ${response.error || 'Unknown error'}`);
                }
            } catch (error) {
                console.error('Error calling open_personal_folder endpoint:', error);
                console.error(`Error opening folder: ${error.message}`);
            }
        },

        initializeClientId() {
            const storedClientId = localStorage.getItem('lollms_client_id');
            if (storedClientId) {
                this.clientId = storedClientId; // Use this.clientId
            } else {
                this.clientId = `client_${Date.now()}_${Math.random().toString(16).substring(2, 8)}`;
                localStorage.setItem('lollms_client_id', this.clientId);
                console.warn("Generated temporary client ID:", this.clientId);
            }
        }
    },

    mounted() {
        this.initializeClientId(); // Call method using 'this'
        this.refreshHardwareUsage(); // Initial fetch

        // Set up auto-refresh timer, store timer ID in data property
        this.refreshTimer = setInterval(this.refreshHardwareUsage, REFRESH_INTERVAL_MS);

        // Initial Feather icon rendering
        this.$nextTick(() => { // Use this.$nextTick
            feather.replace();
        });
    },

    updated() {
        // This ensures icons are updated if the template changes after initial mount
        this.$nextTick(() => { // Use this.$nextTick
            feather.replace();
        });
    },

    unmounted() {
        // Clear the timer when the component is destroyed
        if (this.refreshTimer) {
            clearInterval(this.refreshTimer); // Use data property
        }
    }
};
</script>

<style scoped>
/* Styles remain exactly the same */
.folder-button {
    @apply flex flex-col items-center justify-center p-4 cursor-pointer border-2 border-dashed rounded-lg transition-all duration-200;
    min-height: 100px; /* Ensure buttons have a minimum height */
}
.folder-button:hover {
     @apply border-solid shadow-sm bg-opacity-50; /* Added bg-opacity for subtle hover */
}

.folder-button span {
    line-height: 1.2; /* Adjust line height for better text wrapping */
}

/* Optional: Add specific hover background colors based on border color */
.border-blue-500:hover { @apply bg-blue-50 dark:bg-blue-900/20; }
.border-green-500:hover { @apply bg-green-50 dark:bg-green-900/20; }
.border-yellow-500:hover { @apply bg-yellow-50 dark:bg-yellow-900/20; }
.border-purple-500:hover { @apply bg-purple-50 dark:bg-purple-900/20; }
.border-red-500:hover { @apply bg-red-50 dark:bg-red-900/20; }

/* Make progress bars smoother */
.transition-all {
    transition-property: all;
}
.duration-300 {
    transition-duration: 300ms;
}

</style>