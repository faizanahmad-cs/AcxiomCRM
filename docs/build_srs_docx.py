import os
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

def set_cell_background(cell, hex_color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>'
        f'<w:top w:w="{top}" w:type="dxa"/>'
        f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
        f'<w:left w:w="{left}" w:type="dxa"/>'
        f'<w:right w:w="{right}" w:type="dxa"/>'
        f'</w:tcMar>'
    )
    tcPr.append(tcMar)

def build_srs_docx():
    doc = Document()

    # Standard 1-inch margins
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)

    BLACK = RGBColor(0, 0, 0)
    logo_path = os.path.abspath("presentation/assets/amu_logo_circle.png")

    # =========================================================================
    # PAGE 1: COVER PAGE (EXACT REPLICA OF ORIGINAL PDF)
    # =========================================================================
    p1 = doc.add_paragraph()
    p1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r1 = p1.add_run("DEPARTMENT OF COMPUTER SCIENCE\nALIGARH MUSLIM UNIVERSITY, ALIGARH-202002")
    r1.bold = True
    r1.font.size = Pt(15)
    r1.font.color.rgb = BLACK

    p_space1 = doc.add_paragraph()
    p_space1.paragraph_format.space_before = Pt(20)

    # Logo
    if os.path.exists(logo_path):
        p_logo = doc.add_paragraph()
        p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_logo.add_run().add_picture(logo_path, width=Inches(1.8))

    p_space2 = doc.add_paragraph()
    p_space2.paragraph_format.space_before = Pt(20)

    p_meta = doc.add_paragraph()
    p_meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_meta = p_meta.add_run("M.C.A SEMESTER – III\nSESSION: 2026-27\nCAMS-3P01: MINI PROJECT")
    r_meta.bold = True
    r_meta.font.size = Pt(12)
    r_meta.font.color.rgb = BLACK

    p_space3 = doc.add_paragraph()
    p_space3.paragraph_format.space_before = Pt(24)

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_title = p_title.add_run("ACADEMIC PERFORMANCE ANALYTICS SYSTEM\n")
    r_title.bold = True
    r_title.font.size = Pt(15)
    r_title.font.color.rgb = BLACK

    r_srs = p_title.add_run("SOFTWARE REQUIREMENT SPECIFICATION")
    r_srs.bold = True
    r_srs.underline = True
    r_srs.font.size = Pt(12)

    p_space4 = doc.add_paragraph()
    p_space4.paragraph_format.space_before = Pt(24)

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_sub = p_sub.add_run("SUBMITTED BY\nNAME: FAIZAN AHMAD\nENROLLMENT NO.: 25CAMSA112")
    r_sub.font.size = Pt(11)
    r_sub.font.color.rgb = BLACK

    p_space5 = doc.add_paragraph()
    p_space5.paragraph_format.space_before = Pt(20)

    p_to = doc.add_paragraph()
    p_to.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_to = p_to.add_run("SUBMITTED TO\nPROF. AASIM ZAFAR\nMR. MOHD ADNAN\nMR. KAUSHAR ALI")
    r_to.font.size = Pt(11)
    r_to.font.color.rgb = BLACK

    doc.add_page_break()

    # =========================================================================
    # PAGE 2: TABLE OF CONTENTS
    # =========================================================================
    h_toc = doc.add_paragraph()
    r = h_toc.add_run("Table of Contents")
    r.bold = True
    r.font.size = Pt(16)
    r.font.color.rgb = BLACK

    toc_items = [
        "1. Information Gathering Methods",
        "   1.1 Method Comparison",
        "2. Detailed Requirements Specification",
        "   2.1 Functional Requirements",
        "   2.2 Non-Functional Requirements",
        "   2.3 Data Requirements",
        "   2.4 System Requirements",
        "3. Design and Analysis",
        "   3.1 System Architecture",
        "   3.2 Detailed Design Diagram",
        "   3.3 Design Tools and Limitations",
        "4. Implementation",
        "   4.1 Technology Stack Justification",
        "   4.2 Interface Design",
        "   4.3 Implementation Status",
        "5. Preliminary Results and Performance Metrics",
        "6. Scope",
        "7. Feasibility Study",
        "8. Preliminary Development Plan",
        "9. Expected Outcome",
        "10. References"
    ]
    for item in toc_items:
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(4)
        r = p.add_run(item)
        r.font.size = Pt(10)
        r.font.color.rgb = BLACK

    doc.add_page_break()

    # Helpers
    def add_h1(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(6)
        r = p.add_run(text)
        r.bold = True
        r.font.size = Pt(14)
        r.font.color.rgb = BLACK
        return p

    def add_h2(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(4)
        r = p.add_run(text)
        r.bold = True
        r.font.size = Pt(12)
        r.font.color.rgb = BLACK
        return p

    def add_h3(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(3)
        r = p.add_run(text)
        r.bold = True
        r.font.size = Pt(11)
        r.font.color.rgb = BLACK
        return p

    def add_body(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(5)
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        r = p.add_run(text)
        r.font.size = Pt(10)
        r.font.color.rgb = BLACK
        return p

    def add_bullet(text):
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_after = Pt(3)
        r = p.add_run(text)
        r.font.size = Pt(10)
        r.font.color.rgb = BLACK
        return p

    def add_diagram(img_path, caption):
        if os.path.exists(img_path):
            p_img = doc.add_paragraph()
            p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_img.paragraph_format.space_before = Pt(10)
            p_img.add_run().add_picture(img_path, width=Inches(6.2))

            p_cap = doc.add_paragraph()
            p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_cap.paragraph_format.space_after = Pt(14)
            r_cap = p_cap.add_run(caption)
            r_cap.bold = True
            r_cap.font.size = Pt(10)
            r_cap.font.color.rgb = BLACK

    # =========================================================================
    # SECTION 1: INFORMATION GATHERING METHODS
    # =========================================================================
    add_h1("1. Information Gathering Methods")
    add_body(
        "The requirements for the Academic Performance Analytics System were identified by examining the existing "
        "academic-record management process and the proposed centralized method of collecting, storing, and analyzing "
        "student academic information. Academic records such as semester marks, attendance, and coding-assignment "
        "performance are currently maintained separately and largely manually."
    )
    add_h2("1.1 Method Comparison")
    add_body("Method 1: Existing Academic Record Analysis")
    add_bullet("Provides an understanding of how marks, attendance, and coding-assignment records are currently maintained.")
    add_bullet("Helps identify the difficulties faced by the HOD, faculty members, and students.")
    add_bullet("Reveals the need for centralized storage, automated analysis, and early-warning information.")

    add_body("Method 2: Structured Google Form-Based Data Collection")
    add_bullet("Provides a structured mechanism for collecting Semester 1 and Semester 2 academic information.")
    add_bullet("Allows collected information to be imported into the relational database.")
    add_bullet("Reduces the learning curve because the class is already using a Google Form for data collection.")

    add_body("Most Effective Approach")
    add_body(
        "A combination of existing-process analysis and structured academic-data collection is used. The first establishes "
        "the requirements, while the second provides the initial dataset for centralized processing and analytics."
    )

    # =========================================================================
    # SECTION 2: DETAILED REQUIREMENTS SPECIFICATION
    # =========================================================================
    add_h1("2. Detailed Requirements Specification")
    add_h2("2.1 Functional Requirements")

    fr_rows = [
        ("FR-001", "User Authentication and Role-Based Login", "Secure login for HOD, Faculty, and Student users with JWT authentication, bcrypt password hashing, and role-based access.", "High"),
        ("FR-002", "Student Academic Data Management", "Faculty can add and update student marks for courses they teach.", "High"),
        ("FR-003", "Attendance Management", "Faculty can record student attendance percentage per semester.", "High"),
        ("FR-004", "Student Academic Dashboard", "Students can view their own marks, attendance, coding performance, and predicted risk.", "High"),
        ("FR-005", "Academic Risk Prediction", "Classify students as Low, Medium, or High risk using marks and attendance trends.", "High"),
        ("FR-006", "Coding Assignment Creation", "Faculty can create programming assignments and define test cases.", "High"),
        ("FR-007", "Automated Code Evaluation", "Evaluate student code through Judge0 API and calculate a score.", "High"),
        ("FR-008", "Coding Assignment Leaderboard", "Display coding-assignment scores in a live leaderboard.", "Medium"),
        ("FR-009", "HOD Performance Dashboard and Reporting", "Provide subject-wise average performance reports and consolidated academic insights.", "High"),
        ("FR-010", "Near Real-Time Dashboard Updates", "Reflect new marks or submissions within approximately 15 seconds without manual reload.", "Medium")
    ]

    t_fr = doc.add_table(rows=1, cols=4)
    t_fr.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr_cells = t_fr.rows[0].cells
    hdr_titles = ["ID", "Requirement", "Description", "Priority"]
    for i, title in enumerate(hdr_titles):
        hdr_cells[i].text = title
        set_cell_background(hdr_cells[i], "EAEAEA")
        hdr_cells[i].paragraphs[0].runs[0].font.color.rgb = BLACK
        hdr_cells[i].paragraphs[0].runs[0].bold = True
        set_cell_margins(hdr_cells[i])

    for r_data in fr_rows:
        row_cells = t_fr.add_row().cells
        for i, val in enumerate(r_data):
            row_cells[i].text = val
            row_cells[i].paragraphs[0].runs[0].font.size = Pt(9)
            row_cells[i].paragraphs[0].runs[0].font.color.rgb = BLACK
            set_cell_margins(row_cells[i])

    # 2.2 Non-Functional Requirements
    add_h2("2.2 Non-Functional Requirements")
    nfr_rows = [
        ("Performance", "Dashboard updates should appear within approximately 15 seconds."),
        ("Security", "Only authenticated users can access the system; passwords use bcrypt hashing and endpoints enforce role-based access."),
        ("Usability", "Charts shall be simple and clearly labelled."),
        ("Reliability", "Relational database constraints and foreign keys shall maintain data integrity."),
        ("Maintainability", "Modular and documented components shall support future extension.")
    ]
    t_nfr = doc.add_table(rows=1, cols=2)
    t_nfr.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr = t_nfr.rows[0].cells
    hdr[0].text = "Category"
    hdr[1].text = "Requirement"
    for c in hdr:
        set_cell_background(c, "EAEAEA")
        c.paragraphs[0].runs[0].font.color.rgb = BLACK
        c.paragraphs[0].runs[0].bold = True
        set_cell_margins(c)

    for cat, req in nfr_rows:
        row = t_nfr.add_row().cells
        row[0].text = cat
        row[1].text = req
        for c in row:
            c.paragraphs[0].runs[0].font.size = Pt(9)
            c.paragraphs[0].runs[0].font.color.rgb = BLACK
            set_cell_margins(c)

    # 2.3 Data Requirements
    add_h2("2.3 Data Requirements")
    data_rows = [
        ("User", "User_ID, Name, Email, Password Hash, Role"),
        ("Student", "Student_ID, Name, Faculty_No, Enrollment_No, Email"),
        ("Faculty", "Faculty_ID, Name, Email, Password Hash"),
        ("Course", "Course_ID, Course_Name, Semester, Faculty_ID"),
        ("Academic Record", "Record_ID, Student_ID, Course_ID, Semester, Marks"),
        ("Attendance", "Attendance_ID, Student_ID, Semester, Attendance_Percentage"),
        ("Coding Assignment", "Assignment_ID, Faculty_ID, Course_ID, Title, Problem, Test Cases"),
        ("Code Submission", "Submission_ID, Assignment_ID, Student_ID, Code, Score, Status"),
        ("Risk Prediction", "Prediction_ID, Student_ID, Risk_Level, Prediction_Date, Model_Result")
    ]
    t_data = doc.add_table(rows=1, cols=2)
    t_data.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr = t_data.rows[0].cells
    hdr[0].text = "Entity"
    hdr[1].text = "Major Attributes"
    for c in hdr:
        set_cell_background(c, "EAEAEA")
        c.paragraphs[0].runs[0].font.color.rgb = BLACK
        c.paragraphs[0].runs[0].bold = True
        set_cell_margins(c)

    for ent, att in data_rows:
        row = t_data.add_row().cells
        row[0].text = ent
        row[1].text = att
        for c in row:
            c.paragraphs[0].runs[0].font.size = Pt(9)
            c.paragraphs[0].runs[0].font.color.rgb = BLACK
            set_cell_margins(c)

    add_body(
        "Relationships: A Student can have many academic and attendance records; Faculty can teach many Courses "
        "and create many Assignments; Assignments can receive many Submissions; Students can have multiple Risk "
        "Predictions as new academic information is processed."
    )

    # 2.4 System Requirements
    add_h2("2.4 System Requirements")
    sys_rows = [
        ("Front-end / Dashboard", "Streamlit (Python)"),
        ("Back-end", "FastAPI (Python)"),
        ("Database", "SQLite; MySQL/PostgreSQL for future scale-up"),
        ("Authentication", "JWT tokens with bcrypt password hashing"),
        ("Machine Learning", "scikit-learn, Pandas, NumPy"),
        ("Coding Assignment Judge", "Judge0 API"),
        ("Development Environment", "VS Code"),
        ("Version Control", "Git")
    ]
    t_sys = doc.add_table(rows=1, cols=2)
    t_sys.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr = t_sys.rows[0].cells
    hdr[0].text = "Component"
    hdr[1].text = "Proposed Technology"
    for c in hdr:
        set_cell_background(c, "EAEAEA")
        c.paragraphs[0].runs[0].font.color.rgb = BLACK
        c.paragraphs[0].runs[0].bold = True
        set_cell_margins(c)

    for comp, tech in sys_rows:
        row = t_sys.add_row().cells
        row[0].text = comp
        row[1].text = tech
        for c in row:
            c.paragraphs[0].runs[0].font.size = Pt(9)
            c.paragraphs[0].runs[0].font.color.rgb = BLACK
            set_cell_margins(c)

    doc.add_page_break()

    # =========================================================================
    # SECTION 3: DESIGN AND ANALYSIS (FORMAL BLACK & WHITE DIAGRAMS)
    # =========================================================================
    add_h1("3. Design and Analysis")
    add_h2("3.1 System Architecture")
    add_body(
        "The system follows a layered architecture consisting of the Streamlit presentation layer, FastAPI backend, "
        "SQLite database, machine-learning analytics layer, and Judge0 code-evaluation service."
    )
    add_diagram("docs/diagrams/fig3_1_architecture.png", "Figure 3.1: High-Level System Architecture")

    add_h3("Database Design")
    add_body(
        "The database consists of normalized relational entities for users, students, faculty, courses, academic records, "
        "attendance, assignments, submissions, and risk predictions. Foreign-key relationships maintain data integrity."
    )
    add_diagram("docs/diagrams/fig3_2_erd.png", "Figure 3.2: Entity Relationship Diagram")

    doc.add_page_break()

    add_h2("3.2 Detailed Design Diagram")
    add_h3("Use Case Diagram")
    add_body(
        "The primary actors are HOD, Faculty, and Student. Their interactions cover authentication, academic-data "
        "management, performance analysis, coding-assignment management, and academic-risk viewing."
    )
    add_diagram("docs/diagrams/fig3_3_usecase.png", "Figure 3.3: Use Case Diagram")

    add_h3("Data Flow Diagrams")
    add_diagram("docs/diagrams/fig3_4_context.png", "Figure 3.4: Context Diagram")
    add_diagram("docs/diagrams/fig3_5_dfd0.png", "Figure 3.5: Level 0 Data Flow Diagram")
    add_diagram("docs/diagrams/fig3_6_dfd1.png", "Figure 3.6: Level 1 DFD - Academic Analytics and Risk Prediction")

    doc.add_page_break()

    add_h3("Class Diagram")
    add_diagram("docs/diagrams/fig3_7_class.png", "Figure 3.7: Class Diagram")

    add_h3("Sequence Diagram")
    add_body(
        "The sequence below illustrates the coding-assignment workflow from faculty assignment creation through "
        "student submission, Judge0 execution, result storage, and leaderboard display."
    )
    add_diagram("docs/diagrams/fig3_8_sequence.png", "Figure 3.8: Sequence Diagram - Coding Assignment Evaluation")

    add_h2("3.3 Design Tools and Limitations")
    add_body(
        "Draw.io may be used to create ER diagrams, use-case diagrams, DFDs, class diagrams, sequence diagrams, and "
        "architecture diagrams. Diagram export and manual insertion into the final document can be time-consuming, "
        "especially for complex diagrams."
    )

    doc.add_page_break()

    # =========================================================================
    # SECTION 4: IMPLEMENTATION
    # =========================================================================
    add_h1("4. Implementation")
    add_h2("4.1 Technology Stack Justification")

    add_body("Frontend / Dashboard")
    add_body("Streamlit is selected for a Python-based interactive dashboard suitable for academic charts and reports.")

    add_body("Backend")
    add_body("FastAPI provides the secure API and business-logic layer.")

    add_body("Database")
    add_body("SQLite is appropriate for the initial class-scale prototype; MySQL/PostgreSQL can be used for future scale-up.")

    add_body("Authentication")
    add_body("JWT tokens and bcrypt hashing provide authenticated and role-based access.")

    add_body("Machine Learning")
    add_body("Pandas and NumPy support data processing while scikit-learn supports academic-risk classification.")

    add_body("Coding Judge")
    add_body("Judge0 provides automated execution and test-case evaluation.")

    add_body("Development / Version Control")
    add_body("VS Code and Git support development, testing, debugging, and version tracking.")

    add_h2("4.2 Interface Design")
    add_body(
        "The interface is designed as a web-based dashboard with separate views for HOD, Faculty, and Student users. "
        "It uses clearly labelled charts and academic indicators."
    )
    add_diagram("docs/diagrams/fig4_1_mockup.png", "Figure 4.1: Dashboard Interface Mockup")

    add_h2("4.3 Implementation Status")
    impl_rows = [
        ("FR-001", "User Authentication", "In Progress / Being Implemented"),
        ("FR-002", "Academic Data Management", "In Progress / Being Implemented"),
        ("FR-003", "Attendance Management", "In Progress / Being Implemented"),
        ("FR-004", "Student Academic Dashboard", "In Progress / Being Implemented"),
        ("FR-005", "Academic Risk Prediction", "In Progress / Being Implemented"),
        ("FR-006", "Coding Assignment Creation", "In Progress / Being Implemented"),
        ("FR-007", "Automated Code Evaluation", "In Progress / Being Implemented"),
        ("FR-008", "Coding Leaderboard", "In Progress / Being Implemented"),
        ("FR-009", "HOD Performance Reporting", "In Progress / Being Implemented")
    ]
    t_impl = doc.add_table(rows=1, cols=3)
    t_impl.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr = t_impl.rows[0].cells
    hdr[0].text = "Requirement"
    hdr[1].text = "Feature"
    hdr[2].text = "Status"
    for c in hdr:
        set_cell_background(c, "EAEAEA")
        c.paragraphs[0].runs[0].font.color.rgb = BLACK
        c.paragraphs[0].runs[0].bold = True
        set_cell_margins(c)

    for req, feat, stat in impl_rows:
        row = t_impl.add_row().cells
        row[0].text = req
        row[1].text = feat
        row[2].text = stat
        for c in row:
            c.paragraphs[0].runs[0].font.size = Pt(9)
            c.paragraphs[0].runs[0].font.color.rgb = BLACK
            set_cell_margins(c)

    doc.add_page_break()

    # =========================================================================
    # SECTION 5: PRELIMINARY RESULTS AND METRICS
    # =========================================================================
    add_h1("5. Preliminary Results and Performance Metrics")
    add_bullet("Dashboard update target: approximately 15 seconds for newly entered marks or submissions.")
    add_bullet("Database integrity: foreign keys and relational constraints shall maintain consistent academic records.")
    add_bullet("Risk prediction: students shall be classified into Low, Medium, or High risk.")
    add_bullet("Coding evaluation: submissions shall be evaluated against defined test cases through Judge0.")
    add_bullet("Usability: charts shall be clearly labelled and understandable without specialized technical training.")

    # SECTION 6: SCOPE
    add_h1("6. Scope")
    add_h2("Included")
    add_bullet("Coverage limited to the Department of Computer Science.")
    add_bullet("Role-based login for HOD, Faculty, and Students.")
    add_bullet("Semester 1 and Semester 2 marks and attendance tracking.")
    add_bullet("Machine-learning-based academic risk prediction.")
    add_bullet("Coding-assignment submission, automated evaluation, and leaderboard.")
    add_bullet("Near real-time performance dashboard.")

    add_h2("Not Included")
    add_bullet("Comparison across multiple departments.")
    add_bullet("Integration with the official university ERP or examination system.")
    add_bullet("Financial, fee, or accounts management.")
    add_bullet("Native mobile application.")
    add_bullet("Large-scale plagiarism detection.")

    # SECTION 7: FEASIBILITY STUDY
    add_h1("7. Feasibility Study")
    add_h2("Technical Feasibility")
    add_body(
        "The system uses freely available, well-documented technologies including Python, FastAPI, SQLite, scikit-learn, "
        "Streamlit, Pandas, NumPy, and Judge0 API. These can operate on a standard development laptop without specialized hardware."
    )
    add_h2("Operational Feasibility")
    add_body(
        "Faculty and students are familiar with web-based forms and dashboards. Semester 1 and Semester 2 data is being "
        "collected through a Google Form already used by the class."
    )
    add_h2("Economic / Resource Feasibility")
    add_body(
        "The core components are free and open source. The only potential cost is exceeding the free tier of the coding-judge "
        "API, which is not required for a semester-scale demonstration."
    )

    doc.add_page_break()

    # SECTION 8: PRELIMINARY DEVELOPMENT PLAN
    add_h1("8. Preliminary Development Plan")
    plan_rows = [
        ("1", "Problem identification and data collection"),
        ("2", "Requirements analysis"),
        ("3", "System design and architecture"),
        ("4", "Database design and implementation"),
        ("5", "Backend and authentication implementation"),
        ("6", "Machine-learning model development and training"),
        ("7", "Coding-assignment module integration"),
        ("8", "Dashboard development"),
        ("9", "Testing"),
        ("10", "Documentation and presentation")
    ]
    t_plan = doc.add_table(rows=1, cols=2)
    t_plan.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr = t_plan.rows[0].cells
    hdr[0].text = "Phase"
    hdr[1].text = "Activity"
    for c in hdr:
        set_cell_background(c, "EAEAEA")
        c.paragraphs[0].runs[0].font.color.rgb = BLACK
        c.paragraphs[0].runs[0].bold = True
        set_cell_margins(c)

    for p_num, act in plan_rows:
        row = t_plan.add_row().cells
        row[0].text = p_num
        row[1].text = act
        for c in row:
            c.paragraphs[0].runs[0].font.size = Pt(9)
            c.paragraphs[0].runs[0].font.color.rgb = BLACK
            set_cell_margins(c)

    # SECTION 9: EXPECTED OUTCOME
    add_h1("9. Expected Outcome")
    add_body(
        "A working prototype, scoped to a single Computer Science class, that demonstrates centralized academic data "
        "storage, secure role-based access, machine-learning-based early identification of at-risk students, and automated "
        "evaluation of coding assignments through a live, near real-time dashboard."
    )

    # SECTION 10: REFERENCES
    add_h1("10. References")
    ref_list = [
        "[1] R. S. Pressman and B. R. Maxim, Software Engineering: A Practitioner’s Approach, 9th ed., McGraw-Hill Education, 2019.",
        "[2] FastAPI, \"FastAPI documentation,\" 2026.",
        "[3] Streamlit Inc., \"Streamlit documentation,\" 2026.",
        "[4] scikit-learn developers, \"scikit-learn: Machine learning in Python,\" 2026.",
        "[5] SQLAlchemy, \"SQLAlchemy documentation,\" 2026.",
        "[6] Judge0, \"Judge0 CE API documentation,\" 2026."
    ]
    for r in ref_list:
        add_body(r)

    docx_filename = os.path.abspath("docs/Academic_Performance_Analytics_System_SRS.docx")
    doc.save(docx_filename)
    print("Formal B&W DOCX generated successfully:", docx_filename)
    return docx_filename

if __name__ == "__main__":
    build_srs_docx()
