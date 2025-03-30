<template>
    <div class="space-y-6 p-4 md:p-6 bg-white dark:bg-gray-800 rounded-lg shadow-md border border-gray-200 dark:border-gray-700">
        <div class="flex justify-between items-center border-b border-gray-200 dark:border-gray-700 pb-2 mb-4">
            <h2 class="text-xl font-semibold text-gray-800 dark:text-gray-200">
                System Status
            </h2>
            <button @click="refreshHardwareUsage" title="Refresh Status" class="p-1 text-gray-500 hover:text-blue-500 dark:text-gray-400 dark:hover:text-blue-400 transition-colors duration-150">
                <i data-feather="refresh-cw" class="w-4 h-4"></i>
            </button>
        </div>


        <!-- Hardware Usage Summary -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 text-sm">
            <!-- VRAM Usage -->
             <div v-if="vramUsage && vramUsage.gpus && vramUsage.gpus.length > 0" class="flex items-center space-x-2 p-3 bg-gray-50 dark:bg-gray-700 rounded-md">
                 <img :src="SVGGPU" width="25" height="25" class="flex-shrink-0" alt="GPU Icon">
                 <div v-if="vramUsage.gpus.length === 1" class="flex-1">
                     <div class="font-medium">GPU VRAM</div>
                     <div>{{ computedFileSize(vramUsage.gpus[0].used_vram) }} / {{ computedFileSize(vramUsage.gpus[0].total_vram) }} ({{ vramUsage.gpus[0].percentage }}%)</div>
                 </div>
                 <div v-else class="flex-1">
                      <div class="font-medium">{{ vramUsage.gpus.length }}x GPUs</div>
                      <!-- Could show average/total usage if needed -->
                      <div class="text-xs text-gray-500 dark:text-gray-400">Total: {{ computedFileSize(totalVramUsed) }} / {{ computedFileSize(totalVram) }} ({{ avgVramPercentage }}%)</div>
                 </div>
            </div>
             <div v-else class="flex items-center space-x-2 p-3 bg-gray-50 dark:bg-gray-700 rounded-md text-gray-500 dark:text-gray-400">
                 <i data-feather="alert-circle" class="w-5 h-5"></i> <!-- Changed icon for clarity -->
                 <div class="flex-1 font-medium">No GPU Detected</div>
             </div>

            <!-- RAM Usage -->
            <div v-if="ramUsage" class="flex items-center space-x-2 p-3 bg-gray-50 dark:bg-gray-700 rounded-md">
                 <i data-feather="cpu" class="w-5 h-5 text-blue-500 flex-shrink-0"></i>
                 <div class="flex-1">
                     <div class="font-medium">CPU RAM</div>
                     <div>{{ computedFileSize(ramUsage.ram_usage) }} / {{ computedFileSize(ramUsage.total_space) }} ({{ ramUsage.percent_usage }}%)</div>
                 </div>
            </div>
             <div v-else class="flex items-center space-x-2 p-3 bg-gray-50 dark:bg-gray-700 rounded-md text-gray-500 dark:text-gray-400">
                 <i data-feather="cpu" class="w-5 h-5"></i>
                 <div class="flex-1 font-medium">RAM N/A</div>
             </div>

            <!-- Disk Usage -->
            <div v-if="diskUsage" class="flex items-center space-x-2 p-3 bg-gray-50 dark:bg-gray-700 rounded-md">
                 <i data-feather="hard-drive" class="w-5 h-5 text-green-500 flex-shrink-0"></i>
                 <div class="flex-1">
                     <div class="font-medium">Disk (Models/DB)</div>
                     <div>{{ computedFileSize(diskUsage.binding_models_usage) }} / {{ computedFileSize(diskUsage.total_space) }} ({{ diskUsage.percent_usage }}%)</div>
                 </div>
            </div>
             <div v-else class="flex items-center space-x-2 p-3 bg-gray-50 dark:bg-gray-700 rounded-md text-gray-500 dark:text-gray-400">
                  <i data-feather="hard-drive" class="w-5 h-5"></i>
                  <div class="flex-1 font-medium">Disk N/A</div>
             </div>
        </div>

        <!-- Detailed Hardware Usage -->
        <div class="space-y-4">
            <!-- RAM Details -->
             <div v-if="ramUsage" class="p-4 border border-gray-200 dark:border-gray-600 rounded-md">
                <label class=" flex items-center gap-1 mb-2 text-sm font-medium text-gray-900 dark:text-white">
                     <i data-feather="cpu" class="w-4 h-4 text-blue-500"></i>
                     CPU RAM Usage Details
                 </label>
                 <div class="text-xs space-y-1 mb-2 text-gray-600 dark:text-gray-400">
                     <div><b>Available: </b>{{ computedFileSize(ramUsage.available_space) }}</div>
                     <div><b>Usage: </b> {{ computedFileSize(ramUsage.ram_usage) }} / {{ computedFileSize(ramUsage.total_space) }} ({{ ramUsage.percent_usage }}%)</div>
                 </div>
                 <div class="w-full bg-gray-200 rounded-full h-2.5 dark:bg-gray-600">
                     <div class="bg-blue-600 h-2.5 rounded-full transition-all duration-300" :style="{ width: ramUsage.percent_usage + '%' }"></div>
                 </div>
             </div>

            <!-- Disk Details -->
             <div v-if="diskUsage" class="p-4 border border-gray-200 dark:border-gray-600 rounded-md">
                <label class="flex items-center gap-1 mb-2 text-sm font-medium text-gray-900 dark:text-white">
                     <i data-feather="hard-drive" class="w-4 h-4 text-green-500"></i>
                     Disk Usage Details
                 </label>
                 <div class="text-xs space-y-1 mb-2 text-gray-600 dark:text-gray-400">
                     <div><b>Available: </b>{{ computedFileSize(diskUsage.available_space) }}</div>
                     <div><b>Usage (Models/DB): </b> {{ computedFileSize(diskUsage.binding_models_usage) }} / {{ computedFileSize(diskUsage.total_space) }} ({{ diskUsage.percent_usage }}%)</div>
                 </div>
                 <div class="w-full bg-gray-200 rounded-full h-2.5 dark:bg-gray-600">
                     <div class="bg-green-600 h-2.5 rounded-full transition-all duration-300" :style="{ width: diskUsage.percent_usage + '%' }"></div>
                 </div>
             </div>

            <!-- GPU Details -->
            <div v-if="vramUsage && vramUsage.gpus && vramUsage.gpus.length > 0">
                 <div v-for="(item, index) in vramUsage.gpus" :key="index" class="p-4 border border-gray-200 dark:border-gray-600 rounded-md mb-4">
                    <label class="flex items-center gap-1 mb-2 text-sm font-medium text-gray-900 dark:text-white">
                        <img :src="SVGGPU" width="20" height="20" class="flex-shrink-0" alt="GPU Icon">
                        GPU {{ index + 1 }} Usage Details <!-- Added +1 for better numbering -->
                    </label>
                    <div class="text-xs space-y-1 mb-2 text-gray-600 dark:text-gray-400">
                        <div><b>Model: </b>{{ item.gpu_model }}</div>
                        <div><b>Available VRAM: </b>{{ computedFileSize(item.available_space) }}</div>
                        <div><b>Usage: </b> {{ computedFileSize(item.used_vram) }} / {{ computedFileSize(item.total_vram) }} ({{ item.percentage }}%)</div>
                    </div>
                     <div class="w-full bg-gray-200 rounded-full h-2.5 dark:bg-gray-600">
                         <div class="bg-purple-600 h-2.5 rounded-full transition-all duration-300" :style="{ width: item.percentage + '%' }"></div>
                     </div>
                 </div>
            </div>
             <div v-else class="p-4 border border-dashed border-gray-300 dark:border-gray-600 rounded-md text-center text-gray-500 dark:text-gray-400">
                 No GPU detected or VRAM information unavailable.
             </div>
        </div>

        <!-- Folders Section -->
        <div class="pt-4 border-t border-gray-200 dark:border-gray-700">
            <h3 class="text-lg font-semibold mb-4 text-gray-800 dark:text-gray-200">Common Folders</h3>
            <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
                <!-- Custom Personalities Folder -->
                <div
                    class="folder-button group border-blue-500 hover:bg-blue-50 dark:hover:bg-blue-900/20"
                    @click="handleFolderClick('custom-personalities')"
                    title="Open Custom Personalities folder"
                >
                    <i data-feather="users" class="w-10 h-10 text-blue-500 group-hover:scale-110 transition-transform duration-200"></i>
                    <span class="mt-2 text-xs text-center text-gray-700 dark:text-gray-300">Custom Personalities</span>
                </div>

                <!-- Custom Function Calls Folder -->
                <div
                    class="folder-button group border-green-500 hover:bg-green-50 dark:hover:bg-green-900/20"
                    @click="handleFolderClick('custom-function-calls')"
                     title="Open Custom Function Calls folder"
               >
                    <i data-feather="tool" class="w-10 h-10 text-green-500 group-hover:scale-110 transition-transform duration-200"></i>
                    <span class="mt-2 text-xs text-center text-gray-700 dark:text-gray-300">Custom Functions</span>
                </div>

                <!-- Configurations Folder -->
                 <div
                    class="folder-button group border-yellow-500 hover:bg-yellow-50 dark:hover:bg-yellow-900/20"
                    @click="handleFolderClick('configurations')"
                     title="Open Configurations folder"
               >
                     <i data-feather="settings" class="w-10 h-10 text-yellow-500 group-hover:scale-110 transition-transform duration-200"></i>
                     <span class="mt-2 text-xs text-center text-gray-700 dark:text-gray-300">Configurations</span>
                 </div>

                <!-- AI Outputs Folder -->
                 <div
                    class="folder-button group border-purple-500 hover:bg-purple-50 dark:hover:bg-purple-900/20"
                    @click="handleFolderClick('ai-outputs')"
                     title="Open AI Outputs folder"
               >
                     <i data-feather="gift" class="w-10 h-10 text-purple-500 group-hover:scale-110 transition-transform duration-200"></i>
                     <span class="mt-2 text-xs text-center text-gray-700 dark:text-gray-300">AI Outputs</span>
                 </div>

                <!-- Discussions Folder -->
                 <div
                    class="folder-button group border-red-500 hover:bg-red-50 dark:hover:bg-red-900/20"
                    @click="handleFolderClick('discussions')"
                     title="Open Discussions folder"
               >
                     <i data-feather="message-square" class="w-10 h-10 text-red-500 group-hover:scale-110 transition-transform duration-200"></i>
                     <span class="mt-2 text-xs text-center text-gray-700 dark:text-gray-300">Discussions</span>
                 </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, onUpdated, nextTick } from 'vue';
import feather from 'feather-icons';
import filesize from '@/plugins/filesize'; // Make sure this path is correct
import SVGGPU from '@/assets/gpu.svg';
import axios from 'axios';

// --- Configuration ---
const REFRESH_INTERVAL_MS = 15000; // Refresh stats every 15 seconds
const VITE_LOLLMS_API_BASEURL = import.meta.env.VITE_LOLLMS_API_BASEURL || 'http://localhost:9600'; // Default API URL

// --- State ---
const diskUsage = ref(null);
const ramUsage = ref(null);
const vramUsage = ref(null);
const clientId = ref(''); // Will be fetched or set
const refreshTimer = ref(null);

// --- API Setup ---
axios.defaults.baseURL = VITE_LOLLMS_API_BASEURL;
const posts_headers = {
    'accept': 'application/json',
    'Content-Type': 'application/json'
};

// --- Computed Properties ---
const totalVram = computed(() => {
    if (!vramUsage.value || !vramUsage.value.gpus) return 0;
    return vramUsage.value.gpus.reduce((sum, gpu) => sum + gpu.total_vram, 0);
});

const totalVramUsed = computed(() => {
    if (!vramUsage.value || !vramUsage.value.gpus) return 0;
    return vramUsage.value.gpus.reduce((sum, gpu) => sum + gpu.used_vram, 0);
});

const avgVramPercentage = computed(() => {
    if (!vramUsage.value || !vramUsage.value.gpus || vramUsage.value.gpus.length === 0) return '0.00';
    const totalPercentage = vramUsage.value.gpus.reduce((sum, gpu) => sum + gpu.percentage, 0);
    return (totalPercentage / vramUsage.value.gpus.length).toFixed(2);
});


// --- Methods ---
const api_get_req = async (endpoint) => {
    try {
        const res = await axios.get(`/${endpoint}`);
        return res.data;
    } catch (error) {
        console.error(`API GET Error (${endpoint}):`, error.message);
        // Optionally show a user-facing error, but avoid flooding
        return null; // Return null to indicate failure
    }
};

const api_post_req = async (endpoint, data = {}) => {
    try {
        const payload = { ...data, client_id: clientId.value }; // Always include client_id
        const res = await axios.post(`/${endpoint}`, payload, { headers: posts_headers });
        return res.data;
    } catch (error) {
        console.error(`API POST Error (${endpoint}):`, error.message);
        // Optionally show a user-facing error
        return { status: false, error: error.message }; // Return error status
    }
};

const computedFileSize = (size) => {
    if (size === null || size === undefined || isNaN(size)) return 'N/A';
    try {
        return filesize(size);
    } catch (e) {
        console.warn("Filesize calculation error:", e);
        return 'Error';
    }
};

const refreshHardwareUsage = async () => {
    console.log("Refreshing hardware usage...");
    // Fetch data concurrently
    const [diskData, ramData, vramData] = await Promise.all([
        api_get_req("disk_usage"),
        api_get_req("ram_usage"),
        api_get_req("vram_usage")
    ]);

    diskUsage.value = diskData;
    ramUsage.value = ramData;
    vramUsage.value = vramData;

    // Ensure Feather icons are re-rendered after data update
    nextTick(() => {
        feather.replace();
    });
};

const handleFolderClick = async (folderType) => {
    if (!clientId.value) {
        console.error("Client ID not available for handleFolderClick");
        // Maybe show a toast here
        return;
    }
    const payload = {
        folder: folderType,
        // client_id is added automatically by api_post_req
    };
    try {
        const response = await api_post_req('open_personal_folder', payload);
        if (response.status) {
            console.log(`Successfully opened folder: ${folderType}`);
            // Replace show_toast with console log or implement a local toast system
            console.info(`Opened ${folderType.replace('-', ' ')} folder`);
        } else {
            console.error(`Failed to open folder: ${folderType}`, response.error);
             console.error(`Failed to open folder: ${response.error || 'Unknown error'}`);
        }
    } catch (error) {
        console.error('Error calling open_personal_folder endpoint:', error);
         console.error(`Error opening folder: ${error.message}`);
    }
};

// Function to get client ID (example - replace with your actual logic)
const initializeClientId = () => {
    // Try getting from localStorage, global variable, or an initial API call
    const storedClientId = localStorage.getItem('lollms_client_id');
    if (storedClientId) {
        clientId.value = storedClientId;
    } else {
        // Fallback or generate/fetch a new one if necessary
        // For demonstration, let's generate a simple one (NOT recommended for production)
        clientId.value = `client_${Date.now()}_${Math.random().toString(16).substring(2, 8)}`;
        localStorage.setItem('lollms_client_id', clientId.value);
        console.warn("Generated temporary client ID:", clientId.value);
    }
};

// --- Lifecycle Hooks ---
onMounted(() => {
    initializeClientId(); // Get the client ID first
    refreshHardwareUsage(); // Initial fetch

    // Set up auto-refresh timer
    refreshTimer.value = setInterval(refreshHardwareUsage, REFRESH_INTERVAL_MS);

    nextTick(() => {
        feather.replace();
    });
});

onUpdated(() => {
    // This ensures icons are updated if the template changes after initial mount
    nextTick(() => {
        feather.replace();
    });
});

onUnmounted(() => {
    // Clear the timer when the component is destroyed
    if (refreshTimer.value) {
        clearInterval(refreshTimer.value);
    }
});

</script>

<style scoped>
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