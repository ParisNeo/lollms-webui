<template>
  <div class="w-full h-auto overflow-y-auto scrollbar-thin scrollbar-track-bg-light-tone scrollbar-thumb-bg-light-tone-panel hover:scrollbar-thumb-primary dark:scrollbar-track-bg-dark-tone dark:scrollbar-thumb-bg-dark-tone-panel dark:hover:scrollbar-thumb-primary active:scrollbar-thumb-secondary" 
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
    ui: {
      handler(newVal) {
        this.$nextTick(() => {
          this.renderAndExecuteScripts(newVal);
        });
      },
      immediate: true
    }
  },
  methods: {
    renderAndExecuteScripts(content) {
      // Clear previous content
      this.$refs.ui.innerHTML = '';

      // Create a temporary container
      const temp = document.createElement('div');
      temp.innerHTML = content;

      // Function to execute a single script
      const executeScript = (script) => {
        return new Promise((resolve) => {
          const newScript = document.createElement('script');
          
          if (script.src) {
            // External script
            newScript.src = script.src;
            newScript.onload = resolve;
          } else {
            // Inline script
            newScript.textContent = script.textContent;
          }
          
          // Copy other attributes
          Array.from(script.attributes).forEach(attr => {
            if (attr.name !== 'src') {
              newScript.setAttribute(attr.name, attr.value);
            }
          });

          // Replace the old script with the new one
          script.parentNode.replaceChild(newScript, script);
          
          if (!script.src) {
            // For inline scripts, resolve immediately
            resolve();
          }
        });
      };

      // Execute scripts sequentially
      const executeScripts = async () => {
        const scripts = temp.querySelectorAll('script');
        for (let script of scripts) {
          await executeScript(script);
        }
      };

      // Render content and execute scripts
      this.$refs.ui.appendChild(temp);
      executeScripts();
    }
  }
};
</script>

<style>
.cursor-pointer {
  cursor: pointer;
}
</style>
