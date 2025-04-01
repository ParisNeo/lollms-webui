<template>
    <div class="progress-bar-container">
      <div class="progress-bar" :style="{ width: `${progress}%` }"></div>
    </div>
  </template>
  
  <script>
  export default {
    props: {
      progress: {
        type: Number,
        required: true,
      },
    },
  };
  </script>
  
  <style scoped>
  .progress-bar-container {
    background-color: #f0f0f0;
    border-radius: 4px;
    height: 8px;
    overflow: hidden;
  }
  
  .progress-bar {
    background-color: #3498db;
    height: 100%;
    transition: width 0.3s ease;
  }
  </style>
  