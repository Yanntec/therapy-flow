<template>
  <div class="min-h-screen bg-slate-50 text-slate-800 flex flex-col font-sans">
    <header class="bg-indigo-600 text-white shadow-md p-4 flex justify-between items-center">
      <div>
        <h1 class="text-xl font-bold">Praxis-Dokumentation</h1>
        <p class="text-xs text-indigo-200">Digitales Session-Tracking & Berichte</p>
      </div>
      <div class="flex items-center space-x-2">
        <span class="inline-block w-3 h-3 bg-emerald-400 rounded-full animate-pulse"></span>
        <span class="text-xs font-medium">System Online (MySQL + FastAPI)</span>
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
              @click="simulateQrScan('QR-ANNA-001')" 
              class="flex-1 bg-slate-100 hover:bg-slate-200 text-slate-700 border border-slate-300 font-medium py-3 px-3 rounded-lg transition flex items-center justify-center space-x-1 active:scale-95 text-sm"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v1m6 11h2m-6 0h-2v4m0-11v3m0 0h.01M12 12h4.01M16 20h4M4 12h4m12 0h.01M5 8h2a1 1 0 001-1V5a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1zm12 0h2a1 1 0 001-1V5a1 1 0 00-1-1h-2a1 1 0 00-1 1v2a1 1 0 001 1zM5 20h2a1 1 0 001-1v-2a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1z" />
              </svg>
              <span>Scan Anna</span>
            </button>
            <button 
              @click="simulateQrScan('QR-MAX-002')" 
              class="flex-1 bg-slate-100 hover:bg-slate-200 text-slate-700 border border-slate-300 font-medium py-3 px-3 rounded-lg transition flex items-center justify-center space-x-1 active:scale-95 text-sm"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v1m6 11h2m-6 0h-2v4m0-11v3m0 0h.01M12 12h4.01M16 20h4M4 12h4m12 0h.01M5 8h2a1 1 0 001-1V5a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1zm12 0h2a1 1 0 001-1V5a1 1 0 00-1-1h-2a1 1 0 00-1 1v2a1 1 0 001 1zM5 20h2a1 1 0 001-1v-2a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1z" />
              </svg>
              <span>Scan Max</span>
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
            <p class="text-xs text-indigo-700">Geburtsdatum: {{ activePatient.geburtsdatum }} | ID: {{ activePatient.id }} | QR: {{ activePatient.qr_code }}</p>
          </div>
          <button @click="activePatient = null" class="text-sm text-red-600 hover:text-red-800 font-medium px-3 py-1 bg-white border border-red-200 rounded-md shadow-sm">
            Wechseln
          </button>
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

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

// Reaktive Variablen für Daten aus dem FastAPI-Backend
const patients = ref([])
const availableTags = ref([])
const textBausteine = ref({})

// Alles beim Start aus dem FastAPI-Backend laden
onMounted(async () => {
  try {
    // 1. Patienten laden
    const resPatients = await fetch('http://127.0.0.1:8000/patients')
    if (resPatients.ok) {
      patients.value = await resPatients.json()
    } else {
      showNotification('Fehler beim Laden der Patienten.', 'error')
    }

    // 2. Tags laden
    const resTags = await fetch('http://127.0.0.1:8000/tags')
    if (resTags.ok) {
      availableTags.value = await resTags.json()
    }

    // 3. Textbausteine laden
    const resBausteine = await fetch('http://127.0.0.1:8000/textbausteine')
    if (resBausteine.ok) {
      textBausteine.value = await resBausteine.json()
      // Ersten Baustein als Standard vorauswählen
      const firstCategory = Object.keys(textBausteine.value)[0]
      if (firstCategory && textBausteine.value[firstCategory].length > 0) {
        selectedTextBaustein.value = textBausteine.value[firstCategory][0]
      }
    }

  } catch (error) {
    console.error('Verbindungsfehler:', error)
    showNotification('Keine Verbindung zum FastAPI-Backend möglich.', 'error')
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

// Fuzzy-Search / Filter Logik für Patienten
const filteredPatients = computed(() => {
  if (!searchQuery.value) return []
  const query = searchQuery.value.toLowerCase()
  return patients.value.filter(p => 
    p.name.toLowerCase().includes(query) || 
    p.geburtsdatum.includes(query)
  )
})

// Funktionen
const selectPatient = (patient) => {
  activePatient.value = patient
  searchQuery.value = ''
  showNotification(`Patient ${patient.name} ausgewählt.`, 'success')
}

// QR-Scan-Simulation über das Backend (ideal für Präsentationen)
const simulateQrScan = async (qrCode) => {
  try {
    showNotification(`Scanne Code (${qrCode})...`, 'success')

    const response = await fetch(`http://127.0.0.1:8000/patient-by-qr/${qrCode}`)

    if (response.ok) {
      const patient = await response.json()
      activePatient.value = patient
      searchQuery.value = ''
      showNotification(`Patientkarte erkannt: ${patient.name}!`, 'success')
    } else {
      showNotification('QR-Code in der Datenbank nicht gefunden.', 'error')
    }
  } catch (error) {
    console.error('QR-Scan Fehler:', error)
    showNotification('Verbindungsfehler beim QR-Scan.', 'error')
  }
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
    const response = await fetch('http://127.0.0.1:8000/sessions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
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
    
    const response = await fetch(`http://127.0.0.1:8000/generate-doc/${activePatient.value.id}`, {
      method: 'GET'
    })

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