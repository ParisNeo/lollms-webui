<template>
    <div class="flex space-x-4">
      <label
        v-for="(option, index) in radioOptions"
        :key="option.value"
        class="flex items-center space-x-2"
      >
        <input
          type="radio"
          :value="option.value"
          v-model="selectedValue"
          @change="handleRadioChange(index)"
          class="text-blue-500 focus:ring-2 focus:ring-blue-200"
        />
        <span class="text-gray-700">{{ option.label }}</span>
      </label>
    </div>
  </template>
  
  <script>
  export default {
    props: {
      radioOptions: {
        type: Array,
        required: true,
      },
      defaultValue: {
        type: String, // Change the type to match your default value type
        default: 0, // Set the default value here
      },
    },
    data() {
      return {
        selectedValue: this.defaultValue, // Set the default value to the defaultValue prop
      };
    },
    methods: {
      handleRadioChange(index) {
        if (this.selectedValue !== null) {
          this.$emit('radio-selected', this.selectedValue, index);
        }
      },
    },
  };
  </script>
  