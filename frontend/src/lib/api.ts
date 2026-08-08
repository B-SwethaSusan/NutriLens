import axios from 'axios'

export const api = axios.create({ baseURL: import.meta.env.VITE_API_URL || '/api' })
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('nutrilens_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('nutrilens_token')
    }
    return Promise.reject(error)
  },
)

export type User = { id: string; email: string; full_name?: string | null; created_at: string }
export type Document = { id: string; filename: string; source?: string | null; author?: string | null; page_count: number; chunk_count: number; file_size: number; status: string; error_message?: string | null; created_at: string; updated_at?: string | null }
export type Citation = { filename: string; page_number: number; chunk_number: number; similarity: number }
export type ChatResponse = { conversation_id: string; answer: string; citations: Citation[] }
export type Conversation = { id: string; title: string; created_at: string; updated_at?: string | null; messages: { id: string; role: string; content: string; citations?: Citation[] | null; created_at: string }[] }
export type Settings = { chunk_size: number; chunk_overlap: number; top_k: number; temperature: number; llm_model: string; embedding_model: string }

export async function authRequest(path: '/signup' | '/login', payload: object) {
  const { data } = await api.post<{ access_token: string; user: User }>(`/auth${path}`, payload)
  localStorage.setItem('nutrilens_token', data.access_token)
  return data
}
