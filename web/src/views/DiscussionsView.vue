<template>
    <WelcomeScreen
        :is-ready="isReady"
        :loading-progress="loading_progress"
        :loading-infos="loading_infos"
        :version-info="version_info"
        :interesting-facts="interestingFacts"
    />

    <div v-if="isReady" class="flex flex-row h-screen w-screen overflow-hidden">
         <LeftPanel
             :show-left-panel="showLeftPanel"
             :discussions-list="discussionsList"
             :current-discussion="currentDiscussion"
             :toolbar-loading="isGenerating"
             :formatted-database-name="formatted_database_name"
             @select-discussion="selectDiscussion"
             @delete-discussion="deleteDiscussion"
             @open-folder="openFolder"
             @edit-title="editTitle"
             @make-title="makeTitle"
             @create-new-discussion="createNewDiscussion"
             @add-discussion-to-skills-library="addDiscussion2SkillsLibrary"
             @toggle-skills-lib="toggleSkillsLib"
             @show-skills-lib="showSkillsLib"
             @reset-database="resetDB"
             @export-database="database_selectorDialogVisible=true"
             @import-discussions="importDiscussions"
             @import-discussions-bundle="importDiscussionsBundle"
             @show-model-config="showModelConfig"
             @set-binding="setBinding"
             @copy-model-name="copyModelNameFrom"
             @set-model="setModel"
             @personality-selected="onPersonalitySelected"
             @unmount-personality="unmountPersonality"
             @remount-personality="remount_personality"
             @talk-personality="handleOnTalk"
             @personalities-ready="onPersonalitiesReadyFun"
             @show-personality-list="onShowPersListFun"
             @delete-selected="deleteDiscussionMulti"
             @export-discussions-as-json="exportDiscussionsAsJson"
             @export-discussions-to-folder="exportDiscussionsToFolder"
             @export-discussions-as-markdown="exportDiscussionsAsMarkdown"
             @show-database-selector="showDatabaseSelector"
             @import-discussion-file="importDiscussionFile"
             @toggle-star-discussion="toggleStarDiscussion"
         />

        <ChatArea
            ref="chatArea"
            :is-ready="isReady"
            :has-active-discussion="!!currentDiscussion?.id"
            :discussion-arr="discussionArr"
            :is-generating="isGenerating"
            :host="host"
            :personality-avatars="personalityAvatars"
            @copy-message="copyToClipBoard"
            @delete-message="deleteMessage"
            @rank-up="rankUpMessage"
            @rank-down="rankDownMessage"
            @update-message="updateMessage"
            @resend-message="resendMessage"
            @continue-message="continueMessage"
            @send-message="sendMsg"
            @send-cmd="sendCmd"
            @add-web-link="add_webpage"
            @create-empty-user-message="createEmptyUserMessage"
            @create-empty-ai-message="createEmptyAIMessage"
            @stop-generating="stopGenerating"
            @recover-files="recoverFiles"
            @talk-personality="handleOnTalk"
            @files-dropped="handleChatFilesDropped"
        />

         <RenderPanel
             :show-right-panel="showRightPanel"
             :html-content="lastMessageHtml"
         />

    </div>

      <ChoiceDialog reference="database_selector" class="z-20"
        :show="database_selectorDialogVisible"
        :choices="databases"
        :can-remove=true
        @choice-removed="ondatabase_selectorDialogRemoved"
        @choice-selected="ondatabase_selectorDialogSelected"
        @close-dialog="onclosedatabase_selectorDialog"
        @choice-validated="onvalidatedatabase_selectorChoice"
      />
      <div v-show="progress_visibility" role="status" class="fixed m-0 p-4 left-4 bottom-4 min-w-[24rem] max-w-[24rem] h-auto flex flex-col justify-center items-center bg-blue-500 dark:bg-blue-700 rounded-lg shadow-lg z-50 text-white">
        <ProgressBar ref="progress" :progress="progress_value" class="w-full h-3 mb-2"></ProgressBar>
        <p class="text-lg font-semibold animate-pulse">{{ loading_infos }} ...</p>
      </div>
      <PersonalityEditor ref="personality_editor" :config="currentPersonConfig" :personality="selectedPersonality"></PersonalityEditor>
      <PopupViewer ref="news"/>
      <SkillsLibraryViewer ref="skills_lib" ></SkillsLibraryViewer>
      <ChangelogPopup/>

</template>

<script>
import { defineComponent, nextTick } from 'vue';
import { mapState, mapGetters, mapActions } from 'vuex';
import axios from 'axios';
import feather from 'feather-icons';
import socket from '@/services/websocket.js';
import storeLogo from '@/assets/logo.png';

import WelcomeScreen from './discussion_page_components/WelcomeScreen.vue';
import LeftPanel from './discussion_page_components/LeftPanel.vue';
import ChatArea from './discussion_page_components/ChatArea.vue';
import RenderPanel from './discussion_page_components/RenderPanel.vue';

import ChoiceDialog from '@/components/ChoiceDialog.vue';
import ProgressBar from "@/components/ProgressBar.vue";
import SkillsLibraryViewer from "@/components/SkillsViewer.vue";
import PersonalityEditor from "@/components/PersonalityEditor.vue";
import PopupViewer from '@/components/PopupViewer.vue';
import ChangelogPopup from "@/components/ChangelogPopup.vue";
import modelImgPlaceholder from "@/assets/default_model.png";


export default defineComponent({
    name: 'DiscussionsView',
    components: {
        WelcomeScreen, LeftPanel, ChatArea, RenderPanel, ChoiceDialog,
        ProgressBar, SkillsLibraryViewer, PersonalityEditor, PopupViewer, ChangelogPopup,
    },
    data() {
        return {
            discussionsList: [],
            currentDiscussion: {},
            discussionArr: [],
            personalityAvatars: [],
            lastMessageHtml: "",
            loading: false,
            database_selectorDialogVisible: false,
            progress_visibility: false,
            progress_value: 0,
            interestingFacts: [
                "ParisNeo, the creator of LoLLMs, originally built his high-performance PC to play Cyberpunk 2077. However, his passion for AI took an unexpected turn, leading him to develop LoLLMs instead. Ironically, he never found the time to actually play the game that inspired his powerful setup!",
                "Saïph, version 14 of LoLLMs, is named after a star in Orion's constellation (Kappa Orionis), representing bright guidance in AI!",
                "The 'LoLLMs' name stands for 'Lord of Large Language Models', a playful nod to the power and potential of these AI systems.",
                "LoLLMs v15 introduced 'Personality Packages', allowing users to customize AI interactions like never before.",
                "Did you know? LoLLMs supports multiple AI backends, giving you flexibility in choosing the best engine for your needs.",
                "LoLLMs v16 focused heavily on optimizing performance, making interactions faster and smoother.",
                "The project is open-source, fostering a community of developers and users contributing to its growth.",
                "LoLLMs v17 brought enhanced multi-modal capabilities, allowing interaction with images and potentially other media.",
                "From text generation to coding assistance, LoLLMs aims to be a versatile AI tool.",
                "LoLLMs v18, codenamed 'Orion', aimed for stellar improvements in stability and user experience.",
                "The integrated 'Skills Library' allows LoLLMs to learn and perform specialized tasks.",
                "LoLLMs is designed to run locally, ensuring data privacy and control for users.",
                "The development of LoLLMs is driven by community feedback and the pursuit of cutting-edge AI accessibility.",
                "Version 19, 'Fish Edition', dives deep into refining core features and improving aquatic-themed puns (results may vary).",
                "The LoLLMs mascot, a wise owl, symbolizes knowledge and the ability to see through complex data.",
                "Future versions aim to expand integration with various platforms and enhance collaborative features.",
                "The configuration system in LoLLMs allows for deep customization of AI behavior and performance.",
                "LoLLMs supports extensions, enabling developers to add new functionalities and integrations.",
                "Keeping your LoLLMs updated ensures you have the latest features, optimizations, and security enhancements.",
                "**Binary Brain Teaser:** The version number contains a secret message: `01100001 01110010 01110000 01101001 01101100 00100000 01100110 01101111 01101111 01101100`. If you decoded that, you truly understand the spirit of v19.1 'Fish Edition'!"
            ],
            host:"",
            rebooting_audio: new Audio("/rebooting.wav"),
            connection_lost_audio: new Audio("/connection_lost.wav"),
            connection_recovered_audio: new Audio("/connection_recovered.wav"),
            chime: new Audio("/chime_aud.wav"),
             msgTypes: {
                MSG_TYPE_CONTENT                   : 1, MSG_TYPE_CONTENT_INVISIBLE_TO_AI   : 2, MSG_TYPE_CONTENT_INVISIBLE_TO_USER : 3,
            },
            operationTypes: {
                MSG_OPERATION_TYPE_ADD_CHUNK    : 0, MSG_OPERATION_TYPE_SET_CONTENT  : 1, MSG_OPERATION_TYPE_SET_CONTENT_INVISIBLE_TO_AI      : 2,
                MSG_OPERATION_TYPE_SET_CONTENT_INVISIBLE_TO_USER    : 3, MSG_OPERATION_TYPE_EXCEPTION              : 4, MSG_OPERATION_TYPE_WARNING                : 5,
                MSG_OPERATION_TYPE_INFO                   : 6, MSG_OPERATION_TYPE_STEP                   : 7, MSG_OPERATION_TYPE_STEP_START             : 8,
                MSG_OPERATION_TYPE_STEP_PROGRESS          : 9, MSG_OPERATION_TYPE_STEP_END_SUCCESS       : 10, MSG_OPERATION_TYPE_STEP_END_FAILURE       : 11,
                MSG_OPERATION_TYPE_JSON_INFOS             : 12, MSG_OPERATION_TYPE_REF                    : 13, MSG_OPERATION_TYPE_CODE                   : 14,
                MSG_OPERATION_TYPE_UI                     : 15, MSG_OPERATION_TYPE_NEW_MESSAGE            : 16, MSG_OPERATION_TYPE_FINISHED_MESSAGE       : 17,
            },
            senderTypes: {
                SENDER_TYPES_USER               : 0, SENDER_TYPES_AI                 : 1, SENDER_TYPES_SYSTEM             : 2,
            },
            is_first_connection: true,
            defaultMessageHtml: `<div class="flex flex-col items-center justify-center h-full"> <img src="${storeLogo}" alt="Welcome" class="w-40 h-40 mb-4 opacity-80" /> <p class="text-lg text-gray-600 dark:text-gray-400">Render Panel Ready</p> </div>`
        };
    },
    computed: {
        ...mapState([
            'ready', 'loading_infos', 'loading_progress', 'version', 'config',
            'databases', 'isConnected', 'isGenerating', 'client_id', 'leftPanelCollapsed',
            'rightPanelCollapsed', 'theme_vars', 'selectedPersonality',
            'currentPersonConfig', 'personalities', 'personalities_ready'
        ]),
        ...mapGetters(['getIsReady', 'getVersion', 'getConfig', 'getClientId', 'getDatabases', 'getIsConnected', 'getIsGenerating', 'getLeftPanelCollapsed', 'getRightPanelCollapsed']),
        isReady() {
            return this.getIsReady;
        },
        version_info() {
            const ver = this.getVersion;
            return (ver && ver !== "unknown") ? ver : "...";
        },
        showLeftPanel() {
             return this.isReady && !this.getLeftPanelCollapsed;
        },
        showRightPanel() {
            return this.isReady && !this.getRightPanelCollapsed;
        },
         formatted_database_name() {
            const db_name = this.config?.discussion_db_name || "default";
            return db_name.replace(/_/g, " ");
        },
    },
    methods: {
        ...mapActions(['refreshConfig', 'refreshDatabase', 'refreshBindings', 'refreshPersonalitiesZoo', 'refreshMountedPersonalities', 'refreshModelsZoo', 'refreshModels', 'fetchLanguages', 'fetchLanguage', 'fetchIsRtOn', 'toggleStarPersonality', 'toggleStarDiscussion', 'applyConfiguration', 'saveConfiguration', 'refreshModelStatus']),

        async initialLoad() {
             console.log("Initial Load Started");
             try {
                this.$store.commit('setLoadingInfos', "Getting version"); this.$store.commit('setLoadingProgress', 10);
                await this.$store.dispatch('getVersion');

                this.$store.commit('setLoadingInfos', "Connecting..."); this.$store.commit('setLoadingProgress', 20);
                while (!socket || socket.id === undefined) { await new Promise(resolve => setTimeout(resolve, 200)); }
                 this.$store.commit('setClientId', socket.id);

                this.$store.commit('setLoadingInfos', "Loading Configuration"); this.$store.commit('setLoadingProgress', 30); await this.refreshConfig();
                this.$store.commit('setLoadingInfos', "Loading Database"); this.$store.commit('setLoadingProgress', 40); await this.refreshDatabase();
                this.$store.commit('setLoadingInfos', "Getting Bindings list"); this.$store.commit('setLoadingProgress', 50); await this.refreshBindings();
                this.$store.commit('setLoadingInfos', "Getting personalities zoo"); this.$store.commit('setLoadingProgress', 60); await this.refreshPersonalitiesZoo();
                this.$store.commit('setLoadingInfos', "Getting mounted personalities"); this.$store.commit('setLoadingProgress', 70); await this.refreshMountedPersonalities();
                this.$store.commit('setLoadingInfos', "Getting models zoo"); this.$store.commit('setLoadingProgress', 80); await this.refreshModelsZoo();
                this.$store.commit('setLoadingInfos', "Getting active models"); this.$store.commit('setLoadingProgress', 90); await this.refreshModels(); await this.refreshModelStatus();

                 await this.fetchLanguages(); await this.fetchLanguage(); await this.fetchIsRtOn();
                 await this.list_discussions(); await this.getPersonalityAvatars(); this.loadLastUsedDiscussion();

                this.$store.commit('setLoadingProgress', 100); this.$store.commit('setLoadingInfos', "Ready");
                await new Promise(resolve => setTimeout(resolve, 500)); this.$store.commit('setIsReady', true);
                 console.log("Initial Load Complete"); this.setupSocketListeners();
            } catch (error) {
                console.error("Initial load failed:", error);
                 this.$store.commit('setLoadingInfos', `Error: ${error.message || 'Initialization failed'}`);
            }
        },

        setupSocketListeners() {
            socket.on('connected', this.socketIOConnected);
            socket.on('disconnect', this.socketIODisconnected);
            socket.on('show_progress', this.show_progress);
            socket.on('hide_progress', this.hide_progress);
            socket.on('update_progress', this.update_progress);
            socket.on('notification', this.notify);
            socket.on('new_message', this.handleNewMessage);
            socket.on('update_message', this.handleUpdateMessage);
            socket.on('close_message', this.finalMsgEvent);
            socket.on('discussion_renamed', this.handleDiscussionRenamed);
            socket.on('refresh_files', this.recoverFiles);
            socket.on("connect_error", this.handleConnectError);
            socket.onerror = this.handleSocketError;
            socket.onclose = this.handleSocketClose;
        },

         async list_discussions() {
            try {
                this.loading = true;
                const res = await axios.get('/list_discussions');
                if (res && Array.isArray(res.data)) {
                    this.discussionsList = res.data.map(item => ({
                        id: item.id,
                        title: item.title,
                        created_at: item.created_at, // Keep creation time for sorting/grouping
                        loading: false,
                    })).sort((a, b) => b.id - a.id);
                } else { this.discussionsList = []; }
                 this.loading = false;
            } catch (error) {
                console.error("Error listing discussions:", error);
                this.$store.state.toast.showToast(`Error fetching discussions: ${error.message}`, 4, false);
                this.discussionsList = []; this.loading = false;
            }
        },

        loadLastUsedDiscussion() {
            const id = localStorage.getItem('selected_discussion');
             if (id) {
                 const discussionItem = this.discussionsList.find(d => String(d.id) === id);
                 if (discussionItem) { this.selectDiscussion(discussionItem); }
                 else { localStorage.removeItem('selected_discussion'); this.currentDiscussion = {}; this.discussionArr = []; }
             } else { this.currentDiscussion = {}; this.discussionArr = []; }
        },

        selectDiscussion(item) {
             if (this.isGenerating) { this.$store.state.toast.showToast("Please wait for generation to finish or stop.", 4, false); return; }
             if (item && this.currentDiscussion?.id !== item.id) {
                 this.currentDiscussion = { ...item }; this.setPageTitle(item);
                 localStorage.setItem('selected_discussion', item.id); this.load_discussion(item.id);
             } else if (!item) {
                 this.currentDiscussion = {}; this.discussionArr = []; this.setPageTitle(); localStorage.removeItem('selected_discussion');
             }
             nextTick(() => this.scrollToDiscussionElement(item?.id));
        },

        async createNewDiscussion() {
             try {
                 this.loading = true; this.$store.state.toast.showToast("Creating new discussion...", 2, true);
                 socket.emit('new_discussion', { title: null });
                 socket.once('discussion_created', async (data) => {
                     if (data && data.id) {
                         await this.list_discussions();
                         const newItem = this.discussionsList.find(d => d.id === data.id);
                         if (newItem) { this.selectDiscussion(newItem); }
                         else { console.error("Newly created discussion not found in list:", data.id); this.$store.state.toast.showToast("Error: Couldn't find new discussion.", 4, false); }
                     } else { console.error("Invalid discussion_created data:", data); this.$store.state.toast.showToast("Error creating discussion.", 4, false); }
                     this.loading = false;
                 });
                 setTimeout(() => {
                     if (this.loading && !this.currentDiscussion?.id) {
                        socket.off('discussion_created'); this.loading = false; this.$store.state.toast.showToast("Timeout creating discussion.", 4, false);
                     }
                 }, 10000);
             } catch (error) {
                 console.error("Error initiating new discussion:", error); this.$store.state.toast.showToast(`Error: ${error.message}`, 4, false); this.loading = false;
             }
        },

        async deleteDiscussion(id) {
             if (!id) return;
             this.$store.state.yesNoDialog.askQuestion(`Are you sure you want to delete discussion ${id}?`, 'Delete', 'Cancel')
                 .then(async (confirmed) => {
                     if (confirmed) {
                         try {
                             this.setDiscussionLoading(id, true);
                             await axios.post('/delete_discussion', { client_id: this.client_id, id: id });
                             this.$store.state.toast.showToast(`Discussion ${id} deleted.`, 4, true);
                             this.discussionsList = this.discussionsList.filter(d => d.id !== id);
                             if (this.currentDiscussion?.id === id) { this.selectDiscussion(null); }
                         } catch (error) {
                             console.error("Error deleting discussion:", error); this.$store.state.toast.showToast(`Error deleting discussion ${id}: ${error.message}`, 4, false); this.setDiscussionLoading(id, false);
                         }
                     }
                 });
        },

        async deleteDiscussionMulti(idsToDelete) {
            if (!Array.isArray(idsToDelete) || idsToDelete.length === 0) return;
             const numToDelete = idsToDelete.length;
             this.$store.state.yesNoDialog.askQuestion(`Are you sure you want to delete ${numToDelete} discussion(s)?`, 'Delete Selected', 'Cancel')
                .then(async (confirmed) => {
                    if (confirmed) {
                        this.$store.state.toast.showToast(`Deleting ${numToDelete} discussions...`, 5, true);
                         let deletedCount = 0; let failedCount = 0;
                         idsToDelete.forEach(id => this.setDiscussionLoading(id, true));
                        for (const id of idsToDelete) {
                            try {
                                await axios.post('/delete_discussion', { client_id: this.client_id, id: id });
                                deletedCount++; this.discussionsList = this.discussionsList.filter(d => d.id !== id);
                                if (this.currentDiscussion?.id === id) { this.selectDiscussion(null); }
                            } catch (error) { console.error(`Error deleting discussion ${id}:`, error); failedCount++; this.setDiscussionLoading(id, false); }
                        }
                        if (failedCount > 0) { this.$store.state.toast.showToast(`Deleted ${deletedCount} discussions. Failed to delete ${failedCount}.`, 5, false); }
                        else { this.$store.state.toast.showToast(`Successfully deleted ${deletedCount} discussions.`, 4, true); }
                    }
                });
        },

        async editTitle({ id, title }) {
            try {
                 this.setDiscussionLoading(id, true);
                 const res = await axios.post('/edit_title', { client_id: this.client_id, id: id, title: title });
                 if (res.status === 200) {
                     const index = this.discussionsList.findIndex(d => d.id === id);
                     if (index > -1) this.discussionsList[index].title = title;
                     if (this.currentDiscussion?.id === id) this.currentDiscussion.title = title;
                     this.$store.state.toast.showToast("Title updated.", 3, true);
                 } else { throw new Error(res.data?.error || "Failed to edit title"); }
            } catch (error) { console.error("Error editing title:", error); this.$store.state.toast.showToast(`Error editing title: ${error.message}`, 4, false); }
            finally { this.setDiscussionLoading(id, false); }
        },

        async makeTitle(item) {
             const id = item.id;
             try {
                this.setDiscussionLoading(id, true); this.$store.state.toast.showToast("Generating title...", 3, true);
                 const res = await axios.post('/make_title', { client_id: this.client_id, id: id });
                 if (res.status === 200 && res.data.title) {
                     const newTitle = res.data.title; const index = this.discussionsList.findIndex(d => d.id === id);
                     if (index > -1) this.discussionsList[index].title = newTitle;
                     if (this.currentDiscussion?.id === id) this.currentDiscussion.title = newTitle;
                     this.$store.state.toast.showToast("Title generated.", 3, true);
                 } else { throw new Error(res.data?.error || "Failed to generate title"); }
             } catch (error) { console.error("Error making title:", error); this.$store.state.toast.showToast(`Error generating title: ${error.message}`, 4, false); }
             finally { this.setDiscussionLoading(id, false); }
        },

        async openFolder(item) {
            const id = item.id;
             try { await axios.post('/open_discussion_folder', { client_id: this.client_id, discussion_id: id }); this.$store.state.toast.showToast(`Opening folder for discussion ${id}...`, 3, true); }
             catch (error) { console.error("Error opening folder:", error); this.$store.state.toast.showToast(`Could not open folder: ${error.message}`, 4, false); }
        },

         toggleStarDiscussion(item) {
             this.toggleStarDiscussion(item.id);
             this.$nextTick(() => { this.$forceUpdate(); }); // May be needed for LeftPanel list re-render based on getter
        },

        load_discussion(id, callback) {
             if (!id) { this.discussionArr = []; this.lastMessageHtml = this.defaultMessageHtml; this.extractHtml(); if(callback) callback(); return; };
             this.loading = true; this.setDiscussionLoading(id, true); this.discussionArr = [];
             socket.off('discussion');
             socket.on('discussion', (data) => {
                 socket.off('discussion'); this.loading = false; this.setDiscussionLoading(id, false);
                 if (data && Array.isArray(data)) {
                     this.discussionArr = data.filter(item => item.message_type === this.msgTypes.MSG_TYPE_CONTENT || item.message_type === this.msgTypes.MSG_TYPE_CONTENT_INVISIBLE_TO_AI)
                                             .map(item => ({ ...item, status_message: "Done" }));
                     if (this.discussionArr.length > 1 && (!this.currentDiscussion.title || this.currentDiscussion.title === "untitled")) {
                          this.autoChangeTitle(id, this.discussionArr[1].content);
                     }
                     this.extractHtml(); this.recoverFiles(); if (callback) callback();
                 } else { console.warn("Received invalid discussion data for ID:", id); this.discussionArr = []; this.extractHtml(); }
                 this.scrollToBottomMessages();
             });
             socket.emit('load_discussion', { id: id });
             setTimeout(() => {
                 if (this.loading && this.currentDiscussion?.id === id) {
                     socket.off('discussion'); this.loading = false; this.setDiscussionLoading(id, false); this.$store.state.toast.showToast(`Timeout loading discussion ${id}.`, 5, false);
                 }
             }, 15000);
        },

        handleNewMessage(msgObj) {
            if (this.currentDiscussion?.id !== msgObj.discussion_id) { console.log("Received message for non-active discussion:", msgObj.discussion_id); return; }
            if (msgObj.sender_type === this.senderTypes.SENDER_TYPES_AI) { this.$store.commit('setIsGenerating', true); }
             const newMessage = {
                 sender: msgObj.sender, message_type: msgObj.message_type, sender_type: msgObj.sender_type, content: msgObj.content || (msgObj.sender_type === this.senderTypes.SENDER_TYPES_AI ? "" : ""),
                 id: msgObj.id, discussion_id: msgObj.discussion_id, parent_id: msgObj.parent_id, binding: msgObj.binding, model: msgObj.model, personality: msgObj.personality,
                 created_at: msgObj.created_at, finished_generating_at: msgObj.finished_generating_at, rank: msgObj.rank || 0, ui: msgObj.ui, steps: [], parameters: msgObj.parameters,
                 nb_tokens: msgObj.nb_tokens?msgObj.nb_tokens:0,metadata: msgObj.metadata || [], open: msgObj.open, status_message: msgObj.sender_type === this.senderTypes.SENDER_TYPES_AI ? "Generating..." : "Sent",
             };
             this.discussionArr.push(newMessage);
             if (this.discussionArr.length === 2 && (!this.currentDiscussion.title || this.currentDiscussion.title === "untitled") && newMessage.sender_type === this.senderTypes.SENDER_TYPES_USER) {
                 this.autoChangeTitle(this.currentDiscussion.id, newMessage.content);
             }
            this.extractHtml(); this.scrollToBottomMessages();
        },

        handleUpdateMessage(msgObj) {
             if (this.currentDiscussion?.id !== msgObj.discussion_id) return;
            const index = this.discussionArr.findIndex(m => m.id === msgObj.id);
             if (index === -1) { console.warn("Update received for non-existent message ID:", msgObj.id); return; }
            const messageItem = this.discussionArr[index];
             switch (msgObj.operation_type) {
                case this.operationTypes.MSG_OPERATION_TYPE_SET_CONTENT:
                case this.operationTypes.MSG_OPERATION_TYPE_SET_CONTENT_INVISIBLE_TO_AI: messageItem.content = msgObj.content; this.$store.commit('setIsGenerating', true); break;
                case this.operationTypes.MSG_OPERATION_TYPE_ADD_CHUNK: messageItem.content += msgObj.content; this.$store.commit('setIsGenerating', true); break;
                case this.operationTypes.MSG_OPERATION_TYPE_STEP: case this.operationTypes.MSG_OPERATION_TYPE_STEP_START: case this.operationTypes.MSG_OPERATION_TYPE_STEP_END_SUCCESS: case this.operationTypes.MSG_OPERATION_TYPE_STEP_END_FAILURE:
                     if (Array.isArray(msgObj.steps)) { messageItem.steps = msgObj.steps; messageItem.status_message = msgObj.steps[msgObj.steps.length - 1]?.text || messageItem.status_message; } break;
                case this.operationTypes.MSG_OPERATION_TYPE_JSON_INFOS:
                     try { messageItem.metadata = typeof msgObj.metadata === 'string' ? JSON.parse(msgObj.metadata) : msgObj.metadata || []; } catch (e) { console.error("Failed to parse metadata JSON:", e); messageItem.metadata = { error: "Failed to parse", raw: msgObj.metadata }; } break;
                case this.operationTypes.MSG_OPERATION_TYPE_UI: messageItem.ui = msgObj.ui; break;
                case this.operationTypes.MSG_OPERATION_TYPE_EXCEPTION: this.$store.state.toast.showToast(`Error: ${msgObj.content}`, 5, false); messageItem.status_message = "Error"; this.$store.commit('setIsGenerating', false); break;
                case this.operationTypes.MSG_OPERATION_TYPE_WARNING: this.$store.state.toast.showToast(`Warning: ${msgObj.content}`, 4, false); break;
             }
             if (msgObj.created_at) messageItem.created_at = msgObj.created_at; if (msgObj.started_generating_at) messageItem.started_generating_at = msgObj.started_generating_at;
             if (msgObj.nb_tokens) messageItem.nb_tokens = msgObj.nb_tokens; if (msgObj.finished_generating_at) messageItem.finished_generating_at = msgObj.finished_generating_at;
            this.extractHtml();
        },

        finalMsgEvent(msgObj) {
            if (this.currentDiscussion?.id !== msgObj.discussion_id) return;
            const index = this.discussionArr.findIndex(m => m.id === msgObj.id);
             if (index !== -1) {
                 const messageItem = this.discussionArr[index];
                 if (msgObj.content !== undefined) messageItem.content = msgObj.content;
                 messageItem.finished_generating_at = msgObj.finished_generating_at; messageItem.nb_tokens = msgObj.nb_tokens; messageItem.binding = msgObj.binding;
                 messageItem.model = msgObj.model; messageItem.personality = msgObj.personality; messageItem.status_message = "Done";
                 this.$store.commit('setIsGenerating', false); this.setDiscussionLoading(this.currentDiscussion.id, false);
                 this.extractHtml(); this.recoverFiles(); this.scrollToBottomMessages(); this.playChime();
                 if (this.config?.auto_speak && this.config?.xtts_enable) {
                     nextTick(() => {
                         const msgComponentRef = this.$refs[`msg-${msgObj.id}`];
                         if (msgComponentRef && msgComponentRef[0] && typeof msgComponentRef[0].speak === 'function') { msgComponentRef[0].speak(); }
                         else { console.warn("Could not find message component ref or speak method for ID:", msgObj.id); }
                     });
                 }
             } else {
                 console.warn("Final message event received for non-existent message ID:", msgObj.id);
                 this.$store.commit('setIsGenerating', false); this.setDiscussionLoading(this.currentDiscussion?.id, false);
             }
        },

        sendMsg({ message, type }) {
             if (!message || !message.trim()) { this.$store.state.toast.showToast("Message cannot be empty.", 4, false); return; }
             if (!this.currentDiscussion?.id) { this.$store.state.toast.showToast("Please select or create a discussion first.", 4, false); return; }
             if (this.isGenerating) { this.$store.state.toast.showToast("Please wait for the current response.", 4, false); return; }

             this.$store.commit('setIsGenerating', true); this.setDiscussionLoading(this.currentDiscussion.id, true);
             const emitEvent = type === 'internet' ? 'generate_msg_with_internet' : 'generate_msg';      
            socket.emit(emitEvent, { prompt: message });
            this.scrollToBottomMessages();
        },

        sendCmd(command) {
            if (!command || !this.currentDiscussion?.id || this.isGenerating) { if(this.isGenerating) this.$store.state.toast.showToast("Please wait for the current response.", 4, false); return; }
            this.$store.commit('setIsGenerating', true); this.setDiscussionLoading(this.currentDiscussion.id, true); this.$store.state.toast.showToast(`Executing command: ${command}...`, 3, true);
            socket.emit('execute_command', { command: command, parameters: [] });
        },

        async deleteMessage(msgId) {
             try { await axios.post('/delete_message', { client_id: this.client_id, id: msgId }); this.discussionArr = this.discussionArr.filter(m => m.id !== msgId); this.$store.state.toast.showToast("Message deleted.", 3, true); this.extractHtml(); }
             catch (error) { console.error("Error deleting message:", error); this.$store.state.toast.showToast(`Error deleting message: ${error.message}`, 4, false); }
        },

        async rankUpMessage(msgId) {
             try {
                 const res = await axios.post('/message_rank_up', { client_id: this.client_id, id: msgId });
                 if (res.data && res.data.new_rank !== undefined) { const index = this.discussionArr.findIndex(m => m.id === msgId); if (index !== -1) this.discussionArr[index].rank = res.data.new_rank; this.$store.state.toast.showToast("Rank updated.", 3, true); }
                 else { throw new Error("Invalid rank response"); }
             } catch (error) { console.error("Error ranking up:", error); this.$store.state.toast.showToast(`Error ranking up: ${error.message}`, 4, false); }
        },

        async rankDownMessage(msgId) {
             try {
                 const res = await axios.post('/message_rank_down', { client_id: this.client_id, id: msgId });
                 if (res.data && res.data.new_rank !== undefined) { const index = this.discussionArr.findIndex(m => m.id === msgId); if (index !== -1) this.discussionArr[index].rank = res.data.new_rank; this.$store.state.toast.showToast("Rank updated.", 3, true); }
                 else { throw new Error("Invalid rank response"); }
             } catch (error) { console.error("Error ranking down:", error); this.$store.state.toast.showToast(`Error ranking down: ${error.message}`, 4, false); }
        },

        async updateMessage({ id: msgId, content: newContent, metadata: audio_url }) {
             try { await axios.post('/edit_message', { client_id: this.client_id, id: msgId, message: newContent, metadata: audio_url ? [{ audio_url: audio_url }] : [] }); const index = this.discussionArr.findIndex(m => m.id === msgId); if (index !== -1) { this.discussionArr[index].content = newContent; } this.$store.state.toast.showToast("Message updated.", 3, true); this.extractHtml(); }
             catch (error) { console.error("Error updating message:", error); this.$store.state.toast.showToast(`Error updating message: ${error.message}`, 4, false); }
        },

         resendMessage({ id, content, type }) {
            if (this.isGenerating) { this.$store.state.toast.showToast("Please wait for the current response.", 4, false); return; }
             this.$store.commit('setIsGenerating', true); this.setDiscussionLoading(this.currentDiscussion.id, true); this.$store.state.toast.showToast(`Resending message ${id}...`, 3, true);
             const resendIndex = this.discussionArr.findIndex(m => m.id === id);
             if (resendIndex !== -1) { this.discussionArr = this.discussionArr.slice(0, resendIndex + 1); this.discussionArr[resendIndex].status_message = "Resending..."; }
            socket.emit('generate_msg_from', { prompt: content, id: id, msg_type: type }); this.scrollToBottomMessages();
        },

         continueMessage({ id, content }) {
            if (this.isGenerating) { this.$store.state.toast.showToast("Please wait for the current response.", 4, false); return; }
             this.$store.commit('setIsGenerating', true); this.setDiscussionLoading(this.currentDiscussion.id, true); this.$store.state.toast.showToast(`Continuing message ${id}...`, 3, true);
             const index = this.discussionArr.findIndex(m => m.id === id); if (index !== -1) { this.discussionArr[index].status_message = "Continuing..."; }
            socket.emit('continue_generate_msg_from', { prompt: content, id: id }); this.scrollToBottomMessages();
        },

        stopGenerating() {
             if (!this.isGenerating) return; socket.emit('cancel_generation'); this.$store.commit('setIsGenerating', false); this.setDiscussionLoading(this.currentDiscussion?.id, false); this.$store.state.toast.showToast("Generation stopped.", 4, true);
             if (this.discussionArr.length > 0) {
                 const lastMessage = this.discussionArr[this.discussionArr.length - 1];
                 if (lastMessage.status_message === "Generating..." || lastMessage.sender_type === this.senderTypes.SENDER_TYPES_AI && !lastMessage.finished_generating_at) { lastMessage.status_message = "Stopped"; }
             } this.scrollToBottomMessages();
        },

         createEmptyUserMessage(message) { if (!this.currentDiscussion?.id) return; socket.emit('create_empty_message', { type: 0, message: message }); this.$store.state.toast.showToast("Creating empty user message...", 2, true); },
         createEmptyAIMessage() { if (!this.currentDiscussion?.id) return; socket.emit('create_empty_message', { type: 1 }); this.$store.state.toast.showToast("Creating empty AI message...", 2, true); },

        setDiscussionLoading(id, isLoading) {
             const index = this.discussionsList.findIndex(d => d.id === id);
             if (index !== -1) { this.discussionsList[index].loading = isLoading; }
        },
        setPageTitle(item = null) {
            const baseTitle = 'L🌟LLMS WebUI'; let discussionTitle = "Welcome";
            if (item && item.title && item.title !== "untitled") { discussionTitle = item.title; } else if (item) { discussionTitle = "New Discussion"; }
            document.title = `${baseTitle} - ${discussionTitle}`;
        },
        scrollToBottomMessages() {
             nextTick(() => { const msgList = document.getElementById('messages-list'); if (msgList) { msgList.scrollTop = msgList.scrollHeight; } });
        },
         scrollToDiscussionElement(id) {
            if (!id) return;
             nextTick(() => { const el = document.getElementById(`dis-${id}`); const container = document.getElementById('leftPanelScroll'); if (el && container) { container.scrollTo({ top: el.offsetTop, behavior: 'smooth' }); } });
        },
        copyToClipBoard(messageEntry) {
             let content = messageEntry.message.content || ""; let result = content;
             if (this.config?.copy_to_clipboard_add_all_details) {
                 const details = [
                     messageEntry.message.sender ? `Sender: ${messageEntry.message.sender}` : null, messageEntry.message.personality ? `Personality: ${messageEntry.message.personality}` : null,
                     messageEntry.created_at_parsed ? `Created: ${messageEntry.created_at_parsed}` : null, messageEntry.message.binding ? `Binding: ${messageEntry.message.binding}` : null,
                     messageEntry.message.model ? `Model: ${messageEntry.message.model}` : null, messageEntry.message.seed ? `Seed: ${messageEntry.message.seed}` : null,
                     messageEntry.time_spent ? `Time spent: ${messageEntry.time_spent}` : null,
                 ].filter(Boolean).join('\n'); result = `${details}\n\n${content}`;
             }
             navigator.clipboard.writeText(result) .then(() => this.$store.state.toast.showToast("Copied to clipboard.", 3, true)) .catch(err => { console.error("Clipboard copy failed:", err); this.$store.state.toast.showToast("Failed to copy.", 4, false); });
        },
        playChime() { this.chime.play().catch(e => console.debug("Chime play interrupted or failed:", e)); },

        async recoverFiles() {
             if (!this.currentDiscussion?.id) return;
             try {
                 const res = await axios.post('/get_discussion_files_list', { client_id: this.client_id });
                 const chatBoxRef = this.$refs.chatArea?.$refs.chatBox;
                 if (res.data && chatBoxRef) {
                     chatBoxRef.filesList = res.data.files || [];
                     chatBoxRef.isFileSentList = (res.data.files || []).map(() => true);
                 }
             } catch (error) { console.error("Error recovering files:", error); this.$store.state.toast.showToast("Could not load discussion files.", 4, false); }
        },
        handleChatFilesDropped(files) { if (this.$refs.chatArea?.$refs.chatBox) { this.$refs.chatArea.$refs.chatBox.handleFiles(files); } },
         importDiscussionFile(file) { if (!file || file.type !== 'application/json') { this.$store.state.toast.showToast("Please drop a valid JSON discussion file.", 4, false); return; } this.parseAndImportDiscussions(file); },
        async parseAndImportDiscussions(file) {
             try { this.$store.state.toast.showToast("Importing discussion(s)...", 3, true); const jsonData = await this.readFileAsJson(file); const discussionsToImport = Array.isArray(jsonData) ? jsonData : [jsonData]; if (discussionsToImport.length === 0) { throw new Error("JSON file contains no discussion data."); }
                 const res = await axios.post('/import_multiple_discussions', { client_id: this.client_id, jArray: discussionsToImport });
                 if (res.data?.status) { this.$store.state.toast.showToast(`Successfully imported ${discussionsToImport.length} discussion(s).`, 4, true); await this.list_discussions(); }
                 else { throw new Error(res.data?.error || "Import failed on backend."); }
             } catch (error) { console.error("Error importing discussions:", error); this.$store.state.toast.showToast(`Import failed: ${error.message}`, 5, false); }
        },
         readFileAsJson(file) { return new Promise((resolve, reject) => { const reader = new FileReader(); reader.onload = (event) => { try { resolve(JSON.parse(event.target.result)); } catch (e) { reject(new Error("Failed to parse JSON file.")); } }; reader.onerror = (error) => reject(new Error("Failed to read file.")); reader.readAsText(file); }); },
         importDiscussions(event) { const file = event.target.files[0]; if (file) { this.parseAndImportDiscussions(file); } event.target.value = null; },
        importDiscussionsBundle(event){ console.warn("Discussion bundle import not implemented yet."); this.$store.state.toast.showToast("Bundle import not yet available.", 4, false); event.target.value = null; },

         async exportDiscussionsAsFormat(format, selectedIds) {
            if (!Array.isArray(selectedIds) || selectedIds.length === 0) { this.$store.state.toast.showToast("No discussions selected for export.", 4, false); return; }
            try { this.$store.state.toast.showToast(`Exporting ${selectedIds.length} discussions as ${format}...`, 4, true); this.loading = true;
                 const res = await axios.post('/export_multiple_discussions', { client_id: this.client_id, discussion_ids: selectedIds, export_format: format }, { responseType: format === 'json' ? 'json' : 'blob' }); // Adjust responseType
                 if (res.data) {
                     const filename = `discussions_export_${new Date().toISOString().replace(/[:.]/g, '-')}.${format}`;
                     const blob = format === 'json' ? new Blob([JSON.stringify(res.data, null, 2)], { type: 'application/json' }) : new Blob([res.data], { type: 'text/plain' }); // Create Blob correctly
                     const url = URL.createObjectURL(blob); const a = document.createElement('a'); a.href = url; a.download = filename; document.body.appendChild(a); a.click(); document.body.removeChild(a); URL.revokeObjectURL(url);
                     this.$store.state.toast.showToast("Export successful.", 4, true);
                 } else { throw new Error("Backend returned no data for export."); }
            } catch (error) { console.error(`Error exporting discussions as ${format}:`, error); this.$store.state.toast.showToast(`Export failed: ${error.response?.data?.error || error.message}`, 5, false); }
            finally { this.loading = false; }
        },
        exportDiscussionsAsJson(selectedItems) { this.exportDiscussionsAsFormat('json', selectedItems.map(item => item.id)); },
        exportDiscussionsAsMarkdown(selectedItems) { this.exportDiscussionsAsFormat('markdown', selectedItems.map(item => item.id)); },
        exportDiscussionsToFolder(selectedItems) { console.warn("Export to folder not implemented yet."); this.$store.state.toast.showToast("Export to folder is not yet available.", 4, false); },

        showDatabaseSelector() { this.database_selectorDialogVisible = true; },
        onclosedatabase_selectorDialog() { this.database_selectorDialogVisible = false; },
        async ondatabase_selectorDialogRemoved(choice) { console.log("Database removal not implemented on backend:", choice); },
        async ondatabase_selectorDialogSelected(choice) { /* Selection validated in next step */ },
        async onvalidatedatabase_selectorChoice(choice) {
             this.database_selectorDialogVisible = false; const dbName = typeof choice === 'string' ? choice : choice.name; if (dbName === this.config?.discussion_db_name) { this.$store.state.toast.showToast("Database already selected.", 3, true); return; }
             try { this.$store.state.toast.showToast(`Selecting database: ${dbName}...`, 4, true); const res = await axios.post("/select_database", { client_id: this.client_id, name: dbName });
                 if (res.data?.status) { this.$store.state.toast.showToast("Database changed. Reloading...", 5, true); setTimeout(() => window.location.reload(), 1500); }
                 else { throw new Error(res.data?.error || "Failed to select database."); }
             } catch (error) { console.error("Error selecting database:", error); this.$store.state.toast.showToast(`Error selecting database: ${error.message}`, 5, false); }
        },

         extractHtml() {
            if (this.discussionArr && this.discussionArr.length > 0) {
                 const lastMessageContent = this.discussionArr[this.discussionArr.length - 1].content || "";
                 const startTag = '```html'; const endTag = '```'; let startIndex = lastMessageContent.indexOf(startTag);
                 if (startIndex !== -1) { startIndex += startTag.length; let endIndex = lastMessageContent.indexOf(endTag, startIndex); this.lastMessageHtml = endIndex === -1 ? lastMessageContent.substring(startIndex).trim() : lastMessageContent.substring(startIndex, endIndex).trim(); }
                 else { const trimmedContent = lastMessageContent.trim().toLowerCase(); if (trimmedContent.startsWith('<!doctype html') || trimmedContent.startsWith('<html')) { this.lastMessageHtml = lastMessageContent.trim(); } else { this.lastMessageHtml = this.defaultMessageHtml; } }
            } else { this.lastMessageHtml = this.defaultMessageHtml; }
        },

        async addDiscussion2SkillsLibrary() {
             if (!this.currentDiscussion?.id) { this.$store.state.toast.showToast("No discussion selected.", 4, false); return; }
             try { this.$store.state.toast.showToast("Adding discussion to skills library...", 3, true); const res = await axios.post("/add_discussion_to_skills_library", { client_id: this.client_id }); if (res.data?.status) { this.$store.state.toast.showToast("Discussion added to skills.", 4, true); } else { throw new Error(res.data?.error || "Failed to add to skills library."); } }
             catch (error) { console.error("Error adding to skills library:", error); this.$store.state.toast.showToast(`Error: ${error.message}`, 5, false); }
        },
        async toggleSkillsLib() {
             const newState = !this.config.activate_skills_lib;
             try { this.$store.commit('setConfig', { ...this.config, activate_skills_lib: newState }); await this.applyConfiguration(); this.$store.state.toast.showToast(`Skills library ${newState ? 'activated' : 'deactivated'}.`, 4, true); }
             catch (error) { this.$store.commit('setConfig', { ...this.config, activate_skills_lib: !newState }); console.error("Error toggling skills library:", error); }
        },
        showSkillsLib() { this.$refs.skills_lib?.showSkillsLibrary(); },
        resetDB(){ console.warn("Reset DB function not fully implemented."); this.$store.state.toast.showToast("Database reset functionality not available.", 4, false); },

        showModelConfig(item = null) {
            const bindingToShow = item || this.$store.state.installedBindings.find(b => b.name === this.config.binding_name);
            if (!bindingToShow) { this.$store.state.toast.showToast("No binding selected or found.", 4, false); return; }
             try { this.loading = true; axios.post('/get_active_binding_settings', { client_id: this.client_id, binding_name: bindingToShow.name }) .then(res => { if (res.data && Object.keys(res.data).length > 0) { this.$store.state.universalForm.showForm(res.data, `Configure ${bindingToShow.name}`, "Save", "Cancel") .then(formData => { axios.post('/set_binding_settings', { client_id: this.client_id, binding_name: bindingToShow.name, settings: formData }).then(saveRes => { if (!saveRes.data?.status) throw new Error(saveRes.data?.error || "Save failed."); this.$store.state.toast.showToast(`${bindingToShow.name} settings updated.`, 4, true); }).catch(saveErr => this.$store.state.toast.showToast(`Error saving settings: ${saveErr.message}`, 5, false)); }) .catch(() => {}); } else { this.$store.state.toast.showToast(`${bindingToShow.name} has no configurable settings.`, 3, true); } }) .catch(err => this.$store.state.toast.showToast(`Error getting settings: ${err.message}`, 5, false)) .finally(() => this.loading = false); }
             catch (error) { this.loading = false; this.$store.state.toast.showToast(`Error: ${error.message}`, 5, false); }
        },
        async setBinding(selectedBinding) {
            if (!selectedBinding || this.config.binding_name === selectedBinding.name) return; this.loading = true; this.$store.state.messageBox.showBlockingMessage(`Switching to binding: ${selectedBinding.name}...`);
             try { const res = await axios.post("/update_setting", { client_id: this.client_id, setting_name: "binding_name", setting_value: selectedBinding.name }); if (!res.data?.status) throw new Error(res.data?.error || "Update failed"); this.$store.state.toast.showToast(`Binding set to ${selectedBinding.name}. Refreshing...`, 4, true); await this.refreshConfig(); await this.refreshBindings(); await this.refreshModelsZoo(); await this.refreshModels(); this.$store.state.messageBox.hideMessage(); }
             catch (err) { this.$store.state.messageBox.hideMessage(); this.$store.state.toast.showToast(`Error setting binding: ${err.message}`, 5, false); } finally { this.loading = false; }
        },
        async setModel(selectedModel) {
            if (!selectedModel || this.config.model_name === selectedModel.name) return; this.loading = true; this.$store.state.messageBox.showBlockingMessage(`Loading model: ${selectedModel.name}...`);
             try { const res = await axios.post("/update_setting", { client_id: this.client_id, setting_name: "model_name", setting_value: selectedModel.name }); if (!res.data?.status) throw new Error(res.data?.error || "Update failed"); this.$store.state.toast.showToast(`Model set to ${selectedModel.name}.`, 4, true); await this.refreshConfig(); await this.refreshModels(); await this.refreshModelStatus(); this.$store.state.messageBox.hideMessage(); }
             catch (err) { this.$store.state.messageBox.hideMessage(); this.$store.state.toast.showToast(`Error setting model: ${err.message}`, 5, false); } finally { this.loading = false; }
        },
        copyModelNameFrom(item) { const nameToCopy = item ? `${this.config.binding_name}::${item.name}` : `${this.config.binding_name}::${this.config.model_name}`; navigator.clipboard.writeText(nameToCopy).then(() => this.$store.state.toast.showToast(`Copied: ${nameToCopy}`, 3, true)).catch(err => this.$store.state.toast.showToast(`Copy failed: ${err.message}`, 4, false)); },
        async onPersonalitySelected(pers) {
             if (!pers || !pers.full_path) return;
             const currentActivePathArr = (this.config.personalities && this.config.active_personality_id >= 0 && this.config.active_personality_id < this.config.personalities.length) ? this.config.personalities[this.config.active_personality_id] : null;
             let targetPath = pers.full_path; if(pers.language && pers.languages && pers.languages.includes(pers.language)){ targetPath = `${pers.full_path}:${pers.language}`; }
             const isSelected = currentActivePathArr === targetPath;
             if (isSelected) { this.$store.state.toast.showToast(`${pers.name} is already selected.`, 3, true); return; }
            this.loading = true; this.$store.state.toast.showToast(`Selecting personality: ${pers.name}...`, 3, true);
            try { const id = this.config.personalities.findIndex(item => item === targetPath); if (id === -1) { throw new Error("Personality path not found in current configuration."); }
                 const res = await axios.post('/select_personality', { client_id: this.client_id, id: id }); if (!res.data?.status) { throw new Error(res.data?.error || "Selection failed on backend."); }
                 this.$store.state.toast.showToast(`Selected ${pers.name}. Refreshing...`, 4, true); await this.refreshConfig(); await this.refreshMountedPersonalities(); this.load_discussion(this.currentDiscussion?.id); }
            catch (error) { console.error("Error selecting personality:", error); this.$store.state.toast.showToast(`Error selecting ${pers.name}: ${error.message}`, 5, false); } finally { this.loading = false; }
        },
        async unmountPersonality(pers) {
            if (!pers || !pers.full_path) return; this.loading = true; this.$store.state.toast.showToast(`Unmounting ${pers.name}...`, 3, true);
            try { const res = await axios.post('/unmount_personality', { client_id: this.client_id, language: pers.language || '', category: pers.category, folder: pers.folder }); if (!res.data?.status) throw new Error(res.data?.error || "Unmount failed on backend."); this.$store.state.toast.showToast(`${pers.name} unmounted. Refreshing...`, 4, true); await this.refreshConfig(); await this.refreshPersonalitiesZoo(); await this.refreshMountedPersonalities(); if (this.config.active_personality_id === -1 && this.config.personalities.length > 0 && this.$store.state.mountedPersArr.length>0) { await this.onPersonalitySelected(this.$store.state.mountedPersArr[0]); } else if (this.config.personalities.length === 0) { console.warn("No personalities left mounted."); this.$store.state.toast.showToast("Warning: No personalities mounted.", 4, false); } }
            catch (error) { console.error("Error unmounting personality:", error); this.$store.state.toast.showToast(`Error unmounting ${pers.name}: ${error.message}`, 5, false); } finally { this.loading = false; }
        },
        async remount_personality(pers) {
             if (!pers || !pers.full_path) return; this.loading = true; this.$store.state.toast.showToast(`Remounting ${pers.name}...`, 3, true);
             try { const res = await axios.post('/remount_personality', { client_id: this.client_id, category: pers.category, folder: pers.folder, language: pers.language || '' }); if (!res.data?.status) throw new Error(res.data?.error || "Remount failed."); this.$store.state.toast.showToast(`${pers.name} remounted. Refreshing...`, 4, true); await this.refreshConfig(); await this.refreshMountedPersonalities(); }
             catch (error) { console.error("Error remounting personality:", error); this.$store.state.toast.showToast(`Error remounting ${pers.name}: ${error.message}`, 5, false); } finally { this.loading = false; }
        },
        async handleOnTalk(pers) {
             if (!pers || !pers.full_path || this.isGenerating || !this.currentDiscussion?.id) { if(this.isGenerating) this.$store.state.toast.showToast("Please wait.", 4, false); if(!this.currentDiscussion?.id) this.$store.state.toast.showToast("Select discussion.", 4, false); return; }
            this.$store.commit('setIsGenerating', true); this.setDiscussionLoading(this.currentDiscussion.id, true); this.$store.state.toast.showToast(`Asking ${pers.name} to talk...`, 3, true);
             try { const currentActivePathArr = (this.config.personalities && this.config.active_personality_id >= 0 && this.config.active_personality_id < this.config.personalities.length) ? this.config.personalities[this.config.active_personality_id] : null; const targetPath = pers.language ? `${pers.full_path}:${pers.language}` : pers.full_path; const isSelected = currentActivePathArr === targetPath;
                 if (!isSelected) { const idToSelect = this.config.personalities.findIndex(item => item === targetPath); if (idToSelect === -1) { throw new Error("Target personality not mounted or path mismatch."); } const selectRes = await axios.post('/select_personality', { client_id: this.client_id, id: idToSelect }); if (!selectRes.data?.status) { throw new Error(selectRes.data?.error || "Failed to select target personality first."); } await this.refreshConfig(); await this.refreshMountedPersonalities(); this.$store.state.toast.showToast(`Switched to ${pers.name}. Now talking...`, 3, true); }
                 socket.emit('generate_msg_from', { id: -1 });
             } catch (error) { console.error("Error initiating talk:", error); this.$store.state.toast.showToast(`Error talking with ${pers.name}: ${error.message}`, 5, false); this.$store.commit('setIsGenerating', false); this.setDiscussionLoading(this.currentDiscussion.id, false); }
        },
        onPersonalitiesReadyFun() { this.$store.commit('setPersonalitiesReady', true); },
        onShowPersListFun() { /* Optional logging or action */ },

        socketIOConnected() { console.log("Socket connected:", socket.id); this.$store.commit('setIsConnected', true); this.$store.commit('setClientId', socket.id); if (!this.is_first_connection) { this.$store.state.messageBox.hideMessage(); this.$store.state.messageBox.showMessage("Server reconnected.", 3); if (this.config?.activate_audio_infos) this.connection_recovered_audio.play(); this.refreshConfig(); this.list_discussions(); if(this.currentDiscussion?.id) this.load_discussion(this.currentDiscussion.id); } this.is_first_connection = false; },
        socketIODisconnected() { console.warn("Socket disconnected."); this.$store.commit('setIsConnected', false); this.$store.commit('setIsGenerating', false); if (!this.is_first_connection) { this.$store.state.messageBox.showBlockingMessage("Server disconnected. Attempting to reconnect..."); if (this.config?.activate_audio_infos) this.connection_lost_audio.play(); } },
        handleConnectError(error) { console.error("Socket connection error:", error.message); this.$store.commit('setIsConnected', false); this.$store.commit('setIsGenerating', false); if (!this.is_first_connection) { this.$store.state.messageBox.showBlockingMessage(`Connection Error: ${error.message}. Please check the server.`); } },
        handleSocketError(event) { console.error("Socket general error:", event); this.socketIODisconnected(); },
         handleSocketClose(event) { console.warn("Socket connection closed.", event.code, event.reason); this.socketIODisconnected(); },
        handleDiscussionRenamed({ discussion_id, title }) { if (discussion_id && title) { const index = this.discussionsList.findIndex(d => d.id === discussion_id); if (index !== -1) { this.discussionsList[index].title = title; } if (this.currentDiscussion?.id === discussion_id) { this.currentDiscussion.title = title; this.setPageTitle(this.currentDiscussion); } } },
         notify(notif) { console.log("Notification received:", notif); if (['finished', 'cancelled', 'error'].includes(notif.status)) { this.$store.commit('setIsGenerating', false); this.setDiscussionLoading(this.currentDiscussion?.id, false); this.scrollToBottomMessages(); this.playChime(); }
             switch (notif.display_type) {
                 case 0: this.$store.state.toast.showToast(notif.content, notif.duration || 4, notif.notification_type !== 0); break;
                 case 1: this.$store.state.messageBox.showMessage(notif.content); break;
                 case 2: this.$store.state.messageBox.hideMessage(); this.$store.state.yesNoDialog.askQuestion(notif.content, 'Yes', 'No').then(yesRes => socket.emit("yesNoRes", { yesRes: yesRes, notification_id: notif.id })).catch(() => socket.emit("yesNoRes", { yesRes: false, notification_id: notif.id })); break;
                 case 3: this.$store.state.messageBox.showBlockingMessage(notif.content); break;
                 case 4: this.$store.state.messageBox.hideMessage(); break;
                 default: console.warn("Unknown notification display type:", notif.display_type); this.$store.state.toast.showToast(notif.content, 4, true);
             }
        },
        show_progress() { this.progress_visibility = true; },
        hide_progress() { this.progress_visibility = false; this.progress_value = 0; },
        update_progress(data) { this.progress_value = data.value || 0; },

        async getPersonalityAvatars() {
             while (!this.personalities_ready) { await new Promise(resolve => setTimeout(resolve, 200)); }
             this.personalityAvatars = (this.personalities || []).map(item => ({ name: item.name, avatar: item.avatar }));
        },
        autoChangeTitle(id, messageContent) { if (!id || !messageContent || messageContent.length === 0) return; const newTitle = messageContent.substring(0, 50) + (messageContent.length > 50 ? '...' : ''); this.editTitle({ id, title: newTitle }); },
        add_webpage() { if (this.$store.state.web_url_input_box) { this.$store.state.web_url_input_box.showPanel().then(url => { if (url && url.trim()) { this.sendWebpageAddRequest(url.trim()); } }).catch(() => {}); } else { console.error("web_url_input_box not available"); const url = prompt("Enter URL to add:"); if (url && url.trim()) { this.sendWebpageAddRequest(url.trim()); } } },
        async sendWebpageAddRequest(url) { if (!this.currentDiscussion?.id) { this.$store.state.toast.showToast("Select a discussion first.", 4, false); return; } try { this.$store.state.toast.showToast(`Adding webpage: ${url}...`, 4, true); const res = await axios.post('/add_webpage', { client_id: this.client_id, url: url }); if (res.data?.status) { this.$store.state.toast.showToast("Webpage added successfully.", 4, true); this.recoverFiles(); } else { throw new Error(res.data?.error || "Failed to add webpage."); } } catch (error) { console.error("Error adding webpage:", error); this.$store.state.toast.showToast(`Error: ${error.message}`, 5, false); } },
        handleShortcut(event) { if (event.ctrlKey && event.key === 'd') { event.preventDefault(); event.stopPropagation(); this.createNewDiscussion(); } },
    },
    watch: {
         leftPanelCollapsed(newVal) { localStorage.setItem('lollms_webui_left_panel_collapsed', newVal); },
         rightPanelCollapsed(newVal) { localStorage.setItem('lollms_webui_right_panel_collapsed', newVal); }
    },
    created() {
        const leftCollapsed = localStorage.getItem('lollms_webui_left_panel_collapsed') === 'true';
        const rightCollapsed = localStorage.getItem('lollms_webui_right_panel_collapsed') === 'true';
        this.$store.commit('setLeftPanelCollapsed', leftCollapsed); this.$store.commit('setRightPanelCollapsed', rightCollapsed);
        this.initialLoad();
    },
    mounted() {
         this.$store.commit('setNews', this.$refs.news); this.$store.commit('setPersonalityEditor', this.$refs.personality_editor);
        window.addEventListener('keydown', this.handleShortcut);
         nextTick(() => { feather.replace(); });
         if (this.config?.show_news_panel && this.$refs.news) { setTimeout(() => this.$refs.news.show(), 500); }
    },
    beforeUnmount() {
         window.removeEventListener('keydown', this.handleShortcut);
         socket.off('connected', this.socketIOConnected); socket.off('disconnect', this.socketIODisconnected); socket.off('show_progress', this.show_progress);
         socket.off('hide_progress', this.hide_progress); socket.off('update_progress', this.update_progress); socket.off('notification', this.notify);
         socket.off('new_message', this.handleNewMessage); socket.off('update_message', this.handleUpdateMessage); socket.off('close_message', this.finalMsgEvent);
         socket.off('discussion_renamed', this.handleDiscussionRenamed); socket.off('refresh_files', this.recoverFiles); socket.off("connect_error", this.handleConnectError);
         socket.onerror = null; socket.onclose = null;
    },
    updated() { nextTick(() => { feather.replace(); }); },
});
</script>

<style>
/* Global styles can remain here if truly global, otherwise move to App.vue or specific components */
.slide-right-enter-active, .slide-right-leave-active,
.slide-left-enter-active, .slide-left-leave-active {
  transition: transform 0.3s ease-in-out;
}
.slide-right-enter-from, .slide-right-leave-to { transform: translateX(-100%); }
.slide-left-enter-from, .slide-left-leave-to { transform: translateX(100%); }

.animate-pulse { animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite; }
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: .7; } }
</style>