<template>
    <div class="absolute bottom-16 right-2 z-20 flex flex-col gap-3 min-w-[300px]">
        <TransitionGroup name="toastItem" tag="div">
            <div v-for=" t in toastArr" :key="t.id" class="relative">
                <div class="flex flex-row items-center w-full p-4 mb-4 text-gray-500 bg-white rounded-lg shadow dark:text-gray-400 dark:bg-gray-800" role="alert">
                    <div class="flex flex-row flex-grow items-center h-auto">
                        <div v-if="t.log_type==0"
                            class="inline-flex items-center justify-center flex-shrink-0 w-8 h-8 text-red-500 bg-red-100 rounded-lg dark:bg-red-800 dark:text-red-200">
                            <i data-feather="x"></i>
                            <span class="sr-only">Cross icon</span>
                        </div>
                        <div v-if="t.log_type==1"
                            class="inline-flex items-center justify-center flex-shrink-0 w-8 h-8 text-green-500 bg-green-100 rounded-lg dark:bg-green-800 dark:text-green-200">
                            <i data-feather="check"></i>
                            <span class="sr-only">Check icon</span>
                        </div>
                        <div v-if="t.log_type==2"
                            class="inline-flex items-center justify-center flex-shrink-0 w-8 h-8 text-blue-500 bg-blue-100 rounded-lg dark:bg-blue-800 dark:text-blue-200">
                            <i data-feather="info"></i>
                            <span class="sr-only"></span>
                        </div>
                        <div v-if="t.log_type==3"
                            class="inline-flex items-center justify-center flex-shrink-0 w-8 h-8 text-orange-500 bg-orange-100 rounded-lg dark:bg-orange-800 dark:text-orange-200">
                            <i data-feather="alert-triangle"></i>
                            <span class="sr-only"></span>
                        </div>
                        <div class="ml-3 text-sm font-normal whitespace-pre-wrap line-clamp-3 max-w-xs max-h-[400px] overflow-auto break-words" :title="t.message">{{ t.message }}</div>

                    </div>
                
                    <div class="flex ">
                        <button type="button" @click.stop="copyToClipBoard(t.message)" title="Copy message"
                            class=" bg-white text-gray-400 hover:text-gray-900 rounded-lg focus:ring-2 focus:ring-gray-300 p-1.5 hover:bg-gray-100 inline-flex h-8 w-8 dark:text-gray-500 dark:hover:text-white dark:bg-gray-800 dark:hover:bg-gray-700">
                            <span class="sr-only">Copy message</span>
                            <i data-feather="clipboard" class="w-5 h-5"></i>

                        </button>
                        <button type="button" @click="close(t.id)" title="Close"
                            class=" bg-white text-gray-400 hover:text-gray-900 rounded-lg focus:ring-2 focus:ring-gray-300 p-1.5 hover:bg-gray-100 inline-flex h-8 w-8 dark:text-gray-500 dark:hover:text-white dark:bg-gray-800 dark:hover:bg-gray-700">
                            <span class="sr-only">Close</span>
                            <svg aria-hidden="true" class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"
                                xmlns="http://www.w3.org/2000/svg">
                                <path fill-rule="evenodd"
                                    d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                                    clip-rule="evenodd"></path>
                            </svg>
                        </button>
                    </div>

                </div>
            </div>
        </TransitionGroup>
    </div>
</template>

<script>
import feather from 'feather-icons'
import { nextTick, TransitionGroup } from 'vue'
export default {
    name: 'Toast',

    props: {

    },
    data() {
        return {
            show: false,
            log_type: 1, // 0=error, 1=success, 2=info, 3=warning
            message: '',
            toastArr: []
        };
    },
    methods: {
        close(id) {

            this.toastArr = this.toastArr.filter(item => item.id != id)
        },
        copyToClipBoard(content) {

            navigator.clipboard.writeText(content);

          

            nextTick(() => {
                feather.replace()

            })


        },
        showToast(message, duration_s = 3, log_type = true) {
            const id = parseInt(((new Date()).getTime() * Math.random()).toString()).toString()
            const toastObj = {
                id: id,
                log_type: log_type,
                message: message,
                show: true,
                //copy: this.copyToClipBoard(message)
            }


            this.toastArr.push(toastObj)

            nextTick(() => {
                feather.replace()

            })
            setTimeout(() => {

                this.toastArr = this.toastArr.filter(item => item.id != id)

            }, duration_s * 1000);
        }

    },
    watch: {

    }
}
</script>
<style scoped>
.toastItem-enter-active,
.toastItem-leave-active {
    transition: all 0.5s ease;
}

.toastItem-enter-from,
.toastItem-leave-to {
    opacity: 0;
    transform: translateX(-30px);
}
</style>