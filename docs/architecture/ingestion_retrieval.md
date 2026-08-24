# Ingestion, Chunking, Embedding, and Retrieval Design

## Ingestion
1. **Fetching**: Fetch artifacts (HTML/PDF) idempotently. Generate SHA-256 hashes for deduplication.
2. **Parsing**: Extract structure (headings, tables). For PDFs, parse text and layout mapping.
3. **Chunking**: Sectional boundary preservation. Tokens partitioned by semantic sections (250–500 tokens).

## Embedding
Passages are enriched with `scheme_ids`, `plan`, `option`, and `heading_path`. Embedded using `BGE Large` (1024-dimensional pgvector).

## Retrieval
Uses a hybrid approach (PostgreSQL keyword search + pgvector). Re-ranking favors precise passages (e.g. matched sections/tables) over generic mentions. Hard filters applied to `scheme_id`, `plan`, and `option` before vector search.
