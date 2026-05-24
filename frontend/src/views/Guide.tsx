import type { ReactNode } from 'react'
import { useState } from 'react'

interface GuideSection {
  id: string
  title: string
  content: ReactNode
}

const guideSections: GuideSection[] = [
  {
    id: 'overview',
    title: 'Overview',
    content: (
      <>
        <p>CTEM (Continuous Threat Exposure Management) is an operating model that moves security teams from patch-counting to exposure reduction. This workbench simulates a full CTEM cycle so leaders can learn the workflow, practice the decisions, and build a takeaway pack for their own programs.</p>
        <p>The app comes pre-loaded with a realistic demo scenario based on a fictional retail organization. All data is fictional — use it to explore without risk.</p>
      </>
    ),
  },
  {
    id: 'stages',
    title: 'The Five CTEM Stages',
    content: (
      <>
        <p>The sidebar guides you through five stages in order. Each stage answers a leadership question before handing off to the next:</p>
        <dl className="guide-dl">
          <dt><strong>1. Scoping</strong></dt>
          <dd>Define crown-jewel services, owners, and risk appetite. Decide what is in scope for the first CTEM sprint.</dd>
          <dt><strong>2. Discovery</strong></dt>
          <dd>Normalize exposures across CVEs, cloud misconfigurations, identity risks, secrets, and SaaS controls.</dd>
          <dt><strong>3. Prioritization</strong></dt>
          <dd>Rank exposures by business impact, attacker utility, and validation evidence — not just CVSS severity.</dd>
          <dt><strong>4. Validation</strong></dt>
          <dd>Map attack paths and assess evidence confidence to prove or disprove each exposure path.</dd>
          <dt><strong>5. Mobilization</strong></dt>
          <dd>Assign owners, set SLAs, track remediation, and manage accepted risk with a RACI-driven board.</dd>
        </dl>
      </>
    ),
  },
  {
    id: 'features',
    title: 'Key Features',
    content: (
      <>
        <ul className="guide-list">
          <li><strong>Dashboard</strong> — See the operating cycle, program maturity, and leadership principles at a glance.</li>
          <li><strong>Workshop Pack</strong> — Generate a facilitator-ready takeaway with templates, a remediation board snapshot, and a 30/60/90-day roadmap.</li>
          <li><strong>Sessions</strong> — Save and load named snapshots of your workspace. Use this to explore "what if" scenarios or preserve a workshop state.</li>
          <li><strong>CSV Import/Export</strong> — Export assets, exposures, or remediation actions to CSV for offline analysis, or import changes back in.</li>
          <li><strong>Executive Summary</strong> — Download a Markdown or HTML report summarizing the current program state.</li>
        </ul>
      </>
    ),
  },
  {
    id: 'glossary',
    title: 'Glossary',
    content: (
      <>
        <dl className="guide-dl glossary">
          <dt><strong>CTEM Score</strong></dt>
          <dd>A composite score (0–100) that ranks exposures by business impact, attacker utility, validation confidence, and mobilization feasibility. Higher scores demand faster action.</dd>
          <dt><strong>EPSS</strong> (Exploit Prediction Scoring System)</dt>
          <dd>A data-driven model that estimates the probability a vulnerability will be exploited in the wild within 30 days. Shown as a percentage.</dd>
          <dt><strong>KEV</strong> (Known Exploited Vulnerabilities)</dt>
          <dd>A CISA-maintained catalog of vulnerabilities with confirmed active exploitation. A KEV signal means threat actors are already using this vector.</dd>
          <dt><strong>CVSS</strong> (Common Vulnerability Scoring System)</dt>
          <dd>The standard severity rating (0–10) for vulnerabilities. CTEM uses CVSS as one input but overrides it with business context.</dd>
          <dt><strong>Attack Path</strong></dt>
          <dd>A sequence of exposures an attacker could chain together to reach a crown-jewel asset. Each step shows a technique, source, and destination.</dd>
          <dt><strong>Evidence Confidence</strong></dt>
          <dd>How sure the team is that a finding is real and reachable. Used to decide whether to act, validate further, or monitor.</dd>
          <dt><strong>RACI</strong> (Responsible, Accountable, Consulted, Informed)</dt>
          <dd>A responsibility assignment matrix used in the Mobilization stage to clarify who does what.</dd>
          <dt><strong>SLA</strong> (Service-Level Agreement)</dt>
          <dd>The target timeline for remediating an exposure. Set by the business owner based on risk and criticality.</dd>
          <dt><strong>Risk Acceptance</strong></dt>
          <dd>A formal decision to accept an exposure without remediation, typically with a timebox and executive sign-off.</dd>
        </dl>
      </>
    ),
  },
]

const Guide = () => {
  const [activeSection, setActiveSection] = useState(guideSections[0].id)

  return (
    <div className="page-stack">
      <section className="page-header">
        <div>
          <p className="eyebrow">Reference</p>
          <h1 className="page-title">User Guide</h1>
          <p className="page-intro">Learn how to use the CTEM Leader Lab workbench and understand the key concepts.</p>
        </div>
      </section>

      <div className="guide-layout">
        <nav className="guide-toc">
          {guideSections.map((section) => (
            <button
              key={section.id}
              className={`guide-toc-item ${activeSection === section.id ? 'active' : ''}`}
              onClick={() => setActiveSection(section.id)}
            >
              {section.title}
            </button>
          ))}
        </nav>
        <section className="content-section guide-content">
          {guideSections.map((section) => (
            <div key={section.id} style={{ display: activeSection === section.id ? 'block' : 'none' }}>
              <div className="section-heading">
                <h2>{section.title}</h2>
              </div>
              {section.content}
            </div>
          ))}
        </section>
      </div>
    </div>
  )
}

export default Guide
