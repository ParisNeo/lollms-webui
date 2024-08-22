<!-- ToolbarButton.vue -->
<template>
    <button 
      class="text-lg hover:text-secondary duration-75 active:scale-90 p-2 cursor-pointer"
      :title="title"
      @click="$emit('click')"
    >
      <svg class="w-6 h-6" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
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
            return '<path d="M16 18l6-6-6-6M8 6l-6 6 6 6"/>'
          case 'python':
            return '<path d="M12 9H5a2 2 0 0 0-2 2v4a2 2 0 0 0 2 2h3m6-8h7a2 2 0 0 1 2 2v4a2 2 0 0 1-2 2h-3"/><path d="M8 9v8m8-8v8"/>'
          case 'js':
            return '<path d="M20 4l-2 14.5-6 2-6-2L4 4z"/><path d="M7.5 8h3v8l-2-1"/><path d="M16.5 8H13v8l2-1"/>'
          case 'braces':
            return '<path d="M7 7H4a2 2 0 0 0-2 2v6a2 2 0 0 0 2 2h3m10-10h3a2 2 0 0 1 2 2v6a2 2 0 0 1-2 2h-3"/>'
          case 'cplusplus':
            return '<path d="M16 9h2m-1-1v2m3-2h2m-1-1v2M20 4L4 20"/><path d="M4 4l16 16"/>'
          case 'html5':
            return '<path d="M13 16l5-5-5-5M11 8L6 13l5 5"/>'
          case 'mathFunction':
            return '<path d="M4 4h16v16H4z"/><path d="M9 8v8m3-8v8m3-8v8"/>'
          case 'terminal':
            return '<path d="M4 17l6-6-6-6m8 14h8"/>'
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
  