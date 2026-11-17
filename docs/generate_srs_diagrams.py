import os
from PIL import Image, ImageDraw, ImageFont

os.makedirs("docs/diagrams", exist_ok=True)

def draw_rect(d, xy, fill=None, outline="#222222", width=2, radius=8):
    d.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)

def draw_arrow(d, p1, p2, color="#222222", width=2, arrow_size=8):
    x1, y1 = p1
    x2, y2 = p2
    d.line([x1, y1, x2, y2], fill=color, width=width)
    import math
    angle = math.atan2(y2 - y1, x2 - x1)
    d.polygon([
        (x2, y2),
        (x2 - arrow_size * math.cos(angle - math.pi / 6), y2 - arrow_size * math.sin(angle - math.pi / 6)),
        (x2 - arrow_size * math.cos(angle + math.pi / 6), y2 - arrow_size * math.sin(angle + math.pi / 6)),
    ], fill=color)

def draw_bi_arrow(d, p1, p2, color="#222222", width=2, arrow_size=8):
    draw_arrow(d, p1, p2, color, width, arrow_size)
    draw_arrow(d, p2, p1, color, width, arrow_size)

# =========================================================================
# 1. Figure 3.1: High-Level System Architecture
# =========================================================================
def make_fig3_1():
    w, h = 1200, 750
    img = Image.new("RGB", (w, h), "#FFFFFF")
    d = ImageDraw.Draw(img)

    # Title
    d.text((600, 35), "System Architecture", fill="#111111", anchor="mm")

    # Top Row: 3 Dashboards
    dashboards = [
        (150, "HOD\nDashboard"),
        (600, "Faculty\nDashboard"),
        (1050, "Student\nDashboard")
    ]
    for cx, txt in dashboards:
        draw_rect(d, (cx - 120, 90, cx + 120, 180), fill="#F8FAF9", outline="#0B5E36", width=2)
        d.text((cx, 135), txt, fill="#0B5E36", anchor="mm")

    # Arrows to Streamlit
    draw_arrow(d, (150, 180), (450, 260), "#0B5E36", 2)
    draw_arrow(d, (600, 180), (600, 260), "#0B5E36", 2)
    draw_arrow(d, (1050, 180), (750, 260), "#0B5E36", 2)

    # Streamlit Layer
    draw_rect(d, (200, 260, 1000, 350), fill="#E8F5E9", outline="#0B5E36", width=2, radius=12)
    d.text((600, 290), "Streamlit Presentation Layer", fill="#073B22", anchor="mm")
    d.text((600, 320), "Interactive Web Portals • Charts • Real-Time UI Sync", fill="#555555", anchor="mm")

    # Arrow to FastAPI
    draw_bi_arrow(d, (600, 350), (600, 420), "#073B22", 2)

    # FastAPI Layer
    draw_rect(d, (150, 420, 1050, 520), fill="#E1F5FE", outline="#0277BD", width=2, radius=12)
    d.text((600, 450), "FastAPI Backend Layer", fill="#01579B", anchor="mm")
    d.text((600, 485), "Authentication (JWT & bcrypt) • Business Logic • RESTful API Endpoints", fill="#333333", anchor="mm")

    # Arrows to Bottom 3 Services
    draw_arrow(d, (350, 520), (230, 600), "#0277BD", 2)
    draw_arrow(d, (600, 520), (600, 600), "#0277BD", 2)
    draw_arrow(d, (850, 520), (970, 600), "#0277BD", 2)

    # Bottom 3 Blocks
    draw_rect(d, (80, 600, 380, 700), fill="#F3E5F5", outline="#7B1FA2", width=2)
    d.text((230, 630), "SQLite Database", fill="#4A148C", anchor="mm")
    d.text((230, 665), "Students • Courses • Marks • Attendance", fill="#555555", anchor="mm")

    draw_rect(d, (450, 600, 750, 700), fill="#FFF3E0", outline="#E65100", width=2)
    d.text((600, 630), "ML Analytics Engine", fill="#BF360C", anchor="mm")
    d.text((600, 665), "scikit-learn • Pandas • NumPy", fill="#555555", anchor="mm")

    draw_rect(d, (820, 600, 1120, 700), fill="#E8EAF6", outline="#303F9F", width=2)
    d.text((970, 630), "Judge0 API Service", fill="#1A237E", anchor="mm")
    d.text((970, 665), "Code Execution • Automated Test Cases", fill="#555555", anchor="mm")

    img.save("docs/diagrams/fig3_1_architecture.png")
    print("Saved fig3_1_architecture.png")

# =========================================================================
# 2. Figure 3.2: Entity Relationship Diagram
# =========================================================================
def make_fig3_2():
    w, h = 1200, 750
    img = Image.new("RGB", (w, h), "#FFFFFF")
    d = ImageDraw.Draw(img)

    d.text((600, 30), "Entity Relationship Diagram (ERD)", fill="#111111", anchor="mm")

    # 3x3 Grid of entities
    entities = {
        "USER": (80, 80, 340, 200, "#E8F5E9", "#0B5E36"),
        "FACULTY": (470, 80, 730, 200, "#E1F5FE", "#0277BD"),
        "ASSIGNMENT": (860, 80, 1120, 200, "#FFF3E0", "#E65100"),

        "STUDENT": (80, 300, 340, 420, "#E8F5E9", "#0B5E36"),
        "COURSE": (470, 300, 730, 420, "#E1F5FE", "#0277BD"),
        "SUBMISSION": (860, 300, 1120, 420, "#FFF3E0", "#E65100"),

        "ACADEMIC RECORD": (80, 520, 340, 640, "#F3E5F5", "#7B1FA2"),
        "ATTENDANCE": (470, 520, 730, 640, "#F3E5F5", "#7B1FA2"),
        "RISK PREDICTION": (860, 520, 1120, 640, "#FFEBEE", "#C62828")
    }

    entity_texts = {
        "USER": ("USER", "PK: user_id\nemail, password_hash, role"),
        "FACULTY": ("FACULTY", "PK: faculty_id, FK: user_id\nname, email, department"),
        "ASSIGNMENT": ("ASSIGNMENT", "PK: assignment_id\nFK: faculty_id, course_id, test_cases"),
        "STUDENT": ("STUDENT", "PK: student_id, FK: user_id\nname, enrollment_no, section"),
        "COURSE": ("COURSE", "PK: course_id, FK: faculty_id\ncourse_code, course_name, semester"),
        "SUBMISSION": ("SUBMISSION", "PK: submission_id\nFK: assignment_id, student_id, score"),
        "ACADEMIC RECORD": ("ACADEMIC RECORD", "PK: record_id\nFK: student_id, course_id, marks"),
        "ATTENDANCE": ("ATTENDANCE", "PK: attendance_id\nFK: student_id, semester, percentage"),
        "RISK PREDICTION": ("RISK PREDICTION", "PK: prediction_id, FK: student_id\nrisk_level, model_result, date")
    }

    for k, (x1, y1, x2, y2, bg, border) in entities.items():
        draw_rect(d, (x1, y1, x2, y2), fill=bg, outline=border, width=2)
        title, sub = entity_texts[k]
        d.text(((x1 + x2)//2, y1 + 22), title, fill=border, anchor="mm")
        d.line([x1, y1 + 40, x2, y1 + 40], fill=border, width=1)
        d.text(((x1 + x2)//2, y1 + 75), sub, fill="#333333", anchor="mm")

    # Connect relationships cleanly with cardinality labels
    # USER -> STUDENT (1:1)
    d.line([210, 200, 210, 300], fill="#0B5E36", width=2)
    d.text((220, 245), "1 : 1", fill="#0B5E36")

    # USER -> FACULTY (1:1)
    d.line([340, 140, 470, 140], fill="#0277BD", width=2)
    d.text((400, 122), "1 : 1", fill="#0277BD")

    # FACULTY -> COURSE (1:M)
    d.line([600, 200, 600, 300], fill="#0277BD", width=2)
    d.text((610, 245), "1 : M", fill="#0277BD")

    # FACULTY -> ASSIGNMENT (1:M)
    d.line([730, 140, 860, 140], fill="#E65100", width=2)
    d.text((790, 122), "1 : M", fill="#E65100")

    # STUDENT -> ACADEMIC RECORD (1:M)
    d.line([210, 420, 210, 520], fill="#7B1FA2", width=2)
    d.text((220, 465), "1 : M", fill="#7B1FA2")

    # COURSE -> ACADEMIC RECORD (1:M)
    d.line([500, 420, 340, 530], fill="#7B1FA2", width=2)
    d.text((420, 475), "1 : M", fill="#7B1FA2")

    # STUDENT -> ATTENDANCE (1:M)
    d.line([340, 380, 470, 530], fill="#7B1FA2", width=2)
    d.text((410, 435), "1 : M", fill="#7B1FA2")

    # STUDENT -> RISK PREDICTION (1:M)
    d.line([340, 410, 860, 550], fill="#C62828", width=2)
    d.text((600, 470), "1 : M", fill="#C62828")

    # ASSIGNMENT -> SUBMISSION (1:M)
    d.line([990, 200, 990, 300], fill="#E65100", width=2)
    d.text((1000, 245), "1 : M", fill="#E65100")

    # STUDENT -> SUBMISSION (1:M)
    d.line([340, 360, 860, 360], fill="#E65100", width=2)
    d.text((600, 345), "1 : M", fill="#E65100")

    img.save("docs/diagrams/fig3_2_erd.png")
    print("Saved fig3_2_erd.png")

# =========================================================================
# 3. Figure 3.3: Use Case Diagram
# =========================================================================
def make_fig3_3():
    w, h = 1200, 800
    img = Image.new("RGB", (w, h), "#FFFFFF")
    d = ImageDraw.Draw(img)

    d.text((600, 30), "Use Case Diagram", fill="#111111", anchor="mm")

    # System boundary box
    draw_rect(d, (300, 70, 950, 750), fill="#FAFAFA", outline="#333333", width=2, radius=4)
    d.text((625, 95), "Academic Performance Analytics System", fill="#0B5E36", anchor="mm")

    # Actors: HOD (Left), Faculty (Right top), Student (Right bottom)
    def draw_actor(x, y, name, col):
        d.ellipse([x-20, y-45, x+20, y-5], outline=col, width=2) # head
        d.line([x, y-5, x, y+45], fill=col, width=2) # body
        d.line([x-30, y+15, x+30, y+15], fill=col, width=2) # arms
        d.line([x, y+45, x-25, y+85], fill=col, width=2) # left leg
        d.line([x, y+45, x+25, y+85], fill=col, width=2) # right leg
        d.text((x, y+105), name, fill=col, anchor="mm")

    draw_actor(140, 370, "HOD", "#D84315")
    draw_actor(1080, 240, "Faculty", "#1565C0")
    draw_actor(1080, 560, "Student", "#2E7D32")

    # Use Cases (Ovals in 2 columns)
    use_cases = [
        (470, 160, "Secure Login"),
        (760, 160, "View Dashboard"),
        (470, 270, "View Subject\nPerformance"),
        (760, 270, "Generate Reports"),
        (470, 400, "Manage Marks /\nAttendance"),
        (760, 400, "Risk Prediction"),
        (470, 530, "Create Coding\nAssignment"),
        (760, 530, "Submit / Evaluate\nCode"),
        (615, 660, "View Coding\nLeaderboard")
    ]

    for cx, cy, label in use_cases:
        d.ellipse([cx - 105, cy - 35, cx + 105, cy + 35], fill="#FFFFFF", outline="#0B5E36", width=2)
        d.text((cx, cy), label, fill="#222222", anchor="mm")

    # Connect HOD lines
    d.line([165, 360, 365, 160], fill="#D84315", width=2) # Login
    d.line([165, 370, 655, 160], fill="#D84315", width=2) # View Dashboard
    d.line([165, 370, 365, 270], fill="#D84315", width=2) # Subject Perf
    d.line([165, 380, 655, 270], fill="#D84315", width=2) # Reports
    d.line([165, 390, 655, 400], fill="#D84315", width=2) # Risk Pred

    # Connect Faculty lines
    d.line([1050, 230, 575, 160], fill="#1565C0", width=2) # Login
    d.line([1050, 240, 865, 160], fill="#1565C0", width=2) # View Dashboard
    d.line([1050, 250, 575, 270], fill="#1565C0", width=2) # Subject Perf
    d.line([1050, 260, 575, 400], fill="#1565C0", width=2) # Manage Marks
    d.line([1050, 270, 575, 530], fill="#1565C0", width=2) # Create Assignment

    # Connect Student lines
    d.line([1050, 550, 575, 160], fill="#2E7D32", width=2) # Login
    d.line([1050, 560, 865, 160], fill="#2E7D32", width=2) # View Dashboard
    d.line([1050, 570, 865, 400], fill="#2E7D32", width=2) # Risk Pred
    d.line([1050, 580, 865, 530], fill="#2E7D32", width=2) # Submit Code
    d.line([1050, 590, 720, 660], fill="#2E7D32", width=2) # Leaderboard

    img.save("docs/diagrams/fig3_3_usecase.png")
    print("Saved fig3_3_usecase.png")

# =========================================================================
# 4. Figure 3.4: Context Diagram (Level 0 / Context)
# =========================================================================
def make_fig3_4():
    w, h = 1200, 650
    img = Image.new("RGB", (w, h), "#FFFFFF")
    d = ImageDraw.Draw(img)

    d.text((600, 30), "Context Diagram (Level - Context)", fill="#111111", anchor="mm")

    # Central System Box
    draw_rect(d, (430, 240, 770, 410), fill="#E8F5E9", outline="#0B5E36", width=2, radius=12)
    d.text((600, 305), "Academic Performance", fill="#073B22", anchor="mm")
    d.text((600, 340), "Analytics System", fill="#073B22", anchor="mm")

    # 4 External Entities
    # 1. HOD (Top Left)
    draw_rect(d, (80, 100, 280, 190), fill="#FFF3E0", outline="#E65100", width=2)
    d.text((180, 145), "HOD", fill="#BF360C", anchor="mm")

    # 2. Student (Top Right)
    draw_rect(d, (920, 100, 1120, 190), fill="#E8F5E9", outline="#2E7D32", width=2)
    d.text((1020, 145), "Student", fill="#1B5E20", anchor="mm")

    # 3. Faculty (Bottom Left)
    draw_rect(d, (80, 460, 280, 550), fill="#E1F5FE", outline="#0277BD", width=2)
    d.text((180, 505), "Faculty", fill="#01579B", anchor="mm")

    # 4. Judge0 API (Bottom Right)
    draw_rect(d, (920, 460, 1120, 550), fill="#EDE7F6", outline="#512DA8", width=2)
    d.text((1020, 505), "Judge0 API", fill="#311B92", anchor="mm")

    # Flow arrows with clear non-overlapping annotations
    # HOD -> System
    draw_arrow(d, (280, 160), (440, 260), "#E65100", 2)
    d.text((320, 195), "Report Requests", fill="#BF360C")

    # System -> HOD
    draw_arrow(d, (430, 290), (270, 190), "#E65100", 2)
    d.text((290, 255), "Reports / Academic Insights", fill="#BF360C")

    # Student -> System
    draw_arrow(d, (920, 180), (760, 270), "#2E7D32", 2)
    d.text((790, 205), "View Requests / Code Submissions", fill="#1B5E20")

    # System -> Student
    draw_arrow(d, (770, 250), (930, 160), "#2E7D32", 2)
    d.text((820, 285), "Marks / Attendance / Risk / Scores", fill="#1B5E20")

    # Faculty -> System
    draw_arrow(d, (280, 490), (440, 390), "#0277BD", 2)
    d.text((270, 425), "Marks / Attendance / Assignments", fill="#01579B")

    # System -> Faculty
    draw_arrow(d, (430, 370), (270, 470), "#0277BD", 2)
    d.text((320, 480), "Confirmations / Submissions", fill="#01579B")

    # System -> Judge0 API
    draw_arrow(d, (760, 380), (920, 480), "#512DA8", 2)
    d.text((800, 415), "Code Execution Request", fill="#311B92")

    # Judge0 API -> System
    draw_arrow(d, (930, 510), (770, 410), "#512DA8", 2)
    d.text((810, 485), "Test Results / Execution Scores", fill="#311B92")

    img.save("docs/diagrams/fig3_4_context.png")
    print("Saved fig3_4_context.png")

# =========================================================================
# 5. Figure 3.5: Level 0 Data Flow Diagram
# =========================================================================
def make_fig3_5():
    w, h = 1200, 750
    img = Image.new("RGB", (w, h), "#FFFFFF")
    d = ImageDraw.Draw(img)

    d.text((600, 30), "Level 0 Data Flow Diagram", fill="#111111", anchor="mm")

    # Entity: Users
    draw_rect(d, (60, 80, 220, 160), fill="#FFF3E0", outline="#E65100", width=2)
    d.text((140, 120), "Users\n(HOD/Fac/Stu)", fill="#BF360C", anchor="mm")

    # Process 1.0: Authentication
    draw_rect(d, (350, 80, 550, 160), fill="#E8F5E9", outline="#0B5E36", width=2, radius=16)
    d.text((450, 110), "1.0", fill="#0B5E36", anchor="mm")
    d.text((450, 130), "Authentication", fill="#073B22", anchor="mm")

    # Data Store D1: User DB
    d.line([880, 80, 1100, 80], fill="#0277BD", width=2)
    d.line([880, 160, 1100, 160], fill="#0277BD", width=2)
    d.line([880, 80, 880, 160], fill="#0277BD", width=2)
    d.text((990, 120), "D1: User Database", fill="#01579B", anchor="mm")

    # Arrow Users -> 1.0 -> D1
    draw_arrow(d, (220, 120), (350, 120), "#0B5E36", 2)
    d.text((245, 100), "Credentials", fill="#555555")
    draw_arrow(d, (550, 120), (880, 120), "#0B5E36", 2)
    d.text((680, 100), "User Validation", fill="#555555")

    # Process 2.0: Academic Data Management
    draw_rect(d, (350, 220, 550, 300), fill="#E8F5E9", outline="#0B5E36", width=2, radius=16)
    d.text((450, 250), "2.0", fill="#0B5E36", anchor="mm")
    d.text((450, 270), "Academic Data", fill="#073B22", anchor="mm")

    # Process 3.0: Attendance Management
    draw_rect(d, (350, 360, 550, 440), fill="#E8F5E9", outline="#0B5E36", width=2, radius=16)
    d.text((450, 390), "3.0", fill="#0B5E36", anchor="mm")
    d.text((450, 410), "Attendance Tracking", fill="#073B22", anchor="mm")

    # Process 4.0: ML Analytics Engine
    draw_rect(d, (680, 290, 880, 370), fill="#FFF3E0", outline="#E65100", width=2, radius=16)
    d.text((780, 320), "4.0", fill="#BF360C", anchor="mm")
    d.text((780, 340), "ML Risk Analytics", fill="#BF360C", anchor="mm")

    # Data Store D2: Academic DB
    d.line([950, 290, 1150, 290], fill="#0277BD", width=2)
    d.line([950, 370, 1150, 370], fill="#0277BD", width=2)
    d.line([950, 290, 950, 370], fill="#0277BD", width=2)
    d.text((1050, 330), "D2: Academic DB", fill="#01579B", anchor="mm")

    # Arrow 2.0 & 3.0 -> 4.0 -> D2
    draw_arrow(d, (550, 260), (680, 310), "#0B5E36", 2)
    d.text((570, 270), "Marks Data", fill="#555555")
    draw_arrow(d, (550, 400), (680, 350), "#0B5E36", 2)
    d.text((565, 390), "Attendance %", fill="#555555")
    draw_arrow(d, (880, 330), (950, 330), "#E65100", 2)
    d.text((885, 310), "Risk Results", fill="#555555")

    # Process 5.0: Coding Assignment Module
    draw_rect(d, (350, 500, 550, 580), fill="#E8F5E9", outline="#0B5E36", width=2, radius=16)
    d.text((450, 530), "5.0", fill="#0B5E36", anchor="mm")
    d.text((450, 550), "Coding Module", fill="#073B22", anchor="mm")

    # Process 6.0: Code Evaluation Engine
    draw_rect(d, (680, 500, 880, 580), fill="#EDE7F6", outline="#512DA8", width=2, radius=16)
    d.text((780, 530), "6.0", fill="#311B92", anchor="mm")
    d.text((780, 550), "Code Evaluation", fill="#311B92", anchor="mm")

    # Data Store D3: Results DB
    d.line([950, 500, 1150, 500], fill="#0277BD", width=2)
    d.line([950, 580, 1150, 580], fill="#0277BD", width=2)
    d.line([950, 500, 950, 580], fill="#0277BD", width=2)
    d.text((1050, 540), "D3: Results DB", fill="#01579B", anchor="mm")

    draw_arrow(d, (550, 540), (680, 540), "#0B5E36", 2)
    d.text((585, 520), "Student Code", fill="#555555")
    draw_arrow(d, (880, 540), (950, 540), "#512DA8", 2)
    d.text((895, 520), "Scores", fill="#555555")

    img.save("docs/diagrams/fig3_5_dfd0.png")
    print("Saved fig3_5_dfd0.png")

# =========================================================================
# 6. Figure 3.6: Level 1 DFD - Academic Analytics & Risk Prediction
# =========================================================================
def make_fig3_6():
    w, h = 1200, 700
    img = Image.new("RGB", (w, h), "#FFFFFF")
    d = ImageDraw.Draw(img)

    d.text((600, 30), "Level 1 DFD - Academic Analytics & Risk Prediction", fill="#111111", anchor="mm")

    # Stores D1 & D2 on Left
    d.line([80, 120, 280, 120], fill="#0277BD", width=2)
    d.line([80, 200, 280, 200], fill="#0277BD", width=2)
    d.line([80, 120, 80, 200], fill="#0277BD", width=2)
    d.text((180, 160), "D1: Academic Records", fill="#01579B", anchor="mm")

    d.line([80, 280, 280, 280], fill="#0277BD", width=2)
    d.line([80, 360, 280, 360], fill="#0277BD", width=2)
    d.line([80, 280, 80, 360], fill="#0277BD", width=2)
    d.text((180, 320), "D2: Attendance Records", fill="#01579B", anchor="mm")

    # Process 3.1: Collect & Validate Data
    draw_rect(d, (380, 190, 580, 290), fill="#E8F5E9", outline="#0B5E36", width=2, radius=16)
    d.text((480, 225), "3.1", fill="#0B5E36", anchor="mm")
    d.text((480, 255), "Collect & Validate\nData", fill="#073B22", anchor="mm")

    draw_arrow(d, (280, 160), (380, 220), "#0B5E36", 2)
    d.text((295, 175), "Marks Data", fill="#555555")
    draw_arrow(d, (280, 320), (380, 260), "#0B5E36", 2)
    d.text((285, 300), "Attendance %", fill="#555555")

    # Process 3.2: Process Features
    draw_rect(d, (680, 190, 880, 290), fill="#E8F5E9", outline="#0B5E36", width=2, radius=16)
    d.text((780, 225), "3.2", fill="#0B5E36", anchor="mm")
    d.text((780, 255), "Process Features\n(Pandas / NumPy)", fill="#073B22", anchor="mm")

    draw_arrow(d, (580, 240), (680, 240), "#0B5E36", 2)
    d.text((600, 220), "Validated Data", fill="#555555")

    # Process 3.3: ML Prediction
    draw_rect(d, (380, 430, 580, 530), fill="#FFF3E0", outline="#E65100", width=2, radius=16)
    d.text((480, 465), "3.3", fill="#BF360C", anchor="mm")
    d.text((480, 495), "ML Prediction\n(scikit-learn)", fill="#BF360C", anchor="mm")

    # Arrow 3.2 -> 3.3
    draw_arrow(d, (730, 290), (530, 430), "#E65100", 2)
    d.text((645, 370), "Feature Vectors", fill="#555555")

    # Data Store D3: Risk Predictions
    d.line([680, 450, 880, 450], fill="#0277BD", width=2)
    d.line([680, 530, 880, 530], fill="#0277BD", width=2)
    d.line([680, 450, 680, 530], fill="#0277BD", width=2)
    d.text((780, 490), "D3: Risk Predictions", fill="#01579B", anchor="mm")

    draw_arrow(d, (580, 480), (680, 480), "#E65100", 2)
    d.text((605, 460), "Risk Class", fill="#555555")

    # Dashboard on the right
    draw_rect(d, (970, 280, 1150, 440), fill="#E1F5FE", outline="#0277BD", width=2, radius=12)
    d.text((1060, 345), "Analytics", fill="#01579B", anchor="mm")
    d.text((1060, 375), "Dashboard", fill="#01579B", anchor="mm")

    draw_arrow(d, (880, 240), (970, 330), "#0B5E36", 2)
    d.text((890, 275), "Statistical Analytics", fill="#555555")
    draw_arrow(d, (880, 480), (970, 390), "#E65100", 2)
    d.text((890, 440), "Risk Results", fill="#555555")

    img.save("docs/diagrams/fig3_6_dfd1.png")
    print("Saved fig3_6_dfd1.png")

# =========================================================================
# 7. Figure 3.7: Class Diagram
# =========================================================================
def make_fig3_7():
    w, h = 1200, 850
    img = Image.new("RGB", (w, h), "#FFFFFF")
    d = ImageDraw.Draw(img)

    d.text((600, 30), "Class Diagram", fill="#111111", anchor="mm")

    # 3x3 layout of UML class boxes with Attributes and Methods
    classes = {
        "User": (60, 70, 340, 220, [
            "+ user_id: int", "+ name: str", "+ email: str", "+ password_hash: str", "+ role: str"
        ], [
            "+ verify_password()", "+ generate_token()"
        ]),
        "Student": (440, 70, 740, 220, [
            "+ student_id: int", "+ user_id: int", "+ name: str", "+ enrollment_no: str", "+ section: str"
        ], [
            "+ get_marks()", "+ view_risk_status()", "+ submit_code()"
        ]),
        "Faculty": (840, 70, 1140, 220, [
            "+ faculty_id: int", "+ user_id: int", "+ name: str", "+ email: str", "+ department: str"
        ], [
            "+ enter_marks()", "+ update_attendance()", "+ create_assignment()"
        ]),

        "Course": (60, 290, 340, 440, [
            "+ course_id: int", "+ course_code: str", "+ course_name: str", "+ semester: int", "+ faculty_id: int"
        ], [
            "+ get_course_details()", "+ get_enrolled_records()"
        ]),
        "AcademicRecord": (440, 290, 740, 440, [
            "+ record_id: int", "+ student_id: int", "+ course_id: int", "+ semester: int", "+ marks: float"
        ], [
            "+ update_mark()", "+ get_pass_status()"
        ]),
        "Attendance": (840, 290, 1140, 440, [
            "+ attendance_id: int", "+ student_id: int", "+ semester: int", "+ attendance_pct: float"
        ], [
            "+ update_percentage()", "+ is_eligible_75()"
        ]),

        "Assignment": (60, 510, 340, 660, [
            "+ assignment_id: int", "+ faculty_id: int", "+ course_id: int", "+ title: str", "+ test_cases: JSON"
        ], [
            "+ add_test_case()", "+ get_submissions()"
        ]),
        "Submission": (440, 510, 740, 660, [
            "+ submission_id: int", "+ assignment_id: int", "+ student_id: int", "+ code: str", "+ score: float"
        ], [
            "+ evaluate_test_cases()", "+ compute_score()"
        ]),
        "RiskPrediction": (840, 510, 1140, 660, [
            "+ prediction_id: int", "+ student_id: int", "+ risk_level: str", "+ prediction_date: datetime"
        ], [
            "+ compute_risk()", "+ get_recommendations()"
        ])
    }

    for name, (x1, y1, x2, y2, attrs, methods) in classes.items():
        draw_rect(d, (x1, y1, x2, y2), fill="#FFFFFF", outline="#0B5E36", width=2, radius=4)
        # Title bar
        d.rectangle([x1, y1, x2, y1 + 32], fill="#E8F5E9")
        d.text(((x1 + x2)//2, y1 + 16), name, fill="#073B22", anchor="mm")
        d.line([x1, y1 + 32, x2, y1 + 32], fill="#0B5E36", width=1)

        # Attributes
        ay = y1 + 45
        for att in attrs:
            d.text((x1 + 10, ay), att, fill="#222222")
            ay += 18

        # Line
        d.line([x1, ay + 4, x2, ay + 4], fill="#0B5E36", width=1)
        my = ay + 12
        for met in methods:
            d.text((x1 + 10, my), met, fill="#0277BD")
            my += 18

    # UML Connections
    # User - Student & Faculty
    d.line([340, 140, 440, 140], fill="#0B5E36", width=2)
    d.line([740, 140, 840, 140], fill="#0B5E36", width=2)

    # Student - AcademicRecord & Attendance & RiskPrediction
    d.line([590, 220, 590, 290], fill="#0B5E36", width=2)
    d.line([740, 180, 840, 340], fill="#0B5E36", width=2)
    d.line([740, 200, 840, 550], fill="#0B5E36", width=2)

    # Course - AcademicRecord
    d.line([340, 360, 440, 360], fill="#0B5E36", width=2)

    # Assignment - Submission
    d.line([340, 580, 440, 580], fill="#0B5E36", width=2)

    # Student - Submission
    d.line([590, 440, 590, 510], fill="#0B5E36", width=2)

    img.save("docs/diagrams/fig3_7_class.png")
    print("Saved fig3_7_class.png")

# =========================================================================
# 8. Figure 3.8: Sequence Diagram - Coding Assignment Evaluation
# =========================================================================
def make_fig3_8():
    w, h = 1200, 750
    img = Image.new("RGB", (w, h), "#FFFFFF")
    d = ImageDraw.Draw(img)

    d.text((600, 30), "Sequence Diagram - Coding Assignment Evaluation", fill="#111111", anchor="mm")

    actors = [
        ("Faculty", 100),
        ("Student", 300),
        ("Streamlit UI", 520),
        ("FastAPI Backend", 740),
        ("Judge0 API", 940),
        ("Database", 1100)
    ]

    # Draw Actor Headers and Lifelines
    for name, x in actors:
        draw_rect(d, (x - 65, 70, x + 65, 115), fill="#E8F5E9", outline="#0B5E36", width=2, radius=6)
        d.text((x, 92), name, fill="#073B22", anchor="mm")
        d.line([x, 115, x, 710], fill="#9E9E9E", width=1) # lifeline

    # Steps in sequence
    steps = [
        (100, 520, 150, "1. Create assignment with testcases", "#0B5E36"),
        (520, 740, 190, "2. POST /assignments", "#0277BD"),
        (740, 1100, 230, "3. INSERT Assignment & Testcases", "#4A148C"),
        (1100, 740, 270, "4. DB Confirmation [201 Created]", "#666666"),
        (300, 520, 330, "5. Select assignment & enter code", "#0B5E36"),
        (520, 740, 370, "6. POST /submissions (code, lang)", "#0277BD"),
        (740, 940, 420, "7. Execute code against testcases", "#E65100"),
        (940, 740, 480, "8. Return execution output & verdicts", "#E65100"),
        (740, 1100, 530, "9. Store score & submission status", "#4A148C"),
        (1100, 740, 570, "10. Saved Confirmation", "#666666"),
        (740, 520, 610, "11. Return score & testcase breakdown", "#0277BD"),
        (520, 300, 650, "12. Display score (100/100 Accepted) & update Leaderboard", "#0B5E36")
    ]

    for x1, x2, y, msg, col in steps:
        draw_arrow(d, (x1, y), (x2, y), col, 2)
        mid_x = (x1 + x2) // 2
        d.text((mid_x, y - 14), msg, fill=col, anchor="mm")

    img.save("docs/diagrams/fig3_8_sequence.png")
    print("Saved fig3_8_sequence.png")

# =========================================================================
# 9. Figure 4.1: Dashboard Interface Mockup
# =========================================================================
def make_fig4_1():
    w, h = 1200, 750
    img = Image.new("RGB", (w, h), "#FFFFFF")
    d = ImageDraw.Draw(img)

    # Outer border
    draw_rect(d, (40, 30, 1160, 710), fill="#F8FAF9", outline="#222222", width=3, radius=4)

    # Title
    d.text((600, 65), "ACADEMIC PERFORMANCE DASHBOARD", fill="#111111", anchor="mm")

    # 4 KPI Cards
    kpis = [
        ("Total Students", "60"),
        ("Average Marks", "74%"),
        ("Attendance", "82%"),
        ("High Risk", "8")
    ]
    for i, (t, v) in enumerate(kpis):
        x1 = 70 + i * 270
        x2 = x1 + 240
        draw_rect(d, (x1, 105, x2, 195), fill="#FFFFFF", outline="#333333", width=2)
        d.text(((x1 + x2)//2, 135), t, fill="#555555", anchor="mm")
        d.text(((x1 + x2)//2, 168), v, fill="#111111", anchor="mm")

    # Left: Subject-wise Average Performance
    draw_rect(d, (70, 225, 590, 510), fill="#FFFFFF", outline="#333333", width=2)
    d.text((330, 255), "Subject-wise Average Performance", fill="#111111", anchor="mm")

    subjects = [("Python", 68), ("DBMS", 82), ("CN", 65), ("OS", 74), ("AI", 89)]
    for i, (sub, val) in enumerate(subjects):
        bx = 105 + i * 95
        bh = int(val * 1.8)
        by = 460 - bh
        d.rectangle([bx, by, bx + 55, 460], fill="#E8F5E9", outline="#0B5E36", width=2)
        d.text((bx + 27, by - 12), f"{val}%", fill="#0B5E36", anchor="mm")
        d.text((bx + 27, 480), sub, fill="#333333", anchor="mm")

    # Right: Academic Risk Distribution
    draw_rect(d, (620, 225, 1130, 510), fill="#FFFFFF", outline="#333333", width=2)
    d.text((875, 255), "Academic Risk Distribution", fill="#111111", anchor="mm")

    risk_bars = [("Low", 38, "#D4EDDA", "#28A745"), ("Medium", 14, "#FFF3CD", "#FFC107"), ("High", 8, "#F8D7DA", "#DC3545")]
    for i, (lvl, count, bg, col) in enumerate(risk_bars):
        bx = 680 + i * 150
        bh = count * 4.5
        by = 460 - bh
        d.rectangle([bx, by, bx + 85, 460], fill=bg, outline=col, width=2)
        d.text((bx + 42, by - 14), f"{count} ({int(count/60*100)}%)", fill=col, anchor="mm")
        d.text((bx + 42, 480), lvl, fill="#333333", anchor="mm")

    # Bottom: Coding Assignment Leaderboard
    draw_rect(d, (70, 540, 1130, 680), fill="#FFFFFF", outline="#333333", width=2)
    d.text((600, 570), "Coding Assignment Leaderboard", fill="#111111", anchor="mm")

    lb_entries = [
        "1. Student A   95 pts",
        "2. Student B   91 pts",
        "3. Student C   88 pts",
        "4. Student D   85 pts"
    ]
    for i, item in enumerate(lb_entries):
        lx = 120 + i * 260
        d.text((lx, 630), item, fill="#222222")

    img.save("docs/diagrams/fig4_1_mockup.png")
    print("Saved fig4_1_mockup.png")

if __name__ == "__main__":
    make_fig3_1()
    make_fig3_2()
    make_fig3_3()
    make_fig3_4()
    make_fig3_5()
    make_fig3_6()
    make_fig3_7()
    make_fig3_8()
    make_fig4_1()
