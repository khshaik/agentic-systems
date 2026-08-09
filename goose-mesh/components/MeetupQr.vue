<script setup lang="ts">
// QR for https://www.meetup.com/aiyatra/
// Generated with segno at error level Q (25% recovery), version 3, 29x29
// modules, then decoded back with OpenCV to confirm it resolves to that exact
// URL. Dark modules are merged into horizontal runs to keep the path small.
// The viewBox carries the mandatory 4-module quiet zone, so do not crop it.
withDefaults(defineProps<{ size?: number }>(), { size: 190 })

const path =
  'M0 0h7v1h-7zM8 0h1v1h-1zM11 0h1v1h-1zM13 0h1v1h-1zM15 0h2v1h-2zM19 0h1v1h-1zM22 0h7v1h-7zM0 1h1v1h-1zM6 1h1v1h-1zM9 1h3v1h-3zM14 1h1v1h-1zM16 1h1v1h-1zM18 1h1v1h-1zM20 1h1v1h-1zM22 1h1v1h-1zM28 1h1v1h-1zM0 2h1v1h-1zM2 2h3v1h-3zM6 2h1v1h-1zM8 2h2v1h-2zM11 2h2v1h-2zM14 2h1v1h-1zM16 2h2v1h-2zM22 2h1v1h-1zM24 2h3v1h-3zM28 2h1v1h-1zM0 3h1v1h-1zM2 3h3v1h-3zM6 3h1v1h-1zM8 3h2v1h-2zM15 3h2v1h-2zM19 3h2v1h-2zM22 3h1v1h-1zM24 3h3v1h-3zM28 3h1v1h-1zM0 4h1v1h-1zM2 4h3v1h-3zM6 4h1v1h-1zM11 4h1v1h-1zM13 4h1v1h-1zM15 4h1v1h-1zM18 4h1v1h-1zM22 4h1v1h-1zM24 4h3v1h-3zM28 4h1v1h-1zM0 5h1v1h-1zM6 5h1v1h-1zM8 5h3v1h-3zM12 5h1v1h-1zM14 5h1v1h-1zM18 5h2v1h-2zM22 5h1v1h-1zM28 5h1v1h-1zM0 6h7v1h-7zM8 6h1v1h-1zM10 6h1v1h-1zM12 6h1v1h-1zM14 6h1v1h-1zM16 6h1v1h-1zM18 6h1v1h-1zM20 6h1v1h-1zM22 6h7v1h-7zM8 7h3v1h-3zM14 7h1v1h-1zM16 7h2v1h-2zM19 7h2v1h-2zM1 8h1v1h-1zM3 8h1v1h-1zM5 8h6v1h-6zM12 8h1v1h-1zM14 8h3v1h-3zM21 8h3v1h-3zM25 8h2v1h-2zM28 8h1v1h-1zM1 9h5v1h-5zM7 9h1v1h-1zM11 9h1v1h-1zM13 9h2v1h-2zM18 9h1v1h-1zM20 9h4v1h-4zM25 9h1v1h-1zM28 9h1v1h-1zM3 10h4v1h-4zM8 10h1v1h-1zM10 10h3v1h-3zM14 10h4v1h-4zM19 10h1v1h-1zM22 10h6v1h-6zM0 11h1v1h-1zM3 11h2v1h-2zM8 11h3v1h-3zM12 11h1v1h-1zM14 11h1v1h-1zM16 11h1v1h-1zM19 11h9v1h-9zM0 12h1v1h-1zM3 12h1v1h-1zM6 12h1v1h-1zM8 12h1v1h-1zM11 12h1v1h-1zM14 12h2v1h-2zM17 12h1v1h-1zM19 12h1v1h-1zM22 12h2v1h-2zM0 13h1v1h-1zM4 13h2v1h-2zM9 13h2v1h-2zM13 13h5v1h-5zM19 13h3v1h-3zM23 13h1v1h-1zM25 13h1v1h-1zM0 14h2v1h-2zM4 14h4v1h-4zM9 14h3v1h-3zM15 14h1v1h-1zM18 14h1v1h-1zM20 14h2v1h-2zM27 14h2v1h-2zM0 15h2v1h-2zM3 15h1v1h-1zM7 15h1v1h-1zM9 15h9v1h-9zM20 15h1v1h-1zM22 15h2v1h-2zM0 16h1v1h-1zM3 16h2v1h-2zM6 16h2v1h-2zM9 16h2v1h-2zM12 16h1v1h-1zM17 16h1v1h-1zM19 16h1v1h-1zM21 16h1v1h-1zM27 16h1v1h-1zM1 17h3v1h-3zM5 17h1v1h-1zM8 17h2v1h-2zM13 17h1v1h-1zM15 17h1v1h-1zM17 17h1v1h-1zM21 17h3v1h-3zM27 17h2v1h-2zM0 18h1v1h-1zM4 18h1v1h-1zM6 18h1v1h-1zM9 18h2v1h-2zM12 18h1v1h-1zM16 18h1v1h-1zM21 18h1v1h-1zM23 18h1v1h-1zM27 18h2v1h-2zM2 19h2v1h-2zM5 19h1v1h-1zM11 19h2v1h-2zM15 19h4v1h-4zM24 19h2v1h-2zM0 20h1v1h-1zM3 20h2v1h-2zM6 20h1v1h-1zM8 20h2v1h-2zM12 20h1v1h-1zM19 20h6v1h-6zM26 20h2v1h-2zM8 21h3v1h-3zM12 21h3v1h-3zM16 21h2v1h-2zM20 21h1v1h-1zM24 21h1v1h-1zM28 21h1v1h-1zM0 22h7v1h-7zM8 22h1v1h-1zM10 22h1v1h-1zM13 22h2v1h-2zM16 22h1v1h-1zM18 22h1v1h-1zM20 22h1v1h-1zM22 22h1v1h-1zM24 22h4v1h-4zM0 23h1v1h-1zM6 23h1v1h-1zM8 23h4v1h-4zM15 23h2v1h-2zM18 23h1v1h-1zM20 23h1v1h-1zM24 23h1v1h-1zM26 23h2v1h-2zM0 24h1v1h-1zM2 24h3v1h-3zM6 24h1v1h-1zM9 24h3v1h-3zM13 24h2v1h-2zM16 24h3v1h-3zM20 24h6v1h-6zM27 24h2v1h-2zM0 25h1v1h-1zM2 25h3v1h-3zM6 25h1v1h-1zM8 25h1v1h-1zM11 25h3v1h-3zM15 25h3v1h-3zM19 25h4v1h-4zM24 25h1v1h-1zM28 25h1v1h-1zM0 26h1v1h-1zM2 26h3v1h-3zM6 26h1v1h-1zM11 26h2v1h-2zM14 26h1v1h-1zM17 26h1v1h-1zM19 26h2v1h-2zM24 26h3v1h-3zM28 26h1v1h-1zM0 27h1v1h-1zM6 27h1v1h-1zM8 27h1v1h-1zM11 27h1v1h-1zM13 27h2v1h-2zM16 27h6v1h-6zM23 27h1v1h-1zM27 27h1v1h-1zM0 28h7v1h-7zM9 28h2v1h-2zM12 28h2v1h-2zM15 28h1v1h-1zM17 28h1v1h-1zM20 28h2v1h-2zM24 28h2v1h-2zM27 28h1v1h-1z'
</script>

<template>
  <svg
    :width="size"
    :height="size"
    viewBox="-4 -4 37 37"
    shape-rendering="crispEdges"
    role="img"
    aria-label="QR code linking to meetup.com/aiyatra"
    class="qr"
  >
    <rect x="-4" y="-4" width="37" height="37" fill="#fff" />
    <path :d="path" fill="#101010" />
  </svg>
</template>

<style scoped>
.qr {
  display: block;
  border: 1px solid var(--border);
  border-radius: var(--radius);
}
</style>
