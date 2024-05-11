<template>
  <div class="w-full h-full overflow-y-auto scrollbar-thin scrollbar-track-bg-light-tone scrollbar-thumb-bg-light-tone-panel hover:scrollbar-thumb-primary dark:scrollbar-track-bg-dark-tone dark:scrollbar-thumb-bg-dark-tone-panel dark:hover:scrollbar-thumb-primary active:scrollbar-thumb-secondary" v-html="evaluatedCode" :key="componentKey">
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
      componentKey: 0,
    };
  },
  watch: {
    code: {
      handler(newCode) {
        // Extract and evaluate script tags from the new code
        console.log("Code changed")
        this.evaluateScriptTags(newCode);
        this.componentKey++;
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
      console.log("evaluated code: " + this.evaluatedCode)
    },
  },
};
</script>

<style>
.cursor-pointer {
  cursor: pointer;
}
</style>
