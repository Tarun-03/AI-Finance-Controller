export type ExceptionStatus =
  | 'OPEN'
  | 'INVESTIGATING'
  | 'RESOLVED'
  | 'ESCALATED'
  | 'REJECTED'

export type ExceptionType =
  | 'AMOUNT_MISMATCH'
  | 'FEE_MISMATCH'
  | 'STATUS_MISMATCH'
  | 'MISSING_PAYMENT'
  | 'MISSING_SETTLEMENT'
  | 'MISSING_INVOICE'

export type ExceptionSeverity =
  | 'LOW'
  | 'MEDIUM'
  | 'HIGH'
  | 'CRITICAL'

export interface ExceptionRecord {
  id: string
  reconciliation_id: string
  transaction_id: string

  exception_type: ExceptionType
  severity: ExceptionSeverity

  description: string

  expected_value: string | null
  actual_value: string | null
  difference: string | null

  status: ExceptionStatus

  agent_decision: string | null
  agent_confidence: string | null
  assigned_to: string | null
}

export interface AgentAnalysis {
  analysis: string
  recommended_action: string
  confidence: string
}

export interface InvestigationResult {
  exception_id: string
  transaction_id: string | null
  transaction_reference: string | null

  exception_type: string | null
  severity: string | null

  expected_value: string | null
  actual_value: string | null
  difference: string | null

  risk_score: string | null

  recommendation: string | null
  reasoning: string | null

  agent_analysis: AgentAnalysis | null

  guardrail_passed: boolean | null
  guardrail_reason: string | null

  requires_human_approval: boolean
  final_action: string | null

  error: string | null
}

export interface HumanDecisionResponse {
  exception_id: string
  status: string
  decision: string
  reason: string | null
}
