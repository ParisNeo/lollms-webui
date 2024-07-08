<template>
    <transition name="fade-and-fly">
    <div v-if="!isReady" class="fixed top-0 left-0 w-screen h-screen flex items-center justify-center">
        <!-- SPINNER -->
     
        <div class="flex flex-col text-center">
            <div class="flex flex-col text-center items-center">
                
                <div class="flex items-center gap-3 text-5xl drop-shadow-md align-middle pt-24 ">
                
                    <img class="w-24 animate-bounce" title="LoLLMS WebUI" src="@/assets/logo.png" alt="Logo">
                        <div class="flex flex-col items-start">
                        <p class="text-2xl font-bold text-5xl drop-shadow-md align-middle">LoLLMS {{ version_info }} </p>
                        <p class="text-gray-400 text-base">One tool to rule them all</p>
                        <p class="text-gray-400 text-base">by ParisNeo</p>

                        </div>
                </div>
                <hr class=" mt-1 w-96 h-1 mx-auto my-2 md:my-2 dark:bg-bg-dark-tone-panel bg-bg-light-tone-panel border-0 rounded ">
                <p class="text-2xl mb-10 font-bold drop-shadow-md ">Welcome</p>
                <div role="status" class="text-center w-full display: flex; flex-row align-items: center;">
                        <ProgressBar ref="loading_progress" :progress="loading_progress"></ProgressBar>
                        <p class="text-2xl animate-pulse mt-2"> {{ loading_infos }} ...</p>
                </div> 

            </div>

        </div>  
    </div>

  
    </transition>
    <button v-if="isReady" @click="togglePanel" class="absolute top-2 left-2 p-3 bg-white bg-opacity-10 rounded-full cursor-pointer transition-all duration-300 hover:scale-110 hover:bg-opacity-20 animate-pulse shadow-lg hover:shadow-xl group">
                    <div v-show="leftPanelCollapsed" ><i data-feather='chevron-right'></i></div>
                    <div v-show="!leftPanelCollapsed" ><i data-feather='chevron-left'></i></div>
    </button>
    <!-- Robot SVG -->
    <button v-if="isReady" @click.stop="triggerRobotAction()" class="absolute top-2 right-2 p-3 bg-white bg-opacity-10 rounded-full cursor-pointer transition-all duration-300 hover:scale-110 hover:bg-opacity-20 animate-pulse shadow-lg hover:shadow-xl group">
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="w-10 h-10 text-blue-500 transition-colors duration-300 group-hover:text-yellow-400">
        <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
        <circle cx="12" cy="5" r="2"></circle>
        <path d="M12 7v4"></path>
        <line x1="8" y1="16" x2="8" y2="16"></line>
        <line x1="16" y1="16" x2="16" y2="16"></line>
    </svg>
    </button>
       
    <transition name="slide-right">
    <div  v-if="showLeftPanel"
        class="relative flex flex-col no-scrollbar shadow-lg min-w-[24rem] max-w-[24rem] bg-bg-light-tone dark:bg-bg-dark-tone"
        >
        <!-- LEFT SIDE PANEL -->
        <div id="leftPanel" class="flex flex-col flex-grow overflow-y-scroll no-scrollbar "
            @dragover.stop.prevent="setDropZoneDiscussion()">
            <div class="text-light-text-panel dark:text-dark-text-panel bg-bg-light-panel sticky z-10 top-0 dark:bg-bg-dark-tone shadow-md ">

                <!-- CONTROL PANEL -->
                <div class="flex-row p-4  flex items-center gap-3 flex-0">
                    <!-- MAIN BUTTONS -->
                    <button class="text-2xl hover:text-secondary duration-75 active:scale-90" title="Create new discussion"
                        type="button" @click="createNewDiscussion()">
                        <i data-feather="plus"></i>
                    </button>
                    <button class="text-2xl hover:text-secondary duration-75 active:scale-90" title="Edit discussion list"
                        type="button" @click="isCheckbox = !isCheckbox" :class="isCheckbox ? 'text-secondary' : ''">
                        <i data-feather="check-square"></i>
                    </button>
                    <button class="text-2xl hover:text-secondary duration-75 active:scale-90"
                        title="Reset database, remove all discussions">
                        <i data-feather="trash-2" @click.stop=""></i>
                    </button>
                    <button class="text-2xl hover:text-secondary duration-75 active:scale-90" title="Export database"
                        type="button" @click.stop="database_selectorDialogVisible=true">
                        <i data-feather="database"></i>
                    </button>
                    <input type="file" ref="fileDialog" style="display: none" @change="importDiscussions" />
                    <button class="text-2xl hover:text-secondary duration-75 active:scale-90 rotate-90"
                        title="Import discussions" type="button" @click.stop="$refs.fileDialog.click()">
                        <i data-feather="log-in"></i>
                    </button>
                    <input type="file" ref="bundleLoadingDialog" style="display: none" @change="importDiscussionsBundle" />
                    <button  v-if="!showSaveConfirmation" title="Import discussion bundle" @click.stop="$refs.bundleLoadingDialog.click()" 
                        class="text-2xl hover:text-secondary duration-75 active:scale-90"
                        >
                        <i data-feather="folder"></i>
                    </button>
                    
                    <div v-if="isOpen" class="dropdown">
                      <button @click="importDiscussions">LOLLMS</button> 
                      <button @click="importChatGPT">ChatGPT</button>
                    </div>
                    <button class="text-2xl hover:text-secondary duration-75 active:scale-90" title="Filter discussions"
                        type="button" @click="isSearch = !isSearch" :class="isSearch ? 'text-secondary' : ''">
                        <i data-feather="search"></i>
                    </button>
                    <!-- SAVE CONFIG -->
                    <div v-if="showSaveConfirmation" class="flex gap-3 flex-1 items-center duration-75">
                        <button class="text-2xl hover:text-red-600 duration-75 active:scale-90 " title="Cancel" type="button"
                            @click.stop="showSaveConfirmation = false">
                            <i data-feather="x"></i>
                        </button>
                        <button class="text-2xl hover:text-secondary duration-75 active:scale-90" title="Confirm save changes"
                            type="button" @click.stop="save_configuration()">
                            <i data-feather="check"></i>
                        </button>
                    </div>
                    <button v-if="!loading" type="button" @click.stop="addDiscussion2SkillsLibrary" title="Add this discussion content to skills database"
                        class=" w-6 hover:text-secondary duration-75 active:scale-90">
                        <i data-feather="hard-drive"></i>
                    </button>
                    <button v-if="!loading && $store.state.config.activate_skills_lib" type="button" @click.stop="toggleSkillsLib" title="Skills database is activated"
                        class=" w-6 hover:text-secondary duration-75 active:scale-90">
                        <i data-feather="check-circle"></i>
                    </button>
                    <button v-if="!loading && !$store.state.config.activate_skills_lib" type="button" @click.stop="toggleSkillsLib" title="Skills database is deactivated"
                        class=" w-6 hover:text-secondary duration-75 active:scale-90">
                        <i data-feather="x-octagon"></i>
                    </button>
                    <button v-if="!loading" type="button" @click.stop="showSkillsLib" title="Show Skills database"
                        class=" w-6 hover:text-secondary duration-75 active:scale-90">
                        <i data-feather="book"></i>
                    </button>
   
                    <div v-if="loading" title="Loading.." class="flex flex-row flex-grow justify-end">
                        <!-- SPINNER -->
                        <div role="status">
                            <svg aria-hidden="true" class="w-6 h-6   animate-spin  fill-secondary" viewBox="0 0 100 101"
                                fill="none" xmlns="http://www.w3.org/2000/svg">
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
                <!-- SEARCH BAR -->
                <!-- <Transition name="expand" > -->
                <div v-if="isSearch" class="flex-row  items-center gap-3 flex-0 w-full">
                    <div class="p-4 pt-2 ">
                        <div class="relative">
                            <div class="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
                                <div class="scale-75">
                                    <i data-feather="search"></i>
                                </div>
                            </div>
                            <div class="absolute inset-y-0 right-0 flex items-center pr-3">
                                <div class="hover:text-secondary duration-75 active:scale-90"
                                    :class="filterTitle ? 'visible' : 'invisible'" title="Clear" @click="filterTitle = ''">
                                    <i data-feather="x"></i>
                                </div>
                            </div>

                            <input type="search" id="default-search"
                                class="block w-full p-2 pl-10 pr-10 text-sm border border-gray-300 rounded-lg bg-bg-light focus:ring-secondary focus:border-secondary dark:bg-bg-dark dark:border-gray-600 dark:placeholder-gray-400 dark:focus:ring-secondary dark:focus:border-secondary"
                                placeholder="Search..." title="Filter discussions by title" v-model="filterTitle"
                                @input="filterDiscussions()" />
                        </div>
                    </div>

                </div>
                <!-- </Transition> -->
                <hr v-if="isCheckbox" class="h-px bg-bg-light p-0 mb-4 px-4 mx-4 border-0 dark:bg-bg-dark">
                <div v-if="isCheckbox" class="flex flex-row flex-grow p-4 pt-0 items-center">

                    <!-- CHECK BOX OPERATIONS -->
                    <div class="flex flex-row flex-grow ">
                        <p v-if="selectedDiscussions.length > 0">Selected: {{ selectedDiscussions.length }}</p>
                    </div>
                    <div class="flex flex-row ">

                        <div v-if="selectedDiscussions.length > 0" class="flex gap-3">
                            <!-- DELETE MULTIPLE -->
                            <button v-if="!showConfirmation"
                                class="flex mx-3 flex-1 text-2xl hover:text-red-600 duration-75 active:scale-90 "
                                title="Remove selected" type="button" @click.stop="showConfirmation = true">
                                <i data-feather="trash"></i>
                            </button>
                            <!-- DELETE CONFIRM -->
                            <div v-if="showConfirmation"
                                class="flex gap-3 mx-3 flex-1 items-center justify-end  group-hover:visible duration-75">
                                <button class="text-2xl hover:text-secondary duration-75 active:scale-90"
                                    title="Confirm removal" type="button" @click.stop="deleteDiscussionMulti">
                                    <i data-feather="check"></i>
                                </button>
                                <button class="text-2xl hover:text-red-600 duration-75 active:scale-90 "
                                    title="Cancel removal" type="button" @click.stop="showConfirmation = false">
                                    <i data-feather="x"></i>
                                </button>
                            </div>
                        </div>
                        <div class="flex gap-3">

                            <button class="text-2xl hover:text-secondary duration-75 active:scale-90 rotate-90"
                                title="Export selected to a json file" type="button" @click.stop="exportDiscussionsAsJson">
                                <i data-feather="codepen"></i>
                            </button>
                            <button class="text-2xl hover:text-secondary duration-75 active:scale-90 rotate-90"
                                title="Export selected to a martkdown file" type="button" @click.stop="exportDiscussions">
                                <i data-feather="folder"></i>
                            </button>                            
                            <button class="text-2xl hover:text-secondary duration-75 active:scale-90 rotate-90"
                                title="Export selected to a martkdown file" type="button" @click.stop="exportDiscussionsAsMarkdown">
                                <i data-feather="bookmark"></i>
                            </button>                            
                            <button class="text-2xl hover:text-secondary duration-75 active:scale-90 " title="Select All"
                                type="button" @click.stop="selectAllDiscussions">
                                <i data-feather="list"></i>
                            </button>

                        </div>
                    </div>
                </div>

            </div>
            <div class="relative flex flex-row flex-grow mb-10 z-0  w-full">
                <!-- DISCUSSION LIST -->
                <div class="mx-4 flex flex-col flex-grow  w-full " :class="isDragOverDiscussion ? 'pointer-events-none' : ''">
                    <div id="dis-list" :class="filterInProgress ? 'opacity-20 pointer-events-none' : ''"
                        class="flex flex-col flex-grow  w-full">
                        <TransitionGroup v-if="list.length > 0" name="list">
                            <Discussion v-for="(item, index) in list" :key="item.id" :id="item.id" :title="item.title"
                                :selected="currentDiscussion.id == item.id" :loading="item.loading" :isCheckbox="isCheckbox"
                                :checkBoxValue="item.checkBoxValue" 
                                @select="selectDiscussion(item)"
                                @delete="deleteDiscussion(item.id)" 
                                @openFolder="openFolder"
                                @editTitle="editTitle" 
                                @makeTitle="makeTitle"
                                @checked="checkUncheckDiscussion" />
                        </TransitionGroup>
                        <div v-if="list.length < 1"
                            class="gap-2 py-2 my-2 hover:shadow-md hover:bg-primary-light dark:hover:bg-primary rounded-md p-2 duration-75 group cursor-pointer">
                            <p class="px-3">No discussions are found</p>
                        </div>
                        <div
                            class="sticky bottom-0 bg-gradient-to-t pointer-events-none from-bg-light-tone dark:from-bg-dark-tone flex flex-grow">
                            <!-- FADING DISCUSSION LIST END ELEMENT -->
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <div class="absolute h-15 bottom-0 left-0 w-full bg-bg-light-panel dark:bg-bg-dark-tone light-text-panel py-4 cursor-pointer text-light-text-panel dark:text-dark-text-panel hover:text-secondary" @click="showDatabaseSelector">
            <p class="text-center font-large font-bold text-l drop-shadow-md align-middle">{{ formatted_database_name.replace("_"," ") }}</p>
        </div>
    </div>
    </transition>
        <div v-if="isReady" class="relative flex flex-col flex-grow" >
            <div id="messages-list"
                class="w-full z-0 flex flex-col  flex-grow  overflow-y-auto scrollbar-thin scrollbar-track-bg-light-tone scrollbar-thumb-bg-light-tone-panel hover:scrollbar-thumb-primary dark:scrollbar-track-bg-dark-tone dark:scrollbar-thumb-bg-dark-tone-panel dark:hover:scrollbar-thumb-primary active:scrollbar-thumb-secondary"
                :class="isDragOverChat ? 'pointer-events-none' : ''">

                <!-- CHAT AREA -->
                <div class="container pt-4 pb-50 mb-50 w-full">
                    <TransitionGroup v-if="discussionArr.length > 0" name="list">
                        <Message v-for="(msg, index) in discussionArr" 
                            :key="msg.id" :message="msg"  :id="'msg-' + msg.id" :ref="'msg-' + msg.id"
                            :host="host"
                            ref="messages"
                            
                            @copy="copyToClipBoard" @delete="deleteMessage" @rankUp="rankUpMessage"
                            @rankDown="rankDownMessage" @updateMessage="updateMessage" @resendMessage="resendMessage" @continueMessage="continueMessage"
                            :avatar="getAvatar(msg.sender)" />

                        <!-- REMOVED FOR NOW, NEED MORE TESTING -->
                        <!-- @click="scrollToElementInContainer($event.target, 'messages-list')"  -->


                    </TransitionGroup>
                    <WelcomeComponent v-if="!currentDiscussion.id" />
                    <div><br><br><br><br><br><br><br></div>
                </div>

                <div
                    class="absolute w-full bottom-0 bg-transparent p-10 pt-16 bg-gradient-to-t from-bg-light dark:from-bg-dark from-5% via-bg-light dark:via-bg-dark via-10% to-transparent to-100%">
                </div>
            </div>
            <div class="flex flex-row items-center justify-center h-10" v-if="currentDiscussion.id">
                <ChatBox ref="chatBox" 
                    :loading="isGenerating" 
                    :discussionList="discussionArr" 
                    :on-show-toast-message="showToastMessage"
                    :on-talk="talk"

                    @personalitySelected="recoverFiles"
                    @messageSentEvent="sendMsg" 
                    @sendCMDEvent="sendCmd"
                    @addWebLink="add_webpage"
                    @createEmptyUserMessage="createEmptyUserMessage"
                    @createEmptyAIMessage="createEmptyAIMessage"
                    @stopGenerating="stopGenerating" 
                    @loaded="recoverFiles"
                    >
                </ChatBox>
            </div>        
        </div>
    <transition name="slide-left">
    <div  v-if="showRightPanel"
        class="relative flex flex-col no-scrollbar shadow-lg w-1/2 bg-bg-light-tone dark:bg-bg-dark-tone h-full"
        >
        <!-- RIGHT SIDE PANEL -->
         <!--  <div v-html="lastMessageHtml"></div> --> 
        <div ref="isolatedContent" class="h-full"></div>
    </div>
    </transition>
    <ChoiceDialog reference="database_selector" class="z-20"
      :show="database_selectorDialogVisible"
      :choices="databases"
      @choice-selected="ondatabase_selectorDialogSelected"
      @close-dialog="onclosedatabase_selectorDialog"
      @choice-validated="onvalidatedatabase_selectorChoice"
    />      
    <div v-show="progress_visibility" role="status" class="fixed m-0 p-2 left-2 bottom-2  min-w-[24rem] max-w-[24rem] h-20 flex flex-col justify-center items-center pb-4 bg-blue-500 rounded-lg shadow-lg z-50 background-a">
        <ProgressBar ref="progress" :progress="progress_value" class="w-full h-4"></ProgressBar>
        <p class="text-2xl animate-pulse mt-2 text-light-text-panel dark:text-dark-text-panel">{{ loading_infos }} ...</p>
    </div>
    <InputBox prompt-text="Enter the url to the page to use as discussion support" @ok="addWebpage" ref="web_url_input_box"></InputBox>   
    <SkillsLibraryViewer ref="skills_lib" ></SkillsLibraryViewer>
</template>


<style scoped>

@keyframes custom-pulse {
    0%, 100% { box-shadow: 0 0 0 0 rgba(59, 130, 246, 0.5); }
    50% { box-shadow: 0 0 0 15px rgba(59, 130, 246, 0); }
  }
.animate-pulse {
animation: custom-pulse 2s infinite;
}

.slide-right-enter-active {
  transition: transform 0.3s ease;
}

.slide-right-leave-active {
  transition: transform 0.3s ease;
}

.slide-right-enter,
.slide-right-leave-to {
  transform: translateX(-100%);
}

.slide-left-enter-active {
  transition: transform 0.3s ease;
}

.slide-left-leave-active {
  transition: transform 0.3s ease;
}

.slide-left-enter,
.slide-left-leave-to {
  transform: translateX(100%);
}

.fade-and-fly-enter-active {
  animation: fade-and-fly-enter 0.5s ease;
}

.fade-and-fly-leave-active {
  animation: fade-and-fly-leave 0.5s ease;
}

@keyframes fade-and-fly-enter {
  0% {
    opacity: 0;
    transform: translateY(20px) scale(0.8);
  }
  100% {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

@keyframes fade-and-fly-leave {
  0% {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
  100% {
    opacity: 0;
    transform: translateY(-20px) scale(1.2);
  }
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
import SVGRedBrain from '@/assets/brain_red.svg';
import SVGOrangeBrain from '@/assets/brain_orange.svg';
import SVGGreenBrain from '@/assets/brain_green.svg';
import memory_icon from "../assets/memory_icon.svg"
import active_skills from "../assets/active.svg"
import inactive_skills from "../assets/inactive.svg"
import skillsRegistry from "../assets/registry.svg"
import robot from "../assets/robot.svg"
import { mapState } from 'vuex';

export default {
    
    setup() { },
    
    data() {
        return {
            lastMessageHtml:"",
            defaultMessageHtml: `
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Default Render Panel</title>
            <style>
                body, html {
                    margin: 0;
                    padding: 0;
                    height: 100%;
                    font-family: Arial, sans-serif;
                    background-color: #f0f0f0;
                }
                .container {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    height: 100%;
                    padding: 20px;
                    box-sizing: border-box;
                }
                .message {
                    text-align: center;
                    padding: 30px;
                    background-color: white;
                    border-radius: 12px;
                    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
                    max-width: 600px;
                    width: 100%;
                }
                h1 {
                    color: #2c3e50;
                    margin-bottom: 20px;
                    font-size: 28px;
                }
                p {
                    color: #34495e;
                    margin: 0 0 15px;
                    line-height: 1.6;
                }
                .highlight {
                    color: #e74c3c;
                    font-weight: bold;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="message">
                    <h1>Welcome to the Interactive Render Panel</h1>
                    <p>This space is designed to bring your ideas to life! Currently, it's empty because no HTML has been generated yet.</p>
                    <p>To see something amazing here, try asking the AI to <span class="highlight">create a specific web component or application</span>. For example:</p>
                    <p>"Create a responsive image gallery" or "Build a simple todo list app"</p>
                    <p>Once you request a web component, the AI will generate the necessary HTML, CSS, and JavaScript, and it will be rendered right here in this panel!</p>
                </div>
            </div>
        </body>
        </html>       
            `,
            memory_icon: memory_icon,
            active_skills:active_skills,
            inactive_skills:inactive_skills,
            skillsRegistry:skillsRegistry,
            robot:robot,
            posts_headers : {
                'accept': 'application/json',
                'Content-Type': 'application/json'
            },
            host:"",
            progress_visibility_val         : true,
            progress_value                  : 0,
            // To be synced with the backend database types
            msgTypes: {
                // Messaging
                MSG_TYPE_CHUNK                  : 0, // A chunk of a message (used for classical chat)
                MSG_TYPE_FULL                   : 1, // A full message (for some personality the answer is sent in bulk)
                MSG_TYPE_FULL_INVISIBLE_TO_AI   : 2, // A full message (for some personality the answer is sent in bulk)
                MSG_TYPE_FULL_INVISIBLE_TO_USER : 3, // A full message (for some personality the answer is sent in bulk)

                // Informations
                MSG_TYPE_EXCEPTION              : 4, // An exception occured
                MSG_TYPE_WARNING                : 5, // A warning occured
                MSG_TYPE_INFO                   : 6, // An information to be shown to user

                // Steps
                MSG_TYPE_STEP                   : 7, // An instant step (a step that doesn't need time to be executed)
                MSG_TYPE_STEP_START             : 8, // A step has started (the text contains an explanation of the step done by he personality)
                MSG_TYPE_STEP_PROGRESS          : 9, // The progress value (the text contains a percentage and can be parsed by the reception)
                MSG_TYPE_STEP_END               : 10,// A step has been done (the text contains an explanation of the step done by he personality)

                //Extra
                MSG_TYPE_JSON_INFOS             : 11,// A JSON output that is useful for summarizing the process of generation used by personalities like chain of thoughts and tree of thooughts
                MSG_TYPE_REF                    : 12,// References (in form of  [text](path))
                MSG_TYPE_CODE                   : 13,// A javascript code to execute
                MSG_TYPE_UI                     : 14,// A vue.js component to show (we need to build some and parse the text to show it)


                MSG_TYPE_NEW_MESSAGE            : 15,// A new message
                MSG_TYPE_FINISHED_MESSAGE       : 17 // End of current message

            },
            // Sender types
            senderTypes: {
                SENDER_TYPES_USER               : 0, // Sent by user
                SENDER_TYPES_AI                 : 1, // Sent by ai
                SENDER_TYPES_SYSTEM             : 2, // Sent by athe system
            },
            list                                : [], // Discussion list
            tempList                            : [], // Copy of Discussion list (used for keeping the original list during filtering discussions/searching action)
            currentDiscussion                   : {}, // Current/selected discussion id
            discussionArr                       : [],
            loading: false,
            filterTitle: '',
            filterInProgress: false,
            isCreated: false,
            isCheckbox: false,
            isSelectAll: false,
            showSaveConfirmation: false,
            showBrainConfirmation: false,
            showConfirmation: false,
            chime: new Audio("chime_aud.wav"),
            showToast: false,
            isSearch: false,
            isDiscussionBottom: false,
            personalityAvatars: [], // object array of personality name: and avatar: props
            fileList: [],
            database_selectorDialogVisible:false,
            isDragOverDiscussion: false,
            isDragOverChat: false,
            leftPanelCollapsed: false, // left panel collapse
            rightPanelCollapsed: true, // right panel
            isOpen: false,
            discussion_id: 0,
        }
    },
    methods: {      
        extractHtml() {
            if (this.discussionArr.length > 0) {
                const lastMessage = this.discussionArr[this.discussionArr.length - 1].content;
                const startTag = '```html';
                const endTag = '```';
                let startIndex = lastMessage.indexOf(startTag);
                if (startIndex === -1) {
                    this.lastMessageHtml = this.defaultMessageHtml;
                    this.renderIsolatedContent();
                    return this.defaultMessageHtml;
                }
                
                startIndex += startTag.length;
                let endIndex = lastMessage.indexOf(endTag, startIndex);
                
                if (endIndex === -1) {
                    this.lastMessageHtml = lastMessage.slice(startIndex).trim();
                } else {
                    this.lastMessageHtml = lastMessage.slice(startIndex, endIndex).trim();
                }
            } else {
                this.lastMessageHtml = this.defaultMessageHtml;
            }
            this.renderIsolatedContent()
        },
        renderIsolatedContent() {
            const iframe = document.createElement('iframe');
            iframe.style.border = 'none';
            iframe.style.width = '100%';
            iframe.style.height = '100%'; // Adjust as needed
            if (this.$refs.isolatedContent){
                this.$refs.isolatedContent.innerHTML = '';
                this.$refs.isolatedContent.appendChild(iframe);
                
                const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
                iframeDoc.open();
                iframeDoc.write(`
                    ${this.lastMessageHtml}
                `);
                iframeDoc.close();
            }

        },        
        async triggerRobotAction(){
            this.rightPanelCollapsed = !this.rightPanelCollapsed;
            if(!this.rightPanelCollapsed){
                this.leftPanelCollapsed=true;
                this.$nextTick(() => {
                this.extractHtml()
                });

            }
            console.log(this.rightPanelCollapsed)
        }, 
        add_webpage(){
            console.log("addWebLink received")
            this.$refs.web_url_input_box.showPanel();
        },
        addWebpage(){

            axios.post('/add_webpage', {"client_id":this.client_id, "url": this.$refs.web_url_input_box.inputText}, {headers: this.posts_headers}).then(response => {
                if (response && response.status){
                    console.log("Done")
                    this.recoverFiles()
                }
            });

        },
        show_progress(data){
            this.progress_visibility_val = true;
        },
        hide_progress(data){
            this.progress_visibility_val = false;
        },
        update_progress(data){
            console.log("Progress update")
            this.progress_value = data.value;
        },
        onSettingsBinding() {
            try {
                this.isLoading = true
                axios.get('/get_active_binding_settings').then(res => {
                    this.isLoading = false
                    if (res) {
                        if (res.data && Object.keys(res.data).length > 0) {

                            // open form

                            this.$store.state.universalForm.showForm(res.data, "Binding settings - " + bindingEntry.binding.name, "Save changes", "Cancel").then(res => {
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
        showDatabaseSelector() {
            this.database_selectorDialogVisible = true;
        },        
        async ondatabase_selectorDialogSelected(choice){
            console.log("Selected:",choice)
        },
        onclosedatabase_selectorDialog(){this.database_selectorDialogVisible=false;},
        async onvalidatedatabase_selectorChoice(choice){
            this.database_selectorDialogVisible=false;
            const res = await axios.post("/select_database", {"client_id":this.client_id, "name": choice}, {headers: this.posts_headers});
            if(res.status){
                console.log("Selected database")
                this.$store.state.config = await axios.get("/get_config");
                console.log("new config loaded :",this.$store.state.config)
                let dbs = await axios.get("/list_databases")["data"];
                console.log("New list of database: ",dbs)

                this.$store.state.databases = dbs
                console.log("New list of database: ",this.$store.state.databases)
                location.reload();
            }
        
        },
        async addDiscussion2SkillsLibrary(){
            let result = await axios.post("/add_discussion_to_skills_library", {
                        client_id: this.client_id
                    }, {headers: this.posts_headers});
            if(result.status){
                console.log("done")
            }
        },
        async toggleSkillsLib(){
            this.$store.state.config.activate_skills_lib =! this.$store.state.config.activate_skills_lib;
            await this.applyConfiguration();
        },
        async showSkillsLib(){
            this.$refs.skills_lib.showSkillsLibrary()
        },
        
        async applyConfiguration() {
            this.loading = true;
            const res = await axios.post('/apply_settings', {"client_id":this.$store.state.client_id, "config":this.$store.state.config})
            this.loading = false;
            //console.log('apply-res',res)
            if (res.data.status) {
                
                this.$store.state.toast.showToast("Configuration changed successfully.", 4, true)
                //this.save_configuration()
            } else {
                this.$store.state.toast.showToast("Configuration change failed.", 4, false)
            }
            nextTick(() => {
                feather.replace()
            })
        },
        save_configuration() {
            this.showConfirmation = false
            axios.post('/save_settings', {})
                .then((res) => {
                    if (res) {
                        if (res.status) {
                            this.$store.state.toast.showToast("Settings saved!",4,true)
                        }
                        else
                            this.$store.state.messageBox.showMessage("Error: Couldn't save settings!")
                        return res.data;
                    }
                })
                .catch(error => {
                    console.log(error.message, 'save_configuration')
                    this.$store.state.messageBox.showMessage("Couldn't save settings!")
                    return { 'status': false }
                });

        },        
        showToastMessage(text, duration, isok){
            console.log("sending",text)
            this.$store.state.toast.showToast(text, duration, isok)
        },        
        togglePanel() {
            this.leftPanelCollapsed = !this.leftPanelCollapsed;
            if (!this.leftPanelCollapsed){
                this.rightPanelCollapsed = true;
            }
        },
        toggleDropdown() {
            this.isOpen = !this.isOpen;
        },
        importChatGPT() {
            // handle ChatGPT import
        },  
        async api_get_req(endpoint) {
            try {
                const res = await axios.get("/" + endpoint);

                if (res) {

                    return res.data

                }
            } catch (error) {
                console.log(error.message, 'api_get_req')
                return
            }
        },
        async list_discussions() {
            try {
                const res = await axios.get('/list_discussions')

                if (res) {

                    this.createDiscussionList(res.data)
                    return res.data
                }
            } catch (error) {
                console.log("Error: Could not list discussions", error.message)
                return []
            }
        },
        load_discussion(id, next) {
            if (id) {
                console.log("Loading discussion", id)
                this.loading = true
                this.discussionArr=[]
                this.setDiscussionLoading(id, this.loading)


                socket.on('discussion', (data)=>{
                    console.log("Discussion recovered")
                    this.loading = false
                    this.setDiscussionLoading(id, this.loading)
                    if (data) {
                        // Filter out the user and bot entries
                        this.discussionArr = data.filter((item) => 
                                                                item.message_type == this.msgTypes.MSG_TYPE_CHUNK ||
                                                                item.message_type == this.msgTypes.MSG_TYPE_FULL ||
                                                                item.message_type == this.msgTypes.MSG_TYPE_FULL_INVISIBLE_TO_AI ||
                                                                item.message_type == this.msgTypes.MSG_TYPE_CODE ||
                                                                item.message_type == this.msgTypes.MSG_TYPE_JSON_INFOS ||
                                                                item.message_type == this.msgTypes.MSG_TYPE_UI
                                                        )
                        console.log("this.discussionArr")
                        console.log(this.discussionArr)
                        if(next){
                            next()
                        }
                    }
                    
                    socket.off('discussion')
                    this.extractHtml()
                })

                socket.emit('load_discussion',{"id":id});

            }
        },
        recoverFiles(){
            console.log("Recovering files")
            axios.post('/get_discussion_files_list', {"client_id":this.$store.state.client_id}).then(res=>{
                this.$refs.chatBox.filesList = res.data.files;
                this.$refs.chatBox.isFileSentList= res.data.files.map(file => {
                    return true;
                });
                console.log(`Files recovered: ${this.$refs.chatBox.filesList}`)
            })
        },
        new_discussion(title) {
            try {
                this.loading = true
                socket.on('discussion_created',(data)=>{
                    socket.off('discussion_created')
                    this.list_discussions().then(()=>{
                        const index = this.list.findIndex((x) => x.id == data.id)
                        const discussionItem = this.list[index]
                        this.selectDiscussion(discussionItem)
                        this.load_discussion(data.id,()=>{
                            this.loading = false
                            this.recoverFiles();
                            nextTick(() => {
                                const selectedDisElement = document.getElementById('dis-' + data.id)
                                this.scrollToElement(selectedDisElement)
                                console.log("Scrolling tp "+selectedDisElement)
                            })
                        })
                    });
                });
                console.log("new_discussion ", title)
                socket.emit('new_discussion', {title:title});
            } catch (error) {
                console.log("Error: Could not create new discussion", error.message)
                return {}
            }
        },
        async delete_discussion(id) {
            try {
                if (id) {
                    this.loading = true
                    this.setDiscussionLoading(id, this.loading)
                    await axios.post('/delete_discussion', {
                        client_id: this.client_id,
                        id: id
                    }, {headers: this.posts_headers})
                    this.loading = false
                    this.setDiscussionLoading(id, this.loading)
                }
            } catch (error) {
                console.log("Error: Could not delete discussion", error.message)
                this.loading = false
                this.setDiscussionLoading(id, this.loading)
            }
        },
        async edit_title(id, new_title) {
            try {
                if (id) {
                    this.loading = true
                    this.setDiscussionLoading(id, this.loading)
                    const res = await axios.post('/edit_title', {
                        client_id: this.client_id,
                        id: id,
                        title: new_title
                    }, {headers: this.posts_headers})
                    this.loading = false
                    this.setDiscussionLoading(id, this.loading)
                    if (res.status == 200) {
                        const index = this.list.findIndex((x) => x.id == id)
                        const discussionItem = this.list[index]
                        discussionItem.title = new_title
                        this.tempList = this.list
                    }
                }
            } catch (error) {
                console.log("Error: Could not edit title", error.message)
                this.loading = false
                this.setDiscussionLoading(id, this.loading)
            }
        },
        async make_title(id) {
            try {
                if (id) {
                    this.loading = true
                    this.setDiscussionLoading(id, this.loading)
                    const res = await axios.post('/make_title', {
                        client_id: this.client_id,
                        id: id,
                    }, {headers: this.posts_headers})
                    console.log("Making title:",res)

                    this.loading = false
                    this.setDiscussionLoading(id, this.loading)
                    if (res.status == 200) {
                        const index = this.list.findIndex((x) => x.id == id)
                        const discussionItem = this.list[index]
                        discussionItem.title = res.data.title
                        
                        this.tempList = this.list
                    }
                }
            } catch (error) {
                console.log("Error: Could not edit title", error.message)
                this.loading = false
                this.setDiscussionLoading(id, this.loading)
            }
        },        
        async delete_message(id) {
            try {
                console.log(typeof id)
                console.log(typeof this.client_id)
                console.log(id)
                console.log(this.client_id)
                const res = await axios.post('/delete_message', { client_id: this.client_id, id: id }, {headers: this.posts_headers})

                if (res) {
                    return res.data
                }
            } catch (error) {
                console.log("Error: Could delete message", error.message)
                return {}
            }
        },

        
        async stop_gen() {
            try {
                if (this.discussionArr.length>0)
                {
                    const messageItem = this.discussionArr[this.discussionArr.length-1]            
                    messageItem.status_message = "Generation canceled"
                }
                socket.emit('cancel_generation');
                //const res = await axios.get('/stop_gen')

                if (res) {
                    return res.data
                }
            } catch (error) {
                console.log("Error: Could not stop generating", error.message)
                return {}
            }
        },
        async message_rank_up(id) {
            try {
                const res = await axios.post('/message_rank_up', { client_id: this.client_id, id: id }, {headers: this.posts_headers})

                if (res) {
                    return res.data
                }
            } catch (error) {
                console.log("Error: Could not rank up message", error.message)
                return {}
            }
        },
        async message_rank_down(id) {
            try {
                const res = await axios.post('/message_rank_down', { client_id: this.client_id, id: id } , {headers: this.posts_headers})

                if (res) {
                    return res.data
                }
            } catch (error) {
                console.log("Error: Could not rank down message", error.message)
                return {}
            }
        },
        async edit_message(id, message, audio_url) {
            try {
                console.log(typeof this.client_id)
                console.log(typeof id)
                console.log(typeof message)
                console.log(typeof {audio_url:audio_url})
                const res = await axios.post('/edit_message', {
                                                            client_id: this.client_id, 
                                                            id: id, 
                                                            message: message,
                                                            metadata: [{audio_url:audio_url}]
                                                    }, {headers: this.posts_headers}
                )

                if (res) {
                    return res.data
                }
            } catch (error) {
                console.log("Error: Could not update message", error.message)
                return {}
            }
        },
        async export_multiple_discussions(discussionIdArr, export_format) {
            try {
                if (discussionIdArr.length > 0) {
                    const res = await axios.post('/export_multiple_discussions', {
                        client_id:this.$store.state.client_id,
                        discussion_ids: discussionIdArr,
                        export_format: export_format
                    }, {headers: this.posts_headers})

                    if (res) {
                        return res.data
                    }
                }

            } catch (error) {
                console.log("Error: Could not export multiple discussions", error.message)
                return {}
            }
        },
        async import_multiple_discussions(jArray_) {
            try {
                if (jArray_.length > 0) {
                    console.log('sending import', jArray_)
                    const res = await axios.post('/import_multiple_discussions', {
                        client_id: this.$store.state.client_id,
                        jArray: jArray_
                    }, {headers: this.posts_headers})

                    if (res) {
                        console.log('import response', res.data)
                        return res.data
                    }
                }

            } catch (error) {
                console.log("Error: Could not import multiple discussions", error.message)
                return
            }
        },
        filterDiscussions() {
            // Search bar in for filtering discussions by title (serch)

            if (!this.filterInProgress) {
                this.filterInProgress = true
                setTimeout(() => {
                    if (this.filterTitle) {
                        this.list = this.tempList.filter((item) => item.title && item.title.includes(this.filterTitle))

                    } else {
                        this.list = this.tempList
                    }
                    this.filterInProgress = false
                }, 100)
            }
        },
        async selectDiscussion(item) {
            if(this.isGenerating){
                this.$store.state.toast.showToast("You are currently generating a text. Please wait for text generation to finish or stop it before trying to select another discussion", 4, false)
                return;
            }

            if (item) {
                // When discussion is selected it loads the discussion array
                if (this.currentDiscussion===undefined) {
                    this.currentDiscussion = item

                    this.setPageTitle(item)

                    localStorage.setItem('selected_discussion', this.currentDiscussion.id)

                    this.load_discussion(item.id, ()=>{
                        if (this.discussionArr.length > 1) {
                        if (this.currentDiscussion.title === '' || this.currentDiscussion.title === null) {
                            this.changeTitleUsingUserMSG(this.currentDiscussion.id, this.discussionArr[1].content)
                        }
                        this.recoverFiles()
                    }
                    })

                }
                else{
                    if (this.currentDiscussion.id != item.id) {
                        console.log("item",item)
                        console.log("this.currentDiscussion",this.currentDiscussion)
                        this.currentDiscussion = item
                        console.log("this.currentDiscussion",this.currentDiscussion)

                        this.setPageTitle(item)

                        localStorage.setItem('selected_discussion', this.currentDiscussion.id)

                        this.load_discussion(item.id, ()=>{
                            if (this.discussionArr.length > 1) {
                                if (this.currentDiscussion.title === '' || this.currentDiscussion.title === null) {
                                    this.changeTitleUsingUserMSG(this.currentDiscussion.id, this.discussionArr[1].content)
                                }
                            }
                            this.recoverFiles()
                        });

                    }
                }

                nextTick(() => {


                    const discussionitem = document.getElementById('dis-' + this.currentDiscussion.id)

                    //this.scrollToElement(discussionitem)

                    this.scrollToElementInContainer(discussionitem, 'leftPanel')
                    const msgList = document.getElementById('messages-list')

                    this.scrollBottom(msgList)

                })
            }
        },

        scrollToElement(el) {

            if (el) {
                el.scrollIntoView({ behavior: 'smooth', block: 'start', inline: 'nearest' })
            } else {
                console.log("Error: scrollToElement")
            }
        },
        scrollToElementInContainer(el, containerId) {
            try{
                const topPos = el.offsetTop; //+ el.clientHeight
                const container = document.getElementById(containerId)
                // console.log(el.offsetTop , el.clientHeight, container.clientHeight)


                container.scrollTo(
                    {
                        top: topPos,
                        behavior: "smooth",
                    }
                )

            }
            catch{
                console.log("error")
            }

        },
        scrollBottom(el) {

            if (el) {
                el.scrollTo(
                    {
                        top: el.scrollHeight,
                        behavior: "smooth",
                    }
                )
            } else {
                console.log("Error: scrollBottom")
            }

        },

        scrollTop(el) {

            if (el) {
                el.scrollTo(
                    {
                        top: 0,
                        behavior: "smooth",
                    }
                )
            } else {
                console.log("Error: scrollTop")
            }

        },
        createUserMsg(msgObj) {

            let usrMessage = {
                content: msgObj.message,
                id: msgObj.id,
                rank: 0,
                sender: msgObj.user,
                created_at: msgObj.created_at,
                steps: [],
                html_js_s: [],
                status_message: "Warming up"

            }
            this.discussionArr.push(usrMessage)
            nextTick(() => {
                const msgList = document.getElementById('messages-list')

                this.scrollBottom(msgList)

            })
        },
        updateLastUserMsg(msgObj) {

            // const lastMsg = this.discussionArr[this.discussionArr.length - 1]
            // lastMsg.content = msgObj.message
            // lastMsg.id = msgObj.user_id
            // // lastMsg.parent=msgObj.parent
            // lastMsg.rank = msgObj.rank
            // lastMsg.sender = msgObj.user
            // // lastMsg.type=msgObj.type
            const index = this.discussionArr.indexOf(item => item.id = msgObj.user_id)
            const newMessage ={
                binding: msgObj.binding,
                content: msgObj.message,
                created_at: msgObj.created_at,
                type: msgObj.type,
                finished_generating_at: msgObj.finished_generating_at,
                id: msgObj.user_id,
                model: msgObj.model,
                personality: msgObj.personality,
                sender: msgObj.user,
                steps:[]
            }
            
            
            if (index !== -1) {
                this.discussionArr[index] = newMessage;
            }

        },
        socketIOConnected() {
            console.log("socketIOConnected")
            this.$store.state.isConnected=true;
            this.$store.state.client_id = socket.id
            return true
        },
        socketIODisconnected() {
            console.log("socketIOConnected")
            this.currentDiscussion=null
            this.$store.dispatch('refreshModels');
            this.$store.state.isConnected=false;
            return true
        },
        new_message(msgObj) {
            if(msgObj.sender_type==this.SENDER_TYPES_AI){
                this.isGenerating = true
            }
            console.log("Making a new message")
            console.log('New message', msgObj);
            
            let responseMessage = {
                sender:                 msgObj.sender,
                message_type:           msgObj.message_type,
                sender_type:            msgObj.sender_type,
                content:                msgObj.content,//"✍ please stand by ...",
                id:                     msgObj.id,
                discussion_id:          msgObj.discussion_id,
                parent_id:              msgObj.parent_id,

                binding:                msgObj.binding,
                model:                  msgObj.model,
                personality:            msgObj.personality,

                created_at:             msgObj.created_at,
                finished_generating_at: msgObj.finished_generating_at,
                rank:                   0,

                ui:                     msgObj.ui,

                steps                   : [],
                parameters              : msgObj.parameters,
                metadata                : msgObj.metadata,

                open                    : msgObj.open
            }
            
            responseMessage.status_message = "Warming up"
            console.log(responseMessage)
            this.discussionArr.push(responseMessage)
            // nextTick(() => {
            //     const msgList = document.getElementById('messages-list')

            //     this.scrollBottom(msgList)

            // })

            if (this.currentDiscussion.title === '' || this.currentDiscussion.title === null) {
                this.changeTitleUsingUserMSG(this.currentDiscussion.id, msgObj.message)
            }
            console.log("infos", msgObj)
            /*
            }
            else {
                this.$store.state.toast.showToast("It seems that no model has been loaded. Please download and install a model first, then try again.", 4, false)
                this.isGenerating = false
                this.setDiscussionLoading(this.currentDiscussion.id, this.isGenerating)
                this.chime.play()
            }*/
        },
        async talk(pers){
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
        createEmptyUserMessage(message){
            socket.emit('create_empty_message', {"type":0,"message":message}); // 0 for user and 1 for AI
        },
        createEmptyAIMessage(){
            socket.emit('create_empty_message', {"type":1}); // 0 for user and 1 for AI
        },
        sendMsg(msg,type) {
            // Sends message to binding
            if (!msg) {
                this.$store.state.toast.showToast("Message contains no content!", 4, false)
                return
            }
            this.isGenerating = true;
            this.setDiscussionLoading(this.currentDiscussion.id, this.isGenerating);
            axios.get('/get_generation_status', {}).then((res) => {
                if (res) {
                    //console.log(res.data.status);
                    if (!res.data.status) {
                        if(type=="internet"){
                            socket.emit('generate_msg_with_internet', { prompt: msg });
                        }
                        else{
                            socket.emit('generate_msg', { prompt: msg });
                        }

                        // Create new User message
                        // Temp data
                        let lastmsgid =0
                        if(this.discussionArr.length>0){
                            lastmsgid= Number(this.discussionArr[this.discussionArr.length - 1].id) + 1
                        }
                        
                        
                        let usrMessage = {
                            message: msg,
                            id: lastmsgid,
                            rank: 0,
                            user: this.$store.state.config.user_name,
                            created_at: new Date().toLocaleString(),


                            sender:                 this.$store.state.config.user_name,
                            message_type:           this.msgTypes.MSG_TYPE_FULL,
                            sender_type:            this.senderTypes.SENDER_TYPES_USER,
                            content:                msg,
                            id:                     lastmsgid,
                            discussion_id:          this.discussion_id,
                            parent_id:              lastmsgid,

                            binding:                "",
                            model:                  "",
                            personality:            "",

                            created_at:             new Date().toLocaleString(),
                            finished_generating_at: new Date().toLocaleString(),
                            rank:                   0,

                            steps:                  [],
                            parameters:             null,
                            metadata:               [],
                            ui:                     null

                        };
                        this.createUserMsg(usrMessage);

                    }
                    else {
                        console.log("Already generating");
                    }
                }
            }).catch((error) => {
                console.log("Error: Could not get generation status", error);
            });
        },
        sendCmd(cmd){
            this.isGenerating = true;
            // axios.post('/execute_personality_command', {command: cmd, parameters:[]})
            //     .then((res) => {
            //         if (res) {
            //             if (res.status) {
            //                 this.$store.state.toast.showToast("Command executed",4,true)
            //             }
            //             else
            //                 this.$store.state.messageBox.showMessage("Error: Couldn't execute command!")
            //             return res.data;
            //         }
            //     })
            //     .catch(error => {
            //         console.log(error.message, 'save_configuration')
            //         this.$store.state.messageBox.showMessage("Couldn't save settings!")
                    
            //     });
            
            socket.emit('execute_command', { command: cmd, parameters: [] });            
        },
        notify(notif){
            self.isGenerating = false
            this.setDiscussionLoading(this.currentDiscussion.id, this.isGenerating);
            nextTick(() => {
                const msgList = document.getElementById('messages-list')
                this.scrollBottom(msgList)
            })
            if(notif.display_type==0){
                this.$store.state.toast.showToast(notif.content, notif.duration, notif.notification_type)
            }
            else if(notif.display_type==1){
                this.$store.state.messageBox.showMessage(notif.content)
            }
            else if(notif.display_type==2){
                this.$store.state.messageBox.hideMessage()
                this.$store.state.yesNoDialog.askQuestion(notif.content, 'Yes', 'No').then(yesRes => {
                    socket.emit("yesNoRes",{yesRes:yesRes})
                })
            }
            else if(notif.display_type==3){
                this.$store.state.messageBox.showBlockingMessage(notif.content)
            }
            else if(notif.display_type==4){
                this.$store.state.messageBox.hideMessage()
            }
            
            this.chime.play()
        },
        streamMessageContent(msgObj) {
            // Streams response message content from binding
            this.discussion_id = msgObj.discussion_id
            this.setDiscussionLoading(this.discussion_id, true);
            if (this.currentDiscussion.id == this.discussion_id) {
                //this.isGenerating = true;
                const index = this.discussionArr.findIndex((x) => x.id == msgObj.id)
                const messageItem = this.discussionArr[index]
                
                if (
                    messageItem && (msgObj.message_type==this.msgTypes.MSG_TYPE_FULL ||
                    msgObj.message_type==this.msgTypes.MSG_TYPE_FULL_INVISIBLE_TO_AI)
                ) {
                    this.isGenerating = true;
                    messageItem.content = msgObj.content
                    messageItem.created_at = msgObj.created_at
                    messageItem.started_generating_at = msgObj.started_generating_at
                    messageItem.nb_tokens = msgObj.nb_tokens
                    messageItem.finished_generating_at = msgObj.finished_generating_at
                    this.extractHtml()
                }
                else if(messageItem && msgObj.message_type==this.msgTypes.MSG_TYPE_CHUNK){
                    this.isGenerating = true;
                    messageItem.content += msgObj.content
                    messageItem.created_at = msgObj.created_at
                    messageItem.started_generating_at = msgObj.started_generating_at
                    messageItem.nb_tokens = msgObj.nb_tokens
                    messageItem.finished_generating_at = msgObj.finished_generating_at
                    this.extractHtml()
                } else if (msgObj.message_type == this.msgTypes.MSG_TYPE_STEP){
                    messageItem.status_message = msgObj.content
                    messageItem.steps.push({"message":msgObj.content,"done":true, "status":true, "type": "instantanious" })
                } else if (msgObj.message_type == this.msgTypes.MSG_TYPE_STEP_START){
                    messageItem.status_message = msgObj.content
                    messageItem.steps.push({"message":msgObj.content,"done":false, "status":true, "type": "start_end" })
                } else if (msgObj.message_type == this.msgTypes.MSG_TYPE_STEP_END) {
                    console.log("received step end", msgObj)
                    try{

                        // Iterate over each step and update the 'done' property if the message matches msgObj.content
                        messageItem.steps.forEach(step => {
                            if (step.message === msgObj.content) {
                                step.done = true;
                                try {
                                    console.log(msgObj.parameters)
                                    const parameters = msgObj.parameters;
                                    if(parameters !== undefined){
                                        step.status = parameters.status;
                                        console.log(parameters);
                                    }
                                    
                                } catch (error) {
                                    console.error('Error parsing JSON:', error.message);
                                }
                            }
                        });

                    }
                    catch{
                        console.log("error")
                    }
                } else if (msgObj.message_type == this.msgTypes.MSG_TYPE_JSON_INFOS) {
                    console.log("JSON message")
                    console.log(msgObj.metadata)
                    messageItem.metadata = msgObj.metadata
                } else if (msgObj.message_type == this.msgTypes.MSG_TYPE_UI) {
                    console.log("UI message")
                    messageItem.ui = msgObj.ui
                } else if (msgObj.message_type == this.msgTypes.MSG_TYPE_EXCEPTION) {
                    this.$store.state.toast.showToast(msgObj.content, 5, false)
                }
                // // Disables as per request
                // nextTick(() => {
                //     const msgList = document.getElementById('messages-list')
                //     this.scrollBottom(msgList)
                // })
            }
            // Force an immediate UI update
            this.$nextTick(() => {
                // UI updates are rendered here
                feather.replace()
            });

        },
        async changeTitleUsingUserMSG(id, msg) {
            // If discussion is untitled or title is null then it sets the title to first user message.

            const index = this.list.findIndex((x) => x.id == id)
            const discussionItem = this.list[index]
            if (msg) {
                discussionItem.title = msg
                this.tempList = this.list
                await this.edit_title(id, msg)
            }

        },
        async createNewDiscussion() {
            // Creates new discussion on binding,
            // gets new discussion list, selects
            // newly created discussion,
            // scrolls to the discussion
            this.new_discussion(null)
        },
        loadLastUsedDiscussion() {
            // Checks local storage for last selected discussion
            console.log("Loading last discussion")
            const id = localStorage.getItem('selected_discussion')
            console.log("Last discussion id: ",id)
            if (id) {
                const index = this.list.findIndex((x) => x.id == id)
                const discussionItem = this.list[index]
                if (discussionItem) {
                    this.selectDiscussion(discussionItem)
                }
            }
        },        
        onCopyPersonalityName(personality) {
            this.$store.state.toast.showToast("Copied name to clipboard!", 4, true)
            navigator.clipboard.writeText(personality.name);
        },
        async deleteDiscussion(id) {
            // Deletes discussion from binding and frontend

            await this.delete_discussion(id)
            if (this.currentDiscussion.id == id) {
                this.currentDiscussion = {}
                this.discussionArr = []
                this.setPageTitle()
            }
            this.list.splice(this.list.findIndex(item => item.id == id), 1)

            this.createDiscussionList(this.list)
        },
        async deleteDiscussionMulti() {
            // Delete selected discussions

            const deleteList = this.selectedDiscussions

            for (let i = 0; i < deleteList.length; i++) {
                const discussionItem = deleteList[i]
                //discussionItem.loading = true
                await this.delete_discussion(discussionItem.id)
                if (this.currentDiscussion.id == discussionItem.id) {
                    this.currentDiscussion = {}
                    this.discussionArr = []
                    this.setPageTitle()
                }
                this.list.splice(this.list.findIndex(item => item.id == discussionItem.id), 1)
            }
            this.tempList = this.list
            this.isCheckbox = false
            this.$store.state.toast.showToast("Removed (" + deleteList.length + ") items", 4, true)
            this.showConfirmation = false
            console.log("Multi delete done")
        },
        async deleteMessage(msgId) {

            await this.delete_message(msgId).then(() => {

                this.discussionArr.splice(this.discussionArr.findIndex(item => item.id == msgId), 1)

            }).catch(() => {
                this.$store.state.toast.showToast("Could not remove message", 4, false)
                console.log("Error: Could not delete message")
            })

        },
        async openFolder(id){
            const json = JSON.stringify({ 'client_id': this.$store.state.client_id, 'discussion_id': id.id })   
            console.log(json)     
            await axios.post(`/open_discussion_folder`, json, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
            })
        },
        async editTitle(newTitleObj) {

            const index = this.list.findIndex((x) => x.id == newTitleObj.id)
            const discussionItem = this.list[index]
            discussionItem.title = newTitleObj.title
            discussionItem.loading = true
            await this.edit_title(newTitleObj.id, newTitleObj.title)
            discussionItem.loading = false
        },
        async makeTitle(editTitleObj) {
            const index = this.list.findIndex((x) => x.id == editTitleObj.id)
            await this.make_title(editTitleObj.id)
        },

        checkUncheckDiscussion(event, id) {
            // If checked = true and item is not in array then add item to list
            const index = this.list.findIndex((x) => x.id == id)
            const discussionItem = this.list[index]
            discussionItem.checkBoxValue = event.target.checked
            this.tempList = this.list
        },
        selectAllDiscussions() {

            // Check if there is one discussion not selected
            this.isSelectAll = !this.tempList.filter((item) => item.checkBoxValue == false).length > 0
            // Selects or deselects all discussions
            for (let i = 0; i < this.tempList.length; i++) {
                this.tempList[i].checkBoxValue = !this.isSelectAll
            }

            this.tempList = this.list
            this.isSelectAll = !this.isSelectAll
        },
        createDiscussionList(disList) {
            // This creates a discussion list for UI with additional properties
            if (disList) {
                const newDisList = disList.map((item) => {

                    const newItem = {
                        id: item.id,
                        title: item.title,
                        selected: false,
                        loading: false,
                        checkBoxValue: false
                    }
                    return newItem

                }).sort(function (a, b) {
                    return b.id - a.id
                })

                this.list = newDisList
                this.tempList = newDisList
            }
        },
        setDiscussionLoading(id, loading) {
            try{
                const index = this.list.findIndex((x) => x.id == id)
                const discussionItem = this.list[index]
                discussionItem.loading = loading
            }
            catch{
                console.log("Error setting discussion loading")
            }
        },
        setPageTitle(item) {
            // item is either title:String or {id:Number, title:String}
            if (item) {
                if (item.id) {
                    const realTitle = item.title ? item.title === "untitled" ? "New discussion" : item.title : "New discussion"
                    document.title = 'LoLLMS WebUI - ' + realTitle
                } else {
                    const title = item || "Welcome"
                    document.title = 'LoLLMS WebUI - ' + title
                }
            } else {
                const title = item || "Welcome"
                document.title = 'LoLLMS WebUI - ' + title
            }

        },
        async rankUpMessage(msgId) {
            await this.message_rank_up(msgId).then((res) => {

                const message = this.discussionArr[this.discussionArr.findIndex(item => item.id == msgId)]
                message.rank = res.new_rank
            }).catch(() => {
                this.$store.state.toast.showToast("Could not rank up message", 4, false)
                console.log("Error: Could not rank up message")
            })

        },
        async rankDownMessage(msgId) {
            await this.message_rank_down(msgId).then((res) => {

                const message = this.discussionArr[this.discussionArr.findIndex(item => item.id == msgId)]
                message.rank = res.new_rank
            }).catch(() => {
                this.$store.state.toast.showToast("Could not rank down message", 4, false)

                console.log("Error: Could not rank down message")
            })

        },
        async updateMessage(msgId, msg, audio_url) {
            await this.edit_message(msgId, msg, audio_url).then(() => {

                const message = this.discussionArr[this.discussionArr.findIndex(item => item.id == msgId)]
                message.content = msg

            }).catch(() => {
                this.$store.state.toast.showToast("Could not update message", 4, false)

                console.log("Error: Could not update message")
            })

        },
        resendMessage(msgId, msg, msg_type) {
            nextTick(() => {
                feather.replace()

            })
            // Resend message
            this.isGenerating = true;
            this.setDiscussionLoading(this.currentDiscussion.id, this.isGenerating);
            axios.get('/get_generation_status', {}).then((res) => {
                if (res) {
                    if (!res.data.status) {
                        socket.emit('generate_msg_from', { prompt: msg, id: msgId, msg_type: msg_type });
                    }
                    else {
                        this.$store.state.toast.showToast("The server is busy. Wait", 4, false)
                        console.log("Already generating");
                    }
                }
            }).catch((error) => {
                console.log("Error: Could not get generation status", error);
            });
        },
        continueMessage(msgId, msg) {
            nextTick(() => {
                feather.replace()

            })
            // Resend message
            this.isGenerating = true;
            this.setDiscussionLoading(this.currentDiscussion.id, this.isGenerating);
            axios.get('/get_generation_status', {}).then((res) => {
                if (res) {
                    if (!res.data.status) {
                        socket.emit('continue_generate_msg_from', { prompt: msg, id: msgId });


                    }
                    else {
                        console.log("Already generating");
                    }
                }
            }).catch((error) => {
                console.log("Error: Could not get generation status", error);
            });
        },
        stopGenerating() {
            this.stop_gen()
            this.isGenerating = false
            this.setDiscussionLoading(this.currentDiscussion.id, this.isGenerating)
            console.log("Stopped generating")
            nextTick(() => {
                const msgList = document.getElementById('messages-list')
                this.scrollBottom(msgList)
            })
        },
        finalMsgEvent(msgObj) {
            let index=0;
            // Last message contains halucination suppression so we need to update the message content too
            this.discussion_id = msgObj.discussion_id
            if (this.currentDiscussion.id == this.discussion_id) {
                index = this.discussionArr.findIndex((x) => x.id == msgObj.id)
                this.discussionArr[index].content = msgObj.content
                this.discussionArr[index].finished_generating_at = msgObj.finished_generating_at

                // const messageItem = this.discussionArr[index]
                // if (messageItem) {
                //     messageItem.content = msgObj.content
                // }
            }
            nextTick(() => {
                const msgList = document.getElementById('messages-list')
                this.scrollBottom(msgList)
                this.recoverFiles()
            })


            this.isGenerating = false
            this.setDiscussionLoading(this.currentDiscussion.id, this.isGenerating)
            this.chime.play()
            index = this.discussionArr.findIndex((x) => x.id == msgObj.id)
            const messageItem = this.discussionArr[index]            
            messageItem.status_message = "Done"
            console.log("final", msgObj)
            if(this.$store.state.config.auto_speak && (this.$store.state.config.xtts_enable && this.$store.state.config.xtts_use_streaming_mode)){
                index = this.discussionArr.findIndex((x) => x.id == msgObj.id)
                let message_component = this.$refs['msg-' + msgObj.id][0]
                console.log(message_component)
                message_component.speak()
            }

        },
        copyToClipBoard(messageEntry) {
            let content = ""
            if (messageEntry.message.content) {
                content = messageEntry.message.content
            }


            if(this.$store.state.config.copy_to_clipboard_add_all_details){
                let binding = ""
                if (messageEntry.message.binding) {
                    binding = `Binding: ${messageEntry.message.binding}`
                }
                let personality = ""
                if (messageEntry.message.personality) {
                    personality = `\nPersonality: ${messageEntry.message.personality}`
                }
                let time = ""
                if (messageEntry.created_at_parsed) {
                    time = `\nCreated: ${messageEntry.created_at_parsed}`
                }
                let model = ""
                if (messageEntry.message.model) {
                    model = `Model: ${messageEntry.message.model}`
                }
                let seed = ""
                if (messageEntry.message.seed) {
                    seed = `Seed: ${messageEntry.message.seed}`
                }
                let time_spent = ""
                if (messageEntry.time_spent) {
                    time_spent = `\nTime spent: ${messageEntry.time_spent}`
                }                
                let bottomRow = ''
                bottomRow = `${binding} ${model} ${seed} ${time_spent}`.trim()
                const result = `${messageEntry.message.sender}${personality}${time}\n\n${content}\n\n${bottomRow}`

                navigator.clipboard.writeText(result);
            }
            else{
                navigator.clipboard.writeText(content);
            }



            this.$store.state.toast.showToast("Copied to clipboard successfully", 4, true)

            nextTick(() => {
                feather.replace()

            })
        },
        closeToast() {
            this.showToast = false
        },
        saveJSONtoFile(jsonData, filename) {
            filename = filename || "data.json"
            const a = document.createElement("a");
            a.href = URL.createObjectURL(new Blob([JSON.stringify(jsonData, null, 2)], {
                type: "text/plain"
            }));
            a.setAttribute("download", filename);
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
        },
        saveMarkdowntoFile(markdownData, filename) {
            filename = filename || "data.md"
            const a = document.createElement("a");
            a.href = URL.createObjectURL(new Blob([markdownData], {
                type: "text/plain"
            }));
            a.setAttribute("download", filename);
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
        },
        parseJsonObj(obj) {
            try {
                const ret = JSON.parse(obj)
                return ret
            } catch (error) {
                this.$store.state.toast.showToast("Could not parse JSON. \n" + error.message, 4, false)
                return null
            }

        },
        async parseJsonFile(file) {

            return new Promise((resolve, reject) => {
                const fileReader = new FileReader()
                fileReader.onload = event => resolve(this.parseJsonObj(event.target.result))
                fileReader.onerror = error => reject(error)
                fileReader.readAsText(file)
            })
        },
        
        async exportDiscussionsAsMarkdown() {
            // Export selected discussions

            const discussionIdArr = this.list.filter((item) => item.checkBoxValue == true).map((item) => {
                return item.id
            })

            if (discussionIdArr.length > 0) {
                console.log("export", discussionIdArr)
                let dateObj = new Date()

                const year = dateObj.getFullYear();
                const month = (dateObj.getMonth() + 1).toString().padStart(2, "0");
                const day = dateObj.getDate().toString().padStart(2, "0");
                const hours = dateObj.getHours().toString().padStart(2, "0");
                const minutes = dateObj.getMinutes().toString().padStart(2, "0");
                const seconds = dateObj.getSeconds().toString().padStart(2, "0");
                const formattedDate =
                    year +
                    "." +
                    month +
                    "." +
                    day +
                    "." +
                    hours +
                    "" +
                    minutes +
                    "" +
                    seconds;

                const filename = 'discussions_export_' + formattedDate + '.md'
                this.loading = true
                const res = await this.export_multiple_discussions(discussionIdArr,"markdown")

                if (res) {
                    this.saveMarkdowntoFile(res, filename)
                    this.$store.state.toast.showToast("Successfully exported", 4, true)
                    this.isCheckbox = false
                } else {
                    this.$store.state.toast.showToast("Failed to export discussions", 4, false)
                }
                this.loading = false
            }

        },
        async exportDiscussions(){

        },
        async exportDiscussionsAsJson() {
            // Export selected discussions

            const discussionIdArr = this.list.filter((item) => item.checkBoxValue == true).map((item) => {
                return item.id
            })

            if (discussionIdArr.length > 0) {
                console.log("export", discussionIdArr)
                let dateObj = new Date()

                const year = dateObj.getFullYear();
                const month = (dateObj.getMonth() + 1).toString().padStart(2, "0");
                const day = dateObj.getDate().toString().padStart(2, "0");
                const hours = dateObj.getHours().toString().padStart(2, "0");
                const minutes = dateObj.getMinutes().toString().padStart(2, "0");
                const seconds = dateObj.getSeconds().toString().padStart(2, "0");
                const formattedDate =
                    year +
                    "." +
                    month +
                    "." +
                    day +
                    "." +
                    hours +
                    "" +
                    minutes +
                    "" +
                    seconds;

                const filename = 'discussions_export_' + formattedDate + '.json'
                this.loading = true
                const res = await this.export_multiple_discussions(discussionIdArr, "json")

                if (res) {
                    this.saveJSONtoFile(res, filename)
                    this.$store.state.toast.showToast("Successfully exported", 4, true)
                    this.isCheckbox = false
                } else {
                    this.$store.state.toast.showToast("Failed to export discussions", 4, false)
                }
                this.loading = false
            }

        },
        async importDiscussionsBundle(event){

        },
        async importDiscussions(event) {
            const obj = await this.parseJsonFile(event.target.files[0])

            const res = await this.import_multiple_discussions(obj)
            if (res) {
                this.$store.state.toast.showToast("Successfully imported (" + obj.length + ")", 4, true)
                await this.list_discussions()
            } else {
                this.$store.state.toast.showToast("Failed to import discussions", 4, false)
            }



        },
        async getPersonalityAvatars() {
            while (this.$store.state.personalities === null) {
                await new Promise((resolve) => setTimeout(resolve, 100)); // Wait for 100ms
            }  
            let personalities = this.$store.state.personalities

            this.personalityAvatars = personalities.map(item => {
                const newItem = {
                    name: item.name,
                    avatar: item.avatar
                }
                return newItem
            })
        },
        getAvatar(sender) {
            if (sender.toLowerCase().trim() == this.$store.state.config.user_name.toLowerCase().trim()){
                return "user_infos/"+this.$store.state.config.user_avatar
            }
            const index = this.personalityAvatars.findIndex((x) => x.name === sender)
            const pers = this.personalityAvatars[index]
            if (pers) {
                console.log("Avatar",pers.avatar)
                return pers.avatar
            }

            return
        },
        setFileListChat(files) {


            try {
                this.$refs.chatBox.fileList = this.$refs.chatBox.fileList.concat(files)
            } catch (error) {
                this.$store.state.toast.showToast("Failed to set filelist in chatbox\n" + error.message, 4, false)

            }


            this.isDragOverChat = false


        },
        async setFileListDiscussion(files) {

            if (files.length > 1) {
                this.$store.state.toast.showToast("Failed to import discussions. Too many files", 4, false)
                return
            }
            const obj = await this.parseJsonFile(files[0])

            const res = await this.import_multiple_discussions(obj)
            if (res) {
                this.$store.state.toast.showToast("Successfully imported (" + obj.length + ")", 4, true)
                await this.list_discussions()
            } else {
                this.$store.state.toast.showToast("Failed to import discussions", 4, false)
            }


            this.isDragOverDiscussion = false
        },
    },
    async created() {
        const response = await axios.get('/get_versionID');
        const serverVersionId = response.data.versionId;
        if (this.versionId !== serverVersionId) {
            // Update the store value
            this.$store.commit('updateVersionId', serverVersionId);
            
            // Force a page refresh
            window.location.reload(true);
        }
        this.$nextTick(() => {
            feather.replace();
        });           
        socket.on('disucssion_renamed',(event)=>{
            console.log('Received new title', event.discussion_id, event.title);
            const index = this.list.findIndex((x) => x.id == event.discussion_id)
            const discussionItem = this.list[index]
            discussionItem.title = event.title
            /*
            {
            'status': True,
            'discussion_id':d.id,
            'title':title
            }*/
        })
        socket.onclose = (event) => {
            console.log('WebSocket connection closed:', event.code, event.reason);
            this.socketIODisconnected();
        };
        socket.on("connect_error", (error) => {
            if (error.message === "ERR_CONNECTION_REFUSED") {
            console.error("Connection refused. The server is not available.");
            // Handle the ERR_CONNECTION_REFUSED error here
            } else {
            console.error("Connection error:", error);
            // Handle other connection errors here
            }
            this.$store.state.isConnected = false
        });        
        socket.onerror = (event) => {
            console.log('WebSocket connection error:', event.code, event.reason);
            this.socketIODisconnected();
            socket.disconnect();
        };
        socket.on('connected',this.socketIOConnected)
        socket.on('disconnected',this.socketIODisconnected)
        console.log("Added events")
        
        
        console.log("Waiting to be ready")
        while (this.$store.state.ready === false) {
            await new Promise((resolve) => setTimeout(resolve, 100)); // Wait for 100ms
        }          
        console.log("Ready")
        // Constructor
        this.setPageTitle()
        await this.list_discussions()
        this.loadLastUsedDiscussion()


        // socket responses
        socket.on('show_progress', this.show_progress)
        socket.on('hide_progress', this.hide_progress)
        socket.on('update_progress', this.update_progress)
        
        socket.on('notification', this.notify)
        socket.on('new_message', this.new_message)
        socket.on('update_message', this.streamMessageContent)
        socket.on('close_message', this.finalMsgEvent)

        socket.onopen = () => {
            console.log('WebSocket connection established.');
            if (this.currentDiscussion!=null){
                this.setPageTitle(item)
                localStorage.setItem('selected_discussion', this.currentDiscussion.id)
                this.load_discussion(item.id, ()=>{
                    if (this.discussionArr.length > 1) {
                        if (this.currentDiscussion.title === '' || this.currentDiscussion.title === null) {
                            this.changeTitleUsingUserMSG(this.currentDiscussion.id, this.discussionArr[1].content)
                        }
                    }
                });
            }
        };

        this.isCreated = true
    },
    async mounted() {
        // let serverAddress = "http://localhost:9600/";
        // try {
        //     const response = await fetch('/get_server_address'); // Replace with the actual endpoint on your Flask server
        //     serverAddress = await response.text();
        //     if(serverAddress.includes('<')){
        //         console.log(`Server address not found`)
        //         serverAddress = "http://localhost:9600/"//process.env.VITE_LOLLMS_API
                
        //     }
        //     console.log(`Server address: ${serverAddress}`)
        // } catch (error) {
        //     console.error('Error fetching server address:', error);
            // Handle error if necessary
        //     serverAddress = "http://localhost:9600/"
        // }
        // this.host = `${serverAddress}`; // Construct the full server address dynamically
        // axios.defaults.baseURL = serverAddress
        //console.log('chatbox mnt',this.$refs)
        socket.on('refresh_files',()=>{
            this.recoverFiles()
        })
        this.$nextTick(() => {
            feather.replace();
        });
    },
    async activated() {
        //console.log('settings changed acc', this.$store.state.settingsChanged)
        // await this.getPersonalityAvatars()
        while (this.isReady === false) {
                await new Promise((resolve) => setTimeout(resolve, 100)); // Wait for 100ms
            }  
        await this.getPersonalityAvatars()
        console.log("Avatars found:",this.personalityAvatars)
        if (this.isCreated) {
           // this.loadLastUsedDiscussion()
            nextTick(() => {

                const msgList = document.getElementById('messages-list')

                this.scrollBottom(msgList)

            })
        }
        if (this.$store.state.config.show_news_panel)
            this.$store.state.news.show()
    },
    components: {
        Discussion,
        Message,
        ChatBox,
        WelcomeComponent,
        ChoiceDialog,
        ProgressBar,
        InputBox,
        SkillsLibraryViewer 
    },
    watch: {  
        messages: {
        handler: 'extractHtml',
        deep: true
        },
        progress_visibility_val(newVal) {
            console.log("progress_visibility changed to "+ newVal)
        },
        filterTitle(newVal) {
            if (newVal == '') {
                this.filterInProgress = true
                this.list = this.tempList
                this.filterInProgress = false
            }
        },
        isCheckbox(newval) {
            nextTick(() => {
                feather.replace()
            })
            if (!newval) {
                this.isSelectAll = false
            }
        },
        socketConnected(newval) {
            console.log("Websocket connected (watch)", newval)
        },
        showConfirmation() {
            nextTick(() => {
                feather.replace()

            })
        },
        isSearch() {
            nextTick(() => {
                feather.replace()

            })
        },
        
    },
    computed: { 
        ...mapState({
            versionId: state => state.versionId,
        }),
        progress_visibility: {
            get(){
                return self.progress_visibility_val;
            }
        },        
        version_info:{
            get(){
                if(this.$store.state.version!=undefined && this.$store.state.version!="unknown"){
                    return " v" + this.$store.state.version;
                }
                else{
                    return "";
                }
            }
        },
        
        loading_infos:{
            get(){
                return this.$store.state.loading_infos;
            }
        },
        loading_progress:{
            get(){
                return this.$store.state.loading_progress;
            }
        },
        isModelOk:{
            get(){
                return this.$store.state.isModelOk;
            },
            set(val){
                this.$store.state.isModelOk=val
            }
        },
        isGenerating:{
            get(){
                return this.$store.state.isGenerating;
            },
            set(val){
                this.$store.state.isGenerating=val
            }
        },
        formatted_database_name() {
            const db_name = this.$store.state.config.discussion_db_name;
            const trimmed_name = db_name;
            return trimmed_name;
        },
        UseDiscussionHistory() {
            return this.$store.state.config.activate_skills_lib;
        }, 
        isReady() {
                return this.$store.state.ready;
        },
        databases(){            
            return this.$store.state.databases;
        },
        client_id() {
            return socket.id
        },
        showLeftPanel() {
           return this.$store.state.ready && !this.leftPanelCollapsed;
        },
        showRightPanel() {
           return this.$store.state.ready && !this.rightPanelCollapsed;
        },
        socketConnected() {
            console.log(" --- > Websocket connected")
            this.$store.commit('setIsConnected', true);
            return true
        },
        socketDisconnected() {
            this.$store.commit('setIsConnected', false);
            console.log(" --- > Websocket disconnected")
            return true
        },
        selectedDiscussions() {
            nextTick(() => {
                feather.replace()

            })
            return this.list.filter((item) => item.checkBoxValue == true)
        }
    }
}
</script>

<script setup>


import Discussion from '../components/Discussion.vue'
import ChoiceDialog from '@/components/ChoiceDialog.vue'
import ProgressBar from "@/components/ProgressBar.vue";
import InputBox from "@/components/input_box.vue";
import SkillsLibraryViewer from "@/components/SkillsViewer.vue"

import Message from '../components/Message.vue'
import ChatBox from '../components/ChatBox.vue'
import WelcomeComponent from '../components/WelcomeComponent.vue'

import feather from 'feather-icons'

import axios from 'axios'
import { nextTick, TransitionGroup } from 'vue'

import socket from '@/services/websocket.js'


import { onMounted } from 'vue'
import { initFlowbite } from 'flowbite'
import { store } from '../main'



// initialize components based on data attribute selectors
onMounted(() => {
    initFlowbite()
})

axios.defaults.baseURL = import.meta.env.VITE_LOLLMS_API_BASEURL
</script>
