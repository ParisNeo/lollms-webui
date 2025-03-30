// src/components/ToggleSwitch.vue
<template>
  <label :for="id" class="relative inline-flex items-center cursor-pointer" :class="{ 'opacity-50 cursor-not-allowed': disabled }">
    <input
      type="checkbox"
      :id="id"
      :checked="checked"
      :disabled="disabled"
      @change="$emit('update:checked', $event.target.checked)"
      class="sr-only peer"
    >
    <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
    <!-- Optional: Add slot for text next to the toggle if needed -->
    <slot></slot>
  </label>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue';

defineProps({
  id: {
    type: String,
    required: true,
  },
  checked: {
    type: Boolean,
    default: false,
  },
  disabled: {
    type: Boolean,
    default: false,
  }
});

defineEmits(['update:checked']);
</script>

<style scoped>
/* Basic styling is done with Tailwind classes directly in the template.
   No additional scoped styles needed for this basic implementation. */
</style>