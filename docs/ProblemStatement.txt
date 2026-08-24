# Mutual Fund FAQ Assistant (Facts-Only Q&A)

## Document Control

| Field | Value |
| --- | --- |
| Project | Mutual Fund FAQ Assistant |
| Initial AMC | HDFC Mutual Fund / HDFC Asset Management Company (HDFC AMC) |
| Product context | Groww mutual-fund discovery experience |
| Document type | Problem statement and product requirements context |
| Status | Initial project definition |
| Source date | 23 August 2026 |

## Summary

Build a lightweight Retrieval-Augmented Generation (RAG) assistant that answers objective, verifiable questions about a defined set of 35 HDFC Mutual Fund schemes. The assistant must ground every factual answer in current official public information from HDFC AMC, AMFI, or SEBI; respond concisely with exactly one source link; and refuse investment advice, recommendations, predictions, rankings, and performance-based comparisons.

Groww is the reference product context and provides the scheme-discovery links listed in this document. Groww and other third-party sites must not be used as factual knowledge sources.

## Problem Statement

Retail investors and support or content teams frequently need simple facts about mutual fund schemes, such as an expense ratio, exit load, minimum investment, benchmark, riskometer, lock-in period, or current fund manager. Finding the latest value often requires navigating multiple scheme pages, factsheets, Scheme Information Documents (SIDs), Key Information Memoranda (KIMs), notices, and regulatory resources.

The product must make those facts easier to retrieve without crossing into financial advice. It should prioritize accuracy and traceability over conversational breadth: when approved evidence is missing, ambiguous, stale, or conflicting, it must avoid inference and decline to provide an unsupported answer.

## Objective

Design and implement a facts-only RAG assistant that:

- Answers factual questions about mutual fund schemes.
- Uses a curated corpus of official public documents.
- Provides concise, source-backed responses.
- Supports the 35 HDFC Mutual Fund schemes defined below.
- Distinguishes scheme-level facts from AMC-level information.
- Prefers the latest applicable official source.
- Refuses investment-advisory, recommendation, ranking, and performance-comparison requests.
- Enforces citation, freshness, and response-format rules before returning an answer.

## Target Users

- Retail investors seeking factual information about mutual fund schemes.
- Customer support teams handling repetitive mutual-fund questions.
- Content teams that require verified scheme information.
- Users comparing objective product attributes without receiving investment advice.

## Goals

- Make official scheme facts quick and easy to find.
- Ground answers only in approved official evidence.
- Make each factual answer independently verifiable through one relevant source link.
- Prevent unsupported claims and accidental financial advice.
- Correctly identify and retrieve information for all 35 selected schemes.
- Keep the experience simple, transparent, and understandable.

## Non-Goals

The product will not:

- Recommend a mutual fund or tell a user whether to invest.
- Rank funds or identify a "best" fund.
- Predict future performance or returns.
- Compare, calculate, or rank funds based on performance.
- Calculate expected investment returns.
- Provide personalized asset-allocation or portfolio advice.
- Encourage a user to buy, sell, or hold a mutual fund.
- Execute transactions or access a user's investment account.
- Use Groww, blogs, influencers, or other aggregators as factual sources.
- Collect or process personal or transaction credentials.

## Initial Scheme Universe

The first release covers the following 35 HDFC Mutual Fund schemes. These Groww URLs are reference and product-context links only; they are not approved factual sources for retrieval or citation.

### Equity - Diversified

| # | Scheme | Groww reference |
| ---: | --- | --- |
| 1 | HDFC Mid Cap Fund - Direct Growth | [Reference](https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth) |
| 2 | HDFC Flexi Cap Fund - Direct Growth | [Reference](https://groww.in/mutual-funds/hdfc-equity-fund-direct-growth) |
| 3 | HDFC Small Cap Fund - Direct Growth | [Reference](https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth) |
| 4 | HDFC Large and Mid Cap Fund - Direct Growth | [Reference](https://groww.in/mutual-funds/hdfc-large-and-mid-cap-fund-direct-growth) |
| 5 | HDFC Large Cap Fund - Direct Growth | [Reference](https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth) |
| 6 | HDFC Multi Cap Fund - Direct Growth | [Reference](https://groww.in/nfo/hdfc-multi-cap-fund-direct-growth) |
| 7 | HDFC Focused Fund - Direct Growth | [Reference](https://groww.in/mutual-funds/hdfc-focused-fund-direct-growth) |
| 8 | HDFC Value Fund - Direct Growth | [Reference](https://groww.in/mutual-funds/hdfc-value-fund-direct-growth) |
| 9 | HDFC ELSS Tax Saver Fund - Direct Growth | [Reference](https://groww.in/mutual-funds/hdfc-elss-tax-saver-fund-direct-plan-growth) |
| 10 | HDFC MNC Fund - Direct Growth | [Reference](https://groww.in/mutual-funds/hdfc-mnc-fund-direct-growth) |

### Thematic / Sectoral Equity

| # | Scheme | Groww reference |
| ---: | --- | --- |
| 11 | HDFC Business Cycle Fund - Direct Growth | [Reference](https://groww.in/nfo/hdfc-business-cycle-fund-direct-growth) |
| 12 | HDFC Defence Fund - Direct Growth | [Reference](https://groww.in/nfo/hdfc-defence-fund-direct-growth) |
| 13 | HDFC Consumption Fund - Direct Growth | [Reference](https://groww.in/mutual-funds/hdfc-consumption-fund-direct-growth) |
| 14 | HDFC Transportation and Logistics Fund - Direct Growth | [Reference](https://groww.in/mutual-funds/hdfc-transportation-and-logistics-fund-direct-growth) |
| 15 | HDFC Technology Fund - Direct Growth | [Reference](https://groww.in/mutual-funds/hdfc-technology-fund-direct-growth) |
| 16 | HDFC Pharma and Healthcare Fund - Direct Growth | [Reference](https://groww.in/mutual-funds/hdfc-pharma-and-healthcare-fund-direct-growth) |
| 17 | HDFC Manufacturing Fund - Direct Growth | [Reference](https://groww.in/mutual-funds/hdfc-manufacturing-fund-direct-growth) |
| 18 | HDFC Infrastructure Fund - Direct Growth | [Reference](https://groww.in/mutual-funds/hdfc-infrastructure-fund-direct-growth) |
| 19 | HDFC Innovation Fund - Direct Growth | [Reference](https://groww.in/mutual-funds/hdfc-innovation-fund-direct-growth) |
| 20 | HDFC Children's Fund - Direct Growth | [Reference](https://groww.in/mutual-funds/hdfc-childrens-fund-direct-plan-growth) |

### Index / Passive Funds

| # | Scheme | Groww reference |
| ---: | --- | --- |
| 21 | HDFC NIFTY 50 Index Fund - Direct Growth | [Reference](https://groww.in/mutual-funds/hdfc-nifty-50-index-fund-direct-growth) |
| 22 | HDFC NIFTY Next 50 Index Fund - Direct Growth | [Reference](https://groww.in/mutual-funds/hdfc-nifty-next-50-index-fund-direct-growth) |
| 23 | HDFC NIFTY 100 Index Fund - Direct Growth | [Reference](https://groww.in/mutual-funds/hdfc-nifty-100-index-fund-direct-growth) |
| 24 | HDFC NIFTY 100 Equal Weight Index Fund - Direct Growth | [Reference](https://groww.in/mutual-funds/hdfc-nifty-100-equal-weight-index-fund-direct-growth) |
| 25 | HDFC NIFTY50 Equal Weight Index Fund - Direct Growth | [Reference](https://groww.in/mutual-funds/hdfc-nifty-50-equal-weight-index-fund-direct-growth) |
| 26 | HDFC NIFTY Midcap 150 Index Fund - Direct Growth | [Reference](https://groww.in/mutual-funds/hdfc-nifty-midcap-150-index-fund-direct-growth) |
| 27 | HDFC Nifty Smallcap 250 Index Fund - Direct Growth | [Reference](https://groww.in/mutual-funds/hdfc-nifty-smallcap-250-index-fund-direct-growth) |
| 28 | HDFC Nifty LargeMidcap 250 Index Fund - Direct Growth | [Reference](https://groww.in/mutual-funds/hdfc-nifty-largemidcap-250-index-fund-direct-growth) |
| 29 | HDFC NIFTY200 Momentum 30 Index Fund - Direct Growth | [Reference](https://groww.in/mutual-funds/hdfc-nifty200-momentum-30-index-fund-direct-growth) |
| 30 | HDFC NIFTY100 Low Volatility 30 Index Fund - Direct Growth | [Reference](https://groww.in/mutual-funds/hdfc-nifty100-low-volatility-30-index-fund-direct-growth) |
| 31 | HDFC Nifty100 Quality 30 Index Fund - Direct Growth | [Reference](https://groww.in/mutual-funds/hdfc-nifty100-quality-30-index-fund-direct-growth) |
| 32 | HDFC Nifty Top 20 Equal Weight Index Fund - Direct Growth | [Reference](https://groww.in/mutual-funds/hdfc-nifty-top-20-equal-weight-index-fund-direct-growth) |

### Hybrid / Multi-Asset

| # | Scheme | Groww reference |
| ---: | --- | --- |
| 33 | HDFC Balanced Advantage Fund - Direct Growth | [Reference](https://groww.in/mutual-funds/hdfc-balanced-advantage-fund-direct-growth) |
| 34 | HDFC Multi Asset Allocation Fund - Direct Growth | [Reference](https://groww.in/mutual-funds/hdfc-multi-asset-allocation-fund-direct-growth) |

### Gold / Commodity

| # | Scheme | Groww reference |
| ---: | --- | --- |
| 35 | HDFC Gold ETF Fund of Fund - Direct Growth | [Reference](https://groww.in/mutual-funds/hdfc-gold-etf-fund-of-fund-direct-plan-growth) |

## Supported Questions

The assistant should answer objective questions when the relevant value is explicitly supported by an approved source. Initial question types include:

- Expense ratio.
- Exit load.
- Minimum SIP amount.
- Minimum lump-sum investment.
- ELSS lock-in period.
- Riskometer classification.
- Benchmark index.
- Investment objective as stated in the scheme document.
- Current fund manager.
- Scheme inception or launch date.
- Available plans and options.
- Official factsheet location.
- Process for downloading account statements.
- Process for obtaining a capital-gains statement.
- A factual performance value explicitly stated in the latest approved official factsheet.

Example questions:

- "What is the expense ratio of HDFC Mid Cap Fund?"
- "What is the exit load?"
- "What is the minimum SIP amount?"
- "What is the ELSS lock-in period?"
- "What is the riskometer classification?"
- "What is the benchmark index?"
- "What is the investment objective stated in the scheme document?"
- "Who is the current fund manager?"
- "What is the minimum lump-sum investment?"
- "What is the scheme's inception date?"
- "What plans and options are available?"
- "How can I download my account statement?"
- "How can I obtain a capital-gains statement?"
- "Where can I download the official factsheet?"

## Source Policy

### Approved Sources

Primary sources:

- HDFC AMC official scheme pages.
- HDFC AMC Scheme Information Documents (SIDs).
- HDFC AMC Key Information Memoranda (KIMs).
- HDFC AMC monthly factsheets.
- HDFC AMC official notices and addendums.

Secondary regulatory sources:

- Association of Mutual Funds in India (AMFI).
- Securities and Exchange Board of India (SEBI).

### Source Priority

For scheme facts, use this default precedence when information conflicts:

1. Latest applicable official HDFC AMC document.
2. HDFC AMC official scheme page.
3. AMFI.
4. SEBI.

Regulatory disclosures take precedence when the fact or requirement is regulatory in nature.

### Prohibited Sources

- Groww scheme pages, except as scheme-identification and product-context references.
- Third-party blogs or articles.
- Aggregator websites.
- Financial influencers or social-media posts.
- Model memory or unsupported inference.

### Freshness and Evidence Rules

- Prefer the latest available applicable official document when multiple documents exist.
- Preserve each document's publication or effective date in metadata.
- Distinguish a scheme-level source from an AMC-level source.
- Do not infer a value that is absent from the retrieved evidence.
- Do not answer when evidence is insufficient, ambiguous, or cannot be validated.
- Treat historical documents as potentially superseded.

## Query Classification

Every query must be classified before retrieval and generation.

| Class | Meaning | Required behavior |
| --- | --- | --- |
| Factual | Requests an objective, verifiable scheme-level or AMC-level fact | Retrieve approved evidence and answer only when supported |
| Advisory | Requests a recommendation, opinion, or personalized decision | Refuse politely and state the facts-only boundary |
| Performance / comparison | Requests return calculations, rankings, performance comparisons, or a performance-based recommendation | Refuse; a single factual value may be answered only when explicitly present in an approved source |
| Unsupported / out of scope | Cannot be answered from the approved corpus or falls outside product scope | State that the available official evidence is insufficient or the request is out of scope |

## Functional Requirements

### Retrieval

- Retrieve relevant passages only from the approved HDFC AMC, AMFI, and SEBI corpus.
- Resolve scheme aliases and names to a canonical scheme record.
- Filter or rank evidence using scheme name, category, plan, option, document type, document date, source, and page number.
- Prefer the latest applicable evidence and account for notices or addendums that supersede older documents.
- Return enough provenance for the final answer to cite the specific official source.

### Context Building

- Select only passages relevant to the classified question.
- Keep source provenance attached to every selected passage.
- Avoid combining values from documents with incompatible dates or scopes.
- Pass uncertainty or conflicting-source information to the answer and compliance layers.

### Answer Generation

- State the requested factual value directly.
- Use only retrieved and validated context.
- Never fill gaps using model knowledge or inference.
- Distinguish facts about a scheme from general AMC procedures.
- Use plain, concise language.

### Compliance Validation

Before delivery, validate that the response:

- Contains no more than three answer sentences.
- Contains exactly one official source citation/link for a factual answer.
- Contains no recommendation, ranking, prediction, or unsupported claim.
- Includes the required last-updated footer.
- Refuses advisory and prohibited performance/comparison requests.
- Does not expose or request sensitive personal information.

## Response Contract

Every factual response must:

- Contain a maximum of three sentences.
- Contain exactly one source citation/link.
- Use plain and concise language.
- State the relevant factual value directly.
- End with `Last updated from sources: <date>`.

Example:

```text
The minimum SIP amount for HDFC Mid Cap Fund is INR 100.
Source: [Official HDFC AMC scheme source]
Last updated from sources: 23 August 2026
```

The last-updated date should represent the effective or publication date of the official evidence used, not merely the time at which the question was asked.

## Refusal Handling

The assistant must refuse questions such as:

- "Should I invest in this fund?"
- "Which HDFC fund is better?"
- "Which fund will give the highest return?"
- "Which fund should I buy?"
- "Is HDFC Mid Cap better than HDFC Flexi Cap?"
- "What is the best HDFC mutual fund?"

Refusals must be polite, clearly state the facts-only limitation, avoid implicit recommendations, and may provide one relevant official educational resource where appropriate.

Example:

```text
I can provide verified facts about HDFC mutual fund schemes, but I cannot recommend which fund you should invest in.
For general mutual-fund education, please refer to the official AMFI investor resources.
Last updated from sources: <date>
```

## Performance-Related Queries

The assistant must not calculate, rank, compare, or recommend funds based on performance. It must refuse requests such as:

- "Which fund has the highest return?"
- "Compare the five-year returns of these funds."
- "Which HDFC fund performed best?"
- "Which fund should I invest in based on returns?"

A request for a single factual performance figure, such as "What is the one-year return mentioned in the latest official factsheet?", may be answered only when the exact value is present in the latest applicable approved official source. The preferred citation for such a response is the official HDFC AMC factsheet.

## RAG Architecture

```text
User Query
  -> Query Classification
  -> Retrieval
  -> Source Validation
  -> Context Building
  -> LLM Answer Generation
  -> Compliance Check
  -> Response
```

### Components

#### User Interface

- Minimal chat interface.
- Welcome message.
- Example questions.
- Visible facts-only disclaimer.

#### Query Classifier

- Classifies each query as factual, advisory, performance/comparison, or unsupported/out of scope.

#### Retriever

- Searches relevant chunks from the approved official corpus.
- Uses scheme and document metadata to improve precision and freshness.

#### Source Validator

- Confirms that evidence comes from an approved domain and document type.
- Applies source priority and freshness rules.
- Detects conflicting, superseded, or insufficient evidence.

#### RAG Context Builder

- Selects the most relevant passages.
- Prefers the latest applicable official document.
- Retains document, page, date, and URL provenance.

#### LLM

- Produces a concise answer from the validated context.
- Does not infer facts absent from the context.

#### Compliance Layer

- Enforces the three-sentence maximum.
- Enforces exactly one citation for factual answers.
- Blocks recommendations and unsupported claims.
- Adds and validates the last-updated footer.

## Scheme and Document Metadata

Maintain a canonical record for every selected scheme with at least:

- Scheme name.
- AMC.
- Category.
- Plan.
- Option.
- Official source URL.
- Groww reference URL.
- Source document name and type.
- Document publication or effective date.
- Last-updated date.

Recommended retrieval metadata also includes:

- Canonical scheme identifier.
- Scheme aliases.
- Source organization.
- Source domain.
- Page number or section.
- Ingestion timestamp.
- Supersedes / superseded-by relationship, when known.

## User Experience Requirements

### Welcome Message

> Welcome to the HDFC Mutual Fund FAQ Assistant. Ask me factual questions about HDFC mutual fund schemes, including expense ratio, exit load, minimum SIP, benchmark, riskometer, and scheme details.

### Example Questions

- "What is the expense ratio of HDFC Mid Cap Fund?"
- "What is the benchmark of HDFC Flexi Cap Fund?"
- "What is the lock-in period of HDFC ELSS Tax Saver Fund?"

### Visible Disclaimer

> Facts-only. No investment advice.

## Privacy and Security

The assistant must not collect, store, or process:

- PAN numbers.
- Aadhaar numbers.
- Bank account numbers.
- One-time passwords (OTPs).
- Email addresses.
- Phone numbers.
- Login credentials.
- Transaction credentials.

If a user includes sensitive data, the product should avoid reproducing it and should direct the user to the appropriate secure official channel without processing the information.

## Known Limitations

- Mutual fund information changes over time.
- Expense ratios, fund managers, exit loads, minimum investments, and other scheme attributes may change.
- Historical documents may contain information that is no longer applicable.
- The assistant cannot answer reliably when retrieved evidence is insufficient.
- The assistant is not a financial advisor and cannot provide personalized recommendations.
- Groww pages are contextual references and are not authoritative factual sources.

## Expected Deliverables

### 1. README

The README must include:

- Project overview and setup instructions.
- Selected AMC.
- All 35 selected schemes and their Groww reference links.
- Approved official corpus sources.
- Data-ingestion process.
- Document-chunking strategy.
- Embedding and retrieval approach.
- RAG architecture.
- Query-classification approach.
- Citation strategy.
- Compliance layer.
- Refusal logic.
- Known limitations.

### 2. Disclaimer Snippet

```text
Facts-only. No investment advice.
```

### 3. Scheme Metadata

Structured metadata covering all fields defined in the Scheme and Document Metadata section for each of the 35 schemes.

### 4. Evaluation Dataset

Create test questions that cover:

- Expense ratio.
- Exit load.
- Minimum SIP.
- Minimum lump sum.
- Benchmark.
- Riskometer.
- Lock-in period.
- Investment objective.
- Fund manager.
- Scheme launch date.
- Factsheet retrieval.
- Account-statement and capital-gains-statement questions.
- Advisory and refusal questions.
- Performance and comparison questions.

## Success Criteria

### Accuracy

- Correctly retrieves factual mutual-fund information.
- Grounds answers in official documents.
- Produces no unsupported factual claims.

### Compliance

- Provides no investment advice.
- Correctly refuses advisory questions.
- Provides no performance-based recommendations.
- Correctly handles unsupported and out-of-scope questions.

### Citation Quality

- Includes exactly one source link in each factual response.
- Links to the relevant official source.
- Uses a current and verifiable source.

### Response Quality

- Uses no more than three sentences.
- Uses clear and concise language.
- Includes the last-updated footer consistently.

### Retrieval Quality

- Identifies the correct scheme across all 35 schemes.
- Retrieves the relevant document and passage.
- Prefers the latest applicable official source.

### User Experience

- Provides a simple interface.
- Displays a clear disclaimer.
- Offers useful example questions.
- Returns fast, understandable answers.

## Assumptions to Validate

- The first release is limited to the 35 HDFC schemes listed in this document.
- Direct Growth is the default plan and option context unless the user explicitly asks about another available plan or option.
- A response's last-updated date will be derived from the cited source's effective or publication date.
- The maximum of three sentences applies to the answer body; the `Source` and `Last updated from sources` lines are structured metadata rather than answer sentences.
- Official corpus collection will comply with each source site's access and usage policies.

## Open Questions

- Should refusal responses always contain exactly one official educational link, or may they contain no link when a resource would not be useful?
- How should the system choose among a scheme page, factsheet, SID, KIM, and addendum when two sources with similar dates conflict?
- What freshness threshold should trigger re-crawling or re-indexing each document type?
- What response should be shown when the official source is temporarily unavailable?
- Should users be allowed to ask about Regular plans and non-Growth options, or only the listed Direct Growth variants?
- What latency target defines a "fast" answer?
- What retrieval and answer-accuracy thresholds must the evaluation dataset enforce before release?

## Core Product Principle

Accuracy is more important than apparent intelligence. The assistant must provide short, transparent, and verifiable answers from official HDFC AMC, AMFI, or SEBI evidence, and must refuse whenever answering would require advice, prediction, performance comparison, or unsupported inference.
