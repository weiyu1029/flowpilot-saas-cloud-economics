from streamlit.testing.v1 import AppTest

PAGES = [
    "Executive Overview",
    "Feature Economics",
    "Customer Profitability",
    "AWS FinOps & Reliability",
    "Optimization Center",
    "Data & Architecture",
    "Insights Copilot",
]


def test_all_pages_render_without_exception():
    for page_name in PAGES:
        app = AppTest.from_file("streamlit_app.py", default_timeout=60).run()
        app.radio[0].set_value(page_name).run()
        assert not app.exception, [e.message for e in app.exception]
