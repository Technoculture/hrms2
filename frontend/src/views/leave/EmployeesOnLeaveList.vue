<template>
  <BaseLayout>
    <template #header>
      <div class="flex flex-row items-center gap-2">
        <FeatherIcon
          name="arrow-left"
          @click="$router.back()"
          class="cursor-pointer text-gray-500"
        />
        <h1 class="font-bold text-lg">{{ __("Employees On Leave") }}</h1>
      </div>
    </template>
    <template #body>
      <div class="flex flex-col bg-white">
        <div v-if="employeesOnLeave.loading" class="p-4 text-center text-gray-500">
          {{ __("Loading...") }}
        </div>
        <div v-else-if="!employeesOnLeave.data || employeesOnLeave.data.length === 0" class="p-4 text-center text-gray-500">
          {{ __("No employees are currently on leave") }}
        </div>
        <div 
          v-else
          v-for="employee in employeesOnLeave.data" 
          :key="employee.name"
          class="flex flex-row items-center p-4 border-b last:border-b-0"
        >
          <div class="flex flex-row items-center gap-4">
            <div class="h-10 w-10 rounded-full bg-gray-200 flex items-center justify-center text-gray-700 font-medium">
              {{ getInitials(employee.name) }}
            </div>
            <div class="flex flex-col">
              <div class="text-base font-medium text-gray-800">
                {{ employee.name }}
              </div>
              <div class="text-sm text-gray-500">
                {{ formatDateRange(employee.start_date, employee.end_date) }}
              </div>
              <div class="text-xs text-gray-400">
                {{ isHalfDayToday(employee.half_day_date) ? halfDaySession(employee.custom_half_day_session) : __("Full Day") }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>
  </BaseLayout>
</template>

<script setup>
import { inject } from 'vue'
import { createResource, FeatherIcon } from 'frappe-ui'
import BaseLayout from '@/components/BaseLayout.vue'

const __ = inject('$translate')
const dayjs = inject('$dayjs')

// API call to get employees on leave
const employeesOnLeave = createResource({
  url: 'tcr_erp.tcr_erp.overrides.employee.get_employees_on_leave',
  auto: true,
  transform(data) {
    return data || []
  }
})

function getInitials(name) {
  return name
    .split(' ')
    .map(word => word[0])
    .slice(0, 2)
    .join('')
    .toUpperCase()
}

function formatDateRange(startDate, endDate) {
  const start = dayjs(startDate).format('D MMM')
  const end = dayjs(endDate).format('D MMM')
  return `${start} - ${end}`
}

function halfDaySession(customHalfDaySession) {
  return customHalfDaySession === 'FIRST HALF' ? __("First Half") : __("Second Half")
}

// check if half day date is today
function isHalfDayToday(halfDayDate) {
  return dayjs(halfDayDate).isSame(dayjs(), 'day')
}
</script> 