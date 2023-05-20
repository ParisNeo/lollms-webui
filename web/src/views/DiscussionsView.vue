<template>
    <div
        class="overflow-y-scroll flex flex-col no-scrollbar shadow-lg min-w-[24rem] max-w-[24rem] bg-bg-light-tone dark:bg-bg-dark-tone">
        <!-- LEFT SIDE PANEL -->
        <div class="z-10 sticky top-0 flex-col  bg-bg-light-tone dark:bg-bg-dark-tone shadow-md">


            <!-- CONTROL PANEL -->
            <div class="flex-row p-4  flex items-center gap-3 flex-0">

                <!-- MAIN BUTTONS -->
                <button class="text-2xl hover:text-secondary duration-75 active:scale-90" title="Create new discussion"
                    type="button" @click="createNewDiscussion()">
                    <i data-feather="plus"></i>
                </button>
                <button class="text-2xl hover:text-secondary duration-75 active:scale-90" title="Edit discussion list"
                    type="button" @click="isCheckbox = !isCheckbox" :class="isCheckbox ? 'text-secondary' : ''">
                    <i data-feather="check-square"></i>
                </button>
                <button class="text-2xl hover:text-secondary duration-75 active:scale-90"
                    title="Reset database, remove all discussions">
                    <i data-feather="refresh-ccw"></i>
                </button>
                <button class="text-2xl hover:text-secondary duration-75 active:scale-90" title="Export database"
                    type="button">
                    <i data-feather="database"></i>
                </button>
                <button class="text-2xl hover:text-secondary duration-75 active:scale-90 rotate-90"
                    title="Import discussions" type="button" @click.stop="">
                    <i data-feather="log-in"></i>
                </button>
                <button class="text-2xl hover:text-secondary duration-75 active:scale-90" title="Filter discussions"
                    type="button" @click="isSearch = !isSearch" :class="isSearch ? 'text-secondary' : ''">
                    <i data-feather="search"></i>
                </button>
                <div v-if="loading" title="Loading.." class="flex flex-row flex-grow justify-end">
                    <!-- SPINNER -->
                    <div role="status">
                        <svg aria-hidden="true" class="w-6 h-6   animate-spin  fill-secondary" viewBox="0 0 100 101"
                            fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path
                                d="M100 50.5908C100 78.2051 77.6142 100.591 50 100.591C22.3858 100.591 0 78.2051 0 50.5908C0 22.9766 22.3858 0.59082 50 0.59082C77.6142 0.59082 100 22.9766 100 50.5908ZM9.08144 50.5908C9.08144 73.1895 27.4013 91.5094 50 91.5094C72.5987 91.5094 90.9186 73.1895 90.9186 50.5908C90.9186 27.9921 72.5987 9.67226 50 9.67226C27.4013 9.67226 9.08144 27.9921 9.08144 50.5908Z"
                                fill="currentColor" />
                            <path
                                d="M93.9676 39.0409C96.393 38.4038 97.8624 35.9116 97.0079 33.5539C95.2932 28.8227 92.871 24.3692 89.8167 20.348C85.8452 15.1192 80.8826 10.7238 75.2124 7.41289C69.5422 4.10194 63.2754 1.94025 56.7698 1.05124C51.7666 0.367541 46.6976 0.446843 41.7345 1.27873C39.2613 1.69328 37.813 4.19778 38.4501 6.62326C39.0873 9.04874 41.5694 10.4717 44.0505 10.1071C47.8511 9.54855 51.7191 9.52689 55.5402 10.0491C60.8642 10.7766 65.9928 12.5457 70.6331 15.2552C75.2735 17.9648 79.3347 21.5619 82.5849 25.841C84.9175 28.9121 86.7997 32.2913 88.1811 35.8758C89.083 38.2158 91.5421 39.6781 93.9676 39.0409Z"
                                fill="currentFill" />
                        </svg>
                        <span class="sr-only">Loading...</span>
                    </div>
                </div>
            </div>
            <!-- SEARCH BAR -->
            <div class="flex-row  items-center gap-3 flex-0 w-full">
                <div v-if="isSearch" class="p-4 pt-2">
                    <div class="relative">
                        <div class="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
                            <div class="scale-75">
                                <i data-feather="search"></i>
                            </div>
                        </div>
                        <div class="absolute inset-y-0 right-0 flex items-center pr-3">
                            <div class="hover:text-secondary duration-75 active:scale-90"
                                :class="filterTitle ? 'visible' : 'invisible'" title="Clear" @click="filterTitle = ''">
                                <i data-feather="x"></i>
                            </div>
                        </div>

                        <input type="search" id="default-search"
                            class="block w-full p-2 pl-10 pr-10 text-sm border border-gray-300 rounded-lg bg-bg-light focus:ring-secondary focus:border-secondary dark:bg-bg-dark dark:border-gray-600 dark:placeholder-gray-400 dark:focus:ring-secondary dark:focus:border-secondary"
                            placeholder="Search..." title="Filter discussions by title" v-model="filterTitle"
                            @input="filterDiscussions()" />
                    </div>
                </div>
            </div>
            <hr v-if="isCheckbox" class="h-px bg-bg-light p-0 mb-4 px-4 mx-4 border-0 dark:bg-bg-dark">
            <div v-if="isCheckbox" class="flex flex-row flex-grow p-4 pt-0 items-center">

                <!-- CHECK BOX OPERATIONS -->
                <div class="flex flex-row flex-grow ">
                    <p v-if="selectedDiscussions.length > 0">Selected: {{ selectedDiscussions.length }}</p>
                </div>
                <div class="flex flex-row ">

                    <div v-if="selectedDiscussions.length > 0" class="flex gap-3">
                        <!-- DELETE MULTIPLE -->
                        <button v-if="!showConfirmation"
                            class="flex mx-3 flex-1 text-2xl hover:text-red-600 duration-75 active:scale-90 "
                            title="Remove selected" type="button" @click.stop="showConfirmation = true">
                            <i data-feather="trash"></i>
                        </button>
                        <!-- DELETE CONFIRM -->
                        <div v-if="showConfirmation"
                            class="flex gap-3 mx-3 flex-1 items-center justify-end  group-hover:visible duration-75">
                            <button class="text-2xl hover:text-secondary duration-75 active:scale-90"
                                title="Confirm removal" type="button" @click.stop="deleteDiscussionMulti">
                                <i data-feather="check"></i>
                            </button>
                            <button class="text-2xl hover:text-red-600 duration-75 active:scale-90 " title="Cancel removal"
                                type="button" @click.stop="showConfirmation = false">
                                <i data-feather="x"></i>
                            </button>
                        </div>
                    </div>
                    <div class="flex gap-3">

                        <button class="text-2xl hover:text-secondary duration-75 active:scale-90 rotate-90"
                            title="Export selected to a file" type="button" @click.stop="exportDiscussions">
                            <i data-feather="log-out"></i>
                        </button>
                        <button class="text-2xl hover:text-secondary duration-75 active:scale-90 " title="Select All"
                            type="button" @click.stop="selectAllDiscussions">
                            <i data-feather="list"></i>
                        </button>

                    </div>
                </div>
            </div>
        </div>
        <div class="relative overflow-y-scroll no-scrollbar">
            <!-- DISCUSSION LIST -->
            <div class="mx-4 flex-grow" :class="filterInProgress ? 'opacity-20 pointer-events-none' : ''">
                <Discussion v-for="(item, index) in list" :key="index" :id="item.id" :title="item.title"
                    :selected="currentDiscussion.id == item.id" :loading="item.loading" :isCheckbox="isCheckbox"
                    :checkBoxValue="item.checkBoxValue" @select="selectDiscussion(item)" @delete="deleteDiscussion(item.id)"
                    @editTitle="editTitle" @checked="checkUncheckDiscussion" />

                <div v-if="list.length < 1"
                    class="gap-2 py-2 my-2 hover:shadow-md hover:bg-primary-light dark:hover:bg-primary rounded-md p-2 duration-75 group cursor-pointer">
                    <p class="px-3">No discussions are found</p>
                </div>
                <div
                    class="sticky bottom-0 bg-gradient-to-t pointer-events-none from-bg-light-tone dark:from-bg-dark-tone flex height-64">
                    <!-- FADING DISCUSSION LIST END ELEMENT -->
                </div>
            </div>
        </div>
    </div>
    <div class="overflow-y-auto flex flex-col flex-grow  scrollbar-thin scrollbar-track-bg-light-tone scrollbar-thumb-bg-light-tone-panel hover:scrollbar-thumb-primary dark:scrollbar-track-bg-dark-tone dark:scrollbar-thumb-bg-dark-tone-panel dark:hover:scrollbar-thumb-primary active:scrollbar-thumb-secondary"
        id="messages-list">

        <!-- CHAT AREA -->
        <div class="container flex flex-col flex-grow pt-4 pb-10">
            <!-- REMOVED @click="scrollToElement($event.target)" -->
            <!-- Removed reference to copyToClipBoard() ; function was moved to Message.vue -->
            <Message v-for="(msg, index) in discussionArr" :key="index" :message="msg" :id="'msg-' + msg.id" ref="messages"
                @copy="copyToClipBoard" @delete="deleteMessage" @rankUp="rankUpMessage" @rankDown="rankDownMessage"
                @updateMessage="updateMessage" @resendMessage="resendMessage" />

            <WelcomeComponent v-if="!currentDiscussion.id" />


        </div>
        <div class=" sticky bottom-0">
            <ChatBox v-if="currentDiscussion.id" @messageSentEvent="sendMsg" :loading="isGenerating"
                @stopGenerating="stopGenerating" />
        </div>

    </div>
    <Toast ref="toast">
    </Toast>
</template>
<style scoped>
.height-64 {
    min-height: 64px;
}
</style>

<script>

export default {
    setup() { },
    data() {
        return {
            list: [], // Discussion list
            tempList: [], // Copy of Discussion list (used for keeping the original list during filtering discussions/searching action)
            currentDiscussion: {}, // Current/selected discussion id
            discussionArr: [],
            loading: false,
            filterTitle: '',
            filterInProgress: false,
            isCreated: false,
            isGenerating: false,
            isCheckbox: false,
            isSelectAll: false,
            showConfirmation: false,
            chime: new Audio("chime_aud.wav"),
            showToast: false,
            isSearch: false,
            isDiscussionBottom: false,
        }
    },
    methods: {
        async list_discussions() {
            try {
                const res = await axios.get('/list_discussions')

                if (res) {

                    this.createDiscussionList(res.data)
                    return res.data
                }
            } catch (error) {
                console.log("Error: Could not list discussions", error)
                return []
            }
        },
        async load_discussion(id) {
            try {
                if (id) {
                    this.loading = true
                    this.setDiscussionLoading(id, this.loading)
                    const res = await axios.post('/load_discussion', {
                        id: id
                    })
                    this.loading = false
                    this.setDiscussionLoading(id, this.loading)
                    if (res) {
                        // Filter out the user and bot entries
                        this.discussionArr = res.data.filter((item) => item.type == 0)

                    }
                }
            } catch (error) {
                console.log(error)
                this.loading = false
                this.setDiscussionLoading(id, this.loading)
            }
        },
        async new_discussion(title) {
            try {
                const res = await axios.get('/new_discussion', { params: { title: title } })

                if (res) {
                    return res.data
                }
            } catch (error) {
                console.log("Error: Could not create new discussion", error)
                return {}
            }
        },
        async delete_discussion(id) {
            try {
                if (id) {
                    this.loading = true
                    this.setDiscussionLoading(id, this.loading)
                    await axios.post('/delete_discussion', {
                        id: id
                    })
                    this.loading = false
                    this.setDiscussionLoading(id, this.loading)
                }
            } catch (error) {
                console.log("Error: Could not delete discussion", error)
                this.loading = false
                this.setDiscussionLoading(id, this.loading)
            }
        },
        async edit_title(id, new_title) {
            try {
                if (id) {
                    this.loading = true
                    this.setDiscussionLoading(id, this.loading)
                    const res = await axios.post('/edit_title', {
                        id: id,
                        title: new_title
                    })
                    this.loading = false
                    this.setDiscussionLoading(id, this.loading)
                    if (res.status == 200) {
                        const index = this.list.findIndex((x) => x.id == id)
                        const discussionItem = this.list[index]
                        discussionItem.title = new_title
                        this.tempList = this.list
                    }
                }
            } catch (error) {
                console.log("Error: Could not edit title", error)
                this.loading = false
                this.setDiscussionLoading(id, this.loading)
            }
        },
        async delete_message(id) {
            try {
                const res = await axios.get('/delete_message', { params: { id: id } })

                if (res) {
                    return res.data
                }
            } catch (error) {
                console.log("Error: Could delete message", error)
                return {}
            }
        },
        async stop_gen() {
            try {
                const res = await axios.get('/stop_gen')

                if (res) {
                    return res.data
                }
            } catch (error) {
                console.log("Error: Could not stop generating", error)
                return {}
            }
        },
        async message_rank_up(id) {
            try {
                const res = await axios.get('/message_rank_up', { params: { id: id } })

                if (res) {
                    return res.data
                }
            } catch (error) {
                console.log("Error: Could not rank up message", error)
                return {}
            }
        },
        async message_rank_down(id) {
            try {
                const res = await axios.get('/message_rank_down', { params: { id: id } })

                if (res) {
                    return res.data
                }
            } catch (error) {
                console.log("Error: Could not rank down message", error)
                return {}
            }
        },
        async update_message(id, message) {
            try {
                const res = await axios.get('/update_message', { params: { id: id, message: message } })

                if (res) {
                    return res.data
                }
            } catch (error) {
                console.log("Error: Could not update message", error)
                return {}
            }
        },
        async export_multiple_discussions(discussionIdArr) {
            try {
                if (discussionIdArr.length > 0) {
                    const res = await axios.post('/export_multiple_discussions', {
                        discussions: discussionIdArr
                    })

                    if (res) {
                        return res.data
                    }
                }

            } catch (error) {
                console.log("Error: Could not export multiple discussions", error)
                return {}
            }
        },
        filterDiscussions() {
            // Search bar in for filtering discussions by title (serch)

            if (!this.filterInProgress) {
                this.filterInProgress = true
                setTimeout(() => {
                    this.list = this.tempList.filter((item) => item.title && item.title.includes(this.filterTitle))
                    this.filterInProgress = false
                }, 100)
            }
        },
        async selectDiscussion(item) {
            if (item) {

                // When discussion is selected it loads the discussion array
                if (this.currentDiscussion.id != item.id) {

                    this.currentDiscussion = item

                    this.setPageTitle(item)

                    localStorage.setItem('selected_discussion', this.currentDiscussion.id)

                    await this.load_discussion(item.id)

                    if (this.discussionArr.length > 1) {
                        if (this.currentDiscussion.title === '' || this.currentDiscussion.title === null) {
                            this.changeTitleUsingUserMSG(this.currentDiscussion.id, this.discussionArr[1].content)
                        }
                    }
                }
                nextTick(() => {

                    const msgList = document.getElementById('messages-list')

                    this.scrollBottom(msgList)

                })
            }
        },
        scrollToElement(el) {

            if (el) {
                el.scrollIntoView({ behavior: 'smooth', block: 'start', inline: 'nearest' })
            } else {
                console.log("Error: scrollToElement")
            }
        },
        scrollBottom(el) {

            if (el) {
                el.scrollTo(
                    {
                        top: el.scrollHeight,
                        behavior: "smooth",
                    }
                )
            } else {
                console.log("Error: scrollBottom")
            }

        },

        scrollTop(el) {

            if (el) {
                el.scrollTo(
                    {
                        top: 0,
                        behavior: "smooth",
                    }
                )
            } else {
                console.log("Error: scrollBottom")
            }

        },
        createUserMsg(msgObj) {
            let usrMessage = {
                content: msgObj.message,
                id: msgObj.id,
                //parent: 10,
                rank: 0,
                sender: msgObj.user
                //type: 0
            }
            this.discussionArr.push(usrMessage)
            nextTick(() => {
                const msgList = document.getElementById('messages-list')

                this.scrollBottom(msgList)

            })
        },
        updateLastUserMsg(msgObj) {

            const lastMsg = this.discussionArr[this.discussionArr.length - 1]
            lastMsg.content = msgObj.message
            lastMsg.id = msgObj.user_message_id
            // lastMsg.parent=msgObj.parent
            lastMsg.rank = msgObj.rank
            lastMsg.sender = msgObj.user
            // lastMsg.type=msgObj.type
        },
        createBotMsg(msgObj) {
            // Update previous message with reponse user data
            //
            // msgObj
            // "status": "if the model is not ready this will inform the user that he can't promt the model"
            // "type": "input_message_infos",
            // "bot": self.personality.name,
            // "user": self.personality.user_name,
            // "message":message,#markdown.markdown(message),
            // "user_message_id": self.current_user_message_id,
            // "ai_message_id": self.current_ai_message_id,
            console.log(msgObj);
            if (msgObj["status"] == "generation_started") {
                this.updateLastUserMsg(msgObj)
                // Create response message
                let responseMessage = {
                    content: "✍ please stand by ...",//msgObj.message,
                    id: msgObj.ai_message_id,
                    parent: msgObj.user_message_id,
                    rank: 0,
                    sender: msgObj.bot,
                    //type: msgObj.type
                }
                this.discussionArr.push(responseMessage)
                nextTick(() => {
                    const msgList = document.getElementById('messages-list')

                    this.scrollBottom(msgList)

                })

                if (this.currentDiscussion.title === '' || this.currentDiscussion.title === null) {
                    if (msgObj.type == "input_message_infos") {
                        // This is a user input
                        this.changeTitleUsingUserMSG(this.currentDiscussion.id, msgObj.message)

                    }
                }
                console.log("infos", msgObj)
            }
            else {
                this.$refs.toast.showToast("It seems that no model has been loaded. Please download and install a model first, then try again.", 4, false)
                this.isGenerating = false
                this.setDiscussionLoading(this.currentDiscussion.id, this.isGenerating)
                this.chime.play()
            }
        },
        sendMsg(msg) {
            // Sends message to backend
            this.isGenerating = true;
            this.setDiscussionLoading(this.currentDiscussion.id, this.isGenerating);
            axios.get('/get_generation_status', {}).then((res) => {
                if (res) {
                    //console.log(res.data.status);
                    if (!res.data.status) {
                        socket.emit('generate_msg', { prompt: msg });

                        // Create new User message
                        // Temp data
                        let usrMessage = {
                            message: msg,
                            id: 0,
                            rank: 0,
                            user: "user"
                        };
                        this.createUserMsg(usrMessage);

                    }
                    else {
                        console.log("Already generating");
                    }
                }
            }).catch((error) => {
                console.log("Error: Could not get generation status", error);
            });
        },
        streamMessageContent(msgObj) {
            // Streams response message content from backend
            //console.log("stream", JSON.stringify(content))
            const parent = msgObj.user_message_id
            const discussion_id = msgObj.discussion_id
            // next statement - incorrect comparison: was '=' and should be '=='
            
            this.setDiscussionLoading(discussion_id, true );
            if (this.currentDiscussion.id == discussion_id) {
                
                this.isGenerating = true;
                const index = this.discussionArr.findIndex((x) => x.parent == parent && x.id == msgObj.ai_message_id)
                const messageItem = this.discussionArr[index]
                if (messageItem) {
                    messageItem.content = msgObj.data
                    //console.log("user-msg-id",parent, "ai-msg-id",msgObj.ai_message_id, index, discussion_id, msgObj.data)
                }

            }


            //const lastMsg = this.discussionArr[this.discussionArr.length - 1]
            //lastMsg.content = content.data
        },
        async changeTitleUsingUserMSG(id, msg) {
            // If discussion is untitled or title is null then it sets the title to first user message.

            const index = this.list.findIndex((x) => x.id == id)
            const discussionItem = this.list[index]
            if (msg) {
                discussionItem.title = msg
                this.tempList = this.list
                await this.edit_title(id, msg)
            }

        },
        async createNewDiscussion() {
            // Creates new discussion on backend,
            // gets new discussion list, selects
            // newly created discussion,
            // scrolls to the discussion
            this.loading = true
            const res = await this.new_discussion()
            this.loading = false
            await this.list_discussions()
            const index = this.list.findIndex((x) => x.id == res.id)
            const discussionItem = this.list[index]
            this.selectDiscussion(discussionItem)
            nextTick(() => {
                const selectedDisElement = document.getElementById('dis-' + res.id)
                this.scrollToElement(selectedDisElement)
            })
            //console.log("disc",JSON.stringify(discussionItem))
        },
        loadLastUsedDiscussion() {
            // Checks local storage for last selected discussion
            const id = localStorage.getItem('selected_discussion')
            if (id) {
                const index = this.list.findIndex((x) => x.id == id)
                const discussionItem = this.list[index]
                if (discussionItem) {
                    this.selectDiscussion(discussionItem)
                }
            }
        },
        async deleteDiscussion(id) {
            // Deletes discussion from backend and frontend

            //const index = this.list.findIndex((x) => x.id == id)
            //const discussionItem = this.list[index]
            //discussionItem.loading = true
            await this.delete_discussion(id)
            if (this.currentDiscussion.id == id) {
                this.currentDiscussion = {}
                this.discussionArr = []
                this.setPageTitle()
            }
            this.list.splice(this.list.findIndex(item => item.id == id), 1)

            this.createDiscussionList(this.list)
            //await this.list_discussions()
        },
        async deleteDiscussionMulti() {
            // Delete selected discussions

            const deleteList = this.selectedDiscussions

            for (let i = 0; i < deleteList.length; i++) {
                const discussionItem = deleteList[i]
                //discussionItem.loading = true
                await this.delete_discussion(discussionItem.id)
                if (this.currentDiscussion.id == discussionItem.id) {
                    this.currentDiscussion = {}
                    this.discussionArr = []
                    this.setPageTitle()
                }
                this.list.splice(this.list.findIndex(item => item.id == discussionItem.id), 1)
            }
            this.tempList = this.list
            this.isCheckbox = false
            console.log("Multi delete done")
        },
        async deleteMessage(msgId) {

            await this.delete_message(msgId).then(() => {

                this.discussionArr.splice(this.discussionArr.findIndex(item => item.id == msgId), 1)

            }).catch(() => {

                console.log("Error: Could not delete message")
            })

        },
        async editTitle(newTitleObj) {

            const index = this.list.findIndex((x) => x.id == newTitleObj.id)
            const discussionItem = this.list[index]
            discussionItem.title = newTitleObj.title
            discussionItem.loading = true
            await this.edit_title(newTitleObj.id, newTitleObj.title)
            discussionItem.loading = false
        },
        checkUncheckDiscussion(event, id) {
            // If checked = true and item is not in array then add item to list
            const index = this.list.findIndex((x) => x.id == id)
            const discussionItem = this.list[index]
            discussionItem.checkBoxValue = event.target.checked
            this.tempList = this.list
        },
        selectAllDiscussions() {

            // Check if there is one discussion not selected
            this.isSelectAll = !this.tempList.filter((item) => item.checkBoxValue == false).length > 0
            // Selects or deselects all discussions
            for (let i = 0; i < this.tempList.length; i++) {
                this.tempList[i].checkBoxValue = !this.isSelectAll
            }

            this.tempList = this.list
            this.isSelectAll = !this.isSelectAll
        },
        createDiscussionList(disList) {
            // This creates a discussion list for UI with additional properties
            if (disList) {
                const newDisList = disList.map((item) => {

                    const newItem = {
                        id: item.id,
                        title: item.title,
                        selected: false,
                        loading: false,
                        checkBoxValue: false
                    }
                    return newItem

                })
                this.list = newDisList
                this.tempList = newDisList

            }
        },
        setDiscussionLoading(id, loading) {
            const index = this.list.findIndex((x) => x.id == id)
            const discussionItem = this.list[index]
            discussionItem.loading = loading
        },
        setPageTitle(item) {
            // item is either title:String or {id:Number, title:String}
            if (item) {
                if (item.id) {
                    const realTitle = item.title ? item.title === "untitled" ? "New discussion" : item.title : "New discussion"
                    document.title = 'GPT4ALL - WEBUI - ' + realTitle
                } else {
                    const title = item || "Welcome"
                    document.title = 'GPT4ALL - WEBUI - ' + title
                }
            } else {
                const title = item || "Welcome"
                document.title = 'GPT4ALL - WEBUI - ' + title
            }

        },
        async rankUpMessage(msgId) {
            await this.message_rank_up(msgId).then((res) => {

                const message = this.discussionArr[this.discussionArr.findIndex(item => item.id == msgId)]
                message.rank = res.new_rank
            }).catch(() => {

                console.log("Error: Could not rank up message")
            })

        },
        async rankDownMessage(msgId) {
            await this.message_rank_down(msgId).then((res) => {

                const message = this.discussionArr[this.discussionArr.findIndex(item => item.id == msgId)]
                message.rank = res.new_rank
            }).catch(() => {

                console.log("Error: Could not rank down message")
            })

        },
        async updateMessage(msgId, msg) {
            await this.update_message(msgId, msg).then(() => {

                const message = this.discussionArr[this.discussionArr.findIndex(item => item.id == msgId)]
                message.content = msg

            }).catch(() => {

                console.log("Error: Could not update message")
            })

        },
        resendMessage(msgId, msg) {
            // Resend message
            this.isGenerating = true;
            this.setDiscussionLoading(this.currentDiscussion.id, this.isGenerating);
            axios.get('/get_generation_status', {}).then((res) => {
                if (res) {
                    //console.log(res.data.status);
                    if (!res.data.status) {
                        socket.emit('generate_msg_from', { prompt: msg, id: msgId });


                    }
                    else {
                        console.log("Already generating");
                    }
                }
            }).catch((error) => {
                console.log("Error: Could not get generation status", error);
            });
        },
        stopGenerating() {
            this.stop_gen()
            this.isGenerating = false
            console.log("Stopped generating")
        },
        finalMsgEvent(msgObj) {
            console.log("final", msgObj)

            // Last message contains halucination suppression so we need to update the message content too
            const parent = msgObj.parent
            const discussion_id = msgObj.discussion_id
            if (this.currentDiscussion.id == discussion_id) {
                const index = this.discussionArr.findIndex((x) => x.parent == parent && x.id == msgObj.ai_message_id)
                const messageItem = this.discussionArr[index]
                if (messageItem) {
                    messageItem.content = msgObj.data
                }
            }

            this.isGenerating = false
            this.setDiscussionLoading(this.currentDiscussion.id, this.isGenerating)
            this.chime.play()
        },
        copyToClipBoard(content) {

            this.$refs.toast.showToast("Copied to clipboard successfully")
            nextTick(() => {
                feather.replace()

            })
        },
        closeToast() {
            this.showToast = false
        },
        saveJSONtoFile(jsonData, filename) {
            filename = filename || "data.json"
            const a = document.createElement("a");
            a.href = URL.createObjectURL(new Blob([JSON.stringify(jsonData, null, 2)], {
                type: "text/plain"
            }));
            a.setAttribute("download", filename);
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
        },
        async exportDiscussions() {
            // Export selected discussions

            const discussionIdArr = this.list.filter((item) => item.checkBoxValue == true).map((item) => {
                return item.id
            })

            if (discussionIdArr.length > 0) {
                console.log("export", discussionIdArr)
                let dateObj = new Date()

                const year = dateObj.getFullYear();
                const month = (dateObj.getMonth() + 1).toString().padStart(2, "0");
                const day = dateObj.getDate().toString().padStart(2, "0");
                const hours = dateObj.getHours().toString().padStart(2, "0");
                const minutes = dateObj.getMinutes().toString().padStart(2, "0");
                const seconds = dateObj.getSeconds().toString().padStart(2, "0");
                const formattedDate =
                    year +
                    "." +
                    month +
                    "." +
                    day +
                    "." +
                    hours +
                    "" +
                    minutes +
                    "" +
                    seconds;

                const filename = 'discussions_export_' + formattedDate + '.json'
                this.loading = true
                const res = await this.export_multiple_discussions(discussionIdArr)

                if (res.data) {
                    this.saveJSONtoFile(res.data, filename)

                }
                this.loading = false
            }

        }


    },
    async created() {
        // Constructor



        this.setPageTitle()
        await this.list_discussions()

        this.loadLastUsedDiscussion()
        this.isCreated = true

        nextTick(() => {
            feather.replace()
        })

        // socket responses
        socket.on('infos', this.createBotMsg)
        socket.on('message', this.streamMessageContent)
        socket.on("final", this.finalMsgEvent)

    },
    activated() {
        // This lifecycle hook runs every time you switch from other page back to this page (vue-router)
        // To fix scrolling back to last message, this hook is needed.
        // If anyone knows hor to fix scroll issue when changing pages, please do fix it :D
        console.log("Websocket connected (activated)", this.socketConnected)

        if (this.isCreated) {
            this.loadLastUsedDiscussion()
        }
    },
    components: {
        Discussion,
        Message,
        ChatBox,
        WelcomeComponent,
        Toast
    },
    watch: {
        filterTitle(newVal) {
            if (newVal == '') {
                this.filterInProgress = true
                this.list = this.tempList
                this.filterInProgress = false
            }
        },
        isCheckbox(newval) {
            nextTick(() => {
                feather.replace()
            })
            if (!newval) {
                this.isSelectAll = false
            }
        },
        socketConnected(newval) {
            console.log("Websocket connected (watch)", newval)
        },
        showConfirmation() {
            nextTick(() => {
                feather.replace()

            })
        },
        isSearch() {
            nextTick(() => {
                feather.replace()

            })
        },

    },
    computed: {
        socketConnected() {
            return true
        },
        selectedDiscussions() {
            nextTick(() => {
                feather.replace()

            })
            return this.list.filter((item) => item.checkBoxValue == true)
        }
    }
}
</script>

<script setup>
import Discussion from '../components/Discussion.vue'
import Message from '../components/Message.vue'
import ChatBox from '../components/ChatBox.vue'
import WelcomeComponent from '../components/WelcomeComponent.vue'
import Toast from '../components/Toast.vue'

import feather from 'feather-icons'

import axios from 'axios'
import { nextTick } from 'vue'

import socket from '@/services/websocket.js'

import { onMounted } from 'vue'
import { initFlowbite } from 'flowbite'

// initialize components based on data attribute selectors
onMounted(() => {
    initFlowbite()
})

axios.defaults.baseURL = import.meta.env.VITE_GPT4ALL_API_BASEURL
</script>
