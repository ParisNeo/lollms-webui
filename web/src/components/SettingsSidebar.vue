<template>
    <nav class="p-4">
        <h2 class="text-lg font-semibold mb-4 px-2">Settings</h2>
        <ul>
            <li v-for="section in sections" :key="section.id" class="mb-1">
                <button
                    @click="$emit('update:activeSection', section.id)"
                    :class="[
                        'w-full flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors duration-150',
                        activeSection === section.id
                            ? 'bg-primary text-white shadow-sm'
                            : 'text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
                    ]"
                >
                    <i :data-feather="section.icon" class="w-5 h-5 mr-3 flex-shrink-0"></i>
                    <span>{{ section.name }}</span>
                </button>
            </li>
        </ul>
    </nav>
</template>

<script setup>
import { defineProps, defineEmits, onMounted, nextTick } from 'vue';
import feather from 'feather-icons';

const props = defineProps({
    sections: {
        type: Array,
        required: true,
    },
    activeSection: {
        type: String,
        required: true,
    },
});

defineEmits(['update:activeSection']);

onMounted(() => {
    nextTick(() => {
        feather.replace();
    });
});
</script>

<style scoped>
/* Add any specific sidebar styles if needed */
</style>