import { useEffect, useMemo, useState } from 'react'
import './App.css'

import {
  approveException,
  getExceptions,
  getReconciliations,
  getTransactions,
  healthCheck,
  investigateException,
  rejectException,
  runReconciliation,
} from './services/api'

import type {
  FinanceException,
  InvestigationResult,
  Reconciliation,
  Transaction,
} from './types/finance'

type Page =
  | 'dashboard'
  | 'exceptions'
  | 'transactions'
  | 'reconciliations'

function formatMoney(value: string | number | null | undefined): string {
  if (value === null || value === undefined || value === '') {
    return '—'
  }

  const number = Number(value)

  if (Number.isNaN(number)) {
    return String(value)
  }

  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 2,
  }).format(number)
}

function formatDate(value: unknown): string {
  if (!value) return '—'

  const date = new Date(String(value))

  if (Number.isNaN(date.getTime())) {
    return String(value)
  }

  return date.toLocaleDateString('en-IN', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  })
}

function shortId(value: unknown): string {
  const text = String(value ?? '')

  if (!text) return '—'

  if (text.length <= 12) return text

  return `${text.slice(0, 8)}…${text.slice(-4)}`
}

function statusClass(value: unknown): string {
  return String(value ?? 'UNKNOWN')
    .toLowerCase()
    .replaceAll('_', '-')
}

function getTransactionLabel(
  transactionId: string | undefined,
  transactions: Transaction[],
): string {
  if (!transactionId) return 'Unknown transaction'

  const transaction = transactions.find(
    (tx) => tx.transaction_id === transactionId,
  )

  if (!transaction) {
    return shortId(transactionId)
  }

  return (
    transaction.transaction_reference ||
    transaction.transaction_id ||
    shortId(transactionId)
  )
}

function App() {
  const [page, setPage] = useState<Page>('dashboard')

  const [transactions, setTransactions] = useState<Transaction[]>([])
  const [reconciliations, setReconciliations] = useState<Reconciliation[]>([])
  const [exceptions, setExceptions] = useState<FinanceException[]>([])

  const [apiOnline, setApiOnline] = useState(false)
  const [loading, setLoading] = useState(true)
  const [runningReconciliation, setRunningReconciliation] = useState(false)

  const [selectedException, setSelectedException] =
    useState<FinanceException | null>(null)

  const [investigation, setInvestigation] =
    useState<InvestigationResult | null>(null)

  const [investigating, setInvestigating] = useState(false)
  const [reviewing, setReviewing] = useState(false)

  const [search, setSearch] = useState('')
  const [severityFilter, setSeverityFilter] = useState('ALL')
  const [statusFilter, setStatusFilter] = useState('ALL')

  const [toast, setToast] = useState<{
    type: 'success' | 'error'
    message: string
  } | null>(null)

  useEffect(() => {
    loadData()
  }, [])

  useEffect(() => {
    if (!toast) return

    const timer = window.setTimeout(() => {
      setToast(null)
    }, 3500)

    return () => window.clearTimeout(timer)
  }, [toast])

  async function loadData() {
    setLoading(true)

    try {
      const health = await healthCheck()
      setApiOnline(health.status === 'healthy')

      const [
        transactionData,
        reconciliationData,
        exceptionData,
      ] = await Promise.all([
        getTransactions(),
        getReconciliations(),
        getExceptions(),
      ])

      setTransactions(transactionData)
      setReconciliations(reconciliationData)
      setExceptions(exceptionData)
    } catch (error) {
      setApiOnline(false)

      setToast({
        type: 'error',
        message:
          error instanceof Error
            ? error.message
            : 'Unable to connect to backend',
      })
    } finally {
      setLoading(false)
    }
  }

  async function handleRunReconciliation() {
    setRunningReconciliation(true)

    try {
      const result = await runReconciliation()

      setToast({
        type: 'success',
        message: `Reconciliation completed: ${
          result.matched ?? 0
        } matched, ${
          result.mismatched ?? 0
        } mismatched, ${
          result.total_exceptions ?? 0
        } exceptions.`,
      })

      await loadData()
    } catch (error) {
      setToast({
        type: 'error',
        message:
          error instanceof Error
            ? error.message
            : 'Reconciliation failed',
      })
    } finally {
      setRunningReconciliation(false)
    }
  }

  async function handleInvestigate(exception: FinanceException) {
    setSelectedException(exception)
    setInvestigation(null)
    setInvestigating(true)

    try {
      const result = await investigateException(exception.id)

      setInvestigation(result)

      await refreshExceptions()

      setToast({
        type: 'success',
        message: 'AI investigation completed.',
      })
    } catch (error) {
      setToast({
        type: 'error',
        message:
          error instanceof Error
            ? error.message
            : 'AI investigation failed',
      })
    } finally {
      setInvestigating(false)
    }
  }

  async function refreshExceptions() {
    const data = await getExceptions()
    setExceptions(data)

    if (selectedException) {
      const updated = data.find(
        (item) => item.id === selectedException.id,
      )

      if (updated) {
        setSelectedException(updated)
      }
    }
  }

  async function handleApprove() {
    if (!selectedException) return

    setReviewing(true)

    try {
      const result = await approveException(
        selectedException.id,
        'Human reviewer approved the AI recommendation.',
      )

      setToast({
        type: 'success',
        message: `Exception ${shortId(
          result.exception_id,
        )} resolved successfully.`,
      })

      setSelectedException(null)
      setInvestigation(null)

      await refreshExceptions()
    } catch (error) {
      setToast({
        type: 'error',
        message:
          error instanceof Error
            ? error.message
            : 'Approval failed',
      })
    } finally {
      setReviewing(false)
    }
  }

  async function handleReject() {
    if (!selectedException) return

    setReviewing(true)

    try {
      const result = await rejectException(
        selectedException.id,
        'Human reviewer rejected the AI recommendation.',
      )

      setToast({
        type: 'success',
        message: `Exception ${shortId(
          result.exception_id,
        )} rejected.`,
      })

      setSelectedException(null)
      setInvestigation(null)

      await refreshExceptions()
    } catch (error) {
      setToast({
        type: 'error',
        message:
          error instanceof Error
            ? error.message
            : 'Rejection failed',
      })
    } finally {
      setReviewing(false)
    }
  }

  const stats = useMemo(() => {
    const open = exceptions.filter(
      (item) => item.status === 'OPEN',
    ).length

    const investigatingCount = exceptions.filter(
      (item) => item.status === 'INVESTIGATING',
    ).length

    const resolved = exceptions.filter(
      (item) => item.status === 'RESOLVED',
    ).length

    const rejected = exceptions.filter(
      (item) => item.status === 'REJECTED',
    ).length

    const critical = exceptions.filter(
      (item) => item.severity === 'CRITICAL',
    ).length

    const high = exceptions.filter(
      (item) => item.severity === 'HIGH',
    ).length

    const mismatches = reconciliations.filter(
      (item) =>
        String(
          item.status ??
            item.reconciliation_status ??
            '',
        ).toUpperCase() === 'MISMATCH',
    ).length

    return {
      open,
      investigating: investigatingCount,
      resolved,
      rejected,
      critical,
      high,
      mismatches,
    }
  }, [exceptions, reconciliations])

  const filteredExceptions = useMemo(() => {
    const query = search.trim().toLowerCase()

    return exceptions.filter((exception) => {
      const matchesSearch =
        !query ||
        exception.id.toLowerCase().includes(query) ||
        exception.transaction_id
          .toLowerCase()
          .includes(query) ||
        exception.exception_type
          .toLowerCase()
          .includes(query) ||
        exception.description
          .toLowerCase()
          .includes(query)

      const matchesSeverity =
        severityFilter === 'ALL' ||
        exception.severity === severityFilter

      const matchesStatus =
        statusFilter === 'ALL' ||
        exception.status === statusFilter

      return (
        matchesSearch &&
        matchesSeverity &&
        matchesStatus
      )
    })
  }, [
    exceptions,
    search,
    severityFilter,
    statusFilter,
  ])

  return (
    <div className="app-shell">
      <Sidebar
        page={page}
        setPage={setPage}
        exceptionCount={stats.open}
      />

      <main className="main-content">
        <Header
          apiOnline={apiOnline}
          onRefresh={loadData}
          loading={loading}
        />

        {toast && (
          <div className={`toast ${toast.type}`}>
            <span className="toast-icon">
              {toast.type === 'success' ? '✓' : '⚠'}
            </span>
            <span>{toast.message}</span>
          </div>
        )}

        {page === 'dashboard' && (
          <Dashboard
            stats={stats}
            transactions={transactions}
            exceptions={exceptions}
            reconciliations={reconciliations}
            loading={loading}
            runningReconciliation={
              runningReconciliation
            }
            onRunReconciliation={
              handleRunReconciliation
            }
            onNavigate={setPage}
            onInvestigate={handleInvestigate}
          />
        )}

        {page === 'exceptions' && (
          <ExceptionsPage
            exceptions={filteredExceptions}
            search={search}
            setSearch={setSearch}
            severityFilter={severityFilter}
            setSeverityFilter={setSeverityFilter}
            statusFilter={statusFilter}
            setStatusFilter={setStatusFilter}
            onInvestigate={handleInvestigate}
            selectedException={selectedException}
            investigation={investigation}
            investigating={investigating}
            reviewing={reviewing}
            onClose={() => {
              setSelectedException(null)
              setInvestigation(null)
            }}
            onApprove={handleApprove}
            onReject={handleReject}
          />
        )}

        {page === 'transactions' && (
          <TransactionsPage
            transactions={transactions}
            search={search}
            setSearch={setSearch}
          />
        )}

        {page === 'reconciliations' && (
          <ReconciliationsPage
            reconciliations={reconciliations}
            transactions={transactions}
          />
        )}
      </main>
    </div>
  )
}

/* =====================================================
   SIDEBAR
===================================================== */

function Sidebar({
  page,
  setPage,
  exceptionCount,
}: {
  page: Page
  setPage: (page: Page) => void
  exceptionCount: number
}) {
  return (
    <aside className="sidebar">
      <div className="brand">
        <div className="brand-mark">
          <span>₿</span>
        </div>

        <div>
          <div className="brand-name">
            Finance<span>AI</span>
          </div>
          <div className="brand-subtitle">
            CONTROLLER
          </div>
        </div>
      </div>

      <div className="nav-section">
        <div className="nav-label">WORKSPACE</div>

        <NavItem
          icon="⌂"
          label="Dashboard"
          active={page === 'dashboard'}
          onClick={() => setPage('dashboard')}
        />

        <NavItem
          icon="⚠"
          label="Exceptions"
          active={page === 'exceptions'}
          badge={exceptionCount}
          onClick={() => setPage('exceptions')}
        />

        <NavItem
          icon="↔"
          label="Transactions"
          active={page === 'transactions'}
          onClick={() => setPage('transactions')}
        />

        <NavItem
          icon="◎"
          label="Reconciliations"
          active={page === 'reconciliations'}
          onClick={() => setPage('reconciliations')}
        />
      </div>

      <div className="sidebar-bottom">
        <div className="agent-card">
          <div className="agent-avatar">AI</div>

          <div>
            <strong>Finance Agent</strong>
            <span>Agentic workflow active</span>
          </div>

          <div className="online-dot" />
        </div>

        <div className="version">
          AI Finance Controller v0.1
        </div>
      </div>
    </aside>
  )
}

function NavItem({
  icon,
  label,
  active,
  badge,
  onClick,
}: {
  icon: string
  label: string
  active: boolean
  badge?: number
  onClick: () => void
}) {
  return (
    <button
      className={`nav-item ${active ? 'active' : ''}`}
      onClick={onClick}
    >
      <span className="nav-icon">{icon}</span>
      <span>{label}</span>

      {badge !== undefined && badge > 0 && (
        <span className="nav-badge">{badge}</span>
      )}
    </button>
  )
}

/* =====================================================
   HEADER
===================================================== */

function Header({
  apiOnline,
  onRefresh,
  loading,
}: {
  apiOnline: boolean
  onRefresh: () => void
  loading: boolean
}) {
  return (
    <header className="topbar">
      <div>
        <div className="breadcrumb">
          Finance Operations / Overview
        </div>

        <h1>AI Finance Controller</h1>

        <p className="header-description">
          Autonomous reconciliation, exception
          investigation and human-in-the-loop controls.
        </p>
      </div>

      <div className="topbar-actions">
        <div
          className={`api-status ${
            apiOnline ? 'online' : 'offline'
          }`}
        >
          <span className="status-dot" />
          {apiOnline ? 'API Online' : 'API Offline'}
        </div>

        <button
          className="icon-button"
          onClick={onRefresh}
          disabled={loading}
          title="Refresh data"
        >
          ↻
        </button>

        <div className="user-avatar">F</div>
      </div>
    </header>
  )
}

/* =====================================================
   DASHBOARD
===================================================== */

function Dashboard({
  stats,
  transactions,
  exceptions,
  reconciliations,
  loading,
  runningReconciliation,
  onRunReconciliation,
  onNavigate,
  onInvestigate,
}: {
  stats: {
    open: number
    investigating: number
    resolved: number
    rejected: number
    critical: number
    high: number
    mismatches: number
  }
  transactions: Transaction[]
  exceptions: FinanceException[]
  reconciliations: Reconciliation[]
  loading: boolean
  runningReconciliation: boolean
  onRunReconciliation: () => void
  onNavigate: (page: Page) => void
  onInvestigate: (exception: FinanceException) => void
}) {
  if (loading) {
    return <LoadingState />
  }

  return (
    <div className="page">
      <div className="page-heading">
        <div>
          <h2>Operations overview</h2>
          <p>
            Monitor reconciliation health and resolve
            financial exceptions.
          </p>
        </div>

        <button
          className="primary-button"
          onClick={onRunReconciliation}
          disabled={runningReconciliation}
        >
          {runningReconciliation ? (
            <>
              <span className="spinner" />
              Running...
            </>
          ) : (
            <>
              <span>▶</span>
              Run reconciliation
            </>
          )}
        </button>
      </div>

      <div className="metric-grid">
        <MetricCard
          label="Total transactions"
          value={transactions.length}
          icon="↔"
          detail="Loaded from finance system"
        />

        <MetricCard
          label="Open exceptions"
          value={stats.open}
          icon="⚠"
          tone={stats.open > 0 ? 'warning' : 'normal'}
          detail={
            stats.critical > 0
              ? `${stats.critical} critical`
              : 'No critical exceptions'
          }
        />

        <MetricCard
          label="Investigating"
          value={stats.investigating}
          icon="◌"
          tone="info"
          detail="AI / human review"
        />

        <MetricCard
          label="Resolved"
          value={stats.resolved}
          icon="✓"
          tone="success"
          detail="Exceptions closed"
        />
      </div>

      <div className="dashboard-grid">
        <section className="panel exception-panel">
          <div className="panel-header">
            <div>
              <h3>Priority exceptions</h3>
              <p>
                Highest-risk items requiring attention
              </p>
            </div>

            <button
              className="text-button"
              onClick={() =>
                onNavigate('exceptions')
              }
            >
              View all →
            </button>
          </div>

          {exceptions.length === 0 ? (
            <EmptyState
              title="No exceptions"
              text="Your reconciliation queue is clean."
            />
          ) : (
            <div className="exception-list">
              {exceptions
                .filter(
                  (item) =>
                    item.status === 'OPEN' ||
                    item.status === 'INVESTIGATING',
                )
                .sort(
                  (a, b) =>
                    severityWeight(b.severity) -
                    severityWeight(a.severity),
                )
                .slice(0, 6)
                .map((exception) => (
                  <ExceptionRow
                    key={exception.id}
                    exception={exception}
                    onClick={() =>
                      onInvestigate(exception)
                    }
                  />
                ))}
            </div>
          )}
        </section>

        <section className="panel">
          <div className="panel-header">
            <div>
              <h3>System health</h3>
              <p>Current finance control posture</p>
            </div>
          </div>

          <div className="health-list">
            <HealthRow
              label="Reconciliation engine"
              status="Operational"
            />

            <HealthRow
              label="AI investigation agent"
              status="Operational"
            />

            <HealthRow
              label="Exception workflow"
              status={
                stats.open > 0
                  ? `${stats.open} open`
                  : 'Clear'
              }
              warning={stats.open > 0}
            />

            <HealthRow
              label="High-risk exceptions"
              status={String(stats.high)}
              warning={stats.high > 0}
            />
          </div>

          <div className="health-summary">
            <div className="health-circle">
              <strong>
                {exceptions.length === 0
                  ? 100
                  : Math.max(
                      0,
                      Math.round(
                        ((stats.resolved +
                          stats.rejected) /
                          exceptions.length) *
                          100,
                      ),
                    )}
                %
              </strong>
              <span>closed</span>
            </div>

            <div>
              <strong>Exception resolution</strong>
              <p>
                Automated detection with human approval
                controls.
              </p>
            </div>
          </div>
        </section>
      </div>

      <section className="panel">
        <div className="panel-header">
          <div>
            <h3>Recent reconciliations</h3>
            <p>
              Latest transaction matching activity
            </p>
          </div>

          <button
            className="text-button"
            onClick={() =>
              onNavigate('reconciliations')
            }
          >
            Open reconciliations →
          </button>
        </div>

        <ReconciliationTable
          reconciliations={reconciliations.slice(0, 6)}
          transactions={transactions}
        />
      </section>
    </div>
  )
}

function MetricCard({
  label,
  value,
  icon,
  detail,
  tone = 'normal',
}: {
  label: string
  value: string | number
  icon: string
  detail: string
  tone?: 'normal' | 'warning' | 'success' | 'info'
}) {
  return (
    <div className={`metric-card ${tone}`}>
      <div className="metric-top">
        <span>{label}</span>
        <div className="metric-icon">{icon}</div>
      </div>

      <strong>{value}</strong>

      <small>{detail}</small>
    </div>
  )
}

/* =====================================================
   EXCEPTIONS
===================================================== */

function ExceptionsPage({
  exceptions,
  search,
  setSearch,
  severityFilter,
  setSeverityFilter,
  statusFilter,
  setStatusFilter,
  onInvestigate,
  selectedException,
  investigation,
  investigating,
  reviewing,
  onClose,
  onApprove,
  onReject,
}: {
  exceptions: FinanceException[]
  search: string
  setSearch: (value: string) => void
  severityFilter: string
  setSeverityFilter: (value: string) => void
  statusFilter: string
  setStatusFilter: (value: string) => void
  onInvestigate: (exception: FinanceException) => void
  selectedException: FinanceException | null
  investigation: InvestigationResult | null
  investigating: boolean
  reviewing: boolean
  onClose: () => void
  onApprove: () => void
  onReject: () => void
}) {
  return (
    <div className="page">
      <div className="page-heading">
        <div>
          <h2>Exception management</h2>
          <p>
            Review discrepancies detected during
            reconciliation.
          </p>
        </div>

        <div className="queue-summary">
          <span>{exceptions.length}</span>
          results
        </div>
      </div>

      <div className="filter-bar">
        <div className="search-box">
          <span>⌕</span>
          <input
            value={search}
            onChange={(event) =>
              setSearch(event.target.value)
            }
            placeholder="Search exceptions..."
          />
        </div>

        <select
          value={severityFilter}
          onChange={(event) =>
            setSeverityFilter(event.target.value)
          }
        >
          <option value="ALL">All severities</option>
          <option value="CRITICAL">Critical</option>
          <option value="HIGH">High</option>
          <option value="MEDIUM">Medium</option>
          <option value="LOW">Low</option>
        </select>

        <select
          value={statusFilter}
          onChange={(event) =>
            setStatusFilter(event.target.value)
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

      <div
        className={`exceptions-layout ${
          selectedException ? 'with-detail' : ''
        }`}
      >
        <section className="panel table-panel">
          {exceptions.length === 0 ? (
            <EmptyState
              title="No exceptions found"
              text="Try changing your filters."
            />
          ) : (
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Exception</th>
                    <th>Type</th>
                    <th>Severity</th>
                    <th>Difference</th>
                    <th>Status</th>
                    <th />
                  </tr>
                </thead>

                <tbody>
                  {exceptions.map((exception) => (
                    <tr
                      key={exception.id}
                      className={
                        selectedException?.id ===
                        exception.id
                          ? 'selected-row'
                          : ''
                      }
                      onClick={() =>
                        onInvestigate(exception)
                      }
                    >
                      <td>
                        <div className="primary-cell">
                          <strong>
                            {shortId(exception.id)}
                          </strong>
                          <span>
                            TX{' '}
                            {shortId(
                              exception.transaction_id,
                            )}
                          </span>
                        </div>
                      </td>

                      <td>
                        <span className="type-label">
                          {exception.exception_type.replaceAll(
                            '_',
                            ' ',
                          )}
                        </span>
                      </td>

                      <td>
                        <StatusBadge
                          value={exception.severity}
                          type="severity"
                        />
                      </td>

                      <td className="amount danger-text">
                        {formatMoney(
                          exception.difference,
                        )}
                      </td>

                      <td>
                        <StatusBadge
                          value={exception.status}
                          type="status"
                        />
                      </td>

                      <td>
                        <button
                          className="row-action"
                          onClick={(event) => {
                            event.stopPropagation()
                            onInvestigate(exception)
                          }}
                        >
                          Investigate
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>

        {selectedException && (
          <ExceptionDetail
            exception={selectedException}
            investigation={investigation}
            investigating={investigating}
            reviewing={reviewing}
            onClose={onClose}
            onApprove={onApprove}
            onReject={onReject}
          />
        )}
      </div>
    </div>
  )
}

function ExceptionRow({
  exception,
  onClick,
}: {
  exception: FinanceException
  onClick: () => void
}) {
  return (
    <button className="exception-row" onClick={onClick}>
      <div
        className={`severity-bar ${statusClass(
          exception.severity,
        )}`}
      />

      <div className="exception-main">
        <div className="exception-title">
          {exception.exception_type.replaceAll(
            '_',
            ' ',
          )}
        </div>

        <div className="exception-description">
          {exception.description}
        </div>

        <div className="exception-meta">
          <span>
            TX {shortId(exception.transaction_id)}
          </span>
          <span>
            {formatMoney(exception.difference)}
          </span>
        </div>
      </div>

      <div className="exception-right">
        <StatusBadge
          value={exception.severity}
          type="severity"
        />
        <span className="arrow">→</span>
      </div>
    </button>
  )
}

/* =====================================================
   EXCEPTION DETAIL
===================================================== */

function ExceptionDetail({
  exception,
  investigation,
  investigating,
  reviewing,
  onClose,
  onApprove,
  onReject,
}: {
  exception: FinanceException
  investigation: InvestigationResult | null
  investigating: boolean
  reviewing: boolean
  onClose: () => void
  onApprove: () => void
  onReject: () => void
}) {
  return (
    <aside className="exception-detail">
      <div className="detail-header">
        <div>
          <span className="eyebrow">
            EXCEPTION DETAILS
          </span>

          <h3>{exception.exception_type.replaceAll(
            '_',
            ' ',
          )}</h3>

          <span className="detail-id">
            {exception.id}
          </span>
        </div>

        <button
          className="close-button"
          onClick={onClose}
        >
          ×
        </button>
      </div>

      <div className="detail-status-row">
        <StatusBadge
          value={exception.severity}
          type="severity"
        />

        <StatusBadge
          value={exception.status}
          type="status"
        />
      </div>

      <div className="detail-section">
        <h4>Issue</h4>
        <p className="detail-description">
          {exception.description}
        </p>
      </div>

      <div className="value-grid">
        <ValueBox
          label="Expected"
          value={formatMoney(
            exception.expected_value,
          )}
        />

        <ValueBox
          label="Actual"
          value={formatMoney(exception.actual_value)}
        />

        <ValueBox
          label="Difference"
          value={formatMoney(exception.difference)}
          danger
        />
      </div>

      <div className="detail-section">
        <h4>Transaction</h4>

        <div className="info-list">
          <InfoLine
            label="Transaction ID"
            value={exception.transaction_id}
          />

          <InfoLine
            label="Reconciliation ID"
            value={exception.reconciliation_id}
          />

          <InfoLine
            label="Assigned to"
            value={exception.assigned_to || 'Unassigned'}
          />
        </div>
      </div>

      <div className="ai-section">
        <div className="ai-heading">
          <div className="ai-logo">✦</div>

          <div>
            <h4>AI investigation</h4>
            <span>Finance Agent</span>
          </div>
        </div>

        {!investigation && !investigating && (
          <div className="ai-empty">
            <div className="ai-empty-icon">
              ✦
            </div>

            <strong>
              Ready to investigate
            </strong>

            <p>
              The AI agent will analyze the exception,
              determine risk, recommend an action and
              apply guardrails.
            </p>

            <button
              className="ai-button"
              onClick={() => {
                // Detail is already opened by investigation.
              }}
              disabled
            >
              Investigation available
            </button>
          </div>
        )}

        {investigating && (
          <div className="ai-loading">
            <div className="agent-pulse">✦</div>

            <strong>
              Agent investigating...
            </strong>

            <p>
              Analyzing transaction context, mismatch
              evidence and financial risk.
            </p>

            <div className="loading-lines">
              <span />
              <span />
              <span />
            </div>
          </div>
        )}

        {investigation && !investigating && (
          <div className="investigation-result">
            {investigation.agent_analysis && (
              <div className="analysis-block">
                <div className="analysis-label">
                  AGENT ANALYSIS
                </div>

                <p>
                  {investigation.agent_analysis.analysis}
                </p>
              </div>
            )}

            {investigation.reasoning && (
              <div className="analysis-block">
                <div className="analysis-label">
                  REASONING
                </div>

                <p>{investigation.reasoning}</p>
              </div>
            )}

            <div className="recommendation-box">
              <span>RECOMMENDED ACTION</span>

              <strong>
                {investigation.recommendation ||
                  investigation.agent_analysis
                    ?.recommended_action ||
                  'Review manually'}
              </strong>
            </div>

            <div className="ai-metrics">
              <div>
                <span>Confidence</span>
                <strong>
                  {formatPercent(
                    investigation.agent_analysis
                      ?.confidence,
                  )}
                </strong>
              </div>

              <div>
                <span>Risk score</span>
                <strong>
                  {formatPercent(
                    investigation.risk_score,
                  )}
                </strong>
              </div>

              <div>
                <span>Guardrail</span>
                <strong
                  className={
                    investigation.guardrail_passed
                      ? 'positive'
                      : 'negative'
                  }
                >
                  {investigation.guardrail_passed
                    ? 'PASSED'
                    : 'REVIEW'}
                </strong>
              </div>
            </div>

            {investigation.guardrail_reason && (
              <div className="guardrail-note">
                <span>▣</span>
                {investigation.guardrail_reason}
              </div>
            )}

            {investigation.requires_human_approval && (
              <div className="human-review">
                <div>
                  <strong>
                    Human approval required
                  </strong>

                  <p>
                    This action cannot be finalized
                    automatically.
                  </p>
                </div>

                <div className="review-actions">
                  <button
                    className="reject-button"
                    onClick={onReject}
                    disabled={reviewing}
                  >
                    {reviewing
                      ? 'Processing...'
                      : 'Reject'}
                  </button>

                  <button
                    className="approve-button"
                    onClick={onApprove}
                    disabled={reviewing}
                  >
                    {reviewing
                      ? 'Processing...'
                      : 'Approve'}
                  </button>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </aside>
  )
}

function formatPercent(
  value: string | number | null | undefined,
): string {
  if (value === null || value === undefined) {
    return '—'
  }

  const number = Number(value)

  if (Number.isNaN(number)) {
    return String(value)
  }

  return `${Math.round(number * 100)}%`
}

/* =====================================================
   TRANSACTIONS
===================================================== */

function TransactionsPage({
  transactions,
  search,
  setSearch,
}: {
  transactions: Transaction[]
  search: string
  setSearch: (value: string) => void
}) {
  const filtered = transactions.filter((tx) => {
    const query = search.toLowerCase()

    if (!query) return true

    return (
      tx.transaction_id
        .toLowerCase()
        .includes(query) ||
      String(tx.merchant_id ?? '')
        .toLowerCase()
        .includes(query) ||
      String(tx.customer_id ?? '')
        .toLowerCase()
        .includes(query) ||
      String(tx.status ?? '')
        .toLowerCase()
        .includes(query)
    )
  })

  return (
    <div className="page">
      <div className="page-heading">
        <div>
          <h2>Transactions</h2>
          <p>
            Source transactions used by the
            reconciliation engine.
          </p>
        </div>

        <div className="queue-summary">
          <span>{transactions.length}</span>
          transactions
        </div>
      </div>

      <div className="filter-bar">
        <div className="search-box wide">
          <span>⌕</span>

          <input
            value={search}
            onChange={(event) =>
              setSearch(event.target.value)
            }
            placeholder="Search transaction, merchant, customer..."
          />
        </div>
      </div>

      <section className="panel table-panel">
        {filtered.length === 0 ? (
          <EmptyState
            title="No transactions found"
            text="Try a different search."
          />
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Transaction</th>
                  <th>Merchant</th>
                  <th>Customer</th>
                  <th>Amount</th>
                  <th>Status</th>
                  <th>Date</th>
                </tr>
              </thead>

              <tbody>
                {filtered.map((tx) => (
                  <tr key={tx.transaction_id}>
                    <td>
                      <code>
                        {shortId(tx.transaction_id)}
                      </code>
                    </td>

                    <td>
                      {String(tx.merchant_id ?? '—')}
                    </td>

                    <td>
                      {String(tx.customer_id ?? '—')}
                    </td>

                    <td className="amount">
                      {formatMoney(tx.amount)}
                    </td>

                    <td>
                      <StatusBadge
                        value={String(
                          tx.status ?? 'UNKNOWN',
                        )}
                        type="status"
                      />
                    </td>

                    <td>
                      {formatDate(
                        tx.transaction_date,
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  )
}

/* =====================================================
   RECONCILIATIONS
===================================================== */

function ReconciliationsPage({
  reconciliations,
  transactions,
}: {
  reconciliations: Reconciliation[]
  transactions: Transaction[]
}) {
  return (
    <div className="page">
      <div className="page-heading">
        <div>
          <h2>Reconciliations</h2>
          <p>
            Compare payment, settlement and invoice
            records.
          </p>
        </div>

        <div className="queue-summary">
          <span>{reconciliations.length}</span>
          records
        </div>
      </div>

      <section className="panel table-panel">
        <ReconciliationTable
          reconciliations={reconciliations}
          transactions={transactions}
        />
      </section>
    </div>
  )
}

function ReconciliationTable({
  reconciliations,
  transactions,
}: {
  reconciliations: Reconciliation[]
  transactions: Transaction[]
}) {
  if (reconciliations.length === 0) {
    return (
      <EmptyState
        title="No reconciliation records"
        text="Run reconciliation to generate results."
      />
    )
  }

  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Transaction</th>
            <th>Payment</th>
            <th>Settlement</th>
            <th>Invoice</th>
            <th>Difference</th>
            <th>Status</th>
          </tr>
        </thead>

        <tbody>
          {reconciliations.map((record, index) => {
            const transactionId =
              typeof record.transaction_id === 'string'
                ? record.transaction_id
                : undefined

            const status =
              record.status ??
              record.reconciliation_status ??
              'UNKNOWN'

            return (
              <tr
                key={
                  record.id ||
                  record.reconciliation_id ||
                  `${transactionId}-${index}`
                }
              >
                <td>
                  <div className="primary-cell">
                    <strong>
                      {getTransactionLabel(
                        transactionId,
                        transactions,
                      )}
                    </strong>

                    <span>
                      {shortId(transactionId)}
                    </span>
                  </div>
                </td>

                <td>
                  {formatMoney(record.payment_amount)}
                </td>

                <td>
                  {formatMoney(
                    record.settlement_amount,
                  )}
                </td>

                <td>
                  {formatMoney(record.invoice_amount)}
                </td>

                <td
                  className={
                    Number(
                      record.difference_amount,
                    ) !== 0
                      ? 'danger-text'
                      : ''
                  }
                >
                  {formatMoney(
                    record.difference_amount,
                  )}
                </td>

                <td>
                  <StatusBadge
                    value={String(status)}
                    type="status"
                  />
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}

/* =====================================================
   SMALL COMPONENTS
===================================================== */

function StatusBadge({
  value,
  type,
}: {
  value: string
  type: 'status' | 'severity'
}) {
  const label = value.replaceAll('_', ' ')

  return (
    <span
      className={`status-badge ${type} ${statusClass(
        value,
      )}`}
    >
      <span className="badge-dot" />
      {label}
    </span>
  )
}

function ValueBox({
  label,
  value,
  danger = false,
}: {
  label: string
  value: string | null
  danger?: boolean
}) {
  return (
    <div className={`value-box ${danger ? 'danger' : ''}`}>
      <span>{label}</span>
      <strong>{value ?? '—'}</strong>
    </div>
  )
}

function InfoLine({
  label,
  value,
}: {
  label: string
  value: string
}) {
  return (
    <div className="info-line">
      <span>{label}</span>
      <code>{shortId(value)}</code>
    </div>
  )
}

function HealthRow({
  label,
  status,
  warning = false,
}: {
  label: string
  status: string
  warning?: boolean
}) {
  return (
    <div className="health-row">
      <div className="health-label">
        <span
          className={`health-dot ${
            warning ? 'warning' : ''
          }`}
        />
        {label}
      </div>

      <strong>{status}</strong>
    </div>
  )
}

function LoadingState() {
  return (
    <div className="loading-state">
      <div className="big-spinner" />
      <h3>Loading finance data</h3>
      <p>
        Connecting to the reconciliation platform...
      </p>
    </div>
  )
}

function EmptyState({
  title,
  text,
}: {
  title: string
  text: string
}) {
  return (
    <div className="empty-state">
      <div className="empty-icon">✓</div>
      <strong>{title}</strong>
      <p>{text}</p>
    </div>
  )
}

function severityWeight(
  severity: string,
): number {
  switch (severity) {
    case 'CRITICAL':
      return 4
    case 'HIGH':
      return 3
    case 'MEDIUM':
      return 2
    case 'LOW':
      return 1
    default:
      return 0
  }
}

export default App
