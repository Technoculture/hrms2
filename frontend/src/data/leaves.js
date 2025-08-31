import { createResource } from "frappe-ui"
import { employeeResource } from "./employee"

import dayjs from "@/utils/dayjs"

const transformLeaveData = (data) => {
	return data.map((leave) => {
		leave.leave_dates = getLeaveDates(leave)
		leave.doctype = "Leave Application"
		return leave
	})
}

export const getLeaveDates = (leave) => {
	if (leave.from_date == leave.to_date)
		return dayjs(leave.from_date).format("D MMM")
	else
		return `${dayjs(leave.from_date).format("D MMM")} - ${dayjs(
			leave.to_date
		).format("D MMM")}`
}

export const myLeaves = createResource({
	url: "hrms.api.get_leave_applications",
	params: {
		employee: employeeResource.data.name,
		limit: 5,
	},
	auto: true,
	cache: "hrms:my_leaves",
	transform(data) {
		return transformLeaveData(data)
	},
	onSuccess() {
		leaveBalance.reload()
	},
})
export const teamLeaves = createResource({
	url: "hrms.api.get_leave_applications_for_approval",
	params: {
		employee: employeeResource.data.name,
		approver_id: employeeResource.data.user_id,
		for_approval: 1,
		limit: 5,
	},
	auto: true,
	cache: "hrms:team_leaves",
	transform(data) {
		console.log("data", data)
		return transformLeaveData(data)
	},
})

// export const teamLeaves = createResource({
// 	url: "hrms.api.get_leave_applications",
// 	params: {
// 		employee: employeeResource.data.name,
// 		approver_id: employeeResource.data.user_id,
// 		for_approval: 1,
// 		limit: 5,
// 	},
// 	auto: true,
// 	cache: "hrms:team_leaves",
// 	transform(data) {
// 		return transformLeaveData(data)
// 	},
// })

export const leaveBalance = createResource({
	url: "hrms.api.get_leave_balance_map",
	params: {
		employee: employeeResource.data.name,
	},
	auto: true,
	cache: "hrms:leave_balance",
	transform: (data) => {
		// Calculate balance percentage for each leave type
		return Object.fromEntries(
			Object.entries(data).map(([leave_type, allocation]) => {
				allocation.balance_percentage =
					(allocation.balance_leaves / allocation.allocated_leaves) * 100
				return [leave_type, allocation]
			})
		)
	},
})

export const myLWBalance = createResource({
	url: "hrms.api.get_my_lwp_consumption",
	params: {
		employee: employeeResource.data.name,
	},
	auto: true,
	cache: "hrms:my_lwp_balance",
	transform: (data) => {
		return Object.fromEntries(
			Object.entries(data).map(([leave_type, allocation]) => {
				allocation.balance_percentage =
					(allocation.balance_leaves / allocation.allocated_leaves) * 100
				return [leave_type, allocation]
			})
		)
	},
})

export const halfDayQuota = createResource({
	url: "hrms.api.get_half_day_quota",
	params: {
		employee: employeeResource.data.name,
		date: dayjs().format("YYYY-MM-DD"),
	},
	auto: true,
	cache: "hrms:half_day_quota",
	transform: (data) => {
		if (!data) {
			return null
		}
		return Object.fromEntries(
			Object.entries(data).map(([half_day_type, allocation]) => {
				allocation.balance_percentage =
					(allocation.balance_leaves / allocation.allocated_leaves) * 100
				return [half_day_type, allocation]
			})
		)
	},
})

export const getMergedLeaveBalance = (leaveBalanceData, myLWBalanceData, halfDayQuotaData) => {
	let data = {}
	if (leaveBalanceData) {
		data = { ...data, ...leaveBalanceData }
	}
	if (myLWBalanceData) {
		data = { ...data, ...myLWBalanceData }
	}
	if (halfDayQuotaData) {
		data = { ...data, ...halfDayQuotaData }
	}
	return data
}
