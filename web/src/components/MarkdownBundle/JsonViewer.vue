<!-- JsonViewer.vue -->
<template>
  <div class="json-viewer">
    <div class="viewer-header" @click="toggle">
      <span class="toggle-icon">{{ expanded ? '▼' : '▶' }}</span>
      <span class="title">{{ title }}</span>
    </div>
    <div v-if="expanded" class="viewer-content">
      <json-node :data="parsedData" />
    </div>
  </div>
</template>

<script>
import JsonNode from './JsonNode.vue'

export default {
  name: 'JsonViewer',
  components: { JsonNode },
  props: {
    data: {
      required: true
    },
    title: {
      type: String,
      default: 'JSON Data'
    }
  },
  data() {
    return {
      expanded: true
    }
  },
  computed: {
    parsedData() {
      if (typeof this.data === 'string') {
        try {
          return JSON.parse(this.data)
        } catch (e) {
          return { error: 'Invalid JSON' }
        }
      }
      return this.data
    }
  },
  methods: {
    toggle() {
      this.expanded = !this.expanded
    }
  }
}
</script>

<style scoped>
.json-viewer {
  border: 1px solid #ddd;
  border-radius: 4px;
  margin: 10px;
  background: white;
}

.viewer-header {
  padding: 8px 12px;
  background: #f5f5f5;
  cursor: pointer;
  border-bottom: 1px solid #ddd;
}

.viewer-header:hover {
  background: #eee;
}

.toggle-icon {
  display: inline-block;
  width: 20px;
  color: #666;
}

.title {
  font-weight: bold;
  color: #333;
}

.viewer-content {
  padding: 10px;
}
</style>
