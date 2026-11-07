# Task 11 - Multi-File Student Gradebook

import csv


def get_grade(average):
    if average >= 85:
        return "A"
    elif average >= 70:
        return "B"
    elif average >= 55:
        return "C"
    elif average >= 40:
        return "D"
    return "F"


def make_gradebook(students_file, scores_file):
    students = {}

    with open(students_file, "r", newline="", encoding="utf-8") as file:
        for row in csv.DictReader(file):
            student_id = row["student_id"]

            if student_id in students:
                raise ValueError("Duplicate student ID: " + student_id)

            students[student_id] = {"name": row["name"], "marks": []}

    rejected = []
    used_subjects = set()

    with open(scores_file, "r", newline="", encoding="utf-8") as file:
        for row in csv.DictReader(file):
            student_id = row["student_id"]
            subject = row["subject"]

            try:
                marks = float(row["marks"])
            except ValueError:
                rejected.append({**row, "reason": "Marks must be numeric"})
                continue

            key = (student_id, subject)

            if student_id not in students:
                reason = "Unknown student ID"
            elif key in used_subjects:
                reason = "Duplicate student-subject entry"
            elif marks < 0 or marks > 100:
                reason = "Marks must be from 0 to 100"
            else:
                reason = ""

            if reason:
                rejected.append({**row, "reason": reason})
                continue

            used_subjects.add(key)
            students[student_id]["marks"].append(marks)

    report = []

    for student_id, details in students.items():
        marks_list = details["marks"]

        if marks_list:
            average = sum(marks_list) / len(marks_list)
        else:
            average = 0.0

        report.append({
            "student_id": student_id,
            "name": details["name"],
            "average": round(average, 2),
            "grade": get_grade(average)
        })

    report.sort(key=lambda row: (-row["average"], row["student_id"]))

    for number in range(len(report)):
        report[number]["rank"] = number + 1

    with open("report.csv", "w", newline="", encoding="utf-8") as file:
        fields = ["student_id", "name", "average", "grade", "rank"]
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(report)

    with open("rejected_scores.csv", "w", newline="", encoding="utf-8") as file:
        fields = ["student_id", "subject", "marks", "reason"]
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rejected)

    return report, rejected


if __name__ == "__main__":
    print(make_gradebook("students.csv", "scores.csv"))
