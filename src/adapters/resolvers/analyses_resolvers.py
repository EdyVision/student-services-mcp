from typing import List
from src.adapters.systems.analyses import StudentAnalysesSystem


class AnalysesResolver:
    """Resolver for Student Analytics System."""

    def __init__(self, analyses: StudentAnalysesSystem):
        self.analyses = analyses

    async def resolve_student_dropout_risk(self, student_id: str) -> str:
        """Resolve dropout risk prediction for a student."""
        result = await self.analyses.predict_dropout_risk(student_id)

        if "error" in result:
            return f"Error: {result['error']}"

        # Format the response
        response = f"""Dropout Risk Prediction for {result['name']} ({result['student_id']})

Risk Assessment:
• Risk Level: {result['risk_level']}
• Dropout Probability: {result['dropout_probability']:.1%}
• High Risk Flag: {'Yes' if result['dropout_risk'] else 'No'}

Academic Performance:
• Semesters Completed: {result['attrition_features'].get('semesters_completed', 0)}
• Credits Attempted: {result['attrition_features'].get('credits_attempted', 0)}
• Credits Completed: {result['attrition_features'].get('credits_completed', 0)}
• Completion Rate: {result['attrition_features'].get('completion_rate', 0.0):.1%}
• Failed Courses: {result['attrition_features'].get('failed_courses', 0)}
• Withdrawn Courses: {result['attrition_features'].get('withdrawn_courses', 0)}

Engagement Metrics:
• GPA Trend: {result['attrition_features'].get('gpa_trend', 'Unknown')}
• Attendance Rate: {result['attrition_features'].get('attendance_rate', 0.0):.1%}
• High Stress Terms: {result['attrition_features'].get('stress_frequency', 0)}
• Course Load Variance: {result['attrition_features'].get('course_load_variance', 0.0)}
• Graduation Timeline Risk: {result['attrition_features'].get('graduation_timeline_risk', 'Unknown')}

Recommendations:
"""

        for i, rec in enumerate(result["recommendations"], 1):
            response += f"{i}. {rec}\n"

        return response

    async def resolve_high_risk_students(self, limit: int = 10) -> str:
        """Resolve list of high-risk students."""
        high_risk_students = await self.analyses.get_high_risk_students(limit)

        if not high_risk_students:
            return "No high-risk students found."

        response = f"High-Risk Students (Top {len(high_risk_students)}):\n\n"

        for i, student in enumerate(high_risk_students, 1):
            response += f"{i}. {student['name']} ({student['student_id']})\n"
            response += f"   • Year: {student['year']}\n"
            response += f"   • GPA: {student['gpa']}\n"
            response += (
                f"   • Dropout Probability: {student['dropout_probability']:.1%}\n"
            )
            response += f"   • Completion Rate: {student['completion_rate']:.1%}\n"
            response += f"   • Failed Courses: {student['failed_courses']}\n"
            response += f"   • Attendance Rate: {student['attendance_rate']:.1%}\n\n"

        return response

    async def resolve_attrition_statistics(self) -> str:
        """Resolve overall attrition statistics."""
        stats = await self.analyses.get_attrition_statistics()

        if "error" in stats:
            return f"Error: {stats['error']}"

        response = f"""Attrition Statistics Report

Overall Population:
• Total Students: {stats['total_students']:,}
• Students Who Dropped Out: {stats['dropout_count']:,}
• Overall Dropout Rate: {stats['dropout_rate']:.1%}
• High-Risk Students: {stats['high_risk_count']:,}
• High-Risk Rate: {stats['high_risk_rate']:.1%}
• Average Dropout Probability: {stats['average_dropout_probability']:.1%}

Dropout Rate by Academic Year:
"""

        for year, data in stats["dropout_by_year"].items():
            response += f"• {year}: {data['dropouts']}/{data['total']} ({data['dropout_rate']:.1%})\n"

        response += f"""

Risk Assessment Summary:
• {stats['high_risk_count']:,} students flagged as high risk for dropout
• {stats['dropout_count']:,} students have already dropped out
• Average dropout probability across all students: {stats['average_dropout_probability']:.1%}

This data can be used for:
• Identifying students needing intervention
• Planning retention programs
• Monitoring institutional performance
• Resource allocation for student support services
"""

        return response

    async def resolve_attrition_feature_importance(self) -> str:
        """Resolve attrition feature importance analysis for dropout prediction."""
        analysis = await self.analyses.get_attrition_feature_importance()

        if "error" in analysis:
            return f"Error: {analysis['error']}"

        response = f"""Feature Importance Analysis for Dropout Prediction

CORRELATION ANALYSIS (Top 10 Features):
"""

        for i, (feature, correlation) in enumerate(
            analysis["correlation_analysis"].items(), 1
        ):
            response += f"{i:2d}. {feature:<20} | Correlation: {correlation:.3f}\n"

        response += f"""

MODEL IMPORTANCE WEIGHTS:
"""
        for feature, importance in analysis["model_importance"].items():
            response += f"• {feature:<20} | Weight: {importance:.2f}\n"

        response += f"""

CATEGORICAL FEATURE ANALYSIS:

GPA Trend Dropout Rates:
"""
        for trend, rate in analysis["categorical_analysis"][
            "gpa_trend_dropout_rates"
        ].items():
            response += f"• {trend:<10} | Dropout Rate: {rate:.1%}\n"

        response += f"""

Graduation Timeline Risk Dropout Rates:
"""
        for risk, rate in analysis["categorical_analysis"][
            "timeline_risk_dropout_rates"
        ].items():
            response += f"• {risk:<10} | Dropout Rate: {rate:.1%}\n"

        response += f"""

Academic Year Dropout Rates:
"""
        for year, rate in analysis["categorical_analysis"][
            "year_dropout_rates"
        ].items():
            response += f"• {year:<10} | Dropout Rate: {rate:.1%}\n"

        response += f"""

KEY INSIGHTS:
"""
        for i, insight in enumerate(analysis["insights"], 1):
            response += f"{i}. {insight}\n"

        response += f"""

ANALYSIS SUMMARY:
• Total Students Analyzed: {analysis['total_students_analyzed']:,}
• Strongest Predictor: {list(analysis['correlation_analysis'].keys())[0] if analysis['correlation_analysis'] else 'N/A'}
• Most Important Model Feature: GPA (weight: 0.35)

This analysis helps identify which factors are most predictive of student dropout,
enabling targeted intervention strategies and resource allocation.
"""

        return response

    async def resolve_attrition_factor_analysis(self, student_id: str) -> str:
        """Resolve detailed attrition factor analysis for a student."""
        result = await self.analyses.predict_dropout_risk(student_id)

        if "error" in result:
            return f"Error: {result['error']}"

        features = result["attrition_features"]

        response = f"""Attrition Factor Analysis for {result['name']} ({result['student_id']})

ACADEMIC PERFORMANCE FACTORS:
• Current GPA: {result['attrition_features'].get('gpa', 'N/A')}
• GPA Trend: {features.get('gpa_trend', 'Unknown')} {'⚠️' if features.get('gpa_trend') == 'declining' else ''}
• Completion Rate: {features.get('completion_rate', 0.0):.1%} {'⚠️' if features.get('completion_rate', 0.0) < 0.8 else ''}
• Failed Courses: {features.get('failed_courses', 0)} {'⚠️' if features.get('failed_courses', 0) > 2 else ''}
• Withdrawn Courses: {features.get('withdrawn_courses', 0)} {'⚠️' if features.get('withdrawn_courses', 0) > 1 else ''}

ENGAGEMENT FACTORS:
• Attendance Rate: {features.get('attendance_rate', 0.0):.1%} {'⚠️' if features.get('attendance_rate', 0.0) < 0.8 else ''}
• High Stress Terms: {features.get('stress_frequency', 0)} {'⚠️' if features.get('stress_frequency', 0) > 2 else ''}
• Course Load Variance: {features.get('course_load_variance', 0.0):.1f} {'⚠️' if features.get('course_load_variance', 0.0) > 50 else ''}

PROGRESS FACTORS:
• Semesters Completed: {features.get('semesters_completed', 0)}
• Credits Attempted: {features.get('credits_attempted', 0)}
• Credits Completed: {features.get('credits_completed', 0)}
• Graduation Timeline Risk: {features.get('graduation_timeline_risk', 'Unknown')} {'⚠️' if features.get('graduation_timeline_risk') in ['at_risk', 'delayed'] else ''}

RISK ASSESSMENT:
• Dropout Probability: {result['dropout_probability']:.1%}
• Risk Level: {result['risk_level']}
• High Risk Flag: {'Yes' if result['dropout_risk'] else 'No'}

INTERPRETATION:
"""

        # Add interpretation based on factors
        risk_factors = []
        if features.get("completion_rate", 0.0) < 0.8:
            risk_factors.append("Low completion rate indicates academic struggles")
        if features.get("failed_courses", 0) > 2:
            risk_factors.append("Multiple course failures suggest academic challenges")
        if features.get("attendance_rate", 0.0) < 0.8:
            risk_factors.append("Low attendance may indicate disengagement")
        if features.get("stress_frequency", 0) > 2:
            risk_factors.append("Frequent high stress may impact academic performance")
        if features.get("gpa_trend") == "declining":
            risk_factors.append("Declining GPA trend is a strong predictor of dropout")
        if features.get("graduation_timeline_risk") in ["at_risk", "delayed"]:
            risk_factors.append(
                "Graduation timeline concerns may indicate persistence issues"
            )

        if risk_factors:
            for i, factor in enumerate(risk_factors, 1):
                response += f"{i}. {factor}\n"
        else:
            response += (
                "No major risk factors identified - student appears to be on track.\n"
            )

        response += f"\nRECOMMENDATIONS:\n"
        for i, rec in enumerate(result["recommendations"], 1):
            response += f"{i}. {rec}\n"

        return response
