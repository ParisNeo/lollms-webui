<template>
    <div class="container flex flex-col sm:flex-row item-center gap-2 py-1 ">
        <div class="items-center justify-between hidden w-full md:flex md:w-auto md:order-1">
            <ul class="flex flex-col font-medium p-4 md:p-0 mt-4 md:flex-row md:space-x-8 md:mt-0 ">

                <li>
                    <RouterLink :to="{ name: 'discussions' }" active-class="  bg-bg-light-tone dark:bg-bg-dark-tone p-2 px-4 rounded-t-lg ">
                        <a href="#" class=" hover:text-primary duration-150">Discussions</a>
                    </RouterLink>
                </li>
                <li>
                    <RouterLink :to="{ name: 'settings' }" active-class="  bg-bg-light-tone dark:bg-bg-dark-tone p-2 px-4 rounded-t-lg ">
                        <a href="#" class=" hover:text-primary duration-150">Settings</a>
                    </RouterLink>
                </li>
                <li>
                    <RouterLink :to="{ name: 'extensions' }" active-class="  bg-bg-light-tone dark:bg-bg-dark-tone p-2 px-4 rounded-t-lg ">
                        <a href="#" class=" hover:text-primary duration-150">Extensions</a>
                    </RouterLink>
                </li>

                <li>
                    <RouterLink :to="{ name: 'training' }" active-class="  bg-bg-light-tone dark:bg-bg-dark-tone p-2 px-4 rounded-t-lg ">
                        <a href="#" class=" hover:text-primary duration-150">Training</a>
                    </RouterLink>
                </li>
                <li>
                    <RouterLink :to="{ name: 'help' }" active-class="  bg-bg-light-tone dark:bg-bg-dark-tone p-2 px-4 rounded-t-lg ">
                        <a href="#" class=" hover:text-primary duration-150">Help</a>
                    </RouterLink>
                </li>
            </ul>
        </div>
    </div>
</template>

<script setup>
import {nextTick} from 'vue'
import feather from 'feather-icons'
import { RouterLink } from 'vue-router'
</script>
