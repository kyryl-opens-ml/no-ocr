# Guidelines for Codex

## Repository Layout
- `no-ocr-api` – FastAPI backend with tests in `no-ocr-api/tests`.
- `no-ocr-ui` – React/TypeScript front end. Linting via ESLint.
- `no-ocr-llms` – Scripts for Modal based LLM serving.

## Coding style
- **Python**: run `ruff .` before committing. The configuration is defined in `pyproject.toml` (line length 120, rules `E,F,I,N,Q,W`).
- **TypeScript**: use `npm run lint` in `no-ocr-ui`.

## Tests
- **Python**: run `pytest` from the repository root (tests live in `no-ocr-api/tests`). These tests require a `.env` file inside `no-ocr-api` (see `.env.example`) with valid values for `COLPALI_TOKEN`, `COLPALI_BASE_URL`, `VLLM_URL` and related settings. Sample PDFs are provided in `no-ocr-api/data`.
- **TypeScript**: no unit tests are provided, but please ensure ESLint passes.

## Development
- Use `docker-compose up` to spin up the API, UI, and Qdrant services locally.
