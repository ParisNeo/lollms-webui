<template>
  <div class="break-all container w-full">
    <div ref="mdRender" class="markdown-content">
      <div v-for="(item, index) in markdownItems" :key="index">
        <code-block
          v-if="item.type === 'code'"
          :host="host"
          :language="item.language"
          :code="item.code"
          :discussion_id="discussion_id"
          :message_id="message_id"
          :client_id="client_id"
          @update-code="updateCode(index, $event)"
        ></code-block>
        <div v-else v-html="item.html"></div>
      </div>
    </div>
  </div>
</template>

<script>
import { nextTick, ref, onMounted, watch } from 'vue';
import feather from 'feather-icons';
import MarkdownIt from 'markdown-it';
import emoji from 'markdown-it-emoji';
import anchor from 'markdown-it-anchor';
import MarkdownItMultimdTable from 'markdown-it-multimd-table';
import implicitFigures from 'markdown-it-implicit-figures';
import 'highlight.js/styles/tomorrow-night-blue.css';
import 'highlight.js/styles/tokyo-night-dark.css';
import attrs from 'markdown-it-attrs';
import CodeBlock from './CodeBlock.vue';
import hljs from 'highlight.js';
import mathjax from 'markdown-it-mathjax';


import texmath from 'markdown-it-texmath';
import katex from 'katex';

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
    host: {
      type: String,
      required: false,
      default: "http://localhost:9600",
    },
    client_id: {
      type: String,
      required: true,
    },
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
      breaks: false, // Prevent newlines from being converted to <br> tags
    })
      .use(emoji)
      .use(anchor)
      .use(implicitFigures, {
        figcaption: true,
      })
      .use(attrs)
      .use(MarkdownItMultimdTable, {
        enableRowspan: true,
        enableColspan: true,
        enableGridTables: true,
        enableGridTablesExtra: true,
        enableTableIndentation: true,
        tableCellPadding: ' ',
        tableCellJoiner: '|',
        multilineCellStartMarker: '|>',
        multilineCellEndMarker: '<|',
        multilineCellPadding: ' ',
        multilineCellJoiner: '\n',
      });

    // Add a custom rule to escape backslashes before LaTeX delimiters
    md.core.ruler.before('normalize', 'escape_latex_delimiters', state => {
      state.src = state.src.replace(/(?<!\\)(\\[\(\)\[\]])/g, '\\$1');
    });

    // Modify the inline LaTeX rule to ensure it only triggers once
    md.inline.ruler.before('escape', 'inline_latex', function(state, silent) {
      const start = state.pos;
      const max = state.posMax;

      if (state.src.slice(start, start + 2) !== '\\(') return false;

      let end = start + 2;
      while (end < max) {
        if (state.src.slice(end, end + 2) === '\\)') {
          end += 2;
          break;
        }
        end++;
      }

      if (end === max) return false;

      if (!silent) {
        const token = state.push('latex_inline', 'latex', 0);
        token.content = state.src.slice(start + 2, end - 2);
        token.markup = '\\(\\)';
      }

      state.pos = end;
      return true;
    });

    // Ensure the LaTeX is rendered only once
    md.renderer.rules.latex_inline = function(tokens, idx) {
      return '<span class="inline-latex">' + katex.renderToString(tokens[idx].content, {displayMode: true}) + '</span>';
    };

    // Enhance list rendering
    md.renderer.rules.list_item_open = function (tokens, idx, options, env, self) {
      const token = tokens[idx];
      if (token.markup === '1.') {
        // This is an ordered list item
        const start = token.attrGet('start');
        if (start) {
          return `<li value="${start}">`;
        }
      }
      return self.renderToken(tokens, idx, options);
    };

    md.use(texmath, {
      engine: katex,
      delimiters: [
        {left: '$$', right: '$$', display: true},
        {left: '$', right: '$', display: false},
        {left: '\\[', right: '\\]', display: true}
      ],
      katexOptions: { macros: { "\\RR": "\\mathbb{R}" } }
    });

    const markdownItems = ref([]);
    const updateMarkdown = () => {
      if (props.markdownText) {
        let tokens = md.parse(props.markdownText, {});
        let cumulated = [];
        markdownItems.value = [];
        for (let i = 0; i < tokens.length; i++) {
          if (tokens[i].type !== 'fence') {
            cumulated.push(tokens[i]);
          } else {
            if (cumulated.length > 0) {
              markdownItems.value.push({
                type: 'html',
                html: md.renderer.render(cumulated, md.options, {}),
              });
              cumulated = [];
            }
            markdownItems.value.push({
              type: 'code',
              language: escapeHtml(tokens[i].info),
              code: tokens[i].content,
            });
          }
        }
        if (cumulated.length > 0) {
          markdownItems.value.push({
            type: 'html',
            html: md.renderer.render(cumulated, md.options, {}),
          });
          cumulated = [];
        }
      } else {
        markdownItems.value = [];
      }
      nextTick(() => {
        feather.replace();
      });
    };

    const updateCode = (index, newCode) => {
      markdownItems.value[index].code = newCode;
    };

    watch(() => props.markdownText, updateMarkdown);
    onMounted(() => {
      updateMarkdown();
      nextTick(() => {
        if (window.MathJax) {
          window.MathJax.typesetPromise();
        }
      });
    });
    return { markdownItems, updateCode };
  },
};
</script>

<style>
/* Your existing styles */
.katex-display {
  display: inline-block;
  margin: 0;
}

.katex {
  display: inline-block;
  white-space: nowrap;
}
.inline-latex {
  display: inline !important;
}
</style>
