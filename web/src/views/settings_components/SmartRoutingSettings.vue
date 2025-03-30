<template>
    <div class="space-y-6 p-4 md:p-6 bg-white dark:bg-gray-800 rounded-lg shadow-md border border-gray-200 dark:border-gray-700">
        <h2 class="text-xl font-semibold text-gray-800 dark:text-gray-200 border-b border-gray-200 dark:border-gray-700 pb-2">
            Smart Routing Configuration
        </h2>

        <div class="space-y-4">
            <!-- Use Smart Routing Toggle -->
            <div class="flex items-center justify-between p-3 hover:bg-gray-50 dark:hover:bg-gray-700 rounded-lg transition-colors">
                <label for="use_smart_routing" class="text-sm font-medium text-gray-700 dark:text-gray-300 cursor-pointer flex-1 mr-4">
                    Enable Smart Routing
                    <span class="block text-xs text-gray-500 dark:text-gray-400 mt-1">
                        Allow LoLLMs to automatically select the best model for a given task based on descriptions.
                    </span>
                </label>
                <label class="relative inline-flex items-center cursor-pointer">
                    <input
                        type="checkbox"
                        id="use_smart_routing"
                        :checked="config.use_smart_routing"
                        @change="updateBoolean('use_smart_routing', $event.target.checked)"
                        class="sr-only peer"
                    >
                    <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-600 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-500 peer-checked:bg-primary"></div>
                </label>
            </div>

            <!-- Restore Model After Smart Routing Toggle -->
            <div :class="['flex items-center justify-between p-3 hover:bg-gray-50 dark:hover:bg-gray-700 rounded-lg transition-colors', !config.use_smart_routing ? 'opacity-50 pointer-events-none' : '']">
                <label for="restore_model_after_smart_routing" class="text-sm font-medium text-gray-700 dark:text-gray-300 cursor-pointer flex-1 mr-4">
                    Restore Original Model After Routing
                    <span class="block text-xs text-gray-500 dark:text-gray-400 mt-1">
                        Automatically switch back to the originally selected model after the routed task is complete.
                    </span>
                </label>
                 <label class="relative inline-flex items-center cursor-pointer">
                    <input
                        type="checkbox"
                        id="restore_model_after_smart_routing"
                        :checked="config.restore_model_after_smart_routing"
                        @change="updateBoolean('restore_model_after_smart_routing', $event.target.checked)"
                        :disabled="!config.use_smart_routing"
                         class="sr-only peer"
                   >
                    <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-600 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-500 peer-checked:bg-primary"></div>
                </label>
            </div>

             <!-- Router Model Input -->
             <div :class="['p-3 rounded-lg space-y-2', !config.use_smart_routing ? 'opacity-50 pointer-events-none' : '']">
                 <label for="smart_routing_router_model" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    Router Model Name
                     <span class="block text-xs text-gray-500 dark:text-gray-400 mt-1">
                        The model responsible for deciding which specialized model to use. (e.g., `mistralai/Mistral-7B-Instruct-v0.2`)
                    </span>
                 </label>
                 <input
                     type="text"
                     id="smart_routing_router_model"
                     :value="config.smart_routing_router_model"
                     @input="updateValue('smart_routing_router_model', $event.target.value)"
                     :disabled="!config.use_smart_routing"
                     class="input-field w-full"
                     placeholder="Enter the router model name"
                 >
             </div>

             <!-- Models with Description Dictionary -->
             <div :class="['p-3 rounded-lg space-y-2', !config.use_smart_routing ? 'opacity-50 pointer-events-none' : '']">
                 <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Specialized Models & Descriptions
                     <span class="block text-xs text-gray-500 dark:text-gray-400 mt-1">
                        Define the models that the router can choose from and provide a clear description of their capabilities.
                    </span>
                </label>
                <DictManager
                    :modelValue="config.smart_routing_models_description || {}"
                    @update:modelValue="updateValue('smart_routing_models_description', $event)"
                    key-name="Model Path / Name"
                    value-name="Model Description (Task Capabilities)"
                    placeholder="Enter model name (e.g., openai/gpt-4) or path"
                    value-placeholder="Describe what this model is good at (e.g., 'Excellent for coding tasks and complex reasoning')"
                    :disabled="!config.use_smart_routing"
                    class="flex-grow"
                 />
            </div>
        </div>
    </div>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue';
import DictManager from '@/components/DictManager.vue'; // Adjust path as needed

// Props definition
const props = defineProps({
    config: { type: Object, required: true },
    loading: { type: Boolean, default: false },
    settingsChanged: { type: Boolean, default: false } // Optional: Can be used for local validation/UI hints
});

// Emits definition for updating parent
const emit = defineEmits(['update:setting', 'settings-changed']);

// --- Methods ---
const updateValue = (key, value) => {
    // Simple update for text, numbers, or complex objects like dictionaries
    emit('update:setting', { key, value });
};

const updateBoolean = (key, value) => {
    // Ensures boolean values are correctly emitted
    emit('update:setting', { key, value: Boolean(value) });
};

</script>

<style scoped>
.input-field {
     @apply block w-full px-3 py-2 bg-gray-50 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-primary focus:border-primary sm:text-sm disabled:opacity-50 disabled:cursor-not-allowed;
}

/* Add specific styles for DictManager if needed, or style within DictManager itself */
</style>