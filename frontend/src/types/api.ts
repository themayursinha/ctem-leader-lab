export interface BusinessService {
  id: string;
  name: string;
  description: string;
  executive_owner: string;
  business_owner: string;
  criticality: 'Low' | 'Medium' | 'High' | 'Critical';
  risk_appetite: string;
  customer_impact: string;
  revenue_dependency: string;
  crown_jewel_asset_ids: string[];
  in_scope: boolean;
  scope_reason: string;
}

export interface Asset {
  id: string;
  name: string;
  type: string;
  service_id: string;
  owner: string;
  environment: string;
  criticality: 'Low' | 'Medium' | 'High' | 'Critical';
  crown_jewel: boolean;
  internet_exposed: boolean;
  reachable_from_internet: 'Direct' | 'Indirect' | 'Isolated';
  tags: string[];
}

export interface Exposure {
  id: string;
  title: string;
  description: string;
  exposure_type: 'CVE' | 'Cloud' | 'Identity' | 'Secret' | 'SaaS' | 'Control Gap';
  asset_id: string;
  severity: 'Low' | 'Medium' | 'High' | 'Critical';
  cvss: number | null;
  epss_probability: number;
  kev_signal: boolean;
  ransomware_observed: boolean;
  identity_risk: number;
  control_gap: number;
  attack_path_proximity: 'Crown Jewel' | 'Same Service' | 'Adjacent' | 'None';
  remediation_effort: 'Low' | 'Medium' | 'High';
  evidence_confidence: 'Low' | 'Medium' | 'High';
  evidence: string;
  suggested_action: string;
  source: string | null;
  source_reference: string | null;
  first_seen: string | null;
  last_seen: string | null;
  validated_at: string | null;
  evidence_owner: string | null;
  evidence_expires_at: string | null;
}

export interface ScoreDriver {
  name: string;
  value: number;
  explanation: string;
}

export type Decision = 'Track' | 'Monitor' | 'Attend' | 'Act';

export interface PrioritizedExposure {
  exposure_id: string;
  asset_id: string;
  service_id: string;
  title: string;
  description: string;
  exposure_type: string;
  severity: string;
  decision: Decision;
  ctem_score: number;
  rationale: string;
  why_it_matters: string;
  next_action: string;
  score_drivers: ScoreDriver[];
  validation_evidence: string;
  owner: string;
  sla: string;
  source: string | null;
  validated_at: string | null;
}

export interface AttackPathStep {
  order: number;
  title: string;
  asset_id: string;
  technique: string;
  validation: string;
  control_gap: string;
}

export interface AttackPath {
  id: string;
  name: string;
  objective: string;
  business_service_id: string;
  exposure_ids: string[];
  status: 'Validated' | 'Plausible' | 'Blocked';
  evidence_confidence: 'Low' | 'Medium' | 'High';
  blast_radius: string;
  safe_validation_method: string;
  steps: AttackPathStep[];
}

export interface RemediationAction {
  id: string;
  exposure_id: string;
  title: string;
  owner: string;
  team: string;
  status: 'To Do' | 'In Progress' | 'Done' | 'Accepted Risk';
  priority: Decision;
  sla: string;
  due_in_days: number;
  playbook: string;
  dependency: string;
  retest_status: 'Not Started' | 'Scheduled' | 'Passed' | 'Blocked';
  risk_acceptance_required: boolean;
}

export interface MaturityDomain {
  name: string;
  score: number;
  target: number;
  current_state: string;
  next_step: string;
}

export interface ProgramSummary {
  organization: string;
  goal: string;
  maturity_current: number;
  maturity_target: number;
  metrics: Record<string, number | string>;
  operating_principles: string[];
  cycle: { stage: string; leader_question: string }[];
}

export interface WorkshopArtifacts {
  maturity_assessment: string[];
  crown_jewel_worksheet: string[];
  prioritization_rationale: string[];
  validation_evidence_pack: string[];
  raci: { role: string; responsibility: string }[];
  roadmap_30_60_90: { window: string; outcome: string; actions: string }[];
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: {
    id: string;
    email: string;
    name: string;
    organization_id: string;
    role: string;
  };
}

export interface ImportResult {
  imported: number;
  errors: { row: number; field: string; message: string }[];
}
