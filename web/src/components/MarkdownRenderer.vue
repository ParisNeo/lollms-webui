<template>
    <div :class="['markdown', isDarkMode ? 'dark' : 'light']">
      <div v-html="renderedMarkdown"></div>
    </div>
  </template>
  
  <script>
  import MarkdownIt from 'markdown-it';
  import emoji from 'markdown-it-emoji';
  
  export default {
    props: {
      markdownText: {
        type: String,
        required: true
      },
      isDarkMode: {
        type: Boolean,
        default: false
      }
    },
    data() {
      return {
        renderedMarkdown: ''
      };
    },
    mounted() {
      this.renderMarkdown();
    },
    watch: {
      markdownText(newText) {
        this.renderMarkdown(newText);
      },
      isDarkMode() {
        this.renderMarkdown();
      }
    },
    methods: {
      renderMarkdown(text) {
        const markdownIt = new MarkdownIt().use(emoji);
        this.renderedMarkdown = markdownIt.render(text || this.markdownText);
      }
    }
  };
  </script>
  
  <style scoped>
  .markdown {
    /* Add Tailwind CSS classes for general styling */
    padding: 1rem;
    box-shadow: sm;
    border-radius: 5px;
  }
  
  .light {
    /* Add Tailwind CSS classes for light mode */
    background-color: #ffffff;
    color: #000000;
  }
  
  .dark {
    /* Add Tailwind CSS classes for dark mode */
    background-color: #1a202c;
    color: #ffffff;
  }
  </style>
  