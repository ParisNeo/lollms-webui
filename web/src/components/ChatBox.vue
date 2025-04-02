<template>
  <!-- Chatbar Container: Fixed, centered, and compact with theme styling -->
  <div
      class="chatbox-color fixed bottom-4 left-1/2 transform -translate-x-1/2 w-11/12 max-w-3xl p-3 bg-opacity-90 backdrop-blur-md rounded-xl border border-blue-300 dark:border-blue-700 shadow-lg transition-all duration-300 ease-in-out z-50"
  >
    <!-- Files Panel (if any files are attached) -->
    <div v-if="filesList.length > 0" class="mb-2 border-b border-blue-200 dark:border-blue-700 pb-2">
      <div class="flex items-center justify-between mb-1.5">
        <button
          class="svg-button p-1.5"
          :title="showfilesList ? 'Hide file list' : 'Show file list'"
          @click.stop="showfilesList = !showfilesList"
        >
          <i data-feather="list" class="w-4 h-4"></i>
        </button>
        <div class="flex items-center gap-1.5">
          <span class="text-xs text-blue-600 dark:text-blue-300" title="Total file size and number of files">
            {{ totalSize }} ({{ filesList.length }})
          </span>
          <button @click="clear_files" class="svg-button p-1 hover:text-red-500 dark:hover:text-red-400" title="Clear all files">
            <i data-feather="trash" class="w-3.5 h-3.5"></i>
          </button>
          <button @click="download_files" class="svg-button p-1 hover:text-blue-500 dark:hover:text-blue-400" title="Download all files">
            <i data-feather="download-cloud" class="w-3.5 h-3.5"></i>
          </button>
        </div>
      </div>
      <!-- Expandable files list -->
      <TransitionGroup
        v-show="showfilesList"
        name="list"
        tag="div"
        class="max-h-32 overflow-y-auto rounded-md bg-blue-100 dark:bg-blue-900 divide-y divide-blue-200 dark:divide-blue-700 scrollbar"
      >
        <div
          v-for="(file, index) in filesList"
          :key="index + '-' + file.name"
          class="flex items-center justify-between p-1.5 group hover:bg-blue-200 dark:hover:bg-blue-800 transition-colors duration-150"
        >
          <div class="flex items-center gap-1.5 min-w-0">
            <div v-if="!isFileSentList[index]" class="animate-spin flex-shrink-0" title="Uploading...">
              <i data-feather="loader" class="w-3.5 h-3.5 text-blue-500 dark:text-blue-400"></i>
            </div>
            <i data-feather="file" class="w-3.5 h-3.5 flex-shrink-0 text-blue-600 dark:text-blue-300" title="File"></i>
            <span
              class="truncate text-xs"
              :class="isFileSentList[index] ? 'text-green-600 dark:text-green-400' : 'text-blue-700 dark:text-blue-200'"
              :title="file.name"
            >
              {{ file.name }}
            </span>
          </div>
          <div class="flex items-center gap-1.5 flex-shrink-0">
            <span class="text-xs text-blue-500 dark:text-blue-400" :title="computedFileSize(file.size)">
              {{ computedFileSize(file.size) }}
            </span>
            <button
              @click="removeItem(file)"
              class="svg-button p-0.5 opacity-0 group-hover:opacity-100 hover:text-red-500 dark:hover:text-red-400 transition-all duration-150"
              title="Remove file"
            >
              <i data-feather="x" class="w-3.5 h-3.5"></i>
            </button>
          </div>
        </div>
      </TransitionGroup>
    </div>

    <!-- Main Chat Input and Actions -->
    <div class="flex flex-col gap-1.5">
      <div class="flex flex-row gap-1.5 w-full">

        <!-- Input Box with Integrated Send Buttons -->
        <div class="relative flex-grow">
            <textarea
                id="chat"
                :disabled="loading"
                v-model="message"
                @paste="handlePaste"
                @keydown.enter.exact="submitOnEnter($event)"
                rows="1"
                class="input w-full p-2.5 pr-20 text-sm rounded-lg focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400 border-blue-300 dark:border-blue-600 resize-y min-h-[2.75rem] max-h-28 overflow-auto transition-colors scrollbar text-blue-900 dark:text-blue-100 placeholder-blue-400 dark:placeholder-blue-500"
                placeholder="Write your message..."
                title="Enter your message here"
            ></textarea>
            <!-- Integrated Send Buttons inside the input box -->
            <div class="absolute inset-y-0 right-0 flex items-center pr-1.5 space-x-1">
                <template v-if="loading">
                    <button
                        @click="stopGenerating"
                        class="btn btn-sm bg-red-500 text-white hover:bg-red-600 focus:ring-red-300 dark:focus:ring-red-600 transform hover:scale-105 active:scale-95 transition-all duration-200 ease-in-out shadow-md hover:shadow-lg animate-pulse p-1.5"
                        title="Stop generating"
                        aria-label="Stop generation process"
                    >
                        <i data-feather="stop-circle" class="w-4 h-4 animate-spin-slow"></i>
                        <span class="sr-only">Stop</span>
                    </button>
                </template>
                <template v-else>
                    <button
                        @click="submit"
                        class="svg-button p-1.5"
                        title="Send message"
                    >
                        <i data-feather="send" class="w-4 h-4"></i>
                    </button>
                    <button
                        @click="submitWithInternetSearch"
                        class="svg-button p-1.5"
                        title="Send with internet search"
                    >
                        <i data-feather="globe" class="w-4 h-4"></i>
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
          class="svg-button p-1.5"
          :class="$store.state.leftPanelCollapsed ? '' : 'bg-blue-200 dark:bg-blue-700'"
          :title="$store.state.leftPanelCollapsed ? 'Expand Left Panel' : 'Collapse Left Panel'"
        >
          <!-- Custom Icon for Left Panel Toggle -->
          <svg width="20" height="20" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" class="w-4 h-4">
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
            size="small"
          />
          <PersonalitiesCommands
            v-if="isdataLakeNamesValid"
            :help="'Datalakes'"
            icon="feather:book"
            :commandsList="dataLakeNames"
            :sendCommand="mountDB"
            :on-show-toast-message="onShowToastMessage"
            ref="databasesList"
            size="small"
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
            size="small"
          />
        </div>

        <!-- Central Buttons: Modes -->
         <div class="flex items-center gap-1">
             <button
              @click="toggleThinkFirstMode"
              class="svg-button p-1.5"
              :class="{ 'text-blue-600 dark:text-blue-400 bg-blue-200 dark:bg-blue-700': $store.state.config.think_first_mode }"
              title="Toggle Think First Mode"
              >
              <!-- Bulb Icon -->
              <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M12 2a6 6 0 0 1 6 6c0 2.42-1.61 4.5-4 5.25V15a2 2 0 0 1-4 0v-1.75C7.61 12.5 6 10.42 6 8a6 6 0 0 1 6-6z" />
                  <path d="M9 18h6" /> <path d="M10 22h4" />
              </svg>
              </button>

             <button
                 @click="toggleFunMode"
                 class="svg-button p-1.5"
                 :class="{ 'text-blue-600 dark:text-blue-400 bg-blue-200 dark:bg-blue-700': $store.state.config.fun_mode }"
                 title="Toggle Fun Mode"
             >
                 <!-- Smiley Icon -->
                 <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                     <circle cx="12" cy="12" r="10" /> <path d="M8 14s1.5 2 4 2 4-2 4-2M9 9h.01M15 9h.01" />
                 </svg>
             </button>
          </div>

        <!-- Right Side: Additional Options -->
        <div class="flex items-center gap-1">
          <button
            @click="startSpeechRecognition"
            class="svg-button p-1.5"
            :class="{ 'text-red-500 dark:text-red-400 animate-pulse': isListeningToVoice }"
            title="Voice input"
          >
            <i data-feather="mic" class="w-4 h-4"></i>
          </button>
          <button
            v-if="$store.state.config.active_tts_service !== 'None' && $store.state.config.active_tts_service && $store.state.config.active_stt_service !== 'None'"
            @click="updateRT"
            class="btn btn-sm p-1"
            :class="is_rt ? 'bg-red-500 hover:bg-red-600 text-white' : 'bg-green-500 hover:bg-green-600 text-white'"
            title="Toggle real-time audio mode"
          >
            <span class="text-xs font-bold">RT</span> <!-- Using text instead of emoji for better control -->
          </button>
          <!-- More Actions Dropdown Trigger -->
          <button
            @click="toggleSendMenu"
            class="svg-button p-1.5"
            title="More actions (Add file, take picture, etc.)"
          >
            <i data-feather="plus-circle" class="w-4 h-4"></i>
          </button>
          <!-- Dropdown Menu for Extra Actions -->
          <div
            v-show="isSendMenuVisible"
            class="absolute right-0 bottom-full mb-1 w-44 bg-blue-100 dark:bg-blue-800 rounded-md shadow-lg border border-blue-300 dark:border-blue-600 z-10"
             @mouseleave="isSendMenuVisible=false"
          >
            <div class="p-1.5 space-y-1">
              <button
                @click="add_file"
                class="w-full p-1.5 flex items-center gap-1.5 rounded-md hover:bg-blue-200 dark:hover:bg-blue-700 transition-colors text-blue-700 dark:text-blue-200"
                title="Add a file"
              >
                <i data-feather="file-plus" class="w-3.5 h-3.5"></i>
                <span class="text-xs">Add File</span>
              </button>
              <button
                @click="takePicture"
                class="w-full p-1.5 flex items-center gap-1.5 rounded-md hover:bg-blue-200 dark:hover:bg-blue-700 transition-colors text-blue-700 dark:text-blue-200"
                title="Take a picture"
              >
                <i data-feather="camera" class="w-3.5 h-3.5"></i>
                <span class="text-xs">Take Picture</span>
              </button>
              <button
                @click="addWebLink"
                class="w-full p-1.5 flex items-center gap-1.5 rounded-md hover:bg-blue-200 dark:hover:bg-blue-700 transition-colors text-blue-700 dark:text-blue-200"
                title="Add a web link"
              >
                <i data-feather="link" class="w-3.5 h-3.5"></i>
                <span class="text-xs">Add Web Link</span>
              </button>
            </div>
          </div>
          <button
            @click="makeAnEmptyUserMessage"
            class="svg-button p-1.5"
            title="Insert an empty user message"
          >
            <i data-feather="message-circle" class="w-4 h-4"></i>
          </button>
          <button
            @click="makeAnEmptyAIMessage"
            class="svg-button p-1.5 text-red-400 hover:text-red-500 dark:hover:text-red-400"
            title="Insert an empty AI message"
          >
            <i data-feather="cpu" class="w-4 h-4"></i>
          </button>
           <button @click="toggleHelpModal" class="svg-button p-1.5" title="Show Help">
              <i data-feather="info" class="w-4 h-4"></i>
          </button>
        </div>

          <!-- Right Panel Toggle -->
          <button
            @click="toggleRightPanel"
            class="svg-button p-1.5"
            :class="$store.state.rightPanelCollapsed ? '' : 'bg-blue-200 dark:bg-blue-700'"
            :title="$store.state.rightPanelCollapsed ? 'Expand Right Panel' : 'Collapse Right Panel'"
          >
          <!-- Custom Icon for Right Panel Toggle -->
          <svg width="20" height="20" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" class="w-4 h-4">
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
  <input type="file" ref="fileDialog" @change="addFiles($event.target.files)" multiple class="hidden" />

  <!-- Tutorial Help Overlay -->
  <div v-if="showHelpModal" class="fixed inset-0 z-[100] flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
    <div class="card max-w-lg w-full relative overflow-y-auto max-h-[85vh] scrollbar p-4 md:p-6">
       <button
          @click="toggleHelpModal"
          class="svg-button absolute top-2 right-2 z-10"
          title="Close tutorial"
          >
          <i data-feather="x" class="w-5 h-5"></i>
      </button>
      <h2 class="text-xl md:text-2xl font-bold mb-3 text-center text-blue-700 dark:text-blue-200 border-b border-blue-300 dark:border-blue-600 pb-2">Chatbar Help</h2>

      <p class="mb-4 text-center text-sm md:text-base text-blue-600 dark:text-blue-300">Overview of the chat controls:</p>
      <div class="space-y-2.5">
        <!-- Row 1 -->
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-2.5 items-center">
            <div class="flex items-center gap-2 p-2 rounded-lg bg-blue-100 dark:bg-blue-800/70">
              <button class="svg-button p-1.5" disabled><i data-feather="send" class="w-4 h-4"></i></button>
              <span class="text-xs md:text-sm text-blue-700 dark:text-blue-200">Sends your message to the AI.</span>
            </div>
            <div class="flex items-center gap-2 p-2 rounded-lg bg-blue-100 dark:bg-blue-800/70">
              <button class="svg-button p-1.5" disabled><i data-feather="globe" class="w-4 h-4"></i></button>
              <span class="text-xs md:text-sm text-blue-700 dark:text-blue-200">Sends your message with internet search.</span>
            </div>
        </div>
        <!-- Row 2 -->
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-2.5 items-center">
            <div class="flex items-center gap-2 p-2 rounded-lg bg-blue-100 dark:bg-blue-800/70">
               <button class="svg-button p-1.5" disabled><svg width="20" height="20" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" class="w-4 h-4"><rect x="3" y="2" width="4" height="20" rx="2" fill="currentColor"/><rect x="9" y="6" width="12" height="2" rx="1" fill="currentColor"/><rect x="9" y="11" width="12" height="2" rx="1" fill="currentColor"/><rect x="9" y="16" width="12" height="2" rx="1" fill="currentColor"/></svg></button>
               <span class="text-xs md:text-sm text-blue-700 dark:text-blue-200">Toggles the left panel visibility.</span>
            </div>
            <div class="flex items-center gap-2 p-2 rounded-lg bg-blue-100 dark:bg-blue-800/70">
               <button class="svg-button p-1.5" disabled><svg width="20" height="20" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" class="w-4 h-4"><rect x="17" y="2" width="4" height="20" rx="2" fill="currentColor"/><rect x="3" y="6" width="12" height="2" rx="1" fill="currentColor"/><rect x="3" y="11" width="12" height="2" rx="1" fill="currentColor"/><rect x="3" y="16" width="12" height="2" rx="1" fill="currentColor"/></svg></button>
               <span class="text-xs md:text-sm text-blue-700 dark:text-blue-200">Toggles the right panel visibility.</span>
            </div>
        </div>
        <!-- Row 3 -->
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-2.5 items-center">
            <div class="flex items-center gap-2 p-2 rounded-lg bg-blue-100 dark:bg-blue-800/70">
              <button class="svg-button p-1.5" disabled><svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2a6 6 0 0 1 6 6c0 2.42-1.61 4.5-4 5.25V15a2 2 0 0 1-4 0v-1.75C7.61 12.5 6 10.42 6 8a6 6 0 0 1 6-6z" /><path d="M9 18h6" /> <path d="M10 22h4" /></svg></button>
              <span class="text-xs md:text-sm text-blue-700 dark:text-blue-200">Toggle 'Think First' mode (AI processes before replying).</span>
            </div>
            <div class="flex items-center gap-2 p-2 rounded-lg bg-blue-100 dark:bg-blue-800/70">
              <button class="svg-button p-1.5" disabled><svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10" /> <path d="M8 14s1.5 2 4 2 4-2 4-2M9 9h.01M15 9h.01" /></svg></button>
              <span class="text-xs md:text-sm text-blue-700 dark:text-blue-200">Toggle 'Fun' mode (adds playful elements).</span>
            </div>
        </div>
        <!-- Row 4 -->
         <div class="grid grid-cols-1 sm:grid-cols-2 gap-2.5 items-center">
             <div class="flex items-center gap-2 p-2 rounded-lg bg-blue-100 dark:bg-blue-800/70">
              <button class="svg-button p-1.5" disabled><i data-feather="mic" class="w-4 h-4"></i></button>
              <span class="text-xs md:text-sm text-blue-700 dark:text-blue-200">Activates voice input for your message.</span>
            </div>
            <div class="flex items-center gap-2 p-2 rounded-lg bg-blue-100 dark:bg-blue-800/70">
              <button class="btn btn-sm p-1 bg-green-500 text-white" disabled><span class="text-xs font-bold">RT</span></button>
              <span class="text-xs md:text-sm text-blue-700 dark:text-blue-200">Toggles real-time audio conversation mode.</span>
            </div>
        </div>
        <!-- Row 5 -->
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-2.5 items-center">
            <div class="flex items-center gap-2 p-2 rounded-lg bg-blue-100 dark:bg-blue-800/70">
              <button class="svg-button p-1.5" disabled><i data-feather="plus-circle" class="w-4 h-4"></i></button>
              <span class="text-xs md:text-sm text-blue-700 dark:text-blue-200">Shows more actions (Add File, Picture, Link).</span>
            </div>
             <div class="flex items-center gap-2 p-2 rounded-lg bg-blue-100 dark:bg-blue-800/70">
              <button class="svg-button p-1.5" disabled><i data-feather="message-circle" class="w-4 h-4"></i></button>
              <span class="text-xs md:text-sm text-blue-700 dark:text-blue-200">Inserts an empty user message bubble.</span>
            </div>
        </div>
         <!-- Row 6 -->
         <div class="grid grid-cols-1 sm:grid-cols-2 gap-2.5 items-center">
             <div class="flex items-center gap-2 p-2 rounded-lg bg-blue-100 dark:bg-blue-800/70">
              <button class="svg-button p-1.5 text-red-500 dark:text-red-400" disabled><i data-feather="cpu" class="w-4 h-4"></i></button>
              <span class="text-xs md:text-sm text-blue-700 dark:text-blue-200">Inserts an empty AI message bubble.</span>
            </div>
             <div class="flex items-center gap-2 p-2 rounded-lg bg-blue-100 dark:bg-blue-800/70">
              <button class="svg-button p-1.5" disabled><i data-feather="info" class="w-4 h-4"></i></button>
              <span class="text-xs md:text-sm text-blue-700 dark:text-blue-200">Shows this help information modal.</span>
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

/* Reduce default size for PersonalitiesCommands when size="small" */
:deep(.personalities-commands-container[data-size="small"]) .svg-button {
  @apply p-1.5;
}
:deep(.personalities-commands-container[data-size="small"]) .svg-button svg,
:deep(.personalities-commands-container[data-size="small"]) .svg-button i {
  @apply w-4 h-4;
}
:deep(.personalities-commands-container[data-size="small"]) .context-menu {
  @apply text-xs; /* Smaller text in dropdown */
}
:deep(.personalities-commands-container[data-size="small"]) .context-menu-item {
  @apply px-3 py-1.5; /* Tighter padding in dropdown */
}
:deep(.personalities-commands-container[data-size="small"]) .context-menu-item-icon {
  @apply w-3.5 h-3.5 mr-1.5; /* Smaller icons in dropdown */
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

const bUrl = ""// import.meta.env.VITE_LOLLMS_API_BASEURL

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
            recognition: null, // Added for speech recognition instance
            silenceTimer: null, // Added for speech recognition silence detection
            silenceTimeoutDuration: 3000, // milliseconds of silence before stopping
            recognitionError: false, // Flag for speech recognition errors
            filesList: [],
            isFileSentList: [],
            totalSize: "0 B", // Initialize with a default value
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
            return Array.isArray(this.dataLakeNames) && this.dataLakeNames.length > 0;
        },
        isCommandsValid() {
            const activePersonality = this.$store.state.mountedPersArr[this.$store.state.config.active_personality_id];
            // Ensure activePersonality exists before accessing commands
            return activePersonality && Array.isArray(activePersonality.commands) && activePersonality.commands.length > 0;
        },
        dataLakeNames() {
            // Map datalakes only if the array exists
            const formattedDataSources = (this.$store.state.config.datalakes || []).map(dataLake => {
                return {
                    name: dataLake.alias,
                    value: dataLake.alias || 'default_value', // Ensure value is always set
                    is_checked: dataLake.mounted,
                    icon: '', // Consider adding icons if available
                    help: 'mounts the datalake ' + dataLake.alias
                };
            });
            return formattedDataSources;
        },
        functionCalls(){
             // Map function calls only if the array exists
            const formattedFunctionCalls = (this.$store.state.config.mounted_function_calls || []).map(functionCall => {
                return {
                    name: functionCall.name,
                    value: functionCall, // Pass the whole object if needed by toggleFunctionCall
                    dir: functionCall.dir,
                    is_checked: functionCall.selected,
                    icon: functionCall.icon || 'feather:zap', // Default icon if none provided
                    help: functionCall.help || `Toggles the function call ${functionCall.name}`
                };
            });
            return formattedFunctionCalls;
        }

    },
    methods: {
        toggleThinkFirstMode() {
            this.$store.state.config.think_first_mode = !this.$store.state.config.think_first_mode

            this.$store.state.applyConfiguration()
            // Save configuration might be better handled centrally after applyConfiguration succeeds
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
            // Consider using mouseleave on the menu itself instead of timeout
            this.hideSendMenuTimeout = setTimeout(() => {
                this.isSendMenuVisible = false;
            }, 300);
        },

        toggleLeftPanel(){
            this.$store.commit('setLeftPanelCollapsed', !this.$store.state.leftPanelCollapsed);
        },
        async toggleRightPanel(){
            this.$store.commit('setRightPanelCollapsed', !this.$store.state.rightPanelCollapsed);
            // Consider if extractHtml is needed here or handled elsewhere based on collapse state
            if(!this.$store.state.rightPanelCollapsed){
                // Assuming extractHtml is a method in this component or globally available
                // this.extractHtml() // Example call
            }
        },

        handlePaste(event) {
            const items = (event.clipboardData || event.originalEvent.clipboardData).items;
            let filesToUpload = [];
            for (let item of items) {
                if (item.type.startsWith("image/")) { // More robust image check
                    const blob = item.getAsFile();
                     if (blob) {
                        const uniqueId = Date.now() + '_' + Math.random().toString(36).substr(2, 9);
                        // Try to preserve original extension or default to png
                        const extension = blob.type.split('/')[1] || 'png';
                        const newFileName = `pasted_image_${uniqueId}.${extension}`;
                        const newFile = new File([blob], newFileName, {type: blob.type});
                        filesToUpload.push(newFile); // Add to list to be processed by addFiles
                     }
                }
                else if (item.kind === 'file') {
                    const file = item.getAsFile();
                    if(file){ // Ensure getAsFile() returned something
                        filesToUpload.push(file);
                    }
                }
            }
            if (filesToUpload.length > 0) {
                this.addFiles(filesToUpload); // Process all collected files
            }
        },
        emitloaded(){
            this.$emit('loaded')
        },
        download_files(){
             // This likely needs the discussion ID or some identifier
             // Example: axios.get(`/download_files?discussion_id=${this.$store.state.currentDiscussionId}`)
            axios.get('/download_files').then(response => {
                // Handle download response, e.g., trigger browser download
                 const url = window.URL.createObjectURL(new Blob([response.data]));
                 const link = document.createElement('a');
                 link.href = url;
                 // Extract filename from Content-Disposition header if available
                 const contentDisposition = response.headers['content-disposition'];
                 let filename = 'discussion_files.zip'; // Default filename
                 if (contentDisposition) {
                    const filenameMatch = contentDisposition.match(/filename="?(.+)"?/i);
                    if (filenameMatch && filenameMatch.length === 2)
                      filename = filenameMatch[1];
                  }
                 link.setAttribute('download', filename);
                 document.body.appendChild(link);
                 link.click();
                 document.body.removeChild(link); // Clean up
                 window.URL.revokeObjectURL(url); // Clean up blob URL
            }).catch(error => {
                console.error("Error downloading files:", error);
                 this.$store.state.toast.showToast("Error downloading files.",4,false);
            });
        },
        async remove_file(file) {
            try {
                // Use POST as it modifies server state
                const response = await axios.post('/remove_discussion_file', {
                    client_id: this.$store.state.client_id,
                    name: file.name,
                    // discussion_id: this.$store.state.currentDiscussionId // Important: Identify which discussion
                }, { headers: this.posts_headers });

                console.log("remove_discussion_file:");
                console.log(response.data);

                if (response.data.status) {
                    const index = this.filesList.findIndex(f => f.name === file.name);
                    if (index !== -1) {
                        this.filesList.splice(index, 1);
                        this.isFileSentList.splice(index, 1);
                    }
                    this.$store.state.toast.showToast("File removed.", 4, true);
                } else {
                    this.$store.state.toast.showToast(`Could not remove file: ${response.data.error || 'Unknown reason'}`, 4, false);
                }
            } catch (error) {
                console.error("Error removing file:", error);
                this.$store.state.toast.showToast(`Error removing file: ${error.message}`, 4, false);
            }
        },
        clear_files(){
            axios.post('/clear_discussion_files_list', {
                client_id: this.$store.state.client_id,
                // discussion_id: this.$store.state.currentDiscussionId // Important
                }, { headers: this.posts_headers }).then(res => {
                if(res.data.state){ // Assuming 'state' means success
                    this.$store.state.toast.showToast("All files removed.",4,true);
                    this.filesList = []; // Clear arrays directly
                    this.isFileSentList = [];
                    // recalculateTotalSize will set totalSize to 0
                }
                else{
                    this.$store.state.toast.showToast(`Files couldn't be cleared: ${res.data.error || 'Unknown reason'}`,4,false);
                }
            }).catch(error => {
                 console.error("Error clearing files:", error);
                 this.$store.state.toast.showToast(`Error clearing files: ${error.message}`, 4, false);
            });

        },
        send_file(file, next_callback) { // Renamed callback for clarity
            console.log(`Starting send_file for ${file.name}`);
            const fileReader = new FileReader();
            const chunkSize = 1024 * 1024; // 1MB chunk size - adjust as needed
            let offset = 0;
            let chunkIndex = 0;
             // Find index reliably BEFORE async operations start
            const fileIndexInList = this.filesList.findIndex(f => f === file);
            if (fileIndexInList === -1) {
                 console.error(`File ${file.name} not found in filesList during send_file start.`);
                 // Optionally call next_callback() here if you want the queue to continue
                 // next_callback();
                 return; // Stop processing this file
             }


            fileReader.onload = () => { // Use onload for successful reads
                if (fileReader.result) {
                    const chunk = fileReader.result; // ArrayBuffer
                    const isLastChunk = offset + chunk.byteLength >= file.size;
                    console.log(`Sending chunk ${chunkIndex} for ${file.name}, size: ${chunk.byteLength}, isLast: ${isLastChunk}`);
                    socket.emit('send_file_chunk', {
                        client_id: this.$store.state.client_id, // Send client_id with chunk
                        // discussion_id: this.$store.state.currentDiscussionId, // Send discussion_id
                        filename: file.name,
                        chunk: chunk, // Send ArrayBuffer directly
                        offset: offset,
                        isLastChunk: isLastChunk,
                        chunkIndex: chunkIndex // Useful for server-side ordering if needed
                    });
                    offset += chunk.byteLength;
                    chunkIndex++;
                    if (!isLastChunk) {
                        readNextChunk();
                    } else {
                        console.log(`File ${file.name} sent successfully`);
                         // Check index validity again *before* updating state
                         if (fileIndexInList < this.isFileSentList.length && this.isFileSentList[fileIndexInList] === false) {
                             this.isFileSentList[fileIndexInList] = true;
                             // Trigger reactivity explicitly if direct modification doesn't work
                             // this.$set(this.isFileSentList, fileIndexInList, true);
                         } else {
                              console.warn(`Could not mark file ${file.name} as sent - index ${fileIndexInList} out of bounds or already true.`);
                         }
                         this.$store.state.toast.showToast(`${file.name} uploaded.`,4,true);
                        next_callback(); // Signal that this file is done, process next
                    }
                } else {
                    console.error('Error reading file chunk (result is null):', file.name);
                    // Handle error - maybe stop queue or notify user?
                     this.$store.state.toast.showToast(`Error reading ${file.name}.`,4,false);
                     // Decide if you should call next_callback() to continue with other files
                     // next_callback();
                }
            };

             fileReader.onerror = (error) => {
                 console.error(`Error reading file ${file.name}:`, error);
                 this.$store.state.toast.showToast(`Error reading ${file.name}. Upload failed.`, 4, false);
                 // Decide whether to proceed with the queue or stop
                 // next_callback(); // Call if you want to try the next file anyway
             };

            function readNextChunk() {
                console.log(`Reading chunk starting at offset ${offset} for ${file.name}`);
                const blob = file.slice(offset, offset + chunkSize);
                fileReader.readAsArrayBuffer(blob);
            }
            console.log(`Initiating upload for ${file.name}`);
            readNextChunk(); // Start reading the first chunk
        },
        makeAnEmptyUserMessage() {
            this.$emit('createEmptyUserMessage', this.message) // Pass current input if needed?
            this.message = "" // Clear input after emitting
        },
        makeAnEmptyAIMessage() {
            this.$emit('createEmptyAIMessage')
        },
        toggleSendMenu() {
            this.isSendMenuVisible = !this.isSendMenuVisible;
        },
        toggleHelpModal() {
            this.showHelpModal = !this.showHelpModal;
            this.$nextTick(() => {
                feather.replace(); // Ensure icons are rendered in the modal
            });
        },
        updateRT() {
            if(this.is_rt){
                this.stopRTCom();
            }
            else{
                this.startRTCom();
            }
        },
        startRTCom(){
             if(this.$store.state.config.active_tts_service === 'None' || !this.$store.state.config.active_tts_service || this.$store.state.config.active_stt_service === 'None'){
                 this.$store.state.toast.showToast("TTS and STT services must be configured for Real-Time mode.",4,false);
                 return;
             }
            this.is_rt = true
            socket.emit('start_bidirectional_audio_stream',{client_id: this.$store.state.client_id});
             this.$store.state.toast.showToast("Real-time mode activated.",4,true);
            // No need for feather.replace here, icon class is reactive
        },
        stopRTCom(){
            this.is_rt = false
            socket.emit('stop_bidirectional_audio_stream',{client_id: this.$store.state.client_id});
             this.$store.state.toast.showToast("Real-time mode deactivated.",4,true);
            // No need for feather.replace here
        },
        startSpeechRecognition() {
            if (!('SpeechRecognition' in window || 'webkitSpeechRecognition' in window)) {
                 console.error('Speech recognition is not supported in this browser.');
                 this.$store.state.toast.showToast("Speech recognition is not supported in this browser.",4,false);
                 return;
             }
             if (this.isListeningToVoice) {
                 console.log('Speech recognition already active, stopping...');
                 this.recognition.stop(); // Stop existing session if button is clicked again
                 clearTimeout(this.silenceTimer);
                 this.isListeningToVoice = false;
                 return;
             }

             try{
                 const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
                 this.recognition = new SpeechRecognition();
                 // Ensure language config exists and is valid, otherwise use browser default
                 this.recognition.lang = this.$store.state.config?.audio_in_language || navigator.language;
                 this.recognition.interimResults = true;
                 this.recognition.continuous = false; // Process single utterances

                 this.recognitionError = false; // Reset error flag

                 this.recognition.onstart = () => {
                     console.log('Speech recognition started.');
                     this.isListeningToVoice = true;
                     this.resetSilenceTimer(); // Start silence timer
                 };

                 this.recognition.onresult = (event) => {
                     this.resetSilenceTimer(); // Reset timer on any result

                     let interimTranscript = '';
                     let finalTranscript = '';
                     for (let i = event.resultIndex; i < event.results.length; ++i) {
                         if (event.results[i].isFinal) {
                             finalTranscript += event.results[i][0].transcript;
                         } else {
                             interimTranscript += event.results[i][0].transcript;
                         }
                     }
                     this.message = finalTranscript + interimTranscript; // Update textarea
                 };

                 this.recognition.onerror = (event) => {
                     console.error('Speech recognition error:', event.error);
                      this.recognitionError = true; // Set error flag
                     let errorMessage = event.error;
                     if(event.error === 'no-speech') {
                         errorMessage = "No speech detected. Please try again.";
                     } else if (event.error === 'audio-capture') {
                         errorMessage = "Microphone error. Check permissions and hardware.";
                     } else if (event.error === 'not-allowed') {
                         errorMessage = "Microphone access denied. Please allow access in browser settings.";
                     } else {
                          errorMessage = `Speech recognition error: ${event.error}`;
                     }
                      this.$store.state.toast.showToast(errorMessage, 4, false);
                      // Don't call stop() here, onend will handle cleanup
                 };

                 this.recognition.onend = () => {
                     console.log('Speech recognition ended.');
                     this.isListeningToVoice = false;
                     clearTimeout(this.silenceTimer);
                      // Only submit if there was a final message and no critical error occurred
                     if (this.message.trim() && !this.recognitionError) {
                         this.submit();
                     } else if (this.recognitionError && this.message.trim()) {
                         // Maybe keep the message in the input if there was an error?
                         console.log("Recognition ended with error, message kept in input:", this.message);
                     } else {
                         // Clear message if recognition ends with no speech or just interim results
                         // this.message = ""; // Optional: clear message if nothing final was recognized
                     }
                 };

                 this.recognition.start();

             } catch(e) {
                 console.error("Error initializing SpeechRecognition:", e);
                 this.$store.state.toast.showToast("Could not start voice input.", 4, false);
                 this.isListeningToVoice = false; // Ensure state is correct
             }
        },
        resetSilenceTimer() {
            clearTimeout(this.silenceTimer);
            this.silenceTimer = setTimeout(() => {
                if (this.isListeningToVoice && this.recognition) {
                    console.log('Silence detected, stopping recognition.');
                    this.recognition.stop();
                }
            }, this.silenceTimeoutDuration);
        },
        computedFileSize(size) {
             // Use the imported filesize function
             // Provide options for clarity and standard units (optional)
             return filesize(size, { base: 2, standard: "iec" }); // e.g., KiB, MiB
        },

        removeItem(file) {
             // Call the existing remove_file method which handles API call and list update
             this.remove_file(file);
        },
        sendMessageEvent(msg, type = "no_internet") {
            const trimmedMsg = msg.trim();
            if (trimmedMsg !== '') {
                this.$emit('messageSentEvent', trimmedMsg, type);
                // Clear message only after successful emit? Or handle in parent?
                // this.message = ""; // Keep message clearing consistent
            } else {
                 this.$store.state.toast.showToast("Cannot send empty message.",4,false);
            }
        },
        sendCMDEvent(cmd){
             // Ensure cmd is valid before emitting
            if(cmd && cmd.value){
                 this.$emit('sendCMDEvent', cmd);
             } else {
                  console.warn("Attempted to send invalid command:", cmd);
             }
        },
        async mountDB(cmdName){ // cmd should be the name (value) from the list item
            console.log("Toggling datalake mount for:", cmdName)
            if (!cmdName) {
                 console.error("Mount DB command name is missing.");
                 return;
             }
             // Find the original datalake object to get its current state
             const dataLake = this.$store.state.config.datalakes.find(dl => dl.alias === cmdName);
             const initiallyMounted = dataLake ? dataLake.mounted : false;

             // Optimistic UI update (optional, but provides faster feedback)
             const index = this.dataLakeNames.findIndex(dl => dl.name === cmdName);
             if (index !== -1) {
                this.dataLakeNames[index].is_checked = !initiallyMounted;
             }


            try{
                await axios.post('/toggle_mount_rag_database', {
                     client_id: this.$store.state.client_id,
                     datalake_name: cmdName
                     // discussion_id: this.$store.state.currentDiscussionId // If needed by backend
                     }, {headers: this.posts_headers})
                // Refresh config from server to get the definite state
                await this.$store.dispatch('refreshConfig');
                 this.$store.state.toast.showToast(`Datalake ${cmdName} ${!initiallyMounted ? 'mounted' : 'unmounted'}.`, 4, true);
                console.log("Datalake toggle successful, config refreshed.")

            }catch(error){
                 console.error("Error toggling datalake:", error);
                 this.$store.state.toast.showToast(`Error toggling datalake ${cmdName}.`,4,false);
                 // Revert optimistic UI update on failure
                 if (index !== -1) {
                    this.dataLakeNames[index].is_checked = initiallyMounted;
                 }
                 // Optionally refresh config again to be safe
                 // await this.$store.dispatch('refreshConfig');
            }

        },

        async showFunctionSettings(funcValue){ // Use the value (original object) passed
            const func = funcValue; // func is the original function call object
             if (!func || !func.dir || !func.name) {
                console.error("Invalid function data for settings:", func);
                return;
             }
            console.log("Showing settings for function:", func.name, "in category:", func.dir);

            // Normalize path and extract category (assuming dir structure like 'parent/func_folder')
            let normalizedPath = func.dir.replace(/\\/g, '/');
            const segments = normalizedPath.split('/').filter(segment => segment !== '');
            // Adjust index based on your actual directory structure if needed
            const category = segments.length > 1 ? segments[segments.length - 2] : 'unknown';
            console.log("Determined category:", category);


            try {
                this.isLoading = true; // Consider adding a local isLoading state for the chatbox
                const response = await axios.post('/get_function_call_settings',{
                    client_id: this.$store.state.client_id,
                    category: category,
                    name: func.name
                    }, {headers: this.posts_headers});

                this.isLoading = false;
                if (response.data && Object.keys(response.data).length > 0) {
                    // Use the universal form provided by the store
                     this.$store.state.universalForm.showForm(
                         response.data, // Form definition from backend
                         `Settings: ${func.name}`, // Title
                         "Save Changes", // Submit button text
                         "Cancel" // Cancel button text
                     ).then(formData => {
                         // This promise resolves when the user submits the form
                         console.log("Saving function call settings:", formData);
                         axios.post('/set_function_call_settings', {
                             client_id: this.$store.state.client_id,
                             category: category,
                             name: func.name,
                             settings: formData // Send the updated settings
                         }, { headers: this.posts_headers }).then(setResponse => {
                             if (setResponse.data && setResponse.data.status === 'success') { // Check for explicit success status
                                 this.$store.state.toast.showToast(`Settings for ${func.name} updated.`, 4, true);
                                 // Optionally refresh config if settings affect backend state immediately
                                 // this.$store.dispatch('refreshConfig');
                             } else {
                                 this.$store.state.toast.showToast(`Failed to save settings: ${setResponse.data?.error || 'Unknown error'}`, 4, false);
                             }
                         }).catch(setError => {
                              console.error("Error setting function call settings:", setError);
                              this.$store.state.toast.showToast(`Error saving settings: ${setError.message}`, 4, false);
                         });
                     }).catch(() => {
                          // This catch block executes if the user cancels the form
                          console.log("Function settings form cancelled.");
                     });
                } else {
                     this.$store.state.toast.showToast(`${func.name} has no configurable settings.`, 4, true); // Use 'true' for info toast
                }

            } catch (error) {
                this.isLoading = false;
                console.error("Could not get function call settings:", error);
                this.$store.state.toast.showToast(`Error fetching settings for ${func.name}.`, 4, false);
            }

        },
        async toggleFunctionCall(funcValue){ // Use the value (original object)
            const func = funcValue;
             if (!func || !func.dir || !func.name) {
                console.error("Invalid function data for toggle:", func);
                return;
             }
            console.log("Toggling function call:", func.name);

             const initiallySelected = func.is_checked; // Use the checked state from the computed property

             // Optimistic UI Update
             const index = this.functionCalls.findIndex(fc => fc.value === funcValue); // Find by the value object
             if (index !== -1) {
                 this.functionCalls[index].is_checked = !initiallySelected;
             }


            try {
                 await axios.post('/toggle_function_call', {
                     client_id: this.$store.state.client_id,
                     name: func.name,
                     dir: func.dir,
                      // discussion_id: this.$store.state.currentDiscussionId // If needed
                 }, {headers: this.posts_headers});

                 // Refresh config to get the true state from the server
                 await this.$store.dispatch('refreshConfig');
                  this.$store.state.toast.showToast(`Function call ${func.name} ${!initiallySelected ? 'enabled' : 'disabled'}.`, 4, true);
                 console.log("Function call toggle successful, config refreshed.");
             } catch (error) {
                 console.error("Error toggling function call:", error);
                 this.$store.state.toast.showToast(`Error toggling ${func.name}.`, 4, false);
                 // Revert optimistic update on failure
                 if (index !== -1) {
                     this.functionCalls[index].is_checked = initiallySelected;
                 }
                 // Optionally refresh config again
                 // await this.$store.dispatch('refreshConfig');
             }
        },

        addWebLink(){
            this.isSendMenuVisible = false;
            this.$emit('addWebLink') // Emit event for parent component to handle
        },
        add_file(){
            this.isSendMenuVisible = false;
            // Trigger the hidden file input
            this.$refs.fileDialog.click();
       },
        takePicture(){
            this.isSendMenuVisible = false;
            // Emit request to backend via socket
            socket.emit('take_picture', { client_id: this.$store.state.client_id });
             this.$store.state.toast.showToast("Requesting picture...", 4, true);
            // Listener for 'picture_taken' is in mounted()
        },
        submitOnEnter(event) {
            // Submit on Enter press, allow Shift+Enter for newline
            if (event.key === 'Enter' && !event.shiftKey && !this.loading) {
                event.preventDefault(); // Prevent newline in textarea
                if (!event.repeat) { // Avoid multiple submits if key is held down
                    this.sendMessageEvent(this.message);
                    this.message = ""; // Clear input after sending
                }
            } else if (event.key === 'Enter' && this.loading){
                 event.preventDefault(); // Prevent newline even when loading
                 this.$store.state.toast.showToast("Please wait for the current response.",4,false);
            }
        },
        submit() {
            if (this.loading) {
                 this.$store.state.toast.showToast("Please wait for the current response.",4,false);
                 return;
             }
            this.sendMessageEvent(this.message);
            if (this.message.trim() !== '') { // Clear only if message was actually sent
                 this.message = "";
             }
        },
        submitWithInternetSearch(){
            if (this.loading) {
                 this.$store.state.toast.showToast("Please wait for the current response.",4,false);
                 return;
             }
            this.sendMessageEvent(this.message, "internet"); // Pass type='internet'
            if (this.message.trim() !== '') {
                 this.message = "";
             }
        },
        stopGenerating() {
            this.$emit('stopGenerating') // Emit event for parent component
        },
        // --- Corrected addFiles Method ---
        addFiles(files) {
            // Check if 'files' is valid and not empty
            if (!files || files.length === 0) {
                console.warn("addFiles called with invalid or empty files:", files);
                // Optionally show a user message if appropriate, or just return
                // this.$store.state.toast.showToast("No files selected or invalid input.", 4, false);
                return;
            }

            console.log("Attempting to add files:", files); // Log what is received

            let newFilesArray;
            try {
                 // Use Array.from() for robust conversion from FileList or other iterables/array-likes
                newFilesArray = Array.from(files);
            } catch (e) {
                console.error("Error converting files to array:", e);
                this.$store.state.toast.showToast("Error processing selected files.", 4, false);
                return; // Stop execution if conversion fails
            }

            console.log("Successfully converted to array:", newFilesArray);

            let currentFileIndex = 0;

            const processNextFile = () => {
                if (currentFileIndex >= newFilesArray.length) {
                    console.log("All files processed.");
                    this.recalculateTotalSize(); // Update total size after processing all
                    return;
                }

                const file = newFilesArray[currentFileIndex];

                // Basic check if file is valid
                if (!file || typeof file.name === 'undefined' || typeof file.size === 'undefined') {
                    console.warn(`Skipping invalid file object at index ${currentFileIndex}:`, file);
                    this.$store.state.toast.showToast(`Skipped an invalid file entry.`, 4, false);
                    currentFileIndex++;
                    processNextFile(); // Skip to the next file
                    return;
                }


                // Check if file already exists (by name and size)
                if (!this.filesList.some(existingFile => existingFile.name === file.name && existingFile.size === file.size)) {
                    this.filesList.push(file);
                    this.isFileSentList.push(false); // Mark as not sent initially

                    // Call send_file for the current file, passing the callback to process next
                    this.send_file(file, () => {
                         console.log(`Callback after send_file for ${file.name}.`);
                         currentFileIndex++; // Increment index ONLY after successful send callback
                         processNextFile(); // Process the next file
                    });
                } else {
                    console.log(`File ${file.name} already exists, skipping.`);
                    this.$store.state.toast.showToast(`File ${file.name} already added.`, 4, false);
                    currentFileIndex++;
                    processNextFile(); // Skip to the next file
                }
            };

            processNextFile(); // Start processing the first file
        },
        // --- End of Corrected addFiles Method ---
        recalculateTotalSize() {
            let total = 0;
            this.filesList.forEach(file => {
                // Ensure size is a number before adding
                if (typeof file.size === 'number') {
                     total += file.size;
                 }
            });
            // Update totalSize using the filesize function for formatting
            this.totalSize = this.computedFileSize(total); // Use the computedFileSize for consistent formatting
        }

    },
    watch: {
        // Watch the filesList array for changes (additions/removals)
        filesList: {
            handler(newList, oldList) {
                // console.log("filesList changed, recalculating size.", newList);
                this.recalculateTotalSize();
                // Ensure icons are up-to-date when the list changes (e.g., removing items)
                 nextTick(() => { feather.replace() });
            },
            deep: true // Necessary for watching changes within the array items
        },
        // Watch the individual isFileSentList items for changes
         isFileSentList: {
            handler(newList, oldList) {
                 // This watcher might be less critical now that send_file updates state directly,
                 // but keep it if you need to react to the 'sent' status changing visually beyond the icon class.
                 // console.log("isFileSentList changed.", newList);
                 nextTick(() => { feather.replace() }); // Update icons if needed
            },
            deep: true
        },
        loading(newval) {
            // Update icons when loading state changes (e.g., send button/stop button)
            nextTick(() => {
                feather.replace()
            })
        },
        isSendMenuVisible(newVal){
             // Ensure icons in the dropdown menu are rendered correctly when it becomes visible
             if (newVal) {
                 nextTick(() => {
                    feather.replace()
                });
             }
        },
        // Watch relevant parts of the config that affect the chatbar UI directly
        '$store.state.config.active_personality_id': function() {
             nextTick(() => { feather.replace() }); // Update command list icons/buttons if needed
        },
        '$store.state.config.datalakes': { // Watch deeply for changes within the datalakes array
            handler() {
                 nextTick(() => { feather.replace() }); // Update datalake command list
            },
            deep: true
        },
        '$store.state.config.mounted_function_calls': { // Watch deeply for function call changes
            handler() {
                 nextTick(() => { feather.replace() }); // Update function call list
            },
            deep: true
        },
        '$store.state.config.think_first_mode': function() {
             // Update think first button style reactively (handled by :class binding)
             // nextTick(() => { feather.replace() }); // Feather replace unlikely needed here
        },
         '$store.state.config.fun_mode': function() {
             // Update fun mode button style reactively (handled by :class binding)
             // nextTick(() => { feather.replace() }); // Feather replace unlikely needed here
        },
        // Watch panel collapsed states to update toggle button styles
        '$store.state.leftPanelCollapsed': function() {
             // Button style updated by :class binding
        },
        '$store.state.rightPanelCollapsed': function() {
            // Button style updated by :class binding
        },
         // Watch RT status from store for the button text/style
         '$store.state.is_rt_on': function(newValue) {
            this.is_rt = newValue;
         }
    },
    mounted() {
        this.emitloaded(); // Signal component is loaded
        nextTick(() => {
            feather.replace() // Initial icon rendering
        });
        console.log("Chatbar mounted");

        // --- Socket Listeners ---
        // Listener for Real-Time Communication status changes
        socket.on('rtcom_status_changed', (data)=>{
             // Dispatch action to update the store, which then updates local 'is_rt' via watcher
            this.$store.dispatch('fetchisRTOn');
            console.log("rtcom_status_changed received:", data.status);
        });

        // Listener for when a picture is successfully taken and available
        socket.on('picture_taken', (data) => { // Assuming backend sends file info
            console.log("Picture taken event received", data);
            if(data && data.client_id === this.$store.state.client_id && data.file){
                const newFile = data.file; // Assuming backend sends { name: '...', size: ... } etc.
                 // Check if file already exists in the list before adding
                 if (!this.filesList.some(f => f.name === newFile.name)) {
                     this.filesList.push(newFile);
                     this.isFileSentList.push(true); // Assume sent as it came from backend event
                     this.$store.state.toast.showToast("Picture added successfully!", 4, true);
                 } else {
                      console.log("Picture file already in list, skipping add.");
                 }
                 // Recalculate size is handled by the filesList watcher
            } else {
                 console.warn("Picture taken event received, but data is missing or not for this client.", data);
                 // Optionally, fetch the full file list if backend doesn't send file info
                 // axios.post('/get_discussion_files_list', { "client_id": this.$store.state.client_id }).then(...)
            }
        });
        // --- End Socket Listeners ---

        // Fetch initial RT status when component mounts
        this.$store.dispatch('fetchisRTOn').then(()=>{
            this.is_rt = this.$store.state.is_rt_on; // Set initial local state
        });

        // Initial calculation of total file size
        this.recalculateTotalSize();

         // Add listener for window resize to potentially adjust layout if needed (optional)
         // window.addEventListener('resize', this.handleResize);
    },
    beforeUnmount() {
        console.log("Chatbar beforeUnmount: Cleaning up...");
        // Clean up socket listeners to prevent memory leaks
        socket.off('rtcom_status_changed');
        socket.off('picture_taken');

        // Stop speech recognition if it's active
        if (this.recognition && this.isListeningToVoice) {
            this.recognition.abort(); // Use abort() for immediate stop without triggering 'onend' logic fully
            this.isListeningToVoice = false; // Ensure state is reset
        }
        clearTimeout(this.silenceTimer); // Clear any pending silence timers

         // Remove window event listeners if added
         // window.removeEventListener('resize', this.handleResize);
    },
    activated() {
        // This lifecycle hook is for components inside <keep-alive>
        console.log("Chatbar activated");
        nextTick(() => {
            feather.replace() // Re-render icons if component was kept alive
        });
        // Recalculate size when component is activated (e.g., switching tabs in keep-alive)
        this.recalculateTotalSize();
         // Re-fetch RT status in case it changed while inactive
         this.$store.dispatch('fetchisRTOn').then(()=>{
             this.is_rt = this.$store.state.is_rt_on;
         });
    },
    deactivated() {
         // This lifecycle hook is for components inside <keep-alive>
         console.log("Chatbar deactivated");
         // Optional: Clean up things that should only run when active
         if (this.recognition && this.isListeningToVoice) {
             this.recognition.abort();
             this.isListeningToVoice = false;
         }
         clearTimeout(this.silenceTimer);
    }
}
</script>