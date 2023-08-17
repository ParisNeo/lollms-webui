<template>
  <div v-if="isContentPresent">
    <div class="collapsible-section cursor-pointer mb-4 font-bold hover:text-gray-900" @click="toggleCollapsible">
      <span class="toggle-icon mr-1">
        <i v-if="collapsed" class="fas fa-plus-circle text-gray-600"></i>
        <i v-else class="fas fa-minus-circle text-gray-600"></i>
      </span>
      {{ jsonFormText }}
    </div>
    <div v-show="!collapsed">
      <div class="json-viewer max-h-64 overflow-auto p-4 bg-gray-100 border border-gray-300 rounded dark:bg-gray-600">
        <template v-if="isObject">
          <span @click="toggleCollapsed" class="toggle-icon cursor-pointer mr-1">
            <i v-if="collapsed" class="fas fa-plus-circle text-gray-600"></i>
            <i v-else class="fas fa-minus-circle text-gray-600"></i>
          </span>
        </template>
        <pre v-html="formattedJson"></pre>
      </div>
    </div>
  </div>
</template>


<script>
export default {
  props: {
    jsonData: {
      type: [Object, Array, String],
      default: null,
    },
    jsonFormText: {
      type: String,
      default: "JSON Form",
    },
  },
  data() {
    return {
      collapsed: true,
    };
  },
  computed: {
    formattedJson() {
      console.log(typeof this.jsonData)
      if (typeof this.jsonData==='string'){
        let jsonData = JSON.stringify(JSON.parse(this.jsonData), null, '\t').replace(/\n/g, '<br>')
        console.log(jsonData)
        console.log(this.jsonFormText)
        return  jsonData;

      }
      else{
        let jsonData = JSON.stringify(this.jsonData, null, '\t').replace(/\n/g, '<br>')
        console.log(jsonData)
        console.log(this.jsonFormText)
        return  jsonData;

      }
    },
    isObject() {
      console.log(typeof this.jsonData)
      console.log(this.jsonData)
      return typeof this.jsonData === 'object' && this.jsonData !== null;
    },
    isContentPresent() {
      return (
        this.jsonData !== null &&
        (typeof this.jsonData !== 'string' || this.jsonData.trim() !== '')
      );
    },
  },
  methods: {
    toggleCollapsed() {
      this.collapsed = !this.collapsed;
    },
    toggleCollapsible() {
        this.collapsed = !this.collapsed;
    },
  },
};
</script>

<style>
.collapsible-section {
  cursor: pointer;
  margin-bottom: 10px;
  font-weight: bold;
}

.collapsible-section:hover {
  color: #1a202c;
}

.collapsible-section .toggle-icon {
  margin-right: 0.25rem;
}

.collapsible-section .toggle-icon i {
  color: #4a5568;
}

.collapsible-section .toggle-icon i:hover {
  color: #1a202c;
}

.json-viewer {
  max-height: 300px;
  max-width: 700px;
  flex: auto;
  overflow-y: auto;
  padding: 10px;
  background-color: #f1f1f1;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.json-viewer .toggle-icon {
  cursor: pointer;
  margin-right: 0.25rem;
}

.json-viewer .toggle-icon i {
  color: #4a5568;
}

.json-viewer .toggle-icon i:hover {
  color: #1a202c;
}
</style>
