<template>
    <div>
      <h2>IPython Console</h2>
      <textarea v-model="input"></textarea>
      <button @click="execute">Execute</button>
      <pre v-if="result">{{ result }}</pre>
    </div>
  </template>
  
  <script>
  import * as IPython from 'jupyter';
  
  export default {
    data() {
      return {
        input: '',
        result: '',
      };
    },
    mounted() {
      const widget = this.$refs.console;
      if (widget) {
        // Initialize the IPython console with the existing DOM node.
        IPython.Widget(widget);
        
        // Connect the console's output area to the textarea for reading/writing.
        widget.editor.getOutputArea().attachTo(this.$refs.input);
  
        // Listen for changes in the textarea.
        this.$watch('input', () => {
          if (this.input === '') return;
          this.execute();
        });
      }
    },
    methods: {
      execute() {
        const widget = this.$refs.console;
        const code = this.input;
  
        // Execute the code and display the results.
        widget.executeCode(code, null, (err, result) => {
          if (err) {
            console.error(err);
            this.result = '';
          } else {
            this.result = result;
          }
        });
      },
    },
  };
  </script>