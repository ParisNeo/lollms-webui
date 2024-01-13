<template>
    <!-- <link v-if="codeBlockStylesheet" rel="stylesheet" :href="codeBlockStylesheet"> -->
    <header class=" top-0 shadow-lg">
        <nav class="container flex flex-col lg:flex-row  item-center gap-2 pb-0 ">
            <!-- LOGO -->
            <RouterLink :to="{ name: 'discussions' }">
                <div class="flex items-center gap-3 flex-1">
                    <img class="w-12  hover:scale-95 duration-150 " title="LoLLMS WebUI" src="@/assets/logo.png" alt="Logo">
                    <div class="flex flex-col">
                    <p class="text-2xl ">Lord of Large Language and Multimodal Systems</p>
                    <p class="text-gray-400 ">One tool to rule them all</p>

                    </div>

                </div>
            </RouterLink>
            <!-- GITHUB AND THEME BUTTONS -->
            <div class="flex gap-3 flex-1 items-center justify-end">
                
                <div v-if="isModelOK" title="Model is ok" class="text-green-500 cursor-pointer">
                    <b class="text-2xl">M</b>
                </div>
                <div v-if="!isModelOK" title="Model is not ok" class="text-red-500 cursor-pointer">
                    <b class="text-2xl">M</b>
                </div>
                <div v-if="!isGenerating" title="Text is not being generated. Ready to generate" class="text-green-500 cursor-pointer">
                    <i data-feather="flag"></i>
                </div>
                <div v-if="isGenerating" title="Generation in progress..." class="text-red-500 cursor-pointer">
                    <i data-feather="flag"></i>
                </div>
                <div v-if="isConnected" title="Connection status: Connected" class="text-green-500 cursor-pointer">
                    <i data-feather="zap"></i>
                </div>
                <div v-if="!isConnected" title="Connection status: Not connected" class="text-red-500 cursor-pointer">
                    <i data-feather="zap-off"></i>
                </div>
                <a href="#" @click="restartProgram">
                    <div class="text-2xl  hover:text-primary duration-150" title="restart program">
                        <i data-feather="power"></i>
                    </div>
                </a>
                <a href="#" @click="refreshPage">
                    <div class="text-2xl  hover:text-primary duration-150" title="refresh page">
                        <i data-feather="refresh-ccw"></i>
                    </div>
                </a>
                <a href="https://github.com/ParisNeo/lollms-webui" target="_blank">
                <div class="text-2xl  hover:text-primary duration-150" title="Fast API doc">
                    <a href="/docs"><img :src="FastAPI" width="75" height="25"></a> 
                </div>
                </a>

                <a href="https://github.com/ParisNeo/lollms-webui" target="_blank">

                    <div class="text-2xl  hover:text-primary duration-150" title="Visit repository page">
                        <i data-feather="github"></i>
                    </div>
                </a>
                <a href="https://www.youtube.com/channel/UCJzrg0cyQV2Z30SQ1v2FdSQ" target="_blank">

                    <div class="text-2xl  hover:text-primary duration-150" title="Visit my youtube channel">
                        <i data-feather="youtube"></i>
                    </div>
                </a>

                <a href="https://twitter.com/SpaceNerduino" target="_blank">

                    <div class="text-2xl hover:fill-primary dark:fill-white dark:hover:fill-primary duration-150" title="Follow me on my twitter acount">
                        <svg class="w-10 h-10 rounded-lg object-fill dark:text-white" xmlns="http://www.w3.org/2000/svg"
                            viewBox="0 0 1668.56 1221.19" style="enable-background:new 0 0 1668.56 1221.19;" xml:space="preserve">
                            <g id="layer1" transform="translate(52.390088,-25.058597)">
                                <path id="path1009" d="M283.94,167.31l386.39,516.64L281.5,1104h87.51l340.42-367.76L984.48,1104h297.8L874.15,558.3l361.92-390.99
                                h-87.51l-313.51,338.7l-253.31-338.7H283.94z M412.63,231.77h136.81l604.13,807.76h-136.81L412.63,231.77z"/>
                            </g>
                        </svg>
                    </div>
                </a>

                <a href="https://www.youtube.com/channel/UCJzrg0cyQV2Z30SQ1v2FdSQ" target="_blank">

                    <div class="text-2xl hover:text-primary duration-150" title="Visit my discord channel">
                        <img :src="discord">
                    </div>
                </a>
               <div class="sun text-2xl w-6  hover:text-primary duration-150" title="Swith to Light theme"
                    @click="themeSwitch()">
                    <i data-feather="sun"></i>
                </div>


                <div class="moon text-2xl w-6  hover:text-primary duration-150" title="Swith to Dark theme"
                    @click="themeSwitch()">
                    <i data-feather="moon"></i>
                </div>

            </div>

        </nav>
        <!-- NAVIGATION BUTTONS -->
        <Navigation />
        <Toast ref="toast" />
        <MessageBox ref="messageBox" />
        <div v-show="progress_visibility" role="status" class="fixed m-0 p-2 left-2 bottom-2  min-w-[24rem] max-w-[24rem] h-20 flex flex-col justify-center items-center pb-4 bg-blue-500 rounded-lg shadow-lg z-50 background-a">
            <ProgressBar ref="progress" :progress="progress_value" class="w-full h-4"></ProgressBar>
            <p class="text-2xl animate-pulse mt-2 text-white">{{ loading_infos }} ...</p>
        </div>     
        <UniversalForm ref="universalForm" class="z-20" />
        <YesNoDialog ref="yesNoDialog" class="z-20" />

    </header>

    <body>

    </body>
</template>

<script setup>
import Toast from '../components/Toast.vue'
import MessageBox from "@/components/MessageBox.vue";
import ProgressBar from "@/components/ProgressBar.vue";
import UniversalForm from '../components/UniversalForm.vue';
import YesNoDialog from './YesNoDialog.vue';

import FastAPI from '@/assets/fastapi.png';
import discord from '@/assets/discord.svg';
import { RouterLink } from 'vue-router'
import Navigation from './Navigation.vue'
import { nextTick } from 'vue'
import feather from 'feather-icons'
</script>
<script>

export default {
    name: 'TopBar',
    computed:{
        loading_infos(){
            return this.$store.state.loading_infos;
        },        
        isModelOK(){
            return this.$store.state.isModelOk;
        },
        isGenerating(){
            return this.$store.state.isGenerating;
        },
        isConnected(){
            return this.$store.state.isConnected;
        }
    },
    components: {
        Toast,
        MessageBox,
        ProgressBar,
        UniversalForm,
        YesNoDialog,
        Navigation,
    },
    watch:{
        isConnected(){
            if (!this.isConnected){
                this.disconnected_audio.play()
                this.$store.state.toast.showToast("Server suddenly disconnected. Please reboot the server", 410, false)
            }
            nextTick(() => {
                feather.replace()
            })
        }

    },
    data() {
        return {
            discord:discord,
            FastAPI:FastAPI,
            rebooting_the_tool_audio: new Audio("rebooting.mp3"),            
            disconnected_audio: new Audio("disconnected.mp3"),
            database_selectorDialogVisible:false,
            progress_visibility:false,
            progress_value:0,
            codeBlockStylesheet:'',
            sunIcon: document.querySelector(".sun"),
            moonIcon: document.querySelector(".moon"),
            userTheme: localStorage.getItem("theme"),
            systemTheme: window.matchMedia("prefers-color-scheme: dark").matches,
        }
    },
    mounted() {
        this.$store.state.toast = this.$refs.toast
        this.$store.state.messageBox = this.$refs.messageBox
        this.$store.state.universalForm = this.$refs.universalForm
        this.$store.state.yesNoDialog = this.$refs.yesNoDialog
        
        this.sunIcon = document.querySelector(".sun");
        this.moonIcon = document.querySelector(".moon");
        this.userTheme = localStorage.getItem("theme");
        this.systemTheme = window.matchMedia("prefers-color-scheme: dark").matches;
        this.themeCheck()

        nextTick(() => {
            feather.replace()
        })


    },
    created() {
        this.sunIcon = document.querySelector(".sun");
        this.moonIcon = document.querySelector(".moon");
        this.userTheme = localStorage.getItem("theme");
        this.systemTheme = window.matchMedia("prefers-color-scheme: dark").matches;
    },
    methods: {
        restartProgram(event) {
            event.preventDefault();
            this.$store.state.api_get_req('restart_program')
            this.rebooting_the_tool_audio.play()
            this.$store.state.toast.showToast("Rebooting the app. Please wait...", 410, false)
            //self.$store.state.toast.showToast("Rebooting the app. Please wait...", 50, true);
            console.log("this.$store.state.api_get_req",this.$store.state.api_get_req)
            setTimeout(()=>{
                window.close();
            },2000)
        },
        refreshPage() {
            window.location.reload();
        },
        handleOk(inputText) {
            console.log("Input text:", inputText);
        },
        // codeBlockTheme(theme) {
        //     const styleDark = document.createElement('link');
        //     styleDark.type = "text/css";
        //     styleDark.href = 'highlight.js/styles/tokyo-night-dark.css';

        //     const styleLight = document.createElement('link');
        //     styleLight.type = "text/css";
        //     styleLight.href = 'highlight.js/styles/tomorrow-night-blue.css';
        //    if(theme=='dark'){

        //     document.head.appendChild(styleDark);
        //     document.head.removeChild(styleLight);
        //    }else{
        //     document.head.appendChild(styleLight);
        //     //document.head.removeChild(styleDark);
        //    }
            
        // },
        themeCheck() {

            if (this.userTheme == "dark" || (!this.userTheme && this.systemTheme)) {
                document.documentElement.classList.add("dark");
                this.moonIcon.classList.add("display-none");

                nextTick(()=>{
                    //import('highlight.js/styles/tokyo-night-dark.css');
                    import('highlight.js/styles/stackoverflow-dark.css');

                })

                return
            }

            nextTick(()=>{
                //import('highlight.js/styles/tomorrow-night-blue.css');
                import('highlight.js/styles/stackoverflow-light.css');
            })
            this.sunIcon.classList.add("display-none")

        },
        themeSwitch() {
            
            if (document.documentElement.classList.contains("dark")) {
                document.documentElement.classList.remove("dark");
                localStorage.setItem("theme", "light")
                this.userTheme == "light"
                this.iconToggle()
             
                return

            }
            import('highlight.js/styles/tokyo-night-dark.css');
            document.documentElement.classList.add("dark");
            localStorage.setItem("theme", "dark")
            this.userTheme == "dark"
            this.iconToggle()

        },
        iconToggle() {
            this.sunIcon.classList.toggle("display-none");
            this.moonIcon.classList.toggle("display-none");
        }
    },
}

</script>
<style>
.dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.dot-green {
  background-color: green;
}

.dot-red {
  background-color: red;
}
</style>