import { createResource } from "frappe-ui"
import { employeeResource } from "./employee"
import dayjs from "@/utils/dayjs"

export function transformRemoteWorkRequestData(data) {
	return data.map((request) => {
		request.request_dates = formatRequestDates(request)
		request.doctype = "Remote Work Request"
		return request
	})
}

function formatRequestDates(request) {
	if (!request.from_date && !request.to_date) return ""
	if (request.from_date === request.to_date) {
		return dayjs(request.from_date).format("D MMM YYYY")
	}

	return `${dayjs(request.from_date).format("D MMM YYYY")} - ${dayjs(request.to_date).format("D MMM YYYY")}`
}

export const myRemoteWorkRequests = createResource({
	url: "frappe.client.get_list",
	makeParams() {
		return {
			doctype: "Remote Work Request",
			fields: [
				"name",
				"employee",
				"employee_name",
				"from_date",
				"to_date",
				"status",
				"description",
				"rejection_reason",
				"linked_attendance_request",
				"creation",
				"modified",
				"docstatus",
			],
			filters: {
				employee: employeeResource.data?.name,
			},
			order_by: "creation desc",
			limit: 5,
		}
	},
	auto: true,
	cache: "hrms:my_remote_work_requests",
	transform(data) {
		return transformRemoteWorkRequestData(data)
	},
})
