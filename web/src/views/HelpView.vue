<template>
  <div class="min-h-screen w-full bg-gradient-to-br from-blue-100 to-purple-100 dark:from-blue-900 dark:to-purple-900 overflow-y-auto">
    <div class="container mx-auto px-4 py-8 relative z-10">
      <header class="text-center mb-12 sticky top-0 bg-white dark:bg-gray-800 bg-opacity-90 dark:bg-opacity-90 backdrop-filter backdrop-blur-lg p-4 rounded-b-lg shadow-md">
        <h1 class="text-5xl md:text-6xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600 dark:from-blue-400 dark:to-purple-400 mb-2 animate-glow">
          LoLLMs Help Documentation
        </h1>
        <p class="text-2xl text-gray-600 dark:text-gray-300 italic">
          "One tool to rule them all"
        </p>
      </header>

      <nav class="bg-white dark:bg-gray-800 shadow-md rounded-lg p-6 mb-8 animate-fade-in sticky top-32 max-h-[calc(100vh-8rem)] overflow-y-auto">
        <h2 class="text-3xl font-semibold mb-4 text-gray-800 dark:text-gray-200">Table of Contents</h2>
        <ul class="space-y-2">
          <li v-for="section in sections" :key="section.id" class="ml-4">
            <a :href="`#${section.id}`" @click="scrollToSection(section.id)" class="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 hover:underline transition-colors duration-200">{{ section.title }}</a>
            <ul v-if="section.subsections" class="ml-4 mt-2 space-y-1">
              <li v-for="subsection in section.subsections" :key="subsection.id">
                <a :href="`#${subsection.id}`" @click="scrollToSection(subsection.id)" class="text-blue-500 dark:text-blue-300 hover:text-blue-700 dark:hover:text-blue-200 hover:underline transition-colors duration-200">{{ subsection.title }}</a>
              </li>
            </ul>
          </li>
        </ul>
      </nav>

      <main class="bg-white dark:bg-gray-800 shadow-md rounded-lg p-6 animate-fade-in">
        <section v-for="section in sections" :key="section.id" :id="section.id" class="mb-12">
          <h2 class="text-4xl font-semibold mb-6 text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600 dark:from-blue-400 dark:to-purple-400">{{ section.title }}</h2>
          <div v-html="section.content" class="prose dark:prose-invert max-w-none"></div>

          <div v-if="section.subsections" class="mt-8">
            <section v-for="subsection in section.subsections" :key="subsection.id" :id="subsection.id" class="mb-8">
              <h3 class="text-3xl font-semibold mb-4 text-gray-700 dark:text-gray-300">{{ subsection.title }}</h3>
              <div v-html="subsection.content" class="prose dark:prose-invert max-w-none"></div>
            </section>
          </div>
        </section>
      </main>

      <footer class="mt-12 pt-8 border-t border-gray-300 dark:border-gray-700 animate-fade-in">
        <h2 class="text-3xl font-semibold mb-6 text-center text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600 dark:from-blue-400 dark:to-purple-400">Contact</h2>
        <div class="flex flex-wrap justify-center gap-6 mb-8">
          <a v-for="(link, index) in contactLinks" :key="index" :href="link.url" target="_blank" class="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 hover:underline transition-colors duration-200">
            {{ link.text }}
          </a>
        </div>
        <p class="text-center font-bold text-2xl text-gray-700 dark:text-gray-300">See ya!</p>
      </footer>
    </div>

    <!-- Falling stars background -->
    <div class="fixed inset-0 pointer-events-none overflow-hidden">
      <div v-for="n in 50" :key="n" class="absolute animate-fall"
           :style="{
             left: `${Math.random() * 100}%`,
             top: `-20px`,
             animationDuration: `${3 + Math.random() * 7}s`,
             animationDelay: `${Math.random() * 5}s`
           }">
        <svg class="w-2 h-2 text-yellow-300" fill="currentColor" viewBox="0 0 20 20">
          <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
        </svg>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      sections: [
        {
          id: 'introduction',
          title: 'Introduction',
          content: `
            <p class="mb-4 text-gray-700 dark:text-gray-300">LoLLMs (Lord of Large Language Multimodal Systems) is a powerful and versatile AI system designed to handle a wide range of tasks. Developed by ParisNeo, a computer geek passionate about AI, LoLLMs aims to be the ultimate tool for AI-assisted work and creativity.</p>
            <p class="mb-4 text-gray-700 dark:text-gray-300">With its advanced capabilities in natural language processing, multimodal understanding, and code interpretation, LoLLMs can assist users in various domains, from content creation to complex problem-solving.</p>
          `
        },
        {
          id: 'key-features',
          title: 'Key Features',
          content: `
            <ul class="list-disc list-inside mb-4 text-gray-700 dark:text-gray-300">
              <li>Advanced language understanding and generation</li>
              <li>Multimodal capabilities (text, images, and more)</li>
              <li>Built-in code interpreter for various programming languages</li>
              <li>Internet search integration for up-to-date information</li>
              <li>Customizable personalities for specialized tasks</li>
              <li>File handling and analysis capabilities</li>
            </ul>
          `
        },
        {
          id: 'getting-started',
          title: 'Getting Started',
          content: `
            <p class="mb-4 text-gray-700 dark:text-gray-300">To get started with LoLLMs, follow these steps:</p>
            <ol class="list-decimal list-inside mb-4 text-gray-700 dark:text-gray-300">
              <li>Install LoLLMs on your system (refer to the installation guide)</li>
              <li>Configure your preferences and API keys if necessary</li>
              <li>Choose a personality or mode that fits your task</li>
              <li>Start interacting with LoLLMs through the chat interface</li>
            </ol>
            <p class="mb-4 text-gray-700 dark:text-gray-300">For detailed installation instructions, visit our <a href="#" class="text-blue-600 dark:text-blue-400 hover:underline">installation guide</a>.</p>
          `
        },
        {
          id: 'personalities',
          title: 'Personalities',
          content: `
            <p class="mb-4 text-gray-700 dark:text-gray-300">LoLLMs offers various personalities to cater to different tasks and user needs. Each personality is optimized for specific use cases, ensuring the best possible assistance.</p>
          `,
          subsections: [
            {
              id: 'document-summarization',
              title: 'Document Summarization',
              content: `
                <p class="mb-4 text-gray-700 dark:text-gray-300">The Document Summarization personality, also known as <code class="bg-gray-200 dark:bg-gray-700 rounded px-1">docs_zipper</code>, specializes in condensing large documents into concise summaries while maintaining context and key information.</p>
                <p class="mb-4 text-gray-700 dark:text-gray-300">Key features:</p>
                <ul class="list-disc list-inside mb-4 text-gray-700 dark:text-gray-300">
                  <li>Handles multiple document formats (PDF, DOCX, TXT, etc.)</li>
                  <li>Provides customizable summary lengths</li>
                  <li>Extracts main ideas and key points</li>
                  <li>Maintains document structure in summaries</li>
                </ul>
                <p><a href="/help/personalities/documents summary/index.html" class="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 hover:underline transition-colors duration-200">Learn more about Document Summarization</a></p>
              `
            },
            {
              id: 'code-interpreter',
              title: 'Code Interpreter',
              content: `
                <p class="mb-4 text-gray-700 dark:text-gray-300">The Code Interpreter personality allows LoLLMs to understand, analyze, and execute code in various programming languages.</p>
                <p class="mb-4 text-gray-700 dark:text-gray-300">Key features:</p>
                <ul class="list-disc list-inside mb-4 text-gray-700 dark:text-gray-300">
                  <li>Supports multiple programming languages</li>
                  <li>Provides code explanations and suggestions</li>
                  <li>Assists in debugging and optimizing code</li>
                  <li>Can generate code snippets based on natural language descriptions</li>
                </ul>
              `
            }
          ]
        },
        {
          id: 'advanced-features',
          title: 'Advanced Features',
          content: `
            <p class="mb-4 text-gray-700 dark:text-gray-300">Explore the advanced capabilities of LoLLMs:</p>
            <ul class="list-disc list-inside mb-4 text-gray-700 dark:text-gray-300">
              <li>Internet Search Integration: Access up-to-date information by using the "send message with internet search" feature</li>
              <li>File Handling: Upload and analyze various file types, including images and documents</li>
              <li>SVG and Diagram Generation: Create visual representations using SVG, Graphviz, and Mermaid</li>
              <li>HTML and JavaScript Generation: Develop interactive web content directly through LoLLMs</li>
              <li>Python Code Execution: Run Python scripts for data analysis and more</li>
            </ul>
          `
        },
        {
          id: 'use-cases',
          title: 'Use Cases',
          content: `
            <p class="mb-4 text-gray-700 dark:text-gray-300">LoLLMs can be applied to a wide range of tasks, including:</p>
            <ul class="list-disc list-inside mb-4 text-gray-700 dark:text-gray-300">
              <li>Content Creation and Editing</li>
              <li>Data Analysis and Visualization</li>
              <li>Code Development and Debugging</li>
              <li>Research and Information Gathering</li>
              <li>Language Translation and Localization</li>
              <li>Creative Writing and Brainstorming</li>
              <li>Technical Documentation</li>
              <li>Educational Support and Tutoring</li>
            </ul>
          `
        },
        {
          id: 'troubleshooting',
          title: 'Troubleshooting',
          content: `
            <p class="mb-4 text-gray-700 dark:text-gray-300">If you encounter any issues while using LoLLMs, try the following steps:</p>
            <ol class="list-decimal list-inside mb-4 text-gray-700 dark:text-gray-300">
              <li>Check your internet connection</li>
              <li>Verify that you're using the latest version of LoLLMs</li>
              <li>Clear your browser cache (if using the web interface)</li>
              <li>Review the error messages for specific information</li>
              <li>Consult the <a href="#" class="text-blue-600 dark:text-blue-400 hover:underline">FAQ section</a> for common issues and solutions</li>
            </ol>
            <p class="mb-4 text-gray-700 dark:text-gray-300">If problems persist, please reach out to our support team through one of the contact methods listed below.</p>
          `
        }
      ],
      contactLinks: [
        { text: 'Email', url: 'mailto:parisneoai@gmail.com' },
        { text: 'Twitter', url: 'https://twitter.com/ParisNeo_AI' },
        { text: 'Discord', url: 'https://discord.gg/BDxacQmv' },
        { text: 'Sub-Reddit', url: 'https://www.reddit.com/r/lollms' },
        { text: 'Instagram', url: 'https://www.instagram.com/spacenerduino/' }
      ]
    };
  },
  methods: {
    scrollToSection(sectionId) {
      const element = document.getElementById(sectionId);
      if (element) {
        element.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    }
  }
};
</script>

<style>
@keyframes glow {
  0%, 100% { text-shadow: 0 0 5px rgba(59, 130, 246, 0.5), 0 0 10px rgba(147, 51, 234, 0.5); }
  50% { text-shadow: 0 0 20px rgba(59, 130, 246, 0.75), 0 0 30px rgba(147, 51, 234, 0.75); }
}

.animate-glow {
  animation: glow 3s ease-in-out infinite;
}

@keyframes fade-in {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.animate-fade-in {
  animation: fade-in 1s ease-out;
}

@keyframes fall {
  from { transform: translateY(-20px) rotate(0deg); opacity: 1; }
  to { transform: translateY(100vh) rotate(360deg); opacity: 0; }
}

.animate-fall {
  animation: fall linear infinite;
}

/* Smooth scrolling for the whole page */
html {
  scroll-behavior: smooth;
}

/* Custom scrollbar styles */
::-webkit-scrollbar {
  width: 10px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
}

::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 5px;
}

::-webkit-scrollbar-thumb:hover {
  background: #555;
}

/* Dark mode scrollbar */
.dark ::-webkit-scrollbar-track {
  background: #2d3748;
}

.dark ::-webkit-scrollbar-thumb {
  background: #4a5568;
}

.dark ::-webkit-scrollbar-thumb:hover {
  background: #718096;
}

/* Improved typography */
body {
  font-family: 'Inter', sans-serif;
  line-height: 1.6;
}

h1, h2, h3, h4, h5, h6 {
  font-family: 'Poppins', sans-serif;
  line-height: 1.2;
}

/* Add some hover effects to links */
a {
  transition: all 0.3s ease;
}

a:hover {
  transform: translateY(-2px);
}

/* Add a subtle shadow to main content sections */
main section {
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  transition: all 0.3s ease;
}

main section:hover {
  box-shadow: 0 8px 15px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

/* Improve code block styling */
code {
  font-family: 'Fira Code', monospace;
  padding: 2px 4px;
  border-radius: 4px;
  font-size: 0.9em;
}

/* Add a subtle gradient background to the page */
.bg-gradient-to-br {
  background-size: 400% 400%;
  animation: gradientBG 15s ease infinite;
}

@keyframes gradientBG {
  0% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
  100% {
    background-position: 0% 50%;
  }
}

/* Improve accessibility with focus styles */
a:focus, button:focus {
  outline: 2px solid #3b82f6;
  outline-offset: 2px;
}

/* Add a pulsing effect to the header */
header h1 {
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.05);
  }
  100% {
    transform: scale(1);
  }
}

/* Improve mobile responsiveness */
@media (max-width: 640px) {
  header h1 {
    font-size: 2rem;
  }
  
  nav {
    position: static;
    max-height: none;
  }
}

/* Add a nice transition effect when switching between light and dark mode */
body {
  transition: background-color 0.3s ease, color 0.3s ease;
}

/* Improve the appearance of lists */
ul, ol {
  padding-left: 1.5rem;
}

li {
  margin-bottom: 0.5rem;
}

/* Add a subtle animation to the footer */
footer {
  animation: fadeInUp 1s ease-out;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>