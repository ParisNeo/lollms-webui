<template>
    <div>
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
      }
    },
    data() {
      return {
        renderedMarkdown: ''
      };
    },
    mounted() {
      const markdownIt = new MarkdownIt().use(emoji);
      this.renderedMarkdown = markdownIt.render(this.markdownText);
    },
    watch: {
      markdownText(newText) {
        const markdownIt = new MarkdownIt().use(emoji);
        this.renderedMarkdown = markdownIt.render(newText);
      }
    }
  };
</script>
  