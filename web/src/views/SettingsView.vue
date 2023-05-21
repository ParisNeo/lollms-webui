<template>
    <div class="container overflow-y-scroll flex flex-col no-scrollbar shadow-lg p-10 pt-0 ">
        <!-- CONTROL PANEL -->
        <div
            class="sticky top-0 z-10 flex flex-row mb-2 p-3 gap-3 w-full rounded-b-lg bg-bg-light-tone dark:bg-bg-dark-tone  shadow-lg">
            <!-- SAVE CONFIG -->
            <div v-if="showConfirmation" class="flex gap-3 flex-1 items-center duration-75">
                <button class="text-2xl hover:text-red-600 duration-75 active:scale-90 " title="Cancel" type="button"
                    @click.stop="showConfirmation = false">
                    <i data-feather="x"></i>
                </button>
                <button class="text-2xl hover:text-secondary duration-75 active:scale-90" title="Confirm save changes"
                    type="button" @click.stop="save_configuration()">
                    <i data-feather="check"></i>
                </button>
            </div>
            <!-- SAVE AND RESET -->
            <div v-if="!showConfirmation" class="flex gap-3 flex-1 items-center ">
                <button title="Save configuration" class="text-2xl hover:text-secondary duration-75 active:scale-90"
                    @click="showConfirmation = true">
                    <i data-feather="save"></i>
                </button>
                <button title="Reset configuration" class="text-2xl hover:text-secondary duration-75 active:scale-90"
                    @click="reset_configuration()">
                    <i data-feather="refresh-ccw"></i>
                </button>
                <button class="text-2xl hover:text-secondary duration-75 active:scale-90"
                    title="Collapse / Expand all panels" type="button" @click.stop="all_collapsed = !all_collapsed">
                    <i data-feather="list"></i>
                </button>
            </div>
            <div class="flex gap-3 flex-1 items-center justify-end">


                <div v-if="!isModelSelected" class="text-red-600 flex gap-3 items-center">
                    <i data-feather="alert-triangle"></i>
                    No model selected!
                </div>
                <div v-if="settingsChanged" class="flex gap-3 items-center">

                    Apply changes:
                    <button v-if="!isLoading" class="text-2xl hover:text-secondary duration-75 active:scale-90"
                        title="Apply changes" type="button" @click.stop="applyConfiguration()">
                        <i data-feather="check"></i>
                    </button>
                    <!-- SPINNER -->
                    <div v-if="isLoading" role="status">
                        <svg aria-hidden="true" class="w-6 h-6   animate-spin  fill-secondary" viewBox="0 0 100 101"
                            fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path
                                d="M100 50.5908C100 78.2051 77.6142 100.591 50 100.591C22.3858 100.591 0 78.2051 0 50.5908C0 22.9766 22.3858 0.59082 50 0.59082C77.6142 0.59082 100 22.9766 100 50.5908ZM9.08144 50.5908C9.08144 73.1895 27.4013 91.5094 50 91.5094C72.5987 91.5094 90.9186 73.1895 90.9186 50.5908C90.9186 27.9921 72.5987 9.67226 50 9.67226C27.4013 9.67226 9.08144 27.9921 9.08144 50.5908Z"
                                fill="currentColor" />
                            <path
                                d="M93.9676 39.0409C96.393 38.4038 97.8624 35.9116 97.0079 33.5539C95.2932 28.8227 92.871 24.3692 89.8167 20.348C85.8452 15.1192 80.8826 10.7238 75.2124 7.41289C69.5422 4.10194 63.2754 1.94025 56.7698 1.05124C51.7666 0.367541 46.6976 0.446843 41.7345 1.27873C39.2613 1.69328 37.813 4.19778 38.4501 6.62326C39.0873 9.04874 41.5694 10.4717 44.0505 10.1071C47.8511 9.54855 51.7191 9.52689 55.5402 10.0491C60.8642 10.7766 65.9928 12.5457 70.6331 15.2552C75.2735 17.9648 79.3347 21.5619 82.5849 25.841C84.9175 28.9121 86.7997 32.2913 88.1811 35.8758C89.083 38.2158 91.5421 39.6781 93.9676 39.0409Z"
                                fill="currentFill" />
                        </svg>
                        <span class="sr-only">Loading...</span>
                    </div>
                    <!-- <button @click="applyConfiguration" class="bg-primary text-white py-1 px-4 rounded">
                    Apply Configuration
                    <div v-if="isLoading" class="loader"></div>    v-if="settingsChanged"
                </button> -->
                </div>
            </div>
        </div>
        <!-- BACKEND -->
        <!-- DISABLED FOR NOW -->
        <!-- <div
            class="flex flex-col mb-2 p-3 rounded-lg bg-bg-light-tone dark:bg-bg-dark-tone hover:bg-bg-light-tone-panel hover:dark:bg-bg-dark-tone-panel duration-150 shadow-lg">
            <div class="flex flex-row ">
                <button @click.stop="bec_collapsed = !bec_collapsed"
                    class="text-2xl hover:text-primary duration-75 p-2 -m-2 w-full text-left active:translate-y-1 flex items-center">
                    <i :data-feather="mzc_collapsed ? 'chevron-right' : 'chevron-down'" class="mr-2"></i>
                    <h3 class="text-lg font-semibold cursor-pointer select-none">
                        Backend Configuration</h3>
                </button>
            </div>
            <div :class="{ 'hidden': bec_collapsed }" class="flex flex-col mb-2 p-2">
                <div class="m-2">
                    <label for="backend" class="block mb-2 text-sm font-medium text-gray-900 dark:text-white">
                        Backend:
                    </label>
                    <select id="backend" @change="update_backend($event.target.value)"
                        class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500">

                        <option v-for="item in backendsArr" :selected="item === configFile.backend">{{ item }}</option>
                    </select>
                </div>
                <div class="m-2">
                    <label for="model" class="block mb-2 text-sm font-medium text-gray-900 dark:text-white">
                        Model:
                    </label>
                    <select id="model" @change="update_model($event.target.value)"
                        @mouseup="update_model($event.target.value)"
                        class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500">

                        <option v-for="item in modelsArr" :selected="item === configFile.model">{{ item }}</option>

                    </select>
                </div>
            </div>
        </div> -->
        <div
            class="flex flex-col mb-2  rounded-lg bg-bg-light-tone dark:bg-bg-dark-tone hover:bg-bg-light-tone-panel hover:dark:bg-bg-dark-tone-panel duration-150 shadow-lg">
            <div class="flex flex-row p-3">
                <button @click.stop="mzc_collapsed = !mzc_collapsed"
                    class="text-2xl hover:text-primary duration-75 p-2 -m-2 w-full text-left active:translate-y-1 flex items-center">
                    <i :data-feather="mzc_collapsed ? 'chevron-right' : 'chevron-down'" class="mr-2"></i>
                    <h3 class="text-lg font-semibold cursor-pointer select-none">
                        Models zoo</h3>
                </button>
            </div>
            <div :class="{ 'hidden': mzc_collapsed }" class="flex flex-col mb-2 px-3 pb-0">
                <div class="mx-2 mb-4">
                    <label for="backend" class="block mb-2 text-sm font-medium text-gray-900 dark:text-white">
                        Backend:
                    </label>
                    <select id="backend" @change="update_backend($event.target.value)"
                        class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500">

                        <option v-for="item in backendsArr" :selected="item === configFile.backend">{{ item }}</option>
                    </select>
                </div>
                <div v-if="models.length > 0" class="mb-2">
                    <label for="model" class="block ml-2 mb-2 text-sm font-medium text-gray-900 dark:text-white">
                        Models:
                    </label>
                    <div ref="modelZoo" class="overflow-y-auto no-scrollbar p-2 pb-0"
                        :class="mzl_collapsed ? '' : 'max-h-96'">
                        <model-entry v-for="(model, index) in models" :key="index" :title="model.title" :icon="model.icon"
                            :path="model.path" :owner="model.owner" :owner_link="model.owner_link" :license="model.license" :description="model.description" :is-installed="model.isInstalled"
                            :on-install="onInstall" :on-uninstall="onUninstall" :on-selected="onSelected"
                            :selected="model.title === configFile.model" />
                    </div>
                </div>
                <!-- EXPAND / COLLAPSE BUTTON -->
                <button v-if="mzl_collapsed"
                    class="text-2xl hover:text-secondary duration-75 flex justify-center  hover:bg-bg-light-tone hover:dark:bg-bg-dark-tone rounded-lg "
                    title="Collapse" type="button" @click="mzl_collapsed = !mzl_collapsed">
                    <i data-feather="chevron-up"></i>
                </button>
                <button v-else
                    class="text-2xl hover:text-secondary duration-75 flex justify-center  hover:bg-bg-light-tone hover:dark:bg-bg-dark-tone rounded-lg "
                    title="Expand" type="button" @click="mzl_collapsed = !mzl_collapsed">
                    <i data-feather="chevron-down"></i>
                </button>
            </div>

        </div>
        <!-- PERSONALITY -->
        <div
            class="flex flex-col mb-2 p-3 rounded-lg bg-bg-light-tone dark:bg-bg-dark-tone hover:bg-bg-light-tone-panel hover:dark:bg-bg-dark-tone-panel duration-150 shadow-lg">
            <div class="flex flex-row">
                <button @click.stop="pc_collapsed = !pc_collapsed"
                    class="text-2xl hover:text-primary duration-75 p-2 -m-2 w-full text-left active:translate-y-1 flex items-center">
                    <i :data-feather="pc_collapsed ? 'chevron-right' : 'chevron-down'" class="mr-2"></i>
                    <h3 class="text-lg font-semibold cursor-pointer select-none">
                        Personality Configuration</h3>
                </button>
            </div>
            <div :class="{ 'hidden': pc_collapsed }" class="flex flex-col mb-2 p-2">
                <div class="m-2">
                    <label for="persLang" class="block mb-2 text-sm font-medium text-gray-900 dark:text-white">
                        Personalities Languages:
                    </label>
                    <select id="persLang" @change="update_setting('personality_language', $event.target.value, refresh)"
                        class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500">

                        <option v-for="item in persLangArr" :selected="item === configFile.personality_language">{{ item }}

                        </option>

                    </select>
                </div>
                <div class="m-2">
                    <label for="persCat" class="block mb-2 text-sm font-medium text-gray-900 dark:text-white">
                        Personalities Category:
                    </label>
                    <select id="persCat" @change="update_setting('personality_category', $event.target.value, refresh)"
                        class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500">

                        <option v-for="item in persCatgArr" :selected="item === configFile.personality_category">{{ item }}

                        </option>

                    </select>
                </div>
                <div class="m-2">
                    <label for="persona" class="block mb-2 text-sm font-medium text-gray-900 dark:text-white">
                        Personality:
                    </label>
                    <select id="persona" @change="update_setting('personality', $event.target.value, refresh)"
                        class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500">

                        <option v-for="item in persArr" :selected="item === configFile.personality">{{ item }}</option>

                    </select>
                </div>
                <div class="m-2">
                        <button @click="applyConfiguration" class="bg-blue-500 text-white py-2 px-4 rounded">
                            Apply Configuration
                        </button>
                        <div v-if="isLoading" class="loader"></div>
                </div>                      

            </div>
        </div>
        <div
            class="flex flex-col mb-2 p-3 rounded-lg bg-bg-light-tone dark:bg-bg-dark-tone hover:bg-bg-light-tone-panel hover:dark:bg-bg-dark-tone-panel duration-150 shadow-lg">
            <div class="flex flex-row ">
                <button @click.stop="pzc_collapsed = !pzc_collapsed"
                    class="text-2xl hover:text-primary duration-75 p-2 -m-2 w-full text-left active:translate-y-1 flex items-center">
                    <i :data-feather="mc_collapsed ? 'chevron-right' : 'chevron-down'" class="mr-2"></i>
                    <h3 class="text-lg font-semibold cursor-pointer select-none">
                        Personalities zoo
                    </h3>
                </button>
            </div>
            <div :class="{ 'hidden': pzc_collapsed }" class="flex flex-col mb-2 p-2">
                <div v-if="models.length > 0" class="my-2">
                    <label for="model" class="block ml-2 mb-2 text-sm font-medium text-gray-900 dark:text-white">
                        Install more models:
                    </label>
                    <div class="overflow-y-auto max-h-96 no-scrollbar p-2">

                    </div>
                </div>
            </div>
        </div>
        <!-- MODEL -->
        <div
            class="flex flex-col mb-2 p-3 rounded-lg bg-bg-light-tone dark:bg-bg-dark-tone hover:bg-bg-light-tone-panel hover:dark:bg-bg-dark-tone-panel duration-150 shadow-lg">
            <div class="flex flex-row">
                <button @click.stop="mc_collapsed = !mc_collapsed"
                    class="text-2xl hover:text-primary duration-75 p-2 -m-2 w-full text-left active:translate-y-1 flex items-center">
                    <i :data-feather="mc_collapsed ? 'chevron-right' : 'chevron-down'" class="mr-2"></i>
                    <h3 class="text-lg font-semibold cursor-pointer select-none">
                        Model Configuration</h3>
                </button>
            </div>
            <div :class="{ 'hidden': mc_collapsed }" class="flex flex-col mb-2 p-2">
                <div class="m-2">
                    <label for="seed" class="block mb-2 text-sm font-medium ">
                        Seed:
                    </label>
                    <input type="text" id="seed" v-model="configFile.seed"
                        class="bg-gray-50 border border-gray-300 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400  dark:focus:ring-blue-500 dark:focus:border-blue-500">
                </div>
                <div class="m-2">
                    <div class="flex flex-col align-bottom ">
                        <div class="relative">
                            <p class="absolute left-0 mt-6">
                                <label for="temperature" class=" text-sm font-medium">
                                    Temperature:
                                </label>
                            </p>
                            <p class="absolute right-0">

                                <input type="text" id="temp-val" v-model="configFile.temperature"
                                    class="mt-2 w-16 text-right p-2 border border-gray-300 rounded-lg bg-gray-50 sm:text-xs focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500">
                            </p>

                        </div>

                        <input id="temperature" @change="update_setting('temperature', $event.target.value)" type="range"
                            v-model="configFile.temperature" min="0" max="5" step="0.1"
                            class="flex-none h-2 mt-14 mb-2 w-full bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700  focus:ring-blue-500 focus:border-blue-500  dark:border-gray-600 dark:placeholder-gray-400  dark:focus:ring-blue-500 dark:focus:border-blue-500">
                    </div>
                </div>
                <div class="m-2">
                    <div class="flex flex-col align-bottom ">
                        <div class="relative">
                            <p class="absolute left-0 mt-6">
                                <label for="predict" class=" text-sm font-medium">
                                    N Predict:
                                </label>
                            </p>
                            <p class="absolute right-0">

                                <input type="text" id="predict-val" v-model="configFile.n_predict"
                                    class="mt-2 w-16 text-right p-2 border border-gray-300 rounded-lg bg-gray-50 sm:text-xs focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500">
                            </p>

                        </div>

                        <input id="predict" @change="update_setting('n_predict', $event.target.value)" type="range"
                            v-model="configFile.n_predict" min="0" max="2048" step="32"
                            class="flex-none h-2 mt-14 mb-2 w-full bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700  focus:ring-blue-500 focus:border-blue-500  dark:border-gray-600 dark:placeholder-gray-400  dark:focus:ring-blue-500 dark:focus:border-blue-500">
                    </div>
                </div>
                <div class="m-2">
                    <div class="flex flex-col align-bottom ">
                        <div class="relative">
                            <p class="absolute left-0 mt-6">
                                <label for="top_k" class=" text-sm font-medium">
                                    Top-K:
                                </label>
                            </p>
                            <p class="absolute right-0">

                                <input type="text" id="top_k-val" v-model="configFile.top_k"
                                    class="mt-2 w-16 text-right p-2 border border-gray-300 rounded-lg bg-gray-50 sm:text-xs focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500">
                            </p>

                        </div>

                        <input id="top_k" @change="update_setting('top_k', $event.target.value)" type="range"
                            v-model="configFile.top_k" min="0" max="100" step="1"
                            class="flex-none h-2 mt-14 mb-2 w-full bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700  focus:ring-blue-500 focus:border-blue-500  dark:border-gray-600 dark:placeholder-gray-400  dark:focus:ring-blue-500 dark:focus:border-blue-500">
                    </div>
                </div>
                <div class="m-2">
                    <div class="flex flex-col align-bottom ">
                        <div class="relative">
                            <p class="absolute left-0 mt-6">
                                <label for="top_p" class=" text-sm font-medium">
                                    Top-P:
                                </label>
                            </p>
                            <p class="absolute right-0">

                                <input type="text" id="top_p-val" v-model="configFile.top_p"
                                    class="mt-2 w-16 text-right p-2 border border-gray-300 rounded-lg bg-gray-50 sm:text-xs focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500">
                            </p>

                        </div>

                        <input id="top_p" @change="update_setting('top_p', $event.target.value)" type="range"
                            v-model="configFile.top_p" min="0" max="1" step="0.01"
                            class="flex-none h-2 mt-14 mb-2 w-full bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700  focus:ring-blue-500 focus:border-blue-500  dark:border-gray-600 dark:placeholder-gray-400  dark:focus:ring-blue-500 dark:focus:border-blue-500">
                    </div>
                </div>
                <div class="m-2">
                    <div class="flex flex-col align-bottom ">
                        <div class="relative">
                            <p class="absolute left-0 mt-6">
                                <label for="repeat_penalty" class=" text-sm font-medium">
                                    Repeat penalty:
                                </label>
                            </p>
                            <p class="absolute right-0">

                                <input type="text" id="repeat_penalty-val" v-model="configFile.repeat_penalty"
                                    class="mt-2 w-16 text-right p-2 border border-gray-300 rounded-lg bg-gray-50 sm:text-xs focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500">
                            </p>

                        </div>

                        <input id="repeat_penalty" @change="update_setting('repeat_penalty', $event.target.value)"
                            type="range" v-model="configFile.repeat_penalty" min="0" max="2" step="0.01"
                            class="flex-none h-2 mt-14 mb-2 w-full bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700  focus:ring-blue-500 focus:border-blue-500  dark:border-gray-600 dark:placeholder-gray-400  dark:focus:ring-blue-500 dark:focus:border-blue-500">
                    </div>
                </div>
                <div class="m-2">
                    <div class="flex flex-col align-bottom ">
                        <div class="relative">
                            <p class="absolute left-0 mt-6">
                                <label for="repeat_last_n" class=" text-sm font-medium">
                                    Repeat last N:
                                </label>
                            </p>
                            <p class="absolute right-0">

                                <input type="text" id="repeat_last_n-val" v-model="configFile.repeat_last_n"
                                    class="mt-2 w-16 text-right p-2 border border-gray-300 rounded-lg bg-gray-50 sm:text-xs focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500">
                            </p>

                        </div>

                        <input id="repeat_last_n" @change="update_setting('repeat_last_n', $event.target.value)"
                            type="range" v-model="configFile.repeat_last_n" min="0" max="100" step="1"
                            class="flex-none h-2 mt-14 mb-2 w-full bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700  focus:ring-blue-500 focus:border-blue-500  dark:border-gray-600 dark:placeholder-gray-400  dark:focus:ring-blue-500 dark:focus:border-blue-500">
                    </div>
                </div>
            </div>
        </div>


    </div>

    <YesNoDialog ref="yesNoDialog" />
    <MessageBox ref="messageBox" />
    <Toast ref="toast" />
</template>

<script>
import axios from "axios";
import feather from 'feather-icons'
import { nextTick } from 'vue'
import MessageBox from "@/components/MessageBox.vue";
import YesNoDialog from "@/components/YesNoDialog.vue";
import Toast from '../components/Toast.vue'
import ModelEntry from '@/components/ModelEntry.vue';
import PersonalityViewer from '@/components/PersonalityViewer.vue';
import socket from '@/services/websocket.js'
axios.defaults.baseURL = import.meta.env.VITE_GPT4ALL_API_BASEURL
export default {
    components: {
        MessageBox,
        YesNoDialog,
        ModelEntry,
        // eslint-disable-next-line vue/no-unused-components
        PersonalityViewer,
        Toast
    },
    data() {

        return {
            // Models zoo installer stuff
            models: [],
            personalities: [],
            // Accordeon stuff 
            collapsedArr: [],
            all_collapsed: true,
            bec_collapsed: true,
            mzc_collapsed: true, // models zoo
            pzc_collapsed: true, // personalities zoo
            pc_collapsed: true,
            mc_collapsed: true,
            // Zoo accordeoon
            mzl_collapsed: false,
            // Settings stuff
            backendsArr: [],
            modelsArr: [], // not used anymore but still have references in some methods
            persLangArr: [],
            persCatgArr: [],
            persArr: [],
            langArr: [],
            configFile: {},
            showConfirmation: false,
            showToast: false,
            isLoading: false,
            settingsChanged: false,
            isModelSelected: false

        }
    },
    created() {

    }, methods: {
        collapseAll(val) {
            this.bec_collapsed = val
            this.mzc_collapsed = val
            this.pzc_collapsed = val
            this.pc_collapsed = val
            this.mc_collapsed = val
        },
        fetchModels() {
            console.log("Fetching models")
            axios.get('/get_available_models')
                .then(response => {
                    console.log(`Models list recovered successfuly: ${JSON.stringify(response.data)}`)
                    this.models = response.data;
                })
                .catch(error => {
                    console.log(error);
                });
        },
        onSelected(model_object) {
            console.log("Selected model")
            // eslint-disable-next-line no-unused-vars
            if (model_object) {
                if (model_object.isInstalled) {
                    if (this.configFile.model != model_object.title) {
                        this.update_model(model_object.title)
                        this.configFile.model = model_object.title
                        this.$refs.toast.showToast("Model:\n" + model_object.title + "\nselected", 4, true)
                        this.settingsChanged = true
                        this.isModelSelected = true
                    }

                } else {
                    this.$refs.toast.showToast("Model:\n" + model_object.title + "\nis not installed", 4, false)
                }
                nextTick(() => {
                    feather.replace()

                })
            }

            //this.update_setting('model', model_object.title, (res)=>{console.log("Model selected"); })
        },
        // Model installation

        onInstall(model_object) {
            let path = model_object.path;
            this.showProgress = true;
            this.progress = 0;
            console.log("installing...");

            // Use an arrow function for progressListener
            const progressListener = (response) => {
                console.log("received something");
                if (response.status === 'progress') {
                    console.log(`Progress = ${response.progress}`);
                    model_object.progress = response.progress
                } else if (response.status === 'succeeded') {
                    socket.off('install_progress', progressListener);
                    // Update the isInstalled property of the corresponding model
                    const index = this.models.findIndex((model) => model.path === path);
                    this.models[index].isInstalled = true;
                    this.showProgress = false;

                } else if (response.status === 'failed') {
                    socket.off('install_progress', progressListener);
                    // Installation failed or encountered an error
                    model_object.installing = false;
                    this.showProgress = false;
                    console.error('Installation failed:', response.error);
                }
            };

            socket.on('install_progress', progressListener);
            socket.emit('install_model', { path: path });
            console.log("Started installation, please wait");
        },
        onUninstall(model_object) {
            console.log("uninstalling model...")
            const progressListener = (response) => {
                if (response.status === 'progress') {
                    this.progress = response.progress;
                } else if (response.status === 'succeeded') {
                    console.log(model_object)
                    // Installation completed
                    model_object.uninstalling = false;
                    socket.off('install_progress', progressListener);
                    this.showProgress = false;
                    const index = this.models.findIndex((model) => model.path === model_object.path);
                    this.models[index].isInstalled = false;
                } else if (response.status === 'failed') {
                    // Installation failed or encountered an error
                    model_object.uninstalling = false;
                    this.showProgress = false;
                    socket.off('install_progress', progressListener);
                    // eslint-disable-next-line no-undef
                    console.error('Installation failed:', message.error);
                }
            };
            socket.on('install_progress', progressListener);
            socket.emit('uninstall_model', { path: model_object.path });
        },
        // messagebox ok stuff
        onMessageBoxOk() {
            console.log("OK button clicked");
        },
        // Refresh stuff
        refresh() {

            console.log("Refreshing")
            // No need to refresh all lists because they never change during using application. 
            // On settings change only config file chnages.
            //
            //this.api_get_req("list_backends").then(response => { this.backendsArr = response })
            this.api_get_req("list_models").then(response => { this.modelsArr = response })
            //this.api_get_req("list_personalities_languages").then(response => { this.persLangArr = response })
            this.api_get_req("list_personalities_categories").then(response => { this.persCatgArr = response })
            this.api_get_req("list_personalities").then(response => { this.persArr = response })
            //this.api_get_req("list_languages").then(response => { this.langArr = response })
            this.api_get_req("get_config").then(response => {
                this.configFile = response
                console.log("selecting model")
                this.models.forEach(model => {
                    console.log(`${model} -> ${response["model"]}`)
                    if (model.title == response["model"]) {
                        model.selected = true;

                    }
                    else {
                        model.selected = false;
                    }
                });
            })

            this.fetchModels();
        },
        // Accordeon stuff
        toggleAccordion() {
            this.showAccordion = !this.showAccordion;
        },
        update_setting(setting_name_val, setting_value_val, next) {
            const obj = {
                setting_name: setting_name_val,
                setting_value: setting_value_val
            }
            console.log("change", setting_name_val, setting_value_val, obj)
            axios.post('/update_setting', obj).then((res) => {
                console.log("Update setting done")
                if (res) {
                    console.log("res is ok")
                    if (next !== undefined) {
                        console.log("Calling next")
                        next(res)
                    }
                    return res.data;
                }
            })
                // eslint-disable-next-line no-unused-vars
                .catch(error => { return { 'status': false } });
        },
        update_backend(value) {

            console.log("Upgrading backend")
            // eslint-disable-next-line no-unused-vars
            this.update_setting('backend', value, (res) => {
                this.refresh();
                console.log("Backend changed");
                console.log(res);
                this.$refs.toast.showToast("Backend changed.", 4, true)
                this.settingsChanged = true

                nextTick(() => {
                    feather.replace()

                })
                // If backend changes then reset model
                this.update_model(null)
            })

        },
        update_model(value) {
            if (!value) this.isModelSelected = false

            console.log("Upgrading model")
            // eslint-disable-next-line no-unused-vars
            this.update_setting('model', value, (res) => { console.log("Model changed"); this.fetchModels(); })
        },
        applyConfiguration() {
            if (!this.configFile.model) {
                console.log("applying configuration failed")
                    this.$refs.toast.showToast("Configuration changed failed.\nPlease select model first", 4, false)
                    nextTick(() => {
                    feather.replace()
                })
                return
            }
            this.isLoading = true;
            axios.post('/apply_settings').then((res) => {
                this.isLoading = false;
                console.log(res.data)
                if (res.data.status === "succeeded") {
                    console.log("applying configuration succeeded")
                    this.$refs.toast.showToast("Configuration changed successfully.", 4, true)
                    this.settingsChanged = false
                } else {
                    console.log("applying configuration failed")
                    this.$refs.toast.showToast("Configuration change failed.", 4, false)

                }
                nextTick(() => {
                    feather.replace()

                })
            })
        },
        save_configuration() {
            this.showConfirmation = false
            axios.post('/save_settings', {})
                .then((res) => {
                    if (res) {
                        if (res.status){
                            this.$refs.messageBox.showMessage("Settings saved!")
                        }
                        else
                            this.$refs.messageBox.showMessage("Error: Couldn't save settings!")
                        return res.data;
                    }
                })
                .catch(error => {
                    console.log(error)
                    this.$refs.messageBox.showMessage("Couldn't save settings!")
                    return { 'status': false }
                });

        },
        reset_configuration() {
            this.$refs.yesNoDialog.askQuestion("Are you sure?\nThis will delete all your configurations and get back to default configuration.").then(response => {
                if (response) {
                    // User clicked Yes
                    axios.post('/reset_settings', {})
                        .then((res) => {
                            if (res) {
                                if (res.status)
                                    this.$refs.messageBox.showMessage("Settings have been reset correctly")
                                else
                                    this.$refs.messageBox.showMessage("Couldn't reset settings!")
                                return res.data;
                            }
                        })
                        .catch(error => {
                            console.log(error)
                            this.$refs.messageBox.showMessage("Couldn't reset settings!")
                            return { 'status': false }
                        });
                    // Perform delete operation
                } else {
                    // User clicked No
                    // Do nothing
                }
            });
        },

        async api_get_req(endpoint) {
            try {
                const res = await axios.get("/" + endpoint);

                if (res) {

                    return res.data

                }
            } catch (error) {
                console.log(error)
                return
            }


        },
        closeToast() {
            this.showToast = false
        },

    }, async mounted() {
        nextTick(() => {
            feather.replace()

        })
        this.configFile = await this.api_get_req("get_config")
        if (this.configFile.model) {
            this.isModelSelected = true
        }
        this.fetchModels();
        this.backendsArr = await this.api_get_req("list_backends")
        this.modelsArr = await this.api_get_req("list_models")
        this.persLangArr = await this.api_get_req("list_personalities_languages")
        this.persCatgArr = await this.api_get_req("list_personalities_categories")
        this.persArr = await this.api_get_req("list_personalities")
        this.langArr = await this.api_get_req("list_languages")

    },
    watch: {
        bec_collapsed() {
            nextTick(() => {
                feather.replace()

            })
        },
        pc_collapsed() {
            nextTick(() => {
                feather.replace()

            })
        },
        mc_collapsed() {
            nextTick(() => {
                feather.replace()

            })
        },
        showConfirmation() {
            nextTick(() => {
                feather.replace()

            })
        },
        mzl_collapsed() {

            nextTick(() => {
                feather.replace()

            })
        },
        all_collapsed(val) {
            this.collapseAll(val)
            nextTick(() => {
                feather.replace()

            })
        },
        settingsChanged() {
            nextTick(() => {
                feather.replace()

            })
        },
        isModelSelected(val) {

            console.log('iss selected:', val)
        }
        // configFile(){
        //     nextTick(() => {
        //         feather.replace()

        //     }) 
        // }

    }
}
</script>


<style>
.loader {
    border: 4px solid #f3f3f3;
    border-top: 4px solid #3498db;
    border-radius: 50%;
    width: 16px;
    height: 16px;
    animation: spin 2s linear infinite;
    margin-left: 8px;
    display: inline-block;
}

.height-64 {
    min-height: 64px;
}

@keyframes spin {
    0% {
        transform: rotate(0deg);
    }

    100% {
        transform: rotate(360deg);
    }
}
</style>