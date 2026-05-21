# "id": 3,
#     "title": "Student Grade Manager",
#     "skills": ["Python"],
#     "level": "Beginner",
#     "interest": "Education",
#     "time": "Medium",
#     "description": "A Python application to store student names and their grades, compute averages, and display a class report. Ideal for practicing data structures, functions, and file persistence.",
#     "features": [
#       "Add students and assign grades per subject",
#       "Calculate individual and class averages",
#       "Assign letter grades automatically",
#       "Save and load data from a JSON file"
#     ],
#     "tech_stack": ["Python", "json module", "os module"],
#     "roadmap": [
#       "Step 1: Define the student data structure using a dictionary",
#       "Step 2: Write add_student() and add_grade() functions",
#       "Step 3: Implement average calculation logic",
#       "Step 4: Create a letter grade converter function",
#       "Step 5: Build the JSON save/load functions",
#       "Step 6: Create a simple text menu for user interaction",
#       "Step 7: Write a class report printer function"
#     ],
#     "resources": [
#       "Python JSON module: https://docs.python.org/3/library/json.html",
#       "Python functions tutorial: https://realpython.com/defining-your-own-python-function",
#       "W3Schools Python: https://www.w3schools.com/python"
#     ],
#     "starter_code": "starter_code/grade_manager.py"
#   },

import json
import os

# Step 1: Define the student data structure using a dictionary
# Example structure: 
# students = {
#     "Alice": {"Math": [90, 85], "Science": [92]},
#     "Bob": {"Math": [70], "Science": [80, 75]}
# }
students = {}
DATA_FILE = "students_data.json"

# Step 4: Create a letter grade converter function
def calculate_letter_grade(average):
    if average >= 90: return "A"
    elif average >= 80: return "B"
    elif average >= 70: return "C"
    elif average >= 60: return "D"
    else: return "F"

# Step 2: Write add_student() and add_grade() functions
def add_student():
    name = input("Enter student name: ").strip()
    if not name:
        print("❌ Name cannot be empty.")
        return
    if name in students:
        print(f"ℹ️ {name} already exists.")
    else:
        students[name] = {}
        print(f"✅ Student '{name}' added successfully.")

def add_grade():
    name = input("Enter student name: ").strip()
    if name not in students:
        print("❌ Student not found. Add the student first.")
        return
    
    subject = input("Enter subject: ").strip()
    if not subject:
        print("❌ Subject cannot be empty.")
        return
        
    try:
        grade = float(input(f"Enter grade for {subject}: "))
        if not (0 <= grade <= 100):
            print("❌ Grade must be between 0 and 100.")
            return
    except ValueError:
        print("❌ Invalid input. Please enter a numerical grade.")
        return

    if subject not in students[name]:
        students[name][subject] = []
    
    students[name][subject].append(grade)
    print(f"✅ Added grade {grade} to {name}'s {subject} record.")

# Step 3: Implement average calculation logic
def get_student_averages(name):
    """Calculates subject averages and overall average for a single student."""
    if name not in students or not students[name]:
        return {}, 0.0
        
    subject_averages = {}
    total_grades_sum = 0
    total_grades_count = 0
    
    for subject, grades in students[name].items():
        if grades:
            sub_avg = sum(grades) / len(grades)
            subject_averages[subject] = sub_avg
            total_grades_sum += sum(grades)
            total_grades_count += len(grades)
            
    overall_avg = total_grades_sum / total_grades_count if total_grades_count > 0 else 0.0
    return subject_averages, overall_avg

# Step 7: Write a class report printer function
def generate_class_report():
    if not students:
        print("\n📭 No student data available to report.")
        return

    print("\n========================================")
    print("           CLASS REPORT CARD            ")
    print("========================================")
    
    class_total_sum = 0
    class_student_count = 0

    for name in students:
        print(f"\n👤 Student: {name}")
        sub_avgs, overall_avg = get_student_averages(name)
        
        if not sub_avgs:
            print("  No grades recorded yet.")
            continue
            
        for sub, avg in sub_avgs.items():
            print(f"  - {sub}: {avg:.2f} ({calculate_letter_grade(avg)})")
            
        print(f"  ⭐ Overall Average: {overall_avg:.2f} ({calculate_letter_grade(overall_avg)})")
        class_total_sum += overall_avg
        class_student_count += 1

    print("\n----------------------------------------")
    if class_student_count > 0:
        class_avg = class_total_sum / class_student_count
        print(f"🏫 Total Class Average: {class_avg:.2f} ({calculate_letter_grade(class_avg)})")
    print("========================================")

# Step 5: Build the JSON save/load functions
def save_data():
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(students, f, indent=4)
        print("💾 Data saved successfully.")
    except Exception as e:
        print(f"❌ Error saving data: {e}")

def load_data():
    global students
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                students = json.load(f)
            print("📂 Previous data loaded successfully.")
        except Exception as e:
            print(f"⚠️ Error loading data file (corrupted JSON?). Starting fresh. Details: {e}")
    else:
        print("ℹ️ No saved data found. Starting a fresh session.")

# Step 6: Create a simple text menu for user interaction
def main_menu():
    load_data()
    while True:
        print("\n--- STUDENT GRADE MANAGER ---")
        print("1. Add Student")
        print("2. Add Grade to Student")
        print("3. Generate Class Report")
        print("4. Save Data")
        print("5. Exit")
        
        choice = input("Select an option (1-5): ").strip()
        
        if choice == "1":
            add_student()
        elif choice == "2":
            add_grade()
        elif choice == "3":
            generate_class_report()
        elif choice == "4":
            save_data()
        elif choice == "5":
            save_data()  # Auto-save before exiting
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid selection. Please choose 1, 2, 3, 4, or 5.")

if __name__ == "__main__":
    main_menu()