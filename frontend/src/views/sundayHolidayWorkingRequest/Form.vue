<template>
	<ion-page>
		<ion-content :fullscreen="true">
			<FormView
				v-if="formFields.data"
				doctype="Sunday Holiday Working Request"
				v-model="sundayHolidayWorkingRequest"
				:isSubmittable="true"
				:fields="formFields.data"
				:id="props.id"
				:showAttachmentView="false"
				@validateForm="validateForm"
			/>
		</ion-content>
	</ion-page>
</template>

<script setup>
import { IonPage, IonContent } from "@ionic/vue"
import { createResource } from "frappe-ui"
import { ref, watch, inject } from "vue"

import FormView from "@/components/FormView.vue"

const dayjs = inject("$dayjs")
const __ = inject("$translate")
const today = dayjs().format("YYYY-MM-DD")

const props = defineProps({
	id: {
		type: String,
		required: false,
	},
})

const sessionEmployee = inject("$employee")
const currEmployee = ref(sessionEmployee.data.name)

// reactive object to store form data
const sundayHolidayWorkingRequest = ref({})

// get form fields
const formFields = createResource({
	url: "hrms.api.get_doctype_fields",
	params: { doctype: "Sunday Holiday Working Request" },
	transform(data) {
		let fields = getFilteredFields(data)

		return fields.map((field) => {
			// Set default values and configurations
			if (field.fieldname === "employee") {
				field.default = currEmployee.value
			}
			if (field.fieldname === "status") {
				field.default = "Open"
			}
			if (field.fieldname === "work_date") {
				// Set minimum date to today
				field.minDate = today
			}
			if (field.fieldname === "rejection_reason") {
				// Initially hide rejection reason field
				field.hidden = true
				field.reqd = false
			}

			return field
		})
	},
})
formFields.reload()

// form scripts
watch(
	() => sundayHolidayWorkingRequest.value.employee,
	(employee_id) => {
		if (props.id && employee_id !== currEmployee.value) {
			// if employee is not the current user, check if current user can approve
			checkApprovalRights()
		}
		currEmployee.value = employee_id
	}
)

watch(
	() => sundayHolidayWorkingRequest.value.work_date,
	(work_date) => {
		validateWorkDate(work_date)
	}
)

watch(
	() => sundayHolidayWorkingRequest.value.status,
	(status) => {
		handleStatusChange(status)
	}
)

// helper functions
function getFilteredFields(fields) {
	// reduce noise from the form view by excluding unnecessary fields
	const excludeFields = [
		"amended_from",
		"section_main",
		"column_right",
	]

	const employeeFields = [
		"employee",
	]

	// Always exclude status field for new requests (users can't choose status)
	// For existing requests, only show status field for managers
	if (!props.id) {
		excludeFields.push(...employeeFields, "status")
	}

	return fields.filter((field) => !excludeFields.includes(field.fieldname))
}

function checkApprovalRights() {
	// Check if current user can approve this request
	// Allow editing if the user is different from the employee (HR Manager scenario)
	const isHRManager = sessionEmployee.data.name !== sundayHolidayWorkingRequest.value.employee
	
	if (isHRManager) {
		// HR Manager can edit status and rejection reason
		formFields.data.forEach((field) => {
			if (["status", "rejection_reason"].includes(field.fieldname)) {
				field.read_only = false
				// Show status field for HR managers
				if (field.fieldname === "status") {
					field.hidden = false
				}
			} else {
				// Make other fields read-only for HR managers
				field.read_only = true
			}
		})
	} else {
		// Employee viewing their own request - make everything read-only
		formFields.data.forEach((field) => {
			field.read_only = true
		})
	}
}

function validateWorkDate(work_date) {
	if (!work_date) return

	const workDate = dayjs(work_date)
	const todayDate = dayjs()

	// Check if date is in the past
	if (workDate.isBefore(todayDate, 'day')) {
		const workDateField = formFields.data.find(
			(field) => field.fieldname === "work_date"
		)
		if (workDateField) {
			workDateField.error_message = __("Work date cannot be in the past")
		}
		return
	}

	// Check if it's a Sunday (day 0) or within current week
	const isCurrentWeek = workDate.isSame(todayDate, 'week')
	const isSunday = workDate.day() === 0
	const isUpcomingSunday = isSunday && workDate.isAfter(todayDate, 'day')

	if (!isCurrentWeek && !isUpcomingSunday) {
		const workDateField = formFields.data.find(
			(field) => field.fieldname === "work_date"
		)
		if (workDateField) {
			workDateField.error_message = __("You can only request for current week holidays or upcoming Sunday")
		}
	} else {
		// Clear error message if validation passes
		const workDateField = formFields.data.find(
			(field) => field.fieldname === "work_date"
		)
		if (workDateField) {
			workDateField.error_message = ""
		}
	}
}

function handleStatusChange(status) {
	// Show/hide rejection reason field based on status
	const rejectionReasonField = formFields.data?.find(
		(field) => field.fieldname === "rejection_reason"
	)
	
	if (rejectionReasonField) {
		if (status === "Rejected") {
			rejectionReasonField.hidden = false
			rejectionReasonField.reqd = true
		} else {
			rejectionReasonField.hidden = true
			rejectionReasonField.reqd = false
			// Clear rejection reason if status is not rejected
			sundayHolidayWorkingRequest.value.rejection_reason = ""
		}
	}
}

function validateForm() {
	// Set employee to current user for new requests
	if (!props.id) {
		sundayHolidayWorkingRequest.value.employee = currEmployee.value
	}
	
	// Validate required fields
	if (!sundayHolidayWorkingRequest.value.work_date) {
		throw new Error(__("Work Date is required"))
	}
	
	if (!sundayHolidayWorkingRequest.value.work_description) {
		throw new Error(__("Work Description is required"))
	}

	// Validate rejection reason if status is rejected
	if (sundayHolidayWorkingRequest.value.status === "Rejected" && !sundayHolidayWorkingRequest.value.rejection_reason) {
		throw new Error(__("Rejection reason is required when rejecting a request"))
	}

	// Validate work date
	validateWorkDate(sundayHolidayWorkingRequest.value.work_date)
}
</script>