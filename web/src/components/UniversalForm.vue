<template>
    <div v-if="show"
         class="fixed inset-0 flex items-center justify-center bg-black/50 backdrop-blur-sm transition-opacity duration-300" style="z-index: 1000;">
        <!-- Dialog Container -->
        <div class="relative w-full mx-4 max-w-2xl transform transition-all duration-300 ease-out scale-95 opacity-0"
             :class="{ 'scale-100 opacity-100': show }">
            <!-- Main Panel -->
            <div class="flex flex-col rounded-xl panels-color shadow-2xl max-h-[90vh]">
                <!-- Header -->
                <div class="flex items-center justify-between p-5 border-b border-blue-200 dark:border-blue-700">
                    <div class="flex items-center gap-3">
                        <i data-feather="sliders" class="w-6 h-6 text-blue-600 dark:text-blue-400"></i>
                        <h3 class="text-xl font-semibold text-blue-800 dark:text-blue-100">{{ title }}</h3>
                    </div>
                    <button @click.stop="hide(false)"
                            class="svg-button">
                        <i data-feather="x" class="w-5 h-5"></i>
                    </button>
                </div>

                <!-- Scrollable Content -->
                <div class="overflow-y-auto px-6 py-5 scrollbar">
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-x-6 gap-y-5">
                        <template v-for="(item, index) in controls_array" :key="index">
                            <div class="flex flex-col" :class="{'md:col-span-2': item.spanFull || ['btn', 'text', 'list', 'file', 'folder'].includes(item.type)}">
                                <!-- Label and Help -->
                                <div class="flex items-center justify-between mb-2">
                                    <label :for="`control-${index}`" class="flex items-center gap-1.5 label">
                                        <span>{{ item.name }}</span>
                                        <button v-if="item.help" @click="item.isHelp = !item.isHelp"
                                                class="text-blue-500 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 transition-colors">
                                            <i data-feather="help-circle" class="w-4 h-4"></i>
                                        </button>
                                    </label>
                                    <span v-if="item.required" class="text-xs text-red-500 dark:text-red-400 font-medium">* Required</span>
                                </div>

                                <!-- Help Text -->
                                <p v-if="item.isHelp" class="text-sm text-blue-600 dark:text-blue-400 mb-3 p bg-blue-100 dark:bg-blue-800 p-2 rounded-md border border-blue-200 dark:border-blue-700">
                                    {{ item.help }}
                                </p>

                                <!-- Input Fields -->
                                <div class="mt-1">
                                    <!-- Text/Select Input -->
                                    <div v-if="['str', 'string'].includes(item.type)">
                                        <input v-if="!item.options"
                                               :id="`control-${index}`"
                                               type="text"
                                               v-model="item.value"
                                               :placeholder="item.placeholder || 'Enter text'"
                                               class="input w-full">

                                        <select v-else v-model="item.value"
                                                :id="`control-${index}`"
                                                class="input w-full appearance-none">
                                            <option v-for="(op, i) in item.options" :key="i" :value="op">
                                                {{ op }}
                                            </option>
                                        </select>
                                    </div>

                                    <!-- Button -->
                                    <div v-if="item.type === 'btn'">
                                        <button @click="btn_clicked(item)"
                                                class="btn btn-secondary w-full justify-center">
                                            <i v-if="item.icon" :data-feather="item.icon" class="w-4 h-4 mr-2"></i>
                                            {{ item.name }}
                                        </button>
                                    </div>

                                    <!-- Text Area -->
                                    <div v-if="item.type === 'text'">
                                        <textarea v-model="item.value"
                                                  :id="`control-${index}`"
                                                  rows="4"
                                                  class="input w-full resize-y min-h-[80px]"></textarea>
                                    </div>

                                    <!-- Number Inputs -->
                                    <div v-if="['int', 'float'].includes(item.type)" class="space-y-3">
                                        <input type="number"
                                               :id="`control-${index}`"
                                               v-model="item.value"
                                               :step="item.type === 'int' ? 1 : (item.step || 0.1)"
                                               class="input w-full">

                                        <input v-if="item.min !== undefined && item.max !== undefined"
                                               type="range"
                                               v-model="item.value"
                                               :min="item.min"
                                               :max="item.max"
                                               :step="item.step || (item.type === 'int' ? 1 : 0.1)"
                                               class="range-input w-full">
                                    </div>

                                    <!-- Boolean Input (Toggle Switch) -->
                                    <div v-if="item.type === 'bool'" class="flex items-center gap-3">
                                        <label :for="`control-${index}`" class="relative inline-flex items-center cursor-pointer">
                                            <input type="checkbox" :id="`control-${index}`" v-model="item.value" class="sr-only peer">
                                            <div class="w-11 h-6 bg-blue-200 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-blue-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
                                        </label>
                                        <span class="text-sm text-blue-700 dark:text-blue-300">{{ item.value ? 'Enabled' : 'Disabled' }}</span>
                                    </div>

                                    <!-- Color Picker -->
                                    <div v-if="item.type === 'color'" class="flex items-center gap-3">
                                        <input type="color"
                                               v-model="item.value"
                                               class="w-10 h-10 p-0 border-0 rounded-md cursor-pointer bg-transparent appearance-none"
                                               :style="{ backgroundColor: item.value }">
                                        <input type="text"
                                               :id="`control-${index}`"
                                               v-model="item.value"
                                               class="input flex-1">
                                    </div>

                                    <!-- File/Folder Input -->
                                    <div v-if="['file', 'folder'].includes(item.type)" class="flex gap-2">
                                        <input type="text"
                                               :id="`control-${index}`"
                                               v-model="item.value"
                                               readonly
                                               class="input flex-1 bg-blue-50 dark:bg-blue-800 cursor-not-allowed">
                                        <button @click="openFileDialog(item)"
                                                class="btn btn-secondary flex-shrink-0">
                                            <i data-feather="folder" class="w-4 h-4 mr-1"></i>
                                            <span>Browse</span>
                                        </button>
                                    </div>
                                </div>

                            </div>
                        </template>
                    </div>
                </div>

                <!-- Footer -->
                <div class="flex justify-end gap-3 p-5 border-t border-blue-200 dark:border-blue-700">
                    <button @click.stop="hide(false)"
                            class="btn btn-secondary">
                        {{ DenyButtonText }}
                    </button>
                    <button @click.stop="hide(true)"
                            class="btn btn-primary">
                        <i data-feather="check" class="w-4 h-4 mr-1"></i>
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