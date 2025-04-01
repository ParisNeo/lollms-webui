<template>
    <!-- Sidebar container with theme-appropriate padding -->
    <nav class="p-4">
        <!-- Sidebar Title - Use primary text color and add standard padding/margin -->
        <h2 class="text-lg font-semibold mb-4 px-2 theme-text-primary">Settings</h2>

        <!-- List container - Ensure no default list styling (like bullet points) -->
        <ul class="list-none p-0 m-0">
            <!-- Loop through sections -->
            <li v-for="section in sections" :key="section.id" class="mb-1">
                <!-- Navigation Button for each section -->
                <button
                    @click="$emit('update:activeSection', section.id)"
                    :class="[
                        'w-full flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors duration-150 focus:outline-none focus:ring-2 focus:ring-opacity-50', // Base styles: full width, flex layout, padding, rounded corners, font, transitions, focus ring
                        activeSection === section.id
                            ? 'theme-bg-accent theme-text-accent-contrast shadow-sm' // Active state: Use accent background and contrasting text color
                            : 'theme-text-secondary hover:theme-bg-hover hover:theme-text-primary focus:theme-ring-accent' // Inactive state: Use secondary text color, themed hover background/text, themed focus ring
                    ]"
                >
                    <!-- Icon: THIS IS THE ICON ELEMENT - It inherits text color from the button. -->
                    <i :data-feather="section.icon" class="w-5 h-5 mr-3 flex-shrink-0"></i>

                    <!-- Section Name: Text color is handled by the button's class -->
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