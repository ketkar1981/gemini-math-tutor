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
- Preferred (Codespaces): add `GEMINI_API_KEY` as a Codespaces secret so the key is injected securely into the container. This avoids placing the key in shell history or files.

	To add a Codespaces secret:
	1. Go to your repository → Settings → Secrets and variables → Codespaces.
 2. Click "New repository secret".
 3. Name: `GEMINI_API_KEY`  Value: (paste the key).
 4. Rebuild the Codespace / devcontainer so the secret is available in the environment.

- Local (developer machine): if you're running the script locally you can set the environment variable in your shell for the current session. Avoid committing keys or placing them in files that might be checked in.

	Example (temporary for the session):
	```bash
	export GEMINI_API_KEY="<your-api-key-here>"
	bash start_dev.sh
	```

- If `npm` is not available the script will skip starting the frontend and write a short note to `.devlogs/frontend.log`.
- If you change `.devcontainer/devcontainer.json` (ports behavior), rebuild the devcontainer so the settings take effect.

That's it — run `bash start_dev.sh` and follow the printed messages.

Updated: October 25, 2025

