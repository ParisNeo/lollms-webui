<template>
    <div class="flex-none sticky bottom-0 p-6 items-center justify-center self-center right-0 left-0 ">
        <form>
            <label for="chat" class="sr-only">Send message</label>
            <div
                class="flex items-center gap-2 px-3 py-3 rounded-lg bg-bg-light-tone-panel dark:bg-bg-dark-tone-panel shadow-lg  ">

                <textarea id="chat" rows="1"
                    class="block min-h-11  no-scrollbar  p-2.5 w-full text-sm text-gray-900 bg-bg-light rounded-lg border border-gray-300 focus:ring-blue-500 focus:border-blue-500 dark:bg-bg-dark dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
                    placeholder="Send message..." @keydown.enter.exact="submitOnEnter($event)"></textarea>
                <button type="submit" on on-click=""
                    class="inline-flex justify-center p-2 rounded-full cursor-pointer hover:text-primary duration-75 active:scale-90">

                    <i data-feather="send" class=" w-6 h-6 m-1"></i>

                    <span class="sr-only">Send message</span>
                </button>
            </div>
        </form>
    </div>
</template>


<script>
import { nextTick } from 'vue'
import feather from 'feather-icons'

export default {
    name: 'ChatBox',
    emits: ["messageSentEvent"],
    setup() {
        return {}
    },
    methods: {
        sendMessageEvent(msg) {

            this.$emit('messageSentEvent', msg)

        },
        submitOnEnter(event) {
            if (event.which === 13) {
                event.preventDefault(); // Prevents the addition of a new line in the text field
                console.log("enter detected");
                if (!event.repeat) {

                    this.sendMessageEvent(event.target.value)
                    event.target.value="" // Clear input field
                }

            }
        },
    }, 
    mounted() {
        nextTick(() => {
            feather.replace()
        })
    },
    activated() {

    }
}
</script>
