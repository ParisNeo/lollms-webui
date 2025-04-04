<template>
    <div class="user-settings-panel space-y-6">
        <h2 class="text-xl font-semibold text-blue-800 dark:text-blue-100 border-b border-blue-300 dark:border-blue-600 pb-2">
            Smart Routing Configuration
        </h2>

        <p class="text-sm text-blue-600 dark:text-blue-400 mb-4">
            Configure LoLLMs to automatically select the best model for a given task based on descriptions.
        </p>

        <div class="space-y-4">
            <div class="toggle-item border-t border-blue-200 dark:border-blue-700 pt-3 mt-2">
                <label for="use_smart_routing" class="toggle-label">
                    Enable Smart Routing
                    <span class="toggle-description">
                        Allow automatic model selection based on task descriptions.
                    </span>
                </label>
                <ToggleSwitch
                    id="use_smart_routing"
                    :checked="config.use_smart_routing"
                    @update:checked="updateValue('use_smart_routing', $event)"
                />
            </div>

            <div :class="['toggle-item border-t border-blue-200 dark:border-blue-700 pt-3 mt-2', !config.use_smart_routing ? 'opacity-50 pointer-events-none' : '']">
                <label for="restore_model_after_smart_routing" class="toggle-label">
                    Restore Original Model After Routing
                    <span class="toggle-description">
                        Switch back to the original model after the routed task.
                    </span>
                </label>
                 <ToggleSwitch
                    id="restore_model_after_smart_routing"
                    :checked="config.restore_model_after_smart_routing"
                    @update:checked="updateValue('restore_model_after_smart_routing', $event)"
                    :disabled="!config.use_smart_routing"
                 />
            </div>

             <div :class="['setting-item border-t border-blue-200 dark:border-blue-700 pt-3 mt-2', !config.use_smart_routing ? 'opacity-50 pointer-events-none' : '']">
                 <label for="smart_routing_router_model" class="setting-label">
                    Router Model Name
                     <span class="block text-xs font-normal text-blue-500 dark:text-blue-400 mt-1">
                        The model that decides which specialized model to use.
                    </span>
                 </label>
                 <input
                     type="text"
                     id="smart_routing_router_model"
                     :value="config.smart_routing_router_model"
                     @input="updateValue('smart_routing_router_model', $event.target.value)"
                     :disabled="!config.use_smart_routing"
                     class="input flex-grow"
                     placeholder="e.g., mistralai/Mistral-7B-Instruct-v0.2"
                 >
             </div>

             <div :class="['space-y-2 border-t border-blue-200 dark:border-blue-700 pt-3 mt-2', !config.use_smart_routing ? 'opacity-50 pointer-events-none' : '']">
                 <label class="label mb-1">
                    Specialized Models & Descriptions
                     <span class="block text-xs font-normal text-blue-500 dark:text-blue-400 mt-1">
                        Define models the router can choose from and their capabilities.
                    </span>
                </label>
                <DictManager
                    :modelValue="config.smart_routing_models_description || {}" 
                    @update:modelValue="updateValue('smart_routing_models_description', $event)"
                    key-name="Model Path / Name"
                    value-name="Model Description (Capabilities)"
                    key-placeholder="e.g., openai/gpt-4"
                    value-placeholder="e.g., Excellent for coding tasks"
                    :disabled="!config.use_smart_routing"
                    class="flex-grow panels-color p-2 rounded border border-gray-300 dark:border-gray-600" 
                 />
            </div>
        </div>
    </div>
</template>

<script>
import ToggleSwitch from '@/components/ToggleSwitch.vue';
import DictManager from '@/components/DictManager.vue'; // Ensure path is correct

export default {
    name: 'SmartRoutingSettings', // Changed name
    components: {
        ToggleSwitch,
        DictManager
    },
    props: {
        config: { type: Object, required: true }, // Receive editable config copy
        loading: { type: Boolean, default: false }
    },
    emits: ['setting-updated'], // Declare the event

    methods: {
        updateValue(key, value) {
            // For DictManager, the value is already the updated object
            // For ToggleSwitch, the value is boolean
            // For text input, value is string
            this.$emit('setting-updated', { key, value });
        }
        // No need for updateBoolean, ToggleSwitch emits boolean directly
    }
}
</script>

<style scoped>
/* Using shared styles defined in previous components */
.setting-item { @apply flex flex-col md:flex-row md:items-center gap-2 md:gap-4 py-2; }
.setting-label { @apply block text-sm font-medium text-gray-700 dark:text-gray-300 w-full md:w-1/3 lg:w-1/4 flex-shrink-0; }
.input { @apply block w-full px-3 py-2 bg-gray-50 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 focus:border-blue-500 dark:focus:ring-offset-gray-900 sm:text-sm disabled:opacity-50 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500; }
.label { @apply block text-sm font-medium text-gray-700 dark:text-gray-300; }
.panels-color { @apply bg-white dark:bg-gray-800; }
.toggle-item { @apply flex items-center justify-between p-3 hover:bg-gray-50 dark:hover:bg-gray-700 rounded-lg transition-colors; }
.toggle-label { @apply text-sm font-medium text-gray-700 dark:text-gray-300 cursor-pointer flex-1 mr-4; }
.toggle-description { @apply block text-xs text-gray-500 dark:text-gray-400 mt-1 font-normal; }
</style>