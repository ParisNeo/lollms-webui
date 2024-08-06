<template>
    <div>
      <div class="flex mb-2">
        <input
          type="text"
          v-model="newItem"
          :placeholder="placeholder"
          @keyup.enter="addItem"
          class="flex-grow mr-2 px-2 py-1 border border-gray-300 rounded dark:bg-gray-600"
        >
        <button @click="addItem" class="bg-blue-500 text-white px-4 py-1 rounded hover:bg-blue-600">Add</button>
      </div>
      <ul class="list-disc list-inside" v-if="modelValue.length > 0">
        <li
          v-for="(item, index) in modelValue"
          :key="index"
          class="flex items-center mb-1 relative"
          :class="{ 'bg-gray-200': draggingIndex === index }"
        >
          <span class="flex-grow">{{ item }}</span>
          <button
            @click="removeItem(index)"
            class="text-red-500 hover:text-red-700 ml-2"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
            </svg>
          </button>
          <div
            v-if="draggingIndex === index"
            class="absolute top-0 left-0 w-full h-full bg-gray-200 opacity-50 cursor-move"
            @mousedown="startDragging(index)"
            @mousemove="dragItem(index)"
            @mouseup="stopDragging"
          ></div>
          <div
            v-if="draggingIndex !== index && index > draggingIndex"
            class="absolute top-0 left-0 w-full h-full bg-gray-200 opacity-50 cursor-move"
            @mousedown="startDragging(index)"
            @mousemove="dragItem(index)"
            @mouseup="stopDragging"
          ></div>
          <div
            v-if="draggingIndex !== index && index < draggingIndex"
            class="absolute top-0 left-0 w-full h-full bg-gray-200 opacity-50 cursor-move"
            @mousedown="startDragging(index)"
            @mousemove="dragItem(index)"
            @mouseup="stopDragging"
          ></div>
        </li>
      </ul>
      <div class="mt-2" v-if="modelValue.length > 0">
        <button @click="removeAll" class="bg-red-500 text-white px-4 py-1 rounded hover:bg-red-600">Remove All</button>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    name: 'StringListManager',
    props: {
      modelValue: {
        type: Array,
        default: () => [],
      },
      placeholder: {
        type: String,
        default: 'Enter an item',
      },
    },
    emits: ['update:modelValue', 'change'],
    data() {
      return {
        newItem: '',
        draggingIndex: null,
      };
    },
    methods: {
      addItem() {
        if (this.newItem.trim()) {
          const updatedList = [...this.modelValue, this.newItem.trim()];
          this.$emit('update:modelValue', updatedList);
          this.$emit('change');
          this.newItem = '';
        }
      },
      removeItem(index) {
        const updatedList = this.modelValue.filter((_, i) => i !== index);
        this.$emit('update:modelValue', updatedList);
        this.$emit('change');
      },
      removeAll() {
        this.$emit('update:modelValue', []);
        this.$emit('change');
      },
      startDragging(index) {
        this.draggingIndex = index;
      },
      dragItem(index) {
        if (this.draggingIndex !== null) {
          const updatedList = [...this.modelValue];
          const draggedItem = updatedList.splice(this.draggingIndex, 1)[0];
          updatedList.splice(index, 0, draggedItem);
          this.$emit('update:modelValue', updatedList);
          this.$emit('change');
        }
      },
      stopDragging() {
        this.draggingIndex = null;
      },
    },
  };
  </script>
  
  