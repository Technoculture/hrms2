<template>
	<BaseLayout>
		<template #body>
			<div class="flex flex-col items-center my-7 p-4 gap-7">
				<CheckInPanel />
				<QuickLinks :items="quickLinks" :title="__('My Dashboard 📊')" />
				<EmployeesOnLeave />
				<TodayHoliday />
				<RequestPanel />
			</div>
		</template>
	</BaseLayout>
</template>

<script setup>
import { inject, markRaw } from "vue"

import CheckInPanel from "@/components/CheckInPanel.vue"
import QuickLinks from "@/components/QuickLinks.vue"
import BaseLayout from "@/components/BaseLayout.vue"
import RequestPanel from "@/components/RequestPanel.vue"
import EmployeesOnLeave from "@/components/EmployeesOnLeave.vue"
import TodayHoliday from "@/components/TodayHoliday.vue"
import AttendanceIcon from "@/components/icons/AttendanceIcon.vue"
import ShiftIcon from "@/components/icons/ShiftIcon.vue"
import LeaveIcon from "@/components/icons/LeaveIcon.vue"
import RegularizationIcon from "@/components/icons/RegularizationIcon.vue"
import ExpenseIcon from "@/components/icons/ExpenseIcon.vue"
import EmployeeAdvanceIcon from "@/components/icons/EmployeeAdvanceIcon.vue"
import SalaryIcon from "@/components/icons/SalaryIcon.vue"
import SundayHolidayWorkingIcon from "@/components/icons/SundayHolidayWorkingIcon.vue"

const __ = inject("$translate")

const quickLinks = [
	{
		icon: markRaw(RegularizationIcon),
		title: __("Attendance Regularization"),
		route: "AttendanceRegularizationFormView",
	},
	// {
		// icon: markRaw(ShiftIcon),
		// title: __("Request a Shift"),
		// route: "ShiftRequestFormView",
	//},
	{
		icon: markRaw(LeaveIcon),
		title: __("Request Leave"),
		route: "LeaveApplicationFormView",
	},	
	// {
	// 	icon: markRaw(ExpenseIcon),
	// 	title: __("Claim an Expense"),
	// 	route: "ExpenseClaimFormView",
	// },
	// {
	// 	icon: markRaw(EmployeeAdvanceIcon),
	// 	title: __("Request an Advance"),
	// 	route: "EmployeeAdvanceFormView",
	// },
	// {
	// 	icon: markRaw(SalaryIcon),
	// 	title: __("View Salary Slips"),
	// 	route: "SalarySlipsDashboard",
	// },
	{
		icon: markRaw(AttendanceIcon),
		title: __("Attendance Summary"),
		route: "AttendanceHistoryView",
	},
	{
		icon: markRaw(SundayHolidayWorkingIcon),
		title: __("Sunday/Holiday Working Request"),
		route: "SundayHolidayWorkingRequestFormView",
	},
	// {
	// 	icon: markRaw(AttendanceIcon),
	// 	title: __("Remote Work Request"),
	// 	route: "RemoteWorkRequestFormView",
	// },
	// {
	// 	icon: markRaw(RegularizationIcon),
	// 	title: __("Regularization History"),
	// 	route: "AttendanceRegularizationHistoryView",
	// },
]
</script>
