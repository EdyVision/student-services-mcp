# systems/synthetic_data.py
import os
import random
import uuid
import pandas as pd
from datetime import datetime

# List of fields of study
FIELDS_OF_STUDY = [
    "Computer Science",
    "Engineering",
    "Mathematics",
    "IT",
    "Statistics",
    "Psychology",
    "Sociology",
    "Social Work",
    "Anthropology",
    "Paralegal",
    "Law",
    "Business",
    "English",
    "History",
    "Philosophy",
    "Art",
    "Music",
]


def generate_student():
    """Generate a synthetic student record."""
    gpa = round(random.uniform(2.0, 4.0), 2)
    student_id = f"S{uuid.uuid4().hex[:5].upper()}"

    return {
        "student_id": student_id,
        "name": random.choice(
            ["Alice", "Bob", "Charlie", "Diana", "Evan", "Fiona", "George"]
        )
        + " "
        + random.choice(
            ["Smith", "Johnson", "Williams", "Brown", "Jones", "Miller", "Davis"]
        ),
        "email": f"{student_id.lower()}@university.edu",
        "phone": f"555-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
        "address": f"{random.randint(100, 999)} University Ave, College Town, CT {random.randint(10000, 99999)}",
        "enrollment_status": random.choice(["Full-time", "Part-time"]),
        "major": random.choice(FIELDS_OF_STUDY),
        "year": random.choice(["Freshman", "Sophomore", "Junior", "Senior"]),
        "gpa": gpa,
        "financial_status": {
            "efc": random.randint(0, 20000),
            "dependency_status": random.choice(["Independent", "Dependent"]),
            "household_income": random.randint(20000, 100000),
            "household_size": random.randint(1, 6),
        },
    }


def determine_financial_aid_eligibility(gpa, field_of_study):
    """
    Uses a student record to determine coverage against defined parameters
    """
    financial_aid = []
    requirements = []

    if gpa >= 3.6:
        requirements.append("GPA ≥ 3.6")

    if field_of_study in [
        "Computer Science",
        "Engineering",
        "Mathematics",
        "IT",
        "Statistics",
    ]:
        financial_aid.append("STEM Excellence Award")
        requirements.append("Field of Study in STEM")

    if field_of_study in ["Psychology", "Sociology", "Social Work", "Anthropology"]:
        financial_aid.append("Behavioral and Social Sciences Grant")
        requirements.append("Field of Study in Behavioral and Social Sciences")

    if field_of_study in ["Paralegal", "Law"]:
        financial_aid.append("Legal Studies Full Ride")
        requirements.append("Field of Study in Legal Studies")

    return requirements, financial_aid


def build_synthetic_data(num_students=50, directory="dist/data"):
    """Generate synthetic student data and financial aid determinations."""
    # Create directory if it doesn't exist
    os.makedirs(directory, exist_ok=True)

    # Generate synthetic student records
    synthetic_population_data = [generate_student() for _ in range(num_students)]

    # Determine financial aid eligibility for each student
    financial_aid_determinations = []
    for record in synthetic_population_data:
        requirements, financial_aid = determine_financial_aid_eligibility(
            record["gpa"], record["major"]
        )
        financial_aid_determinations.append(
            {
                "id": record["student_id"],
                "name": record["name"],
                "gpa": record["gpa"],
                "field_of_study": record["major"],
                "financial_aid": financial_aid,
                "requirements": requirements,
            }
        )

    # Save synthetic student data to CSV
    student_df = pd.DataFrame(synthetic_population_data)
    student_df.to_csv(f"{directory}/synthetic_population_data.csv", index=False)

    # Save financial aid determinations to CSV
    financial_aid_df = pd.DataFrame(financial_aid_determinations)
    financial_aid_df.to_csv(
        f"{directory}/synthetic_financial_aid_determinations.csv", index=False
    )

    return synthetic_population_data, financial_aid_determinations


def split_data_and_save(directory="dist/data"):
    """Split financial aid determinations into train, test, and validation sets."""
    # Load financial aid determinations from CSV
    data = pd.read_csv(f"{directory}/synthetic_financial_aid_determinations.csv")

    # Split data
    train = data.sample(frac=0.8, random_state=42)
    temp = data.drop(train.index)
    val = temp.sample(frac=0.5, random_state=42)
    test = temp.drop(val.index)

    # Save splits to CSV
    train.to_csv(f"{directory}/train.csv", index=False)
    val.to_csv(f"{directory}/validation.csv", index=False)
    test.to_csv(f"{directory}/test.csv", index=False)

    return train, val, test
