<template>
    <div class="user-settings-panel space-y-6">
        <h2 class="text-xl font-semibold text-blue-800 dark:text-blue-100 border-b border-blue-300 dark:border-blue-600 pb-2">
            Internet Search
        </h2>

         <p class="text-sm text-blue-600 dark:text-blue-400 mb-4">
            Configure how LoLLMs interacts with the internet to answer questions or find information. Requires a model capable of function calling or specific instruction following.
        </p>

        <section class="space-y-4 p-4 border border-blue-300 dark:border-blue-600 rounded-lg panels-color">
            <h3 class="text-lg font-medium text-blue-700 dark:text-blue-300 mb-3">Activation & Behavior</h3>

            <div class="toggle-item">
                <label for="activate_internet_search" class="toggle-label">
                    Enable Automatic Internet Search
                     <span class="toggle-description">Allow the AI to decide when to search the internet based on the prompt.</span>
                </label>
                <ToggleSwitch id="activate_internet_search" :checked="config.activate_internet_search" @update:checked="updateValue('activate_internet_search', $event)" />
            </div>

            <div class="toggle-item" :class="{ 'opacity-50 pointer-events-none': !config.activate_internet_search }">
                <label for="internet_activate_search_decision" class="toggle-label">
                    Enable Explicit Search Decision
                     <span class="toggle-description">Make the AI explicitly state whether it needs to search the internet before performing the search.</span>
                </label>
                <ToggleSwitch id="internet_activate_search_decision" :checked="config.internet_activate_search_decision" @update:checked="updateValue('internet_activate_search_decision', $event)" :disabled="!config.activate_internet_search"/>
            </div>

            <div class="toggle-item" :class="{ 'opacity-50 pointer-events-none': !config.activate_internet_search }">
                <label for="activate_internet_pages_judgement" class="toggle-label">
                    Enable Search Result Evaluation
                     <span class="toggle-description">Allow the AI to evaluate the relevance and quality of search result snippets before using them.</span>
                </label>
                <ToggleSwitch id="activate_internet_pages_judgement" :checked="config.activate_internet_pages_judgement" @update:checked="updateValue('activate_internet_pages_judgement', $event)" :disabled="!config.activate_internet_search"/>
            </div>

            <div class="toggle-item" :class="{ 'opacity-50 pointer-events-none': !config.activate_internet_search }">
                <label for="internet_quick_search" class="toggle-label">
                    Enable Quick Search
                     <span class="toggle-description">Perform a faster search potentially using fewer results or less processing, might be less accurate.</span>
                </label>
                 <ToggleSwitch id="internet_quick_search" :checked="config.internet_quick_search" @update:checked="updateValue('internet_quick_search', $event)" :disabled="!config.activate_internet_search"/>
            </div>
        </section>

        <section :class="['space-y-4 p-4 border border-blue-300 dark:border-blue-600 rounded-lg panels-color', !config.activate_internet_search ? 'opacity-50 pointer-events-none' : '']">
            <h3 class="text-lg font-medium text-blue-700 dark:text-blue-300 mb-3">Search Parameters</h3>

            <div class="setting-item">
                <label for="internet_nb_search_pages" class="setting-label">
                    Number of Search Results
                     <span class="block text-xs font-normal text-blue-500 dark:text-blue-400 mt-1">Controls how many search result snippets are initially retrieved.</span>
                </label>
                <div class="flex-1 flex items-center gap-4">
                    <input id="internet_nb_search_pages-range" :value="config.internet_nb_search_pages" @input="handleNumberInput('internet_nb_search_pages', $event.target.value, true)" type="range" min="1" max="20" step="1" class="range-input" :disabled="!config.activate_internet_search">
                    <input id="internet_nb_search_pages-number" :value="config.internet_nb_search_pages" @input="handleNumberInput('internet_nb_search_pages', $event.target.value, true)" type="number" min="1" max="20" step="1" class="input-sm w-20 text-center" :disabled="!config.activate_internet_search">
                </div>
            </div>

            <div class="setting-item">
                <label for="internet_vectorization_chunk_size" class="setting-label">
                     Content Chunk Size
                    <span class="block text-xs font-normal text-blue-500 dark:text-blue-400 mt-1">Size of text chunks when processing content from searched web pages (if applicable).</span>
                 </label>
                <div class="flex-1 flex items-center gap-4">
                     <input id="internet_vectorization_chunk_size-range" :value="config.internet_vectorization_chunk_size" @input="handleNumberInput('internet_vectorization_chunk_size', $event.target.value, true)" type="range" min="100" max="1000" step="50" class="range-input" :disabled="!config.activate_internet_search">
                    <input id="internet_vectorization_chunk_size-number" :value="config.internet_vectorization_chunk_size" @input="handleNumberInput('internet_vectorization_chunk_size', $event.target.value, true)" type="number" min="100" max="1000" step="50" class="input-sm w-20 text-center" :disabled="!config.activate_internet_search">
                 </div>
            </div>

             <div class="setting-item">
                <label for="internet_vectorization_overlap_size" class="setting-label">
                     Content Overlap Size
                     <span class="block text-xs font-normal text-blue-500 dark:text-blue-400 mt-1">Overlap between text chunks when processing web page content.</span>
                </label>
                <div class="flex-1 flex items-center gap-4">
                     <input id="internet_vectorization_overlap_size-range" :value="config.internet_vectorization_overlap_size" @input="handleNumberInput('internet_vectorization_overlap_size', $event.target.value, true)" type="range" min="0" max="200" step="10" class="range-input" :disabled="!config.activate_internet_search">
                     <input id="internet_vectorization_overlap_size-number" :value="config.internet_vectorization_overlap_size" @input="handleNumberInput('internet_vectorization_overlap_size', $event.target.value, true)" type="number" min="0" max="200" step="10" class="input-sm w-20 text-center" :disabled="!config.activate_internet_search">
                </div>
             </div>

             <div class="setting-item">
                <label for="internet_vectorization_nb_chunks" class="setting-label">
                     Number of Content Chunks to Use
                     <span class="block text-xs font-normal text-blue-500 dark:text-blue-400 mt-1">Maximum number of processed text chunks from web pages to include in the context.</span>
                </label>
                 <div class="flex-1 flex items-center gap-4">
                     <input id="internet_vectorization_nb_chunks-range" :value="config.internet_vectorization_nb_chunks" @input="handleNumberInput('internet_vectorization_nb_chunks', $event.target.value, true)" type="range" min="1" max="20" step="1" class="range-input" :disabled="!config.activate_internet_search">
                     <input id="internet_vectorization_nb_chunks-number" :value="config.internet_vectorization_nb_chunks" @input="handleNumberInput('internet_vectorization_nb_chunks', $event.target.value, true)" type="number" min="1" max="20" step="1" class="input-sm w-20 text-center" :disabled="!config.activate_internet_search">
                </div>
            </div>

        </section>

    </div>
</template>

<script>
import feather from 'feather-icons';
import { nextTick } from 'vue';
import ToggleSwitch from '@/components/ToggleSwitch.vue';

export default {
    name: 'InternetSettings',
    components: {
        ToggleSwitch
    },
    props: {
        config: { type: Object, required: true }, // Receive editable config copy
        loading: { type: Boolean, default: false }
    },
    emits: ['setting-updated'], // Declare the event

    methods: {
        updateValue(key, value) {
            // Emit update for parent component
            this.$emit('setting-updated', { key, value });
        },
        handleNumberInput(key, value, isInt = false) {
            // Parse the value
            let parsedValue = isInt ? parseInt(value) : parseFloat(value);
            // Check for NaN after parsing
            if (isNaN(parsedValue)) {
                 console.warn(`Attempted to set invalid number for ${key}:`, value);
                 // Fallback to a reasonable default, like the minimum allowed value or 0
                 const minVal = {
                      'internet_nb_search_pages': 1,
                      'internet_vectorization_chunk_size': 100,
                      'internet_vectorization_overlap_size': 0,
                      'internet_vectorization_nb_chunks': 1
                 }[key] || 0; // Default to 0 if key not found
                 parsedValue = minVal;
                 // Optionally update the input field visually to the fallback value if needed
                 // e.g., by finding the element and setting its value, but emitting is usually enough
            }
            this.updateValue(key, parsedValue);
        },
        replaceFeatherIcons() {
             nextTick(() => { try { feather.replace(); } catch (e) {} });
        }
    },
    mounted() {
        this.replaceFeatherIcons();
    },
    updated() {
        this.replaceFeatherIcons();
    }
};
</script>

<style scoped>
/* Using shared styles defined in previous components */
.setting-item { @apply flex flex-col md:flex-row md:items-center gap-2 md:gap-4 py-2; }
.setting-label { @apply block text-sm font-medium text-gray-700 dark:text-gray-300 w-full md:w-1/3 lg:w-1/4 flex-shrink-0; }
.input-sm { @apply block w-full px-2.5 py-1.5 text-sm bg-gray-50 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 focus:border-blue-500 dark:focus:ring-offset-gray-900 sm:text-sm disabled:opacity-50 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500; }
.range-input { @apply w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-600 accent-blue-600 dark:accent-blue-500 disabled:opacity-50; }
.toggle-item { @apply flex items-center justify-between p-3 hover:bg-gray-50 dark:hover:bg-gray-700 rounded-lg transition-colors; }
.toggle-label { @apply text-sm font-medium text-gray-700 dark:text-gray-300 cursor-pointer flex-1 mr-4; }
.toggle-description { @apply block text-xs text-gray-500 dark:text-gray-400 mt-1 font-normal; }
.panels-color { @apply bg-white dark:bg-gray-800; }
</style>