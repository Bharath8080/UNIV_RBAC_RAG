"""
scripts/gen_students_csv.py — Clean, concise generator for 200 Indian student records.
"""
import csv
import random
from pathlib import Path

random.seed(42)

FIRST_NAMES = [
    "Aarav", "Aditi", "Rohan", "Ananya", "Karthik", "Pooja", "Vikram", "Sneha", "Rahul", "Divya",
    "Arjun", "Kavya", "Siddharth", "Priyanka", "Pranav", "Tanvi", "Harsh", "Meera", "Ayush", "Riya",
    "Nikhil", "Anushka", "Varun", "Sanjana", "Devansh", "Ishita", "Manish", "Tejas", "Shreya", "Abhishek",
    "Nandini", "Gaurav", "Lavanya", "Chirag", "Aditya", "Neha", "Rohit", "Simran", "Pawan", "Keerthi",
    "Deepak", "Anirudh", "Bhavana", "Vishal", "Akash", "Kunal", "Deepika", "Sameer", "Swati", "Mihir"
]

LAST_NAMES = [
    "Agarwal", "Sharma", "Verma", "Iyer", "Reddy", "Hegde", "Deshmukh", "Kulkarni", "Nair", "Pillai",
    "Banerjee", "Menon", "Joshi", "Nambiar", "Bhatia", "Mukherjee", "Vardhan", "Dasgupta", "Mishra", "Sen",
    "Kapoor", "Chawla", "Tripathi", "Roy", "Saxena", "Chatterjee", "Pandey", "Soni", "Bhat", "Rao",
    "Mehta", "Chauhan", "Patil", "Shukla", "Kaur", "Kalyan", "Suresh", "Nayak", "Dixit", "Singhal"
]

BRANCHES = ["CSE", "AI&DS", "ECE", "IT", "MECH", "CIVIL", "EEE"]
COMPANIES = [("Google", 38.5), ("Microsoft", 44.0), ("Amazon", 32.0), ("Uber", 42.0), ("Cisco", 17.5), ("TCS Digital", 7.5), ("Infosys SP", 9.5), ("Accenture", 8.0)]
SCHOLARSHIPS = ["None", "Merit-Cum-Means", "JVD-Reimbursement", "State-Minority-Grant"]


def generate_students(count: int = 200) -> list[dict]:
    students = []
    for i in range(count):
        fn = FIRST_NAMES[i % len(FIRST_NAMES)]
        ln = LAST_NAMES[i % len(LAST_NAMES)]
        name = f"{fn} {ln}"
        branch = random.choice(BRANCHES)
        sem = random.randint(1, 8)
        adm_yr = 2025 - ((sem + 1) // 2)
        pin = f"{str(adm_yr)[2:]}A91A05{i+1:02d}"

        cgpa = round(min(9.9, max(5.0, random.gauss(7.8, 1.1))), 2)
        backlogs = 0 if cgpa >= 7.5 else random.choice([0, 1, 2, 3])
        attendance = round(min(98.0, max(55.0, random.gauss(82.0, 8.0))), 1)

        fee_due = 0 if random.random() < 0.7 else random.choice([25000, 45000, 65000])
        scholarship = random.choice(SCHOLARSHIPS) if fee_due == 0 else "None"

        # Placements (Sem 7 & 8)
        if sem in [7, 8] and backlogs == 0 and cgpa >= 6.5 and random.random() < 0.75:
            comp, pkg = random.choice(COMPANIES)
        else:
            comp, pkg = "None", 0.0

        detained = (attendance < 65.0)
        hall_ticket = "Hold" if (detained or fee_due > 0) else "Issued"
        disc_flag = (random.random() < 0.05)

        students.append({
            "pin_number": pin,
            "student_name": name,
            "branch": branch,
            "current_semester": sem,
            "cgpa": cgpa,
            "active_backlogs": backlogs,
            "attendance_percentage": attendance,
            "hall_ticket_status": hall_ticket,
            "tuition_fee_due": fee_due,
            "scholarship_type": scholarship,
            "placed_company": comp,
            "placement_package_lpa": pkg,
            "disciplinary_flag": 1 if disc_flag else 0,
        })
    return students


def main():
    out_file = Path(__file__).resolve().parent.parent / "data" / "students.csv"
    out_file.parent.mkdir(parents=True, exist_ok=True)
    data = generate_students(200)
    with open(out_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(data[0].keys()))
        writer.writeheader()
        writer.writerows(data)
    print(f"✅ Generated 200 student records ({len(data[0])} core columns) -> {out_file}")


if __name__ == "__main__":
    main()
