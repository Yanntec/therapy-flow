
<template>
  <div class="min-h-screen bg-slate-100">

    <!-- Header -->
    <header class="bg-white shadow-sm px-8 py-5 flex justify-between items-center">
      <div>
        <h1 class="text-2xl font-bold text-indigo-700">
          TherapyFlow Admin
        </h1>
        <p class="text-sm text-slate-500 mt-1">
          Administration and user management
        </p>
      </div>

      <button
        @click="$emit('logout')"
        class="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg"
      >
        Logout
      </button>
    </header>

    <!-- Main content -->
    <main class="max-w-7xl mx-auto p-8">

      <div class="mb-8">
        <h2 class="text-2xl font-semibold text-slate-800">
          User Management
        </h2>
        <p class="text-slate-500 mt-1">
          View all registered TherapyFlow users.
        </p>
      </div>


<!-- Dashboard Statistics -->
<div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">

  <!-- Total Users -->
  <div class="bg-white p-6 rounded-xl shadow-sm border border-slate-100">
    <p class="text-sm text-slate-500 font-medium">
      Total Users
    </p>

    <h3 class="text-3xl font-bold text-slate-800 mt-2">
      {{ totalUsers }}
    </h3>

    <p class="text-xs text-slate-400 mt-2">
      Registered accounts
    </p>
  </div>

  <!-- Active Users -->
  <div class="bg-white p-6 rounded-xl shadow-sm border border-slate-100">
    <p class="text-sm text-slate-500 font-medium">
      Active Users
    </p>

    <h3 class="text-3xl font-bold text-green-600 mt-2">
      {{ activeUsers }}
    </h3>

    <p class="text-xs text-slate-400 mt-2">
      Currently active accounts
    </p>
  </div>

  <!-- Administrators -->
  <div class="bg-white p-6 rounded-xl shadow-sm border border-slate-100">
    <p class="text-sm text-slate-500 font-medium">
      Administrators
    </p>

    <h3 class="text-3xl font-bold text-indigo-600 mt-2">
      {{ adminUsers }}
    </h3>

    <p class="text-xs text-slate-400 mt-2">
      Users with admin privileges
    </p>
  </div>

</div>

<!-- Account action feedback -->
<div
  v-if="actionMessage"
  :class="actionMessageType === 'success'
    ? 'bg-green-50 text-green-700 border-green-200'
    : 'bg-red-50 text-red-700 border-red-200'"
  class="mb-5 p-4 rounded-lg border text-sm"
>
  {{ actionMessage }}
</div>

      <!-- Users table -->
      <div class="bg-white rounded-xl shadow-sm overflow-hidden">

        <div class="px-6 py-4 border-b flex justify-between items-center">
          <h3 class="font-semibold text-slate-800">
            Registered Users
          </h3>

          <button
            @click="loadUsers"
            class="text-indigo-600 hover:text-indigo-800 text-sm font-medium"
          >
            Refresh
          </button>
        </div>

        <!-- Loading -->
        <div v-if="loading" class="p-8 text-center text-slate-500">
          Loading users...
        </div>

        <!-- Error -->
        <div v-else-if="error" class="p-8 text-center text-red-600">
          {{ error }}
        </div>

        <!-- Table -->
        <div v-else class="overflow-x-auto">
          <table class="w-full text-left">

            <thead class="bg-slate-50 text-slate-500 text-sm">
              <tr>
                <th class="px-6 py-4">ID</th>
                <th class="px-6 py-4">Name</th>
                <th class="px-6 py-4">Email</th>
                <th class="px-6 py-4">Role</th>
                <th class="px-6 py-4">Status</th>
                <th class="px-6 py-4">Action</th>
                <th class="px-6 py-4">Role Management</th>
              </tr>
            </thead>

            <tbody class="divide-y divide-slate-100">


<tr
  v-for="user in users"
  :key="user.id"
  class="hover:bg-slate-50"
>
  <!-- User ID -->
  <td class="px-6 py-4 text-slate-500">
    {{ user.id }}
  </td>

  <!-- Name -->
  <td class="px-6 py-4 font-medium text-slate-800">
    {{ user.name }}
  </td>

  <!-- Email -->
  <td class="px-6 py-4 text-slate-600">
    {{ user.email }}
  </td>

  <!-- Role -->
  <td class="px-6 py-4">
    <span
      :class="user.is_admin
        ? 'bg-indigo-100 text-indigo-700'
        : 'bg-slate-100 text-slate-700'"
      class="px-3 py-1 rounded-full text-xs font-medium"
    >
      {{ user.is_admin ? 'Administrator' : 'User' }}
    </span>
  </td>

  <!-- Status -->
  <td class="px-6 py-4">
    <span
      :class="user.is_active
        ? 'bg-green-100 text-green-700'
        : 'bg-red-100 text-red-700'"
      class="px-3 py-1 rounded-full text-xs font-medium"
    >
      {{ user.is_active ? 'Active' : 'Inactive' }}
    </span>
  </td>

  <!-- Account Action -->
  <td class="px-6 py-4">
    <button
      @click="toggleUserStatus(user)"
      :disabled="
        user.id === props.currentUserId ||
        updatingUserId === user.id
      "
      :class="user.is_active
        ? 'bg-red-100 text-red-700 hover:bg-red-200'
        : 'bg-green-100 text-green-700 hover:bg-green-200'"
      class="px-3 py-2 rounded-lg text-xs font-semibold disabled:opacity-40 disabled:cursor-not-allowed"
    >
      {{ updatingUserId === user.id
        ? 'Updating...'
        : user.is_active
          ? 'Deactivate'
          : 'Activate'
      }}
    </button>

    <p
      v-if="user.id === props.currentUserId"
      class="text-xs text-slate-400 mt-1"
    >
      Your account
    </p>
  </td>

  <!-- Role Management -->
  <td class="px-6 py-4">
    <button
      @click="toggleUserRole(user)"
      :disabled="
        (user.id === props.currentUserId && user.is_admin) ||
        updatingRoleUserId === user.id
      "
      :class="user.is_admin
        ? 'bg-orange-100 text-orange-700 hover:bg-orange-200'
        : 'bg-indigo-100 text-indigo-700 hover:bg-indigo-200'"
      class="px-3 py-2 rounded-lg text-xs font-semibold disabled:opacity-40 disabled:cursor-not-allowed"
    >
      {{ updatingRoleUserId === user.id
        ? 'Updating...'
        : user.is_admin
          ? 'Demote'
          : 'Promote'
      }}
    </button>

    <p
      v-if="user.id === props.currentUserId"
      class="text-xs text-slate-400 mt-1"
    >
      Your account
    </p>
  </td>
</tr>

              <tr v-if="users.length === 0">
                <td colspan="7" class="px-6 py-8 text-center text-slate-500">
                  No registered users found.
                </td>
              </tr>

            </tbody>
          </table>
        </div>

      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

const props = defineProps({
  accessToken: {
    type: String,
    required: true
  },
  currentUserId: {
    type: Number,
    required: true
  }
})

defineEmits(['logout'])

const users = ref([])
const loading = ref(false)
const error = ref('')

// Account management state
const updatingUserId = ref(null)
const actionMessage = ref('')
const actionMessageType = ref('success')

// Tracks which user's role is currently being updated
const updatingRoleUserId = ref(null)

// Activate or deactivate a user
const toggleUserStatus = async (user) => {

  const newStatus = !user.is_active

  const action = newStatus ? 'activate' : 'deactivate'

  const confirmed = window.confirm(
    `Are you sure you want to ${action} ${user.name}'s account?`
  )

  if (!confirmed) return

  updatingUserId.value = user.id
  actionMessage.value = ''

  try {
    const response = await fetch(
      `http://127.0.0.1:8000/admin/users/${user.id}/status`,
      {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${props.accessToken}`
        },
        body: JSON.stringify({
          is_active: newStatus
        })
      }
    )

    const data = await response.json()

    if (!response.ok) {
      throw new Error(
        data.detail || 'Could not update the account status.'
      )
    }

    // Update the user in the table
    users.value = users.value.map(existingUser =>
      existingUser.id === user.id
        ? { ...existingUser, ...data }
        : existingUser
    )

    actionMessage.value = data.message || `Account ${action}d successfully.`
    actionMessageType.value = 'success'

  } catch (err) {
    console.error('Account status update error:', err)

    actionMessage.value = err.message
    actionMessageType.value = 'error'

  } finally {
    updatingUserId.value = null
  }
}

// Promote or demote a user
const toggleUserRole = async (user) => {

  const newRole = !user.is_admin

  const action = newRole ? 'promote' : 'demote'

  const confirmed = window.confirm(
    `Are you sure you want to ${action} ${user.name} ${
      newRole ? 'to administrator' : 'to a normal user'
    }?`
  )

  if (!confirmed) return

  updatingRoleUserId.value = user.id
  actionMessage.value = ''

  try {
    const response = await fetch(
      `http://127.0.0.1:8000/admin/users/${user.id}/role`,
      {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${props.accessToken}`
        },
        body: JSON.stringify({
          is_admin: newRole
        })
      }
    )

    const data = await response.json()

    if (!response.ok) {
      throw new Error(
        data.detail || 'Could not update the user role.'
      )
    }

    // Update the user immediately in the table
    users.value = users.value.map(existingUser =>
      existingUser.id === user.id
        ? { ...existingUser, ...data }
        : existingUser
    )

    actionMessage.value =
      data.message || `User successfully ${action}d.`

    actionMessageType.value = 'success'

  } catch (err) {
    console.error('Role update error:', err)

    actionMessage.value = err.message
    actionMessageType.value = 'error'

  } finally {
    updatingRoleUserId.value = null
  }
}

// Dashboard statistics
const totalUsers = computed(() => users.value.length)

const activeUsers = computed(() =>
  users.value.filter(user => user.is_active).length
)

const adminUsers = computed(() =>
  users.value.filter(user => user.is_admin).length
)

// Load users from the backend
const loadUsers = async () => {
  loading.value = true
  error.value = ''

  try {
    const response = await fetch(
      'http://127.0.0.1:8000/admin/users',
      {
        headers: {
          Authorization: `Bearer ${props.accessToken}`
        }
      }
    )

    if (!response.ok) {
      throw new Error(`Could not load users. HTTP ${response.status}`)
    }

    const data = await response.json()

    // Support either a direct list or an object containing users
    users.value = Array.isArray(data)
      ? data
      : (data.users ?? [])

  } catch (err) {
    console.error('Error loading users:', err)
    error.value = err.message
  } finally {
    loading.value = false
  }
}

// Load users when the dashboard opens
onMounted(() => {
  loadUsers()
})
</script>
