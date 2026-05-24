const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;
const isLiveMode = !!API_BASE_URL;

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
    const response = await fetch(`${API_BASE_URL}${path}`);
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
  const response = await fetch(`${API_BASE_URL}${path}`);
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
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: 'POST',
    body: formData,
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(`Import failed (${response.status}): ${text}`);
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
    const response = await fetch(`${API_BASE_URL}/api/reset?X-Confirm-Reset=true`, {
      method: 'POST',
    });
    if (!response.ok) {
      const text = await response.text();
      throw new Error(`Reset failed (${response.status}): ${text}`);
    }
    return response.json();
  },
};
