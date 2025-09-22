<template>
	<div class="bg-white rounded-lg border border-gray-200 p-4 cursor-pointer hover:bg-gray-50 transition-colors">
		<div class="flex items-center justify-between">
			<div class="flex items-center gap-3 flex-1">
				<!-- Calendar Icon -->
				<div class="flex-shrink-0">
					<FeatherIcon name="calendar-clock" class="h-5 w-5 text-gray-400" />
				</div>
				
				<!-- Request Details -->
				<div class="flex-1 min-w-0">
					<div class="flex items-center gap-2 mb-1">
						<span class="text-xs text-gray-900">
							
							<span>
								{{ getEmployeeName(props.doc) }} {{ props.doc.employee ? "(" + props.doc.employee + ")" : "" }}
							</span>
						</span>
					</div>
					<p class="text-xs text-gray-500">
						{{ formatDate(props.doc.work_date) }} • {{ formatRelativeTime(props.doc.creation) }}
					</p>
					<p class="text-xs text-gray-600 mt-1 truncate" v-if="props.doc.work_description">
						{{ truncateText(props.doc.work_description, 20) }}
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
	return dayjs(date).format('D MMM YYYY')
}

function formatRelativeTime(datetime) {
	const now = dayjs()
	const target = dayjs(datetime)

	const diffDays = now.startOf('day').diff(target.startOf('day'), 'day')

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
		case 'Cancelled':
			return 'bg-gray-100 text-gray-700'
		case 'Open':
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
		case 'Cancelled':
			return __('Cancelled')
		case 'Open':
			return __('Pending')
		case 'Pending':
			return __('Pending')
		case 'Draft':
			return __('Draft')
		default:
			return status || __('Pending')
	}
}

function truncateText(text, maxLength) {
	if (!text) return ""
	return text.length > maxLength ? text.substring(0, maxLength) + "..." : text
}

// Field mapping functions for API response
function getEmployeeName(doc) {
	return doc.employee_name || doc.employee || ''
}

function getWorkflowState(doc) {
	// For Sunday Holiday Working Request, use the status field directly
	// Map docstatus for submitted/cancelled states
	if (doc.docstatus === 1 && doc.status === 'Approved') {
		return 'Approved'
	} else if (doc.docstatus === 1 && doc.status === 'Rejected') {
		return 'Rejected'
	} else if (doc.docstatus === 2) {
		return 'Cancelled'
	} else if (doc.status === 'Open') {
		return 'Open'
	}
	return doc.status || 'Open'
}
</script>