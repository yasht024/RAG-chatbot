# Mutual Fund FAQ Assistant: Product & Performance Improvements

As a Product Manager, looking at the initial v1 release of the Mutual Fund FAQ Assistant, here are strategic areas we can improve across Performance, User Experience, Data Freshness, and Analytics to elevate the product from a basic RAG tool to a robust, highly-engaging user feature.

## 1. Performance & Latency Optimizations ⚡

Currently, running a full RAG pipeline (Embedding -> Vector Search -> LLM Generation) for every query can be slow and expensive.

- **Semantic Caching (Fast Path):** Implement a semantic cache (e.g., Redis with vector search). If a user asks "What is the exit load for HDFC Mid Cap?" and another user recently asked a semantically identical question, serve the cached answer immediately. This reduces LLM costs and drops latency to milliseconds.
- **Hybrid Architecture (Structured + Unstructured):** Highly objective facts (Expense Ratio, Minimum SIP, NAV) shouldn't require an LLM to read a document chunk every time. We should extract these into a structured database during ingestion. Route objective queries to the database (0-shot retrieval) and use RAG only for complex unstructured queries (e.g., "What is the investment objective?").
- **Streaming UI:** Stream the LLM response token-by-token in the UI. Even if the total generation takes 3 seconds, getting the first word on screen in 400ms drastically improves perceived performance.

## 2. User Experience & Usability (Product Perspective) 🎯

The current interface relies heavily on the user knowing what to ask. We need to guide them to successful interactions.

- **Predictive Auto-complete & Prompts:** As users type, suggest supported factual queries. This subtly trains the user on what the bot *can* answer, reducing the friction of hitting the "no advice" guardrails.
- **Contextual Follow-up Chips:** After answering a question about "HDFC Flexi Cap Fund", provide 1-click follow-up chips like `[View Exit Load]`, `[View Fund Manager]`, or `[Download Factsheet]`. This turns a single Q&A interaction into an exploratory session.
- **Factual Comparison Tables:** While we explicitly *refuse* performance comparisons and rankings, we should allow **objective attribute comparisons**. E.g., "Compare the exit loads of HDFC Mid Cap and HDFC Small Cap." The bot should output a clean, markdown table of facts without offering an opinion.
- **Graceful "Out-of-Scope" Handoffs:** When a user asks an advisory question ("Should I buy this?"), don't just hit a hard wall. Provide a polite refusal but immediately pivot to utility: *"I can't give investment advice, but I can show you the fund's **Investment Objective** or **Riskometer** to help you decide. Which would you like?"*

## 3. Data Freshness & Integrity 🔄

Trust is the core metric for this product. If a fact is stale, user trust evaporates.

- **Event-Driven Ingestion:** Move away from batch cron-jobs. Set up monitors on HDFC/AMFI sitemaps or RSS feeds to trigger a re-index the moment a new addendum or factsheet is published.
- **Confidence Scoring & Conflict Resolution:** If the LLM notices a conflict between the AMC scheme page and the latest AMFI data, it shouldn't just guess. It should transparently surface both: *"According to the AMC page it is X, but the latest AMFI data from [Date] states Y."*
- **Source Highlighting:** Instead of just providing a source link at the bottom, eventually allow users to click a button that opens a PDF viewer side-by-side, highlighting the exact sentence the LLM extracted the fact from.

## 4. Analytics & Growth Metrics 📈

To prioritize Phase 2, we need to know what users actually want.

- **"Missed Intent" Tracking:** Log every query that results in an "Unsupported" or "Out of Scope" response. If 30% of users are asking about SIP cancellation processes, we know exactly what documents to add to the corpus next.
- **Advisory Funnel Analysis:** Track how often users trigger the advisory guardrail. If this number is too high, our UI onboarding needs to better explain the "Facts-Only" nature of the bot before they type.
- **User Feedback Loop:** Add simple 👍 / 👎 buttons on every response. Any thumbs-down should flag the query and retrieved context for manual review by the product team to catch hallucination or poor chunking.
