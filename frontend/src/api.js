const BASE = import.meta.env.VITE_API_URL ?? '/api'

async function request(method, path, body) {
  const res = await fetch(BASE + path, {
    method,
    headers: body ? { 'Content-Type': 'application/json' } : {},
    body: body ? JSON.stringify(body) : undefined,
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || `HTTP ${res.status}`)
  }
  return res.json()
}

export const api = {
  health:          ()   => request('GET',  '/health'),
  runAnalysis:     ()   => request('POST', '/analysis/run'),
  getRuns:         ()   => request('GET',  '/analysis/runs'),
  getSuggestions:  (status) => request('GET', `/suggestions${status ? `?status=${status}` : ''}`),
  approveSuggestion: (id)       => request('POST', `/suggestions/${id}/approve`),
  rejectSuggestion:  (id, body) => request('POST', `/suggestions/${id}/reject`, body ?? {}),
  getConstraints:    ()         => request('GET',  '/constraints'),
  addConstraint:     (content)  => request('POST', '/constraints', { content }),
  deleteConstraint:  (id)       => request('DELETE', `/constraints/${id}`),
  updateConstraint:  (id, content) => request('PATCH', `/constraints/${id}`, { content }),
  getActionLogs:   ()   => request('GET',  '/action-logs'),
  getAds:              ()   => request('GET',  '/ads'),
  getKeywordVolume:    ()   => request('GET',  '/ads/keyword-volume'),
  getCoupangProducts:  ()   => request('GET',  '/coupang/products'),
}
