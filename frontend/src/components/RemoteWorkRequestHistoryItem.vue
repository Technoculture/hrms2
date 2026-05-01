<template>
	<div class="bg-white rounded-lg border border-gray-200 p-4 cursor-pointer hover:bg-gray-50 transition-colors">
		<div class="flex items-center justify-between">
			<div class="flex items-center gap-3 flex-1">
				<div class="flex-shrink-0">
					<FeatherIcon name="monitor" class="h-5 w-5 text-gray-400" />
				</div>

				<div class="flex-1 min-w-0">
					<div class="flex items-center gap-2 mb-1">
						<span class="text-xs text-gray-900">
							{{ props.doc.employee_name || props.doc.employee }}
							{{ props.doc.employee ? "(" + props.doc.employee + ")" : "" }}
						</span>
					</div>
					<p class="text-xs text-gray-500">
						{{ props.doc.request_dates || formatRequestDates(props.doc) }} • {{ formatRelativeTime(props.doc.creation) }}
					</p>
					<p class="text-xs text-gray-600 mt-1 truncate" v-if="props.doc.description">
						{{ truncateText(props.doc.description, 28) }}
					</p>
				</div>
			</div>

			<div class="flex items-center gap-2 flex-shrink-0">
				<div class="px-2 py-1 rounded-full text-xs font-medium" :class="getStatusClass(props.doc.status)">
					{{ getStatusText(props.doc.status) }}
				</div>
				<FeatherIcon name="chevron-right" class="h-4 w-4 text-gray-400" />
			</div>
		</div>

		<div class="text-xs text-red-600 mt-2" v-if="props.doc.status === 'Rejected' && props.doc.rejection_reason">
			<span class="font-medium">{{ __("Rejection Reason:") }}</span> {{ props.doc.rejection_reason }}
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
})

function formatRequestDates(doc) {
	if (!doc.from_date && !doc.to_date) return ""
	if (doc.from_date === doc.to_date) {
		return dayjs(doc.from_date).format("D MMM YYYY")
	}

	return `${dayjs(doc.from_date).format("D MMM YYYY")} - ${dayjs(doc.to_date).format("D MMM YYYY")}`
}

function formatRelativeTime(datetime) {
	const now = dayjs()
	const target = dayjs(datetime)
	const diffDays = now.startOf("day").diff(target.startOf("day"), "day")

	if (diffDays === 0) return __("Today")
	if (diffDays === 1) return __("Yesterday")
	if (diffDays < 7) return `${diffDays}${__("d")}`

	return target.format("D MMM")
}

function getStatusClass(status) {
	switch (status) {
		case "Approved":
			return "bg-green-100 text-green-700"
		case "Rejected":
			return "bg-red-100 text-red-700"
		case "Cancelled":
			return "bg-gray-100 text-gray-700"
		default:
			return "bg-orange-100 text-orange-700"
	}
}

function getStatusText(status) {
	switch (status) {
		case "Approved":
			return __("Approved")
		case "Rejected":
			return __("Rejected")
		case "Cancelled":
			return __("Cancelled")
		case "Open":
			return __("Pending")
		default:
			return __(status || "Pending")
	}
}

function truncateText(text, maxLength) {
	if (!text) return ""
	return text.length > maxLength ? text.substring(0, maxLength) + "..." : text
}
</script>
