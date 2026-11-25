
<template>
  <div class="auth-container">
    <div class="auth-card">

      <div class="auth-header">
        <h1>TherapieFlow</h1>
        <p>Praxis-Dokumentation</p>
      </div>

      <h2>{{ isRegister ? 'Create an account' : 'Welcome back' }}</h2>

      <p class="subtitle">
        {{
          isRegister
            ? 'Register to access TherapieFlow.'
            : 'Please log in to continue.'
        }}
      </p>

      <form @submit.prevent="handleSubmit">

        <!-- Name: only shown during registration -->
        <div v-if="isRegister" class="form-group">
          <label for="name">Full name</label>
          <input
            id="name"
            v-model.trim="name"
            type="text"
            placeholder="Enter your full name"
            autocomplete="name"
            required
          />
        </div>

        <!-- Email -->
        <div class="form-group">
          <label for="email">Email address</label>
          <input
            id="email"
            v-model.trim="email"
            type="email"
            placeholder="Enter your email"
            autocomplete="email"
            required
          />
        </div>

        <!-- Password -->
        <div class="form-group">
          <label for="password">Password</label>
          <input
            id="password"
            v-model="password"
            type="password"
            placeholder="Enter your password"
            :autocomplete="isRegister ? 'new-password' : 'current-password'"
            required
          />
        </div>

        <!-- Error message -->
        <p v-if="errorMessage" class="error-message">
          {{ errorMessage }}
        </p>

        <!-- Success message -->
        <p v-if="successMessage" class="success-message">
          {{ successMessage }}
        </p>

        <button type="submit" :disabled="loading">
          {{
            loading
              ? 'Please wait...'
              : isRegister
                ? 'Create account'
                : 'Log in'
          }}
        </button>

      </form>

      <div class="switch-mode">
        <span>
          {{
            isRegister
              ? 'Already have an account?'
              : "Don't have an account?"
          }}
        </span>

        <button
          type="button"
          class="text-button"
          @click="switchMode"
        >
          {{ isRegister ? 'Log in' : 'Register' }}
        </button>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

// Backend address
const API_URL = 'http://127.0.0.1:8000'

// Form state
const isRegister = ref(false)
const name = ref('')
const email = ref('')
const password = ref('')

const loading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

// Send successful login information to App.vue
const emit = defineEmits(['authenticated'])

// Switch between login and registration
const switchMode = () => {
  isRegister.value = !isRegister.value

  errorMessage.value = ''
  successMessage.value = ''
  password.value = ''
}

// Handle registration and login
const handleSubmit = async () => {
  loading.value = true
  errorMessage.value = ''
  successMessage.value = ''

  const endpoint = isRegister.value
    ? '/register'
    : '/login'

  const payload = isRegister.value
    ? {
        name: name.value,
        email: email.value,
        password: password.value
      }
    : {
        email: email.value,
        password: password.value
      }

  try {
    const response = await fetch(`${API_URL}${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    })

    const data = await response.json()

    if (!response.ok) {
      throw new Error(
        data.detail || 'Something went wrong.'
      )
    }

    if (isRegister.value) {
      successMessage.value =
        'Account created successfully! You can now log in.'

      isRegister.value = false
      password.value = ''
    } else {
      // Send the token to the parent component
      emit('authenticated', data.access_token)
    }

  } catch (error) {
    errorMessage.value =
      error.message || 'Could not connect to the server.'

  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-container {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: #f3f4f6;
  padding: 20px;
}

.auth-card {
  width: 100%;
  max-width: 420px;
  background: white;
  padding: 35px;
  border-radius: 14px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08);
}

.auth-header {
  text-align: center;
  margin-bottom: 30px;
}

.auth-header h1 {
  color: #2563eb;
  font-size: 28px;
  margin-bottom: 5px;
}

.auth-header p,
.subtitle {
  color: #6b7280;
}

.auth-card h2 {
  margin-bottom: 8px;
  color: #111827;
}

.subtitle {
  margin-bottom: 25px;
}

.form-group {
  display: flex;
  flex-direction: column;
  margin-bottom: 18px;
}

.form-group label {
  margin-bottom: 7px;
  font-weight: 600;
  color: #374151;
}

.form-group input {
  padding: 12px;
  border: 1px solid #d1d5db;
  border-radius: 7px;
  font-size: 15px;
}

.form-group input:focus {
  outline: none;
  border-color: #2563eb;
}

.auth-card form > button {
  width: 100%;
  padding: 13px;
  background: #2563eb;
  color: white;
  border: none;
  border-radius: 7px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
}

.auth-card form > button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.switch-mode {
  margin-top: 22px;
  text-align: center;
  color: #6b7280;
}

.text-button {
  border: none;
  background: none;
  color: #2563eb;
  font-weight: 600;
  cursor: pointer;
  margin-left: 5px;
}

.error-message {
  color: #dc2626;
  margin-bottom: 15px;
}

.success-message {
  color: #15803d;
  margin-bottom: 15px;
}
</style>
