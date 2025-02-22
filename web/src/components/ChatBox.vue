<template>
    <!-- Chatbar Container: Fixed, centered, and compact with a modern look -->
    <div
        class="fixed bottom-8 left-1/2 transform -translate-x-1/2 w-full max-w-2xl p-6 bg-white/95 dark:bg-gray-900/95 backdrop-blur-sm rounded-xl border border-gray-200 dark:border-gray-700 shadow-2xl transition-all duration-300 ease-in-out z-50"
    >
      <!-- Files Panel (if any files are attached) -->
      <div v-if="filesList.length > 0" class="mb-3">
        <div class="flex items-center justify-between mb-2">
          <button
            class="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors"
            :title="showfilesList ? 'Hide file list' : 'Show file list'"
            @click.stop="showfilesList = !showfilesList"
          >
            <i data-feather="list" class="w-5 h-5"></i>
          </button>
          <div class="flex items-center gap-2">
            <span class="text-sm" title="Total file size and number of files">
              {{ totalSize }} ({{ filesList.length }})
            </span>
            <button @click="clear_files" class="p-2 hover:text-red-500 transition-colors" title="Clear all files">
              <i data-feather="trash" class="w-4 h-4"></i>
            </button>
            <button @click="download_files" class="p-2 hover:text-primary transition-colors" title="Download all files">
              <i data-feather="download-cloud" class="w-4 h-4"></i>
            </button>
          </div>
        </div>
        <!-- Expandable files list -->
        <TransitionGroup
          v-show="showfilesList"
          name="list"
          tag="div"
          class="max-h-40 overflow-y-auto rounded-lg bg-gray-50 dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700"
        >
          <div
            v-for="(file, index) in filesList"
            :key="index + '-' + file.name"
            class="flex items-center justify-between p-2 group hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
          >
            <div class="flex items-center gap-2 min-w-0">
              <div v-if="!isFileSentList[index]" class="animate-spin" title="Uploading...">
                <i data-feather="loader" class="w-4 h-4 text-secondary"></i>
              </div>
              <i data-feather="file" class="w-4 h-4 flex-shrink-0" title="File"></i>
              <span
                class="truncate text-sm"
                :class="isFileSentList[index] ? 'text-green-500' : 'text-gray-500'"
                :title="file.name"
              >
                {{ file.name }}
              </span>
            </div>
            <div class="flex items-center gap-2 flex-shrink-0">
              <span class="text-xs text-gray-500" :title="computedFileSize(file.size)">
                {{ computedFileSize(file.size) }}
              </span>
              <button
                @click="removeItem(file)"
                class="opacity-0 group-hover:opacity-100 p-1 hover:text-red-500 transition-all"
                title="Remove file"
              >
                <i data-feather="x" class="w-4 h-4"></i>
              </button>
            </div>
          </div>
        </TransitionGroup>
      </div>
  
      <!-- Main Chat Input and Actions -->
      <div class="flex flex-col gap-2">
        <div class="flex flex-row gap-2 w-full">

        <!-- Input Box with Integrated Send Buttons -->
        <div class="relative flex-grow">
            <textarea
                id="chat"
                :disabled="loading"
                v-model="message"
                @paste="handlePaste"
                @keydown.enter.exact="submitOnEnter($event)"
                rows="1"
                class="w-full p-3 pr-24 text-sm rounded-lg bg-gray-100 dark:bg-gray-800 focus:ring-2 focus:ring-primary border border-gray-300 dark:border-gray-700 resize-y min-h-[3rem] max-h-32 overflow-auto transition-colors"
                placeholder="Write your message to the AI here..."
                title="Enter your message here"
            ></textarea>
            <!-- Integrated Send Buttons inside the input box -->
            <div class="absolute inset-y-0 right-0 flex items-center pr-2 space-x-1">
                <template v-if="loading">
                    <button
                        @click="stopGenerating"
                        class="p-2 bg-red-500 text-white rounded-lg hover:bg-red-600 
                              transform hover:scale-105 active:scale-95
                              transition-all duration-200 ease-in-out
                              shadow-md hover:shadow-lg
                              animate-pulse
                              focus:outline-none focus:ring-2 focus:ring-red-400
                              disabled:opacity-50"
                        title="Stop generating"
                        aria-label="Stop generation process"
                    >
                        <i data-feather="stop-circle" 
                          class="w-5 h-5 animate-spin-slow" 
                        ></i>
                        <span class="sr-only">Stop Generation</span>
                    </button>
                </template>                <template v-else>
                <button
                    @click="submit"
                    class="p-2 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-lg transition-colors"
                    title="Send message"
                >
                    <i data-feather="send" class="w-5 h-5"></i>
                </button>
                <button
                    @click="submitWithInternetSearch"
                    class="p-2 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-lg transition-colors"
                    title="Send with internet search"
                >
                    <i data-feather="globe" class="w-5 h-5"></i>
                </button>
                </template>
            </div>
        </div>    
        </div>

  
        <!-- Additional Actions Row -->
        <div class="flex items-center justify-between relative">
          <!-- Left Panel Toggle -->
          <button
          @click="toggleLeftPanel"
          class="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors"
          :class="$store.state.leftPanelCollapsed ? '' : 'bg-gray-300'"
          :title="$store.state.leftPanelCollapsed ? 'Expand Left Panel' : 'Collapse Left Panel'"
          >
          <svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <!-- Main vertical bar with rounded corners -->
              <rect x="3" y="2" width="4" height="20" rx="2" fill="currentColor"/>
              
              <!-- Three horizontal lines with rounded corners -->
              <rect x="9" y="6" width="12" height="2" rx="1" fill="currentColor"/>
              <rect x="9" y="11" width="12" height="2" rx="1" fill="currentColor"/>
              <rect x="9" y="16" width="12" height="2" rx="1" fill="currentColor"/>
          </svg>          
          </button>

          <!-- Left Side: Personalities / Commands -->
          <div class="flex items-center gap-2">
            <PersonalitiesCommands
              v-if="isCommandsValid"
              :help="'Personality commands'"
              :commandsList="$store.state.mountedPersArr[$store.state.config.active_personality_id].commands"
              :sendCommand="sendCMDEvent"
              :on-show-toast-message="onShowToastMessage"
              ref="personalityCMD"
            />
            <PersonalitiesCommands
              v-if="isdataLakeNamesValid"
              :help="'Datalakes'"
              icon="feather:book"
              :commandsList="dataLakeNames"
              :sendCommand="mountDB"
              :on-show-toast-message="onShowToastMessage"
              ref="databasesList"
            />
            <PersonalitiesCommands
              v-if="$store.state.config.mounted_function_calls.length>0"
              icon="feather:zap"
              :help="'Function calls (WIP)'"
              :commandsList="functionCalls"
              :sendCommand="toggleFunctionCall"
              :on-show-toast-message="onShowToastMessage"
              ref="functioncalls"
            />
          </div>
    
          <!-- Right Side: Additional Options -->
            <!-- Think First Mode Toggle -->
            <button
                @click="toggleThinkFirstMode"
                class="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                :class="{ 'text-primary': $store.state.config.think_first_mode }"
                title="Toggle Think First Mode"
                >
                <svg
                    xmlns="http://www.w3.org/2000/svg"
                    class="w-5 h-5"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                >
                    <!-- Bulb outline with filament -->
                    <path d="M12 2a6 6 0 0 1 6 6c0 2.42-1.61 4.5-4 5.25V15a2 2 0 0 1-4 0v-1.75C7.61 12.5 6 10.42 6 8a6 6 0 0 1 6-6z" />
                    <!-- Bulb base -->
                    <path d="M9 18h6" />
                    <path d="M10 22h4" />
                </svg>
                </button>


            <!-- Fun Mode Toggle -->
            <button
                @click="toggleFunMode"
                class="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                :class="{ 'text-primary': $store.state.config.fun_mode }"
                title="Toggle Fun Mode"
            >
                <svg
                    xmlns="http://www.w3.org/2000/svg"
                    class="w-5 h-5"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                >
                    <!-- Smiley face icon for Fun Mode -->
                    <path d="M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20z" />
                    <!-- Smiley face icon -->
                    <circle cx="12" cy="12" r="10" />
                    <path d="M8 14s1.5 2 4 2 4-2 4-2M9 9h.01M15 9h.01" />
                </svg>
            </button>

          <div class="flex items-center gap-2">
            <button
              @click="startSpeechRecognition"
              class="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
              :class="{ 'text-red-500': isListeningToVoice }"
              title="Voice input"
            >
              <i data-feather="mic" class="w-5 h-5"></i>
            </button>
            <button
              v-if="$store.state.config.active_tts_service !== 'None' && $store.state.config.active_tts_service && $store.state.config.active_stt_service !== 'None'"
              @click="updateRT"
              class="p-2 rounded-lg transition-colors"
              :class="is_rt ? 'bg-red-500 text-white' : 'bg-green-500 text-white'"
              title="Toggle real-time audio mode"
            >
              🌟
            </button>
            <!-- More Actions Dropdown Trigger -->
            <button
              @click="toggleSendMenu"
              class="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
              title="More actions (Add file, take picture, etc.)"
            >
              <i data-feather="plus-circle" class="w-5 h-5"></i>
            </button>
            <!-- Dropdown Menu for Extra Actions -->
            <div
              v-show="isSendMenuVisible"
              class="absolute right-0 bottom-full mb-12 w-48 bg-white dark:bg-gray-900 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 z-10"
            >
              <div class="p-2 space-y-1">
                <button
                  @click="add_file"
                  class="w-full p-2 flex items-center gap-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
                  title="Add a file"
                >
                  <i data-feather="file-plus" class="w-4 h-4"></i>
                  <span>Add File</span>
                </button>
                <button
                  @click="takePicture"
                  class="w-full p-2 flex items-center gap-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
                  title="Take a picture"
                >
                  <i data-feather="camera" class="w-4 h-4"></i>
                  <span>Take Picture</span>
                </button>
                <button
                  @click="addWebLink"
                  class="w-full p-2 flex items-center gap-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
                  title="Add a web link"
                >
                  <i data-feather="link" class="w-4 h-4"></i>
                  <span>Add Web Link</span>
                </button>
              </div>
            </div>
            <button
              @click="makeAnEmptyUserMessage"
              class="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
              title="Insert an empty user message"
            >
              <i data-feather="message-circle" class="w-5 h-5"></i>
            </button>
            <button
              @click="makeAnEmptyAIMessage"
              class="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors text-red-400"
              title="Insert an empty AI message"
            >
              <i data-feather="cpu" class="w-5 h-5"></i>
            </button>
          </div>
          
            <!-- Right Panel Toggle -->
            <button
            @click="toggleRightPanel"
            class="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors"
            :class="$store.state.rightPanelCollapsed ? '' : 'bg-gray-300'"
            :title="$store.state.rightPanelCollapsed ? 'Expand Right Panel' : 'Collapse Right Panel'"
            >
            <svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <!-- Main vertical bar with rounded corners (right side) -->
                <rect x="17" y="2" width="4" height="20" rx="2" fill="currentColor"/>
                
                <!-- Three horizontal lines with rounded corners -->
                <rect x="3" y="6" width="12" height="2" rx="1" fill="currentColor"/>
                <rect x="3" y="11" width="12" height="2" rx="1" fill="currentColor"/>
                <rect x="3" y="16" width="12" height="2" rx="1" fill="currentColor"/>
            </svg>
            </button>            

        </div>
      </div>
    </div>
  
    <!-- Hidden File Input -->
    <input type="file" ref="fileDialog" @change="addFiles" multiple class="hidden" />
  
    <!-- Tutorial Help Overlay -->
    <div v-if="showHelpModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/70">
      <div class="bg-white dark:bg-gray-900 rounded-lg p-6 max-w-xl w-full relative overflow-y-auto max-h-[80vh]">
        <h2 class="text-2xl font-bold mb-4 text-center">Tutorial</h2>
        <button
            @click="toggleHelpModal"
            class="absolute top-2 right-2 text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
            title="Close tutorial"
            >
            <i data-feather="x" class="w-6 h-6"></i>
        </button>

        <p class="mb-4 text-center">Below is an overview of the chatbar buttons and what they do.</p>
        <div class="space-y-4">
          <div class="flex items-center gap-3">
            <button class="p-2 bg-primary text-white rounded-lg">
              <i data-feather="send" class="w-5 h-5"></i>
            </button>
            <span>Sends your message to the AI.</span>
          </div>
          <div class="flex items-center gap-3">
            <button class="p-2 bg-gray-50 rounded-lg border">
              <i data-feather="globe" class="w-5 h-5"></i>
            </button>
            <span>Sends your message with an internet search.</span>
          </div>
          <div class="flex items-center gap-3">
            <button class="p-2 hover:bg-gray-100 rounded-lg">
              <i data-feather="mic" class="w-5 h-5"></i>
            </button>
            <span>Activates voice input.</span>
          </div>
          <div class="flex items-center gap-3">
            <button class="p-2 bg-green-500 text-white rounded-lg">
              <span>🌟</span>
            </button>
            <span>Toggles real-time audio mode.</span>
          </div>
          <div class="flex items-center gap-3">
            <button class="p-2 hover:bg-gray-100 rounded-lg">
              <i data-feather="plus-circle" class="w-5 h-5"></i>
            </button>
            <span>Opens more actions (Add File, Take Picture, Add Web Link).</span>
          </div>
          <div class="flex items-center gap-3">
            <button class="p-2 hover:bg-gray-100 rounded-lg">
              <i data-feather="info" class="w-5 h-5"></i>
            </button>
            <span>Opens this tutorial overlay.</span>
          </div>
          <div class="flex items-center gap-3">
            <button class="p-2 hover:bg-gray-100 rounded-lg">
              <i data-feather="message-circle" class="w-5 h-5"></i>
            </button>
            <span>Inserts an empty user message.</span>
          </div>
          <div class="flex items-center gap-3">
            <button class="p-2 hover:bg-gray-100 rounded-lg text-red-400">
              <i data-feather="cpu" class="w-5 h-5"></i>
            </button>
            <span>Inserts an empty AI message.</span>
          </div>
          <div class="flex items-center gap-3">
            <button class="p-2 hover:bg-gray-100 rounded-lg">
              <i data-feather="chevron-left" class="w-5 h-5"></i>
            </button>
            <span>Toggles the left panel.</span>
          </div>
          <div class="flex items-center gap-3">
            <button class="p-2 hover:bg-gray-100 rounded-lg">
              <i data-feather="chevron-right" class="w-5 h-5"></i>
            </button>
            <span>Toggles the right panel.</span>
          </div>
        </div>
        <button
          @click="toggleHelpModal"
          class="absolute top-2 right-2 text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
          title="Close tutorial"
        >
          <i data-feather="x" class="w-6 h-6"></i>
        </button>
      </div>
    </div>
  </template>
  
  
<style scoped>
@keyframes spin-slow {
    from {
        transform: rotate(0deg);
    }
    to {
        transform: rotate(360deg);
    }
}

.animate-spin-slow {
    animation: spin-slow 3s linear infinite;
}
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
            showHelpModal: false,
            models_menu_icon:"",
            posts_headers : {
                'accept': 'application/json',
                'Content-Type': 'application/json'
            }
        }
    },
    computed: {
        isCompactMode() {
            return this.$store.state.view_mode === 'compact';
        },
        isdataLakeNamesValid() {
            console.log('dataLakeNames:', this.dataLakeNames);
            console.log('Type of dataLakeNames:', typeof this.dataLakeNames);
            return Array.isArray(this.dataLakeNames) && this.dataLakeNames.length > 0;
        },  
        isCommandsValid() {
            return Array.isArray(this.$store.state.mountedPersArr[this.$store.state.config.active_personality_id].commands) && this.$store.state.mountedPersArr[this.$store.state.config.active_personality_id].commands.length > 0;
        },        
        dataLakeNames() {
            console.log("rag_databases", this.$store.state.config.datalakes);
            // Extract the names from the combined array and transform them into the desired format
            const formattedDataSources = this.$store.state.config.datalakes.map(dataLake => {
                console.log("entry", dataLake);
                return {
                    name: dataLake.alias,
                    value: dataLake.alias || 'default_value',
                    is_checked: dataLake.mounted,
                    icon: '',
                    help: 'mounts the datalake'
                };
            });

            console.log("formatted datalake", formattedDataSources);
            return formattedDataSources;
        },
        functionCalls(){
            console.log("Function calls", this.$store.state.config.mounted_function_calls);
            // Extract the names from the combined array and transform them into the desired format
            const formattedFunctionCalls = this.$store.state.config.mounted_function_calls.map(functionCall => {
                console.log("entry", functionCall);
                return {
                    name: functionCall.name,
                    value: functionCall,
                    dir: functionCall.dir,
                    is_checked: functionCall.selected,
                    icon: functionCall.icon,
                    help: functionCall.help
                };
            });

            console.log("formatted function calls", formattedFunctionCalls);
            return formattedFunctionCalls;
        }

    },
    methods: { 
        toggleThinkFirstMode() {
            this.$store.state.config.think_first_mode = !this.$store.state.config.think_first_mode
            
            this.$store.state.applyConfiguration()
            this.$store.state.saveConfiguration()
        },
        toggleFunMode() {
            this.$store.state.config.fun_mode = !this.$store.state.config.fun_mode

            this.$store.state.applyConfiguration()
            this.$store.state.saveConfiguration()
        },
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
            console.log(this.$store.state.leftPanelCollapsed)
            this.$store.commit('setLeftPanelCollapsed', !this.$store.state.leftPanelCollapsed); // Assuming you have a mutation to set the view mode
        },
        async toggleRightPanel(){
            console.log(this.$store.state.rightPanelCollapsed)
            
            this.$store.commit('setRightPanelCollapsed', !this.$store.state.rightPanelCollapsed); // Assuming you have a mutation to set the view mode
            if(this.$store.state.rightPanelCollapsed){
                this.$store.commit('setleftPanelCollapsed', true); // Assuming you have a mutation to set the view mode
                this.$nextTick(() => {
                this.extractHtml()
                });

            }
            console.log(this.$store.state.rightPanelCollapsed)
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
        toggleSendMenu() {
            this.isSendMenuVisible = !this.isSendMenuVisible;
        },
        toggleHelpModal() {
            this.showHelpModal = !this.showHelpModal;
        },
        updateRT() {
            console.log("Updating rt status")
            if(this.is_rt){
                this.stopRTCom();
            }
            else{
                this.startRTCom();
            }             
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
            console.log("datalake_name:")
            console.log(cmd)
            await axios.post('/toggle_mount_rag_database', {"client_id":this.$store.state.client_id,"datalake_name":cmd})
            await this.$store.dispatch('refreshConfig');
            console.log("Refreshed")

        },
        async toggleFunctionCall(func){
            console.log("function call:")
            console.log(func)
            await axios.post('/toggle_function_call', {
                        client_id: this.$store.state.client_id,
                        name: func.name,
                        dir: func.dir
                    })
            await this.$store.dispatch('refreshConfig');
            console.log("Refreshed")

        },
        
        addWebLink(){
            this.isSendMenuVisible = false;
            console.log("Emitting addWebLink")
            this.$emit('addWebLink')
        },
        add_file(){
            this.isSendMenuVisible = false;
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
            this.isSendMenuVisible = false;
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
            console.log("SUBMIT")
            if (this.message) {
                this.sendMessageEvent(this.message)
                this.message = ""
            }

        },
        submitWithInternetSearch(){
            console.log("SUBMIT WITH internet")
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
