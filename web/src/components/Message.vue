<template>
    <div
        class="message group border-2 border-transparent hover:border-blue-400 dark:hover:border-blue-500">
        <div class="flex flex-row gap-2">
            <div class="flex-shrink-0">
                <!-- AVATAR -->
                <div class="group/avatar">
                    <img :src="getImgUrl()" @error="defaultImg($event)" :data-popover-target="'avatar' + message.id" data-popover-placement="bottom"
                        class="w-10 h-10 rounded-full object-fill border border-blue-300 dark:border-blue-600">
                </div>
            </div>

            <div class="flex flex-col w-full flex-grow">
                <div class="flex flex-row flex-grow items-start">
                    <!-- SENDER NAME & TIMESTAMP -->
                    <div class="flex flex-col mb-2">
                        <div class="message-header text-blue-800 dark:text-blue-100 font-bold text-lg ">{{ message.sender }}</div>
                        <div class="text-xs text-blue-500 dark:text-blue-400 font-thin" v-if="message.created_at"
                            :title="'Created at: ' + created_at_parsed">
                            {{ created_at }}
                        </div>
                    </div>
                    <div class="flex-grow"></div>
                </div>

                <div class="message-content overflow-x-auto w-full overflow-y-auto scrollbar space-y-2">
                    <!-- MESSAGE CONTENT -->
                    <MarkdownRenderer ref="mdRender" v-if="!editMsgMode" :host="host" :markdown-text="message.content" :message_id="message.id" :discussion_id="message.discussion_id" :client_id="this.$store.state.client_id">
                    </MarkdownRenderer>
                    
                    <!-- EDIT MODE TEXTAREA -->
                    <div v-if="editMsgMode">
                        <textarea ref="mdTextarea" @keydown.tab.prevent="insertTab"
                        class="input w-full min-h-[200px] p-2.5 text-blue-900 dark:text-blue-100 focus:ring-blue-500 focus:border-blue-500 dark:focus:ring-blue-500 dark:focus:border-blue-400 scrollbar shadow-inner"
                        :rows="Math.max(4, message.content.split('\n').length)" 
                        placeholder="Enter message here..."
                        v-model="message.content">
                        </textarea>
                    </div>

                    <!-- METADATA/JSON VIEWER -->
                    <div v-if="message.metadata !== null && !editMsgMode">
                        <div v-for="(metadata, index) in (message.metadata?.filter(metadata => metadata!=null && metadata.hasOwnProperty('title') && metadata.hasOwnProperty('content')) || [])" :key="'json-' + message.id + '-' + index" class="mt-2">
                            <JsonViewer :title="metadata.title" :data="metadata.content" :key="'msgjson-' + message.id" />
                        </div>
                    </div>
                    
                    <!-- DYNAMIC UI RENDERER -->
                    <DynamicUIRenderer v-if="message.ui && !editMsgMode" ref="ui" class="w-full mt-2" :ui="message.ui" :key="'msgui-' + message.id" />
                    
                    <!-- AUDIO PLAYER -->
                    <audio controls v-if="audio_url!=null && !editMsgMode" class="w-full mt-2" :key="audio_url">
                        <source :src="audio_url" type="audio/wav" ref="audio_player">
                        Your browser does not support the audio element.
                    </audio>

                <!-- DETAILS SECTION (STEPS & HTML/JS) -->
                <div class="message-details w-full max-w-4xl mx-auto mt-2">
                    <!-- Processing Steps Section -->
                     <div v-if="message.steps.length > 0 && !editMsgMode" class="steps-container">
                        <div
                            class="steps-header"
                            @click="toggleExpanded"
                        >
                            <!-- DYNAMIC ICON based on processing state -->
                            <div class="w-5 h-5 mr-2 flex-shrink-0 flex items-center justify-center">
                                <transition name="fade-icon" mode="out-in">
                                    <!-- Show spinner if processing -->
                                    <div v-if="isProcessingSteps" key="header-spinner" class="step-spinner"></div>
                                    <!-- Show final status icon if done -->
                                    <svg
                                        v-else-if="finalStepsStatus"
                                        key="header-success"
                                        class="step-icon-success w-4 h-4"
                                        fill="currentColor"
                                        viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"
                                    >
                                         <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path>
                                    </svg>
                                    <svg
                                        v-else
                                        key="header-fail"
                                        class="step-icon-fail w-4 h-4"
                                        fill="currentColor"
                                        viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"
                                    >
                                       <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"></path>
                                    </svg>
                                </transition>
                            </div>

                            <!-- DYNAMIC STATUS TEXT -->
                            <span class="steps-status truncate pr-2">{{ headerStepText }}</span>

                            <!-- Chevron remains the same -->
                            <span
                                class="toggle-icon text-xs text-blue-500 dark:text-blue-400 transform transition-transform duration-200 ml-auto"
                                :class="{ 'rotate-180': expanded }"
                            >
                                <i data-feather="chevron-down" class="w-5 h-5"></i>
                            </span>
                        </div>

                        <!-- Expansion content remains the same -->
                        <transition
                            enter-active-class="transition-all duration-300 ease-out overflow-hidden"
                            leave-active-class="transition-all duration-200 ease-in overflow-hidden"
                            enter-from-class="opacity-0 max-h-0"
                            enter-to-class="opacity-100 max-h-[500px]"
                            leave-from-class="opacity-100 max-h-[500px]"
                            leave-to-class="opacity-0 max-h-0"
                        >
                            <div v-if="expanded" class="steps-content">
                                <div class="pb-1">
                                    <div
                                        v-for="(step, index) in message.steps"
                                        :key="`step-${message.id}-${index}`"
                                        class="step-item animate-step-slide-in"
                                        :style="{ animationDelay: `${index * 80}ms` }"
                                    >
                                        <Step
                                            :done="step.done"
                                            :text="step.text"
                                            :status="step.status"
                                            :description="step.description"
                                        />
                                    </div>
                                </div>
                            </div>
                        </transition>
                    </div>

                        <!-- Content Renderer Section (HTML/JS) -->
                        <div 
                            v-if="message.html_js_s && message.html_js_s.length && !editMsgMode"
                            class="mt-2 flex flex-col items-start w-full overflow-y-auto scrollbar"
                        >
                            <div 
                                v-for="(html_js, index) in message.html_js_s" 
                                :key="`htmljs-${message.id}-${index}`" 
                                class="w-full animate-fadeIn"
                                :style="{ animationDelay: `${index * 200}ms` }"
                            >
                                <RenderHTMLJS :htmlContent="html_js" />
                            </div>
                        </div>
                    </div>
                </div>

                <!-- MESSAGE CONTROLS TOOLBAR -->
                 <div class="flex flex-row justify-end items-center mt-1 mx-2">
                    <div class="absolute bottom-2 right-2 invisible group-hover:visible flex flex-row items-center gap-1 bg-blue-200/70 dark:bg-blue-900/70 rounded-md p-1 shadow">
                        <!-- EDIT CONTROLS -->
                        <div v-if="editMsgMode" class="flex items-center gap-1">
                            <ToolbarButton @click.stop="editMsgMode = false" title="Cancel edit" icon="x" class="svg-button text-red-500 hover:bg-red-100 dark:hover:bg-red-900" />
                            <ToolbarButton @click.stop="updateMessage" title="Update message" icon="check" class="svg-button text-green-500 hover:bg-green-100 dark:hover:bg-green-900" />
                            
                            <!-- Add Block Dropdown (only in edit mode) -->
                            <DropdownMenu title="Add Block" icon="plus-square" class="svg-button">
                                <DropdownSubmenu title="Programming Languages" icon="code">
                                    <ToolbarButton @click.stop="addBlock('python')" title="Python" icon="python" class="svg-button"/>
                                    <ToolbarButton @click.stop="addBlock('javascript')" title="JavaScript" icon="js" class="svg-button"/>
                                    <ToolbarButton @click.stop="addBlock('typescript')" title="TypeScript" icon="typescript" class="svg-button"/>
                                    <ToolbarButton @click.stop="addBlock('java')" title="Java" icon="java" class="svg-button"/>
                                    <ToolbarButton @click.stop="addBlock('c++')" title="C++" icon="cplusplus" class="svg-button"/>
                                    <ToolbarButton @click.stop="addBlock('csharp')" title="C#" icon="csharp" class="svg-button"/>
                                    <ToolbarButton @click.stop="addBlock('go')" title="Go" icon="go" class="svg-button"/>
                                    <ToolbarButton @click.stop="addBlock('rust')" title="Rust" icon="rust" class="svg-button"/>
                                    <ToolbarButton @click.stop="addBlock('swift')" title="Swift" icon="swift" class="svg-button"/>
                                    <ToolbarButton @click.stop="addBlock('kotlin')" title="Kotlin" icon="kotlin" class="svg-button"/>
                                    <ToolbarButton @click.stop="addBlock('r')" title="R" icon="r-project" class="svg-button"/>
                                </DropdownSubmenu>
                                <DropdownSubmenu title="Web Technologies" icon="chrome">
                                    <ToolbarButton @click.stop="addBlock('html')" title="HTML" icon="html5" class="svg-button"/>
                                    <ToolbarButton @click.stop="addBlock('css')" title="CSS" icon="css3" class="svg-button"/>
                                    <ToolbarButton @click.stop="addBlock('vue')" title="Vue.js" icon="vuejs" class="svg-button"/>
                                    <ToolbarButton @click.stop="addBlock('react')" title="React" icon="react" class="svg-button"/>
                                    <ToolbarButton @click.stop="addBlock('angular')" title="Angular" icon="angular" class="svg-button"/>
                                </DropdownSubmenu>
                                <DropdownSubmenu title="Markup and Data" icon="file-text">
                                    <ToolbarButton @click.stop="addBlock('xml')" title="XML" icon="xml" class="svg-button"/>
                                    <ToolbarButton @click.stop="addBlock('json')" title="JSON" icon="json" class="svg-button"/>
                                    <ToolbarButton @click.stop="addBlock('yaml')" title="YAML" icon="yaml" class="svg-button"/>
                                    <ToolbarButton @click.stop="addBlock('markdown')" title="Markdown" icon="markdown" class="svg-button"/>
                                    <ToolbarButton @click.stop="addBlock('latex')" title="LaTeX" icon="latex" class="svg-button"/>
                                </DropdownSubmenu>
                                <DropdownSubmenu title="Scripting and Shell" icon="terminal">
                                    <ToolbarButton @click.stop="addBlock('bash')" title="Bash" icon="bash" class="svg-button"/>
                                    <ToolbarButton @click.stop="addBlock('powershell')" title="PowerShell" icon="powershell" class="svg-button"/>
                                    <ToolbarButton @click.stop="addBlock('perl')" title="Perl" icon="perl" class="svg-button"/>
                                </DropdownSubmenu>
                                <DropdownSubmenu title="Diagramming" icon="git-branch">
                                    <ToolbarButton @click.stop="addBlock('mermaid')" title="Mermaid" icon="mermaid" class="svg-button"/>
                                    <ToolbarButton @click.stop="addBlock('graphviz')" title="Graphviz" icon="graphviz" class="svg-button"/>
                                    <ToolbarButton @click.stop="addBlock('plantuml')" title="PlantUML" icon="plantuml" class="svg-button"/>
                                </DropdownSubmenu>
                                <DropdownSubmenu title="Database" icon="database">
                                    <ToolbarButton @click.stop="addBlock('sql')" title="SQL" icon="sql" class="svg-button"/>
                                    <ToolbarButton @click.stop="addBlock('mongodb')" title="MongoDB" icon="mongodb" class="svg-button"/>
                                </DropdownSubmenu>
                                <ToolbarButton @click.stop="addBlock('')" title="Generic Block" icon="code" class="svg-button"/>
                            </DropdownMenu>
                        </div>

                        <!-- STANDARD VIEW CONTROLS -->
                         <div v-else class="flex items-center gap-1">
                            <ToolbarButton @click.stop="editMsgMode = true" title="Edit message" icon="edit" class="svg-button" />
                            <ToolbarButton @click="copyContentToClipboard" title="Copy message to clipboard" icon="copy" class="svg-button" />
                            
                            <!-- Resend options (only if not user message) -->
                            <div v-if="message.sender !== $store.state.mountedPers.name" class="flex items-center gap-1">
                                <ToolbarButton @click.stop="resendMessage('full_context')" title="Resend message with full context" icon="send" class="svg-button" />
                                <ToolbarButton @click.stop="resendMessage('full_context_with_internet')" title="Resend message with internet search" icon="globe" class="svg-button" />
                                <ToolbarButton @click.stop="resendMessage('simple_question')" title="Resend message without context" icon="refresh-cw" class="svg-button" />
                            </div>
                            
                            <!-- Continue option (only if user message) -->
                            <div v-if="message.sender === $store.state.mountedPers.name" class="flex items-center gap-1">
                                <ToolbarButton @click.stop="continueMessage" title="Continue message" icon="fast-forward" class="svg-button" />
                            </div>
                            
                            <!-- Delete Button/Confirmation -->
                            <div v-if="deleteMsgMode" class="flex items-center gap-1">
                                <ToolbarButton @click.stop="deleteMsgMode = false" title="Cancel removal" icon="x" class="svg-button text-blue-500 hover:bg-blue-100 dark:hover:bg-blue-700" />
                                <ToolbarButton @click.stop="deleteMsg()" title="Confirm removal" icon="check" class="svg-button text-red-500 hover:bg-red-100 dark:hover:bg-red-900" />
                            </div>
                            <ToolbarButton v-else title="Remove message" icon="trash" @click="deleteMsgMode = true" class="svg-button text-red-500 hover:bg-red-100 dark:hover:bg-red-900" />

                            <!-- Ranking Buttons -->
                            <ToolbarButton @click.stop="rankUp()" title="Upvote" icon="thumbs-up" class="svg-button text-blue-500 dark:text-blue-400" />
                            <div class="flex items-center">
                                <ToolbarButton @click.stop="rankDown()" title="Downvote" icon="thumbs-down" class="svg-button text-red-500 dark:text-red-400" />
                                <div v-if="message.rank != 0"
                                    class="text-xs font-bold rounded-full px-1.5 py-0.5 flex items-center justify-center cursor-default"
                                    :class="message.rank > 0 ? 'bg-blue-500 text-white' : 'bg-red-500 text-white'" title="Rank">{{ message.rank }}
                                </div>
                            </div>

                            <!-- Speak/Audio Generation Buttons -->
                            <div v-if="this.$store.state.config.active_tts_service!='None'" class="flex items-center gap-1">
                                <ToolbarButton 
                                    title="Speak message" 
                                    icon="volume-2" 
                                    @click.stop="speak()" 
                                    class="svg-button" 
                                    :class="{ 'text-red-500 dark:text-red-400 animate-pulse': isTalking }"
                                />
                            </div>
                            <div v-if="this.$store.state.config.xtts_enable && !this.$store.state.config.xtts_use_streaming_mode" class="flex items-center gap-1">
                                <ToolbarButton v-if="!isSynthesizingVoice" 
                                    title="Generate audio" 
                                    icon="mic" 
                                    @click.stop="read()" 
                                    class="svg-button" 
                                />
                                <img v-else :src="loading_svg" class="w-5 h-5 animate-spin text-blue-500 dark:text-blue-400">
                            </div>
                        </div>
                    </div>
                </div>

                <!-- FOOTER DETAILS -->
                 <div class="text-xs text-blue-500 dark:text-blue-400 mt-2">
                    <div class="flex flex-row flex-wrap items-center gap-x-3 gap-y-1">
                        <p v-if="message.binding" class="footer-item">Binding: <span class="footer-value">{{ message.binding }}</span></p>
                        <p v-if="message.model" class="footer-item">Model: <span class="footer-value">{{ message.model }}</span></p>
                        <p v-if="message.seed" class="footer-item">Seed: <span class="footer-value">{{ message.seed }}</span></p>
                        <p v-if="message.nb_tokens" class="footer-item">Tokens: <span class="footer-value">{{ message.nb_tokens }}</span></p>
                        <p v-if="warmup_duration" class="footer-item">Warmup: <span class="footer-value">{{ warmup_duration }}</span></p>
                        <p v-if="time_spent" class="footer-item">Gen time: <span class="footer-value">{{ time_spent }}</span></p>
                        <p v-if="generation_rate" class="footer-item">Rate: <span class="footer-value">{{ generation_rate }}</span></p>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

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
import StatusIcon from './StatusIcon.vue'; // Make sure StatusIcon is imported
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

import ToolbarButton from './ToolbarButton.vue'
import DropdownMenu from './DropdownMenu.vue'
export default {
    // eslint-disable-next-line vue/multi-word-component-names
    name: 'Message',
    emits: ['copy', 'delete', 'rankUp', 'rankDown', 'updateMessage', 'resendMessage', 'continueMessage'],
    components: {
        MarkdownRenderer,
        Step,
        StatusIcon, // Register StatusIcon
        RenderHTMLJS,
        JsonViewer,
        DynamicUIRenderer,
        ToolbarButton,
        DropdownMenu,
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
            ui_componentKey:0,
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
            expanded: false, // For steps expansion
            showConfirmation: false,
            editMsgMode_: false,
            deleteMsgMode: false,
            mdRenderHeight: Number

        }
    }, 
    mounted() {
        // Check if speech synthesis is supported by the browser
        if ('speechSynthesis' in window) {
            this.speechSynthesis = window.speechSynthesis;

            // Load the available voices
            this.voices = this.speechSynthesis.getVoices();

            // Make sure the voices are loaded before starting speech synthesis
            if (this.voices.length === 0) {
                this.speechSynthesis.addEventListener('voiceschanged', this.onVoicesChanged);
            } else {
                console.log("Voices available:", this.voices.length)
            }
        } else {
        console.error('Speech synthesis is not supported in this browser.');
        }

        nextTick(() => {
            feather.replace()
            if (this.$refs.mdRender && this.$refs.mdRender.$el) {
                 this.mdRenderHeight = this.$refs.mdRender.$el.offsetHeight
            }
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

    }, 
    methods: {
        toggleExpanded() {
           this.expanded = !this.expanded
           nextTick(() => {
               feather.replace() // Re-render icons if needed inside the expanded section
           })
        },
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
            const tab = '    '; // 4 spaces for a tab

            if (start === end) {
                // No text selected, insert tab/backtab
                if (isShiftPressed) {
                    // Backtab: Check if the characters before cursor are the tab string
                    if (textarea.value.substring(start - tab.length, start) === tab) {
                        const textBefore = textarea.value.substring(0, start - tab.length);
                        const textAfter = textarea.value.substring(end);
                        this.message.content = textBefore + textAfter;
                        this.$nextTick(() => {
                            textarea.selectionStart = textarea.selectionEnd = start - tab.length;
                        });
                    }
                } else {
                    // Tab: Insert tab character
                    const textBefore = textarea.value.substring(0, start);
                    const textAfter = textarea.value.substring(end);
                    this.message.content = textBefore + tab + textAfter;
                    this.$nextTick(() => {
                        textarea.selectionStart = textarea.selectionEnd = start + tab.length;
                    });
                }
            } else {
                // Text is selected, indent/unindent lines
                const selectedText = textarea.value.substring(start, end);
                const lines = selectedText.split('\n');
                let changeInLength = 0;

                const updatedLines = lines.map((line, index) => {
                    if (isShiftPressed) {
                        // Backtab selected lines
                        if (line.startsWith(tab)) {
                            changeInLength -= tab.length;
                            return line.substring(tab.length);
                        }
                        return line;
                    } else {
                        // Tab selected lines
                        changeInLength += tab.length;
                        return tab + line;
                    }
                });

                const textBefore = textarea.value.substring(0, start);
                const textAfter = textarea.value.substring(end);
                this.message.content = textBefore + updatedLines.join('\n') + textAfter;

                this.$nextTick(() => {
                    textarea.selectionStart = start;
                    textarea.selectionEnd = end + changeInLength;
                });
            }
            event.preventDefault(); // Prevent default tab behavior
            this.adjustTextareaHeight(textarea); // Adjust height after modification
        },
        adjustTextareaHeight(textarea) {
            textarea.style.height = 'auto'; // Temporarily shrink height
            textarea.style.height = textarea.scrollHeight + 'px'; // Set to scroll height
        },
        onVoicesChanged() {
            // This event will be triggered when the voices are loaded
            this.voices = this.speechSynthesis.getVoices();
            console.log("Voices loaded:", this.voices.length);
        },
        read(){
            if(this.isSynthesizingVoice){
                this.isSynthesizingVoice=false
                if (this.$refs.audio_player) {
                    this.$refs.audio_player.pause()
                }
            }
            else{
                this.isSynthesizingVoice=true
                axios.post(`${this.host}/text2wav`,{text:this.message.content}).then(response => {
                    this.isSynthesizingVoice=false
                    let url = response.data.url
                    console.log(url)
                    this.audio_url = url
                    if(!this.message.metadata) {
                        this.message.metadata = [];
                    }

                    let found = false;

                    for(let metadata_entry of this.message.metadata){
                        if (metadata_entry && Object.prototype.hasOwnProperty.call(metadata_entry, "audio_url")){
                            metadata_entry.audio_url = this.audio_url;
                            found = true;
                            break; // Exit loop once updated
                        }
                    }

                    if (!found) {
                        this.message.metadata.push({audio_url: this.audio_url});
                    }
                    // Only emit update if the content hasn't changed (audio URL is metadata)
                    // this.$emit('updateMessage', this.message.id, this.message.content, this.message.metadata) // Maybe send metadata?
                    // For now, let's assume audio generation doesn't require saving immediately unless user explicitly saves.
                     nextTick(()=>{
                        if (this.$refs.audio_player) {
                            this.$refs.audio_player.load(); // Ensure the new source is loaded
                            this.$refs.audio_player.play(); // Optional: auto-play
                        }
                     })

                }).catch(ex=>{
                    this.$store.state.toast.showToast(`Error generating audio: ${ex.message || ex}`,4,false)
                    this.isSynthesizingVoice=false
                });
            }
        },
        async speak() {
            if (this.isSpeaking) {
                 // If already speaking, try to stop
                 if (this.$store.state.config.active_tts_service !== "browser" && this.$store.state.config.active_tts_service !== "None") {
                     axios.post(`${this.host}/stop_audio`, { client_id: this.$store.state.client_id }).then(response => {
                         this.isSpeaking = false;
                     }).catch(ex => {
                         this.$store.state.toast.showToast(`Error stopping audio: ${ex.message || ex}`, 4, false);
                         // Force state change even if stop fails, to allow trying again
                         this.isSpeaking = false;
                     });
                 } else if (this.speechSynthesis) {
                     this.speechSynthesis.cancel();
                     this.msg = null;
                     this.isSpeaking = false;
                 }
                 return; // Exit after attempting to stop
             }

            // Start speaking
            this.isSpeaking = true;
            console.log("Starting speech...");

            if (this.$store.state.config.active_tts_service !== "browser" && this.$store.state.config.active_tts_service !== "None") {
                // Use backend TTS service
                axios.post(`${this.host}/text2Audio`, { client_id: this.$store.state.client_id, text: this.message.content }).then(response => {
                    // Backend handles streaming or completion, we just update state when done/stopped
                    // The backend should ideally notify when finished, or we assume stop means finished.
                    // For now, we rely on the stop button press to set isSpeaking = false.
                     console.log("Backend TTS request sent.");
                     // Need a mechanism from backend/websocket to know when speech ends naturally
                     // Assuming for now, it only stops when user clicks stop again.
                }).catch(ex => {
                    this.$store.state.toast.showToast(`Error starting backend TTS: ${ex.message || ex}`, 4, false);
                    this.isSpeaking = false; // Reset state on error
                });
            } else if (this.speechSynthesis) {
                // Use browser speech synthesis
                let startIndex = 0;
                const chunkSize = 180; // Slightly smaller chunk size for browser limits
                const contentToSpeak = this.message.content;

                this.msg = new SpeechSynthesisUtterance();
                this.msg.pitch = this.$store.state.config.audio_pitch || 1;
                this.msg.rate = this.$store.state.config.audio_rate || 1; // Add rate control if desired

                const selectedVoice = this.voices.find(voice => voice.name === this.$store.state.config.audio_out_voice);
                if (selectedVoice) {
                    this.msg.voice = selectedVoice;
                    console.log("Using voice:", selectedVoice.name);
                } else {
                    console.warn("Selected voice not found, using default.");
                }

                const findLastSentenceIndex = (startIdx) => {
                    let textChunk = contentToSpeak.substring(startIdx, startIdx + chunkSize);
                    const endOfSentenceMarkers = ['.', '!', '?', '\n', ';', ':']; // Added more markers
                    let lastIndex = -1;

                    endOfSentenceMarkers.forEach(marker => {
                        const markerIndex = textChunk.lastIndexOf(marker);
                        if (markerIndex > lastIndex) {
                            lastIndex = markerIndex;
                        }
                    });

                    if (lastIndex === -1 && textChunk.length === chunkSize) {
                       // If no sentence end and chunk is full, find last space
                       lastIndex = textChunk.lastIndexOf(' ');
                       if (lastIndex === -1) {
                           // No space found, just cut at chunk size
                           lastIndex = chunkSize -1;
                       }
                    } else if (lastIndex === -1) {
                        // No sentence end and chunk is not full (end of text)
                        lastIndex = textChunk.length -1;
                    }

                    return lastIndex + startIdx + 1; // Return index relative to original string
                };

                const speakChunk = () => {
                    if (!this.isSpeaking || startIndex >= contentToSpeak.length) {
                        console.log("Speech stopped or finished.");
                        this.isSpeaking = false;
                        this.msg = null;
                        return;
                    }

                    const endIndex = findLastSentenceIndex(startIndex);
                    const chunk = contentToSpeak.substring(startIndex, endIndex).trim();
                    startIndex = endIndex; // Move start index for next chunk

                    if (chunk) {
                        console.log("Speaking chunk:", chunk);
                        this.msg = new SpeechSynthesisUtterance(chunk); // Create new utterance for each chunk
                        this.msg.pitch = this.$store.state.config.audio_pitch || 1;
                        this.msg.rate = this.$store.state.config.audio_rate || 1;
                        if (selectedVoice) this.msg.voice = selectedVoice;

                        this.msg.onend = (event) => {
                            console.log("Chunk ended.");
                            // Use setTimeout for a tiny delay between chunks if needed
                             setTimeout(speakChunk, 50);
                            //speakChunk(); // Speak next chunk immediately
                        };
                        this.msg.onerror = (event) => {
                           console.error("Speech synthesis error:", event.error);
                           this.isSpeaking = false; // Stop on error
                           this.msg = null;
                        };

                        this.speechSynthesis.speak(this.msg);
                    } else if (startIndex < contentToSpeak.length) {
                         // If chunk was empty but content remains, try next chunk
                         speakChunk();
                    } else {
                         // Empty chunk and end of content
                         this.isSpeaking = false;
                         this.msg = null;
                         console.log("Finished speaking naturally.");
                    }
                };

                console.log("Starting first chunk...");
                speakChunk(); // Start the process
            } else {
                 console.error("Speech synthesis not available.");
                 this.isSpeaking = false; // Reset state if speech is unavailable
            }
        },
   
        toggleModel() {
            // This seemed unused, repurposing for step expansion?
            // this.expanded = !this.expanded;
            // Keeping the step expansion logic separate in toggleExpanded()
            console.warn("toggleModel function called but seems unused.");
        },
        addBlock(bloc_name){
            if (!this.$refs.mdTextarea) return; // Ensure textarea exists

            let textarea = this.$refs.mdTextarea;
            let ss = textarea.selectionStart;
            let se = textarea.selectionEnd;
            let selectedText = this.message.content.slice(ss, se);
            let blockStart = "```" + bloc_name + "\n";
            let blockEnd = "\n```";
            let finalInsertion = "";
            let cursorPos = ss; // Default cursor position

             // Check if cursor is at the beginning of a line or file
            let isOnNewLine = ss === 0 || this.message.content[ss - 1] === '\n';
            
            let prefix = isOnNewLine ? "" : "\n"; // Add newline before if not already on one
            let suffix = "\n"; // Always add newline after block

            if (selectedText) {
                // Wrap selected text
                finalInsertion = prefix + blockStart + selectedText + blockEnd + suffix;
                this.message.content = this.message.content.slice(0, ss) + finalInsertion + this.message.content.slice(se);
                cursorPos = ss + prefix.length + blockStart.length + selectedText.length + blockEnd.length; // Place cursor after the block
            } else {
                // Insert empty block
                finalInsertion = prefix + blockStart + blockEnd + suffix;
                this.message.content = this.message.content.slice(0, ss) + finalInsertion + this.message.content.slice(ss);
                cursorPos = ss + prefix.length + blockStart.length; // Place cursor inside the block
            }


            this.$nextTick(() => {
                textarea.focus();
                textarea.selectionStart = textarea.selectionEnd = cursorPos;
                this.adjustTextareaHeight(textarea); // Adjust height after adding block
            });
        },
        copyContentToClipboard() {
            navigator.clipboard.writeText(this.message.content).then(() => {
                this.$store.state.toast.showToast("Message copied to clipboard!", 4, true);
            }).catch(err => {
                this.$store.state.toast.showToast("Failed to copy message: " + err, 4, false);
            });
            // Original emit might be needed for other integrations
            // this.$emit('copy', this) 
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
             // Include metadata when updating
            this.$emit('updateMessage', this.message.id, this.message.content, this.message.metadata);
            this.editMsgMode = false
        },
        resendMessage(msg_type) {
            this.$emit('resendMessage', this.message.id, this.message.content, msg_type)
        },
        continueMessage() {
            console.log("Emitting continueMessage")
            this.$emit('continueMessage', this.message.id, this.message.content)
        },
        getImgUrl() {
            if (this.avatar) {
                return this.avatar; // If avatar is a full URL
            } 
            //console.log("No valid avatar found, using placeholder.")
            return botImgPlaceholder;
        },
        defaultImg(event) {
            console.warn("Failed to load avatar, using placeholder.")
            event.target.src = botImgPlaceholder
        },
        parseDate(tdate) { // Kept original logic, but prettyDate is used
            let system_date = new Date(Date.parse(tdate));
            let user_date = new Date();
            if (isNaN(system_date)) return tdate; // Handle invalid date

            let diff = Math.floor((user_date - system_date) / 1000);
            if (diff <= 1) { return "just now"; }
            if (diff < 20) { return diff + " seconds ago"; }
            if (diff < 40) { return "half a minute ago"; }
            if (diff < 60) { return "less than a minute ago"; }
            if (diff <= 90) { return "one minute ago"; }
            if (diff <= 3540) { return Math.round(diff / 60) + " minutes ago"; }
            if (diff <= 5400) { return "1 hour ago"; }
            if (diff <= 86400) { return Math.round(diff / 3600) + " hours ago"; }
            if (diff <= 129600) { return "1 day ago"; }
            if (diff < 604800) { return Math.round(diff / 86400) + " days ago"; }
            if (diff <= 777600) { return "1 week ago"; }
            // Format older dates more conventionally
             const options = { year: 'numeric', month: 'short', day: 'numeric' };
             return system_date.toLocaleDateString(undefined, options);
        },
        prettyDate(time) {
            if (!time) return "";
            let date;
            try {
                 date = new Date((time || "").replace(/-/g, "/").replace(/[TZ]/g, " "));
                 if (isNaN(date)) throw new Error("Invalid date");
            } catch(e) {
                console.error("Error parsing date:", time, e);
                return time; // Return original string if parsing fails
            }

            let diff = (((new Date()).getTime() - date.getTime()) / 1000);
            let day_diff = Math.floor(diff / 86400);

            if (day_diff < 0) { // Handle future dates?
                 return date.toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' });
            }

            if (day_diff === 0) {
                if (diff < 60) return "just now";
                if (diff < 120) return "1 minute ago";
                if (diff < 3600) return Math.floor(diff / 60) + " minutes ago";
                if (diff < 7200) return "1 hour ago";
                return Math.floor(diff / 3600) + " hours ago";
            } else if (day_diff === 1) {
                return "Yesterday";
            } else if (day_diff < 7) {
                return day_diff + " days ago";
            } else if (day_diff < 31) {
                 return Math.ceil(day_diff / 7) + " weeks ago";
            } else {
                 const options = { year: 'numeric', month: 'short', day: 'numeric' };
                 return date.toLocaleDateString(undefined, options);
            }
        },
        checkForFullSentence() {
            // Basic check: Does the new content end with a sentence terminator?
             const trimmedContent = this.message.content.trim();
             const lastChar = trimmedContent.slice(-1);
             const sentenceEnders = ['.', '!', '?', '\n']; // Consider newline as ender too

             if (sentenceEnders.includes(lastChar)) {
                 // More robust check: has at least a few words?
                 if (trimmedContent.split(/\s+/).length > 2) {
                     this.speak();
                 }
             }
        },

    }, watch: {
        audio_url(newUrl) {
             nextTick(()=>{
                 if (newUrl && this.$refs.audio_player) {
                     this.$refs.audio_player.load(); // Load the new source
                 }
             })
        },
        'message.content': function (newContent, oldContent) {
             if (this.editMsgMode && this.$refs.mdTextarea) {
                 this.$nextTick(() => {
                     this.adjustTextareaHeight(this.$refs.mdTextarea); // Adjust height while editing
                 });
             } else if (this.$store.state.config.auto_speak &&
                       !(this.$store.state.config.xtts_enable && this.$store.state.config.xtts_use_streaming_mode) &&
                       !this.isSpeaking && newContent !== oldContent) {
                 // Only check for sentence if content actually changed and we're not editing
                 this.checkForFullSentence();
             }
        },
        'message.ui': function (newUI, oldUI) {
            if (JSON.stringify(newUI) !== JSON.stringify(oldUI)) { // Basic change detection
                console.log("UI changed detected", newUI)
                this.ui_componentKey++; // Force re-render if UI structure changes significantly
            }
        },
        showConfirmation(newVal) {
            if (newVal) {
                nextTick(() => { feather.replace() });
            }
        },
        deleteMsgMode(newVal) {
            nextTick(() => { feather.replace() });
        },
        editMsgMode(newVal) {
             nextTick(() => {
                 feather.replace();
                 if (newVal && this.$refs.mdTextarea) {
                     this.$refs.mdTextarea.focus();
                     this.adjustTextareaHeight(this.$refs.mdTextarea); // Adjust height when entering edit mode
                 }
             });
        }
    },
    computed: {
        activeStepIndex() {
            if (!this.message || !this.message.steps || this.message.steps.length === 0) {
                return -1; // No steps
            }
            return this.message.steps.findIndex(step => !step.done);
        },
        isProcessingSteps() {
            return this.activeStepIndex !== -1;
        },
        headerStepText() {
            if (this.isProcessingSteps && this.message.steps[this.activeStepIndex]) {
                 // Show current step text, add ellipsis if needed
                const currentText = this.message.steps[this.activeStepIndex].text || "Processing...";
                return `${currentText}`; // You could add "Step X: " prefix if desired
            } else if (this.message.steps.length > 0) {
                // All steps done, show final status message
                return this.message.status_message || "Processing Complete";
            }
            return "Processing Steps"; // Default fallback
        },
        finalStepsStatus() {
            // Determine the overall status *after* all steps are done.
            // This logic assumes the *last* step's status determines the overall outcome,
            // or relies on message.status_message potentially being set externally
            // based on the overall success/failure. Adjust if your logic differs.
            if (this.isProcessingSteps || this.message.steps.length === 0) {
                return null; // Not finished or no steps
            }
            // Option 1: Use the status of the very last step
             // return this.message.steps[this.message.steps.length - 1].status;

            // Option 2: Infer from status_message (crude example, adjust keywords)
            const lowerCaseStatus = (this.message.status_message || "").toLowerCase();
            if (lowerCaseStatus.includes("error") || lowerCaseStatus.includes("fail")) {
                return false;
            }
             return true; // Assume success if no explicit failure keywords

             // Option 3: Rely on an explicit final status property if you add one to the message object
        },        
        editMsgMode:{
            get(){
                // Ensure message.open reflects the internal edit state if property exists
                if(this.message && this.message.hasOwnProperty('open')) {
                    return this.editMsgMode_ || this.message.open;
                }
                return this.editMsgMode_;
            },
            set(value){
                // Update both internal state and message property if it exists
                 if(this.message && this.message.hasOwnProperty('open')) {
                    this.message.open = value;
                }
                this.editMsgMode_ = value;
                // Feather replace is handled by the watcher now
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
             try {
                return new Date(Date.parse(this.message.created_at)).toLocaleString()
             } catch (e) { return this.message.created_at; }
        },
        finished_generating_at_parsed() {
             try {
                return new Date(Date.parse(this.message.finished_generating_at)).toLocaleString()
             } catch (e) { return this.message.finished_generating_at; }
        },

        time_spent() {
            if (!this.message.started_generating_at || !this.message.finished_generating_at) return undefined;
            try {
                const startTime = new Date(Date.parse(this.message.started_generating_at));
                const endTime = new Date(Date.parse(this.message.finished_generating_at));
                if (isNaN(startTime) || isNaN(endTime)) return undefined;

                const same = endTime.getTime() === startTime.getTime();
                if (same) { return "0s"; } // Indicate zero duration clearly

                let [hours, mins, secs] = this.computeTimeDiff(startTime, endTime);

                function addZero(i) { return i < 10 ? "0" + i : i; }

                let parts = [];
                if (hours > 0) parts.push(addZero(hours) + "h");
                if (mins > 0) parts.push(addZero(mins) + "m");
                if (secs >= 0) parts.push(addZero(secs) + 's'); // Always show seconds if > 0 or if total time is < 1 min
                
                return parts.join(':') || "0s"; // Ensure something is returned

            } catch (e) { return undefined; }
        },
        warmup_duration() {
            if (!this.message.created_at || !this.message.started_generating_at) return undefined;
            try {
                const createdTime = new Date(Date.parse(this.message.created_at));
                const startTime = new Date(Date.parse(this.message.started_generating_at));
                 if (isNaN(createdTime) || isNaN(startTime)) return undefined;


                const same = startTime.getTime() === createdTime.getTime();
                if (same || startTime < createdTime ) { return "0s"; } // No warmup or invalid times

                let [hours, mins, secs] = this.computeTimeDiff(createdTime, startTime);

                function addZero(i) { return i < 10 ? "0" + i : i; }

                 let parts = [];
                 if (hours > 0) parts.push(addZero(hours) + "h");
                 if (mins > 0) parts.push(addZero(mins) + "m");
                 if (secs >= 0) parts.push(addZero(secs) + 's');

                return parts.join(':') || "0s";

            } catch (e) { return undefined; }
        },
        generation_rate() {
            if (!this.message.started_generating_at || !this.message.finished_generating_at || !this.message.nb_tokens || this.message.nb_tokens <= 0) return undefined;
             try {
                const startTime = new Date(Date.parse(this.message.started_generating_at));
                const endTime = new Date(Date.parse(this.message.finished_generating_at));
                const nb_tokens = this.message.nb_tokens;
                 if (isNaN(startTime) || isNaN(endTime)) return undefined;

                const timeDiff = endTime.getTime() - startTime.getTime();
                if (timeDiff <= 0) { return undefined; } // Avoid division by zero or negative time

                const secs = timeDiff / 1000;
                const rate = nb_tokens / secs;

                return Math.round(rate) + " t/s";
             } catch(e) { return undefined; }
        }
    }
}
</script>

<style scoped>
/* Add specific scoped styles if absolutely necessary, but prefer theme.css */
.message-details .steps-container .step-item:last-child {
     margin-bottom: 0; /* Ensure no extra margin on last item */
}

/* Keyframe for the slide-in animation (can also be global in theme.css) */
@keyframes step-slide-in {
    from {
        opacity: 0;
        transform: translateX(-15px); /* Start slightly further left */
    }
    to {
        opacity: 1;
        transform: translateX(0);
    }
}
.animate-step-slide-in {
    animation: step-slide-in 0.35s ease-out forwards;
}

/* Ensure fade icon transition is defined if not global */
.fade-icon-enter-active,
.fade-icon-leave-active {
  transition: opacity 0.2s ease-in-out, transform 0.2s ease-in-out;
}
.fade-icon-enter-from,
.fade-icon-leave-to {
  opacity: 0;
  transform: scale(0.8);
}
.fade-icon-enter-to,
.fade-icon-leave-from {
  opacity: 1;
  transform: scale(1);
}
</style>