const API_URL = (
  import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'
).replace(/\/$/, '')

async function request(path, options = {}) {
  const response = await fetch(`${API_URL}${path}`, options)

  const contentType = response.headers.get('content-type') || ''
  const data = contentType.includes('application/json')
    ? await response.json()
    : await response.text()

  if (!response.ok) {
    const message =
      typeof data === 'object' && data?.detail
        ? data.detail
        : `Error HTTP ${response.status}`

    throw new Error(message)
  }

  return data
}

export const api = {
  health: () => request('/health'),

  getWanted: ({ limit = 100, activeOnly = true } = {}) =>
    request(`/api/wanted?limit=${limit}&active_only=${activeOnly}`),

  createWanted: (payload) =>
    request('/api/wanted', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    }),

  deactivateWanted: (id) =>
    request(`/api/wanted/${id}/deactivate`, {
      method: 'PATCH',
    }),

  getDetections: (limit = 100) =>
    request(`/api/detections?limit=${limit}`),

  getAlerts: ({ limit = 100, status = '' } = {}) => {
    const statusQuery = status ? `&status=${encodeURIComponent(status)}` : ''
    return request(`/api/alerts?limit=${limit}${statusQuery}`)
  },

  updateAlert: (id, estatus) =>
    request(`/api/alerts/${id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ estatus }),
    }),

  predictImage: (file, register = true) => {
    const body = new FormData()
    body.append('file', file)

    return request(`/api/predict/image?register=${register}`, {
      method: 'POST',
      body,
    })
  },

  predictFrame: (blob, register = true) => {
    const body = new FormData()
    body.append('file', blob, 'camera-frame.jpg')

    return request(`/api/predict/frame?register=${register}`, {
      method: 'POST',
      body,
    })
  },
}

export { API_URL }
