import os
import pathlib
from config import LLM_PROVIDER, ANTHROPIC_API_KEY, ANTHROPIC_MODEL, OPENAI_API_KEY, OPENAI_MODEL, OPENAI_BASE_URL

SYSTEM_PROMPT = pathlib.Path(__file__).parent.parent / "fil_prompt.md"


def _load_system_prompt() -> str:
    return SYSTEM_PROMPT.read_text(encoding="utf-8")


def get_reply(history: list[dict]) -> str:
    """
    history — список сообщений в формате:
    [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}, ...]
    """
    system = _load_system_prompt()

    if LLM_PROVIDER == "anthropic":
        return _anthropic_reply(system, history)
    elif LLM_PROVIDER == "openai":
        return _openai_reply(system, history)
    else:
        raise ValueError(f"Неизвестный LLM_PROVIDER: {LLM_PROVIDER}")


def _anthropic_reply(system: str, history: list[dict]) -> str:
    import anthropic
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    response = client.messages.create(
        model=ANTHROPIC_MODEL,
        max_tokens=1024,
        system=system,
        messages=history,
    )
    return response.content[0].text


def _openai_reply(system: str, history: list[dict]) -> str:
    import urllib.request
    import json
    messages = [{"role": "system", "content": system}] + history
    payload = json.dumps({
        "model": OPENAI_MODEL,
        "messages": messages,
        "max_tokens": 1024,
    }).encode("utf-8")
    req = urllib.request.Request(
        f"{OPENAI_BASE_URL}/chat/completions",
        data=payload,
        headers={
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        raise RuntimeError(f"RouterAI {e.code}: {body}") from e
    return data["choices"][0]["message"]["content"]
