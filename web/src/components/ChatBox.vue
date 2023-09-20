<template>
    <div class="absolute bottom-0 min-w-96  w-full  justify-center text-center p-4 ">
        <div v-if="loading" class="flex items-center justify-center w-full">
            <div class="flex flex-row p-2 rounded-t-lg ">

                <button type="button"
                    class="bg-bg-light-tone-panel dark:bg-bg-dark-tone-panel hover:bg-bg-light-tone focus:ring-4 focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 mr-2 mb-2 dark:hover:bg-bg-dark-tone focus:outline-none dark:focus:ring-blue-800"
                    @click.stop="stopGenerating">
                    Stop generating
                </button>
            </div>
        </div>

        <form>
            <label for="chat" class="sr-only">Send message</label>
            <div class="px-3 py-3 rounded-lg bg-bg-light-tone-panel dark:bg-bg-dark-tone-panel shadow-lg  ">

                <div class="flex flex-col gap-2">
                    <!-- EXPAND / COLLAPSE BUTTON -->
                    <div class="flex">
                        <button v-if="filesList.length > 0"
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
                                            class="flex flex-row items-center gap-1 text-left p-2 text-sm font-medium bg-bg-dark-tone-panel dark:bg-bg-dark-tone rounded-lg hover:bg-primary dark:hover:bg-primary">
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


                                            <div class="line-clamp-1 w-3/5" :class="isFileSentList[index]?'text-green-200':'text-red-200'">
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
                    <div v-if="filesList.length > 0" class="flex items-center mx-1">

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
                    <!-- CHAT BOX -->
                    <div class="flex flex-row flex-grow items-center gap-2 overflow-visible">
                        <InteractiveMenu 
                                :title="selectedModel"
                                :execute_cmd="setModel"  
                                :icon="models_menu_icon" 
                                :commands="commandify(models)"
                                :selected_entry="selectedModel"></InteractiveMenu>
                        <div v-if="selecting_model" title="Selecting model" class="flex flex-row flex-grow justify-end">
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
                                <span class="sr-only">Selecting model...</span>
                            </div>
                        </div>                        
                        <div class="w-fit">
                            <MountedPersonalities ref="mountedPers" :onShowPersList="onShowPersListFun" :onReady="onPersonalitiesReadyFun"/>
                            <!-- :onShowPersList="onShowPersListFun" -->
                        </div>

                        <div class="w-fit">
                            <PersonalitiesCommands
                                v-if="personalities_ready && this.$store.state.mountedPersArr[this.$store.state.config.active_personality_id].commands!=''" 
                                :commandsList="this.$store.state.mountedPersArr[this.$store.state.config.active_personality_id].commands"
                                :sendCommand="sendMessageEvent"
                                :on-show-toast-message="onShowToastMessage"
                                ref="personalityCMD"
                            ></PersonalitiesCommands>
                        </div>

                        <div class="relative grow">
                            <textarea id="chat" rows="1" v-model="message" title="Hold SHIFT + ENTER to add new line"
                                class="inline-block  no-scrollbar  p-2.5 w-full text-sm text-gray-900 bg-bg-light rounded-lg border border-gray-300 focus:ring-blue-500 focus:border-blue-500 dark:bg-bg-dark dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
                                placeholder="Send message..." @keydown.enter.exact="submitOnEnter($event)">


                            </textarea>
                            <input type="file" ref="fileDialog" style="display: none" @change="addFiles" multiple />
                            <button type="button" @click.stop="$refs.fileDialog.click()" title="Add files"
                                class="absolute inset-y-0 right-0 flex items-center mr-2 w-6 hover:text-secondary duration-75 active:scale-90">

                                <i data-feather="file-plus"></i>

                            </button>
                        </div>
                        <!-- BUTTONS -->
                        <div class="inline-flex justify-center  rounded-full ">
                            <button
                                type="button"
                                @click="startSpeechRecognition"
                                :class="{ 'text-red-500': isLesteningToVoice }"
                                class="w-6 hover:text-secondary duration-75 active:scale-90 cursor-pointer"
                            >
                            <i data-feather="mic"></i>
                            </button>                          
                            <button v-if="!loading" type="button" @click="submit"
                                class=" w-6 hover:text-secondary duration-75 active:scale-90">

                                <i data-feather="send"></i>

                                <span class="sr-only">Send message</span>
                            </button>
                            <div v-if="loading" title="Waiting for reply">
                                <!-- SPINNER -->
                                <div role="status">
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
                            </div>

                        </div>
                    </div>
                </div>
            </div>
        </form>
    </div>
    <Toast ref="toast"/>
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
import { useStore } from 'vuex'; // Import the useStore function
import { inject } from 'vue';
import socket from '@/services/websocket.js'
import Toast from '../components/Toast.vue'

export default {
    name: 'ChatBox',
    emits: ["messageSentEvent", "stopGenerating", "loaded"],
    props: {
        onTalk: Function,
        discussionList: Array,
        loading: false,
        onShowToastMessage: Function

    },
    components: {        
        Toast,
        MountedPersonalities,
        MountedPersonalitiesList,
        PersonalitiesCommands,
        InteractiveMenu
    },
    setup() {



    },
    data() {
        return {
            message: "",
            selecting_model:false,
            selectedModel:'',
            models:{},
            isLesteningToVoice:false,
            filesList: [],
            isFileSentList: [],
            totalSize: 0,
            showfilesList: true,
            showPersonalities: false,
            personalities_ready: false,
            models_menu_icon:'#M'
        }
    },
    computed: {
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

        }
    },
    methods: {   
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
        commandify(list_of_strings){
            let list_of_dicts=[]
            for (var i = 0; i < list_of_strings.length; i++) {
                let dict={}
                dict["name"]=list_of_strings[i]
                dict["value"]=list_of_strings[i]
                list_of_dicts.push(dict)
            }
            return list_of_dicts

        },
        setModel(selectedModel){
            console.log("Setting model to "+selectedModel);
            this.selecting_model=true
            this.selectedModel = selectedModel
            axios.post("/update_setting", {                
                        setting_name: "model_name",
                        setting_value: selectedModel.value
                    }).then((response) => {
                console.log(response);
                this.$refs.toast.showToast(`Model changed to ${selectedModel.value}`,4,true)
                this.selecting_model=false
                }).catch(err=>{
                this.$refs.toast.showToast(`Error ${err}`,4,true)
                this.selecting_model=false
                });
        
        },
        clear_files(){
            axios.get('/clear_personality_files_list').then(res=>{
                if(res.data.status){
                    console.log(`Files removed`)
                }
                else{
                    console.log(`Files couldn't be removed`)
                }
            })

            this.filesList = []
            this.isFileSentList = []
        },
        send_file(file){
            const formData = new FormData();
            formData.append('file', file);
            console.log("Uploading file")
            // Read the file as a data URL and emit it to the server
            const reader = new FileReader();
            reader.onload = () => {
                const data = {
                filename: file.name,
                fileData: reader.result,
                };
                socket.on('file_received',(resp)=>{
                    if(resp.status){
                        console.log(resp.filename)

                        let index = this.filesList.findIndex((file) => file.name === resp.filename);
                        if(index>=0){
                            this.isFileSentList[index]=true;
                            console.log(this.isFileSentList)
                        }
                        else{
                            console.log("Not found")
                        }
                        this.onShowToastMessage("File uploaded successfully",4,true);
                    }
                    else{
                        this.onShowToastMessage("Couldn't upload file\n"+resp.error,4,false);
                        try{
                            this.filesList.removeItem(file)
                        }
                        catch{

                        }
                        
                    }
                    socket.off('file_received')
                }) 
                socket.emit('send_file', data);
            };
            reader.readAsDataURL(file);        
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
            this.filesList = this.filesList.filter((item) => item != file)
            // console.log(this.filesList)
        },
        sendMessageEvent(msg) {
            this.filesList = []
            this.$emit('messageSentEvent', msg)

        },
        submitOnEnter(event) {
            if (event.which === 13) {
                event.preventDefault(); // Prevents the addition of a new line in the text field

                if (!event.repeat) {

                    this.sendMessageEvent(this.message)
                    this.message = "" // Clear input field
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
        addFiles(event) {
            console.log("Adding file")
            this.filesList = this.filesList.concat([...event.target.files])
            console.log(`Files_list : ${this.filesList}`)
            this.isFileSentList = this.isFileSentList.concat([false] * this.filesList.length)
            this.send_file(this.filesList[this.filesList.length-1])
        }
    },
    watch: {
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
        axios.get('list_models').then(response => {
          console.log("List models "+response.data)
          this.models=response.data
          axios.get('get_active_model').then(response => {
            console.log("Active model " + JSON.stringify(response.data))
            if(response.data!=undefined){
              this.selectedModel = response.data["model"]
            }
            
          }).catch(ex=>{
            this.$refs.toast.showToast(`Error: ${ex}`,4,false)
          });    

        }).catch(ex=>{
          this.$refs.toast.showToast(`Error: ${ex}`,4,false)
        });    
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
