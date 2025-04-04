<template>
    <div class="message group border-2 border-transparent hover:border-blue-400 dark:hover:border-blue-500">
        <div class="flex flex-row gap-2">
            <div class="flex-shrink-0">
                <div class="group/avatar">
                    <img :src="getImgUrl()" @error="defaultImg($event)" :data-popover-target="'avatar' + message.id" data-popover-placement="bottom"
                        class="w-10 h-10 rounded-full object-fill border border-blue-300 dark:border-blue-600">
                </div>
            </div>

            <div class="flex flex-col w-full flex-grow">
                <div class="flex flex-row flex-grow items-start">
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
                    <MarkdownRenderer
                        ref="mdRender"
                        v-if="!editMsgMode"
                        :host="host"
                        v-model:markdown-text="message.content"
                        :message_id="message.id"
                        :discussion_id="message.discussion_id"
                        :client_id="this.$store.state.client_id"
                    >
                    </MarkdownRenderer>

                    <div v-if="editMsgMode">
                        <textarea ref="mdTextarea" @keydown.tab.prevent="insertTab"
                        class="edit-textarea input w-full p-2.5 text-blue-900 dark:text-blue-100 focus:ring-blue-500 focus:border-blue-500 dark:focus:ring-blue-500 dark:focus:border-blue-400 scrollbar shadow-inner"
                        placeholder="Enter message here..."
                        v-model="message.content">
                        </textarea>
                    </div>

                    <div v-if="message.metadata !== null && !editMsgMode">
                        <div v-for="(metadata, index) in (message.metadata?.filter(m => m?.title && m?.content) || [])" :key="'json-' + message.id + '-' + index" class="mt-2">
                            <JsonViewer :title="metadata.title" :data="metadata.content" :key="'msgjson-' + message.id" />
                        </div>
                    </div>

                    <DynamicUIRenderer v-if="message.ui && !editMsgMode" ref="ui" class="w-full mt-2" :ui="message.ui" :key="'msgui-' + message.id + '-' + ui_componentKey" />

                    <audio controls v-if="audio_url!=null && !editMsgMode" class="w-full mt-2" :key="audio_url">
                        <source :src="audio_url" type="audio/wav" ref="audio_player">
                        Your browser does not support the audio element.
                    </audio>

                    <div class="message-details w-full max-w-4xl mx-auto mt-2">
                         <div v-if="message.steps && message.steps.length > 0 && !editMsgMode" class="steps-container">
                            <div class="steps-header" @click="toggleExpanded">
                                <div class="w-5 h-5 mr-2 flex-shrink-0 flex items-center justify-center">
                                    <transition name="fade-icon" mode="out-in">
                                        <div v-if="isProcessingSteps" key="header-spinner" class="step-spinner"></div>
                                        <svg v-else-if="finalStepsStatus === true" key="header-success" class="step-icon-success w-4 h-4" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path></svg>
                                        <svg v-else-if="finalStepsStatus === false" key="header-fail" class="step-icon-fail w-4 h-4" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"></path></svg>
                                        <!-- Optional: Add an icon for unknown/null status if needed -->
                                    </transition>
                                </div>
                                <span class="steps-status truncate pr-2">{{ headerStepText }}</span>
                                <span class="toggle-icon text-xs text-blue-500 dark:text-blue-400 transform transition-transform duration-200 ml-auto" :class="{ 'rotate-180': expanded }">
                                    <i data-feather="chevron-down" class="w-5 h-5"></i>
                                </span>
                            </div>
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
                                        <div v-for="(step, index) in message.steps" :key="`step-${message.id}-${index}`" class="step-item animate-step-slide-in" :style="{ animationDelay: `${index * 80}ms` }">
                                            <Step :done="step.done" :text="step.text" :status="step.status" :description="step.description"/>
                                        </div>
                                    </div>
                                </div>
                            </transition>
                        </div>

                        <div v-if="message.html_js_s && message.html_js_s.length && !editMsgMode" class="mt-2 flex flex-col items-start w-full overflow-y-auto scrollbar">
                            <div v-for="(html_js, index) in message.html_js_s" :key="`htmljs-${message.id}-${index}`" class="w-full animate-fadeIn" :style="{ animationDelay: `${index * 200}ms` }">
                                <RenderHTMLJS :htmlContent="html_js" />
                            </div>
                        </div>
                    </div>
                </div>

                 <div class="flex flex-row justify-end items-center mt-1 mx-2">
                    <div class="absolute bottom-2 right-2 invisible group-hover:visible flex flex-row items-center gap-1 bg-blue-200/70 dark:bg-blue-900/70 rounded-md p-1 shadow">
                        <div v-if="editMsgMode" class="flex items-center gap-1">
                            <ToolbarButton @click.stop="cancelEdit" title="Cancel edit" icon="x" class="svg-button text-red-500 hover:bg-red-100 dark:hover:bg-red-900" />
                            <ToolbarButton @click.stop="updateMessage" title="Update message" icon="check" class="svg-button text-green-500 hover:bg-green-100 dark:hover:bg-green-900" />
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

                         <div v-else class="flex items-center gap-1">
                            <ToolbarButton @click.stop="startEdit" title="Edit message" icon="edit" class="svg-button" />
                            <ToolbarButton @click="copyContentToClipboard" title="Copy message to clipboard" icon="copy" class="svg-button" />
                            <div v-if="message.sender !== $store.state.mountedPers.name" class="flex items-center gap-1">
                                <ToolbarButton @click.stop="resendMessage('full_context')" title="Resend message with full context" icon="send" class="svg-button" />
                                <ToolbarButton @click.stop="resendMessage('full_context_with_internet')" title="Resend message with internet search" icon="globe" class="svg-button" />
                                <ToolbarButton @click.stop="resendMessage('simple_question')" title="Resend message without context" icon="refresh-cw" class="svg-button" />
                            </div>
                            <div v-if="message.sender === $store.state.mountedPers.name" class="flex items-center gap-1">
                                <ToolbarButton @click.stop="continueMessage" title="Continue message" icon="fast-forward" class="svg-button" />
                            </div>
                            <div v-if="deleteMsgMode" class="flex items-center gap-1">
                                <ToolbarButton @click.stop="deleteMsgMode = false" title="Cancel removal" icon="x" class="svg-button text-blue-500 hover:bg-blue-100 dark:hover:bg-blue-700" />
                                <ToolbarButton @click.stop="deleteMsg()" title="Confirm removal" icon="check" class="svg-button text-red-500 hover:bg-red-100 dark:hover:bg-red-900" />
                            </div>
                            <ToolbarButton v-else title="Remove message" icon="trash" @click="deleteMsgMode = true" class="svg-button text-red-500 hover:bg-red-100 dark:hover:bg-red-900" />
                            <ToolbarButton @click.stop="rankUp()" title="Upvote" icon="thumbs-up" class="svg-button text-blue-500 dark:text-blue-400" />
                            <div class="flex items-center">
                                <ToolbarButton @click.stop="rankDown()" title="Downvote" icon="thumbs-down" class="svg-button text-red-500 dark:text-red-400" />
                                <div v-if="message.rank != 0" class="text-xs font-bold rounded-full px-1.5 py-0.5 flex items-center justify-center cursor-default" :class="message.rank > 0 ? 'bg-blue-500 text-white' : 'bg-red-500 text-white'" title="Rank">{{ message.rank }}</div>
                            </div>
                            <div v-if="this.$store.state.config.active_tts_service!='None'" class="flex items-center gap-1">
                                <ToolbarButton title="Speak message" icon="volume-2" @click.stop="speak()" class="svg-button" :class="{ 'text-red-500 dark:text-red-400 animate-pulse': isSpeaking }"/>
                            </div>
                            <div v-if="this.$store.state.config.xtts_enable && !this.$store.state.config.xtts_use_streaming_mode" class="flex items-center gap-1">
                                <ToolbarButton v-if="!isSynthesizingVoice" title="Generate audio" icon="mic" @click.stop="read()" class="svg-button" />
                                <img v-else :src="loading_svg" class="w-5 h-5 animate-spin text-blue-500 dark:text-blue-400">
                            </div>
                        </div>
                    </div>
                </div>

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
import { nextTick } from 'vue'
import feather from 'feather-icons'
import DynamicUIRenderer from "./DynamicUIRenderer.vue"
import MarkdownRenderer from './MarkdownRenderer.vue';
import RenderHTMLJS from './RenderHTMLJS.vue';
import JsonViewer from "./JsonViewer.vue";
import Step from './Step.vue';
import StatusIcon from './StatusIcon.vue';
import axios from 'axios';
import loading_svg from '@/assets/loading.svg';
import ToolbarButton from './ToolbarButton.vue';
import DropdownMenu from './DropdownMenu.vue';
import DropdownSubmenu from './DropdownSubmenu.vue'; // Assuming this exists based on usage

export default {
    name: 'Message',
    emits: ['delete', 'rankUp', 'rankDown', 'updateMessage', 'resendMessage', 'continueMessage'],
    components: {
        MarkdownRenderer,
        Step,
        StatusIcon,
        RenderHTMLJS,
        JsonViewer,
        DynamicUIRenderer,
        ToolbarButton,
        DropdownMenu,
        DropdownSubmenu, // Register if it exists
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
            loading_svg:loading_svg,
            audio_url: null,
            isSpeaking:false,
            speechSynthesis: null,
            voices: [],
            expanded: false,
            editMsgMode_: false,
            originalContentBeforeEdit: '', // Store original content
            deleteMsgMode: false,
        }
    },
    mounted() {
        if ('speechSynthesis' in window) {
            this.speechSynthesis = window.speechSynthesis;
            this.loadVoices();
            this.speechSynthesis.onvoiceschanged = this.loadVoices; // Ensure voices are loaded if they change later
        } else {
            console.error('Speech synthesis is not supported in this browser.');
        }

        this.syncAudioUrlFromMetadata();
        nextTick(feather.replace);
    },
    methods: {
        loadVoices() {
            if (!this.speechSynthesis) return;
            this.voices = this.speechSynthesis.getVoices();
            if (this.voices.length > 0) {
                // console.log("Voices available:", this.voices.length);
            }
        },
        syncAudioUrlFromMetadata() {
            if (Array.isArray(this.message.metadata)) {
                const audioEntry = this.message.metadata.find(m => m?.audio_url);
                if (audioEntry) {
                    this.audio_url = audioEntry.audio_url;
                } else {
                     this.audio_url = null; // Ensure it's null if not found
                }
            } else {
                 this.audio_url = null;
            }
        },
        toggleExpanded() {
           this.expanded = !this.expanded;
           nextTick(feather.replace);
        },
        computeTimeDiff(startTime, endTime){
            let timeDiff = endTime.getTime() - startTime.getTime();
            const hours = Math.floor(timeDiff / 3600000);
            timeDiff -= hours * 3600000;
            const mins = Math.floor(timeDiff / 60000);
            timeDiff -= mins * 60000;
            const secs = Math.floor(timeDiff / 1000);
            return [hours, mins, secs];
        },
        insertTab(event) {
            const textarea = event.target;
            const start = textarea.selectionStart;
            const end = textarea.selectionEnd;
            const isShiftPressed = event.shiftKey;
            const tab = '    ';

            // Use document.execCommand for better undo/redo support
            textarea.focus(); // Ensure focus
            if (start !== end) {
                // Handle multi-line selection indent/outdent
                const selectedLines = textarea.value.substring(start, end).split('\n');
                let currentPos = start;
                let adjustment = 0;
                let firstLineAdjust = 0;

                selectedLines.forEach((line, index) => {
                    if (isShiftPressed) {
                        if (line.startsWith(tab)) {
                            document.execCommand('delete', false, tab);
                             if(index === 0) firstLineAdjust = -tab.length;
                             adjustment -= tab.length;
                        }
                        // Move cursor to next line start if not last line
                        if (index < selectedLines.length - 1) {
                            currentPos += line.length - (line.startsWith(tab) ? tab.length : 0) + 1; // +1 for newline
                            textarea.setSelectionRange(currentPos, currentPos);
                        }
                    } else {
                         document.execCommand('insertText', false, tab);
                         if(index === 0) firstLineAdjust = tab.length;
                         adjustment += tab.length;
                         // Move cursor to next line start
                         if (index < selectedLines.length - 1) {
                            currentPos += line.length + tab.length + 1; // +1 for newline
                            textarea.setSelectionRange(currentPos, currentPos);
                         }
                    }
                });
                // Restore original selection adjusted for changes
                textarea.setSelectionRange(start + firstLineAdjust, end + adjustment);

            } else {
                 // Single cursor position
                 if (isShiftPressed) {
                     // Try to remove tab before cursor
                     if (textarea.value.substring(start - tab.length, start) === tab) {
                         textarea.setSelectionRange(start - tab.length, start);
                         document.execCommand('delete');
                     }
                 } else {
                     // Insert tab at cursor
                     document.execCommand('insertText', false, tab);
                 }
            }
             // Update v-model manually after execCommand
             this.message.content = textarea.value;
             this.adjustTextareaHeight(textarea);
             event.preventDefault();
        },
        adjustTextareaHeight(textarea) {
            if (!textarea) return;
            textarea.style.height = 'auto';
            textarea.style.height = Math.max(textarea.scrollHeight, textarea.clientHeight) + 'px'; // Use max to prevent shrinking below min-height/initial size
        },
        read(){
            if(this.isSynthesizingVoice){
                this.isSynthesizingVoice=false;
                if (this.$refs.audio_player) {
                    this.$refs.audio_player.pause();
                }
            }
            else{
                this.isSynthesizingVoice=true;
                axios.post(`${this.host}/text2wav`,{text:this.message.content}).then(response => {
                    this.isSynthesizingVoice=false;
                    const newAudioUrl = response.data.url;
                    this.audio_url = newAudioUrl;

                    if(!Array.isArray(this.message.metadata)) {
                        this.message.metadata = [];
                    }
                    let audioEntry = this.message.metadata.find(m => m && typeof m === 'object' && m.hasOwnProperty('audio_url'));
                    if (audioEntry) {
                        audioEntry.audio_url = newAudioUrl;
                    } else {
                        this.message.metadata.push({audio_url: newAudioUrl});
                    }
                     nextTick(()=>{
                        if (this.$refs.audio_player) {
                            this.$refs.audio_player.load();
                            this.$refs.audio_player.play().catch(e => console.error("Audio autoplay failed:", e));
                        }
                     });
                }).catch(ex=>{
                    this.$store.state.toast.showToast(`Error generating audio: ${ex.message || ex}`,4,false);
                    this.isSynthesizingVoice=false;
                });
            }
        },
        async speak() {
             if (this.isSpeaking) {
                 if (this.$store.state.config.active_tts_service !== "browser" && this.$store.state.config.active_tts_service !== "None") {
                     try {
                        await axios.post(`${this.host}/stop_audio`, { client_id: this.$store.state.client_id });
                        this.isSpeaking = false;
                    } catch(ex) {
                         this.$store.state.toast.showToast(`Error stopping audio: ${ex.message || ex}`, 4, false);
                         this.isSpeaking = false;
                    }
                 } else if (this.speechSynthesis) {
                     this.speechSynthesis.cancel();
                     this.isSpeaking = false;
                 }
                 return;
             }

            this.isSpeaking = true;
            const contentToSpeak = this.message.content;

            if (this.$store.state.config.active_tts_service !== "browser" && this.$store.state.config.active_tts_service !== "None") {
                axios.post(`${this.host}/text2Audio`, { client_id: this.$store.state.client_id, text: contentToSpeak })
                 .then(response => {
                    // Need backend mechanism (e.g., WebSocket) to know when done
                    // Assume stop button is the only way to stop for now
                 })
                 .catch(ex => {
                    this.$store.state.toast.showToast(`Error starting backend TTS: ${ex.message || ex}`, 4, false);
                    this.isSpeaking = false;
                });
            } else if (this.speechSynthesis && contentToSpeak) {
                let startIndex = 0;
                const chunkSize = 180;
                const selectedVoice = this.voices.find(voice => voice.name === this.$store.state.config.audio_out_voice);

                const findLastSentenceIndex = (startIdx) => {
                    let textChunk = contentToSpeak.substring(startIdx, startIdx + chunkSize);
                    const endOfSentenceMarkers = ['.', '!', '?', '\n', ';', ':'];
                    let lastIndex = -1;
                    endOfSentenceMarkers.forEach(marker => {
                        lastIndex = Math.max(lastIndex, textChunk.lastIndexOf(marker));
                    });
                    if (lastIndex === -1) {
                        lastIndex = textChunk.length === chunkSize ? (textChunk.lastIndexOf(' ') > -1 ? textChunk.lastIndexOf(' ') : chunkSize - 1) : textChunk.length - 1;
                    }
                    return lastIndex + startIdx + 1;
                };

                const speakChunk = () => {
                    if (!this.isSpeaking || startIndex >= contentToSpeak.length) {
                        this.isSpeaking = false; return;
                    }
                    const endIndex = findLastSentenceIndex(startIndex);
                    const chunk = contentToSpeak.substring(startIndex, endIndex).trim();
                    startIndex = endIndex;

                    if (chunk) {
                        const msg = new SpeechSynthesisUtterance(chunk);
                        msg.pitch = this.$store.state.config.audio_pitch || 1;
                        msg.rate = this.$store.state.config.audio_rate || 1;
                        if (selectedVoice) msg.voice = selectedVoice;
                        msg.onend = () => setTimeout(speakChunk, 50); // Slight pause
                        msg.onerror = (event) => { console.error("Speech error:", event.error); this.isSpeaking = false; };
                        this.speechSynthesis.speak(msg);
                    } else if (startIndex < contentToSpeak.length) {
                         speakChunk(); // Skip empty chunk
                    } else {
                         this.isSpeaking = false; // End of content
                    }
                };
                speakChunk();
            } else {
                 this.isSpeaking = false;
            }
        },
        addBlock(bloc_name){
            if (!this.$refs.mdTextarea) return;
            let textarea = this.$refs.mdTextarea;
            textarea.focus();
            let ss = textarea.selectionStart;
            let se = textarea.selectionEnd;
            let selectedText = textarea.value.slice(ss, se);
            let blockStart = "```" + (bloc_name || '') + "\n";
            let blockEnd = "\n```";
            let prefix = (ss === 0 || textarea.value[ss - 1] === '\n') ? "" : "\n";
            let suffix = "\n";
            let finalInsertion = "";
            let cursorPos = ss;

            if (selectedText) {
                finalInsertion = prefix + blockStart + selectedText + blockEnd + suffix;
                document.execCommand('insertText', false, finalInsertion); // Replace selection
                // Adjust cursor position after replacement (difficult with execCommand)
                // For simplicity, place cursor after inserted block
                cursorPos = ss + finalInsertion.length - suffix.length; // Place before final suffix newline
            } else {
                finalInsertion = prefix + blockStart + blockEnd + suffix;
                document.execCommand('insertText', false, finalInsertion);
                cursorPos = ss + prefix.length + blockStart.length; // Place inside the block
            }

            this.message.content = textarea.value; // Update model
            this.$nextTick(() => {
                textarea.selectionStart = textarea.selectionEnd = cursorPos;
                this.adjustTextareaHeight(textarea);
            });
        },
        copyContentToClipboard() {
            navigator.clipboard.writeText(this.message.content).then(() => {
                this.$store.state.toast.showToast("Message copied to clipboard!", 4, true);
            }).catch(err => {
                this.$store.state.toast.showToast("Failed to copy message: " + err, 4, false);
            });
        },
        deleteMsg() {
            this.$emit('delete', this.message.id);
            this.deleteMsgMode = false;
        },
        rankUp() {
            this.$emit('rankUp', this.message.id);
        },
        rankDown() {
            this.$emit('rankDown', this.message.id);
        },
        startEdit() {
            this.originalContentBeforeEdit = this.message.content; // Store original
            this.editMsgMode = true;
        },
        cancelEdit() {
            this.message.content = this.originalContentBeforeEdit; // Restore original
            this.editMsgMode = false;
        },
        updateMessage() {
            this.$emit('updateMessage', this.message.id, this.message.content, this.message.metadata);
            this.editMsgMode = false;
        },
        resendMessage(msg_type) {
            this.$emit('resendMessage', this.message.id, this.message.content, msg_type);
        },
        continueMessage() {
            this.$emit('continueMessage', this.message.id, this.message.content);
        },
        getImgUrl() {
            return this.avatar || botImgPlaceholder;
        },
        defaultImg(event) {
            event.target.src = botImgPlaceholder;
        },
        prettyDate(time) {
            if (!time) return "";
            try {
                 const date = new Date((time || "").replace(/-/g, "/").replace(/[TZ]/g, " "));
                 if (isNaN(date)) return time;
                 const diff = (((new Date()).getTime() - date.getTime()) / 1000);
                 const day_diff = Math.floor(diff / 86400);

                 if (day_diff < 0) return date.toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' });
                 if (day_diff === 0) {
                     if (diff < 60) return "just now";
                     if (diff < 120) return "1 minute ago";
                     if (diff < 3600) return Math.floor(diff / 60) + " minutes ago";
                     if (diff < 7200) return "1 hour ago";
                     return Math.floor(diff / 3600) + " hours ago";
                 }
                 if (day_diff === 1) return "Yesterday";
                 if (day_diff < 7) return day_diff + " days ago";
                 if (day_diff < 31) return Math.ceil(day_diff / 7) + " weeks ago";
                 return date.toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' });
            } catch(e) {
                return time;
            }
        },
        checkForFullSentence() {
             const trimmedContent = this.message.content.trim();
             const lastChar = trimmedContent.slice(-1);
             const sentenceEnders = ['.', '!', '?', '\n'];
             if (sentenceEnders.includes(lastChar) && trimmedContent.split(/\s+/).length > 2) {
                 this.speak();
             }
        },
    },
    watch: {
        audio_url(newUrl) {
             nextTick(()=>{
                 if (newUrl && this.$refs.audio_player) {
                     this.$refs.audio_player.load();
                 }
             });
        },
        'message.content': function (newContent, oldContent) {
             if (this.editMsgMode && this.$refs.mdTextarea) {
                 this.$nextTick(() => this.adjustTextareaHeight(this.$refs.mdTextarea));
             } else if (this.$store.state.config.auto_speak &&
                       !(this.$store.state.config.xtts_enable && this.$store.state.config.xtts_use_streaming_mode) &&
                       !this.isSpeaking && newContent !== oldContent) {
                 this.checkForFullSentence();
             }
        },
        'message.ui': function (newUI, oldUI) {
            if (JSON.stringify(newUI) !== JSON.stringify(oldUI)) {
                this.ui_componentKey++;
            }
        },
        'message.metadata': {
             handler() { this.syncAudioUrlFromMetadata(); },
             deep: true
        },
        deleteMsgMode() { nextTick(feather.replace); },
        editMsgMode(newVal) {
             nextTick(() => {
                 feather.replace();
                 if (newVal && this.$refs.mdTextarea) {
                     this.$refs.mdTextarea.focus();
                     this.adjustTextareaHeight(this.$refs.mdTextarea);
                 }
             });
        }
    },
    computed: {
        activeStepIndex() {
            return Array.isArray(this.message.steps) ? this.message.steps.findIndex(step => !step.done) : -1;
        },
        isProcessingSteps() {
            return this.activeStepIndex !== -1;
        },
        headerStepText() {
             if (!Array.isArray(this.message.steps) || this.message.steps.length === 0) {
                 return "Processing Steps"; // Default if no steps array
             }
            if (this.isProcessingSteps && this.message.steps[this.activeStepIndex]) {
                return this.message.steps[this.activeStepIndex].text || "Processing...";
            }
            return this.message.status_message || "Processing Complete";
        },
        finalStepsStatus() {
            if (!Array.isArray(this.message.steps) || this.isProcessingSteps || this.message.steps.length === 0) {
                return null; // Null means indeterminate or processing
            }
            // Check if any step failed explicitly
            const failedStep = this.message.steps.find(step => step.status === false);
            if (failedStep) {
                return false; // If any step failed, overall status is fail
            }
            // Check status message for failure keywords if no step explicitly failed
             const lowerCaseStatus = (this.message.status_message || "").toLowerCase();
             if (lowerCaseStatus.includes("error") || lowerCaseStatus.includes("fail")) {
                 return false;
             }
             return true; // Assume success if all steps done and no failure detected
        },
        editMsgMode:{
            get(){
                return this.editMsgMode_;
            },
            set(value){
                this.editMsgMode_ = value;
                if (value && this.message && typeof this.message === 'object') {
                    this.message.open = true; // Reflect in message object if needed
                } else if (this.message && typeof this.message === 'object') {
                     this.message.open = false;
                }
            }
        },
        created_at() {
            return this.prettyDate(this.message.created_at);
        },
        created_at_parsed() {
             try { return new Date(Date.parse(this.message.created_at)).toLocaleString(); }
             catch (e) { return this.message.created_at; }
        },
        finished_generating_at_parsed() {
             try { return new Date(Date.parse(this.message.finished_generating_at)).toLocaleString(); }
             catch (e) { return this.message.finished_generating_at; }
        },
        time_spent() {
            if (!this.message.started_generating_at || !this.message.finished_generating_at) return undefined;
            try {
                const startTime = new Date(Date.parse(this.message.started_generating_at));
                const endTime = new Date(Date.parse(this.message.finished_generating_at));
                if (isNaN(startTime) || isNaN(endTime) || endTime <= startTime) return "0s";
                let [h, m, s] = this.computeTimeDiff(startTime, endTime);
                const z = (n) => n < 10 ? "0" + n : n;
                let parts = [];
                if (h > 0) parts.push(z(h) + "h");
                if (m > 0) parts.push(z(m) + "m");
                parts.push(z(s) + 's');
                return parts.join(':');
            } catch (e) { return undefined; }
        },
        warmup_duration() {
            if (!this.message.created_at || !this.message.started_generating_at) return undefined;
            try {
                const createdTime = new Date(Date.parse(this.message.created_at));
                const startTime = new Date(Date.parse(this.message.started_generating_at));
                 if (isNaN(createdTime) || isNaN(startTime) || startTime <= createdTime) return "0s";
                let [h, m, s] = this.computeTimeDiff(createdTime, startTime);
                const z = (n) => n < 10 ? "0" + n : n;
                 let parts = [];
                 if (h > 0) parts.push(z(h) + "h");
                 if (m > 0) parts.push(z(m) + "m");
                 parts.push(z(s) + 's');
                return parts.join(':');
            } catch (e) { return undefined; }
        },
        generation_rate() {
            if (!this.message.started_generating_at || !this.message.finished_generating_at || !this.message.nb_tokens || this.message.nb_tokens <= 0) return undefined;
             try {
                const startTime = new Date(Date.parse(this.message.started_generating_at));
                const endTime = new Date(Date.parse(this.message.finished_generating_at));
                 if (isNaN(startTime) || isNaN(endTime)) return undefined;
                const timeDiff = endTime.getTime() - startTime.getTime();
                if (timeDiff <= 0) return undefined;
                const secs = timeDiff / 1000;
                return Math.round(this.message.nb_tokens / secs) + " t/s";
             } catch(e) { return undefined; }
        }
    }
}
</script>

<style scoped>
.edit-textarea {
    font-family: 'Consolas', 'Monaco', 'Courier New', Courier, monospace;
    background-color: rgba(240, 240, 240, 0.9); /* Slightly distinct light background */
    border: 1px solid #c0c0c0;
    min-height: 150px; /* Minimum height */
    max-height: 50vh; /* Maximum height (e.g., 50% of viewport height) */
    overflow-y: auto; /* Enable vertical scrollbar when content exceeds max-height */
    resize: vertical; /* Allow user resizing vertically */
}
.dark .edit-textarea {
    background-color: rgba(40, 48, 61, 0.9); /* Slightly distinct dark background */
    border-color: #5a6678;
    color: #e2e8f0;
}

.message-details .steps-container .step-item:last-child {
     margin-bottom: 0;
}
@keyframes step-slide-in {
    from { opacity: 0; transform: translateX(-15px); }
    to { opacity: 1; transform: translateX(0); }
}
.animate-step-slide-in {
    animation: step-slide-in 0.35s ease-out forwards;
}
.fade-icon-enter-active,
.fade-icon-leave-active {
  transition: opacity 0.2s ease-in-out, transform 0.2s ease-in-out;
}
.fade-icon-enter-from,
.fade-icon-leave-to {
  opacity: 0; transform: scale(0.8);
}
.fade-icon-enter-to,
.fade-icon-leave-from {
  opacity: 1; transform: scale(1);
}
/* Style for spinner (ensure this class exists in your CSS or Tailwind config) */
.step-spinner {
    border: 2px solid rgba(0, 0, 0, 0.1);
    border-left-color: #2563eb; /* Example color - blue */
    border-radius: 50%;
    width: 1rem; /* 16px */
    height: 1rem; /* 16px */
    animation: spin 1s linear infinite;
}
.dark .step-spinner {
    border-left-color: #60a5fa; /* Lighter blue for dark mode */
}
@keyframes spin { to { transform: rotate(360deg); } }
</style>