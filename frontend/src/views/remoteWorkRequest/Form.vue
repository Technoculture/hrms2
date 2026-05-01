<template>
	<ion-page>
		<ion-content :fullscreen="true">
			<FormView
				v-if="formFields.data"
				doctype="Remote Work Request"
				v-model="remoteWorkRequest"
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
const sessionEmployee = inject("$employee")
const today = dayjs().format("YYYY-MM-DD")

const props = defineProps({
	id: {
		type: String,
		required: false,
	},
})

const remoteWorkRequest = ref({})

const formFields = createResource({
	url: "hrms.api.get_doctype_fields",
	params: { doctype: "Remote Work Request" },
	transform(data) {
		return getFilteredFields(data).map((field) => {
			if (["from_date", "to_date"].includes(field.fieldname)) {
				field.minDate = today
			}

			if (field.fieldname === "status") {
				field.default = "Open"
				field.read_only = true
			}

			if (field.fieldname === "rejection_reason") {
				field.hidden = true
			}

			return field
		})
	},
})
formFields.reload()

watch(
	() => remoteWorkRequest.value.from_date,
	(fromDate) => {
		if (!fromDate) return

		const toDateField = formFields.data?.find((field) => field.fieldname === "to_date")
		if (toDateField) {
			toDateField.minDate = fromDate
		}

		if (!remoteWorkRequest.value.to_date) {
			remoteWorkRequest.value.to_date = fromDate
		}
	}
)

watch(
	() => remoteWorkRequest.value.status,
	(status) => {
		const rejectionReasonField = formFields.data?.find(
			(field) => field.fieldname === "rejection_reason"
		)
		if (!rejectionReasonField) return

		rejectionReasonField.hidden = status !== "Rejected"
	}
)

function getFilteredFields(fields) {
	const excludeFields = [
		"amended_from",
		"employee",
		"employee_name",
		"l1_manager",
		"department",
		"company",
		"attendance_snapshots",
	]

	if (!props.id) {
		excludeFields.push("status", "rejection_reason", "linked_attendance_request")
	}

	return fields.filter((field) => !excludeFields.includes(field.fieldname))
}

function validateForm() {
	remoteWorkRequest.value.employee = sessionEmployee.data.name

	if (!remoteWorkRequest.value.from_date) {
		throw new Error(__("From Date is required"))
	}

	if (!remoteWorkRequest.value.to_date) {
		throw new Error(__("To Date is required"))
	}

	if (dayjs(remoteWorkRequest.value.to_date).isBefore(dayjs(remoteWorkRequest.value.from_date), "day")) {
		throw new Error(__("To Date cannot be before From Date"))
	}

	if (!remoteWorkRequest.value.description) {
		throw new Error(__("Reason / Work Plan is required"))
	}
}
</script>
