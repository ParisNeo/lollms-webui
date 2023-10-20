<template>
  <div class="break-all">
    <div ref="mdRender" class="markdown-content">
      <div v-for="(item, index) in markdownItems" :key="index">
        <code-block
          v-if="item.type === 'code'"
          :language="item.language"
          :code="item.code"
          :discussion_id="discussion_id"
          :message_id="message_id"
        ></code-block>
        <div v-else v-html="item.html"></div>
      </div>
    </div>
  </div>
</template>

<script>
import {nextTick, ref, onMounted, watch } from 'vue';
import feather from 'feather-icons';
import MarkdownIt from 'markdown-it';
import emoji from 'markdown-it-emoji';
import anchor from 'markdown-it-anchor';
import implicitFigures from 'markdown-it-implicit-figures';
import 'highlight.js/styles/tomorrow-night-blue.css';
import 'highlight.js/styles/tokyo-night-dark.css';
import attrs from 'markdown-it-attrs';
import CodeBlock from './CodeBlock.vue';
import hljs from 'highlight.js';
function escapeHtml(unsafe) {
  return unsafe
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
export default {
  name: 'MarkdownRenderer',
  props: {
    markdownText: {
      type: String,
      required: true,
    },
    discussion_id: {
      type: [String, Number],
      default: "0",
      required: false,
    },
    message_id: {
      value: "0",
      type: [String, Number],
      required: false,
    },
  },
  components: {
    CodeBlock,
  },
  setup(props) {
    const md = new MarkdownIt({
      html: true,
      highlight: (code, language) => {
        const validLanguage = language && hljs.getLanguage(language) ? language : 'plaintext';
        return hljs.highlight(validLanguage, code).value;
      },
      renderInline: true,
      breaks: true,
    })
      .use(emoji)
      .use(anchor)
      .use(implicitFigures, {
        figcaption: true,
      })
      .use(attrs);
    const markdownItems = ref([]);
    const updateMarkdown = () => {
      if (props.markdownText) {
        let tokens = md.parse(props.markdownText, {});
        markdownItems.value = tokens.map(token => {
          if (token.type === 'fence') {
            return {
              type: 'code',
              language: escapeHtml(token.info),
              code: token.content,
            };
          } else {
            return {
              type: 'html',
              html: md.renderer.render([token], md.options, {}),
            };
          }
        });
      } else {
        markdownItems.value = [];
      }
      nextTick(() => {
        feather.replace();
      });
    };
    watch(() => props.markdownText, updateMarkdown);
    onMounted(updateMarkdown);
    return { markdownItems };
  },
};
</script>
<style>
/* Your existing styles */
</style>

