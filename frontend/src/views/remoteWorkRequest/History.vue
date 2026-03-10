<template>
	<ion-page>
		<ion-header class="ion-no-border">
			<div class="w-full sm:w-96">
				<div class="flex flex-col bg-white shadow-sm">
					<div class="flex items-center justify-between p-4">
						<div class="flex items-center gap-3">
							<button @click="goBack" class="p-1">
								<FeatherIcon name="chevron-left" class="h-6 w-6 text-gray-700" />
							</button>
							<h1 class="text-xl font-semibold text-gray-900">{{ __('Remote Work') }}</h1>
						</div>
						<div class="flex items-center gap-3">
							<router-link
								:to="{ name: 'RemoteWorkRequestFormView' }"
								class="bg-black text-white px-3 py-1.5 rounded-lg text-sm font-medium flex items-center gap-1"
							>
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
				<div class="flex-1 overflow-y-auto scrollbar-hide p-4 space-y-3">
					<div v-if="requests.loading" class="text-center py-8">
						<div class="text-gray-500 text-sm">{{ __('Loading...') }}</div>
					</div>

					<div v-else-if="!requests.data || requests.data.length === 0" class="text-center py-8">
						<EmptyState :message="__('You have not submitted any remote work requests')" />
					</div>

					<div v-else class="flex flex-col gap-3 mb-0 pb-0">
						<RemoteWorkRequestHistoryItem
							v-for="request in requests.data"
							:key="request.name"
							:doc="request"
							@click="viewRequest(request)"
						/>
					</div>
				</div>
			</div>
		</ion-content>
	</ion-page>
</template>

<script setup>
import { IonPage, IonHeader, IonContent } from "@ionic/vue"
import { createResource, FeatherIcon } from "frappe-ui"
import { inject } from "vue"
import { useRouter } from "vue-router"

import EmptyState from "@/components/EmptyState.vue"
import RemoteWorkRequestHistoryItem from "@/components/RemoteWorkRequestHistoryItem.vue"
import { employeeResource } from "@/data/employee"
import { transformRemoteWorkRequestData } from "@/data/remoteWorkRequest"

const __ = inject("$translate")
const router = useRouter()

const requests = createResource({
	url: "frappe.client.get_list",
	makeParams() {
		return {
			doctype: "Remote Work Request",
			fields: [
				"name",
				"employee",
				"employee_name",
				"from_date",
				"to_date",
				"status",
				"description",
				"rejection_reason",
				"linked_attendance_request",
				"creation",
				"modified",
				"docstatus",
			],
			filters: {
				employee: employeeResource.data?.name,
			},
			order_by: "creation desc",
		}
	},
	auto: true,
	transform(data) {
		return transformRemoteWorkRequestData(data)
	},
})

function goBack() {
	router.back()
}

function viewRequest(request) {
	router.push({
		name: "RemoteWorkRequestDetailView",
		params: { id: request.name },
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
