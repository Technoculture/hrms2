<template>
	<BaseLayout pageTitle="Attendance">
		<template #body>
			<div class="flex flex-col mt-7 mb-7 p-4 gap-7">
				<AttendanceCalendar />
				<div class="w-full">
					<router-link :to="{ name: 'AttendanceRegularizationFormView' }" v-slot="{ navigate }">
						<Button @click="navigate" variant="solid" class="w-full py-5 text-base">
							{{ __("Raise Regularization") }}
						</Button>
					</router-link>
				</div>
				<div>
					<div class="text-lg text-gray-800 font-bold">{{ __("Recent Attendance Regularizations") }}</div>
					<!-- <RequestList
						:component="markRaw(AttendanceRequestItem)"
						:items="myAttendanceRequests?.data?.slice(0, 5)"
						:addListButton="true"
						:listButtonRoute="__('AttendanceRequestListView')"
					/> -->
					<div class="flex flex-col bg-white rounded mt-5 overflow-auto p-4">
						<div v-if="myRegularisationRequests.loading" class="text-center py-8">
							<div class="text-gray-500 text-sm">{{ __('Loading...') }}</div>
						</div>
						
						<div v-else-if="!myRegularisationRequests.data || myRegularisationRequests.data.length === 0" class="text-center py-8">
							<EmptyState 
								message="You have not submitted any attendance regularization requests"
							/>
						</div>
						
						<div v-else class="flex flex-col gap-3 mb-0 pb-0">
							<AttendanceRegularizationItem 
								v-for="request in myRegularisationRequests.data" 
								:key="request.name"
								:doc="request"
								:showEmployee="true"
								:class="' borner-none border-0 border-b-2 !p-3 rounded-none'"
								@click="viewRequest(request)"
							/>
						</div>
						<router-link
							:to="{ name: 'AttendanceRegularizationHistoryView' }"
							v-slot="{ navigate }"
							:class="'h-full'"
						>
							<Button
								variant="ghost"
								@click="navigate"
								class="w-full !text-gray-600 pt-6 text-sm border-none bg-white hover:bg-white"
							>
								{{ __("View List") }}
							</Button>
						</router-link>
					</div>
				</div>
				<div>
					<div class="text-lg text-gray-800 font-bold">{{ __("My Shifts") }}</div>
					<RequestList
						:component="markRaw(ShiftAssignmentItem)"
						:items="upcomingShifts"
						:addListButton="true"
						listButtonRoute="ShiftAssignmentListView"
						:emptyStateMessage="__('You have no upcoming shifts')"
					/>
				</div>
				<!-- <div class="w-full">
					<router-link :to="{ name: 'ShiftRequestFormView' }" v-slot="{ navigate }">
						<Button @click="navigate" variant="solid" class="w-full py-5 text-base">
							{{ __("Request a Shift") }}
						</Button>
					</router-link>
				</div> -->
				<!-- <div>
					<div class="text-lg text-gray-800 font-bold">{{ __("Recent Shift Requests") }}</div>
					<RequestList
						:component="markRaw(ShiftRequestItem)"
						:items="myShiftRequests?.data?.slice(0, 5)"
						:addListButton="true"
						listButtonRoute="ShiftRequestListView"
					/>
				</div> -->
			</div>
		</template>
	</BaseLayout>
</template>

<script setup>
import { computed, inject, markRaw } from "vue"
import { createResource } from "frappe-ui"

import BaseLayout from "@/components/BaseLayout.vue"
import AttendanceRequestItem from "@/components/AttendanceRequestItem.vue"
import ShiftRequestItem from "@/components/ShiftRequestItem.vue"
import ShiftAssignmentItem from "@/components/ShiftAssignmentItem.vue"
import RequestList from "@/components/RequestList.vue"
import AttendanceCalendar from "@/components/AttendanceCalendar.vue"
import AttendanceRegularizationItem from "@/components/AttendanceRegularizationItem.vue"
import { useRouter } from "vue-router"

import {
	getShiftDates,
	getTotalShiftDays,
	getShiftTiming,
	myAttendanceRequests,
	myShiftRequests,
} from "@/data/attendance"
import { myRegularisationRequests } from "@/data/regularisation"

const employee = inject("$employee")
const dayjs = inject("$dayjs")
const router = useRouter()
const shifts = createResource({
	url: "hrms.api.get_shifts",
	auto: true,
	cache: "hrms:shifts",
	makeParams() {
		return {
			employee: employee.data?.name,
		}
	},
	transform: (data) => {
		return data.map((assignment) => {
			assignment.doctype = "Shift Assignment"
			assignment.is_upcoming = !assignment.end_date || dayjs(assignment.end_date).isAfter(dayjs())
			assignment.shift_dates = getShiftDates(assignment)
			assignment.total_shift_days = getTotalShiftDays(assignment)
			assignment.shift_timing = getShiftTiming(assignment)
			return assignment
		})
	},
})
function viewRequest(request) {
	router.push({
		name: 'AttendanceRegularizationDetailView',
		params: { id: request.name }
	})
}

const upcomingShifts = computed(() => {
	const filteredShifts = shifts.data?.filter((shift) => shift.is_upcoming)

	// show only 5 upcoming shifts
	return filteredShifts?.slice(0, 5)
})
</script>
