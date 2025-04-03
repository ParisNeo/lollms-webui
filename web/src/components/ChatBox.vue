<template>
    <div>
      <Transition
          name="shrink-fade"
          enter-active-class="transition ease-out duration-300"
          enter-from-class="transform opacity-0 scale-50"
          enter-to-class="transform opacity-100 scale-100"
          leave-active-class="transition ease-in duration-200"
          leave-from-class="transform opacity-100 scale-100"
          leave-to-class="transform opacity-0 scale-50"
      >
        <button
          v-if="isShrunk"
          @click="toggleShrink"
          class="fixed bottom-4 right-4 z-[60] p-3 bg-blue-500 dark:bg-blue-600 text-white rounded-full shadow-lg hover:bg-blue-600 dark:hover:bg-blue-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-400 dark:focus:ring-offset-gray-900 animate-heartbeat"
          title="Expand Chat"
          aria-label="Expand Chat"
        >
          <i data-feather="message-square" class="w-6 h-6"></i>
        </button>
      </Transition>

      <Transition
          name="chatbar-fade-scale"
          enter-active-class="transition ease-out duration-300"
          enter-from-class="transform opacity-0 scale-95 translate-y-4"
          enter-to-class="transform opacity-100 scale-100 translate-y-0"
          leave-active-class="transition ease-in duration-200"
          leave-from-class="transform opacity-100 scale-100 translate-y-0"
          leave-to-class="transform opacity-0 scale-95 translate-y-4"
      >
        <div
          v-if="!isShrunk"
          ref="chatbarRef"
          :class="[
            'chatbox-color fixed w-11/12 max-w-3xl bg-opacity-90 backdrop-blur-md rounded-xl border border-blue-300 dark:border-blue-700 shadow-lg transition-shadow duration-300 ease-in-out z-50', // Removed overflow-hidden
            !isPositionModified ? 'bottom-4 left-1/2 transform -translate-x-1/2' : '',
            isDragging ? 'cursor-grabbing' : ''
          ]"
          :style="chatbarStyle"
        >
          <div
            class="flex items-center justify-between h-7 px-2 bg-blue-100/80 dark:bg-blue-900/70 border-b border-blue-300 dark:border-blue-600 hover:bg-blue-200/90 dark:hover:bg-blue-800/90 transition-colors duration-150 rounded-t-xl"
            :class="[ isDragging ? 'cursor-grabbing' : 'cursor-grab' ]"
            @mousedown.prevent="onMouseDown"
          >
            <span class="text-xs font-medium text-blue-700 dark:text-blue-300 select-none">Chat</span>
            <button
                @click.stop="toggleShrink"
                class="svg-button p-1 rounded-full hover:bg-blue-300 dark:hover:bg-blue-700"
                title="Shrink Chat"
                @mousedown.stop
            >
                <i data-feather="minus" class="w-4 h-4"></i>
            </button>
          </div>

          <div class="p-3 rounded-b-xl">
              <div v-if="filesList.length > 0" class="mb-2 border-b border-blue-200 dark:border-blue-700 pb-2" @mousedown.stop>
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
                    <button @click.stop="clear_files" class="svg-button p-1 hover:text-red-500 dark:hover:text-red-400" title="Clear all files">
                      <i data-feather="trash" class="w-3.5 h-3.5"></i>
                    </button>
                    <button @click.stop="download_files" class="svg-button p-1 hover:text-blue-500 dark:hover:text-blue-400" title="Download all files">
                      <i data-feather="download-cloud" class="w-3.5 h-3.5"></i>
                    </button>
                  </div>
                </div>
                <TransitionGroup
                  v-show="showfilesList"
                  name="list"
                  tag="div"
                  class="max-h-32 overflow-y-auto rounded-md bg-blue-100 dark:bg-blue-900 divide-y divide-blue-200 dark:divide-blue-700 scrollbar"
                >
                  <div
                    v-for="(file, index) in filesList"
                    :key="file.name + '-' + file.lastModified + '-' + file.size"
                    class="flex items-center justify-between p-1.5 group hover:bg-blue-200 dark:hover:bg-blue-800 transition-colors duration-150"
                  >
                    <div class="flex items-center gap-1.5 min-w-0">
                      <div v-if="!isFileSentList[index]" class="animate-spin flex-shrink-0" title="Uploading...">
                        <i data-feather="loader" class="w-3.5 h-3.5 text-blue-500 dark:text-blue-400"></i>
                      </div>
                      <i v-else data-feather="file" class="w-3.5 h-3.5 flex-shrink-0 text-blue-600 dark:text-blue-300" title="File"></i>
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
                        @click.stop="removeItem(file)"
                        class="svg-button p-0.5 opacity-0 group-hover:opacity-100 hover:text-red-500 dark:hover:text-red-400 transition-all duration-150"
                        title="Remove file"
                      >
                        <i data-feather="x" class="w-3.5 h-3.5"></i>
                      </button>
                    </div>
                  </div>
                </TransitionGroup>
              </div>

              <div class="flex flex-col gap-1.5" @mousedown.stop>
                <div class="flex flex-row gap-1.5 w-full">
                  <div class="relative flex-grow">
                      <textarea
                          id="chat"
                          ref="textareaRef"
                          :disabled="loading"
                          v-model="message"
                          @paste="handlePaste"
                          @keydown.enter.exact="submitOnEnter($event)"
                          rows="1"
                          class="input w-full p-2.5 pr-28 text-sm rounded-lg focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400 border-blue-300 dark:border-blue-600 resize-y min-h-[2.75rem] max-h-28 overflow-auto transition-colors scrollbar text-blue-900 dark:text-blue-100 placeholder-blue-400 dark:placeholder-blue-500"
                          placeholder="Write your message..."
                          title="Enter your message here"
                      ></textarea>
                      <!-- Popover outside clipping context now -->
                      <div v-if="showEmojiPicker" class="absolute bottom-full right-0 mb-1 z-20" v-click-outside="closeEmojiPicker">
                          <EmojiPicker :native="true" @select="onEmojiSelect" />
                      </div>
                      <div class="absolute inset-y-0 right-0 flex items-center pr-1.5 space-x-1">
                          <button @click.stop="toggleEmojiPicker" class="svg-button p-1.5" title="Add emoji">
                              <i data-feather="smile" class="w-4 h-4"></i>
                          </button>
                          <template v-if="loading">
                              <button
                                  @click.stop="stopGenerating"
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
                                  @click.stop="submit"
                                  class="svg-button p-1.5"
                                  title="Send message"
                              >
                                  <i data-feather="send" class="w-4 h-4"></i>
                              </button>
                              <button
                                  @click.stop="submitWithInternetSearch"
                                  class="svg-button p-1.5"
                                  title="Send with internet search"
                              >
                                  <i data-feather="globe" class="w-4 h-4"></i>
                              </button>
                          </template>
                      </div>
                  </div>
                </div>

                <div class="flex items-center justify-between relative">
                  <button
                    @click.stop="toggleLeftPanel"
                    class="svg-button p-1.5"
                    :class="$store.state.leftPanelCollapsed ? '' : 'bg-blue-200 dark:bg-blue-700'"
                    :title="$store.state.leftPanelCollapsed ? 'Expand Left Panel' : 'Collapse Left Panel'"
                  >
                    <svg width="20" height="20" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" class="w-4 h-4">
                        <rect x="3" y="2" width="4" height="20" rx="2" fill="currentColor"/>
                        <rect x="9" y="6" width="12" height="2" rx="1" fill="currentColor"/>
                        <rect x="9" y="11" width="12" height="2" rx="1" fill="currentColor"/>
                        <rect x="9" y="16" width="12" height="2" rx="1" fill="currentColor"/>
                    </svg>
                  </button>

                  <div class="flex items-center gap-1">
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

                   <div class="flex items-center gap-1">
                       <button
                        @click.stop="toggleThinkFirstMode"
                        class="svg-button p-1.5"
                        :class="{ 'text-blue-600 dark:text-blue-400 bg-blue-200 dark:bg-blue-700': $store.state.config.think_first_mode }"
                        title="Toggle Think First Mode"
                        >
                        <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M12 2a6 6 0 0 1 6 6c0 2.42-1.61 4.5-4 5.25V15a2 2 0 0 1-4 0v-1.75C7.61 12.5 6 10.42 6 8a6 6 0 0 1 6-6z" />
                            <path d="M9 18h6" /> <path d="M10 22h4" />
                        </svg>
                        </button>
                       <button
                           @click.stop="toggleFunMode"
                           class="svg-button p-1.5"
                           :class="{ 'text-blue-600 dark:text-blue-400 bg-blue-200 dark:bg-blue-700': $store.state.config.fun_mode }"
                           title="Toggle Fun Mode"
                       >
                           <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                               <circle cx="12" cy="12" r="10" /> <path d="M8 14s1.5 2 4 2 4-2 4-2M9 9h.01M15 9h.01" />
                           </svg>
                       </button>
                    </div>

                  <div class="flex items-center gap-1">
                    <button
                      @click.stop="startSpeechRecognition"
                      class="svg-button p-1.5"
                      :class="{ 'text-red-500 dark:text-red-400 animate-pulse': isListeningToVoice }"
                      title="Voice input"
                    >
                      <i data-feather="mic" class="w-4 h-4"></i>
                    </button>
                    <button
                      v-if="$store.state.config.active_tts_service !== 'None' && $store.state.config.active_tts_service && $store.state.config.active_stt_service !== 'None'"
                      @click.stop="updateRT"
                      class="btn btn-sm p-1"
                      :class="is_rt ? 'bg-red-500 hover:bg-red-600 text-white' : 'bg-green-500 hover:bg-green-600 text-white'"
                      title="Toggle real-time audio mode"
                    >
                      <span class="text-xs font-bold">RT</span>
                    </button>
                    <button
                      @click.stop="toggleSendMenu"
                      class="svg-button p-1.5"
                      title="More actions (Add file, take picture, etc.)"
                    >
                      <i data-feather="plus-circle" class="w-4 h-4"></i>
                    </button>
                     <!-- Popover outside clipping context now -->
                    <div
                      v-show="isSendMenuVisible"
                      class="absolute right-0 bottom-full mb-1 w-44 bg-blue-100 dark:bg-blue-800 rounded-md shadow-lg border border-blue-300 dark:border-blue-600 z-10"
                       @mouseleave="closeSendMenu" @mousedown.stop
                    >
                      <div class="p-1.5 space-y-1">
                        <button
                          @click.stop="add_file"
                          class="w-full p-1.5 flex items-center gap-1.5 rounded-md hover:bg-blue-200 dark:hover:bg-blue-700 transition-colors text-blue-700 dark:text-blue-200"
                          title="Add a file"
                        >
                          <i data-feather="file-plus" class="w-3.5 h-3.5"></i>
                          <span class="text-xs">Add File</span>
                        </button>
                        <button
                          @click.stop="takePicture"
                          class="w-full p-1.5 flex items-center gap-1.5 rounded-md hover:bg-blue-200 dark:hover:bg-blue-700 transition-colors text-blue-700 dark:text-blue-200"
                          title="Take a picture"
                        >
                          <i data-feather="camera" class="w-3.5 h-3.5"></i>
                          <span class="text-xs">Take Picture</span>
                        </button>
                        <button
                          @click.stop="addWebLink"
                          class="w-full p-1.5 flex items-center gap-1.5 rounded-md hover:bg-blue-200 dark:hover:bg-blue-700 transition-colors text-blue-700 dark:text-blue-200"
                          title="Add a web link"
                        >
                          <i data-feather="link" class="w-3.5 h-3.5"></i>
                          <span class="text-xs">Add Web Link</span>
                        </button>
                      </div>
                    </div>
                    <button
                      @click.stop="makeAnEmptyUserMessage"
                      class="svg-button p-1.5"
                      title="Insert an empty user message"
                    >
                      <i data-feather="message-circle" class="w-4 h-4"></i>
                    </button>
                    <button
                      @click.stop="makeAnEmptyAIMessage"
                      class="svg-button p-1.5 text-red-400 hover:text-red-500 dark:hover:text-red-400"
                      title="Insert an empty AI message"
                    >
                      <i data-feather="cpu" class="w-4 h-4"></i>
                    </button>
                     <button @click.stop="toggleHelpModal" class="svg-button p-1.5" title="Show Help">
                        <i data-feather="info" class="w-4 h-4"></i>
                    </button>
                  </div>

                  <button
                      @click.stop="toggleRightPanel"
                      class="svg-button p-1.5"
                      :class="$store.state.rightPanelCollapsed ? '' : 'bg-blue-200 dark:bg-blue-700'"
                      :title="$store.state.rightPanelCollapsed ? 'Expand Right Panel' : 'Collapse Right Panel'"
                    >
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
        </div>
      </Transition>
    </div>

    <input type="file" ref="fileDialog" @change="addFilesFromInput($event.target.files)" multiple class="hidden" />

    <div v-if="showHelpModal" class="fixed inset-0 z-[100] flex items-center justify-center bg-black/70 backdrop-blur-sm p-4" @click="toggleHelpModal">
      <div class="card max-w-lg w-full relative overflow-y-auto max-h-[85vh] scrollbar p-4 md:p-6" @click.stop>
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
           <div class="grid grid-cols-1 sm:grid-cols-2 gap-2.5 items-center">
              <div class="flex items-center gap-2 p-2 rounded-lg bg-blue-100 dark:bg-blue-800/70">
                <button class="svg-button p-1.5" disabled><i data-feather="smile" class="w-4 h-4"></i></button>
                <span class="text-xs md:text-sm text-blue-700 dark:text-blue-200">Opens the emoji picker.</span>
              </div>
              <div class="flex items-center gap-2 p-2 rounded-lg bg-blue-100 dark:bg-blue-800/70">
                 <button class="svg-button p-1.5" disabled><i data-feather="minus" class="w-4 h-4"></i></button>
                 <span class="text-xs md:text-sm text-blue-700 dark:text-blue-200">Shrinks the chatbar.</span>
              </div>
           </div>
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
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-2.5 items-center">
              <div class="flex items-center gap-2 p-2 rounded-lg bg-blue-100 dark:bg-blue-800/70">
                <button class="svg-button p-1.5" disabled><svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2a6 6 0 0 1 6 6c0 2.42-1.61 4.5-4 5.25V15a2 2 0 0 1-4 0v-1.75C7.61 12.5 6 10.42 6 8a6 6 0 0 1 6-6z" /><path d="M9 18h6" /> <path d="M10 22h4" /></svg></button>
                <span class="text-xs md:text-sm text-blue-700 dark:text-blue-200">Toggle 'Think First' mode.</span>
              </div>
              <div class="flex items-center gap-2 p-2 rounded-lg bg-blue-100 dark:bg-blue-800/70">
                <button class="svg-button p-1.5" disabled><svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10" /> <path d="M8 14s1.5 2 4 2 4-2 4-2M9 9h.01M15 9h.01" /></svg></button>
                <span class="text-xs md:text-sm text-blue-700 dark:text-blue-200">Toggle 'Fun' mode.</span>
              </div>
          </div>
           <div class="grid grid-cols-1 sm:grid-cols-2 gap-2.5 items-center">
               <div class="flex items-center gap-2 p-2 rounded-lg bg-blue-100 dark:bg-blue-800/70">
                <button class="svg-button p-1.5" disabled><i data-feather="mic" class="w-4 h-4"></i></button>
                <span class="text-xs md:text-sm text-blue-700 dark:text-blue-200">Activates voice input.</span>
              </div>
              <div class="flex items-center gap-2 p-2 rounded-lg bg-blue-100 dark:bg-blue-800/70">
                <button class="btn btn-sm p-1 bg-green-500 text-white" disabled><span class="text-xs font-bold">RT</span></button>
                <span class="text-xs md:text-sm text-blue-700 dark:text-blue-200">Toggles real-time audio mode.</span>
              </div>
          </div>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-2.5 items-center">
              <div class="flex items-center gap-2 p-2 rounded-lg bg-blue-100 dark:bg-blue-800/70">
                <button class="svg-button p-1.5" disabled><i data-feather="plus-circle" class="w-4 h-4"></i></button>
                <span class="text-xs md:text-sm text-blue-700 dark:text-blue-200">Shows more actions menu.</span>
              </div>
               <div class="flex items-center gap-2 p-2 rounded-lg bg-blue-100 dark:bg-blue-800/70">
                <button class="svg-button p-1.5" disabled><i data-feather="message-circle" class="w-4 h-4"></i></button>
                <span class="text-xs md:text-sm text-blue-700 dark:text-blue-200">Inserts empty user message.</span>
              </div>
          </div>
           <div class="grid grid-cols-1 sm:grid-cols-2 gap-2.5 items-center">
               <div class="flex items-center gap-2 p-2 rounded-lg bg-blue-100 dark:bg-blue-800/70">
                <button class="svg-button p-1.5 text-red-500 dark:text-red-400" disabled><i data-feather="cpu" class="w-4 h-4"></i></button>
                <span class="text-xs md:text-sm text-blue-700 dark:text-blue-200">Inserts empty AI message.</span>
              </div>
               <div class="flex items-center gap-2 p-2 rounded-lg bg-blue-100 dark:bg-blue-800/70">
                <button class="svg-button p-1.5" disabled><i data-feather="info" class="w-4 h-4"></i></button>
                <span class="text-xs md:text-sm text-blue-700 dark:text-blue-200">Shows this help modal.</span>
              </div>
           </div>
           <div class="grid grid-cols-1 gap-2.5 items-center">
               <div class="flex items-center gap-2 p-2 rounded-lg bg-blue-100 dark:bg-blue-800/70">
                <button class="svg-button p-1.5 cursor-grab" disabled><i data-feather="move" class="w-4 h-4"></i></button>
                <span class="text-xs md:text-sm text-blue-700 dark:text-blue-200">Click and drag the header bar to move the chatbox.</span>
              </div>
           </div>
        </div>
      </div>
    </div>
</template>


<style scoped>
  @keyframes spin-slow {
      from { transform: rotate(0deg); }
      to { transform: rotate(360deg); }
  }
  .animate-spin-slow { animation: spin-slow 3s linear infinite; }

  @keyframes heartbeat {
    0% { transform: scale(1); box-shadow: 0 0 0 0 rgba(37, 99, 235, 0.5); }
    50% { transform: scale(1.05); box-shadow: 0 0 0 8px rgba(37, 99, 235, 0); }
    100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(37, 99, 235, 0); }
  }
  .animate-heartbeat { animation: heartbeat 1.5s ease-in-out infinite; }

  .scrollbar {
    scrollbar-width: thin;
    scrollbar-color: rgba(155, 155, 155, 0.5) transparent;
  }
  .scrollbar::-webkit-scrollbar { width: 6px; }
  .scrollbar::-webkit-scrollbar-track { background: transparent; }
  .scrollbar::-webkit-scrollbar-thumb {
    background-color: rgba(155, 155, 155, 0.5);
    border-radius: 20px;
    border: transparent;
  }

  .list-move, .list-enter-active, .list-leave-active { transition: all 0.5s ease; }
  .list-enter-from { opacity: 0; transform: translateY(-30px); }
  .list-leave-to { opacity: 0; transform: translateY(30px); }
  .list-leave-active { position: absolute; width: calc(100% - 1.5rem); }


  :deep(.personalities-commands-container[data-size="small"]) .svg-button { @apply p-1.5; }
  :deep(.personalities-commands-container[data-size="small"]) .svg-button svg,
  :deep(.personalities-commands-container[data-size="small"]) .svg-button i { @apply w-4 h-4; }
  :deep(.personalities-commands-container[data-size="small"]) .context-menu { @apply text-xs; }
  :deep(.personalities-commands-container[data-size="small"]) .context-menu-item { @apply px-3 py-1.5; }
  :deep(.personalities-commands-container[data-size="small"]) .context-menu-item-icon { @apply w-3.5 h-3.5 mr-1.5; }

  .cursor-grabbing { cursor: grabbing; }
  .user-select-none { user-select: none; -webkit-user-select: none; -moz-user-select: none; -ms-user-select: none; }

  :deep(.v3-emoji-picker) { }
  .dark :deep(.v3-emoji-picker) { }
</style>

<script>
import { nextTick } from 'vue'
import axios from "axios";
import feather from 'feather-icons'
import filesize from '../plugins/filesize'
import PersonalitiesCommands from '@/components/PersonalitiesCommands.vue';
import socket from '@/services/websocket.js'
import EmojiPicker from 'vue3-emoji-picker'
import 'vue3-emoji-picker/css'

const clickOutside = {
  beforeMount(el, binding) {
    el.clickOutsideEvent = function(event) {
      if (!(el === event.target || el.contains(event.target))) {
         if (binding.arg) {
           let excluded = false;
           try {
             const excludedElements = Array.isArray(binding.arg) ? binding.arg : [binding.arg];
             excluded = excludedElements.some(excludedEl => {
               const targetEl = excludedEl.value || excludedEl;
               return targetEl && (targetEl === event.target || targetEl.contains(event.target));
             });
           } catch (e) { console.error("Error in clickOutside directive arg:", e); }
           if (excluded) return;
         }
        binding.value(event);
      }
    };
    document.body.addEventListener('mousedown', el.clickOutsideEvent, true);
  },
  unmounted(el) {
    document.body.removeEventListener('mousedown', el.clickOutsideEvent, true);
  },
};


const bUrl = ""

export default {
    name: 'ChatBox',
    emits: ["messageSentEvent", "sendCMDEvent", "stopGenerating", "loaded", "createEmptyUserMessage", "createEmptyAIMessage", "personalitySelected","addWebLink"],
    props: {
        onTalk: Function,
        discussionList: Array,
        loading: { default: false },
        onShowToastMessage: Function
    },
    directives: {
        clickOutside
    },
    components: {
        PersonalitiesCommands,
        EmojiPicker
    },
    data() {
        return {
            message: "",
            isSendMenuVisible: false,
            is_rt: false,
            isListeningToVoice: false,
            recognition: null,
            silenceTimer: null,
            silenceTimeoutDuration: 3000,
            recognitionError: false,
            filesList: [],
            isFileSentList: [],
            totalSize: "0 B",
            showfilesList: true,
            showHelpModal: false,
            showEmojiPicker: false,
            isDragging: false,
            isPositionModified: false,
            startDragPos: { x: 0, y: 0 },
            startChatboxPos: { x: 0, y: 0 },
            currentChatboxPos: null,
            isShrunk: false,
            posts_headers: {
                'accept': 'application/json',
                'Content-Type': 'application/json'
            }
        }
    },
    computed: {
        chatbarStyle() {
            if (this.isPositionModified && this.currentChatboxPos) {
                return {
                    transform: `translate(${this.currentChatboxPos.x}px, ${this.currentChatboxPos.y}px)`,
                    left: '0px',
                    top: '0px',
                    bottom: 'auto',
                    'margin-left': '0px',
                    'transform-origin': 'top left',
                };
            }
            return {};
        },
        isCompactMode() {
            return this.$store.state.view_mode === 'compact';
        },
        isdataLakeNamesValid() {
            return Array.isArray(this.dataLakeNames) && this.dataLakeNames.length > 0;
        },
        isCommandsValid() {
            const activePers = this.$store.state.mountedPersArr[this.$store.state.config.active_personality_id];
            return activePers && Array.isArray(activePers.commands) && activePers.commands.length > 0;
        },
        dataLakeNames() {
            return (this.$store.state.config.datalakes || []).map(dl => ({
                name: dl.alias,
                value: dl.alias || 'default_value',
                is_checked: dl.mounted,
                icon: '',
                help: 'Mounts the datalake ' + dl.alias
            }));
        },
        functionCalls() {
            return (this.$store.state.config.mounted_function_calls || []).map(fc => ({
                name: fc.name,
                value: fc,
                dir: fc.dir,
                is_checked: fc.selected,
                icon: fc.icon || 'feather:zap',
                help: fc.help || `Toggles the function call ${fc.name}`
            }));
        }
    },
    methods: {
        updateFeatherIcons() {
            nextTick(() => {
                try {
                    feather.replace();
                } catch (e) {
                    console.error("Feather error:", e);
                }
            });
        },
        toggleShrink() {
            this.isShrunk = !this.isShrunk;
            localStorage.setItem('chatbarShrunk', JSON.stringify(this.isShrunk));
            this.updateFeatherIcons();
        },
        onMouseDown(event) {
            if (event.button !== 0 || this.isShrunk) return;

            this.isDragging = true;
            document.body.classList.add('user-select-none');

            this.startDragPos = { x: event.clientX, y: event.clientY };

            const chatbarElement = this.$refs.chatbarRef;
            if (!chatbarElement) return;

            const rect = chatbarElement.getBoundingClientRect();

             if (!this.isPositionModified) {
                 this.currentChatboxPos = { x: rect.left, y: rect.top };
                 this.isPositionModified = true;
             }

             if (!this.currentChatboxPos) {
                this.currentChatboxPos = { x: rect.left, y: rect.top };
             }

             this.startChatboxPos = { ...this.currentChatboxPos };

            window.addEventListener('mousemove', this.onMouseMove);
            window.addEventListener('mouseup', this.onMouseUp);
            window.addEventListener('mouseleave', this.onMouseLeave);
        },
        onMouseMove(event) {
            if (!this.isDragging || !this.$refs.chatbarRef) return;
            event.preventDefault();

            const dx = event.clientX - this.startDragPos.x;
            const dy = event.clientY - this.startDragPos.y;

            this.currentChatboxPos = {
                x: this.startChatboxPos.x + dx,
                y: this.startChatboxPos.y + dy,
            };
        },
        onMouseUp() {
            if (!this.isDragging) return;

            this.isDragging = false;
            document.body.classList.remove('user-select-none');

            window.removeEventListener('mousemove', this.onMouseMove);
            window.removeEventListener('mouseup', this.onMouseUp);
            window.removeEventListener('mouseleave', this.onMouseLeave);

            if (this.isPositionModified && this.currentChatboxPos) {
                localStorage.setItem('chatbarPosition', JSON.stringify(this.currentChatboxPos));
                localStorage.setItem('chatbarPositionModified', 'true');
            }
        },
        onMouseLeave(event){
            if (this.isDragging) {
                this.onMouseUp();
            }
        },
        toggleEmojiPicker() {
            this.showEmojiPicker = !this.showEmojiPicker;
        },
        closeEmojiPicker() {
             if (this.showEmojiPicker) {
                this.showEmojiPicker = false;
             }
        },
        onEmojiSelect(emoji) {
            this.insertEmojiAtCursor(emoji.i);
            this.closeEmojiPicker();
            this.$refs.textareaRef?.focus();
        },
        insertEmojiAtCursor(emoji) {
            const textarea = this.$refs.textareaRef;
            if (!textarea) return;
            const start = textarea.selectionStart;
            const end = textarea.selectionEnd;
            const text = this.message;
            this.message = text.substring(0, start) + emoji + text.substring(end);
            nextTick(() => {
                if(textarea) {
                    textarea.selectionStart = textarea.selectionEnd = start + emoji.length;
                }
            });
        },
        computedFileSize(size) {
             if (typeof size !== 'number') return 'N/A';
             return filesize(size, { base: 2, standard: "iec" });
        },
        recalculateTotalSize() {
            let total = 0;
            this.filesList.forEach(file => {
                 if (file && typeof file.size === 'number') {
                     total += file.size;
                 }
            });
            this.totalSize = this.computedFileSize(total);
        },
        addFilesFromInput(filesFromDialog) {
            if (filesFromDialog && filesFromDialog.length > 0) {
                this.addFiles(filesFromDialog);
            }
             if (this.$refs.fileDialog) {
                this.$refs.fileDialog.value = '';
            }
        },
        addFiles(filesToAdd) {
             if (!filesToAdd || filesToAdd.length === 0) {
                 return;
             }
             let newFilesArray;
             try {
                 newFilesArray = Array.from(filesToAdd);
             } catch (e) {
                 this.onShowToastMessage("Error processing selected files.", 4, false);
                 return;
             }
             let fileAdded = false;
             newFilesArray.forEach(file => {
                 if (!file || typeof file.name === 'undefined' || typeof file.size === 'undefined') {
                     this.onShowToastMessage(`Skipped an invalid file entry.`, 4, false);
                     return;
                 }
                 const isDuplicate = this.filesList.some(existingFile =>
                     existingFile.name === file.name && existingFile.size === file.size
                 );
                 if (!isDuplicate) {
                    const fileIndex = this.filesList.length;
                    this.filesList.push(file);
                    this.isFileSentList.push(false);
                    this.send_file(file, fileIndex);
                    fileAdded = true;
                 } else {
                     this.onShowToastMessage(`File ${file.name} already added.`, 4, false);
                 }
             });
             if (fileAdded) {
                 this.updateFeatherIcons();
             }
        },
        send_file(file, fileIndexInList) {
             const fileReader = new FileReader();
             const chunkSize = 1024 * 1024;
             let offset = 0;
             let chunkIndex = 0;
             const totalChunks = Math.ceil(file.size / chunkSize);

             fileReader.onload = () => {
                 if (fileReader.result) {
                     const chunk = fileReader.result;
                     const isLastChunk = offset + chunk.byteLength >= file.size;
                     socket.emit('send_file_chunk', {
                         client_id: this.$store.state.client_id,
                         filename: file.name,
                         chunk: chunk,
                         offset: offset,
                         isLastChunk: isLastChunk,
                         chunkIndex: chunkIndex,
                         totalChunks: totalChunks,
                         fileIndex: fileIndexInList
                     });
                     offset += chunk.byteLength;
                     chunkIndex++;
                     if (!isLastChunk) {
                         setTimeout(readNextChunk, 0);
                     }
                 } else {
                     this.onShowToastMessage(`Error reading ${file.name}. Upload failed.`, 4, false);
                 }
             };
              fileReader.onerror = (error) => {
                  this.onShowToastMessage(`Error reading ${file.name}. Upload failed.`, 4, false);
              };
             const readNextChunk = () => {
                 const currentFile = this.filesList[fileIndexInList];
                 if (currentFile && offset < currentFile.size) {
                     const blob = currentFile.slice(offset, offset + chunkSize);
                     fileReader.readAsArrayBuffer(blob);
                 }
             }
             readNextChunk();
         },
         handleFileUploadComplete(data) {
            if (data && data.client_id === this.$store.state.client_id && typeof data.fileIndex === 'number') {
                const index = data.fileIndex;
                if (index >= 0 && index < this.isFileSentList.length) {
                    this.isFileSentList[index] = true;
                    this.onShowToastMessage(`${data.filename || 'File'} uploaded successfully.`, 4, true);
                }
            }
         },
          handleFileUploadError(data) {
             if (data && data.client_id === this.$store.state.client_id) {
                 this.onShowToastMessage(`Upload failed for ${data.filename}: ${data.error}`, 4, false);
                  const index = data.fileIndex;
                  if (typeof index === 'number' && index >= 0 && index < this.filesList.length) {
                  }
             }
          },
         removeItem(fileToRemove) {
             const index = this.filesList.findIndex(f =>
                f.name === fileToRemove.name &&
                f.size === fileToRemove.size &&
                f.lastModified === fileToRemove.lastModified
             );
             if (index !== -1) {
                 this.removeFileByIndex(index);
                 this.notifyServerFileRemoved(fileToRemove.name);
             }
         },
         removeFileByIndex(index) {
            if (index >= 0 && index < this.filesList.length) {
                const removedFileName = this.filesList[index].name;
                this.filesList.splice(index, 1);
                this.isFileSentList.splice(index, 1);
                this.onShowToastMessage(`Removed ${removedFileName}.`, 4, true);
                this.updateFeatherIcons();
            }
         },
        async notifyServerFileRemoved(filename) {
             try {
                const response = await axios.post('/remove_discussion_file', {
                    client_id: this.$store.state.client_id,
                    name: filename,
                }, { headers: this.posts_headers });
                if (!response.data.status) {
                }
             } catch (error) {
             }
        },
         async clear_files() {
              try {
                  const response = await axios.post('/clear_discussion_files_list', {
                      client_id: this.$store.state.client_id,
                  }, { headers: this.posts_headers });
                  if (response.data.status) {
                      this.onShowToastMessage("All files removed.", 4, true);
                      this.filesList = [];
                      this.isFileSentList = [];
                      this.updateFeatherIcons();
                  } else {
                      this.onShowToastMessage(`Files couldn't be cleared: ${response.data.error || 'Unknown server error'}`, 4, false);
                  }
              } catch (error) {
                   this.onShowToastMessage(`Error clearing files: ${error.message}`, 4, false);
              }
         },
         download_files() {
              axios.get('/download_files', { responseType: 'blob', params: { client_id: this.$store.state.client_id } }).then(response => {
                  const url = window.URL.createObjectURL(new Blob([response.data]));
                  const link = document.createElement('a');
                  link.href = url;
                  const contentDisposition = response.headers['content-disposition'];
                  let filename = 'discussion_files.zip';
                  if (contentDisposition) {
                     const filenameMatch = contentDisposition.match(/filename\*?=['"]?([^'";]+)['"]?/i);
                     if (filenameMatch && filenameMatch[1]) {
                        try {
                             filename = decodeURIComponent(filenameMatch[1].replace(/['"]/g, ''));
                         } catch (e) {
                             const simplerMatch = contentDisposition.match(/filename="?(.+)"?/i);
                             if (simplerMatch && simplerMatch[1]) filename = simplerMatch[1];
                         }
                     }
                   }
                  link.setAttribute('download', filename);
                  document.body.appendChild(link);
                  link.click();
                   setTimeout(() => {
                      document.body.removeChild(link);
                      window.URL.revokeObjectURL(url);
                   }, 100);
             }).catch(error => {
                  this.onShowToastMessage("Error downloading files.",4,false);
             });
         },
         handlePaste(event) {
             const items = (event.clipboardData || window.clipboardData)?.items;
             if (!items) return;
             let filesToUpload = [];
             for (let i = 0; i < items.length; i++) {
                  const item = items[i];
                  if (item.kind === 'file') {
                      const file = item.getAsFile();
                      if (file) {
                          if (item.type.startsWith("image/") && !file.name) {
                              const uniqueId = Date.now() + '_' + Math.random().toString(36).substring(2, 9);
                              const extension = item.type.split('/')[1] || 'png';
                              const newFileName = `pasted_image_${uniqueId}.${extension}`;
                              const namedFile = new File([file], newFileName, { type: file.type, lastModified: file.lastModified });
                              filesToUpload.push(namedFile);
                          } else {
                              filesToUpload.push(file);
                          }
                      }
                  }
             }
             if (filesToUpload.length > 0) {
                 event.preventDefault();
                 this.addFiles(filesToUpload);
                 this.onShowToastMessage(`Added ${filesToUpload.length} file(s) from paste.`, 4, true);
             }
         },
         toggleLeftPanel() {
              this.$store.commit('setLeftPanelCollapsed', !this.$store.state.leftPanelCollapsed);
         },
         toggleRightPanel() {
             this.$store.commit('setRightPanelCollapsed', !this.$store.state.rightPanelCollapsed);
         },
         toggleThinkFirstMode() {
             this.$store.state.config.think_first_mode = !this.$store.state.config.think_first_mode;
             this.$store.dispatch('applyConfiguration');
             this.$store.dispatch('saveConfiguration');
         },
         toggleFunMode() {
             this.$store.state.config.fun_mode = !this.$store.state.config.fun_mode;
             this.$store.dispatch('applyConfiguration');
             this.$store.dispatch('saveConfiguration');
         },
         startSpeechRecognition() {
              const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
              if (!SpeechRecognition) {
                  this.onShowToastMessage("Speech recognition not supported by your browser.", 4, false);
                  return;
              }
              if (this.isListeningToVoice) {
                  this.recognition?.stop();
                  clearTimeout(this.silenceTimer);
                  this.isListeningToVoice = false;
                  return;
              }
              try{
                  this.recognition = new SpeechRecognition();
                  this.recognition.lang = this.$store.state.config?.audio_in_language || navigator.language || 'en-US';
                  this.recognition.interimResults = true;
                  this.recognition.continuous = false;
                  this.recognitionError = false;
                  this.recognition.onstart = () => {
                      this.isListeningToVoice = true;
                      this.resetSilenceTimer();
                  };
                  this.recognition.onresult = (event) => {
                      this.resetSilenceTimer();
                      let interimTranscript = '';
                      let finalTranscript = '';
                      for (let i = event.resultIndex; i < event.results.length; ++i) {
                          const transcript = event.results[i][0].transcript;
                          if (event.results[i].isFinal) {
                              finalTranscript += transcript + ' ';
                          } else {
                              interimTranscript += transcript;
                          }
                      }
                      this.message = finalTranscript.trim() + (interimTranscript ? ' ' + interimTranscript : '');
                  };
                  this.recognition.onerror = (event) => {
                      this.recognitionError = true;
                      let errorMsg = "Speech recognition error";
                      switch(event.error) {
                          case 'no-speech': errorMsg = "No speech detected. Please try again."; break;
                          case 'audio-capture': errorMsg = "Microphone error. Check microphone connection and permissions."; break;
                          case 'not-allowed': errorMsg = "Microphone access denied. Please allow microphone access in browser settings."; break;
                          case 'network': errorMsg = "Network error during speech recognition."; break;
                          case 'service-not-allowed': errorMsg = "Speech recognition service denied. Check browser/OS settings."; break;
                          default: errorMsg = `Speech error: ${event.error}`;
                      }
                       this.onShowToastMessage(errorMsg, 4, false);
                       this.isListeningToVoice = false;
                       clearTimeout(this.silenceTimer);
                  };
                  this.recognition.onend = () => {
                      this.isListeningToVoice = false;
                      clearTimeout(this.silenceTimer);
                      if (this.message.trim() && !['no-speech', 'not-allowed', 'audio-capture'].includes(this.recognitionError ? this.recognition.error : '')) {
                           this.submit();
                      }
                      this.recognition = null;
                  };
                  this.recognition.start();
              } catch(e) {
                  this.onShowToastMessage("Could not start voice input. Please check browser compatibility and permissions.", 4, false);
                  this.isListeningToVoice = false;
              }
         },
         resetSilenceTimer() {
             clearTimeout(this.silenceTimer);
             this.silenceTimer = setTimeout(() => {
                 if (this.isListeningToVoice && this.recognition) {
                     this.recognition.stop();
                 }
             }, this.silenceTimeoutDuration);
         },
         updateRT() {
             if (this.is_rt) {
                 this.stopRTCom();
             } else {
                 this.startRTCom();
             }
         },
         startRTCom() {
              if(this.$store.state.config.active_tts_service === 'None' || !this.$store.state.config.active_tts_service || this.$store.state.config.active_stt_service === 'None' || !this.$store.state.config.active_stt_service) {
                  this.onShowToastMessage("Both TTS and STT services must be configured and selected to use Real-Time mode.", 4, false);
                  return;
              }
             socket.emit('start_bidirectional_audio_stream', { client_id: this.$store.state.client_id });
             this.onShowToastMessage("Attempting to start Real-time audio...", 4, true);
         },
         stopRTCom() {
             socket.emit('stop_bidirectional_audio_stream', { client_id: this.$store.state.client_id });
             this.onShowToastMessage("Stopping Real-time audio...", 4, true);
         },
         handleRTComStatusChanged(data) {
             if (data && data.client_id === this.$store.state.client_id) {
                this.is_rt = data.status;
                const message = `Real-time audio mode ${this.is_rt ? 'activated' : 'deactivated'}.`;
                this.onShowToastMessage(message, 4, this.is_rt);
             }
         },
         toggleSendMenu() {
            this.isSendMenuVisible = !this.isSendMenuVisible;
            if (this.isSendMenuVisible) {
                this.updateFeatherIcons();
            }
         },
         closeSendMenu() {
            if (this.isSendMenuVisible) {
                this.isSendMenuVisible = false;
            }
         },
         add_file() {
            this.closeSendMenu();
            this.$refs.fileDialog?.click();
         },
         takePicture() {
             this.closeSendMenu();
             socket.emit('take_picture', { client_id: this.$store.state.client_id });
             this.onShowToastMessage("Requesting picture from camera service...", 4, true);
         },
         addWebLink() {
            this.closeSendMenu();
            this.$emit('addWebLink');
         },
        handlePictureTaken(data) {
            if (data && data.client_id === this.$store.state.client_id && data.status === 'success' && data.file) {
                const pictureFile = this.createFileObjectFromBase64(data.file.data, data.file.name, data.file.type);
                if (pictureFile) {
                    this.addFiles([pictureFile]);
                    this.onShowToastMessage("Picture added successfully!", 4, true);
                } else {
                    this.onShowToastMessage("Error processing received picture.", 4, false);
                }
            } else if (data && data.client_id === this.$store.state.client_id && data.status === 'error') {
                this.onShowToastMessage(`Failed to take picture: ${data.error}`, 4, false);
            }
        },
        createFileObjectFromBase64(base64Data, fileName, fileType) {
            try {
                const byteCharacters = atob(base64Data);
                const byteNumbers = new Array(byteCharacters.length);
                for (let i = 0; i < byteCharacters.length; i++) {
                    byteNumbers[i] = byteCharacters.charCodeAt(i);
                }
                const byteArray = new Uint8Array(byteNumbers);
                const blob = new Blob([byteArray], { type: fileType });
                return new File([blob], fileName, { type: fileType });
            } catch (error) {
                return null;
            }
        },
         makeAnEmptyUserMessage() {
            this.$emit('createEmptyUserMessage', this.message);
            this.message = "";
         },
         makeAnEmptyAIMessage() {
            this.$emit('createEmptyAIMessage');
         },
         toggleHelpModal() {
            this.showHelpModal = !this.showHelpModal;
            if (this.showHelpModal) {
                this.updateFeatherIcons();
            }
         },
         sendMessageEvent(msgContent, type = "no_internet") {
             const trimmedMsg = msgContent.trim();
             if (trimmedMsg === '' && this.filesList.length === 0) {
                 this.onShowToastMessage("Cannot send an empty message without attached files.", 4, false);
                 return;
             }
             this.$emit('messageSentEvent', trimmedMsg, type);
             this.message = "";
             nextTick(() => {
                 this.$refs.textareaRef?.focus();
             });
         },
          submitOnEnter(event) {
             if (event.key === 'Enter' && !event.shiftKey && !this.loading) {
                 event.preventDefault();
                 if (!event.repeat) {
                     this.sendMessageEvent(this.message);
                 }
             } else if (event.key === 'Enter' && !event.shiftKey && this.loading){
                  event.preventDefault();
                  this.onShowToastMessage("Please wait for the current response to complete.", 4, false);
             }
         },
         submit() {
             if (this.loading) {
                 this.onShowToastMessage("Please wait for the AI to finish responding.", 4, false);
                 return;
             }
             this.sendMessageEvent(this.message);
         },
         submitWithInternetSearch() {
             if (this.loading) {
                 this.onShowToastMessage("Please wait for the AI to finish responding.", 4, false);
                 return;
             }
             this.sendMessageEvent(this.message, "internet");
         },
         stopGenerating() {
            this.$emit('stopGenerating');
         },
         sendCMDEvent(cmd) {
             if(cmd && typeof cmd.value !== 'undefined') {
                 this.$emit('sendCMDEvent', cmd);
             }
         },
         async mountDB(cmdValue) {
             const datalakeAlias = cmdValue;
             if (!datalakeAlias) {
                 return;
             }
             const dataLake = this.$store.state.config.datalakes.find(dl => dl.alias === datalakeAlias);
             const initiallyMounted = dataLake ? dataLake.mounted : false;
             const action = !initiallyMounted ? 'Mounting' : 'Unmounting';
             this.onShowToastMessage(`${action} datalake ${datalakeAlias}...`, 4, true);
             try{
                 const response = await axios.post('/toggle_mount_rag_database', {
                      client_id: this.$store.state.client_id,
                      datalake_name: datalakeAlias
                 }, { headers: this.posts_headers });
                 if (response.data?.status) {
                     const finalAction = !initiallyMounted ? 'mounted' : 'unmounted';
                     this.onShowToastMessage(`Datalake ${datalakeAlias} ${finalAction} successfully.`, 4, true);
                 } else {
                    this.onShowToastMessage(`Failed to toggle datalake ${datalakeAlias}: ${response.data?.error || 'Server error'}`, 4, false);
                 }
                 await this.$store.dispatch('refreshConfig');
             } catch(error) {
                  this.onShowToastMessage(`Error toggling datalake ${datalakeAlias}. Check console for details.`, 4, false);
                  await this.$store.dispatch('refreshConfig');
             }
         },
         async showFunctionSettings(funcValue) {
             const func = funcValue;
              if (!func || !func.dir || !func.name) {
                 return;
              }
              let normalizedPath = func.dir.replace(/\\/g, '/');
              const segments = normalizedPath.split('/').filter(Boolean);
              const category = segments.length > 1 ? segments[segments.length - 2] : 'general';
             this.onShowToastMessage(`Fetching settings for ${func.name}...`, 4, true);
              try {
                 const response = await axios.post('/get_function_call_settings',{
                     client_id: this.$store.state.client_id,
                     category: category,
                     name: func.name
                 }, { headers: this.posts_headers });
                 if (response.data && Object.keys(response.data).length > 0) {
                      this.$store.state.universalForm.showForm(
                          response.data,
                          `Settings: ${func.name}`,
                          "Save Changes",
                          "Cancel"
                      ).then(formData => {
                          this.onShowToastMessage(`Saving settings for ${func.name}...`, 4, true);
                          axios.post('/set_function_call_settings', {
                              client_id: this.$store.state.client_id,
                              category: category,
                              name: func.name,
                              settings: formData
                          }, { headers: this.posts_headers }).then(setResponse => {
                              if (setResponse.data?.status === 'success') {
                                  this.onShowToastMessage(`Settings for ${func.name} saved successfully.`, 4, true);
                              } else {
                                  this.onShowToastMessage(`Failed to save settings: ${setResponse.data?.error || 'Unknown server error'}`, 4, false);
                              }
                          }).catch(setError => {
                               this.onShowToastMessage(`Error saving settings: ${setError.message}`, 4, false);
                          });
                      }).catch(() => {
                          this.onShowToastMessage("Settings changes cancelled.", 4, true);
                      });
                 } else {
                      this.onShowToastMessage(`${func.name} has no configurable settings.`, 4, true);
                 }
             } catch (error) {
                 this.onShowToastMessage(`Error fetching settings for ${func.name}. Check console.`, 4, false);
             }
         },
         async toggleFunctionCall(funcValue) {
             const func = funcValue;
              if (!func || !func.dir || !func.name) {
                  return;
              }
              const initiallySelected = func.is_checked;
              const action = !initiallySelected ? 'Enabling' : 'Disabling';
              this.onShowToastMessage(`${action} function call ${func.name}...`, 4, true);
             try {
                  const response = await axios.post('/toggle_function_call', {
                      client_id: this.$store.state.client_id,
                      name: func.name,
                      dir: func.dir
                  }, { headers: this.posts_headers });
                 if (response.data?.status) {
                    const finalAction = !initiallySelected ? 'enabled' : 'disabled';
                    this.onShowToastMessage(`Function call ${func.name} ${finalAction}.`, 4, true);
                 } else {
                    this.onShowToastMessage(`Failed to toggle ${func.name}: ${response.data?.error || 'Server error'}`, 4, false);
                 }
                  await this.$store.dispatch('refreshConfig');
              } catch (error) {
                  this.onShowToastMessage(`Error toggling ${func.name}. Check console.`, 4, false);
                   await this.$store.dispatch('refreshConfig');
              }
         },
    },
    watch: {
        filesList: {
            handler() {
                this.recalculateTotalSize();
                 this.updateFeatherIcons();
            },
            deep: true
        },
        loading: 'updateFeatherIcons',
        isSendMenuVisible(newVal) {
             if (newVal) this.updateFeatherIcons();
        },
        isShrunk(newVal, oldVal) {
            if (newVal !== oldVal) {
                this.updateFeatherIcons();
            }
        },
        showHelpModal(newVal) {
             if (newVal) this.updateFeatherIcons();
        },
        showEmojiPicker(newVal) {
        },
        '$store.state.is_rt_on'(newValue) {
            if (this.is_rt !== newValue) {
                this.is_rt = newValue;
            }
        },
        '$store.state.config.active_personality_id': 'updateFeatherIcons',
        '$store.state.config.datalakes': {
            handler: 'updateFeatherIcons',
            deep: true
        },
        '$store.state.config.mounted_function_calls': {
            handler: 'updateFeatherIcons',
            deep: true
        },
    },
    mounted() {
        this.$emit('loaded');
        try {
            const storedShrunk = localStorage.getItem('chatbarShrunk');
            if (storedShrunk !== null) {
                this.isShrunk = JSON.parse(storedShrunk);
            }
            const storedPositionModified = localStorage.getItem('chatbarPositionModified');
            const storedPosition = localStorage.getItem('chatbarPosition');
             if (storedPositionModified === 'true' && storedPosition) {
                this.currentChatboxPos = JSON.parse(storedPosition);
                this.isPositionModified = true;
            } else {
                 this.isPositionModified = false;
                 this.currentChatboxPos = null;
            }
        } catch (e) {
             this.isShrunk = false;
             this.isPositionModified = false;
             this.currentChatboxPos = null;
             localStorage.removeItem('chatbarShrunk');
             localStorage.removeItem('chatbarPositionModified');
             localStorage.removeItem('chatbarPosition');
        }
        socket.on('rtcom_status_changed', this.handleRTComStatusChanged);
        socket.on('picture_taken', this.handlePictureTaken);
        socket.on('file_upload_complete', this.handleFileUploadComplete);
        socket.on('file_upload_error', this.handleFileUploadError);
        this.is_rt = this.$store.state.is_rt_on;
        this.recalculateTotalSize();
        this.updateFeatherIcons();
    },
    beforeUnmount() {
        socket.off('rtcom_status_changed', this.handleRTComStatusChanged);
        socket.off('picture_taken', this.handlePictureTaken);
        socket.off('file_upload_complete', this.handleFileUploadComplete);
        socket.off('file_upload_error', this.handleFileUploadError);
        if (this.recognition && this.isListeningToVoice) {
            this.recognition.abort();
            this.isListeningToVoice = false;
        }
        clearTimeout(this.silenceTimer);
         window.removeEventListener('mousemove', this.onMouseMove);
         window.removeEventListener('mouseup', this.onMouseUp);
         window.removeEventListener('mouseleave', this.onMouseLeave);
         document.body.classList.remove('user-select-none');
    },
    activated() {
       this.recalculateTotalSize();
       this.is_rt = this.$store.state.is_rt_on;
       nextTick(() => {
            try {
                const storedPositionModified = localStorage.getItem('chatbarPositionModified');
                const storedPosition = localStorage.getItem('chatbarPosition');
                if (storedPositionModified === 'true' && storedPosition) {
                    this.currentChatboxPos = JSON.parse(storedPosition);
                    this.isPositionModified = true;
                } else {
                    this.isPositionModified = false;
                    this.currentChatboxPos = null;
                }
                const storedShrunk = localStorage.getItem('chatbarShrunk');
                if (storedShrunk !== null) {
                    this.isShrunk = JSON.parse(storedShrunk);
                }
            } catch(e){ console.error("Error reapplying state on activation:", e) }
           this.updateFeatherIcons();
       });
    },
    deactivated() {
       if (this.recognition && this.isListeningToVoice) {
           this.recognition.abort();
           this.isListeningToVoice = false;
           clearTimeout(this.silenceTimer);
       }
        if (this.isDragging) {
            this.onMouseUp();
        }
    }
}
</script>