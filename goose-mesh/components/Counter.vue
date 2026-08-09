<script setup lang="ts">
import { ref } from 'vue'

const props = defineProps<{ count?: number }>()
const counter = ref(props.count ?? 0)
</script>

<template>
  <div class="flex items-center gap-3 select-none">
    <button
      class="w-10 h-10 rounded border border-gray-400 hover:bg-gray-400/20"
      @click="counter -= 1"
    >
      -
    </button>
    <span class="text-3xl tabular-nums w-12 text-center">{{ counter }}</span>
    <button
      class="w-10 h-10 rounded border border-gray-400 hover:bg-gray-400/20"
      @click="counter += 1"
    >
      +
    </button>
  </div>
</template>
