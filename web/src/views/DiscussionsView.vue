<template>
    <transition name="fade-and-fly">
    <div v-if="!isReady" class="fixed top-0 left-0 w-screen h-screen flex items-center justify-center">
        <!-- SPINNER -->
     
        <div class="flex flex-col text-center">
            <div class="flex flex-col text-center items-center">
                
                <div class="flex items-center gap-3 text-5xl drop-shadow-md align-middle pt-24 ">
                
                    <img class="w-24 animate-bounce" title="LoLLMS WebUI" src="@/assets/logo.png" alt="Logo">
                        <div class="flex flex-col items-start">
                        <p class="text-2xl ">Lord of Large Language Models v {{ store.state.version }} </p>
                        <p class="text-gray-400 text-base">One tool to rule them all</p>
                        <p class="text-gray-400 text-base">by ParisNeo</p>

                        </div>
                </div>
                <hr
                    class=" mt-1 w-96 h-1 mx-auto my-2 md:my-2 dark:bg-bg-dark-tone-panel bg-bg-light-tone-panel border-0 rounded ">
                    <p class="text-2xl">Welcome</p>
                    <div role="status" class="text-center w-full display: flex; flex-row align-items: center;">
                            <p class="text-2xl animate-pulse">Loading ...</p>
                    </div> 

            </div>

        </div>  
    </div>

  
    </transition>
    <button v-if="isReady" @click="togglePanel" class="absolute top-0 left-0 z-50 p-2 m-2 bg-white rounded-full shadow-md  bg-bg-light-tone dark:bg-bg-dark-tone hover:bg-primary-light dark:hover:bg-primary">
                    <div v-show="panelCollapsed" ><i data-feather='chevron-right'></i></div>
                    <div v-show="!panelCollapsed" ><i data-feather='chevron-left'></i></div>
    </button>        
    <transition name="slide-right">
    <div  v-if="showPanel"
        class="relative flex flex-col no-scrollbar shadow-lg min-w-[24rem] max-w-[24rem] bg-bg-light-tone dark:bg-bg-dark-tone"
        >
        <!-- LEFT SIDE PANEL -->
        <div id="leftPanel" class="flex flex-col flex-grow overflow-y-scroll no-scrollbar "
            @dragover.stop.prevent="setDropZoneDiscussion()">
            <div class=" sticky z-10 top-0  bg-bg-light-tone dark:bg-bg-dark-tone shadow-md ">




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
                        <i data-feather="refresh-ccw"></i>
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
                    
                    <div v-if="isOpen" class="dropdown">
                      <button @click="importDiscussions">LOLLMS</button> 
                      <button @click="importChatGPT">ChatGPT</button>
                    </div>
                    <button class="text-2xl hover:text-secondary duration-75 active:scale-90" title="Filter discussions"
                        type="button" @click="isSearch = !isSearch" :class="isSearch ? 'text-secondary' : ''">
                        <i data-feather="search"></i>
                    </button>
                    <button  v-if="!showSaveConfirmation" title="Save configuration" class="text-2xl hover:text-secondary duration-75 active:scale-90"
                        @click="showSaveConfirmation = true">
                        <i data-feather="save"></i>
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
                    <button  v-if="!showBrainConfirmation" title="Activate Long term Memory" class="text-2xl hover:text-secondary duration-75 active:scale-90"
                        @click="toggleLTM()">
                        <img v-if="loading" :src="SVGOrangeBrain" width="25" height="25" class="animate-pulse" title="Applying config, please stand by...">
                        <img v-else-if="UseDiscussionHistory" :src="SVGGreenBrain" width="25" height="25">
                        <img v-else :src="SVGRedBrain" width="25" height="25">
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
                                <i data-feather="log-out"></i>
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
            <div class="relative flex flex-row flex-grow mb-10 z-0">

                <!-- DISCUSSION LIST -->
                <div class="mx-4 flex flex-col flex-grow " :class="isDragOverDiscussion ? 'pointer-events-none' : ''">


                    <div id="dis-list" :class="filterInProgress ? 'opacity-20 pointer-events-none' : ''"
                        class="flex flex-col flex-grow  ">
                        <TransitionGroup v-if="list.length > 0" name="list">
                            <Discussion v-for="(item, index) in list" :key="item.id" :id="item.id" :title="item.title"
                                :selected="currentDiscussion.id == item.id" :loading="item.loading" :isCheckbox="isCheckbox"
                                :checkBoxValue="item.checkBoxValue" 
                                @select="selectDiscussion(item)"
                                @delete="deleteDiscussion(item.id)" 
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
        <div class="absolute bottom-0 left-0 w-full bg-blue-200 dark:bg-blue-800 text-white py-2 cursor-pointer hover:text-green-500" @click="showDatabaseSelector">
            <p class="ml-2">Current database: {{ formatted_database_name }}</p>
        </div>
    </div>
    </transition>
    <div v-if="isReady" class="relative flex flex-col flex-grow " >
        <div id="messages-list"
            class=" z-0 flex flex-col  flex-grow  overflow-y-auto scrollbar-thin scrollbar-track-bg-light-tone scrollbar-thumb-bg-light-tone-panel hover:scrollbar-thumb-primary dark:scrollbar-track-bg-dark-tone dark:scrollbar-thumb-bg-dark-tone-panel dark:hover:scrollbar-thumb-primary active:scrollbar-thumb-secondary"
            :class="isDragOverChat ? 'pointer-events-none' : ''">

            <!-- CHAT AREA -->
            <div class=" container pt-4 pb-10 mb-28">
                <TransitionGroup v-if="discussionArr.length > 0" name="list">
                    <Message v-for="(msg, index) in discussionArr" 
                        :key="msg.id" :message="msg"  :id="'msg-' + msg.id"
                        :host="host"
                        ref="messages"
                        
                        @copy="copyToClipBoard" @delete="deleteMessage" @rankUp="rankUpMessage"
                        @rankDown="rankDownMessage" @updateMessage="updateMessage" @resendMessage="resendMessage" @continueMessage="continueMessage"
                        :avatar="getAvatar(msg.sender)" />

                    <!-- REMOVED FOR NOW, NEED MORE TESTING -->
                    <!-- @click="scrollToElementInContainer($event.target, 'messages-list')"  -->


                </TransitionGroup>
                <WelcomeComponent v-if="!currentDiscussion.id" />

            </div>

            <div
                class="absolute w-full bottom-0 bg-transparent p-10 pt-16 bg-gradient-to-t from-bg-light dark:from-bg-dark from-5% via-bg-light dark:via-bg-dark via-10% to-transparent to-100%">

            </div>
            <div class=" bottom-0 container flex flex-row items-center justify-center " v-if="currentDiscussion.id">
                <ChatBox ref="chatBox" 
                    :loading="isGenerating" 
                    :discussionList="discussionArr" 
                    :on-show-toast-message="showToastMessage"
                    :on-talk="talk"
                    @messageSentEvent="sendMsg" 
                    @sendCMDEvent="sendCmd"
                    @createEmptyUserMessage="createEmptyUserMessage"
                    @createEmptyAIMessage="createEmptyAIMessage"
                    @stopGenerating="stopGenerating" 
                    @loaded="recoverFiles"
                    >
                </ChatBox>
            </div>
            <!-- CAN ADD FOOTER PANEL HERE -->
        </div>

    </div>
    <Toast ref="toast">
    </Toast>
    <MessageBox ref="messageBox" />
    <ChoiceDialog reference="database_selector" class="z-20"
      :show="database_selectorDialogVisible"
      :choices="databases"
      @choice-selected="ondatabase_selectorDialogSelected"
      @close-dialog="onclosedatabase_selectorDialog"
      @choice-validated="onvalidatedatabase_selectorChoice"
    />      
</template>


<style scoped>



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


export default {
    
    setup() { },
    
    data() {
        return {
            host:"",
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
            panelCollapsed: false, // left panel collapse
            isOpen: false,
            discussion_id: 0,
        }
    },
    methods: {     
        onSettingsBinding() {
            try {
                this.isLoading = true
                axios.get('/get_active_binding_settings').then(res => {
                    this.isLoading = false
                    if (res) {

                        console.log('binding sett', res)

                        if (res.data && Object.keys(res.data).length > 0) {

                            // open form

                            this.$refs.universalForm.showForm(res.data, "Binding settings - " + bindingEntry.binding.name, "Save changes", "Cancel").then(res => {
                                // send new data
                                try {
                                    axios.post('/set_active_binding_settings',
                                        res).then(response => {

                                            if (response && response.data) {
                                                console.log('binding set with new settings', response.data)
                                                this.$refs.toast.showToast("Binding settings updated successfully!", 4, true)

                                            } else {
                                                this.$refs.toast.showToast("Did not get binding settings responses.\n" + response, 4, false)
                                                this.isLoading = false
                                            }


                                        })
                                } catch (error) {
                                    this.$refs.toast.showToast("Did not get binding settings responses.\n Endpoint error: " + error.message, 4, false)
                                    this.isLoading = false
                                }



                            })
                        } else {
                            this.$refs.toast.showToast("Binding has no settings", 4, false)
                            this.isLoading = false
                        }

                    }
                })

            } catch (error) {
                this.isLoading = false
                this.$refs.toast.showToast("Could not open binding settings. Endpoint error: " + error.message, 4, false)
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
            const res = await axios.post("/select_database",{"name": choice});
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
        toggleLTM(){
            this.$store.state.config.use_discussions_history =! this.$store.state.config.use_discussions_history;
            this.applyConfiguration();
        },
        applyConfiguration() {
            this.loading = true;
            axios.post('/apply_settings', {"config":this.$store.state.config}).then((res) => {
                this.loading = false;
                //console.log('apply-res',res)
                if (res.data.status) {
                    this.$refs.toast.showToast("Configuration changed successfully.", 4, true)
                    //this.save_configuration()
                } else {
                    this.$refs.toast.showToast("Configuration change failed.", 4, false)
                }
                nextTick(() => {
                    feather.replace()
                })
            }).catch((err)=>{
                this.loading = false;
                this.$refs.toast.showToast("Configuration change failed.", 4, false)
            })
        },
        save_configuration() {
            this.showConfirmation = false
            axios.post('/save_settings', {})
                .then((res) => {
                    if (res) {
                        if (res.status) {
                            this.$refs.toast.showToast("Settings saved!",4,true)
                        }
                        else
                            this.$refs.messageBox.showMessage("Error: Couldn't save settings!")
                        return res.data;
                    }
                })
                .catch(error => {
                    console.log(error.message, 'save_configuration')
                    this.$refs.messageBox.showMessage("Couldn't save settings!")
                    return { 'status': false }
                });

        },        
        showToastMessage(text, duration, isok){
            console.log("sending",text)
            this.$refs.toast.showToast(text, duration, isok)
        },        
        togglePanel() {
            this.panelCollapsed = !this.panelCollapsed;
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
                })

                socket.emit('load_discussion',{"id":id});

            }
        },
        recoverFiles(){
            console.log("Recovering files")
            axios.get('/get_current_personality_files_list').then(res=>{
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
                            axios.get('/get_current_personality_files_list').then(res=>{
                                console.log("Files recovered")
                                this.fileList = res.files
                            });
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
                    })
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
                    })
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
                    })
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
                const res = await axios.get('/delete_message', { params: { client_id: this.client_id, id: id } })

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
                const res = await axios.get('/message_rank_up', { params: { client_id: this.client_id, id: id } })

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
                const res = await axios.get('/message_rank_down', { params: { client_id: this.client_id, id: id } })

                if (res) {
                    return res.data
                }
            } catch (error) {
                console.log("Error: Could not rank down message", error.message)
                return {}
            }
        },
        async edit_message(id, message) {
            try {
                const res = await axios.get('/edit_message', { params: { client_id: this.client_id, id: id, message: message } })

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
                        discussion_ids: discussionIdArr,
                        export_format: export_format
                    })

                    if (res) {
                        return res.data
                    }
                }

            } catch (error) {
                console.log("Error: Could not export multiple discussions", error.message)
                return {}
            }
        },
        async import_multiple_discussions(jArray) {
            try {
                if (jArray.length > 0) {
                    console.log('sending import', jArray)
                    const res = await axios.post('/import_multiple_discussions', {
                        jArray
                    })

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
                this.$refs.toast.showToast("You are currently generating a text. Please wait for text generation to finish or stop it before trying to select another discussion", 4, false)
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
                    }
                    })

                }
                else{
                    if (this.currentDiscussion.id != item.id) {

                        this.currentDiscussion = item

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
                html_js_s: []

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
                this.$refs.toast.showToast("It seems that no model has been loaded. Please download and install a model first, then try again.", 4, false)
                this.isGenerating = false
                this.setDiscussionLoading(this.currentDiscussion.id, this.isGenerating)
                this.chime.play()
            }*/
        },
        talk(pers){
            this.isGenerating = true;
            this.setDiscussionLoading(this.currentDiscussion.id, this.isGenerating);
            axios.get('/get_generation_status', {}).then((res) => {
                if (res) {
                    //console.log(res.data.status);
                    if (!res.data.status) {
                        console.log('Generating message from ',res.data.status);
                        socket.emit('generate_msg_from', { id: -1 });
                        // Temp data
                        let lastmsgid =0
                        if(this.discussionArr.length>0){
                            lastmsgid= Number(this.discussionArr[this.discussionArr.length - 1].id) + 1
                        }
                        
                    }
                    else {
                        console.log("Already generating");
                    }
                }
            }).catch((error) => {
                console.log("Error: Could not get generation status", error);
            });
        },
        createEmptyUserMessage(){
            socket.emit('create_empty_message', {"type":0}); // 0 for user and 1 for AI
        },
        createEmptyAIMessage(){
            socket.emit('create_empty_message', {"type":1}); // 0 for user and 1 for AI
        },
        sendMsg(msg) {
            // Sends message to binding
            if (!msg) {
                this.$refs.toast.showToast("Message contains no content!", 4, false)
                return
            }
            this.isGenerating = true;
            this.setDiscussionLoading(this.currentDiscussion.id, this.isGenerating);
            axios.get('/get_generation_status', {}).then((res) => {
                if (res) {
                    //console.log(res.data.status);
                    if (!res.data.status) {
                        socket.emit('generate_msg', { prompt: msg });

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
                            id:             lastmsgid,
                            discussion_id:  this.discussion_id,
                            parent_id:      lastmsgid,

                            binding:                "",
                            model:                  "",
                            personality:            "",

                            created_at:             new Date().toLocaleString(),
                            finished_generating_at:  new Date().toLocaleString(),
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
            socket.emit('execute_command', { command: cmd, parameters: [] });            
        },
        notify(notif){
            self.isGenerating = false
            this.setDiscussionLoading(this.currentDiscussion.id, this.isGenerating);
            nextTick(() => {
                const msgList = document.getElementById('messages-list')
                this.scrollBottom(msgList)
            })            
            this.$refs.toast.showToast(notif.content, 5, notif.status)
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
                    messageItem.content = msgObj.content
                    messageItem.finished_generating_at = msgObj.finished_generating_at
                }
                else if(messageItem && msgObj.message_type==this.msgTypes.MSG_TYPE_CHUNK){
                    messageItem.content += msgObj.content
                } else if (msgObj.message_type == this.msgTypes.MSG_TYPE_STEP_START){
                    messageItem.steps.push({"message":msgObj.content,"done":false, "status":true })
                } else if (msgObj.message_type == this.msgTypes.MSG_TYPE_STEP_END) {
                    // Find the step with the matching message and update its 'done' property to true
                    const matchingStep = messageItem.steps.find(step => step.message === msgObj.content);

                    if (matchingStep) {
                        matchingStep.done = true;
                        try {
                            console.log(msgObj.parameters)
                            const parameters = msgObj.parameters;
                            matchingStep.status=parameters.status
                            console.log(parameters);
                            
                        } catch (error) {
                            console.error('Error parsing JSON:', error.message);
                        }
                    }
                } else if (msgObj.message_type == this.msgTypes.MSG_TYPE_JSON_INFOS) {
                    console.log("JSON message")
                    console.log(msgObj.metadata)
                    messageItem.metadata = msgObj.metadata
                } else if (msgObj.message_type == this.msgTypes.MSG_TYPE_UI) {
                    console.log("UI message")
                    messageItem.ui = msgObj.ui      
                    console.log(messageItem.ui)
                } else if (msgObj.message_type == this.msgTypes.MSG_TYPE_EXCEPTION) {
                    this.$refs.toast.showToast(msgObj.content, 5, false)
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
            this.$refs.toast.showToast("Copied name to clipboard!", 4, true)
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
            this.$refs.toast.showToast("Removed (" + deleteList.length + ") items", 4, true)
            this.showConfirmation = false
            console.log("Multi delete done")
        },
        async deleteMessage(msgId) {

            await this.delete_message(msgId).then(() => {

                this.discussionArr.splice(this.discussionArr.findIndex(item => item.id == msgId), 1)

            }).catch(() => {
                this.$refs.toast.showToast("Could not remove message", 4, false)
                console.log("Error: Could not delete message")
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
            const index = this.list.findIndex((x) => x.id == id)
            const discussionItem = this.list[index]
            discussionItem.loading = loading
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
                this.$refs.toast.showToast("Could not rank up message", 4, false)
                console.log("Error: Could not rank up message")
            })

        },
        async rankDownMessage(msgId) {
            await this.message_rank_down(msgId).then((res) => {

                const message = this.discussionArr[this.discussionArr.findIndex(item => item.id == msgId)]
                message.rank = res.new_rank
            }).catch(() => {
                this.$refs.toast.showToast("Could not rank down message", 4, false)

                console.log("Error: Could not rank down message")
            })

        },
        async updateMessage(msgId, msg) {
            await this.edit_message(msgId, msg).then(() => {

                const message = this.discussionArr[this.discussionArr.findIndex(item => item.id == msgId)]
                message.content = msg

            }).catch(() => {
                this.$refs.toast.showToast("Could not update message", 4, false)

                console.log("Error: Could not update message")
            })

        },
        resendMessage(msgId, msg) {
            nextTick(() => {
                feather.replace()

            })
            // Resend message
            this.isGenerating = true;
            this.setDiscussionLoading(this.currentDiscussion.id, this.isGenerating);
            axios.get('/get_generation_status', {}).then((res) => {
                if (res) {
                    if (!res.data.status) {
                        socket.emit('generate_msg_from', { prompt: msg, id: msgId });
                    }
                    else {
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
            console.log("final", msgObj)

            // Last message contains halucination suppression so we need to update the message content too
            const parent_id = msgObj.parent_id
            this.discussion_id = msgObj.discussion_id
            if (this.currentDiscussion.id == this.discussion_id) {
                const index = this.discussionArr.findIndex((x) => x.id == msgObj.id)
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
            })


            this.isGenerating = false
            this.setDiscussionLoading(this.currentDiscussion.id, this.isGenerating)
            this.chime.play()
        },
        copyToClipBoard(messageEntry) {
            this.$refs.toast.showToast("Copied to clipboard successfully", 4, true)

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
            let content = ""
            if (messageEntry.message.content) {
                content = messageEntry.message.content
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
                this.$refs.toast.showToast("Could not parse JSON. \n" + error.message, 4, false)
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
                    this.$refs.toast.showToast("Successfully exported", 4, true)
                    this.isCheckbox = false
                } else {
                    this.$refs.toast.showToast("Failed to export discussions", 4, false)
                }
                this.loading = false
            }

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
                    this.$refs.toast.showToast("Successfully exported", 4, true)
                    this.isCheckbox = false
                } else {
                    this.$refs.toast.showToast("Failed to export discussions", 4, false)
                }
                this.loading = false
            }

        },
        async importDiscussions(event) {
            const obj = await this.parseJsonFile(event.target.files[0])

            const res = await this.import_multiple_discussions(obj)
            if (res) {
                this.$refs.toast.showToast("Successfully imported (" + obj.length + ")", 4, true)
                await this.list_discussions()
            } else {
                this.$refs.toast.showToast("Failed to import discussions", 4, false)
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
                this.$refs.toast.showToast("Failed to set filelist in chatbox\n" + error.message, 4, false)

            }


            this.isDragOverChat = false


        },
        async setFileListDiscussion(files) {

            if (files.length > 1) {
                this.$refs.toast.showToast("Failed to import discussions. Too many files", 4, false)
                return
            }
            const obj = await this.parseJsonFile(files[0])

            const res = await this.import_multiple_discussions(obj)
            if (res) {
                this.$refs.toast.showToast("Successfully imported (" + obj.length + ")", 4, true)
                await this.list_discussions()
            } else {
                this.$refs.toast.showToast("Failed to import discussions", 4, false)
            }


            this.isDragOverDiscussion = false
        },
    },
    async created() {
        this.$nextTick(() => {
            feather.replace();
        });           

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
            console.log(this.$store.state.ready)
        }          
        console.log("Ready")
        // Constructor
        this.setPageTitle()
        await this.list_discussions()
        this.loadLastUsedDiscussion()


        // socket responses
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
        try {
            const response = await fetch('/get_server_address'); // Replace with the actual endpoint on your Flask server
            const serverAddress = await response.text();

            if(serverAddress.includes('<')){
                console.log(`Server address not found`)
                return "http://localhost:9600/"//process.env.VITE_LOLLMS_API
                
            }

            console.log(`Server address: ${serverAddress}`)
            this.host = `${serverAddress}`; // Construct the full server address dynamically
        } catch (error) {
            console.error('Error fetching server address:', error);
            // Handle error if necessary
            this.host =  "http://localhost:9600/"//process.env.VITE_LOLLMS_API
        }        
        //console.log('chatbox mnt',this.$refs)
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
    },
    components: {
        Discussion,
        Message,
        ChatBox,
        WelcomeComponent,
        Toast,
        ChoiceDialog        
    },
    watch: {  
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
        isGenerating:{
            get(){
                return this.$store.state.isGenerating;
            },
            set(val){
                this.$store.state.isGenerating=val
            }
        },
        formatted_database_name() {
            const db_name = this.$store.state.config.db_path;
            const trimmed_name = db_name.slice(0, db_name.length - 3);
            return trimmed_name;
        },
        UseDiscussionHistory() {
            return this.$store.state.config.use_discussions_history;
        }, 
        isReady:{
            
            get() {
                return this.$store.state.ready;
            },
        },
        databases(){            
            return this.$store.state.databases;
        },
        client_id() {
            return socket.id
        },
        isReady(){
            console.log("verify ready", this.isCreated)
            return this.isCreated
        },
        showPanel() {
           return this.$store.state.ready && !this.panelCollapsed;
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
import Message from '../components/Message.vue'
import ChatBox from '../components/ChatBox.vue'
import WelcomeComponent from '../components/WelcomeComponent.vue'
import Toast from '../components/Toast.vue'
import MessageBox from "@/components/MessageBox.vue";
import feather from 'feather-icons'

import axios from 'axios'
import { nextTick, TransitionGroup } from 'vue'

import socket from '@/services/websocket.js'


import { onMounted } from 'vue'
import { initFlowbite } from 'flowbite'
import { store } from '../main'

import ChoiceDialog from '@/components/ChoiceDialog.vue'


// initialize components based on data attribute selectors
onMounted(() => {
    initFlowbite()
})

axios.defaults.baseURL = import.meta.env.VITE_LOLLMS_API_BASEURL
</script>
