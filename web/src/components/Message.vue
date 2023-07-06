<template>
    <div
        class="relative group rounded-lg m-2 shadow-lg hover:border-primary dark:hover:border-primary hover:border-solid hover:border-2 border-2 border-transparent even:bg-bg-light-discussion-odd dark:even:bg-bg-dark-discussion-odd flex flex-col flex-grow flex-wrap overflow-visible p-4 pb-2 ">
        <div class="flex flex-row  gap-2 ">
            <div class=" flex-shrink-0">
                <!-- AVATAR -->
                <div class="group/avatar " >
                    <img :src="getImgUrl()" @error="defaultImg($event)" :data-popover-target="'avatar' + message.id" data-popover-placement="bottom"
                        class="w-10 h-10 rounded-full object-fill text-red-700">
                        
                        <!-- ADDITIONAL INFO -->
                    <!-- <div data-popper :id="'avatar' + message.id"   role="tooltip"
                        class=" -mx-2 absolute invisible rounded-lg bg-bg-light-tone-panel dark:bg-bg-dark-tone-panel block  m-2 p-1 opacity-0 z-10  transition-opacity ease-in-out  duration-500 group-hover/avatar:visible group-hover/avatar:opacity-100 ">
                        
                        <div class="relative flex flex-row items-start">
                            
                            <img :src="getImgUrl()" @error="defaultImg($event)" class=" border-2 border-primary p-1 rounded-lg w-60 h-60" />

                            <div class="flex flex-col justify-between p-4 leading-normal">
                                <h5 class="mb-2 text-2xl font-bold tracking-tight text-gray-900 dark:text-white">Noteworthy
                                    technology acquisitions 2021</h5>
                                <p class="mb-3 font-normal text-gray-700 dark:text-gray-400">Here are the biggest enterprise
                                    technology acquisitions of 2021 so far, in reverse chronological order.</p>
                            </div>
                            
                        </div>
                     
                    </div> -->
                    
                    
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
                            <div v-if="!editMsgMode" class="text-lg hover:text-secondary duration-75 active:scale-90 p-2"
                                title="Edit message" @click.stop="editMsgMode = true">
                                <i data-feather="edit"></i>
                            </div>
                            <div class="text-lg hover:text-secondary duration-75 active:scale-90 p-2"
                                title="Copy message to clipboard" @click.stop="copyContentToClipboard()">
                                <i data-feather="copy"></i>
                            </div>
                            <div class="text-lg hover:text-secondary duration-75 active:scale-90 p-2" title="Resend message"
                                @click.stop="resendMessage()">
                                <i data-feather="refresh-cw"></i>
                            </div>
                            <!-- DELETE CONFIRMATION -->
                            <div v-if="deleteMsgMode" class="flex items-center duration-75">
                                <button class="text-2xl hover:text-red-600 duration-75 active:scale-90 p-2"
                                    title="Cancel removal" type="button" @click.stop="deleteMsgMode = false">
                                    <i data-feather="x"></i>
                                </button>
                                <button class="text-2xl hover:text-secondary duration-75 active:scale-90 p-2"
                                    title="Confirm removal" type="button" @click.stop="deleteMsg()">
                                    <i data-feather="check"></i>
                                </button>

                            </div>
                            <div v-if="!deleteMsgMode" class="text-lg hover:text-red-600 duration-75 active:scale-90 p-2"
                                title="Remove message" @click="deleteMsgMode = true">
                                <i data-feather="trash"></i>
                            </div>
                            <div class="text-lg hover:text-secondary duration-75 active:scale-90 p-2" title="Upvote"
                                @click.stop="rankUp()">
                                <i data-feather="thumbs-up"></i>
                            </div>
                            <div class="flex flex-row items-center">
                                <div class="text-lg hover:text-red-600 duration-75 active:scale-90 p-2" title="Downvote"
                                    @click.stop="rankDown()">
                                    <i data-feather="thumbs-down"></i>
                                </div>
                                <div v-if="message.rank != 0"
                                    class="rounded-full px-2 text-sm flex items-center justify-center font-bold"
                                    :class="message.rank > 0 ? 'bg-secondary' : 'bg-red-600'" title="Rank">{{
                                        message.rank }}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="overflow-x-auto w-full ">
                    <!-- MESSAGE CONTENT -->
                    <div class="flex flex-col items-start w-full">
                        <div v-for="(step, index) in message.steps" :key="'step-' + message.id + '-' + index" class="step font-bold" :style="{ backgroundColor: step.done ? 'transparent' : 'inherit' }">
                            <Step :done="step.done" :message="step.message" />
                        </div>
                    </div>


                    <MarkdownRenderer ref="mdRender" v-if="!editMsgMode" :markdown-text="message.content">
                    </MarkdownRenderer>
                    <textarea v-if="editMsgMode" ref="mdTextarea" :rows="4"
                        class="block p-2.5 w-full text-sm text-gray-900 bg-gray-50 rounded-lg border border-gray-300 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
                        :style="{ minHeight: mdRenderHeight + `px` }" placeholder="Enter message here..."
                        v-model="new_message_content"></textarea>
                </div>
                <!-- FOOTER -->
                <div class="text-sm text-gray-400 mt-2">
                    <div class="flex flex-row items-center gap-2">
                        <p v-if="message.binding">Binding: <span class="font-thin">{{ message.binding }}</span></p>
                        <p v-if="message.model">Model: <span class="font-thin">{{ message.model }}</span></p>
                        <p v-if="message.seed">Seed: <span class="font-thin">{{ message.seed }}</span></p>
                        <p v-if="time_spent">Time spent: <span class="font-thin"
                                :title="'Finished generating: ' + finished_generating_at_parsed">{{ time_spent }}</span></p>
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
</style>
<script>
import botImgPlaceholder from "../assets/logo.svg"
import userImgPlaceholder from "../assets/default_user.svg"
const bUrl = import.meta.env.VITE_GPT4ALL_API_BASEURL
import { nextTick } from 'vue'
import feather from 'feather-icons'
import MarkdownRenderer from './MarkdownRenderer.vue';
import Step from './Step.vue';
export default {
    // eslint-disable-next-line vue/multi-word-component-names
    name: 'Message',
    emits: ['copy', 'delete', 'rankUp', 'rankDown', 'updateMessage', 'resendMessage'],
    components: {
        MarkdownRenderer,
        Step
    },
    props: {
        message: Object,
        avatar: ''
    },
    data() {
        return {
            expanded: false,
            new_message_content: '',
            showConfirmation: false,
            editMsgMode: false,
            deleteMsgMode: false,
            mdRenderHeight: Number

        }
    }, mounted() {
        console.log("Mounted message")
        console.log(this.message)
        this.new_message_content = this.message.content
        nextTick(() => {
            feather.replace()

            this.mdRenderHeight = this.$refs.mdRender.$el.offsetHeight


        })

    }, methods: {
        toggleModel() {
            this.expanded = !this.expanded;
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
            this.$emit('updateMessage', this.message.id, this.new_message_content)
            this.editMsgMode = false
        },
        resendMessage() {
            this.$emit('resendMessage', this.message.id, this.new_message_content)
        },
        getImgUrl() {

            if (this.message.sender == "user") {
                if (this.avatar) {

                    return this.avatar
                }

                return userImgPlaceholder;

            }
            if (this.avatar) {
                return bUrl + this.avatar
            }
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
        }


    }, watch: {
        showConfirmation() {
            nextTick(() => {
                feather.replace()

            })
        },

        editMsgMode(val) {

            if (!val) {
                this.new_message_content = this.message.content
            }

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
            const startTime = new Date(Date.parse(this.message.created_at))
            const endTime = new Date(Date.parse(this.message.finished_generating_at))
            //const spentTime = new Date(endTime - startTime)
            const same = endTime.getTime() === startTime.getTime();
            if (same) {

                return undefined
            }

            if (!endTime.getTime()) {
                return undefined
            }
            let timeDiff = endTime.getTime() - startTime.getTime();


            const hours = Math.floor(timeDiff / (1000 * 60 * 60));

            timeDiff -= hours * (1000 * 60 * 60);



            const mins = Math.floor(timeDiff / (1000 * 60));

            timeDiff -= mins * (1000 * 60);

            const secs = Math.floor(timeDiff / 1000)
            timeDiff -= secs * 1000;



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


        }
    }


}
</script>