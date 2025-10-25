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

Frontend (web UI)

- A minimal frontend is included in `frontend/` that serves a static page and proxies `/api` requests to the backend. The frontend dev server runs on port 3000 by default and proxies to the backend on port 8000.
- To run the frontend locally (when backend is running):

```bash
cd frontend
npm start        # starts the frontend at http://localhost:3000 (devcontainer installs deps automatically)
```

- If your backend is on a different host/port, set `API_TARGET` before starting the frontend, for example:

```bash
API_TARGET=http://127.0.0.1:8000 npm start
```

- The frontend UI posts JSON to `/api/generate`, which the frontend server proxies to the backend's `/generate` endpoint so you won't need to deal with CORS in the browser.


Devcontainer / Codespaces notes

- The devcontainer is configured in `.devcontainer/devcontainer.json` and forwards port `8000` so VS Code/Codespaces can open the FastAPI server in the browser automatically.
- For Codespaces, add `GEMINI_API_KEY` as a Codespaces secret (Settings → Secrets and variables → Codespaces) so the secret is injected securely into the container.

Adding `GEMINI_API_KEY` for collaborators

If you want other contributors to be able to run the server in Codespaces or the devcontainer, ask them to add `GEMINI_API_KEY` to the repository's secrets. Here are short, reliable options you can include in onboarding instructions:

- Add as a Codespaces secret (recommended for Codespaces users):
	1. Go to the GitHub repository → Settings → Secrets and variables → Codespaces.
 2. Click "New repository secret".
 3. Name: `GEMINI_API_KEY`  Value: (paste the key).
 4. Rebuild the Codespace / devcontainer so the secret is injected into the environment.

- Add as a repository secret for Actions (if you use Actions to run server tests):
	1. Settings → Secrets and variables → Actions → New repository secret.
	2. Name: `GEMINI_API_KEY`  Value: (paste the key).

- If contributors are running locally (not Codespaces):
	- They can set the key in their shell for the session:
		```bash
		export GEMINI_API_KEY="your_real_api_key_here"
		```
	- Or create a local `.env` file (add it to `.gitignore`) with:
		```ini
		GEMINI_API_KEY=your_real_api_key_here
		```

Security notes

- Only repository admins can add repo-level secrets. If a contributor can't add the secret, they can run locally with a personal `.env` or a local env var instead.
- Never store the secret in the repo or commit `.env` files. Use Codespaces/Actions secrets or local `.env` excluded by `.gitignore`.

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

