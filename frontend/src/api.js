const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

async function request(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    throw new Error(body.detail || `요청 실패 (${res.status})`)
  }
  return res.json()
}

export function fetchRobloxGames() {
  return request('/api/games/roblox')
}

export function fetchMinecraftMods() {
  return request('/api/games/minecraft')
}

export function submitRobloxSurvey(payload) {
  return request('/api/survey/roblox', { method: 'POST', body: JSON.stringify(payload) })
}

export function submitMinecraftSurvey(payload) {
  return request('/api/survey/minecraft', { method: 'POST', body: JSON.stringify(payload) })
}

export function sendChatMessage(message, msApiKey = null) {
  const key = msApiKey || localStorage.getItem('ms_api_key') || ''
  return request('/api/chat', {
    method: 'POST',
    body: JSON.stringify({ message, ms_api_key: key }),
  })
}

export async function resetChat() {
  try {
    return await request('/api/chat/reset', { method: 'POST' })
  } catch (error) {
    if (!/요청 실패 \(405\)/.test(error.message)) throw error
    return request('/api/chat/reset', { method: 'GET' })
  }
}
