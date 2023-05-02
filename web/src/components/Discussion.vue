<template>
    <div :class="selected ? 'bg-bg-light-discussion dark:bg-bg-dark-discussion shadow-md' : ''"
        class="container flex flex-col sm:flex-row item-center  gap-2 py-2 my-2 hover:shadow-md hover:bg-primary-light dark:hover:bg-primary rounded-md p-2 duration-75 group cursor-pointer">
        <!-- INDICATOR FOR SELECTED ITEM -->
        <div v-if="selected" class="items-center inline-block min-h-full w-2 rounded-xl self-stretch "
            :class="loading ? 'animate-bounce bg-accent ' : ' bg-secondary '"></div>
        <div v-else class="items-center inline-block min-h-full w-2 rounded-xl self-stretch"></div>

        <!-- TITLE -->
        <p class="truncate w-auto">{{ title }}</p>
        <!-- CONTROL BUTTONS -->
        <div class="flex items-center gap-3 flex-1 max-h-6">
            <div class="flex gap-3 flex-1 items-center justify-end invisible group-hover:visible duration-75">
                <div class="text-2xl hover:text-secondary duration-75 active:scale-90" title="Edit title">
                    <i data-feather="edit-2"></i>
                </div>
                <div class="text-2xl hover:text-red-600 duration-75 active:scale-90" title="Remove discussion">
                    <i data-feather="trash"></i>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import { nextTick } from 'vue'
import feather from 'feather-icons'

export default {
    name: 'Discussion',
    props: {
        id: Number,
        title: String,
        selected: Boolean,
        loading: Boolean
    },
    setup() {

    },
    data() {
        return {


        }
    },
    methods: {

    }, mounted() {
        nextTick(() => {
            feather.replace()

        })
    },

}
</script>
<style scoped></style>
