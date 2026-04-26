export type Verdict = 'SUPPORTED' | 'CONTRADICTED' | 'INSUFFICIENT'

export interface Evidence {
  quote: string
  citation: string
}

export interface ClassifiedStatement {
  verdict: Verdict
  rationale: string
  evidence: Evidence[]
  confidence: number
}

export interface Speaker {
  name: string
  surname: string
  party: string | null
  photo_url: string | null
}

export interface ClassifiedStatementWithContext extends ClassifiedStatement {
  speaker: Speaker
  statement: string
}

export interface SpeakerStats {
  speaker: Speaker
  total_statements: number
  supported: ClassifiedStatementWithContext[]
  contradicted: ClassifiedStatementWithContext[]
  insufficient: ClassifiedStatementWithContext[]
}

export interface StatsResult {
  total_speakers: number
  total_statements: number
  speakers_stats: SpeakerStats[]
}

export interface ClassifyStatementResult {
  type: 'STATEMENT_CLASSIFICATION'
  classified_statements: ClassifiedStatement[]
}

export type JobStatus = 'PENDING' | 'COMPLETED' | 'FAILED'

export interface JobPollResult {
  status: JobStatus
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  result?: any
  error?: string
}
