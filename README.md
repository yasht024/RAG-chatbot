# Mutual Fund FAQ Assistant

## Overview
A production-ready facts-only AI assistant for HDFC Mutual Fund schemes. It answers objective facts supported by current approved Groww evidence. It strictly refuses advice, recommendations, predictions, and prohibited performance requests.

**Live Demo:** [https://rag-chatbot-5vi7dgcu2-yash-4f7a.vercel.app/](https://rag-chatbot-5vi7dgcu2-yash-4f7a.vercel.app/)

## Setup and Local Development
1. Install dependencies:
   `pip install -r requirements.txt` (Backend)
   `cd apps/web && npm install` (Frontend)
2. Run API (from project root):
   `uvicorn services.assistant_api.main:app --reload`
   - API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)
3. Run Web UI:
   `cd apps/web && npm run dev`
   - App: [http://localhost:5173](http://localhost:5173)

## Documentation & Architecture
- [Implementation Plan](docs/implementation-plan.md)
- [Architecture](docs/Architecture.md)
- [Sources Policy](docs/policies/sources_policy.md)
- [Scheme Catalog](docs/reports/scheme_catalog.md)
