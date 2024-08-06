<template>
    <div :class="selected ? 'discussion-hilighted shadow-md  min-w-[23rem] max-w-[23rem]' : 'discussion min-w-[23rem] max-w-[23rem]'"
        class="m-1 py-2 flex flex-row sm:flex-row  flex-wrap flex-shrink: 0 item-center shadow-sm hover:shadow-md rounded-md duration-75 group cursor-pointer"
        :id="'dis-' + id" @click.stop="selectEvent()">

        <!-- PRE TITLE SECTION -->
        <div class="flex flex-row items-center gap-2">
            <!-- CHECKBOX  -->
            <div v-if="isCheckbox">
                <input type="checkbox"
                    class="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-700 dark:focus:ring-offset-gray-700 focus:ring-2 dark:bg-gray-600 dark:border-gray-500"
                    @click.stop v-model="checkBoxValue_local" @input="checkedChangeEvent($event, id)">

            </div>
            <!-- INDICATOR FOR SELECTED ITEM -->
            <div v-if="selected" class="min-h-full w-2 rounded-xl self-stretch "
                :class="loading ? 'animate-bounce bg-accent ' : ' bg-secondary '"></div>
            <div v-if="!selected" class="w-2"
                :class="loading ? 'min-h-full w-2 rounded-xl self-stretch animate-bounce bg-accent ' : '  '"></div>

        </div>
        <!-- CONTAINER FOR TITLE AND CONTROL BUTTONS -->
        <div class="flex flex-row items-center w-full">
            <!-- TITLE -->
            <p v-if="!editTitle" :title="title" class="line-clamp-1 w-4/6 ml-1 -mx-5 ">{{ title ? title === "untitled" ? "New discussion" :
                title : "New discussion" }}</p>

            <input v-if="editTitle" type="text" id="title-box" ref="titleBox"
                class="bg-bg-light dark:bg-bg-dark rounded-md border-0 w-full -m-1 p-1" :value="title" required
                @keydown.enter.exact="editTitleEvent()" @keydown.esc.exact="editTitleMode = false"
                @input="chnageTitle($event.target.value)" @click.stop>

            <!-- CONTROL BUTTONS -->
            <div class="flex items-center flex-1 max-h-6">
                <!-- EDIT TITLE CONFIRM -->
                <div v-if="showConfirmation" class="flex gap-3 flex-1 items-center justify-end  duration-75">
                    <button class="text-2xl hover:text-red-600 duration-75 active:scale-90 " title="Discard title changes"
                        type="button" @click.stop="cancel()">
                        <i data-feather="x"></i>
                    </button>
                    <button class="text-2xl hover:text-secondary duration-75 active:scale-90" title="Confirm title changes"
                        type="button" @click.stop="editTitleMode?editTitleEvent():deleteMode?deleteEvent():makeTitleEvent()">
                        <i data-feather="check"></i>
                    </button>
                </div>
                <!-- EDIT AND REMOVE -->
                <div v-if="!showConfirmation"
                    class="flex gap-3 flex-1 items-center justify-end invisible group-hover:visible duration-75">
                    <button class="text-2xl hover:text-secondary duration-75 active:scale-90" title="Open folder" type="button"
                        @click.stop="openFolderEvent()">
                        <i data-feather="folder"></i>
                    </button>
                    <button class="text-2xl hover:text-secondary duration-75 active:scale-90" title="Make a title" type="button"
                        @click.stop="makeTitleMode = true">
                        <i data-feather="type"></i>
                    </button>
                    <button class="text-2xl hover:text-secondary duration-75 active:scale-90" title="Edit title" type="button"
                        @click.stop="editTitleMode = true">
                        <i data-feather="edit-2"></i>
                    </button>
                    <button class="text-2xl hover:text-red-600 duration-75 active:scale-90 " title="Remove discussion" type="button"
                        @click.stop="deleteMode = true">
                        <i data-feather="trash"></i>
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import { nextTick } from 'vue'
import feather from 'feather-icons'

export default {
    name: 'Discussion',
    emits: ['delete', 'select', 'openFolder', 'editTitle', 'makeTitle', 'checked'],
    props: {
        id: Number,
        title: String,
        selected: Boolean,
        loading: Boolean,
        isCheckbox: Boolean,
        checkBoxValue: Boolean
    },
    setup() {

    },
    data() {
        return {
            showConfirmation: false,
            editTitleMode: false,
            makeTitleMode: false,
            deleteMode:false,
            openFolder:false,
            editTitle: false,
            newTitle: String,
            checkBoxValue_local: false
        }
    },
    methods: {
        cancel(){
            this.editTitleMode = false
            this.makeTitleMode = false
            this.deleteMode = false
            this.showConfirmation = false
        },
        deleteEvent() {
            this.showConfirmation = false
            this.$emit("delete")
        },
        selectEvent() {
            this.$emit("select")
        },
        openFolderEvent() {
            this.$emit("openFolder",
                {
                    id: this.id
                })
        },
        editTitleEvent() {
            this.editTitle = false
            this.editTitleMode = false
            this.makeTitleMode = false
            this.deleteMode = false
            this.showConfirmation = false
            this.$emit("editTitle",
                {
                    title: this.newTitle,
                    id: this.id
                })
        },
        makeTitleEvent(){
            this.$emit("makeTitle",
                {
                    id: this.id
                })
            this.showConfirmation = false
        },
        chnageTitle(text) {
            this.newTitle = text
        },
        checkedChangeEvent(event, id) {
            this.$emit("checked", event, id)
        }
    },
    mounted() {
        this.newTitle = this.title
        nextTick(() => {
            feather.replace()

        })

    }, watch: {
        showConfirmation() {
            nextTick(() => {
                feather.replace()

            })
        },
        editTitleMode(newval) {

            this.showConfirmation = newval
            this.editTitle = newval
            if (newval) {
                nextTick(() => {
                    try{
                        this.$refs.titleBox.focus()
                    }catch{}

                })
            }

        },

        deleteMode(newval) {
            this.showConfirmation = newval
            if (newval) {


                nextTick(() => {
                    this.$refs.titleBox.focus()

                })
            }

        },
        makeTitleMode(newval) {
            this.showConfirmation = newval
        },

        checkBoxValue(newval, oldval) {
            this.checkBoxValue_local = newval

        }
    }
}
</script>
<style scoped></style>
