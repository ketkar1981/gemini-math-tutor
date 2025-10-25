(The file `/workspaces/gemini-math-tutor/README.md` exists, but is empty)
# Gemini Math Tutor

This repository contains a small FastAPI wrapper around the Gemini API and a lightweight client script that posts to the server.

Files of interest
- `backend/gemini_client.py` — Gemini client wrapper + a CLI that can call the running server (`/generate`).
- `backend/gemini_server.py` — FastAPI server exposing `/health` and `/generate` endpoints.
- `backend/requirements.txt` — Python dependencies.

Quick start (local)

1. Install dependencies:

```bash
pip install -r backend/requirements.txt
```

2. Set your Gemini API key in the environment (do NOT commit this key):

```bash
export GEMINI_API_KEY="your_real_api_key_here"
```

3. Start the server (recommended with auto-reload for dev):

```bash
uvicorn backend.gemini_server:app --host 0.0.0.0 --port 8000 --reload
```

4. Health check:

```bash
curl http://localhost:8000/health
# Expected: {"status":"ok"}
```

Call the server from the included client script (no additional deps)

```bash
python backend/gemini_client.py --question "Solve 2x+3=11. Show steps."
```

You can also call the endpoint directly with curl:

```bash
curl -X POST http://localhost:8000/generate \
	-H "Content-Type: application/json" \
	-d '{"question":"Solve 2x+3=11. Show steps.","temperature":0.1}'
```

Devcontainer / Codespaces notes

- The devcontainer is configured in `.devcontainer/devcontainer.json` and forwards port `8000` so VS Code/Codespaces can open the FastAPI server in the browser automatically.
- For Codespaces, add `GEMINI_API_KEY` as a Codespaces secret (Settings → Secrets and variables → Codespaces) so the secret is injected securely into the container.

Testing without a real Gemini key

- You can test the server's health endpoint without an API key. To test `/generate` without making real Gemini calls, modify `backend/gemini_server.py` to mock `GeminiClient.generate()` or I can add a `--mock` mode if you'd like.

Git / housekeeping

- A `.gitignore` is present to ignore `__pycache__` and other common Python artifacts. If you see `backend/__pycache__/` in `git status`, remove it from the index:

```bash
git rm -r --cached backend/__pycache__ || true
```

Security

- Never commit your `GEMINI_API_KEY` or `.env` files containing secrets. Use Codespaces secrets or a local `.env` added to `.gitignore` for local testing.

Need help?

If you want I can:
- Add a `--mock` server mode for offline testing.
- Commit this README and the `.gitignore` change for you.
- Add a minimal pytest test that mocks the Gemini client.

---
Updated: October 25, 2025

