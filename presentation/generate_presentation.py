import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

def create_deck():
    prs = Presentation()
    # 16:9 Widescreen standard
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # AMU Palette
    DARK_GREEN = RGBColor(7, 59, 34)      # #073B22
    AMU_GREEN  = RGBColor(11, 94, 54)     # #0B5E36
    LIGHT_GREEN= RGBColor(232, 245, 233)  # #E8F5E9
    GOLD       = RGBColor(197, 155, 39)   # #C59B27
    DARK_TEXT  = RGBColor(33, 37, 41)     # #212529
    MUTED_TEXT = RGBColor(108, 117, 125)  # #6C757D
    WHITE      = RGBColor(255, 255, 255)
    CARD_BG    = RGBColor(255, 255, 255)
    BORDER_COL = RGBColor(220, 224, 222)
    BG_LIGHT   = RGBColor(246, 248, 247)  # #F6F8F7
    RED_ACCENT = RGBColor(220, 53, 69)

    logo_path = os.path.abspath("presentation/assets/amu_logo_circle.png")
    shot_hod  = os.path.abspath("presentation/assets/shot_hod_dashboard.png")
    shot_stu  = os.path.abspath("presentation/assets/shot_student_judge.png")
    shot_ren  = os.path.abspath("presentation/assets/shot_live_render.png")

    def add_footer(slide):
        # Left footer
        left_box = slide.shapes.add_textbox(Inches(0.8), Inches(7.05), Inches(5.0), Inches(0.35))
        tf_l = left_box.text_frame
        tf_l.word_wrap = True
        p_l = tf_l.paragraphs[0]
        p_l.text = "FAIZAN AHMAD"
        p_l.font.size = Pt(10)
        p_l.font.bold = True
        p_l.font.color.rgb = AMU_GREEN
        p_l.alignment = PP_ALIGN.LEFT

        # Center subtle note
        cnt_box = slide.shapes.add_textbox(Inches(4.5), Inches(7.05), Inches(4.333), Inches(0.35))
        tf_c = cnt_box.text_frame
        p_c = tf_c.paragraphs[0]
        p_c.text = "Department of Computer Science • AMU • MCA Sem III"
        p_c.font.size = Pt(9)
        p_c.font.color.rgb = MUTED_TEXT
        p_c.alignment = PP_ALIGN.CENTER

        # Right footer
        right_box = slide.shapes.add_textbox(Inches(7.533), Inches(7.05), Inches(5.0), Inches(0.35))
        tf_r = right_box.text_frame
        tf_r.word_wrap = True
        p_r = tf_r.paragraphs[0]
        p_r.text = "25CAMSA112"
        p_r.font.size = Pt(10)
        p_r.font.bold = True
        p_r.font.color.rgb = AMU_GREEN
        p_r.alignment = PP_ALIGN.RIGHT

    def create_base_slide(title_text, subtitle_text):
        slide = prs.slides.add_slide(blank_layout)
        # Background
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = BG_LIGHT
        bg.line.fill.background()

        # Top banner
        top_bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(1.15))
        top_bar.fill.solid()
        top_bar.fill.fore_color.rgb = AMU_GREEN
        top_bar.line.fill.background()

        # Gold stripe
        stripe = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, Inches(1.15), Inches(13.333), Inches(0.06))
        stripe.fill.solid()
        stripe.fill.fore_color.rgb = GOLD
        stripe.line.fill.background()

        # Small AMU Logo on top right
        if os.path.exists(logo_path):
            slide.shapes.add_picture(logo_path, Inches(12.2), Inches(0.12), width=Inches(0.92))

        # Title text
        tb = slide.shapes.add_textbox(Inches(0.8), Inches(0.15), Inches(11.2), Inches(0.55))
        p = tb.text_frame.paragraphs[0]
        p.text = title_text
        p.font.size = Pt(22)
        p.font.bold = True
        p.font.color.rgb = WHITE

        # Subtitle text
        sb = slide.shapes.add_textbox(Inches(0.8), Inches(0.68), Inches(11.2), Inches(0.40))
        sp = sb.text_frame.paragraphs[0]
        sp.text = subtitle_text
        sp.font.size = Pt(11)
        sp.font.color.rgb = RGBColor(210, 240, 225)

        add_footer(slide)
        return slide

    # =========================================================================
    # SLIDE 1: TITLE SLIDE
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    bg1 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg1.fill.solid()
    bg1.fill.fore_color.rgb = DARK_GREEN
    bg1.line.fill.background()

    # Inner decorative border
    in_rect = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.4), Inches(0.4), Inches(12.533), Inches(6.7))
    in_rect.fill.background()
    in_rect.line.color.rgb = GOLD
    in_rect.line.width = Pt(1.5)

    # Logo in circle format
    if os.path.exists(logo_path):
        s1.shapes.add_picture(logo_path, Inches(5.95), Inches(0.7), width=Inches(1.45))

    # Header / Topic
    t_box = s1.shapes.add_textbox(Inches(0.8), Inches(2.25), Inches(11.733), Inches(1.3))
    tf1 = t_box.text_frame
    tf1.word_wrap = True
    
    p0 = tf1.paragraphs[0]
    p0.text = "Presentation for a project :"
    p0.font.size = Pt(14)
    p0.font.bold = True
    p0.font.color.rgb = GOLD
    p0.alignment = PP_ALIGN.CENTER

    p1 = tf1.add_paragraph()
    p1.text = "Academic Performance Analytics System"
    p1.font.size = Pt(28)
    p1.font.bold = True
    p1.font.color.rgb = WHITE
    p1.alignment = PP_ALIGN.CENTER

    p_sub = tf1.add_paragraph()
    p_sub.text = "CAMS-3P01: MINI PROJECT | MCA SEMESTER – III (SESSION: 2026–27)"
    p_sub.font.size = Pt(11)
    p_sub.font.color.rgb = RGBColor(190, 230, 210)
    p_sub.alignment = PP_ALIGN.CENTER

    # Left Column: Student Credentials
    left_c = s1.shapes.add_textbox(Inches(1.5), Inches(3.7), Inches(4.5), Inches(2.5))
    tl = left_c.text_frame
    tl.word_wrap = True
    
    pl0 = tl.paragraphs[0]
    pl0.text = "Submitted By:"
    pl0.font.size = Pt(13)
    pl0.font.bold = True
    pl0.font.color.rgb = GOLD

    items_student = [
        ("Name:", "FAIZAN AHMAD"),
        ("Faculty No:", "25CAMSA112"),
        ("Enrollment No:", "GR0622"),
        ("Course:", "MCA"),
        ("Semester:", "3rd")
    ]
    for lbl, val in items_student:
        pi = tl.add_paragraph()
        pi.text = f"{lbl}  {val}"
        pi.font.size = Pt(11.5)
        pi.font.color.rgb = WHITE

    # Right Column: Supervisory Committee
    right_c = s1.shapes.add_textbox(Inches(7.2), Inches(3.7), Inches(5.0), Inches(2.6))
    tr = right_c.text_frame
    tr.word_wrap = True

    pr0 = tr.paragraphs[0]
    pr0.text = "Under Supervision of:"
    pr0.font.size = Pt(13)
    pr0.font.bold = True
    pr0.font.color.rgb = GOLD

    supervisors = [
        "Prof. AASIM ZAFAR",
        "DR. FARAZ MASOOD",
        "MR. MOHD ADNAN",
        "MR. KAUSHAR ALI",
        "MR. SAAD SHAMIM",
        "MR. AHSAN SHAMEEM"
    ]
    for sup in supervisors:
        pi = tr.add_paragraph()
        pi.text = f"•  {sup}"
        pi.font.size = Pt(11)
        pi.font.color.rgb = WHITE

    # Bottom Dept Header
    b_box = s1.shapes.add_textbox(Inches(0.8), Inches(6.45), Inches(11.733), Inches(0.55))
    tb_f = b_box.text_frame
    pb = tb_f.paragraphs[0]
    pb.text = "DEPARTMENT OF COMPUTER SCIENCE\nALIGARH MUSLIM UNIVERSITY, ALIGARH"
    pb.font.size = Pt(11)
    pb.font.bold = True
    pb.font.color.rgb = GOLD
    pb.alignment = PP_ALIGN.CENTER


    # =========================================================================
    # SLIDE 2: BACKGROUND & PROBLEM STATEMENT
    # =========================================================================
    s2 = create_base_slide(
        "1. Background & Problem Statement",
        "Current academic record maintenance challenges identified in the Department of Computer Science"
    )
    problems = [
        ("Fragmented Academic Records", "Marks, semester grades, and attendance are maintained in disparate paper registers, local spreadsheets, and detached Google Forms without centralized storage."),
        ("Absence of Early-Warning Risk Analytics", "Academic difficulties and potential course failures are discovered post-examinations, leaving no window for proactive remedial tutorials or counseling."),
        ("Manual Attendance Tracking", "Manual registers delay the identification of students falling below the mandatory 75% AMU examination eligibility threshold."),
        ("Manual Programming Evaluation", "Coding assignments are graded manually without standardized test cases, continuous execution benchmarks, or motivating competitive leaderboards."),
        ("Lack of Executive Insights for HOD & Faculty", "Department leadership lacks consolidated, near real-time dashboards to analyze subject-wise pass rates, teacher performance, and at-risk cohorts.")
    ]
    for i, (title, desc) in enumerate(problems):
        y = 1.5 + i * 1.05
        # Card box
        card = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(y), Inches(11.733), Inches(0.92))
        card.fill.solid()
        card.fill.fore_color.rgb = WHITE
        card.line.color.rgb = BORDER_COL
        # Left tag
        tag = s2.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(y), Inches(0.12), Inches(0.92))
        tag.fill.solid()
        tag.fill.fore_color.rgb = RED_ACCENT
        tag.line.fill.background()

        tb = s2.shapes.add_textbox(Inches(1.1), Inches(y + 0.08), Inches(11.2), Inches(0.8))
        tf = tb.text_frame
        p_t = tf.paragraphs[0]
        p_t.text = f"• {title}"
        p_t.font.size = Pt(13)
        p_t.font.bold = True
        p_t.font.color.rgb = DARK_TEXT

        p_d = tf.add_paragraph()
        p_d.text = desc
        p_d.font.size = Pt(11)
        p_d.font.color.rgb = MUTED_TEXT


    # =========================================================================
    # SLIDE 3: PROPOSED SOLUTION
    # =========================================================================
    s3 = create_base_slide(
        "2. Proposed Solution: Academic Performance Analytics System",
        "A centralized, multi-role web platform integrating data analytics, ML risk forecasting, and automated code evaluation"
    )
    solutions = [
        ("Centralized Data Ingestion & Relational Storage", "Unified SQLite database tracking students, courses, semester marks, and attendance records with strict foreign-key integrity constraints."),
        ("Role-Based Dynamic Dashboards", "Tailored interfaces for Head of Department (executive analytics), Course Faculty (data entry & assignment management), and Students (self-monitoring)."),
        ("Automated Machine Learning Risk Engine", "Supervised scikit-learn classifier evaluating grade trajectories, attendance deficits, and subject failures to categorize academic risk into Low, Medium, and High."),
        ("Integrated Online Coding Judge (Judge0 Architecture)", "In-browser programming workspace that compiles, runs, and evaluates student code against predefined test cases with automated scoring."),
        ("Departmental Live Leaderboard", "Live gamification ranking student programming performance across problem difficulty and automated testcase completion."),
        ("Near Real-Time Synchronization (< 15 Seconds)", "Dynamic updates reflecting newly recorded marks or code submissions across all dashboards without manual page reloading.")
    ]
    for i, (title, desc) in enumerate(solutions):
        row = i // 2
        col = i % 2
        x = 0.8 + col * 5.95
        y = 1.45 + row * 1.75

        card = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(5.75), Inches(1.58))
        card.fill.solid()
        card.fill.fore_color.rgb = WHITE
        card.line.color.rgb = BORDER_COL

        tag = s3.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(0.12), Inches(1.58))
        tag.fill.solid()
        tag.fill.fore_color.rgb = AMU_GREEN
        tag.line.fill.background()

        tb = s3.shapes.add_textbox(Inches(x + 0.25), Inches(y + 0.12), Inches(5.35), Inches(1.35))
        tf = tb.text_frame
        tf.word_wrap = True
        p_t = tf.paragraphs[0]
        p_t.text = f"{i+1}. {title}"
        p_t.font.size = Pt(12.5)
        p_t.font.bold = True
        p_t.font.color.rgb = AMU_GREEN

        p_d = tf.add_paragraph()
        p_d.text = desc
        p_d.font.size = Pt(10.5)
        p_d.font.color.rgb = DARK_TEXT


    # =========================================================================
    # SLIDE 4: TECHNOLOGY STACK & JUSTIFICATION
    # =========================================================================
    s4 = create_base_slide(
        "3. Technology Stack & Architectural Justification",
        "Aligned strictly with Section 2.4 & 4.1 of the Software Requirements Specification (SRS)"
    )
    tech_data = [
        ("Presentation Layer", "Streamlit (Python)", "Enables rapid, interactive, data-driven visualization with Plotly charts, customizable sidebars, and real-time state caching."),
        ("Application Backend", "FastAPI (Python)", "Modern, asynchronous high-performance REST API with automated Swagger OpenAPI documentation and pydantic schema validation."),
        ("Database Layer", "SQLite (SQLAlchemy ORM)", "Relational database maintaining normalized entities, foreign keys, and referential constraints with zero setup overhead; easily scalable to PostgreSQL."),
        ("Security & Auth", "JWT + bcrypt", "Industry-standard cryptographic password hashing and stateless JSON Web Tokens implementing strict Role-Based Access Control (RBAC)."),
        ("Machine Learning", "scikit-learn, Pandas, NumPy", "Provides standard scalers, ensemble random forest classifiers, and tabular data wrangling for risk modeling."),
        ("Online Code Judge", "Judge0 API + Local Sandbox", "Executes programming assignments inside isolated containers with standard I/O validation, timeout protection, and scoring."),
        ("Cloud Deployment", "Render.com & Git", "Continuous deployment from GitHub main branch with live HTTPS SSL endpoint and automated database initialization.")
    ]
    # Add Table
    table_shape = s4.shapes.add_table(8, 3, Inches(0.8), Inches(1.45), Inches(11.733), Inches(5.2))
    table = table_shape.table
    table.columns[0].width = Inches(2.2)
    table.columns[1].width = Inches(3.0)
    table.columns[2].width = Inches(6.533)

    headers = ["Layer", "Technology Selected", "Architectural Justification"]
    for c_idx, h in enumerate(headers):
        cell = table.cell(0, c_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = AMU_GREEN
        p = cell.text_frame.paragraphs[0]
        p.text = h
        p.font.size = Pt(11.5)
        p.font.bold = True
        p.font.color.rgb = WHITE

    for r_idx, (layer, tech, just) in enumerate(tech_data, start=1):
        c0 = table.cell(r_idx, 0)
        c0.fill.solid()
        c0.fill.fore_color.rgb = LIGHT_GREEN if r_idx % 2 == 1 else WHITE
        p0 = c0.text_frame.paragraphs[0]
        p0.text = layer
        p0.font.size = Pt(10)
        p0.font.bold = True
        p0.font.color.rgb = DARK_TEXT

        c1 = table.cell(r_idx, 1)
        c1.fill.solid()
        c1.fill.fore_color.rgb = LIGHT_GREEN if r_idx % 2 == 1 else WHITE
        p1 = c1.text_frame.paragraphs[0]
        p1.text = tech
        p1.font.size = Pt(10)
        p1.font.bold = True
        p1.font.color.rgb = AMU_GREEN

        c2 = table.cell(r_idx, 2)
        c2.fill.solid()
        c2.fill.fore_color.rgb = LIGHT_GREEN if r_idx % 2 == 1 else WHITE
        p2 = c2.text_frame.paragraphs[0]
        p2.text = just
        p2.font.size = Pt(9.5)
        p2.font.color.rgb = DARK_TEXT


    # =========================================================================
    # SLIDE 5: SYSTEM ARCHITECTURE & DATA FLOW
    # =========================================================================
    s5 = create_base_slide(
        "4. System Architecture & Relational Design",
        "Layered software architecture and Level-1 Academic Analytics Data Flow Diagram (DFD)"
    )
    # Left: Architecture Layers
    arch_card = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.45), Inches(5.6), Inches(5.3))
    arch_card.fill.solid()
    arch_card.fill.fore_color.rgb = WHITE
    arch_card.line.color.rgb = BORDER_COL

    tb_a = s5.shapes.add_textbox(Inches(1.0), Inches(1.55), Inches(5.2), Inches(5.0))
    tf_a = tb_a.text_frame
    tf_a.word_wrap = True
    p = tf_a.paragraphs[0]
    p.text = "Multi-Tier Layered Architecture"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = AMU_GREEN

    arch_layers = [
        ("1. Presentation Layer (Streamlit)", "Provides interactive role-based views (HOD, Faculty, Student) with responsive Plotly charts and session state management."),
        ("2. Application API Layer (FastAPI)", "Processes HTTP REST endpoints, validates schemas via Pydantic, and enforces JWT Role-Based Access Control."),
        ("3. Analytics & Evaluation Engine", "scikit-learn Random Forest model computes risk probabilities; Judge0 service coordinates automated code evaluation."),
        ("4. Relational Database Layer (SQLite)", "Maintains 9 normalized entities: Users, Students, Faculty, Courses, AcademicRecords, Attendance, Assignments, Submissions, RiskPredictions.")
    ]
    for t, d in arch_layers:
        p_t = tf_a.add_paragraph()
        p_t.text = f"\n{t}"
        p_t.font.size = Pt(11)
        p_t.font.bold = True
        p_t.font.color.rgb = DARK_TEXT

        p_d = tf_a.add_paragraph()
        p_d.text = d
        p_d.font.size = Pt(10)
        p_d.font.color.rgb = MUTED_TEXT

    # Right: Relational Database Entities & Key Relationships
    db_card = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.45), Inches(5.733), Inches(5.3))
    db_card.fill.solid()
    db_card.fill.fore_color.rgb = WHITE
    db_card.line.color.rgb = BORDER_COL

    tb_d = s5.shapes.add_textbox(Inches(7.0), Inches(1.55), Inches(5.333), Inches(5.0))
    tf_d = tb_d.text_frame
    tf_d.word_wrap = True
    p = tf_d.paragraphs[0]
    p.text = "Normalized Relational Data Entities (SRS 2.3)"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = AMU_GREEN

    entities = [
        ("User", "User_ID, Name, Email, Password_Hash, Role (HOD, Faculty, Student)"),
        ("Student", "Student_ID, User_ID, Name, Faculty_No, Enrollment_No, Section"),
        ("Faculty", "Faculty_ID, User_ID, Name, Email, Department"),
        ("Course", "Course_ID, Course_Code, Course_Name, Semester (1/2), Faculty_ID"),
        ("AcademicRecord", "Record_ID, Student_ID, Course_ID, Semester, Marks (out of 100)"),
        ("Attendance", "Attendance_ID, Student_ID, Semester, Attendance_Percentage"),
        ("Assignment", "Assignment_ID, Course_ID, Title, Problem, Test_Cases (JSON)"),
        ("Submission", "Submission_ID, Assignment_ID, Student_ID, Code, Score, Status"),
        ("RiskPrediction", "Prediction_ID, Student_ID, Risk_Level, Probabilities, Recommendations")
    ]
    for ent, attrs in entities:
        pe = tf_d.add_paragraph()
        pe.text = f"• {ent}: {attrs}"
        pe.font.size = Pt(9.5)
        pe.font.color.rgb = DARK_TEXT


    # =========================================================================
    # SLIDE 6: DATASET & ACADEMIC INGESTION PIPELINE
    # =========================================================================
    s6 = create_base_slide(
        "5. Student Dataset & Academic Data Ingestion",
        "Processing structured Google Form academic dataset collected from MCA students"
    )
    left_ds = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.45), Inches(5.7), Inches(5.3))
    left_ds.fill.solid()
    left_ds.fill.fore_color.rgb = WHITE
    left_ds.line.color.rgb = BORDER_COL

    tb_ds = s6.shapes.add_textbox(Inches(1.0), Inches(1.55), Inches(5.3), Inches(5.0))
    tf_ds = tb_ds.text_frame
    tf_ds.word_wrap = True
    p = tf_ds.paragraphs[0]
    p.text = "Dataset Characteristics (students_data.csv)"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = AMU_GREEN

    ds_bullets = [
        ("Cohort Size", "60 MCA students enrolled in Semester 1 & Semester 2."),
        ("Collection Method", "Structured Google Form with student verification."),
        ("Total Academic Records", "720 individual course marks (12 subjects × 60 students)."),
        ("Attendance Records", "120 semester attendance entries (Sem 1 & Sem 2)."),
        ("Data Cleaning Pipeline", "String stripping, whitespace sanitization, null value imputations, email parsing, enrollment ID normalization (e.g. GR0622, 25CAMSA111)."),
        ("Database Ingestion Script", "Automated ingestion via `seed_data.py` inserting relational records and generating default credentials.")
    ]
    for t, d in ds_bullets:
        pt = tf_ds.add_paragraph()
        pt.text = f"\n• {t}:"
        pt.font.size = Pt(11)
        pt.font.bold = True
        pt.font.color.rgb = DARK_TEXT

        pd = tf_ds.add_paragraph()
        pd.text = d
        pd.font.size = Pt(10)
        pd.font.color.rgb = MUTED_TEXT

    # Right: Course Breakdown by Semester
    right_ds = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.9), Inches(1.45), Inches(5.633), Inches(5.3))
    right_ds.fill.solid()
    right_ds.fill.fore_color.rgb = WHITE
    right_ds.line.color.rgb = BORDER_COL

    tb_c = s6.shapes.add_textbox(Inches(7.1), Inches(1.55), Inches(5.233), Inches(5.0))
    tf_c = tb_c.text_frame
    tf_c.word_wrap = True
    p = tf_c.paragraphs[0]
    p.text = "Academic Curriculum Mapped"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = AMU_GREEN

    p1 = tf_c.add_paragraph()
    p1.text = "\nSemester 1 Courses (CS101 – CS106):"
    p1.font.size = Pt(11.5)
    p1.font.bold = True
    p1.font.color.rgb = AMU_GREEN

    s1_courses = [
        "CS101: Data Structures using C++",
        "CS102: Database Management Systems (DBMS)",
        "CS103: Digital Electronics",
        "CS104: Analysis & Design of Information Systems",
        "CS105: Soft Skills Development",
        "CS106: Computer Laboratory - I"
    ]
    for c in s1_courses:
        pi = tf_c.add_paragraph()
        pi.text = f"  - {c}"
        pi.font.size = Pt(9.5)
        pi.font.color.rgb = DARK_TEXT

    p2 = tf_c.add_paragraph()
    p2.text = "\nSemester 2 Courses (CS201 – CS206):"
    p2.font.size = Pt(11.5)
    p2.font.bold = True
    p2.font.color.rgb = AMU_GREEN

    s2_courses = [
        "CS201: Object-Oriented Programming using JAVA",
        "CS202: Web Development",
        "CS203: Computer Networks",
        "CS204: Computer Laboratory - II",
        "CS205: E-Commerce",
        "CS206: Open Elective"
    ]
    for c in s2_courses:
        pi = tf_c.add_paragraph()
        pi.text = f"  - {c}"
        pi.font.size = Pt(9.5)
        pi.font.color.rgb = DARK_TEXT


    # =========================================================================
    # SLIDE 7: MACHINE LEARNING ACADEMIC RISK ENGINE
    # =========================================================================
    s7 = create_base_slide(
        "6. Machine Learning Academic Risk Prediction Engine",
        "Early warning classification using scikit-learn Random Forest model (FR-005)"
    )
    # 3 Cards for Risk Categories
    cats = [
        ("LOW RISK (63.3%)", "38 Students", "#28A745", "#D4EDDA", [
            "Consistent marks (Overall Average ≥ 65%)",
            "Safe attendance (≥ 75% AMU Rule)",
            "0 failed or backlog subjects",
            "Action: Eligible for advanced coding electives & peer mentoring"
        ]),
        ("MEDIUM RISK (23.3%)", "14 Students", "#FFC107", "#FFF3CD", [
            "Moderate marks (Overall Average 50% – 65%)",
            "Borderline attendance (70% – 75%)",
            "Single subject backlogs or downward trend",
            "Action: Academic monitoring & practical tutorial reinforcement"
        ]),
        ("HIGH RISK (13.4%)", "8 Students", "#DC3545", "#F8D7DA", [
            "Low overall average (< 50%) or severe grade decline",
            "Critical attendance shortage (< 70% attendance)",
            "Multiple failing marks (< 40% pass criteria)",
            "Action: Immediate faculty mentoring & parental notification"
        ])
    ]
    for i, (title, count, border_col, bg_col, points) in enumerate(cats):
        x = 0.8 + i * 3.95
        card = s7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(1.45), Inches(3.8), Inches(3.6))
        card.fill.solid()
        card.fill.fore_color.rgb = RGBColor.from_string(bg_col.replace('#', ''))
        card.line.color.rgb = RGBColor.from_string(border_col.replace('#', ''))
        card.line.width = Pt(1.5)

        tb = s7.shapes.add_textbox(Inches(x + 0.15), Inches(1.55), Inches(3.5), Inches(3.4))
        tf = tb.text_frame
        tf.word_wrap = True
        pt = tf.paragraphs[0]
        pt.text = title
        pt.font.size = Pt(12)
        pt.font.bold = True
        pt.font.color.rgb = RGBColor.from_string(border_col.replace('#', ''))

        pc = tf.add_paragraph()
        pc.text = f"Current Cohort: {count}"
        pc.font.size = Pt(10)
        pc.font.bold = True
        pc.font.color.rgb = DARK_TEXT

        for pt_str in points:
            pp = tf.add_paragraph()
            pp.text = f"• {pt_str}"
            pp.font.size = Pt(9.5)
            pp.font.color.rgb = DARK_TEXT

    # Bottom Model Feature Box
    feat_card = s7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(5.2), Inches(11.733), Inches(1.6))
    feat_card.fill.solid()
    feat_card.fill.fore_color.rgb = WHITE
    feat_card.line.color.rgb = BORDER_COL

    tb_f = s7.shapes.add_textbox(Inches(1.0), Inches(5.3), Inches(11.333), Inches(1.4))
    tf_f = tb_f.text_frame
    tf_f.word_wrap = True
    p = tf_f.paragraphs[0]
    p.text = "Model Specifications & Feature Vector"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = AMU_GREEN

    p_f = tf_f.add_paragraph()
    p_f.text = "• Algorithm: Random Forest Classifier (100 estimators, max depth 6) with StandardScaler preprocessing pipeline.\n" \
               "• 9 Input Features: Sem 1 Average, Sem 2 Average, Overall Average, Sem 1 Attendance, Sem 2 Attendance, Overall Attendance, " \
               "Grade Trajectory Trend (Sem 2 – Sem 1), Minimum Subject Mark, and Total Failed Courses Count.\n" \
               "• Continuous Dynamic Inference: Whenever faculty updates student marks or attendance, the model automatically re-predicts the risk class in real time."
    p_f.font.size = Pt(10)
    p_f.font.color.rgb = DARK_TEXT


    # =========================================================================
    # SLIDE 8: ONLINE CODING LAB & JUDGE0 EVALUATION
    # =========================================================================
    s8 = create_base_slide(
        "7. Online Coding Lab & Automated Evaluation",
        "Testcase-driven code execution engine with Judge0 architecture (FR-006, FR-007, FR-008)"
    )
    c_left = s8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.45), Inches(5.7), Inches(5.3))
    c_left.fill.solid()
    c_left.fill.fore_color.rgb = WHITE
    c_left.line.color.rgb = BORDER_COL

    tb_jl = s8.shapes.add_textbox(Inches(1.0), Inches(1.55), Inches(5.3), Inches(5.0))
    tf_jl = tb_jl.text_frame
    tf_jl.word_wrap = True
    p = tf_jl.paragraphs[0]
    p.text = "Automated Evaluation Workflow"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = AMU_GREEN

    judge_steps = [
        ("Assignment Creation (Faculty)", "Course faculty defines problem statement, sample input/output, and hidden test cases with input-output specifications."),
        ("In-Browser Code IDE (Student)", "Student writes code directly in the dashboard editor with language support for Python, C++, and Java."),
        ("Automated Judge0 Service Execution", "Code is passed to Judge0 service (or local sandbox runner) and executed against test cases within memory/time bounds."),
        ("Verdict & Score Generation", "Detailed execution report generated: Passed, Wrong Answer, Runtime Error, or Time Limit Exceeded. Score computed: (Passed / Total) × 100."),
        ("Departmental Live Leaderboard", "Live leaderboard aggregates total points and solved problems across all enrolled students in real time.")
    ]
    for t, d in judge_steps:
        pt = tf_jl.add_paragraph()
        pt.text = f"\n• {t}"
        pt.font.size = Pt(11)
        pt.font.bold = True
        pt.font.color.rgb = DARK_TEXT

        pd = tf_jl.add_paragraph()
        pd.text = d
        pd.font.size = Pt(10)
        pd.font.color.rgb = MUTED_TEXT

    # Right: Embedded Graphic
    if os.path.exists(shot_stu):
        s8.shapes.add_picture(shot_stu, Inches(6.8), Inches(1.55), width=Inches(5.733))


    # =========================================================================
    # SLIDE 9: ROLE-BASED DASHBOARD MODULES
    # =========================================================================
    s9 = create_base_slide(
        "8. Role-Based System Portals & Functional Modules",
        "Customized experiences for HOD, Faculty, and Students (FR-001 through FR-004, FR-009)"
    )
    roles = [
        ("HOD Executive Portal", "Department Leadership", AMU_GREEN, [
            "KPI Performance Cards (Total 60 students, Average Marks 74.0%, Attendance 82.0%, High Risk 8)",
            "Subject-wise Average Marks comparative bar chart across Sem 1 & Sem 2",
            "Departmental Academic Risk Distribution pie chart",
            "Student directory with instant drill-down into individual academic history",
            "Consolidated class performance report export (downloadable CSV)"
        ]),
        ("Faculty Management Portal", "Course Instructors", RGBColor(2, 119, 189), [
            "Add and update semester marks per student with immediate risk recalculation",
            "Record and modify semester attendance percentages",
            "Author programming assignments with problem statements & test cases",
            "Inspect student code submissions, test verdicts, and execution logs"
        ]),
        ("Student Academic Portal", "Enrolled Students", RGBColor(197, 155, 39), [
            "Personalized academic performance cards (Sem 1 & Sem 2 averages)",
            "Overall attendance meter with AMU 75% examination eligibility indicator",
            "AI Academic Risk status badge with personalized improvement recommendations",
            "Integrated Online Coding Lab to practice, submit solutions, and climb the leaderboard"
        ])
    ]
    for i, (title, sub, col, items) in enumerate(roles):
        x = 0.8 + i * 3.95
        card = s9.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(1.45), Inches(3.8), Inches(5.3))
        card.fill.solid()
        card.fill.fore_color.rgb = WHITE
        card.line.color.rgb = col
        card.line.width = Pt(1.5)

        # Header tag
        tag = s9.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(1.45), Inches(3.8), Inches(0.85))
        tag.fill.solid()
        tag.fill.fore_color.rgb = col
        tag.line.fill.background()

        tb_h = s9.shapes.add_textbox(Inches(x + 0.15), Inches(1.48), Inches(3.5), Inches(0.8))
        tf_h = tb_h.text_frame
        p_th = tf_h.paragraphs[0]
        p_th.text = title
        p_th.font.size = Pt(12)
        p_th.font.bold = True
        p_th.font.color.rgb = WHITE

        p_sh = tf_h.add_paragraph()
        p_sh.text = sub
        p_sh.font.size = Pt(9.5)
        p_sh.font.color.rgb = RGBColor(230, 245, 255)

        tb_b = s9.shapes.add_textbox(Inches(x + 0.15), Inches(2.45), Inches(3.5), Inches(4.1))
        tf_b = tb_b.text_frame
        tf_b.word_wrap = True
        for idx, item in enumerate(items):
            p_i = tf_b.add_paragraph() if idx > 0 else tf_b.paragraphs[0]
            p_i.text = f"• {item}"
            p_i.font.size = Pt(10)
            p_i.font.color.rgb = DARK_TEXT


    # =========================================================================
    # SLIDE 10: CLOUD DEPLOYMENT & RENDER ANALYSIS
    # =========================================================================
    s10 = create_base_slide(
        "9. Cloud Deployment & Live Render Verification",
        "Production deployment architecture on Render.com Cloud Web Service"
    )
    # Left: Deployment Details
    c_dl = s10.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.45), Inches(5.7), Inches(5.3))
    c_dl.fill.solid()
    c_dl.fill.fore_color.rgb = WHITE
    c_dl.line.color.rgb = BORDER_COL

    tb_dl = s10.shapes.add_textbox(Inches(1.0), Inches(1.55), Inches(5.3), Inches(5.0))
    tf_dl = tb_dl.text_frame
    tf_dl.word_wrap = True
    p = tf_dl.paragraphs[0]
    p.text = "Live Deployment Verification"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = AMU_GREEN

    p_url = tf_dl.add_paragraph()
    p_url.text = "\nLive Production URL:\nhttps://academic-performance-analytics-n044.onrender.com/"
    p_url.font.size = Pt(10.5)
    p_url.font.bold = True
    p_url.font.color.rgb = AMU_GREEN

    render_points = [
        ("Deployment Status", "HTTP 200 OK (Verified Live in Production)"),
        ("Hosting Architecture", "Containerized Linux Web Service with Python 3 runtime."),
        ("Continuous Integration", "Direct webhook integration with GitHub repository; auto-builds on code push."),
        ("Built-in Data Seeding", "Auto-executes database seeding on build, loading 60 students and 12 courses automatically."),
        ("Security & Encryption", "Full HTTPS / SSL certificate encryption managed by Render."),
        ("Near Real-Time Responsiveness", "Sub-second UI response time for data filtration and analytics rendering.")
    ]
    for t, d in render_points:
        pt = tf_dl.add_paragraph()
        pt.text = f"\n• {t}:"
        pt.font.size = Pt(10.5)
        pt.font.bold = True
        pt.font.color.rgb = DARK_TEXT

        pd = tf_dl.add_paragraph()
        pd.text = d
        pd.font.size = Pt(9.5)
        pd.font.color.rgb = MUTED_TEXT

    # Right: Render Graphic
    if os.path.exists(shot_ren):
        s10.shapes.add_picture(shot_ren, Inches(6.8), Inches(1.55), width=Inches(5.733))


    # =========================================================================
    # SLIDE 11: VISUAL PROJECT DEMONSTRATION & GALLERY
    # =========================================================================
    s11 = create_base_slide(
        "10. Project Visual Gallery & Interface Showcase",
        "Direct visual screenshots from the deployed Academic Performance Analytics System"
    )
    # Graphic left (HOD Dashboard)
    if os.path.exists(shot_hod):
        s11.shapes.add_picture(shot_hod, Inches(0.8), Inches(1.5), width=Inches(5.7))

    # Graphic right (Student Portal & Coding Judge)
    if os.path.exists(shot_stu):
        s11.shapes.add_picture(shot_stu, Inches(6.8), Inches(1.5), width=Inches(5.7))

    # Bottom Caption Box
    cap_box = s11.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(5.4), Inches(11.733), Inches(1.4))
    cap_box.fill.solid()
    cap_box.fill.fore_color.rgb = WHITE
    cap_box.line.color.rgb = BORDER_COL

    tb_cap = s11.shapes.add_textbox(Inches(1.0), Inches(5.45), Inches(11.333), Inches(1.3))
    tf_cap = tb_cap.text_frame
    tf_cap.word_wrap = True
    p = tf_cap.paragraphs[0]
    p.text = "Key Visual Highlights Demonstrated Above"
    p.font.size = Pt(11.5)
    p.font.bold = True
    p.font.color.rgb = AMU_GREEN

    p_c = tf_cap.add_paragraph()
    p_c.text = "1. (Left) Executive HOD Dashboard: Top 4 KPI metrics (60 Total Students, 74.0% Avg Marks, 82.0% Attendance, 8 High-Risk Students) accompanied by 12-subject performance bar charts and risk distribution pie chart.\n" \
               "2. (Right) Student Portal & Coding Judge: Personal profile card (FAIZAN AHMAD, GR0622), AI Risk Level determination with 91.2% confidence, in-browser code editor, and instantaneous Judge0 testcase verdicts (100/100 Accepted)."
    p_c.font.size = Pt(9.5)
    p_c.font.color.rgb = DARK_TEXT


    # =========================================================================
    # SLIDE 12: CONCLUSION, EXPECTED OUTCOMES & FUTURE SCOPE
    # =========================================================================
    s12 = prs.slides.add_slide(blank_layout)
    bg12 = s12.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg12.fill.solid()
    bg12.fill.fore_color.rgb = DARK_GREEN
    bg12.line.fill.background()

    in_rect12 = s12.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.4), Inches(0.4), Inches(12.533), Inches(6.7))
    in_rect12.fill.background()
    in_rect12.line.color.rgb = GOLD
    in_rect12.line.width = Pt(1.5)

    tb_t12 = s12.shapes.add_textbox(Inches(0.8), Inches(0.7), Inches(11.733), Inches(0.9))
    tf12 = tb_t12.text_frame
    p0 = tf12.paragraphs[0]
    p0.text = "11. Project Conclusion & Future Enhancements"
    p0.font.size = Pt(24)
    p0.font.bold = True
    p0.font.color.rgb = WHITE
    p0.alignment = PP_ALIGN.CENTER

    # Left: Outcomes Achieved
    c_ach = s12.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0), Inches(1.7), Inches(5.4), Inches(4.3))
    c_ach.fill.solid()
    c_ach.fill.fore_color.rgb = WHITE
    c_ach.line.color.rgb = GOLD

    tb_ach = s12.shapes.add_textbox(Inches(1.2), Inches(1.8), Inches(5.0), Inches(4.1))
    tf_ach = tb_ach.text_frame
    tf_ach.word_wrap = True
    p = tf_ach.paragraphs[0]
    p.text = "Key Achievements (SRS Alignment)"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = AMU_GREEN

    achievements = [
        "100% SRS Compliance: Implemented all functional requirements (FR-001 through FR-010).",
        "Centralized Analytics: Consolidated Sem 1 & Sem 2 Google Form data of 60 MCA students into normalized SQLite storage.",
        "Proactive ML Risk Warning: Early detection of 8 high-risk students before examinations.",
        "Automated Programming Evaluation: Seamless Judge0 testcase evaluation and class leaderboard.",
        "Live Cloud Verification: Operational and accessible on Render.com."
    ]
    for ach in achievements:
        pa = tf_ach.add_paragraph()
        pa.text = f"• {ach}"
        pa.font.size = Pt(10)
        pa.font.color.rgb = DARK_TEXT

    # Right: Future Scope
    c_fut = s12.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.9), Inches(1.7), Inches(5.4), Inches(4.3))
    c_fut.fill.solid()
    c_fut.fill.fore_color.rgb = WHITE
    c_fut.line.color.rgb = GOLD

    tb_fut = s12.shapes.add_textbox(Inches(7.1), Inches(1.8), Inches(5.0), Inches(4.1))
    tf_fut = tb_fut.text_frame
    tf_fut.word_wrap = True
    p = tf_fut.paragraphs[0]
    p.text = "Future Scope & Extensions"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = AMU_GREEN

    future_items = [
        "Multi-Departmental Scale-Up: Transition from SQLite to PostgreSQL/MySQL for faculty-wide adoption.",
        "University ERP Integration: Direct API synchronization with AMU Controller of Examinations.",
        "Automated Code Plagiarism Detection: Integration of MOSS/JPlag algorithms for assignment originality.",
        "Automated Alerts: WhatsApp/SMS push notifications for students approaching attendance shortages (<75%).",
        "Mobile App: Native Android/iOS companion app for instant student grade alerts."
    ]
    for fut in future_items:
        pf = tf_fut.add_paragraph()
        pf.text = f"• {fut}"
        pf.font.size = Pt(10)
        pf.font.color.rgb = DARK_TEXT

    # Bottom Thank You & Q&A
    tb_ty = s12.shapes.add_textbox(Inches(0.8), Inches(6.1), Inches(11.733), Inches(0.7))
    tf_ty = tb_ty.text_frame
    pty = tf_ty.paragraphs[0]
    pty.text = "Thank You! Questions & Discussion Welcome."
    pty.font.size = Pt(16)
    pty.font.bold = True
    pty.font.color.rgb = GOLD
    pty.alignment = PP_ALIGN.CENTER

    # Save presentation
    out_pptx = os.path.abspath("presentation/Academic_Performance_Analytics_System_Presentation.pptx")
    prs.save(out_pptx)
    print("Presentation created successfully at:", out_pptx)
    return out_pptx

if __name__ == "__main__":
    create_deck()
