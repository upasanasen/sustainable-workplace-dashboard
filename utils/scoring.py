"""Vendor scoring, compliance rates and RAG banding.

The vendor formula is the one that was inline on the procurement page, kept
deliberately unchanged so published scorecards still reconcile; it is moved here
so it can be tested and so the weight handling has one definition instead of
being re-derived per page.
"""

from __future__ import annotations

import pandas as pd

# A vendor at or beyond this lead time scores zero on cost.
LEAD_TIME_CEILING_WEEKS = 20.0
MAX_RATING = 5.0
# Credit for a vendor holding the environmental management certification.
SUSTAINABILITY_CERTIFIED_SCORE = 1.0
SUSTAINABILITY_UNCERTIFIED_SCORE = 0.7
SUSTAINABILITY_CERT = "ISO 14001"

RISK_RANK = {"Low": 1, "Medium": 2, "High": 3}


def normalise_weights(cost: float, quality: float, sustainability: float) -> dict | None:
    """Scale three weights to sum to 1, or None if they are all zero."""
    total = float(cost) + float(quality) + float(sustainability)
    if total <= 0:
        return None
    return {
        "cost": float(cost) / total,
        "quality": float(quality) / total,
        "sustainability": float(sustainability) / total,
    }


def vendor_score(vendor: pd.Series, cost_weight: float, quality_weight: float,
                 sustainability_weight: float) -> dict | None:
    """Weighted 0-1 score for one vendor, with its components exposed.

    Returns None when every weight is zero, which the caller surfaces as a
    prompt rather than dividing by zero.
    """
    weights = normalise_weights(cost_weight, quality_weight, sustainability_weight)
    if weights is None:
        return None

    cost_score = 1.0 - min(float(vendor["lead_time_weeks"]) / LEAD_TIME_CEILING_WEEKS, 1.0)
    quality_score = min(float(vendor["rating"]) / MAX_RATING, 1.0)
    certified = SUSTAINABILITY_CERT in str(vendor.get("certs", ""))
    sustainability_score = (
        SUSTAINABILITY_CERTIFIED_SCORE if certified else SUSTAINABILITY_UNCERTIFIED_SCORE
    )

    total = (
        weights["cost"] * cost_score
        + weights["quality"] * quality_score
        + weights["sustainability"] * sustainability_score
    )
    return {
        "total": total,
        "cost_score": cost_score,
        "quality_score": quality_score,
        "sustainability_score": sustainability_score,
        "weights": weights,
    }


def compliance_rate(status: pd.Series) -> float:
    """Share of controls marked Completed, as a percentage. Empty input is 0."""
    if len(status) == 0:
        return 0.0
    return float((status == "Completed").sum()) / float(len(status)) * 100.0


def rag_status(percent_complete: float) -> str:
    """RAG band for a completion percentage."""
    pct = float(percent_complete)
    if pct >= 80:
        return "Green"
    if pct >= 50:
        return "Amber"
    return "Red"


def risk_severity(impact: str, likelihood: str) -> dict:
    """Impact x likelihood on the 1-3 scale, banded for display."""
    impact_rank = RISK_RANK.get(str(impact), 0)
    likelihood_rank = RISK_RANK.get(str(likelihood), 0)
    score = impact_rank * likelihood_rank
    # Attainable scores are 1, 2, 3, 4, 6 and 9. Thresholds are set so each
    # band is actually reachable: 9 Critical, 6 High, 3-4 Medium, 1-2 Low.
    if score >= 9:
        band = "Critical"
    elif score >= 6:
        band = "High"
    elif score >= 3:
        band = "Medium"
    else:
        band = "Low"
    return {"score": score, "band": band,
            "impact_rank": impact_rank, "likelihood_rank": likelihood_rank}
