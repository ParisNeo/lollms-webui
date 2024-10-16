<template>
    <div
        :class="selected ? 'discussion-hilighted min-w-[11rem] max-w-[12rem]' : 'discussion min-w-[12rem] max-w-[12rem]'"
        class="m-1 py-2 flex flex-row sm:flex-row flex-wrap flex-shrink-0 items-center rounded-md duration-75 group cursor-pointer relative"
        :id="'dis-' + id"
        @click.stop="selectEvent()"
    >
        <!-- PRE TITLE SECTION -->
        <div class="flex flex-row items-center gap-2">
            <!-- CHECKBOX  -->
            <div v-if="isCheckbox">
                <input
                    type="checkbox"
                    class="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-700 dark:focus:ring-offset-gray-700 focus:ring-2 dark:bg-gray-600 dark:border-gray-500"
                    @click.stop
                    v-model="checkBoxValue_local"
                    @input="checkedChangeEvent($event, id)"
                />
            </div>
            <!-- INDICATOR FOR SELECTED ITEM -->
            <div
                v-if="selected"
                class="min-h-full w-2 rounded-xl self-stretch"
                :class="loading ? 'animate-bounce bg-accent' : 'bg-secondary'"
            ></div>
            <div
                v-if="!selected"
                class="w-2"
                :class="loading ? 'min-h-full w-2 rounded-xl self-stretch animate-bounce bg-accent' : ''"
            ></div>
        </div>
        <!-- CONTAINER FOR TITLE -->
        <div class="flex flex-row items-center w-full">
            <!-- TITLE -->
            <p
                v-if="!editTitle"
                :title="title"
                class="line-clamp-1 w-full ml-1 -mx-5  text-xs"
            >
                {{
                    title
                        ? title === 'untitled'
                            ? 'New discussion'
                            : title
                        : 'New discussion'
                }}
            </p>

            <input
                v-if="editTitle"
                type="text"
                id="title-box"
                ref="titleBox"
                class="bg-bg-light dark:bg-bg-dark rounded-md border-0 w-full -m-1 p-1"
                :value="title"
                required
                @keydown.enter.exact="editTitleEvent()"
                @keydown.esc.exact="editTitleMode = false"
                @input="chnageTitle($event.target.value)"
                @click.stop
            />
        </div>
        <!-- CONTROL BUTTONS AS SLIDING FLOATING MENU -->
        <div
            class="absolute top-0 right-0 h-full flex items-center"
        >
            <div
                class="flex gap-2 items-center bg-white dark:bg-gray-800 p-2 rounded-l-md shadow-md transform translate-x-full group-hover:translate-x-0 transition-transform duration-300"
            >
                <!-- EDIT TITLE CONFIRM -->
                <div v-if="showConfirmation" class="flex gap-2 items-center">
                    <button
                        class="text-2xl hover:text-red-600 duration-75 active:scale-90"
                        title="Discard title changes"
                        type="button"
                        @click.stop="cancel()"
                    >
                        <i data-feather="x"></i>
                    </button>
                    <button
                        class="text-2xl hover:text-secondary duration-75 active:scale-90"
                        title="Confirm title changes"
                        type="button"
                        @click.stop="editTitleMode ? editTitleEvent() : deleteMode ? deleteEvent() : makeTitleEvent()"
                    >
                        <i data-feather="check"></i>
                    </button>
                </div>
                <!-- EDIT AND REMOVE -->
                <div v-if="!showConfirmation" class="flex gap-2 items-center">
                    <button
                        class="text-2xl hover:text-secondary duration-75 active:scale-90"
                        title="Open folder"
                        type="button"
                        @click.stop="openFolderEvent()"
                    >
                        <i data-feather="folder"></i>
                    </button>
                    <button
                        class="text-2xl hover:text-secondary duration-75 active:scale-90"
                        title="Make a title"
                        type="button"
                        @click.stop="makeTitleMode = true"
                    >
                        <i data-feather="type"></i>
                    </button>
                    <button
                        class="text-2xl hover:text-secondary duration-75 active:scale-90"
                        title="Edit title"
                        type="button"
                        @click.stop="editTitleMode = true"
                    >
                        <i data-feather="edit-2"></i>
                    </button>
                    <button
                        class="text-2xl hover:text-red-600 duration-75 active:scale-90"
                        title="Remove discussion"
                        type="button"
                        @click.stop="deleteMode = true"
                    >
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
<style scoped>
/* Style for the control buttons container */
.control-buttons {
  position: absolute;
  top: 0;
  right: 0;
  height: 100%;
  display: flex;
  align-items: center;
  transform: translateX(100%);
  transition: transform 0.3s;
}

.group:hover .control-buttons {
  transform: translateX(0);
}

.control-buttons-inner {
  display: flex;
  gap: 10px;
  align-items: center;
  background-color: white; /* or your desired color */
  padding: 8px;
  border-radius: 0 0 0 8px; /* Rounded left corners */
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

</style>
