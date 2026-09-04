import type {
  ExceptionRecord,
  HumanDecisionResponse,
  InvestigationResult,
} from '../types/finance'

const API_BASE = 'http://localhost:8000/api/v1'

async function request<T>(
  endpoint: string,
  options?: RequestInit,
): Promise<T> {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(options?.headers || {}),
    },
    ...options,
  })

  if (!response.ok) {
    let message = `Request failed: ${response.status}`

    try {
      const body = await response.json()
      if (body.detail) {
        message = body.detail
      }
    } catch {
      // Keep default error message.
    }

    throw new Error(message)
  }

  return response.json()
}

export async function getExceptions(): Promise<ExceptionRecord[]> {
  return request<ExceptionRecord[]>('/exceptions')
}

export async function getException(
  exceptionId: string,
): Promise<ExceptionRecord> {
  return request<ExceptionRecord>(`/exceptions/${exceptionId}`)
}

export async function investigateException(
  exceptionId: string,
): Promise<InvestigationResult> {
  return request<InvestigationResult>(
    `/agent/exceptions/${exceptionId}/investigate`,
    {
      method: 'POST',
    },
  )
}

export async function approveException(
  exceptionId: string,
  reason: string,
): Promise<HumanDecisionResponse> {
  return request<HumanDecisionResponse>(
    `/exceptions/${exceptionId}/approve`,
    {
      method: 'POST',
      body: JSON.stringify({ reason }),
    },
  )
}

export async function rejectException(
  exceptionId: string,
  reason: string,
): Promise<HumanDecisionResponse> {
  return request<HumanDecisionResponse>(
    `/exceptions/${exceptionId}/reject`,
    {
      method: 'POST',
      body: JSON.stringify({ reason }),
    },
  )
}

export async function getHealth(): Promise<{ status: string }> {
  return fetch('http://localhost:8000/health').then(async (response) => {
    if (!response.ok) {
      throw new Error('Backend unavailable')
    }

    return response.json()
  })
}
