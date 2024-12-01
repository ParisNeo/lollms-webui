<template>
  <div :title="title" :class="['cursor-pointer', isOk ? 'text-green-500' : 'text-red-500']">
    <i v-if="isStringIcon" :data-feather="icon" class="w-6 h-6"></i>
    <span v-else class="text-xl font-bold">{{ icon }}</span>
  </div>
</template>

<script setup>
import { computed, onMounted, nextTick } from 'vue';
import feather from 'feather-icons';

const props = defineProps({
  isOk: Boolean,
  icon: [String, Object],
  title: String
});

const isStringIcon = computed(() => typeof props.icon === 'string');

onMounted(() => {
  if (isStringIcon.value) {
    nextTick(() => feather.replace());
  }
});
</script>
