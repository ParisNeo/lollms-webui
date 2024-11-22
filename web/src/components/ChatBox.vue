<template>

            <div class="absolute bottom-0 left-0 w-fit min-w-96  w-full justify-center text-center">
                <div v-if="filesList.length > 0" class="items-center gap-2 panels-color shadow-sm hover:shadow-none dark:border-gray-800  w-fit">
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
                            @click="download_files">
                            <i data-feather="download-cloud" class="w-5 h-5 "></i>
                        </button>                        
                    </div>
                </div>

                <!-- CHAT BOX -->
                <div v-if="selecting_model||selecting_binding" title="Selecting model" class="flex flex-row flex-grow justify-end panels-color">
                    <!-- SPINNER -->
                    <div role="status">
                        <img :src="loader_v0" class="w-50 h-50">
                        <span class="sr-only">Selecting model...</span>
                    </div>
                </div>
                <div class="flex w-fit relative grow w-full">
                    <div class="chat-bar" tabindex="0">
                        <div v-if="loading" title="Waiting for reply">
                            <img :src="loader_v0">
                            <!-- SPINNER -->
                            <div role="status">
                                <span class="sr-only">Loading...</span>
                            </div>
                        </div>

                        <ChatBarButton 
                            @click="toggleLeftPanel" 
                            :class="{ 'text-red-500': leftPanelCollapsed }" 
                            title="Toggle View Mode"
                        >
                            <div v-show="leftPanelCollapsed">
                                <!-- Chevron Right SVG -->
                                <svg
                                xmlns="http://www.w3.org/2000/svg"
                                width="24"
                                height="24"
                                fill="none"
                                stroke="currentColor"
                                stroke-width="2"
                                stroke-linecap="round"
                                stroke-linejoin="round"
                                >
                                <polyline points="9 18 15 12 9 6"></polyline>
                                </svg>
                            </div>
                            <div v-show="!leftPanelCollapsed">
                                <!-- Chevron Left SVG -->
                                <svg
                                xmlns="http://www.w3.org/2000/svg"
                                width="24"
                                height="24"
                                fill="none"
                                stroke="currentColor"
                                stroke-width="2"
                                stroke-linecap="round"
                                stroke-linejoin="round"
                                >
                                <polyline points="15 18 9 12 15 6"></polyline>
                                </svg>
                            </div>
                        </ChatBarButton>                             
                              
                        

                        
                        <div class="w-fit">
                            <PersonalitiesCommands
                                v-if="this.$store.state.personalities_ready && this.$store.state.mountedPersArr[this.$store.state.config.active_personality_id].commands!=''" 
                                :commandsList="this.$store.state.mountedPersArr[this.$store.state.config.active_personality_id].commands"
                                :sendCommand="sendCMDEvent"
                                :on-show-toast-message="onShowToastMessage"
                                ref="personalityCMD"
                            ></PersonalitiesCommands>
                        </div>   
                        <div class="w-fit">
                            <PersonalitiesCommands
                                v-if="isDataSourceNamesValid"
                                :icon="'feather:book'"
                                :commandsList="dataSourceNames"
                                :sendCommand="mountDB"
                                :on-show-toast-message="onShowToastMessage"
                                ref="databasesList"
                            ></PersonalitiesCommands>                                    
                        </div>      
                        <div class="relative grow m-0 p-0">
                            <form class="m-0 p-0">
                                <textarea
                                    id="chat"
                                    rows="1"
                                    v-model="message"
                                    @paste="handlePaste"
                                    @keydown.enter.exact="submitOnEnter($event)"
                                    class="w-full p-2 text-sm text-gray-900 dark:text-white bg-gray-100 dark:bg-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                                    placeholder="Send message..."
                                ></textarea>
                            </form>
                            </div>

                            <div class="flex items-center space-x-3">
                            <ChatBarButton
                                v-if="loading"
                                @click="stopGenerating"
                                class="bg-red-500 dark:bg-red-600 hover:bg-red-600 dark:hover:bg-red-700"
                            >
                                <template #icon>
                                <svg class="animate-spin h-5 w-5" viewBox="0 0 24 24">
                                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                </svg>
                                </template>
                                <span>Stop</span>
                            </ChatBarButton>

                            <ChatBarButton v-else @click="submit" title="Send">
                                <template #icon>
                                <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"/>
                                </svg>
                                </template>
                            </ChatBarButton>

                            <ChatBarButton @click="submitWithInternetSearch" title="Send with internet search">
                                <template #icon>
                                <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9"/>
                                </svg>
                                </template>
                            </ChatBarButton>
                            <ChatBarButton 
                                @click="startSpeechRecognition" 
                                :class="{ 'text-red-500': isListeningToVoice }" 
                                title="Voice input"
                            >
                                <template #icon>
                                <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"/>
                                </svg>
                                </template>
                            </ChatBarButton>

                            <ChatBarButton 
                                v-if="$store.state.config.active_tts_service != 'None' && $store.state.config.active_tts_service != null && this.$store.state.config.active_stt_service!='None' && this.$store.state.config.active_stt_service!=null"
                                @click="is_rt ? stopRTCom : startRTCom"
                                :class="is_rt ? 'bg-red-500 dark:bg-red-600' : 'bg-green-500 dark:bg-green-600'"
                                title="Real-time audio mode"
                            >
                                <template #icon>
                                    🌟
                                </template>
                            </ChatBarButton>
                            <div class="relative" @mouseleave="hideSendMenu" v-if="!loading">
                                <div class="relative inline-block">
                                    <!-- Send menu positioned above the button -->
                                    <div v-show="isSendMenuVisible" @mouseenter="showSendMenu" class="absolute m-0 p-0 z-10 bottom-full left-1/2 transform -translate-x-1/2 w-25 bg-white dark:bg-gray-900 rounded-md shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none transition-all duration-300 ease-out mb-2">
                                        <div class="p-4 m-0 flex flex-col gap-4 max-h-96 overflow-y-auto custom-scrollbar">
                                            <!-- Additional Buttons -->
                                            <div class="flex flex-col gap-2">
                                                <ChatBarButton @click="add_file" title="Send file">
                                                    <template #icon>
                                                        <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 13h6m-3-3v6m5 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
                                                        </svg>
                                                    </template>
                                                </ChatBarButton>


                                                <ChatBarButton @click="takePicture" title="Take picture" >
                                                    <template #icon>
                                                        <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"/>
                                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"/>
                                                        </svg>
                                                    </template>
                                                </ChatBarButton>

                                                <ChatBarButton @click="addWebLink" title="Add web link">
                                                    <template #icon>
                                                        <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"/>
                                                        </svg>
                                                    </template>
                                                </ChatBarButton>
                                            </div>
                                        </div>
                                    </div>

                                    <div @mouseenter="showSendMenu">
                                        <button @click.prevent="toggleSendMenu" class="chat-bar-button">
                                            <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v3m0 0v3m0-3h3m-3 0H9m12 0a9 9 0 11-18 0 9 9 0 0118 0z"/>
                                            </svg>
                                        </button>
                                    </div>
                                </div>
                            </div>


                            <ChatBarButton @click="makeAnEmptyUserMessage" title="New user message">
                                <template #icon>
                                <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"/>
                                </svg>
                                </template>
                            </ChatBarButton>

                            <ChatBarButton @click="makeAnEmptyAIMessage" title="New AI message" class="text-red-400 dark:text-red-300">
                                <template #icon>
                                <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
                                </svg>
                                </template>
                            </ChatBarButton>
                            
                            <ChatBarButton 
                                @click="toggleRightPanel" 
                                :class="{ 'text-red-500': !rightPanelCollapsed }" 
                                title="Toggle right Panel"
                            >
                                <div v-show="rightPanelCollapsed">
                                    <!-- Chevron Left SVG -->
                                    <svg
                                    xmlns="http://www.w3.org/2000/svg"
                                    width="24"
                                    height="24"
                                    fill="none"
                                    stroke="currentColor"
                                    stroke-width="2"
                                    stroke-linecap="round"
                                    stroke-linejoin="round"
                                    >
                                    <polyline points="15 18 9 12 15 6"></polyline>
                                    </svg>
                                </div>
                                <div v-show="!rightPanelCollapsed">
                                    <!-- Chevron Right SVG -->
                                    <svg
                                    xmlns="http://www.w3.org/2000/svg"
                                    width="24"
                                    height="24"
                                    fill="none"
                                    stroke="currentColor"
                                    stroke-width="2"
                                    stroke-linecap="round"
                                    stroke-linejoin="round"
                                    >
                                    <polyline points="9 18 15 12 9 6"></polyline>
                                    </svg>
                                </div>
                            </ChatBarButton>   

                            </div>
                            
                            <input type="file" ref="fileDialog" @change="addFiles" multiple style="display: none" />
                    </div> 
                    <div class="ml-auto gap-2"> 
                        
                    </div>
                </div>
            </div>
        
</template>
<style scoped>
.personalities-hover-area {
  position: relative;
  padding-top: 10px; /* Adjust this value to create enough space to move the cursor to the menu */
}
.custom-scrollbar {
  scrollbar-width: thin;
  scrollbar-color: rgba(155, 155, 155, 0.5) transparent;
}

.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}

.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  background-color: rgba(155, 155, 155, 0.5);
  border-radius: 20px;
  border: transparent;
}




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
import MountedPersonalitiesList from '@/components/MountedPersonalitiesList.vue'
import PersonalitiesCommands from '@/components/PersonalitiesCommands.vue';
import ChatBarButton from '@/components/ChatBarButton.vue'
import socket from '@/services/websocket.js'
import sendGlobe from "../assets/send_globe.svg"
import loader_v0 from "../assets/loader_v0.svg"

const bUrl = import.meta.env.VITE_LOLLMS_API_BASEURL

export default {
    name: 'ChatBox',
    emits: ["messageSentEvent", "sendCMDEvent", "stopGenerating", "loaded", "createEmptyUserMessage", "createEmptyAIMessage", "personalitySelected","addWebLink"],
    props: {
        onTalk: Function,
        discussionList: Array,
        loading: {
            default:false
        },
        onShowToastMessage: Function

    },
    components: {        
        PersonalitiesCommands,
        ChatBarButton
    },
    setup() {



    },
    data() {
        return {
            isSendMenuVisible:false,
            is_rt:false,
            bindingHoveredIndex:null,
            modelHoveredIndex:null,
            personalityHoveredIndex:null,
            loader_v0:loader_v0,
            sendGlobe:sendGlobe,
            bUrl:bUrl,
            message: "",
            selecting_binding:false,
            selecting_model:false,
            selectedModel:'',
            isListeningToVoice:false,
            filesList: [],
            isFileSentList: [],
            totalSize: 0,
            showfilesList: true,
            models_menu_icon:"",
            posts_headers : {
                'accept': 'application/json',
                'Content-Type': 'application/json'
            }
        }
    },
    computed: {
        leftPanelCollapsed(){
            return this.$store.state.leftPanelCollapsed;
        },
        rightPanelCollapsed(){
            return this.$store.state.rightPanelCollapsed;
        },
        isCompactMode() {
            return this.$store.state.view_mode === 'compact';
        },
        isDataSourceNamesValid() {
            console.log('dataSourceNames:', this.dataSourceNames);
            console.log('Type of dataSourceNames:', typeof this.dataSourceNames);
            return Array.isArray(this.dataSourceNames) && this.dataSourceNames.length > 0;
        },        
        dataSourceNames() {
            console.log("dataSourceNames", this.$store.state.config.rag_databases);
            // Extract the names from the rag_databases array and transform them into the desired format
            const formattedDataSources = this.$store.state.config.rag_databases.map(dataSource => {
                console.log("entry", dataSource);
                const parts = dataSource.split('::');
                console.log("extracted", parts[0]);

                const isMounted = dataSource.endsWith('mounted');
                const icon = isMounted ? 'feather:check' : '';

                console.log("icon decision", icon);

                return {
                    name: parts[0], 
                    value: parts[0] || 'default_value', 
                    icon: icon, 
                    help: 'mounts the database'
                };
            });
            console.log("formatted data sources", formattedDataSources);
            return formattedDataSources;
        },    
    },
    methods: { 
        showSendMenu() {
            clearTimeout(this.hideSendMenuTimeout);
            this.isSendMenuVisible = true
        },
        hideSendMenu() {
            this.hideSendMenuTimeout = setTimeout(() => {
                this.isSendMenuVisible = false;
            }, 300); // 300ms delay before hiding the menu            
        },

        toggleLeftPanel(){
            console.log(this.leftPanelCollapsed)
            this.$store.commit('setLeftPanelCollapsed', ! this.leftPanelCollapsed); // Assuming you have a mutation to set the view mode
        },
        async toggleRightPanel(){
            console.log(this.rightPanelCollapsed)
            this.$store.commit('setRightPanelCollapsed', !this.rightPanelCollapsed); // Assuming you have a mutation to set the view mode
            if(this.rightPanelCollapsed){
                this.$store.commit('setleftPanelCollapsed', true); // Assuming you have a mutation to set the view mode
                this.$nextTick(() => {
                this.extractHtml()
                });

            }
            console.log(this.rightPanelCollapsed)
        }, 

        handlePaste(event) {
            const items = (event.clipboardData || event.originalEvent.clipboardData).items;
            let filesToUpload = [];
            for (let item of items) {
                if (item.type.indexOf("image") !== -1) {
                    const blob = item.getAsFile();
                    // Generate a unique identifier for the file
                    const uniqueId = Date.now() + '_' + Math.random().toString(36).substr(2, 9);
                    const newFileName = `image_${uniqueId}.png`;
                    console.log("newFileName",newFileName)
                    // Create a new file with the unique name
                    const newFile = new File([blob], newFileName, {type: blob.type});

                    this.addFiles([newFile]); // Assuming addFiles accepts an array of files
                }
                else if (item.kind === 'file') {
                    const file = item.getAsFile();
                    filesToUpload.push(file);
                }
            }
            if (filesToUpload.length > 0) {
                this.addFiles(filesToUpload);
            }
        },
        emitloaded(){
            this.$emit('loaded')
        },
        download_files(){
            axios.get('/download_files')
        },
        remove_file(file){
            axios.get('/remove_discussion_file',{client_id:this.$store.state.client_id, name: file}).then(res=>{
                console.log(res)
            })
        },
        clear_files(){
            axios.post('/clear_discussion_files_list', {"client_id":this.$store.state.client_id}).then(res=>{
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
        startRTCom(){
            this.is_rt = true
            console.log("is_rt:",this.is_rt)
            socket.emit('start_bidirectional_audio_stream');
            nextTick(() => {
                feather.replace()
            })
        },
        stopRTCom(){
            this.is_rt = false
            console.log("is_rt:",this.is_rt)
            socket.emit('stop_bidirectional_audio_stream');
            nextTick(() => {
                feather.replace()
            }
            )
        },
        startSpeechRecognition() {
            if ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window) {
                this.recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
                this.recognition.lang = this.$store.state.config.audio_in_language; // Set the language, adjust as needed
                this.recognition.interimResults = true; // Enable interim results to get real-time updates

                this.recognition.onstart = () => {
                this.isListeningToVoice = true;
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
                this.isListeningToVoice = false;
                clearTimeout(this.silenceTimer); // Clear the silence timeout on error
                };

                this.recognition.onend = () => {
                console.log('Speech recognition ended.');
                this.isListeningToVoice = false;
                clearTimeout(this.silenceTimer); // Clear the silence timeout when recognition ends normally
                this.submit(); // Call the function to handle form submission or action once speech recognition ends
                };

                this.recognition.start();
            } else {
                console.error('Speech recognition is not supported in this browser.');
            }
        },
        computedFileSize(size) {
            nextTick(() => {
                feather.replace()
            })
            return filesize(size)
        },

        removeItem(file) {
            console.log("Removing ",file.name)
            axios.post('/remove_discussion_file',{
                                        client_id:this.$store.state.client_id, 
                                        name:file.name
                                    },
                                    {headers: this.posts_headers}
                                ).then(()=>{
                    this.filesList = this.filesList.filter((item) => item != file)
                })            

            console.log(this.filesList)
        },
        sendMessageEvent(msg, type="no_internet") {
            this.$emit('messageSentEvent', msg, type)

        },
        sendCMDEvent(cmd){
            this.$emit('sendCMDEvent', cmd)
        },
        async mountDB(cmd){
            await axios.post('/toggle_mount_rag_database', {"client_id":this.$store.state.client_id,"database_name":cmd})
            await this.$store.dispatch('refreshConfig');
            console.log("Refreshed")

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
                axios.post('/get_discussion_files_list', {"client_id":this.$store.state.client_id}).then(res=>{
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
        submitWithInternetSearch(){
            if (this.message) {
                this.sendMessageEvent(this.message, "internet")
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
        console.log("Chatbar mounted")
        socket.on('rtcom_status_changed', (data)=>{
                this.$store.dispatch('fetchisRTOn');
                console.log("rtcom_status_changed: ",data.status)
                console.log("active_tts_service: ",this.$store.state.config.active_tts_service)
                console.log("is_rt_on: ",this.$store.state.is_rt_on)
                //this.is_rt = this.$store.state.is_rt_on
            });
        this.$store.dispatch('fetchisRTOn');
    },
    
    activated() {
        nextTick(() => {
            feather.replace()
        })
    }
}
</script>
