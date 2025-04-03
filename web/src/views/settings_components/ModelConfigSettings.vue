<template>
    <div class="user-settings-panel space-y-6">
        <h2 class="text-xl font-semibold text-blue-800 dark:text-blue-100 border-b border-blue-300 dark:border-blue-600 pb-2">
            Model Generation Parameters
        </h2>

         <p class="text-sm text-blue-600 dark:text-blue-400 mb-4">
            Adjust the core parameters that influence how the AI generates text. These settings can be overridden by specific personalities unless the option below is checked.
        </p>

        <div class="toggle-item !justify-start gap-4 border border-blue-200 dark:border-blue-700 rounded-lg p-3 panels-color">
            <ToggleSwitch
                id="override_personality_model_parameters"
                :checked="config.override_personality_model_parameters"
                @update:checked="updateValue('override_personality_model_parameters', $event)"
            />
            <label for="override_personality_model_parameters" class="toggle-label !flex-none">
                Override Personality Parameters
                 <span class="toggle-description">Force the use of these global parameters, ignoring any settings defined within the selected personality.</span>
            </label>
        </div>

        <div :class="['space-y-5 pt-4', isDisabled ? 'opacity-50 pointer-events-none' : '']">
            <div class="setting-item">
                <label for="seed" class="setting-label flex items-center">
                    Seed
                     <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="w-4 h-4 ml-1 text-blue-400 dark:text-blue-500 cursor-help feather feather-info"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>
                 </label>
                <input
                    type="number"
                    id="seed"
                    :value="config.seed"
                    @input="handleNumberInput('seed', $event.target.value, true)"
                    class="input-sm w-full md:w-32"
                    step="1"
                    placeholder="-1"
                    :disabled="isDisabled"
                 >
            </div>

            <div class="setting-item items-start md:items-center border-t border-blue-200 dark:border-blue-700 pt-4 mt-4">
                 <label for="temperature-range" class="setting-label flex items-center">
                    Temperature
                     <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="w-4 h-4 ml-1 text-blue-400 dark:text-blue-500 cursor-help feather feather-info"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>
                </label>
                 <div class="flex-1 flex flex-col sm:flex-row items-center gap-4 w-full">
                    <input id="temperature-range" :value="config.temperature" @input="handleNumberInput('temperature', $event.target.value)" type="range" min="0" max="2" step="0.01" class="range-input flex-grow" :disabled="isDisabled">
                    <input id="temperature-number" :value="config.temperature" @input="handleNumberInput('temperature', $event.target.value)" type="number" min="0" max="2" step="0.01" class="input-sm w-24 text-center" :disabled="isDisabled">
                 </div>
            </div>

             <div class="setting-item items-start md:items-center border-t border-blue-200 dark:border-blue-700 pt-4 mt-4">
                 <label for="n_predict-range" class="setting-label flex items-center">
                    Max New Tokens
                     <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="w-4 h-4 ml-1 text-blue-400 dark:text-blue-500 cursor-help feather feather-info"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>
                </label>
                 <div class="flex-1 flex flex-col sm:flex-row items-center gap-4 w-full">
                     <input id="n_predict-range" :value="config.n_predict" @input="handleNumberInput('n_predict', $event.target.value, true)" type="range" min="32" max="8192" step="32" class="range-input flex-grow" :disabled="isDisabled">
                     <input id="n_predict-number" :value="config.n_predict" @input="handleNumberInput('n_predict', $event.target.value, true)" type="number" min="32" max="8192" step="32" class="input-sm w-24 text-center" :disabled="isDisabled">
                 </div>
             </div>

             <div class="setting-item items-start md:items-center border-t border-blue-200 dark:border-blue-700 pt-4 mt-4">
                <label for="top_k-range" class="setting-label flex items-center">
                     Top-K Sampling
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="w-4 h-4 ml-1 text-blue-400 dark:text-blue-500 cursor-help feather feather-info"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>
                 </label>
                 <div class="flex-1 flex flex-col sm:flex-row items-center gap-4 w-full">
                    <input id="top_k-range" :value="config.top_k" @input="handleNumberInput('top_k', $event.target.value, true)" type="range" min="0" max="100" step="1" class="range-input flex-grow" :disabled="isDisabled">
                    <input id="top_k-number" :value="config.top_k" @input="handleNumberInput('top_k', $event.target.value, true)" type="number" min="0" max="100" step="1" class="input-sm w-24 text-center" :disabled="isDisabled">
                 </div>
             </div>

             <div class="setting-item items-start md:items-center border-t border-blue-200 dark:border-blue-700 pt-4 mt-4">
                 <label for="top_p-range" class="setting-label flex items-center">
                    Top-P (Nucleus) Sampling
                     <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="w-4 h-4 ml-1 text-blue-400 dark:text-blue-500 cursor-help feather feather-info"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>
                 </label>
                 <div class="flex-1 flex flex-col sm:flex-row items-center gap-4 w-full">
                     <input id="top_p-range" :value="config.top_p" @input="handleNumberInput('top_p', $event.target.value)" type="range" min="0" max="1" step="0.01" class="range-input flex-grow" :disabled="isDisabled">
                     <input id="top_p-number" :value="config.top_p" @input="handleNumberInput('top_p', $event.target.value)" type="number" min="0" max="1" step="0.01" class="input-sm w-24 text-center" :disabled="isDisabled">
                </div>
             </div>

             <div class="setting-item items-start md:items-center border-t border-blue-200 dark:border-blue-700 pt-4 mt-4">
                <label for="repeat_penalty-range" class="setting-label flex items-center">
                     Repeat Penalty
                     <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="w-4 h-4 ml-1 text-blue-400 dark:text-blue-500 cursor-help feather feather-info"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>
                </label>
                 <div class="flex-1 flex flex-col sm:flex-row items-center gap-4 w-full">
                    <input id="repeat_penalty-range" :value="config.repeat_penalty" @input="handleNumberInput('repeat_penalty', $event.target.value)" type="range" min="0.5" max="2.0" step="0.01" class="range-input flex-grow" :disabled="isDisabled">
                    <input id="repeat_penalty-number" :value="config.repeat_penalty" @input="handleNumberInput('repeat_penalty', $event.target.value)" type="number" min="0.5" max="2.0" step="0.01" class="input-sm w-24 text-center" :disabled="isDisabled">
                 </div>
             </div>

            <div class="setting-item items-start md:items-center border-t border-blue-200 dark:border-blue-700 pt-4 mt-4">
                 <label for="repeat_last_n-range" class="setting-label flex items-center">
                    Repeat Penalty Lookback
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="w-4 h-4 ml-1 text-blue-400 dark:text-blue-500 cursor-help feather feather-info"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>
                 </label>
                 <div class="flex-1 flex flex-col sm:flex-row items-center gap-4 w-full">
                    <input id="repeat_last_n-range" :value="config.repeat_last_n" @input="handleNumberInput('repeat_last_n', $event.target.value, true)" type="range" min="0" max="512" step="8" class="range-input flex-grow" :disabled="isDisabled">
                    <input id="repeat_last_n-number" :value="config.repeat_last_n" @input="handleNumberInput('repeat_last_n', $event.target.value, true)" type="number" min="0" max="512" step="8" class="input-sm w-24 text-center" :disabled="isDisabled">
                 </div>
             </div>
        </div>
    </div>
</template>

<script>
import { nextTick } from 'vue';
import feather from 'feather-icons';
import ToggleSwitch from '@/components/ToggleSwitch.vue';

export default {
    name: 'ModelConfigSettings',
    components: {
        ToggleSwitch
    },
    props: {
        config: { type: Object, required: true }, // Receive the editable config copy
        loading: { type: Boolean, default: false }
    },
    emits: ['setting-updated'], // Declare the event used to notify parent
    computed: {
        isDisabled() {
            // Read from the config prop
            return !this.config.override_personality_model_parameters;
        }
    },
    methods: {
        updateValue(key, value) {
            // Emit the update event for the parent to handle
            this.$emit('setting-updated', { key, value: value });
        },
        handleNumberInput(key, value, isInt = false) {
            // Parse the value
            let parsedValue = isInt ? parseInt(value) : parseFloat(value);

            // Handle specific case for seed allowing -1 and intermediate '-'
            if (key === 'seed') {
                 if (String(value) === '-') {
                    // Allow '-' to be typed, don't emit yet
                    return;
                }
                if (isNaN(parsedValue)) {
                    parsedValue = -1; // Default to random if invalid
                } else if (parsedValue < -1) {
                    parsedValue = -1; // Enforce minimum
                }
            }
             // Check for NaN after parsing (except for the allowed '-' case for seed)
            else if (isNaN(parsedValue)) {
                 // Maybe show a validation message or just don't emit?
                 // For now, we won't emit NaN values.
                 console.warn(`Attempted to set invalid number for ${key}:`, value);
                 return;
            }

            // Emit the parsed value
            this.updateValue(key, parsedValue);
        },
        replaceFeatherIcons() {
             nextTick(() => {
                try { feather.replace(); } catch (e) {}
             });
        }
    },
    mounted() {
        this.replaceFeatherIcons();
    },
    updated() {
        this.replaceFeatherIcons();
    }
}
</script>

<style scoped>
.setting-item { @apply flex flex-col md:flex-row md:items-center gap-2 md:gap-4 py-2; }
.setting-label { @apply block text-sm font-medium text-gray-700 dark:text-gray-300 w-full md:w-1/3 lg:w-1/4 flex-shrink-0; }
.input-sm { @apply block w-full px-2.5 py-1.5 text-sm bg-gray-50 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 focus:border-blue-500 dark:focus:ring-offset-gray-900 sm:text-sm disabled:opacity-50 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500; }
.range-input { @apply w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-600 accent-blue-600 dark:accent-blue-500 disabled:opacity-50; }
.toggle-item { @apply flex items-center justify-between p-3 hover:bg-gray-50 dark:hover:bg-gray-700 rounded-lg transition-colors; }
.toggle-label { @apply text-sm font-medium text-gray-700 dark:text-gray-300 cursor-pointer flex-1 mr-4; }
.toggle-description { @apply block text-xs text-gray-500 dark:text-gray-400 mt-1 font-normal; }
.panels-color { @apply bg-white dark:bg-gray-800; }
</style>