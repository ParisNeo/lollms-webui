<template>
  <div>
    <div v-html="renderedMarkdown" class=""></div>
  </div>
</template>

<script>
import { nextTick } from 'vue'
import feather from 'feather-icons'
import MarkdownIt from 'markdown-it';
import emoji from 'markdown-it-emoji';
import 'highlight.js/styles/tomorrow-night-blue.css'
//import 'highlight.js/styles/tokyo-night-dark.css'
import hljs from 'highlight.js';


const markdownIt = new MarkdownIt('commonmark', {
  html: false,
  xhtmlOut: true,
  breaks: true,
  linkify: true,
  typographer: true,
  highlight: (str, lang) => {

    if (lang && hljs.getLanguage(lang)) {
      try {

        return (
          '<pre class="hljs p-4 overflow-x-auto shadow-lg scrollbar-thin scrollbar-track-bg-light-tone scrollbar-thumb-bg-light-tone-panel hover:scrollbar-thumb-primary dark:scrollbar-track-bg-dark-tone dark:scrollbar-thumb-bg-dark-tone-panel dark:hover:scrollbar-thumb-primary active:scrollbar-thumb-secondary">'+
      '<code>' +
          hljs.highlight(str, { language: lang }).value +
          '</code></pre>'
        );

      } catch (__) { }
    }
    return (
      '<pre class="hljs p-4 overflow-x-auto shadow-lg scrollbar-thin scrollbar-track-bg-light-tone scrollbar-thumb-bg-light-tone-panel hover:scrollbar-thumb-primary dark:scrollbar-track-bg-dark-tone dark:scrollbar-thumb-bg-dark-tone-panel dark:hover:scrollbar-thumb-primary active:scrollbar-thumb-secondary">'+
      '<code>' +
      markdownIt.utils.escapeHtml(str) +
      '</code></pre>'
    );
  }
}).use(emoji);

export default {
  name: 'MarkdownRenderer',
  props: {
    markdownText: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      renderedMarkdown: ''
    };
  },
  mounted() {
 
    this.renderedMarkdown = markdownIt.render(this.markdownText);
    nextTick(() => {
      feather.replace()

    })
  },
  methods: {
    copyContentToClipboard() {

      navigator.clipboard.writeText(theCode);
    },
  },
  watch: {
    markdownText(newText) {

      this.renderedMarkdown = markdownIt.render(newText);
      nextTick(() => {
        feather.replace()

      })
    }
  }
};
</script>
  
