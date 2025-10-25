import os
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

try:
    # when used as a package
    from .gemini_client import GeminiClient, build_default_client
except Exception:
    # when executed directly (python backend/gemini_server.py) import by file path
    import importlib.util
    import os

    script_dir = os.path.dirname(__file__)
    client_path = os.path.join(script_dir, "gemini_client.py")
    spec = importlib.util.spec_from_file_location("gemini_client", client_path)
    gemini_client = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gemini_client)
    GeminiClient = gemini_client.GeminiClient
    build_default_client = gemini_client.build_default_client


class GenerateRequest(BaseModel):
    question: str
    temperature: Optional[float] = 0.2
    max_output_tokens: Optional[int] = 512


class GenerateResponse(BaseModel):
    answer: str
    model: Optional[str]


app = FastAPI(title="Gemini Math Tutor API")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/generate", response_model=GenerateResponse)
def generate(req: GenerateRequest):
    """Generate a math-tutor style answer from the Gemini API.

    Expects GEMINI_API_KEY to be set in the environment. Returns a short JSON with the answer.
    """
    # build client lazily so import doesn't require a key
    client = None
    try:
        client = GeminiClient(api_key=os.environ.get("GEMINI_API_KEY"))
    except ValueError:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY not configured on server")
    except RuntimeError as e:
        # e.g., google-genai not installed
        raise HTTPException(status_code=500, detail=str(e))

    try:
        text = client.generate(
            question=req.question,
            temperature=req.temperature,
            max_output_tokens=req.max_output_tokens,
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))

    return GenerateResponse(answer=text, model=client.model)


if __name__ == "__main__":
    # Allow running with `python backend/gemini_server.py`
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
