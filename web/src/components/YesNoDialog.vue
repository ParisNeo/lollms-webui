<template>
    <div v-if="show" class="fixed top-0 left-0 right-0 bottom-0 flex items-center justify-center bg-black bg-opacity-50">
      <div class="bg-bg-light dark:bg-bg-dark p-8 rounded-lg shadow-lg">
        <h3 class="text-lg font-medium">{{ message }}</h3>
        <div class="mt-4 flex justify-end">
          <button @click="hide(false)" class="bg-secondary text-white px-4 py-2 rounded-lg shadow-lg hover:bg-secondary-dark">
            No
          </button>
          <button @click="hide(true)" class="bg-secondary text-white px-4 py-2 rounded-lg shadow-lg hover:bg-secondary-dark ml-4">
            Yes
          </button>
        </div>
      </div>
    </div>
</template>
  
<script>
  export default {
    data() {
      return {
        show: false,
        message: "",
        resolve: null,
      };
    },
    methods: {
      hide(response) {
        this.show = false;
        if (this.resolve) {
          this.resolve(response);
          this.resolve = null;
        }
      },
      askQuestion(message) {
        return new Promise((resolve) => {
          this.message = message;
          this.show = true;
          this.resolve = resolve;
        });
      },
    },
  };
</script>
  