<template>
    <div v-if="show"
        class="fixed top-0 left-0 right-0 bottom-0 flex items-center justify-center bg-black bg-opacity-50 p-4">
        <div class="relative w-full max-w-md">

            <div
                class="flex flex-col  rounded-lg bg-bg-light-tone-panel dark:bg-bg-dark-tone-panel duration-150 shadow-lg max-h-screen">
                <div class="flex flex-row flex-grow items-center m-2 p-1">
                    <div class="grow flex items-center">
                        <i data-feather="sliders" class="mr-2 flex-shrink-0"></i>
                        <h3 class="text-lg font-semibold select-none mr-2">
                            {{ title }}</h3>
                    </div>


                    <!-- CLOSE BUTTON -->
                    <div class="items-end">
                        <button type="button" @click.stop="hide(false)" title="Close"
                            class=" bg-transparent hover:bg-gray-200 hover:text-gray-900 rounded-lg text-sm p-1.5 ml-auto inline-flex items-center dark:hover:bg-gray-800 dark:hover:text-white">
                            <svg aria-hidden="true" class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"
                                xmlns="http://www.w3.org/2000/svg">
                                <path fill-rule="evenodd"
                                    d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                                    clip-rule="evenodd"></path>
                            </svg>
                            <span class="sr-only">Close form modal</span>
                        </button>
                    </div>
                </div>
                <!-- FORM AREA -->
                <div class="flex flex-col relative no-scrollbar overflow-y-scroll p-2">
                    <!-- odd:bg-bg-light-tone odd:dark:bg-bg-dark-tone even:bg-bg-light-tone-panel dark:even:bg-bg-dark-tone-panel -->
                    <div class="px-2 " v-for="(item, index) in controls_array">

                        <div v-if="item.type == 'str'">
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
                        <hr class="h-px my-4 bg-gray-200 border-0 dark:bg-gray-700">
                    </div>

                    <!-- SUBMIT AND CANCEL BUTTONS -->
                    <div class="flex  flex-row flex-grow gap-3">
                        <div class="p-2 text-center grow">
                            <button @click.stop="hide(true)" type="button"
                                class="mr-2 text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-lg text-sm  sm:w-auto px-5 py-2.5 text-center dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800">
                                {{ ConfirmButtonText }}
                            </button>
                            <button @click.stop="hide(false)" type="button"
                                class="text-gray-500 bg-white hover:bg-gray-100 focus:ring-4 focus:outline-none focus:ring-gray-200 rounded-lg border border-gray-200 text-sm font-medium px-5 py-2.5 hover:text-gray-900 focus:z-11 dark:bg-gray-700 dark:text-gray-300 dark:border-gray-500 dark:hover:text-white dark:hover:bg-gray-600 dark:focus:ring-gray-600">
                                {{ DenyButtonText }}
                            </button>
                        </div>

                    </div>



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
                console.log('show foam', this.controls_array)
            });
        },

    },
    watch: {
        show() {
            nextTick(() => {
                feather.replace()

            })
        }
    }
}
</script>

