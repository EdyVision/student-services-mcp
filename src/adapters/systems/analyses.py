import os
import pandas as pd
import numpy as np
import json
import random
from typing import Dict, List, Tuple, Optional


class StudentAnalysesSystem:
    """Student Analytics and Prediction System using synthetic data."""

    def __init__(self, data_path="../../dist/data/synthetic_population_data.csv"):
        current_dir = os.path.dirname(__file__)
        data_path = os.path.abspath(os.path.join(current_dir, data_path))

        # Initialize with empty data
        self.students = {}
        self.attrition_features = {}

        # Load synthetic data if file exists
        if os.path.exists(data_path):
            try:
                df = pd.read_csv(data_path)
                # Convert dataframe to dictionary keyed by student ID
                for _, row in df.iterrows():
                    student_id = row["student_id"]

                    # Store basic student info
                    self.students[student_id] = {
                        "student_id": student_id,
                        "name": row["name"],
                        "gpa": row["gpa"],
                        "major": row["major"],
                        "year": row["year"],
                        "work_hours": row.get("work_hours", 0),
                    }

                    # Store attrition features
                    self.attrition_features[student_id] = {
                        "semesters_completed": row.get("semesters_completed", 0),
                        "credits_attempted": row.get("credits_attempted", 0),
                        "credits_completed": row.get("credits_completed", 0),
                        "completion_rate": row.get("completion_rate", 0.0),
                        "failed_courses": row.get("failed_courses", 0),
                        "withdrawn_courses": row.get("withdrawn_courses", 0),
                        "gpa_trend": row.get("gpa_trend", "stable"),
                        "attendance_rate": row.get("attendance_rate", 0.0),
                        "stress_frequency": row.get("stress_frequency", 0),
                        "course_load_variance": row.get("course_load_variance", 0.0),
                        "graduation_timeline_risk": row.get(
                            "graduation_timeline_risk", "delayed"
                        ),
                        "dropped_out": row.get("dropped_out", False),
                        "dropout_encoded": row.get("dropout_encoded", 0),
                        "dropout_risk": row.get("dropout_risk", False),
                        "dropout_probability": row.get("dropout_probability", 0.0),
                    }

            except Exception as e:
                print(f"Error loading synthetic data: {e}")
                self.students = {}
                self.attrition_features = {}
        else:
            raise FileNotFoundError(
                f"Data file not found at {data_path}. Please ensure the file exists."
            )

    def calculate_attrition_features(self, student: Dict) -> Dict:
        """Calculate attrition features for a student."""
        if not student:
            return {}

        # Basic academic metrics
        gpa = student.get("gpa", 0.0)
        work_hours = student.get("work_hours", 0)
        major = student.get("major", "Unknown")
        year = student.get("year", "Unknown")

        # Parse past terms if available
        past_terms = student.get("past_terms", [])
        if isinstance(past_terms, str):
            try:
                past_terms = json.loads(past_terms)
            except:
                past_terms = []

        # Calculate basic metrics
        semesters_completed = len(past_terms)
        credits_attempted = sum(term.get("credits", 0) for term in past_terms)

        # Calculate credits completed and failed courses
        credits_completed = 0
        failed_courses = 0
        withdrawn_courses = 0
        stress_counts = {"low": 0, "moderate": 0, "high": 0}
        credit_loads = []

        for term in past_terms:
            term_credits = 0
            for course in term.get("courses", []):
                grade = course.get("grade", "")
                credits = course.get("credits", 0)

                # Count failed courses (D, F grades)
                if grade in ["D", "D+", "D-", "F"]:
                    failed_courses += 1
                elif grade == "W":  # Withdrawn
                    withdrawn_courses += 1
                else:
                    # Only count credits for passing grades
                    term_credits += credits
                    credits_completed += credits

            credit_loads.append(term_credits)

            # Track stress levels
            stress = term.get("stress", "moderate")
            stress_counts[stress] += 1

        # Calculate derived metrics
        completion_rate = (
            credits_completed / credits_attempted if credits_attempted > 0 else 0
        )

        # Calculate GPA trend (simplified)
        estimated_historical_gpa = max(2.0, gpa - random.uniform(-0.3, 0.3))
        if gpa > estimated_historical_gpa + 0.2:
            gpa_trend = "improving"
        elif gpa < estimated_historical_gpa - 0.2:
            gpa_trend = "declining"
        else:
            gpa_trend = "stable"

        # Estimate attendance rate based on performance
        base_attendance = 0.85
        if gpa >= 3.5:
            attendance_rate = base_attendance + random.uniform(0.1, 0.15)
        elif gpa >= 3.0:
            attendance_rate = base_attendance + random.uniform(0.0, 0.1)
        elif gpa >= 2.5:
            attendance_rate = base_attendance + random.uniform(-0.05, 0.05)
        else:
            attendance_rate = base_attendance + random.uniform(-0.15, 0.0)

        attendance_rate = max(0.0, min(1.0, attendance_rate))

        # Stress frequency
        stress_frequency = stress_counts["high"]

        # Course load variance
        course_load_variance = np.var(credit_loads) if len(credit_loads) > 1 else 0

        # Graduation timeline risk
        expected_total_credits = 120  # Typical bachelor's degree
        current_progress = (
            credits_completed / expected_total_credits
            if expected_total_credits > 0
            else 0
        )

        if current_progress >= 0.8:
            graduation_timeline_risk = "on_track"
        elif current_progress >= 0.6:
            graduation_timeline_risk = "at_risk"
        else:
            graduation_timeline_risk = "delayed"

        return {
            "semesters_completed": semesters_completed,
            "credits_attempted": credits_attempted,
            "credits_completed": credits_completed,
            "completion_rate": round(completion_rate, 3),
            "failed_courses": failed_courses,
            "withdrawn_courses": withdrawn_courses,
            "gpa_trend": gpa_trend,
            "attendance_rate": round(attendance_rate, 3),
            "stress_frequency": stress_frequency,
            "course_load_variance": round(course_load_variance, 2),
            "graduation_timeline_risk": graduation_timeline_risk,
        }

    def calculate_dropout_probability(
        self, student: Dict, attrition_features: Dict
    ) -> float:
        """Calculate dropout probability based on student data and attrition features."""
        # Base dropout probability (15% as mentioned in requirements)
        base_dropout_prob = 0.15

        # Risk factors that increase dropout probability
        risk_factors = 0

        # Academic performance factors
        gpa = student.get("gpa", 0.0)
        if gpa < 2.5:
            risk_factors += 0.3
        elif gpa < 3.0:
            risk_factors += 0.15

        completion_rate = attrition_features.get("completion_rate", 0.0)
        if completion_rate < 0.7:
            risk_factors += 0.25
        elif completion_rate < 0.8:
            risk_factors += 0.1

        failed_courses = attrition_features.get("failed_courses", 0)
        if failed_courses > 3:
            risk_factors += 0.2
        elif failed_courses > 1:
            risk_factors += 0.1

        withdrawn_courses = attrition_features.get("withdrawn_courses", 0)
        if withdrawn_courses > 2:
            risk_factors += 0.15

        if attrition_features.get("gpa_trend") == "declining":
            risk_factors += 0.15

        attendance_rate = attrition_features.get("attendance_rate", 0.0)
        if attendance_rate < 0.7:
            risk_factors += 0.2
        elif attendance_rate < 0.8:
            risk_factors += 0.1

        # Work and financial factors
        work_hours = student.get("work_hours", 0)
        if work_hours > 30:
            risk_factors += 0.1

        # Academic year factors
        year = student.get("year", "Unknown")
        if year == "Freshman":
            risk_factors += 0.05  # Freshmen are more likely to drop out
        elif year == "Senior":
            risk_factors -= 0.1  # Seniors are less likely to drop out

        # Stress and course load factors
        stress_frequency = attrition_features.get("stress_frequency", 0)
        if stress_frequency > 2:
            risk_factors += 0.1

        course_load_variance = attrition_features.get("course_load_variance", 0.0)
        if course_load_variance > 50:  # High variance in course load
            risk_factors += 0.05

        graduation_timeline_risk = attrition_features.get(
            "graduation_timeline_risk", "delayed"
        )
        if graduation_timeline_risk == "delayed":
            risk_factors += 0.1
        elif graduation_timeline_risk == "at_risk":
            risk_factors += 0.05

        # Calculate final dropout probability
        dropout_probability = min(0.95, base_dropout_prob + risk_factors)

        return round(dropout_probability, 3)

    async def predict_dropout_risk(self, student_id: str) -> Dict:
        """Predict dropout risk for a specific student."""
        if student_id not in self.students:
            return {"error": "Student not found"}

        student = self.students[student_id]
        attrition_features = self.attrition_features.get(student_id, {})

        # Calculate dropout probability
        dropout_probability = self.calculate_dropout_probability(
            student, attrition_features
        )

        # Determine risk level
        if dropout_probability > 0.4:
            dropout_risk = True
            risk_level = "High"
        elif dropout_probability > 0.25:
            dropout_risk = False
            risk_level = "Medium"
        else:
            dropout_risk = False
            risk_level = "Low"

        return {
            "student_id": student_id,
            "name": student["name"],
            "dropout_probability": dropout_probability,
            "dropout_risk": dropout_risk,
            "risk_level": risk_level,
            "attrition_features": attrition_features,
            "recommendations": self._generate_recommendations(
                attrition_features, dropout_probability
            ),
        }

    async def get_high_risk_students(self, limit: int = 10) -> List[Dict]:
        """Get list of high-risk students."""
        high_risk_students = []

        for student_id, features in self.attrition_features.items():
            if features.get("dropout_risk", False):
                student = self.students[student_id]
                high_risk_students.append(
                    {
                        "student_id": student_id,
                        "name": student["name"],
                        "gpa": student["gpa"],
                        "year": student["year"],
                        "dropout_probability": features.get("dropout_probability", 0.0),
                        "completion_rate": features.get("completion_rate", 0.0),
                        "failed_courses": features.get("failed_courses", 0),
                        "attendance_rate": features.get("attendance_rate", 0.0),
                    }
                )

        # Sort by dropout probability (highest first)
        high_risk_students.sort(key=lambda x: x["dropout_probability"], reverse=True)

        return high_risk_students[:limit]

    async def get_attrition_statistics(self) -> Dict:
        """Get overall attrition statistics."""
        total_students = len(self.students)
        if total_students == 0:
            return {"error": "No students found"}

        # Calculate statistics
        dropout_count = sum(
            1
            for features in self.attrition_features.values()
            if features.get("dropped_out", False)
        )
        high_risk_count = sum(
            1
            for features in self.attrition_features.values()
            if features.get("dropout_risk", False)
        )

        dropout_rate = dropout_count / total_students
        high_risk_rate = high_risk_count / total_students

        # Calculate average dropout probability
        avg_dropout_prob = np.mean(
            [
                features.get("dropout_probability", 0.0)
                for features in self.attrition_features.values()
            ]
        )

        # Dropout by year
        dropout_by_year = {}
        for student_id, student in self.students.items():
            year = student["year"]
            if year not in dropout_by_year:
                dropout_by_year[year] = {"total": 0, "dropouts": 0}
            dropout_by_year[year]["total"] += 1
            if self.attrition_features[student_id].get("dropped_out", False):
                dropout_by_year[year]["dropouts"] += 1

        # Calculate dropout rates by year
        for year in dropout_by_year:
            total = dropout_by_year[year]["total"]
            dropouts = dropout_by_year[year]["dropouts"]
            dropout_by_year[year]["dropout_rate"] = dropouts / total if total > 0 else 0

        return {
            "total_students": total_students,
            "dropout_count": dropout_count,
            "dropout_rate": round(dropout_rate, 3),
            "high_risk_count": high_risk_count,
            "high_risk_rate": round(high_risk_rate, 3),
            "average_dropout_probability": round(avg_dropout_prob, 3),
            "dropout_by_year": dropout_by_year,
        }

    def _generate_recommendations(
        self, attrition_features: Dict, dropout_probability: float
    ) -> List[str]:
        """Generate recommendations based on attrition features."""
        recommendations = []

        if dropout_probability > 0.6:
            recommendations.append(
                "Immediate intervention recommended - student is at very high risk"
            )

        if attrition_features.get("completion_rate", 0.0) < 0.8:
            recommendations.append(
                "Focus on improving course completion - consider academic support"
            )

        if attrition_features.get("failed_courses", 0) > 2:
            recommendations.append(
                "Multiple course failures detected - recommend tutoring or course retake"
            )

        if attrition_features.get("attendance_rate", 0.0) < 0.8:
            recommendations.append("Low attendance rate - check for engagement issues")

        if attrition_features.get("stress_frequency", 0) > 2:
            recommendations.append(
                "High stress frequency - recommend counseling services"
            )

        if attrition_features.get("gpa_trend") == "declining":
            recommendations.append(
                "Declining GPA trend - investigate academic challenges"
            )

        if attrition_features.get("graduation_timeline_risk") == "delayed":
            recommendations.append("Graduation timeline at risk - review academic plan")

        if not recommendations:
            recommendations.append(
                "Student appears to be on track - continue monitoring"
            )

        return recommendations

    async def get_attrition_feature_importance(self) -> Dict:
        """Get feature importance analysis for dropout prediction."""
        if not self.attrition_features:
            return {"error": "No data available for analysis"}

        # Calculate correlations between features and dropout
        feature_correlations = {}

        # Numeric features for correlation analysis
        numeric_features = [
            "gpa",
            "work_hours",
            "semesters_completed",
            "credits_attempted",
            "credits_completed",
            "completion_rate",
            "failed_courses",
            "withdrawn_courses",
            "attendance_rate",
            "stress_frequency",
            "course_load_variance",
            "dropout_probability",
        ]

        # Calculate correlations
        for feature in numeric_features:
            if feature in ["gpa", "work_hours"]:
                # These come from student data
                values = [
                    self.students[sid].get(feature, 0) for sid in self.students.keys()
                ]
            else:
                # These come from attrition features
                values = [
                    self.attrition_features[sid].get(feature, 0)
                    for sid in self.attrition_features.keys()
                ]

            # Calculate correlation with dropout_encoded
            dropout_values = [
                self.attrition_features[sid].get("dropout_encoded", 0)
                for sid in self.attrition_features.keys()
            ]

            if len(values) == len(dropout_values) and len(values) > 1:
                correlation = np.corrcoef(values, dropout_values)[0, 1]
                if not np.isnan(correlation):
                    feature_correlations[feature] = round(abs(correlation), 4)

        # Sort by importance (absolute correlation)
        sorted_features = sorted(
            feature_correlations.items(), key=lambda x: x[1], reverse=True
        )

        # Calculate feature importance based on our risk model weights
        model_importance = {
            "gpa": 0.35,  # Strongest predictor
            "completion_rate": 0.30,
            "attendance_rate": 0.25,
            "failed_courses": 0.20,
            "withdrawn_courses": 0.15,
            "gpa_trend": 0.15,
            "work_hours": 0.10,
            "stress_frequency": 0.10,
            "course_load_variance": 0.05,
            "graduation_timeline_risk": 0.10,
            "semesters_completed": 0.05,
            "credits_attempted": 0.05,
            "credits_completed": 0.10,
            "dropout_probability": 0.45,  # This is the model output
        }

        # Categorical feature analysis
        categorical_analysis = {}

        # GPA trend analysis
        gpa_trend_dropout = {}
        for trend in ["improving", "stable", "declining"]:
            trend_students = [
                sid
                for sid, features in self.attrition_features.items()
                if features.get("gpa_trend") == trend
            ]
            if trend_students:
                dropout_rate = sum(
                    self.attrition_features[sid].get("dropped_out", False)
                    for sid in trend_students
                ) / len(trend_students)
                gpa_trend_dropout[trend] = round(dropout_rate, 3)

        # Graduation timeline risk analysis
        timeline_dropout = {}
        for risk in ["on_track", "at_risk", "delayed"]:
            risk_students = [
                sid
                for sid, features in self.attrition_features.items()
                if features.get("graduation_timeline_risk") == risk
            ]
            if risk_students:
                dropout_rate = sum(
                    self.attrition_features[sid].get("dropped_out", False)
                    for sid in risk_students
                ) / len(risk_students)
                timeline_dropout[risk] = round(dropout_rate, 3)

        # Academic year analysis
        year_dropout = {}
        for year in ["Freshman", "Sophomore", "Junior", "Senior"]:
            year_students = [
                sid
                for sid, student in self.students.items()
                if student.get("year") == year
            ]
            if year_students:
                dropout_rate = sum(
                    self.attrition_features[sid].get("dropped_out", False)
                    for sid in year_students
                ) / len(year_students)
                year_dropout[year] = round(dropout_rate, 3)

        return {
            "correlation_analysis": dict(sorted_features[:10]),  # Top 10 features
            "model_importance": model_importance,
            "categorical_analysis": {
                "gpa_trend_dropout_rates": gpa_trend_dropout,
                "timeline_risk_dropout_rates": timeline_dropout,
                "year_dropout_rates": year_dropout,
            },
            "total_students_analyzed": len(self.attrition_features),
            "insights": self._generate_feature_insights(
                sorted_features, gpa_trend_dropout, timeline_dropout
            ),
        }

    def _generate_feature_insights(
        self, sorted_features, gpa_trend_dropout, timeline_dropout
    ):
        """Generate insights from feature importance analysis."""
        insights = []

        # Top predictor insights
        if sorted_features:
            top_feature = sorted_features[0]
            insights.append(
                f"'{top_feature[0]}' is the strongest predictor of dropout (correlation: {top_feature[1]:.3f})"
            )

        # GPA trend insights
        if gpa_trend_dropout:
            declining_rate = gpa_trend_dropout.get("declining", 0)
            stable_rate = gpa_trend_dropout.get("stable", 0)
            if declining_rate > stable_rate:
                insights.append(
                    f"Students with declining GPA trend have {declining_rate:.1%} dropout rate vs {stable_rate:.1%} for stable trend"
                )

        # Timeline risk insights
        if timeline_dropout:
            delayed_rate = timeline_dropout.get("delayed", 0)
            on_track_rate = timeline_dropout.get("on_track", 0)
            if delayed_rate > on_track_rate:
                insights.append(
                    f"Students with delayed graduation timeline have {delayed_rate:.1%} dropout rate vs {on_track_rate:.1%} for on-track students"
                )

        # Academic performance insights
        completion_corr = next(
            (corr for feature, corr in sorted_features if feature == "completion_rate"),
            0,
        )
        if completion_corr > 0.2:
            insights.append(
                f"Course completion rate is a strong predictor (correlation: {completion_corr:.3f})"
            )

        return insights

    async def disconnect(self):
        """Disconnect from the student analytics system."""
        # No actual connections to close in this mock implementation
        pass
