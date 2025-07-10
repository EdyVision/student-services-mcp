import os
import random
import uuid
import pandas as pd
import json
from datetime import datetime
from faker import Faker

fake = Faker(locale="en_US")

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
    "Biology",
    "Chemistry",
    "Physics",
    "Nursing",
    "Education",
    "Economics",
]


def generate_courses_for_term(major, term_index, gpa, target_credits):
    """Generate courses for a specific term based on major and progression."""
    # Course prefixes by major
    major_to_prefix = {
        "Computer Science": "CS",
        "Engineering": "ENG",
        "Mathematics": "MATH",
        "IT": "IT",
        "Statistics": "STAT",
        "Psychology": "PSY",
        "Sociology": "SOC",
        "Social Work": "SW",
        "Anthropology": "ANTH",
        "Paralegal": "PARA",
        "Law": "LAW",
        "Business": "BUS",
        "English": "ENG",
        "History": "HIST",
        "Philosophy": "PHIL",
        "Art": "ART",
        "Music": "MUS",
        "Biology": "BIO",
        "Chemistry": "CHEM",
        "Physics": "PHYS",
        "Nursing": "NURS",
        "Education": "EDU",
        "Economics": "ECON",
    }

    # Course titles by major
    major_courses = {
        "Computer Science": [
            "Introduction to Programming",
            "Data Structures",
            "Algorithms",
            "Database Systems",
            "Software Engineering",
            "Machine Learning",
            "Computer Networks",
            "Operating Systems",
            "Web Development",
        ],
        "Engineering": [
            "Engineering Fundamentals",
            "Thermodynamics",
            "Fluid Mechanics",
            "Materials Science",
            "Control Systems",
            "Design Project",
            "Statics",
            "Dynamics",
            "Circuit Analysis",
        ],
        "Psychology": [
            "General Psychology",
            "Cognitive Psychology",
            "Research Methods",
            "Statistics",
            "Abnormal Psychology",
            "Social Psychology",
            "Developmental Psychology",
            "Personality Psychology",
            "Neuroscience",
        ],
        "Business": [
            "Business Fundamentals",
            "Marketing",
            "Finance",
            "Accounting",
            "Operations Management",
            "Strategic Management",
            "Business Ethics",
            "Economics",
            "Management",
        ],
        "Biology": [
            "General Biology",
            "Genetics",
            "Cell Biology",
            "Ecology",
            "Biochemistry",
            "Molecular Biology",
            "Anatomy",
            "Physiology",
            "Microbiology",
        ],
        "Mathematics": [
            "Calculus I",
            "Calculus II",
            "Calculus III",
            "Linear Algebra",
            "Differential Equations",
            "Statistics",
            "Abstract Algebra",
            "Discrete Math",
            "Number Theory",
        ],
        "English": [
            "English Composition",
            "Literature Survey",
            "American Literature",
            "British Literature",
            "Creative Writing",
            "Poetry",
            "Drama",
            "Rhetoric",
            "Linguistics",
        ],
        "History": [
            "World History",
            "American History",
            "European History",
            "Ancient History",
            "Modern History",
            "Historical Research",
            "Historiography",
            "Cultural History",
            "Political History",
        ],
        "Nursing": [
            "Fundamentals of Nursing",
            "Anatomy & Physiology",
            "Pharmacology",
            "Medical-Surgical Nursing",
            "Pediatric Nursing",
            "Mental Health Nursing",
            "Community Health",
            "Nursing Leadership",
            "Clinical Practice",
        ],
    }

    prefix = major_to_prefix.get(major, "GEN")
    course_titles = major_courses.get(
        major,
        [
            "Introduction to Field",
            "Advanced Topics",
            "Research Methods",
            "Seminar",
            "Practicum",
            "Capstone Project",
        ],
    )

    # Generate grade based on GPA
    def get_grade(gpa):
        if gpa >= 3.8:
            return random.choice(["A", "A", "A", "A-", "A-", "B+"])
        elif gpa >= 3.5:
            return random.choice(["A", "A-", "A-", "B+", "B+", "B"])
        elif gpa >= 3.2:
            return random.choice(["A-", "B+", "B+", "B", "B", "B-"])
        elif gpa >= 2.8:
            return random.choice(["B+", "B", "B", "B-", "B-", "C+"])
        elif gpa >= 2.5:
            return random.choice(["B", "B-", "C+", "C+", "C", "C"])
        elif gpa >= 2.2:
            return random.choice(["B-", "C+", "C", "C", "C-", "C-"])
        else:
            return random.choice(["C+", "C", "C-", "D+", "D", "D"])

    # Calculate number of courses needed for target credits
    num_courses = max(2, target_credits // 3)  # Usually 3-4 credits per course
    courses = []

    for i in range(num_courses):
        # Course number increases with term progression and course index
        course_number = 100 + (term_index * 100) + (i * 10) + random.randint(1, 9)
        course_code = f"{prefix}{course_number}"

        # Select course title
        title = course_titles[i % len(course_titles)]
        if i >= len(course_titles):
            title = f"Advanced {title}"

        credits = random.choice([3, 4])  # Most courses are 3 or 4 credits
        grade = get_grade(gpa)

        courses.append(
            {
                "course_code": course_code,
                "title": title,
                "credits": credits,
                "grade": grade,
            }
        )

    return courses


def generate_student():
    """Generate a synthetic student record."""
    gpa = round(random.uniform(2.0, 4.0), 2)
    student_id = f"S{uuid.uuid4().hex[:5].upper()}"
    major = random.choice(FIELDS_OF_STUDY)

    # Generate graduation goals (2-5 years)
    graduation_years = random.randint(2, 5)
    graduation_goals = [
        f"graduate in {graduation_years} years",
        f"complete degree in {graduation_years} years",
        f"finish program within {graduation_years} years",
    ]

    # Generate varying work hours (0-40 hours)
    work_hours = random.choice([0, 10, 15, 20, 25, 30, 35, 40])

    # Generate past terms with varying stress levels, credit loads, and courses
    terms = ["Fall 2023", "Spring 2024", "Summer 2024", "Fall 2024", "Spring 2025"]
    stress_levels = ["low", "moderate", "high"]
    num_past_terms = random.randint(1, 4)

    past_terms = []
    for i in range(num_past_terms):
        term = random.choice(terms)
        # Remove used term to avoid duplicates
        if term in terms:
            terms.remove(term)

        target_credits = random.choice([9, 12, 15, 18, 21])  # Varying credit loads
        stress = random.choice(stress_levels)

        # Generate courses for this term
        courses = generate_courses_for_term(major, i, gpa, target_credits)
        actual_credits = sum(course["credits"] for course in courses)

        past_terms.append(
            {
                "term": term,
                "credits": actual_credits,
                "stress": stress,
                "courses": courses,
            }
        )

    max_credits = max(term["credits"] for term in past_terms)
    enrollment_status = "Full-time" if max_credits > 11 else "Part-time"

    return {
        "student_id": student_id,
        "name": fake.name(),
        "email": f"{student_id.lower()}@university.edu",
        "phone": f"555-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
        "address": f"{random.randint(100, 999)} University Ave, College Town, CT {random.randint(10000, 99999)}",
        "enrollment_status": enrollment_status,
        "major": major,
        "year": random.choice(["Freshman", "Sophomore", "Junior", "Senior"]),
        "gpa": gpa,
        "work_hours": work_hours,
        "goal": random.choice(graduation_goals),
        "past_terms": json.dumps(past_terms),
        "notes": json.dumps([]),
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

    # GPA-based awards
    if gpa >= 3.8:
        financial_aid.append("Presidential Scholarship")
        requirements.append("GPA ≥ 3.8")
    elif gpa >= 3.6:
        financial_aid.append("Dean's Merit Scholarship")
        requirements.append("GPA ≥ 3.6")
    elif gpa >= 3.2:
        financial_aid.append("Academic Achievement Grant")
        requirements.append("GPA ≥ 3.2")

    # Field-specific awards
    if field_of_study in [
        "Computer Science",
        "Engineering",
        "Mathematics",
        "IT",
        "Statistics",
        "Biology",
        "Chemistry",
        "Physics",
    ]:
        financial_aid.append("STEM Excellence Award")
        requirements.append("Field of Study in STEM")

    if field_of_study in ["Psychology", "Sociology", "Social Work", "Anthropology"]:
        financial_aid.append("Behavioral and Social Sciences Grant")
        requirements.append("Field of Study in Behavioral and Social Sciences")

    if field_of_study in ["Paralegal", "Law"]:
        financial_aid.append("Legal Studies Full Ride")
        requirements.append("Field of Study in Legal Studies")

    if field_of_study in ["English", "History", "Philosophy", "Art", "Music"]:
        financial_aid.append("Liberal Arts Fellowship")
        requirements.append("Field of Study in Liberal Arts")

    if field_of_study in ["Business", "Economics"]:
        financial_aid.append("Business Leadership Scholarship")
        requirements.append("Field of Study in Business/Economics")

    if field_of_study in ["Nursing", "Education"]:
        financial_aid.append("Public Service Grant")
        requirements.append("Field of Study in Public Service")

    # Need-based aid (for students with lower GPAs who don't qualify for merit aid)
    if gpa < 3.2 and len(financial_aid) == 0:
        financial_aid.append("Need-Based Grant")
        requirements.append("Demonstrated Financial Need")

    # Special combined awards for high achievers in specific fields
    if gpa >= 3.6 and field_of_study in [
        "Computer Science",
        "Engineering",
        "Mathematics",
    ]:
        financial_aid.append("STEM Leadership Award")
        requirements.append("GPA ≥ 3.6 + STEM Field")

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
