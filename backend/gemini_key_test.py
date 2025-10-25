"""Small CLI utility to validate the Gemini API key from the environment.

This script is intended to be invoked by `start_dev.sh` to check that the
`GEMINI_API_KEY` works. It attempts a lightweight text generation and exits
with status 0 on success and non-zero on error.

Usage:
  python backend/gemini_key_test.py [--model MODEL] [--prompt PROMPT]

Environment:
  GEMINI_API_KEY  (required)
"""

from __future__ import annotations

import argparse
import os
import sys
import json

try:
    from google import genai
except Exception:
    genai = None


def perform_check(model: str, prompt: str, max_output_tokens: int = 64) -> int:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: GEMINI_API_KEY environment variable not set.", file=sys.stderr)
        return 2

    if genai is None:
        print("ERROR: google-genai client not installed. Install via `pip install google-genai`.", file=sys.stderr)
        return 3

    try:
        client = genai.Client(api_key=api_key)

        # Some versions of google-genai expose generate_content in different
        # shapes. We attempt a minimal call and fall back to a safe alternative
        # if necessary.
        sig = None
        try:
            from inspect import signature

            sig = signature(client.models.generate_content)
        except Exception:
            sig = None

        # Prepare kwargs guarded by signature to avoid unexpected-kw errors
        kwargs = {}
        if sig is None or 'model' in sig.parameters:
            kwargs['model'] = model
        if sig is None or 'contents' in sig.parameters:
            kwargs['contents'] = prompt
        if sig is None or 'max_output_tokens' in sig.parameters:
            kwargs['max_output_tokens'] = max_output_tokens

        resp = client.models.generate_content(**kwargs)

        # The response object shape varies; try common access patterns.
        text = None
        if hasattr(resp, 'text'):
            text = resp.text
        else:
            try:
                # some versions return a dict-like object
                text = getattr(resp, 'candidates', None)
                if text and isinstance(text, (list, tuple)):
                    # join candidate texts if present
                    text = '\n'.join(getattr(c, 'content', str(c))
                                     for c in text)
                else:
                    text = json.dumps(resp.__dict__)
            except Exception:
                text = str(resp)

        print("Gemini key test successful. Sample output:\n")
        print(text)
        return 0
    except Exception as exc:
        print(f"ERROR: failed to call Gemini API: {exc}", file=sys.stderr)
        return 4


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description="Test GEMINI_API_KEY by making a small generation.")
    p.add_argument(
        "--model", default=os.environ.get("GEMINI_MODEL", "gemini-2.5-flash"))
    p.add_argument("--prompt", default="Say hello in one sentence.")
    p.add_argument("--max-tokens", type=int, default=64)
    args = p.parse_args(argv)

    return perform_check(args.model, args.prompt, args.max_tokens)


if __name__ == "__main__":
    raise SystemExit(main())
