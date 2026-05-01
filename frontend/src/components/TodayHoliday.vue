<template>
  <div class="flex flex-col gap-5 my-4 w-full" v-if="hasHolidaysToday">
    <div class="flex flex-row justify-between items-center">
      <div class="text-lg font-medium text-gray-900">
        {{ isManager ? __("Team Holidays") : __("Holiday") }}
      </div>
      <div class="flex items-center gap-3">
        <div v-if="isManager && totalEmployeesOnHoliday > 0" class="text-sm text-gray-600">
          {{ totalEmployeesOnHoliday }} {{ __("employees") }}
        </div>
        <router-link 
          v-if="isManager && hasHolidaysToday"
          :to="{ name: 'TodayHolidaysList' }" 
          class="text-sm font-medium text-blue-600"
        >
          {{ __("View All") }}
        </router-link>
      </div>
    </div>
    
    <!-- Single Holiday (Employee View) -->
    <div v-if="!isManager" class="bg-white rounded p-4">
      <div class="flex flex-row items-center justify-between">
        <div class="flex flex-row items-center gap-3">
          <FeatherIcon name="calendar" class="h-5 w-5 text-gray-500" />
          <div class="flex flex-col">
            <div class="text-base font-bold text-gray-800">
              {{ holidayLists[0]?.holidays[0]?.description }}
            </div>
            <div class="text-sm text-gray-600">
              {{ __("Today is holiday") }}
            </div>
          </div>
        </div>
        <div class="text-base font-bold text-gray-800">
          {{ formattedTodayDate }}
        </div>
      </div>
    </div>

    <!-- Multiple Holiday Lists (Manager View) -->
    <div v-else class="flex flex-col gap-3">
      <div 
        v-for="holidayList in holidayLists" 
        :key="holidayList.holiday_list_name"
        class="bg-white rounded p-4"
      >
        <!-- Holiday List Header -->
        <div class="flex flex-row items-center justify-between mb-3">
          <div class="flex flex-row items-center gap-3">
            <FeatherIcon name="calendar" class="h-5 w-5 text-gray-500" />
            <div class="flex flex-col">
              <div class="text-base font-bold text-gray-800">
                {{ holidayList.holidays[0]?.description }}
              </div>
              <div class="text-sm text-gray-600">
                {{ holidayList.holiday_list_name }}
              </div>
            </div>
          </div>
          <div class="text-base font-bold text-gray-800">
            {{ formattedTodayDate }}
          </div>
        </div>

        <!-- Employees on this holiday -->
        <div v-if="holidayList.employees_count > 0" class="flex flex-col gap-2">
          <div class="text-sm text-gray-600">
            {{ holidayList.employees_count }} {{ __("employees on holiday") }}
          </div>
          
          <!-- Sample employee avatars -->
          <div class="flex flex-row gap-2 items-center">
            <div 
              v-for="employee in holidayList.sample_employees?.slice(0, 3)" 
              :key="employee"
              class="h-8 w-8 rounded-full bg-gray-200 flex items-center justify-center text-xs font-medium text-gray-700"
            >
              {{ getEmployeeInitials(employee) }}
            </div>
            
            <!-- Show more indicator -->
            <div 
              v-if="holidayList.employees_count > 3"
              class="h-8 w-8 rounded-full bg-gray-100 flex items-center justify-center text-xs font-medium text-gray-600"
            >
              +{{ holidayList.employees_count - 3 }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, inject } from 'vue'
import { FeatherIcon } from 'frappe-ui'
import { createTodayHolidaysResource, getEmployeeInitials } from '@/data/todayHolidaysData.js'

const __ = inject('$translate')
const employee = inject('$employee')
const dayjs = inject('$dayjs')

// Use the new enhanced API resource
const todayHolidaysData = createTodayHolidaysResource(employee.data)

// Check if there are any holidays today
const hasHolidaysToday = computed(() => {
  return todayHolidaysData.data?.has_holidays_today || false
})

// Check if current user is a manager
const isManager = computed(() => {
  return todayHolidaysData.data?.is_manager || false
})

// Get holiday lists
const holidayLists = computed(() => {
  return todayHolidaysData.data?.holiday_lists || []
})

// Calculate total employees on holiday (for managers)
const totalEmployeesOnHoliday = computed(() => {
  if (!isManager.value || !holidayLists.value.length) return 0
  
  return holidayLists.value.reduce((total, list) => {
    return total + (list.employees_count || 0)
  }, 0)
})

// Format today's date
const formattedTodayDate = computed(() => {
  return dayjs().format('ddd, D MMM YYYY')
})
</script>