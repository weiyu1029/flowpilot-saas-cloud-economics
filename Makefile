.PHONY: setup data test run clean

setup:
	python -m pip install -r requirements-dev.txt

data:
	python scripts/run_pipeline.py

test:
	pytest

run:
	streamlit run streamlit_app.py

clean:
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	rm -rf .pytest_cache
