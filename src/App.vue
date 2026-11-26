<template>
<!-- Login screen -->
<LoginForm
  v-if="!isAuthenticated"
  @authenticated="handleAuthenticated"
/>

<!-- Admin dashboard -->
<AdminDashboard
  v-else-if="currentUser?.is_admin"
  :access-token="accessToken"
  :current-user-id="currentUser.id"
  @logout="logout"
/>

<!-- Normal patient dashboard -->
<div v-else class="min-h-screen bg-slate-50 text-slate-800 flex flex-col font-sans">
  <header class="bg-indigo-600 text-white shadow-md p-4 flex justify-between items-center">
      <div>
        <h1 class="text-xl font-bold">Praxis-Dokumentation</h1>
        <p class="text-xs text-indigo-200">Digitales Session-Tracking & Berichte</p>
      </div>
  <div class="flex items-center space-x-3">
    <span class="text-xs font-medium">
    System Online (FastAPI)
    </span>

  <button
    @click="logout"
    class="bg-white text-indigo-700 px-3 py-2 rounded-lg text-sm font-semibold hover:bg-indigo-50">
    Logout
  </button>
</div>
    </header>

    <main class="flex-1 max-w-4xl w-full mx-auto p-4 md:p-6 space-y-6">

      <!-- 1. Patienten-Erkennung -->
      <section class="bg-white rounded-xl shadow-sm border border-slate-200 p-5">
        <h2 class="text-lg font-semibold text-slate-700 mb-3 flex items-center">
          <span class="bg-indigo-100 text-indigo-700 w-7 h-7 rounded-full inline-flex items-center justify-center text-sm mr-2">1</span>
          Patienten-Erkennung
        </h2>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-slate-600 mb-1">Suche (Name / Geburtsdatum)</label>
            <input 
              type="text" 
              v-model="searchQuery" 
              placeholder="z.B. Anna Schmidt oder 14.05..." 
              class="w-full px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none text-base"
            />
          </div>

          
      <div class="flex items-end space-x-2">
        <button
        @click="showPatientForm = !showPatientForm"
        class="flex-1 bg-emerald-600 hover:bg-emerald-700 text-white font-medium py-3 px-3 rounded-lg transition text-sm"
        >
        + Neuer Patient
        </button>

        <button
        @click="openScanModal"
        class="flex-1 bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-3 px-3 rounded-lg transition flex items-center justify-center space-x-2 active:scale-95 text-sm"
        >
        <span>QR-Code scannen</span>
        </button>
      </div>

        </div>


<!-- New patient registration form -->
<div
  v-if="showPatientForm"
  class="mt-4 p-4 bg-emerald-50 border border-emerald-200 rounded-lg space-y-3"
>
  <h3 class="font-semibold text-emerald-800">
    Neuen Patienten registrieren
  </h3>

  <div>
    <label class="block text-sm font-medium text-slate-600 mb-1">
      Name
    </label>
    <input
      v-model="newPatient.name"
      type="text"
      placeholder="Vor- und Nachname"
      class="w-full px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:outline-none"
    />
  </div>

  <div>
    <label class="block text-sm font-medium text-slate-600 mb-1">
      Geburtsdatum
    </label>
    <input
      v-model="newPatient.geburtsdatum"
      type="text"
      placeholder="TT.MM.JJJJ"
      class="w-full px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:outline-none"
    />
  </div>

  <div class="flex gap-2">
    <button
      @click="registerPatient"
      :disabled="isRegistering"
      class="flex-1 bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 text-white font-semibold py-3 rounded-lg"
    >
      {{ isRegistering ? 'Speichern...' : 'Patient speichern' }}
    </button>

    <button
      @click="showPatientForm = false"
      class="px-4 py-3 bg-white border border-slate-300 rounded-lg"
    >
      Abbrechen
    </button>
  </div>
</div>

        <div v-if="filteredPatients.length > 0 && !activePatient" class="mt-3 border border-slate-200 rounded-lg divide-y divide-slate-100 bg-slate-50">
          <div 
            v-for="patient in filteredPatients" 
            :key="patient.id"
            @click="selectPatient(patient)"
            class="p-3 hover:bg-indigo-50 cursor-pointer flex justify-between items-center transition"
          >
            <div>
              <p class="font-semibold text-slate-800">{{ patient.name }}</p>
              <p class="text-xs text-slate-500">Geb.: {{ patient.geburtsdatum }}</p>
            </div>
            <span class="text-xs bg-indigo-100 text-indigo-700 px-2.5 py-1 rounded-md font-medium">Auswählen</span>
          </div>
        </div>

        <div v-if="activePatient" class="mt-4 p-4 bg-indigo-50 border border-indigo-200 rounded-lg flex justify-between items-center">
          <div>
            <span class="text-xs font-bold uppercase tracking-wider text-indigo-600">Aktiver Patient</span>
            <p class="text-lg font-bold text-indigo-900">{{ activePatient.name }}</p>
            <p class="text-xs text-indigo-700">Geburtsdatum: {{ activePatient.geburtsdatum }} | ID: {{ activePatient.id }}</p>
          </div>
          <div class="flex items-center space-x-2">
            <button @click="openQrModal" class="text-sm text-indigo-700 hover:text-indigo-900 font-medium px-3 py-1 bg-white border border-indigo-200 rounded-md shadow-sm">
              QR-Code
            </button>
            <button @click="activePatient = null" class="text-sm text-red-600 hover:text-red-800 font-medium px-3 py-1 bg-white border border-red-200 rounded-md shadow-sm">
              Wechseln
            </button>
          </div>
        </div>
      </section>

      <!-- 2. Therapie-Sitzung erfassen -->
      <section v-if="activePatient" class="bg-white rounded-xl shadow-sm border border-slate-200 p-5 space-y-4 transition-all">
        <h2 class="text-lg font-semibold text-slate-700 flex items-center">
          <span class="bg-indigo-100 text-indigo-700 w-7 h-7 rounded-full inline-flex items-center justify-center text-sm mr-2">2</span>
          Therapie-Sitzung erfassen (Schnell-Modus)
        </h2>

        <div>
          <label class="block text-sm font-medium text-slate-600 mb-2">Tags / Verlaufsschwerpunkte wählen:</label>
          <div class="flex flex-wrap gap-2">
            <button 
              v-for="tag in availableTags" 
              :key="tag"
              @click="toggleTag(tag)"
              :class="[
                'px-4 py-2.5 rounded-xl text-sm font-medium transition active:scale-95 border',
                selectedTags.includes(tag) 
                  ? 'bg-indigo-600 text-white border-indigo-600 shadow-sm' 
                  : 'bg-slate-100 text-slate-700 border-slate-200 hover:bg-slate-200'
              ]"
            >
              {{ tag }}
            </button>
          </div>
        </div>

        <div>
          <label class="block text-sm font-medium text-slate-600 mb-2">Strukturierte Notizen / Textbaustein:</label>
          <select v-model="selectedTextBaustein" class="w-full px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none mb-3 bg-white text-base">
            <template v-for="(category, catName) in textBausteine" :key="catName">
              <optgroup :label="catName">
                <option v-for="baustein in category" :value="baustein" :key="baustein">{{ baustein }}</option>
              </optgroup>
            </template>
          </select>
          
          <textarea 
            v-model="customNotes" 
            rows="3" 
            placeholder="Ergänzende Notizen zur Sitzung (optional)..." 
            class="w-full px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none text-base"
          ></textarea>
        </div>

        <button 
          @click="saveSession" 
          class="w-full bg-emerald-600 hover:bg-emerald-700 text-white font-bold py-3.5 px-4 rounded-xl shadow-md transition active:scale-95 flex items-center justify-center space-x-2 text-base"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
          </svg>
          <span>Sitzung speichern</span>
        </button>
      </section>

      <!-- 3. Bericht / Dokument generieren -->
      <section v-if="activePatient" class="bg-white rounded-xl shadow-sm border border-slate-200 p-5 space-y-4">
        <h2 class="text-lg font-semibold text-slate-700 flex items-center">
          <span class="bg-indigo-100 text-indigo-700 w-7 h-7 rounded-full inline-flex items-center justify-center text-sm mr-2">3</span>
          Bericht / Dokument generieren (.docx)
        </h2>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-slate-600 mb-1">Gewünschte Vorlage</label>
            <select v-model="selectedTemplate" class="w-full px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none bg-white text-base">
              <option v-for="tmpl in templates" :value="tmpl.id" :key="tmpl.id">{{ tmpl.name }}</option>
            </select>
          </div>

          <div class="flex items-end">
            <button 
              @click="generateDocument" 
              class="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-3 px-4 rounded-lg shadow transition active:scale-95 flex items-center justify-center space-x-2"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <span>Dokument erstellen (.docx)</span>
            </button>
          </div>
        </div>
      </section>

      <!-- Benachrichtigungen -->
      <div v-if="notification" :class="['p-4 rounded-xl text-white font-medium shadow-lg flex items-center justify-between', notification.type === 'success' ? 'bg-emerald-600' : 'bg-amber-600']">
        <span>{{ notification.message }}</span>
        <button @click="notification = null" class="text-white font-bold px-2">&times;</button>
      </div>

    </main>

    <!-- Erfolgs-Pop-up (Modal) -->
    <div v-if="showSuccessModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-2xl p-6 max-w-sm w-full shadow-2xl border border-slate-100 text-center space-y-4">
        <div class="w-14 h-14 bg-emerald-100 text-emerald-600 rounded-full flex items-center justify-center mx-auto text-3xl font-bold shadow-inner">
          ✓
        </div>
        <h3 class="text-xl font-bold text-slate-800">Erfolgreich gespeichert!</h3>
        <p class="text-sm text-slate-600">Die Sitzung und alle Notizen wurden sicher in der Datenbank hinterlegt.</p>
        <button
          @click="showSuccessModal = false"
          class="w-full bg-emerald-600 hover:bg-emerald-700 text-white font-semibold py-3 rounded-xl shadow transition active:scale-95"
        >
          Super, weiter arbeiten
        </button>
      </div>
    </div>

    <!-- QR-Code Modal: Anzeigen, Drucken, Herunterladen -->
    <div v-if="showQrModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4 print:hidden">
      <div class="bg-white rounded-2xl p-6 max-w-sm w-full shadow-2xl border border-slate-100 text-center space-y-4">
        <h3 class="text-xl font-bold text-slate-800">QR-Code – {{ activePatient?.name }}</h3>
        <p class="text-xs text-slate-500">Dieser Code identifiziert ausschließlich diesen Patienten. Bei Verlust eines Ausdrucks bitte neu generieren.</p>

        <div class="flex justify-center">
          <img v-if="qrImageUrl" :src="qrImageUrl" alt="QR-Code" class="w-56 h-56 border border-slate-200 rounded-lg p-2" />
        </div>

        <div class="grid grid-cols-2 gap-2">
          <button @click="printQrCode" class="bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-2.5 rounded-lg shadow transition active:scale-95 text-sm">
            Drucken
          </button>
          <button @click="downloadQrCode" class="bg-slate-100 hover:bg-slate-200 text-slate-700 border border-slate-300 font-medium py-2.5 rounded-lg transition active:scale-95 text-sm">
            Als PNG speichern
          </button>
        </div>
        <button @click="regenerateQrCode" class="w-full text-sm text-amber-700 hover:text-amber-900 font-medium py-2 rounded-lg border border-amber-200 bg-amber-50 hover:bg-amber-100 transition active:scale-95">
          Neuen Code generieren (alter Ausdruck wird ungültig)
        </button>
        <button @click="showQrModal = false" class="w-full text-slate-500 hover:text-slate-700 font-medium py-2 text-sm">
          Schließen
        </button>
      </div>
    </div>

    <!-- Druckbereich: nur beim Drucken sichtbar -->
    <div v-if="activePatient" id="qr-print-area" class="hidden">
      <h2>{{ activePatient.name }}</h2>
      <p>Geburtsdatum: {{ activePatient.geburtsdatum }}</p>
      <img v-if="qrImageUrl" :src="qrImageUrl" alt="QR-Code" />
    </div>

    <!-- Scan Modal: Kamerazugriff zum Einscannen eines Patienten-QR-Codes -->
    <div v-if="showScanModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-2xl p-6 max-w-md w-full shadow-2xl border border-slate-100 text-center space-y-4">
        <h3 class="text-xl font-bold text-slate-800">QR-Code scannen</h3>
        <p class="text-xs text-slate-500">Patientenkarte vor die Kamera halten.</p>
        <div id="qr-scanner-region" class="rounded-lg overflow-hidden"></div>
        <button @click="closeScanModal" class="w-full bg-slate-100 hover:bg-slate-200 text-slate-700 border border-slate-300 font-medium py-2.5 rounded-lg transition active:scale-95 text-sm">
          Abbrechen
        </button>
      </div>
    </div>

  </div>
</template>

<script setup>
import API_URL from './api'
import LoginForm from './components/LoginForm.vue'
import { ref, computed, onMounted, nextTick } from 'vue'
import { Html5QrcodeScanner } from 'html5-qrcode'
import AdminDashboard from './components/AdminDashboard.vue'

// Authentication state
const accessToken = ref(localStorage.getItem('access_token'))

const currentUser = ref(null)
const isAuthenticated = computed(() => {
  return Boolean(accessToken.value)
})

// Store the token after successful login
const handleAuthenticated = async (token) => {
  accessToken.value = token
  localStorage.setItem('access_token', token)

  await loadCurrentUser()
}

// Remove the token when logging out
const logout = () => {
  if (qrScanner) {
    qrScanner.clear().catch(() => {})
    qrScanner = null
  }

  localStorage.removeItem('access_token')
  accessToken.value = null
  currentUser.value = null

  activePatient.value = null
  showQrModal.value = false
  showScanModal.value = false
  showSuccessModal.value = false
}

// Add the JWT token to API requests
const authHeaders = (headers = {}) => ({
  ...headers,
  Authorization: `Bearer ${accessToken.value}`
})

// Get the currently logged-in user's profile
const loadCurrentUser = async () => {
  try {
    const response = await fetch(
      `${API_URL}/me`,
      {
        headers: authHeaders()
      }
    )

    if (!response.ok) {
      throw new Error('Session expired or authentication failed.')
    }

    currentUser.value = await response.json()

    // Only normal users need the patient dashboard data
    if (!currentUser.value.is_admin) {
      await loadDashboardData()
    }

  } catch (error) {
    console.error('Authentication error:', error)

    logout()

    alert('Your session has expired. Please log in again.')
  }
}

// Reaktive Variablen für Daten aus dem FastAPI-Backend
const patients = ref([])
const availableTags = ref([])
const textBausteine = ref({})

// Load dashboard data after authentication
const loadDashboardData = async () => {
  try {
    // 1. Load patients
    const resPatients = await fetch(
      `${API_URL}/patients`,
      {
        headers: authHeaders()
      }
    )

    if (resPatients.ok) {
      patients.value = await resPatients.json()
    } else {
      showNotification('Fehler beim Laden der Patienten.', 'error')
    }

    // 2. Load tags
    const resTags = await fetch(
      `${API_URL}/tags`,
      {
        headers: authHeaders()
      }
    )

    if (resTags.ok) {
      availableTags.value = await resTags.json()
    }

    // 3. Load text blocks
    const resBausteine = await fetch(
      `${API_URL}/textbausteine`,
      {
        headers: authHeaders()
      }
    )

    if (resBausteine.ok) {
      textBausteine.value = await resBausteine.json()

      const firstCategory = Object.keys(textBausteine.value)[0]

      if (
        firstCategory &&
        textBausteine.value[firstCategory].length > 0
      ) {
        selectedTextBaustein.value =
          textBausteine.value[firstCategory][0]
      }
    }

  } catch (error) {
    console.error('Verbindungsfehler:', error)

    showNotification(
      'Keine Verbindung zum FastAPI-Backend möglich.',
      'error'
    )
  }
}

// Only load dashboard data if already logged in
onMounted(() => {
  if (isAuthenticated.value) {
    loadCurrentUser()
  }
})

// Nur noch den Standard Verlaufsbericht anbieten
const templates = ref([
  { id: 1, name: 'Standard Verlaufsbericht.docx' }
])

// State Management
const searchQuery = ref('')
const activePatient = ref(null)
const selectedTags = ref([])
const selectedTextBaustein = ref('')
const customNotes = ref('')
const selectedTemplate = ref(1)
const notification = ref(null)
const showSuccessModal = ref(false)
const showQrModal = ref(false)
const showScanModal = ref(false)
const qrImgCacheBuster = ref(0)
let qrScanner = null

// New patient registration
const showPatientForm = ref(false)
const isRegistering = ref(false)

const newPatient = ref({
  name: '',
  geburtsdatum: ''
})
// Fuzzy-Search / Filter Logik für Patienten
const filteredPatients = computed(() => {
  if (!searchQuery.value) return []
  const query = searchQuery.value.toLowerCase()
  return patients.value.filter(p => 
    p.name.toLowerCase().includes(query) || 
    p.geburtsdatum.includes(query)
  )
})

// QR-Code-Bild-URL für den aktiven Patienten (Cache-Buster nach Neu-Generierung)
const qrImageUrl = ref('')

const loadQrImage = async () => {
  if (!activePatient.value) {
    qrImageUrl.value = ''
    return
  }

  try {
    const response = await fetch(
      `${API_URL}/patients/${activePatient.value.id}/qr-image?v=${qrImgCacheBuster.value}`,
      {
        headers: authHeaders()
      }
    )

    if (!response.ok) {
      throw new Error('Could not load QR image.')
    }

    const imageBlob = await response.blob()
    const newImageUrl = URL.createObjectURL(imageBlob)

    if (qrImageUrl.value.startsWith('blob:')) {
      URL.revokeObjectURL(qrImageUrl.value)
    }

    qrImageUrl.value = newImageUrl

  } catch (error) {
    console.error('QR image loading error:', error)
    qrImageUrl.value = ''
  }
}


// Register a new patient
const registerPatient = async () => {
  if (!newPatient.value.name.trim() || !newPatient.value.geburtsdatum.trim()) {
    showNotification('Bitte Name und Geburtsdatum eingeben.', 'error')
    return
  }

  isRegistering.value = true

  try {
    const response = await fetch(`${API_URL}/patients`, {
      method: 'POST',
      headers: authHeaders({
        'Content-Type': 'application/json'
      }),
      body: JSON.stringify({
        name: newPatient.value.name.trim(),
        geburtsdatum: newPatient.value.geburtsdatum.trim()
      })
    })

    if (!response.ok) {
      throw new Error('Patient konnte nicht gespeichert werden.')
    }

    const createdPatient = await response.json()

    // Add the new patient to the existing list
    patients.value.push(createdPatient)

    // Reset the form
    newPatient.value = {
      name: '',
      geburtsdatum: ''
    }

    showPatientForm.value = false

    showNotification(
      `Patient ${createdPatient.name} erfolgreich registriert!`,
      'success'
    )

  } catch (error) {
    console.error('Patient registration error:', error)
    showNotification('Fehler bei der Patientenregistrierung.', 'error')
  } finally {
    isRegistering.value = false
  }
}

// Funktionen
const selectPatient = (patient) => {
  activePatient.value = patient
  searchQuery.value = ''
  loadQrImage()
  showNotification(`Patient ${patient.name} ausgewählt.`, 'success')
}

// Patient anhand eines gescannten/eingegebenen QR-Codes laden
const handleQrScan = async (qrCode) => {
  try {
const response = await fetch(
  `${API_URL}/patient-by-qr/${qrCode}`,
  {
    headers: authHeaders()
  }
)

    if (response.ok) {
      const patient = await response.json()
      activePatient.value = patient
      searchQuery.value = ''
      activePatient.value = patient
      searchQuery.value = ''
      loadQrImage()
      showNotification(`Patientkarte erkannt: ${patient.name}!`, 'success')
    } else {
      showNotification('QR-Code in der Datenbank nicht gefunden.', 'error')
    }
  } catch (error) {
    console.error('QR-Scan Fehler:', error)
    showNotification('Verbindungsfehler beim QR-Scan.', 'error')
  }
}

// --- QR-Code Anzeige / Drucken / Download ---

const openQrModal = () => {
  showQrModal.value = true
}

const printQrCode = () => {
  window.print()
}

const downloadQrCode = async () => {
  if (!activePatient.value) return
  try {

const response = await fetch(qrImageUrl.value, {
  headers: authHeaders()
})

    if (!response.ok) throw new Error('QR-Bild konnte nicht geladen werden.')
    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `QR-Code_${activePatient.value.name.replace(' ', '_')}.png`
    document.body.appendChild(a)
    a.click()
    a.remove()
    window.URL.revokeObjectURL(url)
  } catch (error) {
    console.error('QR-Download-Fehler:', error)
    showNotification('QR-Code konnte nicht heruntergeladen werden.', 'error')
  }
}

const regenerateQrCode = async () => {
  if (!activePatient.value) return
  const confirmed = window.confirm(
    'Wirklich einen neuen QR-Code generieren? Bereits ausgedruckte Codes für diesen Patienten funktionieren danach nicht mehr.'
  )
  if (!confirmed) return

  try {
    const response = await fetch(`${API_URL}/patients/${activePatient.value.id}/regenerate-qr`, {
      method: 'POST',
      headers: authHeaders()
    })
    if (response.ok) {
      const updated = await response.json()
      activePatient.value = updated
      qrImgCacheBuster.value++
      showNotification('Neuer QR-Code wurde generiert.', 'success')
    } else {
      showNotification('QR-Code konnte nicht neu generiert werden.', 'error')
    }
  } catch (error) {
    console.error('QR-Regenerierungs-Fehler:', error)
    showNotification('Verbindungsfehler bei der QR-Code-Neugenerierung.', 'error')
  }
}

// --- QR-Code per Kamera scannen ---

const openScanModal = () => {
  showScanModal.value = true
  nextTick(() => {
    qrScanner = new Html5QrcodeScanner(
      'qr-scanner-region',
      { fps: 10, qrbox: { width: 250, height: 250 } },
      /* verbose= */ false
    )
    qrScanner.render(
      (decodedText) => {
        closeScanModal()
        handleQrScan(decodedText)
      },
      () => {
        // Kein Code im aktuellen Kamerabild erkannt - kein Fehler, wird laufend erneut versucht
      }
    )
  })
}

const closeScanModal = () => {
  if (qrScanner) {
    qrScanner.clear().catch(() => {})
    qrScanner = null
  }
  showScanModal.value = false
}

const toggleTag = (tag) => {
  if (selectedTags.value.includes(tag)) {
    selectedTags.value = selectedTags.value.filter(t => t !== tag)
  } else {
    selectedTags.value.push(tag)
  }
}

// Sitzung an FastAPI-Backend senden und in MySQL speichern
const saveSession = async () => {
  if (!activePatient.value) return
  
  const kombinierterFreitext = `[Baustein: ${selectedTextBaustein.value}]\n${customNotes.value}`

  const payload = {
    patient_id: activePatient.value.id,
    therapeut_id: "Nicole",
    tags: selectedTags.value,
    freitext: kombinierterFreitext,
    textbaustein_id: null
  }

  try {
    const response = await fetch(`${API_URL}/sessions`, {
      method: 'POST',
headers: authHeaders({
  'Content-Type': 'application/json'
}),
      body: JSON.stringify(payload)
    })

    if (response.ok) {
      showSuccessModal.value = true
      selectedTags.value = []
      customNotes.value = ''
    } else {
      showNotification('Fehler beim Speichern der Sitzung.', 'error')
    }
  } catch (error) {
    console.error('Netzwerkfehler:', error)
    showNotification('Verbindungsfehler beim Speichern.', 'error')
  }
}

// Dokument für den aktiven Patienten vom Backend generieren lassen
const generateDocument = async () => {
  if (!activePatient.value) {
    showNotification('Bitte zuerst einen Patienten auswählen.', 'error')
    return
  }

  try {
    showNotification('Generiere Verlaufsbericht für ' + activePatient.value.name + '...', 'success')
    
const response = await fetch(
  `${API_URL}/generate-doc/${activePatient.value.id}`,
  {
    method: 'GET',
    headers: authHeaders()
  }
)
    if (response.ok) {
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `Verlaufsbericht_${activePatient.value.name.replace(' ', '_')}.docx`
      document.body.appendChild(a)
      a.click()
      a.remove()
      
      showNotification('Bericht erfolgreich heruntergeladen!', 'success')
    } else {
      showNotification('Fehler beim Generieren des Dokuments im Backend.', 'error')
    }
  } catch (error) {
    console.error('Download-Fehler:', error)
    showNotification('Verbindungsfehler beim Dokumenten-Download.', 'error')
  }
}

const showNotification = (message, type = 'success') => {
  notification.value = { message, type }
  setTimeout(() => {
    notification.value = null
  }, 4000)
}
</script>

<style>
/* Beim Drucken (z.B. für den QR-Code) nur den Druckbereich zeigen */
@media print {
  body * {
    visibility: hidden;
  }
  #qr-print-area,
  #qr-print-area * {
    visibility: visible;
  }
  #qr-print-area {
    display: block !important;
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    text-align: center;
  }
  #qr-print-area img {
    width: 240px;
    height: 240px;
    margin: 1rem auto;
  }
}
</style>