"""Data access for the dashboard.

Every table the app displays comes from `data/*.csv` through this module. Two
reasons it exists rather than pages calling `pd.read_csv` directly:

1. Paths. A bare `pd.read_csv("data/sites.csv")` only resolves when the process
   happens to start in the repository root, so running a page from anywhere
   else raised FileNotFoundError. Paths here are anchored to this file.
2. Schema. Each loader declares the columns it guarantees, so a malformed CSV
   fails with a message naming the file and the missing column instead of a
   KeyError several frames away in a page.

This module imports no Streamlit, which keeps the loaders and the calculation
modules testable without running a script. See tests/.
"""

from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def load_csv(name: str, required: tuple[str, ...] = ()) -> pd.DataFrame:
    """Load `data/<name>` and verify it declares `required` columns."""
    path = DATA_DIR / name
    if not path.exists():
        raise FileNotFoundError(f"Missing data file: {path}")
    df = pd.read_csv(path)
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"{name} is missing required column(s): {', '.join(missing)}")
    return df


def load_sites() -> pd.DataFrame:
    return load_csv(
        "sites.csv",
        ("site", "region", "employees", "office_area_sqm", "lat", "lon", "roof_area_sqm"),
    )


def load_scenarios() -> pd.DataFrame:
    return load_csv(
        "scenarios.csv",
        ("scenario", "lighting_upgrade", "hvac_upgrade", "green_roof",
         "low_carbon_materials", "target_kwh_per_sqm"),
    )


def load_cost_catalog() -> pd.DataFrame:
    """Unit costs per improvement measure.

    `flag_column` joins each row to the matching 0/1 column in scenarios.csv;
    `basis` names the site column the unit cost multiplies.
    """
    return load_csv(
        "cost_catalog.csv",
        ("measure", "flag_column", "basis", "unit_cost_eur", "lifetime_years"),
    )


def load_vendors() -> pd.DataFrame:
    return load_csv(
        "vendors.csv",
        ("vendor", "category", "region", "rating", "lead_time_weeks", "risk", "certs"),
    )


def load_raid_log() -> pd.DataFrame:
    """Risks, Assumptions, Issues and Dependencies, distinguished by `type`."""
    return load_csv(
        "raid_log.csv",
        ("id", "type", "title", "impact", "likelihood", "owner", "status"),
    )


def load_change_log() -> pd.DataFrame:
    return load_csv(
        "change_log.csv",
        ("id", "date", "title", "requested_by", "cost_impact_eur",
         "schedule_impact_weeks", "status"),
    )


def load_standards_checklist() -> pd.DataFrame:
    return load_csv(
        "standards_checklist.csv",
        ("standard_code", "standard", "category", "owner", "risk_if_failed"),
    )


def load_site_standards_status() -> pd.DataFrame:
    return load_csv(
        "site_standards_status.csv",
        ("site", "standard_code", "status", "evidence", "last_reviewed"),
    )


def compliance_register(site: str | None = None) -> pd.DataFrame:
    """Checklist joined to per-site status, optionally filtered to one site.

    Passing None returns every site, which is what the "All Sites" view needs.
    """
    checklist = load_standards_checklist()
    status = load_site_standards_status()
    merged = status.merge(checklist, on="standard_code", how="left", validate="many_to_one")
    if site is not None:
        merged = merged[merged["site"] == site]
    columns = ["site", "standard", "category", "owner", "status",
               "evidence", "risk_if_failed", "last_reviewed"]
    return merged[columns].reset_index(drop=True)
