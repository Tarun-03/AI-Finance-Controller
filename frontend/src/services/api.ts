import type {
  FinanceException,
  HumanDecisionResponse,
  InvestigationResult,
  Reconciliation,
  ReconciliationRunResult,
  Transaction,
} from '../types/finance'

const API_BASE = 'http://localhost:8000/api/v1'

async function request<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    },
  })

  const text = await response.text()

  let data: unknown = null

  if (text) {
    try {
      data = JSON.parse(text)
    } catch {
      data = text
    }
  }

  if (!response.ok) {
    const message =
      typeof data === 'object' &&
      data !== null &&
      'detail' in data
        ? String((data as { detail: unknown }).detail)
        : `Request failed with status ${response.status}`

    throw new Error(message)
  }

  return data as T
}

/* ---------------- HEALTH ---------------- */

export async function healthCheck(): Promise<{ status: string }> {
  const response = await fetch('http://localhost:8000/health')

  if (!response.ok) {
    throw new Error('Backend is offline')
  }

  return response.json() as Promise<{ status: string }>
}

/* ---------------- TRANSACTIONS ---------------- */

export async function getTransactions(): Promise<Transaction[]> {
  return request<Transaction[]>('/transactions')
}

export async function getTransaction(
  transactionId: string,
): Promise<Transaction> {
  return request<Transaction>(
    `/transactions/${encodeURIComponent(transactionId)}`,
  )
}

/* ---------------- RECONCILIATIONS ---------------- */

export async function getReconciliations(): Promise<Reconciliation[]> {
  return request<Reconciliation[]>('/reconciliations')
}

export async function getReconciliation(
  reconciliationId: string,
): Promise<Reconciliation> {
  return request<Reconciliation>(
    `/reconciliations/${encodeURIComponent(reconciliationId)}`,
  )
}

export async function runReconciliation(): Promise<ReconciliationRunResult> {
  return request<ReconciliationRunResult>(
    '/reconciliations/run',
    {
      method: 'POST',
    },
  )
}

/* ---------------- EXCEPTIONS ---------------- */

export async function getExceptions(): Promise<FinanceException[]> {
  return request<FinanceException[]>('/exceptions')
}

export async function getOpenExceptions(): Promise<FinanceException[]> {
  return request<FinanceException[]>('/exceptions/open')
}

export async function getException(
  exceptionId: string,
): Promise<FinanceException> {
  return request<FinanceException>(
    `/exceptions/${encodeURIComponent(exceptionId)}`,
  )
}

/* ---------------- AI AGENT ---------------- */

export async function investigateException(
  exceptionId: string,
): Promise<InvestigationResult> {
  return request<InvestigationResult>(
    `/agent/exceptions/${encodeURIComponent(exceptionId)}/investigate`,
    {
      method: 'POST',
    },
  )
}

/* ---------------- HUMAN REVIEW ---------------- */

export async function approveException(
  exceptionId: string,
  reason?: string,
): Promise<HumanDecisionResponse> {
  return request<HumanDecisionResponse>(
    `/exceptions/${encodeURIComponent(exceptionId)}/approve`,
    {
      method: 'POST',
      body: JSON.stringify({
        reason: reason || null,
      }),
    },
  )
}

export async function rejectException(
  exceptionId: string,
  reason?: string,
): Promise<HumanDecisionResponse> {
  return request<HumanDecisionResponse>(
    `/exceptions/${encodeURIComponent(exceptionId)}/reject`,
    {
      method: 'POST',
      body: JSON.stringify({
        reason: reason || null,
      }),
    },
  )
}
