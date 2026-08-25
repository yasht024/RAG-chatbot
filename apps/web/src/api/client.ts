/**
 * This is an auto-generated client stub for the Mutual Fund FAQ Assistant API.
 * Generated for Phase 2B frontend integration.
 */

export type TerminalState = 
  | "FACTUAL_ANSWER"
  | "POLICY_REFUSAL"
  | "INSUFFICIENT_EVIDENCE"
  | "AMBIGUOUS_SCHEME"
  | "SOURCE_CONFLICT"
  | "SENSITIVE_DATA_WARNING"
  | "TEMPORARILY_UNAVAILABLE";

export interface Message {
  role: string;
  content: string;
}

export interface QueryRequest {
  query: string;
  conversation_id: string;
  history?: Message[];
}

export interface FactualResponse {
  status: TerminalState;
  answer?: string;
  citation?: {
    url?: string;
    last_updated?: string;
  };
  error?: {
    reason?: string;
  };
  evidence_passage_ids?: string[];
}

export class AssistantClient {
  private baseUrl: string;

  constructor(baseUrl: string = import.meta.env.PROD ? "" : "http://localhost:8000") {
    this.baseUrl = baseUrl;
  }

  /**
   * Submits a factual question to the RAG backend.
   * @param request The query payload
   * @param idempotencyKey Optional key to safely retry requests without double-processing
   */
  async askQuestion(request: QueryRequest, idempotencyKey?: string): Promise<FactualResponse> {
    const headers: Record<string, string> = {
      "Content-Type": "application/json"
    };
    
    if (idempotencyKey) {
      headers["Idempotency-Key"] = idempotencyKey;
    }

    const response = await fetch(`${this.baseUrl}/v1/questions`, {
      method: "POST",
      headers,
      body: JSON.stringify(request)
    });

    if (!response.ok) {
      if (response.status === 429) {
        throw new Error("Too Many Requests (Rate Limited)");
      }
      throw new Error(`HTTP Error: ${response.status}`);
    }

    return await response.json() as FactualResponse;
  }
}
