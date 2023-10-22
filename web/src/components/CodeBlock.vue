<template>
  <div class="bg-bg-light-tone-panel dark:bg-bg-dark-tone-panel p-2 rounded-lg shadow-sm">
    <div class="flex flex-row bg-bg-light-tone-panel dark:bg-bg-dark-tone-panel p-2 rounded-lg shadow-sm">
      <span>{{ language }}</span>
      <button @click="copyCode" title="copy"
              :class="isCopied ? 'bg-green-500' : 'bg-bg-dark-tone-panel dark:bg-bg-dark-tone'" 
              class="px-2 py-1 ml-2 text-left p-2 text-sm font-medium rounded-lg hover:bg-primary dark:hover:bg-primary text-white text-xs transition-colors duration-200">
        <i data-feather="copy"></i>
      </button>
      <button v-if="['python', 'shell', 'bash', 'cmd', 'powershell'].includes(language)" ref="btn_code_exec" @click="executeCode"  title="execute"
              class="px-2 py-1 ml-2 text-left p-2 text-sm font-medium bg-bg-dark-tone-panel dark:bg-bg-dark-tone rounded-lg hover:bg-primary dark:hover:bg-primary text-white text-xs transition-colors duration-200">
        <i data-feather="play-circle"></i>
      </button>
      <button v-if="['python'].includes(language)" @click="openFolder"  title="open code project folder"
              class="px-2 py-1 ml-2 text-left p-2 text-sm font-medium bg-bg-dark-tone-panel dark:bg-bg-dark-tone rounded-lg hover:bg-primary dark:hover:bg-primary text-white text-xs transition-colors duration-200">
        <i data-feather="folder"></i>
      </button>
    </div>
    <pre  class="hljs p-1 rounded-md break-all grid grid-cols-1">
      <code class="overflow-x-auto break-all scrollbar-thin scrollbar-track-bg-light-tone scrollbar-thumb-bg-light-tone-panel hover:scrollbar-thumb-primary dark:scrollbar-track-bg-dark-tone dark:scrollbar-thumb-bg-dark-tone-panel dark:hover:scrollbar-thumb-primary active:scrollbar-thumb-secondary" v-html="highlightedCode"></code>
    </pre>    
    <pre  class="hljs p-1 rounded-md break-all grid grid-cols-1" v-if="executionOutput">
      <div class="overflow-x-auto break-all scrollbar-thin scrollbar-track-bg-light-tone scrollbar-thumb-bg-light-tone-panel hover:scrollbar-thumb-primary dark:scrollbar-track-bg-dark-tone dark:scrollbar-thumb-bg-dark-tone-panel dark:hover:scrollbar-thumb-primary active:scrollbar-thumb-secondary">
        <div ref="execution_output" v-html="executionOutput"></div>
      </div>
    </pre>    
  </div>
</template>
<script>
import { nextTick } from 'vue'
import hljs from 'highlight.js'
import 'highlight.js/styles/tomorrow-night-blue.css';
import 'highlight.js/styles/tokyo-night-dark.css';

hljs.configure({ languages: [] }); // Reset languages
hljs.configure({ languages: ['bash'] }); // Set bash as the default language

hljs.highlightAll();
export default {
  props: {
    language: {
      type: String,
      required: true,
    },
    code: {
      type: String,
      required: true,
    },
    discussion_id: {
      type: [String, Number],
      required: true,
    },
    message_id: {
      type: [String, Number],
      required: true,
    },
  },
  data() {
    return {
      isCopied: false,
      executionOutput: '',  // new property
    };
  },
  computed: {
    highlightedCode() {
      let validLanguage;
      if (this.language === 'vue' || this.language === 'vue.js') {
        validLanguage = 'javascript';
      } else {
        validLanguage = hljs.getLanguage(this.language) ? this.language : 'plaintext';
      }
      const trimmedCode = this.code.trim(); // Remove leading and trailing whitespace
      return hljs.highlight(validLanguage, trimmedCode).value;
    },
  },
  methods: {
    copyCode() {
      this.isCopied = true;
      console.log("Copying code")
      const el = document.createElement('textarea');
      el.value = this.code;
      document.body.appendChild(el);
      el.select();
      document.execCommand('copy');
      document.body.removeChild(el);
      nextTick(() => {
          feather.replace()
      })
    },
    executeCode() {
      const json = JSON.stringify({ 'code': this.code, 'discussion_id': this.discussion_id, 'message_id': this.message_id, 'language': this.language})   
      console.log(json)     
      fetch('http://localhost:9600/execute_code', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: json
      }).then(response=>{
        // Parse the JSON data from the response body
        return response.json();
      })
      .then(jsonData => {
        // Now you can work with the JSON data
        console.log(jsonData);
        this.executionOutput = jsonData.output;
      })
      .catch(error => {
        // Handle any errors that occurred during the fetch process
        console.error('Fetch error:', error);
      });
    },
    openFolder() {
      const json = JSON.stringify({ 'discussion_id': this.discussion_id })   
      console.log(json)     
      fetch('http://localhost:9600/open_code_folder', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: json
      }).then(response=>{
        // Parse the JSON data from the response body
        return response.json();
      })
      .then(jsonData => {
        // Now you can work with the JSON data
        console.log(jsonData);
      })
      .catch(error => {
        // Handle any errors that occurred during the fetch process
        console.error('Fetch error:', error);
      });
    },
  },
};
</script>
