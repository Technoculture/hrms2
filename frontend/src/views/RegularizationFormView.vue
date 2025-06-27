<template>
  <BaseLayout pageTitle="Attendance Regularization">
    <template #body>
      <div class="flex flex-col p-4 gap-5">
        <div class="w-full bg-white rounded-lg shadow p-5">
          <form @submit.prevent="submitRegularization" class="space-y-5">
            <!-- Date Selection -->
            <div class="form-group">
              <label class="block text-sm font-medium text-gray-700 mb-2">
                {{ __("Date") }}
              </label>
              <div class="relative">
                <input
                  type="date"
                  v-model="formData.date"
                  class="w-full px-3 py-2 border rounded-md pr-10"
                  :max="maxDate"
                  required
                  placeholder="dd/mm/yyyy"
                />
              </div>
              <p class="text-xs text-gray-500 mt-1">{{ __("Only dates up to today in the current month are allowed") }}</p>
            </div>

            <!-- In/Out Records -->
            <div class="form-group">
              <label class="block text-sm font-medium text-gray-700 mb-2">
                {{ __("In/Out Records") }}
              </label>
              <div class="border rounded-md p-4 bg-gray-50">
                <div v-for="(record, index) in formData.in_out_records" :key="index" class="flex gap-4 mb-4">
                  <div class="flex-1">
                    <label class="block text-sm text-gray-600 mb-1">{{ __("In Time") }}</label>
                    <div class="relative">
                      <input
                        type="time"
                        v-model="record.in_time"
                        class="w-full px-3 py-2 border rounded-md pr-10"
                        :required="!record.out_time"
                        placeholder="--:--"
                      />
                    </div>
                  </div>
                  <div class="flex-1">
                    <label class="block text-sm text-gray-600 mb-1">{{ __("Out Time") }}</label>
                    <div class="relative">
                      <input
                        type="time"
                        v-model="record.out_time"
                        class="w-full px-3 py-2 border rounded-md pr-10"
                        :required="!record.in_time"
                        placeholder="--:--"
                      />
                    </div>
                  </div>
                  <button
                    type="button"
                    @click="removeRecord(index)"
                    class="mt-6 text-red-600 hover:text-red-800"
                    v-if="formData.in_out_records.length > 1"
                  >
                    <FeatherIcon name="trash-2" class="h-5 w-5" />
                  </button>
                </div>
                <p class="text-xs text-gray-500 mb-2">{{ __("At least one of In Time or Out Time is required for each record") }}</p>
                <button
                  type="button"
                  @click="addRecord"
                  class="mt-2 flex items-center gap-1 text-blue-600 hover:text-blue-800 text-sm font-medium"
                >
                  <FeatherIcon name="plus" class="h-4 w-4" />
                  {{ __("Add Record") }}
                </button>
              </div>
            </div>

            <!-- Reason -->
            <div class="form-group">
              <label class="block text-sm font-medium text-gray-700 mb-2">
                {{ __("Reason") }}
              </label>
              <textarea
                v-model="formData.regularisation_reasonn"
                rows="4"
                class="w-full px-3 py-2 border rounded-md"
                required
              ></textarea>
            </div>

            <!-- Submit Button -->
            <div class="flex justify-end">
              <Button
                type="submit"
                :loading="isSubmitting"
                :disabled="isSubmitting"
                variant="solid"
                class="w-full md:w-auto"
              >
                {{ isSubmitting ? __("Submitting...") : __("Submit") }}
              </Button>
            </div>
          </form>
          
          <!-- Error Display -->
          <div v-if="error" class="mt-4">
            <div class="p-3 bg-red-100 text-red-700 rounded-md">
              {{ error }}
            </div>
          </div>
        </div>
      </div>
    </template>
  </BaseLayout>
</template>

<script setup>
import { ref, inject, computed } from "vue"
import { IonPage, IonContent } from "@ionic/vue"
import { useRouter } from "vue-router"
import BaseLayout from "@/components/BaseLayout.vue"
import { Button, FeatherIcon, toast } from "frappe-ui"

const router = useRouter()
const __ = inject("$translate")

const isSubmitting = ref(false)
const error = ref(null)
const formData = ref({
  date: "",
  in_out_records: [
    {
      in_time: "",
      out_time: ""
    }
  ],
  regularisation_reasonn: ""
})

// Calculate max date (today's date)
const maxDate = computed(() => {
  const today = new Date()
  return today.toISOString().split('T')[0]
})

const addRecord = () => {
  formData.value.in_out_records.push({
    in_time: "",
    out_time: ""
  })
}

const removeRecord = (index) => {
  if (formData.value.in_out_records.length > 1) {
    formData.value.in_out_records.splice(index, 1)
  }
}

const validateForm = () => {
  // Check date
  if (!formData.value.date) {
    throw new Error(__("Please select a date"))
  }
  
  // Check if date is in the future
  const selectedDate = new Date(formData.value.date)
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  
  if (selectedDate > today) {
    throw new Error(__("Future dates are not allowed"))
  }
  
  // Check if date is in current month
  const currentMonth = new Date().getMonth()
  const selectedMonth = selectedDate.getMonth()
  const currentYear = new Date().getFullYear()
  const selectedYear = selectedDate.getFullYear()
  
  if (selectedYear < currentYear || (selectedYear === currentYear && selectedMonth < currentMonth)) {
    throw new Error(__("Only dates in the current month are allowed"))
  }
  
  // Check reason
  if (!formData.value.regularisation_reasonn.trim()) {
    throw new Error(__("Please provide a reason for regularization"))
  }
  
  // Check in/out records
  for (const record of formData.value.in_out_records) {
    if (!record.in_time && !record.out_time) {
      throw new Error(__("Please provide at least In Time or Out Time for each record"))
    }
  }
  
  return true
}

const submitRegularization = async () => {
  try {
    error.value = null
    isSubmitting.value = true

    // Validate form inputs
    validateForm()

    const response = await fetch("/api/method/hrms.api.attendance_regularization.submit_attendance_regularization", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Accept": "application/json"
      },
      body: JSON.stringify({
        date: formData.value.date,
        regularisation_reasonn: formData.value.regularisation_reasonn,
        in_out_records: formData.value.in_out_records
        // Note: employee is resolved from session on the server side
      })
    })

    const contentType = response.headers.get("content-type")
    if (!response.ok || !contentType.includes("application/json")) {
      throw new Error(`Invalid server response (status: ${response.status})`)
    }

    const data = await response.json()

    if (data.message?.status === "success") {
      toast({
        title: __("Success"),
        text: __("Regularization request submitted successfully"),
        icon: "check",
        iconClasses: "text-green-500",
        position: "bottom-center"
      })
      router.push("/")
    } else {
      throw new Error(data.message?.message || __("Failed to submit request"))
    }
  } catch (err) {
    console.error("Error submitting regularization:", err)
    error.value = err.message || __("Submission failed")

    toast({
      title: __("Error"),
      text: err.message || __("Submission failed"),
      icon: "x",
      iconClasses: "text-red-500",
      position: "bottom-center"
    })
  } finally {
    isSubmitting.value = false
  }
}

</script> 