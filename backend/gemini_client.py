import os
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
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                temperature=temperature,
                max_output_tokens=max_output_tokens,
            )

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
