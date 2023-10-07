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
              :class="{'selected-choice': choice === selectedChoice}"
              class="py-2 px-4 cursor-pointer hover:bg-gray-200 dark:hover:bg-gray-700"
            >
              <span class="font-bold"> {{ displayName(choice) }} </span><br>
              <span class="text-xs text-gray-500" v-if="choice.size"> {{ this.formatSize(choice.size) }}</span>
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
            :class="{
              'bg-gray-400 cursor-not-allowed': !selectedChoice,
              'bg-blue-500 hover:bg-blue-600': selectedChoice,
              'text-white': selectedChoice,
              'text-gray-500': !selectedChoice,
            }"
            :disabled="!selectedChoice"
            class="py-2 px-4 rounded-lg transition duration-300"
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
  data() {
    return {
      selectedChoice: null,
    };
  },
  methods: {
    displayName(choice) {
      console.log("choice:",choice)
      if (typeof choice === 'string') {
        return choice;
      } else if (choice && choice.name) {
        return choice.name;
      } else {
        return ''; 
      }
    },
    selectChoice(choice) {
      this.selectedChoice = choice; // Update the selectedChoice when a choice is clicked
      this.$emit("choice-selected", choice);
    },
    closeDialog() {
      this.$emit("close-dialog");
    },
    validateChoice() {
      // Perform validation if needed
      this.$emit("choice-validated");
    },
    formatSize(size) {
      if (size < 1024) {
        return size + " bytes";
      } else if (size < 1024 * 1024) {
        return (size / 1024).toFixed(2) + " KB";
      } else if (size < 1024 * 1024 * 1024) {
        return (size / (1024 * 1024)).toFixed(2) + " MB";
      } else {
        return (size / (1024 * 1024 * 1024)).toFixed(2) + " GB";
      }
    },
  },
};
</script>

<style>
/* ... (unchanged) */
.selected-choice {
  background-color: #bde4ff; /* Change this color as per your preference */
}
</style>
