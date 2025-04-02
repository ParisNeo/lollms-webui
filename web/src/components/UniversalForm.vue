<template>
    <div v-if="show"
         class="fixed inset-0 flex items-center justify-center bg-black/50 backdrop-blur-sm transition-all" style="z-index: 1000;">
        <div class="relative w-full mx-4 max-w-2xl">
            <!-- Main Container -->
            <div class="card flex flex-col rounded-xl shadow-2xl transform transition-all max-h-[90vh]">
                <!-- Header -->
                <div class="flex items-center justify-between p-6 border-b border-blue-200 dark:border-blue-700">
                    <div class="flex items-center gap-3">
                        <i data-feather="sliders" class="w-6 h-6 text-blue-500 dark:text-blue-400"></i>
                        <h3 class="text-xl font-bold text-blue-800 dark:text-blue-100">{{ title }}</h3>
                    </div>
                    <button @click.stop="hide(false)"
                            class="svg-button">
                        <i data-feather="x" class="w-5 h-5"></i> <!-- svg-button class handles text color -->
                    </button>
                </div>

                <!-- Scrollable Content -->
                <div class="overflow-y-auto px-6 py-5 scrollbar"> <!-- Use theme scrollbar -->
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <template v-for="(item, index) in controls_array" :key="index">
                            <div class="group" :class="{'md:col-span-2': item.spanFull || ['btn', 'text', 'list', 'file', 'folder'].includes(item.type)}">
                                <!-- Common Help Button Structure -->
                                <div class="flex items-center justify-between mb-2"> <!-- Reduced margin -->
                                    <label :for="'input-' + index" class="label flex items-center gap-2 !mb-0"> <!-- Use theme label, adjusted margin -->
                                        <span>
                                            {{ item.name }}
                                        </span>
                                        <button v-if="item.help" @click="item.isHelp = !item.isHelp"
                                                class="text-blue-500 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 transition-colors">
                                            <i data-feather="help-circle" class="w-4 h-4"></i>
                                        </button>
                                    </label>
                                    <span v-if="item.required" class="text-xs text-red-500 dark:text-red-400">* Required</span>
                                </div>

                                <!-- Help Text -->
                                <p v-if="item.isHelp" class="text-sm text-blue-600 dark:text-blue-400 mb-3">
                                    {{ item.help }}
                                </p>

                                <!-- Input Fields -->
                                <div class="space-y-2">
                                    <!-- Text/Select Input -->
                                    <div v-if="['str', 'string'].includes(item.type)">
                                        <input v-if="!item.options"
                                               :id="'input-' + index"
                                               type="text"
                                               v-model="item.value"
                                               :placeholder="item.placeholder || 'Enter text'"
                                               class="input w-full text-sm"> <!-- Use theme input -->

                                        <select v-else
                                                :id="'input-' + index"
                                                v-model="item.value"
                                                class="input w-full text-sm appearance-none"> <!-- Use theme input, keep appearance-none -->
                                            <option v-for="(op, i) in item.options" :key="i" :value="op">
                                                {{ op }}
                                            </option>
                                        </select>
                                    </div>

                                    <!-- Button -->
                                    <div v-if="item.type === 'btn'">
                                        <button @click="btn_clicked(item)"
                                                class="btn btn-primary w-full justify-center text-sm"> <!-- Use theme button -->
                                            <i v-if="item.icon" :data-feather="item.icon" class="w-4 h-4 mr-2"></i> <!-- Dynamic feather icon -->
                                            {{ item.name }}
                                        </button>
                                    </div>

                                    <!-- Text Area -->
                                    <div v-if="item.type === 'text'">
                                        <textarea :id="'input-' + index"
                                                  v-model="item.value"
                                                  rows="4"
                                                  class="input w-full text-sm resize-none"></textarea> <!-- Use theme input -->
                                    </div>

                                    <!-- Number Inputs -->
                                    <div v-if="['int', 'float'].includes(item.type)" class="space-y-3">
                                        <input :id="'input-' + index"
                                               type="number"
                                               v-model="item.value"
                                               :step="item.type === 'int' ? 1 : (item.step || 0.1)"
                                               class="input w-full text-sm"> <!-- Use theme input -->

                                        <input v-if="item.min !== undefined && item.max !== undefined"
                                               :id="'range-' + index"
                                               type="range"
                                               v-model="item.value"
                                               :min="item.min"
                                               :max="item.max"
                                               :step="item.step || (item.type === 'int' ? 1 : 0.1)"
                                               class="range-input w-full cursor-pointer"> <!-- Use theme range input -->
                                    </div>

                                    <!-- Boolean Input -->
                                    <div v-if="item.type === 'bool'" class="flex items-center gap-3">
                                        <label class="relative inline-flex items-center cursor-pointer switch">
                                            <input :id="'input-' + index" type="checkbox" v-model="item.value" class="sr-only peer">
                                            <!-- Keep local switch style but use theme colors -->
                                            <div class="w-11 h-6 bg-blue-200 dark:bg-blue-700 rounded-full peer peer-checked:bg-blue-500 dark:peer-checked:bg-blue-600 transition-colors">
                                                <div class="switch-thumb"></div>
                                            </div>
                                        </label>
                                        <span class="text-sm text-blue-700 dark:text-blue-300">{{ item.value ? 'Enabled' : 'Disabled' }}</span>
                                    </div>

                                    <!-- Color Picker -->
                                    <div v-if="item.type === 'color'" class="flex items-center gap-3">
                                        <input :id="'input-' + index"
                                               type="color"
                                               v-model="item.value"
                                               class="w-10 h-10 rounded-lg border border-blue-300 dark:border-blue-600 cursor-pointer p-0.5 bg-clip-content bg-blue-100 dark:bg-blue-800"> <!-- Adjusted styling -->
                                        <input type="text"
                                               v-model="item.value"
                                               class="input flex-1 text-sm"> <!-- Use theme input -->
                                    </div>

                                    <!-- File/Folder Input -->
                                    <div v-if="['file', 'folder'].includes(item.type)" class="flex gap-2">
                                        <input :id="'input-' + index"
                                               type="text"
                                               v-model="item.value"
                                               readonly
                                               class="input flex-1 text-sm bg-blue-50 dark:bg-blue-800"> <!-- Use theme input, adjust readonly bg -->
                                        <button @click="openFileDialog(item)"
                                                class="btn btn-secondary text-sm"> <!-- Use theme button -->
                                            <i data-feather="folder" class="w-4 h-4 mr-1"></i>
                                            <span>Browse</span>
                                        </button>
                                    </div>
                                </div>

                                <!-- Divider (Removed visual divider, relying on grid gap) -->
                                <!-- <div v-if="index < controls_array.length - 1 && !item.spanFull"
                                     class="h-px bg-blue-200 dark:bg-blue-700 my-6"></div> -->
                            </div>
                        </template>
                    </div>
                </div>

                <!-- Footer -->
                <div class="flex justify-end gap-3 p-6 border-t border-blue-200 dark:border-blue-700">
                    <button @click.stop="hide(false)"
                            class="btn btn-secondary text-sm"> <!-- Use theme button -->
                        {{ DenyButtonText }}
                    </button>
                    <button @click.stop="hide(true)"
                            class="btn btn-primary text-sm"> <!-- Use theme button -->
                        <i data-feather="check" class="w-4 h-4 mr-1"></i>
                        {{ ConfirmButtonText }}
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>

<!-- Keep minimal local styles for elements not covered by the theme, like the switch -->
<style scoped>
/* Keep the switch styles locally, but colors can be adapted from theme vars if needed */
.switch-thumb {
    @apply absolute top-0.5 left-0.5 w-5 h-5 bg-white dark:bg-blue-100 rounded-full shadow-sm transform transition-transform duration-200;
}
.peer:checked + div > .switch-thumb { /* Target child div for thumb positioning */
    @apply translate-x-5;
}
/* Color input background */
input[type="color"]::-webkit-color-swatch-wrapper {
    padding: 0;
}
input[type="color"]::-webkit-color-swatch {
    border: none;
    border-radius: 6px; /* Slightly less than parent */
}
input[type="color"]::-moz-color-swatch {
    border: none;
    border-radius: 6px;
}
</style>