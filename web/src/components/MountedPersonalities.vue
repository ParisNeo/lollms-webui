<template>
    <div class="relative group/item">
      <button @click.prevent="onSettingsPersonality" class="w-6 h-6 rounded-full overflow-hidden transition-transform duration-200 transform group-hover/item:scale-110 focus:outline-none">
        <img :src="mountedPers.avatar" @error="personalityImgPlacehodler" :alt="mountedPers.name" class="w-full h-full object-cover" :class="{'border-2 border-secondary': isActive}">
      </button>
      
      <div class="absolute bottom-6 left-0 w-full flex items-center justify-center opacity-0 group-hover/item:opacity-100 transition-opacity duration-200 p-1">
        <button @click.prevent="remount_personality()" class="p-1 bg-blue-500 rounded-full text-white hover:bg-blue-600 focus:outline-none" title="Remount">
          <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path></svg>
        </button>
        <button @click.prevent="handleOnTalk()" class="p-1 bg-green-500 rounded-full text-white hover:bg-green-600 focus:outline-none ml-1" title="Talk">
          <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"></path></svg>
        </button>
        <button class="p-1 bg-gray-500 rounded-full text-white hover:bg-gray-600 focus:outline-none ml-1" title="Show more">
          <span class="text-xs font-bold">+{{ mountedPersArr.length - 1 }}</span>
        </button>
      </div>
    </div>
    <UniversalForm ref="universalForm" class="z-50" />
  </template>
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
                console.log("asked for:", this.$store.state.mountedPers)
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

