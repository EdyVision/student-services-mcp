import os
import pandas as pd
import random
import json


class RegistrarSystem:
    """Student Records System using synthetic data."""

    def __init__(self, data_path="../../dist/data/synthetic_population_data.csv"):
        current_dir = os.path.dirname(__file__)
        data_path = os.path.abspath(os.path.join(current_dir, data_path))

        # Initialize with empty data
        self.students = {}

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

                    # Handle past_terms as JSON
                    past_terms = row.get("past_terms", "[]")
                    if isinstance(past_terms, str):
                        try:
                            past_terms = json.loads(past_terms)
                        except:
                            past_terms = []

                    # Handle notes as JSON
                    notes = row.get("notes", "[]")
                    if isinstance(notes, str):
                        try:
                            notes = json.loads(notes)
                        except:
                            notes = []

                    self.students[student_id] = {
                        "student_id": student_id,
                        "name": row["name"],
                        "email": row.get("email", f"{student_id}@university.edu"),
                        "phone": row.get("phone", ""),
                        "address": row.get("address", ""),
                        "enrollment_status": row.get("enrollment_status", "enrolled"),
                        "major": row["major"],
                        "year": row.get("year", "Unknown"),
                        "gpa": row["gpa"],
                        "work_hours": row.get("work_hours", 0),
                        "goal": row.get("goal", "graduate"),
                        "past_terms": past_terms,
                        "notes": notes,
                        "financial_status": financial_status,
                        "is_need_based_qualified": random.choice([True, False]),
                    }

            except Exception as e:
                print(f"Error loading synthetic data: {e}")
                # If there's an error, we'll use empty data
                self.students = {}
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
        return self.students.get(student_id, {"error": "Student not found"})

    async def get_student_profiles(self, num_records: int) -> dict:
        """Get a student's profile information."""
        return list(self.students.values())[:num_records]

    async def get_student_profile_by_name(self, student_name: str) -> dict:
        """Get a student's profile information by name (case-insensitive)."""
        for student in self.students.values():
            if student["name"].lower() == student_name.lower():
                return student
        return {"error": "Student not found"}

    async def get_academic_history(self, student_id: str) -> dict:
        """Get a student's academic history (now from past_terms)."""
        student = self.students.get(student_id)
        if not student or not student.get("past_terms"):
            return {"error": "Academic history not found"}
        return {
            "student_id": student_id,
            "name": student["name"],
            "past_terms": student["past_terms"],
        }

    async def add_note(self, student_id: str, note: str, stress_level: str) -> bool:
        """Add a note and update stress level for a student."""
        if student_id not in self.students:
            return False

        # Create note entry with timestamp
        import datetime

        note_entry = {
            "note": note,
            "stress_level": stress_level,
            "timestamp": datetime.datetime.now().isoformat(),
        }

        # Add to student's notes
        self.students[student_id]["notes"].append(note_entry)

        # Update current stress level
        self.students[student_id]["current_stress_level"] = stress_level

        return True

    async def generate_course_plan(
        self, student_id: str, target_credits: int, stress_level: str
    ) -> str:
        """Generate a course plan based on target credits and stress level."""
        if student_id not in self.students:
            return "Student not found"

        student = self.students[student_id]
        major = student["major"]
        past_terms = student["past_terms"]

        # Course recommendations based on stress level
        if stress_level == "low":
            max_courses = min(target_credits // 3, 6)  # Max 6 courses for low stress
            course_load_desc = "light course load"
        elif stress_level == "moderate":
            max_courses = min(
                target_credits // 3, 5
            )  # Max 5 courses for moderate stress
            course_load_desc = "moderate course load"
        else:  # high stress
            max_courses = min(target_credits // 3, 4)  # Max 4 courses for high stress
            course_load_desc = "manageable course load due to high stress"

        # Calculate recommended credits per course
        credits_per_course = 3 if target_credits <= 12 else 4
        total_courses = min(
            max_courses, (target_credits + credits_per_course - 1) // credits_per_course
        )

        # Generate course suggestions based on major
        major_courses = {
            "Computer Science": [
                "Data Structures",
                "Algorithms",
                "Database Systems",
                "Software Engineering",
                "Machine Learning",
            ],
            "Engineering": [
                "Thermodynamics",
                "Fluid Mechanics",
                "Materials Science",
                "Control Systems",
                "Design Project",
            ],
            "Psychology": [
                "Cognitive Psychology",
                "Research Methods",
                "Statistics",
                "Abnormal Psychology",
                "Social Psychology",
            ],
            "Business": [
                "Marketing",
                "Finance",
                "Operations Management",
                "Strategic Management",
                "Business Ethics",
            ],
            "Biology": [
                "Genetics",
                "Cell Biology",
                "Ecology",
                "Biochemistry",
                "Molecular Biology",
            ],
            "Mathematics": [
                "Calculus III",
                "Linear Algebra",
                "Differential Equations",
                "Statistics",
                "Abstract Algebra",
            ],
        }

        suggested_courses = major_courses.get(
            major, ["Core Course 1", "Core Course 2", "Elective 1", "Elective 2"]
        )

        # Build course plan
        plan = f"Recommended {course_load_desc} for {target_credits} credit hours:\n\n"

        for i in range(total_courses):
            course_name = suggested_courses[i % len(suggested_courses)]
            plan += f"• {course_name} ({credits_per_course} credits)\n"

        actual_credits = total_courses * credits_per_course

        plan += f"\nTotal: {actual_credits} credits"

        if actual_credits < target_credits:
            plan += f"\nNote: Reduced from {target_credits} credits due to {stress_level} stress level for better academic success."

        # Add study tips based on stress level
        if stress_level == "high":
            plan += "\n\nRecommendations for high stress management:\n"
            plan += "• Schedule regular study breaks\n"
            plan += "• Use campus counseling services\n"
            plan += "• Consider tutoring support\n"
            plan += "• Maintain work-life balance"

        return plan

    async def submit_course_plan(
        self, student_id: str, plan: str, justification: str
    ) -> bool:
        """Submit a course plan with justification."""
        if student_id not in self.students:
            return False

        import datetime

        # Create plan submission entry
        plan_entry = {
            "plan": plan,
            "justification": justification,
            "timestamp": datetime.datetime.now().isoformat(),
            "status": "submitted",
        }

        # Add to student's record
        if "submitted_plans" not in self.students[student_id]:
            self.students[student_id]["submitted_plans"] = []

        self.students[student_id]["submitted_plans"].append(plan_entry)

        return True
