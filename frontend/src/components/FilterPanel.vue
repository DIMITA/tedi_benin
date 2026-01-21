<template>
  <div class="card mb-6">
    <h3 class="text-lg font-semibold mb-4">Filters</h3>
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <!-- Commune Filter -->
      <div>
        <label for="commune" class="block text-sm font-medium text-gray-700 mb-2">
          Commune
        </label>
        <select
          id="commune"
          v-model="localFilters.commune_id"
          class="input-field"
          @change="emitFilters"
        >
          <option :value="null">All Communes</option>
          <option
            v-for="commune in communes"
            :key="commune.id"
            :value="commune.id"
          >
            {{ commune.name }}
          </option>
        </select>
      </div>

      <!-- Crop Filter -->
      <div>
        <label for="crop" class="block text-sm font-medium text-gray-700 mb-2">
          Crop
        </label>
        <select
          id="crop"
          v-model="localFilters.crop_id"
          class="input-field"
          @change="emitFilters"
        >
          <option :value="null">All Crops</option>
          <option
            v-for="crop in crops"
            :key="crop.id"
            :value="crop.id"
          >
            {{ crop.name }}
          </option>
        </select>
      </div>

      <!-- Year Filter -->
      <div>
        <label for="year" class="block text-sm font-medium text-gray-700 mb-2">
          Year
        </label>
        <select
          id="year"
          v-model="localFilters.year"
          class="input-field"
          @change="emitFilters"
        >
          <option :value="null">All Years</option>
          <option v-for="year in years" :key="year" :value="year">
            {{ year }}
          </option>
        </select>
      </div>

      <!-- Actions -->
      <div class="flex items-end">
        <button
          @click="clearFilters"
          class="btn-secondary w-full"
        >
          Clear Filters
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  communes: {
    type: Array,
    default: () => [],
  },
  crops: {
    type: Array,
    default: () => [],
  },
  years: {
    type: Array,
    default: () => [2020, 2021, 2022, 2023],
  },
  modelValue: {
    type: Object,
    default: () => ({}),
  },
})

const emit = defineEmits(['update:modelValue', 'filter-change'])

const localFilters = ref({
  commune_id: props.modelValue.commune_id || null,
  crop_id: props.modelValue.crop_id || null,
  year: props.modelValue.year || null,
})

watch(() => props.modelValue, (newVal) => {
  localFilters.value = { ...newVal }
}, { deep: true })

const emitFilters = () => {
  emit('update:modelValue', localFilters.value)
  emit('filter-change', localFilters.value)
}

const clearFilters = () => {
  localFilters.value = {
    commune_id: null,
    crop_id: null,
    year: null,
  }
  emitFilters()
}
</script>
