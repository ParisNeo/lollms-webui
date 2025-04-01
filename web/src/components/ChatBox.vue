<template>
  <!-- Chatbar Container: Fixed, centered, and compact with theme styling -->
  <div
      class="chatbox-color fixed bottom-8 left-1/2 transform -translate-x-1/2 w-full max-w-2xl p-4 bg-opacity-95 backdrop-blur-sm rounded-xl border border-blue-300 dark:border-blue-600 shadow-xl transition-all duration-300 ease-in-out z-50"
  >
    <!-- Files Panel (if any files are attached) -->
    <div v-if="filesList.length > 0" class="mb-3 border-b border-blue-200 dark:border-blue-700 pb-3">
      <div class="flex items-center justify-between mb-2">
        <button
          class="svg-button"
          :title="showfilesList ? 'Hide file list' : 'Show file list'"
          @click.stop="showfilesList = !showfilesList"
        >
          <i data-feather="list" class="w-5 h-5"></i>
        </button>
        <div class="flex items-center gap-2">
          <span class="text-sm text-blue-600 dark:text-blue-300" title="Total file size and number of files">
            {{ totalSize }} ({{ filesList.length }})
          </span>
          <button @click="clear_files" class="svg-button hover:text-red-500" title="Clear all files">
            <i data-feather="trash" class="w-4 h-4"></i>
          </button>
          <button @click="download_files" class="svg-button hover:text-blue-500" title="Download all files">
            <i data-feather="download-cloud" class="w-4 h-4"></i>
          </button>
        </div>
      </div>
      <!-- Expandable files list -->
      <TransitionGroup
        v-show="showfilesList"
        name="list"
        tag="div"
        class="max-h-40 overflow-y-auto rounded-lg bg-blue-100 dark:bg-blue-800 divide-y divide-blue-200 dark:divide-blue-700 scrollbar"
      >
        <div
          v-for="(file, index) in filesList"
          :key="index + '-' + file.name"
          class="flex items-center justify-between p-2 group hover:bg-blue-200 dark:hover:bg-blue-700 transition-colors"
        >
          <div class="flex items-center gap-2 min-w-0">
            <div v-if="!isFileSentList[index]" class="animate-spin" title="Uploading...">
              <i data-feather="loader" class="w-4 h-4 text-blue-500 dark:text-blue-400"></i>
            </div>
            <i data-feather="file" class="w-4 h-4 flex-shrink-0 text-blue-600 dark:text-blue-300" title="File"></i>
            <span
              class="truncate text-sm"
              :class="isFileSentList[index] ? 'text-green-500 dark:text-green-400' : 'text-blue-700 dark:text-blue-200'"
              :title="file.name"
            >
              {{ file.name }}
            </span>
          </div>
          <div class="flex items-center gap-2 flex-shrink-0">
            <span class="text-xs text-blue-500 dark:text-blue-400" :title="computedFileSize(file.size)">
              {{ computedFileSize(file.size) }}
            </span>
            <button
              @click="removeItem(file)"
              class="svg-button opacity-0 group-hover:opacity-100 hover:text-red-500 transition-all"
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
              class="input w-full p-3 pr-24 text-sm rounded-lg focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400 border-blue-300 dark:border-blue-600 resize-y min-h-[3rem] max-h-32 overflow-auto transition-colors scrollbar text-blue-900 dark:text-blue-100 placeholder-blue-400 dark:placeholder-blue-500"
              placeholder="Write your message to the AI here..."
              title="Enter your message here"
          ></textarea>
          <!-- Integrated Send Buttons inside the input box -->
          <div class="absolute inset-y-0 right-0 flex items-center pr-2 space-x-1">
              <template v-if="loading">
                  <button
                      @click="stopGenerating"
                      class="btn bg-red-500 text-white hover:bg-red-600 focus:ring-red-400 transform hover:scale-105 active:scale-95 transition-all duration-200 ease-in-out shadow-md hover:shadow-lg animate-pulse p-2"
                      title="Stop generating"
                      aria-label="Stop generation process"
                  >
                      <i data-feather="stop-circle" class="w-5 h-5 animate-spin-slow"></i>
                      <span class="sr-only">Stop Generation</span>
                  </button>
              </template>
              <template v-else>
                  <button
                      @click="submit"
                      class="svg-button"
                      title="Send message"
                  >
                      <i data-feather="send" class="w-5 h-5"></i>
                  </button>
                  <button
                      @click="submitWithInternetSearch"
                      class="svg-button"
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
          class="svg-button"
          :class="$store.state.leftPanelCollapsed ? '' : 'bg-blue-300 dark:bg-blue-700'"
          :title="$store.state.leftPanelCollapsed ? 'Expand Left Panel' : 'Collapse Left Panel'"
        >
          <!-- Custom Icon for Left Panel Toggle -->
          <svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" class="w-5 h-5">
              <rect x="3" y="2" width="4" height="20" rx="2" fill="currentColor"/>
              <rect x="9" y="6" width="12" height="2" rx="1" fill="currentColor"/>
              <rect x="9" y="11" width="12" height="2" rx="1" fill="currentColor"/>
              <rect x="9" y="16" width="12" height="2" rx="1" fill="currentColor"/>
          </svg>          
        </button>

        <!-- Left Side: Personalities / Commands -->
        <div class="flex items-center gap-1">
          <!-- Assuming PersonalitiesCommands has internal styling -->
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
            :showSettings="showFunctionSettings"
            :on-show-toast-message="onShowToastMessage"
            ref="functioncalls"
          />
        </div>
  
        <!-- Central Buttons: Modes -->
         <div class="flex items-center gap-1">
             <button
              @click="toggleThinkFirstMode"
              class="svg-button"
              :class="{ 'text-blue-600 dark:text-blue-400 bg-blue-200 dark:bg-blue-700': $store.state.config.think_first_mode }"
              title="Toggle Think First Mode"
              >
              <!-- Bulb Icon -->
              <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M12 2a6 6 0 0 1 6 6c0 2.42-1.61 4.5-4 5.25V15a2 2 0 0 1-4 0v-1.75C7.61 12.5 6 10.42 6 8a6 6 0 0 1 6-6z" />
                  <path d="M9 18h6" /> <path d="M10 22h4" />
              </svg>
              </button>

             <button
                 @click="toggleFunMode"
                 class="svg-button"
                 :class="{ 'text-blue-600 dark:text-blue-400 bg-blue-200 dark:bg-blue-700': $store.state.config.fun_mode }"
                 title="Toggle Fun Mode"
             >
                 <!-- Smiley Icon -->
                 <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                     <circle cx="12" cy="12" r="10" /> <path d="M8 14s1.5 2 4 2 4-2 4-2M9 9h.01M15 9h.01" />
                 </svg>
             </button>
          </div>

        <!-- Right Side: Additional Options -->
        <div class="flex items-center gap-1">
          <button
            @click="startSpeechRecognition"
            class="svg-button"
            :class="{ 'text-red-500 dark:text-red-400 animate-pulse': isListeningToVoice }"
            title="Voice input"
          >
            <i data-feather="mic" class="w-5 h-5"></i>
          </button>
          <button
            v-if="$store.state.config.active_tts_service !== 'None' && $store.state.config.active_tts_service && $store.state.config.active_stt_service !== 'None'"
            @click="updateRT"
            class="btn btn-sm p-1.5"
            :class="is_rt ? 'bg-red-500 hover:bg-red-600 text-white' : 'bg-green-500 hover:bg-green-600 text-white'"
            title="Toggle real-time audio mode"
          >
            <span class="text-xs font-bold">RT</span> <!-- Using text instead of emoji for better control -->
          </button>
          <!-- More Actions Dropdown Trigger -->
          <button
            @click="toggleSendMenu"
            class="svg-button"
            title="More actions (Add file, take picture, etc.)"
          >
            <i data-feather="plus-circle" class="w-5 h-5"></i>
          </button>
          <!-- Dropdown Menu for Extra Actions -->
          <div
            v-show="isSendMenuVisible"
            class="absolute right-0 bottom-full mb-2 w-48 bg-blue-100 dark:bg-blue-800 rounded-lg shadow-lg border border-blue-300 dark:border-blue-600 z-10"
             @mouseleave="isSendMenuVisible=false"
          >
            <div class="p-2 space-y-1">
              <button
                @click="add_file"
                class="w-full p-2 flex items-center gap-2 rounded-lg hover:bg-blue-200 dark:hover:bg-blue-700 transition-colors text-blue-700 dark:text-blue-200"
                title="Add a file"
              >
                <i data-feather="file-plus" class="w-4 h-4"></i>
                <span class="text-sm">Add File</span>
              </button>
              <button
                @click="takePicture"
                class="w-full p-2 flex items-center gap-2 rounded-lg hover:bg-blue-200 dark:hover:bg-blue-700 transition-colors text-blue-700 dark:text-blue-200"
                title="Take a picture"
              >
                <i data-feather="camera" class="w-4 h-4"></i>
                <span class="text-sm">Take Picture</span>
              </button>
              <button
                @click="addWebLink"
                class="w-full p-2 flex items-center gap-2 rounded-lg hover:bg-blue-200 dark:hover:bg-blue-700 transition-colors text-blue-700 dark:text-blue-200"
                title="Add a web link"
              >
                <i data-feather="link" class="w-4 h-4"></i>
                <span class="text-sm">Add Web Link</span>
              </button>
            </div>
          </div>
          <button
            @click="makeAnEmptyUserMessage"
            class="svg-button"
            title="Insert an empty user message"
          >
            <i data-feather="message-circle" class="w-5 h-5"></i>
          </button>
          <button
            @click="makeAnEmptyAIMessage"
            class="svg-button text-red-400 hover:text-red-500"
            title="Insert an empty AI message"
          >
            <i data-feather="cpu" class="w-5 h-5"></i>
          </button>
           <button @click="toggleHelpModal" class="svg-button" title="Show Help">
              <i data-feather="info" class="w-5 h-5"></i>
          </button>
        </div>
        
          <!-- Right Panel Toggle -->
          <button
            @click="toggleRightPanel"
            class="svg-button"
            :class="$store.state.rightPanelCollapsed ? '' : 'bg-blue-300 dark:bg-blue-700'"
            :title="$store.state.rightPanelCollapsed ? 'Expand Right Panel' : 'Collapse Right Panel'"
          >
          <!-- Custom Icon for Right Panel Toggle -->
          <svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" class="w-5 h-5">
              <rect x="17" y="2" width="4" height="20" rx="2" fill="currentColor"/>
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
  <div v-if="showHelpModal" class="fixed inset-0 z-[100] flex items-center justify-center bg-black/70 backdrop-blur-sm">
    <div class="card max-w-xl w-full relative overflow-y-auto max-h-[80vh] scrollbar">
       <button
          @click="toggleHelpModal"
          class="svg-button absolute top-3 right-3 z-10"
          title="Close tutorial"
          >
          <i data-feather="x" class="w-6 h-6"></i>
      </button>
      <h2 class="text-2xl font-bold mb-4 text-center text-blue-700 dark:text-blue-200 border-b border-blue-300 dark:border-blue-600 pb-2">Chatbar Help</h2>

      <p class="mb-6 text-center text-blue-600 dark:text-blue-300">Overview of the chat controls:</p>
      <div class="space-y-3">
        <!-- Row 1 -->
        <div class="grid grid-cols-2 gap-3 items-center">
            <div class="flex items-center gap-3 p-2 rounded-lg bg-blue-100 dark:bg-blue-700/50">
              <button class="svg-button" disabled><i data-feather="send" class="w-5 h-5"></i></button>
              <span class="text-sm text-blue-700 dark:text-blue-200">Sends your message to the AI.</span>
            </div>
            <div class="flex items-center gap-3 p-2 rounded-lg bg-blue-100 dark:bg-blue-700/50">
              <button class="svg-button" disabled><i data-feather="globe" class="w-5 h-5"></i></button>
              <span class="text-sm text-blue-700 dark:text-blue-200">Sends your message with internet search.</span>
            </div>
        </div>
        <!-- Row 2 -->
        <div class="grid grid-cols-2 gap-3 items-center">
            <div class="flex items-center gap-3 p-2 rounded-lg bg-blue-100 dark:bg-blue-700/50">
               <button class="svg-button" disabled><svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" class="w-5 h-5"><rect x="3" y="2" width="4" height="20" rx="2" fill="currentColor"/><rect x="9" y="6" width="12" height="2" rx="1" fill="currentColor"/><rect x="9" y="11" width="12" height="2" rx="1" fill="currentColor"/><rect x="9" y="16" width="12" height="2" rx="1" fill="currentColor"/></svg></button>
               <span class="text-sm text-blue-700 dark:text-blue-200">Toggles the left panel.</span>
            </div>
            <div class="flex items-center gap-3 p-2 rounded-lg bg-blue-100 dark:bg-blue-700/50">
               <button class="svg-button" disabled><svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" class="w-5 h-5"><rect x="17" y="2" width="4" height="20" rx="2" fill="currentColor"/><rect x="3" y="6" width="12" height="2" rx="1" fill="currentColor"/><rect x="3" y="11" width="12" height="2" rx="1" fill="currentColor"/><rect x="3" y="16" width="12" height="2" rx="1" fill="currentColor"/></svg></button>
               <span class="text-sm text-blue-700 dark:text-blue-200">Toggles the right panel.</span>
            </div>
        </div>
        <!-- Row 3 -->
        <div class="grid grid-cols-2 gap-3 items-center">
            <div class="flex items-center gap-3 p-2 rounded-lg bg-blue-100 dark:bg-blue-700/50">
              <button class="svg-button" disabled><svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2a6 6 0 0 1 6 6c0 2.42-1.61 4.5-4 5.25V15a2 2 0 0 1-4 0v-1.75C7.61 12.5 6 10.42 6 8a6 6 0 0 1 6-6z" /><path d="M9 18h6" /> <path d="M10 22h4" /></svg></button>
              <span class="text-sm text-blue-700 dark:text-blue-200">Toggle 'Think First' mode.</span>
            </div>
            <div class="flex items-center gap-3 p-2 rounded-lg bg-blue-100 dark:bg-blue-700/50">
              <button class="svg-button" disabled><svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10" /> <path d="M8 14s1.5 2 4 2 4-2 4-2M9 9h.01M15 9h.01" /></svg></button>
              <span class="text-sm text-blue-700 dark:text-blue-200">Toggle 'Fun' mode.</span>
            </div>
        </div>
        <!-- Row 4 -->
         <div class="grid grid-cols-2 gap-3 items-center">
             <div class="flex items-center gap-3 p-2 rounded-lg bg-blue-100 dark:bg-blue-700/50">
              <button class="svg-button" disabled><i data-feather="mic" class="w-5 h-5"></i></button>
              <span class="text-sm text-blue-700 dark:text-blue-200">Activates voice input.</span>
            </div>
            <div class="flex items-center gap-3 p-2 rounded-lg bg-blue-100 dark:bg-blue-700/50">
              <button class="btn btn-sm p-1.5 bg-green-500 text-white" disabled><span class="text-xs font-bold">RT</span></button>
              <span class="text-sm text-blue-700 dark:text-blue-200">Toggles real-time audio mode.</span>
            </div>
        </div>
        <!-- Row 5 -->
        <div class="grid grid-cols-2 gap-3 items-center">
            <div class="flex items-center gap-3 p-2 rounded-lg bg-blue-100 dark:bg-blue-700/50">
              <button class="svg-button" disabled><i data-feather="plus-circle" class="w-5 h-5"></i></button>
              <span class="text-sm text-blue-700 dark:text-blue-200">More actions (Add File, etc.).</span>
            </div>
             <div class="flex items-center gap-3 p-2 rounded-lg bg-blue-100 dark:bg-blue-700/50">
              <button class="svg-button" disabled><i data-feather="message-circle" class="w-5 h-5"></i></button>
              <span class="text-sm text-blue-700 dark:text-blue-200">Inserts empty user message.</span>
            </div>
        </div>
         <!-- Row 6 -->
         <div class="grid grid-cols-2 gap-3 items-center">
             <div class="flex items-center gap-3 p-2 rounded-lg bg-blue-100 dark:bg-blue-700/50">
              <button class="svg-button text-red-400" disabled><i data-feather="cpu" class="w-5 h-5"></i></button>
              <span class="text-sm text-blue-700 dark:text-blue-200">Inserts empty AI message.</span>
            </div>
             <div class="flex items-center gap-3 p-2 rounded-lg bg-blue-100 dark:bg-blue-700/50">
              <button class="svg-button" disabled><i data-feather="info" class="w-5 h-5"></i></button>
              <span class="text-sm text-blue-700 dark:text-blue-200">Shows this help information.</span>
            </div>
         </div>

      </div>
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
        
        async showFunctionSettings(entry){
            const func = entry
            // Split the path by '/' and filter out empty segments
            let normalizedPath = func.dir.replace(/\\/g, '/');
            const segments = normalizedPath.split('/').filter(segment => segment !== '');
 
            // Get the parent folder name (second-to-last segment)
            const category = segments[segments.length - 2];
            try {
                this.isLoading = true
                axios.post('/get_function_call_settings',{client_id:this.$store.state.client_id,category:category,name:func.name}).then(res => {
                    this.isLoading = false
                    if (res) {
                        if (res.data && Object.keys(res.data).length > 0) {
                            // open form
                            this.$store.state.universalForm.showForm(res.data, "Function call settings - " +func.name, "Save changes", "Cancel").then(res => {
                                // send new data
                                try {
                                    axios.post('/set_function_call_settings',
                                        {client_id:this.$store.state.client_id,category:category,name:func.name, "settings":res}, {headers: this.posts_headers}).then(response => {
                                            if (response && response.data) {
                                                console.log('function call set with new settings', response.data)
                                                this.$store.state.toast.showToast("function call settings updated successfully!", 4, true)
                                            } else {
                                                this.$store.state.toast.showToast("Did not get function call settings responses.\n" + response, 4, false)
                                                this.isLoading = false
                                            }
                                        })
                                } catch (error) {
                                    this.$store.state.toast.showToast("Did not get function call settings responses.\n Endpoint error: " + error.message, 4, false)
                                    this.isLoading = false
                                }
                            })
                        } else {
                            this.$store.state.toast.showToast("Function call has no settings", 4, false)
                            this.isLoading = false
                        }

                    }
                })

            } catch (error) {
                this.isLoading = false
                this.$store.state.toast.showToast("Could not open function call settings. Endpoint error: " + error.message, 4, false)
            }

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
