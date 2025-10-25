import os
import inspect
from typing import Optional

try:
    # prefer the official google genai client if available
    from google import genai
except Exception:  # pragma: no cover - runtime optional
    genai = None


DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
DEFAULT_SYSTEM_PROMPT = os.getenv(
    "GEMINI_SYSTEM_PROMPT",
    (
        "You are a helpful, patient math tutor. For each student question, restate the problem briefly, "
        "provide clear step-by-step reasoning, show the final answer, and give a short tip to check the result. "
        "Use simple language suitable for learners and avoid skipping steps. Be concise but thorough."
    ),
)


class GeminiClient:
    """Small wrapper around the Gemini API (using `google-genai` when available).

    Usage:
      client = GeminiClient()
      out = client.generate("What is 7*8?")

    The client reads the API key from the GEMINI_API_KEY env var by default.
    """

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            # Do not create a client at import-time; only raise if user actually instantiates
            raise ValueError(
                "GEMINI_API_KEY environment variable not set and no api_key provided")

        if genai is None:
            raise RuntimeError(
                "google-genai package is required but not installed. Install `google-genai` or set up an alternative client."
            )

        # initialize official client
        self.client = genai.Client(api_key=self.api_key)
        self.model = model or DEFAULT_MODEL
        self.system_prompt = DEFAULT_SYSTEM_PROMPT

    def generate(
        self,
        question: str,
        temperature: float = 0.2,
        max_output_tokens: int = 512,
    ) -> str:
        """Generate a single completion from Gemini.

        Returns the text of the model's response.
        Raises RuntimeError on API errors.
        """
        if not question:
            raise ValueError("question must be a non-empty string")

        prompt = f"System: {self.system_prompt}\n\nStudent: {question}\n\nTutor:"

        try:
            # match the simple pattern used in existing examples (client.models.generate_content)
            generate_fn = getattr(self.client.models, "generate_content")

            # Build base kwargs and only pass supported args to avoid unexpected-keyword errors
            base_kwargs = {
                "model": self.model,
                "contents": prompt,
            }
            optional_kwargs = {
                "temperature": temperature,
                "max_output_tokens": max_output_tokens,
            }

            try:
                sig = inspect.signature(generate_fn)
                supported = set(sig.parameters.keys())
            except Exception:
                # If we can't introspect, fall back to passing only base kwargs
                supported = set(base_kwargs.keys())

            for k, v in optional_kwargs.items():
                if k in supported:
                    base_kwargs[k] = v

            response = generate_fn(**base_kwargs)

            # The official client returns an object with .text (as shown in repo example)
            text = getattr(response, "text", None)
            if text is None:
                # fallback: try dict-like access
                try:
                    text = response["text"]
                except Exception:
                    text = str(response)

            return text
        except Exception as exc:
            raise RuntimeError(f"Gemini API request failed: {exc}") from exc


def build_default_client() -> Optional[GeminiClient]:
    """Helper to build a client if the environment has a key, otherwise return None.

    Useful for servers that want to construct lazily and provide clearer error messaging.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return None
    return GeminiClient(api_key=api_key)


def call_server(server_url: str, question: str, temperature: float = 0.2, max_output_tokens: int = 512) -> str:
    """POST to the FastAPI server /generate endpoint and return the raw response body as text.

    This uses only the standard library so it works without installing extra HTTP clients.
    """
    import json
    from urllib import request, error

    server_url = server_url.rstrip("/") + "/generate"
    payload = {
        "question": question,
        "temperature": temperature,
        "max_output_tokens": max_output_tokens,
    }
    data = json.dumps(payload).encode("utf-8")
    req = request.Request(server_url, data=data, headers={"Content-Type": "application/json"}, method="POST")

    try:
        with request.urlopen(req, timeout=30) as resp:
            return resp.read().decode("utf-8")
    except error.HTTPError as e:
        # try to read error body
        try:
            body = e.read().decode("utf-8")
        except Exception:
            body = str(e)
        raise RuntimeError(f"Server returned HTTP {e.code}: {body}") from e
    except Exception as e:
        raise RuntimeError(f"Failed to call server: {e}") from e


def _cli_main():
    """Simple CLI to call a running server.

    Example:
      python backend/gemini_client.py --server http://localhost:8000 --question "What is 2+2?"
    """
    import argparse
    parser = argparse.ArgumentParser(description="Call Gemini Math Tutor server /generate endpoint")
    parser.add_argument("--server", default="http://localhost:8000", help="Server base URL (default: http://localhost:8000)")
    parser.add_argument("--question", required=True, help="Question to send to the tutor")
    parser.add_argument("--temperature", type=float, default=0.2)
    parser.add_argument("--max-output-tokens", type=int, default=512)
    args = parser.parse_args()

    try:
        out = call_server(args.server, args.question, args.temperature, args.max_output_tokens)
        print(out)
    except Exception as e:
        import sys

        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    _cli_main()
