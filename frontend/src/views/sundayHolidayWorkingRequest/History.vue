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
							<h1 class="text-xl font-semibold text-gray-900">{{ __('Sunday/Holiday Working') }}</h1>
						</div>
						<div class="flex items-center gap-3">
							<router-link :to="{ name: 'SundayHolidayWorkingRequestFormView' }" class="bg-black text-white px-3 py-1.5 rounded-lg text-sm font-medium flex items-center gap-1">
								<FeatherIcon name="plus" class="h-4 w-4" />
								{{ __('New') }}
							</router-link>
						</div>
					</div>
				</div>
			</div>
		</ion-header>

		<ion-content class="ion-no-padding">
			<div class="flex flex-col h-full w-screen sm:w-96 bg-gray-50">
				
				<!-- Tab Buttons -->
				<div class="bg-white p-4">
					<div class="flex bg-gray-100 rounded-lg p-1">
						<button 
							@click="activeTab = 'my'"
							:class="[
								'flex-1 py-2 px-4 text-sm font-medium rounded-md transition-colors',
								activeTab === 'my' 
									? 'bg-white text-gray-900 shadow-sm' 
									: 'text-gray-500 hover:text-gray-700'
							]"
						>
							{{ __('My Requests') }}
						</button>
						<button 
							@click="activeTab = 'team'"
							:class="[
								'flex-1 py-2 px-4 text-sm font-medium rounded-md transition-colors',
								activeTab === 'team' 
									? 'bg-white text-gray-900 shadow-sm' 
									: 'text-gray-500 hover:text-gray-700'
							]"
						>
							{{ __('Team Requests') }}
						</button>
					</div>
				</div>

				<!-- Content -->
				<div class="flex-1 overflow-y-auto scrollbar-hide">
					
					<!-- My Requests Tab -->
					<div v-if="activeTab === 'my'" class="p-4 space-y-3">
						<div v-if="myRequests.loading" class="text-center py-8">
							<div class="text-gray-500 text-sm">{{ __('Loading...') }}</div>
						</div>
						
						<div v-else-if="!myRequests.data || myRequests.data.length === 0" class="text-center py-8">
							<EmptyState 
								message="You have not submitted any Sunday/Holiday working requests"
							/>
						</div>
						
						<div v-else class="flex flex-col gap-3 mb-0 pb-0">
							<SundayHolidayWorkingRequestHistoryItem 
								v-for="request in myRequests.data" 
								:key="request.name"
								:doc="request"
								@click="viewRequest(request)"
							/>
						</div>
					</div>

					<!-- Team Requests Tab -->
					<div v-if="activeTab === 'team'" class="p-4 space-y-3">
						<div v-if="teamRequests.loading" class="text-center py-8">
							<div class="text-gray-500 text-sm">{{ __('Loading...') }}</div>
						</div>
						
						<div v-else-if="!teamRequests.data || teamRequests.data.length === 0" class="text-center py-8">
							<EmptyState 
								message="No Sunday/Holiday working requests from your team"
							/>
						</div>
						
						<div v-else class="flex flex-col gap-3 mb-0 pb-0">
							<SundayHolidayWorkingRequestHistoryItem 
								v-for="request in teamRequests.data" 
								:key="request.name"
								:doc="request"
								:showEmployee="true"
								@click="viewRequest(request)"
							/>
						</div>
					</div>

				</div>
			</div>
		</ion-content>
	</ion-page>
</template>

<script setup>
import { ref, inject, watch } from "vue"
import { IonPage, IonHeader, IonContent } from "@ionic/vue"
import { createResource, FeatherIcon } from "frappe-ui"
import { useRouter } from "vue-router"

import SundayHolidayWorkingRequestHistoryItem from "@/components/SundayHolidayWorkingRequestHistoryItem.vue"
import EmptyState from "@/components/EmptyState.vue"

const __ = inject("$translate")
const employee = inject("$employee")
const router = useRouter()

// Active tab state
const activeTab = ref('my')

// API resources
const myRequests = createResource({
	url: "frappe.client.get_list",
	makeParams() {
		return {
			doctype: "Sunday Holiday Working Request",
			fields: [
				"name",
				"employee",
				"employee_name",
				"work_date",
				"status",
				"work_description",
				"rejection_reason",
				"creation",
				"modified",
				"docstatus"
			],
			filters: {
				employee: employee.data?.name
			},
			order_by: "creation desc",
		}
	},
	auto: true,
})

const teamRequests = createResource({
	url: "frappe.client.get_list",
	makeParams() {
		return {
			doctype: "Sunday Holiday Working Request",
			fields: [
				"name",
				"employee",
				"employee_name",
				"work_date",
				"status",
				"work_description",
				"rejection_reason",
				"creation",
				"modified",
				"docstatus"
			],
			filters: {
				employee: ["!=", employee.data?.name]				
			},
			order_by: "creation desc",
		}
	},
})

// Watch for tab changes to load team requests when needed
watch(activeTab, (newTab) => {
	if (newTab === 'team' && !teamRequests.data) {
		teamRequests.reload()
	}
})

// Functions
function goBack() {
	router.back()
}

function viewRequest(request) {
	router.push({
		name: 'SundayHolidayWorkingRequestDetailView',
		params: { id: request.name }
	})
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