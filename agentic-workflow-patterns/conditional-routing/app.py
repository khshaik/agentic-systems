"""A small LangGraph workflow that routes by a model-classified energy level."""

from __future__ import annotations

import os
import re
from typing import Any, TypedDict

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, StateGraph

load_dotenv()


class EnergyState(TypedDict, total=False):
    """Data passed between nodes in the recommendation graph."""

    input: str
    energy_level: str
    response: str


_llm: Any | None = None


def build_model() -> Any:
    """Create the configured chat model.

    Gemini is the zero-configuration default. Set ``LLM_PROVIDER=nvidia`` to
    use an NVIDIA-hosted model instead.
    """

    provider = os.getenv("LLM_PROVIDER", "gemini").strip().lower()
    temperature = float(os.getenv("LLM_TEMPERATURE", "0"))

    if provider == "gemini":
        api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "Set GOOGLE_API_KEY in .env before running the Gemini provider."
            )
        return ChatGoogleGenerativeAI(
            model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
            google_api_key=api_key,
            temperature=temperature,
        )

    if provider == "nvidia":
        if not os.getenv("NVIDIA_API_KEY"):
            raise RuntimeError(
                "Set NVIDIA_API_KEY in .env before running the NVIDIA provider."
            )
        try:
            from langchain_nvidia_ai_endpoints import ChatNVIDIA
        except ImportError as exc:  # pragma: no cover - depends on local extras
            raise RuntimeError("Run 'uv sync --extra nvidia' to install NVIDIA support.") from exc

        return ChatNVIDIA(
            model=os.getenv("NVIDIA_MODEL", "moonshotai/kimi-k2.6"),
            temperature=temperature,
        )

    raise RuntimeError(
        f"Unsupported LLM_PROVIDER={provider!r}. Choose 'gemini' or 'nvidia'."
    )


def get_model() -> Any:
    """Lazily initialize the model so the graph can be imported without secrets."""

    global _llm
    if _llm is None:
        _llm = build_model()
    return _llm


def detect_energy_level(state: EnergyState) -> dict[str, str]:
    """Classify the input and return a routing-safe energy label."""

    prompt = f"""
Classify the energy expressed in the message below.
Return exactly one lowercase word: low, medium, or high.

Message: {state['input']!r}
""".strip()

    content = str(get_model().invoke(prompt).content).strip().lower()
    match = re.search(r"\b(low|medium|high)\b", content)
    if not match:
        raise ValueError(
            "The model did not return a supported energy level. Try describing "
            "how active, tired, or motivated you feel."
        )
    return {"energy_level": match.group(1)}


def low_energy_node(_: EnergyState) -> dict[str, str]:
    return {
        "response": (
            "It sounds like your energy is low. Consider resting, stretching, "
            "or choosing a calm activity such as reading. 🛋️📚"
        )
    }


def medium_energy_node(_: EnergyState) -> dict[str, str]:
    return {
        "response": (
            "You seem to have medium energy. A walk, a focused hobby, or a short "
            "learning session could be a good fit. 🚶📖"
        )
    }


def high_energy_node(_: EnergyState) -> dict[str, str]:
    return {
        "response": (
            "Your energy sounds high. Try a run, a workout, a sport, or a creative "
            "project that can use that momentum. 🏃⚽🔥"
        )
    }


def route_energy(state: EnergyState) -> str:
    """Return the branch key selected by the classifier node."""

    return state["energy_level"]


def build_graph():
    """Build and compile the conditional LangGraph workflow."""

    builder = StateGraph(EnergyState)
    builder.add_node("detect_energy_level", detect_energy_level)
    builder.add_node("low", low_energy_node)
    builder.add_node("medium", medium_energy_node)
    builder.add_node("high", high_energy_node)
    builder.set_entry_point("detect_energy_level")
    builder.add_conditional_edges(
        "detect_energy_level",
        route_energy,
        {"low": "low", "medium": "medium", "high": "high"},
    )
    builder.add_edge("low", END)
    builder.add_edge("medium", END)
    builder.add_edge("high", END)
    return builder.compile()


graph = build_graph()


def run_cli() -> None:
    """Run the interactive weekend activity recommender."""

    print("-" * 54)
    print("Weekend Activity Recommender")
    print("Describe your energy, or type 'quit' to exit.")
    print("-" * 54)

    while True:
        try:
            user_input = input("\nHow are you feeling today? ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            return

        if user_input.lower() in {"quit", "exit", "q"}:
            print("Goodbye!")
            return
        if not user_input:
            continue

        try:
            result = graph.invoke({"input": user_input})
        except (RuntimeError, ValueError) as exc:
            print(f"Unable to produce a recommendation: {exc}")
            continue

        print(f"Energy: {result['energy_level'].upper()}")
        print(f"Recommendation: {result['response']}")


if __name__ == "__main__":
    run_cli()
