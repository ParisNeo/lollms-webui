<template>
  <div class="break-all container w-full">
    <div class="markdown-content">
      <div v-for="(item, index) in markdownItems" :key="item.id">
        <code-block
          v-if="item.type === 'code'"
          :host="host"
          :language="item.language"
          :code="item.code"
          :discussion_id="discussion_id"
          :message_id="message_id"
          :client_id="client_id"
          @update-code="handleCodeUpdate(item.id, $event)"
        ></code-block>
        <thinking-block
          v-else-if="item.type === 'thinking'"
          :content="item.content"
          :is-done="item.is_done"
        ></thinking-block>
        <div v-else-if="item.type === 'markdown'" v-html="renderMarkdownChunk(item.content)"></div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, watch, nextTick } from 'vue';
import feather from 'feather-icons';
import MarkdownIt from 'markdown-it';
import emoji from 'markdown-it-emoji';
import anchor from 'markdown-it-anchor';
import implicitFigures from 'markdown-it-implicit-figures';
import 'highlight.js/styles/github.css'; // Light theme
import 'highlight.js/styles/tokyo-night-dark.css'; // Dark theme
import attrs from 'markdown-it-attrs';
import { debounce } from 'lodash-es';

import CodeBlock from './CodeBlock.vue';
import ThinkingBlock from './ThinkingBlock.vue';

const MARKDOWN_UPDATE_DEBOUNCE_MS = 200; // Debounce interval for markdown parsing

export default {
  name: 'MarkdownRenderer',
  props: {
    host: { type: String, required: false, default: "" },
    client_id: { type: String, required: true },
    markdownText: { type: String, required: true },
    discussion_id: { type: [String, Number], default: "0", required: false },
    message_id: { type: [String, Number], default: "0", required: false },
  },
  components: {
    CodeBlock,
    ThinkingBlock,
  },
  emits: ['code-block-updated'], // Event emitted when a code block's content changes

  setup(props, { emit }) {
    // Configure MarkdownIt instance
    const md = new MarkdownIt({
      html: true, // Allow HTML tags passed through from markdown source
      breaks: true, // Convert '\n' in paragraphs into <br>
      linkify: true, // Autoconvert URL-like text to links
      typographer: true, // Enable smart quotes and other typographic improvements
    }).use(emoji)
      .use(anchor, { // Add anchors to headings
          permalink: anchor.permalink.ariaHidden({ placement: 'before', symbol: '#' })
       })
      .use(implicitFigures, { figcaption: true }) // Auto-wrap images in <figure>
      .use(attrs); // Allow adding classes/IDs like {.class #id}

    const markdownItems = ref([]); // Reactive array holding parsed markdown segments
    let uniqueIdCounter = 0; // Counter for generating unique keys for v-for

    // Function to parse the markdown text into structured items
    const parseAndStructure = (text) => {
        const items = [];
        uniqueIdCounter = 0;
        let currentIndex = 0;

        // Regex to find the start of code blocks or thinking blocks
        const delimiterRegex = /(```(\w*)\r?\n)|(<(thinking|think)>)/g;
        let match;

        while ((match = delimiterRegex.exec(text)) !== null) {
            const matchIndex = match.index;

            // Add preceding markdown chunk
            if (matchIndex > currentIndex) {
                items.push({ id: uniqueIdCounter++, type: 'markdown', content: text.substring(currentIndex, matchIndex) });
            }

            let blockType = '';
            let blockInfo = {};
            let delimiterLength = match[0].length;
            let blockContent = '';
            let consumedLength = delimiterLength;
            let blockEndIndex = -1;

            if (match[1]) { // Code block started (match[1] is ```lang\n)
                blockType = 'code';
                blockInfo = { language: match[2] || 'plaintext' }; // match[2] is the language
                const endCodeDelimiter = '\n```';
                blockEndIndex = text.indexOf(endCodeDelimiter, matchIndex + delimiterLength);

                if (blockEndIndex !== -1) {
                    blockContent = text.substring(matchIndex + delimiterLength, blockEndIndex);
                    consumedLength += blockContent.length + endCodeDelimiter.length;
                } else { // Unclosed block
                    blockContent = text.substring(matchIndex + delimiterLength);
                    consumedLength += blockContent.length;
                }
                 items.push({ id: uniqueIdCounter++, type: 'code', language: blockInfo.language, code: blockContent });

            } else if (match[3]) { // Thinking block started (match[3] is <thinking> or <think>)
                blockType = 'thinking';
                const startTag = match[3]; // e.g., <thinking>
                const endTag = startTag.replace('<', '</'); // e.g., </thinking>
                blockEndIndex = text.indexOf(endTag, matchIndex + delimiterLength);
                let isDone = false;

                if (blockEndIndex !== -1) {
                    blockContent = text.substring(matchIndex + delimiterLength, blockEndIndex);
                    consumedLength += blockContent.length + endTag.length;
                    isDone = true;
                } else { // Unclosed block
                    blockContent = text.substring(matchIndex + delimiterLength);
                    consumedLength += blockContent.length;
                }
                 items.push({ id: uniqueIdCounter++, type: 'thinking', content: blockContent, is_done: isDone });
            }

             currentIndex = matchIndex + consumedLength;
             // Ensure regex search continues from the new position
             delimiterRegex.lastIndex = currentIndex;

        } // end while

        // Add any remaining markdown chunk after the last delimiter
        if (currentIndex < text.length) {
            items.push({ id: uniqueIdCounter++, type: 'markdown', content: text.substring(currentIndex) });
        }

        // Update the reactive ref; Vue handles efficient DOM updates
        markdownItems.value = items;

        // Update Feather icons after the DOM has potentially changed
        nextTick(() => {
            try { feather.replace(); } catch (e) { /* Ignore errors if icons aren't present */ }
        });
    };

    // Create a debounced version of the parsing function
    const debouncedParseAndStructure = debounce(parseAndStructure, MARKDOWN_UPDATE_DEBOUNCE_MS, { leading: false, trailing: true });

    // Renders a markdown string chunk to HTML using the configured MarkdownIt instance
    const renderMarkdownChunk = (markdown) => {
      try {
        return md.render(markdown || '');
      } catch (e) {
        console.error("Markdown rendering error:", e);
        // Return escaped error message for safety
        const safeError = String(e).replace(/</g, "<").replace(/>/g, ">");
        return `<pre style="color: red; background-color: #fdd; padding: 5px; border: 1px solid red;">Error rendering markdown chunk:\n${safeError}</pre>`;
      }
    };

    // Handles the 'update-code' event from CodeBlock components
    const handleCodeUpdate = (itemId, newCode) => {
        const itemIndex = markdownItems.value.findIndex(item => item.id === itemId);
         if (itemIndex !== -1 && markdownItems.value[itemIndex].type === 'code') {
            // Emit an event upwards for the parent component to handle the data change
            emit('code-block-updated', {
                id: itemId, // Pass the unique ID for reliable identification
                index: itemIndex, // Pass index as well, might be useful
                language: markdownItems.value[itemIndex].language,
                newCode: newCode, // The updated code content
            });
            // *Immediately* update the local state for a responsive UI.
            // The parent's update will eventually confirm this via prop change,
            // but this prevents perceived lag during editing.
             markdownItems.value[itemIndex].code = newCode;
         }
    };

    // Watch the incoming markdownText prop for changes
    watch(() => props.markdownText, (newValue) => {
        // Use the debounced function to avoid excessive parsing during rapid updates (e.g., streaming)
        debouncedParseAndStructure(newValue || '');
    }, { immediate: true }); // Parse immediately on component mount

    onMounted(() => {
      // Initial parse is handled by the immediate watcher
      // Feather icons update is handled within parseAndStructure's nextTick
    });

    // Expose necessary data and methods to the template
    return {
      markdownItems,
      handleCodeUpdate,
      renderMarkdownChunk,
      // Make props directly available if needed in template (though already accessible)
      host: props.host,
      client_id: props.client_id,
      discussion_id: props.discussion_id,
      message_id: props.message_id
    };
  }
};
</script>

<style>
/* Apply styles globally within this component's scope or remove 'scoped' if needed */
.markdown-content { word-wrap: break-word; }
.markdown-content p { margin-bottom: 0.5rem; }
.markdown-content h1, .markdown-content h2, .markdown-content h3, .markdown-content h4, .markdown-content h5, .markdown-content h6 { margin-top: 1rem; margin-bottom: 0.5rem; font-weight: 600; }
.markdown-content ul, .markdown-content ol { margin-left: 1.5rem; margin-bottom: 0.5rem; padding-left: 1rem; } /* Added padding-left */
.markdown-content li { margin-bottom: 0.25rem; }
.markdown-content li > p { margin-bottom: 0.1rem; }
.markdown-content blockquote { margin-left: 0; padding-left: 1rem; border-left: 4px solid #e2e8f0; /* Tailwind gray-200 */ color: #4a5568; /* Tailwind gray-700 */ margin-bottom: 0.5rem; }
.dark .markdown-content blockquote { border-left-color: #4a5568; /* Tailwind gray-600 */ color: #a0aec0; /* Tailwind gray-400 */ }
.markdown-content code:not(pre > code) { @apply font-mono bg-gray-100 dark:bg-gray-700 px-1 py-0.5 rounded text-sm text-red-600 dark:text-red-400; } /* Example color change */
.markdown-content a { @apply text-blue-600 dark:text-blue-400 hover:underline; }
.thinking-block { /* Optional container styles */ }
.thinking-content { white-space: pre-wrap; font-style: italic; color: #718096; /* Tailwind gray-600 */ }
.dark .thinking-content { color: #a0aec0; /* Tailwind gray-500 */ }
.markdown-content .feather { width: 1em; height: 1em; vertical-align: -0.125em; stroke-width: 2; }
.markdown-content table { @apply w-full border-collapse border border-gray-300 dark:border-gray-600 my-2 text-sm; }
.markdown-content th, .markdown-content td { @apply border border-gray-300 dark:border-gray-600 p-1.5 text-left; }
.markdown-content th { @apply bg-gray-100 dark:bg-gray-700 font-semibold; }
.markdown-content figure { margin: 1em 0; text-align: center; }
.markdown-content figure img { @apply inline-block; } /* Center image within figure */
.markdown-content figure figcaption { font-size: 0.9em; color: #718096; /* Tailwind gray-600 */ margin-top: 0.5em; font-style: italic; }
.dark .markdown-content figure figcaption { color: #a0aec0; /* Tailwind gray-500 */ }
/* Header anchor link style */
.markdown-content .header-anchor { margin-left: 0.25rem; opacity: 0.5; transition: opacity 0.2s ease-in-out; text-decoration: none; }
.markdown-content h1:hover .header-anchor,
.markdown-content h2:hover .header-anchor,
.markdown-content h3:hover .header-anchor,
.markdown-content h4:hover .header-anchor,
.markdown-content h5:hover .header-anchor,
.markdown-content h6:hover .header-anchor { opacity: 1; }
</style>