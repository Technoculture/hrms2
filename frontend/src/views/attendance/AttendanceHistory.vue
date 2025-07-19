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
							<h1 class="text-xl font-semibold text-gray-900">{{ __('Time logs') }}</h1>
						</div>
						<div class="flex items-center gap-3">
							<FeatherIcon name="bell" class="h-5 w-5 text-gray-500" />
							<div class="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center">
								<span class="text-sm font-medium text-gray-600">P</span>
							</div>
						</div>
					</div>
					
					<!-- Month Navigation -->
					<div class="flex justify-between items-center px-4 pb-4">
						<button @click="previousMonth" class="p-2">
							<FeatherIcon name="chevron-left" class="h-5 w-5 text-gray-600" />
						</button>
						<h2 class="text-base font-medium text-purple-600">{{ currentMonthLabel }}</h2>
						<button @click="nextMonth" class="p-2" :disabled="isCurrentMonth">
							<FeatherIcon name="chevron-right" class="h-5 w-5" :class="isCurrentMonth ? 'text-gray-300' : 'text-gray-600'" />
						</button>
					</div>
				</div>
			</div>
		</ion-header>

		<ion-content class="ion-no-padding">
			<div class="flex flex-col h-full w-screen sm:w-96">
				<!-- Content -->
				<div class="flex-1 overflow-y-auto p-4 scrollbar-hide">
					<div v-if="attendanceHistory.loading" class="flex justify-center items-center py-8">
						<div class="text-gray-500">{{ __('Loading...') }}</div>
					</div>
					
					<div v-else-if="attendanceHistory.error" class="text-center py-8">
						<div class="text-red-600">{{ __('Error loading attendance history') }}</div>
					</div>
					
					<div v-else-if="!attendanceHistory.data || attendanceHistory.data.length === 0" class="text-center py-8">
						<EmptyState 
							:title="__('No attendance records')"
							:description="__('No attendance data found for this month')"
						/>
					</div>
					
					<div v-else class="space-y-3">
						<AttendanceHistoryItem 
							v-for="record in attendanceHistory.data" 
							:key="record.date"
							:ref="el => itemRefs[record.date] = el"
							:doc="record"
							@expand="handleExpand"
						/>
					</div>
				</div>

				<!-- Today Button (floating) -->
				<div class="fixed bottom-20 right-4 z-10">
					<button 
						@click="goToToday"
						v-if="!isCurrentMonth"
						class="bg-purple-600 text-white px-4 py-2 rounded-full shadow-lg flex items-center gap-2"
					>
						<FeatherIcon name="calendar" class="h-4 w-4" />
						{{ __('Today') }}
					</button>
				</div>
			</div>
		</ion-content>
	</ion-page>
</template>

<script setup>
import { ref, computed, inject, watch } from "vue"
import { IonPage, IonHeader, IonContent } from "@ionic/vue"
import { createResource, FeatherIcon } from "frappe-ui"
import { useRouter } from "vue-router"

import AttendanceHistoryItem from "@/components/AttendanceHistoryItem.vue"
import EmptyState from "@/components/EmptyState.vue"

const __ = inject("$translate")
const dayjs = inject("$dayjs")
const employee = inject("$employee")
const router = useRouter()

// Current month state
const currentMonth = ref(dayjs())

// Refs for managing expand/collapse
const itemRefs = ref({})

const currentMonthLabel = computed(() => {
	return currentMonth.value.format('MMMM, YYYY')
})

const isCurrentMonth = computed(() => {
	return currentMonth.value.isSame(dayjs(), 'month')
})

// Attendance history resource
const attendanceHistory = createResource({
	url: "hrms.api.get_attendance_history",
	makeParams() {
		return {
			employee: employee.data?.name,
			month: currentMonth.value.format('YYYY-MM'),
		}
	},
	auto: true,
})

// Watch for month changes
watch(currentMonth, () => {
	attendanceHistory.reload()
})

// Navigation functions
function previousMonth() {
	currentMonth.value = currentMonth.value.subtract(1, 'month')
}

function nextMonth() {
	if (!isCurrentMonth.value) {
		currentMonth.value = currentMonth.value.add(1, 'month')
	}
}

function goToToday() {
	currentMonth.value = dayjs()
}

function goBack() {
	router.back()
}

function handleExpand(expandedDate) {
	// Collapse all other cards
	Object.keys(itemRefs.value).forEach(date => {
		if (date !== expandedDate && itemRefs.value[date]) {
			itemRefs.value[date].collapse()
		}
	})
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