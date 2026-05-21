/**
 * Backend Bridge - Vue ES Module version
 * Provides HTTP call() and SSE sseChat() to the Python backend.
 *
 * Origin auto-detection:
 * - Vite dev (localhost:5173): same-origin, Vite proxy forwards /api → :8000
 * - Tauri (tauri.localhost): direct → http://localhost:8000
 * - Production build served by FastAPI: same-origin
 */

class BackendBridge {
  constructor() {
    const origin = window.location.origin
    this.apiBase =
      origin && origin !== 'null' && !origin.includes('tauri.localhost')
        ? ''  // same-origin (Vite proxy or FastAPI static)
        : 'http://localhost:8000'
  }

  async call(method, params = {}) {
    try {
      const response = await fetch(`${this.apiBase}/api/${method}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(params),
      })
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`)
      }
      return await response.json()
    } catch (error) {
      console.error(`[BackendBridge] call ${method} failed:`, error)
      return { success: false, error: error.message }
    }
  }

  async sseChat(params = {}) {
    const response = await fetch(`${this.apiBase}/ai_chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params),
    })
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`)
    }
    return response
  }

  async checkHealth() {
    try {
      const response = await fetch(`${this.apiBase}/health`)
      return response.ok
    } catch {
      return false
    }
  }
}

const backendBridge = new BackendBridge()
export default backendBridge
export { BackendBridge }
