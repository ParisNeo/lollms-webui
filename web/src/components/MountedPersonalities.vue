<template>
    <!-- LIST OF MOUNTED PERSONALITIES -->

    <div class="w-fit flex select-none">
        <div class="w-fit flex select-none">
            <div class="w-8 h-8 group relative" >
                <img :src="bUrl + mountedPers.avatar" @error="personalityImgPlacehodler"
                        class="w-8 h-8 rounded-full object-fill text-red-700 hover:scale-150 active:scale-90 hover:z-50 hover:-translate-y-2 duration-150  border-secondary cursor-pointer"
                        :title="'Active personality: '+mountedPers.name" @click="onSettingsPersonality(mountedPers)">
                <div class="opacity-0 group-hover:opacity-100">
                    <button class="-top-1 group-hover:translate-x-5 border-gray-500 absolute active:scale-90  w-7 h-7 hover:scale-150 transition bg-bg-light dark:bg-bg-dark rounded-full border-2" @click.prevent="remount_personality()" v-if="personalityHoveredIndex === index">
                        <span
                            title="Remount">
                            <!-- UNMOUNT BUTTON -->
                            <svg xmlns="http://www.w3.org/2000/svg"  class="top-0 left-1 relative w-4 h-4 text-red-600 hover:text-red-500 " viewBox="0 0 30 30" width="2" height="2" fill="none" stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round">
                                <g id="surface1">
                                <path style=" " d="M 16 4 C 10.886719 4 6.617188 7.160156 4.875 11.625 L 6.71875 12.375 C 8.175781 8.640625 11.710938 6 16 6 C 19.242188 6 22.132813 7.589844 23.9375 10 L 20 10 L 20 12 L 27 12 L 27 5 L 25 5 L 25 8.09375 C 22.808594 5.582031 19.570313 4 16 4 Z M 25.28125 19.625 C 23.824219 23.359375 20.289063 26 16 26 C 12.722656 26 9.84375 24.386719 8.03125 22 L 12 22 L 12 20 L 5 20 L 5 27 L 7 27 L 7 23.90625 C 9.1875 26.386719 12.394531 28 16 28 C 21.113281 28 25.382813 24.839844 27.125 20.375 Z "/>
                                </g>
                            </svg>

                        </span>
                    </button>

                    
                    <button class="-top-1 group-hover:-translate-x-12 border-gray-500 active:scale-90 absolute items-center  w-7 h-7 hover:scale-150 transition text-red-200 absolute active:scale-90 bg-bg-light dark:bg-bg-dark rounded-full border-2" @click.prevent="handleOnTalk()" v-if="personalityHoveredIndex === index">
                        <span
                            title="Talk">
                            <!-- UNMOUNT BUTTON -->
                            <svg xmlns="http://www.w3.org/2000/svg"  class="left-1 relative w-4 h-4 text-red-600 hover:text-red-500 " viewBox="0 0 24 24" width="2" height="2" fill="none" stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round">
                            <line x1="22" y1="2" x2="11" y2="13"></line>
                            <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
                            </svg>

                        </span>
                    </button>                    

                </div>
            </div>
        </div>
        <div class="flex -space-x-4 " v-if="mountedPersArr.length > 1">
            <div class="flex items-center justify-center w-8 h-8 cursor-pointer text-xs font-medium bg-bg-light dark:bg-bg-dark border-2 hover:border-secondary  rounded-full hover:bg-bg-light-tone dark:hover:bg-bg-dark-tone dark:border-gray-800 hover:z-50 hover:-translate-y-2 duration-150 active:scale-90"
                @click.stop="toggleShowPersList" title="Click to show more">+{{ mountedPersArr.length - 1 }}</div>
        </div>
    </div>  
    <UniversalForm ref="universalForm" class="z-50" />
</template>
<Toast ref="toast">
</Toast>
<script>
import axios from "axios";
import defaultPersonalityImgPlaceholder from "../assets/logo.svg"
import UniversalForm from '@/components/UniversalForm.vue';
import Toast from '../components/Toast.vue'

import { nextTick } from "vue";
import { useStore } from 'vuex'; // Import the useStore function
import { computed } from 'vue'; // Import the computed function
import { watch, ref } from 'vue';

import feather from 'feather-icons'
import socket from '@/services/websocket.js'

const bUrl = import.meta.env.VITE_LOLLMS_API_BASEURL
axios.defaults.baseURL = import.meta.env.VITE_LOLLMS_API_BASEURL


export default {
    name: 'MountedPersonalities',
    props: {
        onShowPersList: Function,
        onReady:Function,
    },
    components: {
        Toast,
        UniversalForm
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
        async handleOnTalk(){
            const pers = this.mountedPers
            console.log("pers:",pers)
            this.isGenerating = true;
            this.setDiscussionLoading(this.currentDiscussion.id, this.isGenerating);
            let res = await axios.get('/get_generation_status', {})
            if (res) {
                //console.log(res.data.status);
                if (!res.data.status) {
                    const id = this.$store.state.config.personalities.findIndex(item => item === pers.full_path)
                    const obj = {
                    client_id:this.$store.state.client_id,
                    id: id
                    }
                    res = await axios.post('/select_personality', obj);

                    console.log('Generating message from ',res.data.status);
                    socket.emit('generate_msg_from', { id: -1 });
                }
                else {
                    console.log("Already generating");
                }
            }
        },
        async remount_personality() {
            const pers = this.mountedPers
            console.log("Remounting personality ", pers)
            if (!pers) { return { 'status': false, 'error': 'no personality - mount_personality' } }
            try {
                console.log("before")
                const obj = {
                    client_id: this.$store.state.client_id,
                    category: pers.category,
                    folder: pers.folder,
                    language: pers.language
                }
                console.log("after")
                const res = await axios.post('/remount_personality', obj);
                console.log("Remounting personality executed:",res)
                

                if (res) {
                    console.log("Remounting personality res")
                    this.$store.state.toast.showToast("Personality remounted", 4, true)

                    return res.data

                }
                else{
                    console.log("failed remount_personality")
                }
            } catch (error) {
                console.log(error.message, 'remount_personality - settings')
                return
            }

        },            
        onSettingsPersonality(persEntry) {
            try {

                axios.get('/get_active_personality_settings').then(res => {

                    if (res) {

                        console.log('pers sett', res)
                        if (res.data && Object.keys(res.data).length > 0) {

                            this.$refs.universalForm.showForm(res.data, "Personality settings - " + persEntry.name, "Save changes", "Cancel").then(res => {

                                // send new data
                                try {
                                    axios.post('/set_active_personality_settings',
                                        res).then(response => {

                                            if (response && response.data) {
                                                console.log('personality set with new settings', response.data)
                                                this.$refs.toast.showToast("Personality settings updated successfully!", 4, true)

                                            } else {
                                                this.$refs.toast.showToast("Did not get Personality settings responses.\n" + response, 4, false)

                                            }


                                        })
                                } catch (error) {
                                    this.$refs.toast.showToast("Did not get Personality settings responses.\n Endpoint error: " + error.message, 4, false)

                                }

                            })
                        } else {
                            this.$refs.toast.showToast("Personality has no settings", 4, false)

                        }

                    }
                })

            } catch (error) {

                this.$refs.toast.showToast("Could not open personality settings. Endpoint error: " + error.message, 4, false)
            }

        },        
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

