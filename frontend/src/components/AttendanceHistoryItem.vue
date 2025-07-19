<template>
	<div class="bg-white rounded-lg border border-gray-200 p-3 mb-2">
		<!-- Date and Status Header -->
		<div class="flex justify-between items-start mb-2">
			<div>
				<h3 class="text-base font-medium text-gray-900">{{ formatDate(props.doc.date) }}</h3>
				<p v-if="props.doc.shift_name" class="text-xs text-gray-600 mt-0.5">
					{{ props.doc.shift_name }} ({{ props.doc.shift_start_time }} - {{ props.doc.shift_end_time }})
				</p>
			</div>
			<div v-if="getStatusInfo(props.doc).label" class="px-2 py-0.5 rounded-full text-[10px] font-medium" :class="getStatusInfo(props.doc).class">
				{{ getStatusInfo(props.doc).label }}
			</div>
		</div>

		<!-- Week Off, Holiday, or Leave -->
		<div v-if="['Week Off', 'Holiday', 'Leave'].includes(props.doc.status)" class="text-center py-3">
			<div class="px-3 py-1 rounded-full text-[10px] font-medium" :class="getStatusBadgeClass(props.doc.status)">
				{{ getStatusBadgeText(props.doc.status) }}
			</div>
		</div>

		<!-- No Time Entries -->
		<div v-else-if="props.doc.status === 'Absent' && !props.doc.clock_in_time" class="text-center py-3">
			<div class="text-red-600 text-xs font-medium">{{ __('No Time Entries Logged') }}</div>
		</div>

		<!-- Clock In/Out Details -->
		<div v-else-if="props.doc.clock_in_time || props.doc.clock_out_time" class="space-y-2">
			<!-- Clock In/Out Times -->
			<div class="flex justify-between items-center">
				<div class="flex-1">
					<p class="text-xs text-gray-500">{{ __('Check In') }}</p>
					<div class="flex flex-col">
						<p class="text-sm font-medium" :class="props.doc.late_entry ? 'text-red-600' : 'text-gray-900'">
							{{ props.doc.clock_in_time || '--' }}
						</p>
						<p v-if="props.doc.swipe_missing_in" class="text-[10px] text-red-600 font-medium">
							{{ __('SWIPE(S) MISSING') }}
						</p>
					</div>
				</div>
				<div class="flex-1 text-right">
					<p class="text-xs text-gray-500">{{ __('Check Out') }}</p>
					<div class="flex flex-col items-end">
						<p class="text-sm font-medium" :class="getMissingOutClass(props.doc)">
							{{ getMissingOutText(props.doc) }}
						</p>
						<p v-if="props.doc.swipe_missing_out" class="text-[10px] text-red-600 font-medium">
							{{ __('SWIPE(S) MISSING') }}
						</p>
					</div>
				</div>
			</div>

			<!-- Penalties -->
			<div v-if="props.doc.penalties && props.doc.penalties.length > 0" class="bg-red-50 border border-red-200 rounded-md p-2">
				<p class="text-red-700 text-xs font-medium">
					{{ props.doc.penalties.length }} {{ props.doc.penalties.length === 1 ? __('Penalty has been recorded') : __('Penalties have been recorded') }}
				</p>
			</div>

			<!-- Attendance Adjustment -->
			<div v-if="props.doc.attendance_adjustment_pending" class="bg-orange-50 border border-orange-200 rounded-md p-2">
				<p class="text-orange-700 text-xs font-medium">{{ __('Attendance Adjustment Pending approval') }}</p>
			</div>

			<!-- Working Hours -->
			<div class="flex justify-between items-center pt-2 border-t border-gray-100">
				<div>
					<p class="text-xs text-gray-500">{{ __('Effective hours') }}</p>
					<p class="text-xs font-medium text-gray-700">{{ props.doc.effective_hours || '--' }}</p>
				</div>
				<div class="text-right">
					<p class="text-xs text-gray-500">{{ __('Gross hours') }}</p>
					<p class="text-xs font-medium text-gray-700">{{ props.doc.gross_hours || '--' }}</p>
				</div>
			</div>

			<!-- Expand Button -->
			<div v-if="props.doc.time_logs && props.doc.time_logs.length > 0" class="flex justify-center pt-2">
				<button 
					@click="toggleExpand"
					class="flex items-center gap-1 text-xs text-gray-500 hover:text-gray-700"
				>
					<FeatherIcon 
						:name="isExpanded ? 'chevron-up' : 'chevron-down'" 
						class="h-3 w-3" 
					/>
					{{ isExpanded ? __('Hide Details') : __('Show Details') }}
				</button>
			</div>

			<!-- Expanded Time Logs -->
			<div v-if="isExpanded && props.doc.time_logs" class="mt-3 bg-gray-50 rounded-md p-3">
				<h4 class="text-xs font-medium text-gray-700 mb-2 uppercase">{{ __('TIME LOGS') }}</h4>
				<div class="space-y-1">
					<div v-for="(log, index) in props.doc.time_logs" :key="index" class="flex items-center gap-2">
						<FeatherIcon 
							:name="log.log_type === 'IN' ? 'arrow-down-right' : 'arrow-up-right'" 
							:class="log.log_type === 'IN' ? 'text-green-600' : 'text-red-600'"
							class="h-3 w-3" 
						/>
						<span class="text-xs text-gray-700">
							{{ log.time }}
							<span v-if="log.missing" class="text-red-600 ml-1">{{ __('missing') }}</span>
						</span>
					</div>
				</div>
			</div>
		</div>
	</div>
</template>

<script setup>
import { inject, ref } from "vue"
import { FeatherIcon } from "frappe-ui"

const __ = inject("$translate")
const dayjs = inject("$dayjs")

const props = defineProps({
	doc: {
		type: Object,
		required: true,
	},
})

const emit = defineEmits(['expand'])

const isExpanded = ref(false)

function formatDate(date) {
	const today = dayjs()
	const targetDate = dayjs(date)
	
	if (targetDate.isSame(today, 'day')) {
		return `${targetDate.format('ddd, D')} (Today)`
	}
	
	return targetDate.format('ddd, D')
}

function getStatusInfo(doc) {
	if (doc.late_entry && doc.early_exit) {
		return { label: __('LATE & EARLY EXIT'), class: 'bg-red-100 text-red-700' }
	} else if (doc.late_entry) {
		const lateMinutes = doc.late_minutes || 0
		const hours = Math.floor(lateMinutes / 60)
		const minutes = lateMinutes % 60
		let timeStr = ''
		if (hours > 0) timeStr += `${hours}:${minutes.toString().padStart(2, '0')}`
		else timeStr = `0:${minutes.toString().padStart(2, '0')}`
		return { label: `${timeStr} ${__('LATE')}`, class: 'bg-orange-100 text-orange-700' }
	} else if (doc.early_exit) {
		return { label: __('EARLY EXIT'), class: 'bg-orange-100 text-orange-700' }
	} else if (doc.status === 'Present' && doc.clock_in_time && doc.clock_out_time) {
		return { label: __('ON TIME'), class: 'bg-green-100 text-green-700' }
	}
	
	return { label: '', class: '' }
}

function getStatusBadgeClass(status) {
	switch (status) {
		case 'Week Off':
			return 'bg-purple-100 text-purple-700'
		case 'Holiday':
			return 'bg-blue-100 text-blue-700'
		case 'Leave':
			return 'bg-green-100 text-green-700'
		default:
			return 'bg-gray-100 text-gray-700'
	}
}

function getStatusBadgeText(status) {
	switch (status) {
		case 'Week Off':
			return __('WEEK OFF')
		case 'Holiday':
			return __('HOLIDAY')
		case 'Leave':
			return __('LEAVE')
		default:
			return status.toUpperCase()
	}
}

function getMissingOutClass(doc) {
	if (!doc.clock_out_time || doc.clock_out_missing) {
		return 'text-red-600'
	}
	return doc.early_exit ? 'text-red-600' : 'text-gray-900'
}

function getMissingOutText(doc) {
	if (!doc.clock_out_time || doc.clock_out_missing) {
		return __('MISSING')
	}
	return doc.clock_out_time || '--'
}

function toggleExpand() {
	if (!isExpanded.value) {
		// Emit event to parent to collapse other cards
		emit('expand', props.doc.date)
	}
	isExpanded.value = !isExpanded.value
}

// Expose method to parent for collapsing
defineExpose({
	collapse: () => {
		isExpanded.value = false
	}
})
</script>