<template>
  <div class="flex flex-col gap-5 my-4 w-full" v-if="employeesOnLeave.data && employeesOnLeave.data.length">
    <div class="flex flex-row justify-between items-center">
      <div class="text-lg font-medium text-gray-900">{{ __("Team Leaves  👥") }}</div>
      <div class="flex items-center gap-3">
        <div v-if="employeesOnLeave.data.length > 0" class="text-sm text-gray-600">
          {{ new Set(employeesOnLeave.data.map(e => e.employee)).size }} {{ __("employees") }}
        </div>
      <router-link 
        :to="{ name: 'EmployeesOnLeaveList' }" 
        class="text-sm font-medium text-blue-600"
      >
        {{ __("View All") }}
      </router-link>
      </div>
    </div>
    
    <div class="flex flex-row flex-wrap gap-4 bg-white rounded p-4">
      <div 
        v-for="employee in displayedEmployees" 
        :key="employee.name"
        class="flex flex-col items-center gap-2"
      >
        <div class="h-8 w-8 rounded-full bg-gray-200 flex items-center justify-center text-xs font-medium text-gray-700">
          {{ getInitials(employee.name) }}
        </div>
        <!-- <div class="text-xs text-center font-medium text-gray-800 max-w-16 truncate">
          {{ employee.name }}
        </div> -->
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, inject } from 'vue'
import { createResource } from 'frappe-ui'

const __ = inject('$translate')

// API call to get employees on leave
const employeesOnLeave = createResource({
  url: 'tcr_erp.tcr_erp.overrides.employee.get_employees_on_leave',
  auto: true,
  transform(data) {
    return data || []
  }
})

// Display only first 4 employees
const displayedEmployees = computed(() => {
  if (!employeesOnLeave.data || employeesOnLeave.data.length === 0) return []
  return employeesOnLeave.data.slice(0, 4)
})

function getInitials(name) {
  return name
    .split(' ')
    .map(word => word[0])
    .slice(0, 2)
    .join('')
    .toUpperCase()
}
</script>

<style scoped>
.max-w-16 {
  max-width: 4rem;
}
</style> 