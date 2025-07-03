<template>
  <ion-page>
    <ion-header>
      <ion-toolbar>
        <ion-title>Attendance Regularization</ion-title>
      </ion-toolbar>
    </ion-header>

    <ion-content class="ion-padding">
      <form @submit.prevent="submitRequest">
        <ion-item>
          <ion-label>Date</ion-label>
          <ion-datetime
            v-model="form.date"
            presentation="date"
            :max="today"
          />
        </ion-item>

        <ion-item>
          <ion-label>Reason</ion-label>
          <ion-input v-model="form.reason" />
        </ion-item>

        <div v-for="(entry, index) in form.in_out_records" :key="index">
          <ion-item>
            <ion-label>In Time</ion-label>
            <ion-datetime
              v-model="entry.in_time"
              presentation="time"
            />
          </ion-item>
          <ion-item>
            <ion-label>Out Time</ion-label>
            <ion-datetime
              v-model="entry.out_time"
              presentation="time"
            />
          </ion-item>
          <ion-button color="danger" fill="clear" @click="removeEntry(index)">Remove</ion-button>
        </div>

        <ion-button expand="block" @click="addEntry">+ Add Entry</ion-button>
        <ion-button expand="block" type="submit" :disabled="loading">
          {{ loading ? 'Submitting...' : 'Submit Request' }}
        </ion-button>
      </form>
    </ion-content>
  </ion-page>
</template>

<script setup>
import { ref } from 'vue'
import {
  IonPage, IonHeader, IonToolbar, IonTitle,
  IonContent, IonItem, IonLabel, IonDatetime,
  IonInput, IonButton, toastController
} from '@ionic/vue'
import axios from 'axios'

const today = new Date().toISOString().split('T')[0]

const form = ref({
  date: '',
  reason: '',
  employee: '', // Will fetch this below
  company: '',
  in_out_records: [
    { in_time: '', out_time: '' }
  ]
})

const loading = ref(false)

const addEntry = () => {
  form.value.in_out_records.push({ in_time: '', out_time: '' })
}

const removeEntry = (index) => {
  form.value.in_out_records.splice(index, 1)
}

// Fetch current user’s employee and company
const fetchMeta = async () => {
  const { data } = await axios.get('/api/method/frappe.auth.get_logged_user')
  const user = data.message
  const res = await axios.get('/api/resource/Employee?filters=[["user_id","=","' + user + '"]]')
  const emp = res.data.data[0]
  form.value.employee = emp.name
  form.value.company = emp.company
}

fetchMeta()

const submitRequest = async () => {
  loading.value = true
  try {
    const response = await axios.post('/api/method/tcr_erp.api.create_regularization_request', form.value)
    const msg = await toastController.create({
      message: response.data.message || 'Request submitted!',
      duration: 2000,
      color: response.data.status === 'success' ? 'success' : 'danger'
    })
    msg.present()
    if (response.data.status === 'success') {
      // Optional: redirect back to dashboard
    }
  } catch (err) {
    const msg = await toastController.create({
      message: err.response?.data?.message || 'Failed to submit request.',
      duration: 2000,
      color: 'danger'
    })
    msg.present()
  }
  loading.value = false
}
</script>
