import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 120000, // 2 min — LLM calls can be slow
})

export const createCase = (data) => api.post('/cases/', data)
export const listCases = () => api.get('/cases/')
export const getCase = (id) => api.get(`/cases/${id}`)
export const getCaseTasks = (id) => api.get(`/cases/${id}/tasks`)
export const getCaseStats = (id) => api.get(`/cases/${id}/stats`)
export const getTaskDraft = (taskId) => api.get(`/tasks/${taskId}/draft`)
export const approveTask = (taskId) => api.put(`/tasks/${taskId}/approve`)
export const editDraft = (taskId, data) => api.put(`/tasks/${taskId}/edit`, data)
export const rejectTask = (taskId) => api.put(`/tasks/${taskId}/reject`)
export const completeTask = (taskId) => api.put(`/tasks/${taskId}/complete`)
export const triggerFollowup = (taskId) => api.post(`/tasks/${taskId}/followup`)

export default api
