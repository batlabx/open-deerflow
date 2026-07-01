"""Central configuration for Open-DeerFlow.

Everything that used to need a cloud key is now a local / OSS default.
Override with environment variables (see .env.example) or by editing the
dataclasses below. Nothing here reaches the network until an agent runs.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field


@dataclass
class LLMConfig:
    """DeerFlow uses two model tiers: a strong 'reasoning' model for planning
    and analysis, and a cheaper 'basic' model for routing/formatting. We point
    both at a local Ollama server so the whole stack runs offline."""
    provider: str = os.getenv("LLM_PROVIDER", "ollama")
    base_url: str = os.getenv("LLM_BASE_URL", "http://localhost:11434")
    reasoning_model: str = os.getenv("REASONING_MODEL", "qwen2.5:14b-instruct")
    basic_model: str = os.getenv("BASIC_MODEL", "llama3.1:8b-instruct")
    temperature: float = float(os.getenv("LLM_TEMPERATURE", "0.2"))


@dataclass
class ToolConfig:
    searxng_url: str = os.getenv("SEARXNG_URL", "http://localhost:8080")
    max_search_results: int = int(os.getenv("MAX_SEARCH_RESULTS", "6"))
    sandbox_image: str = os.getenv("SANDBOX_IMAGE", "python:3.12-slim")
    sandbox_timeout_s: int = int(os.getenv("SANDBOX_TIMEOUT_S", "20"))


@dataclass
class AppConfig:
    llm: LLMConfig = field(default_factory=LLMConfig)
    tools: ToolConfig = field(default_factory=ToolConfig)
    max_plan_steps: int = int(os.getenv("MAX_PLAN_STEPS", "6"))
    checkpoint_db: str = os.getenv("CHECKPOINT_DB", "checkpoints.sqlite")


CONFIG = AppConfig()


def get_llm(tier: str = "reasoning"):
    """Return a LangChain chat model bound to the configured provider.

    We only implement the Ollama path here (the whole point of the rewrite),
    but the ``provider`` switch shows where you'd add OpenAI/Anthropic/etc.
    """
    if CONFIG.llm.provider == "ollama":
        from langchain_ollama import ChatOllama

        model = (CONFIG.llm.reasoning_model if tier == "reasoning"
                 else CONFIG.llm.basic_model)
        return ChatOllama(
            model=model,
            base_url=CONFIG.llm.base_url,
            temperature=CONFIG.llm.temperature,
        )
    raise ValueError(f"Unsupported provider: {CONFIG.llm.provider}")
