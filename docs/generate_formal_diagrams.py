import os
import math
from PIL import Image, ImageDraw, ImageFont

os.makedirs("docs/diagrams", exist_ok=True)

# Strict Academic Black & White Colors
BLACK = "#000000"
WHITE = "#FFFFFF"
LIGHT_GRAY = "#F0F0F0"
MID_GRAY = "#888888"

def draw_rect(d, xy, fill=WHITE, outline=BLACK, width=2):
    d.rectangle(xy, fill=fill, outline=outline, width=width)

def draw_rounded_rect(d, xy, radius=8, fill=WHITE, outline=BLACK, width=2):
    d.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)

def draw_diamond(d, center, size_x, size_y, fill=WHITE, outline=BLACK, width=2):
    cx, cy = center
    pts = [
        (cx, cy - size_y),
        (cx + size_x, cy),
        (cx, cy + size_y),
        (cx - size_x, cy)
    ]
    d.polygon(pts, fill=fill, outline=outline)
    # PIL polygon doesn't always stroke with width > 1 cleanly, so draw lines
    if width > 1:
        d.line([pts[0], pts[1], pts[2], pts[3], pts[0]], fill=outline, width=width)

def draw_oval(d, xy, fill=WHITE, outline=BLACK, width=2):
    d.ellipse(xy, fill=fill, outline=outline, width=width)

def draw_arrow(d, p1, p2, color=BLACK, width=2, arrow_size=8, dashed=False):
    x1, y1 = p1
    x2, y2 = p2
    if dashed:
        dist = math.hypot(x2 - x1, y2 - y1)
        dots = int(dist / 10)
        for i in range(dots):
            if i % 2 == 0:
                sx = x1 + (x2 - x1) * (i / dots)
                sy = y1 + (y2 - y1) * (i / dots)
                ex = x1 + (x2 - x1) * ((i + 1) / dots)
                ey = y1 + (y2 - y1) * ((i + 1) / dots)
                d.line([sx, sy, ex, ey], fill=color, width=width)
    else:
        d.line([x1, y1, x2, y2], fill=color, width=width)

    angle = math.atan2(y2 - y1, x2 - x1)
    d.polygon([
        (x2, y2),
        (x2 - arrow_size * math.cos(angle - math.pi / 6), y2 - arrow_size * math.sin(angle - math.pi / 6)),
        (x2 - arrow_size * math.cos(angle + math.pi / 6), y2 - arrow_size * math.sin(angle + math.pi / 6)),
    ], fill=color)

def draw_bi_arrow(d, p1, p2, color=BLACK, width=2, arrow_size=8):
    draw_arrow(d, p1, p2, color, width, arrow_size)
    draw_arrow(d, p2, p1, color, width, arrow_size)

# =========================================================================
# 1. Figure 3.1: High-Level System Architecture (Strict Black & White)
# =========================================================================
def make_fig3_1():
    w, h = 1200, 750
    img = Image.new("RGB", (w, h), WHITE)
    d = ImageDraw.Draw(img)

    d.text((600, 35), "Figure 3.1: High-Level System Architecture", fill=BLACK, anchor="mm")

    # Top Row: 3 Dashboards
    dashboards = [
        (180, "HOD\nDashboard"),
        (600, "Faculty\nDashboard"),
        (1020, "Student\nDashboard")
    ]
    for cx, txt in dashboards:
        draw_rounded_rect(d, (cx - 110, 85, cx + 110, 165), radius=10, fill=WHITE, outline=BLACK, width=2)
        d.text((cx, 125), txt, fill=BLACK, anchor="mm")

    # Arrows to Streamlit
    draw_arrow(d, (180, 165), (450, 245), BLACK, 2)
    draw_arrow(d, (600, 165), (600, 245), BLACK, 2)
    draw_arrow(d, (1020, 165), (750, 245), BLACK, 2)

    # Streamlit Presentation Layer
    draw_rounded_rect(d, (180, 245, 1020, 345), radius=12, fill=WHITE, outline=BLACK, width=2)
    d.text((600, 280), "Streamlit Presentation Layer", fill=BLACK, anchor="mm")
    d.text((600, 312), "(Interactive Web Interface • Dynamic Charts • Near Real-Time UI Sync)", fill=BLACK, anchor="mm")

    # Arrow to FastAPI
    draw_bi_arrow(d, (600, 345), (600, 420), BLACK, 2)

    # FastAPI Backend Layer
    draw_rounded_rect(d, (140, 420, 1060, 520), radius=12, fill=WHITE, outline=BLACK, width=2)
    d.text((600, 455), "FastAPI Backend", fill=BLACK, anchor="mm")
    d.text((600, 488), "Authentication (JWT & bcrypt) • Business Logic • RESTful API Endpoints", fill=BLACK, anchor="mm")

    # Arrows to Bottom 3 Services
    draw_arrow(d, (320, 520), (220, 595), BLACK, 2)
    draw_arrow(d, (600, 520), (600, 595), BLACK, 2)
    draw_arrow(d, (880, 520), (980, 595), BLACK, 2)

    # Bottom 3 Services
    draw_rounded_rect(d, (60, 595, 380, 705), radius=10, fill=WHITE, outline=BLACK, width=2)
    d.text((220, 635), "SQLite Database", fill=BLACK, anchor="mm")
    d.text((220, 670), "Students • Courses • Marks • Attendance", fill=BLACK, anchor="mm")

    draw_rounded_rect(d, (440, 595, 760, 705), radius=10, fill=WHITE, outline=BLACK, width=2)
    d.text((600, 635), "ML Analytics", fill=BLACK, anchor="mm")
    d.text((600, 670), "Pandas • NumPy • scikit-learn", fill=BLACK, anchor="mm")

    draw_rounded_rect(d, (820, 595, 1140, 705), radius=10, fill=WHITE, outline=BLACK, width=2)
    d.text((980, 635), "Judge0 API", fill=BLACK, anchor="mm")
    d.text((980, 670), "Code Execution & Test Cases", fill=BLACK, anchor="mm")

    img.save("docs/diagrams/fig3_1_architecture.png")
    print("Saved formal fig3_1_architecture.png")

# =========================================================================
# 2. Figure 3.2: Formal Chen ER Diagram (Rectangles for Entities, Diamonds for Relationships, Ovals for Attributes)
# =========================================================================
def make_fig3_2():
    w, h = 1300, 920
    img = Image.new("RGB", (w, h), WHITE)
    d = ImageDraw.Draw(img)

    d.text((650, 25), "Figure 3.2: Entity Relationship Diagram (ERD)", fill=BLACK, anchor="mm")

    # Helper for Chen Entity (Rectangle)
    def draw_entity(x, y, w_box, h_box, name):
        draw_rect(d, (x, y, x + w_box, y + h_box), fill=WHITE, outline=BLACK, width=2)
        d.text((x + w_box//2, y + h_box//2), name, fill=BLACK, anchor="mm")
        return (x + w_box//2, y + h_box//2)

    # Helper for Chen Relationship (Diamond)
    def draw_rel(cx, cy, rx, ry, name):
        draw_diamond(d, (cx, cy), rx, ry, fill=WHITE, outline=BLACK, width=2)
        d.text((cx, cy), name, fill=BLACK, anchor="mm")
        return (cx, cy)

    # Helper for Chen Attribute (Oval)
    def draw_attr(cx, cy, rx, ry, name, is_pk=False):
        draw_oval(d, (cx - rx, cy - ry, cx + rx, cy + ry), fill=WHITE, outline=BLACK, width=1)
        d.text((cx, cy), name, fill=BLACK, anchor="mm")
        if is_pk:
            tw = len(name) * 5.5
            d.line([cx - tw//2, cy + 6, cx + tw//2, cy + 6], fill=BLACK, width=1)

    # 1. USER entity (Top Left)
    e_user = draw_entity(80, 100, 160, 55, "USER")
    draw_attr(80, 45, 45, 18, "user_id", is_pk=True)
    d.line([80, 63, 120, 100], fill=BLACK, width=1)
    draw_attr(180, 45, 40, 18, "email")
    d.line([180, 63, 170, 100], fill=BLACK, width=1)
    draw_attr(260, 55, 40, 18, "role")
    d.line([250, 73, 210, 100], fill=BLACK, width=1)

    # 2. FACULTY entity (Top Center)
    e_fac = draw_entity(560, 100, 160, 55, "FACULTY")
    draw_attr(550, 45, 48, 18, "faculty_id", is_pk=True)
    d.line([550, 63, 600, 100], fill=BLACK, width=1)
    draw_attr(660, 45, 45, 18, "department")
    d.line([660, 63, 670, 100], fill=BLACK, width=1)

    # 3. ASSIGNMENT entity (Top Right)
    e_ass = draw_entity(1040, 100, 180, 55, "ASSIGNMENT")
    draw_attr(1040, 45, 55, 18, "assignment_id", is_pk=True)
    d.line([1050, 63, 1080, 100], fill=BLACK, width=1)
    draw_attr(1170, 45, 45, 18, "test_cases")
    d.line([1160, 63, 1140, 100], fill=BLACK, width=1)

    # 4. STUDENT entity (Mid Left)
    e_stu = draw_entity(80, 380, 160, 55, "STUDENT")
    draw_attr(50, 310, 48, 18, "student_id", is_pk=True)
    d.line([65, 328, 110, 380], fill=BLACK, width=1)
    draw_attr(155, 310, 50, 18, "enrollment_no")
    d.line([155, 328, 160, 380], fill=BLACK, width=1)
    draw_attr(255, 320, 38, 18, "section")
    d.line([240, 338, 200, 380], fill=BLACK, width=1)

    # 5. COURSE entity (Mid Center)
    e_cou = draw_entity(560, 380, 160, 55, "COURSE")
    draw_attr(530, 315, 48, 18, "course_id", is_pk=True)
    d.line([540, 333, 590, 380], fill=BLACK, width=1)
    draw_attr(640, 315, 48, 18, "course_name")
    d.line([640, 333, 640, 380], fill=BLACK, width=1)
    draw_attr(740, 325, 42, 18, "semester")
    d.line([720, 343, 690, 380], fill=BLACK, width=1)

    # 6. SUBMISSION entity (Mid Right)
    e_sub = draw_entity(1040, 380, 180, 55, "SUBMISSION")
    draw_attr(1040, 315, 55, 18, "submission_id", is_pk=True)
    d.line([1060, 333, 1090, 380], fill=BLACK, width=1)
    draw_attr(1170, 315, 40, 18, "score")
    d.line([1160, 333, 1140, 380], fill=BLACK, width=1)

    # 7. ACADEMIC RECORD entity (Bottom Left)
    e_rec = draw_entity(80, 710, 180, 55, "ACADEMIC RECORD")
    draw_attr(60, 810, 48, 18, "record_id", is_pk=True)
    d.line([80, 792, 120, 765], fill=BLACK, width=1)
    draw_attr(170, 810, 40, 18, "marks")
    d.line([170, 792, 170, 765], fill=BLACK, width=1)

    # 8. ATTENDANCE entity (Bottom Center)
    e_att = draw_entity(560, 710, 160, 55, "ATTENDANCE")
    draw_attr(540, 810, 50, 18, "attendance_id", is_pk=True)
    d.line([560, 792, 600, 765], fill=BLACK, width=1)
    draw_attr(670, 810, 52, 18, "percentage")
    d.line([660, 792, 650, 765], fill=BLACK, width=1)

    # 9. RISK PREDICTION entity (Bottom Right)
    e_rsk = draw_entity(1040, 710, 180, 55, "RISK PREDICTION")
    draw_attr(1040, 810, 52, 18, "prediction_id", is_pk=True)
    d.line([1060, 792, 1090, 765], fill=BLACK, width=1)
    draw_attr(1175, 810, 48, 18, "risk_level")
    d.line([1165, 792, 1140, 765], fill=BLACK, width=1)

    # Relationships (Diamonds) with explicit Chen notation:
    # 1. USER -> STUDENT [is_a] (1:1)
    r1 = draw_rel(160, 260, 45, 26, "Profile")
    d.line([160, 155, 160, 234], fill=BLACK, width=2)
    d.text((170, 185), "1", fill=BLACK)
    d.line([160, 286, 160, 380], fill=BLACK, width=2)
    d.text((170, 340), "1", fill=BLACK)

    # 2. USER -> FACULTY [has_profile] (1:1)
    r2 = draw_rel(400, 127, 45, 26, "Identifies")
    d.line([240, 127, 355, 127], fill=BLACK, width=2)
    d.text((275, 110), "1", fill=BLACK)
    d.line([445, 127, 560, 127], fill=BLACK, width=2)
    d.text((500, 110), "1", fill=BLACK)

    # 3. FACULTY -> COURSE [teaches] (1:M)
    r3 = draw_rel(640, 260, 45, 26, "Teaches")
    d.line([640, 155, 640, 234], fill=BLACK, width=2)
    d.text((650, 185), "1", fill=BLACK)
    d.line([640, 286, 640, 380], fill=BLACK, width=2)
    d.text((650, 340), "M", fill=BLACK)

    # 4. FACULTY -> ASSIGNMENT [creates] (1:M)
    r4 = draw_rel(880, 127, 45, 26, "Creates")
    d.line([720, 127, 835, 127], fill=BLACK, width=2)
    d.text((760, 110), "1", fill=BLACK)
    d.line([925, 127, 1040, 127], fill=BLACK, width=2)
    d.text((980, 110), "M", fill=BLACK)

    # 5. STUDENT -> ACADEMIC RECORD [scores] (1:M)
    r5 = draw_rel(160, 560, 45, 26, "Scores")
    d.line([160, 435, 160, 534], fill=BLACK, width=2)
    d.text((170, 480), "1", fill=BLACK)
    d.line([160, 586, 160, 710], fill=BLACK, width=2)
    d.text((170, 660), "M", fill=BLACK)

    # 6. COURSE -> ACADEMIC RECORD [has_record] (1:M)
    r6 = draw_rel(380, 560, 45, 26, "Evaluates")
    d.line([560, 420, 415, 540], fill=BLACK, width=2)
    d.text((495, 465), "1", fill=BLACK)
    d.line([345, 580, 240, 710], fill=BLACK, width=2)
    d.text((300, 645), "M", fill=BLACK)

    # 7. STUDENT -> ATTENDANCE [attends] (1:M)
    r7 = draw_rel(400, 470, 45, 26, "Attends")
    d.line([240, 415, 360, 460], fill=BLACK, width=2)
    d.text((290, 420), "1", fill=BLACK)
    d.line([440, 485, 570, 710], fill=BLACK, width=2)
    d.text((500, 600), "M", fill=BLACK)

    # 8. ASSIGNMENT -> SUBMISSION [receives] (1:M)
    r8 = draw_rel(1130, 260, 45, 26, "Receives")
    d.line([1130, 155, 1130, 234], fill=BLACK, width=2)
    d.text((1140, 185), "1", fill=BLACK)
    d.line([1130, 286, 1130, 380], fill=BLACK, width=2)
    d.text((1140, 340), "M", fill=BLACK)

    # 9. STUDENT -> SUBMISSION [submits] (1:M)
    r9 = draw_rel(880, 407, 45, 26, "Submits")
    d.line([240, 407, 835, 407], fill=BLACK, width=2)
    d.text((360, 390), "1", fill=BLACK)
    d.line([925, 407, 1040, 407], fill=BLACK, width=2)
    d.text((980, 390), "M", fill=BLACK)

    # 10. STUDENT -> RISK PREDICTION [generates] (1:M)
    r10 = draw_rel(880, 630, 45, 26, "Predicts")
    d.line([240, 425, 840, 620], fill=BLACK, width=2)
    d.text((450, 480), "1", fill=BLACK)
    d.line([920, 645, 1040, 720], fill=BLACK, width=2)
    d.text((980, 670), "M", fill=BLACK)

    img.save("docs/diagrams/fig3_2_erd.png")
    print("Saved formal fig3_2_erd.png")

# =========================================================================
# 3. Figure 3.3: Use Case Diagram (Clean UML Black & White)
# =========================================================================
def make_fig3_3():
    w, h = 1200, 800
    img = Image.new("RGB", (w, h), WHITE)
    d = ImageDraw.Draw(img)

    d.text((600, 25), "Figure 3.3: Use Case Diagram", fill=BLACK, anchor="mm")

    # System Boundary Box
    draw_rect(d, (300, 60, 950, 760), fill=WHITE, outline=BLACK, width=2)
    d.text((625, 85), "Academic Performance Analytics System", fill=BLACK, anchor="mm")

    # Actor stick figures in pure black lines
    def draw_actor(x, y, name):
        d.ellipse([x-20, y-45, x+20, y-5], outline=BLACK, fill=WHITE, width=2) # head
        d.line([x, y-5, x, y+45], fill=BLACK, width=2) # body
        d.line([x-30, y+15, x+30, y+15], fill=BLACK, width=2) # arms
        d.line([x, y+45, x-25, y+85], fill=BLACK, width=2) # left leg
        d.line([x, y+45, x+25, y+85], fill=BLACK, width=2) # right leg
        d.text((x, y+105), name, fill=BLACK, anchor="mm")

    draw_actor(140, 380, "HOD")
    draw_actor(1080, 240, "Faculty")
    draw_actor(1080, 560, "Student")

    # Use Cases (Ovals in 2 clean columns)
    use_cases = [
        (470, 150, "Secure Login"),
        (760, 150, "View Dashboard"),
        (470, 260, "View Subject\nPerformance"),
        (760, 260, "Generate Reports"),
        (470, 390, "Manage Marks /\nAttendance"),
        (760, 390, "Risk Prediction"),
        (470, 520, "Create Coding\nAssignment"),
        (760, 520, "Submit / Evaluate\nCode"),
        (615, 650, "View Coding\nLeaderboard")
    ]

    for cx, cy, label in use_cases:
        draw_oval(d, (cx - 105, cy - 35, cx + 105, cy + 35), fill=WHITE, outline=BLACK, width=2)
        d.text((cx, cy), label, fill=BLACK, anchor="mm")

    # Connect HOD lines
    d.line([165, 360, 365, 150], fill=BLACK, width=2) # Login
    d.line([165, 370, 655, 150], fill=BLACK, width=2) # View Dashboard
    d.line([165, 375, 365, 260], fill=BLACK, width=2) # Subject Perf
    d.line([165, 385, 655, 260], fill=BLACK, width=2) # Reports
    d.line([165, 395, 655, 390], fill=BLACK, width=2) # Risk Pred

    # Connect Faculty lines
    d.line([1050, 230, 575, 150], fill=BLACK, width=2) # Login
    d.line([1050, 240, 865, 150], fill=BLACK, width=2) # View Dashboard
    d.line([1050, 250, 575, 260], fill=BLACK, width=2) # Subject Perf
    d.line([1050, 260, 575, 390], fill=BLACK, width=2) # Manage Marks
    d.line([1050, 270, 575, 520], fill=BLACK, width=2) # Create Assignment

    # Connect Student lines
    d.line([1050, 550, 575, 150], fill=BLACK, width=2) # Login
    d.line([1050, 560, 865, 150], fill=BLACK, width=2) # View Dashboard
    d.line([1050, 570, 865, 390], fill=BLACK, width=2) # Risk Pred
    d.line([1050, 580, 865, 520], fill=BLACK, width=2) # Submit Code
    d.line([1050, 590, 720, 650], fill=BLACK, width=2) # Leaderboard

    img.save("docs/diagrams/fig3_3_usecase.png")
    print("Saved formal fig3_3_usecase.png")

# =========================================================================
# 4. Figure 3.4: Context Diagram (Strict Black & White)
# =========================================================================
def make_fig3_4():
    w, h = 1200, 650
    img = Image.new("RGB", (w, h), WHITE)
    d = ImageDraw.Draw(img)

    d.text((600, 30), "Figure 3.4: Context Diagram (Level - Context)", fill=BLACK, anchor="mm")

    # Central System Rounded Box
    draw_rounded_rect(d, (430, 240, 770, 410), radius=12, fill=WHITE, outline=BLACK, width=2)
    d.text((600, 305), "Academic Performance", fill=BLACK, anchor="mm")
    d.text((600, 340), "Analytics System", fill=BLACK, anchor="mm")

    # 4 External Entities (Pure black & white)
    draw_rounded_rect(d, (80, 100, 280, 190), radius=8, fill=WHITE, outline=BLACK, width=2)
    d.text((180, 145), "HOD", fill=BLACK, anchor="mm")

    draw_rounded_rect(d, (920, 100, 1120, 190), radius=8, fill=WHITE, outline=BLACK, width=2)
    d.text((1020, 145), "Student", fill=BLACK, anchor="mm")

    draw_rounded_rect(d, (80, 460, 280, 550), radius=8, fill=WHITE, outline=BLACK, width=2)
    d.text((180, 505), "Faculty", fill=BLACK, anchor="mm")

    draw_rounded_rect(d, (920, 460, 1120, 550), radius=8, fill=WHITE, outline=BLACK, width=2)
    d.text((1020, 505), "Judge0 API", fill=BLACK, anchor="mm")

    # Clean non-overlapping directional arrows
    draw_arrow(d, (280, 160), (440, 260), BLACK, 2)
    d.text((320, 195), "Report Requests", fill=BLACK)

    draw_arrow(d, (430, 290), (270, 190), BLACK, 2)
    d.text((290, 255), "Reports / Insights", fill=BLACK)

    draw_arrow(d, (920, 180), (760, 270), BLACK, 2)
    d.text((790, 205), "View Requests / Code", fill=BLACK)

    draw_arrow(d, (770, 250), (930, 160), BLACK, 2)
    d.text((815, 285), "Marks / Attendance / Risk", fill=BLACK)

    draw_arrow(d, (280, 490), (440, 390), BLACK, 2)
    d.text((260, 425), "Marks / Attendance / Assignments", fill=BLACK)

    draw_arrow(d, (430, 370), (270, 470), BLACK, 2)
    d.text((320, 480), "Confirmations / Results", fill=BLACK)

    draw_arrow(d, (760, 380), (920, 480), BLACK, 2)
    d.text((800, 415), "Code Execution Request", fill=BLACK)

    draw_arrow(d, (930, 510), (770, 410), BLACK, 2)
    d.text((810, 485), "Evaluation Result", fill=BLACK)

    img.save("docs/diagrams/fig3_4_context.png")
    print("Saved formal fig3_4_context.png")

# =========================================================================
# 5. Figure 3.5: Level 0 Data Flow Diagram (Strict Black & White)
# =========================================================================
def make_fig3_5():
    w, h = 1200, 750
    img = Image.new("RGB", (w, h), WHITE)
    d = ImageDraw.Draw(img)

    d.text((600, 30), "Figure 3.5: Level 0 Data Flow Diagram", fill=BLACK, anchor="mm")

    # External Entity: Users
    draw_rounded_rect(d, (60, 80, 220, 160), radius=8, fill=WHITE, outline=BLACK, width=2)
    d.text((140, 120), "Users", fill=BLACK, anchor="mm")

    # Process 1.0: Authentication
    draw_rounded_rect(d, (350, 80, 550, 160), radius=16, fill=WHITE, outline=BLACK, width=2)
    d.text((450, 110), "1.0", fill=BLACK, anchor="mm")
    d.text((450, 130), "Authentication", fill=BLACK, anchor="mm")

    # Data Store D1: User DB
    d.line([880, 80, 1100, 80], fill=BLACK, width=2)
    d.line([880, 160, 1100, 160], fill=BLACK, width=2)
    d.line([880, 80, 880, 160], fill=BLACK, width=2)
    d.text((990, 120), "D1 User DB", fill=BLACK, anchor="mm")

    draw_arrow(d, (220, 120), (350, 120), BLACK, 2)
    d.text((250, 100), "credentials", fill=BLACK)
    draw_arrow(d, (550, 120), (880, 120), BLACK, 2)
    d.text((680, 100), "user data", fill=BLACK)

    # Process 2.0: Academic Data
    draw_rounded_rect(d, (350, 220, 550, 300), radius=16, fill=WHITE, outline=BLACK, width=2)
    d.text((450, 250), "2.0", fill=BLACK, anchor="mm")
    d.text((450, 270), "Academic Data", fill=BLACK, anchor="mm")

    # Process 3.0: Attendance
    draw_rounded_rect(d, (350, 360, 550, 440), radius=16, fill=WHITE, outline=BLACK, width=2)
    d.text((450, 390), "3.0", fill=BLACK, anchor="mm")
    d.text((450, 410), "Attendance", fill=BLACK, anchor="mm")

    # Process 4.0: ML Analytics
    draw_rounded_rect(d, (680, 290, 880, 370), radius=16, fill=WHITE, outline=BLACK, width=2)
    d.text((780, 320), "4.0", fill=BLACK, anchor="mm")
    d.text((780, 340), "ML Analytics", fill=BLACK, anchor="mm")

    # Data Store D2: Academic DB
    d.line([950, 290, 1150, 290], fill=BLACK, width=2)
    d.line([950, 370, 1150, 370], fill=BLACK, width=2)
    d.line([950, 290, 950, 370], fill=BLACK, width=2)
    d.text((1050, 330), "D2 Academic DB", fill=BLACK, anchor="mm")

    draw_arrow(d, (450, 160), (450, 220), BLACK, 2)
    d.text((460, 185), "user id", fill=BLACK)

    draw_arrow(d, (550, 260), (680, 310), BLACK, 2)
    d.text((570, 270), "academic data", fill=BLACK)
    draw_arrow(d, (550, 400), (680, 350), BLACK, 2)
    d.text((565, 390), "attendance", fill=BLACK)
    draw_arrow(d, (880, 330), (950, 330), BLACK, 2)
    d.text((890, 310), "records", fill=BLACK)

    # Process 5.0: Coding Module
    draw_rounded_rect(d, (350, 500, 550, 580), radius=16, fill=WHITE, outline=BLACK, width=2)
    d.text((450, 530), "5.0", fill=BLACK, anchor="mm")
    d.text((450, 550), "Coding Module", fill=BLACK, anchor="mm")

    # Process 6.0: Code Evaluation
    draw_rounded_rect(d, (680, 500, 880, 580), radius=16, fill=WHITE, outline=BLACK, width=2)
    d.text((780, 530), "6.0", fill=BLACK, anchor="mm")
    d.text((780, 550), "Code Evaluation", fill=BLACK, anchor="mm")

    # Data Store D3: Results DB
    d.line([950, 500, 1150, 500], fill=BLACK, width=2)
    d.line([950, 580, 1150, 580], fill=BLACK, width=2)
    d.line([950, 500, 950, 580], fill=BLACK, width=2)
    d.text((1050, 540), "D3 Results DB", fill=BLACK, anchor="mm")

    draw_arrow(d, (780, 370), (480, 500), BLACK, 2)
    d.text((640, 440), "risk / insights", fill=BLACK)

    draw_arrow(d, (550, 540), (680, 540), BLACK, 2)
    d.text((590, 520), "code", fill=BLACK)
    draw_arrow(d, (880, 540), (950, 540), BLACK, 2)
    d.text((895, 520), "scores", fill=BLACK)

    img.save("docs/diagrams/fig3_5_dfd0.png")
    print("Saved formal fig3_5_dfd0.png")

# =========================================================================
# 6. Figure 3.6: Level 1 DFD (Strict Black & White)
# =========================================================================
def make_fig3_6():
    w, h = 1200, 700
    img = Image.new("RGB", (w, h), WHITE)
    d = ImageDraw.Draw(img)

    d.text((600, 30), "Figure 3.6: Level 1 DFD - Academic Analytics & Risk Prediction", fill=BLACK, anchor="mm")

    # Stores D1 & D2
    d.line([80, 120, 280, 120], fill=BLACK, width=2)
    d.line([80, 200, 280, 200], fill=BLACK, width=2)
    d.line([80, 120, 80, 200], fill=BLACK, width=2)
    d.text((180, 160), "D1 Academic\nRecords", fill=BLACK, anchor="mm")

    d.line([80, 280, 280, 280], fill=BLACK, width=2)
    d.line([80, 360, 280, 360], fill=BLACK, width=2)
    d.line([80, 280, 80, 360], fill=BLACK, width=2)
    d.text((180, 320), "D2 Attendance\nRecords", fill=BLACK, anchor="mm")

    # Process 3.1: Collect & Validate Data
    draw_rounded_rect(d, (380, 190, 580, 290), radius=16, fill=WHITE, outline=BLACK, width=2)
    d.text((480, 225), "3.1", fill=BLACK, anchor="mm")
    d.text((480, 255), "Collect & Validate\nData", fill=BLACK, anchor="mm")

    draw_arrow(d, (280, 160), (380, 220), BLACK, 2)
    d.text((295, 175), "marks", fill=BLACK)
    draw_arrow(d, (280, 320), (380, 260), BLACK, 2)
    d.text((285, 300), "attendance", fill=BLACK)

    # Process 3.2: Process Features
    draw_rounded_rect(d, (680, 190, 880, 290), radius=16, fill=WHITE, outline=BLACK, width=2)
    d.text((780, 225), "3.2", fill=BLACK, anchor="mm")
    d.text((780, 255), "Process Features\n(Pandas / NumPy)", fill=BLACK, anchor="mm")

    draw_arrow(d, (580, 240), (680, 240), BLACK, 2)
    d.text((600, 220), "validated data", fill=BLACK)

    # Process 3.3: ML Prediction
    draw_rounded_rect(d, (380, 430, 580, 530), radius=16, fill=WHITE, outline=BLACK, width=2)
    d.text((480, 465), "3.3", fill=BLACK, anchor="mm")
    d.text((480, 495), "ML Prediction\n(scikit-learn)", fill=BLACK, anchor="mm")

    draw_arrow(d, (730, 290), (530, 430), BLACK, 2)
    d.text((645, 370), "features", fill=BLACK)

    # Data Store D3: Risk Predictions
    d.line([680, 450, 880, 450], fill=BLACK, width=2)
    d.line([680, 530, 880, 530], fill=BLACK, width=2)
    d.line([680, 450, 680, 530], fill=BLACK, width=2)
    d.text((780, 490), "D3 Risk\nPredictions", fill=BLACK, anchor="mm")

    draw_arrow(d, (580, 480), (680, 480), BLACK, 2)
    d.text((605, 460), "risk class", fill=BLACK)

    # Dashboard sink
    draw_rounded_rect(d, (970, 280, 1150, 440), radius=12, fill=WHITE, outline=BLACK, width=2)
    d.text((1060, 360), "Dashboard", fill=BLACK, anchor="mm")

    draw_arrow(d, (880, 240), (970, 330), BLACK, 2)
    d.text((890, 275), "analytics", fill=BLACK)
    draw_arrow(d, (880, 480), (970, 390), BLACK, 2)
    d.text((890, 440), "risk results", fill=BLACK)

    img.save("docs/diagrams/fig3_6_dfd1.png")
    print("Saved formal fig3_6_dfd1.png")

# =========================================================================
# 7. Figure 3.7: Class Diagram (Strict UML 3-Box with Private - and Public +)
# =========================================================================
def make_fig3_7():
    w, h = 1200, 900
    img = Image.new("RGB", (w, h), WHITE)
    d = ImageDraw.Draw(img)

    d.text((600, 30), "Figure 3.7: Class Diagram", fill=BLACK, anchor="mm")

    # 3x3 layout of standard UML 3-compartment class boxes
    # Department standard: - for private attributes, + for public operations
    classes = {
        "User": (60, 70, 350, 240, [
            "- user_id: int",
            "- name: string",
            "- email: string",
            "- password_hash: string",
            "- role: string"
        ], [
            "+ verify_password(): bool",
            "+ generate_jwt_token(): string"
        ]),
        "Student": (440, 70, 750, 240, [
            "- student_id: int",
            "- faculty_no: string",
            "- enrollment_no: string",
            "- section: string"
        ], [
            "+ get_academic_records(): list",
            "+ get_risk_status(): dict",
            "+ submit_assignment(): bool"
        ]),
        "Faculty": (840, 70, 1140, 240, [
            "- faculty_id: int",
            "- user_id: int",
            "- name: string",
            "- department: string"
        ], [
            "+ update_student_marks(): void",
            "+ record_attendance(): void",
            "+ create_assignment(): int"
        ]),

        "Course": (60, 320, 350, 490, [
            "- course_id: int",
            "- course_code: string",
            "- course_name: string",
            "- semester: int",
            "- faculty_id: int"
        ], [
            "+ get_enrolled_students(): list",
            "+ calculate_subject_avg(): float"
        ]),
        "AcademicRecord": (440, 320, 750, 490, [
            "- record_id: int",
            "- student_id: int",
            "- course_id: int",
            "- semester: int",
            "- marks: float"
        ], [
            "+ set_marks(val: float): void",
            "+ get_pass_fail_status(): string"
        ]),
        "Attendance": (840, 320, 1140, 490, [
            "- attendance_id: int",
            "- student_id: int",
            "- semester: int",
            "- percentage: float"
        ], [
            "+ update_attendance(pct): void",
            "+ is_eligible_75_rule(): bool"
        ]),

        "Assignment": (60, 570, 350, 740, [
            "- assignment_id: int",
            "- faculty_id: int",
            "- course_id: int",
            "- title: string",
            "- test_cases: json"
        ], [
            "+ add_test_case(): void",
            "+ get_submissions(): list"
        ]),
        "Submission": (440, 570, 750, 740, [
            "- submission_id: int",
            "- assignment_id: int",
            "- student_id: int",
            "- code: text",
            "- score: float",
            "- status: string"
        ], [
            "+ evaluate_test_cases(): dict",
            "+ calculate_score(): float"
        ]),
        "RiskPrediction": (840, 570, 1140, 740, [
            "- prediction_id: int",
            "- student_id: int",
            "- risk_level: string",
            "- prediction_date: date",
            "- model_result: json"
        ], [
            "+ predict_risk(): string",
            "+ get_actionable_advice(): list"
        ])
    }

    for name, (x1, y1, x2, y2, attrs, methods) in classes.items():
        # Outer box
        draw_rect(d, (x1, y1, x2, y2), fill=WHITE, outline=BLACK, width=2)
        # Compartment 1: Class Name
        d.text(((x1 + x2)//2, y1 + 16), name, fill=BLACK, anchor="mm")
        d.line([x1, y1 + 32, x2, y1 + 32], fill=BLACK, width=1)

        # Compartment 2: Attributes
        ay = y1 + 44
        for att in attrs:
            d.text((x1 + 8, ay), att, fill=BLACK)
            ay += 18

        # Line between attributes and methods
        div_y = y1 + 32 + max(len(attrs) * 18 + 14, 90)
        d.line([x1, div_y, x2, div_y], fill=BLACK, width=1)

        # Compartment 3: Methods
        my = div_y + 10
        for met in methods:
            d.text((x1 + 8, my), met, fill=BLACK)
            my += 18

    # UML Association Lines
    # User - Student & Faculty (Inheritance/Generalization or Association)
    d.line([350, 150, 440, 150], fill=BLACK, width=2)
    d.line([750, 150, 840, 150], fill=BLACK, width=2)

    # Student - AcademicRecord
    d.line([595, 240, 595, 320], fill=BLACK, width=2)

    # Course - AcademicRecord
    d.line([350, 400, 440, 400], fill=BLACK, width=2)

    # Student - Attendance
    d.line([750, 200, 840, 360], fill=BLACK, width=2)

    # Faculty - Course
    d.line([840, 220, 350, 340], fill=BLACK, width=1)

    # Assignment - Submission
    d.line([350, 650, 440, 650], fill=BLACK, width=2)

    # Student - Submission
    d.line([595, 490, 595, 570], fill=BLACK, width=2)

    # Student - RiskPrediction
    d.line([750, 220, 840, 620], fill=BLACK, width=2)

    # Attendance - RiskPrediction
    d.line([990, 490, 990, 570], fill=BLACK, width=2)

    img.save("docs/diagrams/fig3_7_class.png")
    print("Saved formal fig3_7_class.png")

# =========================================================================
# 8. Figure 3.8: Sequence Diagram (Strict Black & White)
# =========================================================================
def make_fig3_8():
    w, h = 1200, 750
    img = Image.new("RGB", (w, h), WHITE)
    d = ImageDraw.Draw(img)

    d.text((600, 30), "Figure 3.8: Sequence Diagram - Coding Assignment Evaluation", fill=BLACK, anchor="mm")

    actors = [
        ("Faculty", 100),
        ("Student", 300),
        ("Streamlit", 520),
        ("FastAPI", 740),
        ("Judge0 API", 940),
        ("Database", 1100)
    ]

    for name, x in actors:
        draw_rect(d, (x - 60, 65, x + 60, 105), fill=WHITE, outline=BLACK, width=2)
        d.text((x, 85), name, fill=BLACK, anchor="mm")
        # Lifeline (dashed)
        draw_arrow(d, (x, 105), (x, 710), BLACK, 1, arrow_size=0, dashed=True)

    # Sequence Messages
    steps = [
        (100, 520, 140, "Create assignment", False),
        (300, 520, 200, "Submit code", False),
        (520, 740, 260, "POST submission", False),
        (740, 940, 320, "Execute code", False),
        (940, 740, 380, "Result / score", True),
        (740, 1100, 440, "Store result", False),
        (1100, 740, 500, "Saved", True),
        (740, 520, 550, "Return result", True),
        (520, 300, 600, "Display score", True),
        (520, 300, 650, "Update leaderboard", True)
    ]

    for x1, x2, y, msg, is_return in steps:
        draw_arrow(d, (x1, y), (x2, y), BLACK, 2, arrow_size=8, dashed=is_return)
        mid_x = (x1 + x2) // 2
        d.text((mid_x, y - 12), msg, fill=BLACK, anchor="mm")

    img.save("docs/diagrams/fig3_8_sequence.png")
    print("Saved formal fig3_8_sequence.png")

# =========================================================================
# 9. Figure 4.1: Dashboard Interface Mockup (Clean Monochrome Wireframe)
# =========================================================================
def make_fig4_1():
    w, h = 1200, 750
    img = Image.new("RGB", (w, h), WHITE)
    d = ImageDraw.Draw(img)

    # Big outer frame
    draw_rect(d, (40, 30, 1160, 710), fill=WHITE, outline=BLACK, width=3)

    # Title
    d.text((600, 65), "ACADEMIC PERFORMANCE DASHBOARD", fill=BLACK, anchor="mm")

    # 4 KPI Boxes
    kpis = [
        ("Total Students", "60"),
        ("Average Marks", "74%"),
        ("Attendance", "82%"),
        ("High Risk", "8")
    ]
    for i, (t, v) in enumerate(kpis):
        x1 = 70 + i * 270
        x2 = x1 + 240
        draw_rect(d, (x1, 105, x2, 195), fill=WHITE, outline=BLACK, width=2)
        d.text(((x1 + x2)//2, 135), t, fill=BLACK, anchor="mm")
        d.text(((x1 + x2)//2, 168), v, fill=BLACK, anchor="mm")

    # Left: Subject-wise Average Performance
    draw_rect(d, (70, 225, 590, 510), fill=WHITE, outline=BLACK, width=2)
    d.text((330, 255), "Subject-wise Average Performance", fill=BLACK, anchor="mm")

    subjects = [("Python", 60), ("DBMS", 85), ("CN", 50), ("OS", 70), ("AI", 90)]
    for i, (sub, val) in enumerate(subjects):
        bx = 105 + i * 95
        bh = int(val * 1.8)
        by = 460 - bh
        draw_rect(d, (bx, by, bx + 55, 460), fill=WHITE, outline=BLACK, width=2)
        d.text((bx + 27, 480), sub, fill=BLACK, anchor="mm")

    # Right: Academic Risk Distribution
    draw_rect(d, (620, 225, 1130, 510), fill=WHITE, outline=BLACK, width=2)
    d.text((875, 255), "Academic Risk Distribution", fill=BLACK, anchor="mm")

    risk_bars = [("Low", 90), ("Medium", 55), ("High", 20)]
    for i, (lvl, val) in enumerate(risk_bars):
        bx = 680 + i * 150
        bh = int(val * 1.8)
        by = 460 - bh
        draw_rect(d, (bx, by, bx + 85, 460), fill=WHITE, outline=BLACK, width=2)
        d.text((bx + 42, 480), lvl, fill=BLACK, anchor="mm")

    # Bottom: Coding Assignment Leaderboard
    draw_rect(d, (70, 540, 1130, 680), fill=WHITE, outline=BLACK, width=2)
    d.text((600, 570), "Coding Assignment Leaderboard", fill=BLACK, anchor="mm")

    lb_entries = [
        "1. Student A  95",
        "2. Student B  91",
        "3. Student C  88",
        "4. Student D  85"
    ]
    for i, item in enumerate(lb_entries):
        lx = 130 + i * 260
        d.text((lx, 630), item, fill=BLACK)

    img.save("docs/diagrams/fig4_1_mockup.png")
    print("Saved formal fig4_1_mockup.png")

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
