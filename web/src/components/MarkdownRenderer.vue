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
        <latex-editor
          v-else-if="item.type === 'latex'"
          :initial-latex-code="item.code"
          :inline="item.inline"
          @update:latexCode="updateLatex(index, $event)"
          class="my-1"
        ></latex-editor>
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
import LatexEditor from './LatexEditor.vue';
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
    LatexEditor,
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
                const result = hljs.highlight(validLanguage, code, true);
                return `<pre class="hljs"><code>${result.value}</code></pre>`;
            } catch (__) {
                return `<pre class="hljs"><code>${escapeHtml(code)}</code></pre>`;
            }
        },
    })
    .use(emoji)
    .use(anchor)
    .use(implicitFigures, { figcaption: true })
    .use(attrs)
    .use(mathjax);

    this.md.renderer.rules.fence = () => '';
    this.md.renderer.rules.thinking_open = () => '';
    this.md.renderer.rules.thinking_content = () => '';
    this.md.renderer.rules.thinking_close = () => '';
    this.md.renderer.rules.math_inline = () => '';
    this.md.renderer.rules.math_block = () => '';

    this.md.block.ruler.before('fence', 'thinking', thinkingRule);
  },
  mounted() {
    this.parseAndRenderMarkdown();
  },
  methods: {
// Inside MarkdownRenderer.vue methods:

getRawMarkdownChunk(startLine, endLine) {
    if (typeof startLine !== 'number' || typeof endLine !== 'number' || startLine < 0 || endLine <= startLine) {
        // console.warn(`getRawMarkdownChunk called with invalid lines: ${startLine}, ${endLine}`);
        return '';
    }
    const lines = this.markdownText.split(/\r?\n/);
    const safeStartLine = Math.min(startLine, lines.length);
    const safeEndLine = Math.min(endLine, lines.length);
    if (safeStartLine >= safeEndLine) return '';
    // Slice captures lines from start index up to, but not including, end index.
    return lines.slice(safeStartLine, safeEndLine).join('\n');
},

parseAndRenderMarkdown() {
    if (!this.markdownText || !this.md) {
        this.markdownItems = [];
        return;
    }

    try {
        const tokens = this.md.parse(this.markdownText, {});
        const newItems = [];
        let lastProcessedLine = 0;
        const totalLines = this.markdownText.split(/\r?\n/).length;

        for (let i = 0; i < tokens.length; i++) {
            const token = tokens[i];

            // Skip tokens that don't represent distinct blocks or are handled implicitly
            if (!token.map || !Array.isArray(token.map) || token.map.length < 2) continue;
            // Skip closing tags for blocks we handle explicitly by their opening tag
            if (token.type === 'thinking_close' || token.type === 'thinking_content') continue;
            // Skip inline math handled by math_block/math_inline rules already
            // if (token.type === 'math_inline_double' || token.type === 'math_block_label') continue;

            const startLine = token.map[0];
            let endLine = token.map[1]; // Use let for potential adjustment

             // --- Logic ---

             // 1. Render any standard markdown *before* this token's block starts
            if (startLine > lastProcessedLine) {
                const rawChunk = this.getRawMarkdownChunk(lastProcessedLine, startLine);
                if (rawChunk) { // Add even if just whitespace, preserving structure
                    newItems.push({
                        type: 'markdown',
                        raw: rawChunk,
                        html: this.md.render(rawChunk) // Render only this chunk
                    });
                }
                lastProcessedLine = startLine; // Advance past the rendered gap
            } else if (startLine < lastProcessedLine) {
                 // Overlap situation, likely means this token is inside a block already processed.
                 // Safest is often to skip it to avoid duplication.
                 continue;
            }


            // 2. Identify and process the *current* block based on the token type
            let blockProcessed = false;
            if (token.type === 'thinking_open') {
                // Look ahead for content and close tokens to get the full range & data
                let thinkingEndLine = endLine;
                let thinkingContent = '';
                let isDone = false; // Assume not done unless close tag found
                let consumedTokens = 0;

                if (i + 1 < tokens.length && tokens[i+1].type === 'thinking_content') {
                     thinkingContent = tokens[i+1].content;
                     consumedTokens = 1;
                     if(tokens[i+1].map) thinkingEndLine = Math.max(thinkingEndLine, tokens[i+1].map[1]);

                     if (i + 2 < tokens.length && tokens[i+2].type === 'thinking_close') {
                         isDone = tokens[i+2].is_done !== undefined ? tokens[i+2].is_done : true; // Default to true if closed
                         consumedTokens = 2;
                         if(tokens[i+2].map) thinkingEndLine = Math.max(thinkingEndLine, tokens[i+2].map[1]);
                     }
                }

                const rawContent = this.getRawMarkdownChunk(startLine, thinkingEndLine);
                newItems.push({
                    type: 'thinking',
                    raw: rawContent,
                    content: thinkingContent,
                    is_done: isDone,
                    implicit: token.implicit || false,
                });
                lastProcessedLine = thinkingEndLine;
                i += consumedTokens; // Skip the consumed content/close tokens
                blockProcessed = true;

            } else if (token.type === 'fence') {
                const rawFence = this.getRawMarkdownChunk(startLine, endLine);
                 newItems.push({
                    type: 'code',
                    raw: rawFence,
                    language: escapeHtml(token.info.trim()),
                    code: token.content,
                });
                lastProcessedLine = endLine;
                blockProcessed = true;

            } else if (token.type === 'math_inline' || token.type === 'math_block') {
                const isInline = token.type === 'math_inline';
                const delimiter = isInline ? '$' : '$$';
                const rawLatex = token.markup && token.content ? `${delimiter}${token.content}${delimiter}` : this.getRawMarkdownChunk(startLine, endLine);
                 newItems.push({
                    type: 'latex',
                    raw: rawLatex,
                    code: token.content,
                    inline: isInline,
                });
                lastProcessedLine = endLine;
                blockProcessed = true;

            } else if (token.level === 0 && !token.hidden && token.type.endsWith('_open')) {
                 // --- Potential Standard Markdown Block Start ---
                 // This is a heuristic: identifies top-level opening tags like paragraph_open, list_item_open, etc.
                 // We need to find the corresponding closing tag to get the full range.
                 let blockEndLine = endLine;
                 let nestingLevel = 0;
                 let j = i + 1;
                 for (; j < tokens.length; j++) {
                    const innerToken = tokens[j];
                    if(innerToken.type === token.type) { // Same opening tag type
                        nestingLevel++;
                    } else if (innerToken.type === token.type.replace('_open', '_close')) {
                        if (nestingLevel === 0) {
                            blockEndLine = innerToken.map ? Math.max(endLine, innerToken.map[1]) : endLine;
                            break; // Found the matching close tag
                        } else {
                            nestingLevel--;
                        }
                    }
                     // Make sure endLine tracks the maximum extent within the block
                     if(innerToken.map) blockEndLine = Math.max(blockEndLine, innerToken.map[1]);
                 }

                 // Now we have the range [startLine, blockEndLine] for this standard block
                const rawChunk = this.getRawMarkdownChunk(startLine, blockEndLine);
                if (rawChunk.trim()) { // Only add if it has content
                     newItems.push({
                        type: 'markdown',
                        raw: rawChunk,
                        html: this.md.render(rawChunk)
                    });
                     lastProcessedLine = blockEndLine;
                     i = j; // Skip all tokens within this processed block
                     blockProcessed = true;
                } else if (rawChunk) { // Preserve whitespace blocks if necessary
                    newItems.push({ type: 'markdown', raw: rawChunk, html: '' });
                     lastProcessedLine = blockEndLine;
                     i = j;
                     blockProcessed = true;
                } else {
                     // Empty block, just advance lastProcessedLine if needed
                     lastProcessedLine = Math.max(lastProcessedLine, blockEndLine);
                }
            }

            // 3. If no block was explicitly processed, but the token advanced lines, update lastProcessedLine.
            // This catches simple cases or tokens missed by the block logic.
             if (!blockProcessed && endLine > lastProcessedLine) {
                 // This path should ideally be hit less often with the block detection above.
                 // Could render the single token's range as markdown if needed, but might cause issues.
                 // For now, just advance the line counter.
                 lastProcessedLine = endLine;
             }
        } // End for loop

        // 4. Handle any final trailing markdown chunk after the last processed token/block.
        if (lastProcessedLine < totalLines) {
            const rawChunk = this.getRawMarkdownChunk(lastProcessedLine, totalLines);
             if (rawChunk) { // Add if non-empty (including whitespace)
                newItems.push({
                    type: 'markdown',
                    raw: rawChunk,
                    html: this.md.render(rawChunk),
                });
            }
        }

        this.markdownItems = newItems;

    } catch (error) {
        console.error("Error parsing markdown:", error);
        // Fallback: Render the whole thing simply in case of error
        this.markdownItems = [{ type: 'markdown', raw: this.markdownText, html: this.md.render(this.markdownText) }];
    } finally {
        nextTick(() => {
            feather.replace();
            // MathJax if needed
        });
    }
},

    updateCode(index, newCode) {
      if (index >= 0 && index < this.markdownItems.length && this.markdownItems[index]?.type === 'code') {
        const item = this.markdownItems[index];
        item.code = newCode;
        const lang = item.language || '';
        const tick = '```';
        item.raw = `${tick}${lang}\n${newCode}\n${tick}`;

        const newMarkdownText = this.reconstructMarkdown();

        this._isUpdatingInternally = true;
        this.$emit('update:markdownText', newMarkdownText);
      } else {
        console.warn(`updateCode called with invalid index ${index} or item type`);
      }
    },

    updateLatex(index, newLatexCode) {
      if (index >= 0 && index < this.markdownItems.length && this.markdownItems[index]?.type === 'latex') {
        const item = this.markdownItems[index];
        item.code = newLatexCode;
        const delimiter = item.inline ? '$' : '$$';
        item.raw = `${delimiter}${newLatexCode}${delimiter}`;

        const newMarkdownText = this.reconstructMarkdown();

        this._isUpdatingInternally = true;
        this.$emit('update:markdownText', newMarkdownText);
      } else {
        console.warn(`updateLatex called with invalid index ${index} or item type`);
      }
    },

    reconstructMarkdown() {
      return this.markdownItems.map(item => item.raw).join('');
    },
  }
};
</script>

<style scoped>
.markdown-content :deep(code:not(pre code)) {
  background-color: #f0f0f0;
  padding: 0.2em 0.4em;
  margin: 0 0.1em;
  font-size: 85%;
  border-radius: 3px;
  color: #333;
  word-break: break-word;
}
.markdown-content :deep(pre.hljs) {
  padding: 1em;
  margin: 1em 0;
  overflow-x: auto;
  border-radius: 6px;
  background-color: #2a2734;
}

.markdown-content :deep(pre.hljs code) {
   background-color: transparent;
   padding: 0;
   margin: 0;
   font-size: inherit;
   border-radius: 0;
   color: inherit;
   white-space: pre;
   word-break: normal;
}

.markdown-content :deep(.thinking-block) {
  border-left: 3px solid orange;
  padding: 0.5em 1em;
  margin: 1em 0;
  background-color: #fff8e1;
  opacity: 0.8;
  transition: opacity 0.3s ease-in-out;
  border-radius: 0 4px 4px 0;
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

.markdown-content :deep(p) {
    margin-bottom: 1rem;
}
/* Reduce margin for paragraphs immediately followed by LatexEditor */
.markdown-content :deep(p + .latex-editor-container) {
    margin-top: -0.5rem; /* Adjust as needed */
}
/* Adjust spacing around LatexEditor itself slightly */
.markdown-content :deep(.latex-editor-container) {
    margin-top: 0.5rem;
    margin-bottom: 0.5rem;
}
/* Make inline latex blend better */
.markdown-content :deep(.latex-editor-container .latex-inline) {
    display: inline-block;
    vertical-align: baseline; /* Align with text */
    margin: 0 0.15em; /* Minimal horizontal spacing */
    padding: 0 !important; /* Remove padding for inline */
}
.markdown-content :deep(.latex-editor-container .latex-inline .katex) {
     font-size: 1em; /* Match surrounding text size */
     padding: 0 !important;
}


.markdown-content :deep(li > p),
.markdown-content :deep(blockquote > p) {
    margin-bottom: 0;
}
.markdown-content :deep(ul),
.markdown-content :deep(ol) {
    margin-bottom: 1rem;
    padding-left: 2em;
}
.markdown-content :deep(blockquote) {
    margin: 1em 0;
    padding-left: 1em;
    border-left: 3px solid #ccc;
    color: #666;
}
.markdown-content :deep(hr) {
    margin: 2em 0;
    border: 0;
    border-top: 1px solid #eee;
}
</style>