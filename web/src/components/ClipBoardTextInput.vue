<template>
  <div class="flex items-center space-x-2">
    <!-- Render the slider if useSlider is true -->
    <input
      v-if="!useSlider"
      :value="inputValue"
      :type="inputType"
      :placeholder="placeholderText"
      @input="handleInput"
      @paste="handlePaste"
      class="flex-1 px-4 py-2 text-lg dark:bg-gray-600 border border-gray-300 rounded-md focus:outline-none focus:ring focus:border-blue-500"
    />
    <input
      v-else
      type="range"
      :value="parseInt(inputValue)"
      :min="minSliderValue"
      :max="maxSliderValue"
      @input="handleSliderInput"
      class="flex-1 px-4 py-2 text-lg border dark:bg-gray-600 border-gray-300 rounded-md focus:outline-none focus:ring focus:border-blue-500"
    />
    <button
      @click="pasteFromClipboard"
      class="p-2 bg-blue-500 dark:bg-gray-600 text-white rounded-md hover:bg-blue-600 focus:outline-none focus:ring focus:border-blue-300"
    >
      <i data-feather="clipboard"></i>
    </button>
    <!-- File type button -->
    <button
      v-if="inputType === 'file'"
      @click="openFileInput"
      class="p-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 focus:outline-none focus:ring focus:border-blue-300"
    >
      <i data-feather="upload"></i>
    </button>

    <!-- Hidden file input -->
    <input
      v-if="inputType === 'file'"
      ref="fileInput"
      type="file"
      style="display: none"
      :accept="fileAccept"
      @change="handleFileInputChange"
    />
    
  </div>
</template>

<script>
import feather from "feather-icons";
import { nextTick } from "vue";

export default {
  props: {
    value: String, // Custom v-model prop to receive the input value
    inputType: {
      type: String,
      default: "text",
      validator: (value) =>
        ["text", "email", "password", "file", "path", "integer", "float"].includes(
          value
        ),
    },
    fileAccept: String, // Prop to specify the accepted file types
  },
  data() {
    return {
      inputValue: this.value,
      placeholderText: this.getPlaceholderText(),
    };
  },
  watch: {
    value(newVal) {
      // Watch for changes from parent component to keep inputValue in sync
      console.log("Changing value to ", newVal)
      this.inputValue = newVal;
    },
  },
  mounted() {
    nextTick(() => {
      feather.replace();
    });
    console.log("Changing value to ", this.value)
    this.inputValue = this.value;
  },
  methods: {
    handleSliderInput(event) {
      this.inputValue = event.target.value;
      this.$emit("input", event.target.value);
    },
    getPlaceholderText() {
      switch (this.inputType) {
        case "text":
          return "Enter text here";
        case "email":
          return "Enter your email";
        case "password":
          return "Enter your password";
        case "file":
        case "path":
          return "Choose a file";
        case "integer":
          return "Enter an integer";
        case "float":
          return "Enter a float";
        default:
          return "Enter value here";
      }
    },
    handleInput(event) {
      if (this.inputType === "integer") {
        const sanitizedValue = event.target.value.replace(/[^0-9]/g, "");
        this.inputValue = sanitizedValue;
      }
      console.log("handling input : ", event.target.value)
      this.$emit('input', event.target.value)
    },    
    async pasteFromClipboard() {
      try {
        const text = await navigator.clipboard.readText();
        this.handleClipboardData(text);
      } catch (error) {
        console.error("Failed to read from clipboard:", error);
        // Handle the error gracefully, e.g., show a message to the user
      }
    },
    handlePaste(event) {
      const text = event.clipboardData.getData("text");
      this.handleClipboardData(text);
    },
    handleClipboardData(text) {
      switch (this.inputType) {
        case "email":
          this.inputValue = this.isValidEmail(text) ? text : "";
          break;
        case "password":
          // Here, you can add validation for password strength if needed
          this.inputValue = text;
          break;
        case "file":
        case "path":
          // For file and path types, you might not want to allow pasting directly
          // into the input field. You can handle this as per your requirements.
          this.inputValue = "";
          break;
        case "integer":
          this.inputValue = this.parseInteger(text);
          break;
        case "float":
          this.inputValue = this.parseFloat(text);
          break;
        default:
          this.inputValue = text;
          break;
      }
    },
    isValidEmail(value) {
      // Simple email validation using regex
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      return emailRegex.test(value);
    },
    parseInteger(value) {
      // Parse integer value or return empty if invalid
      const parsedValue = parseInt(value);
      return isNaN(parsedValue) ? "" : parsedValue;
    },
    parseFloat(value) {
      // Parse float value or return empty if invalid
      const parsedValue = parseFloat(value);
      return isNaN(parsedValue) ? "" : parsedValue;
    },
    openFileInput() {
      this.$refs.fileInput.click(); // Trigger the file input when the button is clicked
    },
    handleFileInputChange(event) {
      const file = event.target.files[0];
      if (file) {
        // Display the file path in the input field
        this.inputValue = file.name;
      }
    },
  },
};
</script>

<style>
/* Optional: You can add more custom styling here if needed */
</style>
