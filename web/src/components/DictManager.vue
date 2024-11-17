<template>
    <div class="max-w-4xl mx-auto p-4">
      <div class="flex flex-col sm:flex-row mb-4 gap-2">
        <input
          type="text"
          v-model="newKey"
          :placeholder="keyName"
          @keyup.enter="addItem"
          class="flex-grow px-4 py-2 border border-gray-300 rounded dark:bg-gray-700 dark:text-white text-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
        <input
          type="text"
          v-model="newValue"
          :placeholder="valueName"
          @keyup.enter="addItem"
          class="flex-grow px-4 py-2 border border-gray-300 rounded dark:bg-gray-700 dark:text-white text-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
        <button @click="addItem" class="bg-blue-500 text-white px-6 py-2 rounded hover:bg-blue-600 text-lg transition duration-300 ease-in-out">Add</button>
      </div>
      <ul class="space-y-4" v-if="Object.keys(modelValue).length > 0">
        <li
          v-for="(value, key) in modelValue"
          :key="key"
          class="flex flex-col sm:flex-row items-center p-4 bg-white dark:bg-gray-800 rounded-lg shadow-md hover:shadow-lg transition duration-300 ease-in-out"
          :class="{ 'bg-gray-100 dark:bg-gray-700': draggingKey === key }"
        >
          <div class="flex-grow mb-2 sm:mb-0 sm:mr-4 w-full sm:w-auto">
            <label :for="'key-' + key" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">{{ keyName }}</label>
            <input
              :id="'key-' + key"
              :value="key"
              @input="updateKey(key, $event.target.value)"
              class="w-full px-3 py-2 border border-gray-300 rounded dark:bg-gray-600 dark:text-white text-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
          </div>
          <div class="flex-grow mb-2 sm:mb-0 sm:mr-4 w-full sm:w-auto">
            <label :for="'value-' + key" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">{{ valueName }}</label>
            <input
              :id="'value-' + key"
              :value="value"
              @input="updateValue(key, $event.target.value)"
              class="w-full px-3 py-2 border border-gray-300 rounded dark:bg-gray-600 dark:text-white text-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
          </div>
          <div class="flex items-center space-x-2">
            <button
              @click="removeItem(key)"
              class="text-red-500 hover:text-red-700 p-2 rounded-full hover:bg-red-100 dark:hover:bg-red-900 transition duration-300 ease-in-out"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd" />
              </svg>
            </button>
            <button
              @click="moveUp(key)"
              class="bg-gray-200 dark:bg-gray-600 hover:bg-gray-300 dark:hover:bg-gray-500 p-2 rounded-full transition duration-300 ease-in-out"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M14.707 12.707a1 1 0 01-1.414 0L10 9.414l-3.293 3.293a1 1 0 01-1.414-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 010 1.414z" clip-rule="evenodd" />
              </svg>
            </button>
            <button
              @click="moveDown(key)"
              class="bg-gray-200 dark:bg-gray-600 hover:bg-gray-300 dark:hover:bg-gray-500 p-2 rounded-full transition duration-300 ease-in-out"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
              </svg>
            </button>
          </div>
        </li>
      </ul>
      <div class="mt-6" v-if="Object.keys(modelValue).length > 0">
        <button @click="removeAll" class="bg-red-500 text-white px-6 py-2 rounded hover:bg-red-600 text-lg transition duration-300 ease-in-out">Remove All</button>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    name: 'DictionaryManager',
    props: {
      modelValue: {
        type: Object,
        default: () => ({}),
      },
      keyName: {
        type: String,
        default: 'Key',
      },
      valueName: {
        type: String,
        default: 'Value',
      },
    },
    emits: ['update:modelValue', 'change'],
    data() {
      return {
        newKey: '',
        newValue: '',
        draggingKey: null,
      };
    },
    methods: {
      addItem() {
        if (this.newKey.trim()) {
          const updatedDict = { ...this.modelValue };
          updatedDict[this.newKey.trim()] = this.newValue;
          this.$emit('update:modelValue', updatedDict);
          this.$emit('change');
          this.newKey = '';
          this.newValue = '';
        }
      },
      removeItem(key) {
        const updatedDict = { ...this.modelValue };
        delete updatedDict[key];
        this.$emit('update:modelValue', updatedDict);
        this.$emit('change');
      },
      removeAll() {
        this.$emit('update:modelValue', {});
        this.$emit('change');
      },
      updateKey(oldKey, newKey) {
        if (newKey.trim() && newKey !== oldKey) {
          const updatedDict = { ...this.modelValue };
          updatedDict[newKey.trim()] = updatedDict[oldKey];
          delete updatedDict[oldKey];
          this.$emit('update:modelValue', updatedDict);
          this.$emit('change');
        }
      },
      updateValue(key, newValue) {
        const updatedDict = { ...this.modelValue };
        updatedDict[key] = newValue;
        this.$emit('update:modelValue', updatedDict);
        this.$emit('change');
      },
      moveUp(key) {
        const keys = Object.keys(this.modelValue);
        const index = keys.indexOf(key);
        if (index > 0) {
          const updatedDict = {};
          keys.forEach((k, i) => {
            if (i === index - 1) {
              updatedDict[key] = this.modelValue[key];
            }
            if (k !== key) {
              updatedDict[k] = this.modelValue[k];
            }
          });
          this.$emit('update:modelValue', updatedDict);
          this.$emit('change');
        }
      },
      moveDown(key) {
        const keys = Object.keys(this.modelValue);
        const index = keys.indexOf(key);
        if (index < keys.length - 1) {
          const updatedDict = {};
          keys.forEach((k, i) => {
            if (k !== key) {
              updatedDict[k] = this.modelValue[k];
            }
            if (i === index + 1) {
              updatedDict[key] = this.modelValue[key];
            }
          });
          this.$emit('update:modelValue', updatedDict);
          this.$emit('change');
        }
      },
    },
  };
  </script>
  