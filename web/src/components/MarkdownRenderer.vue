<template>
  <div class="break-all">
    <div v-html="renderedMarkdown" class="markdown-content"></div>
  </div>
</template>

<script>
import { nextTick } from 'vue';
import feather from 'feather-icons';
import MarkdownIt from 'markdown-it';
import emoji from 'markdown-it-emoji';
import anchor from 'markdown-it-anchor';
import implicitFigures from 'markdown-it-implicit-figures';
//import hljs from 'highlight.js/lib/core';
import 'highlight.js/styles/tomorrow-night-blue.css';
import 'highlight.js/styles/tokyo-night-dark.css';
import hljs  from 'highlight.js/lib/common';


import 'highlight.js/styles/tomorrow-night-blue.css';
import 'highlight.js/styles/tokyo-night-dark.css';
import attrs from 'markdown-it-attrs';

function generateUniqueId() {
  const timestamp = Date.now().toString();
  const randomSuffix = Math.floor(Math.random() * 1000).toString();
  return timestamp + randomSuffix;
}

const markdownIt = new MarkdownIt('commonmark', {
  html: true,
  xhtmlOut: true,
  breaks: true,
  linkify: true,
  typographer: true,
  highlight: (str, lang) => {
    let id = generateUniqueId();
    if (lang && hljs.getLanguage(lang)) {
      try {
        const highlightedCode = hljs.highlight(lang, str).value;
        return (
          '<div class="bg-bg-light-tone-panel dark:bg-bg-dark-tone-panel p-2 rounded-lg shadow-sm">' +
          lang +
          '<button class="px-2 py-1 ml-10 mb-2 text-left p-2 text-sm font-medium bg-bg-dark-tone-panel dark:bg-bg-dark-tone rounded-lg hover:bg-primary dark:hover:bg-primary text-white text-xs transition-colors duration-200">' +
          '<span class="mr-1" id="copy-btn_' +
          id +
          '" onclick="copyContentToClipboard(' +
          id +
          ')">Copy</span>' +
          '<span class="hidden text-xs text-green-500" id="copyed-btn_' +
          id +
          '" onclick="copyContentToClipboard(' +
          id +
          ')">Copied!</span>' +
          '</button>' +

          '<button class="px-2 py-1 ml-10 mb-2 text-left p-2 text-sm font-medium bg-bg-dark-tone-panel dark:bg-bg-dark-tone rounded-lg hover:bg-primary dark:hover:bg-primary text-white text-xs transition-colors duration-200">' +
          '<span class="mr-1" id="exec-btn_' +
          id +
          '" onclick="executeCode(' +
          id +
          ')">Execute</span>'+
          '</button>' +


          '<pre class="hljs p-1 rounded-md break-all grid grid-cols-1">' +
          '<code id="code_' +
          id +
          '" class="overflow-x-auto break-all scrollbar-thin scrollbar-track-bg-light-tone scrollbar-thumb-bg-light-tone-panel hover:scrollbar-thumb-primary dark:scrollbar-track-bg-dark-tone dark:scrollbar-thumb-bg-dark-tone-panel dark:hover:scrollbar-thumb-primary active:scrollbar-thumb-secondary">' +
          highlightedCode +
          '</code>' +
          '</pre>' +
          '<pre id="pre_exec_' +
          id + '" class="hljs p-1  hidden rounded-md break-all grid grid-cols-1  mt-2">' +
          'Execution output:<br>' +
          '<code id="code_exec_' +
          id +
          '" class="overflow-x-auto break-all scrollbar-thin scrollbar-track-bg-light-tone scrollbar-thumb-bg-light-tone-panel hover:scrollbar-thumb-primary dark:scrollbar-track-bg-dark-tone dark:scrollbar-thumb-bg-dark-tone-panel dark:hover:scrollbar-thumb-primary active:scrollbar-thumb-secondary">' +
          '</code>' +
          '</pre>' +

          '</div>'
        );
      } catch (error) {
        console.error(`Syntax highlighting failed for language '${lang}':`, error);
      }
    }
    let btn_exec_txt = lang=='python'?'<button class="px-2 py-1 ml-10 mb-2 text-left p-2 text-sm font-medium bg-bg-dark-tone-panel dark:bg-bg-dark-tone rounded-lg hover:bg-primary dark:hover:bg-primary text-white text-xs transition-colors duration-200">' +
      '<span class="mr-1" id="exec-btn_' +
      id +
      '" onclick="executeCode(' +
      id +
      ')">Execute</span>'+
      '</button>':''

    let codeString =
      '<div class="bg-bg-light-tone-panel dark:bg-bg-dark-tone-panel p-2 rounded-lg shadow-sm">' +
      lang +
      '<button class="px-2 py-1 ml-10 mb-2 text-left p-2 text-sm font-medium bg-bg-dark-tone-panel dark:bg-bg-dark-tone rounded-lg hover:bg-primary dark:hover:bg-primary text-white text-xs transition-colors duration-200">' +
      '<span class="mr-1" id="copy-btn_' +
      id +
      '" onclick="copyContentToClipboard(' +
      id +
      ')">Copy</span>' +
      '<span class="hidden text-xs text-green-500" id="copyed-btn_' +
      id +
      '" onclick="copyContentToClipboard(' +
      id +
      ')">Copied!</span>' +
      '</button>' +


      btn_exec_txt +

      '<pre class="hljs p-1 rounded-md break-all grid grid-cols-1">' +
      '<code id="code_' +
      id +
      '" class="overflow-x-auto break-all scrollbar-thin scrollbar-track-bg-light-tone scrollbar-thumb-bg-light-tone-panel hover:scrollbar-thumb-primary dark:scrollbar-track-bg-dark-tone dark:scrollbar-thumb-bg-dark-tone-panel dark:hover:scrollbar-thumb-primary active:scrollbar-thumb-secondary">' +
      hljs.highlightAuto(str).value +
      '</code>' +
      '<code id="code_exec_' +
      id +
      '" class="overflow-x-auto mt-2 hidden break-all scrollbar-thin scrollbar-track-bg-light-tone scrollbar-thumb-bg-light-tone-panel hover:scrollbar-thumb-primary dark:scrollbar-track-bg-dark-tone dark:scrollbar-thumb-bg-dark-tone-panel dark:hover:scrollbar-thumb-primary active:scrollbar-thumb-secondary">' +
      '</code>' +
      '</pre>' +
      '</div>';
    return codeString;
  },
  bulletListMarker: '-',
}).use(attrs).use(anchor).use(implicitFigures).use(emoji); // Add attrs plugin for adding attributes to elements


// ... register other languages


hljs.configure({ languages: [] }); // Reset languages
hljs.configure({ languages: ['javascript'] }); // Set JavaScript as the default language

markdownIt.renderer.rules.link_open = (tokens, idx, options, env, self) => {
  const token = tokens[idx];
  const hrefIndex = token.attrIndex('href');
  if (hrefIndex >= 0) {
    const hrefValue = token.attrs[hrefIndex][1];
    token.attrs[hrefIndex][1] = hrefValue;
    token.attrPush(['style', 'color: blue; font-weight: bold; text-decoration: underline;']);
  }
  return self.renderToken(tokens, idx, options);
};


// Define a custom rendering function for lists
const renderList = (tokens, idx, options, env, self) => {
  const token = tokens[idx];
  const listType = token.attrGet('type') || 'ul'; // Default to unordered list

  // Custom handling for unordered lists
  if (listType === 'ul') {
    // Add Tailwind CSS classes for unordered lists
    return '<ul class="list-disc ml-4">' + self.renderToken(tokens, idx, options) + '</ul>';
  }

  // Custom handling for ordered lists
  if (listType === 'ol') {
    // Add Tailwind CSS classes for ordered lists
    return '<ol class="list-decimal ml-4">' + self.renderToken(tokens, idx, options) + '</ol>';
  }

  // Fallback to the default renderer for other list types
  return self.renderToken(tokens, idx, options);
};

// Override the default list renderer with the custom function
markdownIt.renderer.rules.bullet_list_open = renderList;
markdownIt.renderer.rules.ordered_list_open = renderList;



export default {
  name: 'MarkdownRenderer',
  props: {
    markdownText: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      renderedMarkdown: '',
      isCopied: false,
    };
  },

  mounted() {
    const script = document.createElement('script');
    script.textContent = `

      // Your inline script code here
      function copyContentToClipboard(id) {
        console.log("copied");
        const codeElement = document.getElementById('code_' + id);
        const copybtnElement = document.getElementById('copy-btn_' + id);
        const copyedbtnElement = document.getElementById('copyed-btn_' + id);
        copybtnElement.classList.add('hidden');
        copyedbtnElement.classList.remove('hidden');
        const range = document.createRange();
        range.selectNode(codeElement);
        window.getSelection().removeAllRanges();
        window.getSelection().addRange(range);
        document.execCommand('copy');
        window.getSelection().removeAllRanges();
      }
      function executeCode(id) {
        const codeElement = document.getElementById('code_' + id);
        const codeExecElement = document.getElementById('code_exec_' + id);
        const preExecElement = document.getElementById('pre_exec_' + id);
        
        const code = codeElement.innerText
        const json = JSON.stringify({ 'code': code })   
        console.log(json)     
        fetch('http://localhost:9600/execute_python_code', {
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
          preExecElement.classList.remove('hidden');
          codeExecElement.innerText=jsonData.output
        })
        .catch(error => {
          // Handle any errors that occurred during the fetch process
          console.error('Fetch error:', error);
        });

      }
      `;
    script.async = true; // Set to true if the script should be loaded asynchronously
    document.body.appendChild(script);
    this.renderedMarkdown = markdownIt.render(this.markdownText);
    nextTick(() => {
      feather.replace();
    });
  },
  methods: {},
  watch: {
    markdownText(newText) {
      this.renderedMarkdown = markdownIt.render(newText);
      nextTick(() => {
        feather.replace();
      });
    },
  },
};
</script>

<style>
/* Include any additional styles you need */
ul {
  list-style-type: disc;
}

ol {
  list-style-type: decimal;
}
</style>
