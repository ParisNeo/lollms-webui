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
              <span class="font-bold">{{ displayName(choice) }}</span><br>
              <span class="text-xs text-gray-500" v-if="choice.size">{{ formatSize(choice.size) }}</span>
              <button v-if="can_remove" @click="removeChoice(choice, index)" class="ml-2 text-red-500 hover:text-red-600">
                X
              </button>              
            </li>
          </ul>
        </div>
        <div class="mt-4" v-if="showInput">
          <input v-model="newFilename" placeholder="Enter a filename" class="border border-gray-300 p-2 rounded-lg w-full">
          <button @click="addNewFilename" class="mt-2 py-2 px-4 bg-green-500 hover:bg-green-600 text-white rounded-lg transition duration-300">
            Add
          </button>
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
          <button
            @click="toggleInput"
            class="py-2 px-4 ml-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg transition duration-300"
          >
            Add New
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
      default: false,
      required: false,
    },
    can_remove: {
      type: Boolean,
      default: false,
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
      showInput: false, // Control the visibility of the input box
      newFilename: '', // Store the new filename
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
      this.$emit("choice-validated", this.selectedChoice);
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
    toggleInput() {
      // Toggle the visibility of the input box
      this.showInput = !this.showInput;
    },
    addNewFilename() {
      // Add the new filename to the choices array
      const newChoice = this.newFilename.trim();
      if (newChoice !== '') {
        this.choices.push(newChoice);
        this.newFilename = ''; // Clear the input field
        this.selectChoice(newChoice); // Select the newly added filename
      }
      this.showInput = false;
    },
    removeChoice(choice, index) {
      this.choices.splice(index, 1); // Remove the choice from the array
      if (choice === this.selectedChoice) {
        this.selectedChoice = null; // Clear the selected choice if it was removed
      }
      this.$emit("choice-removed", choice); // Emit a custom event to notify the parent component
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
