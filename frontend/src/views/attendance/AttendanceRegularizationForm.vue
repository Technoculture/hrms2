<template>
	<ion-page>
		<ion-header class="ion-no-border">
			<div class="w-full sm:w-96">
				<div class="flex flex-col bg-white shadow-sm">
					<!-- Header with back button -->
					<div class="flex items-center justify-between p-4">
						<div class="flex items-center gap-3">
							<button @click="goBack" class="p-1">
								<FeatherIcon name="chevron-left" class="h-6 w-6 text-gray-700" />
							</button>
							<h1 class="text-xl font-semibold text-gray-900">{{ __('Attendance Regularization') }}</h1>
						</div>
						<div class="flex items-center gap-3">
							<FeatherIcon name="bell" class="h-5 w-5 text-gray-500" />
							<div class="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center">
								<span class="text-sm font-medium text-gray-600">P</span>
							</div>
						</div>
					</div>
				</div>
			</div>
		</ion-header>

		<ion-content class="ion-no-padding">
			<div class="flex flex-col h-full w-screen sm:w-96 bg-gray-50">
				<div class="flex-1 overflow-y-auto scrollbar-hide p-4 space-y-6">
					
					<!-- Date Selection -->
					<div class="bg-white rounded-lg p-3 shadow-sm">
						<label class="block text-xs font-medium text-gray-700 mb-2">{{ __('Date') }}</label>
						<div class="relative">
							<input
								v-model="selectedDate"
								type="date"
								:min="minDate"
								:max="maxDate"
								@change="onDateChange"
								class="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
							/>
						</div>
						<p class="text-xs text-gray-500 mt-1">
							{{ __('Only dates from last week and current week until yesterday are allowed') }}
						</p>
					</div>

					<!-- Existing Records Display -->
					<div v-if="selectedDate" class="bg-white rounded-lg p-3 shadow-sm">
						<h3 class="text-xs font-medium text-gray-700 mb-3">{{ __('Existing Records for') }} {{ formatSelectedDate }}</h3>
						
						<div v-if="existingRecords.loading" class="text-center py-4">
							<div class="text-gray-500 text-sm">{{ __('Loading existing records...') }}</div>
						</div>
						
						<div v-else-if="!existingRecords.data || existingRecords.data.length === 0" class="text-center py-4">
							<div class="text-gray-500 text-sm">{{ __('No existing records found') }}</div>
						</div>
						
						<div v-else class="space-y-2">
							<div 
								v-for="(record, index) in existingRecords.data" 
								:key="index"
								class="flex items-center justify-between p-2 bg-gray-50 rounded-md"
							>
								<div class="flex items-center gap-2">
									<FeatherIcon 
										:name="record.log_type === 'IN' ? 'arrow-down-right' : 'arrow-up-right'" 
										:class="record.log_type === 'IN' ? 'text-green-600' : 'text-red-600'"
										class="h-4 w-4" 
									/>
									<span class="text-sm font-medium">{{ record.log_type }}</span>
								</div>
								<span class="text-sm text-gray-600">{{ formatTimeWithAMPM(record.timestamp) }}</span>
							</div>
						</div>
					</div>

					<!-- In/Out Records Form -->
					<div class="bg-white rounded-lg p-3 shadow-sm">
						<h3 class="text-xs font-medium text-gray-700 mb-3">{{ __('In/Out Records') }}</h3>
						
						<div class="space-y-4">
							<div 
								v-for="(record, index) in inOutRecords" 
								:key="index"
								class="border border-gray-200 rounded-lg p-3"
							>
								<div class="grid grid-cols-2 gap-3">
									<!-- In Time -->
									<div>
										<label class="block text-xs font-medium text-gray-600 mb-1">{{ __('In Time') }}</label>
										<input
											v-model="record.in_time"
											type="time"
											class="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
											placeholder="--:--"
										/>
									</div>
									
									<!-- Out Time -->
									<div>
										<label class="block text-xs font-medium text-gray-600 mb-1">{{ __('Out Time') }}</label>
										<input
											v-model="record.out_time"
											type="time"
											class="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
											placeholder="--:--"
										/>
									</div>
								</div>
								
								<!-- Remove Record Button -->
								<div v-if="inOutRecords.length > 1" class="flex justify-end mt-2">
									<button 
										@click="removeRecord(index)"
										class="text-red-600 text-xs font-medium hover:text-red-700"
									>
										{{ __('Remove Record') }}
									</button>
								</div>
							</div>
						</div>
						
						<p class="text-xs text-gray-500 mt-2">
							{{ __('At least one of In Time or Out Time is required for each record') }}
						</p>
						
						<!-- Add Record Button -->
						<button 
							@click="addRecord"
							class="flex items-center gap-2 text-blue-600 text-sm font-medium mt-3 hover:text-blue-700"
						>
							<FeatherIcon name="plus" class="h-4 w-4" />
							{{ __('Add Record') }}
						</button>
					</div>

					<!-- Reason -->
					<div class="bg-white rounded-lg p-3 shadow-sm">
						<label class="block text-xs font-medium text-gray-700 mb-2">{{ __('Reason') }}</label>
						<textarea
							v-model="reason"
							rows="4"
							class="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
							:placeholder="__('Please provide a reason for the attendance regularization')"
						></textarea>
					</div>

				</div>

				<!-- Submit Button -->
				<div class="p-4 bg-white border-t border-gray-200">
					<Button 
						@click="submitForm"
						:loading="submitting"
						variant="solid"
						class="w-full py-3 text-base font-medium"
					>
						{{ __('Submit') }}
					</Button>
				</div>
			</div>
		</ion-content>
	</ion-page>
</template>

<script setup>
import { ref, computed, inject, watch } from "vue"
import { IonPage, IonHeader, IonContent } from "@ionic/vue"
import { createResource, FeatherIcon, Button, toast, ErrorMessage, Badge, Dropdown, Dialog, LoadingIndicator } from "frappe-ui"

import { useRouter } from "vue-router"

const __ = inject("$translate")
const dayjs = inject("$dayjs")
const employee = inject("$employee")
const router = useRouter()

const props = defineProps({
	id: {
		type: String,
		required: false,
	},
})

// Form state
const selectedDate = ref('')
const reason = ref('')
const submitting = ref(false)
const inOutRecords = ref([
	{ in_time: '', out_time: '' }
])

// Computed values
const maxDate = computed(() => dayjs().subtract(1, 'day').format('YYYY-MM-DD')) // Yesterday
const minDate = computed(() => {
	// Calculate the start of last week (Monday of last week)
	const today = dayjs()
	const currentWeekStart = today.startOf('week').add(1, 'day') // Monday of current week
	const lastWeekStart = currentWeekStart.subtract(1, 'week') // Monday of last week
	return lastWeekStart.format('YYYY-MM-DD')
})

const formatSelectedDate = computed(() => {
	if (!selectedDate.value) return ''
	return dayjs(selectedDate.value).format('DD MMM YYYY')
})

// API resource for existing records
const existingRecords = createResource({
	url: "hrms.api.get_employee_checkin_records",
	makeParams() {
		return {
			employee: employee.data?.name,
			date: selectedDate.value,
		}
	},
})

// Watch for date changes
watch(selectedDate, (newDate) => {
	if (newDate) {
		existingRecords.reload()
	}
})

// Functions
function goBack() {
	router.back()
}

function onDateChange() {
	// Reset form when date changes
	inOutRecords.value = [{ in_time: '', out_time: '' }]
	reason.value = ''
}

function addRecord() {
	inOutRecords.value.push({ in_time: '', out_time: '' })
}

function removeRecord(index) {
	if (inOutRecords.value.length > 1) {
		inOutRecords.value.splice(index, 1)
	}
}

function formatTimeWithAMPM(timestamp) {
	if (!timestamp) return '--'
	
	// If the timestamp already contains AM/PM, return as is
	if (timestamp.includes('AM') || timestamp.includes('PM')) {
		return timestamp
	}
	
	// Parse timestamp format like "2025-07-21 10:00:19" or "2025-07-21 19:25:05"
	let timeString = timestamp
	
	// If it's a full timestamp, extract the time part
	if (timestamp.includes(' ')) {
		timeString = timestamp.split(' ')[1]
	}
	
	// Parse time string (format like "14:30:00" or "10:00:19")
	const timeParts = timeString.split(':')
	if (timeParts.length < 2) return timestamp
	
	let hours = parseInt(timeParts[0])
	const minutes = timeParts[1]
	
	// Convert to 12-hour format
	const ampm = hours >= 12 ? 'PM' : 'AM'
	hours = hours % 12
	hours = hours ? hours : 12 // 0 should be 12
	
	return `${hours}:${minutes} ${ampm}`
}

function validateForm() {
	if (!selectedDate.value) {
		throw new Error(__('Please select a date'))
	}
	
	if (!reason.value.trim()) {
		throw new Error(__('Please provide a reason'))
	}
	
	// Check if at least one record has either in_time or out_time
	const hasValidRecord = inOutRecords.value.some(record => 
		record.in_time.trim() || record.out_time.trim()
	)
	
	if (!hasValidRecord) {
		throw new Error(__('At least one In Time or Out Time is required'))
	}
	
	return true
}

async function submitForm() {
	try {
		validateForm()
		submitting.value = true
		
		// Prepare data for submission
		const formData = {
			employee: employee.data.name,
			date: selectedDate.value,
			existing_checkins: existingRecords.data || [],
			regularisation_reasonn: reason.value,
			in_out_records: inOutRecords.value.filter(record => 
				record.in_time.trim() || record.out_time.trim()
			).map(record => ({
				in_time: record.in_time || null,
				out_time: record.out_time || null
			}))
		}
		
		// Submit to API
		const submitResource = createResource({
			url: "hrms.api.attendance_regularization.submit_attendance_regularization",
			params: formData,
		})
		
		const response = await submitResource.reload()
		
		// Check if the API returned an error
		if (response.status === "error") {
			if (response.type === "validation") {
				throw new Error(response.message || __('Validation error occurred'))
			} else {
				throw new Error(response.message || __('Failed to submit request'))
			}
		}
		
		// Show success message and navigate back
		toast({
			title: __('Success'),
			text: __('Attendance regularization request raised successfully!'),
			icon: "check-circle",
			position: "bottom-center",
			iconClasses: "text-green-500",
		})
		router.back()
		
	} catch (error) {
		console.error('Form submission error:', error)
		
		// Show user-friendly error message
		let errorMessage = __('Failed to submit attendance regularization request.')
		
		if (error.message) {
			if (error.message.includes('ValidationError')) {
				errorMessage = __('Please check your input data and try again.')
			} else if (error.message.includes('PermissionError')) {
				errorMessage = __('You do not have permission to submit this request.')
			} else if (error.message.includes('DuplicateEntryError')) {
				errorMessage = __('A regularization request for this date already exists.')
			} else {
				errorMessage = error.message
			}
		}
		
		toast({
			title: __('Error'),
			text: errorMessage,
			icon: "alert-circle",
			position: "bottom-center",
			iconClasses: "text-red-500",
		})
	} finally {
		submitting.value = false
	}
}

// Initialize form if editing existing record
if (props.id) {
	// Load existing attendance request data
	// This would be implemented based on your API structure
}
</script>

<style scoped>
.scrollbar-hide {
	-ms-overflow-style: none;
	scrollbar-width: none;
}
.scrollbar-hide::-webkit-scrollbar { 
	display: none;
}
</style>