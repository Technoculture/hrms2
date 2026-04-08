import router from "@/router"
import { createResource } from "frappe-ui"
import { reactive } from "vue"
import { employeeResource } from "./employee"

let employeesByID = reactive({})
let employeesByUserID = reactive({})

export const employees = createResource({
	url: "hrms.api.get_all_employees",
	auto: true,
	transform(data) {
		Object.keys(employeesByID).forEach((key) => delete employeesByID[key])
		Object.keys(employeesByUserID).forEach((key) => delete employeesByUserID[key])

		const rows = Array.isArray(data) ? data : []
		return rows.map((employee) => {
			employee.isActive = employee.status === "Active"
			employeesByID[employee.name] = employee
			if (employee.user_id) {
				employeesByUserID[employee.user_id] = employee
			}

			return employee
		})
	},
	onError(error) {
		if (error && error.exc_type === "AuthenticationError") {
			router.push({ name: "Login" })
		}
	},
})

export function getEmployeeInfo(employeeID) {
	if (!employeeID) employeeID = employeeResource.data.name

	return employeesByID[employeeID]
}

export function getEmployeeInfoByUserID(userID) {
	return employeesByUserID[userID]
}
