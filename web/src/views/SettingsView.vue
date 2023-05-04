<template>
    <div
        class="overflow-y-scroll flex flex-col no-scrollbar shadow-lg min-w-[29rem] max-w-[29rem] bg-bg-light-tone dark:bg-bg-dark-tone ">
        <div class="p-2">
            <div class="m-2">
                <label for="backend" class="block mb-2 text-sm font-medium text-gray-900 dark:text-white">
                    Backend:
                </label>
                <select id="backend"
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
            <div class="m-2">
                <label for="persLang" class="block mb-2 text-sm font-medium text-gray-900 dark:text-white">
                    Personalities Languages:
                </label>
                <select id="persLang"
                    class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500">

                    <option v-for="item in persLangArr">{{ item }}</option>

                </select>
            </div>
            <div class="m-2">
                <label for="persCat" class="block mb-2 text-sm font-medium text-gray-900 dark:text-white">
                    Personalities Category:
                </label>
                <select id="persCat"
                    class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500">

                    <option v-for="item in persCatgArr">{{ item }}</option>

                </select>
            </div>
            <div class="m-2">
                <label for="persona" class="block mb-2 text-sm font-medium text-gray-900 dark:text-white">
                    Persona:
                </label>
                <select id="persona"
                    class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500">

                    <option v-for="item in persArr">{{ item }}</option>

                </select>
            </div>
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

                    <input id="temperature" type="range" v-model="configFile.temp" min="0" max="5" step="0.1"
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

                    <input id="predict" type="range" v-model="configFile.n_predict" min="0" max="2048" step="32"
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

                    <input id="top_k" type="range" v-model="configFile.top_k" min="0" max="100" step="1"
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

                    <input id="top_p" type="range" v-model="configFile.top_p" min="0" max="1" step="0.01"
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

                    <input id="repeat_penalty" type="range" v-model="configFile.repeat_penalty" min="0" max="2" step="0.01"
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

                    <input id="repeat_last_n" type="range" v-model="configFile.repeat_last_n" min="0" max="100" step="1"
                        class="flex-none h-2 mt-14 mb-2 w-full bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700  focus:ring-blue-500 focus:border-blue-500  dark:border-gray-600 dark:placeholder-gray-400  dark:focus:ring-blue-500 dark:focus:border-blue-500">
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import axios from "axios";
export default {
    setup() {


        return {

        }
    },
    data() {

        return {
            backendsArr: [],
            modelsArr: [],
            persLangArr: [],
            persCatgArr: [],
            persArr: [],
            langArr: [],
            configFile: {},

        }
    }, methods: {
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

