const BASE = import.meta.env.VITE_API_URL ?? '/api'
const TOKEN = import.meta.env.VITE_API_TOKEN ?? ''

async function request(method, path, body) {
  const headers = {}
  if (body) headers['Content-Type'] = 'application/json'
  if (TOKEN) headers['X-API-Token'] = TOKEN

  const res = await fetch(BASE + path, {
    method,
    headers,
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
  getFarmProfile:    ()         => request('GET',  '/farm-profile'),
  saveFarmProfile:   (content)  => request('PUT',  '/farm-profile', { content }),
  getConstraints:    ()         => request('GET',  '/constraints'),
  addConstraint:     (content)  => request('POST', '/constraints', { content }),
  deleteConstraint:  (id)       => request('DELETE', `/constraints/${id}`),
  updateConstraint:  (id, content) => request('PATCH', `/constraints/${id}`, { content }),
  getProductLabels:    ()   => request('GET',  '/product-labels'),
  setProductLabel: (id, berry_type) => request('PUT', `/product-labels/${id}`, { berry_type }),
  getActionLogs:       ()   => request('GET',  '/action-logs'),
  verifyActionLog:     (id) => request('POST', `/action-logs/${id}/verify`),
  getAds:              ()   => request('GET',  '/ads'),
  getKeywordVolume:    ()   => request('GET',  '/ads/keyword-volume'),
  getCampaigns:        ()   => request('GET',  '/campaigns'),
  getNaverProducts:    ()   => request('GET',  '/products'),
  getCoupangProducts:      ()   => request('GET', '/coupang/products'),
  getCoupangAdSummary:     ()   => request('GET', '/coupang-ads/summary'),
  uploadCoupangAdReport: (formData) => {
    const headers = TOKEN ? { 'X-API-Token': TOKEN } : {}
    return fetch(BASE + '/coupang-ads/upload', { method: 'POST', body: formData, headers })
      .then(async res => {
        if (!res.ok) {
          const err = await res.json().catch(() => ({}))
          throw new Error(err.detail || `HTTP ${res.status}`)
        }
        return res.json()
      })
  },
}
