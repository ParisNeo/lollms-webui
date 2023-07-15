<template>
    <!-- <link v-if="codeBlockStylesheet" rel="stylesheet" :href="codeBlockStylesheet"> -->
    <header class=" top-0 shadow-lg">
        <nav class="container flex flex-col lg:flex-row  item-center gap-2 py-2 ">
            <!-- LOGO -->
            <RouterLink :to="{ name: 'discussions' }">
                <div class="flex items-center gap-3 flex-1">
                    <img class="w-12  hover:scale-95 duration-150 " title="LoLLMS WebUI" src="@/assets/logo.png" alt="Logo">
                    <div class="flex flex-col">
                    <p class="text-2xl ">Lord of Large Language Models</p>
                    <p class="text-gray-400 ">One tool to rule them all</p>

                    </div>

                </div>
            </RouterLink>
            <!-- GITHUB AND THEME BUTTONS -->
            <div class="flex gap-3 flex-1 items-center justify-end">
                <div title="Connection status" :class="['dot', { 'dot-green': isConnected, 'dot-red': !isConnected }]"></div>
                <a href="https://github.com/ParisNeo/lollms-webui" target="_blank">

                    <div class="text-2xl  hover:text-primary duration-150" title="Visit repository page">
                        <i data-feather="github"></i>
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
    </header>

    <body>

    </body>
</template>

<script setup>
import { RouterLink } from 'vue-router'
import Navigation from './Navigation.vue'
import { nextTick } from 'vue'
import feather from 'feather-icons'
</script>
<script>
import { mapState } from 'vuex';

export default {
    name: 'TopBar',
    computed:{
        ...mapState(['isConnected']),
        // Add a watcher to log the changes

    },
    data() {
        return {
            codeBlockStylesheet:'',
            sunIcon: document.querySelector(".sun"),
            moonIcon: document.querySelector(".moon"),
            userTheme: localStorage.getItem("theme"),
            systemTheme: window.matchMedia("prefers-color-scheme: dark").matches,
        }
    },
    mounted() {
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
    components: {
        Navigation,

    }
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