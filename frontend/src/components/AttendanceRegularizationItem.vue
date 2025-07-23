<template>
	<div class="bg-white rounded-lg border border-gray-200 p-4 cursor-pointer hover:bg-gray-50 transition-colors">
		<div class="flex items-center justify-between">
			<div class="flex items-center gap-3 flex-1">
				<!-- Calendar Icon -->
				<div class="flex-shrink-0">
					<FeatherIcon name="calendar" class="h-5 w-5 text-gray-400" />
				</div>
				
				<!-- Request Details -->
				<div class="flex-1 min-w-0">
					<div class="flex items-center gap-2 mb-1">
						<!-- <h3 class="text-sm font-medium text-gray-900 truncate">
							{{ __('Attendance Regularization') }}
						</h3> -->
						<span  class="text-xs text-gray-900">
							• {{ getEmployeeName(props.doc) }}
						</span>
					</div>
					<p class="text-xs text-gray-500">
						{{ formatDate(getAttendanceDate(props.doc)) }} • {{ formatRelativeTime(props.doc.creation) }}
					</p>
				</div>
			</div>
			
			<!-- Status and Arrow -->
			<div class="flex items-center gap-2 flex-shrink-0">
				<div class="px-2 py-1 rounded-full text-xs font-medium" :class="getStatusClass(getWorkflowState(props.doc))">
					{{ getStatusText(getWorkflowState(props.doc)) }}
				</div>
				<FeatherIcon name="chevron-right" class="h-4 w-4 text-gray-400" />
			</div>
		</div>
	</div>
</template>

<script setup>
import { inject } from "vue"
import { FeatherIcon } from "frappe-ui"

const __ = inject("$translate")
const dayjs = inject("$dayjs")

const props = defineProps({
	doc: {
		type: Object,
		required: true,
	},
	showEmployee: {
		type: Boolean,
		default: false,
	},
})

function formatDate(date) {
	return dayjs(date).format('D MMM')
}

function formatRelativeTime(datetime) {
	const now = dayjs()
	const target = dayjs(datetime)
	const diffDays = now.diff(target, 'day')
	
	if (diffDays === 0) {
		return __('Today')
	} else if (diffDays === 1) {
		return __('Yesterday')
	} else if (diffDays < 7) {
		return `${diffDays}${__('d')}`
	} else {
		return target.format('D MMM')
	}
}

function getStatusClass(status) {
	switch (status) {
		case 'Approved':
			return 'bg-green-100 text-green-700'
		case 'Rejected':
			return 'bg-red-100 text-red-700'
		case 'Pending':
		case 'Draft':
		default:
			return 'bg-orange-100 text-orange-700'
	}
}

function getStatusText(status) {
	switch (status) {
		case 'Approved':
			return __('Approved')
		case 'Rejected':
			return __('Rejected')
		case 'Pending':
			return __('Pending')
		case 'Draft':
			return __('Draft')
		default:
			return status || __('Pending')
	}
}

// Field mapping functions for API response
function getEmployeeName(doc) {
	return doc.custom_employee_name || doc.employee_name || doc.employee || ''
}

function getAttendanceDate(doc) {
	return doc.date || doc.attendance_date || ''
}

function getWorkflowState(doc) {
	// Map docstatus to workflow state
	if (doc.docstatus === 1) {
		return 'Approved'
	} else if (doc.docstatus === 2) {
		return 'Rejected'
	} else if (doc.docstatus === 0) {
		return 'Pending'
	}
	return doc.workflow_state || 'Pending'
}
</script>