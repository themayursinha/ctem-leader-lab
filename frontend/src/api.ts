import type {
  AuthResponse,
  ProgramSummary,
  MaturityDomain,
  BusinessService,
  Asset,
  Exposure,
  PrioritizedExposure,
  AttackPath,
  RemediationAction,
  WorkshopArtifacts,
  ImportResult,
} from './types/api'

import { useAuthStore } from './store'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL as string | undefined
const isLiveMode = !!import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_LIVE === 'true'

const ADMIN_TOKEN_KEY = 'ctem-admin-token'

function getAdminToken(): string {
  return sessionStorage.getItem(ADMIN_TOKEN_KEY) || ''
}

function setAdminToken(token: string): void {
  const clean = token.trim()
  if (clean) {
    sessionStorage.setItem(ADMIN_TOKEN_KEY, clean)
  } else {
    sessionStorage.removeItem(ADMIN_TOKEN_KEY)
  }
}

function adminHeaders(): Record<string, string> {
  const token = getAdminToken()
  return token ? { 'X-CTEM-Admin-Token': token } : {}
}

function authHeaders(): Record<string, string> {
  const token = useAuthStore.getState().token
  return token ? { Authorization: `Bearer ${token}` } : {}
}

async function mutationError(response: Response, label: string): Promise<never> {
  const text = await response.text()
  if (response.status === 401) {
    throw new Error(`${label} failed: admin token is missing or invalid.`)
  }
  throw new Error(`${label} failed (${response.status}): ${text}`)
}

function apiUrl(path: string): string {
  return API_BASE_URL ? `${API_BASE_URL}${path}` : path
}

async function getJson<T>(path: string): Promise<T> {
  const staticName = path.replace('/api/', '')
  const staticUrl = `${import.meta.env.BASE_URL}api/${staticName}.json`

  if (!isLiveMode) {
    const staticResponse = await fetch(staticUrl)
    if (!staticResponse.ok) {
      throw new Error(`Static API request failed: ${staticResponse.status} ${staticUrl}`)
    }
    return staticResponse.json()
  }

  try {
    const headers: Record<string, string> = { ...authHeaders() }
    const response = await fetch(apiUrl(path), { headers })
    if (!response.ok) {
      throw new Error(`API request failed: ${response.status} ${path}`)
    }
    return response.json()
  } catch (error) {
    const staticResponse = await fetch(staticUrl)
    if (!staticResponse.ok) {
      throw error
    }
    return staticResponse.json()
  }
}

async function getBlob(path: string): Promise<Blob> {
  const response = await fetch(apiUrl(path))
  if (!response.ok) {
    throw new Error(`API request failed: ${response.status} ${path}`)
  }
  return response.blob()
}

function triggerDownload(blob: Blob, filename: string): void {
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

async function postFile(path: string, file: File): Promise<ImportResult> {
  const formData = new FormData()
  formData.append('file', file)
  const response = await fetch(apiUrl(path), {
    method: 'POST',
    headers: adminHeaders(),
    body: formData,
  })
  if (!response.ok) {
    await mutationError(response, 'Import')
  }
  return response.json()
}

export const api = {
  getProgramSummary: () => getJson<ProgramSummary>('/api/program-summary'),
  getMaturity: () => getJson<MaturityDomain[]>('/api/maturity'),
  getBusinessServices: () => getJson<BusinessService[]>('/api/business-services'),
  getAssets: () => getJson<Asset[]>('/api/assets'),
  getExposures: () => getJson<Exposure[]>('/api/exposures'),
  getPrioritizedExposures: () => getJson<PrioritizedExposure[]>('/api/prioritized-exposures'),
  getAttackPaths: () => getJson<AttackPath[]>('/api/attack-paths'),
  getRemediationActions: () => getJson<RemediationAction[]>('/api/remediation-actions'),
  getWorkshopArtifacts: () => getJson<WorkshopArtifacts>('/api/workshop-artifacts'),

  isLiveMode: () => isLiveMode,
  getAdminToken,
  setAdminToken,

  async exportAssetsCsv() {
    const blob = await getBlob('/api/assets/export')
    triggerDownload(blob, 'assets.csv')
  },

  async exportExposuresCsv() {
    const blob = await getBlob('/api/exposures/export')
    triggerDownload(blob, 'exposures.csv')
  },

  async exportRemediationCsv() {
    const blob = await getBlob('/api/remediation-actions/export')
    triggerDownload(blob, 'remediation-actions.csv')
  },

  async importAssetsCsv(file: File) {
    return postFile('/api/assets/import', file)
  },

  async importExposuresCsv(file: File) {
    return postFile('/api/exposures/import', file)
  },

  async importRemediationCsv(file: File) {
    return postFile('/api/remediation-actions/import', file)
  },

  async resetData() {
    const response = await fetch(apiUrl('/api/reset?X-Confirm-Reset=true'), {
      method: 'POST',
      headers: adminHeaders(),
    })
    if (!response.ok) {
      await mutationError(response, 'Reset')
    }
    return response.json()
  },

  async saveSession(name: string) {
    const response = await fetch(apiUrl(`/api/sessions?name=${encodeURIComponent(name)}`), {
      method: 'POST',
      headers: adminHeaders(),
    })
    if (!response.ok) {
      await mutationError(response, 'Save session')
    }
    return response.json()
  },

  async listSessions() {
    const response = await fetch(apiUrl('/api/sessions'))
    if (!response.ok) {
      throw new Error(`List sessions failed: ${response.status}`)
    }
    return response.json()
  },

  async listAuditEvents(limit = 100) {
    const response = await fetch(apiUrl(`/api/audit-events?limit=${limit}`))
    if (!response.ok) {
      throw new Error(`List audit events failed: ${response.status}`)
    }
    return response.json()
  },

  async loadSession(sessionId: string) {
    const response = await fetch(apiUrl(`/api/sessions/${sessionId}/load`), {
      method: 'POST',
      headers: adminHeaders(),
    })
    if (!response.ok) {
      await mutationError(response, 'Load session')
    }
    return response.json()
  },

  async deleteSession(sessionId: string) {
    const response = await fetch(apiUrl(`/api/sessions/${sessionId}`), {
      method: 'DELETE',
      headers: adminHeaders(),
    })
    if (!response.ok) {
      await mutationError(response, 'Delete session')
    }
    return response.json()
  },

  async getExecutiveSummary(format: string = 'markdown') {
    const response = await fetch(apiUrl(`/api/executive-summary?format=${format}`))
    if (!response.ok) {
      throw new Error(`Executive summary failed: ${response.status}`)
    }
    if (format === 'html') {
      return response.text()
    }
    return response.blob()
  },

  // Auth endpoints
  async register(email: string, password: string, name: string, organizationName?: string) {
    const response = await fetch(apiUrl('/api/auth/register'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password, name, organization_name: organizationName }),
    })
    if (!response.ok) {
      const text = await response.text()
      throw new Error(`Registration failed (${response.status}): ${text}`)
    }
    return response.json() as Promise<AuthResponse>
  },

  async login(email: string, password: string) {
    const response = await fetch(apiUrl('/api/auth/login'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    })
    if (!response.ok) {
      throw new Error(`Login failed: ${response.status}`)
    }
    return response.json() as Promise<AuthResponse>
  },

  async getMe(token: string) {
    const response = await fetch(apiUrl('/api/auth/me'), {
      headers: { Authorization: `Bearer ${token}` },
    })
    if (!response.ok) {
      throw new Error(`Get user failed: ${response.status}`)
    }
    return response.json()
  },
}
