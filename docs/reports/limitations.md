# Known Limitations and Controlled Failure Behavior

## Known Limitations
1. **Document Types**: The system only parses HTML factsheets and natively digital PDFs. Scanned PDFs without OCR confidence >90% will fall back to `INSUFFICIENT_EVIDENCE`.
2. **Tabular Reasoning**: Extremely complex cross-table calculations are not supported; the system pulls scalar facts directly.

## Controlled Failure States
- **Missing Evidence**: Returns `INSUFFICIENT_EVIDENCE`. No hallucinations allowed.
- **Ambiguity**: Returns `AMBIGUOUS_SCHEME` if a query matches multiple schemes equally.
- **Source Conflict**: If two valid sources disagree on a scalar fact, returns `SOURCE_CONFLICT`.
