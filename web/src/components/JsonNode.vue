<!-- JsonNode.vue -->
<template>
    <div class="json-tree">
      <!-- Object -->
      <div v-if="isObject" class="tree-node">
        <div class="node-label" @click="toggle">
          <span class="toggle-icon">{{ expanded ? '▼' : '▶' }}</span>
          <span class="key">{{ label }}</span>
          <span class="bracket">{{ isArray ? '[' : '{' }}</span>
        </div>
        <div v-if="expanded" class="node-content">
          <div v-for="(value, key) in data" :key="key" class="node-item">
            <json-node 
              :data="value"
              :label="key"
              :depth="depth + 1"
            />
          </div>
        </div>
        <div v-if="expanded" class="bracket-close">{{ isArray ? ']' : '}' }}</div>
      </div>
  
      <!-- Primitive values -->
      <div v-else class="tree-leaf">
        <span class="key" v-if="label">{{ label }}:</span>
        <span :class="['value', getValueType(data)]">{{ formatValue(data) }}</span>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    name: 'JsonNode',
    props: {
      data: {
        required: true
      },
      label: {
        type: String,
        default: ''
      },
      depth: {
        type: Number,
        default: 0
      }
    },
    data() {
      return {
        expanded: true
      }
    },
    computed: {
      isObject() {
        return this.data !== null && typeof this.data === 'object'
      },
      isArray() {
        return Array.isArray(this.data)
      }
    },
    methods: {
      toggle() {
        this.expanded = !this.expanded
      },
      getValueType(value) {
        if (value === null) return 'null'
        return typeof value
      },
      formatValue(value) {
        if (value === null) return 'null'
        if (typeof value === 'string') return `"${value}"`
        return value
      }
    }
  }
  </script>
  
  <style scoped>
  .json-tree {
    font-family: monospace;
    font-size: 14px;
    line-height: 1.5;
    margin-left: 20px;
  }
  
  .tree-node {
    position: relative;
  }
  
  .node-label {
    cursor: pointer;
    padding: 2px 0;
  }
  
  .node-label:hover {
    background-color: #f0f0f0;
  }
  
  .toggle-icon {
    display: inline-block;
    width: 20px;
    color: #666;
  }
  
  .node-content {
    border-left: 1px dotted #ccc;
    margin-left: 7px;
    padding-left: 13px;
  }
  
  .key {
    color: #881391;
    margin-right: 5px;
  }
  
  .value {
    padding: 2px 4px;
  }
  
  .value.string { color: #22863a; }
  .value.number { color: #005cc5; }
  .value.boolean { color: #d73a49; }
  .value.null { color: #6a737d; }
  
  .bracket {
    color: #444;
    margin-left: 5px;
  }
  
  .bracket-close {
    color: #444;
    margin-left: 7px;
  }
  </style>
  