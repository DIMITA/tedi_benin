<template>
  <div class="relative inline-block" ref="dropdownRef">
    <button
      @click="toggleDropdown"
      class="btn-primary inline-flex items-center"
      :disabled="disabled || exporting"
    >
      <svg v-if="!exporting" class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
      </svg>
      <svg v-else class="animate-spin w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
      <span>{{ exporting ? 'Exporting...' : 'Export' }}</span>
      <svg class="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
      </svg>
    </button>
    
    <transition
      enter-active-class="transition ease-out duration-100"
      enter-from-class="transform opacity-0 scale-95"
      enter-to-class="transform opacity-100 scale-100"
      leave-active-class="transition ease-in duration-75"
      leave-from-class="transform opacity-100 scale-100"
      leave-to-class="transform opacity-0 scale-95"
    >
      <div
        v-if="isOpen"
        class="absolute right-0 mt-2 w-56 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5 z-50"
      >
        <div class="py-1" role="menu" aria-orientation="vertical">
          <button
            v-for="format in formats"
            :key="format.value"
            @click="selectFormat(format.value)"
            class="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 hover:text-gray-900 flex items-center"
            role="menuitem"
          >
            <span class="w-8 h-8 flex items-center justify-center rounded-full mr-3" :class="format.bgColor">
              <component :is="format.icon" class="w-4 h-4" :class="format.iconColor" />
            </span>
            <div>
              <div class="font-medium">{{ format.label }}</div>
              <div class="text-xs text-gray-500">{{ format.description }}</div>
            </div>
          </button>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, h } from 'vue'

const props = defineProps({
  disabled: {
    type: Boolean,
    default: false
  },
  exporting: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['export'])

const isOpen = ref(false)
const dropdownRef = ref(null)

// Format icons as functional components
const CsvIcon = {
  render() {
    return h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
      h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z' })
    ])
  }
}

const ExcelIcon = {
  render() {
    return h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
      h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M3 10h18M3 14h18m-9-4v8m-7 0h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z' })
    ])
  }
}

const JsonIcon = {
  render() {
    return h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
      h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4' })
    ])
  }
}

const PdfIcon = {
  render() {
    return h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
      h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z' })
    ])
  }
}

const GeoJsonIcon = {
  render() {
    return h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
      h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z' })
    ])
  }
}

const formats = [
  {
    value: 'csv',
    label: 'CSV',
    description: 'Compatible Excel, tableurs',
    icon: CsvIcon,
    bgColor: 'bg-blue-100',
    iconColor: 'text-blue-600'
  },
  {
    value: 'xlsx',
    label: 'Excel',
    description: 'Microsoft Excel (.xlsx)',
    icon: ExcelIcon,
    bgColor: 'bg-green-100',
    iconColor: 'text-green-600'
  },
  {
    value: 'json',
    label: 'JSON',
    description: 'Format structuré pour développeurs',
    icon: JsonIcon,
    bgColor: 'bg-yellow-100',
    iconColor: 'text-yellow-600'
  },
  {
    value: 'pdf',
    label: 'PDF',
    description: 'Rapport imprimable',
    icon: PdfIcon,
    bgColor: 'bg-red-100',
    iconColor: 'text-red-600'
  },
  {
    value: 'geojson',
    label: 'GeoJSON',
    description: 'Données géospatiales',
    icon: GeoJsonIcon,
    bgColor: 'bg-purple-100',
    iconColor: 'text-purple-600'
  }
]

const toggleDropdown = () => {
  isOpen.value = !isOpen.value
}

const selectFormat = (format) => {
  isOpen.value = false
  emit('export', format)
}

const handleClickOutside = (event) => {
  if (dropdownRef.value && !dropdownRef.value.contains(event.target)) {
    isOpen.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>
