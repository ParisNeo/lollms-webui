<template>
    <div class="user-settings-panel space-y-6">
        <h2 class="text-xl font-semibold text-blue-800 dark:text-blue-100 border-b border-blue-300 dark:border-blue-600 pb-2">
            Internet Search
        </h2>

         <p class="text-sm text-blue-600 dark:text-blue-400 mb-4">
            Configure how LoLLMs interacts with the internet to answer questions or find information. Requires a model capable of function calling or specific instruction following.
        </p>

        <!-- Internet Search Toggles -->
        <section class="space-y-4 p-4 border border-blue-300 dark:border-blue-600 rounded-lg panels-color">
            <h3 class="text-lg font-medium text-blue-700 dark:text-blue-300 mb-3">Activation & Behavior</h3>

            <!-- Activate Internet Search -->
            <div class="toggle-item">
                <label for="activate_internet_search" class="toggle-label">
                    Enable Automatic Internet Search
                     <span class="toggle-description">Allow the AI to decide when to search the internet based on the prompt.</span>
                </label>
                <ToggleSwitch id="activate_internet_search" :checked="$store.state.config.activate_internet_search" @update:checked="updateBoolean('activate_internet_search', $event)" />
            </div>

             <!-- Activate Search Decision -->
            <div class="toggle-item" :class="{ 'opacity-50 pointer-events-none': !$store.state.config.activate_internet_search }">
                <label for="internet_activate_search_decision" class="toggle-label">
                    Enable Explicit Search Decision
                     <span class="toggle-description">Make the AI explicitly state whether it needs to search the internet before performing the search.</span>
                </label>
                <ToggleSwitch id="internet_activate_search_decision" :checked="$store.state.config.internet_activate_search_decision" @update:checked="updateBoolean('internet_activate_search_decision', $event)" :disabled="!$store.state.config.activate_internet_search"/>
            </div>

            <!-- Activate Pages Judgement -->
            <div class="toggle-item" :class="{ 'opacity-50 pointer-events-none': !$store.state.config.activate_internet_search }">
                <label for="activate_internet_pages_judgement" class="toggle-label">
                    Enable Search Result Evaluation
                     <span class="toggle-description">Allow the AI to evaluate the relevance and quality of search result snippets before using them.</span>
                </label>
                <ToggleSwitch id="activate_internet_pages_judgement" :checked="$store.state.config.activate_internet_pages_judgement" @update:checked="updateBoolean('activate_internet_pages_judgement', $event)" :disabled="!$store.state.config.activate_internet_search"/>
            </div>

            <!-- Activate Quick Search -->
            <div class="toggle-item" :class="{ 'opacity-50 pointer-events-none': !$store.state.config.activate_internet_search }">
                <label for="internet_quick_search" class="toggle-label">
                    Enable Quick Search
                     <span class="toggle-description">Perform a faster search potentially using fewer results or less processing, might be less accurate.</span>
                </label>
                 <ToggleSwitch id="internet_quick_search" :checked="$store.state.config.internet_quick_search" @update:checked="updateBoolean('internet_quick_search', $event)" :disabled="!$store.state.config.activate_internet_search"/>
            </div>
        </section>

        <!-- Internet Search Parameters -->
        <section :class="['space-y-4 p-4 border border-blue-300 dark:border-blue-600 rounded-lg panels-color', !$store.state.config.activate_internet_search ? 'opacity-50 pointer-events-none' : '']">
            <h3 class="text-lg font-medium text-blue-700 dark:text-blue-300 mb-3">Search Parameters</h3>

            <!-- Number of Search Pages/Results -->
            <div class="setting-item">
                <label for="internet_nb_search_pages" class="setting-label">
                    Number of Search Results
                     <span class="block text-xs font-normal text-blue-500 dark:text-blue-400 mt-1">Controls how many search result snippets are initially retrieved.</span>
                </label>
                <div class="flex-1 flex items-center gap-4">
                    <input id="internet_nb_search_pages-range" :value="$store.state.config.internet_nb_search_pages" @input="updateValue('internet_nb_search_pages', $event.target.value)" type="range" min="1" max="20" step="1" class="range-input" :disabled="!$store.state.config.activate_internet_search">
                    <input id="internet_nb_search_pages-number" :value="$store.state.config.internet_nb_search_pages" @input="updateValue('internet_nb_search_pages', $event.target.value)" type="number" min="1" max="20" step="1" class="input-sm w-20 text-center" :disabled="!$store.state.config.activate_internet_search">
                </div>
            </div>

             <!-- Vectorization Chunk Size -->
            <div class="setting-item">
                <label for="internet_vectorization_chunk_size" class="setting-label">
                     Content Chunk Size
                    <span class="block text-xs font-normal text-blue-500 dark:text-blue-400 mt-1">Size of text chunks when processing content from searched web pages (if applicable).</span>
                 </label>
                <div class="flex-1 flex items-center gap-4">
                     <input id="internet_vectorization_chunk_size-range" :value="$store.state.config.internet_vectorization_chunk_size" @input="updateValue('internet_vectorization_chunk_size', $event.target.value)" type="range" min="100" max="1000" step="50" class="range-input" :disabled="!$store.state.config.activate_internet_search">
                    <input id="internet_vectorization_chunk_size-number" :value="$store.state.config.internet_vectorization_chunk_size" @input="updateValue('internet_vectorization_chunk_size', $event.target.value)" type="number" min="100" max="1000" step="50" class="input-sm w-20 text-center" :disabled="!$store.state.config.activate_internet_search">
                 </div>
            </div>

             <!-- Vectorization Overlap Size -->
             <div class="setting-item">
                <label for="internet_vectorization_overlap_size" class="setting-label">
                     Content Overlap Size
                     <span class="block text-xs font-normal text-blue-500 dark:text-blue-400 mt-1">Overlap between text chunks when processing web page content.</span>
                </label>
                <div class="flex-1 flex items-center gap-4">
                     <input id="internet_vectorization_overlap_size-range" :value="$store.state.config.internet_vectorization_overlap_size" @input="updateValue('internet_vectorization_overlap_size', $event.target.value)" type="range" min="0" max="200" step="10" class="range-input" :disabled="!$store.state.config.activate_internet_search">
                     <input id="internet_vectorization_overlap_size-number" :value="$store.state.config.internet_vectorization_overlap_size" @input="updateValue('internet_vectorization_overlap_size', $event.target.value)" type="number" min="0" max="200" step="10" class="input-sm w-20 text-center" :disabled="!$store.state.config.activate_internet_search">
                </div>
             </div>

             <!-- Number of Vectorization Chunks to Use -->
             <div class="setting-item">
                <label for="internet_vectorization_nb_chunks" class="setting-label">
                     Number of Content Chunks to Use
                     <span class="block text-xs font-normal text-blue-500 dark:text-blue-400 mt-1">Maximum number of processed text chunks from web pages to include in the context.</span>
                </label>
                 <div class="flex-1 flex items-center gap-4">
                     <input id="internet_vectorization_nb_chunks-range" :value="$store.state.config.internet_vectorization_nb_chunks" @input="updateValue('internet_vectorization_nb_chunks', $event.target.value)" type="range" min="1" max="20" step="1" class="range-input" :disabled="!$store.state.config.activate_internet_search">
                     <input id="internet_vectorization_nb_chunks-number" :value="$store.state.config.internet_vectorization_nb_chunks" @input="updateValue('internet_vectorization_nb_chunks', $event.target.value)" type="number" min="1" max="20" step="1" class="input-sm w-20 text-center" :disabled="!$store.state.config.activate_internet_search">
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
    name: 'InternetSettings', // Give the component a name
    components: {
        ToggleSwitch
    },
    props: {
        loading: { // Note: loading prop is defined but not used in the template/script
            type: Boolean,
            default: false
        }
    },
    emits: ['update:setting'],

    data() {
        return {
            // No specific reactive data needed for this component's logic
        };
    },

    methods: {
        updateValue(key, value) {
            // Ensure numeric values from range/number inputs are parsed correctly
            const numericKeys = [
                'internet_nb_search_pages',
                'internet_vectorization_chunk_size',
                'internet_vectorization_overlap_size',
                'internet_vectorization_nb_chunks'
            ];
            // Use Number() for potentially better handling of empty strings/non-numeric input
            // Default to 0 or a reasonable minimum if parsing fails
            const finalValue = numericKeys.includes(key) ? (Number(value) || 0) : value;

            this.$emit('update:setting', { key, value: finalValue });
        },

        updateBoolean(key, value) {
            this.$emit('update:setting', { key, value: Boolean(value) });
        },

        // Helper to ensure Feather icons are rendered after DOM updates
        replaceFeatherIcons() {
             nextTick(() => {
                 try {
                    // Check if feather is available (it might not be in all test environments)
                    if (typeof feather !== 'undefined' && feather && typeof feather.replace === 'function') {
                       feather.replace();
                    }
                 } catch (e) {
                    console.error("Feather icons replacement failed:", e);
                 }
            });
        }
    },

    mounted() {
        this.replaceFeatherIcons();
        // Since feather icons are static here (no v-if toggling them),
        // calling it only in mounted might be sufficient.
    },
    updated() {
        // Optional: Re-run feather replace if the component structure might change dynamically
        // though in this specific component, it might not be strictly necessary.
        this.replaceFeatherIcons();
    }
};
</script>

<style scoped>
/* Root variables (if not defined globally) - Adjust colors as needed */
:root {
     --color-primary: #3b82f6; /* Tailwind blue-500 */
     --color-primary-rgb: 59, 130, 246;
}
.dark:root { /* Use :root within .dark selector if needed */
     --color-primary: #60a5fa; /* Tailwind blue-400 */
     --color-primary-rgb: 96, 165, 250;
}

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
/* Custom styling for range input thumb and track with accent color */
.range-input {
    @apply w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-600 disabled:opacity-50;
    accent-color: var(--color-primary); /* Modern way to color the track/thumb */
}

/* Thumb base style */
.range-input::-webkit-slider-thumb {
    @apply appearance-none w-4 h-4 bg-primary rounded-full cursor-pointer transition-colors shadow; /* Use theme primary color var */
    background-color: var(--color-primary); /* Explicitly set */
}
.range-input::-moz-range-thumb {
    @apply w-4 h-4 bg-primary rounded-full cursor-pointer border-none transition-colors shadow; /* Use theme primary color var */
    background-color: var(--color-primary); /* Explicitly set */
}

/* Disabled thumb style */
.range-input:disabled::-webkit-slider-thumb {
     @apply bg-gray-400 dark:bg-gray-500 cursor-not-allowed;
}
.range-input:disabled::-moz-range-thumb {
     @apply bg-gray-400 dark:bg-gray-500 cursor-not-allowed;
}

/* --- Updated Focus Style --- */
.range-input:focus {
    @apply outline-none; /* Remove default browser outline */
}

.range-input:focus::-webkit-slider-thumb {
    /* Ring effect using box-shadow */
    /* Offset color (white in light, gray-800 in dark) + Ring color (primary with 50% alpha) */
    box-shadow: 0 0 0 2px theme('colors.white'), 0 0 0 4px rgba(var(--color-primary-rgb), 0.5);
}
.dark .range-input:focus::-webkit-slider-thumb {
    box-shadow: 0 0 0 2px theme('colors.gray.800'), 0 0 0 4px rgba(var(--color-primary-rgb), 0.5);
}

.range-input:focus::-moz-range-thumb {
    /* Ring effect using box-shadow */
    box-shadow: 0 0 0 2px theme('colors.white'), 0 0 0 4px rgba(var(--color-primary-rgb), 0.5);
}
.dark .range-input:focus::-moz-range-thumb {
    box-shadow: 0 0 0 2px theme('colors.gray.800'), 0 0 0 4px rgba(var(--color-primary-rgb), 0.5);
}
/* --- End Updated Focus Style --- */


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