"""CAPEX, energy saving and payback maths for the ROI simulator.

Page 2 used to hold this inline, with one weakness worth naming: the scenario
dropdown was decorative. The user picked "Efficiency Pack" or "Full Package"
and nothing changed, because the 0/1 measure flags in scenarios.csv were never
read — CAPEX came from a single hand-set euro-per-sqm number.

`scenario_capex` closes that: each scenario flag selects rows from
cost_catalog.csv, and each row's unit cost multiplies the site column named in
its `basis`, so office-area measures and roof-area measures scale correctly.
"""

from __future__ import annotations

import pandas as pd

# Blended commercial tariff, euro per kWh. Overridable in the UI.
DEFAULT_ELECTRICITY_PRICE_EUR_PER_KWH = 0.25
DEFAULT_BASELINE_KWH_PER_SQM = 120.0


def capex_breakdown(site: pd.Series, scenario: pd.Series, catalog: pd.DataFrame) -> pd.DataFrame:
    """One row per measure the scenario switches on, with its cost.

    Measures whose flag is absent or 0 are excluded, so "Baseline" yields an
    empty frame and zero CAPEX rather than a spurious cost.
    """
    rows = []
    for _, measure in catalog.iterrows():
        flag = scenario.get(measure["flag_column"], 0)
        if not bool(int(flag)):
            continue
        basis_column = measure["basis"]
        if basis_column not in site.index:
            raise ValueError(
                f"cost_catalog.csv measure {measure['measure']!r} uses basis "
                f"{basis_column!r}, which is not a column in sites.csv"
            )
        quantity = float(site[basis_column])
        unit_cost = float(measure["unit_cost_eur"])
        rows.append(
            {
                "measure": measure["measure"],
                "basis": basis_column,
                "quantity_sqm": quantity,
                "unit_cost_eur": unit_cost,
                "capex_eur": quantity * unit_cost,
                "lifetime_years": measure.get("lifetime_years"),
            }
        )
    return pd.DataFrame(rows, columns=["measure", "basis", "quantity_sqm",
                                       "unit_cost_eur", "capex_eur", "lifetime_years"])


def scenario_capex(site: pd.Series, scenario: pd.Series, catalog: pd.DataFrame) -> float:
    breakdown = capex_breakdown(site, scenario, catalog)
    return float(breakdown["capex_eur"].sum())


def annual_kwh(office_area_sqm: float, kwh_per_sqm: float) -> float:
    return float(office_area_sqm) * float(kwh_per_sqm)


def energy_saved_kwh(baseline_kwh: float, target_kwh: float) -> float:
    """Never negative: a target above baseline is zero saving, not a penalty."""
    return max(0.0, float(baseline_kwh) - float(target_kwh))


def payback_years(capex_eur: float, annual_saving_eur: float) -> float | None:
    """None when payback is undefined, which the caller must handle explicitly.

    Zero CAPEX pays back immediately (0.0); zero saving never pays back (None).
    """
    if float(annual_saving_eur) <= 0:
        return None if float(capex_eur) > 0 else 0.0
    return float(capex_eur) / float(annual_saving_eur)


def roi_summary(
    site: pd.Series,
    scenario: pd.Series,
    catalog: pd.DataFrame,
    baseline_kwh_per_sqm: float = DEFAULT_BASELINE_KWH_PER_SQM,
    target_kwh_per_sqm: float | None = None,
    electricity_price: float = DEFAULT_ELECTRICITY_PRICE_EUR_PER_KWH,
) -> dict:
    """Full ROI picture for one site/scenario pair.

    `target_kwh_per_sqm` defaults to the scenario's own target, so the selected
    scenario drives both sides of the calculation: CAPEX via its measure flags
    and savings via its energy target.
    """
    if target_kwh_per_sqm is None:
        target_kwh_per_sqm = float(scenario["target_kwh_per_sqm"])

    office_area = float(site["office_area_sqm"])
    breakdown = capex_breakdown(site, scenario, catalog)
    capex = float(breakdown["capex_eur"].sum())

    baseline = annual_kwh(office_area, baseline_kwh_per_sqm)
    target = annual_kwh(office_area, target_kwh_per_sqm)
    saved_kwh = energy_saved_kwh(baseline, target)
    saved_eur = saved_kwh * float(electricity_price)

    return {
        "capex_eur": capex,
        "capex_breakdown": breakdown,
        "capex_per_sqm": capex / office_area if office_area else 0.0,
        "baseline_kwh": baseline,
        "target_kwh": target,
        "annual_kwh_saved": saved_kwh,
        "annual_eur_saved": saved_eur,
        "payback_years": payback_years(capex, saved_eur),
    }
