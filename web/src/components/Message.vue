<template>
    <div class="message group relative border-2 border-transparent hover:border-blue-400 dark:hover:border-sky-500 rounded-lg transition-colors duration-150 ease-in-out">
        <div class="flex flex-row gap-2">
            <div class="flex-shrink-0">
                <div class="group/avatar">
                    <img :src="getImgUrl()" @error="defaultImg($event)" :data-popover-target="'avatar' + message.id" data-popover-placement="bottom"
                        class="w-10 h-10 rounded-full object-fill border border-blue-300 dark:border-slate-600">
                </div>
            </div>

            <div class="flex flex-col w-full flex-grow">
                <div class="flex flex-row flex-grow items-start">
                    <div class="flex flex-col mb-2">
                        <div class="message-header">{{ message.sender }}</div>
                        <div class="text-xs text-blue-500 dark:text-slate-400 font-thin" v-if="message.created_at"
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

                    <div v-if="editMsgMode" class="w-full">
                        <MarkdownEditor
                            ref="markdownEditor"
                            v-model="editableContent"
                            :theme="editorTheme"
                            editor-class="min-h-[150px] max-h-[70vh] message-editor-content"
                            toolbar-class="md-editor-toolbar-theme"
                            button-class="md-editor-button-theme"
                            :toolbar-button-icon-size="16"
                        />
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
                                        <svg v-else key="header-unknown" class="w-4 h-4 text-gray-400 dark:text-slate-500" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"></path></svg>
                                    </transition>
                                </div>
                                <span class="steps-status truncate pr-2 text-sm">{{ headerStepText }}</span>
                                <span class="toggle-icon text-xs transform transition-transform duration-200 ml-auto" :class="{ 'rotate-180': expanded }">
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
                                    <div v-for="(step, index) in message.steps" :key="`step-${message.id}-${index}`" class="step-item animate-step-slide-in" :style="{ animationDelay: `${index * 80}ms` }">
                                        <Step :done="step.done" :text="step.text" :status="step.status" :description="step.description"/>
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

                <div class="message-toolbar-wrapper">
                    <div class="message-toolbar">
                        <div v-if="editMsgMode" class="flex items-center gap-1">
                            <ToolbarButton @click.stop="cancelEdit" title="Cancel edit" icon="x" class="svg-button text-red-500 hover:bg-red-100 dark:hover:bg-red-900" />
                            <ToolbarButton @click.stop="updateMessage" title="Update message" icon="check" class="svg-button text-green-500 hover:bg-green-100 dark:hover:bg-green-900" />

                        </div>
                         <div v-else class="flex items-center gap-1">
                            <ToolbarButton @click.stop="startEdit" title="Edit message" icon="edit" class="svg-button toolbar-button" />
                            <ToolbarButton @click="copyContentToClipboard" title="Copy message to clipboard" icon="copy" class="svg-button toolbar-button" />
                            <div v-if="message.sender !== $store.state.mountedPers.name" class="flex items-center gap-1">
                                <ToolbarButton @click.stop="resendMessage('full_context')" title="Resend message with full context" icon="send" class="svg-button toolbar-button" />
                                <ToolbarButton @click.stop="resendMessage('full_context_with_internet')" title="Resend message with internet search" icon="globe" class="svg-button toolbar-button" />
                                <ToolbarButton @click.stop="resendMessage('simple_question')" title="Resend message without context" icon="refresh-cw" class="svg-button toolbar-button" />
                            </div>
                            <div v-if="message.sender === $store.state.mountedPers.name" class="flex items-center gap-1">
                                <ToolbarButton @click.stop="continueMessage" title="Continue message" icon="fast-forward" class="svg-button toolbar-button" />
                            </div>
                            <div v-if="deleteMsgMode" class="flex items-center gap-1">
                                <ToolbarButton @click.stop="deleteMsgMode = false" title="Cancel removal" icon="x" class="svg-button toolbar-button text-blue-500 hover:bg-blue-100 dark:hover:bg-blue-700" />
                                <ToolbarButton @click.stop="deleteMsg()" title="Confirm removal" icon="check" class="svg-button text-red-500 hover:bg-red-100 dark:hover:bg-red-900" />
                            </div>
                            <ToolbarButton v-else title="Remove message" icon="trash" @click="deleteMsgMode = true" class="svg-button text-red-500 hover:bg-red-100 dark:hover:bg-red-900" />
                            <ToolbarButton @click.stop="rankUp()" title="Upvote" icon="thumbs-up" class="svg-button toolbar-button text-blue-500 dark:text-blue-400" />
                            <div class="flex items-center">
                                <ToolbarButton @click.stop="rankDown()" title="Downvote" icon="thumbs-down" class="svg-button text-red-500 dark:text-red-400" />
                                <div v-if="message.rank != 0" class="text-xs font-bold rounded-full px-1.5 py-0.5 flex items-center justify-center cursor-default" :class="message.rank > 0 ? 'bg-blue-500 text-white' : 'bg-red-500 text-white'" title="Rank">{{ message.rank }}</div>
                            </div>
                            <div v-if="this.$store.state.config.active_tts_service!='None'" class="flex items-center gap-1">
                                <ToolbarButton title="Speak message" icon="volume-2" @click.stop="speak()" class="svg-button toolbar-button" :class="{ 'text-red-500 dark:text-red-400 animate-pulse': isSpeaking }"/>
                            </div>
                            <div v-if="this.$store.state.config.xtts_enable && !this.$store.state.config.xtts_use_streaming_mode" class="flex items-center gap-1">
                                <ToolbarButton v-if="!isSynthesizingVoice" title="Generate audio" icon="mic" @click.stop="read()" class="svg-button toolbar-button" />
                                <img v-else :src="loading_svg" class="w-5 h-5 animate-spin text-blue-500 dark:text-sky-400">
                            </div>
                        </div>
                    </div>
                </div>

                 <div class="message-footer">
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
import { nextTick, computed } from 'vue'
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
import DropdownSubmenu from './DropdownSubmenu.vue';
import MarkdownEditor from './MarkdownEditor.vue';
import { oneDark } from '@codemirror/theme-one-dark';
import { EditorView } from '@codemirror/view';

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
        DropdownSubmenu,
        MarkdownEditor,
    },
    props: {
        host: { type: String, required: false, default: "http://localhost:9600" },
        message: Object,
        avatar: { default: '' }
    },
    data() {
        return {
            ui_componentKey: 0,
            isSynthesizingVoice: false,
            loading_svg: loading_svg,
            audio_url: null,
            isSpeaking: false,
            speechSynthesis: null,
            voices: [],
            expanded: false,
            editMsgMode_: false,
            originalContentBeforeEdit: '',
            editableContent: '',
            deleteMsgMode: false,
        }
    },
    mounted() {
        if ('speechSynthesis' in window) {
            this.speechSynthesis = window.speechSynthesis;
            this.loadVoices();
            this.speechSynthesis.onvoiceschanged = this.loadVoices;
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
        },
        syncAudioUrlFromMetadata() {
            if (Array.isArray(this.message.metadata)) {
                const audioEntry = this.message.metadata.find(m => m?.audio_url);
                this.audio_url = audioEntry ? audioEntry.audio_url : null;
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
        read(){
            if(this.isSynthesizingVoice){
                this.isSynthesizingVoice=false;
                if (this.$refs.audio_player) {
                    this.$refs.audio_player.pause();
                }
            } else {
                this.isSynthesizingVoice=true;
                axios.post(`${this.host}/text2wav`,{text:this.message.content}).then(response => {
                    this.isSynthesizingVoice=false;
                    const newAudioUrl = response.data.url;
                    this.audio_url = newAudioUrl;
                    if(!Array.isArray(this.message.metadata)) this.message.metadata = [];
                    let audioEntry = this.message.metadata.find(m => m && typeof m === 'object' && m.hasOwnProperty('audio_url'));
                    if (audioEntry) audioEntry.audio_url = newAudioUrl;
                    else this.message.metadata.push({audio_url: newAudioUrl});
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
                    endOfSentenceMarkers.forEach(marker => { lastIndex = Math.max(lastIndex, textChunk.lastIndexOf(marker)); });
                    if (lastIndex === -1) lastIndex = textChunk.length === chunkSize ? (textChunk.lastIndexOf(' ') > -1 ? textChunk.lastIndexOf(' ') : chunkSize - 1) : textChunk.length - 1;
                    return lastIndex + startIdx + 1;
                };
                const speakChunk = () => {
                    if (!this.isSpeaking || startIndex >= contentToSpeak.length) { this.isSpeaking = false; return; }
                    const endIndex = findLastSentenceIndex(startIndex);
                    const chunk = contentToSpeak.substring(startIndex, endIndex).trim();
                    startIndex = endIndex;
                    if (chunk) {
                        const msg = new SpeechSynthesisUtterance(chunk);
                        msg.pitch = this.$store.state.config.audio_pitch || 1;
                        msg.rate = this.$store.state.config.audio_rate || 1;
                        if (selectedVoice) msg.voice = selectedVoice;
                        msg.onend = () => setTimeout(speakChunk, 50);
                        msg.onerror = (event) => { console.error("Speech error:", event.error); this.isSpeaking = false; };
                        this.speechSynthesis.speak(msg);
                    } else if (startIndex < contentToSpeak.length) speakChunk();
                    else this.isSpeaking = false;
                };
                speakChunk();
            } else this.isSpeaking = false;
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
        rankUp() { this.$emit('rankUp', this.message.id); },
        rankDown() { this.$emit('rankDown', this.message.id); },
        startEdit() {
            this.originalContentBeforeEdit = this.message.content;
            this.editableContent = this.message.content;
            this.editMsgMode = true;
             nextTick(() => {
                 if(this.$refs.markdownEditor && this.$refs.markdownEditor.editorView) {
                    this.$refs.markdownEditor.editorView.focus();
                 }
             });
        },
        cancelEdit() { this.editMsgMode = false; },
        updateMessage() {
            console.log(`sending updateMessage with: ${this.message.id}, ${this.editableContent}, ${this.message.metadata}`)
            this.$emit('updateMessage', {id:this.message.id, content:this.editableContent, metadata:this.message.metadata});
            this.editMsgMode = false;
        },
        resendMessage(msg_type) { this.$emit('resendMessage', this.message.id, this.message.content, msg_type); },
        continueMessage() { this.$emit('continueMessage', this.message.id, this.message.content); },
        getImgUrl() { return this.avatar || botImgPlaceholder; },
        defaultImg(event) { event.target.src = botImgPlaceholder; },
        prettyDate(time) {
            if (!time) return "";
            try {
                 const date = new Date((time || "").replace(/-/g, "/").replace(/[TZ]/g, " "));
                 if (isNaN(date)) return time;
                 const diff = (((new Date()).getTime() - date.getTime()) / 1000), day_diff = Math.floor(diff / 86400);
                 if (day_diff < 0) return date.toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' });
                 if (day_diff === 0) {
                     if (diff < 60) return "just now"; if (diff < 120) return "1 minute ago"; if (diff < 3600) return Math.floor(diff / 60) + " minutes ago";
                     if (diff < 7200) return "1 hour ago"; return Math.floor(diff / 3600) + " hours ago";
                 }
                 if (day_diff === 1) return "Yesterday"; if (day_diff < 7) return day_diff + " days ago";
                 if (day_diff < 31) return Math.ceil(day_diff / 7) + " weeks ago";
                 return date.toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' });
            } catch(e) { return time; }
        },
        checkForFullSentence() {
             const trimmedContent = this.message.content.trim(); const lastChar = trimmedContent.slice(-1);
             const sentenceEnders = ['.', '!', '?', '\n'];
             if (sentenceEnders.includes(lastChar) && trimmedContent.split(/\s+/).length > 2) this.speak();
        },
    },
    watch: {
        'message.open': {
            handler(newValue) {
                if (newValue === true && !this.editMsgMode_) this.startEdit();
                else if (newValue === false && this.editMsgMode_) this.cancelEdit();
            },
            immediate: true
        },
        editMsgMode_(newVal) { nextTick(feather.replace); },
        audio_url(newUrl) {
             nextTick(()=>{ if (newUrl && this.$refs.audio_player) this.$refs.audio_player.load(); });
        },
        'message.content': function (newContent, oldContent) {
             if (this.$store.state.config.auto_speak &&
                       !(this.$store.state.config.xtts_enable && this.$store.state.config.xtts_use_streaming_mode) &&
                       !this.isSpeaking && newContent !== oldContent && !this.editMsgMode_) {
                 this.checkForFullSentence();
             }
             if(!this.editMsgMode_) this.editableContent = newContent;
        },
        'message.ui': function (newUI, oldUI) {
            if (JSON.stringify(newUI) !== JSON.stringify(oldUI)) this.ui_componentKey++;
        },
        'message.metadata': { handler() { this.syncAudioUrlFromMetadata(); }, deep: true },
        deleteMsgMode() { nextTick(feather.replace); },
    },
    computed: {
        editorTheme() {
            const isDarkMode = this.$store.state.config.darkMode;
            return isDarkMode ? oneDark : EditorView.baseTheme({});
        },
        editMsgMode:{
            get(){ return this.editMsgMode_; },
            set(value){
                if (this.editMsgMode_ === value) return;
                this.editMsgMode_ = value;
                if (this.message && typeof this.message === 'object' && this.message.hasOwnProperty('open')) {
                    if (this.message.open !== value) this.message.open = value;
                }
            }
        },
        activeStepIndex() { return Array.isArray(this.message.steps) ? this.message.steps.findIndex(step => !step.done) : -1; },
        isProcessingSteps() { return this.activeStepIndex !== -1; },
        headerStepText() {
             if (!Array.isArray(this.message.steps) || this.message.steps.length === 0) return this.message.status_message || "Processing Steps";
             if (this.isProcessingSteps && this.message.steps[this.activeStepIndex]) return this.message.steps[this.activeStepIndex].text || "Processing...";
             if (this.message.status_message && this.message.status_message !== 'Thinking...') return this.message.status_message;
             return "Processing Complete";
        },
        finalStepsStatus() {
            if (!Array.isArray(this.message.steps) || this.isProcessingSteps || this.message.steps.length === 0) return null;
            const failedStep = this.message.steps.find(step => step.status === false);
            if (failedStep) return false;
            const lowerCaseStatus = (this.message.status_message || "").toLowerCase();
            if (lowerCaseStatus.includes("error") || lowerCaseStatus.includes("fail")) return false;
            return true;
        },
        created_at() { return this.prettyDate(this.message.created_at); },
        created_at_parsed() { try { return new Date(Date.parse(this.message.created_at)).toLocaleString(); } catch (e) { return this.message.created_at; } },
        finished_generating_at_parsed() { try { return new Date(Date.parse(this.message.finished_generating_at)).toLocaleString(); } catch (e) { return this.message.finished_generating_at; } },
        time_spent() {
            if (!this.message.started_generating_at || !this.message.finished_generating_at) return undefined;
            try {
                const startTime = new Date(Date.parse(this.message.started_generating_at)), endTime = new Date(Date.parse(this.message.finished_generating_at));
                if (isNaN(startTime) || isNaN(endTime) || endTime <= startTime) return "0s";
                let [h, m, s] = this.computeTimeDiff(startTime, endTime); const z = (n) => n < 10 ? "0" + n : n; let parts = [];
                if (h > 0) parts.push(z(h) + "h"); if (m > 0) parts.push(z(m) + "m"); parts.push(z(s) + 's'); return parts.join(':');
            } catch (e) { return undefined; }
        },
        warmup_duration() {
            if (!this.message.created_at || !this.message.started_generating_at) return undefined;
            try {
                const createdTime = new Date(Date.parse(this.message.created_at)), startTime = new Date(Date.parse(this.message.started_generating_at));
                if (isNaN(createdTime) || isNaN(startTime) || startTime <= createdTime) return "0s";
                let [h, m, s] = this.computeTimeDiff(createdTime, startTime); const z = (n) => n < 10 ? "0" + n : n; let parts = [];
                if (h > 0) parts.push(z(h) + "h"); if (m > 0) parts.push(z(m) + "m"); parts.push(z(s) + 's'); return parts.join(':');
            } catch (e) { return undefined; }
        },
        generation_rate() {
            if (!this.message.started_generating_at || !this.message.finished_generating_at || !this.message.nb_tokens || this.message.nb_tokens <= 0) return undefined;
            try {
                const startTime = new Date(Date.parse(this.message.started_generating_at)), endTime = new Date(Date.parse(this.message.finished_generating_at));
                if (isNaN(startTime) || isNaN(endTime)) return undefined; const timeDiff = endTime.getTime() - startTime.getTime();
                if (timeDiff <= 0) return undefined; const secs = timeDiff / 1000; return Math.round(this.message.nb_tokens / secs) + " t/s";
            } catch(e) { return undefined; }
        }
    }
}
</script>

<style scoped>
.message { padding-bottom: 2.5rem; }
.message-details .steps-container .step-item:last-child { margin-bottom: 0; }
@keyframes step-slide-in { from { opacity: 0; transform: translateX(-15px); } to { opacity: 1; transform: translateX(0); } }
.animate-step-slide-in { animation: step-slide-in 0.35s ease-out forwards; }
.fade-icon-enter-active, .fade-icon-leave-active { transition: opacity 0.2s ease-in-out, transform 0.2s ease-in-out; }
.fade-icon-enter-from, .fade-icon-leave-to { opacity: 0; transform: scale(0.8); }
.fade-icon-enter-to, .fade-icon-leave-from { opacity: 1; transform: scale(1); }
@keyframes spin { to { transform: rotate(360deg); } }
.svg-button i[data-feather] { width: 1.1rem; height: 1.1rem; }
:deep(.cm-editor) { font-size: 0.95rem; }
:deep(.cm-scroller) { font-family: 'Consolas', 'Monaco', 'Courier New', Courier, monospace; }
</style>