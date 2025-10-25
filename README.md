# Gemini Math Tutor

Run the project with the single helper script:

```bash
bash start_dev.sh
```

What `start_dev.sh` does:
- Verifies that `GEMINI_API_KEY` is set in the environment.
- Runs a small key-check that exercises the Gemini client (prints a short sample output).
- Starts the FastAPI backend (uvicorn) on port 8000 and waits for `/health`.
- Performs a quick end-to-end request to the running server using the bundled client.
- Attempts to start the frontend dev server (port 3000) if `npm` is available.
- Waits for the frontend to be ready and prints (or opens) a preview URL appropriate for your environment (Codespaces preview or localhost).
- Tails backend and frontend logs and cleans up background processes when you press Ctrl-C.

Notes:
- Make sure `GEMINI_API_KEY` is set before running the script. In Codespaces add it as a Codespaces secret; locally export it in your shell:

```bash
export GEMINI_API_KEY="your_real_api_key_here"
bash start_dev.sh
```

- If `npm` is not available the script will skip starting the frontend and write a short note to `.devlogs/frontend.log`.
- If you change `.devcontainer/devcontainer.json` (ports behavior), rebuild the devcontainer so the settings take effect.

That's it — run `bash start_dev.sh` and follow the printed messages.

Updated: October 25, 2025


- A minimal frontend is included in `frontend/` that serves a static page and proxies `/api` requests to the backend. The frontend dev server runs on port 3000 by default and proxies to the backend on port 8000.
