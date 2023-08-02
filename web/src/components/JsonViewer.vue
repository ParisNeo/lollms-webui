
<template>
    <pre class="json-viewer">
      <template v-if="isObject">
        <span @click="toggleCollapsed" class="toggle-icon">
          <i v-if="collapsed" class="fas fa-plus-circle"></i>
          <i v-else class="fas fa-minus-circle"></i>
        </span>
      </template>
      {{ formattedJson }}
    </pre>
  </template>
  
  <script>
  export default {
    props: {
      data: {
        type: [Object, Array],
        required: true,
      },
    },
    data() {
      return {
        collapsed: false,
      };
    },
    computed: {
      formattedJson() {
        return this.collapsed ? '{}' : JSON.stringify(this.data, null, 2);
      },
      isObject() {
        return typeof this.data === 'object' && this.data !== null;
      },
    },
    methods: {
      toggleCollapsed() {
        this.collapsed = !this.collapsed;
      },
    },
  };
  </script>
  
  <style>
  .json-viewer {
    max-height: 300px;
    overflow-y: auto;
    padding: 10px;
    background-color: #f1f1f1;
    border: 1px solid #ccc;
    border-radius: 4px;
  }
  
  .toggle-icon {
    cursor: pointer;
    margin-right: 0.25rem;
  }
  
  .toggle-icon i {
    color: #4a5568;
  }
  
  .toggle-icon i:hover {
    color: #1a202c;
  }
  </style>
  