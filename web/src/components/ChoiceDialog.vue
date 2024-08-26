<template>
  <transition name="fade">
    <div v-if="show" class="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-20">
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl p-6 w-96 max-w-md">
        <h2 class="text-2xl font-bold mb-4 text-gray-800 dark:text-white flex items-center">
          <svg class="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01"></path>
          </svg>
          {{ title }}
        </h2>
        <div class="h-48 bg-gray-100 dark:bg-gray-700 rounded-lg mb-4 overflow-y-auto scrollbar-thin scrollbar-thumb-gray-400 scrollbar-track-gray-200 dark:scrollbar-thumb-gray-600 dark:scrollbar-track-gray-800">
          <ul>
            <li
              v-for="(choice, index) in choices"
              :key="index"
              class="py-2 px-4 hover:bg-gray-200 dark:hover:bg-gray-600 transition duration-150 ease-in-out"
            >
              <div class="flex items-center justify-between">
                <div class="flex-grow">
                  <span v-if="!choice.isEditing" @click="selectChoice(choice)" :class="{'font-semibold': choice === selectedChoice}" class="text-gray-800 dark:text-white cursor-pointer">
                    {{ displayName(choice) }}
                  </span>
                  <input
                    v-else
                    v-model="choice.editName"
                    @blur="finishEditing(choice)"
                    @keyup.enter="finishEditing(choice)"
                    class="bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded px-2 py-1 text-sm"
                    autofocus
                  >
                  <span v-if="choice.size" class="text-xs text-gray-500 dark:text-gray-400 ml-2">{{ formatSize(choice.size) }}</span>
                </div>
                <div class="flex items-center">
                  <button @click="editChoice(choice)" class="text-blue-500 hover:text-blue-600 mr-2">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"></path>
                    </svg>
                  </button>
                  <button v-if="can_remove" @click="removeChoice(choice, index)" class="text-red-500 hover:text-red-600">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                    </svg>
                  </button>
                </div>
              </div>
            </li>
          </ul>
        </div>
        <div class="flex flex-col mb-4" v-if="showInput">
          <input
            v-model="newFilename"
            placeholder="Enter a filename"
            class="border border-gray-300 dark:border-gray-600 p-2 rounded-lg w-full mb-2 bg-white dark:bg-gray-700 text-gray-800 dark:text-white"
          >
          <button @click="addNewFilename" class="bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded-lg transition duration-300">
            Add
          </button>
        </div>
        <div class="flex justify-between">
          <button
            @click="closeDialog"
            class="bg-gray-300 hover:bg-gray-400 text-gray-800 font-bold py-2 px-4 rounded-lg transition duration-300"
          >
            Cancel
          </button>
          <button
            @click="validateChoice"
            :disabled="!selectedChoice"
            :class="{
              'bg-blue-500 hover:bg-blue-600': selectedChoice,
              'bg-gray-400 cursor-not-allowed': !selectedChoice
            }"
            class="text-white font-bold py-2 px-4 rounded-lg transition duration-300"
          >
            Validate
          </button>
          <button
            @click="toggleInput"
            class="bg-green-500 hover:bg-green-600 text-white font-bold py-2 px-4 rounded-lg transition duration-300"
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
      showInput: false,
      newFilename: '',
    };
  },
  methods: {
    displayName(choice) {
      if (typeof choice === 'string') {
        return choice;
      } else if (choice && choice.name) {
        return choice.name;
      } else {
        return ''; 
      }
    },
    selectChoice(choice) {
      this.selectedChoice = choice;
      this.$emit("choice-selected", choice);
    },
    closeDialog() {
      this.$emit("close-dialog");
    },
    validateChoice() {
      this.$emit("choice-validated", this.selectedChoice);
    },
    formatSize(size) {
      const units = ['bytes', 'KB', 'MB', 'GB'];
      let i = 0;
      while (size >= 1024 && i < units.length - 1) {
        size /= 1024;
        i++;
      }
      return `${size.toFixed(2)} ${units[i]}`;
    },
    toggleInput() {
      this.showInput = !this.showInput;
    },
    addNewFilename() {
      const newChoice = this.newFilename.trim();
      if (newChoice !== '') {
        this.choices.push({ name: newChoice, isEditing: false });
        this.newFilename = '';
        this.selectChoice(this.choices[this.choices.length - 1]);
      }
      this.showInput = false;
    },
    removeChoice(choice, index) {
      this.choices.splice(index, 1);
      if (choice === this.selectedChoice) {
        this.selectedChoice = null;
      }
      this.$emit("choice-removed", choice);
    },
    editChoice(choice) {
      choice.isEditing = true;
      choice.editName = this.displayName(choice);
    },
    finishEditing(choice) {
      if (typeof choice === 'string') {
        const index = this.choices.indexOf(choice);
        if (index !== -1) {
          this.choices[index] = choice.editName;
        }
      } else {
        choice.name = choice.editName;
      }
      choice.isEditing = false;
      delete choice.editName;
    },
  },
};
</script>

<style scoped>
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s;
}
.fade-enter, .fade-leave-to {
  opacity: 0;
}
</style>
