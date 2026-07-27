"""Run the complete local synthetic data pipeline."""
from generate_data import main as generate
from build_curated import main as curate

if __name__ == "__main__":
    generate()
    curate()
