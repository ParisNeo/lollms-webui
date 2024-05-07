<template>
    <div
        class="relative w-full group rounded-lg m-2 shadow-lg hover:border-primary dark:hover:border-primary hover:border-solid hover:border-2 border-2 border-transparent even:bg-bg-light-discussion-odd dark:even:bg-bg-dark-discussion-odd flex flex-col flex-grow flex-wrap overflow-visible p-4 pb-2 ">
        <div class="flex flex-row  gap-2 ">
            <div class=" flex-shrink-0">
                <!-- AVATAR -->
                <div class="group/avatar " >
                    <img :src="getImgUrl()" @error="defaultImg($event)" :data-popover-target="'avatar' + message.id" data-popover-placement="bottom"
                        class="w-10 h-10 rounded-full object-fill text-red-700">
                </div>
                
            </div>

            <div class="flex flex-col w-full flex-grow-0 ">
                <div class="flex flex-row flex-grow items-start ">
                    <!-- SENDER NAME -->
                    <div class="flex flex-col mb-2">
                        <div class="drop-shadow-sm text-lg text-opacity-95 font-bold grow ">{{ message.sender }}
                            <!-- <button @click="toggleModel"  class="expand-button">{{ expanded ? ' - ' : ' + ' }}</button>
                        <p v-if="expanded" class="drop-shadow-sm text-lg text-opacity-95 font-bold grow">
                        {{ message.model }}
                        </p> -->

                        </div>
                        <div class="text-sm text-gray-400 font-thin" v-if="message.created_at"
                            :title="'Created at: ' + created_at_parsed">
                            {{ created_at }}

                        </div>
                    </div>
                    <div class="flex-grow ">

                    </div>
                    <!-- MESSAGE CONTROLS -->
                    <div class="flex-row justify-end mx-2">
                        <div class="invisible group-hover:visible flex flex-row ">
                            <!-- MESSAGE CONTROLS -->
                            <!-- EDIT CONFIRMATION -->
                            <div v-if="editMsgMode" class="flex items-center duration-75">
                                <button class="text-2xl hover:text-red-600 duration-75 active:scale-90 p-2"
                                    title="Cancel edit" type="button" @click.stop="editMsgMode = false">
                                    <i data-feather="x"></i>
                                </button>
                                <button class="text-2xl hover:text-secondary duration-75 active:scale-90 p-2"
                                    title="Update message" type="button" @click.stop="updateMessage">
                                    <i data-feather="check"></i>
                                </button>

                            </div>
                            <div v-if="!editMsgMode" class="text-lg hover:text-secondary duration-75 active:scale-90 p-2 cursor-pointer"
                                title="Edit message" @click.stop="editMsgMode = true">
                                <i data-feather="edit"></i>
                            </div>
                            <div v-if="editMsgMode" class="text-lg hover:text-secondary duration-75 active:scale-90 p-2 cursor-pointer hover:border-2"
                                title="Add generic block" @click.stop="addBlock('')">
                                <img :src="code_block" width="25" height="25">
                            </div>                            
                            <div v-if="editMsgMode" class="text-lg hover:text-secondary duration-75 active:scale-90 p-2 cursor-pointer hover:border-2"
                                title="Add python block" @click.stop="addBlock('python')">
                                <img :src="python_block" width="25" height="25">
                            </div>
                            <div v-if="editMsgMode" class="text-lg hover:text-secondary duration-75 active:scale-90 p-2 cursor-pointer"
                                title="Add javascript block" @click.stop="addBlock('javascript')">
                                <img :src="javascript_block" width="25" height="25">
                            </div>
                            <div v-if="editMsgMode" class="text-lg hover:text-secondary duration-75 active:scale-90 p-2 cursor-pointer"
                                title="Add json block" @click.stop="addBlock('json')">
                                <img :src="json_block" width="25" height="25">
                            </div>
                            
                            <div v-if="editMsgMode" class="text-lg hover:text-secondary duration-75 active:scale-90 p-2 cursor-pointer"
                                title="Add c++ block" @click.stop="addBlock('c++')">
                                <img :src="cpp_block" width="25" height="25">
                            </div>
                            <div v-if="editMsgMode" class="text-lg hover:text-secondary duration-75 active:scale-90 p-2 cursor-pointer"
                                title="Add html block" @click.stop="addBlock('html')">
                                <img :src="html5_block" width="25" height="25">
                            </div>
                            <div v-if="editMsgMode" class="text-lg hover:text-secondary duration-75 active:scale-90 p-2 cursor-pointer"
                                title="Add LaTex block" @click.stop="addBlock('latex')">
                                <img :src="LaTeX_block" width="25" height="25">
                            </div>
                            <div v-if="editMsgMode" class="text-lg hover:text-secondary duration-75 active:scale-90 p-2 cursor-pointer"
                                title="Add bash block" @click.stop="addBlock('bash')">
                                <img :src="bash_block" width="25" height="25">
                            </div>
                            
                            <div class="text-lg hover:text-secondary duration-75 active:scale-90 p-2 cursor-pointer"
                                title="Copy message to clipboard" @click.stop="copyContentToClipboard()">
                                <i data-feather="copy"></i>
                            </div>
                            <div v-if="!editMsgMode && message.sender!=this.$store.state.mountedPers.name" class="text-lg text-red-500 hover:text-secondary duration-75 active:scale-90 p-2 cursor-pointer" 
                                title="Resend message with full context"
                                @click.stop="resendMessage('full_context')" 
                                :class="{ 'text-5xl': editMsgMode }">
                                <i data-feather="send"></i>
                            </div>
                            <div v-if="!editMsgMode && message.sender!=this.$store.state.mountedPers.name" class="text-lg hover:text-secondary duration-75 active:scale-90 p-2 cursor-pointer" 
                                title="Resend message without the full context"
                                @click.stop="resendMessage('full_context_with_internet')" 
                                :class="{ 'text-5xl': editMsgMode }">
                                <img :src="sendGlobe" width="25" height="25">
                            </div>

                            <div v-if="!editMsgMode && message.sender!=this.$store.state.mountedPers.name" class="text-lg hover:text-secondary duration-75 active:scale-90 p-2 cursor-pointer" 
                                title="Resend message without the full context"
                                @click.stop="resendMessage('simple_question')" 
                                :class="{ 'text-5xl': editMsgMode }">
                                <i data-feather="send"></i>
                            </div>
                            <div v-if="!editMsgMode && message.sender==this.$store.state.mountedPers.name" class="text-lg hover:text-secondary duration-75 active:scale-90 p-2 cursor-pointer" 
                                title="Resend message"
                                @click.stop="continueMessage()" 
                                >
                                <i data-feather="fast-forward"></i>
                            </div>                            
                            <!-- DELETE CONFIRMATION -->
                            <div v-if="deleteMsgMode" class="flex items-center duration-75">
                                <button class="text-2xl hover:text-red-600 duration-75 active:scale-90 p-2 cursor-pointer"
                                    title="Cancel removal" type="button" @click.stop="deleteMsgMode = false">
                                    <i data-feather="x"></i>
                                </button>
                                <button class="text-2xl hover:text-secondary duration-75 active:scale-90 p-2 cursor-pointer"
                                    title="Confirm removal" type="button" @click.stop="deleteMsg()">
                                    <i data-feather="check"></i>
                                </button>

                            </div>
                            <div v-if="!editMsgMode && !deleteMsgMode" class="text-lg hover:text-red-600 duration-75 active:scale-90 p-2 cursor-pointer"
                                title="Remove message" @click="deleteMsgMode = true">
                                <i data-feather="trash"></i>
                            </div>
                            <div class="text-lg hover:text-secondary duration-75 active:scale-90 p-2 cursor-pointer" title="Upvote"
                                @click.stop="rankUp()">
                                <i data-feather="thumbs-up"></i>
                            </div>
                            <div class="flex flex-row items-center">
                                <div class="text-lg hover:text-red-600 duration-75 active:scale-90 p-2 cursor-pointer" title="Downvote"
                                    @click.stop="rankDown()">
                                    <i data-feather="thumbs-down"></i>
                                </div>
                                <div v-if="message.rank != 0"
                                    class="rounded-full px-2 text-sm flex items-center justify-center font-bold cursor-pointer"
                                    :class="message.rank > 0 ? 'bg-secondary' : 'bg-red-600'" title="Rank">{{
                                        message.rank }}
                                </div>
                            </div>
                            <div class="flex flex-row items-center">
                                <div class="text-lg hover:text-red-600 duration-75 active:scale-90 p-2 cursor-pointer" 
                                    title="speak"
                                    @click.stop="speak()"
                                    :class="{ 'text-red-500': isTalking }">
                                    <i data-feather="volume-2"></i>
                                </div>
                            </div>    
                            <div v-if="this.$store.state.config.xtts_enable && !this.$store.state.config.xtts_use_streaming_mode" class="flex flex-row items-center">
                                <div v-if="!isSynthesizingVoice" class="text-lg hover:text-red-600 duration-75 active:scale-90 p-2 cursor-pointer" 
                                    title="generate_audio"
                                    @click.stop="read()"
                                >
                                    <i data-feather="voicemail"></i>
                                </div>
                                <img v-else :src="loading_svg">
                                
                            </div>                                                       
                        </div>
                    </div>
                </div>

                <div class="overflow-x-auto w-full">
                    <!-- MESSAGE CONTENT -->
                    <details v-show="message != undefined && message.steps != undefined && message.steps.length>0" class="flex w-full cursor-pointer rounded-xl border border-gray-200 bg-white shadow-sm dark:border-gray-800 dark:bg-gray-900 mb-3.5 max-w-full">
                        <summary class="grid min-w-72 select-none grid-cols-[40px,1fr] items-center gap-2.5 p-2">
                            <div class="relative grid aspect-square place-content-center overflow-hidden rounded-lg bg-gray-300 dark:bg-gray-200">
                                <img v-if="message.status_message!='Done' & message.status_message!= 'Generation canceled'" :src="loading_svg" class="w-50 h-50 absolute inset-0 text-gray-100 transition-opacity dark:text-gray-800 opacity-100">
                                <img v-if="message.status_message== 'Generation canceled'" :src="failed_svg" class="w-50 h-50 absolute inset-0 text-gray-100 transition-opacity dark:text-gray-800 opacity-100">
                                <img v-if="message.status_message=='Done'" :src="ok_svg" class="w-50 h-50 absolute m-2 w-6 inset-0 text-geen-100 transition-opacity dark:text-gray-800 opacity-100">
                            </div> 
                            <dl class="leading-4">
                                <dd class="text-sm">Processing infos</dd>
                                <dt class="flex items-center gap-1 truncate whitespace-nowrap text-[.82rem] text-gray-400">{{ message==undefined?"":message.status_message }}</dt>
                            </dl>
                        </summary> 
                        <div class="content px-5 pb-5 pt-4">
                            <ol class="list-none">
                                <div v-for="(step, index) in message.steps" :key="'step-' + message.id + '-' + index" class="group border-l pb-6 last:!border-transparent last:pb-0 dark:border-gray-800" :style="{ backgroundColor: step.done ? 'transparent' : 'inherit' }">
                                    <Step :done="step.done" :message="step.message" :status="step.status" :step_type = "step.type"/>
                                </div>
                            </ol>
                        </div>
                    </details>
                    <div class="flex flex-col items-start w-full">
                    </div>
                    <div class="flex flex-col items-start w-full">
                        <div v-for="(html_js, index) in message.html_js_s" :key="'htmljs-' + message.id + '-' + index" class="htmljs font-bold" :style="{ backgroundColor: step.done ? 'transparent' : 'inherit' }">
                            <RenderHTMLJS :htmlContent="html_js" />
                        </div>
                    </div>
                    
                    <MarkdownRenderer ref="mdRender" v-if="!editMsgMode" :host="host" :markdown-text="message.content" :message_id="message.id" :discussion_id="message.discussion_id" :client_id="this.$store.state.client_id">
                    </MarkdownRenderer>
                    <div >
                        <textarea v-if="message.open" ref="mdTextarea" @keydown.tab.prevent="insertTab"
                        class="block min-h-[900px] p-2.5 w-full text-gray-900 bg-gray-50 rounded-lg border border-gray-300 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500 overflow-y-scroll flex flex-col shadow-lg p-10 pt-0 overflow-y-scroll dark:bg-bg-dark scrollbar-thin scrollbar-track-bg-light-tone scrollbar-thumb-bg-light-tone-panel hover:scrollbar-thumb-primary dark:scrollbar-track-bg-dark-tone dark:scrollbar-thumb-bg-dark-tone-panel dark:hover:scrollbar-thumb-primary active:scrollbar-thumb-secondary"
                        :rows="4" 
                        placeholder="Enter message here..."
                        v-model="message.content">
                        </textarea>
                    </div>
                    <div  v-if="message.metadata !== null">
                        <div v-for="(metadata, index) in (message.metadata?.filter(metadata => metadata!=null && metadata.hasOwnProperty('title') && metadata.hasOwnProperty('content')) || [])" :key="'json-' + message.id + '-' + index" class="json font-bold">
                            <JsonViewer :jsonFormText="metadata.title" :jsonData="metadata.content" />
                        </div>
                    </div>

                    <DynamicUIRenderer v-if="message.ui !== null && message.ui !== undefined && message.ui !== ''" class="w-full h-full" :code="message.ui"></DynamicUIRenderer>
                    <audio controls v-if="audio_url!=null" :key="audio_url">
                        <source :src="audio_url" type="audio/wav"  ref="audio_player" >
                        Your browser does not support the audio element.
                    </audio>  

                </div>
                <!-- FOOTER -->
                <div class="text-sm text-gray-400 mt-2">
                    <div class="flex flex-row items-center gap-2">
                        <p v-if="message.binding">Binding: <span class="font-thin">{{ message.binding }}</span></p>
                        <p v-if="message.model">Model: <span class="font-thin">{{ message.model }}</span></p>
                        <p v-if="message.seed">Seed: <span class="font-thin">{{ message.seed }}</span></p>
                        <p v-if="message.nb_tokens">Number of tokens: <span class="font-thin"
                                :title="'Number of Tokens: ' + message.nb_tokens">{{ message.nb_tokens }}</span></p>
                        <p v-if="warmup_duration">Warmup duration: <span class="font-thin"
                                :title="'Warmup duration: ' + warmup_duration">{{ warmup_duration }}</span></p>
                        <p v-if="time_spent">Generation duration: <span class="font-thin"
                                :title="'Finished generating: ' + time_spent">{{ time_spent }}</span></p>
                        <p v-if="generation_rate">Rate: <span class="font-thin"
                                :title="'Generation rate: ' + generation_rate">{{ generation_rate }}</span></p>
                    </div>

                </div>
            </div>


        </div>



    </div>
</template>
<style>
.expand-button {
    margin-left: 10px;
    /* Add space between sender and expand button */
    margin-right: 10px;
    /* Add space between sender and expand button */
    background: none;
    border: none;
    padding: 0;
    cursor: pointer;
}
.htmljs{
    background: none;
}
</style>
<script>
import botImgPlaceholder from "../assets/logo.png"
const bUrl = import.meta.env.VITE_LOLLMS_API_BASEURL
import { nextTick } from 'vue'
import feather from 'feather-icons'
import DynamicUIRenderer from "./DynamicUIRenderer.vue"
import MarkdownRenderer from './MarkdownRenderer.vue';
import RenderHTMLJS from './RenderHTMLJS.vue';
import JsonViewer from "./JsonViewer.vue";
import Step from './Step.vue';
import axios from 'axios';

import code_block from '@/assets/code_block.svg';
import python_block from '@/assets/python_block.png';
import javascript_block from '@/assets/javascript_block.svg';
import json_block from '@/assets/json_block.png';
import cpp_block from '@/assets/cpp_block.png';
import html5_block from '@/assets/html5_block.png';
import LaTeX_block from '@/assets/LaTeX_block.png';
import bash_block from '@/assets/bash_block.png';

import process_svg from '@/assets/process.svg';
import ok_svg from '@/assets/ok.svg';
import failed_svg from '@/assets/failed.svg';

import loading_svg from '@/assets/loading.svg';
import sendGlobe from "../assets/send_globe.svg"

export default {
    // eslint-disable-next-line vue/multi-word-component-names
    name: 'Message',
    emits: ['copy', 'delete', 'rankUp', 'rankDown', 'updateMessage', 'resendMessage', 'continueMessage'],
    components: {
        MarkdownRenderer,
        Step,
        RenderHTMLJS,
        JsonViewer,
        DynamicUIRenderer,
    },
    props: {
        host: {
            type: String,
            required: false,
            default: "http://localhost:9600",
        },            
        message: Object,
        avatar: {
            default: ''
        }
    },
    data() {
        return {
            isSynthesizingVoice:false,
            cpp_block:cpp_block,
            html5_block:html5_block,
            LaTeX_block:LaTeX_block,
            json_block:json_block,
            javascript_block:javascript_block,
            process_svg:process_svg,
            ok_svg:ok_svg,
            failed_svg:failed_svg,
            loading_svg:loading_svg,
            sendGlobe:sendGlobe,
            code_block:code_block,
            python_block:python_block,
            bash_block:bash_block,
            audio_url: null,
            audio:null,
            msg:null,
            isSpeaking:false,
            speechSynthesis: null,
            voices: [],            
            expanded: false,
            showConfirmation: false,
            editMsgMode_: false,
            deleteMsgMode: false,
            mdRenderHeight: Number

        }
    }, mounted() {
        // Check if speech synthesis is supported by the browser
        if ('speechSynthesis' in window) {
            this.speechSynthesis = window.speechSynthesis;

            // Load the available voices
            this.voices = this.speechSynthesis.getVoices();

            // Make sure the voices are loaded before starting speech synthesis
            if (this.voices.length === 0) {
                this.speechSynthesis.addEventListener('voiceschanged', this.onVoicesChanged);
            } else {
                console.log("No voices found")
            }
        } else {
        console.error('Speech synthesis is not supported in this browser.');
        }

        nextTick(() => {
            feather.replace()
            this.mdRenderHeight = this.$refs.mdRender.$el.offsetHeight
        })
        console.log("Checking metadata")
        console.log(this.message)
        
        if (Object.prototype.hasOwnProperty.call(this.message,"metadata")){
            if(this.message.metadata!=null){
                console.log("Metadata found!")
                if (!Array.isArray(this.message.metadata)) {
                    this.message.metadata = [];
                }                
                console.log(typeof this.message.metadata)
                console.log(this.message.metadata)
                for(let metadata_entry of this.message.metadata){
                    if (Object.prototype.hasOwnProperty.call(metadata_entry, "audio_url")){
                        if(metadata_entry.audio_url!=null){
                            this.audio_url =  metadata_entry.audio_url
                            console.log("Audio URL:", this.audio_url)
                        }
                    }
                }
            }
        }

    }, methods: {
        computeTimeDiff(startTime, endTime){
            let timeDiff = endTime.getTime() - startTime.getTime();


            const hours = Math.floor(timeDiff / (1000 * 60 * 60));

            timeDiff -= hours * (1000 * 60 * 60);



            const mins = Math.floor(timeDiff / (1000 * 60));

            timeDiff -= mins * (1000 * 60);

            const secs = Math.floor(timeDiff / 1000)
            timeDiff -= secs * 1000;

            return [hours, mins, secs]
        },


        insertTab(event) {
            const textarea = event.target;
            const start = textarea.selectionStart;
            const end = textarea.selectionEnd;
            const isShiftPressed = event.shiftKey;

            if (start === end) {
                // If no text is selected, insert a tab or backtab as usual
                if (isShiftPressed) {
                    if(textarea.value.substring(start - 4,start)=="    "){
                        // Backtab
                        const textBefore = textarea.value.substring(0, start - 4);
                        const textAfter = textarea.value.substring(end);

                        // Remove the tab character (or spaces if you prefer) before the cursor position
                        const newText = textBefore + textAfter;

                        // Update the textarea content and cursor position
                        this.message.content = newText;
                        this.$nextTick(() => {
                            textarea.selectionStart = textarea.selectionEnd = start - 4;
                        });
                    }

                } else {
                // Tab
                const textBefore = textarea.value.substring(0, start);
                const textAfter = textarea.value.substring(end);

                // Insert a tab character (or spaces if you prefer) at the cursor position
                const newText = textBefore + '    ' + textAfter;

                // Update the textarea content and cursor position
                this.message.content = newText;
                this.$nextTick(() => {
                    textarea.selectionStart = textarea.selectionEnd = start + 4;
                });
                }
            } else {
                // If text is selected, insert a tab or backtab at the beginning of each selected line
                const lines = textarea.value.substring(start, end).split('\n');
                const updatedLines = lines.map((line) => {
                if (line.trim() === '') {
                    return line; // Skip empty lines
                } else if (isShiftPressed) {
                    // Backtab
                    if (line.startsWith('    ')) {
                    return line.substring(4); // Remove the tab character (or spaces if you prefer)
                    } else {
                    return line; // Line doesn't start with a tab, skip backtab
                    }
                } else {
                    // Tab
                    return '    ' + line; // Insert a tab character (or spaces if you prefer) at the beginning of the line
                }
                });

                const textBefore = textarea.value.substring(0, start);
                const textAfter = textarea.value.substring(end);

                // Update the textarea content with the modified lines
                const newText = textBefore + updatedLines.join('\n') + textAfter;
                this.message.content = newText;

                // Update the textarea selection range
                this.$nextTick(() => {
                textarea.selectionStart = start;
                textarea.selectionEnd = end + (updatedLines.length * 4); // Adjust selection end based on the added tabs
                });
            }

            event.preventDefault();
        },

        onVoicesChanged() {
        // This event will be triggered when the voices are loaded
        this.voices = this.speechSynthesis.getVoices();
        },
        read(){
            if(this.isSynthesizingVoice){
                this.isSynthesizingVoice=false
                this.$refs.audio_player.pause()
            }
            else{
                this.isSynthesizingVoice=true
                axios.post("./text2wav",{text:this.message.content}).then(response => {
                    this.isSynthesizingVoice=false
                    let url = response.data.url
                    console.log(url)
                    this.audio_url = url
                    if(!this.message.metadata) {
                        this.message.metadata = [];
                    }

                    let found = false;

                    for(let metadata_entry of this.message.metadata){
                        if (Object.prototype.hasOwnProperty.call(metadata_entry, "audio_url")){
                            metadata_entry.audio_url = this.audio_url;
                            found = true;
                        }
                    }

                    if (!found) {
                        this.message.metadata.push({audio_url: this.audio_url});
                    }
                    this.$emit('updateMessage', this.message.id, this.message.content, this.audio_url)
                }).catch(ex=>{
                    this.$store.state.toast.showToast(`Error: ${ex}`,4,false)
                    this.isSynthesizingVoice=false
                });
            }
        },
        speak() {
            if(this.$store.state.config.xtts_enable && this.$store.state.config.xtts_use_streaming_mode){
                this.isSpeaking = true;
                axios.post("./text2Audio",{text:this.message.content}).then(response => {
                    this.isSpeaking = false;
                }).catch(ex=>{
                    this.$store.state.toast.showToast(`Error: ${ex}`,4,false)
                    this.isSpeaking = false;
                });
            }
            else{
                if (this.msg) {
                    this.speechSynthesis.cancel();
                    this.msg = null;
                    this.isSpeaking = false;
                    return;
                }
                let startIndex =0;
                // Set isSpeaking to true before starting synthesis
                console.log("voice on")
                this.isSpeaking = true;

                const chunkSize = 200; // You can adjust the chunk size as needed
                this.message.content;

                // Create a new SpeechSynthesisUtterance instance
                this.msg = new SpeechSynthesisUtterance();
                this.msg.pitch = this.$store.state.config.audio_pitch;

                // Optionally, set the voice and other parameters as before
                if (this.voices.length > 0) {
                    this.msg.voice = this.voices.filter(voice => voice.name === this.$store.state.config.audio_out_voice)[0];
                }


                // Function to find the index of the last sentence that fits within the chunk size
                const findLastSentenceIndex = (startIndex) => {
                    let txt = this.message.content.substring(startIndex, startIndex+chunkSize)
                    // Define an array of characters that represent end of sentence markers.
                    const endOfSentenceMarkers = ['.', '!', '?', '\n'];

                    // Initialize a variable to store the index of the last end of sentence marker.
                    let lastIndex = -1;

                    // Iterate through the end of sentence markers and find the last occurrence in the txt string.
                    endOfSentenceMarkers.forEach(marker => {
                    const markerIndex = txt.lastIndexOf(marker);
                    if (markerIndex > lastIndex) {
                        lastIndex = markerIndex;
                    }
                    });
                    if(lastIndex==-1){lastIndex=txt.length}
                    console.log(lastIndex)
                    return lastIndex+startIndex+1;
                };

                // Function to speak a chunk of text
                const speakChunk = () => {
                    if (this.message.content.includes('.')){
                        const endIndex = findLastSentenceIndex(startIndex);
                        const chunk = this.message.content.substring(startIndex, endIndex);
                        this.msg.text = chunk;
                        startIndex = endIndex + 1;
                        this.msg.onend = (event) => {
                            if (startIndex < this.message.content.length-2) {
                                // Use setTimeout to add a brief delay before speaking the next chunk
                                setTimeout(() => {
                                    speakChunk();
                                }, 1); // Adjust the delay as needed
                            } else {
                                this.isSpeaking = false;
                                console.log("voice off :",this.message.content.length,"  ",endIndex)
                            }
                        };
                        this.speechSynthesis.speak(this.msg);

                    }
                    else{
                        setTimeout(() => {
                                speakChunk();
                            }, 1); // Adjust the delay as needed
                    }
                };

                // Speak the first chunk
                speakChunk();
            }





        },
   
        toggleModel() {
            this.expanded = !this.expanded;
        },
        addBlock(bloc_name){
            let ss =this.$refs.mdTextarea.selectionStart
            let se =this.$refs.mdTextarea.selectionEnd
            if(ss==se){
                if(speechSynthesis==0 || this.message.content[ss-1]=="\n"){
                    this.message.content = this.message.content.slice(0, ss) + "```"+bloc_name+"\n\n```\n" + this.message.content.slice(ss)
                    ss = ss+4+bloc_name.length
                }
                else{
                    this.message.content = this.message.content.slice(0, ss) + "\n```"+bloc_name+"\n\n```\n" + this.message.content.slice(ss)
                    ss = ss+3+bloc_name.length
                }
            }
            else{
                if(speechSynthesis==0 || this.message.content[ss-1]=="\n"){
                    this.message.content = this.message.content.slice(0, ss) + "```"+bloc_name+"\n"+this.message.content.slice(ss, se)+"\n```\n" + this.message.content.slice(se)
                    ss = ss+4+bloc_name.length
                }
                else{
                    this.message.content = this.message.content.slice(0, ss) + "\n```"+bloc_name+"\n"+this.message.content.slice(ss, se)+"\n```\n" + this.message.content.slice(se)
                    p = p+3+bloc_name.length
                }
            }

            this.$refs.mdTextarea.focus();
            this.$refs.mdTextarea.selectionStart = this.$refs.mdTextarea.selectionEnd = p;
        },
        copyContentToClipboard() {
            this.$emit('copy', this)

        },
        deleteMsg() {
            this.$emit('delete', this.message.id)
            this.deleteMsgMode = false
        },
        rankUp() {
            this.$emit('rankUp', this.message.id)

        },
        rankDown() {
            this.$emit('rankDown', this.message.id)

        },
        updateMessage() {
            this.$emit('updateMessage', this.message.id, this.message.content, this.audio_url)
            this.editMsgMode = false
        },
        resendMessage(msg_type) {
            this.$emit('resendMessage', this.message.id, this.message.content, msg_type)
        },
        continueMessage() {
            this.$emit('continueMessage', this.message.id, this.message.content)
        },
        getImgUrl() {
            if (this.avatar) {
                return bUrl + this.avatar
            }
            console.log("No avatar found")
            return botImgPlaceholder;

        },
        defaultImg(event) {
            event.target.src = botImgPlaceholder
        },
        parseDate(tdate) {
            let system_date = new Date(Date.parse(tdate));
            let user_date = new Date();

            let diff = Math.floor((user_date - system_date) / 1000);
            if (diff <= 1) {
                return "just now";
            }
            if (diff < 20) {
                return diff + " seconds ago";
            }
            if (diff < 40) {
                return "half a minute ago";
            }
            if (diff < 60) {
                return "less than a minute ago";
            }
            if (diff <= 90) {
                return "one minute ago";
            }
            if (diff <= 3540) {
                return Math.round(diff / 60) + " minutes ago";
            }
            if (diff <= 5400) {
                return "1 hour ago";
            }
            if (diff <= 86400) {
                return Math.round(diff / 3600) + " hours ago";
            }
            if (diff <= 129600) {
                return "1 day ago";
            }
            if (diff < 604800) {
                return Math.round(diff / 86400) + " days ago";
            }
            if (diff <= 777600) {
                return "1 week ago";
            }
            return tdate;
        },
        prettyDate(time) {
            let date = new Date((time || "").replace(/-/g, "/").replace(/[TZ]/g, " ")),
                diff = (((new Date()).getTime() - date.getTime()) / 1000),
                day_diff = Math.floor(diff / 86400);

            if (isNaN(day_diff) || day_diff < 0 || day_diff >= 31)
                return;

            return day_diff == 0 && (
                diff < 60 && "just now" ||
                diff < 120 && "1 minute ago" ||
                diff < 3600 && Math.floor(diff / 60) + " minutes ago" ||
                diff < 7200 && "1 hour ago" ||
                diff < 86400 && Math.floor(diff / 3600) + " hours ago") ||
                day_diff == 1 && "Yesterday" ||
                day_diff < 7 && day_diff + " days ago" ||
                day_diff < 31 && Math.ceil(day_diff / 7) + " weeks ago";
        },
        checkForFullSentence() {
            if(this.message.content.trim().split(" ").length>3){
                // If the sentence contains at least 3 words, call the speak() method
                this.speak();
                return; // Exit the loop after the first full sentence is found
            }
        },

    }, watch: {
        audio_url(newUrl) {
            if (newUrl) {
                this.$refs.audio_player.src = newUrl;
            }
        },
        'message.content': function (newContent) {
            if(this.$store.state.config.auto_speak)
                if(!(this.$store.state.config.xtts_enable && this.$store.state.config.xtts_use_streaming_mode)){
                    if(!this.isSpeaking){
                        // Watch for changes to this.message.content and call the checkForFullSentence method
                        this.checkForFullSentence();
                    }
                }
        },
        'message.ui': function (newContent) {
            console.log("ui changed")
            console.log(this.message.ui)
        },
        showConfirmation() {
            nextTick(() => {
                feather.replace()

            })
        },

        deleteMsgMode() {
            nextTick(() => {
                feather.replace()

            })
        },
    },
    computed: {
        editMsgMode:{
            get(){
                if(this.message.hasOwnProperty('open'))
                    return this.editMsgMode_ || this.message.open;
                else
                return this.editMsgMode_;
            },
            set(value){
                this.message.open = value
                this.editMsgMode_ = value
                nextTick(() => {
                    feather.replace()

                })
            }
        },
        isTalking :{
            get(){
                return this.isSpeaking
            }
        },
        created_at() {
            return this.prettyDate(this.message.created_at)

        },
        created_at_parsed() {
            return new Date(Date.parse(this.message.created_at)).toLocaleString()

        },
        finished_generating_at_parsed() {
            return new Date(Date.parse(this.message.finished_generating_at)).toLocaleString()

        },

        time_spent() {
            const startTime = new Date(Date.parse(this.message.started_generating_at))
            const endTime = new Date(Date.parse(this.message.finished_generating_at))
            console.log("Computing the generation duration, ", startTime," -> ", endTime)

            //const spentTime = new Date(endTime - startTime)
            const same = endTime.getTime() === startTime.getTime();
            if (same) {
                return undefined
            }

            if (!startTime.getTime() || !endTime.getTime()) {
                return undefined
            }
            let [hours, mins, secs] = this.computeTimeDiff(startTime, endTime)

            // let spentTime = Math.floor((endTime.getTime() - startTime.getTime()) / 1000);
            // const result = spentTime.getSeconds();

            function addZero(i) {
                if (i < 10) { i = "0" + i }
                return i;
            }

            // const d = new Date();
            // let h = addZero(spentTime.getHours());
            // let m = addZero(spentTime.getMinutes());
            // let s = addZero(spentTime.getSeconds());
            const time = addZero(hours) + "h:" + addZero(mins) + "m:" + addZero(secs) + 's';


            return time


        },
        warmup_duration() {
            const createdTime = new Date(Date.parse(this.message.created_at))
            const endTime = new Date(Date.parse(this.message.started_generating_at))
            console.log("Computing the warmup duration, ",createdTime," -> ", endTime)
            //const spentTime = new Date(endTime - startTime)
            const same = endTime.getTime() === createdTime.getTime();
            if (same) {
                return 0
            }

            if (!createdTime.getTime() || !endTime.getTime()) {
                return undefined
            }
            let hours, mins, secs;
            [hours, mins, secs] = this.computeTimeDiff(createdTime, endTime)

            // let spentTime = Math.floor((endTime.getTime() - startTime.getTime()) / 1000);
            // const result = spentTime.getSeconds();

            function addZero(i) {
                if (i < 10) { i = "0" + i }
                return i;
            }

            // const d = new Date();
            // let h = addZero(spentTime.getHours());
            // let m = addZero(spentTime.getMinutes());
            // let s = addZero(spentTime.getSeconds());
            const time = addZero(hours) + "h:" + addZero(mins) + "m:" + addZero(secs) + 's';


            return time


        },
        generation_rate() {
            const startTime = new Date(Date.parse(this.message.started_generating_at))
            const endTime = new Date(Date.parse(this.message.finished_generating_at))
            const nb_tokens = this.message.nb_tokens
            console.log("Computing the generation rate, ", nb_tokens, " in ", startTime," -> ", endTime)
            //const spentTime = new Date(endTime - startTime)
            const same = endTime.getTime() === startTime.getTime();
            if (same) {
                return undefined
            }
            if (!nb_tokens){
                return undefined
            }
            if (!startTime.getTime() || !endTime.getTime()) {
                return undefined
            }
            let timeDiff = endTime.getTime() - startTime.getTime();
            const secs = Math.floor(timeDiff / 1000)

            const rate = nb_tokens/secs;


            return Math.round(rate) + " t/s"


        }

    }


}
</script>