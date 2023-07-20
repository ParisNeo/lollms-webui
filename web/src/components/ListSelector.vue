<!-- ChoiceDialog.vue -->
<template>
    <transition name="fade">
      <div v-if="show" class="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50">
        <div class="bg-white dark:bg-gray-800 rounded-lg p-6 w-96">
          <h2 class="text-xl font-semibold mb-4">{{ title }}</h2>
          <div class="h-48 overflow-y-auto">
            <ul>
              <li
                v-for="(choice, index) in choices"
                :key="index"
                @click="selectChoice(choice)"
                class="py-2 px-4 cursor-pointer hover:bg-gray-200 dark:hover:bg-gray-700"
              >
                {{ choice }}
              </li>
            </ul>
          </div>
          <div class="flex justify-end mt-4">
            <button
              @click="closeDialog"
              class="py-2 px-4 mr-2 bg-red-500 hover:bg-red-600 text-white rounded-lg transition duration-300"
            >
              Cancel
            </button>
            <button
              @click="validateChoice"
              class="py-2 px-4 bg-blue-500 hover:bg-blue-600 text-white rounded-lg transition duration-300"
            >
              Validate
            </button>
          </div>
        </div>
      </div>
    </transition>
  </template>
  
  <script>
  export default {
    props: {
      show: {
        type: Boolean,
        required: true,
      },
      title: {
        type: String,
        default: "Select an option",
      },
      choices: {
        type: Array,
        required: true,
      },
    },
    methods: {
      selectChoice(choice) {
        this.$emit("choice-selected", choice);
      },
      closeDialog() {
        this.$emit("close-dialog");
      },
      validateChoice() {
        // Perform validation if needed
        this.$emit("choice-validated");
      },
    },
  };
  </script>
  
  <style>
  .fade-enter-active,
  .fade-leave-active {
    transition: opacity 0.3s;
  }
  
  .fade-enter-from,
  .fade-leave-to {
    opacity: 0;
  }
  </style>
  