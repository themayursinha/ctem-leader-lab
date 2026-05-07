const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

async function getJson(path) {
  const response = await fetch(`${API_BASE_URL}${path}`);
  if (!response.ok) {
    throw new Error(`API request failed: ${response.status} ${path}`);
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
};
