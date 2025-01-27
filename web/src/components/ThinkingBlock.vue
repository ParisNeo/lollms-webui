<!-- ThinkingBlock.vue -->
<template>
  <div class="my-4">
    <div class="flex items-center gap-2">
      <button
        @click="toggle"
        class="group flex items-center gap-2 px-3 py-2 text-sm font-medium text-gray-700 hover:text-gray-900 transition-colors duration-200 rounded-md hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        :aria-expanded="isOpen"
      >
        <svg
          class="w-4 h-4 transition-transform duration-200"
          :class="{ 'rotate-90': isOpen }"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M9 5l7 7-7 7"
          />
        </svg>
        
        <span v-if="isThinking" class="flex items-center gap-2">
          Thinking
          <div class="flex space-x-1">
            <div v-for="i in 3" :key="i"
                 class="w-1 h-1 bg-blue-500 rounded-full animate-pulse"
                 :style="{ animationDelay: `${(i-1)*150}ms` }"
            ></div>
          </div>
        </span>
        <span v-else>AI Thoughts</span>
      </button>

      <button
        v-if="!isThinking && content"
        @click="downloadMarkdown"
        class="px-2 py-1 text-xs font-medium text-gray-600 hover:text-gray-900 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500"
        title="Download as Markdown"
      >
        <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
      </button>
    </div>

    <transition
      enter-active-class="transition duration-200 ease-out"
      enter-from-class="transform scale-95 opacity-0"
      enter-to-class="transform scale-100 opacity-100"
      leave-active-class="transition duration-150 ease-in"
      leave-from-class="transform scale-100 opacity-100"
      leave-to-class="transform scale-95 opacity-0"
    >
      <div v-if="isOpen" class="mt-2 text-gray-600">
        <div 
          ref="contentContainer"
          class="p-4 rounded-lg prose prose-sm max-w-none overflow-y-auto max-h-[500px]"
        >
          <div v-if="$slots.default">
            <slot></slot>
          </div>
          <div v-else v-html="renderedContent"></div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script>
import { marked } from 'marked';
import DOMPurify from 'dompurify';
import hljs from 'highlight.js';
import 'highlight.js/styles/github.css';

marked.setOptions({
  highlight: function(code, lang) {
    if (lang && hljs.getLanguage(lang)) {
      return hljs.highlight(code, { language: lang }).value;
    }
    return hljs.highlightAuto(code).value;
  },
  breaks: true,
  gfm: true
});

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
    }
  },
  data() {
    return {
      isOpen: false,
    }
  },
  computed: {
    isThinking() {
      return !this.isDone
    },
    renderedContent() {
      return DOMPurify.sanitize(marked.parse(this.content));
    }
  },
  watch: {
    content: {
      handler() {
        this.$nextTick(() => {
          this.scrollToBottom();
        });
      },
      immediate: true
    }
  },
  methods: {
    toggle() {
      this.isOpen = !this.isOpen;
      if (this.isOpen) {
        this.$nextTick(() => {
          this.scrollToBottom();
        });
      }
    },
    scrollToBottom() {
      if (this.$refs.contentContainer) {
        const container = this.$refs.contentContainer;
        container.scrollTop = container.scrollHeight;
      }
    },
    downloadMarkdown() {
      const blob = new Blob([this.content], { type: 'text/markdown' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'ai_thoughts.md');
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    }
  }
}
</script>

<style>
/* Base markdown styles */
.prose {
  @apply text-inherit;
}

.prose h1 {
  @apply text-2xl font-bold mb-4 mt-6;
}

.prose h2 {
  @apply text-xl font-bold mb-3 mt-5;
}

.prose h3 {
  @apply text-lg font-bold mb-2 mt-4;
}

.prose p {
  @apply mb-4;
}

.prose ul {
  @apply list-disc pl-5 mb-4;
}

.prose ol {
  @apply list-decimal pl-5 mb-4;
}

.prose code {
  @apply px-1 py-0.5 rounded text-sm font-mono bg-opacity-10 bg-gray-200;
}

.prose pre {
  @apply p-4 rounded-lg overflow-x-auto mb-4;
}

.prose pre code {
  @apply bg-transparent p-0;
}

.prose blockquote {
  @apply pl-4 border-l-4 border-gray-300 italic my-4;
}

.prose a {
  @apply text-blue-600 hover:text-blue-800 underline;
}

/* Custom scrollbar */
.prose::-webkit-scrollbar {
  @apply w-2;
}

.prose::-webkit-scrollbar-track {
  @apply bg-transparent;
}

.prose::-webkit-scrollbar-thumb {
  @apply bg-gray-300 rounded-full hover:bg-gray-400 transition-colors;
}

/* Smooth scrolling */
.prose {
  scroll-behavior: smooth;
}
</style>
