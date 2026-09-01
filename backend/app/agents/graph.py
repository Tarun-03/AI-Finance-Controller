from functools import partial
from typing import Literal

from langgraph.graph import END, START, StateGraph
from sqlalchemy.orm import Session

from app.agents.nodes import (
    assess_risk_node,
    decide_action_node,
    escalate_node,
    failed_node,
    guardrail_node,
    human_review_node,
    load_context_node,
    resolve_node,
    llm_investigation_node,
)
from app.agents.state import FinanceAgentState


def route_after_context(
    state: FinanceAgentState,
) -> Literal[
    "assess_risk",
    "failed",
]:
    """
    Route execution after loading the exception
    and transaction context.
    """

    if state.get("error"):
        return "failed"

    return "assess_risk"


def route_after_guardrail(
    state: FinanceAgentState,
) -> Literal[
    "resolve",
    "human_review",
    "escalate",
]:
    """
    Determine the final execution path.

    Guardrails always have authority over the
    final action.
    """

    # Any guardrail failure goes to human review.
    if not state.get("guardrail_passed"):
        return "human_review"

    recommendation = state.get(
        "recommendation"
    )

    if recommendation == "AUTO_RESOLVE":
        return "resolve"

    if recommendation == "HUMAN_REVIEW":
        return "human_review"

    return "escalate"


def build_finance_graph(
    db: Session,
):
    """
    Build and compile the finance controller
    LangGraph workflow.
    """

    builder = StateGraph(
        FinanceAgentState
    )

    # --------------------------------------------------
    # NODES
    # --------------------------------------------------

    builder.add_node(
        "load_context",
        partial(
            load_context_node,
            db=db,
        ),
    )

    builder.add_node(
        "assess_risk",
        assess_risk_node,
    )

    builder.add_node(
        "decide_action",
        decide_action_node,
    )

    builder.add_node(
        "llm_investigation",
        llm_investigation_node,
    )

    builder.add_node(
        "guardrail",
        guardrail_node,
    )

    builder.add_node(
        "resolve",
        resolve_node,
    )

    builder.add_node(
        "human_review",
        human_review_node,
    )

    builder.add_node(
        "escalate",
        escalate_node,
    )

    builder.add_node(
        "failed",
        failed_node,
    )

    # --------------------------------------------------
    # START
    # --------------------------------------------------

    builder.add_edge(
        START,
        "load_context",
    )

    # --------------------------------------------------
    # CONTEXT → RISK
    # --------------------------------------------------

    builder.add_conditional_edges(
        "load_context",
        route_after_context,
    )

    # --------------------------------------------------
    # RISK → DECISION
    # --------------------------------------------------

    builder.add_edge(
        "assess_risk",
        "decide_action",
    )

    # --------------------------------------------------
    # DECISION → LLM INVESTIGATION
    # --------------------------------------------------

    builder.add_edge(
        "decide_action",
        "llm_investigation",
    )

    # --------------------------------------------------
    # LLM INVESTIGATION → GUARDRAIL
    # --------------------------------------------------

    builder.add_edge(
        "llm_investigation",
        "guardrail",
    )

    # --------------------------------------------------
    # GUARDRAIL → FINAL ACTION
    # --------------------------------------------------

    builder.add_conditional_edges(
        "guardrail",
        route_after_guardrail,
    )

    # --------------------------------------------------
    # TERMINAL NODES
    # --------------------------------------------------

    builder.add_edge(
        "resolve",
        END,
    )

    builder.add_edge(
        "human_review",
        END,
    )

    builder.add_edge(
        "escalate",
        END,
    )

    builder.add_edge(
        "failed",
        END,
    )

    return builder.compile()