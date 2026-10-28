"""Headless smoke tests: every page must render without raising.

Uses Streamlit's own AppTest, so these exercise the real scripts — including the
utils imports and the data loads — without a browser.
"""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = [ROOT / "app.py"] + sorted((ROOT / "pages").glob("*.py"))


@pytest.mark.parametrize("script", SCRIPTS, ids=lambda p: p.name)
def test_page_renders_without_exception(script):
    at = AppTest.from_file(str(script), default_timeout=60).run()
    assert not at.exception, f"{script.name} raised: {at.exception}"


def test_roi_page_reacts_to_the_scenario_selector():
    """The scenario dropdown used to be decorative; CAPEX must now respond."""
    at = AppTest.from_file(str(ROOT / "pages" / "2_Cost_ROI_Simulator.py"), default_timeout=60).run()
    assert not at.exception

    at.selectbox[1].select("Baseline").run()
    baseline_capex = at.metric[0].value

    at.selectbox[1].select("Full Package").run()
    full_capex = at.metric[0].value

    assert baseline_capex != full_capex, "CAPEX did not change with the scenario"
    assert baseline_capex == "0"


def test_compliance_page_reacts_to_the_site_selector():
    """The site selector used to be read but never applied."""
    at = AppTest.from_file(str(ROOT / "pages" / "6_Standards_Compliance.py"), default_timeout=60).run()
    assert not at.exception

    at.selectbox[0].select("All Sites").run()
    all_controls = at.metric[0].value

    at.selectbox[0].select("Stockholm Office").run()
    one_site_controls = at.metric[0].value

    assert all_controls != one_site_controls
    assert one_site_controls == "6"
