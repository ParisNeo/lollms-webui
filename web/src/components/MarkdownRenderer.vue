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
    let discussion_id = 0
    let message_id = 0

    let btn_exec_txt = (lang=='python' || lang=='bash') ?'<button class="px-2 py-1 ml-10 mb-2 text-left p-2 text-sm font-medium bg-bg-dark-tone-panel dark:bg-bg-dark-tone rounded-lg hover:bg-primary dark:hover:bg-primary text-white text-xs transition-colors duration-200">' +
      '<span class="mr-1" id="exec-btn_' +
      id +
      '" onclick="executeCode(' +
      id + ',' + discussion_id + ',' + message_id + ',`' + lang +
      '`)">Execute</span>'+
      '</button>':''
    let btn_open_in_vs_code_txt = (lang=='python' || lang=='bash') ?'<button class="px-2 py-1 ml-10 mb-2 text-left p-2 text-sm font-medium bg-bg-dark-tone-panel dark:bg-bg-dark-tone rounded-lg hover:bg-primary dark:hover:bg-primary text-white text-xs transition-colors duration-200">' +
      '<span class="mr-1" id="exec-btn_' +
      id + '5' +
      '" onclick="openInVsCode(' +
      id + '5,' + discussion_id + ',' + message_id + ',`' + lang +
      '`)">Show in vs code</span>'+
      '</button>':''

      let btn_open_folder_txt = (lang=='python' || lang=='bash') ?'<button class="px-2 py-1 ml-10 mb-2 text-left p-2 text-sm font-medium bg-bg-dark-tone-panel dark:bg-bg-dark-tone rounded-lg hover:bg-primary dark:hover:bg-primary text-white text-xs transition-colors duration-200">' +
      '<span class="mr-1" id="exec-btn_' +
      id + '6' +
      '" onclick="openFolder(' +
      id + '6,' + discussion_id + ',' + message_id + ',`' + lang +
      '`)">Open folder</span>'+
      '</button>':''


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
          btn_exec_txt +
          btn_open_in_vs_code_txt +
          
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

      btn_open_in_vs_code_txt +

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
hljs.configure({ languages: ['bash'] }); // Set bash as the default language

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
      function executeCode(id, discussion_id, message_id, lang) {
        const codeElement = document.getElementById('code_' + id);
        const codeExecElement = document.getElementById('code_exec_' + id);
        const preExecElement = document.getElementById('pre_exec_' + id);
        
        const code = codeElement.innerText
        const json = JSON.stringify({ 'code': code, 'discussion_id': discussion_id, 'message_id':message_id, 'language': lang})   
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
          preExecElement.classList.remove('hidden');
          codeExecElement.innerHTML = jsonData.output
        })
        .catch(error => {
          // Handle any errors that occurred during the fetch process
          console.error('Fetch error:', error);
        });

      }
      function openInVsCode(id, discussion_id, message_id, lang) {
        const codeElement = document.getElementById('code_' + id);
        const codeExecElement = document.getElementById('code_exec_' + id);
        const preExecElement = document.getElementById('pre_exec_' + id);
        
        const code = codeElement.innerText
        const json = JSON.stringify({ 'code': code, 'discussion_id': discussion_id, 'message_id':message_id, 'language': lang})   
        console.log(json)     
        fetch('http://localhost:9600/open_in_vs_code', {
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
          codeExecElement.innerHTML = jsonData.output
        })
        .catch(error => {
          // Handle any errors that occurred during the fetch process
          console.error('Fetch error:', error);
        });

      }
      function openFolder(id, discussion_id, message_id, lang) {
        const codeElement = document.getElementById('code_' + id);
        const codeExecElement = document.getElementById('code_exec_' + id);
        const preExecElement = document.getElementById('pre_exec_' + id);
        
        const code = codeElement.innerText
        const json = JSON.stringify({ 'code': code, 'discussion_id': discussion_id, 'message_id':message_id, 'language': lang})   
        console.log(json)     
        fetch('http://localhost:9600/open_folder', {
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
          codeExecElement.innerHTML = jsonData.output
        })
        .catch(error => {
          // Handle any errors that occurred during the fetch process
          console.error('Fetch error:', error);
        });

      }
      
      `;
    script.async = true; // Set to true if the script should be loaded asynchronously
    document.body.appendChild(script);
    if(this.markdownText){
      this.renderedMarkdown = markdownIt.render(this.markdownText);
    }
    else{
      this.renderedMarkdown = "";
    }
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
