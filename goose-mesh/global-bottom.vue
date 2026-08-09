<script setup lang="ts">
import { computed } from 'vue'
import { useNav } from '@slidev/client'

const { currentPage, total } = useNav()

// Hidden on the cover and the closing slide, so the deck opens and closes clean.
const show = computed(() => currentPage.value > 1 && currentPage.value < total.value)
const pct = computed(() => `${(currentPage.value / total.value) * 100}%`)
const num = computed(() => String(currentPage.value).padStart(2, '0'))
</script>

<template>
  <div v-if="show">
    <div class="deck-rail">
      <div class="deck-rail-fill" :style="{ width: pct }" />
    </div>
    <div class="deck-no">{{ num }}</div>
  </div>
</template>
