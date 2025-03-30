<template>
    <div class="space-y-6 p-4 md:p-6 bg-white dark:bg-gray-800 rounded-lg shadow-md border border-gray-200 dark:border-gray-700">
        <h2 class="text-xl font-semibold text-gray-800 dark:text-gray-200 border-b border-gray-200 dark:border-gray-700 pb-2">
            Internet Search
        </h2>

         <p class="text-sm text-gray-500 dark:text-gray-400 mb-4">
            Configure how LoLLMs interacts with the internet to answer questions or find information. Requires a model capable of function calling or specific instruction following.
        </p>

        <!-- Internet Search Toggles -->
        <section class="space-y-4 p-4 border border-gray-200 dark:border-gray-600 rounded-lg">
            <h3 class="text-lg font-medium text-gray-700 dark:text-gray-300 mb-3">Activation & Behavior</h3>

            <!-- Activate Internet Search -->
            <div class="toggle-item">
                <label for="activate_internet_search" class="toggle-label">
                    Enable Automatic Internet Search
                     <span class="toggle-description">Allow the AI to decide when to search the internet based on the prompt.</span>
                </label>
                <ToggleSwitch id="activate_internet_search" :checked="config.activate_internet_search" @update:checked="updateBoolean('activate_internet_search', $event)" />
            </div>

             <!-- Activate Search Decision -->
            <div class="toggle-item" :class="{ 'opacity-50 pointer-events-none': !config.activate_internet_search }">
                <label for="internet_activate_search_decision" class="toggle-label">
                    Enable Explicit Search Decision
                     <span class="toggle-description">Make the AI explicitly state whether it needs to search the internet before performing the search.</span>
                </label>
                <ToggleSwitch id="internet_activate_search_decision" :checked="config.internet_activate_search_decision" @update:checked="updateBoolean('internet_activate_search_decision', $event)" :disabled="!config.activate_internet_search"/>
            </div>

            <!-- Activate Pages Judgement -->
            <div class="toggle-item" :class="{ 'opacity-50 pointer-events-none': !config.activate_internet_search }">
                <label for="activate_internet_pages_judgement" class="toggle-label">
                    Enable Search Result Evaluation
                     <span class="toggle-description">Allow the AI to evaluate the relevance and quality of search result snippets before using them.</span>
                </label>
                <ToggleSwitch id="activate_internet_pages_judgement" :checked="config.activate_internet_pages_judgement" @update:checked="updateBoolean('activate_internet_pages_judgement', $event)" :disabled="!config.activate_internet_search"/>
            </div>

            <!-- Activate Quick Search -->
            <div class="toggle-item" :class="{ 'opacity-50 pointer-events-none': !config.activate_internet_search }">
                <label for="internet_quick_search" class="toggle-label">
                    Enable Quick Search
                     <span class="toggle-description">Perform a faster search potentially using fewer results or less processing, might be less accurate.</span>
                </label>
                 <ToggleSwitch id="internet_quick_search" :checked="config.internet_quick_search" @update:checked="updateBoolean('internet_quick_search', $event)" :disabled="!config.activate_internet_search"/>
            </div>
        </section>

        <!-- Internet Search Parameters -->
        <section :class="['space-y-4 p-4 border border-gray-200 dark:border-gray-600 rounded-lg', !config.activate_internet_search ? 'opacity-50 pointer-events-none' : '']">
            <h3 class="text-lg font-medium text-gray-700 dark:text-gray-300 mb-3">Search Parameters</h3>

            <!-- Number of Search Pages/Results -->
            <div class="setting-item">
                <label for="internet_nb_search_pages" class="setting-label">
                    Number of Search Results
                     <span class="block text-xs font-normal text-gray-500 dark:text-gray-400 mt-1">Controls how many search result snippets are initially retrieved.</span>
                </label>
                <div class="flex-1 flex items-center gap-4">
                    <input id="internet_nb_search_pages-range" :value="config.internet_nb_search_pages" @input="updateValue('internet_nb_search_pages', parseInt($event.target.value))" type="range" min="1" max="20" step="1" class="range-input" :disabled="!config.activate_internet_search">
                    <input id="internet_nb_search_pages-number" :value="config.internet_nb_search_pages" @input="updateValue('internet_nb_search_pages', parseInt($event.target.value))" type="number" min="1" max="20" step="1" class="input-field-sm w-20 text-center" :disabled="!config.activate_internet_search">
                </div>
            </div>

             <!-- Vectorization Chunk Size -->
            <div class="setting-item">
                <label for="internet_vectorization_chunk_size" class="setting-label">
                     Content Chunk Size
                    <span class="block text-xs font-normal text-gray-500 dark:text-gray-400 mt-1">Size of text chunks when processing content from searched web pages (if applicable).</span>
                 </label>
                <div class="flex-1 flex items-center gap-4">
                     <input id="internet_vectorization_chunk_size-range" :value="config.internet_vectorization_chunk_size" @input="updateValue('internet_vectorization_chunk_size', parseInt($event.target.value))" type="range" min="100" max="1000" step="50" class="range-input" :disabled="!config.activate_internet_search">
                    <input id="internet_vectorization_chunk_size-number" :value="config.internet_vectorization_chunk_size" @input="updateValue('internet_vectorization_chunk_size', parseInt($event.target.value))" type="number" min="100" max="1000" step="50" class="input-field-sm w-20 text-center" :disabled="!config.activate_internet_search">
                 </div>
            </div>

             <!-- Vectorization Overlap Size -->
             <div class="setting-item">
                <label for="internet_vectorization_overlap_size" class="setting-label">
                     Content Overlap Size
                     <span class="block text-xs font-normal text-gray-500 dark:text-gray-400 mt-1">Overlap between text chunks when processing web page content.</span>
                </label>
                <div class="flex-1 flex items-center gap-4">
                     <input id="internet_vectorization_overlap_size-range" :value="config.internet_vectorization_overlap_size" @input="updateValue('internet_vectorization_overlap_size', parseInt($event.target.value))" type="range" min="0" max="200" step="10" class="range-input" :disabled="!config.activate_internet_search">
                     <input id="internet_vectorization_overlap_size-number" :value="config.internet_vectorization_overlap_size" @input="updateValue('internet_vectorization_overlap_size', parseInt($event.target.value))" type="number" min="0" max="200" step="10" class="input-field-sm w-20 text-center" :disabled="!config.activate_internet_search">
                </div>
             </div>

             <!-- Number of Vectorization Chunks to Use -->
             <div class="setting-item">
                <label for="internet_vectorization_nb_chunks" class="setting-label">
                     Number of Content Chunks to Use
                     <span class="block text-xs font-normal text-gray-500 dark:text-gray-400 mt-1">Maximum number of processed text chunks from web pages to include in the context.</span>
                </label>
                 <div class="flex-1 flex items-center gap-4">
                     <input id="internet_vectorization_nb_chunks-range" :value="config.internet_vectorization_nb_chunks" @input="updateValue('internet_vectorization_nb_chunks', parseInt($event.target.value))" type="range" min="1" max="20" step="1" class="range-input" :disabled="!config.activate_internet_search">
                     <input id="internet_vectorization_nb_chunks-number" :value="config.internet_vectorization_nb_chunks" @input="updateValue('internet_vectorization_nb_chunks', parseInt($event.target.value))" type="number" min="1" max="20" step="1" class="input-field-sm w-20 text-center" :disabled="!config.activate_internet_search">
                </div>
            </div>

        </section>

    </div>
</template>

<script setup>
import { defineProps, defineEmits, onMounted, nextTick } from 'vue';
import feather from 'feather-icons';
import ToggleSwitch from '@/components/ToggleSwitch.vue';

// Props definition
const props = defineProps({
    config: { type: Object, required: true },
    loading: { type: Boolean, default: false }
});

// Emits definition
const emit = defineEmits(['update:setting']);

// --- Methods ---
const updateValue = (key, value) => {
    // Ensure numeric values from range/number inputs are parsed correctly
    const numericKeys = [
        'internet_nb_search_pages',
        'internet_vectorization_chunk_size',
        'internet_vectorization_overlap_size',
        'internet_vectorization_nb_chunks'
    ];
    const finalValue = numericKeys.includes(key) ? parseInt(value) || 0 : value; // Default to 0 if parse fails
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

</script>

<style scoped>
/* Using shared styles defined in previous components or globally */
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