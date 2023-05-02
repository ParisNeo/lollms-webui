<template>
    <div class="flex-none sticky bottom-0 p-6 items-center justify-center self-center right-0 left-0 ">
        <form>
            <label for="chat" class="sr-only">Send message</label>
            <div class="flex items-center gap-2 px-3 py-3 rounded-lg bg-bg-light-tone-panel dark:bg-bg-dark-tone-panel shadow-lg  ">

                <textarea id="chat" rows="1"
                    class="block min-h-11  no-scrollbar  p-2.5 w-full text-sm text-gray-900 bg-bg-light rounded-lg border border-gray-300 focus:ring-blue-500 focus:border-blue-500 dark:bg-bg-dark dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
                    placeholder="Send message..." @keydown.enter.exact="submitOnEnter($event)" ></textarea>
                <button type="submit" on on-click=""
                    class="inline-flex justify-center p-2 rounded-full cursor-pointer hover:text-primary duration-75 active:scale-90">
                    
                    <i data-feather="send" class=" w-6 h-6 m-1"></i>
                    
                    <span class="sr-only">Send message</span>
                </button>
            </div>
        </form>
    </div>
</template>
<style>

</style>

<script>
import {nextTick} from 'vue'
import feather from 'feather-icons'
import websocket from '@/services/websocket.js';

export default {
    name: 'ChatBox',
    setup() {
        return {}
    },
    methods: {
        submitOnEnter(event) {
            if (event.which === 13) {
                event.preventDefault(); // Prevents the addition of a new line in the text field
                console.log("enter detected");
                if (!event.repeat) {
                    // const newEvent = new Event("submit", { cancelable: true });
                    // event.target.form.dispatchEvent(newEvent);
                    console.log(event.target.value)
                    console.log(websocket)
                    websocket.emit('generate_msg',{prompt: event.target.value});
                }

            }
        },
        submit(event){
            event.preventDefault(); // Prevents the addition of a new line in the text field
            websocket.emit('generate_msg',{prompt: event.target.value});

        }
    },mounted(){
        nextTick(()=>{
                feather.replace()

            })
    },
    activated(){

    }
}
</script>
<script setup>

</script>