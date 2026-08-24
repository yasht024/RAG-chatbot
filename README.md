# Mutual Fund FAQ Assistant

## Overview
A production-ready facts-only AI assistant for HDFC Mutual Fund schemes. It answers objective facts supported by current approved Groww evidence. It strictly refuses advice, recommendations, predictions, and prohibited performance requests.

## Setup and Local Development
1. Install dependencies:
   `pip install -r requirements.txt` (Backend)
   `cd apps/web && npm install` (Frontend)
2. Start local services (Postgres, Redis):
   `docker-compose up -d`
3. Run API:
   `cd services/assistant_api && uvicorn orchestrator:app --reload`
   - API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)
4. Run Web UI:
   `cd apps/web && npm run dev`
   - App: [http://localhost:3000](http://localhost:3000)

## Documentation & Architecture
- [Implementation Plan](docs/implementation-plan.md)
- [Architecture](docs/Architecture.md)
- [Sources Policy](docs/policies/sources_policy.md)
- [Scheme Catalog](docs/reports/scheme_catalog.md)
