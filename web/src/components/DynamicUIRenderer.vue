<template>
  <div :id="containerId" ref="container"></div>
</template>

<script>
export default {
  name: 'DynamicUIRenderer',
  props: {
    ui: {
      type: String,
      required: true
    },
    instanceId: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      containerId: `dynamic-ui-${this.instanceId}`
    };
  },
  watch: {
    ui: {
      immediate: true,
      handler(newValue) {
        console.log(`UI prop changed for instance ${this.instanceId}:`, newValue);
        this.$nextTick(() => {
          this.renderContent();
        });
      }
    }
  },
  methods: {
    renderContent() {
      console.log(`Rendering content for instance ${this.instanceId}...`);
      const container = this.$refs.container;
      
      // Parse the UI string
      const parser = new DOMParser();
      const doc = parser.parseFromString(this.ui, 'text/html');
      
      // Extract and inject CSS
      const styles = doc.getElementsByTagName('style');
      Array.from(styles).forEach(style => {
        const scopedStyle = document.createElement('style');
        scopedStyle.textContent = this.scopeCSS(style.textContent);
        document.head.appendChild(scopedStyle);
      });
      
      // Extract and inject HTML
      container.innerHTML = doc.body.innerHTML;
      
      // Extract and execute JavaScript
      const scripts = doc.getElementsByTagName('script');
      Array.from(scripts).forEach(script => {
        const newScript = document.createElement('script');
        newScript.textContent = script.textContent;
        container.appendChild(newScript);
      });
    },
    scopeCSS(css) {
      return css.replace(/([^\r\n,{}]+)(,(?=[^}]*{)|\s*{)/g, `#${this.containerId} $1$2`);
    }
  }
};
</script>
