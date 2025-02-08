<template>
    <div class="json-tree">
      <!-- When data is an object -->
      <template v-if="isObject">
        <div v-for="(value, key) in data" :key="key" class="node">
          <div class="node-header" @click.stop="toggleCollapse(key)">
            <span class="toggle">
              <i :class="collapsedItems[key] ? 'fas fa-chevron-right' : 'fas fa-chevron-down'"></i>
            </span>
            <span class="key">{{ key }}:</span>
            <span v-if="debug" class="node-debug"> [key = {{ key }}]</span>
          </div>
          <div v-if="!collapsedItems[key]" class="node-children">
            <JsonNode :data="value" />
          </div>
        </div>
      </template>
  
      <!-- When data is an array -->
      <template v-else-if="isArray">
        <div v-for="(item, index) in data" :key="index" class="node">
          <div class="node-header" @click.stop="toggleCollapse(index)">
            <span class="toggle">
              <i :class="collapsedItems[index] ? 'fas fa-chevron-right' : 'fas fa-chevron-down'"></i>
            </span>
            <span class="index">[{{ index }}]:</span>
            <span v-if="debug" class="node-debug"> [index = {{ index }}]</span>
          </div>
          <div v-if="!collapsedItems[index]" class="node-children">
            <JsonNode :data="item" />
          </div>
        </div>
      </template>
  
      <!-- When data is a primitive -->
      <template v-else>
        <span class="primitive">{{ formatPrimitive(data) }}</span>
      </template>
    </div>
  </template>
  
  <script>
  export default {
    name: 'JsonNode',
    props: {
      data: {
        type: [Object, Array, String, Number, Boolean, null],
        required: true,
      },
    },
    data() {
      return {
        // Use a plain object to track which keys/indices are collapsed.
        collapsedItems: {},
        debug: true, // Toggle node-level debug logs/output.
      };
    },
    computed: {
      isObject() {
        const result =
          typeof this.data === 'object' &&
          this.data !== null &&
          !Array.isArray(this.data);
        if (this.debug) {
          console.log('[JsonNode] isObject:', result, 'Data:', this.data);
        }
        return result;
      },
      isArray() {
        const result = Array.isArray(this.data);
        if (this.debug) {
          console.log('[JsonNode] isArray:', result, 'Data:', this.data);
        }
        return result;
      },
    },
    methods: {
      toggleCollapse(key) {
        console.log('[JsonNode] Toggling collapse for key:', key, 'Current:', this.collapsedItems[key]);
        // Toggle the collapse state for the given key/index.
        this.$set(this.collapsedItems, key, !this.collapsedItems[key]);
        console.log('[JsonNode] New collapse state for key:', key, this.collapsedItems[key]);
      },
      formatPrimitive(value) {
        if (value === null) return 'null';
        if (typeof value === 'string') return '"' + value + '"';
        return value.toString();
      },
    },
    mounted() {
      if (this.debug) {
        console.log('[JsonNode] Mounted with data:', this.data);
      }
    },
  };
  </script>
  
  <style scoped>
  .json-tree {
    margin-left: 16px;
  }
  .node-header {
    cursor: pointer;
    display: flex;
    align-items: center;
    padding: 4px 0;
  }
  .node-header:hover {
    background-color: #f9f9f9;
  }
  .toggle {
    width: 16px;
    margin-right: 4px;
  }
  .key {
    color: #92278f;
    font-weight: 500;
  }
  .index {
    color: #2e6f9a;
  }
  .primitive {
    color: #2a9394;
  }
  .node-children {
    margin-left: 16px;
    border-left: 1px dashed #ddd;
    padding-left: 8px;
  }
  .node-debug {
    font-size: 12px;
    color: #555;
    margin-left: 4px;
  }
  </style>
  