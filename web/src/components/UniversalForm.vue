<template>
    <div v-if="show"
         class="fixed inset-0 flex items-center justify-center bg-black/50 backdrop-blur-sm transition-all" style="z-index: 1000;">
        <div class="relative w-full mx-4 max-w-2xl">
            <!-- Main Container -->
            <div class="flex flex-col rounded-xl bg-white dark:bg-gray-800 shadow-2xl transform transition-all max-h-[90vh]">
                <!-- Header -->
                <div class="flex items-center justify-between p-6 border-b border-gray-100 dark:border-gray-700">
                    <div class="flex items-center gap-3">
                        <i data-feather="sliders" class="w-6 h-6 text-blue-500"></i>
                        <h3 class="text-xl font-bold text-gray-800 dark:text-gray-200">{{ title }}</h3>
                    </div>
                    <button @click.stop="hide(false)"
                            class="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors">
                        <i data-feather="x" class="w-5 h-5 text-gray-500 dark:text-gray-400"></i>
                    </button>
                </div>

                <!-- Scrollable Content -->
                <div class="overflow-y-auto px-6 py-5 custom-scrollbar">
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <template v-for="(item, index) in controls_array" :key="index">
                            <div class="group" :class="{'md:col-span-2': item.spanFull || ['btn', 'text', 'list', 'file', 'folder'].includes(item.type)}">
                                <!-- Common Help Button Structure -->
                                <div class="flex items-center justify-between mb-3">
                                    <label class="flex items-center gap-2">
                                        <span class="text-base font-semibold text-gray-700 dark:text-gray-300">
                                            {{ item.name }}
                                        </span>
                                        <button v-if="item.help" @click="item.isHelp = !item.isHelp"
                                                class="text-gray-400 hover:text-blue-500 transition-colors">
                                            <i data-feather="help-circle" class="w-4 h-4"></i>
                                        </button>
                                    </label>
                                    <span v-if="item.required" class="text-xs text-red-500">* Required</span>
                                </div>

                                <!-- Help Text -->
                                <p v-if="item.isHelp" class="text-sm text-gray-500 dark:text-gray-400 mb-3">
                                    {{ item.help }}
                                </p>

                                <!-- Input Fields -->
                                <div class="space-y-2">
                                    <!-- Text/Select Input -->
                                    <div v-if="['str', 'string'].includes(item.type)">
                                        <input v-if="!item.options" 
                                               type="text" 
                                               v-model="item.value"
                                               :placeholder="item.placeholder || 'Enter text'"
                                               class="w-full px-4 py-3 text-sm rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all">
                                        
                                        <select v-else v-model="item.value"
                                                class="w-full px-4 py-3 text-sm rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 appearance-none">
                                            <option v-for="(op, i) in item.options" :key="i" :value="op">
                                                {{ op }}
                                            </option>
                                        </select>
                                    </div>

                                    <!-- Button -->
                                    <div v-if="item.type === 'btn'">
                                        <button @click="btn_clicked(item)"
                                                class="w-full px-4 py-3 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors flex justify-center items-center gap-2">
                                            <i v-if="item.icon" data-feather="item.icon" class="w-4 h-4"></i>
                                            {{ item.name }}
                                        </button>
                                    </div>

                                    <!-- Text Area -->
                                    <div v-if="item.type === 'text'">
                                        <textarea v-model="item.value" 
                                                  rows="4"
                                                  class="w-full px-4 py-3 text-sm rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"></textarea>
                                    </div>

                                    <!-- Number Inputs -->
                                    <div v-if="['int', 'float'].includes(item.type)" class="space-y-3">
                                        <input type="number" 
                                               v-model="item.value" 
                                               :step="item.type === 'int' ? 1 : 0.1"
                                               class="w-full px-4 py-3 text-sm rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
                                        
                                        <input v-if="item.min !== undefined && item.max !== undefined" 
                                               type="range" 
                                               v-model="item.value" 
                                               :min="item.min" 
                                               :max="item.max"
                                               :step="item.step || (item.type === 'int' ? 1 : 0.1)"
                                               class="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-full appearance-none cursor-pointer range-thumb">
                                    </div>

                                    <!-- Boolean Input -->
                                    <div v-if="item.type === 'bool'" class="flex items-center gap-3">
                                        <label class="relative inline-flex items-center cursor-pointer switch">
                                            <input type="checkbox" v-model="item.value" class="sr-only peer">
                                            <div class="w-11 h-6 bg-gray-200 rounded-full peer peer-checked:bg-blue-600 transition-colors">
                                                <div class="switch-thumb"></div>
                                            </div>
                                        </label>
                                        <span class="text-sm text-gray-600 dark:text-gray-300">{{ item.value ? 'Enabled' : 'Disabled' }}</span>
                                    </div>

                                    <!-- Color Picker -->
                                    <div v-if="item.type === 'color'" class="flex items-center gap-3">
                                        <input type="color" 
                                               v-model="item.value"
                                               class="w-12 h-12 rounded-lg border border-gray-200 dark:border-gray-700 cursor-pointer">
                                        <input type="text" 
                                               v-model="item.value"
                                               class="flex-1 px-4 py-3 text-sm rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
                                    </div>

                                    <!-- File/Folder Input -->
                                    <div v-if="['file', 'folder'].includes(item.type)" class="flex gap-2">
                                        <input type="text" 
                                               v-model="item.value" 
                                               readonly
                                               class="flex-1 px-4 py-3 text-sm rounded-lg border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900">
                                        <button @click="openFileDialog(item)"
                                                class="px-4 py-3 text-sm font-medium text-gray-700 dark:text-gray-200 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-lg transition-colors flex items-center gap-2">
                                            <i data-feather="folder" class="w-4 h-4"></i>
                                            <span>Browse</span>
                                        </button>
                                    </div>
                                </div>

                                <!-- Divider -->
                                <div v-if="index < controls_array.length - 1 && !item.spanFull" 
                                     class="h-px bg-gray-100 dark:bg-gray-700 my-6"></div>
                            </div>
                        </template>
                    </div>
                </div>

                <!-- Footer -->
                <div class="flex justify-end gap-3 p-6 border-t border-gray-100 dark:border-gray-700">
                    <button @click.stop="hide(false)"
                            class="px-6 py-3 text-sm font-medium text-gray-700 dark:text-gray-200 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-lg transition-colors duration-200">
                        {{ DenyButtonText }}
                    </button>
                    <button @click.stop="hide(true)"
                            class="px-6 py-3 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors flex items-center gap-2">
                        <i data-feather="check" class="w-4 h-4"></i>
                        {{ ConfirmButtonText }}
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import feather from 'feather-icons'

export default {
    name: 'UniversalForm',
    data() {
        return {
            show: false,
            resolve: null,
            controls_array: [],
            title: "Universal Form",
            ConfirmButtonText: "Submit",
            DenyButtonText: "Cancel",
        }
    },
    mounted() {
        feather.replace()
    },
    methods: {
        btn_clicked(item) {
            if (item.callback) {
                item.callback(item)
            } else {
                console.log('Button clicked:', item)
            }
        },
        
        hide(response) {
            this.show = false
            if (this.resolve) {
                if(response){
                    this.resolve(this.controls_array);
                this.resolve = null;
                }
            }
        },


        
        
        showForm(controls_array, title, ConfirmButtonText, DenyButtonText) {
            if (typeof controls_array === 'object' && !Array.isArray(controls_array)) {
                return this._newShowForm(controls_array)
            }
            
            this.ConfirmButtonText = ConfirmButtonText || this.ConfirmButtonText
            this.DenyButtonText = DenyButtonText || this.DenyButtonText
            
            this.controls_array = controls_array.map(item => ({
                ...item,
                isHelp: false,
                placeholder: item.placeholder || '',
                required: item.required || false,
                spanFull: item.spanFull || ['btn', 'text', 'list', 'file', 'folder'].includes(item.type)
            }))
            
            
            return new Promise((resolve) => {
                console.log('Resolve')
                console.log(resolve)
                this.title = title || this.title
                this.show = true
                this.resolve = resolve
                this.$nextTick(() => feather.replace())
            })
        },
        
        _newShowForm(config) {
            this.title = config.title || this.title
            this.ConfirmButtonText = config.confirmText || this.ConfirmButtonText
            this.DenyButtonText = config.denyText || this.DenyButtonText
            
            this.controls_array = config.fields.map(f => ({
                ...f,
                isHelp: false,
                placeholder: f.placeholder || '',
                required: f.required || false,
                spanFull: f.spanFull || ['btn', 'text', 'list', 'file', 'folder'].includes(f.type)
            }))
            
            this.show = true
            
            return new Promise((resolve) => {
                this.resolve = resolve
                this.$nextTick(() => feather.replace())
            })
        },
        
        parseValue(item) {
            switch(item.type) {
                case 'int': return parseInt(item.value) || 0
                case 'float': return parseFloat(item.value) || 0.0
                case 'bool': return Boolean(item.value)
                case 'list': return item.value.split(',').map(i => i.trim())
                default: return item.value
            }
        },
        
        openFileDialog(item) {
            const input = document.createElement('input')
            input.type = item.type === 'folder' ? 'file' : item.type
            if(item.type === 'folder') input.webkitdirectory = true
            if(item.accept) input.accept = item.accept
            
            input.onchange = (e) => {
                const files = Array.from(e.target.files)
                item.value = files.map(f => f.path).join(', ')
            }
            
            input.click()
        }
    },
    watch: {
        controls_array: {
            deep: true,
            handler(newArray) {
                newArray.forEach(item => {
                    if(item.type === 'int') item.value = parseInt(item.value) || 0
                    if(item.type === 'float') item.value = parseFloat(item.value) || 0.0
                })
            }
        }
    }
}
</script>

<style scoped>
.custom-scrollbar {
    scrollbar-width: thin;
    scrollbar-color: rgba(156, 163, 175, 0.5) transparent;
}

.custom-scrollbar::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}

.custom-scrollbar::-webkit-scrollbar-track {
    @apply bg-transparent;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
    @apply bg-gray-300 dark:bg-gray-600 rounded-full;
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
    @apply bg-gray-400 dark:bg-gray-500;
}

.range-thumb {
    @apply appearance-none w-4 h-4 bg-blue-500 rounded-full shadow-sm -mt-1;
}

.dark .range-thumb {
    @apply bg-blue-600;
}

.switch-thumb {
    @apply absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full shadow-sm transform transition-transform duration-200;
}

.peer:checked ~ .switch-thumb {
    @apply translate-x-5;
}

.peer:checked ~ div {
    @apply bg-blue-600;
}

.dark .peer:checked ~ div {
    @apply bg-blue-700;
}
</style>