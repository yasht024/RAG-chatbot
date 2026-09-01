# AI PM Interview Script: Mutual Fund FAQ Assistant

This script is tailored specifically to your project: the **Mutual Fund FAQ Assistant**. Use this to structure your narrative around building a production-ready, compliance-first AI product.

## 1. Introduction & Project Narrative
**Interviewer:** "Tell me about a recent AI product you managed."
**Your Strategy:**
- "I recently led the development of a **Mutual Fund FAQ Assistant**, a production-ready, facts-only AI assistant for HDFC Mutual Fund schemes."
- "The core problem we solved was providing users with instant, accurate, and objective information about financial products. However, the biggest challenge—and where I focused my product strategy—was strict adherence to compliance constraints. We had to build a system that strictly refuses advice, recommendations, predictions, and prohibited performance requests."
- "My focus was on balancing AI capabilities (using RAG for accurate retrieval) with rigid safety guardrails and setting the right user expectations through UX."

---

## 2. Technical Strategy: Why RAG?
**Interviewer:** "What was the technical approach for this product, and why did you choose it?"
**Your Answer:**
- **Core Architecture:** "We utilized a **Retrieval-Augmented Generation (RAG)** architecture. In the financial sector, LLM hallucination is a catastrophic risk. RAG was non-negotiable."
- **Build vs. Buy / Fine-tuning:** "We chose RAG over fine-tuning because fine-tuning teaches an LLM a *style*, but it doesn't prevent it from confidently making up facts. RAG grounds the LLM's answers strictly in our approved, curated data source—specifically, current approved Groww evidence and our Scheme Catalog."
- **The LLM's Role:** "We treat the LLM purely as a reasoning and natural language generation engine. It is *not* a knowledge base. If the answer isn't in our provided context window, the system is instructed to refuse the answer."

### The Tech Stack (What we used)
Be prepared to discuss the specific technologies used in this project if the interviewer asks about implementation details:

| Component | Technology / Model Used | Why we chose it (PM Perspective) |
| :--- | :--- | :--- |
| **Generation LLM** | **Groq API (Llama-3.3-70b-versatile)** | Extremely low latency (Groq's LPU infrastructure) offsets the time added by our multiple compliance guardrail checks. Llama 3 70B is highly capable for factual synthesis. |
| **Embedding Model** | **BAAI/bge-large-en-v1.5 (1024-dim)** | High-performance open-source embedding model that creates dense vector representations of our financial documents, allowing for highly accurate semantic search. |
| **Search Strategy** | **Hybrid Search (BM25 + Vector + RRF)** | Pure vector search misses exact terms (like specific percentages or fund names). We combined keyword (BM25) and semantic vector search, fusing results with Reciprocal Rank Fusion (RRF) for maximum precision. |
| **Database** | **PostgreSQL with `pgvector`** | Allowed us to keep strict relational metadata (Scheme Catalog, source approval status) and vector embeddings in the same robust database, eliminating sync issues between a separate Vector DB and SQL DB. |
| **Backend Framework** | **FastAPI (Python)** | High performance, async support, and native Pydantic integration for strict data validation (crucial for our compliance-first approach). |
| **Resilience & Safety** | **Pydantic, Circuit Breakers, Token Limiters** | Pydantic ensures the LLM output rigidly matches expected JSON schemas. Circuit breakers and token limiters prevent cascading failures and manage API costs/quotas. |
| **Frontend / Web UI** | **React / Node.js** | Provided a seamless, responsive chat interface to clearly render the required disclaimers, facts, and source citations to the user. |

---

## 3. The Product Lifecycle (How you built it)
Be prepared to walk through how you built this from 0 to 1.

1. **Problem Definition & Compliance First:** "Before writing any code, we defined the hard boundaries. The assistant must be 'facts-only'. I worked on defining the scope: objective facts are in; advice and predictions are strictly out."
2. **Data Strategy (The Ground Truth):** "The AI is only as good as its data. We established a strict 'Sources Policy' and built a structured 'Scheme Catalog'. This curated data is our moat and our safety net."
3. **Prompt Engineering & Guardrails:** "A massive part of the product work was designing the system instructions. We built strict guardrails to categorize user intents and gracefully refuse out-of-scope questions (e.g., 'What should I invest in?') instead of letting the AI guess."
4. **Evaluation:** 
   - *Offline:* "We tested against a golden dataset of questions. Our primary metrics were a 0% hallucination rate on factual questions and a 100% refusal rate on 'advice' or 'prediction' questions."
5. **UX Design:** "We designed the UI to clearly set expectations. The assistant must transparently state it is an AI and only provides factual information, preventing users from relying on it for financial planning."

---

## 4. Key PM Decisions & Trade-offs
Highlight these in your interview to show deep PM thinking.

- **Precision over Recall:** "In our retrieval system, we prioritized precision. It is much better for the assistant to say 'I don't have that information in my approved sources' than to retrieve slightly irrelevant data and risk hallucinating an incorrect financial fact."
- **Latency vs. Safety:** "Implementing multiple layers of safety checks (e.g., intent classification to block prohibited performance requests) adds latency. I had to balance the UX of a fast chat response with the necessity of 100% safe answers."
- **Designing the 'I Don't Know' Experience:** "A major PM challenge was the refusal UX. When a user asks for advice, a dead-end 'I can't answer that' is a bad experience. We designed the refusals to guide users back to factual topics we *can* help with."

---

## 5. Practice Interview Questions for this Project
Use these to run mock interviews with yourself:

- **Safety/Compliance:** "A user asks the assistant, *'Which HDFC fund will give me the best return next year?'* How exactly does your system handle this, and how did you measure its success?"
- **Architecture:** "Why did you choose RAG instead of just prompting a very smart model like GPT-4 with a general instruction to be careful?"
- **Metrics:** "What are your primary online success metrics for the Mutual Fund FAQ Assistant? How do you know if it's actually providing value to users?"
- **Roadmap:** "Now that the facts-only assistant is live, what is your roadmap for v2? How do you safely expand its capabilities without crossing into financial advice?"

---

## 6. Questions to Ask the Interviewer (If they are in Fintech/AI)
- "How does your product team handle the tension between building engaging, helpful conversational AI and adhering to strict financial compliance?"
- "What is your approach to maintaining the 'ground truth' data as financial products, interest rates, and regulations constantly change?"
