<template>
    <div
        class="overflow-y-scroll flex flex-col no-scrollbar shadow-lg min-w-[24rem] max-w-[24rem] bg-bg-light-tone dark:bg-bg-dark-tone ">
        <!-- LEFT SIDE PANEL -->
        <div
            class="z-10 sticky top-0 flex-row p-2 flex items-center gap-3 flex-0 bg-bg-light-tone dark:bg-bg-dark-tone mt-0 px-4  shadow-md">
            <!-- CONTROL PANEL -->
            <button class=" text-2xl  hover:text-secondary duration-75 active:scale-90 " title="Create new discussion"
                type="button" @click="createNewDiscussion()">
                <i data-feather="plus"></i>
            </button>
            <button class=" text-2xl  hover:text-secondary duration-75 active:scale-90 "
                title="Reset database, remove all discussions">
                <i data-feather="refresh-ccw"></i>
            </button>
            <button class=" text-2xl  hover:text-secondary duration-75 active:scale-90 " title="Export database"
                type="button">
                <i data-feather="database"></i>
            </button>
            <button class=" text-2xl  hover:text-secondary duration-75 active:scale-90 rotate-90"
                title="Export discussion to a file" type="button">
                <i data-feather="log-out"></i>
            </button>

            <!-- SEARCH BAR -->
            <form>
                <div class="relative">
                    <div class="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
                        <div class="scale-75 ">
                            <i data-feather="search"></i>
                        </div>
                    </div>
                    <div class="absolute inset-y-0 right-0 flex items-center pr-3 ">
                        <div class=" hover:text-secondary duration-75 active:scale-90 "
                            :class="filterTitle ? 'visible' : 'invisible'" title="Clear" @click="filterTitle = ''">
                            <i data-feather="x"></i>
                        </div>
                    </div>

                    <input type="search" id="default-search"
                        class="block w-full p-2 pl-10 pr-10 text-sm border border-gray-300 rounded-lg bg-bg-light focus:ring-secondary focus:border-secondary  dark:bg-bg-dark dark:border-gray-600 dark:placeholder-gray-400 dark:focus:ring-secondary dark:focus:border-secondary "
                        placeholder="Search..." title="Filter discussions by title" v-model="filterTitle"
                        @input="filterDiscussions()">
                </div>
            </form>

        </div>
        <div id="dis-list" class="relative overflow-y-scroll no-scrollbar">
            <!-- DISCUSSION LIST -->
            <div class="mx-4 flex-grow" :class="filterInProgress ? 'opacity-20 pointer-events-none' : ''">

                <Discussion v-for="(item, index) in list" :key="index" :id="item.id" :title="item.title"
                    ref="discussionList" :selected="currentDiscussion.id == item.id"
                    :loading="currentDiscussion.id == item.id && loading" @select="selectDiscussion(item)"
                    @delete="deleteDiscussion(item.id)" @editTitle="editTitle" />

                <div v-if="list.length < 1"
                    class=" gap-2 py-2 my-2 hover:shadow-md hover:bg-primary-light dark:hover:bg-primary rounded-md p-2 duration-75 group cursor-pointer">
                    <p class="px-3">No discussions are found</p>
                </div>
                <div
                    class="sticky bottom-0  bg-gradient-to-t  pointer-events-none from-bg-light-tone dark:from-bg-dark-tone  flex height-64 ">
                    <!-- FADING DISCUSSION LIST END ELEMENT -->
                </div>
            </div>

        </div>

    </div>
    <div id="msg-list" class="overflow-y-scroll flex flex-col no-scrollbar flex-grow "
        :class="loading ? 'opacity-20 pointer-events-none' : ''">
        <!-- CHAT AREA -->
        <div>
            <Message v-for="(msg, index) in discussionArr" :key="index" :message="msg"
                @click="scrollToElement($event.target)" :id="'msg-' + msg.id" />

            <WelcomeComponent v-if="discussionArr.length < 1" />

            <ChatBox v-if="discussionArr.length > 0" @messageSentEvent="sendMsg" />

        </div>


    </div>
</template>
<style scoped>
.height-64 {
    min-height: 64px;
}
</style>

<script>

export default {

    setup() {


    },
    data() {

        return {
            list: [], // Discussion list
            tempList: [], // Copy of Discussion list (used for keeping the original list during filtering discussions/searching action)
            currentDiscussion: {}, // Current/selected discussion id
            discussionArr: [],
            loading: false,
            filterTitle: "",
            filterInProgress: false,
        }
    },
    methods: {
        async list_discussions() {
            try {
                const res = await axios.get("/list_discussions");

                if (res) {
                    this.list = res.data
                    this.tempList = this.list
                    return res.data

                }
            } catch (error) {
                console.log(error)
                return []
            }

        },
        async load_discussion(id) {
            try {
                if (id) {
                    this.loading = true
                    const res = await axios.post("/load_discussion", {
                        id: id
                    });
                    this.loading = false
                    if (res) {

                        // Filter out the user and bot entries
                        this.discussionArr = res.data.filter((item) => item.type == 0)
                        const lastMessage = this.discussionArr[this.discussionArr.length - 1]
                        if (lastMessage) {
                            nextTick(() => {
                                const selectedElement = document.getElementById('msg-' + lastMessage.id)
                                this.scrollToElement(selectedElement)

                            })
                        }

                    }
                }

            } catch (error) {
                console.log(error)
                this.loading = false
            }

        },
        async new_discussion(title) {
            try {
                const res = await axios.get("/new_discussion", { params: { title: title } });

                if (res) {
                    return res.data

                }
            } catch (error) {
                console.log(error)
                return {}
            }
        },
        async delete_discussion(id) {
            try {
                if (id) {
                    this.loading = true
                    const res = await axios.post("/delete_discussion", {
                        id: id
                    });
                    this.loading = false
                }

            } catch (error) {
                console.log(error)
                this.loading = false
            }

        },
        async edit_title(discussion_id, new_title) {
            try {
                if (discussion_id) {
                    this.loading = true
                    const res = await axios.post("/edit_title", {
                        id: discussion_id,
                        title: new_title
                    });
                    this.loading = false
                    if (res.status == 200) {
                        const index = this.list.findIndex(x => x.id == discussion_id);
                        const discussionItem = this.list[index]
                        discussionItem.title = new_title
                        this.tempList = this.list
                    }
                }

            } catch (error) {
                console.log(error)
                this.loading = false
            }

        },
        filterDiscussions() {

            // Search bar in for filtering discussions by title (serch)

            if (!this.filterInProgress) {
                this.filterInProgress = true
                setTimeout(() => {

                    this.list = this.tempList.filter((item) => item.title.includes(this.filterTitle))
                    this.filterInProgress = false

                }, 100)
            }
        },
        async selectDiscussion(item) {

            // When discussion is selected it loads the discussion array

            this.currentDiscussion = item

            localStorage.setItem("selected_discussion", this.currentDiscussion.id)

            await this.load_discussion(item.id)

            if (this.discussionArr.length > 1) {

                if (this.currentDiscussion.title === "" || this.currentDiscussion.title === null) {
                    this.changeTitleUsingUserMSG(this.currentDiscussion.id, this.discussionArr[1].content)
                }
            }
            nextTick(() => {
                const selectedDisElement = document.getElementById('dis-' + item.id)
                this.scrollToElement(selectedDisElement)

            })

        },
        scrollToElement(el) {

            if (el) {

                el.scrollIntoView({ behavior: 'smooth', block: "center", inline: "nearest" });
            }
        },
        createMsg(msgObj) {
            // From websocket.on("infos")

            // Create user input message
            let usrMessage = {
                content: msgObj.message,
                id: msgObj.message,
                //parent: 10,
                rank: 0,
                sender: msgObj.user,
                //type: 0
            }
            this.discussionArr.push(usrMessage)
            nextTick(() => {
                const userMsgElement = document.getElementById('msg-' + msgObj.message)
                this.scrollToElement(userMsgElement)

            })

            // Create response message
            let responseMessage = {
                content: "..typing",
                id: msgObj.response_id,
                //parent: 10,
                rank: 0,
                sender: msgObj.bot,
                //type: 0
            }
            this.discussionArr.push(responseMessage)
            nextTick(() => {
                const responseMessageElement = document.getElementById('msg-' + msgObj.response_id)
                this.scrollToElement(responseMessageElement)
            })

            if (this.currentDiscussion.title === "" || this.currentDiscussion.title === null) {
                this.changeTitleUsingUserMSG(this.currentDiscussion.id, usrMessage.content)
            }

        },
        sendMsg(msg) {

            // Sends message to backend

            websocket.emit('generate_msg', { prompt: msg });

        },
        steamMessageContent(content) {

            // Streams response message content from backend

            const lastMsg = this.discussionArr[this.discussionArr.length - 1]
            lastMsg.content = content.data
        },
        async changeTitleUsingUserMSG(id, msg) {

            // If discussion is untitled or title is null then it sets the title to first user message.

            const index = this.list.findIndex(x => x.id == id);
            const discussionItem = this.list[index]
            if (msg) {
                discussionItem.title = msg
                this.tempList = this.list
            }
            await this.edit_title(id, msg)

        },
        async createNewDiscussion() {

            // Creates new discussion on backend, 
            // gets new discussion list, selects 
            // newly created discussion, 
            // scrolls to the discussion

            const res = await this.new_discussion()
            await this.list_discussions()
            const index = this.list.findIndex(x => x.id == res.id);
            const discussionItem = this.list[index]
            this.selectDiscussion(discussionItem)
            nextTick(() => {
                const selectedDisElement = document.getElementById('dis-' + res.id)
                this.scrollToElement(selectedDisElement)

            })

        },
        loadLastUsedDiscussion() {
            // Checks local storage for last selected discussion
            const id = localStorage.getItem("selected_discussion")
            if (id) {
                const index = this.list.findIndex(x => x.id == id);
                const discussionItem = this.list[index]
                this.selectDiscussion(discussionItem)

            }

        },
        async deleteDiscussion(id) {

            // Deletes discussion from backend and frontend

            const index = this.list.findIndex(x => x.id == id);
            const discussionItem = this.list[index]
            discussionItem.loading = true
            this.delete_discussion(id)
            if (this.currentDiscussion.id == id) {
                this.currentDiscussion = {}
            }
            await this.list_discussions()
        },
        async editTitle(newTitleObj) {
            //const index = this.$refs.discussionList.findIndex(x => x.id == newTitleObj.id);
            //const discussionItem = this.$refs.discussionList[index]
            //console.log(JSON.stringify(discussionItem))
            //discussionItem.loading.value=true
            //console.log(discussionItem.title)
            await this.edit_title(newTitleObj.id, newTitleObj.title)

        },


    },
    async created() {

        // Constructor

        await this.list_discussions()

        this.loadLastUsedDiscussion()

        nextTick(() => {
            feather.replace()
        })

        // WebSocket responses
        websocket.on("infos", this.createMsg)
        websocket.on("message", this.steamMessageContent)

    }, components: {
        Discussion,
        Message,
        ChatBox,
        WelcomeComponent,

    }, watch: {
        filterTitle(newVal, oldVal) {
            if (newVal == "") {
                this.filterInProgress = true
                this.list = this.tempList
                this.filterInProgress = false
            }
        }
    }

}
</script>

<script setup >
import Discussion from '../components/Discussion.vue';
import Message from '../components/Message.vue';
import ChatBox from '../components/ChatBox.vue'
import WelcomeComponent from '../components/WelcomeComponent.vue'

import feather from 'feather-icons'

import axios from "axios";
import { nextTick } from 'vue';

import websocket from '@/services/websocket.js';

import { onMounted } from 'vue'
import { initFlowbite } from 'flowbite'

// initialize components based on data attribute selectors
onMounted(() => {
    initFlowbite();
})

axios.defaults.baseURL = import.meta.env.VITE_GPT4ALL_API_BASEURL;

</script>