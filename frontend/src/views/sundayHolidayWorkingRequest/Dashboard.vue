<template>
	<ion-page>
		<BaseLayout :pageTitle="__('Sunday/Holiday Working')">
			<template #body>
				<div class="flex flex-col items-center mt-7 mb-7 py-4">
					<div class="flex flex-col gap-7 mt-5 px-4 w-full">
						<router-link
							:to="{ name: 'SundayHolidayWorkingRequestFormView' }"
							v-slot="{ navigate }"
						>
							<Button
								@click="navigate"
								variant="solid"
								class="py-5 text-base w-full"
							>
								{{ __("Request Sunday/Holiday Working") }}
							</Button>
						</router-link>
						
						<div>
							<div class="text-lg text-gray-800 font-bold mb-3">
								{{ __('Recent Requests') }}
							</div>
							
							<!-- Tab Buttons -->
							<TabButtons
								:buttons="TAB_BUTTONS"
								v-model="activeTab"
								class="mb-4"
							/>

							<!-- My Requests Tab -->
							<div v-if="activeTab === 'My Requests'">
								<div class="flex flex-col bg-white rounded overflow-hidden" v-if="myRequests.data?.length">
									<div
										class="flex flex-row p-3.5 items-center justify-between border-b cursor-pointer"
										v-for="request in myRequests.data.slice(0, 5)"
										:key="request.name"
										@click="openRequestModal(request)"
									>
										<SundayHolidayWorkingRequestItem
											:doc="request"
											:isTeamRequest="false"
										/>
									</div>
									<router-link
										:to="{ name: 'SundayHolidayWorkingRequestHistoryView' }"
										v-slot="{ navigate }"
									>
										<Button
											variant="ghost"
											@click="navigate"
											class="w-full !text-gray-600 py-6 text-sm border-none bg-white hover:bg-white"
										>
											{{ __("View All") }}
										</Button>
									</router-link>
								</div>
								<div v-else class="bg-white rounded p-8 text-center text-gray-500">
									{{ __('No recent requests') }}
								</div>
							</div>

							<!-- Team Requests Tab -->
							<div v-if="activeTab === 'Team Requests'">
								<div class="flex flex-col bg-white rounded overflow-hidden" v-if="teamRequests.data?.length">
									<div
										class="flex flex-row p-3.5 items-center justify-between border-b cursor-pointer"
										v-for="request in teamRequests.data.slice(0, 5)"
										:key="request.name"
										@click="openRequestModal(request)"
									>
										<SundayHolidayWorkingRequestItem
											:doc="request"
											:isTeamRequest="true"
										/>
									</div>
									<router-link
										:to="{ name: 'SundayHolidayWorkingRequestHistoryView' }"
										v-slot="{ navigate }"
									>
										<Button
											variant="ghost"
											@click="navigate"
											class="w-full !text-gray-600 py-6 text-sm border-none bg-white hover:bg-white"
										>
											{{ __("View All") }}
										</Button>
									</router-link>
								</div>
								<div v-else class="bg-white rounded p-8 text-center text-gray-500">
									{{ __('No team requests') }}
								</div>
							</div>
						</div>
					</div>
				</div>
			</template>
		</BaseLayout>

		<ion-modal
			ref="modal"
			:is-open="isRequestModalOpen"
			@didDismiss="closeRequestModal"
			:initial-breakpoint="1"
			:breakpoints="[0, 1]"
		>
			<RequestActionSheet :fields="SUNDAY_HOLIDAY_WORKING_REQUEST_FIELDS" v-model="selectedRequest" />
		</ion-modal>
	</ion-page>
</template>

<script setup>
import { ref, inject } from "vue"
import { IonModal, IonPage } from "@ionic/vue"
import { Button } from "frappe-ui"

import BaseLayout from "@/components/BaseLayout.vue"
import SundayHolidayWorkingRequestItem from "@/components/SundayHolidayWorkingRequestItem.vue"
import RequestActionSheet from "@/components/RequestActionSheet.vue"
import TabButtons from "@/components/TabButtons.vue"

import { mySundayHolidayWorkingRequests, teamSundayHolidayWorkingRequests } from "@/data/sundayHolidayWorkingRequest"
import { SUNDAY_HOLIDAY_WORKING_REQUEST_FIELDS } from "@/data/config/requestSummaryFields"

const __ = inject("$translate")

const TAB_BUTTONS = ["My Requests", "Team Requests"]
const activeTab = ref("My Requests")

const myRequests = mySundayHolidayWorkingRequests
const teamRequests = teamSundayHolidayWorkingRequests

const isRequestModalOpen = ref(false)
const selectedRequest = ref(null)

const openRequestModal = async (request) => {
	selectedRequest.value = request
	isRequestModalOpen.value = true
}

const closeRequestModal = async () => {
	isRequestModalOpen.value = false
	selectedRequest.value = null
}
</script>