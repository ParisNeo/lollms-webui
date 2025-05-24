<template>
    <div v-if="show" class="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-50 p-4">
      <!-- Added p-4 to the overlay to prevent modal edges from touching screen edges on small screens -->
      <div class="bg-bg-light dark:bg-bg-dark p-6 sm:p-8 rounded-lg shadow-lg w-full max-w-lg flex flex-col">
        <!--
          - Changed pl-10 pr-10 to p-6 sm:p-8 for consistent padding.
          - Added w-full max-w-lg for better responsiveness.
          - Added flex flex-col to manage height correctly with the scrollable content.
        -->
        <div class="flex-grow overflow-hidden"> <!-- This div allows the next one to take available space and scroll -->
          <div class="max-h-[70vh] overflow-y-auto pr-2 sm:pr-4 scrollbar-thin scrollbar-thumb-gray-400 dark:scrollbar-thumb-gray-600 scrollbar-track-gray-200 dark:scrollbar-track-gray-800 hover:scrollbar-thumb-gray-500 dark:hover:scrollbar-thumb-gray-500 scrollbar-thumb-rounded-md scrollbar-track-rounded-md">
            <!--
              - Changed max-h-500 to max-h-[70vh] for viewport-relative max height.
              - Added pr-2 sm:pr-4 for padding next to the scrollbar.
              - Added tailwind-scrollbar utility classes.
              - The direct child of overflow-y-auto gets the scrollbar.
            -->
            <div class="text-lg font-medium"> <!-- Removed 'container' class, not strictly needed here -->
              <MarkdownRenderer ref="mdRender" :host="''" :markdown-text="message" :message_id="0" :discussion_id="0">
              </MarkdownRenderer>
            </div>
          </div>
        </div>
        <div class="mt-6 flex justify-center flex-shrink-0">
          <!-- Added mt-6 (was mt-4) for a bit more space, flex-shrink-0 to prevent button area from shrinking -->
          <button v-if="has_button" @click="hide" class="bg-primary hover:bg-primary-light active:scale-95 duration-150 text-white px-4 py-2 rounded-lg shadow-lg hover:bg-secondary-dark">
            OK
          </button>
          <svg v-if="!has_button" aria-hidden="true" class="w-8 h-8 animate-spin fill-secondary" viewBox="0 0 100 101"
              fill="none" xmlns="http://www.w3.org/2000/svg">
              <!-- Increased spinner size slightly to w-8 h-8 -->
              <path
                  d="M100 50.5908C100 78.2051 77.6142 100.591 50 100.591C22.3858 100.591 0 78.2051 0 50.5908C0 22.9766 22.3858 0.59082 50 0.59082C77.6142 0.59082 100 22.9766 100 50.5908ZM9.08144 50.5908C9.08144 73.1895 27.4013 91.5094 50 91.5094C72.5987 91.5094 90.9186 73.1895 90.9186 50.5908C90.9186 27.9921 72.5987 9.67226 50 9.67226C27.4013 9.67226 9.08144 27.9921 9.08144 50.5908Z"
                  fill="currentColor" />
              <path
                  d="M93.9676 39.0409C96.393 38.4038 97.8624 35.9116 97.0079 33.5539C95.2932 28.8227 92.871 24.3692 89.8167 20.348C85.8452 15.1192 80.8826 10.7238 75.2124 7.41289C69.5422 4.10194 63.2754 1.94025 56.7698 1.05124C51.7666 0.367541 46.6976 0.446843 41.7345 1.27873C39.2613 1.69328 37.813 4.19778 38.4501 6.62326C39.0873 9.04874 41.5694 10.4717 44.0505 10.1071C47.8511 9.54855 51.7191 9.52689 55.5402 10.0491C60.8642 10.7766 65.9928 12.5457 70.6331 15.2552C75.2735 17.9648 79.3347 21.5619 82.5849 25.841C84.9175 28.9121 86.7997 32.2913 88.1811 35.8758C89.083 38.2158 91.5421 39.6781 93.9676 39.0409Z"
                  fill="currentFill" />
          </svg>
        </div>
      </div>
    </div>
  </template>

  <script>
  import MarkdownRenderer from './MarkdownBundle/MarkdownRenderer.vue'; // Ensure this path is correct

  export default {
    name: 'MessageModal', // Good practice to name components
    data() {
      return {
        show: false,
        has_button: true,
        message: "",
      };
    },
    components:{
      MarkdownRenderer
    },
    methods: {
      hide() {
        this.show = false;
        this.$emit("ok");
      },
      showMessage(message) {
        this.message = message;
        this.has_button = true;
        this.show = true;
      },
      showBlockingMessage(message) {
        this.message = message;
        this.has_button = false;
        this.show = true;
      },
      updateMessage(message) {
        this.message = message;
        // Retain current show state, only update if already visible or let showMessage/showBlockingMessage handle it
        // this.show = true; // Original behavior, might be fine
      },
      hideMessage() {
        this.show = false;
        // Optionally emit an event if needed when programmatically hidden
        // this.$emit("closed");
      },
    },
  };
  </script>

  <style scoped>
  /* You can add component-specific styles here if needed,
     but Tailwind should cover most cases.
     For example, if tailwind-scrollbar plugin doesn't work as expected
     or you need very custom scrollbars for specific browsers,
     you might add ::-webkit-scrollbar styles here.
  */
  </style>