<template>
    <!-- DEFAULT FIRST PAGE LOAD VIEW -->
    <div class="flex flex-col text-center">
        <div class="flex flex-col text-center items-center">
            
            <div class="flex items-center gap-3 text-5xl drop-shadow-md align-middle pt-24 ">
               
                <img class="w-24 animate-bounce" title="LoLLMS WebUI" src="@/assets/logo.png" alt="Logo">
                    <div class="flex flex-col items-start">
                    <p class="text-2xl ">LoLLMS</p>
                    <p class="text-gray-400 text-base">One tool to rule them all</p>

                    </div>
            </div>
            <hr
                class=" mt-1 w-96 h-1 mx-auto my-2 md:my-2 dark:bg-bg-dark-tone-panel bg-bg-light-tone-panel border-0 rounded ">
                <p class="text-2xl">Welcome</p>
            <p class="text-lg ">Please create a new discussion or select existing one to start</p>

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
