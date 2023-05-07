<template>
    <div>
      <div v-html="renderedMarkdown" class=""></div>
    </div>
  </template>
  
  <script>
  import MarkdownIt from 'markdown-it';
  import emoji from 'markdown-it-emoji';
  import hljs from 'highlight.js';
  
  export default {
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
      const markdownIt = new MarkdownIt({
        highlight: (str, lang) => {
          if (lang && hljs.getLanguage(lang)) {
            try {
              return (
                '<pre class="hljs rounded-lg dark:bg-primary shadow-lg"><code>' +
                hljs.highlight(lang, str, true).value +
                '</code></pre>'
              );
            } catch (__) {}
          }
          return (
            '<pre class="hljs rounded-lg dark:bg-primary shadow-lg"><code>' +
            markdownIt.utils.escapeHtml(str) +
            '</code></pre>'
          );
        }
      }).use(emoji);
  
      this.renderedMarkdown = markdownIt.render(this.markdownText);
    },
    watch: {
      markdownText(newText) {
        const markdownIt = new MarkdownIt({
          highlight: (str, lang) => {
            if (lang && hljs.getLanguage(lang)) {
              try {
                return (
                  '<pre class="hljs rounded-lg dark:bg-primary shadow-lg"><code>' +
                  hljs.highlight(lang, str, true).value +
                  '</code></pre>'
                );
              } catch (__) {}
            }
            return (
              '<pre class="hljs rounded-lg dark:bg-primary shadow-lg"><code>' +
              markdownIt.utils.escapeHtml(str) +
              '</code></pre>'
            );
          }
        }).use(emoji);
  
        this.renderedMarkdown = markdownIt.render(newText);
      }
    }
  };
  </script>
  
  <style>
  /* Add styles for code highlighting */
  .hljs {
    display: block;
    overflow-x: auto;
    padding: 0.5em;
    background: #f5f5f5;
  }
  
  .hljs code {
    display: inline;
    padding: 0;
    border: none;
    background: none;
  }
  </style>
  