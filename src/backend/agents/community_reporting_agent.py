"""
Community Reporting Agent.

Stores an anonymised test result and, when the reading is unsafe, raises a
community hazard alert in a pending-review state. The alert is not published
until a reviewer (NGO or public-health admin) approves it. Persistence uses the
AWS DB tool and degrades gracefully when the database is unavailable.
"""
from tools.aws_db_tool import store_user_result
from agents.schemas import CommunityReport
from agents.state import GraphState


def community_reporting_agent(state: GraphState) -> dict:
    request = state["request"]
    quality = state["quality"]

    record = {
        "anonymised_user_id": request.user_id,
        "area": request.location,
        "overall_risk": quality.overall_risk,
        "failed_parameters": quality.failed_parameters,
        "recommended_action": "; ".join(state["treatment"].steps) if state.get("treatment") else "",
    }
    persist = store_user_result(record)

    alert_status = "none"
    escalation = ""
    if quality.overall_risk == "unsafe":
        alert_status = "pending_review"
        escalation = (
            f"Unsafe reading in {request.location or 'this area'} "
            f"({', '.join(quality.failed_parameters)}). Alert awaiting reviewer approval."
        )

    report = CommunityReport(
        area=request.location,
        anonymised_user_id=request.user_id,
        overall_risk=quality.overall_risk,
        failed_parameters=quality.failed_parameters,
        alert_status=alert_status,
        escalation=escalation,
    )

    out = {"community": report}
    if not persist["persisted"]:
        warnings = list(state.get("warnings", []))
        warnings.append(f"Community result not persisted: {persist['note']}")
        out["warnings"] = warnings
    return out
