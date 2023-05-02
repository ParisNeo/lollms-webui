<template>
    <!-- DEFAULT FIRST PAGE LOAD VIEW -->
    <div class="flex flex-col text-center">
        <div class="flex flex-col text-center items-center">

            <div class="flex items-center gap-3 text-5xl drop-shadow-md align-middle pt-24 ">
                <img class="w-24 animate-bounce" title="GPT4ALL-UI" src="@/assets/logo.svg" alt="Logo">
                <p class=" ">GPT4ALL-UI</p>


            </div>
            <hr
                class=" mt-1 w-96 h-1 mx-auto my-2 md:my-2 dark:bg-bg-dark-tone-panel bg-bg-light-tone-panel border-0 rounded ">
            <p class="text-lg ">Welcome, please create a new discussion or select existing one to start</p>

        </div>

    </div>
</template>

<script>
export default {
    name: 'WelcomeComponent',
    setup() {


        return {}
    }
}
</script>
