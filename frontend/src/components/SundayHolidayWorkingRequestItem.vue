<template>
	<div class="flex flex-col gap-2 w-full">
		<div class="flex flex-row items-center justify-between">
			<div class="flex flex-col gap-1">
				<div class="text-base font-medium text-gray-900">
					{{ doc.work_date_formatted }}
				</div>
				<div class="text-sm text-gray-600" v-if="isTeamRequest">
					{{ doc.employee_name }}
				</div>
			</div>
			<div class="flex flex-col items-end gap-1">
				<FormattedField
					:fieldtype="'Select'"
					:value="doc.status"
					class="text-sm"
				/>
				<div class="text-xs text-gray-500">
					{{ doc.name }}
				</div>
			</div>
		</div>
		<div class="text-sm text-gray-700" v-if="doc.work_description">
			{{ truncateText(doc.work_description, 20) }}
		</div>
		<div class="text-sm text-red-600" v-if="doc.status === 'Rejected' && doc.rejection_reason">
			<span class="font-medium">Rejection Reason:</span> {{ doc.rejection_reason }}
		</div>
	</div>
</template>

<script setup>
import FormattedField from "@/components/FormattedField.vue"

defineProps({
	doc: {
		type: Object,
		required: true,
	},
	isTeamRequest: {
		type: Boolean,
		default: false,
	},
})

const truncateText = (text, maxLength) => {
	if (!text) return ""
	return text.length > maxLength ? text.substring(0, maxLength) + "..." : text
}
</script>