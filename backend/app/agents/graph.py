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
    retrieve_policies_node,
    llm_investigation_node,
    mcp_evidence_node,
)
from app.agents.state import FinanceAgentState


def route_after_context(
    state: FinanceAgentState,
) -> Literal[
    "mcp_evidence",
    "failed",
]:
    if state.get("error"):
        return "failed"

    return "mcp_evidence"


def route_after_guardrail(
    state: FinanceAgentState,
) -> Literal[
    "resolve",
    "human_review",
    "escalate",
]:
    if not state.get("guardrail_passed"):
        return "human_review"

    recommendation = state.get("recommendation")

    if recommendation == "AUTO_RESOLVE":
        return "resolve"

    if recommendation == "HUMAN_REVIEW":
        return "human_review"

    return "escalate"


def build_finance_graph(
    db: Session,
):
    builder = StateGraph(
        FinanceAgentState
    )

    # -------------------------
    # Nodes
    # -------------------------

    builder.add_node(
        "load_context",
        partial(
            load_context_node,
            db=db,
        ),
    )

    builder.add_node(
        "mcp_evidence",
        mcp_evidence_node,
    )

    builder.add_node(
        "retrieve_policies",
        partial(
            retrieve_policies_node,
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

    # -------------------------
    # Start
    # -------------------------

    builder.add_edge(
        START,
        "load_context",
    )

    # -------------------------
    # Context -> RAG
    # -------------------------

    builder.add_conditional_edges(
        "load_context",
        route_after_context,
    )

    builder.add_edge(
        "mcp_evidence",
        "retrieve_policies",
    )

    # -------------------------
    # RAG -> Risk
    # -------------------------

    builder.add_edge(
        "retrieve_policies",
        "assess_risk",
    )

    # -------------------------
    # Risk -> Decision
    # -------------------------

    builder.add_edge(
        "assess_risk",
        "decide_action",
    )

    # -------------------------
    # Decision -> LLM
    # -------------------------

    builder.add_edge(
        "decide_action",
        "llm_investigation",
    )

    # -------------------------
    # LLM -> Guardrail
    # -------------------------

    builder.add_edge(
        "llm_investigation",
        "guardrail",
    )

    # -------------------------
    # Guardrail -> Action
    # -------------------------

    builder.add_conditional_edges(
        "guardrail",
        route_after_guardrail,
    )

    # -------------------------
    # End states
    # -------------------------

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