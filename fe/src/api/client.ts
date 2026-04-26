import type { JobPollResult } from '../types'

const API_BASE = import.meta.env.VITE_API_URL ?? ''
const API_KEY  = import.meta.env.VITE_API_KEY  ?? ''

function authUrl(path: string) {
  return `${API_BASE}${path}?x-api-key=${encodeURIComponent(API_KEY)}`
}

// ── Conversation verification ─────────────────────────────────────────────────

export interface Speaker {
  name: string
  surname: string
  party: string | null
}

export async function startVerification(
  text: string,
  collectionName: string,
  year: number,
  speakers: Speaker[],
  mode: 'sync' | 'async' = 'async',
): Promise<string> {
  const jobId = crypto.randomUUID()
  const res = await fetch(authUrl('/api/v1/jobs/verify_political_statements'), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      job_id: jobId,
      payload: {
        text,
        collection_name: collectionName,
        year,
        mode,
        speaker_list: speakers.length > 0 ? speakers : null,
      },
    }),
  })
  if (!res.ok) {
    const body = await res.json().catch(() => ({})) as { detail?: string }
    throw new Error(body.detail ?? `HTTP ${res.status}`)
  }
  return jobId
}

// ── Single statement classification ──────────────────────────────────────────

export async function startSingleStatement(
  query: string,
  collectionName: string,
  party: string | null,
  year: number,
): Promise<string> {
  const jobId = crypto.randomUUID()
  const res = await fetch(authUrl('/api/v1/jobs/classify_statements'), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      job_id: jobId,
      payload: {
        statements: [{ query, collection_name: collectionName, party, year }],
      },
    }),
  })
  if (!res.ok) {
    const body = await res.json().catch(() => ({})) as { detail?: string }
    throw new Error(body.detail ?? `HTTP ${res.status}`)
  }
  return jobId
}

// ── Add document ──────────────────────────────────────────────────────────────

export async function startAddDocument(
  url: string,
  name: string,
  collectionName: string,
  party: string | null,
  year: number,
): Promise<string> {
  const jobId = crypto.randomUUID()
  const res = await fetch(authUrl('/api/v1/jobs/add_document'), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      job_id: jobId,
      payload: {
        documents: [{ url, name, collection_name: collectionName, party, year }],
      },
    }),
  })
  if (!res.ok) {
    const body = await res.json().catch(() => ({})) as { detail?: string }
    throw new Error(body.detail ?? `HTTP ${res.status}`)
  }
  return jobId
}

// ── Speakers ──────────────────────────────────────────────────────────────────

export interface SpeakerInfo { name: string; party: string }

export async function fetchSpeakers(): Promise<SpeakerInfo[]> {
  const res = await fetch(authUrl('/api/v1/speakers'))
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  const data = await res.json() as { speakers: SpeakerInfo[] }
  return data.speakers
}

// ── Collections ───────────────────────────────────────────────────────────────

export interface PartyStats { party: string; chunk_count: number }
export interface CollectionStats { collection_name: string; parties: PartyStats[] }

export async function fetchCollections(): Promise<CollectionStats[]> {
  const res = await fetch(authUrl('/api/v1/collections'))
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  const data = await res.json() as { collections: CollectionStats[] }
  return data.collections
}

export async function deleteParty(collectionName: string, party: string): Promise<void> {
  const res = await fetch(authUrl(`/api/v1/collections/${encodeURIComponent(collectionName)}/parties/${encodeURIComponent(party)}`), {
    method: 'DELETE',
  })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
}

// ── Job polling ───────────────────────────────────────────────────────────────

export async function pollJobResult(jobId: string): Promise<JobPollResult> {
  const res = await fetch(authUrl(`/api/v1/jobs/result/${jobId}`))
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return res.json() as Promise<JobPollResult>
}
