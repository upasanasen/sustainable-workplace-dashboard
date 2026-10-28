"""Data access and calculation layer for the workplace transformation dashboard.

Streamlit-free by design: the pages in `pages/` handle layout and widgets, these
modules handle loading and arithmetic, so the logic is unit-testable without
running a script. See tests/test_data_layer.py.
"""
