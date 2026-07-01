"""Open-DeerFlow — an open-source rewrite of ByteDance's DeerFlow SuperAgent.

Same LangGraph topology (coordinator -> planner -> research team -> reporter),
but every hosted dependency is swapped for a local / open-source one:

    cloud LLM      -> Ollama (Qwen2.5 / Llama-3.1)
    Tavily search  -> SearxNG (self-hosted) with a DuckDuckGo fallback
    hosted reader  -> trafilatura
    K8s sandbox    -> Docker + nsjail
    everything else (LangGraph, MCP, checkpointer) is already open.
"""
__version__ = "0.1.0"
