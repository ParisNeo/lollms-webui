<template>
    <div :class="selected ? 'bg-bg-light-discussion dark:bg-bg-dark-discussion shadow-md' : ''"
        class="container flex flex-col sm:flex-row item-center shadow-sm gap-2 py-2 my-2 hover:shadow-md hover:bg-primary-light dark:hover:bg-primary rounded-md p-2 duration-75 group cursor-pointer"
        :id="'dis-' + id" @click.stop="selectEvent()">
        <!-- INDICATOR FOR SELECTED ITEM -->
        <div v-if="selected" class="items-center inline-block min-h-full w-2 rounded-xl self-stretch "
            :class="loading ? 'animate-bounce bg-accent ' : ' bg-secondary '"></div>
        <div v-if="!selected" class="items-center inline-block min-h-full w-2 rounded-xl self-stretch"></div>

        <!-- TITLE -->
        <p v-if="!editTitle" :title="title" class="truncate w-full">{{ title ? title === "untitled" ? "New discussion" : title : "New discussion" }}</p>

        <input v-if="editTitle" type="text" id="title-box" class="bg-bg-light dark:bg-bg-dark rounded-md border-0 w-full -m-1 p-1"
            :value="title" required  @input="chnageTitle($event.target.value)" @click.stop>

        <!-- CONTROL BUTTONS -->
        <div class="flex items-center flex-1 max-h-6">
            <!-- DELETE CONFIRM -->
            <div v-if="showConfirmation && !editTitleMode" class="flex gap-3 flex-1 items-center justify-end  duration-75">
                <button class="text-2xl hover:text-secondary duration-75 active:scale-90" title="Confirm removal"
                    type="button" @click.stop="deleteEvent()">
                    <i data-feather="check"></i>
                </button>
                <button class="text-2xl hover:text-red-600 duration-75 active:scale-90 " title="Cancel removal"
                    type="button" @click.stop="showConfirmation = false">
                    <i data-feather="x"></i>
                </button>
            </div>
            <!-- EDIT TITLE CONFIRM -->
            <div v-if="showConfirmation && editTitleMode" class="flex gap-3 flex-1 items-center justify-end  duration-75">
                <button class="text-2xl hover:text-red-600 duration-75 active:scale-90 " title="Discard title changes"
                    type="button" @click.stop="editTitleMode = false ">
                    <i data-feather="x"></i>
                </button>
                <button class="text-2xl hover:text-secondary duration-75 active:scale-90" title="Confirm title changes"
                    type="button" @click.stop="editTitleEvent()">
                    <i data-feather="check"></i>
                </button>

            </div>
            <!-- EDIT AND REMOVE -->
            <div v-if="!showConfirmation"
                class="flex gap-3 flex-1 items-center justify-end invisible group-hover:visible duration-75">
                <button class="text-2xl hover:text-secondary duration-75 active:scale-90" title="Edit title" type="button"
                    @click.stop="editTitleMode = true">
                    <i data-feather="edit-2"></i>
                </button>
                <button class="text-2xl hover:text-red-600 duration-75 active:scale-90 " title="Remove discussion"
                    type="button" @click.stop="showConfirmation = true">
                    <i data-feather="trash"></i>
                </button>
            </div>
        </div>
    </div>
</template>

<script>
import { nextTick } from 'vue'
import feather from 'feather-icons'

export default {
    name: 'Discussion',
    emits: ['delete', 'select', 'editTitle'],
    props: {
        id: Number,
        title: String,
        selected: Boolean,
        loading: Boolean
    },
    setup() {

    },
    data() {
        return {
            showConfirmation: false,
            editTitleMode: false,
            editTitle: false,
            newTitle: String,
        }
    },
    methods: {
        deleteEvent() {
            this.showConfirmation = false
            this.$emit("delete")
        },
        selectEvent() {
            this.$emit("select")
        },
        editTitleEvent() {
            this.editTitle= false
            this.editTitleMode= false
            this.showConfirmation = false
            this.$emit("editTitle", 
            {
                title: this.newTitle, 
                id: this.id
            })
        },
        chnageTitle(text){
            this.newTitle=text
        }
    },
    mounted() {
        this.newTitle= this.title
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

            this.showConfirmation=newval
            this.editTitle = newval
        }
    }
}
</script>
<style scoped></style>
