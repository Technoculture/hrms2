<template>
	<ion-page>
	<BaseLayout :pageTitle="__('Leaves & Holidays')">
		<template #body>
			<div class="flex flex-col items-center mt-7 mb-7 py-4">
				<LeaveBalance />

				<div class="flex flex-col gap-7 mt-5 px-4 w-full">
					<router-link
						:to="{ name: 'LeaveApplicationFormView' }"
						v-slot="{ navigate }"
					>
						<Button
							@click="navigate"
							variant="solid"
							class="py-5 text-base w-full"
						>
							{{ __("Request a Leave") }}
						</Button>
					</router-link>
					<div>
						<div class="text-lg text-gray-800 font-bold mb-3">{{ __('Recent Leaves') }}</div>
						
						<!-- Tab Buttons -->
						<TabButtons
							:buttons="TAB_BUTTONS"
							v-model="activeTab"
							class="mb-4"
						/>

						<!-- My Leaves Tab -->
						<div v-if="activeTab === 'My Leaves'">
							<div class="flex flex-col bg-white rounded overflow-hidden" v-if="myLeaves.data?.length">
								<div
									class="flex flex-row p-3.5 items-center justify-between border-b cursor-pointer"
									v-for="leave in myLeaves.data.slice(0, 5)"
									:key="leave.name"
									@click="openRequestModal(leave)"
								>
									<LeaveRequestItem
										:doc="leave"
										:workflowStateField="leave.workflow_state_field"
										:isTeamRequest="false"
									/>
								</div>
								<router-link
									:to="{ name: 'LeaveApplicationListView', query: { tab: 'My Leaves' } }"
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
								{{ __('No recent leaves') }}
							</div>
						</div>

						<!-- Team Leaves Tab -->
						<div v-if="activeTab === 'Team Leaves'">
							<div class="flex flex-col bg-white rounded overflow-hidden" v-if="teamLeaves.data?.length">
								<div
									class="flex flex-row p-3.5 items-center justify-between border-b cursor-pointer"
									v-for="leave in teamLeaves.data.slice(0, 5)"
									:key="leave.name"
									@click="openRequestModal(leave)"
								>
									<LeaveRequestItem
										:doc="leave"
										:workflowStateField="leave.workflow_state_field"
										:isTeamRequest="true"
									/>
								</div>
								<router-link
									:to="{ name: 'LeaveApplicationListView', query: { tab: 'Team Leaves' } }"
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
								{{ __('No team leaves') }}
							</div>
						</div>
					</div>
					<Holidays />
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
		<RequestActionSheet :fields="LEAVE_FIELDS" v-model="selectedRequest" />
	</ion-modal>
</ion-page>
</template>

<script setup>
import { ref, inject } from "vue"
import { IonModal, IonPage } from "@ionic/vue"
import { Button } from "frappe-ui"

import BaseLayout from "@/components/BaseLayout.vue"
import LeaveBalance from "@/components/LeaveBalance.vue"
import LeaveRequestItem from "@/components/LeaveRequestItem.vue"
import Holidays from "@/components/Holidays.vue"
import RequestActionSheet from "@/components/RequestActionSheet.vue"
import TabButtons from "@/components/TabButtons.vue"

import { myLeaves, teamLeaves } from "@/data/leaves"
import { LEAVE_FIELDS } from "@/data/config/requestSummaryFields"

const __ = inject("$translate")

const TAB_BUTTONS = ["My Leaves", "Team Leaves"]
const activeTab = ref("My Leaves")

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
