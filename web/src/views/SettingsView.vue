<template>
    <div class="overflow-y-scroll flex flex-col no-scrollbar shadow-lg  w-full bg-bg-light-tone dark:bg-bg-dark-tone ">
        <div class="flex flex-row justify-start">
            <div class="overflow-y-scroll flex-col no-scrollbar shadow-lg bg-bg-light-tone dark:bg-bg-dark-tone ">
                <button title="Save configuration" class="text-2xl hover:text-secondary duration-75 active:scale-90 mr-2" @click="save_configuration()">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M5 3H19C20.1046 3 21 3.89543 21 5V19C21 20.1046 20.1046 21 19 21H5C3.89543 21 3 20.1046 3 19V5C3 3.89543 3.89543 3 5 3Z"></path>
                    <path d="M17 8L12 13L7 8"></path>
                </svg>
                </button>
            </div>
            <div class="overflow-y-scroll flex-col no-scrollbar shadow-lg bg-bg-light-tone dark:bg-bg-dark-tone ">
                <button title="Reset configuration" class="text-2xl hover:text-secondary duration-75 active:scale-90 mr-2" @click="reset_configuration()">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                </svg>
                </button>
            </div>
        </div>

        <div class="flex flex-row">
            <button @click="bec_collapsed = !bec_collapsed">
                <svg class="h-6 w-6 hover:text-secondary duration-75 active:scale-90" :class="{'rotate-90': !bec_collapsed}" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path d="M9 19l7-7-7-7" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
                </svg>
            </button>
            <h3 class="text-lg font-semibold">Backend Configuration</h3>
        </div>
        <div :class="{'hidden': bec_collapsed}">
            <div class="m-2">
                <label for="backend" class="block mb-2 text-sm font-medium text-gray-900 dark:text-white">
                    Backend:
                </label>
                <select id="backend" @change="update_backend($event.target.value)"
                    class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500">

                    <option v-for="item in backendsArr">{{ item }}</option>

                </select>
            </div>
            <div class="m-2">
                <label for="model" class="block mb-2 text-sm font-medium text-gray-900 dark:text-white">
                    Model:
                </label>
                <select id="model"
                    class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500">

                    <option v-for="item in modelsArr">{{ item }}</option>

                </select>
            </div>
        </div>
        <div class="flex flex-row">
            <button @click="pc_collapsed = !pc_collapsed">
                <svg class="h-6 w-6 hover:text-secondary duration-75 active:scale-90" :class="{'rotate-90': !pc_collapsed}" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path d="M9 19l7-7-7-7" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
                </svg>
            </button>
            <h3 class="text-lg font-semibold">Personality Configuration</h3>
        </div>

        <div :class="{'hidden': pc_collapsed}">
            <div class="m-2">
                <label for="persLang" class="block mb-2 text-sm font-medium text-gray-900 dark:text-white">
                    Personalities Languages:
                </label>
                <select id="persLang" @change="update_setting('personality_language', $event.target.value, refresh)"
                    class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500">

                    <option v-for="item in persLangArr">{{ item }}</option>

                </select>
            </div>
            <div class="m-2">
                <label for="persCat" class="block mb-2 text-sm font-medium text-gray-900 dark:text-white">
                    Personalities Category:
                </label>
                <select id="persCat" @change="update_setting('personality_category', $event.target.value, refresh)"
                    class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500">

                    <option v-for="item in persCatgArr">{{ item }}</option>

                </select>
            </div>
            <div class="m-2">
                <label for="persona" class="block mb-2 text-sm font-medium text-gray-900 dark:text-white">
                    Personality:
                </label>
                <select id="persona" @change="update_setting('personality', $event.target.value, refresh)"
                    class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500">

                    <option v-for="item in persArr">{{ item }}</option>

                </select>
            </div>                

        </div>
        <div class="flex flex-row">
            <button @click="mc_collapsed = !mc_collapsed">
                <svg class="h-6 w-6 hover:text-secondary duration-75 active:scale-90" :class="{'rotate-90': !mc_collapsed}" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path d="M9 19l7-7-7-7" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
                </svg>
            </button>
            <h3 class="text-lg font-semibold">Model Configuration</h3>
        </div>

        <div :class="{'hidden': mc_collapsed}">
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

                            <input type="text" id="temp-val" v-model="configFile.temp"
                                class="mt-2 w-16 text-right p-2 border border-gray-300 rounded-lg bg-gray-50 sm:text-xs focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500">
                        </p>

                    </div>

                    <input id="temperature" @change="update_setting('temperature', $event.target.value)" type="range" v-model="configFile.temp" min="0" max="5" step="0.1"
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

                    <input id="predict" @change="update_setting('n_predict', $event.target.value)" type="range" v-model="configFile.n_predict" min="0" max="2048" step="32"
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

                            <input type="text" id="top_k-val"  v-model="configFile.top_k"
                                class="mt-2 w-16 text-right p-2 border border-gray-300 rounded-lg bg-gray-50 sm:text-xs focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500">
                        </p>

                    </div>

                    <input id="top_k" @change="update_setting('top_k', $event.target.value)" type="range" v-model="configFile.top_k" min="0" max="100" step="1"
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

                            <input type="text" id="top_p-val"  v-model="configFile.top_p"
                                class="mt-2 w-16 text-right p-2 border border-gray-300 rounded-lg bg-gray-50 sm:text-xs focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500">
                        </p>

                    </div>

                    <input id="top_p" @change="update_setting('top_p', $event.target.value)" type="range" v-model="configFile.top_p" min="0" max="1" step="0.01"
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

                    <input id="repeat_penalty" @change="update_setting('repeat_penalty', $event.target.value)" type="range" v-model="configFile.repeat_penalty" min="0" max="2" step="0.01"
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

                    <input id="repeat_last_n" @change="update_setting('repeat_last_n', $event.target.value)" type="range" v-model="configFile.repeat_last_n" min="0" max="100" step="1"
                        class="flex-none h-2 mt-14 mb-2 w-full bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700  focus:ring-blue-500 focus:border-blue-500  dark:border-gray-600 dark:placeholder-gray-400  dark:focus:ring-blue-500 dark:focus:border-blue-500">
                </div>
            </div>        
        </div>
    </div>
    
    <YesNoDialog ref="yesNoDialog" />
    <MessageBox ref="messageBox" />
   
</template>

<script>
import axios from "axios";
import MessageBox from "@/components/MessageBox.vue";
import YesNoDialog from "@/components/YesNoDialog.vue";
axios.defaults.baseURL = import.meta.env.VITE_GPT4ALL_API_BASEURL
export default {
    components: {
        MessageBox,
        YesNoDialog
    },    
    setup() {


        return {

        }
    },
    data() {

        return {
            // Accordeon stuff     
            bec_collapsed: true,
            pc_collapsed: true,
            mc_collapsed: true,
            // Settings stuff
            backendsArr: [],
            modelsArr: [],
            persLangArr: [],
            persCatgArr: [],
            persArr: [],
            langArr: [],
            configFile: {},

        }
    }, methods: {
        // messagebox ok stuff
        onMessageBoxOk() {
            console.log("OK button clicked");
        },
        // Refresh stuff
        refresh(){
            this.api_get_req("list_backends").then(response=>{this.backendsArr = response})
            this.api_get_req("list_models").then(response=>{this.modelsArr = response})
            this.api_get_req("list_personalities_languages").then(response=>{this.persLangArr = response})
            this.api_get_req("list_personalities_categories").then(response=>{this.persCatgArr = response})
            this.api_get_req("list_personalities").then(response=>{this.persArr = response})
            this.api_get_req("list_languages").then(response=>{this.langArr = response})
            this.api_get_req("get_config").then(response=>{this.configFile = response})
        },
        // Accordeon stuff
        toggleAccordion() {
            this.showAccordion = !this.showAccordion;
        },
        update_setting(setting_name, setting_value, next=undefined){
            axios.post('/update_setting', {'setting_name':setting_name, 'setting_value':setting_value})
            .then((res) => {
                if (res) {
                    if(next!==undefined){
                        next()
                    }
                    return res.data;
                }
            })
            .catch(error=>{return {'status':false}});
        },
        save_configuration(){
            axios.post('/save_settings', {})
            .then((res) => {
                if (res) {
                    if(res.status)
                        this.$refs.messageBox.showMessage("Settings saved")
                    else
                        this.$refs.messageBox.showMessage("Couldn't save settings!")
                    return res.data;
                }
            })
            .catch(error=>{
                console.log(error)
                this.$refs.messageBox.showMessage("Couldn't save settings!")
                return {'status':false}
            });

        },
        reset_configuration(){
            this.$refs.yesNoDialog.askQuestion("Are you sure?<br>This will delete all your configurations and get back to default configuration.").then(response=>{
            if (response) {
                // User clicked Yes
                axios.post('/reset_settings', {})
                .then((res) => {
                    if (res) {
                        if(res.status)
                            this.$refs.messageBox.showMessage("Settings have been reset correctly")
                        else
                            this.$refs.messageBox.showMessage("Couldn't reset settings!")
                        return res.data;
                    }
                })
                .catch(error=>{
                    console.log(error)
                    this.$refs.messageBox.showMessage("Couldn't reset settings!")
                    return {'status':false}
                });            
            // Perform delete operation
            } else {
                // User clicked No
                // Do nothing
            }
        });
        },
        update_backend(value){
            res = update_setting('backend', value)
            if(res.status){
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
        this.backendsArr = await this.api_get_req("list_backends")
        this.modelsArr = await this.api_get_req("list_models")
        this.persLangArr = await this.api_get_req("list_personalities_languages")
        this.persCatgArr = await this.api_get_req("list_personalities_categories")
        this.persArr = await this.api_get_req("list_personalities")
        this.langArr = await this.api_get_req("list_languages")
        this.configFile = await this.api_get_req("get_config")
    }
}
</script>
<style>
.settings {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: 50px;
}

.section {
  margin-top: 20px;
}

h2 {
  font-size: 1.2rem;
  margin-bottom: 10px;
}

label {
  margin-right: 10px;
}

select {
  margin-right: 10px;
}

input[type="text"],
input[type="email"],
input[type="file"] {
  margin-right: 10px;
}
</style>
