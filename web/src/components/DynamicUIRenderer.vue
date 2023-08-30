<template>
    <div>
      <iframe ref="outputFrame" :srcdoc="code"></iframe>
    </div>
  </template>
  
  <script>
  export default {
    props: {
      code: String, // The HTML/CSS/JavaScript code as a prop
    },
  };
  </script>
  
  <style>
  /* Add any styling for the component here */
  </style>
  