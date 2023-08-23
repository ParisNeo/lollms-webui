<template>
    <div class="menu-container">
        <button @click.prevent="toggleMenu" class="menu-button bg-blue-500 text-white dark:bg-blue-200 dark:text-gray-800 rounded-full flex items-center justify-center w-6 h-6 border-none cursor-pointer hover:bg-blue-400 w-8 h-8 rounded-full object-fill text-red-700 border-2 active:scale-90 hover:z-20 hover:-translate-y-2 duration-150  border-gray-300 border-secondary cursor-pointer" ref="menuButton">
            <i data-feather="command" class="w-5 h-5"></i>
        </button>
        <transition name="slide">
        <div v-if="isMenuOpen" class="menu-list flex-grow" :style="menuPosition" ref="menu">
            <ul class="flex-grow menu-ul">
            <li v-for="(command, index) in commands" :key="index" @click="executeCommand(command)" class="menu-command menu-li flex-grow hover:bg-blue-400 ">
                <img v-if="command.icon && !command.is_file" :src="command.icon" :alt="command.name" class="menu-icon">
                <span v-else class="menu-icon"></span>
                <span>{{ command.name }}</span>
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
      },
      execute_cmd: {
        type: Function, // The execute_cmd property should be a function
        required: false
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
handleClickOutside(event) {
      // Close the menu if the click occurs outside the menu container
      const menuContainer = this.$refs.menu;
      const menuButton = this.$refs.menuButton;
      if (menuContainer && !menuContainer.contains(event.target) && !menuButton.contains(event.target)) {
        this.isMenuOpen = false;
        window.removeEventListener('click', this.handleClickOutside);
      }
    },
      toggleMenu() {
        this.positionMenu();
        this.isMenuOpen = !this.isMenuOpen;
        if (this.isMenuOpen) {
          // Attach the click event listener when the menu opens
          window.addEventListener('click', this.handleClickOutside);
        } else {
          // Remove the click event listener when the menu closes
          window.removeEventListener('click', this.handleClickOutside);
        }        
      },
      executeCommand(command) {
        if (typeof this[command.value] === 'function') {
          this[command.value]();
        }
        this.isMenuOpen = false;
        if (this.execute_cmd) {
          this.execute_cmd(command); // Call the execute_cmd property with the current command
        }
      },
      positionMenu() {
        if (this.$refs.menuButton!=undefined){
            const buttonRect = this.$refs.menuButton.getBoundingClientRect();
            //const menuRect = this.$refs.menu.getBoundingClientRect();
    
            const windowHeight = window.innerHeight;
            const isMenuAboveButton = buttonRect.bottom > windowHeight / 2;
    
            this.menuPosition.top = isMenuAboveButton ? 'auto' : 'calc(100% + 10px)';
            this.menuPosition.bottom = isMenuAboveButton ? '100%' : 'auto';
        }
      }
    },
    mounted() {
      // Listen to window resize to reposition the menu if needed
      window.addEventListener('resize', this.positionMenu);
      this.positionMenu(); // Initial positioning
    },
    beforeDestroy() {
      // Cleanup the event listener
      window.removeEventListener('resize', this.positionMenu);
    },
    watch: {
      isMenuOpen: 'positionMenu'
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
    color: black;
    border: 1px solid #ccc;
    border-radius: 4px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    padding: 10px;
    max-width: 500px;
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
  
  .menu-ul {
    list-style: none;
    padding: 0;
    margin: 0;
  }
  
  .menu-li {
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

  .menu-command{
    min-width: 200px;
    text-align: left;
  }
  </style>
  