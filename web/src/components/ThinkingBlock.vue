<!-- ThinkingBlock.vue -->
<template>
  <div class="my-4 bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden border border-gray-200 dark:border-gray-700">
    <!-- Header / Toggle Area -->
    <div class="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700/50 border-b border-gray-200 dark:border-gray-700">
      <button
        @click="toggle"
        :aria-expanded="isOpen"
        :aria-controls="contentId"
        class="group flex items-center gap-2 text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400 focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-blue-500 dark:focus-visible:ring-offset-gray-800 rounded"
      >
        <!-- Chevron Icon -->
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor"
             class="w-5 h-5 transition-transform duration-300 ease-in-out flex-shrink-0"
             :class="{ 'rotate-90': isOpen }">
          <path fill-rule="evenodd" d="M7.21 14.77a.75.75 0 01.02-1.06L11.168 10 7.23 6.29a.75.75 0 111.04-1.08l4.5 4.25a.75.75 0 010 1.08l-4.5 4.25a.75.75 0 01-1.06-.02z" clip-rule="evenodd" />
        </svg>

        <!-- Thinking State / Title -->
        <span v-if="isThinking" class="flex items-center gap-2">
          <span>Thinking</span>
          <span class="inline-flex items-center space-x-1">
            <span v-for="i in 3" :key="i"
                 class="w-1.5 h-1.5 bg-blue-500 rounded-full animate-bounce"
                 :style="{ animationDelay: `${(i-1)*150}ms` }"></span>
          </span>
        </span>
        <span v-else>AI Thoughts</span>
      </button>

      <!-- Download Button -->
      <button
        v-if="!isThinking && content"
        @click="downloadMarkdown"
        class="p-1.5 text-gray-500 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-full focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-1 focus-visible:ring-blue-500 dark:focus-visible:ring-offset-gray-700/50 transition-colors duration-150"
        title="Download as Markdown"
      >
        <span class="sr-only">Download AI Thoughts as Markdown</span>
        <!-- Download Icon -->
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-5 h-5">
          <path d="M10.75 2.75a.75.75 0 00-1.5 0v8.614L6.295 8.235a.75.75 0 10-1.09 1.03l4.25 4.5a.75.75 0 001.09 0l4.25-4.5a.75.75 0 00-1.09-1.03l-2.955 3.129V2.75z" />
          <path d="M3.5 12.75a.75.75 0 00-1.5 0v2.5A2.75 2.75 0 004.75 18h10.5A2.75 2.75 0 0018 15.25v-2.5a.75.75 0 00-1.5 0v2.5c0 .69-.56 1.25-1.25 1.25H4.75c-.69 0-1.25-.56-1.25-1.25v-2.5z" />
        </svg>
      </button>
    </div>

    <!-- Collapsible Content Area -->
    <transition
      enter-active-class="transition duration-300 ease-out"
      enter-from-class="transform -translate-y-2 scale-95 opacity-0"
      enter-to-class="transform translate-y-0 scale-100 opacity-100"
      leave-active-class="transition duration-200 ease-in"
      leave-from-class="transform translate-y-0 scale-100 opacity-100"
      leave-to-class="transform -translate-y-2 scale-95 opacity-0"
    >
      <div v-show="isOpen" class="content-wrapper" :id="contentId">
        <div
          ref="contentContainer"
          class="p-4 text-gray-700 dark:text-gray-300 thinking-prose prose-sm max-w-none overflow-y-auto max-h-[400px] bg-gray-50 dark:bg-gray-800/50"
        >
          <!-- Slot for potential custom rendering -->
          <slot v-if="$slots.default"></slot>
          <!-- Default Markdown Rendering -->
          <div v-else v-html="renderedContent"></div>
          <!-- Optional: Blinking cursor effect while thinking -->
          <span v-if="isThinking" class="inline-block w-2 h-4 ml-1 bg-gray-600 dark:bg-gray-400 animate-pulse"></span>
        </div>
      </div>
    </transition>
  </div>
</template>

<script>
import { ref, computed, watch, nextTick, onMounted } from 'vue';
import { marked } from 'marked';
import DOMPurify from 'dompurify';
import hljs from 'highlight.js';
// Choose a theme for highlight.js - github-dark is a good option for dark mode support
import 'highlight.js/styles/github-dark.css'; // Or choose another theme like github.css

// Configure Marked
marked.setOptions({
  highlight: function(code, lang) {
    const language = hljs.getLanguage(lang) ? lang : 'plaintext';
    try {
      return hljs.highlight(code, { language, ignoreIllegals: true }).value;
    } catch (error) {
      console.error("Highlight.js error:", error);
      return hljs.highlightAuto(code).value; // Fallback
    }
  },
  breaks: true, // Render line breaks as <br>
  gfm: true,    // Enable GitHub Flavored Markdown
  pedantic: false,
  smartLists: true,
  smartypants: false,
});

// Unique ID generation helper (simple)
let idCounter = 0;

export default {
  name: 'ThinkingBlock',
  props: {
    content: {
      type: String,
      required: true,
    },
    isDone: {
      type: Boolean,
      required: true,
      default: false,
    },
    startOpen: { // Optional: Prop to control initial state
      type: Boolean,
      default: false,
    }
  },
  setup(props) {
    const isOpen = ref(props.startOpen);
    const contentContainer = ref(null);
    const contentId = `thinking-content-${idCounter++}`; // Unique ID for aria-controls

    const isThinking = computed(() => !props.isDone);

    const renderedContent = computed(() => {
      // Sanitize *after* Markdown parsing
      const rawHtml = marked.parse(props.content || '');
      // Allow specific target attributes if needed, e.g., for links
      return DOMPurify.sanitize(rawHtml, { ADD_ATTR: ['target'] });
    });

    const toggle = () => {
      isOpen.value = !isOpen.value;
      if (isOpen.value) {
        nextTick(scrollToBottom);
      }
    };

    const scrollToBottom = () => {
      if (contentContainer.value) {
        contentContainer.value.scrollTop = contentContainer.value.scrollHeight;
      }
    };

    const downloadMarkdown = () => {
      const blob = new Blob([props.content], { type: 'text/markdown;charset=utf-8' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'ai_thoughts.md');
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    };

    // Watch for content changes to scroll down, especially when open
    watch(() => props.content, () => {
      if (isOpen.value) {
        nextTick(scrollToBottom);
      }
    });

    // Watch for `isDone` changing
    watch(() => props.isDone, (newValue) => {
        // Ensure scroll happens if it finishes while open
        if (newValue && isOpen.value) {
             nextTick(scrollToBottom);
        }
    });

    // Initial scroll if starting open
    onMounted(() => {
        if (isOpen.value) {
            nextTick(scrollToBottom);
        }
    });

    return {
      isOpen,
      isThinking,
      renderedContent,
      contentContainer,
      contentId,
      toggle,
      downloadMarkdown,
    };
  }
}
</script>
