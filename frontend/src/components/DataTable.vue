<template>
  <div class="data-table">
    <!-- Table Container -->
    <div class="overflow-x-auto">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th
              v-for="column in columns"
              :key="column.key"
              class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
            >
              {{ column.label }}
            </th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr
            v-for="(row, index) in data"
            :key="index"
            class="hover:bg-gray-50 transition-colors"
          >
            <td
              v-for="column in columns"
              :key="column.key"
              class="px-6 py-4 whitespace-nowrap text-sm"
            >
              <slot :name="`cell-${column.key}`" :row="row" :value="row[column.key]">
                {{ formatValue(row[column.key], column.format) }}
              </slot>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Empty State -->
    <div v-if="data.length === 0" class="text-center py-12">
      <svg
        class="mx-auto h-12 w-12 text-gray-400"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"
        />
      </svg>
      <h3 class="mt-2 text-sm font-medium text-gray-900">No data</h3>
      <p class="mt-1 text-sm text-gray-500">{{ emptyMessage }}</p>
    </div>

    <!-- Pagination -->
    <div
      v-if="pagination && data.length > 0"
      class="bg-white px-4 py-3 flex items-center justify-between border-t border-gray-200 sm:px-6"
    >
      <div class="flex-1 flex justify-between sm:hidden">
        <button
          @click="$emit('page-change', pagination.page - 1)"
          :disabled="!pagination.has_prev"
          class="btn-secondary"
        >
          Previous
        </button>
        <button
          @click="$emit('page-change', pagination.page + 1)"
          :disabled="!pagination.has_next"
          class="btn-secondary ml-3"
        >
          Next
        </button>
      </div>
      <div class="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
        <div class="flex items-center gap-4">
          <p class="text-sm text-gray-700">
            Showing
            <span class="font-medium">{{ (pagination.page - 1) * pagination.per_page + 1 }}</span>
            to
            <span class="font-medium">{{
              Math.min(pagination.page * pagination.per_page, pagination.total)
            }}</span>
            of
            <span class="font-medium">{{ pagination.total }}</span>
            results
          </p>
          <div class="flex items-center gap-2">
            <label class="text-sm text-gray-600">Per page:</label>
            <select
              :value="pagination.per_page"
              @change="$emit('per-page-change', Number($event.target.value))"
              class="border border-gray-300 rounded-md text-sm px-2 py-1 focus:outline-none focus:ring-2 focus:ring-tedi-primary focus:border-transparent"
            >
              <option v-for="option in perPageOptions" :key="option" :value="option">{{ option }}</option>
            </select>
          </div>
        </div>
        <div>
          <nav class="relative z-0 inline-flex rounded-md shadow-sm -space-x-px">
            <button
              @click="$emit('page-change', pagination.page - 1)"
              :disabled="!pagination.has_prev"
              class="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Previous
            </button>
            <span class="relative inline-flex items-center px-4 py-2 border border-gray-300 bg-white text-sm font-medium text-gray-700">
              Page {{ pagination.page }} of {{ pagination.total_pages }}
            </span>
            <button
              @click="$emit('page-change', pagination.page + 1)"
              :disabled="!pagination.has_next"
              class="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Next
            </button>
          </nav>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue'
import { formatPrice } from '@/utils/formatters'

const props = defineProps({
  columns: {
    type: Array,
    required: true,
  },
  data: {
    type: Array,
    required: true,
  },
  pagination: {
    type: Object,
    default: null,
  },
  emptyMessage: {
    type: String,
    default: 'No data available',
  },
  perPageOptions: {
    type: Array,
    default: () => [10, 25, 50, 100],
  },
})

defineEmits(['page-change', 'per-page-change'])

const formatValue = (value, format) => {
  if (value === null || value === undefined) return '-'

  if (format === 'number') {
    return new Intl.NumberFormat('fr-FR', {
      minimumFractionDigits: 0,
      maximumFractionDigits: 2,
    }).format(value)
  }

  if (format === 'price') {
    return formatPrice(value)
  }

  if (format === 'currency') {
    return formatPrice(value) + ' XOF'
  }

  if (format === 'percent') {
    return `${(value * 100).toFixed(1)}%`
  }

  return value
}
</script>
