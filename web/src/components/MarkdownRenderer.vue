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
        <thinking-block
          v-else-if="item.type === 'thinking'"
          :content="item.content"
          :is-done="item.is_done"
        ></thinking-block>
        <div v-else v-html="item.html"></div>
      </div>
    </div>
  </div>
</template>

<script>
import { nextTick } from 'vue';
import feather from 'feather-icons';
import MarkdownIt from 'markdown-it';
import emoji from 'markdown-it-emoji';
import anchor from 'markdown-it-anchor';
import implicitFigures from 'markdown-it-implicit-figures';
import 'highlight.js/styles/tokyo-night-dark.css';
import attrs from 'markdown-it-attrs';
import CodeBlock from './CodeBlock.vue';
import ThinkingBlock from './ThinkingBlock.vue';
import hljs from 'highlight.js';
import mathjax from 'markdown-it-mathjax3';

function escapeHtml(unsafe) {
  return unsafe
    .replace(/&/g, "&")
    .replace(/</g, "<")
    .replace(/>/g, ">")
    .replace(/"/g, "\"")
    .replace(/'/g, "'");
}

function findNextTag(state, startLine) {
  for (let i = startLine; i < state.lineMax; i++) {
    let line = state.src.slice(state.bMarks[i], state.eMarks[i]).trim();
    if (line === '<thinking>' || line === '<think>' || line === '</thinking>' || line === '</think>') {
      return { line: i, tag: line };
    }
  }
  return null;
}

const thinkingRule = (state, startLine, endLine, silent) => {
    let startPos = state.bMarks[startLine] + state.tShift[startLine];
    let maxPos = state.eMarks[startLine];
    let lineTextTrimmed = state.src.slice(startPos, maxPos).trim();
    let isExplicitStart = lineTextTrimmed === '<thinking>' || lineTextTrimmed === '<think>';
    let nextTagInfo = findNextTag(state, startLine + (isExplicitStart ? 1 : 0));
    let isImplicitStart = !isExplicitStart && nextTagInfo && (nextTagInfo.tag === '</thinking>' || nextTagInfo.tag === '</think>');

    if (isExplicitStart || isImplicitStart) {
        let startTag = isExplicitStart ? lineTextTrimmed : (nextTagInfo.tag === '</thinking>' ? '<thinking>' : '<think>');
        let endTag = startTag.replace('<', '</');
        let contentLines = [];
        let contentStartLine = startLine + (isExplicitStart ? 1 : 0);
        let blockEndLine = endLine;
        let foundEndTag = false;
        let currentLineIdx = contentStartLine;

        while (currentLineIdx < endLine) {
             let currentLineRaw = state.src.slice(state.bMarks[currentLineIdx], state.eMarks[currentLineIdx]);
             let currentLineTrimmed = currentLineRaw.trim();

             if (isExplicitStart && currentLineTrimmed === endTag) {
                foundEndTag = true;
                blockEndLine = currentLineIdx + 1;
                break;
             }
             if (isImplicitStart && currentLineIdx === nextTagInfo.line) {
                 foundEndTag = true;
                 blockEndLine = currentLineIdx + 1;
                 break;
             }
             if( (!isExplicitStart || currentLineIdx < endLine) && (!isImplicitStart || currentLineIdx < nextTagInfo.line) ){
                contentLines.push(currentLineRaw);
             }
             currentLineIdx++;
        }
        if (isImplicitStart) {
            blockEndLine = nextTagInfo.line + 1;
        } else if (!foundEndTag){
             blockEndLine = currentLineIdx;
        }

        let isDone = (isExplicitStart && foundEndTag) || isImplicitStart;

        if (silent) return true;

        let rawBlockContent = state.src.slice(state.bMarks[startLine], state.eMarks[blockEndLine - 1]);
        let innerContent = contentLines.join('\n');

        let token = state.push('thinking_open', 'div', 1);
        token.markup = startTag;
        token.block = true;
        token.is_done = isDone;
        token.implicit = isImplicitStart;
        token.map = [startLine, blockEndLine];
        token.meta = { rawBlock: rawBlockContent, innerContent: innerContent };

        token = state.push('thinking_content', '', 0);
        token.content = innerContent;
        token.is_done = isDone;

        token = state.push('thinking_close', 'div', -1);
        token.markup = endTag;
        token.block = true;
        token.is_done = isDone;

        state.line = blockEndLine;
        return true;
    }
    return false;
};

export default {
  name: 'MarkdownRenderer',
  components: {
    CodeBlock,
    ThinkingBlock,
  },
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
      type: [String, Number],
      default: "0",
      required: false,
    },
  },
  emits: ['update:markdownText'],
  data() {
    return {
      markdownItems: [],
      md: null,
      _isUpdatingInternally: false,
    };
  },
  watch: {
    markdownText(newValue) {
      if (!this._isUpdatingInternally) {
        this.parseAndRenderMarkdown();
      }
      this._isUpdatingInternally = false;
    }
  },
  created() {
    this.md = new MarkdownIt({
        html: false,
        breaks: true,
        highlight: (code, language) => {
            const validLanguage = language && hljs.getLanguage(language) ? language : 'plaintext';
            try {
                return hljs.highlight(validLanguage, code).value;
            } catch (__) {
                return escapeHtml(code);
            }
        },
    })
    .use(emoji)
    .use(anchor)
    .use(implicitFigures, { figcaption: true })
    .use(attrs)
    .use(mathjax);

    this.md.renderer.rules.thinking_open = () => '';
    this.md.renderer.rules.thinking_content = () => '';
    this.md.renderer.rules.thinking_close = () => '';
    this.md.renderer.rules.fence = () => '';

    this.md.block.ruler.before('fence', 'thinking', thinkingRule);
  },
  mounted() {
    this.parseAndRenderMarkdown();
  },
  methods: {
    getRawMarkdownChunk(startLine, endLine) {
        if (startLine == null || endLine == null || startLine < 0 || endLine <= startLine) {
            return '';
        }
        const lines = this.markdownText.split('\n');
        const safeEndLine = Math.min(endLine, lines.length);
        if(startLine >= safeEndLine) return '';
        return lines.slice(startLine, safeEndLine).join('\n');
    },
    parseAndRenderMarkdown() {
      if (!this.markdownText || !this.md) {
        this.markdownItems = [];
        return;
      }

      const tokens = this.md.parse(this.markdownText, {});
      const newItems = [];
      let lastProcessedLine = 0;
      const lineCount = this.markdownText.split('\n').length;

      for (let i = 0; i < tokens.length; i++) {
        const token = tokens[i];

        if (!token.map || token.map[0] < lastProcessedLine) {
             if (token.type === 'thinking_content' || token.type === 'thinking_close') continue;
        }

        const startLine = token.map ? token.map[0] : lastProcessedLine;
        const endLine = token.map ? token.map[1] : startLine + 1;

        if (startLine > lastProcessedLine) {
          const rawChunk = this.getRawMarkdownChunk(lastProcessedLine, startLine);
          if (rawChunk) { // Store even if just whitespace to preserve structure
            newItems.push({
              type: 'markdown',
              raw: rawChunk,
              html: this.md.render(rawChunk),
            });
          }
        }

        if (token.type === 'thinking_open') {
          const blockEndLine = token.map ? token.map[1] : endLine;
          newItems.push({
            type: 'thinking',
            raw: token.meta?.rawBlock || this.getRawMarkdownChunk(startLine, blockEndLine),
            content: token.meta?.innerContent || '',
            is_done: token.is_done,
            implicit: token.implicit,
          });
          lastProcessedLine = blockEndLine;
          i += 2;

        } else if (token.type === 'fence') {
           const rawFence = this.getRawMarkdownChunk(startLine, endLine);
           newItems.push({
            type: 'code',
            raw: rawFence,
            language: escapeHtml(token.info.trim()),
            code: token.content,
          });
          lastProcessedLine = endLine;
        }
      }

      if (lastProcessedLine < lineCount) {
        const rawChunk = this.getRawMarkdownChunk(lastProcessedLine, lineCount);
        if (rawChunk) {
          newItems.push({
            type: 'markdown',
            raw: rawChunk,
            html: this.md.render(rawChunk),
          });
        }
      }

      this.markdownItems = newItems;

      nextTick(() => {
        feather.replace();
        if (window.MathJax && typeof window.MathJax.typesetPromise === 'function') {
           window.MathJax.typesetPromise([this.$refs.mdRender]).catch((err) => console.error('MathJax typesetting failed:', err));
        } else if (window.MathJax && typeof window.MathJax.Hub !== 'undefined') {
           window.MathJax.Hub.Queue(["Typeset", window.MathJax.Hub, this.$refs.mdRender]);
        }
      });
    },
    updateCode(index, newCode) {
      if (this.markdownItems[index]?.type === 'code') {
        const item = this.markdownItems[index];
        item.code = newCode;
        // Regenerate raw based on current state
        const lang = item.language || '';
        const tick = '```';
        item.raw = `${tick}${lang}\n${newCode}\n${tick}`; // Add newline before closing ticks

        const newMarkdownText = this.reconstructMarkdown();

        this._isUpdatingInternally = true;
        this.$emit('update:markdownText', newMarkdownText);
      }
    },
    reconstructMarkdown() {
      // Join raw parts, ensuring correct spacing potentially lost if chunks didn't capture trailing/leading newlines perfectly
      return this.markdownItems.map(item => item.raw).join('');
    },
  }
};
</script>

<style scoped>
.markdown-content :deep(code:not(pre code)) {
  background-color: #f0f0f0;
  padding: 0.2em 0.4em;
  margin: 0;
  font-size: 85%;
  border-radius: 3px;
  color: #333;
}
.markdown-content :deep(pre code) {
   background-color: transparent;
   padding: 0;
   margin: 0;
   font-size: inherit;
   border-radius: 0;
   color: inherit;
}
.markdown-content :deep(.MathJax_Display) {
  display: block !important;
  margin: 1em 0 !important;
}
.markdown-content :deep(mjx-container[display="true"]) {
  display: block !important;
  margin: 1em 0 !important;
}
.markdown-content :deep(mjx-container[display="false"]) {
 display: inline-block !important;
}
.markdown-content :deep(.thinking-block) {
  border-left: 3px solid orange;
  padding: 0.5em 1em;
  margin: 1em 0;
  background-color: #fff8e1;
  opacity: 0.8;
  transition: opacity 0.3s ease-in-out;
}
.markdown-content :deep(.thinking-block[data-done="true"]) {
   opacity: 1;
   border-left-color: #4caf50;
   background-color: #e8f5e9;
}
.markdown-content :deep(.thinking-content) {
  white-space: pre-wrap;
  font-style: italic;
  color: #616161;
}
</style>