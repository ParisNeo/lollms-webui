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
        @change="handleRadioChange"
        class="text-blue-500 focus:ring-2 focus:ring-blue-200"
        :aria-checked="selectedValue === option.value.toString()"
        role="radio"
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
      type: String, // Ensure this matches the expected type of your options' values
      default: '0', // Ensure the default is a string to match the value type
    },
  },
  data() {
    return {
      selectedValue: this.defaultValue,
    };
  },
  computed: {
    selectedLabel() {
      const selectedOption = this.radioOptions.find(option => option.value === this.selectedValue);
      return selectedOption ? selectedOption.label : '';
    },
  },
  watch: {
    selectedValue(newValue, oldValue) {
      // Perform any side effect here if needed
      this.$emit('radio-selected', newValue);
    },
  },
  methods: {
    handleRadioChange() {
      // Now, this method might be redundant unless you have specific logic here
      // Otherwise, consider removing it and handle changes through the watcher or directly via v-model binding
    },
  },
};
</script>
