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
							<h1 class="text-xl font-semibold text-gray-900">{{ __('Employees On Leave') }}</h1>
						</div>
						<div class="flex items-center gap-3">
							<FeatherIcon name="bell" class="h-5 w-5 text-gray-500" />
							<div class="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center">
								<span class="text-sm font-medium text-gray-600">P</span>
							</div>
						</div>
					</div>
				</div>
			</div>
		</ion-header>

		<ion-content class="ion-no-padding">
			<div class="flex flex-col h-full w-screen sm:w-96">
				<div class="flex-1 overflow-y-auto scrollbar-hide">
					<div v-if="employeesOnLeave.loading" class="p-4 text-center text-gray-500">
						{{ __("Loading...") }}
					</div>
					<div v-else-if="!employeesOnLeave.data || employeesOnLeave.data.length === 0" class="p-4 text-center">
						<EmptyState 
							:title="__('No employees on leave')"
							:description="__('No employees are currently on leave')"
						/>
					</div>
					<div v-else class="bg-white">
						<div 
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
				</div>
			</div>
		</ion-content>
	</ion-page>
</template>

<script setup>
import { inject } from 'vue'
import { IonPage, IonHeader, IonContent } from '@ionic/vue'
import { createResource, FeatherIcon } from 'frappe-ui'
import { useRouter } from 'vue-router'
import EmptyState from '@/components/EmptyState.vue'

const __ = inject('$translate')
const dayjs = inject('$dayjs')
const router = useRouter()

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