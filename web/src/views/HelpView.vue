<template>
  <div class="help-view bg-gradient-to-br from-gray-100 to-blue-50 dark:from-gray-900 dark:to-gray-800 min-h-screen flex">
    <!-- Left Sidebar -->
    <div class="left-bar w-64 bg-white dark:bg-gray-800 shadow-lg p-6 fixed h-full overflow-y-auto transition-all duration-300 md:w-72 lg:w-80">
      <h2 class="text-2xl font-semibold text-gray-800 dark:text-gray-100 mb-6">Help Topics</h2>
      <ul class="space-y-3">
        <li v-for="(section, index) in helpSections" :key="index">
          <a @click.prevent="scrollToSection(index)" class="block p-3 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-blue-100 dark:hover:bg-gray-700 hover:text-blue-600 dark:hover:text-blue-400 transition-colors duration-200 cursor-pointer">
            {{ section.title }}
          </a>
        </li>
      </ul>
    </div>

    <!-- Main Content -->
    <div class="main-content ml-64 md:ml-72 lg:ml-80 flex-1 p-8">
      <div class="big-card bg-white dark:bg-gray-900 rounded-xl shadow-md p-8 max-w-4xl mx-auto">
        <h1 class="text-4xl md:text-5xl font-bold text-gray-800 dark:text-gray-100 mb-8 flex items-center">
          <span class="mr-2">📚</span> LoLLMs Help
        </h1>
        <div class="help-sections-container space-y-6">
          <div v-for="(section, index) in helpSections" :key="index" :id="'section-' + index" class="help-section bg-gray-50 dark:bg-gray-800 rounded-lg p-6 transition-all duration-300">
            <h2 @click="toggleSection(index)" class="menu-item cursor-pointer flex justify-between items-center text-xl font-semibold text-gray-800 dark:text-gray-200 hover:text-blue-600 dark:hover:text-blue-400">
              {{ section.title }}
              <span class="toggle-icon text-gray-500 dark:text-gray-400">{{ section.isOpen ? '▼' : '▶' }}</span>
            </h2>
            <transition name="fade">
              <div v-if="section.isOpen" class="help-content mt-4 text-gray-600 dark:text-gray-300 prose dark:prose-invert">
                <div v-html="section.content"></div>
              </div>
            </transition>
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
    };
  },
  methods: {
    toggleSection(index) {
      this.helpSections[index].isOpen = !this.helpSections[index].isOpen;
    },
    scrollToSection(index) {
      this.helpSections.forEach((section, i) => {
        section.isOpen = i === index; // Open only the clicked section
      });
      const element = document.getElementById(`section-${index}`);
      if (element) {
        element.scrollIntoView({ behavior: 'smooth' });
      }
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
          content: content,
          isOpen: false
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
  width: 8px;
}

.left-bar::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 10px;
}

.left-bar::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 10px;
}

.left-bar::-webkit-scrollbar-thumb:hover {
  background: #555;
}

/* Main Content Styling */
.main-content {
  @apply transition-all duration-300;
}

.big-card {
  @apply transform transition-all duration-300 hover:shadow-xl;
}

.help-sections-container {
  @apply max-h-[70vh] overflow-y-auto;
}

.help-section {
  @apply hover:bg-gray-100 dark:hover:bg-gray-700;
}

/* Fade Transition */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

/* Scrollbar Styling for Main Content */
.help-sections-container::-webkit-scrollbar {
  width: 10px;
}

.help-sections-container::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 10px;
}

.help-sections-container::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 10px;
  border: 2px solid #f1f1f1;
}

.help-sections-container::-webkit-scrollbar-thumb:hover {
  background: #555;
}

/* Responsive Design */
@media (max-width: 768px) {
  .left-bar {
    @apply w-full fixed top-0 left-0 h-auto z-10 transform -translate-x-full md:translate-x-0 md:w-64;
  }
  .main-content {
    @apply ml-0;
  }
  .left-bar.open {
    @apply translate-x-0;
  }
}
</style>