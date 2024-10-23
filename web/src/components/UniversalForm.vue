<template>
    <div v-if="show"
        class="fixed top-0 left-0 right-0 bottom-0 flex items-center justify-center bg-black bg-opacity-50 p-4 overflow-hidden">
        <div class="relative w-full max-w-md max-h-[80vh]">
            <!-- Main Container with shadow and rounded corners -->
            <div class="flex flex-col rounded-lg bg-bg-light-tone-panel dark:bg-bg-dark-tone-panel shadow-lg">
                <!-- Header -->
                <div class="flex flex-row items-center p-4 border-b border-gray-200 dark:border-gray-700">
                    <div class="grow flex items-center">
                        <i data-feather="sliders" class="mr-2 flex-shrink-0"></i>
                        <h3 class="text-lg font-semibold select-none">{{ title }}</h3>
                    </div>
                    <!-- Close Button -->
                    <button @click.stop="hide(false)" title="Close"
                        class="p-1.5 hover:bg-gray-200 rounded-lg dark:hover:bg-gray-800">
                        <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                            <path fill-rule="evenodd"
                                d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z">
                            </path>
                        </svg>
                    </button>
                </div>

                <!-- Scrollable Content Area -->
                <div class="overflow-y-auto p-4 max-h-[60vh] custom-scrollbar">
                    <div class="space-y-2">
                        <div v-for="(item, index) in controls_array" :key="index" class="p-1">

                            <div v-if="item.type == 'str' || item.type == 'string'">
                                <div v-if="!item.options">
                                    <label
                                        class="mb-2 relative flex items-center gap-2 text-sm font-medium text-gray-900 dark:text-white select-none"
                                        :class="item.help ? 'cursor-pointer ' : ''">
                                        <!-- TITLE -->
                                        <div class="text-base font-semibold">
                                            {{ item.name }}:
                                        </div>

                                        <!-- HELP BUTTON -->
                                        <label v-if="item.help" class="relative inline-flex">
                                            <input type="checkbox" v-model="item.isHelp" class="sr-only peer">
                                            <div
                                                class="hover:text-secondary duration-75 active:scale-90 peer-checked:text-primary">
                                                <i data-feather="help-circle" class="w-5 h-5 "></i>
                                            </div>
                                        </label>

                                    </label>
                                    <!-- HELP DESCRIPTION -->
                                    <p v-if="item.isHelp" class="text-sm font-normal text-gray-700 dark:text-gray-400 mb-2">
                                        {{ item.help }}
                                    </p>

                                    <input type="text" v-model="item.value"
                                        class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
                                        placeholder="Enter string">
                                </div>
                                <div v-if="item.options">
                                    <label
                                        class="mb-2 relative flex items-center gap-2 text-sm font-medium text-gray-900 dark:text-white select-none"
                                        :class="item.help ? 'cursor-pointer ' : ''">
                                        <!-- TITLE -->
                                        <div class="text-base font-semibold">
                                            {{ item.name }}:
                                        </div>

                                        <!-- HELP BUTTON -->
                                        <label v-if="item.help" class="relative inline-flex">
                                            <input type="checkbox" v-model="item.isHelp" class="sr-only peer">
                                            <div
                                                class="hover:text-secondary duration-75 active:scale-90 peer-checked:text-primary">
                                                <i data-feather="help-circle" class="w-5 h-5 "></i>
                                            </div>
                                        </label>

                                    </label>
                                    <!-- HELP DESCRIPTION -->
                                    <p v-if="item.isHelp" class="text-sm font-normal text-gray-700 dark:text-gray-400 mb-2">
                                        {{ item.help }}
                                    </p>
                                    <select v-model="item.value"
                                        class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500">

                                        <option v-for="op in item.options" :value="op" :selected="item.value === op">{{
                                            op
                                        }}

                                        </option>

                                    </select>

                                </div>


                            </div>
                            <div v-if="item.type == 'btn'">
                                <button class="" onclick="btn_clicked(item)"> {{ item.name }} </button>
                            </div>
                            <div v-if="item.type == 'text'">
                                <div v-if="!item.options">
                                    <label
                                        class="mb-2 relative flex items-center gap-2 text-sm font-medium text-gray-900 dark:text-white select-none"
                                        :class="item.help ? 'cursor-pointer ' : ''">
                                        <!-- TITLE -->
                                        <div class="text-base font-semibold">
                                            {{ item.name }}:
                                        </div>

                                        <!-- HELP BUTTON -->
                                        <label v-if="item.help" class="relative inline-flex">
                                            <input type="checkbox" v-model="item.isHelp" class="sr-only peer">
                                            <div
                                                class="hover:text-secondary duration-75 active:scale-90 peer-checked:text-primary">
                                                <i data-feather="help-circle" class="w-5 h-5 "></i>
                                            </div>
                                        </label>

                                    </label>
                                    <!-- HELP DESCRIPTION -->
                                    <p v-if="item.isHelp" class="text-sm font-normal text-gray-700 dark:text-gray-400 mb-2">
                                        {{ item.help }}
                                    </p>

                                    <textarea v-model="item.value"
                                        class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
                                        placeholder="Enter string"></textarea>
                                </div>
                                <div v-if="item.options">
                                    <label
                                        class="mb-2 relative flex items-center gap-2 text-sm font-medium text-gray-900 dark:text-white select-none"
                                        :class="item.help ? 'cursor-pointer ' : ''">
                                        <!-- TITLE -->
                                        <div class="text-base font-semibold">
                                            {{ item.name }}:
                                        </div>

                                        <!-- HELP BUTTON -->
                                        <label v-if="item.help" class="relative inline-flex">
                                            <input type="checkbox" v-model="item.isHelp" class="sr-only peer">
                                            <div
                                                class="hover:text-secondary duration-75 active:scale-90 peer-checked:text-primary">
                                                <i data-feather="help-circle" class="w-5 h-5 "></i>
                                            </div>
                                        </label>

                                    </label>
                                    <!-- HELP DESCRIPTION -->
                                    <p v-if="item.isHelp" class="text-sm font-normal text-gray-700 dark:text-gray-400 mb-2">
                                        {{ item.help }}
                                    </p>
                                    <select v-model="item.value"
                                        class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500">

                                        <option v-for="op in item.options" :value="op" :selected="item.value === op">{{
                                            op
                                        }}

                                        </option>

                                    </select>

                                </div>
                            </div>                        
                            <div v-if="item.type == 'int'">
                                <label
                                    class="mb-2 relative flex items-center gap-2 text-sm font-medium text-gray-900 dark:text-white select-none"
                                    :class="item.help ? 'cursor-pointer ' : ''">
                                    <!-- TITLE -->
                                    <div class="text-base font-semibold">
                                        {{ item.name }}:
                                    </div>

                                    <!-- HELP BUTTON -->
                                    <label v-if="item.help" class="relative inline-flex">
                                        <input type="checkbox" v-model="item.isHelp" class="sr-only peer">
                                        <div class="hover:text-secondary duration-75 active:scale-90 peer-checked:text-primary">
                                            <i data-feather="help-circle" class="w-5 h-5 "></i>
                                        </div>
                                    </label>

                                </label>
                                <!-- HELP DESCRIPTION -->
                                <p v-if="item.isHelp" class="text-sm font-normal text-gray-700 dark:text-gray-400 mb-2">
                                    {{ item.help }}
                                </p>

                                <input type="number" v-model="item.value"  step="1"
                                    class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
                                    placeholder="Enter number">

                                <input v-if="(item.min != null && item.max != null)" type="range" v-model="item.value"
                                    :min="item.min" :max="item.max" step="1"
                                    class="flex-none h-2 w-full bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700  focus:ring-blue-500 focus:border-blue-500  dark:border-gray-600 dark:placeholder-gray-400  dark:focus:ring-blue-500 dark:focus:border-blue-500">
                            </div>
                            <div v-if="item.type == 'float'">
                                <label
                                    class="mb-2 relative flex items-center gap-2 text-sm font-medium text-gray-900 dark:text-white select-none"
                                    :class="item.help ? 'cursor-pointer ' : ''">
                                    <!-- TITLE -->
                                    <div class="text-base font-semibold">
                                        {{ item.name }}:
                                    </div>

                                    <!-- HELP BUTTON -->
                                    <label v-if="item.help" class="relative inline-flex">
                                        <input type="checkbox" v-model="item.isHelp" class="sr-only peer">
                                        <div class="hover:text-secondary duration-75 active:scale-90 peer-checked:text-primary">
                                            <i data-feather="help-circle" class="w-5 h-5 "></i>
                                        </div>
                                    </label>

                                </label>
                                <!-- HELP DESCRIPTION -->
                                <p v-if="item.isHelp" class="text-sm font-normal text-gray-700 dark:text-gray-400 mb-2">
                                    {{ item.help }}
                                </p>

                                <input type="number" v-model="item.value"
                                    class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
                                    placeholder="Enter number">

                                <input v-if="(item.min != null && item.max != null)" type="range" v-model="item.value"
                                    :min="item.min" :max="item.max" step="0.1"
                                    class="flex-none h-2 w-full bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700  focus:ring-blue-500 focus:border-blue-500  dark:border-gray-600 dark:placeholder-gray-400  dark:focus:ring-blue-500 dark:focus:border-blue-500">
                            </div>                        
                            <div v-if="item.type == 'bool'">
                                <div class="mb-2 relative flex items-center gap-2">

                                    <label for="default-checkbox" class="text-base font-semibold">
                                        {{ item.name }}:
                                    </label>
                                    <input type="checkbox" v-model="item.value"
                                        class="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600">

                                    <!-- HELP BUTTON -->
                                    <label v-if="item.help" class="relative inline-flex">
                                        <input type="checkbox" v-model="item.isHelp" class="sr-only peer">
                                        <div class="hover:text-secondary duration-75 active:scale-90 peer-checked:text-primary">
                                            <i data-feather="help-circle" class="w-5 h-5 "></i>
                                        </div>
                                    </label>


                                </div>
                                <!-- HELP DESCRIPTION -->
                                <p v-if="item.isHelp" class="text-sm font-normal text-gray-700 dark:text-gray-400 mb-2">
                                    {{ item.help }}
                                </p>

                            </div>
                            <div v-if="item.type == 'list'">


                                <label
                                    class="mb-2 relative flex items-center gap-2 text-sm font-medium text-gray-900 dark:text-white select-none"
                                    :class="item.help ? 'cursor-pointer ' : ''">
                                    <!-- TITLE -->
                                    <div class="text-base font-semibold">
                                        {{ item.name }}:
                                    </div>

                                    <!-- HELP BUTTON -->
                                    <label v-if="item.help" class="relative inline-flex">
                                        <input type="checkbox" v-model="item.isHelp" class="sr-only peer">
                                        <div class="hover:text-secondary duration-75 active:scale-90 peer-checked:text-primary">
                                            <i data-feather="help-circle" class="w-5 h-5 "></i>
                                        </div>
                                    </label>

                                </label>
                                <!-- HELP DESCRIPTION -->
                                <p v-if="item.isHelp" class="text-sm font-normal text-gray-700 dark:text-gray-400 mb-2">
                                    {{ item.help }}
                                </p>

                                <input type="text" v-model="item.value"
                                    class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
                                    placeholder="Enter comma separated values">
                            </div>

                            <!-- New File/Folder Input Type -->
                            <div v-if="item.type === 'file' || item.type === 'folder'" class="space-y-2">
                                <label class="flex items-center gap-2">
                                    <span class="text-base font-semibold">{{ item.name }}:</span>
                                    <!-- Help Button -->
                                    <label v-if="item.help" class="relative inline-flex">
                                        <input type="checkbox" v-model="item.isHelp" class="sr-only peer">
                                        <div class="hover:text-secondary duration-75 active:scale-90 peer-checked:text-primary">
                                            <i data-feather="help-circle" class="w-5 h-5"></i>
                                        </div>
                                    </label>
                                </label>
                                <!-- Help Text -->
                                <p v-if="item.isHelp" class="text-sm text-gray-600 dark:text-gray-400">
                                    {{ item.help }}
                                </p>
                                <!-- File/Folder Selection Input -->
                                <div class="flex gap-2">
                                    <input type="text" v-model="item.value" readonly
                                        class="flex-1 bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                                        :placeholder="item.type === 'file' ? 'Select file...' : 'Select folder...'">
                                    <button @click="openFileDialog(item)"
                                        class="px-3 py-2 text-sm font-medium text-gray-900 bg-white border border-gray-300 rounded-lg hover:bg-gray-100 dark:bg-gray-700 dark:text-white dark:border-gray-600 dark:hover:bg-gray-600">
                                        ...
                                    </button>
                                </div>
                            </div>

                            <hr v-if="index < controls_array.length - 1"
                                class="h-px my-4 bg-gray-200 border-0 dark:bg-gray-700">
                        </div>
                    </div>
                </div>

                <!-- Footer with Buttons -->
                <div class="flex justify-center gap-3 p-4 border-t border-gray-200 dark:border-gray-700">
                    <button @click.stop="hide(true)"
                        class="px-5 py-2.5 text-sm font-medium text-white bg-blue-700 rounded-lg hover:bg-blue-800 dark:bg-blue-600 dark:hover:bg-blue-700">
                        {{ ConfirmButtonText }}
                    </button>
                    <button @click.stop="hide(false)"
                        class="px-5 py-2.5 text-sm font-medium text-gray-500 bg-white rounded-lg border border-gray-200 hover:bg-gray-100 dark:bg-gray-700 dark:text-gray-300 dark:border-gray-500 dark:hover:bg-gray-600">
                        {{ DenyButtonText }}
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>
<script >
import feather from 'feather-icons'
import { nextTick, TransitionGroup } from 'vue'
export default {
    setup() {
        return {}
    },
    name: 'UniversalForm',
    //emits: ['panelLeave', 'panelDrop'],

    data() {
        return {
            show: false,
            resolve: null,
            controls_array: [],
            title: "Universal form",
            ConfirmButtonText: "Submit",
            DenyButtonText: "Cancel",
        }
    },
    mounted() {

        nextTick(() => {
            feather.replace()

        })
    },
    methods: {
        btn_clicked(item) {
            console.log(item)
        },
        hide(response) {
            this.show = false;
            
            if (this.resolve) {
                if(response){
                    this.resolve(this.controls_array);
                this.resolve = null;
                }

            }
        },
        showForm(controls_array, title, ConfirmButtonText, DenyButtonText) {
            this.ConfirmButtonText = ConfirmButtonText || this.ConfirmButtonText
            this.DenyButtonText = DenyButtonText || this.DenyButtonText
            //let moddedArr =[]
            // add aditional values for UI
            for (let i = 0; i < controls_array.length; i++) {
                controls_array[i].isHelp = false

            }


            return new Promise((resolve) => {
                this.controls_array = controls_array;
                this.show = true;
                this.title = title || this.title
                this.resolve = resolve;
                console.log('show form', this.controls_array)
            });
        },
        openFileDialog(item) {
            // Create input element
            const input = document.createElement('input');
            input.type = 'file';
            if (item.type === 'folder') {
                input.webkitdirectory = true;
                input.directory = true;
            }
            
            // Set accepted file types if specified
            if (item.accept) {
                input.accept = item.accept;
            }

            // Handle file selection
            input.onchange = (e) => {
                if (e.target.files.length > 0) {
                    item.value = e.target.files[0].path;
                }
            };

            // Trigger file dialog
            input.click();
        }

    },
    watch: {
        controls_array: {
        deep: true,
        handler(newArray) {
            newArray.forEach(item => {
            if (item.type === 'int') {
                item.value = parseInt(item.value);
            } else if (item.type === 'float') {
                item.value = parseFloat(item.value);
            }
            // Add more conditions for other types if needed
            });
        }
        },
        show() {
            nextTick(() => {
                feather.replace()

            })
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
    width: 6px;
}

.custom-scrollbar::-webkit-scrollbar-track {
    background: transparent;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
    background-color: rgba(156, 163, 175, 0.5);
    border-radius: 3px;
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
    background-color: rgba(156, 163, 175, 0.7);
}
</style>
