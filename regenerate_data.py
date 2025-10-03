#!/usr/bin/env python3
"""
Script to regenerate synthetic student data with new fields.
"""

import sys
import os

# Add src to path to import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src.adapters.systems.synthetic_data import build_synthetic_data


def main():
    """Regenerate synthetic data with approximately 35,000 students."""
    print("Regenerating synthetic student data...")

    # Generate the same number of students as before (35,000)
    synthetic_population_data, financial_aid_determinations = build_synthetic_data(
        num_students=35000, directory="dist/data"
    )

    print(f"Generated {len(synthetic_population_data)} student records")
    print(f"Generated {len(financial_aid_determinations)} financial aid determinations")
    print("Data saved to dist/data/")

    # Show a sample of the new data structure
    print("\nSample student record:")
    import json

    sample = synthetic_population_data[0]
    for key, value in sample.items():
        if key == "past_terms":
            print(f"  {key}: {json.loads(value)}")
        elif key == "notes":
            print(f"  {key}: {json.loads(value)}")
        elif key != "financial_status":
            print(f"  {key}: {value}")

    print("\nData regeneration complete!")


if __name__ == "__main__":
    main()
