<template>
  <div class="menu relative">
    <div class="commands-menu-items-wrapper">
      <button
        id="commands-menu"
        @click.prevent="toggleMenu"
        class="menu-button bg-blue-500 text-white dark:bg-blue-200 dark:text-gray-800 rounded-full flex items-center justify-center w-6 h-6 border-none cursor-pointer hover:bg-blue-400 w-8 h-8 rounded-full object-fill text-red-700 border-2 active:scale-90 hover:z-20 hover:-translate-y-2 duration-150  border-gray-300 border-secondary cursor-pointer"
      >
        <i data-feather="command" class="w-5 h-5"></i>
      </button>
      <div v-if="showMenu" id="commands-menu-items" class="absolute left-0 mt-4 bg-white border border-gray-300 z-10 w-48 overflow-y-auto custom-scrollbar" :style="{ top: '-200px', maxHeight: '200px' }">
        <button
          v-for="command in commands"
          :key="command.value"
          @click.prevent="execute_cmd(command)"
          class="menu-button py-2 px-4 w-full text-left cursor-pointer bg-blue-500 text-white dark:bg-blue-200 dark:text-gray-800 hover:bg-blue-400"
          :class="{ 'bg-blue-400 text-white': hoveredCommand === command.value }"
          :title="command.help"
          @mouseover="hoveredCommand = command.value"
          @mouseout="hoveredCommand = null"
        >
          <div class="flex items-center">
            <img v-if="command.icon" :src="command.icon" alt="Command Icon" class="w-4 h-4 mr-2" style="width: 25px; height: 25px;">
            <div class="flex-grow">
              {{ command.name }}
            </div>
          </div>
        </button>
      </div>
    </div>
  </div>
</template>





<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 8px;
}

.custom-scrollbar::-webkit-scrollbar-track {
  background-color: #f1f1f1;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  background-color: #888;
  border-radius: 4px;
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background-color: #555;
}
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
import axios from "axios";
export default {
props: {
    commandsList: {
    type: Array,
    required: true,
    },
    sendCommand:Function,
    onShowToastMessage:Function
},
data() {
    return {
    selectedFile: null,
    showMenu: false,
    showHelpText: false,
    helpText: '',
    commands: [],
    };
},
async mounted() {
    //this.fileSize = await this.getFileSize(this.model.path)
    //console.log('model path', this.model.path)
    nextTick(() => {
      feather.replace()


    })
  },
methods: {
    selectFile(next) {
      const input = document.createElement('input');
      input.type = 'file';
      input.accept = 'application/pdf'; // Specify the file type you want to accept
      input.onchange = (e) => {
        this.selectedFile = e.target.files[0];
        console.log("File selected")
        next()
      };
      input.click();
    },
    uploadFile() {
      const formData = new FormData();
      formData.append('file', this.selectedFile);
      console.log("Uploading file")

      axios.post('/send_file', formData)
        .then(response => {
          // Handle the server response if needed
          console.log(response.data);
          this.onShowToastMessage("File uploaded successfully")
        })
        .catch(error => {
          // Handle any errors that occur during the upload
          console.error(error);
        });
    }, 
    async constructor() {
      nextTick(() => {
          feather.replace()
      })
    },
    toggleMenu() {
    this.showMenu = !this.showMenu;
    },
    execute_cmd(cmd) {
      this.showMenu = !this.showMenu;
      if (cmd.hasOwnProperty('is_file')) {
        console.log("Need to send a file.");
        this.selectFile(()=>{
          if(this.selectedFile!=null){
            this.uploadFile()
          }

        });
      } else {
        this.sendCommand(cmd);
      }      
      
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
  