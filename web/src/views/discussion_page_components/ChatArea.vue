<template>
    <div class="relative flex flex-col flex-grow background-color h-full">
        <div id="messages-list"
             class="w-full z-0 flex flex-col flex-grow overflow-y-auto scrollbar"
             :class="isDragOverChat ? 'opacity-50 border-2 border-dashed border-blue-500' : ''"
             @dragover.prevent="isDragOverChat = true" @dragleave="isDragOverChat = false" @drop.prevent="handleDrop">

            <div class="container pt-4 pb-10 mb-10 w-full mx-auto px-4">
                <TransitionGroup v-if="discussionArr && discussionArr.length > 0" name="list">
                    <!-- Message components remain unchanged -->
                    <Message v-for="msg in discussionArr"
                             :key="msg.id"
                             :message="msg"
                             :id="'msg-' + msg.id"
                             :ref="'msg-' + msg.id"
                             :host="host"
                             @copy="$emit('copy-message', $event)"
                             @delete="$emit('delete-message', msg.id)"
                             @rankUp="$emit('rank-up', msg.id)"
                             @rankDown="$emit('rank-down', msg.id)"
                             @updateMessage="$emit('update-message', $event)"
                             @resendMessage="$emit('resend-message', {id: msg.id, content: msg.content, type: msg.type})"
                             @continueMessage="$emit('continue-message', {id: msg.id, content: msg.content})"
                             :avatar="getAvatar(msg.sender)"
                    />
                </TransitionGroup>

                 <!-- Use the new PromptExamples component -->
                 <PromptExamples
                     v-if="showPromptExamples"
                     :prompts="personality?.prompts_list || []"
                     @prompt-selected="handlePromptSelection"
                     class="my-4"
                 />

                 <!-- Placeholder Modal (Remains the same) -->
                 <div v-if="showPlaceholderModal" class="fixed inset-0 bg-black bg-opacity-60 dark:bg-opacity-70 flex items-center justify-center z-50 p-4">
                     <!-- Modal Content -->
                     <div class="card max-w-4xl w-full max-h-[90vh] flex flex-col p-0">
                         <h3 class="text-lg font-semibold p-4 border-b border-blue-200 dark:border-blue-700 text-blue-800 dark:text-blue-100">Fill in the placeholders</h3>
                         <div class="flex-1 flex flex-col min-h-0 overflow-hidden p-4 space-y-4">
                             <div class="p-3 bg-blue-100 dark:bg-blue-800 rounded-lg border border-blue-200 dark:border-blue-700">
                                 <h4 class="label !mb-1">Live Preview:</h4>
                                 <MarkdownRenderer
                                    ref="mdRender"
                                    :host="host"
                                    v-model:markdown-text="previewPrompt"
                                    :message_id="0"
                                    :discussion_id="0"
                                    :client_id="this.$store.state.client_id"
                                />
                                 <!-- Use the specific content getter for preview -->
                                 <div class="flex-1 h-[150px] overflow-y-auto scrollbar bg-white dark:bg-blue-900 p-2 rounded text-sm">
                                     <span class="whitespace-pre-wrap text-blue-900 dark:text-blue-100">{{ getPromptContent(previewPrompt) }}</span>
                                 </div>
                             </div>
                             <div class="flex-1 overflow-y-auto scrollbar space-y-3 pr-2">
                                 <div v-for="(placeholder, index) in parsedPlaceholders" :key="placeholder.fullText" class="flex flex-col">
                                     <label :for="'placeholder-'+index" class="label">{{ placeholder.label }}</label>
                                     <!-- Input types remain the same -->
                                     <input v-if="placeholder.type === 'text'" :id="'placeholder-'+index" v-model="placeholderValues[index]" type="text" class="input" :placeholder="placeholder.label" @input="updatePreview">
                                     <input v-if="placeholder.type === 'int'" :id="'placeholder-'+index" v-model.number="placeholderValues[index]" type="number" step="1" class="input" @input="updatePreview">
                                     <input v-if="placeholder.type === 'float'" :id="'placeholder-'+index" v-model.number="placeholderValues[index]" type="number" step="0.01" class="input" @input="updatePreview">
                                     <textarea v-if="placeholder.type === 'multiline'" :id="'placeholder-'+index" v-model="placeholderValues[index]" rows="4" class="input" @input="updatePreview"></textarea>
                                     <div v-if="placeholder.type === 'code'" class="border border-blue-300 dark:border-blue-600 rounded-md overflow-hidden">
                                         <div class="bg-blue-200 dark:bg-blue-700 p-1 px-2 text-xs text-blue-700 dark:text-blue-200">{{ placeholder.language || 'Plain text' }}</div>
                                         <textarea :id="'placeholder-'+index" v-model="placeholderValues[index]" rows="6" class="w-full p-2 font-mono bg-blue-50 dark:bg-blue-900 border-t border-blue-300 dark:border-blue-600 text-sm" @input="updatePreview"></textarea>
                                     </div>
                                     <select v-if="placeholder.type === 'options'" :id="'placeholder-'+index" v-model="placeholderValues[index]" class="input" @change="updatePreview">
                                         <option value="" disabled>Select an option</option>
                                         <option v-for="option in placeholder.options" :key="option" :value="option" class="text-blue-900 dark:text-blue-100 bg-blue-100 dark:bg-blue-800">{{ option }}</option>
                                     </select>
                                 </div>
                             </div>
                         </div>
                         <div class="p-4 flex justify-end space-x-2 border-t border-blue-200 dark:border-blue-700">
                             <button @click="cancelPlaceholders" class="btn btn-secondary">Cancel</button>
                             <button @click="applyPlaceholders" class="btn btn-primary">Apply</button>
                         </div>
                     </div>
                 </div>

                 <WelcomeComponent v-if="!hasActiveDiscussion" />

                <div class="h-40"></div> <!-- Padding at the bottom -->
            </div>

            <!-- Gradient overlay remains the same -->
            <div class="sticky bottom-0 left-0 right-0 h-48 pointer-events-none bg-gradient-to-t from-blue-100 to-transparent dark:from-blue-900 z-10"></div>
        </div>

        <!-- ChatBox remains the same -->
        <div class="sticky bottom-0 left-0 right-0 p-4 z-20 w-full max-w-4xl mx-auto" v-if="hasActiveDiscussion">
             <ChatBox ref="chatBox"
                     :loading="isGenerating"
                     :discussionList="discussionArr"
                     :on-show-toast-message="(text, duration, isok) => $store.state.toast.showToast(text, duration, isok)"
                     :on-talk="(pers) => $emit('talk-personality', pers)"
                     class="toolbar-color p-2 rounded-t-lg shadow-md"
                     @personalitySelected="$emit('recover-files')"
                     @messageSentEvent="(msg, type) => $emit('send-message', { message: msg, type: type })"
                     @sendCMDEvent="(cmd) => $emit('send-cmd', cmd)"
                     @addWebLink="$emit('add-web-link')"
                     @createEmptyUserMessage="(msg) => $emit('create-empty-user-message', msg)"
                     @createEmptyAIMessage="$emit('create-empty-ai-message')"
                     @stopGenerating="$emit('stop-generating')"
                     @loaded="$emit('recover-files')"
                     @files-dropped="handleFilesDropped"
             />
        </div>
    </div>
</template>

<script>
import { nextTick } from 'vue';
import { mapState } from 'vuex';
import Message from './Message.vue';
import ChatBox from './ChatBox.vue';
import WelcomeComponent from '@/components/WelcomeComponent.vue';
import PromptExamples from './PromptExamples.vue'; // Import the new component
import feather from 'feather-icons';
import MarkdownRenderer from '../../components/MarkdownBundle/MarkdownRenderer.vue';

// Keep parsePlaceholder function here as it's used for the modal
const parsePlaceholder = (placeholder) => {
    const parts = placeholder.replace(/^\[|\]$/g, '').split('::');
    const label = parts[0];
    if (parts.length === 1) return { label, type: 'text', fullText: placeholder };
    const type = parts[1].toLowerCase();
    const result = { label, type, fullText: placeholder };
    switch (type) {
        case 'int': case 'float': case 'multiline': break;
        case 'code': result.language = parts[2] || 'plaintext'; break;
        case 'options': result.options = parts[2] ? parts[2].split(',').map(o => o.trim()) : []; break;
        default: result.type = 'text';
    }
    return result;
};

export default {
    name: 'ChatArea',
    // Register the new component
    components: { Message, ChatBox, WelcomeComponent, PromptExamples, MarkdownRenderer, },
    props: {
        isReady: Boolean,
        hasActiveDiscussion: Boolean,
        discussionArr: Array,
        isGenerating: Boolean,
        host: String,
        personalityAvatars: Array,
    },
    emits: [
        'copy-message', 'delete-message', 'rank-up', 'rank-down', 'update-message', 'resend-message',
        'continue-message', 'send-message', 'send-cmd', 'add-web-link', 'create-empty-user-message',
        'create-empty-ai-message', 'stop-generating', 'recover-files', 'talk-personality', 'files-dropped'
    ],
    data() {
        return {
            isDragOverChat: false,
            showPlaceholderModal: false,
            selectedPrompt: '', // The original prompt string with title and placeholders
            placeholders: [], // Raw placeholder strings like "[placeholder::type]"
            placeholderValues: {}, // Values entered by the user for placeholders
            previewPrompt: '', // The prompt string used for live preview in the modal
        };
    },
    computed: {
        ...mapState(['config']),
        personality() {
            // Personality computation logic remains the same
            if (!this.config || !this.config.personalities || this.config.active_personality_id < 0 || this.config.active_personality_id >= this.config.personalities.length) {
                return null;
            }
            const activePersPath = this.config.personalities[this.config.active_personality_id];
            // Make sure this logic correctly finds the personality object containing `prompts_list`
            const fullPersonality = this.$store.state.personalities.find(p => p.full_path === activePersPath);
             return fullPersonality || { prompts_list: [] }; // Ensure it returns an object, even if empty
        },
        showPromptExamples() {
            // Condition to show prompt examples
            return this.hasActiveDiscussion && // Show only if a discussion exists
                   this.discussionArr &&
                   this.discussionArr.length < 2 && // Show only at the start of a conversation (e.g., 0 or 1 message)
                   this.personality &&
                   this.personality.prompts_list &&
                   this.personality.prompts_list.length > 0;
        },
        parsedPlaceholders() {
            // Logic remains the same
            const uniqueMap = new Map();
            this.placeholders.forEach(p => {
                const parsed = parsePlaceholder(p);
                uniqueMap.set(parsed.fullText, parsed);
            });
            return Array.from(uniqueMap.values());
        }
    },
    methods: {
        // Methods like getAvatar, scrollToBottom, handleDrop, handleFilesDropped remain the same
        getAvatar(sender) {
             if (!this.config || !sender) return null;
             const senderLower = sender.toLowerCase().trim();
             const userLower = this.config.user_name?.toLowerCase().trim();

             if (senderLower === userLower) {
                 return this.config.user_avatar ? `user_infos/${this.config.user_avatar}` : null;
             }

             // Assuming personalityAvatars is correctly populated [{ name: 'PersonalityName', avatar: 'path/to/avatar.png' }, ...]
             const personality = this.personalityAvatars.find(p => p.name?.toLowerCase().trim() === senderLower);
             return personality?.avatar ? `/${personality.avatar}` : null; // Ensure leading slash if needed
        },
        scrollToBottom() {
             nextTick(() => {
                 const msgList = document.getElementById('messages-list');
                 if (msgList) {
                     msgList.scrollTop = msgList.scrollHeight;
                 }
             });
        },
        handleDrop(event) {
            this.isDragOverChat = false;
            const files = Array.from(event.dataTransfer.files);
            this.$emit('files-dropped', files);
        },
        handleFilesDropped(files) {
            this.$emit('files-dropped', files);
        },

        // --- Placeholder and Prompt Handling Logic ---

        // Utility to get content part of the prompt (without title tag)
        getPromptContent(prompt) {
            if (!prompt) return '';
            return prompt.replace(/@<.*?>@/, '').trim();
        },

        // Triggered by the 'prompt-selected' event from PromptExamples component
        handlePromptSelection(prompt) {
            this.selectedPrompt = prompt; // Store the full original prompt
            this.previewPrompt = prompt; // Initialize preview with the full prompt (will be updated)
            this.placeholders = this.extractPlaceholders(prompt);

            if (this.placeholders.length > 0) {
                this.placeholderValues = {}; // Reset values
                this.parsedPlaceholders.forEach((ph, index) => {
                    this.placeholderValues[index] = ''; // Initialize as empty
                });
                this.showPlaceholderModal = true;
                this.updatePreview(); // Initial preview update
            } else {
                // If no placeholders, directly use the content part of the prompt
                this.setPromptInChatbox(this.getPromptContent(prompt));
            }
        },

        extractPlaceholders(prompt) {
            // Extracts placeholders like [placeholder::type] or [placeholder]
            const placeholderRegex = /\[(.*?)\]/g;
            const uniquePlaceholders = new Set([...(prompt || '').matchAll(placeholderRegex)].map(match => match[0]));
            return Array.from(uniquePlaceholders);
        },

        updatePreview() {
            let preview = this.selectedPrompt; // Start with the original prompt
            this.parsedPlaceholders.forEach((placeholder, index) => {
                const value = this.placeholderValues[index];
                const regex = new RegExp(this.escapeRegExp(placeholder.fullText), 'g');
                // Replace placeholder with value, or keep original placeholder if value is empty
                preview = preview.replace(regex, value || placeholder.fullText);
            });
            this.previewPrompt = preview; // Update the reactive preview property
        },

        escapeRegExp(string) {
             return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
        },

        cancelPlaceholders() {
            this.showPlaceholderModal = false;
            // No need to reset here, state will be reset if another prompt is selected
        },

        applyPlaceholders() {
            let finalPromptWithValues = this.selectedPrompt; // Start with original
            this.parsedPlaceholders.forEach((placeholder, index) => {
                const value = this.placeholderValues[index];
                // Only replace if a value is actually provided
                if (value !== undefined && value !== null && value !== '') {
                     const regex = new RegExp(this.escapeRegExp(placeholder.fullText), 'g');
                     finalPromptWithValues = finalPromptWithValues.replace(regex, value);
                }
                // If value is empty, the original placeholder might remain.
            });

            // Now, remove any remaining placeholder syntax *and* the title tag for the final chatbox input
            const finalContent = this.getPromptContent(finalPromptWithValues) // Remove title tag first
                                   .replace(/\[(.*?)\]/g, ''); // Remove any remaining empty/unfilled placeholder brackets

            this.showPlaceholderModal = false;
            this.setPromptInChatbox(finalContent.trim()); // Set the processed content in the chatbox
        },

        setPromptInChatbox(promptContent) {
             if (this.$refs.chatBox) {
                 this.$refs.chatBox.message = promptContent;
                 this.$refs.chatBox.focusInput(); // Optional: focus the input
             }
        },

         // --- End Placeholder Logic ---
    },
    watch: {
        // Watchers remain the same
        discussionArr: {
            handler() {
                //this.scrollToBottom();
                this.$nextTick(() => feather.replace());
            },
            deep: true
        },
         personality: {
            handler(newVal, oldVal) {
                if (newVal?.full_path !== oldVal?.full_path) {
                    // Reset placeholder state if personality changes
                    this.showPlaceholderModal = false;
                    this.selectedPrompt = '';
                    this.placeholders = [];
                    this.placeholderValues = {};
                    this.previewPrompt = '';
                }
            },
            deep: true
        }
    },
    mounted() {
        // Mounted logic remains the same
        // this.scrollToBottom();
         nextTick(() => {
            feather.replace();
         });
    },
    updated() {
        // Updated logic remains the same
         nextTick(() => {
            feather.replace();
         });
    }
};
</script>

<style scoped>
/* Scoped styles for ChatArea remain unchanged */
.pb-10 { /* Ensure enough padding at the bottom inside the scrollable area */
    padding-bottom: 10px; /* Adjust as needed */
}
.mb-10 { /* Ensure enough margin at the bottom inside the scrollable area if using margin instead */
    margin-bottom: 10px; /* Adjust as needed */
}
</style>