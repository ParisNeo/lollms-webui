<template>
  <div v-if="loading" title="Loading.." class="flex flex-row flex-grow justify-end">
      <!-- SPINNER -->
      <div role="status">
          <svg aria-hidden="true" class="w-6 h-6   animate-spin  fill-secondary" viewBox="0 0 100 101"
              fill="none" xmlns="http://www.w3.org/2000/svg">
              <path
                  d="M100 50.5908C100 78.2051 77.6142 100.591 50 100.591C22.3858 100.591 0 78.2051 0 50.5908C0 22.9766 22.3858 0.59082 50 0.59082C77.6142 0.59082 100 22.9766 100 50.5908ZM9.08144 50.5908C9.08144 73.1895 27.4013 91.5094 50 91.5094C72.5987 91.5094 90.9186 73.1895 90.9186 50.5908C90.9186 27.9921 72.5987 9.67226 50 9.67226C27.4013 9.67226 9.08144 27.9921 9.08144 50.5908Z"
                  fill="currentColor" />
              <path
                  d="M93.9676 39.0409C96.393 38.4038 97.8624 35.9116 97.0079 33.5539C95.2932 28.8227 92.871 24.3692 89.8167 20.348C85.8452 15.1192 80.8826 10.7238 75.2124 7.41289C69.5422 4.10194 63.2754 1.94025 56.7698 1.05124C51.7666 0.367541 46.6976 0.446843 41.7345 1.27873C39.2613 1.69328 37.813 4.19778 38.4501 6.62326C39.0873 9.04874 41.5694 10.4717 44.0505 10.1071C47.8511 9.54855 51.7191 9.52689 55.5402 10.0491C60.8642 10.7766 65.9928 12.5457 70.6331 15.2552C75.2735 17.9648 79.3347 21.5619 82.5849 25.841C84.9175 28.9121 86.7997 32.2913 88.1811 35.8758C89.083 38.2158 91.5421 39.6781 93.9676 39.0409Z"
                  fill="currentFill" />
          </svg>
          <span class="sr-only">Loading...</span>
      </div>
  </div>      
  <InteractiveMenu v-else :commands="commandsList" :execute_cmd="execute_cmd">

  </InteractiveMenu>

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
import InteractiveMenu from "@/components/InteractiveMenu.vue"

export default {
  components:{
    InteractiveMenu
  },
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
    loading: false,
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
    isHTML(str) {
      const parser = new DOMParser();
      const doc = parser.parseFromString(str, 'text/html');
      return Array.from(doc.body.childNodes).some(node => node.nodeType === Node.ELEMENT_NODE);
    },
    selectFile(file_types, next) {
      const input = document.createElement('input');
      input.type = 'file';
      input.accept = file_types; // Specify the file type you want to accept
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
      this.loading=true;

      axios.post('/send_file', formData)
        .then(response => {
          this.loading = false;
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
        this.selectFile(cmd.hasOwnProperty('file_types')?cmd.file_types:"*",()=>{
          if(this.selectedFile!=null){
            this.uploadFile()
          }

        });
      } else {
        this.sendCommand(cmd.value);
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
  