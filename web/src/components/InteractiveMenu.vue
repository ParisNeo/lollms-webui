<template>
  <div class="menu-container">
      <button @click.prevent="toggleMenu" :title="title" :class="menuIconClass" class="menu-button m-0 p-0 bg-blue-500 text-white dark:bg-blue-200 dark:text-gray-800 rounded flex items-center justify-center w-6 h-6 border-none cursor-pointer hover:bg-blue-400 w-8 h-8 object-fill text-red-700 border-2 active:scale-90 hover:z-20 hover:-translate-y-2 duration-150  border-gray-300 border-secondary cursor-pointer" ref="menuButton">
          <img v-if="icon && !icon.includes('#') && !icon.includes('feather')" :src="icon" class="w-5 h-5 p-0 m-0 shadow-lg bold">
          <i v-else-if="icon && icon.includes('feather')" :data-feather="icon.split(':')[1]" class="w-5 h-5"></i>             
          <p v-else-if="icon && icon.includes('#')" class="w-5 h-5">{{ icon.split('#')[1] }}</p>             
          <i v-else data-feather="menu" ></i>
      </button>
      <transition name="slide">
      <div v-if="isMenuOpen" class="menu-list flex-grow" :style="menuPosition" ref="menu">
          <ul class="flex-grow menu-ul">
          <li v-for="(command, index) in commands" :key="index" @click.prevent="executeCommand(command)" class="menu-command menu-li flex-grow hover:bg-blue-400 ">
              <i v-if="selected_entry==command.name" data-feather="check"></i>
              <img v-else-if="command.icon && !command.icon.includes('feather') && !command.is_file" :src="command.icon" :alt="command.name" class="menu-icon">
              <i v-if="command.icon && command.icon.includes('feather') && !command.is_file" :data-feather="command.icon.split(':')[1]" class="mr-2"></i>             
              <span v-else class="menu-icon"></span>
              <span>{{ command.name }}</span>
          </li>
          </ul>
      </div>
      </transition>
  </div>
</template>

<script>
import { nextTick } from 'vue'
import feather from 'feather-icons'
export default {
  props: {
    title: {
      type:String,
      required:false,
      value:"menu"
    },
    icon: {
      type:String,
      required:false,
      value:"feather:menu"
    },
    commands: {
      type: Array,
      required: true
    },
    force_position:{
      required: false,
      value:0
    },
    execute_cmd: {
      type: Function, // The execute_cmd property should be a function
      required: false
    },
    menuIconClass: {
      type: String,
      required: false,
      default:""
    },
    selected_entry: {
      type: String,
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
      nextTick(() => {
                feather.replace()
            })       
    },
    executeCommand(command) {
      this.isMenuOpen = false;
      console.log("Selected")
      console.log(command.value)
      
      if (typeof command.value === 'function') {
        console.log("Command detected",command)
        command.value();
      }
      if (this.execute_cmd) {
        console.log("executing generic command")
        this.execute_cmd(command); // Call the execute_cmd property with the current command
      }
    },
    positionMenu() {
      var isMenuAboveButton;
      if (this.$refs.menuButton!=undefined){
        if(this.force_position==0 || this.force_position==undefined){
          const buttonRect = this.$refs.menuButton.getBoundingClientRect();
          //const menuRect = this.$refs.menu.getBoundingClientRect();
  
          const windowHeight = window.innerHeight;
          isMenuAboveButton = buttonRect.bottom > windowHeight / 2;
  
        }
        else if (this.force_position==1){
          isMenuAboveButton=true;
        }
        else{
          isMenuAboveButton=false;
        }
        this.menuPosition.top = isMenuAboveButton ? 'auto' : 'calc(100% + 10px)';
        this.menuPosition.bottom = isMenuAboveButton ? '100%' : 'auto';
      }
    }
  },
  mounted() {
    // Listen to window resize to reposition the menu if needed
    window.addEventListener('resize', this.positionMenu);
    this.positionMenu(); // Initial positioning
    nextTick(() => {
                feather.replace()
            })
  },
  beforeUnmount() {
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
