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
    const markdownIt = new MarkdownIt({
      html: false,        
      xhtmlOut: true,        
      breaks: true,
      linkify: true,
      typographer: true,
      highlight: (str, lang) => {
        if (lang && hljs.getLanguage(lang)) {
          try {
            return (
              '<pre class="hljs p-4 overflow-x-auto  rounded-lg dark:bg-bg-dark-code-block bg-bg-light-code-block shadow-lg"><code>' +
              hljs.highlight(lang, str, true).value +
              '</code></pre>'
            );
          } catch (__) { }
        }
        return (
          '<pre class="hljs p-4 overflow-x-auto rounded-lg dark:bg-bg-dark-code-block bg-bg-light-code-block shadow-lg"><code>' +
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
                '<pre class="hljs p-4 overflow-x-auto rounded-lg dark:bg-bg-dark-code-block bg-bg-light-code-block shadow-lg"><code>' +
                hljs.highlight(lang, str, true).value +
                '</code></pre>'
              );
            } catch (__) { }
          }
          return (
            '<pre class="hljs p-4 overflow-x-auto rounded-lg dark:bg-bg-dark-code-block bg-bg-light-code-block shadow-lg"><code>' +
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
  
