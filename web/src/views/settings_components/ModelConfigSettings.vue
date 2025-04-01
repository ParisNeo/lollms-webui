<template>
    <div class="user-settings-panel space-y-6">
        <h2 class="text-xl font-semibold text-blue-800 dark:text-blue-100 border-b border-blue-300 dark:border-blue-600 pb-2">
            Model Generation Parameters
        </h2>

         <p class="text-sm text-blue-600 dark:text-blue-400 mb-4">
            Adjust the core parameters that influence how the AI generates text. These settings can be overridden by specific personalities unless the option below is checked.
        </p>

        <!-- Override Personality Toggle -->
        <div class="toggle-item !justify-start gap-4 border border-blue-200 dark:border-blue-700 rounded-lg p-3 panels-color"> <!-- Use toggle-item and add panel color -->
            <ToggleSwitch
                id="override_personality_model_parameters"
                :checked="$store.state.config.override_personality_model_parameters"
                @update:checked="updateBoolean('override_personality_model_parameters', $event)"
            />
            <label for="override_personality_model_parameters" class="toggle-label !flex-none">
                Override Personality Parameters
                 <span class="toggle-description">Force the use of these global parameters, ignoring any settings defined within the selected personality.</span>
            </label>
        </div>

        <!-- Parameter Controls -->
        <div :class="['space-y-5 pt-4', isDisabled ? 'opacity-50 pointer-events-none' : '']">
            <!-- Seed -->
            <div class="setting-item">
                <label for="seed" class="setting-label flex items-center">
                    Seed
                     <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="w-4 h-4 ml-1 text-blue-400 dark:text-blue-500 cursor-help feather feather-info"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>
                 </label>
                <input
                    type="number"
                    id="seed"
                    :value="$store.state.config.seed"
                    @input="updateValue('seed', parseInt($event.target.value))"
                    class="input-sm w-full md:w-32"
                    step="1"
                    placeholder="-1"
                    :disabled="isDisabled"
                 >
            </div>

            <!-- Temperature -->
            <div class="setting-item items-start md:items-center border-t border-blue-200 dark:border-blue-700 pt-4 mt-4">
                 <label for="temperature-range" class="setting-label flex items-center">
                    Temperature
                     <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="w-4 h-4 ml-1 text-blue-400 dark:text-blue-500 cursor-help feather feather-info"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>
                </label>
                 <div class="flex-1 flex flex-col sm:flex-row items-center gap-4 w-full">
                    <input id="temperature-range" :value="$store.state.config.temperature" @input="updateValue('temperature', parseFloat($event.target.value))" type="range" min="0" max="2" step="0.01" class="range-input flex-grow" :disabled="isDisabled">
                    <input id="temperature-number" :value="$store.state.config.temperature" @input="updateValue('temperature', parseFloat($event.target.value))" type="number" min="0" max="2" step="0.01" class="input-sm w-24 text-center" :disabled="isDisabled">
                 </div>
            </div>

            <!-- N Predict (Max Tokens) -->
             <div class="setting-item items-start md:items-center border-t border-blue-200 dark:border-blue-700 pt-4 mt-4">
                 <label for="n_predict-range" class="setting-label flex items-center">
                    Max New Tokens
                     <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="w-4 h-4 ml-1 text-blue-400 dark:text-blue-500 cursor-help feather feather-info"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>
                </label>
                 <div class="flex-1 flex flex-col sm:flex-row items-center gap-4 w-full">
                     <input id="n_predict-range" :value="$store.state.config.n_predict" @input="updateValue('n_predict', parseInt($event.target.value))" type="range" min="32" max="8192" step="32" class="range-input flex-grow" :disabled="isDisabled">
                     <input id="n_predict-number" :value="$store.state.config.n_predict" @input="updateValue('n_predict', parseInt($event.target.value))" type="number" min="32" max="8192" step="32" class="input-sm w-24 text-center" :disabled="isDisabled">
                 </div>
             </div>

             <!-- Top-K -->
             <div class="setting-item items-start md:items-center border-t border-blue-200 dark:border-blue-700 pt-4 mt-4">
                <label for="top_k-range" class="setting-label flex items-center">
                     Top-K Sampling
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="w-4 h-4 ml-1 text-blue-400 dark:text-blue-500 cursor-help feather feather-info"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>
                 </label>
                 <div class="flex-1 flex flex-col sm:flex-row items-center gap-4 w-full">
                    <input id="top_k-range" :value="$store.state.config.top_k" @input="updateValue('top_k', parseInt($event.target.value))" type="range" min="0" max="100" step="1" class="range-input flex-grow" :disabled="isDisabled">
                    <input id="top_k-number" :value="$store.state.config.top_k" @input="updateValue('top_k', parseInt($event.target.value))" type="number" min="0" max="100" step="1" class="input-sm w-24 text-center" :disabled="isDisabled">
                 </div>
             </div>

             <!-- Top-P -->
             <div class="setting-item items-start md:items-center border-t border-blue-200 dark:border-blue-700 pt-4 mt-4">
                 <label for="top_p-range" class="setting-label flex items-center">
                    Top-P (Nucleus) Sampling
                     <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="w-4 h-4 ml-1 text-blue-400 dark:text-blue-500 cursor-help feather feather-info"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>
                 </label>
                 <div class="flex-1 flex flex-col sm:flex-row items-center gap-4 w-full">
                     <input id="top_p-range" :value="$store.state.config.top_p" @input="updateValue('top_p', parseFloat($event.target.value))" type="range" min="0" max="1" step="0.01" class="range-input flex-grow" :disabled="isDisabled">
                     <input id="top_p-number" :value="$store.state.config.top_p" @input="updateValue('top_p', parseFloat($event.target.value))" type="number" min="0" max="1" step="0.01" class="input-sm w-24 text-center" :disabled="isDisabled">
                </div>
             </div>

             <!-- Repeat Penalty -->
             <div class="setting-item items-start md:items-center border-t border-blue-200 dark:border-blue-700 pt-4 mt-4">
                <label for="repeat_penalty-range" class="setting-label flex items-center">
                     Repeat Penalty
                     <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="w-4 h-4 ml-1 text-blue-400 dark:text-blue-500 cursor-help feather feather-info"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>
                </label>
                 <div class="flex-1 flex flex-col sm:flex-row items-center gap-4 w-full">
                    <input id="repeat_penalty-range" :value="$store.state.config.repeat_penalty" @input="updateValue('repeat_penalty', parseFloat($event.target.value))" type="range" min="0.5" max="2.0" step="0.01" class="range-input flex-grow" :disabled="isDisabled">
                    <input id="repeat_penalty-number" :value="$store.state.config.repeat_penalty" @input="updateValue('repeat_penalty', parseFloat($event.target.value))" type="number" min="0.5" max="2.0" step="0.01" class="input-sm w-24 text-center" :disabled="isDisabled">
                 </div>
             </div>

            <!-- Repeat Last N -->
            <div class="setting-item items-start md:items-center border-t border-blue-200 dark:border-blue-700 pt-4 mt-4">
                 <label for="repeat_last_n-range" class="setting-label flex items-center">
                    Repeat Penalty Lookback
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="w-4 h-4 ml-1 text-blue-400 dark:text-blue-500 cursor-help feather feather-info"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>
                 </label>
                 <div class="flex-1 flex flex-col sm:flex-row items-center gap-4 w-full">
                    <input id="repeat_last_n-range" :value="$store.state.config.repeat_last_n" @input="updateValue('repeat_last_n', parseInt($event.target.value))" type="range" min="0" max="512" step="8" class="range-input flex-grow" :disabled="isDisabled">
                    <input id="repeat_last_n-number" :value="$store.state.config.repeat_last_n" @input="updateValue('repeat_last_n', parseInt($event.target.value))" type="number" min="0" max="512" step="8" class="input-sm w-24 text-center" :disabled="isDisabled">
                 </div>
             </div>
        </div>
    </div>
</template>

<script>
import { nextTick } from 'vue'; // Import nextTick
import feather from 'feather-icons';
import ToggleSwitch from '@/components/ToggleSwitch.vue';

export default {
    name: 'ModelGenerationParameters',
    components: {
        ToggleSwitch
    },
    props: {
        loading: { // Although not directly used in this template conversion, keeping it for completeness
            type: Boolean,
            default: false
        }
    },
    emits: ['update:setting'],
    computed: {
        // Computed property to check if parameters should be disabled
        isDisabled() {
            // Access props using 'this' in Options API
            return !this.$store.state.config.override_personality_model_parameters;
        }
    },
    methods: {
        updateValue(key, value) {
            // Ensure correct type (Number for ranges/numbers, leave Seed as potentially string/number)
            let finalValue = value;
             if (key !== 'seed' && typeof value !== 'boolean') {
                 finalValue = Number(value);
                 if (isNaN(finalValue)) {
                     console.warn(`Invalid number input for ${key}:`, value);
                     // Optionally revert or set to a default if NaN
                     // For now, we let it pass, backend might handle validation
                    finalValue = value; // Keep original if parse fails, might be intermediate typing
                }
            } else if (key === 'seed') {
                // Allow -1 or positive integers for seed
                finalValue = parseInt(value);
                 if (isNaN(finalValue) && String(value) !== '-') { // Allow typing '-' for negative. Use String() to handle the raw input value safely.
                     finalValue = -1; // Default to random if invalid input
                } else if (String(value) === '-') {
                    finalValue = '-'; // Allow '-' intermediate state
                } else if (finalValue < -1) {
                    finalValue = -1; // Enforce minimum of -1
                }
            }

            // Avoid emitting NaN during intermediate number input states
            if (key !== 'seed' && typeof finalValue === 'number' && isNaN(finalValue)) {
                 return;
            }
            if (key === 'seed' && finalValue === '-') {
                return; // Don't emit just the hyphen
            }

            // Use 'this.$emit' in Options API
            this.$emit('update:setting', { key, value: finalValue });
        },

        updateBoolean(key, value) {
             // Use 'this.$emit' in Options API
            this.$emit('update:setting', { key, value: Boolean(value) });
        },

        // Method to replace feather icons, called in lifecycle hooks
        replaceFeatherIcons() {
             nextTick(() => {
                feather.replace();
             });
        }
    },
    mounted() {
        // Call replaceFeatherIcons on mount
        this.replaceFeatherIcons();
    },
    updated() {
        // Call replaceFeatherIcons on update to handle potential dynamic changes
        this.replaceFeatherIcons();
    }
}
</script>

<style scoped>
/* Using shared styles - these remain unchanged */
.setting-item {
    @apply flex flex-col md:flex-row md:items-center gap-2 md:gap-4 py-2;
}
.setting-label {
    @apply block text-sm font-medium text-gray-700 dark:text-gray-300 w-full md:w-1/3 lg:w-1/4 flex-shrink-0;
}
.input-field-sm {
     @apply block w-full px-2.5 py-1.5 text-sm bg-gray-50 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-primary focus:border-primary disabled:opacity-50;
}
.range-input {
    @apply w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-600 accent-primary disabled:opacity-50;
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
</style>