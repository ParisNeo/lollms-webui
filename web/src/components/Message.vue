<template>
    <div
        class="group rounded-lg m-2 shadow-lg hover:border-primary dark:hover:border-primary hover:border-solid hover:border-2 border-2 border-transparent even:bg-bg-light-discussion-odd dark:even:bg-bg-dark-discussion-odd flex-row p-4 pb-2">
        <div class="w-30 flex">
            <!-- SENDER -->
            <div class="w-10 h-10 rounded-lg object-fill drop-shadow-md">

                <img :src="getImgUrl()" class="w-10 h-10 rounded-full object-fill text-red-700">


            </div>
            <p class="drop-shadow-sm   py-0 px-2 text-lg text-opacity-95 font-bold ">{{ message.sender }}</p>
        </div>
        <div class="-mt-4  ml-10 mr-0 pt-1 px-2 ">
            <!-- CONTENT/MESSAGE -->
            <markdown-renderer v-if="!editMsgMode" :markdown-text="message.content"></markdown-renderer>
            <textarea v-if="editMsgMode" rows="4"
                class="block p-2.5 w-full text-sm text-gray-900 bg-gray-50 rounded-lg border border-gray-300 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
                placeholder="Enter message here..." v-model="new_message_content"></textarea>
        </div>
        <div class="invisible group-hover:visible flex flex-row mt-3 -mb-2">
            <!-- MESSAGE CONTROLS -->
            <!-- EDIT CONFIRMATION -->
            <div v-if="editMsgMode" class="flex items-center duration-75">
                <button class="text-2xl hover:text-red-600 duration-75 active:scale-90 p-2" title="Cancel edit" type="button"
                    @click.stop="editMsgMode = false">
                    <i data-feather="x"></i>
                </button>
                <button class="text-2xl hover:text-secondary duration-75 active:scale-90 p-2" title="Update message"
                    type="button" @click.stop="updateMessage">
                    <i data-feather="check"></i>
                </button>

            </div>
            <div v-if="!editMsgMode" class="text-lg hover:text-secondary duration-75 active:scale-90 p-2" title="Edit message"
                @click.stop="editMsgMode =true">
                <i data-feather="edit"></i>
            </div>
            <div class="text-lg hover:text-secondary duration-75 active:scale-90 p-2" title="Copy message to clipboard"
                @click.stop="copyContentToClipboard()">
                <i data-feather="copy"></i>
            </div>
            <div class="text-lg hover:text-secondary duration-75 active:scale-90 p-2" title="Resend message" @click.stop="resendMessage()">
                <i data-feather="refresh-cw"></i>
            </div>
            <!-- DELETE CONFIRMATION -->
            <div v-if="deleteMsgMode" class="flex items-center duration-75">
                <button class="text-2xl hover:text-red-600 duration-75 active:scale-90 p-2" title="Cancel removal" type="button"
                    @click.stop="deleteMsgMode = false">
                    <i data-feather="x"></i>
                </button>
                <button class="text-2xl hover:text-secondary duration-75 active:scale-90 p-2" title="Confirm removal"
                    type="button" @click.stop="deleteMsg()">
                    <i data-feather="check"></i>
                </button>

            </div>
            <div v-if="!deleteMsgMode" class="text-lg hover:text-red-600 duration-75 active:scale-90 p-2"
                title="Remove message" @click="deleteMsgMode = true">
                <i data-feather="trash"></i>
            </div>
            <div class="text-lg hover:text-secondary duration-75 active:scale-90 p-2" title="Upvote" @click.stop="rankUp()">
                <i data-feather="thumbs-up"></i>
            </div>
            <div class="flex flex-row items-center">
                <div class="text-lg hover:text-red-600 duration-75 active:scale-90 p-2" title="Downvote"
                    @click.stop="rankDown()">
                    <i data-feather="thumbs-down"></i>
                </div>
                <div v-if="message.rank != 0" class="rounded-full px-2 text-sm flex items-center justify-center font-bold"
                    :class="message.rank > 0 ? 'bg-secondary' : 'bg-red-600'" title="Rank">{{ message.rank }}
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import botImgPlaceholder from "../assets/logo.svg"
import userImgPlaceholder from "../assets/default_user.svg"
import { nextTick } from 'vue'
import feather from 'feather-icons'
import MarkdownRenderer from './MarkdownRenderer.vue';
export default {
    name: 'Message',
    emits: ['copy', 'delete', 'rankUp', 'rankDown','updateMessage','resendMessage'],
    components: {
        MarkdownRenderer
    },
    props: {
        message: Object
    },
    data() {
        return {

            senderImg: '',
            new_message_content: '',
            showConfirmation: false,
            editMsgMode: false,
            deleteMsgMode: false,

        }
    }, mounted() {
        this.senderImg = botImgPlaceholder
        this.new_message_content = this.message.content
        nextTick(() => {
            feather.replace()

        })
    }, methods: {
        copyContentToClipboard() {
            this.$emit('copy', this.message.content)
            navigator.clipboard.writeText(this.message.content);
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
            this.$emit('updateMessage', this.message.id, this.new_message_content)
            this.editMsgMode = false
        },
        resendMessage(){
            this.$emit('resendMessage', this.message.id, this.new_message_content)
        },
        getImgUrl() {

            if (this.message.sender == "user") {
                return userImgPlaceholder;

            }

            return botImgPlaceholder;
        }

    }, watch: {
        showConfirmation() {
            nextTick(() => {
                feather.replace()

            })
        },
        content(val) {
            this.new_message_content = this.message.content
        
        },
        editMsgMode(val){
            if(!val){
                this.new_message_content = this.message.content 
            }
            nextTick(() => {
                feather.replace()

            })
        },
        deleteMsgMode(){
            nextTick(() => {
                feather.replace()

            })
        },
    },
    computed: {
        content() {
            return this.message.content
        }
    }

}
</script>