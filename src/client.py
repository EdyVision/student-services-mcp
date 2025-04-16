import requests
import json
import uuid

class FinaidClient:
    def __init__(self, base_url="http://localhost:7860"):
        self.base_url = base_url
        self.session_id = str(uuid.uuid4())
    
    def send_message(self, message):
        """Send a message to the server and get the response"""
        response = requests.post(
            f"{self.base_url}/messages/",
            params={"session_id": self.session_id},
            json={"message": message}
        )
        return response.json()
    
    def fetch_students(self):
        """Fetch list of students"""
        return self.send_message("fetch_students")
    
    def check_eligibility(self, student_id):
        """Check eligibility for a specific student"""
        return self.send_message(f"check_eligibility {student_id}")
    
    def fetch_student(self, student_id):
        """Fetch details for a specific student"""
        return self.send_message(f"fetch_student {student_id}")

# Example usage in a notebook:
"""
from client import FinaidClient

# Create a client instance
client = FinaidClient()

# Fetch all students
students = client.fetch_students()
print(students)

# Check eligibility for a specific student
student_id = "df62674f-5641-4657-a614-901a22ea76f2"  # Example student ID
eligibility = client.check_eligibility(student_id)
print(eligibility)

# Fetch details for a specific student
student_details = client.fetch_student(student_id)
print(student_details)
""" 