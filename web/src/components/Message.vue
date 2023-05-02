<template>
    <div
        class="group rounded-lg m-2 shadow-lg hover:border-primary dark:hover:border-primary hover:border-solid hover:border-2 border-2 border-transparent even:bg-bg-light-discussion-odd dark:even:bg-bg-dark-discussion-odd flex-row p-4 pb-2">
        <div class="w-30 flex">
            <!-- SENDER -->
            <div class="w-10 h-10 rounded-lg object-fill drop-shadow-md group-even:bg-primary  bg-secondary">
                <img v-if="senderImg" :src="senderImg" class="w-10 h-10 rounded-full object-fill ">

            </div>
            <p class="drop-shadow-sm   py-0 px-2 text-lg text-opacity-95 font-bold ">{{ message.sender }}</p>
        </div>
        <div class="-mt-4  ml-10 mr-0 pt-1 px-2 max-w-screen-2xl  ">
            <!-- CONTENT/MESSAGE -->
            {{ message.content }}
        </div>
        <div class="invisible group-hover:visible flex flex-row mt-3 -mb-2">
            <!-- MESSAGE CONTROLS -->
            <div class="text-lg hover:text-secondary duration-75 active:scale-90 p-2"
                title="Edit message">
                <i data-feather="edit"></i>
            </div>
            <div class="text-lg hover:text-secondary duration-75 active:scale-90 p-2"
                title="Copy message to clipboard">
                <i data-feather="copy"></i>
            </div>
            <div class="text-lg hover:text-secondary duration-75 active:scale-90 p-2"
                title="Resend message">
                <i data-feather="refresh-cw"></i>
            </div>
            <div class="text-lg hover:text-red-600 duration-75 active:scale-90 p-2"
                title="Remove message">
                <i data-feather="trash"></i>
            </div>
            <div class="text-lg hover:text-secondary duration-75 active:scale-90 p-2"
                title="Upvote">
                <i data-feather="thumbs-up"></i>
            </div>
            <div class="flex flex-row items-center">
                <div class="text-lg hover:text-red-600 duration-75 active:scale-90 p-2"
                title="Downvote">
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
import {nextTick} from 'vue'
import feather from 'feather-icons'
export default {
    name: 'Message',
    props: {
        message: Object
    },
    data() {
        return {
           
            senderImg:''
        }
    },mounted(){
        nextTick(()=>{
                feather.replace()

            })
    },
}
</script>