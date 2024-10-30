Here's the complete component code combining both the template and script:

```vue
<template>
    <div v-if="discussionArr.length < 2 && personality.prompts_list.length > 0" class="w-full rounded-lg m-2 shadow-lg hover:border-primary dark:hover:border-primary hover:border-solid hover:border-2 border-2 border-transparent even:bg-bg-light-discussion-odd dark:even:bg-bg-dark-discussion-odd flex flex-col overflow-hidden p-4 pb-2">
        <h2 class="text-xl font-semibold mb-4">Prompt examples</h2>
        <div class="overflow-x-auto flex-grow scrollbar-thin scrollbar-thumb-gray-400 dark:scrollbar-thumb-gray-600 scrollbar-track-gray-200 dark:scrollbar-track-gray-800 scrollbar-thumb-rounded-full scrollbar-track-rounded-full">
            <div class="flex flex-nowrap gap-4 p-2 min-w-full">
                <div 
                    v-for="(prompt, index) in personality.prompts_list" 
                    :key="index" 
                    @click="handlePromptSelection(prompt)"
                    class="flex-shrink-0 w-[300px] bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg p-4 cursor-pointer hover:shadow-lg transition-all duration-300 ease-in-out transform hover:scale-105 flex flex-col justify-between h-[220px] overflow-hidden group"
                >
                    <div 
                        :title="prompt" 
                        class="text-base text-gray-700 dark:text-gray-300 overflow-hidden relative h-full"
                    >
                        <div class="absolute inset-0 overflow-hidden">
                            {{ prompt }}
                        </div>
                        <div class="absolute inset-0 bg-gradient-to-b from-transparent via-transparent to-white dark:to-gray-800 group-hover:opacity-0 transition-opacity duration-300"></div>
                    </div>
                    <div class="mt-2 text-sm text-gray-500 dark:text-gray-400 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                        Click to select
                    </div>
                </div>
            </div>
        </div>

        <!-- Enhanced Modal for placeholder inputs with live preview -->
        <div v-if="showPlaceholderModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div class="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-xl max-w-4xl w-full">
                <h3 class="text-lg font-semibold mb-4">Fill in the placeholders</h3>
                
                <!-- Live Preview Section -->
                <div class="mb-4 p-4 bg-gray-100 dark:bg-gray-700 rounded-lg">
                    <h4 class="text-sm font-medium mb-2 text-gray-600 dark:text-gray-400">Live Preview:</h4>
                    <div class="text-base">{{ previewPrompt }}</div>
                </div>

                <div class="space-y-4 max-h-[60vh] overflow-y-auto">
                    <div v-for="(placeholder, index) in parsedPlaceholders" :key="placeholder.fullText" class="flex flex-col">
                        <label :for="'placeholder-'+index" class="text-sm font-medium mb-1">
                            {{ placeholder.label }}
                        </label>

                        <!-- Single line text input -->
                        <input 
                            v-if="placeholder.type === 'text'"
                            :id="'placeholder-'+index"
                            v-model="placeholderValues[index]"
                            type="text"
                            class="border rounded-md p-2 dark:bg-gray-700 dark:border-gray-600"
                            :placeholder="placeholder.label"
                            @input="updatePreview"
                        >

                        <!-- Number input (int) -->
                        <input 
                            v-if="placeholder.type === 'int'"
                            :id="'placeholder-'+index"
                            v-model.number="placeholderValues[index]"
                            type="number"
                            step="1"
                            class="border rounded-md p-2 dark:bg-gray-700 dark:border-gray-600"
                            @input="updatePreview"
                        >

                        <!-- Number input (float) -->
                        <input 
                            v-if="placeholder.type === 'float'"
                            :id="'placeholder-'+index"
                            v-model.number="placeholderValues[index]"
                            type="number"
                            step="0.01"
                            class="border rounded-md p-2 dark:bg-gray-700 dark:border-gray-600"
                            @input="updatePreview"
                        >

                        <!-- Multiline text input -->
                        <textarea 
                            v-if="placeholder.type === 'multiline'"
                            :id="'placeholder-'+index"
                            v-model="placeholderValues[index]"
                            rows="4"
                            class="border rounded-md p-2 dark:bg-gray-700 dark:border-gray-600"
                            @input="updatePreview"
                        ></textarea>

                        <!-- Code editor -->
                        <div v-if="placeholder.type === 'code'" class="border rounded-md overflow-hidden">
                            <div class="bg-gray-200 dark:bg-gray-900 p-2 text-sm">
                                {{ placeholder.language || 'Plain text' }}
                            </div>
                            <textarea 
                                :id="'placeholder-'+index"
                                v-model="placeholderValues[index]"
                                rows="8"
                                class="w-full p-2 font-mono bg-gray-100 dark:bg-gray-900 border-t"
                                @input="updatePreview"
                            ></textarea>
                        </div>

                        <!-- Options (dropdown) -->
                        <select 
                            v-if="placeholder.type === 'options'"
                            :id="'placeholder-'+index"
                            v-model="placeholderValues[index]"
                            class="border rounded-md p-2 dark:bg-gray-700 dark:border-gray-600"
                            @change="updatePreview"
                        >
                            <option value="" disabled>Select an option</option>
                            <option 
                                v-for="option in placeholder.options" 
                                :key="option" 
                                :value="option"
                            >
                                {{ option }}
                            </option>
                        </select>
                    </div>
                </div>
                
                <div class="mt-6 flex justify-end space-x-4">
                    <button 
                        @click="cancelPlaceholders"
                        class="px-4 py-2 text-gray-600 hover:text-gray-800 dark:text-gray-400 dark:hover:text-gray-200"
                    >
                        Cancel
                    </button>
                    <button 
                        @click="applyPlaceholders"
                        class="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600"
                    >
                        Apply
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    name: 'PromptExamples',
    props: {
        personality: {
            type: Object,
            required: true
        },
        discussionArr: {
            type: Array,
            required: true
        }
    },
    data() {
        return {
            showPlaceholderModal: false,
            placeholderValues: {},
            selectedPrompt: '',
            previewPrompt: '',
            uniquePlaceholders: new Map(),
        }
    },
    methods: {
        handlePromptSelection(prompt) {
            this.selectedPrompt = prompt;
            this.previewPrompt = prompt;
            const placeholders = this.extractPlaceholders(prompt);
            if (placeholders.length > 0) {
                this.placeholderValues = {};
                this.showPlaceholderModal = true;
            } else {
                this.$emit('prompt-selected', prompt);
            }
        },

        extractPlaceholders(text) {
            const regex = /\[(.*?)\]/g;
            return Array.from(new Set(text.match(regex) || []));
        },

        parsePlaceholder(placeholder) {
            const parts = placeholder.replace('[', '').replace(']', '').split('::');
            const label = parts[0];

            if (parts.length === 1) {
                return {
                    label,
                    type: 'text',
                    fullText: placeholder
                };
            }

            const type = parts[1];
            const result = {
                label,
                type,
                fullText: placeholder
            };

            switch (type) {
                case 'int':
                case 'float':
                case 'multiline':
                    break;
                case 'code':
                    result.language = parts[2] || 'plaintext';
                    break;
                case 'options':
                    result.options = parts[2] ? parts[2].split(',').map(o => o.trim()) : [];
                    break;
                default:
                    result.type = 'text';
            }
            return result;
        },

        escapeRegExp(string) {
            return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
        },

        updatePreview() {
            let preview = this.selectedPrompt;
            this.parsedPlaceholders.forEach((placeholder, index) => {
                const value = this.placeholderValues[index];
                const regex = new RegExp(this.escapeRegExp(placeholder.fullText), 'g');
                preview = preview.replace(regex, value || placeholder.fullText);
            });
            this.previewPrompt = preview;
        },

        applyPlaceholders() {
            let finalPrompt = this.selectedPrompt;
            this.parsedPlaceholders.forEach((placeholder, index) => {
                const value = this.placeholderValues[index];
                if (value) {
                    const regex = new RegExp(this.escapeRegExp(placeholder.fullText), 'g');
                    finalPrompt = finalPrompt.replace(regex, value);
                }
            });
            this.$emit('prompt-selected', finalPrompt);
            this.showPlaceholderModal = false;
        },

        cancelPlaceholders() {
            this.showPlaceholderModal = false;
            this.placeholderValues = {};
            this.selectedPrompt = '';
            this.previewPrompt = '';
        }
    },
    computed: {
        placeholders() {
            return this.extractPlaceholders(this.selectedPrompt);
        },
        parsedPlaceholders() {
            const uniqueMap = new Map();
            this.placeholders.forEach(p => {
                const parsed = this.parsePlaceholder(p);
                uniqueMap.set(parsed.fullText, parsed);
            });
            return Array.from(uniqueMap.values());
        }
    }
}
</script>

<style scoped>
/* Add any additional styling here */
</style>
```

This complete component:
1. Shows a list of prompt examples
2. Handles placeholder detection and parsing
3. Provides appropriate input types based on placeholder syntax
4. Handles repeated placeholders by showing only one input for each unique placeholder
5. Updates all instances of the same placeholder simultaneously
6. Provides a live preview of the final prompt
7. Supports dark mode
8. Has proper styling and transitions

To use it, simply import and include it in your parent component:

```vue
<template>
    <PromptExamples 
        :personality="personality"
        :discussionArr="discussionArr"
        @prompt-selected="handlePromptSelection"
    />
</template>

<script>
import PromptExamples from './PromptExamples.vue'

export default {
    components: {
        PromptExamples
    },
    // ... rest of your component code
}
</script>
```

The component will emit a 'prompt-selected' event with the final processed prompt when the user completes the placeholder inputs and clicks "Apply".
