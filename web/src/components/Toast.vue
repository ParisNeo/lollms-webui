<template>
    <div v-if="show" class="absolute bottom-16 right-2 z-20">
        <div id="toast-success"
            class="flex items-center w-full max-w-xs p-4 mb-4 text-gray-500 bg-white rounded-lg shadow dark:text-gray-400 dark:bg-gray-800"
            role="alert">
            <div class="flex flex-row  items-center">
                <slot>
                <div v-if="success"
                    class="inline-flex items-center justify-center flex-shrink-0 w-8 h-8 text-green-500 bg-green-100 rounded-lg dark:bg-green-800 dark:text-green-200">
                    <i data-feather="check"></i>
                    <span class="sr-only">Check icon</span>
                </div>
                <div v-if="!success" class="inline-flex items-center justify-center flex-shrink-0 w-8 h-8 text-red-500 bg-red-100 rounded-lg dark:bg-red-800 dark:text-red-200">
                    <i data-feather="x"></i>
                    <span class="sr-only">Cross icon</span>
                </div>             
                <div class="ml-3 text-sm font-normal whitespace-pre-wrap">{{ message }}</div>

                </slot>
            </div>
            <button type="button" @click="close"
                class="ml-auto -mx-1.5 -my-1.5 bg-white text-gray-400 hover:text-gray-900 rounded-lg focus:ring-2 focus:ring-gray-300 p-1.5 hover:bg-gray-100 inline-flex h-8 w-8 dark:text-gray-500 dark:hover:text-white dark:bg-gray-800 dark:hover:bg-gray-700"
                data-dismiss-target="#toast-success" aria-label="Close">
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
</template>

<script>

export default {
    name: 'Toast',
    emits: ['close'],
    props: {
        showProp: false
    },
    data() {
        return {
            show: false,
            success: true,
            message: ''
        };
    },
    methods: {
        close() {
            this.$emit('close')
            this.show = false
        },
        showToast(message, duration_s=3, success= true){
            this.success = success;
            this.message = message;
            this.show = true;

            setTimeout(() => {
                    this.$emit('close')
                    this.show = false
                }, duration_s*1000);            
        }
    },
    watch: {
        showProp(val) {
            this.show = val
            if (val) {
                setTimeout(() => {
                    this.$emit('close')
                    this.show = false
                }, 3000);
                
            }

        }
    }
}
</script>
