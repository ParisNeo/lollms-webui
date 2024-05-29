<template>
    <!-- LIST OF MOUNTED PERSONALITIES -->
    <div
        class="text-left overflow-visible text-base font-semibold cursor-pointer select-none items-center flex flex-col flex-grow w-full overflow-x-auto scrollbar-thin scrollbar-track-bg-light scrollbar-thumb-bg-light-tone hover:scrollbar-thumb-primary dark:scrollbar-track-bg-dark dark:scrollbar-thumb-bg-dark-tone dark:hover:scrollbar-thumb-primary active:scrollbar-thumb-secondary">
        <!-- LIST -->
        <!-- SPINNER -->
        <div v-if="isLoading" role="status" class="flex justify-center overflow-y-hidden ">
            <svg aria-hidden="true" class="w-6 h-6   animate-spin  fill-secondary" viewBox="0 0 100 101" fill="none"
                xmlns="http://www.w3.org/2000/svg">
                <path
                    d="M100 50.5908C100 78.2051 77.6142 100.591 50 100.591C22.3858 100.591 0 78.2051 0 50.5908C0 22.9766 22.3858 0.59082 50 0.59082C77.6142 0.59082 100 22.9766 100 50.5908ZM9.08144 50.5908C9.08144 73.1895 27.4013 91.5094 50 91.5094C72.5987 91.5094 90.9186 73.1895 90.9186 50.5908C90.9186 27.9921 72.5987 9.67226 50 9.67226C27.4013 9.67226 9.08144 27.9921 9.08144 50.5908Z"
                    fill="currentColor" />
                <path
                    d="M93.9676 39.0409C96.393 38.4038 97.8624 35.9116 97.0079 33.5539C95.2932 28.8227 92.871 24.3692 89.8167 20.348C85.8452 15.1192 80.8826 10.7238 75.2124 7.41289C69.5422 4.10194 63.2754 1.94025 56.7698 1.05124C51.7666 0.367541 46.6976 0.446843 41.7345 1.27873C39.2613 1.69328 37.813 4.19778 38.4501 6.62326C39.0873 9.04874 41.5694 10.4717 44.0505 10.1071C47.8511 9.54855 51.7191 9.52689 55.5402 10.0491C60.8642 10.7766 65.9928 12.5457 70.6331 15.2552C75.2735 17.9648 79.3347 21.5619 82.5849 25.841C84.9175 28.9121 86.7997 32.2913 88.1811 35.8758C89.083 38.2158 91.5421 39.6781 93.9676 39.0409Z"
                    fill="currentFill" />
            </svg>
            <span class="sr-only">Loading...</span>
        </div>
        <div>



            <div v-if="mountedPersArr.length > 0" :class="isLoading?'pointer-events-none opacity-30 cursor-default':''">

                <!-- EXPAND / COLLAPSE BUTTON -->

                <button
                    class="mt-0 w-full text-2xl hover:text-secondary duration-75 flex justify-center  hover:bg-bg-light-tone hover:dark:bg-bg-dark-tone rounded-lg "
                    title="Close personality list" type="button" @click.stop="toggleShowPersList">

                    <i data-feather="chevron-down"></i>
                </button>
                <label class="block my-2 text-sm font-medium text-gray-900 dark:text-white">
                    Mounted Personalities: ({{ mountedPersArr.length }})
                </label>
                <div class="overflow-y-auto no-scrollbar pb-0 grid lg:grid-cols-3 md:grid-cols-2 gap-4 max-h-96">
                    <TransitionGroup name="bounce">
                        <personality-entry ref="personalitiesZoo" v-for="(pers, index) in this.$store.state.mountedPersArr"
                            :key="'index-' + index + '-' + pers.name" :personality="pers" :full_path="pers.full_path"
                            :select_language="false"
                            :selected="configFile.personalities[configFile.active_personality_id] === pers.full_path  || configFile.personalities[configFile.active_personality_id] === pers.full_path+':'+pers.language"
                            :on-selected="onPersonalitySelected" 
                            :on-mount="onPersonalityMounted" 
                            :on-edit="editPersonality"
                            :on-un-mount="onPersonalityUnMounted"  
                            :on-remount="onPersonalityRemount"
                            :on-settings="onSettingsPersonality"  
                            :on-reinstall="onPersonalityReinstall"
                            :on-talk="handleOnTalk"
                            :on-open-folder="handleOpenFolder"
                           />
                    </TransitionGroup>
                </div>
            </div>

        </div>

        <Toast ref="toast">
        </Toast>
        <UniversalForm ref="universalForm" class="z-20" />
    </div>
</template>
<style scoped>
.bounce-enter-active {
    animation: bounce-in 0.5s;
}

.bounce-leave-active {
    animation: bounce-in 0.5s reverse;
}

@keyframes bounce-in {
    0% {
        transform: scale(0);
    }

    50% {
        transform: scale(1.25);
    }

    100% {
        transform: scale(1);
    }
}
</style>
<script >
import defaultPersonalityImgPlaceholder from "../assets/logo.svg"
import PersonalityEntry from './PersonalityEntry.vue'
import Toast from './Toast.vue'
import UniversalForm from './UniversalForm.vue';
import feather from 'feather-icons'
import {logObjectProperties} from "../main.js"

import axios from "axios";
import { nextTick } from "vue";
import markdownItAttrs from "markdown-it-attrs";

const bUrl = import.meta.env.VITE_LOLLMS_API_BASEURL
axios.defaults.baseURL = import.meta.env.VITE_LOLLMS_API_BASEURL
export default {
    props: {
        onTalk:Function,
        onMounted: Function,
        onUnmounted: Function,
        onRemounted: Function,
        discussionPersonalities: Array,
        onShowPersList: Function,

    },
    components: {
        PersonalityEntry,
        Toast,
        UniversalForm,
    },
    name: 'MountedPersonalitiesList',
    data() {


        return {

            posts_headers : {
                'accept': 'application/json',
                'Content-Type': 'application/json'
            },            
            bUrl: bUrl,
            isMounted: false,
            isLoading: false
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
        },
    },
    methods: {
        toggleShowPersList() {
            //this.show = !this.show
            this.onShowPersList()
        },
        async constructor() {
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
        
        onPersonalityReinstall(persItem){
            console.log('on reinstall ', persItem)
            this.isLoading = true
            axios.post('/reinstall_personality', { name: persItem.personality.full_path }).then((res) => {

                if (res) {
                    this.isLoading = false
                    console.log('reinstall_personality', res)
                    if (res.data.status) {
                        this.$refs.toast.showToast("Personality reinstalled successfully!", 4, true)
                    } else {
                        this.$refs.toast.showToast("Could not reinstall personality", 4, false)
                    }
                    return res.data;
                }
                this.isLoading = false
            })
                // eslint-disable-next-line no-unused-vars

                .catch(error => {
                    this.isLoading = false
                    this.$refs.toast.showToast("Could not reinstall personality\n" + error.message, 4, false)
                    return { 'status': false }
                });
        },
        editPersonality(pers) {
            pers=pers.personality;
            // Make a POST request to the '/get_personality_config' endpoint using Axios
            axios.post('/get_personality_config', {
                client_id:this.$store.state.client_id,
                category: pers.category,
                name: pers.folder,
            })
            .then(response => {
            const data = response.data;
            console.log("Done")
            if (data.status) {
                // Update the currentPersonConfig with the received data
                this.$store.state.currentPersonConfig = data.config;
                this.$store.state.showPersonalityEditor = true;
                this.$store.state.personality_editor.showPanel()
                this.$store.state.selectedPersonality = pers
            } else {
                // Handle the error
                console.error(data.error);
            }
            })
            .catch(error => {
            // Handle the error
            console.error(error);
            });
        },   
        onPersonalityMounted(persItem) {
            //persItem.ismounted = true
            this.mountPersonality(persItem)
        },
        onPersonalityUnMounted(persItem) {
            this.unmountPersonality(persItem)
        },
        onPersonalityRemount(persItem){
            this.reMountPersonality(persItem)
        },
        async handleOpenFolder(pers){
            const data = {
                                    client_id:this.$store.state.client_id, 
                                    personality_folder: pers.personality.folder
                                }
            console.log(data)                    
            await axios.post("/open_personality_folder",
                                data
                            )
        },
        async handleOnTalk(pers){
            // eslint-disable-next-line no-unused-vars
            feather.replace()
            console.log('ppa', pers)
            if (pers) {
                if (pers.isMounted) {
                    const res = await this.select_personality(pers)
                    if (res) {
                        if (res.status) {
                            await this.constructor()
                            this.$refs.toast.showToast("Selected personality:\n" + pers.name, 4, true)
                        }
                    }
                } else {
                    this.onPersonalityMounted(pers)
                }
                this.onTalk(pers)
            }

        },
        async onPersonalitySelected(pers) {
            // eslint-disable-next-line no-unused-vars
            feather.replace()
            console.log('Selected personality : ', JSON.stringify(pers.personality))
            if (pers) {
                if (pers.selected) {
                    this.$refs.toast.showToast("Personality already selected", 4, true)
                    return
                }
                if (pers.isMounted) {
                    const res = await this.select_personality(pers)
                    if (res) {
                        if (res.status) {
                            await this.constructor()
                            this.$refs.toast.showToast("Selected personality:\n" + pers.name, 4, true)

                        }
                    }


                } else {
                    this.onPersonalityMounted(pers)

                }
            }

        },
        onSettingsPersonality(persEntry) {
            try {

                axios.get('/get_active_personality_settings').then(res => {

                    if (res) {

                        console.log('pers sett', res)
                        if (res.data && Object.keys(res.data).length > 0) {

                            this.$refs.universalForm.showForm(res.data, "Personality settings - " + persEntry.personality.name, "Save changes", "Cancel").then(res => {

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
        async mount_personality(pers) {
            if (!pers) { return { 'status': false, 'error': 'no personality - mount_personality' } }

            try {
                const obj = {
                    category: pers.category,
                    folder: pers.folder,
                    language: pers.language
                }
                const res = await axios.post('/mount_personality', obj);

                if (res) {

                    return res.data

                }
            } catch (error) {
                console.log(error.message, 'mount_personality - settings')
                return
            }

        },
        async remount_personality(pers) {
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
        async unmount_personality(pers) {
            if (!pers) { return { 'status': false, 'error': 'no personality - unmount_personality' } }
            const obj = {
                client_id: this.$store.state.client_id,
                language: pers.language,
                category: pers.category,
                folder: pers.folder
            }


            try {
                const res = await axios.post('/unmount_personality', obj, {headers: this.posts_headers});


                if (res) {

                    return res.data
                }
            } catch (error) {
                console.log(error.message, 'unmount_personality - settings')
                return
            }

        },
        async select_personality(pers) {
            if (!pers || !pers.personality) { return { 'status': false, 'error': 'no personality - select_personality' } }
            let id = -1
            console.log("Personality full path : ",pers.full_path)
            console.log("Personality language : ",pers.personality.language)

            if(pers.personality.language!=null && pers.personality.language!=undefined){
                console.log('Mounting a localized version of personality')
                console.log('Mounted personalities :', JSON.stringify(this.configFile.personalities))
                console.log("Personality to select: ",pers.full_path+':'+pers.personality.language)
                id = this.configFile.personalities.findIndex(item => item === pers.full_path+':'+pers.personality.language)
            }
            else{
                console.log('Mounted personalities :', JSON.stringify(this.configFile.personalities))
                id = this.configFile.personalities.findIndex(item => item === pers.full_path)
            }
            if(id>-1){
                console.log('Selecting personality with id:', JSON.stringify(id))
                const obj = {
                    client_id:this.$store.state.client_id,
                    id: id
                }
                try {
                    const res = await axios.post('/select_personality', obj);

                    if (res) {
                        this.$store.dispatch('refreshConfig').then(() => {
                            console.log("recovered config", this.configFile.active_personality_id);
                            this.$store.dispatch('refreshPersonalitiesZoo').then(() => {
                            this.$store.dispatch('refreshMountedPersonalities');
                            });
                        });

                        return res.data

                    }
                } catch (error) {
                    console.log(error, 'select_personality - settings')
                    return
                }

            }
            else{
                console.log('Personality id is wrong')
                this.$refs.toast.showToast("Personality id is wrong!", 4, false)
                return { 'status': false, 'error': 'Personality id is wrong' }
            }
        },
        async mountPersonality(pers) {

            console.log('mount pers', pers)
            if (!pers) { return }

            if (this.configFile.personalities.includes(pers.personality.full_path)) {
                this.$refs.toast.showToast("Personality already mounted", 4, false)
                return
            }

            const res = await this.mount_personality(pers.personality)
            console.log('mount_personality res', res)

            if (res.status) {
                this.configFile.personalities = res.personalities
                this.$refs.toast.showToast("Personality mounted", 4, true)
                pers.isMounted = true
                this.onMounted(this);
                const res2 = await this.select_personality(pers.personality)
                if (res2.status) {
                    this.$refs.toast.showToast("Selected personality:\n" + pers.personality.name, 4, true)

                }
                this.getMountedPersonalities()
            } else {
                pers.isMounted = false
                this.$refs.toast.showToast("Could not mount personality\nError: " + res.error, 4, false)
            }


        },
        async reMountPersonality(pers) {

            console.log('remount pers', pers)
            if (!pers) { return }

            if (!this.configFile.personalities.includes(pers.personality.full_path)) {
                this.$refs.toast.showToast("Personality not mounted", 4, false)
                return
            }

            const res = await this.remount_personality(pers.personality)
            console.log('remount_personality res', res)

            if (res.status) {
                this.configFile.personalities = res.personalities
                this.$refs.toast.showToast("Personality remounted", 4, true)
                pers.isMounted = true
                this.onMounted(this);
                const res2 = await this.select_personality(pers.personality)
                if (res2.status) {
                    this.$refs.toast.showToast("Selected personality:\n" + pers.personality.name, 4, true)

                }
                this.getMountedPersonalities()
            } else {
                pers.isMounted = false
                this.$refs.toast.showToast("Could not mount personality\nError: " + res.error, 4, false)
            }


        },
        async unmountPersonality(pers) {

            if (!pers) { return }
            console.log(`Unmounting ${JSON.stringify(pers.personality)}`)
            const res = await this.unmount_personality(pers.personality)


            if (res.status) {
                
                console.log('unmount response', res)
                this.configFile.active_personality_id = res.active_personality_id
                this.configFile.personalities = res.personalities

                const activePersPath = this.configFile.personalities[this.configFile.active_personality_id]

                const persId = this.personalities.findIndex(item => item.full_path == activePersPath)
                //const persFilteredId = this.personalitiesFiltered.findIndex(item => item.full_path == pers.full_path)
                const persIdZoo = this.$refs.personalitiesZoo.findIndex(item => item.full_path == pers.full_path)
                const activePers = this.personalities[persId]
                activePers.isMounted = false
                activePers.selected = true
                this.$refs.personalitiesZoo[persIdZoo].isMounted = false

                

                //pers.isMounted = false
                this.getMountedPersonalities()
                // Select some other personality
                //const lastPers = this.mountedPersArr[this.mountedPersArr.length - 1]

                //console.log(lastPers, this.mountedPersArr.length)
                // const res2 = await this.select_personality(lastPers.personality)
                const res2 = await this.select_personality(activePers)
                if (res2.status) {
                    feather.replace()
                }
                this.$refs.toast.showToast("Personality unmounted", 4, true)
                this.onUnMounted(this);

            } else {
                this.$refs.toast.showToast("Could not unmount personality\nError: " + res.error, 4, false)
            }


        },
        getMountedPersonalities() {
            this.isLoading = true
            let mountedPersArr = []
            console.log(this.configFile.personalities.length)
            // console.log('perrs listo',this.personalities)
            for (let i = 0; i < this.configFile.personalities.length; i++) {
                const full_path_item = this.configFile.personalities[i]
                const index = this.personalities.findIndex(item => item.full_path == full_path_item)

                const pers = this.personalities[index]
                if (pers) {
                    console.log('adding from config')
                    mountedPersArr.push(pers)
                }
                else {
                    console.log('adding default')
                    const index = this.personalities.findIndex(item2 => item2.full_path == "english/generic/lollms")

                    const pers = this.personalities[index]
                    mountedPersArr.push(pers)
                }
            }
            this.mountedPersArr = []
            this.mountedPersArr = mountedPersArr
            //this.mountedPersArr = mountedPersArr
            console.log('discussionPersonalities', this.discussionPersonalities)
            if (this.discussionPersonalities!=undefined){
                if (this.discussionPersonalities.length > 0) {
                    for (let i = 0; i < this.discussionPersonalities.length; i++) {
                        const per = this.discussionPersonalities[i]
                        console.log('discussionPersonalities - per', per)
                        const perIndex = this.mountedPersArr.findIndex((item) => item.full_path == per)
                        console.log('discussionPersonalities -includes', perIndex)
                        console.log('discussionPersonalities -mounted list', this.mountedPersArr)

                        if (perIndex == -1) {

                            const index2 = this.personalities.findIndex(item2 => item2.full_path == per)
                            // const index22 = this.personalities.filter(item2 => item2.full_path.localeCompare(per) ==1 ) 

                            const pers = this.personalities[index2]
                            console.log('adding discucc121', pers, per)
                            if (pers) {
                                this.mountedPersArr.push(pers)
                                console.log('adding discucc', pers)
                            }

                        }

                    }

                }
            } 


            this.isLoading = false
            console.log('getMountedPersonalities', this.mountedPersArr)
            console.log('fig', this.configFile)

        },
    }
}
</script>

