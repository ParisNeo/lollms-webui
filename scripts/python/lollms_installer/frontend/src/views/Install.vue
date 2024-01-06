<template>
  <div class="flex flex-col items-center justify-center rounded-lg m-2 shadow-lg hover:border-primary dark:hover:border-primary hover:border-solid hover:border-2 border-2 border-transparent even:bg-bg-light-discussion-odd dark:even:bg-bg-dark-discussion-odd flex flex-col flex-grow flex-wrap overflow-visible p-4 pb-2">
    <img :src = "LoLLMSLogo" width="200px" height="200px">
    <h1 class="text-4xl font-bold mb-4">LOLLMS installation tool</h1>
    <p class="text-left">
      Welcome to the installer of lollms. Here you can select your install profile.<br>
      Let's start by selecting the hardware.<br><br>
    </p>
      <div class="flex flex-col gap-2 container h-500 overflow-y-scroll">
        <div>
            <label>Personal path: </label>
            <input type="text" v-bind="personal_path">
        </div>
        <label class="flex items-center">
          <input type="radio" value="cpu-noavx" v-model="selectedOption" class="mr-2">
          Use CPU without AVX (for old CPUs)
        </label>
        <label class="flex items-center">
          <input type="radio" value="cpu" v-model="selectedOption" class="mr-2">
          Use CPU with AVX support (new CPUs)
        </label>
        <label class="flex items-center">
          <input type="radio" value="nvidia" v-model="selectedOption" class="mr-2">
          Use NVIDIA GPU without tensorcore (for old GPUs)
        </label>
        <label class="flex items-center">
          <input type="radio" value="nvidia-tensorcores" v-model="selectedOption" class="mr-2">
          Use NVIDIA GPU with tensorcore (new GPUs)
        </label>
        <label class="flex items-center">
          <input type="radio" value="amd-noavx" v-model="selectedOption" class="mr-2">
          Use AMD GPU with no avx
        </label>
        <label class="flex items-center">
          <input type="radio" value="amd" v-model="selectedOption" class="mr-2">
          Use AMD GPU
        </label>      
        <label class="flex items-center">
          <input type="radio" value="apple-intel" v-model="selectedOption" class="mr-2">
          Apple with intel CPU
        </label>
        <label class="flex items-center">
          <input type="radio" value="apple-silicon" v-model="selectedOption" class="mr-2">
          Apple silicon (M1, M2 M3)
        </label>

      </div>
    <button @click="install" class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 mt-4 rounded">
      Install
    </button>
  </div>
  <Toast ref="toast" />
  <MessageBox ref="messageBox" />
</template>

<script>
import MessageBox from '../components/MessageBox.vue';
import Toast from '../components/Toast.vue';
import axios from 'axios';
import LoLLMSLogo from '../assets/logo.png'
import socket from '../services/websocket'

export default {
  data() {
    return {
      LoLLMSLogo:LoLLMSLogo,
      selectedOption: "cpu",
      personal_path: '',
    };
  },
  async mounted(){
    this.personal_path = await axios.get("/get_personal_path")
    socket.on('notification', this.notify)
  },
  components:{
    MessageBox,
    Toast
  },
  methods: {
    folderSelected(event) {
      const files = event.target.files;
      for (let i = 0; i < files.length; i++) {
        console.log(files[i].webkitRelativePath);
      }
      personal_path = files[0].webkitRelativePath
    },
    notify(notif){
        self.isGenerating = false
        this.setDiscussionLoading(this.currentDiscussion.id, this.isGenerating);
        nextTick(() => {
            const msgList = document.getElementById('messages-list')
            this.scrollBottom(msgList)
        })
        if(notif.display_type==0){
            this.$store.state.toast.showToast(notif.content, notif.duration, notif.notification_type)
        }
        else if(notif.display_type==1){
            this.$store.state.messageBox.showMessage(notif.content)
        }
        else if(notif.display_type==2){
            this.$store.state.messageBox.hideMessage()
            this.$store.state.yesNoDialog.askQuestion(notif.content, 'Yes', 'No').then(yesRes => {
                socket.emit("yesNoRes",{yesRes:yesRes})
            })
        }
        else if(notif.display_type==3){
            this.$store.state.messageBox.showBlockingMessage(notif.content)
        }
        else if(notif.display_type==4){
            this.$store.state.messageBox.hideMessage()
        }
        
        this.chime.play()
    },
    install() {
      this.$refs.toast.showToast(`Starting the install with option:${this.selectedOption}`, 4, true)
      axios.post("/start_installing",{mode:this.selectedOption}).then(()=>{
        this.$refs.messageBox.showMessage("Success!\nPlease close this page and open the run script from your install folder")
      });
    },
    selectFolder() {
      axios.get('/choose_path')
        .then(response => {
          this.personal_path = response.data.new_path;
        })
        .catch(error => {
          console.error(error);
        });
    },
  },
};
</script>

<style>
/* Add any additional styling here */
</style>
