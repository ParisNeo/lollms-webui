<template>
  <div>
    <div class="flex mb-4">
      <input
        type="text"
        v-model="newItem"
        :placeholder="placeholder"
        @keyup.enter="addItem"
        class="flex-grow mr-4 px-4 py-2 border border-gray-300 rounded dark:bg-gray-600 text-lg"
      >
      <button @click="addItem" class="bg-blue-500 text-white px-6 py-2 rounded hover:bg-blue-600 text-lg">Add</button>
    </div>
    <ul class="list-none" v-if="modelValue.length > 0">
      <li
        v-for="(item, index) in modelValue"
        :key="index"
        class="flex items-center mb-2 relative"
        :class="{ 'bg-gray-200': draggingIndex === index }"
      >
        <span class="flex-grow text-xl">{{ item }}</span>
        <div class="flex items-center">
          <button
            @click="removeItem(index)"
            class="text-red-500 hover:text-red-700 p-2"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd" />
            </svg>
          </button>
          <button
            v-if="index > 0"
            @click="moveUp(index)"
            class="bg-gray-300 hover:bg-gray-400 p-2 rounded mr-2"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M14.707 12.707a1 1 0 01-1.414 0L10 9.414l-3.293 3.293a1 1 0 01-1.414-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 010 1.414z" clip-rule="evenodd" />
            </svg>
          </button>
          <button
            v-if="index < modelValue.length - 1"
            @click="moveDown(index)"
            class="bg-gray-300 hover:bg-gray-400 p-2 rounded"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
            </svg>
          </button>
        </div>
        <div
          v-if="draggingIndex === index"
          class="absolute top-0 left-0 w-full h-full bg-gray-200 opacity-50 cursor-move"
          @mousedown="startDragging(index)"
          @mousemove="dragItem(index)"
          @mouseup="stopDragging"
        ></div>
      </li>
    </ul>
    <div class="mt-4" v-if="modelValue.length > 0">
      <button @click="removeAll" class="bg-red-500 text-white px-6 py-2 rounded hover:bg-red-600 text-lg">Remove All</button>
    </div>
  </div>
</template>

<script>
// Script remains unchanged
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
    moveUp(index) {
      if (index > 0) {
        const updatedList = [...this.modelValue];
        const itemToMove = updatedList.splice(index, 1)[0];
        updatedList.splice(index - 1, 0, itemToMove);
        this.$emit('update:modelValue', updatedList);
        this.$emit('change');
      }
    },
    moveDown(index) {
      if (index < this.modelValue.length - 1) {
        const updatedList = [...this.modelValue];
        const itemToMove = updatedList.splice(index, 1)[0];
        updatedList.splice(index + 1, 0, itemToMove);
        this.$emit('update:modelValue', updatedList);
        this.$emit('change');
      }
    },
  },
};
</script>