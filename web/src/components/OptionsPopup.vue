<template>
    <div v-if="showPopup" class="popup-overlay">
      <div class="popup">
        <div class="popup-content">
          <button
            v-for="(option, index) in options"
            :key="index"
            @click="selectOption(index)"
          >
            {{ option }}
          </button>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    data() {
      return {
        showPopup: false,
        options: [],
      };
    },
    methods: {
      show(options) {
        this.options = options;
        this.showPopup = true;
      },
      selectOption(index) {
        this.$emit('option-selected', index);
        this.showPopup = false;
      },
    },
  };
  </script>
  
  <style scoped>
  .popup-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
  }
  
  .popup {
    background-color: white;
    padding: 20px;
    border-radius: 5px;
  }
  
  .popup-content {
    display: flex;
    flex-direction: column;
  }
  
  button {
    margin-bottom: 10px;
  }
  </style>
  