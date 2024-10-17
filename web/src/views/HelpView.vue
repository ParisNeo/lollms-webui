<template>
  <div class="help-view background-color p-6 w-full">
    <div class="big-card w-full">
      <h1 class="text-4xl md:text-5xl font-bold text-gray-800 dark:text-gray-100 mb-6">LoLLMs Help</h1>
      <div class="help-sections-container">
        <div class="help-sections space-y-4">
          <div v-for="(section, index) in helpSections" :key="index" class="help-section message">
            <h2 @click="toggleSection(index)" class="menu-item cursor-pointer flex justify-between items-center">
              {{ section.title }}
              <span class="toggle-icon">{{ section.isOpen ? '▼' : '▶' }}</span>
            </h2>
            <div v-if="section.isOpen" class="help-content mt-4">
              <div v-html="section.content" class="prose dark:prose-invert"></div>
            </div>
          </div>
        </div>
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
      helpSections: []
    }
  },
  methods: {
    toggleSection(index) {
      this.helpSections[index].isOpen = !this.helpSections[index].isOpen;
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
        { title: 'Internet Search', file: 'internet-search.md' }
      ];

      for (const section of sectionFiles) {
        const content = await this.loadMarkdownFile(section.file);
        this.helpSections.push({
          title: section.title,
          content: content,
          isOpen: false
        });
      }
    }
  },
  mounted() {
    this.loadHelpSections();
  }
}
</script>

<style scoped>
.help-view {
  @apply min-h-screen;
}

.big-card {
  @apply bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8 mx-auto;
}

.help-sections-container {
  @apply max-h-[70vh] overflow-y-auto pr-4;
}

.help-section {
  @apply transition-all duration-300 ease-in-out;
}

.help-content {
  @apply text-gray-600 dark:text-gray-300;
}

/* Cute scrollbar styles */
.help-sections-container::-webkit-scrollbar {
  width: 12px;
}

.help-sections-container::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 10px;
}

.help-sections-container::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 10px;
  border: 3px solid #f1f1f1;
}

.help-sections-container::-webkit-scrollbar-thumb:hover {
  background: #555;
}

/* For Firefox */
.help-sections-container {
  scrollbar-width: thin;
  scrollbar-color: #888 #f1f1f1;
}
</style>
