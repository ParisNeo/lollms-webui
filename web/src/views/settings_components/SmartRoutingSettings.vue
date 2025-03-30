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
                        :checked="useSmartRouting"
                        @change="updateBoolean('use_smart_routing', $event.target.checked)"
                        class="sr-only peer"
                    >
                    <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-600 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-500 peer-checked:bg-primary"></div>
                </label>
            </div>

            <!-- Restore Model After Smart Routing Toggle -->
            <div :class="['flex items-center justify-between p-3 hover:bg-gray-50 dark:hover:bg-gray-700 rounded-lg transition-colors', !useSmartRouting ? 'opacity-50 pointer-events-none' : '']">
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
                        :checked="restoreModelAfterRouting"
                        @change="updateBoolean('restore_model_after_smart_routing', $event.target.checked)"
                        :disabled="!useSmartRouting"
                         class="sr-only peer"
                   >
                    <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-600 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-500 peer-checked:bg-primary"></div>
                </label>
            </div>

             <!-- Router Model Input -->
             <div :class="['p-3 rounded-lg space-y-2', !useSmartRouting ? 'opacity-50 pointer-events-none' : '']">
                 <label for="smart_routing_router_model" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    Router Model Name
                     <span class="block text-xs text-gray-500 dark:text-gray-400 mt-1">
                        The model responsible for deciding which specialized model to use. (e.g., `mistralai/Mistral-7B-Instruct-v0.2`)
                    </span>
                 </label>
                 <input
                     type="text"
                     id="smart_routing_router_model"
                     :value="routerModel"
                     @input="updateValue('smart_routing_router_model', $event.target.value)"
                     :disabled="!useSmartRouting"
                     class="input-field w-full"
                     placeholder="Enter the router model name"
                 >
             </div>

             <!-- Models with Description Dictionary -->
             <div :class="['p-3 rounded-lg space-y-2', !useSmartRouting ? 'opacity-50 pointer-events-none' : '']">
                 <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Specialized Models & Descriptions
                     <span class="block text-xs text-gray-500 dark:text-gray-400 mt-1">
                        Define the models that the router can choose from and provide a clear description of their capabilities.
                    </span>
                </label>
                <DictManager
                    :modelValue="modelsDescription"
                    @update:modelValue="updateValue('smart_routing_models_description', $event)"
                    key-name="Model Path / Name"
                    value-name="Model Description (Task Capabilities)"
                    placeholder="Enter model name (e.g., openai/gpt-4) or path"
                    value-placeholder="Describe what this model is good at (e.g., 'Excellent for coding tasks and complex reasoning')"
                    :disabled="!useSmartRouting"
                    class="flex-grow"
                 />
            </div>
        </div>
    </div>
</template>

<script>
import DictManager from '@/components/DictManager.vue'; // Adjust path as needed
// Optionally import mapState if you prefer that over direct $store access
// import { mapState } from 'vuex';

export default {
    name: 'SmartRoutingConfig',
    components: {
        DictManager
    },
    props: {
        loading: {
            type: Boolean,
            default: false
        },
        settingsChanged: { // Optional: Can be used for local validation/UI hints
            type: Boolean,
            default: false
        }
    },
    emits: ['update:setting', 'settings-changed'], // Declare emitted events
    computed: {
        // Using computed properties to access store state for cleaner template
        // This also makes it easier to switch to mapState if desired later
        useSmartRouting() {
            return this.$store.state.config.use_smart_routing;
        },
        restoreModelAfterRouting() {
            return this.$store.state.config.restore_model_after_smart_routing;
        },
        routerModel() {
            return this.$store.state.config.smart_routing_router_model;
        },
        modelsDescription() {
            // Ensure a default empty object if the value might be initially undefined/null
            return this.$store.state.config.smart_routing_models_description || {};
        }

        // --- Alternative using mapState (requires importing mapState) ---
        // ...mapState({
        //     useSmartRouting: state => state.config.use_smart_routing,
        //     restoreModelAfterRouting: state => state.config.restore_model_after_smart_routing,
        //     routerModel: state => state.config.smart_routing_router_model,
        //     modelsDescription: state => state.config.smart_routing_models_description || {}
        // })
    },
    methods: {
        updateValue(key, value) {
            // Simple update for text, numbers, or complex objects like dictionaries
            this.$emit('update:setting', { key, value });
            // Optionally emit settings-changed if needed based on props usage
             if (this.settingsChanged !== undefined) { // Check if the prop is actually being used/passed
                 this.$emit('settings-changed', true);
             }
        },
        updateBoolean(key, value) {
            // Ensures boolean values are correctly emitted
            this.$emit('update:setting', { key, value: Boolean(value) });
            // Optionally emit settings-changed
            if (this.settingsChanged !== undefined) {
                this.$emit('settings-changed', true);
            }
        }
    }
}
</script>

<style scoped>
.input-field {
     @apply block w-full px-3 py-2 bg-gray-50 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-primary focus:border-primary sm:text-sm disabled:opacity-50 disabled:cursor-not-allowed;
}

/* Add specific styles for DictManager if needed, or style within DictManager itself */
</style>