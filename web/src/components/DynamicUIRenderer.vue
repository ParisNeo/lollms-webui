<template>
    <div>
      <iframe ref="outputFrame" :srcdoc="code" @load="adjustDimensions" frameborder="0" scrolling="no"></iframe>
    </div>
  </template>
  
  <script>
  export default {
    props: {
      code: String, // The HTML/CSS/JavaScript code as a prop
    },
    methods:{
      adjustDimensions() {
        // Get the iframe element
        const iframe = this.$refs.outputFrame;

        // Get the iframe's content window and document
        const iframeWindow = iframe.contentWindow;
        const iframeDocument = iframe.contentDocument || iframeWindow.document;

        // Get the width and height of the content
        const contentWidth = iframeDocument.body.scrollWidth;
        const contentHeight = iframeDocument.body.scrollHeight;

        // Set the width and height of the div and iframe to match the content
        this.$el.style.width = contentWidth + 'px';
        this.$el.style.height = contentHeight + 'px';
        iframe.style.width = '100%';
        iframe.style.height = '100%';
        },             
    }
  };
  </script>
  
  <style>
  /* Add any styling for the component here */
  </style>
  