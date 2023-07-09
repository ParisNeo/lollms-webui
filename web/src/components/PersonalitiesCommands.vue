<template>
    <div class="menu relative">
      <div class="commands-menu-items-wrapper">
        <button id="commands-menu" @click.prevent="toggleMenu" class="menu-button bg-blue-500 text-white dark:bg-blue-200 dark:text-gray-800 rounded-full flex items-center justify-center w-12 h-12 border-none cursor-pointer hover:bg-blue-400">
          <i data-feather="command" class="w-6 h-6"></i>
        </button>
        <div v-if="showMenu" id="commands-menu-items" class="absolute mt-4 bg-white border border-gray-300 z-10">
          <button v-for="command in commands" :key="command.value" @click.prevent="execute_cmd(command.value)" class="menu-button py-2 px-4 cursor-pointer bg-blue-500 text-white dark:bg-blue-200 dark:text-gray-800 hover:bg-blue-400" :class="{ 'bg-blue-400 text-white': hoveredCommand === command.value }" :title="command.help" @mouseover="hoveredCommand = command.value" @mouseout="hoveredCommand = null">
            {{ command.name }}
          </button>
        </div>
      </div>
    </div>
</template>

<style scoped>
.menu {
    display: flex;
    flex-direction: column;
    align-items: center;
}

.commands-menu-items-wrapper {
    position: relative;
    display: flex;
    flex-direction: column;
    align-items: center;
}

.commands-menu-items-wrapper > #commands-menu-items {
    top: calc(-100% - 2rem);
}
</style>

<script>
import feather from 'feather-icons'
export default {
props: {
    commandsList: {
    type: Array,
    required: true,
    },
    sendCommand:Function
},
data() {
    return {
    showMenu: false,
    showHelpText: false,
    helpText: '',
    commands: [],
    };
},
methods: {
    toggleMenu() {
    this.showMenu = !this.showMenu;
    },
    execute_cmd(cmd) {
    this.showMenu = !this.showMenu;
    this.sendCommand(cmd);
    },
    showHelp(command) {
    this.showHelpText = true;
    this.helpText = command.help;
    },
    sendCommand(value) {
    // Implement your send_command function here
    console.log('Sending command:', value);
    },
    executeCommand(value) {
    this.sendCommand(value);
    this.$emit('command-executed', value);
    },
    handleClickOutside(event) {
    const menuElement = this.$el.querySelector('.commands-menu-items-wrapper');
    if (menuElement && !menuElement.contains(event.target)) {
        this.showMenu = false;
    }
    },
},
mounted() {
    // Example commands data
    this.commands = this.commandsList;

    document.addEventListener('click', this.handleClickOutside);
},
beforeUnmount() {
    document.removeEventListener('click', this.handleClickOutside);
},
};
</script>
  