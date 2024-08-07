<template>
    <div class="json-tree-view">
      <div v-for="(value, key) in data" :key="key" class="json-item">
        <div class="json-key" @click="toggleCollapse(key)">
          <span class="toggle-icon" v-if="isObject(value) || isArray(value)">
            <i :class="isCollapsed(key) ? 'fas fa-chevron-right' : 'fas fa-chevron-down'"></i>
          </span>
          <span class="key">{{ key }}:</span>
          <span v-if="!isObject(value) && !isArray(value)" class="value" :class="getValueType(value)">
            {{ formatValue(value) }}
          </span>
        </div>
        <div v-if="(isObject(value) || isArray(value)) && !isCollapsed(key)" class="json-nested">
          <json-tree-view :data="value" :depth="depth + 1"></json-tree-view>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    name: 'JsonTreeView',
    props: {
      data: {
        type: [Object, Array],
        required: true
      },
      depth: {
        type: Number,
        default: 0
      }
    },
    data() {
      return {
        collapsedKeys: new Set()
      };
    },
    methods: {
      isObject(value) {
        return typeof value === 'object' && value !== null && !Array.isArray(value);
      },
      isArray(value) {
        return Array.isArray(value);
      },
      toggleCollapse(key) {
        if (this.collapsedKeys.has(key)) {
          this.collapsedKeys.delete(key);
        } else {
          this.collapsedKeys.add(key);
        }
      },
      isCollapsed(key) {
        return this.collapsedKeys.has(key);
      },
      getValueType(value) {
        if (typeof value === 'string') return 'string';
        if (typeof value === 'number') return 'number';
        if (typeof value === 'boolean') return 'boolean';
        if (value === null) return 'null';
        return '';
      },
      formatValue(value) {
        if (typeof value === 'string') return `"${value}"`;
        return String(value);
      }
    }
  };
  </script>
  
  <style scoped>
  .json-tree-view {
    margin-left: 16px;
  }
  
  .json-item {
    margin-bottom: 4px;
  }
  
  .json-key {
    cursor: pointer;
    display: flex;
    align-items: center;
  }
  
  .toggle-icon {
    margin-right: 4px;
    width: 12px;
  }
  
  .key {
    font-weight: bold;
    margin-right: 4px;
  }
  
  .value {
    margin-left: 4px;
  }
  
  .string { color: #0b7285; }
  .number { color: #d9480f; }
  .boolean { color: #5c940d; }
  .null { color: #868e96; }
  
  .json-nested {
    margin-left: 16px;
    border-left: 1px dashed #ccc;
    padding-left: 8px;
  }
  </style>