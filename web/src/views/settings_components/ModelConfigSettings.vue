<template>
    <div class="space-y-6 p-4 md:p-6 bg-white dark:bg-gray-800 rounded-lg shadow-md border border-gray-200 dark:border-gray-700">
        <h2 class="text-xl font-semibold text-gray-800 dark:text-gray-200 border-b border-gray-200 dark:border-gray-700 pb-2">
            Model Generation Parameters
        </h2>

         <p class="text-sm text-gray-500 dark:text-gray-400 mb-4">
            Adjust the core parameters that influence how the AI generates text. These settings can be overridden by specific personalities unless the option below is checked.
        </p>

        <!-- Override Personality Toggle -->
        <div class="toggle-item !justify-start gap-4 border border-gray-200 dark:border-gray-600 rounded-lg p-3">
            <ToggleSwitch
                id="override_personality_model_parameters"
                :checked="config.override_personality_model_parameters"
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
                     <i data-feather="info" class="w-4 h-4 ml-1 text-gray-400 cursor-help" title="Controls randomness. Set to -1 for random, or a specific number for reproducible results."></i>
                 </label>
                <input
                    type="number"
                    id="seed"
                    :value="config.seed"
                    @input="updateValue('seed', parseInt($event.target.value))"
                    class="input-field-sm w-full md:w-32"
                    step="1"
                    placeholder="-1"
                    :disabled="isDisabled"
                 >
            </div>

            <!-- Temperature -->
            <div class="setting-item items-start md:items-center">
                 <label for="temperature-range" class="setting-label flex items-center">
                    Temperature
                     <i data-feather="info" class="w-4 h-4 ml-1 text-gray-400 cursor-help" title="Controls randomness. Lower values (e.g., 0.2) make output more focused and deterministic, higher values (e.g., 0.8) make it more creative and random."></i>
                </label>
                 <div class="flex-1 flex flex-col sm:flex-row items-center gap-4 w-full">
                    <input id="temperature-range" :value="config.temperature" @input="updateValue('temperature', parseFloat($event.target.value))" type="range" min="0" max="2" step="0.01" class="range-input flex-grow" :disabled="isDisabled">
                    <input id="temperature-number" :value="config.temperature" @input="updateValue('temperature', parseFloat($event.target.value))" type="number" min="0" max="2" step="0.01" class="input-field-sm w-24 text-center" :disabled="isDisabled">
                 </div>
            </div>

            <!-- N Predict (Max Tokens) -->
             <div class="setting-item items-start md:items-center">
                 <label for="n_predict-range" class="setting-label flex items-center">
                    Max New Tokens
                     <i data-feather="info" class="w-4 h-4 ml-1 text-gray-400 cursor-help" title="Maximum number of tokens the model is allowed to generate in a single response."></i>
                </label>
                 <div class="flex-1 flex flex-col sm:flex-row items-center gap-4 w-full">
                     <input id="n_predict-range" :value="config.n_predict" @input="updateValue('n_predict', parseInt($event.target.value))" type="range" min="32" max="8192" step="32" class="range-input flex-grow" :disabled="isDisabled">
                     <input id="n_predict-number" :value="config.n_predict" @input="updateValue('n_predict', parseInt($event.target.value))" type="number" min="32" max="8192" step="32" class="input-field-sm w-24 text-center" :disabled="isDisabled">
                 </div>
             </div>

             <!-- Top-K -->
             <div class="setting-item items-start md:items-center">
                <label for="top_k-range" class="setting-label flex items-center">
                     Top-K Sampling
                    <i data-feather="info" class="w-4 h-4 ml-1 text-gray-400 cursor-help" title="Limits generation to the K most likely next tokens. Reduces repetition but can make output less creative. 0 disables it."></i>
                 </label>
                 <div class="flex-1 flex flex-col sm:flex-row items-center gap-4 w-full">
                    <input id="top_k-range" :value="config.top_k" @input="updateValue('top_k', parseInt($event.target.value))" type="range" min="0" max="100" step="1" class="range-input flex-grow" :disabled="isDisabled">
                    <input id="top_k-number" :value="config.top_k" @input="updateValue('top_k', parseInt($event.target.value))" type="number" min="0" max="100" step="1" class="input-field-sm w-24 text-center" :disabled="isDisabled">
                 </div>
             </div>

             <!-- Top-P -->
             <div class="setting-item items-start md:items-center">
                 <label for="top_p-range" class="setting-label flex items-center">
                    Top-P (Nucleus) Sampling
                     <i data-feather="info" class="w-4 h-4 ml-1 text-gray-400 cursor-help" title="Considers only the most probable tokens whose cumulative probability exceeds P. Allows for dynamic vocabulary size. 1.0 disables it. Common values: 0.9, 0.95."></i>
                 </label>
                 <div class="flex-1 flex flex-col sm:flex-row items-center gap-4 w-full">
                     <input id="top_p-range" :value="config.top_p" @input="updateValue('top_p', parseFloat($event.target.value))" type="range" min="0" max="1" step="0.01" class="range-input flex-grow" :disabled="isDisabled">
                     <input id="top_p-number" :value="config.top_p" @input="updateValue('top_p', parseFloat($event.target.value))" type="number" min="0" max="1" step="0.01" class="input-field-sm w-24 text-center" :disabled="isDisabled">
                </div>
             </div>

             <!-- Repeat Penalty -->
             <div class="setting-item items-start md:items-center">
                <label for="repeat_penalty-range" class="setting-label flex items-center">
                     Repeat Penalty
                     <i data-feather="info" class="w-4 h-4 ml-1 text-gray-400 cursor-help" title="Penalizes tokens that have appeared recently. Higher values (e.g., 1.1, 1.2) reduce repetition. 1.0 disables it."></i>
                </label>
                 <div class="flex-1 flex flex-col sm:flex-row items-center gap-4 w-full">
                    <input id="repeat_penalty-range" :value="config.repeat_penalty" @input="updateValue('repeat_penalty', parseFloat($event.target.value))" type="range" min="0.5" max="2.0" step="0.01" class="range-input flex-grow" :disabled="isDisabled">
                    <input id="repeat_penalty-number" :value="config.repeat_penalty" @input="updateValue('repeat_penalty', parseFloat($event.target.value))" type="number" min="0.5" max="2.0" step="0.01" class="input-field-sm w-24 text-center" :disabled="isDisabled">
                 </div>
             </div>

            <!-- Repeat Last N -->
            <div class="setting-item items-start md:items-center">
                 <label for="repeat_last_n-range" class="setting-label flex items-center">
                    Repeat Penalty Lookback
                    <i data-feather="info" class="w-4 h-4 ml-1 text-gray-400 cursor-help" title="Number of recent tokens to consider when applying the repeat penalty. 0 disables considering previous tokens specifically for penalty."></i>
                 </label>
                 <div class="flex-1 flex flex-col sm:flex-row items-center gap-4 w-full">
                    <input id="repeat_last_n-range" :value="config.repeat_last_n" @input="updateValue('repeat_last_n', parseInt($event.target.value))" type="range" min="0" max="512" step="8" class="range-input flex-grow" :disabled="isDisabled">
                    <input id="repeat_last_n-number" :value="config.repeat_last_n" @input="updateValue('repeat_last_n', parseInt($event.target.value))" type="number" min="0" max="512" step="8" class="input-field-sm w-24 text-center" :disabled="isDisabled">
                 </div>
             </div>
        </div>
    </div>
</template>

<script setup>
import { defineProps, defineEmits, computed, onMounted, nextTick } from 'vue';
import feather from 'feather-icons';
import ToggleSwitch from '@/components/ToggleSwitch.vue';

// Props definition
const props = defineProps({
    config: { type: Object, required: true },
    loading: { type: Boolean, default: false }
});

// Emits definition
const emit = defineEmits(['update:setting']);

// Computed property to check if parameters should be disabled
const isDisabled = computed(() => {
    return !props.config.override_personality_model_parameters;
});

// --- Methods ---
const updateValue = (key, value) => {
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
         if (isNaN(finalValue) && value !== '-') { // Allow typing '-' for negative
             finalValue = -1; // Default to random if invalid input
        } else if (value === '-') {
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


    emit('update:setting', { key, value: finalValue });
};

const updateBoolean = (key, value) => {
    emit('update:setting', { key, value: Boolean(value) });
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
/* Using shared styles */
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