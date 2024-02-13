<template>

        <form>
            <div class="absolute bottom-0 left-0 w-fit min-w-96  w-full justify-center text-center p-4">
                <div v-if="filesList.length > 0 || showPersonalities" class="items-center gap-2 rounded-lg border bg-white p-1.5 shadow-sm hover:shadow-none dark:border-gray-800 dark:bg-gray-900  w-fit">
                    <!-- EXPAND / COLLAPSE BUTTON -->
                    <div class="flex">
                        <button 
                            class="mx-1 w-full text-2xl hover:text-secondary duration-75 flex justify-center  hover:bg-bg-light-tone hover:dark:bg-bg-dark-tone rounded-lg "
                            :title="showfilesList ? 'Hide file list' : 'Show file list'" type="button"
                            @click.stop=" showfilesList = !showfilesList">
                            <i data-feather="list"></i>
                        </button>
                    </div>                 
                    <!-- FILES     -->
                    <div v-if="filesList.length > 0 && showfilesList ==true">
                        <div class="flex flex-col max-h-64  ">
                            <TransitionGroup name="list" tag="div"
                                class="flex flex-col flex-grow overflow-y-auto scrollbar-thin scrollbar-track-bg-light scrollbar-thumb-bg-light-tone hover:scrollbar-thumb-primary dark:scrollbar-track-bg-dark dark:scrollbar-thumb-bg-dark-tone dark:hover:scrollbar-thumb-primary active:scrollbar-thumb-secondary">
                                <div v-for="(file, index) in filesList" :key="index + '-' + file.name">
                                    <div class="  m-1" :title="file.name">

                                        <div
                                            class="flex flex-row items-center gap-1 text-left p-2 text-sm font-medium items-center gap-2 rounded-lg border bg-gray-100 p-1.5 shadow-sm hover:shadow-none dark:border-gray-800 dark:bg-gray-700 hover:bg-primary dark:hover:bg-primary">
                                            <div v-if="!isFileSentList[index]" filesList role="status">
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
                                            <div>
                                                <i data-feather="file" class="w-5 h-5"></i>

                                            </div>


                                            <div class="line-clamp-1 w-3/5" :class="isFileSentList[index]?'text-green-500':'text-red-200'">
                                                {{ file.name }}
                                            </div>
                                            <div class="grow">

                                            </div>

                                            <div class="flex flex-row items-center">
                                                <p class="whitespace-nowrap">
                                                    {{ computedFileSize(file.size) }}

                                                </p>
                                                <button type="button" title="Remove item"
                                                    class="flex items-center p-0.5 text-sm rounded-sm hover:text-red-600 active:scale-75"
                                                    @click="removeItem(file)">
                                                    <i data-feather="x" class="w-5 h-5 "></i>

                                                </button>

                                            </div>


                                        </div>


                                    </div>
                                </div>
                            </TransitionGroup>

                        </div>
                    </div>
                    <div v-if="filesList.length > 0" class="flex mx-1 w-500">

                        <!-- ADDITIONAL INFO PANEL -->

                        <div class="whitespace-nowrap flex flex-row gap-2">
                            <p class="font-bold ">
                                Total size:
                            </p>

                            {{ totalSize }}

                            ({{ filesList.length }})


                        </div>
                        <div class="grow">

                        </div>
                        <button type="button" title="Clear all"
                            class="flex items-center p-0.5 text-sm rounded-sm hover:text-red-600 active:scale-75"
                            @click="clear_files">
                            <i data-feather="trash" class="w-5 h-5 "></i>
                        </button>
                        <button type="button" title="Download database"
                            class="flex items-center p-0.5 text-sm rounded-sm hover:text-red-600 active:scale-75"
                            @click="download_database">
                            <i data-feather="download-cloud" class="w-5 h-5 "></i>
                        </button>                        
                    </div>
                    <div v-if="showPersonalities" class="mx-1">
                        <MountedPersonalitiesList ref="mountedPersList" 
                            :onShowPersList="onShowPersListFun"
                            :on-mounted="onMountFun"
                            :on-un-mounted="onUnmountFun"
                            :on-remounted="onRemountFun"
                            :on-talk="handleOnTalk"
                            :discussionPersonalities="allDiscussionPersonalities" />
                    </div>
                </div>

                    <!-- CHAT BOX -->
                        <div v-if="selecting_model" title="Selecting model" class="flex flex-row flex-grow justify-end">
                            <!-- SPINNER -->
                            <div role="status">
                                <img :src="loader_v0" class="w-50 h-50">
                                <span class="sr-only">Selecting model...</span>
                            </div>
                        </div>
                        <div class="flex w-fit pb-3 relative grow   w-full">
                            <div class="relative grow flex h-15 cursor-pointer select-none items-center gap-2 rounded-lg border bg-white p-1.5 shadow-sm hover:shadow-none dark:border-gray-800 dark:bg-gray-900" tabindex="0">
                                <div v-if="loading" title="Waiting for reply">
                                    <img :src="loader_v0">
                                    <!-- SPINNER -->
                                    <div role="status">
                                        <span class="sr-only">Loading...</span>
                                    </div>
                                </div>
                                <div class="w-fit group relative" v-if="!loading" >
                                    <!-- :onShowPersList="onShowPersListFun" -->
                                    <div class= "group w-full inline-flex absolute opacity-0 group-hover:opacity-100 transform group-hover:-translate-y-10 group-hover:translate-x-15 transition-all duration-300">
                                        <div class="w-full"
                                            v-for="(item, index) in installedModels" :key="index + '-' + item.name"
                                            ref="installedModels">
                                            <div v-if="item.name!=model_name" class="group items-center flex flex-row">
                                                <button @click.prevent="setModel(item)" class="w-8 h-8">
                                                    <img :src="item.icon?item.icon:modelImgPlaceholder"
                                                        class="w-8 h-8 rounded-full object-fill text-red-700 border-2 active:scale-90 hover:border-secondary "
                                                        :title="item.name">
                                                </button>
                                            </div>
                                        </div>             
                                    </div>
                                    <div class="group items-center flex flex-row">
                                        <button @click.prevent="showModelConfig()" class="w-8 h-8">
                                            <img :src="currentModel.icon?currentModel.icon:modelImgPlaceholder"
                                                class="w-8 h-8 rounded-full object-fill text-red-700 border-2 active:scale-90 hover:border-secondary "
                                                :title="currentModel?currentModel.name:'unknown'">
                                        </button>
                                    </div>

                                </div>    
                                <div class="w-fit group relative" >
                                    <!-- :onShowPersList="onShowPersListFun" -->
                                    <div class= "group w-full inline-flex absolute opacity-0 group-hover:opacity-100 transform group-hover:-translate-y-10 group-hover:translate-x-15 transition-all duration-300">
                                        <div class="w-full"
                                            v-for="(item, index) in this.$store.state.mountedPersArr" :key="index + '-' + item.name"
                                            ref="mountedPersonalities">
                                            <div v-if="index!=this.$store.state.config.active_personality_id" class="group items-center flex flex-row">
                                                <button @click.prevent="onPersonalitySelected(item)" class="w-8 h-8">
                                                    <img :src="bUrl + item.avatar" @error="personalityImgPlacehodler"
                                                        class="w-8 h-8 rounded-full object-fill text-red-700 border-2 active:scale-90 hover:border-secondary "
                                                        :class="this.$store.state.active_personality_id == this.$store.state.personalities.indexOf(item.full_path) ? 'border-secondary' : 'border-transparent z-0'"
                                                        :title="item.name">
                                                </button>
                                                <button @click.prevent="unmountPersonality (item)">
                                                    <span
                                                        class="hidden hover:block top-3 left-9 absolute active:scale-90 bg-bg-light dark:bg-bg-dark rounded-full border-2  border-transparent"
                                                        title="Unmount personality">
                                                        <svg aria-hidden="true" class="w-4 h-4 text-red-600 hover:text-red-500 "
                                                            fill="currentColor" viewBox="0 0 20 20"
                                                            xmlns="http://www.w3.org/2000/svg">
                                                            <path fill-rule="evenodd"
                                                                d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                                                                clip-rule="evenodd"></path>
                                                        </svg>

                                                    </span>
                                                </button>
                                            </div>
                                        </div>             
                                    </div>
                
                                    <MountedPersonalities ref="mountedPers" :onShowPersList="onShowPersListFun" :onReady="onPersonalitiesReadyFun"/>

                                </div>                                
                                <div class="w-fit">
                                    <PersonalitiesCommands
                                        v-if="personalities_ready && this.$store.state.mountedPersArr[this.$store.state.config.active_personality_id].commands!=''" 
                                        :commandsList="this.$store.state.mountedPersArr[this.$store.state.config.active_personality_id].commands"
                                        :sendCommand="sendCMDEvent"
                                        :on-show-toast-message="onShowToastMessage"
                                        ref="personalityCMD"
                                    ></PersonalitiesCommands>
                                </div>        
                                <div class="group relative w-12">
                                    <button @click.prevent="toggleSwitch">
                                        <svg width="100" height="50">
                                            <rect x="10" y="15" width="40" height="20" rx="12" ry="12" :fill="config.activate_internet_search ? 'green' : 'red'" />
                                            <circle cx="20" cy="25" r="7" :visibility="config.activate_internet_search ? 'hidden' : 'visible'" />
                                            <circle cx="38" cy="25" r="7" :visibility="config.activate_internet_search ? 'visible' : 'hidden'" />
                                        </svg>                                        
                                    </button>
                                    <div class="pointer-events-none absolute -top-20 left-1/2 w-max -translate-x-1/2 rounded-md bg-gray-100 p-2 opacity-0 transition-opacity group-hover:opacity-100 dark:bg-gray-800"><p class="max-w-sm text-sm text-gray-800 dark:text-gray-200">When enabled, the model will try to complement its answer with information queried from the web.</p></div>
                                </div>
                                <div class="relative grow">
                                    <textarea id="chat" rows="1" v-model="message" title="Hold SHIFT + ENTER to add new line"
                                        class="inline-block  no-scrollbar  p-2.5 w-full text-sm text-gray-900 bg-bg-light rounded-lg border border-gray-300 focus:ring-blue-500 focus:border-blue-500 dark:bg-bg-dark dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
                                        placeholder="Send message..." @keydown.enter.exact="submitOnEnter($event)">
                                    </textarea>
                                </div>
                                <button v-if="loading" type="button"   
                                        class="bg-red-500 dark:bg-red-800 hover:bg-red-600 focus:ring-4 focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 mr-2 mb-2 dark:hover:bg-bg-dark-tone focus:outline-none dark:focus:ring-blue-800"
                                        @click.stop="stopGenerating">
                                        Stop generating
                                </button>

                                <div class="group relative w-max">
                                    <button v-if="!loading" type="button" @click="submit" title="Send"
                                    class="w-6 hover:text-secondary duration-75 active:scale-90 cursor-pointer transform transition-transform hover:translate-y-[-5px] active:scale-90">
                                            <i data-feather="send"></i>
                                    </button>                        
                                    <div class="pointer-events-none absolute -top-10 left-1/2 w-max -translate-x-1/2 rounded-md bg-gray-100 p-2 opacity-0 transition-opacity group-hover:opacity-100 dark:bg-gray-800"><p class="max-w-sm text-sm text-gray-800 dark:text-gray-200">Sends your message to the AI.</p></div>
                                </div>
                                <div class="group relative w-max">
                                    <button v-if="!loading" 
                                        type="button"
                                        @click="startSpeechRecognition"
                                        :class="{ 'text-red-500': isLesteningToVoice }"
                                        class="w-6 hover:text-secondary duration-75 active:scale-90 cursor-pointer transform transition-transform hover:translate-y-[-5px] active:scale-90"
                                    >
                                    <i data-feather="mic"></i>
                                    </button>                      
                                    <div class="pointer-events-none absolute -top-10 left-1/2 w-max -translate-x-1/2 rounded-md bg-gray-100 p-2 opacity-0 transition-opacity group-hover:opacity-100 dark:bg-gray-800"><p class="max-w-sm text-sm text-gray-800 dark:text-gray-200">Press and talk.</p></div>
                                </div>
                                <div class="group relative w-max">
                                    <input type="file" ref="fileDialog" style="display: none" @change="addFiles" multiple />
                                    <button type="button" @click.prevent="add_file"
                                        class="w-6 hover:text-secondary duration-75 active:scale-90 cursor-pointer transform transition-transform hover:translate-y-[-5px] active:scale-90">
                                        <i data-feather="file-plus"></i>
                                    </button>                    
                                    <div class="pointer-events-none absolute -top-10 left-1/2 w-max -translate-x-1/2 rounded-md bg-gray-100 p-2 opacity-0 transition-opacity group-hover:opacity-100 dark:bg-gray-800"><p class="max-w-sm text-sm text-gray-800 dark:text-gray-200">Send File to the AI.</p></div>
                                </div>

                                <div class="group relative w-max">
                                    <button type="button" @click.stop="takePicture"
                                        class="w-6 hover:text-secondary duration-75 active:scale-90 cursor-pointer transform transition-transform hover:translate-y-[-5px] active:scale-90">
                                        <i data-feather="camera"></i>
                                    </button>                 
                                    <div class="pointer-events-none absolute -top-10 left-1/2 w-max -translate-x-1/2 rounded-md bg-gray-100 p-2 opacity-0 transition-opacity group-hover:opacity-100 dark:bg-gray-800"><p class="max-w-sm text-sm text-gray-800 dark:text-gray-200">Take a shot from webcam.</p></div>
                                </div>

                                <div class="group relative w-max">
                                    <button type="button" @click.stop="addWebLink" 
                                        class="w-6 hover:text-secondary duration-75 active:scale-90 cursor-pointer transform transition-transform hover:translate-y-[-5px] active:scale-90">
                                        <i data-feather="globe"></i>
                                    </button>               
                                    <div class="pointer-events-none absolute -top-10 left-1/2 w-max -translate-x-1/2 rounded-md bg-gray-100 p-2 opacity-0 transition-opacity group-hover:opacity-100 dark:bg-gray-800"><p class="max-w-sm text-sm text-gray-800 dark:text-gray-200">Add a weblink to the discussion.</p></div>
                                </div>

                                <div class="group relative w-max">
                                    <button v-if="!loading" type="button" @click="makeAnEmptyUserMessage"
                                        class=" w-6 text-blue-400 hover:text-secondary duration-75 active:scale-90">
                                        <i data-feather="message-square"></i>
                                    </button>
         
                                    <div class="pointer-events-none absolute -top-10 left-1/2 w-max -translate-x-1/2 rounded-md bg-gray-100 p-2 opacity-0 transition-opacity group-hover:opacity-100 dark:bg-gray-800"><p class="max-w-sm text-sm text-gray-800 dark:text-gray-200">New empty User message.</p></div>
                                </div>

                                <div class="group relative w-max">
                                    <button v-if="!loading" type="button" @click="makeAnEmptyAIMessage"
                                        class=" w-6 text-red-400 hover:text-secondary duration-75 active:scale-90">
                                        <i data-feather="message-square"></i>
                                    </button>  

         
                                    <div class="pointer-events-none absolute -top-10 left-1/2 w-max -translate-x-1/2 rounded-md bg-gray-100 p-2 opacity-0 transition-opacity group-hover:opacity-100 dark:bg-gray-800"><p class="max-w-sm text-sm text-gray-800 dark:text-gray-200">New empty ai message.</p></div>
                                </div>
                            </div> 
                            <div class="ml-auto gap-2"> 
                                
                            </div>
                        </div>


            </div>
        </form>
    <UniversalForm ref="universalForm" class="z-20" />
</template>
<style scoped>
/* THESE ARE FOR TransitionGroup components */
.list-move,
/* apply transition to moving elements */
.list-enter-active,
.list-leave-active {
    transition: all 0.5s ease;
}

.list-enter-from {
    transform: translatey(-30px);
}

.list-leave-to {
    opacity: 0;
    transform: translatey(30px);
}

/* ensure leaving items are taken out of layout flow so that moving
   animations can be calculated correctly. */
.list-leave-active {
    position: absolute;
}
</style>
<!-- <script setup>
import MountedPersonalitiesComponent from './MountedPersonalitiesComponent.vue'

</script> -->
<script>
import { nextTick, ref, TransitionGroup } from 'vue'
import axios from "axios";
import feather from 'feather-icons'
import filesize from '../plugins/filesize'
import MountedPersonalities from '@/components/MountedPersonalities.vue'
import MountedPersonalitiesList from '@/components/MountedPersonalitiesList.vue'
import PersonalitiesCommands from '@/components/PersonalitiesCommands.vue';
import InteractiveMenu from '@/components/InteractiveMenu.vue';
import { inject } from 'vue';
import socket from '@/services/websocket.js'
import UniversalForm from '../components/UniversalForm.vue';
import modelImgPlaceholder from "../assets/default_model.png"
import loader_v0 from "../assets/loader_v0.svg"

console.log("modelImgPlaceholder:",modelImgPlaceholder)
const bUrl = import.meta.env.VITE_LOLLMS_API_BASEURL
export default {
    name: 'ChatBox',
    emits: ["messageSentEvent", "sendCMDEvent", "stopGenerating", "loaded", "createEmptyUserMessage", "createEmptyAIMessage", "personalitySelected","addWebLink"],
    props: {
        onTalk: Function,
        discussionList: Array,
        loading: false,
        onShowToastMessage: Function

    },
    components: {        
        UniversalForm,
        MountedPersonalities,
        MountedPersonalitiesList,
        PersonalitiesCommands,
        InteractiveMenu,
        
    },
    setup() {



    },
    data() {
        return {
            loader_v0:loader_v0,
            modelImgPlaceholder:modelImgPlaceholder,
            bUrl:bUrl,
            message: "",
            selecting_model:false,
            selectedModel:'',
            isLesteningToVoice:false,
            filesList: [],
            isFileSentList: [],
            totalSize: 0,
            showfilesList: true,
            showPersonalities: false,
            personalities_ready: false,
            models_menu_icon:""
        }
    },
    computed: {
        currentModel() {
            if(this.$store.state.currentModel!=undefined){
                console.log("Model found")
                return this.$store.state.currentModel;
            }
            else{
                console.log("No model found")
                let obj = {}
                obj.name="unknown"
                return obj;

            }
        },
        installedModels() {
            return this.$store.state.installedModels;
        },
        model_name(){
            return this.$store.state.config.model_name    
        },
        config() {
            return this.$store.state.config;
        },
        mountedPers(){
            return this.$store.state.mountedPers;
        },
        allDiscussionPersonalities() {
            if (this.discussionList.length > 0) {

                let persArray = []
                for (let i = 0; i < this.discussionList.length; i++) {
                    if (!persArray.includes(this.discussionList[i].personality) && !this.discussionList[i].personality == "") {
                        persArray.push(this.discussionList[i].personality)
                    };
                }

                console.log('conputer pers', persArray)
                console.log('dis conputer pers', this.discussionList)
                return persArray
            }
            return null;
        }
    },
    methods: {   
        toggleSwitch() {
            this.$store.state.config.activate_internet_search = !this.$store.state.config.activate_internet_search;
            this.isLoading = true;
            axios.post('/apply_settings', {"config":this.$store.state.config}).then((res) => {
                this.isLoading = false;
                //console.log('apply-res',res)
                if (res.data.status) {
                    if(this.$store.state.config.activate_internet_search){
                        this.$store.state.toast.showToast("Websearch activated.", 4, true)
                    }
                    else{
                        this.$store.state.toast.showToast("Websearch deactivated.", 4, true)
                    }
                    this.settingsChanged = false
                    //this.save_configuration()
                } else {

                    this.$store.state.toast.showToast("Configuration change failed.", 4, false)

                }
                nextTick(() => {
                    feather.replace()

                })
            })
        },
        showModelConfig(){
            try {
                this.isLoading = true
                axios.get('/get_active_binding_settings').then(res => {
                    this.isLoading = false
                    if (res) {

                        console.log('binding sett', res)

                        if (res.data && Object.keys(res.data).length > 0) {

                            // open form

                            this.$refs.universalForm.showForm(res.data, "Binding settings ", "Save changes", "Cancel").then(res => {
                                // send new data
                                try {
                                    axios.post('/set_active_binding_settings',
                                        res).then(response => {

                                            if (response && response.data) {
                                                console.log('binding set with new settings', response.data)
                                                this.$store.state.toast.showToast("Binding settings updated successfully!", 4, true)

                                            } else {
                                                this.$store.state.toast.showToast("Did not get binding settings responses.\n" + response, 4, false)
                                                this.isLoading = false
                                            }


                                        })
                                } catch (error) {
                                    this.$store.state.toast.showToast("Did not get binding settings responses.\n Endpoint error: " + error.message, 4, false)
                                    this.isLoading = false
                                }



                            })
                        } else {
                            this.$store.state.toast.showToast("Binding has no settings", 4, false)
                            this.isLoading = false
                        }

                    }
                })

            } catch (error) {
                this.isLoading = false
                this.$store.state.toast.showToast("Could not open binding settings. Endpoint error: " + error.message, 4, false)
            }
        },
        async unmountPersonality(pers) {
            this.loading = true
            if (!pers) { return }

            const res = await this.unmount_personality(pers.personality || pers)


            if (res.status) {
                this.$store.state.config.personalities = res.personalities
                this.$store.state.toast.showToast("Personality unmounted", 4, true)

                //pers.isMounted = false
                this.$store.dispatch('refreshMountedPersonalities');
                // Select some other personality
                const lastPers = this.$store.state.mountedPersArr[this.$store.state.mountedPersArr.length - 1]

                console.log(lastPers, this.$store.state.mountedPersArr.length)
                // const res2 = await this.select_personality(lastPers.personality)
                const res2 = await this.select_personality(pers.personality)
                if (res2.status) {
                    this.$store.state.toast.showToast("Selected personality:\n" + lastPers.name, 4, true)
                }


            } else {
                this.$store.state.toast.showToast("Could not unmount personality\nError: " + res.error, 4, false)
            }

            this.loading = false
        },
        async unmount_personality(pers) {
            if (!pers) { return { 'status': false, 'error': 'no personality - unmount_personality' } }

            const obj = {
                language: pers.language,
                category: pers.category,
                folder: pers.folder
            }


            try {
                const res = await axios.post('/unmount_personality', obj);

                if (res) {
                    return res.data

                }
            } catch (error) {
                console.log(error.message, 'unmount_personality - settings')
                return
            }

        },        
        async onPersonalitySelected(pers) {
            console.log('on pers', pers)
            // eslint-disable-next-line no-unused-vars
            console.log('selecting ', pers)
            if (pers) {

                if (pers.selected) {
                    this.$store.state.toast.showToast("Personality already selected", 4, true)
                    return
                }


                //this.settingsChanged = true
                const pers_path = pers.language===null?pers.full_path:pers.full_path+':'+pers.language
                console.log("pers_path",pers_path)
                console.log("this.$store.state.config.personalities",this.$store.state.config.personalities)
                if (this.$store.state.config.personalities.includes(pers_path)) {

                    const res = await this.select_personality(pers)
                    console.log('pers is mounted', res)
                    if (res && res.status && res.active_personality_id > -1) {
                        this.$store.state.toast.showToast("Selected personality:\n" + pers.name, 4, true)

                    } else {
                        this.$store.state.toast.showToast("Error on select personality:\n" + pers.name, 4, false)
                    }

                } else {
                    console.log('mounting pers')
                }

                this.$emit('personalitySelected')
            

                nextTick(() => {
                    feather.replace()

                })

            }

        },    
        async select_personality(pers) {
            if (!pers) { return { 'status': false, 'error': 'no personality - select_personality' } }
            const pers_path = pers.language===null?pers.full_path:pers.full_path+':'+pers.language
            console.log("Selecting personality ",pers_path)
            const id = this.$store.state.config.personalities.findIndex(item => item === pers_path)

            const obj = {
                id: id
            }


            try {
                const res = await axios.post('/select_personality', obj);

                if (res) {

                    this.$store.dispatch('refreshConfig').then(() => {
                        this.$store.dispatch('refreshPersonalitiesZoo').then(() => {
                        this.$store.dispatch('refreshMountedPersonalities');                
                        });
                    });
                    return res.data

                }
            } catch (error) {
                console.log(error.message, 'select_personality - settings')
                return
            }

        },    
        emitloaded(){
            this.$emit('loaded')
        },
        showModels(event){
            // Prevent the default button behavior
            event.preventDefault();

            // Programmatically trigger the click event on the select element
            const selectElement = this.$refs.modelsSelectionList;
            console.log(selectElement)

            const event_ = new MouseEvent("click");

            selectElement.dispatchEvent(event_);
        }, 
        setModel(selectedModel){
            console.log("Setting model to "+selectedModel.name);
            this.selecting_model=true
            this.selectedModel = selectedModel
            axios.post("/update_setting", {                
                        setting_name: "model_name",
                        setting_value: selectedModel.name
                    }).then(async (response) => {
                console.log("UPDATED");
                console.log(response);
                await this.$store.dispatch('refreshConfig');    
                await this.$store.dispatch('refreshModels');
                this.$store.state.toast.showToast(`Model changed to ${this.currentModel.name}`,4,true)
                this.selecting_model=false
                }).catch(err=>{
                this.$store.state.toast.showToast(`Error ${err}`,4,true)
                this.selecting_model=false
                });
        
        },
        download_database(){
            axios.get('/download_database')
        },
        remove_file(file){
            axios.get('/remove_file',{name: file}).then(res=>{
                console.log(res)
            })
        },
        clear_files(){
            axios.get('/clear_personality_files_list').then(res=>{
                console.log(res)
                if(res.data.state){
                    this.$store.state.toast.showToast("File removed successfully",4,true);
                    this.filesList.length = 0;
                    this.isFileSentList.length = 0;
                    this.totalSize = 0;
                }
                else{
                    this.$store.state.toast.showToast("Files couldn't be removed",4,false);
                }
            })

        },
        send_file(file, next) {
            console.log("Send file triggered")
            const fileReader = new FileReader();
            const chunkSize = 24 * 1024; // Chunk size in bytes (e.g., 1MB)
            let offset = 0;
            let chunkIndex = 0;
            fileReader.onloadend = () => {
                if (fileReader.error) {
                console.error('Error reading file:', fileReader.error);
                return;
                }
                const chunk = fileReader.result;
                const isLastChunk = offset + chunk.byteLength >= file.size;
                socket.emit('send_file_chunk', {
                filename: file.name,
                chunk: chunk,
                offset: offset,
                isLastChunk: isLastChunk,
                chunkIndex: chunkIndex
                });
                offset += chunk.byteLength;
                chunkIndex++;
                if (!isLastChunk) {
                    readNextChunk();
                } else {
                    console.log('File sent successfully');
                    this.isFileSentList[this.filesList.length-1]=true;
                    console.log(this.isFileSentList)
                    this.$store.state.toast.showToast("File uploaded successfully",4,true);
                    next();
                }
            };
            function readNextChunk() {
                const blob = file.slice(offset, offset + chunkSize);
                fileReader.readAsArrayBuffer(blob);
            }
            console.log('Uploading file');
            readNextChunk();
        },    
        makeAnEmptyUserMessage() {
            this.$emit('createEmptyUserMessage',this.message)
            this.message=""
        },
        makeAnEmptyAIMessage() {
            this.$emit('createEmptyAIMessage')
        },
        startSpeechRecognition() {
            if ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window) {
                this.recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
                this.recognition.lang = this.$store.state.config.audio_in_language; // Set the language, adjust as needed
                this.recognition.interimResults = true; // Enable interim results to get real-time updates

                this.recognition.onstart = () => {
                this.isLesteningToVoice = true;
                this.silenceTimer = setTimeout(() => {
                    this.recognition.stop();
                }, this.silenceTimeout); // Set the silence timeout to stop recognition
                };

                this.recognition.onresult = (event) => {
                let result = '';
                for (let i = event.resultIndex; i < event.results.length; i++) {
                    result += event.results[i][0].transcript;
                }
                this.message = result; // Update the textarea with the real-time recognized words
                clearTimeout(this.silenceTimer); // Clear the silence timeout on every recognized result
                this.silenceTimer = setTimeout(() => {
                    this.recognition.stop();
                }, this.silenceTimeout); // Set a new silence timeout after every recognized result
                };

                this.recognition.onerror = (event) => {
                console.error('Speech recognition error:', event.error);
                this.isLesteningToVoice = false;
                clearTimeout(this.silenceTimer); // Clear the silence timeout on error
                };

                this.recognition.onend = () => {
                console.log('Speech recognition ended.');
                this.isLesteningToVoice = false;
                clearTimeout(this.silenceTimer); // Clear the silence timeout when recognition ends normally
                this.submit(); // Call the function to handle form submission or action once speech recognition ends
                };

                this.recognition.start();
            } else {
                console.error('Speech recognition is not supported in this browser.');
            }
        },

        onPersonalitiesReadyFun(){
            this.personalities_ready = true;
        },
        onShowPersListFun(comp) {
            this.showPersonalities = !this.showPersonalities

        },
        handleOnTalk(pers){
            this.showPersonalities=false
            this.onTalk(pers)
        },
                            
        onMountFun(comp) {
            console.log('Mounting personality')
            this.$refs.mountedPers.constructor()
        },     
        onUnmountFun(comp) {
            console.log('Unmounting personality')
            this.$refs.mountedPers.constructor()
            
        },
        onRemount(comp){
            console.log('Remounting chat')
            this.$refs.mountedPers.constructor()
        },
        computedFileSize(size) {
            nextTick(() => {
                feather.replace()
            })
            return filesize(size)
        },

        removeItem(file) {
            console.log(file)
            axios.post('/remove_file',{file}).then(()=>{
                    this.filesList = this.filesList.filter((item) => item != file)
                })            

            console.log(this.filesList)
        },
        sendMessageEvent(msg) {
            this.$emit('messageSentEvent', msg)

        },
        sendCMDEvent(cmd){
            this.$emit('sendCMDEvent', cmd)
        },
        addWebLink(){
            console.log("Emitting addWebLink")
            this.$emit('addWebLink')
        },
        add_file(){
            // Create a new hidden input element
            const input = document.createElement('input');
            input.type = 'file';
            input.style.display = 'none';
            input.multiple = true;

            // Append the input to the body
            document.body.appendChild(input);

            // Listen for the change event
            input.addEventListener('change', () => {
                // Call the add file function
                console.log("Calling Add file...")
                this.addFiles(input.files);

                // Remove the input element from the DOM
                document.body.removeChild(input);
            });            
            // Trigger the file dialog
            input.click();
       },
        takePicture(){
            socket.emit('take_picture')
            socket.on('picture_taken',()=>{
                axios.get('/get_current_personality_files_list').then(res=>{
                    this.filesList = res.data.files;
                    this.isFileSentList= res.data.files.map(file => {
                        return true;
                    });
                    console.log(`Files recovered: ${this.filesList}`)
                })
            });
        },
        submitOnEnter(event) {
            if(!this.loading){
                if (event.which === 13) {
                    event.preventDefault(); // Prevents the addition of a new line in the text field

                    if (!event.repeat) {

                        this.sendMessageEvent(this.message)
                        this.message = "" // Clear input field
                    }

                }
            }
        },
        submit() {
            if (this.message) {
                this.sendMessageEvent(this.message)
                this.message = ""
            }

        },
        stopGenerating() {
            this.$emit('stopGenerating')
        },
        addFiles(files) {
            console.log("Adding files");
            const newFiles = [...files];
            let index = 0;
            const sendNextFile = () => {
                if (index >= newFiles.length) {
                console.log(`Files_list: ${this.filesList}`);
                return;
                }
                const file = newFiles[index];
                this.filesList.push(file);
                this.isFileSentList.push(false);
                this.send_file(file, () => {
                index++;
                sendNextFile();
                }
                );
            };
            sendNextFile();
        }
    },
    watch: {
        installedModels: {
            immediate: true,
            handler(newVal) {
                this.$nextTick(() => {
                this.installedModels = newVal;
                });
            },
        },   
        model_name: {
            immediate: true,
            handler(newVal) {
                this.$nextTick(() => {
                this.model_name = newVal;
                });
            },
        },                
        showfilesList() {
            nextTick(() => {
                feather.replace()
            })
        },
        loading(newval, oldval) {
            nextTick(() => {
                feather.replace()
            })
        },
        filesList: {
            // Calculate total size
            handler(val, oldVal) {
                let total = 0
                if (val.length > 0) {
                    for (let i = 0; i < val.length; i++) {
                        total = total + parseInt(val[i].size)
                    }
                }
                this.totalSize = filesize(total, true)
                console.log("filesList changed")

            },
            deep: true
        },
        discussionList(val) {

            console.log('discussion arr', val)
        }

    },
    mounted() {
        this.emitloaded();
        nextTick(() => {
            feather.replace()
        })
    },
    activated() {
        nextTick(() => {
            feather.replace()
        })
    }
}
</script>
