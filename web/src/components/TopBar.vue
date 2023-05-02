<template>
    <header class=" top-0 shadow-lg">
        <nav class="container flex flex-col lg:flex-row  item-center gap-2 py-2 ">
            <!-- LOGO -->
            <RouterLink :to="{ name: 'discussions' }">
                <div class="flex items-center gap-3 flex-1">
                    <img class="w-12  hover:scale-95 duration-150 " title="GPT4ALL-UI" src="@/assets/logo.svg" alt="Logo">
                    <p class="text-2xl ">GPT4ALL-UI</p>

                </div>
            </RouterLink>
            <!-- GITHUB AND THEME BUTTONS -->
            <div class="flex gap-3 flex-1 items-center justify-end">
                <a href="https://github.com/nomic-ai/gpt4all-ui" target="_blank">

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
export default {
    name: 'TopBar',
    data() {
        return {
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
        themeCheck() {

            if (this.userTheme == "dark" || (!this.userTheme && this.systemTheme)) {
                document.documentElement.classList.add("dark");
                this.moonIcon.classList.add("display-none");
                return
            }
            this.sunIcon.classList.add("display-none")

        },
        themeSwitch() {
            if (document.documentElement.classList.contains("dark")) {
                document.documentElement.classList.remove("dark");
                localStorage.setItem("theme", "light")
                this.iconToggle()
                return

            }
            document.documentElement.classList.add("dark");
            localStorage.setItem("theme", "dark")
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
