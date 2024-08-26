<!-- ToolbarButton.vue -->
<template>
    <button 
      class="text-lg hover:text-secondary duration-75 active:scale-90 p-2 cursor-pointer"
      :title="title"
      @click="$emit('click')"
    >
      <svg class="w-6 h-6" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round">
        <g v-html="iconPath"></g>
      </svg>
    </button>
  </template>
  
  <script>
  export default {
    props: {
      icon: {
        type: String,
        required: true
      },
      title: {
        type: String,
        required: true
      }
    },
    computed: {
      iconPath() {
        return this.getIconPath()
      }
    },
    methods: {
      getIconPath() {
        // Your switch statement remains the same
        switch (this.icon) {
          case 'x':
            return '<path d="M18 6L6 18M6 6l12 12"/>'
          case 'check':
            return '<path d="M20 6L9 17l-5-5"/>'
          case 'code':
            return '<path d="M8 7l-5 5 5 5"/><path d="M16 7l5 5-5 5"/><line x1="10" y1="4" x2="14" y2="20"/>'
          case 'python':
            return '<path d="M12 2C5.4 2 6 4.5 6 4.5v2.8h6.5v1H4.5S2 7.7 2 12c0 4.3 2.5 4.2 2.5 4.2h2.3v-2.5c0-2.5 2.2-2.5 2.2-2.5h6.1c2.3 0 2.2-2.2 2.2-2.2V5c0-2.8-2.9-3-5.8-3zm-3.5 1.7c.5 0 1 .4 1 1s-.4 1-1 1-1-.4-1-1 .4-1 1-1z" fill="currentColor"/><path d="M12 22c6.6 0 6-2.5 6-2.5v-2.8h-6.5v-1H19.5s2.5-.6 2.5-4.9c0-4.3-2.5-4.2-2.5-4.2h-2.3v2.5c0 2.5-2.2 2.5-2.2 2.5H8.9c-2.3 0-2.2 2.2-2.2 2.2V19c0 2.8 2.9 3 5.8 3zm3.5-1.7c-.5 0-1-.4-1-1s.4-1 1-1 1 .4 1 1-.4 1-1 1z" fill="currentColor"/>'
          case 'js':
            return '<text x="12" y="17" font-family="Arial, sans-serif" font-size="14" font-weight="bold" text-anchor="middle" fill="currentColor">JS</text>'
          case 'typescript':
            return '<text x="12" y="17" font-family="Arial, sans-serif" font-size="14" font-weight="bold" text-anchor="middle" fill="currentColor">TS</text>'
          case 'braces':
            return '<path d="M7 7H4a2 2 0 0 0-2 2v6a2 2 0 0 0 2 2h3m10-10h3a2 2 0 0 1 2 2v6a2 2 0 0 1-2 2h-3"/>'
          case 'cplusplus':
          case 'c++':
            return '<text x="12" y="17" font-family="Arial, sans-serif" font-size="10" font-weight="bold" text-anchor="middle" fill="currentColor">C++</text>'
          case 'csharp':
            return '<text x="12" y="17" font-family="Arial, sans-serif" font-size="14" font-weight="bold" text-anchor="middle" fill="currentColor">C#</text>'
          case 'go':
            return '<text x="12" y="17" font-family="Arial, sans-serif" font-size="14" font-weight="bold" text-anchor="middle" fill="currentColor">Go</text>'
          case 'r-project':
            return '<text x="12" y="17" font-family="Arial, sans-serif" font-size="16" font-weight="bold" text-anchor="middle" fill="currentColor">R</text>'
          case 'rust':
            return '<path d="M12 2L2 7v10l10 5 10-5V7L12 2z M12 22v-6 M22 7l-10 5-10-5 M2 17l10-5 10 5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
          case 'swift':
            return '<path d="M21 12c0-4.4-3.6-8-8-8s-8 3.6-8 8 3.6 8 8 8c1.4 0 2.8-.4 4-1 M14 9c-1.7-1.7-3.7-2.6-5.5-2.5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
          case 'kotlin':
            return '<path d="M2 2v20h20L2 2z M2 22L22 2" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
          case 'java':
            return '<path fill="currentColor" d="M8.5 18.5c0 0-1.3.7.9 1 2.7.3 4.1.3 7-.3 0 0 .8.5 1.9.9-6.7 2.9-15.2-.7-9.8-1.6zm-1-3.5c0 0-1.5 1.1.8 1.3 2.9.3 5.2.3 9.1-.4 0 0 .6.6 1.4.9-7.9 2.3-16.7.2-11.3-1.8zm9.2-6.5c1.7 1.9-.4 3.6-.4 3.6s4.2-2.2 2.3-4.9c-1.8-2.5-3.2-3.8 4.3-8.1 0 0-11.8 3-6.2 9.4zm4.9 12.4c0 0 1 .8-1.1 1.4-3.9 1.2-16.3 1.5-19.7.1-1.2-.5 1.1-1.3 1.8-1.4.8-.2 1.2-.1 1.2-.1-1.4-1-9 1.9-3.8 2.7 14.1 2.3 25.8-1 21.6-2.7zm-15.4-9.3c0 0-6.3 1.5-2.2 2 1.7.2 5.1.2 8.3-.1 2.6-.2 5.2-.7 5.2-.7s-.9.4-1.6.8c-6.4 1.7-18.8.9-15.2-.8 3-1.4 5.5-1.2 5.5-1.2zm12.4 6.9c6.5-3.4 3.5-6.6 1.4-6.2-.5.1-.7.2-.7.2s.2-.3.6-.4c4.2-1.5 7.4 4.3-1.4 6.6 0-.1.1-.1.1-.2z"/>'

          case 'html5':
            return '<path fill="currentColor" d="M3 2l1.5 17L12 22l7.5-3L21 2H3zm4.5 6h9l-.3 3H8.4l.2 2h8.5l-.6 6.5L12 21l-4.5-1.5L7 16h2.2l.2 2.2 2.6.7 2.6-.7.4-3.7H7.3L6.5 8z"/>'
          case 'css3':
            return '<path d="M4 3l1.5 17L12 22l6.5-2L20 3H4zm3.5 7h9l-.3 3H8.4l.2 2h8l-.5 5.5-3.8 1.3-3.8-1.3-.3-3H5.5l.5 5.5L12 22l6-2 .8-9H7.5l.3-3z" fill="currentColor"/>'
          case 'vuejs':
            return '<path d="M2 3l10 18L22 3h-4l-6 10.5L6 3H2z" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
          case 'react':
            return '<circle cx="12" cy="12" r="2.5" fill="currentColor"/><path d="M12 9.5c1.8-2.3 3.7-3.8 5.5-3.8 1.3 0 2.4.6 3.1 1.7 1.1 1.9.4 4.5-1.8 7.1M12 14.5c-1.8 2.3-3.7 3.8-5.5 3.8-1.3 0-2.4-.6-3.1-1.7-1.1-1.9-.4-4.5 1.8-7.1M5.5 6.5c1.9-1.1 4.5-.4 7.1 1.8M18.5 17.5c-1.9 1.1-4.5.4-7.1-1.8" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
          case 'angular':
            return '<path d="M12 2L3 6l1.5 13L12 22l7.5-3L21 6L12 2z M12 2v20 M3 6l9 4 M21 6l-9 4" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'

          case 'xml':
            return '<path d="M16 3l-4 18M8 8l-4 4 4 4M16 8l4 4-4 4" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'

          case 'json':
            return '<path d="M4 6h16M4 10h16M4 14h10M4 18h6" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><circle cx="18" cy="18" r="2" fill="currentColor"/>'
          case 'yaml':
            return '<path d="M3 6h18M3 10h18M3 14l4 4M11 14l-4 4M17 14l4 4" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
          case 'markdown':
            return '<path d="M3 3h18v18H3zM5 7v10M9 7v10M9 12l3-3 3 3M15 7l4 5-4 5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
          case 'latex':
            return '<text x="12" y="17" font-family="Times New Roman, serif" font-size="14" font-style="italic" font-weight="bold" text-anchor="middle" fill="currentColor">TEX</text>'

          case 'bash':
            return '<path d="M3 3h18v18H3zM6 7l4 4-4 4M12 15h6" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'

          case 'powershell':
            return '<path d="M3 3h18v18H3zM6 7l6 5-6 5M13 17h5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'

          case 'perl':
            return '<path d="M12 2C6.477 2 2 6.477 2 12s4.477 10 10 10 10-4.477 10-10S17.523 2 12 2z" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M12 7v10M7 12h10" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'

          case 'mermaid':
            return '<circle cx="5" cy="12" r="3" fill="currentColor"/><circle cx="19" cy="12" r="3" fill="currentColor"/><circle cx="12" cy="5" r="3" fill="currentColor"/><circle cx="12" cy="19" r="3" fill="currentColor"/><path d="M5 12h14M12 5v14" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>'

          case 'graphviz':
            return '<circle cx="6" cy="6" r="3" fill="currentColor"/><circle cx="18" cy="6" r="3" fill="currentColor"/><circle cx="6" cy="18" r="3" fill="currentColor"/><circle cx="18" cy="18" r="3" fill="currentColor"/><path d="M6 9v6M18 9v6M9 6h6M9 18h6" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>'

          case 'plantuml':
            return '<path d="M3 3h18v18H3z" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M7 7h10v4H7zM7 15h10M12 11v7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
          case 'sql':
            return '<path d="M3 5h18M3 10h18M3 15h18M3 20h18M7 5v15M17 5v15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'

          case 'mongodb':
            return '<path d="M12 2v20M12 2c-3.5 0-7 3-7 8s3.5 8 7 8 7-3 7-8-3.5-8-7-8z" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M12 18c1.5-1 2-2.5 2-4" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'

            
          case 'mathFunction':
            return '<path d="M3 20h18M3 4v16M3 12h4c3 0 4-3 4-3s1 6 3 6h7" fill="none" stroke="currentColor" stroke-width="2"/>'
          case 'terminal':
            return '<rect x="2" y="4" width="20" height="16" rx="2" ry="2" fill="none"/><path d="M6 8l4 4-4 4M12 16h6"/>'
          case 'edit':
            return '<path d="M17 3a2.85 2.85 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5L17 3z"/>'
          case 'copy':
            return '<rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>'
          case 'send':
            return '<path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z"/>'
          case 'globe':
            return '<circle cx="12" cy="12" r="10"/><path d="M2 12h20M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>'
          case 'fastForward':
            return '<polygon points="13 19 22 12 13 5 13 19"/><polygon points="2 19 11 12 2 5 2 19"/>'
          case 'sendSimple':
            return '<path d="M22 2L11 13M22 2l-7 20-4-9"/>'
          default:
            return ''
        }

      }
    }
  }
  </script>
  