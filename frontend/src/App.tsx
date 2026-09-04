import { useEffect, useMemo, useState } from 'react'
import './App.css'

const API = 'http://localhost:8000/api/v1'

type ExceptionStatus =
  | 'OPEN'
  | 'INVESTIGATING'
  | 'RESOLVED'
  | 'ESCALATED'
  | 'REJECTED'

type ExceptionRecord = {
  id: string
  reconciliation_id: string
  transaction_id: string
  exception_type: string
  severity: string
  description: string
  expected_value: string | null
  actual_value: string | null
  difference: string | null
  status: ExceptionStatus
  agent_decision: string | null
  agent_confidence: string | null
  assigned_to: string | null
}

type Investigation = {
  exception_id: string
  transaction_id?: string | null
  transaction_reference?: string | null
  exception_type?: string | null
  severity?: string | null
  expected_value?: string | null
  actual_value?: string | null
  difference?: string | null
  risk_score?: string | null
  recommendation?: string | null
  reasoning?: string | null
  agent_analysis?: {
    analysis: string
    recommended_action: string
    confidence: string
  } | null
  guardrail_passed?: boolean | null
  guardrail_reason?: string | null
  requires_human_approval: boolean
  final_action?: string | null
  error?: string | null
}

type DecisionResponse = {
  exception_id: string
  status: string
  decision: string
  reason?: string | null
}

function money(value: string | null | undefined) {
  if (value === null || value === undefined) return '—'

  const number = Number(value)

  if (Number.isNaN(number)) return value

  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    minimumFractionDigits: 2,
  }).format(number)
}

function shortId(value: string) {
  return `${value.slice(0, 8)}...`
}

function normalizeType(value: string) {
  return value
    .replaceAll('_', ' ')
    .toLowerCase()
    .replace(/\b\w/g, (char) => char.toUpperCase())
}

function statusLabel(value: string) {
  return value.replaceAll('_', ' ')
}

function App() {
  const [exceptions, setExceptions] = useState<ExceptionRecord[]>([])
  const [selected, setSelected] = useState<ExceptionRecord | null>(null)
  const [investigation, setInvestigation] =
    useState<Investigation | null>(null)

  const [filter, setFilter] = useState<'ALL' | ExceptionStatus>('ALL')
  const [loading, setLoading] = useState(true)
  const [investigating, setInvestigating] = useState(false)
  const [decisionLoading, setDecisionLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

  async function loadExceptions(keepSelection = true) {
    try {
      setLoading(true)
      setError(null)

      const response = await fetch(`${API}/exceptions`)

      if (!response.ok) {
        throw new Error('Unable to load exceptions.')
      }

      const data: ExceptionRecord[] = await response.json()

      setExceptions(data)

      if (keepSelection && selected) {
        const updated = data.find((item) => item.id === selected.id)
        if (updated) setSelected(updated)
      } else if (!selected && data.length > 0) {
        setSelected(data[0])
      }
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Unable to load exceptions.',
      )
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadExceptions(false)
  }, [])

  const filteredExceptions = useMemo(() => {
    if (filter === 'ALL') return exceptions

    return exceptions.filter(
      (exception) => exception.status === filter,
    )
  }, [exceptions, filter])

  const counts = useMemo(() => {
    return {
      total: exceptions.length,
      open: exceptions.filter((e) => e.status === 'OPEN').length,
      investigating: exceptions.filter(
        (e) => e.status === 'INVESTIGATING',
      ).length,
      resolved: exceptions.filter(
        (e) => e.status === 'RESOLVED',
      ).length,
      escalated: exceptions.filter(
        (e) => e.status === 'ESCALATED',
      ).length,
      rejected: exceptions.filter(
        (e) => e.status === 'REJECTED',
      ).length,
    }
  }, [exceptions])

  function selectException(exception: ExceptionRecord) {
    setSelected(exception)
    setInvestigation(null)
    setError(null)
    setSuccess(null)
  }

  async function investigate() {
    if (!selected) return

    try {
      setInvestigating(true)
      setError(null)
      setSuccess(null)

      const response = await fetch(
        `${API}/agent/exceptions/${selected.id}/investigate`,
        {
          method: 'POST',
        },
      )

      const data = await response.json()

      if (!response.ok) {
        throw new Error(
          data.detail || data.error || 'Investigation failed.',
        )
      }

      setInvestigation(data)

      await loadExceptions()

      setSuccess('AI investigation completed.')
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Investigation failed.',
      )
    } finally {
      setInvestigating(false)
    }
  }

  async function makeDecision(
    decision: 'approve' | 'reject',
  ) {
    if (!selected) return

    const message =
      decision === 'approve'
        ? 'Reviewed the exception and approved the resolution.'
        : 'Reviewed the exception and rejected the proposed resolution.'

    try {
      setDecisionLoading(true)
      setError(null)
      setSuccess(null)

      const response = await fetch(
        `${API}/exceptions/${selected.id}/${decision}`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            reason: message,
          }),
        },
      )

      const data: DecisionResponse = await response.json()

      if (!response.ok) {
        throw new Error(
          (data as unknown as { detail?: string }).detail ||
            'Unable to process decision.',
        )
      }

      setInvestigation(null)

      await loadExceptions()

      setSuccess(
        decision === 'approve'
          ? 'Exception approved and resolved.'
          : 'Exception rejected.',
      )
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Unable to process decision.',
      )
    } finally {
      setDecisionLoading(false)
    }
  }

  const displayedInvestigation = investigation

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand">
          <div className="brand-mark">◆</div>

          <div>
            <div className="brand-name">
              AI Finance Controller
            </div>

            <div className="brand-subtitle">
              Intelligent reconciliation & exception management
            </div>
          </div>
        </div>

        <div className="system-status">
          <span />
          System operational
        </div>
      </header>

      <main className="dashboard">
        <section className="page-heading">
          <div>
            <div className="eyebrow">FINANCE OPERATIONS</div>

            <h1>Exception Control Center</h1>

            <p>
              Monitor reconciliation exceptions, review agent
              decisions, and safely resolve financial discrepancies.
            </p>
          </div>

          <button
            className="refresh-button"
            onClick={() => loadExceptions()}
          >
            ↻ Refresh
          </button>
        </section>

        <section className="stats-grid">
          <StatCard
            label="Total Exceptions"
            value={counts.total}
            active={filter === 'ALL'}
            onClick={() => setFilter('ALL')}
          />

          <StatCard
            label="Open"
            value={counts.open}
            active={filter === 'OPEN'}
            onClick={() => setFilter('OPEN')}
          />

          <StatCard
            label="Investigating"
            value={counts.investigating}
            active={filter === 'INVESTIGATING'}
            onClick={() => setFilter('INVESTIGATING')}
          />

          <StatCard
            label="Resolved"
            value={counts.resolved}
            active={filter === 'RESOLVED'}
            onClick={() => setFilter('RESOLVED')}
          />

          <StatCard
            label="Escalated"
            value={counts.escalated}
            active={filter === 'ESCALATED'}
            onClick={() => setFilter('ESCALATED')}
          />

          <StatCard
            label="Rejected"
            value={counts.rejected}
            active={filter === 'REJECTED'}
            onClick={() => setFilter('REJECTED')}
          />
        </section>

        {error && (
          <div className="alert error">
            <strong>Error:</strong> {error}
          </div>
        )}

        {success && (
          <div className="alert success">
            ✓ {success}
          </div>
        )}

        <section className="workspace">
          <div className="exception-list panel">
            <div className="panel-heading">
              <div>
                <h2>Exceptions</h2>
                <span>
                  {filteredExceptions.length} exceptions shown
                </span>
              </div>

              <select
                value={filter}
                onChange={(event) =>
                  setFilter(
                    event.target.value as
                      | 'ALL'
                      | ExceptionStatus,
                  )
                }
              >
                <option value="ALL">All statuses</option>
                <option value="OPEN">Open</option>
                <option value="INVESTIGATING">
                  Investigating
                </option>
                <option value="RESOLVED">Resolved</option>
                <option value="ESCALATED">Escalated</option>
                <option value="REJECTED">Rejected</option>
              </select>
            </div>

            <div className="table-header">
              <span>EXCEPTION</span>
              <span>TYPE</span>
              <span>SEVERITY</span>
              <span>DIFFERENCE</span>
              <span>STATUS</span>
              <span>AGENT</span>
              <span />
            </div>

            {loading ? (
              <div className="empty-state">
                Loading exceptions...
              </div>
            ) : filteredExceptions.length === 0 ? (
              <div className="empty-state">
                No exceptions found.
              </div>
            ) : (
              <div className="table-body">
                {filteredExceptions.map((exception) => (
                  <div
                    className={`exception-row ${
                      selected?.id === exception.id
                        ? 'selected'
                        : ''
                    }`}
                    key={exception.id}
                  >
                    <button
                      className="row-main"
                      onClick={() => selectException(exception)}
                    >
                      <div className="id-block">
                        <strong>
                          {shortId(exception.id)}
                        </strong>
                        <small>
                          {shortId(exception.transaction_id)}
                        </small>
                      </div>

                      <span>
                        {normalizeType(exception.exception_type)}
                      </span>

                      <Severity
                        value={exception.severity}
                      />

                      <span className="difference">
                        {money(exception.difference)}
                      </span>

                      <Status value={exception.status} />

                      <span className="agent">
                        {exception.agent_decision
                          ? statusLabel(
                              exception.agent_decision,
                            )
                          : '—'}
                      </span>

                      <span className="view-label">
                        View
                      </span>
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          <aside className="details panel">
            {!selected ? (
              <div className="empty-details">
                <div className="empty-icon">◈</div>
                <h2>Select an exception</h2>
                <p>
                  Select an exception from the list to inspect
                  its financial impact and agent decision.
                </p>
              </div>
            ) : (
              <>
                <div className="details-header">
                  <div>
                    <div className="eyebrow">
                      EXCEPTION DETAILS
                    </div>

                    <h2>
                      {normalizeType(
                        selected.exception_type,
                      )}
                    </h2>

                    <code>{selected.id}</code>
                  </div>

                  <Status value={selected.status} />
                </div>

                <div className="details-section">
                  <div className="section-label">
                    FINANCIAL IMPACT
                  </div>

                  <div className="financial-grid">
                    <Metric
                      label="Expected"
                      value={money(
                        selected.expected_value,
                      )}
                    />

                    <Metric
                      label="Actual"
                      value={money(
                        selected.actual_value,
                      )}
                    />

                    <Metric
                      label="Difference"
                      value={money(
                        selected.difference,
                      )}
                      danger
                    />
                  </div>
                </div>

                <div className="details-section">
                  <div className="section-label">
                    EXCEPTION
                  </div>

                  <p className="description">
                    {selected.description}
                  </p>

                  <div className="info-grid">
                    <Info
                      label="Severity"
                      value={selected.severity}
                    />

                    <Info
                      label="Transaction"
                      value={shortId(
                        selected.transaction_id,
                      )}
                      mono
                    />

                    <Info
                      label="Reconciliation"
                      value={shortId(
                        selected.reconciliation_id,
                      )}
                      mono
                    />
                  </div>
                </div>

                {displayedInvestigation && (
                  <div className="ai-result">
                    <div className="ai-heading">
                      <div>
                        <div className="section-label">
                          AI INVESTIGATION
                        </div>
                        <h3>Agent Assessment</h3>
                      </div>

                      <div className="ai-badge">
                        AI
                      </div>
                    </div>

                    <div className="ai-metrics">
                      <Metric
                        label="Risk Score"
                        value={
                          displayedInvestigation.risk_score
                            ? Number(
                                displayedInvestigation.risk_score,
                              ).toFixed(2)
                            : '—'
                        }
                      />

                      <Metric
                        label="Confidence"
                        value={
                          displayedInvestigation
                            .agent_analysis?.confidence
                            ? Number(
                                displayedInvestigation
                                  .agent_analysis.confidence,
                              ).toFixed(2)
                            : selected.agent_confidence
                              ? Number(
                                  selected.agent_confidence,
                                ).toFixed(2)
                              : '—'
                        }
                      />

                      <Metric
                        label="Recommendation"
                        value={
                          displayedInvestigation.recommendation
                            ? statusLabel(
                                displayedInvestigation.recommendation,
                              )
                            : '—'
                        }
                      />
                    </div>

                    <div className="reasoning">
                      <div className="section-label">
                        REASONING
                      </div>

                      <p>
                        {displayedInvestigation.reasoning ||
                          displayedInvestigation.agent_analysis
                            ?.analysis ||
                          'No reasoning provided.'}
                      </p>
                    </div>

                    <div className="guardrail">
                      <div
                        className={
                          displayedInvestigation.guardrail_passed
                            ? 'guardrail-icon passed'
                            : 'guardrail-icon failed'
                        }
                      >
                        {displayedInvestigation.guardrail_passed
                          ? '✓'
                          : '!'}
                      </div>

                      <div>
                        <strong>
                          Guardrail{' '}
                          {displayedInvestigation.guardrail_passed
                            ? 'passed'
                            : 'failed'}
                        </strong>

                        <p>
                          {displayedInvestigation.guardrail_reason ||
                            'No guardrail explanation provided.'}
                        </p>
                      </div>
                    </div>
                  </div>
                )}

                <div className="action-area">
                  {selected.status === 'OPEN' && (
                    <button
                      className="primary-action"
                      onClick={investigate}
                      disabled={investigating}
                    >
                      {investigating
                        ? 'Investigating...'
                        : '✦ Investigate with AI'}
                    </button>
                  )}

                  {selected.status === 'INVESTIGATING' && (
                    <div className="decision-actions">
                      <button
                        className="approve-button"
                        onClick={() =>
                          makeDecision('approve')
                        }
                        disabled={decisionLoading}
                      >
                        {decisionLoading
                          ? 'Processing...'
                          : '✓ Approve Resolution'}
                      </button>

                      <button
                        className="reject-button"
                        onClick={() =>
                          makeDecision('reject')
                        }
                        disabled={decisionLoading}
                      >
                        Reject
                      </button>
                    </div>
                  )}

                  {selected.status === 'RESOLVED' && (
                    <div className="final-state resolved-state">
                      <strong>✓ Exception resolved</strong>
                      <span>
                        This exception has been successfully
                        resolved.
                      </span>
                    </div>
                  )}

                  {selected.status === 'ESCALATED' && (
                    <div className="final-state escalated-state">
                      <strong>⚠ Exception escalated</strong>
                      <span>
                        This exception requires additional
                        investigation or financial evidence.
                      </span>
                    </div>
                  )}

                  {selected.status === 'REJECTED' && (
                    <div className="final-state rejected-state">
                      <strong>Exception rejected</strong>
                      <span>
                        The proposed resolution was rejected.
                      </span>
                    </div>
                  )}
                </div>
              </>
            )}
          </aside>
        </section>
      </main>
    </div>
  )
}

function StatCard({
  label,
  value,
  active,
  onClick,
}: {
  label: string
  value: number
  active: boolean
  onClick: () => void
}) {
  return (
    <button
      className={`stat-card ${active ? 'active' : ''}`}
      onClick={onClick}
    >
      <span>{label}</span>
      <strong>{value}</strong>
    </button>
  )
}

function Metric({
  label,
  value,
  danger = false,
}: {
  label: string
  value: string
  danger?: boolean
}) {
  return (
    <div className="metric">
      <span>{label}</span>
      <strong className={danger ? 'danger' : ''}>
        {value}
      </strong>
    </div>
  )
}

function Info({
  label,
  value,
  mono = false,
}: {
  label: string
  value: string
  mono?: boolean
}) {
  return (
    <div className="info-item">
      <span>{label}</span>
      <strong className={mono ? 'mono' : ''}>
        {value}
      </strong>
    </div>
  )
}

function Severity({ value }: { value: string }) {
  return (
    <span
      className={`severity severity-${value.toLowerCase()}`}
    >
      {value}
    </span>
  )
}

function Status({ value }: { value: string }) {
  return (
    <span
      className={`status status-${value.toLowerCase()}`}
    >
      {statusLabel(value)}
    </span>
  )
}

export default App
