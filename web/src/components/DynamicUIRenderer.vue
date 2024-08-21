<template>
  <div ref="container"></div>
</template>

<script>
export default {
  name: 'DynamicUIRenderer',
  props: {
    ui: {
      type: String,
      required: true,
      default: "",
    },
  },
  mounted() {
    this.renderUI();
  },
  watch: {
    ui: {
      handler: 'renderUI',
      immediate: true,
    },
  },
  methods: {
    renderUI() {
      const container = this.$refs.container;
      container.innerHTML = '';

      const parser = new DOMParser();
      const doc = parser.parseFromString(this.ui, 'text/html');

      // Extract and apply styles
      const styles = doc.getElementsByTagName('style');
      Array.from(styles).forEach(style => {
        const styleElement = document.createElement('style');
        styleElement.textContent = style.textContent;
        container.appendChild(styleElement);
      });

      // Extract and execute scripts
      const scripts = doc.getElementsByTagName('script');
      Array.from(scripts).forEach(script => {
        const scriptElement = document.createElement('script');
        scriptElement.textContent = script.textContent;
        container.appendChild(scriptElement);
      });

      // Append body content
      const body = doc.body;
      Array.from(body.children).forEach(child => {
        container.appendChild(child);
      });

      // Apply any inline styles from the body
      if (body.style.cssText) {
        container.style.cssText = body.style.cssText;
      }
    },
  },
};
</script>
