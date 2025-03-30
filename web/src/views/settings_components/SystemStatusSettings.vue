<template>
    <div class="space-y-6 p-4 md:p-6 bg-white dark:bg-gray-800 rounded-lg shadow-md border border-gray-200 dark:border-gray-700">
        <h2 class="text-xl font-semibold text-gray-800 dark:text-gray-200 border-b border-gray-200 dark:border-gray-700 pb-2">
            System Status
        </h2>

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
                      <!-- Maybe show average or total usage if needed -->
                 </div>
            </div>
             <div v-else class="flex items-center space-x-2 p-3 bg-gray-50 dark:bg-gray-700 rounded-md">
                 <i data-feather="cpu" class="w-5 h-5 text-gray-500"></i>
                 <div class="flex-1 font-medium text-gray-500">No GPU Detected</div>
             </div>

            <!-- RAM Usage -->
            <div v-if="ramUsage" class="flex items-center space-x-2 p-3 bg-gray-50 dark:bg-gray-700 rounded-md">
                 <i data-feather="cpu" class="w-5 h-5 text-blue-500 flex-shrink-0"></i>
                 <div class="flex-1">
                     <div class="font-medium">CPU RAM</div>
                     <div>{{ computedFileSize(ramUsage.ram_usage) }} / {{ computedFileSize(ramUsage.total_space) }} ({{ ramUsage.percent_usage }}%)</div>
                 </div>
            </div>

            <!-- Disk Usage -->
            <div v-if="diskUsage" class="flex items-center space-x-2 p-3 bg-gray-50 dark:bg-gray-700 rounded-md">
                 <i data-feather="hard-drive" class="w-5 h-5 text-green-500 flex-shrink-0"></i>
                 <div class="flex-1">
                     <div class="font-medium">Disk (Models/DB)</div>
                     <div>{{ computedFileSize(diskUsage.binding_models_usage) }} / {{ computedFileSize(diskUsage.total_space) }} ({{ diskUsage.percent_usage }}%)</div>
                 </div>
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
                        GPU {{ index }} Usage Details
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
import { ref, computed, onMounted, onUpdated, nextTick, defineProps } from 'vue';
import feather from 'feather-icons';
import filesize from '@/plugins/filesize'; // Assuming filesize plugin is setup
import SVGGPU from '@/assets/gpu.svg'; // Import SVG


// Props definition - Receiving data and functions from parent
const props = defineProps({
    // Config object - might contain paths or other relevant static info
    config: { type: Object, required: true },
    // Direct hardware stats (assuming parent fetches these)
    diskUsage: { type: Object, default: null },
    ramUsage: { type: Object, default: null },
    vramUsage: { type: Object, default: null },
    // API Interaction Functions
    api_post_req: { type: Function, required: true },
    client_id: { type: String, required: true },
    // Utility Functions
    show_toast: { type: Function, required: true }
});


// Methods
const computedFileSize = (size) => {
    if (size === null || size === undefined) return 'N/A';
    return filesize(size);
};

const handleFolderClick = async (folderType) => {
    const payload = {
        client_id: props.client_id,
        folder: folderType,
    };
    try {
        const response = await props.api_post_req('open_personal_folder', payload);
        if (response.status) {
            console.log(`Successfully opened folder: ${folderType}`);
            props.show_toast(`Opened ${folderType.replace('-', ' ')} folder`, 4, true);
        } else {
            console.error(`Failed to open folder: ${folderType}`, response.error);
             props.show_toast(`Failed to open folder: ${response.error || 'Unknown error'}`, 4, false);
        }
    } catch (error) {
        console.error('Error calling open_personal_folder endpoint:', error);
         props.show_toast(`Error opening folder: ${error.message}`, 4, false);
    }
};

// Lifecycle Hooks
onMounted(() => {
    nextTick(() => {
        feather.replace();
    });
});

onUpdated(() => {
    nextTick(() => {
        feather.replace();
    });
});

</script>

<style scoped>
.folder-button {
    @apply flex flex-col items-center justify-center p-4 cursor-pointer border-2 border-dashed rounded-lg transition-all duration-200;
    min-height: 100px; /* Ensure buttons have a minimum height */
}
.folder-button:hover {
     @apply border-solid shadow-sm;
}

.folder-button span {
    line-height: 1.2; /* Adjust line height for better text wrapping */
}
</style>