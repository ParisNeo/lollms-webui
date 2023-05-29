<template>
    <TransitionGroup name="list" tag="div">


        <div key="dropmenu" v-if="show"
            class="select-none text-slate-50 absolute top-0 left-0 right-0 bottom-0 flex flex-col  items-center justify-center bg-black bg-opacity-50 duration-200 backdrop-blur-sm "
            @dragleave.prevent="panelLeave($event)" @drop.stop.prevent="panelDrop($event)">
            <div
                class="flex flex-col  items-center justify-center p-8 rounded-lg shadow-lg border-dashed border-4 border-secondary w-4/5 h-4/5 " >


                <div class="text-4xl " :class="dropRelease?'':'pointer-events-none'">

                    <div v-if="fileList.length == 0">
                        Drop your files here
                    </div>

                    <div v-if="fileList.length > 0" class="flex flex-row gap-2 items-center">
                        <i data-feather="file" class="w-12 h-12"></i>
                        Files to upload
                        ({{ fileList.length }})
                    </div>
                </div>
                <div class=" overflow-auto no-scrollbar">

                    <TransitionGroup name="list" tag="div" class="flex flex-col items-center p-2">
                        <div v-for="file in fileList" :key="file.name">
                            <div class="relative m-1 cursor-pointer">

                                <span
                                    class="inline-flex items-center px-2 py-1 mr-2 text-sm font-medium bg-bg-dark-tone-panel rounded-lg hover:bg-primary-light ">
                                    <i data-feather="file" class="w-5 h-5 mr-1"></i>
                                    {{ file.name }}
                                    ({{ computedFileSize(file.size) }})
                                    <button type="button" title="Remove item"
                                        class="inline-flex items-center p-0.5 ml-2 text-sm rounded-sm hover:text-red-600 active:scale-75"
                                        @click="removeItem(file)">
                                        <i data-feather="x" class="w-5 h-5 "></i>

                                    </button>
                                </span>


                            </div>
                        </div>
                    </TransitionGroup>
                </div>

            </div>
        </div>
    </TransitionGroup>
</template>

<script>
import filesize from '../plugins/filesize'
import feather from 'feather-icons'
import { nextTick, TransitionGroup } from 'vue'
export default {
    setup() {


        return {}
    },
    name: 'DragDrop',
    emits: ['panelLeave', 'panelDrop'],

    data() {
        return {
            fileList: [],
            show: false,
            dropRelease: false
        }
    },
    mounted() {
        //this.fileList.push({ name: 'lol.sss', size: 22 })
        nextTick(() => {
            feather.replace()

        })
    },
    methods: {
        computedFileSize(size) {
            return filesize(size)
        },
        removeItem(file) {
            this.fileList = this.fileList.filter((item) => item != file)
            // console.log(this.fileList)
        },
        panelDrop(event) {
            this.dropRelease = true
            if (event.dataTransfer.files.length > 0) {
                [...event.dataTransfer.files].forEach(element => {
                    this.fileList.push(element)
                });
            }

            nextTick(() => {
                feather.replace()
            })
            this.$emit('panelDrop', this.fileList)
            
            this.show = false
            // console.log("dropped", this.fileList)
            //console.log(event.dataTransfer.files[0]);

        },
        panelLeave() {
            this.$emit('panelLeave')
            console.log('exit/leave')
            this.dropRelease = false
            this.show = false
            //this.fileList = []
            nextTick(() => {
                feather.replace()

            })
        }

    },
}
</script>

<style>
.list-move,
/* apply transition to moving elements */
.list-enter-active,
.list-leave-active {
    transition: all 0.5s ease;
}

.list-enter-from,
.list-leave-to {
    opacity: 0;

}

/* ensure leaving items are taken out of layout flow so that moving
   animations can be calculated correctly. */
.list-leave-active {
    position: absolute;
}
</style>