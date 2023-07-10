<template>
    <!-- LIST OF MOUNTED PERSONALITIES -->


    <div class="w-fit select-none">

        <div class="flex -space-x-4 " v-if="mountedPersArr.length > 1">
            <img :src="bUrl + mountedPers.avatar" @error="personalityImgPlacehodler"
                class="w-8 h-8 rounded-full object-fill text-red-700 border-2 active:scale-90 hover:z-20 hover:-translate-y-2 duration-150  border-secondary cursor-pointer"
                :title="'Active personality: '+mountedPers.name" >

            <div class="flex items-center justify-center w-8 h-8 cursor-pointer text-xs font-medium bg-bg-light dark:bg-bg-dark border-2 hover:border-secondary  rounded-full hover:bg-bg-light-tone dark:hover:bg-bg-dark-tone dark:border-gray-800 hover:z-20 hover:-translate-y-2 duration-150 active:scale-90"
                @click.stop="toggleShowPersList" title="Click to show more">+{{ mountedPersArr.length - 1 }}</div>
        </div>
        <div class="flex -space-x-4 " v-if="mountedPersArr.length == 1">
            <img :src="bUrl + this.$store.state.mountedPers.avatar" @error="personalityImgPlacehodler"
                class="w-8 h-8 rounded-full object-fill text-red-700 border-2 active:scale-90 hover:z-20 cursor-pointer  border-secondary"
                :title="'Active personality: '+this.$store.state.mountedPers.name" @click.stop="toggleShowPersList" >
        </div>
        <div v-if="mountedPersArr.length == 0" title="Loading personalities">
            <!-- SPINNER -->
            <div role="status">
                <svg aria-hidden="true" class="w-6 h-6   animate-spin  fill-secondary"
                    viewBox="0 0 100 101" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path
                        d="M100 50.5908C100 78.2051 77.6142 100.591 50 100.591C22.3858 100.591 0 78.2051 0 50.5908C0 22.9766 22.3858 0.59082 50 0.59082C77.6142 0.59082 100 22.9766 100 50.5908ZM9.08144 50.5908C9.08144 73.1895 27.4013 91.5094 50 91.5094C72.5987 91.5094 90.9186 73.1895 90.9186 50.5908C90.9186 27.9921 72.5987 9.67226 50 9.67226C27.4013 9.67226 9.08144 27.9921 9.08144 50.5908Z"
                        fill="currentColor" />
                    <path
                        d="M93.9676 39.0409C96.393 38.4038 97.8624 35.9116 97.0079 33.5539C95.2932 28.8227 92.871 24.3692 89.8167 20.348C85.8452 15.1192 80.8826 10.7238 75.2124 7.41289C69.5422 4.10194 63.2754 1.94025 56.7698 1.05124C51.7666 0.367541 46.6976 0.446843 41.7345 1.27873C39.2613 1.69328 37.813 4.19778 38.4501 6.62326C39.0873 9.04874 41.5694 10.4717 44.0505 10.1071C47.8511 9.54855 51.7191 9.52689 55.5402 10.0491C60.8642 10.7766 65.9928 12.5457 70.6331 15.2552C75.2735 17.9648 79.3347 21.5619 82.5849 25.841C84.9175 28.9121 86.7997 32.2913 88.1811 35.8758C89.083 38.2158 91.5421 39.6781 93.9676 39.0409Z"
                        fill="currentFill" />
                </svg>
                <span class="sr-only">Loading...</span>
            </div>
        </div>

    </div>
</template>

<script>
import axios from "axios";
import defaultPersonalityImgPlaceholder from "../assets/logo.svg"
import { nextTick } from "vue";
import { useStore } from 'vuex'; // Import the useStore function
import { computed } from 'vue'; // Import the computed function
import { watch, ref } from 'vue';

import feather from 'feather-icons'

const bUrl = import.meta.env.VITE_GPT4ALL_API_BASEURL
axios.defaults.baseURL = import.meta.env.VITE_GPT4ALL_API_BASEURL


export default {
    name: 'MountedPersonalities',
    props: {
        onShowPersList: Function,
        onReady:Function,
    },
    data() {
        return {
            bUrl: bUrl,
            isMounted: false,
            
            show: false

        }
    },
    async mounted() {
        await this.constructor()
        this.isMounted = true
    },
    async activated() {
        if (this.isMounted) {
            await this.constructor()
        }

    },
    computed:{
        configFile: {
            get() {
                return this.$store.state.config;
            },
            set(value) {
                this.$store.commit('setConfig', value);
            },
        },
        mountedPers:{
            get() {
                return this.$store.state.mountedPers;
            },
            set(value) {
                this.$store.commit('setMountedPers', value);
            }
        },        
        
        personalities:{
            get() {
                return this.$store.state.personalities;
            },
            set(value) {
                this.$store.commit('setPersonalities', value);
            }
        },
        mountedPersArr:{
            get() {
                return this.$store.state.mountedPersArr;
            },
            set(value) {
                this.$store.commit('setMountedPers', value);
            }
        }

    },
    methods: {
        toggleShowPersList() {
            //this.show = !this.show
            this.onShowPersList()
        },
        async constructor() {
            nextTick(() => {
                feather.replace()
            })            
            while (this.$store.state.ready === false) {
                await new Promise((resolve) => setTimeout(resolve, 100)); // Wait for 100ms
            }  
            this.onReady();
            /*
            if(this.configFile===null){
                console.log("No config file found.\nreloading")
                this.configFile = await this.api_get_req("get_config")
            } */          
        },
        async api_get_req(endpoint) {
            try {
                const res = await axios.get("/" + endpoint);

                if (res) {

                    return res.data

                }
            } catch (error) {
                console.log(error.message, 'api_get_req - mountedPersonalities')
                return
            }


        },
        personalityImgPlacehodler(event) {
            event.target.src = defaultPersonalityImgPlaceholder
        },
        
    }
}
</script>

