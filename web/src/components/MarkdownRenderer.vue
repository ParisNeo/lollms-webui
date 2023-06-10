<template>
  <div class=" break-all ">
    <div v-html="renderedMarkdown" class=""></div>
  </div>
</template>

<script>
import { nextTick } from 'vue'
import feather from 'feather-icons'
import MarkdownIt from 'markdown-it';
import emoji from 'markdown-it-emoji';
//import 'highlight.js/styles/tomorrow-night-blue.css'
//import 'highlight.js/styles/tokyo-night-dark.css'
import hljs from 'highlight.js';



const markdownIt = new MarkdownIt('commonmark', {
  html: false,
  xhtmlOut: true,
  breaks: true,
  linkify: true,
  typographer: true,
  highlight: (str, lang) => {
    const language = hljs.highlight(str, { language: lang }).language

    const languageCapital = language.charAt(0).toUpperCase() + language.slice(1);


    if (lang && hljs.getLanguage(lang)) {
      try {


        return (
          '<div class="bg-bg-light-tone-panel dark:bg-bg-dark-tone-panel  p-2 rounded-lg shadow-sm ">' +
          languageCapital +

          '<pre class=" hljs  p-1 rounded-md  break-all  grid grid-cols-1 ">' +

          '<code class="overflow-x-auto break-all scrollbar-thin scrollbar-track-bg-light-tone scrollbar-thumb-bg-light-tone-panel hover:scrollbar-thumb-primary dark:scrollbar-track-bg-dark-tone dark:scrollbar-thumb-bg-dark-tone-panel dark:hover:scrollbar-thumb-primary active:scrollbar-thumb-secondary ">' +
          hljs.highlightAuto(str).value +
          '</code></pre>' + '</div>'
        );

      } catch (__) { }
    }

    return (
      '<div class="bg-bg-light-tone-panel dark:bg-bg-dark-tone-panel  p-2 rounded-lg shadow-sm ">' +
      languageCapital +

      '<pre class=" hljs  p-1 rounded-md  break-all  grid grid-cols-1 ">' +

      '<code class="overflow-x-auto break-all scrollbar-thin scrollbar-track-bg-light-tone scrollbar-thumb-bg-light-tone-panel hover:scrollbar-thumb-primary dark:scrollbar-track-bg-dark-tone dark:scrollbar-thumb-bg-dark-tone-panel dark:hover:scrollbar-thumb-primary active:scrollbar-thumb-secondary ">' +
      markdownIt.utils.escapeHtml(str) +
      '</code></pre>' + '</div>'
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
      renderedMarkdown: '',

    };
  },
  mounted() {

    this.renderedMarkdown = markdownIt.render(this.markdownText);
    nextTick(() => {
      feather.replace()

    })
  },
  created() {


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
    },

  },
  computed: {


  }
};
</script>
  
<style type='text/css'></style>