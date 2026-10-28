"""Tests for the data and calculation layer.

These cover utils/ only. They import no Streamlit, so they run in well under a
second and do not need a browser or a script run. The page smoke tests in
tests/test_pages.py cover the Streamlit side.
"""

import pandas as pd
import pytest

from utils import calc_costs, calc_emissions, io, scoring


# --- io --------------------------------------------------------------------

def test_no_data_file_is_empty():
    """Every CSV the loaders promise has at least one row.

    This repo previously shipped six zero-byte CSVs and four zero-byte modules,
    so the dashboard advertised a data layer that did not exist.
    """
    for path in sorted(io.DATA_DIR.glob("*.csv")):
        assert path.stat().st_size > 0, f"{path.name} is empty"
        assert len(pd.read_csv(path)) > 0, f"{path.name} has a header but no rows"


def test_loaders_return_declared_columns():
    for loader in (
        io.load_sites, io.load_scenarios, io.load_cost_catalog, io.load_vendors,
        io.load_raid_log, io.load_change_log, io.load_standards_checklist,
        io.load_site_standards_status,
    ):
        assert len(loader()) > 0


def test_load_csv_names_the_missing_column():
    with pytest.raises(ValueError, match="nonexistent_column"):
        io.load_csv("sites.csv", required=("site", "nonexistent_column"))


def test_load_csv_reports_a_missing_file():
    with pytest.raises(FileNotFoundError):
        io.load_csv("not_a_real_file.csv")


def test_loaders_are_cwd_independent(tmp_path, monkeypatch):
    """Paths are anchored to the package, not the process working directory."""
    monkeypatch.chdir(tmp_path)
    assert len(io.load_sites()) > 0


def test_cost_catalog_joins_to_scenarios_and_sites():
    """Every catalog row must name a real scenario flag and a real site column."""
    catalog = io.load_cost_catalog()
    scenario_columns = set(io.load_scenarios().columns)
    site_columns = set(io.load_sites().columns)
    for _, row in catalog.iterrows():
        assert row["flag_column"] in scenario_columns, row["flag_column"]
        assert row["basis"] in site_columns, row["basis"]


def test_site_standards_status_references_known_codes_and_sites():
    status = io.load_site_standards_status()
    codes = set(io.load_standards_checklist()["standard_code"])
    sites = set(io.load_sites()["site"])
    assert set(status["standard_code"]) <= codes
    assert set(status["site"]) <= sites


def test_compliance_register_covers_every_site_and_control():
    register = io.compliance_register()
    n_sites = len(io.load_sites())
    n_controls = len(io.load_standards_checklist())
    assert len(register) == n_sites * n_controls
    assert register["standard"].notna().all(), "join left an unmatched standard_code"


def test_compliance_register_filters_to_one_site():
    site = io.load_sites()["site"].iloc[0]
    register = io.compliance_register(site)
    assert set(register["site"]) == {site}
    assert len(register) == len(io.load_standards_checklist())


# --- calc_costs ------------------------------------------------------------

def test_baseline_scenario_has_no_capex():
    """The do-nothing comparator must cost nothing, not a default per-sqm figure."""
    sites, scenarios, catalog = io.load_sites(), io.load_scenarios(), io.load_cost_catalog()
    site = sites.iloc[0]
    baseline = scenarios[scenarios["scenario"] == "Baseline"].iloc[0]
    assert calc_costs.scenario_capex(site, baseline, catalog) == 0.0
    assert calc_costs.capex_breakdown(site, baseline, catalog).empty


def test_capex_rises_with_scenario_ambition():
    sites, scenarios, catalog = io.load_sites(), io.load_scenarios(), io.load_cost_catalog()
    site = sites.iloc[0]
    costs = [
        calc_costs.scenario_capex(site, scenarios[scenarios["scenario"] == name].iloc[0], catalog)
        for name in ["Baseline", "Efficiency Pack", "Efficiency + Green Roof", "Full Package"]
    ]
    assert costs == sorted(costs), costs
    assert costs[0] == 0 and costs[-1] > 0


def test_green_roof_measure_uses_roof_area_not_office_area():
    """A roof measure priced off office area would overstate CAPEX ~4x here."""
    sites, scenarios, catalog = io.load_sites(), io.load_scenarios(), io.load_cost_catalog()
    site = sites.iloc[0]
    scenario = scenarios[scenarios["scenario"] == "Efficiency + Green Roof"].iloc[0]
    breakdown = calc_costs.capex_breakdown(site, scenario, catalog)
    roof_rows = breakdown[breakdown["basis"] == "roof_area_sqm"]
    assert len(roof_rows) == 1
    assert roof_rows.iloc[0]["quantity_sqm"] == float(site["roof_area_sqm"])


def test_capex_breakdown_rejects_an_unknown_cost_basis():
    site = io.load_sites().iloc[0]
    scenario = pd.Series({"lighting_upgrade": 1})
    catalog = pd.DataFrame([{
        "measure": "Bad basis", "flag_column": "lighting_upgrade",
        "basis": "not_a_site_column", "unit_cost_eur": 10, "lifetime_years": 5,
    }])
    with pytest.raises(ValueError, match="not_a_site_column"):
        calc_costs.capex_breakdown(site, scenario, catalog)


def test_energy_saved_never_goes_negative():
    assert calc_costs.energy_saved_kwh(100, 150) == 0.0
    assert calc_costs.energy_saved_kwh(150, 100) == 50.0


@pytest.mark.parametrize(
    "capex, saving, expected",
    [(100_000.0, 25_000.0, 4.0), (0.0, 0.0, 0.0), (0.0, 5_000.0, 0.0)],
)
def test_payback_years(capex, saving, expected):
    assert calc_costs.payback_years(capex, saving) == expected


def test_payback_is_undefined_when_capex_never_pays_back():
    assert calc_costs.payback_years(100_000.0, 0.0) is None


def test_roi_summary_defaults_to_the_scenario_target():
    """The scenario drives savings as well as CAPEX — it used to drive neither."""
    sites, scenarios, catalog = io.load_sites(), io.load_scenarios(), io.load_cost_catalog()
    site = sites.iloc[0]
    scenario = scenarios[scenarios["scenario"] == "Full Package"].iloc[0]
    result = calc_costs.roi_summary(site, scenario, catalog)
    expected_target = float(site["office_area_sqm"]) * float(scenario["target_kwh_per_sqm"])
    assert result["target_kwh"] == expected_target
    assert result["annual_eur_saved"] > 0
    assert result["payback_years"] > 0


# --- calc_emissions --------------------------------------------------------

def test_europe_factor_matches_the_previous_hardcoded_value():
    """Kept at 0.000233 so figures published before the refactor reconcile."""
    assert calc_emissions.grid_intensity("Europe") == 0.000233


def test_grid_intensity_varies_by_region_and_falls_back_safely():
    assert calc_emissions.grid_intensity("Asia") > calc_emissions.grid_intensity("Europe")
    assert calc_emissions.grid_intensity("Atlantis") == calc_emissions.DEFAULT_GRID_INTENSITY_T_PER_KWH
    assert calc_emissions.grid_intensity(None) == calc_emissions.DEFAULT_GRID_INTENSITY_T_PER_KWH


def test_every_site_region_has_an_explicit_factor():
    """A new region in sites.csv silently inheriting the EU average is a trap."""
    regions = set(io.load_sites()["region"])
    missing = regions - set(calc_emissions.GRID_INTENSITY_T_PER_KWH)
    assert not missing, f"no explicit grid factor for: {sorted(missing)}"


def test_same_saving_is_worth_more_carbon_in_a_dirtier_grid():
    eu = calc_emissions.emissions_saved_t(500_000, 400_000, "Europe")
    asia = calc_emissions.emissions_saved_t(500_000, 400_000, "Asia")
    assert asia > eu


def test_emissions_saved_never_negative():
    assert calc_emissions.emissions_saved_t(100_000, 200_000, "Europe") == 0.0


@pytest.mark.parametrize("pct, expected_fraction", [(0, 0.0), (50, 0.5), (100, 1.0)])
def test_green_roof_area_scales_with_percent(pct, expected_fraction):
    summary = calc_emissions.green_roof_summary(1000.0, pct)
    assert summary["green_roof_area_sqm"] == 1000.0 * expected_fraction


@pytest.mark.parametrize("pct", [-10, 150])
def test_green_roof_percent_is_clamped(pct):
    """A stray slider value must not create area larger than the roof."""
    summary = calc_emissions.green_roof_summary(1000.0, pct)
    assert 0.0 <= summary["green_roof_area_sqm"] <= 1000.0


# --- scoring ---------------------------------------------------------------

def test_weights_normalise_to_one():
    weights = scoring.normalise_weights(35, 35, 30)
    assert sum(weights.values()) == pytest.approx(1.0)


def test_only_the_ratio_of_weights_matters():
    assert scoring.normalise_weights(1, 1, 1) == scoring.normalise_weights(50, 50, 50)


def test_all_zero_weights_return_none_rather_than_dividing_by_zero():
    assert scoring.normalise_weights(0, 0, 0) is None
    vendor = io.load_vendors().iloc[0]
    assert scoring.vendor_score(vendor, 0, 0, 0) is None


def test_vendor_score_is_bounded_and_decomposed():
    for _, vendor in io.load_vendors().iterrows():
        result = scoring.vendor_score(vendor, 35, 35, 30)
        assert 0.0 <= result["total"] <= 1.0
        for key in ("cost_score", "quality_score", "sustainability_score"):
            assert 0.0 <= result[key] <= 1.0


def test_shorter_lead_time_scores_better_on_cost():
    fast = pd.Series({"lead_time_weeks": 4, "rating": 4.0, "certs": "ISO 9001"})
    slow = pd.Series({"lead_time_weeks": 16, "rating": 4.0, "certs": "ISO 9001"})
    assert (
        scoring.vendor_score(fast, 100, 0, 0)["total"]
        > scoring.vendor_score(slow, 100, 0, 0)["total"]
    )


def test_environmental_certification_lifts_the_sustainability_component():
    certified = pd.Series({"lead_time_weeks": 8, "rating": 4.0, "certs": "ISO 14001"})
    uncertified = pd.Series({"lead_time_weeks": 8, "rating": 4.0, "certs": "ISO 9001"})
    assert (
        scoring.vendor_score(certified, 0, 0, 100)["total"]
        > scoring.vendor_score(uncertified, 0, 0, 100)["total"]
    )


def test_compliance_rate_and_empty_input():
    assert scoring.compliance_rate(pd.Series(["Completed", "Completed"])) == 100.0
    assert scoring.compliance_rate(pd.Series(["Completed", "Planned"])) == 50.0
    assert scoring.compliance_rate(pd.Series([], dtype=object)) == 0.0


@pytest.mark.parametrize(
    "pct, band", [(100, "Green"), (80, "Green"), (79.9, "Amber"), (50, "Amber"), (49.9, "Red"), (0, "Red")]
)
def test_rag_bands_at_their_boundaries(pct, band):
    assert scoring.rag_status(pct) == band


@pytest.mark.parametrize(
    "impact, likelihood, score, band",
    [
        ("High", "High", 9, "Critical"),
        ("High", "Medium", 6, "High"),
        ("Medium", "High", 6, "High"),
        ("Medium", "Medium", 4, "Medium"),
        ("High", "Low", 3, "Medium"),
        ("Medium", "Low", 2, "Low"),
        ("Low", "Low", 1, "Low"),
    ],
)
def test_risk_severity_covers_every_attainable_score(impact, likelihood, score, band):
    result = scoring.risk_severity(impact, likelihood)
    assert result["score"] == score
    assert result["band"] == band


def test_every_risk_band_is_reachable():
    """Thresholds must not make a band unreachable from any impact/likelihood pair."""
    bands = {
        scoring.risk_severity(i, l)["band"]
        for i in scoring.RISK_RANK for l in scoring.RISK_RANK
    }
    assert bands == {"Low", "Medium", "High", "Critical"}


def test_unknown_impact_scores_zero_rather_than_guessing():
    assert scoring.risk_severity("Catastrophic", "High")["score"] == 0


def test_raid_log_uses_known_impact_and_likelihood_values():
    """An unrecognised value scores 0 and would hide a real risk."""
    raid = io.load_raid_log()
    assert set(raid["impact"]) <= set(scoring.RISK_RANK)
    assert set(raid["likelihood"]) <= set(scoring.RISK_RANK)
