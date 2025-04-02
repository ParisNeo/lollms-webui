<template>
  <!-- Use theme's base background gradient -->
  <div class="help-view background-color min-h-screen  min-w-screen flex overflow-hidden">

    <!-- Left Sidebar -->
    <!-- Apply panel colors, shadow, and theme scrollbar -->
    <div class="help-left-bar w-72 panels-color shadow-lg fixed h-screen overflow-y-auto scrollbar transition-all duration-300 ease-in-out md:w-80 z-10">
      <div class="p-4 sm:p-6">
        <!-- Use theme's h2 styling -->
        <h2 class="text-2xl font-semibold text-blue-700 dark:text-blue-200 mb-6 border-b border-blue-300 dark:border-blue-600 pb-2 flex items-center">
          <i data-feather="folder" class="w-5 h-5 mr-3 flex-shrink-0"></i>
          <span>Help Topics</span>
        </h2>
        <ul class="space-y-2">
          <li v-for="(section, index) in helpSections" :key="index">
            <!-- Use button/link styling from theme, including active state -->
            <a
              @click.prevent="selectSection(index)"
              :class="[
                'nav-button', // Base button style from theme
                'block w-full text-left', // Ensure block layout
                'transition-all duration-200 ease-in-out',
                { 'nav-button-active': selectedSection === index } // Active state from theme
              ]"
              href="#"
              role="button"
            >
              {{ section.title }}
            </a>
          </li>
        </ul>
      </div>
    </div>

    <!-- Main Content -->
    <!-- Apply theme scrollbar -->
    <div class="main-content ml-72 md:ml-80 flex-1 overflow-y-auto h-screen scrollbar">
        <div class="p-6 sm:p-10 flex justify-center items-start">
             <!-- Use card styling from theme for the main container -->
            <div class="card w-full max-w-5xl mx-auto flex flex-col min-h-[calc(100vh-5rem)]"> <!-- Adjust min-height as needed -->
                <!-- Use theme's h1 styling -->
                <h1 class="text-3xl md:text-4xl font-bold text-blue-800 dark:text-blue-100 mb-6 border-b border-blue-300 dark:border-blue-600 pb-3 flex items-center">
                <i data-feather="help-circle" class="w-7 h-7 mr-3 flex-shrink-0"></i>
                <span>LoLLMs Help Center</span>
                </h1>
                <!-- Apply theme's prose styling for markdown content -->
                <div
                class="help-content flex-1 prose-blue max-w-none transition-opacity duration-300"
                v-html="selectedContent"
                ></div>
            </div>
        </div>
    </div>
  </div>
</template>

<script>
import { marked } from 'marked';
import feather from 'feather-icons';
import { nextTick } from 'vue';
// Assuming highlight.js is imported globally or properly configured
// import hljs from 'highlight.js';
// import 'highlight.js/styles/stackoverflow-light.css'; // Import light theme
// import 'highlight.js/styles/stackoverflow-dark.css'; // Import dark theme - ideally load dynamically

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
      // Basic sanitization placeholder - consider a more robust library like DOMPurify
      const rawHtml = this.helpSections[this.selectedSection]?.content || '<p class="text-blue-600 dark:text-blue-400">Select a topic from the sidebar to view help content.</p>';
      return rawHtml;
    }
  },
  methods: {
    selectSection(index) {
      this.selectedSection = index;
      nextTick(() => {
          feather.replace(); // Replace icons if content changes might add them
          // Optional: Add code block highlighting if needed
          this.$el.querySelectorAll('.help-content pre code.hljs').forEach((block) => {
             // If using marked's highlight function with hljs, it might already be done.
             // If not, uncomment the line below. Ensure hljs is available.
             // hljs.highlightElement(block);
          });
      });
    },
    async loadMarkdownFile(filename) {
      try {
        const response = await fetch(`/help/${filename}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const markdown = await response.text();
        // Configure marked (optional, e.g., for syntax highlighting class)
        marked.setOptions({
            highlight: function(code, lang) {
                 // Check if hljs is loaded and language is valid
                if (typeof hljs !== 'undefined' && hljs.getLanguage(lang)) {
                    try {
                        // Add 'hljs' class for base styling + language class
                        return `<pre class="hljs"><code>${hljs.highlight(code, { language: lang, ignoreIllegals: true }).value}</code></pre>`;
                    } catch (__) {}
                }
                 // Fallback for no language or hljs not found
                return `<pre class="hljs"><code>${code}</code></pre>`; // Basic escaping
            },
             langPrefix: 'hljs language-', // CSS class prefix for fenced code blocks
             pedantic: false,
             gfm: true,
             breaks: false,
             sanitize: false, // IMPORTANT: Consider using DOMPurify after marked if markdown is user-generated
             smartLists: true,
             smartypants: false,
             xhtml: false
        });
        return marked(markdown);
      } catch (error) {
        console.error('Error loading markdown file:', filename, error);
        return `<p class="text-red-500 dark:text-red-400">Error loading help content for ${filename}. Please check the file exists in the public/help folder.</p>`;
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
        // Add more sections here
      ];

      const loadedSections = [];
      for (const section of sectionFiles) {
        const content = await this.loadMarkdownFile(section.file);
        loadedSections.push({
          title: section.title,
          content: content
        });
      }
      this.helpSections = loadedSections;
      // Select first section content after loading
      if (this.helpSections.length > 0) {
        this.selectSection(0);
      }
    }
  },
  mounted() {
    this.loadHelpSections().then(() => {
        nextTick(() => {
            feather.replace();
        });
    });
  },
   updated() {
    // Ensure icons are replaced if the component updates for other reasons
    nextTick(() => {
      feather.replace();
    });
  }
};
</script>

<style>
/* Keep custom scrollbar styles if they differ significantly from the theme's default .scrollbar */
/* Otherwise, remove this style block and rely on the .scrollbar class from theme.css */

/* Styling for generated HTML from markdown if prose-blue needs overrides */
/* These styles refine or override prose-blue if necessary */


/* Add highlight.js theme styles here or import them */
/* Example for stackoverflow-light / dark */
/* @import 'highlight.js/styles/stackoverflow-light.css'; */
/* .dark @import 'highlight.js/styles/stackoverflow-dark.css'; */

</style>