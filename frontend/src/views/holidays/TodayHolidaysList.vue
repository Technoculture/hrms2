<template>
	<ion-page>
		<ion-header class="ion-no-border">
			<div class="w-full sm:w-96">
				<div class="flex flex-col bg-white shadow-sm">
					<!-- Header with back button -->
					<div class="flex items-center justify-between p-4">
						<div class="flex items-center gap-3">
							<button @click="goBack" class="p-1">
								<FeatherIcon name="chevron-left" class="h-6 w-6 text-gray-700" />
							</button>
							<h1 class="text-xl font-semibold text-gray-900">{{ __('Team Holidays Today') }}</h1>
						</div>
					</div>
					
					<!-- Summary -->
					<div class="px-4 pb-4">
						<div class="text-sm text-gray-600">
							{{ formattedTodayDate }} • {{ totalEmployeesOnHoliday }} {{ __("employees on holiday") }}
						</div>
					</div>
				</div>
			</div>
		</ion-header>

		<ion-content class="ion-no-padding">
			<div class="flex flex-col h-full w-screen sm:w-96">
				<!-- Content -->
				<div class="flex-1 overflow-y-auto p-4 scrollbar-hide">
					<div v-if="todayHolidaysData.loading" class="flex justify-center items-center py-8">
						<div class="text-gray-500">{{ __('Loading...') }}</div>
					</div>
					
					<div v-else-if="todayHolidaysData.error" class="text-center py-8">
						<div class="text-red-600">{{ __('Error loading holiday data') }}</div>
					</div>
					
					<div v-else-if="!hasHolidaysToday" class="text-center py-8">
						<EmptyState 
							:title="__('No holidays today')"
							:description="__('No team members are on holiday today')"
						/>
					</div>
					
					<div v-else class="space-y-4">
						<!-- Holiday List Sections -->
						<div 
							v-for="holidayList in holidayLists" 
							:key="holidayList.holiday_list_name"
							class="bg-white rounded-lg shadow-sm"
						>
							<!-- Holiday List Header -->
							<div class="p-4 border-b border-gray-100">
								<div class="flex items-center gap-3 mb-2">
									<FeatherIcon name="calendar" class="h-5 w-5 text-gray-500" />
									<div class="flex flex-col">
										<div class="text-lg font-semibold text-gray-900">
											{{ holidayList.holidays[0]?.description }}
										</div>
										<div class="text-sm text-gray-600">
											{{ holidayList.holiday_list_name }}
										</div>
									</div>
								</div>
								<div class="text-sm text-gray-600">
									{{ holidayList.employees_count }} {{ __("employees") }}
								</div>
							</div>

							<!-- Employee List -->
							<div class="divide-y divide-gray-100">
								<div 
									v-for="employeeName in holidayList.sample_employees" 
									:key="employeeName"
									class="p-4 flex items-center gap-3"
								>
									<!-- Employee Avatar -->
									<div class="h-10 w-10 rounded-full bg-gray-200 flex items-center justify-center text-sm font-medium text-gray-700">
										{{ getEmployeeInitials(employeeName) }}
									</div>
									
									<!-- Employee Info -->
									<div class="flex-1">
										<div class="text-base font-medium text-gray-900">
											{{ employeeName }}
										</div>
									</div>
								</div>
							</div>
						</div>
					</div>
				</div>
			</div>
		</ion-content>
	</ion-page>
</template>

<script setup>
import { computed, inject } from "vue"
import { IonPage, IonHeader, IonContent } from "@ionic/vue"
import { FeatherIcon } from "frappe-ui"
import { useRouter } from "vue-router"

import EmptyState from "@/components/EmptyState.vue"
import { createTodayHolidaysResource, getEmployeeInitials } from '@/data/todayHolidaysData.js'

const __ = inject("$translate")
const dayjs = inject("$dayjs")
const employee = inject("$employee")
const router = useRouter()

// Use the same resource as the main component
const todayHolidaysData = createTodayHolidaysResource(employee.data)

// Check if there are any holidays today
const hasHolidaysToday = computed(() => {
  return todayHolidaysData.data?.has_holidays_today || false
})

// Get holiday lists
const holidayLists = computed(() => {
  return todayHolidaysData.data?.holiday_lists || []
})

// Calculate total employees on holiday
const totalEmployeesOnHoliday = computed(() => {
  if (!holidayLists.value.length) return 0
  
  return holidayLists.value.reduce((total, list) => {
    return total + (list.employees_count || 0)
  }, 0)
})

// Format today's date
const formattedTodayDate = computed(() => {
  return dayjs().format('ddd, D MMM YYYY')
})

function goBack() {
  router.back()
}
</script>

<style scoped>
.scrollbar-hide {
	-ms-overflow-style: none;  /* Internet Explorer 10+ */
	scrollbar-width: none;  /* Firefox */
}
.scrollbar-hide::-webkit-scrollbar { 
	display: none;  /* Safari and Chrome */
}
</style>