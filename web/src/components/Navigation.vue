<template>
    <div class="container flex flex-col sm:flex-row item-center gap-2 py-1 ">
        <div class="items-center justify-between  w-full flex-row md:w-auto md:order-1">
            <ul class="flex flex-row font-medium p-0 mt-4 space-x-8  ">

                <li>
                    <RouterLink  :to="{ name: 'discussions' }" class="p-2"
                        active-class="p-2 bg-bg-light-tone dark:bg-bg-dark-tone rounded-t-lg ">
                        <a href="#" class=" hover:text-primary duration-150">Discussions</a>
                    </RouterLink>
                </li>
                <li>
                    <RouterLink :to="{ name: 'settings' }" class="p-2"
                        active-class="p-2   bg-bg-light-tone dark:bg-bg-dark-tone rounded-t-lg ">
                        <a href="#" class=" hover:text-primary duration-150">Settings</a>
                    </RouterLink>
                </li>
                <li>
                    <RouterLink :to="{ name: 'extensions' }" class="p-2"
                        active-class="p-2   bg-bg-light-tone dark:bg-bg-dark-tone rounded-t-lg ">
                        <a href="#" class=" hover:text-primary duration-150">Extensions</a>
                    </RouterLink>
                </li>

                <li>
                    <RouterLink :to="{ name: 'training' }" class="p-2"
                        active-class="p-2   bg-bg-light-tone dark:bg-bg-dark-tone rounded-t-lg ">
                        <a href="#" class=" hover:text-primary duration-150">Training</a>
                    </RouterLink>
                </li>
                <li>
                    <RouterLink :to="{ name: 'help' }" class="p-2"
                        active-class="p-2   bg-bg-light-tone dark:bg-bg-dark-tone rounded-t-lg ">
                        <a href="#" class=" hover:text-primary duration-150">Help</a>
                    </RouterLink>
                </li>
            </ul>
        </div>
    </div>
</template>

<script setup>
import { nextTick } from 'vue'
import feather from 'feather-icons'
import { RouterLink } from 'vue-router'


</script>
<script>
export default {
    data() {
        return {

        };
    },
    activated() {


    },
    methods: {
        
    },
};
</script>