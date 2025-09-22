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
					<div class="text-lg text-gray-800 font-bold mb-3">{{ __("Recent Attendance Regularizations") }}</div>
					
					<!-- Tab Buttons -->
					<TabButtons
						:buttons="TAB_BUTTONS"
						v-model="activeTab"
						class="mb-4"
					/>

					<!-- My Requests Tab -->
					<div v-if="activeTab === 'My Requests'">
						<div class="flex flex-col bg-white rounded overflow-hidden" v-if="myRegularisationRequests.data?.length">
							<div
								class="flex flex-row p-3.5 items-center justify-between border-b cursor-pointer"
								v-for="request in myRegularisationRequests.data.slice(0, 5)"
								:key="request.name"
								@click="viewRequest(request)"
							>
								<AttendanceRegularizationItem
									:doc="request"
									:showEmployee="false"
								/>
							</div>
							<router-link
								:to="{ name: 'AttendanceRegularizationHistoryView', query: { tab: 'my' } }"
								v-slot="{ navigate }"
							>
								<Button
									variant="ghost"
									@click="navigate"
									class="w-full !text-gray-600 py-6 text-sm border-none bg-white hover:bg-white"
								>
									{{ __("View All") }}
								</Button>
							</router-link>
						</div>
						<div v-else class="bg-white rounded p-8 text-center text-gray-500">
							{{ __('You have not submitted any attendance regularization requests') }}
						</div>
					</div>

					<!-- Team Requests Tab -->
					<div v-if="activeTab === 'Team Requests'">
						<div class="flex flex-col bg-white rounded overflow-hidden" v-if="teamRegularisationRequests.data?.length">
							<div
								class="flex flex-row p-3.5 items-center justify-between border-b cursor-pointer"
								v-for="request in teamRegularisationRequests.data.slice(0, 5)"
								:key="request.name"
								@click="viewRequest(request)"
							>
								<AttendanceRegularizationItem
									:doc="request"
									:showEmployee="true"
								/>
							</div>
							<router-link
								:to="{ name: 'AttendanceRegularizationHistoryView', query: { tab: 'team' } }"
								v-slot="{ navigate }"
							>
								<Button
									variant="ghost"
									@click="navigate"
									class="w-full !text-gray-600 py-6 text-sm border-none bg-white hover:bg-white"
								>
									{{ __("View All") }}
								</Button>
							</router-link>
						</div>
						<div v-else class="bg-white rounded p-8 text-center text-gray-500">
							{{ __('No attendance regularization requests from your team') }}
						</div>
					</div>
				</div>
				<div>
					<div class="text-lg text-gray-800 font-bold mb-3">{{ __("Recent Sunday/Holiday Working Requests") }}</div>
					
					<!-- Tab Buttons for Sunday/Holiday Working -->
					<TabButtons
						:buttons="SUNDAY_HOLIDAY_TAB_BUTTONS"
						v-model="sundayHolidayActiveTab"
						class="mb-4"
					/>

					<!-- My Sunday/Holiday Requests Tab -->
					<div v-if="sundayHolidayActiveTab === 'My Requests'">
						<div class="flex flex-col bg-white rounded overflow-hidden" v-if="mySundayHolidayWorkingRequests.data?.length">
							<div
								class="flex flex-row p-3.5 items-center justify-between border-b cursor-pointer"
								v-for="request in mySundayHolidayWorkingRequests.data.slice(0, 5)"
								:key="request.name"
								@click="viewSundayHolidayRequest(request)"
							>
								<SundayHolidayWorkingRequestHistoryItem
									:doc="request"
									:showEmployee="false"
								/>
							</div>
							<router-link
								:to="{ name: 'SundayHolidayWorkingRequestHistoryView' }"
								v-slot="{ navigate }"
							>
								<Button
									variant="ghost"
									@click="navigate"
									class="w-full !text-gray-600 py-6 text-sm border-none bg-white hover:bg-white"
								>
									{{ __("View All") }}
								</Button>
							</router-link>
						</div>
						<div v-else class="bg-white rounded p-8 text-center text-gray-500">
							{{ __('You have not submitted any Sunday/Holiday working requests') }}
						</div>
					</div>

					<!-- Team Sunday/Holiday Requests Tab -->
					<div v-if="sundayHolidayActiveTab === 'Team Requests'">
						<div class="flex flex-col bg-white rounded overflow-hidden" v-if="teamSundayHolidayWorkingRequests.data?.length">
							<div
								class="flex flex-row p-3.5 items-center justify-between border-b cursor-pointer"
								v-for="request in teamSundayHolidayWorkingRequests.data.slice(0, 5)"
								:key="request.name"
								@click="viewSundayHolidayRequest(request)"
							>
								<SundayHolidayWorkingRequestHistoryItem
									:doc="request"
									:showEmployee="true"
								/>
							</div>
							<router-link
								:to="{ name: 'SundayHolidayWorkingRequestHistoryView' }"
								v-slot="{ navigate }"
							>
								<Button
									variant="ghost"
									@click="navigate"
									class="w-full !text-gray-600 py-6 text-sm border-none bg-white hover:bg-white"
								>
									{{ __("View All") }}
								</Button>
							</router-link>
						</div>
						<div v-else class="bg-white rounded p-8 text-center text-gray-500">
							{{ __('No Sunday/Holiday working requests from your team') }}
						</div>
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
import { computed, inject, markRaw, ref } from "vue"
import { createResource, Button } from "frappe-ui"

import BaseLayout from "@/components/BaseLayout.vue"
import ShiftAssignmentItem from "@/components/ShiftAssignmentItem.vue"
import RequestList from "@/components/RequestList.vue"
import AttendanceCalendar from "@/components/AttendanceCalendar.vue"
import AttendanceRegularizationItem from "@/components/AttendanceRegularizationItem.vue"
import SundayHolidayWorkingRequestHistoryItem from "@/components/SundayHolidayWorkingRequestHistoryItem.vue"
import TabButtons from "@/components/TabButtons.vue"
import { useRouter } from "vue-router"

import {
	getShiftDates,
	getTotalShiftDays,
	getShiftTiming,
} from "@/data/attendance"
import { myRegularisationRequests, teamRegularisationRequests } from "@/data/regularisation"
import { mySundayHolidayWorkingRequests, teamSundayHolidayWorkingRequests } from "@/data/sundayHolidayWorkingRequest"

const __ = inject("$translate")
const employee = inject("$employee")
const dayjs = inject("$dayjs")
const router = useRouter()

const TAB_BUTTONS = ["My Requests", "Team Requests"]
const activeTab = ref("My Requests")
const SUNDAY_HOLIDAY_TAB_BUTTONS = ["My Requests", "Team Requests"]
const sundayHolidayActiveTab = ref("My Requests")
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

function viewSundayHolidayRequest(request) {
	router.push({
		name: 'SundayHolidayWorkingRequestDetailView',
		params: { id: request.name }
	})
}

const upcomingShifts = computed(() => {
	const filteredShifts = shifts.data?.filter((shift) => shift.is_upcoming)

	// show only 5 upcoming shifts
	return filteredShifts?.slice(0, 5)
})
</script>
