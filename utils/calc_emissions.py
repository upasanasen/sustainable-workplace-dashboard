"""Operational carbon and green-roof estimates.

The inline version applied one emission factor (0.000233 t CO2e/kWh) to every
site. That is roughly right for an EU average and wrong by a wide margin across
this portfolio: Stockholm's grid is far cleaner than Singapore's, so a single
factor understates the value of saving a kWh in Asia and overstates it in the
Nordics. Factors are therefore per region, with the original value retained for
Europe so previously reported European figures still reconcile.

Figures are order-of-magnitude planning inputs, not an inventory. A real
Scope 2 calculation needs market- and location-based factors per grid per year.
"""

from __future__ import annotations

# Tonnes CO2e per kWh, location-based, illustrative regional averages.
GRID_INTENSITY_T_PER_KWH = {
    "Europe": 0.000233,
    "North America": 0.000369,
    "Asia": 0.000495,
}
DEFAULT_GRID_INTENSITY_T_PER_KWH = 0.000233

# Extensive green roof, per square metre converted.
GREEN_ROOF_SEQUESTRATION_T_PER_SQM_YEAR = 0.0005
GREEN_ROOF_COOLING_KWH_PER_SQM_YEAR = 7.0


def grid_intensity(region: str | None) -> float:
    """Factor for `region`, falling back to the EU average for unknown regions."""
    if region is None:
        return DEFAULT_GRID_INTENSITY_T_PER_KWH
    return GRID_INTENSITY_T_PER_KWH.get(str(region), DEFAULT_GRID_INTENSITY_T_PER_KWH)


def annual_emissions_t(kwh: float, region: str | None = None) -> float:
    return float(kwh) * grid_intensity(region)


def emissions_saved_t(baseline_kwh: float, target_kwh: float, region: str | None = None) -> float:
    return max(0.0, float(baseline_kwh) - float(target_kwh)) * grid_intensity(region)


def green_roof_summary(roof_area_sqm: float, converted_percent: float,
                       region: str | None = None) -> dict:
    """Converted area and the two benefits it is credited with.

    `converted_percent` is clamped to 0-100 so a stray slider value cannot
    produce an area larger than the roof.
    """
    pct = min(100.0, max(0.0, float(converted_percent)))
    area = float(roof_area_sqm) * pct / 100.0
    cooling_kwh = area * GREEN_ROOF_COOLING_KWH_PER_SQM_YEAR
    return {
        "converted_percent": pct,
        "green_roof_area_sqm": area,
        "sequestration_t_per_year": area * GREEN_ROOF_SEQUESTRATION_T_PER_SQM_YEAR,
        "cooling_saving_kwh_per_year": cooling_kwh,
        "cooling_saving_t_per_year": annual_emissions_t(cooling_kwh, region),
    }
