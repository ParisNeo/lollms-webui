<template>
    <div class="container overflow-y-scroll flex flex-col no-scrollbar shadow-lg p-10 pt-0 ">
        <!-- CONTROL PANEL -->
        <div class="sticky top-0 z-10 flex flex-row mb-2 p-3 gap-3 w-full rounded-b-lg bg-bg-light-tone dark:bg-bg-dark-tone  shadow-lg">
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
            </div>

        </div>
        <!-- BACKEND -->
        <div
            class="flex flex-col mb-2 p-3 rounded-lg bg-bg-light-tone dark:bg-bg-dark-tone hover:bg-bg-light-tone-panel hover:dark:bg-bg-dark-tone-panel duration-150 shadow-lg">
            <div class="flex flex-row ">
                <button @click.stop="bec_collapsed = !bec_collapsed"
                    class="text-2xl hover:text-primary duration-75  p-2 -m-2 w-full text-left active:translate-y-1">
                    <!-- <i data-feather="chevron-right"></i> -->

                    <h3 class="text-lg font-semibold cursor-pointer select-none "
                        @click.stop="bec_collapsed = !bec_collapsed">
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
                    <select id="model"
                        class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500">

                        <option v-for="item in modelsArr" :selected="item === configFile.model">{{ item }}</option>

                    </select>
                </div>
                <div v-if="models.length > 0" class="my-2">
                    <label for="model" class="block ml-2 mb-2 text-sm font-medium text-gray-900 dark:text-white">
                        Install more models:
                    </label>
                    <div class="overflow-y-auto max-h-96 no-scrollbar p-2">
                        <model-entry v-for="(model, index) in models" :key="index" :title="model.title" :icon="model.icon"
                            :path="model.path" :description="model.description" :is-installed="model.isInstalled"
                            :on-install="onInstall"
                            :on-uninstall="onUninstall" />
                    </div>
                </div>
            </div>
        </div>

        <!-- PERSONALITY -->
        <div
            class="flex flex-col mb-2 p-3 rounded-lg bg-bg-light-tone dark:bg-bg-dark-tone hover:bg-bg-light-tone-panel hover:dark:bg-bg-dark-tone-panel duration-150 shadow-lg">
            <div class="flex flex-row">
                <button @click.stop="pc_collapsed = !pc_collapsed"
                    class="text-2xl hover:text-primary duration-75  p-2 -m-2 w-full text-left active:translate-y-1">

                    <!-- <i data-feather="chevron-right"></i> -->

                    <h3 class="text-lg font-semibold cursor-pointer select-none" @click.stop="pc_collapsed = !pc_collapsed">
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
            </div>
        </div>

        <!-- MODEL -->
        <div
            class="flex flex-col mb-2 p-3 rounded-lg bg-bg-light-tone dark:bg-bg-dark-tone hover:bg-bg-light-tone-panel hover:dark:bg-bg-dark-tone-panel duration-150 shadow-lg">
            <div class="flex flex-row">
                <button @click.stop="mc_collapsed = !mc_collapsed"
                    class="text-2xl hover:text-primary duration-75 p-2 -m-2 w-full text-left active:translate-y-1">
                    <!-- <i data-feather="chevron-right"></i> -->

                    <h3 class="text-lg font-semibold cursor-pointer select-none "
                        @click.stop="mc_collapsed = !mc_collapsed">
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
                            v-model="configFile.temp" min="0" max="5" step="0.1"
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
</template>

<script>
import axios from "axios";
import feather from 'feather-icons'
import { nextTick } from 'vue'
import MessageBox from "@/components/MessageBox.vue";
import YesNoDialog from "@/components/YesNoDialog.vue";
import ModelEntry from '@/components/ModelEntry.vue';
import { socket, state } from '@/services/websocket.js'
axios.defaults.baseURL = import.meta.env.VITE_GPT4ALL_API_BASEURL
export default {
    components: {
        MessageBox,
        YesNoDialog,
        ModelEntry
    },
    setup() {


        return {

        }
    },
    data() {

        return {
            // Websocket
            socket: socket,
            // Models zoo installer stuff
            models: [],
            // Accordeon stuff     
            bec_collapsed: false,
            pc_collapsed: false,
            mc_collapsed: false,
            // Settings stuff
            backendsArr: [],
            modelsArr: [],
            persLangArr: [],
            persCatgArr: [],
            persArr: [],
            langArr: [],
            configFile: {},
            showConfirmation: false

        }
    },
    created() {
        this.fetchModels();
    }, methods: {
        fetchModels() {
            axios.get('/get_available_models')
                .then(response => {
                    this.models = response.data;
                })
                .catch(error => {
                    console.log(error);
                });
        },
        // Model installation
        onInstall(model_object) {
            let isInstalled = model_object.isInstalled
            let path = model_object.path
            this.showProgress = true;
            this.progress = 0;
            console.log("installing...")

            const progressListener = (response) => {
                if (response.status === 'progress') {
                this.progress = message.progress;
                } else if (message.status === 'succeeded') {
                // Installation completed
                model_object.installing = false;
                this.showProgress = false;
                // Update the isInstalled property of the corresponding model
                const index = this.models.findIndex((model) => model.path === path);
                this.models[index].isInstalled = true;

                this.socket.off('install_progress', progressListener);
                } else if (message.status === 'failed') {
                // Installation failed or encountered an error
                model_object.installing = false;
                this.showProgress = false;
                this.socket.off('install_progress', progressListener);
                console.error('Installation failed:', message.error);
                }
            };
            this.socket.on('install_progress', progressListener);            
            this.socket.emit('install_model', { path: path });
            

        },
        onUninstall(model_object) {
            console.log("uninstalling model...")
            const progressListener = (response) => {
                if (response.status === 'progress') {
                    this.progress = message.progress;
                } else if (message.status === 'succeeded') {
                // Installation completed
                model_object.uninstalling = false;

                this.showProgress = false;
                // Update the isInstalled property of the corresponding model
                const index = this.models.findIndex((model) => model.path === path);
                this.models[index].isInstalled = false;

                this.socket.off('install_progress', progressListener);
                } else if (message.status === 'failed') {
                // Installation failed or encountered an error
                model_object.uninstalling = false;
                this.showProgress = false;
                this.socket.off('install_progress', progressListener);
                console.error('Installation failed:', message.error);
                }
            };
            this.socket.on('install_progress', progressListener);            
            this.socket.emit('uninstall_model', { path: model_object.path });
        },
        // messagebox ok stuff
        onMessageBoxOk() {
            console.log("OK button clicked");
        },
        // Refresh stuff
        refresh() {
            // No need to refresh all lists because they never change during using application. 
            // On settings change only config file chnages.
            //
            //this.api_get_req("list_backends").then(response => { this.backendsArr = response })
            //this.api_get_req("list_models").then(response => { this.modelsArr = response })
            //this.api_get_req("list_personalities_languages").then(response => { this.persLangArr = response })
            //this.api_get_req("list_personalities_categories").then(response => { this.persCatgArr = response })
            //this.api_get_req("list_personalities").then(response => { this.persArr = response })
            //this.api_get_req("list_languages").then(response => { this.langArr = response })
            this.api_get_req("get_config").then(response => { this.configFile = response })
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
                if (res) {
                    if (next !== undefined) {
                        next()
                    }
                    return res.data;
                }
            })
                .catch(error => { return { 'status': false } });
        },
        save_configuration() {
            this.showConfirmation = false
            axios.post('/save_settings', {})
                .then((res) => {
                    if (res) {
                        if (res.status)
                            this.$refs.messageBox.showMessage("Settings saved!")
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
        update_backend(value) {
            res = update_setting('backend', value)
            if (res.status) {
                console.log("Backend changed")
            }

        },
        async api_get_req(endpoint) {
            try {
                const res = await axios.get("/" + endpoint);

                if (res) {

                    return res.data

                }
            } catch (error) {
                console.log(error)
                return []
            }


        },

    }, async mounted() {
        nextTick(() => {
            feather.replace()

        })
        this.configFile = await this.api_get_req("get_config")

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
        }
    }
}
</script>

