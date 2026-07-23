<template>
  <div
    class="relative overflow-hidden bg-[var(--card)] border border-[var(--border)] rounded-[var(--radius-lg)] p-5"
  >
    <div class="absolute left-0 top-0 bottom-0 w-1" :style="{ background: color }" />
    <div class="text-3xl font-semibold text-[var(--foreground)] tabular-nums">
      {{ formattedValue }}
    </div>
    <div class="mt-1 text-sm text-[var(--muted-foreground)]">{{ label }}</div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  label: { type: String, required: true },
  value: { type: [Number, String], default: 0 },
  color: { type: String, default: 'var(--color-primary)' },
})

const formattedValue = computed(() => {
  const v = Number(props.value) || 0
  return v.toLocaleString('zh-CN')
})
</script>
