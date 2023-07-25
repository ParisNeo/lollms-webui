<template>
    <div class="menu-container">
      <button @click="toggleMenu" class="menu-button">Menu</button>
      <transition name="slide">
        <div v-if="isMenuOpen" class="menu-list" :style="menuPosition">
          <ul>
            <li v-for="(command, index) in commands" :key="index" @click="executeCommand(command)">
              <img v-if="command.icon && !command.is_file" :src="command.icon" :alt="command.name" class="menu-icon">
              <span v-else>{{ command.name }}</span>
            </li>
          </ul>
        </div>
      </transition>
    </div>
  </template>
  
  <script>
  export default {
    props: {
      commands: {
        type: Array,
        required: true
      }
    },
    data() {
      return {
        isMenuOpen: false,
        menuPosition: {
          bottom: 'auto',
          top: 'calc(100% + 10px)' // Initial position: below the button
        }
      };
    },
    methods: {
      toggleMenu() {
        this.isMenuOpen = !this.isMenuOpen;
      },
      executeCommand(command) {
        if (typeof this[command.value] === 'function') {
          this[command.value]();
        }
        this.isMenuOpen = false;
      }
    },
    mounted() {
      // Listen to window resize to reposition the menu if needed
      window.addEventListener('resize', this.positionMenu);
    },
    beforeDestroy() {
      // Cleanup the event listener
      window.removeEventListener('resize', this.positionMenu);
    },
    watch: {
      isMenuOpen: 'positionMenu'
    },
    methods: {
      positionMenu() {
        const menu = this.$el.querySelector('.menu-list');
        if (!menu) return;
  
        const rect = menu.getBoundingClientRect();
        const windowHeight = window.innerHeight;
        const isMenuAboveButton = rect.bottom > windowHeight;
  
        this.menuPosition.top = isMenuAboveButton ? 'auto' : 'calc(100% + 10px)';
        this.menuPosition.bottom = isMenuAboveButton ? '100%' : 'auto';
      }
    }
  };
  </script>
  
  <style>
  .menu-container {
    position: relative;
    display: inline-block;
  }
  
  .menu-button {
    background-color: #007bff;
    color: white;
    padding: 10px;
    border: none;
    cursor: pointer;
    border-radius: 4px;
  }
  
  .menu-list {
    position: absolute;
    background-color: white;
    border: 1px solid #ccc;
    border-radius: 4px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    padding: 10px;
    min-width: 150px;
    z-index: 1000;
  }
  
  .slide-enter-active,
  .slide-leave-active {
    transition: transform 0.2s;
  }
  
  .slide-enter-to,
  .slide-leave-from {
    transform: translateY(-10px);
  }
  
  ul {
    list-style: none;
    padding: 0;
    margin: 0;
  }
  
  li {
    cursor: pointer;
    display: flex;
    align-items: center;
    padding: 5px;
  }
  
  .menu-icon {
    width: 20px;
    height: 20px;
    margin-right: 8px;
  }
  </style>
  