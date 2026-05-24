const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';
const isLiveMode = !!import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_LIVE === 'true';

const ADMIN_TOKEN_KEY = 'ctem-admin-token';

function getAdminToken() {
  return sessionStorage.getItem(ADMIN_TOKEN_KEY) || '';
}

function setAdminToken(token) {
  const clean = token.trim();
  if (clean) {
    sessionStorage.setItem(ADMIN_TOKEN_KEY, clean);
  } else {
    sessionStorage.removeItem(ADMIN_TOKEN_KEY);
  }
}

function adminHeaders() {
  const token = getAdminToken();
  return token ? { 'X-CTEM-Admin-Token': token } : {};
}

async function mutationError(response, label) {
  const text = await response.text();
  if (response.status === 401) {
    throw new Error(`${label} failed: admin token is missing or invalid.`);
  }
  throw new Error(`${label} failed (${response.status}): ${text}`);
}

function apiUrl(path) {
  return API_BASE_URL ? `${API_BASE_URL}${path}` : path;
}

async function getJson(path) {
  const staticName = path.replace('/api/', '');
  const staticUrl = `${import.meta.env.BASE_URL}api/${staticName}.json`;

  if (!isLiveMode) {
    const staticResponse = await fetch(staticUrl);
    if (!staticResponse.ok) {
      throw new Error(`Static API request failed: ${staticResponse.status} ${staticUrl}`);
    }
    return staticResponse.json();
  }

  try {
    const response = await fetch(apiUrl(path));
    if (!response.ok) {
      throw new Error(`API request failed: ${response.status} ${path}`);
    }
    return response.json();
  } catch (error) {
    const staticResponse = await fetch(staticUrl);
    if (!staticResponse.ok) {
      throw error;
    }
    return staticResponse.json();
  }
}

async function getBlob(path) {
  const response = await fetch(apiUrl(path));
  if (!response.ok) {
    throw new Error(`API request failed: ${response.status} ${path}`);
  }
  return response.blob();
}

function triggerDownload(blob, filename) {
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

async function postFile(path, file) {
  const formData = new FormData();
  formData.append('file', file);
  const response = await fetch(apiUrl(path), {
    method: 'POST',
    headers: adminHeaders(),
    body: formData,
  });
  if (!response.ok) {
    await mutationError(response, 'Import');
  }
  return response.json();
}

export const api = {
  getProgramSummary: () => getJson('/api/program-summary'),
  getMaturity: () => getJson('/api/maturity'),
  getBusinessServices: () => getJson('/api/business-services'),
  getAssets: () => getJson('/api/assets'),
  getExposures: () => getJson('/api/exposures'),
  getPrioritizedExposures: () => getJson('/api/prioritized-exposures'),
  getAttackPaths: () => getJson('/api/attack-paths'),
  getRemediationActions: () => getJson('/api/remediation-actions'),
  getWorkshopArtifacts: () => getJson('/api/workshop-artifacts'),

  isLiveMode: () => isLiveMode,
  getAdminToken,
  setAdminToken,

  async exportAssetsCsv() {
    const blob = await getBlob('/api/assets/export');
    triggerDownload(blob, 'assets.csv');
  },

  async exportExposuresCsv() {
    const blob = await getBlob('/api/exposures/export');
    triggerDownload(blob, 'exposures.csv');
  },

  async exportRemediationCsv() {
    const blob = await getBlob('/api/remediation-actions/export');
    triggerDownload(blob, 'remediation-actions.csv');
  },

  async importAssetsCsv(file) {
    return postFile('/api/assets/import', file);
  },

  async importExposuresCsv(file) {
    return postFile('/api/exposures/import', file);
  },

  async importRemediationCsv(file) {
    return postFile('/api/remediation-actions/import', file);
  },

  async resetData() {
    const response = await fetch(apiUrl('/api/reset?X-Confirm-Reset=true'), {
      method: 'POST',
      headers: adminHeaders(),
    });
    if (!response.ok) {
      await mutationError(response, 'Reset');
    }
    return response.json();
  },

  async saveSession(name) {
    const response = await fetch(apiUrl(`/api/sessions?name=${encodeURIComponent(name)}`), {
      method: 'POST',
      headers: adminHeaders(),
    });
    if (!response.ok) {
      await mutationError(response, 'Save session');
    }
    return response.json();
  },

  async listSessions() {
    const response = await fetch(apiUrl('/api/sessions'));
    if (!response.ok) {
      throw new Error(`List sessions failed: ${response.status}`);
    }
    return response.json();
  },

  async listAuditEvents(limit = 100) {
    const response = await fetch(apiUrl(`/api/audit-events?limit=${limit}`));
    if (!response.ok) {
      throw new Error(`List audit events failed: ${response.status}`);
    }
    return response.json();
  },

  async loadSession(sessionId) {
    const response = await fetch(apiUrl(`/api/sessions/${sessionId}/load`), {
      method: 'POST',
      headers: adminHeaders(),
    });
    if (!response.ok) {
      await mutationError(response, 'Load session');
    }
    return response.json();
  },

  async deleteSession(sessionId) {
    const response = await fetch(apiUrl(`/api/sessions/${sessionId}`), {
      method: 'DELETE',
      headers: adminHeaders(),
    });
    if (!response.ok) {
      await mutationError(response, 'Delete session');
    }
    return response.json();
  },

  async getExecutiveSummary(format = 'markdown') {
    const response = await fetch(apiUrl(`/api/executive-summary?format=${format}`));
    if (!response.ok) {
      throw new Error(`Executive summary failed: ${response.status}`);
    }
    if (format === 'html') {
      return response.text();
    }
    return response.blob();
  },
};
