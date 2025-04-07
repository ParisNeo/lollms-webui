<template>
    <div class="relative flex flex-col flex-grow background-color h-full">
        <div id="messages-list"
             class="w-full z-0 flex flex-col flex-grow overflow-y-auto scrollbar"
             :class="isDragOverChat ? 'opacity-50 border-2 border-dashed border-blue-500' : ''"
             @dragover.prevent="isDragOverChat = true" @dragleave="isDragOverChat = false" @drop.prevent="handleDrop">

            <div class="container pt-4 pb-50 mb-50 w-full mx-auto px-4">
                <TransitionGroup v-if="discussionArr && discussionArr.length > 0" name="list">
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

                 <div v-if="discussionArr && discussionArr.length < 2 && personality && personality.prompts_list && personality.prompts_list.length > 0" class="w-full rounded-lg m-2 shadow-lg border border-blue-200 dark:border-blue-700 bg-blue-50 dark:bg-blue-900 p-4 pb-2">
                     <h2 class="text-2xl font-bold mb-4 text-blue-700 dark:text-blue-200 border-b border-blue-300 dark:border-blue-600 pb-2">Prompt Examples</h2>
                     <div class="overflow-x-auto flex-grow scrollbar">
                         <div class="flex flex-nowrap gap-4 p-2">
                             <div v-for="(prompt, index) in personality.prompts_list"
                                  :title="extractTitle(prompt)"
                                  :key="index"
                                  @click="handlePromptSelection(prompt)"
                                  class="flex-shrink-0 w-[300px] card hover:shadow-xl transition-all duration-300 ease-in-out transform hover:scale-105 flex flex-col justify-between min-h-[200px] group p-4 cursor-pointer">
                                  <div class="space-y-2">
                                      <h3 class="font-semibold text-lg text-blue-800 dark:text-blue-100 mb-1 truncate" :title="extractTitle(prompt)">
                                        {{ extractTitle(prompt) || 'Prompt Example' }}
                                      </h3>
                                      <div :title="prompt" class="text-sm text-blue-700 dark:text-blue-300 overflow-hidden line-clamp-4 leading-relaxed">
                                        {{ getPromptContent(prompt) }}
                                      </div>
                                  </div>
                                  <div class="mt-3 text-xs font-medium link opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                                      Click to select
                                  </div>
                             </div>
                         </div>
                     </div>

                    <!-- Placeholder Modal -->
                     <div v-if="showPlaceholderModal" class="fixed inset-0 bg-black bg-opacity-60 dark:bg-opacity-70 flex items-center justify-center z-50 p-4">
                         <div class="card max-w-4xl w-full max-h-[90vh] flex flex-col p-0">
                             <h3 class="text-lg font-semibold p-4 border-b border-blue-200 dark:border-blue-700 text-blue-800 dark:text-blue-100">Fill in the placeholders</h3>
                             <div class="flex-1 flex flex-col min-h-0 overflow-hidden p-4 space-y-4">
                                 <div class="p-3 bg-blue-100 dark:bg-blue-800 rounded-lg border border-blue-200 dark:border-blue-700">
                                     <h4 class="label !mb-1">Live Preview:</h4>
                                     <div class="flex-1 h-[150px] overflow-y-auto scrollbar bg-white dark:bg-blue-900 p-2 rounded text-sm">
                                         <span class="whitespace-pre-wrap text-blue-900 dark:text-blue-100">{{ getPromptContent(previewPrompt) }}</span>
                                     </div>
                                 </div>
                                 <div class="flex-1 overflow-y-auto scrollbar space-y-3 pr-2">
                                     <div v-for="(placeholder, index) in parsedPlaceholders" :key="placeholder.fullText" class="flex flex-col">
                                         <label :for="'placeholder-'+index" class="label">{{ placeholder.label }}</label>
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
                 </div>

                 <WelcomeComponent v-if="!hasActiveDiscussion" />

                <div class="h-40"></div>
            </div>

            <div class="sticky bottom-0 left-0 right-0 h-48 pointer-events-none bg-gradient-to-t from-blue-100 to-transparent dark:from-blue-900 z-10"></div>
        </div>

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
import feather from 'feather-icons';

const parsePlaceholder = (placeholder) => {
    const parts = placeholder.replace(/^\[|\]$/g, '').split('::'); // Use regex for cleaner removal
    const label = parts[0];

    if (parts.length === 1) return { label, type: 'text', fullText: placeholder };

    const type = parts[1].toLowerCase(); // Normalize type
    const result = { label, type, fullText: placeholder };

    switch (type) {
        case 'int':
        case 'float':
        case 'multiline': break; // No extra params needed
        case 'code':
            result.language = parts[2] || 'plaintext'; break;
        case 'options':
            result.options = parts[2] ? parts[2].split(',').map(o => o.trim()) : []; break;
        default:
            result.type = 'text'; // Fallback to text
    }
    return result;
};


export default {
    name: 'ChatArea',
    components: { Message, ChatBox, WelcomeComponent },
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
            selectedPrompt: '',
            placeholders: [],
            placeholderValues: {},
            previewPrompt: '',
        };
    },
    computed: {
        ...mapState(['config']),
        personality() {
            if (!this.config || !this.config.personalities || this.config.active_personality_id < 0 || this.config.active_personality_id >= this.config.personalities.length) {
                return null;
            }
            const activePersPath = this.config.personalities[this.config.active_personality_id];
            const basePath = activePersPath?.split(':')[0];
            // Assuming personalities array is available in the parent or Vuex, passed as a prop or accessed directly if needed
            // For now, just returning a placeholder object structure if needed, otherwise rely on parent logic
            // This might need adjustment based on where the full personality details are stored/accessed
             const fullPersonality = this.$store.state.personalities.find(p => p.full_path === basePath);
             return fullPersonality || null; // Return the found personality or null
        },
         parsedPlaceholders() {
            const uniqueMap = new Map();
            this.placeholders.forEach(p => {
                const parsed = parsePlaceholder(p);
                uniqueMap.set(parsed.fullText, parsed);
            });
            return Array.from(uniqueMap.values());
        }
    },
    methods: {
        getAvatar(sender) {
            if (!this.config || !sender) return null;
            const senderLower = sender.toLowerCase().trim();
            const userLower = this.config.user_name?.toLowerCase().trim();

            if (senderLower === userLower) {
                return this.config.user_avatar ? `user_infos/${this.config.user_avatar}` : null; // Handle missing user avatar
            }

            const personality = this.personalityAvatars.find(p => p.name?.toLowerCase().trim() === senderLower);
            return personality?.avatar ? `/${personality.avatar}` : null; // Prepend '/' for web path
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
         extractTitle(prompt) {
            const titleMatch = prompt.match(/@<(.*?)>@/);
            return titleMatch ? titleMatch[1] : null;
        },
        getPromptContent(prompt) {
            return prompt.replace(/@<.*?>@/, '').trim();
        },
        handlePromptSelection(prompt) {
            this.selectedPrompt = prompt;
            this.previewPrompt = this.getPromptContent(prompt); // Use content for preview initially
            this.placeholders = this.extractPlaceholders(prompt);

            if (this.placeholders.length > 0) {
                this.placeholderValues = {}; // Reset values
                this.parsedPlaceholders.forEach((ph, index) => {
                    // Pre-fill with default values if any are defined in the placeholder syntax (future enhancement)
                    this.placeholderValues[index] = ''; // Initialize as empty
                });
                this.showPlaceholderModal = true;
                this.updatePreview(); // Initial preview update
            } else {
                this.setPromptInChatbox(this.getPromptContent(prompt));
            }
        },
        extractPlaceholders(prompt) {
            const placeholderRegex = /\[(.*?)\]/g;
            // Avoid duplicates if the same placeholder appears multiple times
            const uniquePlaceholders = new Set([...prompt.matchAll(placeholderRegex)].map(match => match[0]));
            return Array.from(uniquePlaceholders);
        },
        updatePreview() {
            let preview = this.selectedPrompt;
            this.parsedPlaceholders.forEach((placeholder, index) => {
                const value = this.placeholderValues[index];
                // Replace all occurrences of the same placeholder using RegExp
                const regex = new RegExp(this.escapeRegExp(placeholder.fullText), 'g');
                // Use the original full placeholder text if the value is empty, otherwise use the value
                preview = preview.replace(regex, value || placeholder.fullText);
            });
            this.previewPrompt = preview; // Update the preview reactive property
        },
        escapeRegExp(string) {
             return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); // $& means the whole matched string
        },
        cancelPlaceholders() {
            this.showPlaceholderModal = false;
            // Resetting state is handled in handlePromptSelection if re-opened
        },
        applyPlaceholders() {
            let finalPrompt = this.selectedPrompt;
            this.parsedPlaceholders.forEach((placeholder, index) => {
                const value = this.placeholderValues[index];
                if (value !== undefined && value !== '') { // Apply only if a value is provided
                     const regex = new RegExp(this.escapeRegExp(placeholder.fullText), 'g');
                     finalPrompt = finalPrompt.replace(regex, value);
                }
            });
            this.showPlaceholderModal = false;
            this.setPromptInChatbox(this.getPromptContent(finalPrompt)); // Use the final processed prompt content
        },
        setPromptInChatbox(prompt) {
             if (this.$refs.chatBox) {
                 this.$refs.chatBox.message = prompt;
                 // Optionally focus the input
                 this.$refs.chatBox.focusInput();
             }
        },
    },
    watch: {
        discussionArr: {
            handler() {
                this.scrollToBottom();
                 this.$nextTick(() => feather.replace());
            },
            deep: true
        },
         personality: {
            handler(newVal, oldVal) {
                // Reset prompt example state if personality changes
                if (newVal?.full_path !== oldVal?.full_path) {
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
        this.scrollToBottom();
         nextTick(() => {
            feather.replace();
         });
    },
    updated() {
         nextTick(() => {
            feather.replace();
         });
    }
};
</script>

<style scoped>

</style>
