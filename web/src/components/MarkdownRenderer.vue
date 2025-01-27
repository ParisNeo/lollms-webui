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
            v-if="item.type === 'thinking'"
            :content="item.content"
            :is-done="item.is_done"
          ></thinking-block>
          <div v-else v-html="item.html"></div>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import { nextTick, ref, onMounted, watch } from 'vue';
  import feather from 'feather-icons';
  import MarkdownIt from 'markdown-it'
  import emoji from 'markdown-it-emoji';
  import anchor from 'markdown-it-anchor';
  import MarkdownItMultimdTable from 'markdown-it-multimd-table';
  import implicitFigures from 'markdown-it-implicit-figures';
  import 'highlight.js/styles/tomorrow-night-blue.css';
  import 'highlight.js/styles/tokyo-night-dark.css';
  import attrs from 'markdown-it-attrs';
  import CodeBlock from './CodeBlock.vue';
  import ThinkingBlock from './ThinkingBlock.vue' 
  import hljs from 'highlight.js';
  import mathjax from 'markdown-it-mathjax3';
  
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
      ThinkingBlock,
    },
    setup(props) {
      // Custom rule for thinking blocks
      const thinkingRule = (state, startLine, endLine, silent) => {
        let start = state.bMarks[startLine] + state.tShift[startLine];
        let max = state.eMarks[startLine];
        
        let line = state.src.slice(start, max);

        if (!line.trim().startsWith('<thinking>')) return false;
        
        let currentLine = startLine + 1;
        let content = [];
        let found = false;
        
        // Search for closing tag
        while (currentLine < endLine) {
          let currentLineContent = state.src.slice(
            state.bMarks[currentLine], 
            state.eMarks[currentLine]
          );
          
          if (currentLineContent.trim() === '</thinking>') {
            found = true;
            break;
          }
          content.push(currentLineContent);
          currentLine++;
        }
        
        if (silent) return true;
        
        // Create tokens
        let token = state.push('thinking_open', 'div', 1);
        token.markup = '<thinking>';
        token.block = true;
        token.is_done = found; // Add is_done status
        
        token = state.push('thinking_content', '', 0);
        token.content = content.join('\n');
        token.is_done = found;
        
        token = state.push('thinking_close', 'div', -1);
        token.markup = '</thinking>';
        token.block = true;
        token.is_done = found;
        
        state.line = found ? currentLine + 1 : currentLine;
        return true;
      };

    const md = new MarkdownIt({
      html: true,
      breaks: true,
      highlight: (code, language) => {
        const validLanguage = language && hljs.getLanguage(language) ? language : 'plaintext';
        return hljs.highlight(validLanguage, code).value;
      },
    })
    .use(emoji)
    .use(anchor)
    .use(implicitFigures, {
      figcaption: true,
    })
    .use(attrs);
    // Add renderer rules
    md.renderer.rules.thinking_open = () => '<div class="thinking-block">';
    md.renderer.rules.thinking_content = (tokens, idx) => {
      return `<div class="thinking-content">${md.utils.escapeHtml(tokens[idx].content)}</div>`;
    };
    md.renderer.rules.thinking_close = () => '</div>';

    // Add the rule
    md.block.ruler.before('fence', 'thinking', thinkingRule);
    const markdownItems = ref([]);
    
    const updateMarkdown = () => {
      if (props.markdownText) {
        let tokens = md.parse(props.markdownText, {});
        let cumulated = [];
        markdownItems.value = [];
        
        for (let i = 0; i < tokens.length; i++) {
          const token = tokens[i];
          
          if (token.type === 'thinking_open') {
            if (cumulated.length > 0) {
              markdownItems.value.push({
                type: 'html',
                html: md.renderer.render(cumulated, md.options, {}),
              });
              cumulated = [];
            }
            
            const contentToken = tokens[i + 1];
            if (contentToken && contentToken.type === 'thinking_content') {
              markdownItems.value.push({
                type: 'thinking',
                content: contentToken.content,
                is_done: contentToken.is_done // Add is_done status
              });
            }
            
            i += 2;
          } else if (token.type === 'fence') {
            if (cumulated.length > 0) {
              markdownItems.value.push({
                type: 'html', 
                html: md.renderer.render(cumulated, md.options, {}),
              });
              cumulated = [];
            }
            markdownItems.value.push({
              type: 'code',
              language: escapeHtml(token.info),
              code: token.content,
            });
          } else {
            cumulated.push(token);
          }
        }
        
        if (cumulated.length > 0) {
          markdownItems.value.push({
            type: 'html',
            html: md.renderer.render(cumulated, md.options, {}),
          });
        }
        
        nextTick(() => {
          feather.replace();
          if (window.MathJax) {
            window.MathJax.typesetPromise();
          }
        });
      } else {
        markdownItems.value = [];
      }
    };
      const updateCode = (index, newCode) => {
        markdownItems.value[index].code = newCode;
      };

      watch(() => props.markdownText, updateMarkdown);
      
      onMounted(() => {
        updateMarkdown();
      });

      return { markdownItems, updateCode };
    }
  };
  </script>
  
  <style scoped>
  .math {
    display: inline-block; /* this should allow inline math to display inline */
  }

  .mathjax_block { /* if this class exists, ensure it's not applied to inline math */
    display: block;
  }
  </style>
  