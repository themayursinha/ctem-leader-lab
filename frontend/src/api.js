const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

async function getJson(path) {
  const staticName = path.replace('/api/', '');
  const staticUrl = `${import.meta.env.BASE_URL}api/${staticName}.json`;

  if (!API_BASE_URL) {
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
