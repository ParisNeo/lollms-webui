<template>
  <div  class="w-full h-auto overflow-y-auto scrollbar-thin scrollbar-track-bg-light-tone scrollbar-thumb-bg-light-tone-panel hover:scrollbar-thumb-primary dark:scrollbar-track-bg-dark-tone dark:scrollbar-thumb-bg-dark-tone-panel dark:hover:scrollbar-thumb-primary active:scrollbar-thumb-secondary" 
        ref="ui">
  </div>
</template>

<script>
export default {
  props: {
    ui: {
            type: String,
            required: true,
            default: "",
        },
  },
  watch: {
    ui(newVal, oldVal) {
      console.log(`ui changed from ${oldVal} to ${newVal}`);
      // Add your custom logic here
      this.$nextTick(() => {
        this.evaluateScriptTags();
      });      
    },
  },
  data() {
    return {

    };
  },
  mounted(){
    this.$nextTick(() => {
      this.evaluateScriptTags();
    });
  },
  methods: {
    evaluateScriptTags() {
      console.log("evaluateScriptTags")
      // Create a temporary div element to execute scripts
      const tempDiv = document.createElement('div');
      tempDiv.innerHTML = this.ui;

      // Get all script elements within the div
      const scriptElements = tempDiv.querySelectorAll('script');

      // Loop through script elements and evaluate them
      scriptElements.forEach((script) => {
        const newScript = document.createElement('script');
        newScript.textContent = script.textContent;
        document.body.appendChild(newScript);
        document.body.removeChild(newScript);
      });

      // Set the evaluated ui to the modified HTML
      this.$refs.ui.innerHTML = tempDiv.innerHTML;
      console.log("this.$refs.ui.innerHTML")
      console.log(this.$refs.ui.innerHTML)
    },
  },
};
</script>

<style>
.cursor-pointer {
  cursor: pointer;
}
</style>
