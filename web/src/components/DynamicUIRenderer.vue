<template>
  <div v-html="evaluatedCode">
  </div>
</template>

<script>
export default {
  props: {
    code: String, // The HTML/CSS/JavaScript code as a prop
  },
  data() {
    return {
      evaluatedCode: '', // Store the evaluated code
    };
  },
  watch: {
    code: {
      handler(newCode) {
        // Extract and evaluate script tags from the new code
        this.evaluateScriptTags(newCode);
      },
      immediate: true, // Trigger the handler immediately when the component is mounted
    },
  },
  methods: {
    evaluateScriptTags(code) {
      // Create a temporary div element to execute scripts
      const tempDiv = document.createElement('div');
      tempDiv.innerHTML = code;

      // Get all script elements within the div
      const scriptElements = tempDiv.querySelectorAll('script');

      // Loop through script elements and evaluate them
      scriptElements.forEach((script) => {
        const newScript = document.createElement('script');
        newScript.textContent = script.textContent;
        document.body.appendChild(newScript);
        document.body.removeChild(newScript);
      });

      // Set the evaluated code to the modified HTML
      this.evaluatedCode = tempDiv.innerHTML;
    },
  },
};
</script>

<style>
.cursor-pointer {
  cursor: pointer;
}
</style>
