import asyncio
import json
import logging
import os
import re
import time
from typing import Any, Iterator, Type

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from pydantic import BaseModel, ValidationError


CURRENT_DIR = os.path.dirname(__file__)
PACKAGE_ROOT = os.path.dirname(CURRENT_DIR)
PROJECT_ROOT = os.path.dirname(PACKAGE_ROOT)

load_dotenv(os.path.join(PROJECT_ROOT, ".env"))
load_dotenv(os.path.join(PACKAGE_ROOT, ".env"), override=False)
load_dotenv()

logger = logging.getLogger(__name__)

PLANNING_MODEL = os.getenv("PLANNING_MODEL", "qwen/qwen3-next-80b-a3b-instruct")
CODE_MODEL = os.getenv("CODE_MODEL", "qwen/qwen2.5-coder-32b-instruct")
DEFAULT_RETRIES = int(os.getenv("LLM_MAX_RETRIES", "2"))
RETRY_DELAY_SECONDS = float(os.getenv("LLM_RETRY_DELAY_SECONDS", "2"))

PLANNING_TOP_P = float(os.getenv("PLANNING_TOP_P", "0.95"))
CODE_TOP_P = float(os.getenv("CODE_TOP_P", "0.95"))
PLANNING_MAX_TOKENS = int(os.getenv("PLANNING_MAX_TOKENS", "16384"))
CODE_MAX_TOKENS = int(os.getenv("CODE_MAX_TOKENS", "16384"))
PLANNING_REASONING = os.getenv("PLANNING_REASONING", "true").lower() in {
    "1",
    "true",
    "yes",
    "on",
}
PLANNING_REASONING_EFFORT = os.getenv("PLANNING_REASONING_EFFORT", "high")


def _normalize_content(content: Any) -> str:
    if isinstance(content, str):
        return content.strip()

    if isinstance(content, list):
        text_chunks = []
        for item in content:
            if isinstance(item, str):
                text_chunks.append(item)
            elif isinstance(item, dict):
                if item.get("type") == "text":
                    text_chunks.append(item.get("text", ""))
                elif "text" in item:
                    text_chunks.append(str(item["text"]))
        return "\n".join(chunk for chunk in text_chunks if chunk).strip()

    return str(content).strip()


def _to_dict(model: BaseModel) -> dict:
    if hasattr(model, "model_dump"):
        return model.model_dump()
    return model.dict()


def _schema_json_text(schema: Type[BaseModel]) -> str:
    if hasattr(schema, "model_json_schema"):
        return json.dumps(schema.model_json_schema(), indent=2)
    return schema.schema_json(indent=2)


def _extract_json_payload(text: str) -> dict:
    fenced_match = re.search(r"```json\s*(\{[\s\S]*\})\s*```", text, re.IGNORECASE)
    if fenced_match:
        return json.loads(fenced_match.group(1))

    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        raise ValueError("No JSON object found in model response")

    return json.loads(match.group(0))


def _is_deepseek_model(model_name: str) -> bool:
    return "deepseek" in model_name.lower()


def _resolve_model_options(model_name: str, temperature: float) -> dict[str, Any]:
    if model_name == CODE_MODEL:
        top_p = CODE_TOP_P
        max_tokens = CODE_MAX_TOKENS
    else:
        top_p = PLANNING_TOP_P
        max_tokens = PLANNING_MAX_TOKENS

    options: dict[str, Any] = {
        "model": model_name,
        "temperature": temperature,
        "top_p": top_p,
        "max_completion_tokens": max_tokens,
    }

    if _is_deepseek_model(model_name) and PLANNING_REASONING:
        options["extra_body"] = {
            "chat_template_kwargs": {
                "thinking": True,
                "reasoning_effort": PLANNING_REASONING_EFFORT,
            }
        }

    return options


def _build_model(model_name: str, temperature: float) -> ChatNVIDIA:
    api_key = (
        os.getenv("NVIDIA_API_KEY")
        or os.getenv("NGC_API_KEY")
        or os.getenv("LANGCHAIN_NVIDIA_API_KEY")
    )
    if not api_key:
        raise RuntimeError(
            "NVIDIA_API_KEY is not configured"
        )

    options = _resolve_model_options(model_name=model_name, temperature=temperature)
    print(f"[llm] initializing model: {model_name}", flush=True)

    return ChatNVIDIA(
        api_key=api_key,
        **options,
    )


def _invoke_with_retries(invoke_fn):
    last_error: Exception | None = None

    for attempt in range(1, DEFAULT_RETRIES + 2):
        try:
            print(f"[llm] request attempt {attempt}/{DEFAULT_RETRIES + 1}: started", flush=True)
            start_time = time.monotonic()
            result = invoke_fn()
            elapsed = time.monotonic() - start_time
            print(f"[llm] request attempt {attempt}/{DEFAULT_RETRIES + 1}: completed in {elapsed:.1f}s", flush=True)
            return result
        except Exception as exc:
            last_error = exc
            print(f"[llm] request attempt {attempt}/{DEFAULT_RETRIES + 1}: failed ({exc})", flush=True)
            if attempt > DEFAULT_RETRIES:
                break

            logger.warning(
                "LLM invoke attempt %s/%s failed: %s",
                attempt,
                DEFAULT_RETRIES + 1,
                exc,
            )
            time.sleep(RETRY_DELAY_SECONDS)

    raise RuntimeError(f"LLM invoke failed after retries: {last_error}") from last_error


async def _ainvoke_with_retries(invoke_fn):
    last_error: Exception | None = None

    for attempt in range(1, DEFAULT_RETRIES + 2):
        try:
            print(f"[llm] async request attempt {attempt}/{DEFAULT_RETRIES + 1}: started", flush=True)
            start_time = time.monotonic()
            result = await invoke_fn()
            elapsed = time.monotonic() - start_time
            print(f"[llm] async request attempt {attempt}/{DEFAULT_RETRIES + 1}: completed in {elapsed:.1f}s", flush=True)
            return result
        except Exception as exc:
            last_error = exc
            print(f"[llm] async request attempt {attempt}/{DEFAULT_RETRIES + 1}: failed ({exc})", flush=True)
            if attempt > DEFAULT_RETRIES:
                break

            logger.warning(
                "Async LLM invoke attempt %s/%s failed: %s",
                attempt,
                DEFAULT_RETRIES + 1,
                exc,
            )
            await asyncio.sleep(RETRY_DELAY_SECONDS)

    raise RuntimeError(f"Async LLM invoke failed after retries: {last_error}") from last_error


def invoke_text_model(
    prompt: str,
    system_prompt: str | None = None,
    model_name: str = CODE_MODEL,
    temperature: float = 0.6,
) -> str:
    model = _build_model(model_name=model_name, temperature=temperature)
    messages = []

    if system_prompt:
        messages.append(SystemMessage(content=system_prompt))

    messages.append(HumanMessage(content=prompt))
    response = _invoke_with_retries(lambda: model.invoke(messages))
    return _normalize_content(response.content)


async def invoke_text_model_async(
    prompt: str,
    system_prompt: str | None = None,
    model_name: str = CODE_MODEL,
    temperature: float = 0.6,
) -> str:
    model = _build_model(model_name=model_name, temperature=temperature)
    messages = []

    if system_prompt:
        messages.append(SystemMessage(content=system_prompt))

    messages.append(HumanMessage(content=prompt))
    response = await _ainvoke_with_retries(lambda: model.ainvoke(messages))
    return _normalize_content(response.content)


def stream_text_model(
    prompt: str,
    system_prompt: str | None = None,
    model_name: str = PLANNING_MODEL,
    temperature: float = 0.6,
) -> Iterator[dict[str, str | None]]:
    model = _build_model(model_name=model_name, temperature=temperature)
    messages = []

    if system_prompt:
        messages.append(SystemMessage(content=system_prompt))

    messages.append(HumanMessage(content=prompt))

    last_error: Exception | None = None

    for attempt in range(1, DEFAULT_RETRIES + 2):
        try:
            for chunk in model.stream(messages):
                kwargs = getattr(chunk, "additional_kwargs", {}) or {}
                yield {
                    "reasoning": kwargs.get("reasoning")
                    or kwargs.get("reasoning_content"),
                    "content": str(chunk.content or ""),
                }
            return
        except Exception as exc:
            last_error = exc
            if attempt > DEFAULT_RETRIES:
                break

            logger.warning(
                "LLM stream attempt %s/%s failed: %s",
                attempt,
                DEFAULT_RETRIES + 1,
                exc,
            )
            time.sleep(RETRY_DELAY_SECONDS)

    raise RuntimeError(f"LLM stream failed after retries: {last_error}") from last_error


def invoke_structured_model(
    prompt: str,
    schema: Type[BaseModel],
    system_prompt: str | None = None,
    model_name: str = PLANNING_MODEL,
    temperature: float = 0.2,
    max_attempts: int = 3,
) -> BaseModel:
    model = _build_model(model_name=model_name, temperature=temperature)
    response_format_instructions = (
        f"{prompt}\n\n"
        "Return valid JSON only. Do not wrap the response in markdown. "
        f"The JSON must satisfy this schema:\n{_schema_json_text(schema)}"
    )

    base_messages = []

    if system_prompt:
        base_messages.append(SystemMessage(content=system_prompt))

    base_messages.append(HumanMessage(content=response_format_instructions))

    last_error: Exception | None = None

    for attempt in range(1, max_attempts + 1):
        try:
            print(f"[llm] structured json attempt {attempt}/{max_attempts}: started", flush=True)
            raw_response = _invoke_with_retries(lambda: model.invoke(base_messages))
            payload = _extract_json_payload(_normalize_content(raw_response.content))
            parsed = schema(**payload)
            print(f"[llm] structured json attempt {attempt}/{max_attempts}: parsed", flush=True)
            return parsed

        except (ValidationError, ValueError, TypeError, json.JSONDecodeError) as exc:
            last_error = exc
            print(f"[llm] structured json attempt {attempt}/{max_attempts}: invalid ({exc})", flush=True)
            logger.warning(
                "Structured JSON parse failed on attempt %s/%s: %s",
                attempt,
                max_attempts,
                exc,
            )
        except Exception as exc:
            last_error = exc
            print(f"[llm] structured json attempt {attempt}/{max_attempts}: failed ({exc})", flush=True)
            logger.warning(
                "Structured invoke failed on attempt %s/%s: %s",
                attempt,
                max_attempts,
                exc,
            )

        repair_messages = []
        if system_prompt:
            repair_messages.append(SystemMessage(content=system_prompt))
        repair_messages.append(
            HumanMessage(
                content=(
                    f"{response_format_instructions}\n\n"
                    "Previous response was invalid. Return corrected JSON only."
                )
            )
        )

        try:
            print(f"[llm] structured json repair {attempt}/{max_attempts}: started", flush=True)
            raw_response = _invoke_with_retries(lambda: model.invoke(repair_messages))
            payload = _extract_json_payload(_normalize_content(raw_response.content))
            parsed = schema(**payload)
            print(f"[llm] structured json repair {attempt}/{max_attempts}: parsed", flush=True)
            return parsed
        except Exception as exc:
            last_error = exc
            print(f"[llm] structured json repair {attempt}/{max_attempts}: failed ({exc})", flush=True)
            logger.warning(
                "Structured JSON repair failed on attempt %s/%s: %s",
                attempt,
                max_attempts,
                exc,
            )

    raise RuntimeError(
        f"Structured model failed after {max_attempts} attempts: {last_error}"
    )
