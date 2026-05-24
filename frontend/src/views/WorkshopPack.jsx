import { useEffect, useMemo, useState } from 'react';
import { Check, Clipboard, Download, Printer } from 'lucide-react';

import { api } from '../api';

const buildMarkdown = ({ summary, artifacts, prioritized, actions }) => {
  const actItems = prioritized.filter((item) => item.decision === 'Act');

  return [
    `# CTEM Workshop Pack: ${summary.organization}`,
    '',
    `Goal: ${summary.goal}`,
    '',
    '## Crown-Jewel Scoping Worksheet',
    ...artifacts.crown_jewel_worksheet.map((item, index) => `${index + 1}. ${item}`),
    '',
    '## Prioritization Rubric',
    ...artifacts.prioritization_rationale.map((item, index) => `${index + 1}. ${item}`),
    '',
    '## Validation Evidence Checklist',
    ...artifacts.validation_evidence_pack.map((item, index) => `${index + 1}. ${item}`),
    '',
    '## Mobilization Template',
    '| Field | Prompt |',
    '| --- | --- |',
    '| Owner | Which team accepts delivery accountability? |',
    '| SLA | What deadline matches exploitability, reachability, and business impact? |',
    '| Retest | What evidence proves the exposure is reduced or blocked? |',
    '| Exception | Who can accept residual risk, and for how long? |',
    '',
    '## First Act Decisions',
    ...actItems.map((item) => `- ${item.title}: ${item.next_action}`),
    '',
    '## RACI',
    ...artifacts.raci.map((row) => `- ${row.role}: ${row.responsibility}`),
    '',
    '## 30/60/90 Roadmap',
    ...artifacts.roadmap_30_60_90.map((item) => `- ${item.window}: ${item.outcome}. ${item.actions}`),
    '',
    '## Current Remediation Board',
    ...actions.map((action) => `- ${action.id} (${action.priority}): ${action.title} - ${action.owner}, ${action.sla}`),
    '',
  ].join('\n');
};

const ActionButton = ({ children, icon: Icon, onClick, tone = 'default' }) => (
  <button className={`tool-button ${tone}`} type="button" onClick={onClick}>
    <Icon size={18} />
    <span>{children}</span>
  </button>
);

const ChecklistSection = ({ title, kicker, items }) => (
  <section className="content-section pack-section">
    <div className="section-heading">
      <p className="eyebrow">{kicker}</p>
      <h2>{title}</h2>
    </div>
    <div className="prompt-grid">
      {items.map((item, index) => (
        <div className="prompt-card" key={item}>
          <span>{index + 1}</span>
          <p>{item}</p>
        </div>
      ))}
    </div>
  </section>
);

const WorkshopPack = () => {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [copyState, setCopyState] = useState('idle');

  useEffect(() => {
    Promise.all([
      api.getProgramSummary(),
      api.getWorkshopArtifacts(),
      api.getPrioritizedExposures(),
      api.getRemediationActions(),
    ])
      .then(([summary, artifacts, prioritized, actions]) => {
        setData({ summary, artifacts, prioritized, actions });
      })
      .catch(setError);
  }, []);

  const markdown = useMemo(() => (data ? buildMarkdown(data) : ''), [data]);

  const packJson = useMemo(() => {
    if (!data) return null;
    return {
      organization: data.summary.organization,
      goal: data.summary.goal,
      generated_at: new Date().toISOString(),
      workshop_artifacts: data.artifacts,
      act_decisions: data.prioritized.filter((item) => item.decision === 'Act'),
      remediation_board: data.actions,
    };
  }, [data]);

  const copyMarkdown = async () => {
    if (!markdown) return;
    try {
      await navigator.clipboard.writeText(markdown);
      setCopyState('copied');
      window.setTimeout(() => setCopyState('idle'), 1800);
    } catch {
      setCopyState('failed');
      window.setTimeout(() => setCopyState('idle'), 2200);
    }
  };

  const downloadJson = () => {
    if (!packJson) return;
    const blob = new Blob([JSON.stringify(packJson, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'ctem-workshop-pack.json';
    link.click();
    URL.revokeObjectURL(url);
  };

  if (error) return <div className="notice-panel error">Unable to load workshop pack. {error.message}</div>;
  if (!data) return <div className="notice-panel">Preparing workshop pack...</div>;

  const { summary, artifacts, prioritized, actions } = data;
  const actItems = prioritized.filter((item) => item.decision === 'Act').slice(0, 4);

  return (
    <div className="page-stack workshop-pack">
      <section className="page-header">
        <div>
          <p className="eyebrow">Facilitator Kit</p>
          <h1 className="page-title">Workshop Pack</h1>
          <p className="page-intro">
            A ready-to-run CTEM working session for {summary.organization}, built from the demo scenario.
          </p>
        </div>
        <div className="tool-row" aria-label="Workshop pack actions">
          <ActionButton icon={copyState === 'copied' ? Check : Clipboard} onClick={copyMarkdown} tone={copyState}>
            {copyState === 'copied' ? 'Copied' : copyState === 'failed' ? 'Copy failed' : 'Copy Markdown'}
          </ActionButton>
          <ActionButton icon={Download} onClick={downloadJson}>Download JSON</ActionButton>
          <ActionButton icon={Printer} onClick={() => window.print()}>Print</ActionButton>
        </div>
      </section>

      <section className="metric-grid">
        <div className="metric-card compact">
          <span>Session goal</span>
          <strong>{summary.metrics.exposure_reduction_goal}</strong>
        </div>
        <div className="metric-card compact">
          <span>Act decisions</span>
          <strong>{summary.metrics.act_decisions}</strong>
        </div>
        <div className="metric-card compact">
          <span>Validated paths</span>
          <strong>{summary.metrics.validated_attack_paths}</strong>
        </div>
      </section>

      <ChecklistSection
        title="Crown-Jewel Scoping Worksheet"
        kicker="Part 1"
        items={artifacts.crown_jewel_worksheet}
      />

      <section className="split-grid">
        <ChecklistSection
          title="Prioritization Rubric"
          kicker="Part 2"
          items={artifacts.prioritization_rationale}
        />
        <ChecklistSection
          title="Validation Evidence Checklist"
          kicker="Part 3"
          items={artifacts.validation_evidence_pack}
        />
      </section>

      <section className="content-section">
        <div className="section-heading">
          <p className="eyebrow">Part 4</p>
          <h2>Mobilization Template</h2>
        </div>
        <div className="template-grid">
          {[
            ['Owner', 'Which team accepts delivery accountability?'],
            ['SLA', 'What deadline matches exploitability, reachability, and business impact?'],
            ['Retest', 'What evidence proves the exposure is reduced or blocked?'],
            ['Exception', 'Who can accept residual risk, and for how long?'],
          ].map(([field, prompt]) => (
            <div className="template-field" key={field}>
              <span>{field}</span>
              <p>{prompt}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="content-section">
        <div className="section-heading">
          <p className="eyebrow">Act First</p>
          <h2>First Decisions To Mobilize</h2>
        </div>
        <div className="pack-action-list">
          {actItems.map((item) => (
            <article className="pack-action" key={item.id}>
              <div>
                <h3>{item.title}</h3>
                <p>{item.next_action}</p>
              </div>
              <strong>{item.ctem_score}</strong>
            </article>
          ))}
        </div>
      </section>

      <section className="split-grid">
        <div className="content-section">
          <div className="section-heading">
            <h2>RACI</h2>
          </div>
          <div className="roadmap">
            {artifacts.raci.map((row) => (
              <div className="roadmap-item" key={row.role}>
                <span>{row.role}</span>
                <p>{row.responsibility}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="content-section">
          <div className="section-heading">
            <h2>30/60/90 Roadmap</h2>
          </div>
          <div className="roadmap">
            {artifacts.roadmap_30_60_90.map((item) => (
              <div className="roadmap-item" key={item.window}>
                <span>{item.window}</span>
                <h3>{item.outcome}</h3>
                <p>{item.actions}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="content-section">
        <div className="section-heading">
          <h2>Remediation Board Snapshot</h2>
        </div>
        <div className="table-wrap">
          <table className="data-table">
            <thead>
              <tr>
                <th>Action</th>
                <th>Owner</th>
                <th>SLA</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {actions.map((action) => (
                <tr key={action.id}>
                  <td><strong>{action.title}</strong><span>{action.id}</span></td>
                  <td>{action.owner}</td>
                  <td>{action.sla}</td>
                  <td>{action.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
};

export default WorkshopPack;
