export type Money = string | number | null | undefined

export type ExceptionStatus =
  | 'OPEN'
  | 'INVESTIGATING'
  | 'RESOLVED'
  | 'ESCALATED'
  | 'REJECTED'

export type ExceptionSeverity =
  | 'LOW'
  | 'MEDIUM'
  | 'HIGH'
  | 'CRITICAL'

export type ExceptionType =
  | 'AMOUNT_MISMATCH'
  | 'MISSING_PAYMENT'
  | 'MISSING_SETTLEMENT'
  | 'MISSING_INVOICE'
  | 'FEE_MISMATCH'
  | 'TAX_MISMATCH'
  | 'STATUS_MISMATCH'
  | 'UNKNOWN'
  | string

export interface Transaction {
  transaction_id: string
  merchant_id?: string | null
  customer_id?: string | null
  transaction_reference?: string | null
  transaction_type?: string | null
  amount?: Money
  currency?: string | null
  status?: string | null
  transaction_date?: string | null
  created_at?: string | null
  updated_at?: string | null

  [key: string]: unknown
}

export interface Reconciliation {
  id?: string
  reconciliation_id?: string
  transaction_id?: string
  payment_id?: string | null
  settlement_id?: string | null
  invoice_id?: string | null

  payment_amount?: Money
  settlement_amount?: Money
  invoice_amount?: Money
  difference_amount?: Money

  status?: string | null
  reconciliation_status?: string | null

  payment_status?: string | null
  settlement_status?: string | null
  invoice_status?: string | null

  confidence_score?: Money
  created_at?: string | null
  completed_at?: string | null

  [key: string]: unknown
}

export interface FinanceException {
  id: string
  reconciliation_id: string
  transaction_id: string

  exception_type: ExceptionType
  severity: ExceptionSeverity

  description: string

  expected_value: Money
  actual_value: Money
  difference: Money

  status: ExceptionStatus

  agent_decision?: string | null
  agent_confidence?: Money
  assigned_to?: string | null
}

export interface AgentAnalysis {
  analysis: string
  recommended_action: string
  confidence: Money
}

export interface InvestigationResult {
  exception_id: string

  transaction_id?: string | null
  transaction_reference?: string | null

  exception_type?: string | null
  severity?: string | null

  expected_value?: Money
  actual_value?: Money
  difference?: Money

  risk_score?: Money

  recommendation?: string | null
  reasoning?: string | null

  agent_analysis?: AgentAnalysis | null

  guardrail_passed?: boolean | null
  guardrail_reason?: string | null

  requires_human_approval?: boolean

  final_action?: string | null

  error?: string | null
}

export interface HumanDecisionResponse {
  exception_id: string
  status: string
  decision: string
  reason?: string | null
}

export interface ReconciliationRunResult {
  matched?: number
  mismatched?: number
  total_exceptions?: number
  [key: string]: unknown
}
