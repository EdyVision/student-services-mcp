import os
import pandas as pd
import random


class RegistrarSystem:
    """Student Records System using synthetic data."""

    def __init__(self, data_path="../../dist/data/synthetic_population_data.csv"):
        current_dir = os.path.dirname(__file__)
        data_path = os.path.abspath(os.path.join(current_dir, data_path))

        # Initialize with empty data
        self.students = {}
        self.academic_history = {}

        # Load synthetic data if file exists
        if os.path.exists(data_path):
            try:
                df = pd.read_csv(data_path)
                # Convert dataframe to dictionary keyed by student ID
                for _, row in df.iterrows():
                    student_id = row["student_id"]

                    # Handle nested financial_status as it might be stored as a string
                    financial_status = row.get("financial_status", {})
                    if isinstance(financial_status, str):
                        try:
                            financial_status = eval(financial_status)
                        except:
                            financial_status = {}
                    self.students[student_id] = {
                        "student_id": student_id,
                        "name": row["name"],
                        "courses": row["courses"],
                        "is_need_based_qualified": random.choice([True, False]),
                        "enrollment_status": "enrolled",
                        "major": row["major"],
                        "program": row["program"],
                        "year": random.choice(
                            ["Freshman", "Sophomore", "Junior", "Senior"]
                        ),
                        "gpa": row["gpa"],
                    }

            except Exception as e:
                print(f"Error loading synthetic data: {e}")
                # If there's an error, we'll use empty data
                self.students = {}
                self.academic_history = {}
        else:
            raise FileNotFoundError(
                f"Data file not found at {data_path}. Please ensure the file exists."
            )

    def _generate_academic_history(self, student_id, major, year, gpa):
        """Generate synthetic academic history based on student data."""
        # Define which terms the student has completed based on their year
        year_to_terms = {
            "Freshman": ["Fall 2023", "Spring 2024"],
            "Sophomore": ["Fall 2022", "Spring 2023", "Fall 2023", "Spring 2024"],
            "Junior": [
                "Fall 2021",
                "Spring 2022",
                "Fall 2022",
                "Spring 2023",
                "Fall 2023",
                "Spring 2024",
            ],
            "Senior": [
                "Fall 2020",
                "Spring 2021",
                "Fall 2021",
                "Spring 2022",
                "Fall 2022",
                "Spring 2023",
                "Fall 2023",
                "Spring 2024",
            ],
        }
        student_terms = year_to_terms.get(year, ["Fall 2023", "Spring 2024"])

        # Create a mapping of majors to course prefixes
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
        }

        # Get course prefix for this major
        prefix = major_to_prefix.get(major, "GEN")

        # Generate courses
        courses = []
        credits_attempted = 0
        credits_earned = 0

        # Generate possible course titles for the major
        course_titles = [
            f"Introduction to {major}",
            f"Advanced {major}",
            f"{major} Theory",
            f"{major} Applications",
            f"Research Methods in {major}",
            f"{major} Seminar",
            f"{major} Workshop",
            f"Contemporary Issues in {major}",
        ]

        # Generate a course for each term
        for i, term in enumerate(student_terms):
            # Determine number of courses for this term (3-5)
            num_courses = random.randint(3, 5)

            for j in range(num_courses):
                # Generate course code
                course_number = 100 + (i * 100) + (j * 10)
                course_code = f"{prefix}{course_number}"

                # Select a title
                title = course_titles[j % len(course_titles)]

                # Determine credits (3-4)
                credits = random.choice([3, 4])

                # Determine grade based on GPA
                if gpa >= 3.7:
                    grade_options = ["A", "A", "A-", "B+"]
                elif gpa >= 3.3:
                    grade_options = ["A-", "B+", "B", "B-"]
                elif gpa >= 3.0:
                    grade_options = ["B+", "B", "B-", "C+"]
                elif gpa >= 2.7:
                    grade_options = ["B", "B-", "C+", "C"]
                elif gpa >= 2.3:
                    grade_options = ["B-", "C+", "C", "C-"]
                else:
                    grade_options = ["C+", "C", "C-", "D+"]

                grade = random.choice(grade_options)

                # Add course to list
                courses.append(
                    {
                        "term": term,
                        "course": course_code,
                        "title": title,
                        "credits": credits,
                        "grade": grade,
                    }
                )

                credits_attempted += credits
                credits_earned += credits

        # Add honors based on GPA
        honors = []
        if gpa >= 3.5:
            for term in student_terms[-2:]:  # Last two terms
                honors.append(f"Dean's List {term}")
        if gpa >= 3.8:
            honors.append("Academic Excellence Award")

        return {
            "courses": courses,
            "credits_attempted": credits_attempted,
            "credits_earned": credits_earned,
            "honors": honors,
        }

    async def disconnect(self):
        """Disconnect from the records system."""
        # No actual connections to close in this mock implementation
        pass

    async def get_student_profile(self, student_id: str) -> dict:
        """Get a student's profile information."""
        # TODO: This needs to call out to the live system
        return self.students.get(student_id, {"error": "Student not found"})

    async def get_student_profiles(self, num_records: int) -> dict:
        """Get a student's profile information."""
        # TODO: This needs to call out to the live system
        return list(self.students.values())[:num_records]

    async def get_academic_history(self, student_id: str) -> dict:
        """Get a student's academic history."""
        return self.academic_history.get(
            student_id, {"error": "Academic history not found"}
        )
