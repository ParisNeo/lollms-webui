<template>
  <div v-if="showPopup" class="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center">
    <div class="bg-white p-5 rounded-lg">
      <div class="flex flex-col">
        <button
          v-for="(option, index) in options"
          :key="index"
          @click="selectOption(index)"
          class="mb-2 last:mb-0 py-2 px-4 bg-blue-500 text-white rounded hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50"
        >
          {{ option }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      showPopup: false,
      options: [],
    };
  },
  methods: {
    show(options) {
      this.options = options;
      this.showPopup = true;
    },
    selectOption(index) {
      this.$emit('option-selected', index);
      this.showPopup = false;
    },
  },
};
</script>

<!-- No need for <style scoped> as we're using Tailwind CSS utility classes -->
