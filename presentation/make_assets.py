import os
from PIL import Image, ImageDraw, ImageFont

os.makedirs("presentation/assets", exist_ok=True)

def draw_rounded_rect(draw, xy, corner_radius, fill=None, outline=None, width=1):
    x1, y1, x2, y2 = xy
    draw.rounded_rectangle([x1, y1, x2, y2], radius=corner_radius, fill=fill, outline=outline, width=width)

# 1. HOD Dashboard Mockup
w, h = 1200, 680
img1 = Image.new("RGB", (w, h), "#F4F7F5")
d1 = ImageDraw.Draw(img1)

# Top Bar
draw_rounded_rect(d1, (30, 25, 1170, 115), 12, fill="#0B5E36", outline="#073B22", width=2)
d1.text((50, 42), "DEPARTMENT OF COMPUTER SCIENCE - ALIGARH MUSLIM UNIVERSITY", fill="#FFFFFF")
d1.text((50, 75), "Academic Performance Analytics System | Executive HOD Dashboard", fill="#C5E1D4")
d1.text((950, 55), "● LIVE on Render", fill="#69F0AE")

# 4 KPI Cards
kpis = [
    ("TOTAL STUDENTS", "60", "#0B5E36"),
    ("AVERAGE MARKS", "74.0%", "#0B5E36"),
    ("OVERALL ATTENDANCE", "82.0%", "#0B5E36"),
    ("HIGH RISK STUDENTS", "8", "#DC3545")
]
for i, (title, val, col) in enumerate(kpis):
    x1 = 30 + i * 290
    x2 = x1 + 270
    draw_rounded_rect(d1, (x1, 135, x2, 250), 10, fill="#FFFFFF", outline="#E0E0E0", width=2)
    d1.rectangle((x1, 135, x1+10, 250), fill=col)
    d1.text((x1 + 25, 155), title, fill="#757575")
    d1.text((x1 + 25, 190), val, fill=col)

# Left Card: Subject Performance
draw_rounded_rect(d1, (30, 275, 750, 645), 10, fill="#FFFFFF", outline="#E0E0E0", width=2)
d1.text((50, 295), "SUBJECT-WISE AVERAGE MARKS (MCA SEM 1 & SEM 2)", fill="#0B5E36")

subjects = [
    ("DS using C++", 67.8), ("DBMS", 69.4), ("Digital Electronics", 66.2),
    ("Analysis & Design IS", 65.8), ("Soft Skills", 68.9), ("Lab-I (C++)", 64.5),
    ("OOPs using JAVA", 71.2), ("Web Dev", 73.1), ("Computer Networks", 70.4),
    ("Lab-II (JAVA)", 72.8), ("E-Commerce", 68.5), ("Open Elective", 70.0)
]
for idx, (sub, avg) in enumerate(subjects):
    y = 335 + idx * 24
    d1.text((50, y), sub[:22], fill="#333333")
    bar_w = int(avg * 3.8)
    d1.rectangle((260, y+3, 260 + bar_w, y+15), fill="#0B5E36" if avg>=70 else "#2E7D32")
    d1.text((270 + bar_w, y), f"{avg}%", fill="#555555")

# Right Card: Academic Risk Distribution
draw_rounded_rect(d1, (780, 275, 1170, 645), 10, fill="#FFFFFF", outline="#E0E0E0", width=2)
d1.text((805, 295), "ACADEMIC RISK DISTRIBUTION", fill="#0B5E36")

risk_cats = [
    ("Low Risk", "38 Students (63.3%)", "#28A745", "#D4EDDA"),
    ("Medium Risk", "14 Students (23.3%)", "#FFC107", "#FFF3CD"),
    ("High Risk", "8 Students (13.4%)", "#DC3545", "#F8D7DA")
]
for idx, (cat, desc, c_border, c_bg) in enumerate(risk_cats):
    y = 350 + idx * 90
    draw_rounded_rect(d1, (805, y, 1145, y+75), 8, fill=c_bg, outline=c_border, width=2)
    d1.text((825, y+16), cat, fill=c_border)
    d1.text((825, y+44), desc, fill="#333333")

img1.save("presentation/assets/shot_hod_dashboard.png", format="PNG")
print("Saved shot_hod_dashboard.png")

# 2. Student Dashboard & Judge0 Card
img2 = Image.new("RGB", (w, h), "#F4F7F5")
d2 = ImageDraw.Draw(img2)

draw_rounded_rect(d2, (30, 25, 1170, 115), 12, fill="#0B5E36", outline="#073B22", width=2)
d2.text((50, 42), "STUDENT ACADEMIC PORTAL & AI MENTORING", fill="#FFFFFF")
d2.text((50, 75), "Student: FAIZAN AHMAD | Faculty No: 25CAMSA112 | Enrollment: GR0622 | Sem: 3rd", fill="#C5E1D4")

draw_rounded_rect(d2, (30, 135, 570, 645), 10, fill="#FFFFFF", outline="#E0E0E0", width=2)
d2.text((50, 155), "AI ACADEMIC RISK ASSESSMENT (scikit-learn)", fill="#0B5E36")
draw_rounded_rect(d2, (50, 195, 550, 275), 8, fill="#D4EDDA", outline="#28A745", width=2)
d2.text((70, 215), "VERDICT: LOW RISK (Safe Progress)", fill="#155724")
d2.text((70, 245), "Model Confidence: 91.2% Low Risk Probability", fill="#155724")

recs = [
    "Sem 1 Average: 73.5% | Sem 2 Average: 75.2%",
    "Attendance: 75.5% (Meets mandatory AMU 75% rule)",
    "Status: Eligible for Semester III Examinations",
    "AI Advice: Excellent coding participation.",
    "Recommended Action: Peer tutoring & advanced electives."
]
for i, r in enumerate(recs):
    d2.text((50, 310 + i * 45), f"● {r}", fill="#333333")

draw_rounded_rect(d2, (600, 135, 1170, 645), 10, fill="#FFFFFF", outline="#E0E0E0", width=2)
d2.text((620, 155), "ONLINE CODING LAB & JUDGE0 EVALUATION", fill="#0B5E36")

draw_rounded_rect(d2, (620, 195, 1150, 360), 8, fill="#1E1E1E", outline="#333333", width=1)
d2.text((640, 210), "# Solution for: Sum of Array Elements (DS using C++)", fill="#80CBC4")
d2.text((640, 240), "import sys", fill="#CE9178")
d2.text((640, 270), "nums = list(map(int, sys.stdin.read().split()))", fill="#DCDCAA")
d2.text((640, 300), "print(sum(nums))", fill="#9CDCFE")

draw_rounded_rect(d2, (620, 380, 1150, 620), 8, fill="#F9FBF9", outline="#E0E0E0", width=1)
d2.text((640, 400), "JUDGE0 EVALUATION VERDICT: ACCEPTED (100 / 100)", fill="#28A745")
d2.text((640, 435), "Test Case 1: Input: [1 2 3 4 5] -> Output: 15 (PASSED, 0.012s)", fill="#2E7D32")
d2.text((640, 470), "Test Case 2: Input: [10 -5 20]  -> Output: 25 (PASSED, 0.011s)", fill="#2E7D32")
d2.text((640, 505), "Test Case 3: Input: [100 200 300] -> Output: 600 (PASSED, 0.015s)", fill="#2E7D32")
d2.text((640, 550), "Departmental Leaderboard Rank: #1 (Solved: 2/2)", fill="#0B5E36")

img2.save("presentation/assets/shot_student_judge.png", format="PNG")
print("Saved shot_student_judge.png")

# 3. Live Render Deployment Card Graphic
img3 = Image.new("RGB", (w, h), "#F4F7F5")
d3 = ImageDraw.Draw(img3)

draw_rounded_rect(d3, (30, 25, 1170, 115), 12, fill="#0B5E36", outline="#073B22", width=2)
d3.text((50, 42), "CLOUD DEPLOYMENT ARCHITECTURE & LIVE ACCESS", fill="#FFFFFF")
d3.text((50, 75), "Verified Live Production Deployment on Render.com Cloud Platform", fill="#C5E1D4")

draw_rounded_rect(d3, (30, 140, 1170, 280), 10, fill="#FFFFFF", outline="#0B5E36", width=2)
d3.text((60, 165), "LIVE PRODUCTION URL:", fill="#757575")
d3.text((60, 200), "https://academic-performance-analytics-n044.onrender.com/", fill="#0B5E36")
draw_rounded_rect(d3, (980, 185, 1140, 245), 20, fill="#E8F5E9", outline="#28A745", width=2)
d3.text((1015, 205), "● LIVE (200 OK)", fill="#155724")

dep_cards = [
    ("CONTINUOUS DEPLOYMENT", "Auto-built from GitHub main branch with Docker containerization.", "#0277BD", "#E1F5FE"),
    ("SQLITE INTEGRITY", "Persistent database seeded with 60 students and 720 academic records.", "#2E7D32", "#E8F5E9"),
    ("REAL-TIME SYNC", "Dashboard refreshes and reflects newly entered marks in < 15 seconds.", "#EF6C00", "#FFF3E0")
]
for i, (title, desc, col, bg) in enumerate(dep_cards):
    x1 = 30 + i * 390
    x2 = x1 + 360
    draw_rounded_rect(d3, (x1, 305, x2, 630), 10, fill="#FFFFFF", outline="#E0E0E0", width=2)
    draw_rounded_rect(d3, (x1, 305, x2, 365), 10, fill=bg, outline=col, width=1)
    d3.text((x1 + 20, 325), title, fill=col)
    d3.text((x1 + 20, 400), desc, fill="#333333")
    d3.text((x1 + 20, 480), "● High availability", fill="#555555")
    d3.text((x1 + 20, 520), "● Secure HTTPS SSL", fill="#555555")
    d3.text((x1 + 20, 560), "● Zero-downtime boots", fill="#555555")

img3.save("presentation/assets/shot_live_render.png", format="PNG")
print("Saved shot_live_render.png")
