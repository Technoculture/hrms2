import { createResource } from "frappe-ui"
import { employeeResource } from "./employee"

export const myRegularisationRequests = createResource({
	url: "hrms.api.get_attendance_regularization_requests",
	params: {
        employee: employeeResource.data.user_id,
		limit: 5,
        filters: {
            employee: employeeResource.data.name,
        }
	},
	auto: true,
	cache: "hrms:my_regularisation_requests"
})