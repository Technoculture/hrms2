import { createResource } from "frappe-ui"
import { employeeResource } from "./employee"
import dayjs from "@/utils/dayjs"

const transformSundayHolidayWorkingRequestData = (data) => {
	return data.map((request) => {
		request.work_date_formatted = dayjs(request.work_date).format("D MMM YYYY")
		request.doctype = "Sunday Holiday Working Request"
		return request
	})
}

export const mySundayHolidayWorkingRequests = createResource({
	url: "frappe.client.get_list",
	params: {
		doctype: "Sunday Holiday Working Request",
		fields: [
			"name",
			"employee",
			"employee_name", 
			"work_date",
			"status",
			"work_description",
			"rejection_reason",
			"creation",
			"modified",
			"docstatus"
		],
		filters: {
			employee: employeeResource.data.name
		},
		order_by: "creation desc",
		limit: 5,
	},
	auto: true,
	cache: "hrms:my_sunday_holiday_working_requests",
	transform(data) {
		return transformSundayHolidayWorkingRequestData(data)
	},
})

export const teamSundayHolidayWorkingRequests = createResource({
	url: "hrms.api.get_sunday_holiday_working_requests_for_approver",
	params: {
		approver: employeeResource.data.user_id,
	},
	auto: true,
	cache: "hrms:team_sunday_holiday_working_request",
})