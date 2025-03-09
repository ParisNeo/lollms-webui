<template>
  <div class="help-view bg-gradient-to-br from-gray-50 to-blue-100 dark:from-gray-900 dark:to-blue-950 min-h-screen flex overflow-hidden">
    <!-- Left Sidebar -->
    <div class="left-bar w-72 bg-white dark:bg-gray-800 shadow-2xl p-6 fixed h-screen overflow-y-auto transition-all duration-500 ease-in-out md:w-80 lg:w-96 z-10">
      <h2 class="text-3xl font-bold text-gray-900 dark:text-white mb-8 flex items-center">
        <span class="mr-2">🗂️</span> Help Topics
      </h2>
      <ul class="space-y-4">
        <li v-for="(section, index) in helpSections" :key="index">
          <a @click.prevent="selectSection(index)" class="block p-4 rounded-xl text-gray-700 dark:text-gray-200 bg-gray-50 dark:bg-gray-700/50 hover:bg-blue-500 dark:hover:bg-blue-600 hover:text-white dark:hover:text-white transition-all duration-300 cursor-pointer shadow-sm" :class="{ 'bg-blue-500 text-white dark:bg-blue-600': selectedSection === index }">
            {{ section.title }}
          </a>
        </li>
      </ul>
    </div>

    <!-- Main Content -->
    <div class="main-content ml-72 md:ml-80 lg:ml-96 flex-1 p-10 overflow-y-auto h-screen flex items-center justify-center">
      <div class="big-card bg-white dark:bg-gray-900 rounded-2xl shadow-xl p-10 w-full h-full max-w-6xl mx-auto flex flex-col">
        <h1 class="text-5xl font-extrabold text-gray-900 dark:text-white mb-10 flex items-center">
          <span class="mr-3">📖</span> LoLLMs Help Center
        </h1>
        <div class="help-content flex-1 overflow-y-auto text-gray-700 dark:text-gray-300 prose dark:prose-invert max-w-none transition-opacity duration-500" v-html="selectedContent"></div>
      </div>
    </div>
  </div>
</template>

<script>
import { marked } from 'marked';

export default {
  name: 'HelpView',
  data() {
    return {
      helpSections: [],
      selectedSection: 0, // Default to the first section
    };
  },
  computed: {
    selectedContent() {
      return this.helpSections[this.selectedSection]?.content || 'Select a topic from the sidebar to view help content.';
    }
  },
  methods: {
    selectSection(index) {
      this.selectedSection = index;
    },
    async loadMarkdownFile(filename) {
      try {
        const response = await fetch(`/help/${filename}`);
        const markdown = await response.text();
        return marked(markdown);
      } catch (error) {
        console.error('Error loading markdown file:', error);
        return 'Error loading help content.';
      }
    },
    async loadHelpSections() {
      const sectionFiles = [
        { title: 'About LoLLMs', file: 'lollms-context.md' },
        { title: 'Getting Started', file: 'getting-started.md' },
        { title: 'Uploading Files', file: 'uploading-files.md' },
        { title: 'Sending Images', file: 'sending-images.md' },
        { title: 'Using Code Interpreter', file: 'code-interpreter.md' },
        { title: 'Internet Search', file: 'internet-search.md' },
        { title: 'Text Generation', file: 'text-generation.md' },
        { title: 'Image Generation', file: 'image-generation.md' },
        { title: 'Music Generation', file: 'music-generation.md' },
        { title: 'Managing Personalities', file: 'managing-personalities.md' },
        { title: 'Troubleshooting', file: 'troubleshooting.md' }
      ];

      for (const section of sectionFiles) {
        const content = await this.loadMarkdownFile(section.file);
        this.helpSections.push({
          title: section.title,
          content: content
        });
      }
    }
  },
  mounted() {
    this.loadHelpSections();
  }
};
</script>

<style scoped>
/* General Layout */
.help-view {
  @apply flex flex-col md:flex-row;
}

/* Sidebar Styling */
.left-bar {
  scrollbar-width: thin;
  scrollbar-color: #888 #f1f1f1;
}

.left-bar::-webkit-scrollbar {
  width: 10px;
}

.left-bar::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 10px;
}

.left-bar::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 10px;
  border: 2px solid #f1f1f1;
}

.left-bar::-webkit-scrollbar-thumb:hover {
  background: #555;
}

/* Main Content Styling */
.main-content {
  @apply transition-all duration-500;
}

.big-card {
  @apply transform transition-all duration-300 hover:shadow-2xl;
}

.help-content {
  @apply p-4;
}

/* Scrollbar Styling for Main Content */
.main-content::-webkit-scrollbar,
.help-content::-webkit-scrollbar {
  width: 12px;
}

.main-content::-webkit-scrollbar-track,
.help-content::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 12px;
}

.main-content::-webkit-scrollbar-thumb,
.help-content::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 12px;
  border: 3px solid #f1f1f1;
}

.main-content::-webkit-scrollbar-thumb:hover,
.help-content::-webkit-scrollbar-thumb:hover {
  background: #555;
}

/* Responsive Design */
@media (max-width: 768px) {
  .left-bar {
    @apply w-64 fixed top-0 left-0 h-screen z-20 transform -translate-x-full md:translate-x-0 md:w-72;
  }
  .main-content {
    @apply ml-0 p-6;
  }
  .left-bar.open {
    @apply translate-x-0;
  }
  .big-card {
    @apply p-6;
  }
  h1 {
    @apply text-4xl;
  }
}
</style>