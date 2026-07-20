import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 120000, // 2 min — LLM calls can be slow
})

// Attach Bearer token if available
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export const login = (data) => api.post('/auth/login', data)
export const register = (data) => api.post('/auth/register', data)
export const getMe = () => api.get('/auth/me')

export const createCase = (data) => api.post('/cases/', data)
export const listCases = () => api.get('/cases/')
export const getCase = (id) => api.get(`/cases/${id}`)
export const deleteCase = (id) => api.delete(`/cases/${id}`)
export const getCaseTasks = (id) => api.get(`/cases/${id}/tasks`)
export const getCaseStats = (id) => api.get(`/cases/${id}/stats`)
export const getTaskDraft = (taskId) => api.get(`/tasks/${taskId}/draft`)
export const approveTask = (taskId) => api.put(`/tasks/${taskId}/approve`)
export const sendGmailTask = (taskId, recipientEmail) => api.post(`/tasks/${taskId}/send-gmail?recipient_email=${encodeURIComponent(recipientEmail)}`)
export const syncInbox = (caseId) => api.post(`/cases/${caseId}/sync-inbox`)
export const editDraft = (taskId, data) => api.put(`/tasks/${taskId}/edit`, data)
export const rejectTask = (taskId) => api.put(`/tasks/${taskId}/reject`)
export const completeTask = (taskId) => api.put(`/tasks/${taskId}/complete`)
export const triggerFollowup = (taskId) => api.post(`/tasks/${taskId}/followup`)

// File upload (multipart form data)
export const uploadFile = (file) => {
  const formData = new FormData()
  formData.append('file', file)
  return api.post('/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

export default api
