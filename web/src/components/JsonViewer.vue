<template>
  <div v-if="isContentPresent" class="json-viewer">
    <div class="collapsible-section" @click="toggleCollapsible">
      <span class="toggle-icon">
        <i :class="collapsed ? 'fas fa-chevron-right' : 'fas fa-chevron-down'"></i>
      </span>
      {{ jsonFormText }}
    </div>
    <div v-show="!collapsed" class="json-content panels-color">
      <json-tree-view :data="parsedJsonData" :depth="0"></json-tree-view>
    </div>
  </div>
</template>

<script>
import JsonTreeView from './JsonTreeView.vue';

export default {
  components: {
    JsonTreeView
  },
  props: {
    jsonData: {
      type: [Object, Array, String],
      default: null,
    },
    jsonFormText: {
      type: String,
      default: "JSON Viewer",
    },
  },
  data() {
    return {
      collapsed: true,
    };
  },
  computed: {
    isContentPresent() {
      return (
        this.jsonData !== null &&
        (typeof this.jsonData !== 'string' || this.jsonData.trim() !== '')
      );
    },
    parsedJsonData() {
      if (typeof this.jsonData === 'string') {
        try {
          return JSON.parse(this.jsonData);
        } catch (error) {
          console.error('Error parsing JSON string:', error);
          return { error: 'Invalid JSON string' };
        }
      }
      return this.jsonData;
    }
  },
  methods: {
    toggleCollapsible() {
      this.collapsed = !this.collapsed;
    },
  },
};
</script>

<style scoped>
.json-viewer {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', 'Consolas', 'source-code-pro', monospace;
  font-size: 14px;
  line-height: 1.5;
  color: #333;
}

.collapsible-section {
  cursor: pointer;
  padding: 8px;
  background-color: #f0f0f0;
  border-radius: 4px;
  display: flex;
  align-items: center;
  transition: background-color 0.2s;
}

.collapsible-section:hover {
  background-color: #e0e0e0;
}

.toggle-icon {
  margin-right: 8px;
  transition: transform 0.2s;
}

.json-content {
  margin-top: 8px;
  padding-left: 16px;
}
</style>