import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, PageBreak, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        if self._pageNumber > 1:
            self.saveState()
            self.setFont("Helvetica", 9)
            self.setFillColor(colors.HexColor("#000000"))
            # Header
            self.drawString(54, 755, "Academic Performance Analytics System — SRS")
            self.setStrokeColor(colors.HexColor("#000000"))
            self.setLineWidth(0.5)
            self.line(54, 748, 558, 748)
            
            # Footer
            self.line(54, 45, 558, 45)
            self.drawString(54, 32, "Department of Computer Science, AMU")
            page_text = f"Page {self._pageNumber} of {page_count}"
            self.drawRightString(558, 32, page_text)
            self.restoreState()

def build_srs_pdf():
    pdf_filename = os.path.abspath("docs/Academic_Performance_Analytics_System_SRS.pdf")
    doc = SimpleDocTemplate(
        pdf_filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Cover page styles (exact replica of original PDF page 1)
    style_cover_dept = ParagraphStyle(
        "CoverDept",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=15,
        leading=21,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#000000")
    )

    style_cover_meta = ParagraphStyle(
        "CoverMeta",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=18,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#000000")
    )

    style_cover_title = ParagraphStyle(
        "CoverTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=15,
        leading=21,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#000000")
    )

    style_cover_srs = ParagraphStyle(
        "CoverSRS",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=17,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#000000")
    )

    style_cover_sub = ParagraphStyle(
        "CoverSub",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=11,
        leading=17,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#000000")
    )

    # Document Section Styles (Strict Black Text & Headings)
    style_h1 = ParagraphStyle(
        "SRS_H1",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=14,
        leading=18,
        spaceBefore=14,
        spaceAfter=8,
        textColor=colors.HexColor("#000000")
    )

    style_h2 = ParagraphStyle(
        "SRS_H2",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        spaceBefore=10,
        spaceAfter=6,
        textColor=colors.HexColor("#000000")
    )

    style_h3 = ParagraphStyle(
        "SRS_H3",
        parent=styles["Heading3"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=15,
        spaceBefore=8,
        spaceAfter=4,
        textColor=colors.HexColor("#000000")
    )

    style_body = ParagraphStyle(
        "SRS_Body",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=14,
        alignment=TA_JUSTIFY,
        spaceAfter=6,
        textColor=colors.HexColor("#000000")
    )

    style_bullet = ParagraphStyle(
        "SRS_Bullet",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=14,
        leftIndent=15,
        spaceAfter=4,
        textColor=colors.HexColor("#000000")
    )

    style_caption = ParagraphStyle(
        "SRS_Caption",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=14,
        alignment=TA_CENTER,
        spaceBefore=6,
        spaceAfter=12,
        textColor=colors.HexColor("#000000")
    )

    style_th = ParagraphStyle(
        "SRS_TH",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=12,
        alignment=TA_LEFT,
        textColor=colors.HexColor("#000000")
    )

    style_td = ParagraphStyle(
        "SRS_TD",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=11.5,
        alignment=TA_LEFT,
        textColor=colors.HexColor("#000000")
    )

    story = []

    # =========================================================================
    # PAGE 1: COVER PAGE (EXACT ORIGINAL MATCH)
    # =========================================================================
    story.append(Spacer(1, 20))
    story.append(Paragraph("DEPARTMENT OF COMPUTER SCIENCE", style_cover_dept))
    story.append(Paragraph("ALIGARH MUSLIM UNIVERSITY, ALIGARH-202002", style_cover_dept))
    story.append(Spacer(1, 35))

    logo_path = os.path.abspath("presentation/assets/amu_logo_circle.png")
    if os.path.exists(logo_path):
        story.append(RLImage(logo_path, width=140, height=140))
    story.append(Spacer(1, 40))

    story.append(Paragraph("M.C.A SEMESTER – III", style_cover_meta))
    story.append(Spacer(1, 4))
    story.append(Paragraph("SESSION: 2026-27", style_cover_meta))
    story.append(Spacer(1, 4))
    story.append(Paragraph("CAMS-3P01: MINI PROJECT", style_cover_meta))
    story.append(Spacer(1, 35))

    story.append(Paragraph("ACADEMIC PERFORMANCE ANALYTICS SYSTEM", style_cover_title))
    story.append(Spacer(1, 6))
    story.append(Paragraph("<u>SOFTWARE REQUIREMENT SPECIFICATION</u>", style_cover_srs))
    story.append(Spacer(1, 35))

    story.append(Paragraph("SUBMITTED BY", style_cover_sub))
    story.append(Spacer(1, 4))
    story.append(Paragraph("NAME: FAIZAN AHMAD", style_cover_sub))
    story.append(Spacer(1, 4))
    story.append(Paragraph("ENROLLMENT NO.: 25CAMSA112", style_cover_sub))
    story.append(Spacer(1, 35))

    story.append(Paragraph("SUBMITTED TO", style_cover_sub))
    story.append(Spacer(1, 4))
    story.append(Paragraph("PROF. AASIM ZAFAR", style_cover_sub))
    story.append(Spacer(1, 4))
    story.append(Paragraph("MR. MOHD ADNAN", style_cover_sub))
    story.append(Spacer(1, 4))
    story.append(Paragraph("MR. KAUSHAR ALI", style_cover_sub))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 2: TABLE OF CONTENTS
    # =========================================================================
    story.append(Paragraph("Table of Contents", style_h1))
    story.append(Spacer(1, 10))

    toc_items = [
        ("1. Information Gathering Methods", "3"),
        ("   1.1 Method Comparison", "3"),
        ("2. Detailed Requirements Specification", "3"),
        ("   2.1 Functional Requirements", "3"),
        ("   2.2 Non-Functional Requirements", "4"),
        ("   2.3 Data Requirements", "4"),
        ("   2.4 System Requirements", "5"),
        ("3. Design and Analysis", "5"),
        ("   3.1 System Architecture", "5"),
        ("   3.2 Detailed Design Diagram", "6"),
        ("   3.3 Design Tools and Limitations", "10"),
        ("4. Implementation", "10"),
        ("   4.1 Technology Stack Justification", "10"),
        ("   4.2 Interface Design", "11"),
        ("   4.3 Implementation Status", "11"),
        ("5. Preliminary Results and Performance Metrics", "12"),
        ("6. Scope", "12"),
        ("7. Feasibility Study", "12"),
        ("8. Preliminary Development Plan", "13"),
        ("9. Expected Outcome", "13"),
        ("10. References", "13"),
    ]
    toc_data = []
    for title, pg in toc_items:
        toc_data.append([
            Paragraph(title.replace(" ", "&nbsp;"), style_body),
            Paragraph(pg, ParagraphStyle("TOC_Pg", parent=style_body, alignment=TA_CENTER))
        ])

    toc_table = Table(toc_data, colWidths=[440, 64])
    toc_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('LINEBELOW', (0, 0), (-1, -1), 0.5, colors.HexColor("#DDDDDD")),
    ]))
    story.append(toc_table)
    story.append(PageBreak())

    # =========================================================================
    # SECTION 1: INFORMATION GATHERING METHODS
    # =========================================================================
    story.append(Paragraph("1. Information Gathering Methods", style_h1))
    story.append(Paragraph(
        "The requirements for the Academic Performance Analytics System were identified by examining the existing "
        "academic-record management process and the proposed centralized method of collecting, storing, and analyzing "
        "student academic information. Academic records such as semester marks, attendance, and coding-assignment "
        "performance are currently maintained separately and largely manually.",
        style_body
    ))
    story.append(Paragraph("1.1 Method Comparison", style_h2))
    story.append(Paragraph("<b>Method 1: Existing Academic Record Analysis</b>", style_body))
    story.append(Paragraph("• Provides an understanding of how marks, attendance, and coding-assignment records are currently maintained.", style_bullet))
    story.append(Paragraph("• Helps identify the difficulties faced by the HOD, faculty members, and students.", style_bullet))
    story.append(Paragraph("• Reveals the need for centralized storage, automated analysis, and early-warning information.", style_bullet))

    story.append(Paragraph("<b>Method 2: Structured Google Form-Based Data Collection</b>", style_body))
    story.append(Paragraph("• Provides a structured mechanism for collecting Semester 1 and Semester 2 academic information.", style_bullet))
    story.append(Paragraph("• Allows collected information to be imported into the relational database.", style_bullet))
    story.append(Paragraph("• Reduces the learning curve because the class is already using a Google Form for data collection.", style_bullet))

    story.append(Paragraph("<b>Most Effective Approach</b>", style_body))
    story.append(Paragraph(
        "A combination of existing-process analysis and structured academic-data collection is used. The first establishes "
        "the requirements, while the second provides the initial dataset for centralized processing and analytics.",
        style_body
    ))
    story.append(Spacer(1, 8))

    # =========================================================================
    # SECTION 2: DETAILED REQUIREMENTS SPECIFICATION
    # =========================================================================
    story.append(Paragraph("2. Detailed Requirements Specification", style_h1))
    story.append(Paragraph("2.1 Functional Requirements", style_h2))

    fr_data = [
        [Paragraph("ID", style_th), Paragraph("Requirement", style_th), Paragraph("Description", style_th), Paragraph("Priority", style_th)],
        [Paragraph("FR-001", style_td), Paragraph("User Authentication and Role-Based Login", style_td), Paragraph("Secure login for HOD, Faculty, and Student users with JWT authentication, bcrypt password hashing, and role-based access.", style_td), Paragraph("High", style_td)],
        [Paragraph("FR-002", style_td), Paragraph("Student Academic Data Management", style_td), Paragraph("Faculty can add and update student marks for courses they teach.", style_td), Paragraph("High", style_td)],
        [Paragraph("FR-003", style_td), Paragraph("Attendance Management", style_td), Paragraph("Faculty can record student attendance percentage per semester.", style_td), Paragraph("High", style_td)],
        [Paragraph("FR-004", style_td), Paragraph("Student Academic Dashboard", style_td), Paragraph("Students can view their own marks, attendance, coding performance, and predicted risk.", style_td), Paragraph("High", style_td)],
        [Paragraph("FR-005", style_td), Paragraph("Academic Risk Prediction", style_td), Paragraph("Classify students as Low, Medium, or High risk using marks and attendance trends.", style_td), Paragraph("High", style_td)],
        [Paragraph("FR-006", style_td), Paragraph("Coding Assignment Creation", style_td), Paragraph("Faculty can create programming assignments and define test cases.", style_td), Paragraph("High", style_td)],
        [Paragraph("FR-007", style_td), Paragraph("Automated Code Evaluation", style_td), Paragraph("Evaluate student code through Judge0 API and calculate a score.", style_td), Paragraph("High", style_td)],
        [Paragraph("FR-008", style_td), Paragraph("Coding Assignment Leaderboard", style_td), Paragraph("Display coding-assignment scores in a live leaderboard.", style_td), Paragraph("Medium", style_td)],
        [Paragraph("FR-009", style_td), Paragraph("HOD Performance Dashboard and Reporting", style_td), Paragraph("Provide subject-wise average performance reports and consolidated academic insights.", style_td), Paragraph("High", style_td)],
        [Paragraph("FR-010", style_td), Paragraph("Near Real-Time Dashboard Updates", style_td), Paragraph("Reflect new marks or submissions within approximately 15 seconds without manual reload.", style_td), Paragraph("Medium", style_td)]
    ]
    fr_table = Table(fr_data, colWidths=[55, 125, 274, 50])
    fr_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#EAEAEA")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#000000")),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(fr_table)
    story.append(Spacer(1, 10))

    # 2.2 Non-Functional Requirements
    story.append(Paragraph("2.2 Non-Functional Requirements", style_h2))
    nfr_data = [
        [Paragraph("Category", style_th), Paragraph("Requirement", style_th)],
        [Paragraph("Performance", style_td), Paragraph("Dashboard updates should appear within approximately 15 seconds.", style_td)],
        [Paragraph("Security", style_td), Paragraph("Only authenticated users can access the system; passwords use bcrypt hashing and endpoints enforce role-based access.", style_td)],
        [Paragraph("Usability", style_td), Paragraph("Charts shall be simple and clearly labelled.", style_td)],
        [Paragraph("Reliability", style_td), Paragraph("Relational database constraints and foreign keys shall maintain data integrity.", style_td)],
        [Paragraph("Maintainability", style_td), Paragraph("Modular and documented components shall support future extension.", style_td)]
    ]
    nfr_table = Table(nfr_data, colWidths=[120, 384])
    nfr_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#EAEAEA")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#000000")),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(nfr_table)
    story.append(Spacer(1, 10))

    # 2.3 Data Requirements
    story.append(Paragraph("2.3 Data Requirements", style_h2))
    data_rows = [
        [Paragraph("Entity", style_th), Paragraph("Major Attributes", style_th)],
        [Paragraph("User", style_td), Paragraph("User_ID, Name, Email, Password Hash, Role", style_td)],
        [Paragraph("Student", style_td), Paragraph("Student_ID, Name, Faculty_No, Enrollment_No, Email", style_td)],
        [Paragraph("Faculty", style_td), Paragraph("Faculty_ID, Name, Email, Password Hash", style_td)],
        [Paragraph("Course", style_td), Paragraph("Course_ID, Course_Name, Semester, Faculty_ID", style_td)],
        [Paragraph("Academic Record", style_td), Paragraph("Record_ID, Student_ID, Course_ID, Semester, Marks", style_td)],
        [Paragraph("Attendance", style_td), Paragraph("Attendance_ID, Student_ID, Semester, Attendance_Percentage", style_td)],
        [Paragraph("Coding Assignment", style_td), Paragraph("Assignment_ID, Faculty_ID, Course_ID, Title, Problem, Test Cases", style_td)],
        [Paragraph("Code Submission", style_td), Paragraph("Submission_ID, Assignment_ID, Student_ID, Code, Score, Status", style_td)],
        [Paragraph("Risk Prediction", style_td), Paragraph("Prediction_ID, Student_ID, Risk_Level, Prediction_Date, Model_Result", style_td)]
    ]
    data_table = Table(data_rows, colWidths=[130, 374])
    data_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#EAEAEA")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#000000")),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 3.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3.5),
    ]))
    story.append(data_table)
    story.append(Spacer(1, 5))
    story.append(Paragraph(
        "<b>Relationships:</b> A Student can have many academic and attendance records; Faculty can teach many Courses "
        "and create many Assignments; Assignments can receive many Submissions; Students can have multiple Risk "
        "Predictions as new academic information is processed.",
        style_body
    ))
    story.append(Spacer(1, 8))

    # 2.4 System Requirements
    story.append(Paragraph("2.4 System Requirements", style_h2))
    sys_rows = [
        [Paragraph("Component", style_th), Paragraph("Proposed Technology", style_th)],
        [Paragraph("Front-end / Dashboard", style_td), Paragraph("Streamlit (Python)", style_td)],
        [Paragraph("Back-end", style_td), Paragraph("FastAPI (Python)", style_td)],
        [Paragraph("Database", style_td), Paragraph("SQLite; MySQL/PostgreSQL for future scale-up", style_td)],
        [Paragraph("Authentication", style_td), Paragraph("JWT tokens with bcrypt password hashing", style_td)],
        [Paragraph("Machine Learning", style_td), Paragraph("scikit-learn, Pandas, NumPy", style_td)],
        [Paragraph("Coding Assignment Judge", style_td), Paragraph("Judge0 API", style_td)],
        [Paragraph("Development Environment", style_td), Paragraph("VS Code", style_td)],
        [Paragraph("Version Control", style_td), Paragraph("Git", style_td)]
    ]
    sys_table = Table(sys_rows, colWidths=[150, 354])
    sys_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#EAEAEA")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#000000")),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 3.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3.5),
    ]))
    story.append(sys_table)
    story.append(PageBreak())

    # =========================================================================
    # SECTION 3: DESIGN AND ANALYSIS (FORMAL BLACK & WHITE DIAGRAMS)
    # =========================================================================
    story.append(Paragraph("3. Design and Analysis", style_h1))
    story.append(Paragraph("3.1 System Architecture", style_h2))
    story.append(Paragraph(
        "The system follows a layered architecture consisting of the Streamlit presentation layer, FastAPI backend, "
        "SQLite database, machine-learning analytics layer, and Judge0 code-evaluation service.",
        style_body
    ))

    # Figure 3.1
    fig3_1_path = os.path.abspath("docs/diagrams/fig3_1_architecture.png")
    if os.path.exists(fig3_1_path):
        story.append(KeepTogether([
            RLImage(fig3_1_path, width=480, height=300),
            Paragraph("Figure 3.1: High-Level System Architecture", style_caption)
        ]))

    story.append(Spacer(1, 6))
    story.append(Paragraph("Database Design", style_h3))
    story.append(Paragraph(
        "The database consists of normalized relational entities for users, students, faculty, courses, academic records, "
        "attendance, assignments, submissions, and risk predictions. Foreign-key relationships maintain data integrity.",
        style_body
    ))

    # Figure 3.2
    fig3_2_path = os.path.abspath("docs/diagrams/fig3_2_erd.png")
    if os.path.exists(fig3_2_path):
        story.append(KeepTogether([
            RLImage(fig3_2_path, width=480, height=320),
            Paragraph("Figure 3.2: Entity Relationship Diagram", style_caption)
        ]))

    story.append(PageBreak())

    # 3.2 Detailed Design Diagram
    story.append(Paragraph("3.2 Detailed Design Diagram", style_h2))
    story.append(Paragraph("Use Case Diagram", style_h3))
    story.append(Paragraph(
        "The primary actors are HOD, Faculty, and Student. Their interactions cover authentication, academic-data "
        "management, performance analysis, coding-assignment management, and academic-risk viewing.",
        style_body
    ))

    # Figure 3.3
    fig3_3_path = os.path.abspath("docs/diagrams/fig3_3_usecase.png")
    if os.path.exists(fig3_3_path):
        story.append(KeepTogether([
            RLImage(fig3_3_path, width=480, height=320),
            Paragraph("Figure 3.3: Use Case Diagram", style_caption)
        ]))

    story.append(PageBreak())

    # Data Flow Diagrams
    story.append(Paragraph("Data Flow Diagrams", style_h3))
    fig3_4_path = os.path.abspath("docs/diagrams/fig3_4_context.png")
    if os.path.exists(fig3_4_path):
        story.append(KeepTogether([
            RLImage(fig3_4_path, width=480, height=260),
            Paragraph("Figure 3.4: Context Diagram", style_caption)
        ]))

    story.append(Spacer(1, 8))
    fig3_5_path = os.path.abspath("docs/diagrams/fig3_5_dfd0.png")
    if os.path.exists(fig3_5_path):
        story.append(KeepTogether([
            RLImage(fig3_5_path, width=480, height=300),
            Paragraph("Figure 3.5: Level 0 Data Flow Diagram", style_caption)
        ]))

    story.append(PageBreak())

    # Figure 3.6: Level 1 DFD
    fig3_6_path = os.path.abspath("docs/diagrams/fig3_6_dfd1.png")
    if os.path.exists(fig3_6_path):
        story.append(KeepTogether([
            RLImage(fig3_6_path, width=480, height=280),
            Paragraph("Figure 3.6: Level 1 DFD - Academic Analytics and Risk Prediction", style_caption)
        ]))

    story.append(Spacer(1, 6))
    story.append(Paragraph("Class Diagram", style_h3))
    fig3_7_path = os.path.abspath("docs/diagrams/fig3_7_class.png")
    if os.path.exists(fig3_7_path):
        story.append(KeepTogether([
            RLImage(fig3_7_path, width=480, height=320),
            Paragraph("Figure 3.7: Class Diagram", style_caption)
        ]))

    story.append(PageBreak())

    # Sequence Diagram
    story.append(Paragraph("Sequence Diagram", style_h3))
    story.append(Paragraph(
        "The sequence below illustrates the coding-assignment workflow from faculty assignment creation through "
        "student submission, Judge0 execution, result storage, and leaderboard display.",
        style_body
    ))

    fig3_8_path = os.path.abspath("docs/diagrams/fig3_8_sequence.png")
    if os.path.exists(fig3_8_path):
        story.append(KeepTogether([
            RLImage(fig3_8_path, width=480, height=300),
            Paragraph("Figure 3.8: Sequence Diagram - Coding Assignment Evaluation", style_caption)
        ]))

    story.append(Spacer(1, 8))
    story.append(Paragraph("3.3 Design Tools and Limitations", style_h2))
    story.append(Paragraph(
        "Draw.io may be used to create ER diagrams, use-case diagrams, DFDs, class diagrams, sequence diagrams, and "
        "architecture diagrams. Diagram export and manual insertion into the final document can be time-consuming, "
        "especially for complex diagrams.",
        style_body
    ))
    story.append(PageBreak())

    # =========================================================================
    # SECTION 4: IMPLEMENTATION
    # =========================================================================
    story.append(Paragraph("4. Implementation", style_h1))
    story.append(Paragraph("4.1 Technology Stack Justification", style_h2))
    
    story.append(Paragraph("<b>Frontend / Dashboard</b>", style_body))
    story.append(Paragraph("Streamlit is selected for a Python-based interactive dashboard suitable for academic charts and reports.", style_body))

    story.append(Paragraph("<b>Backend</b>", style_body))
    story.append(Paragraph("FastAPI provides the secure API and business-logic layer.", style_body))

    story.append(Paragraph("<b>Database</b>", style_body))
    story.append(Paragraph("SQLite is appropriate for the initial class-scale prototype; MySQL/PostgreSQL can be used for future scale-up.", style_body))

    story.append(Paragraph("<b>Authentication</b>", style_body))
    story.append(Paragraph("JWT tokens and bcrypt hashing provide authenticated and role-based access.", style_body))

    story.append(Paragraph("<b>Machine Learning</b>", style_body))
    story.append(Paragraph("Pandas and NumPy support data processing while scikit-learn supports academic-risk classification.", style_body))

    story.append(Paragraph("<b>Coding Judge</b>", style_body))
    story.append(Paragraph("Judge0 provides automated execution and test-case evaluation.", style_body))

    story.append(Paragraph("<b>Development / Version Control</b>", style_body))
    story.append(Paragraph("VS Code and Git support development, testing, debugging, and version tracking.", style_body))

    story.append(Spacer(1, 6))
    story.append(Paragraph("4.2 Interface Design", style_h2))
    story.append(Paragraph(
        "The interface is designed as a web-based dashboard with separate views for HOD, Faculty, and Student users. "
        "It uses clearly labelled charts and academic indicators.",
        style_body
    ))

    # Figure 4.1
    fig4_1_path = os.path.abspath("docs/diagrams/fig4_1_mockup.png")
    if os.path.exists(fig4_1_path):
        story.append(KeepTogether([
            RLImage(fig4_1_path, width=480, height=300),
            Paragraph("Figure 4.1: Dashboard Interface Mockup", style_caption)
        ]))

    story.append(Spacer(1, 6))
    story.append(Paragraph("4.3 Implementation Status", style_h2))
    status_data = [
        [Paragraph("Requirement", style_th), Paragraph("Feature", style_th), Paragraph("Status", style_th)],
        [Paragraph("FR-001", style_td), Paragraph("User Authentication", style_td), Paragraph("In Progress / Being Implemented", style_td)],
        [Paragraph("FR-002", style_td), Paragraph("Academic Data Management", style_td), Paragraph("In Progress / Being Implemented", style_td)],
        [Paragraph("FR-003", style_td), Paragraph("Attendance Management", style_td), Paragraph("In Progress / Being Implemented", style_td)],
        [Paragraph("FR-004", style_td), Paragraph("Student Academic Dashboard", style_td), Paragraph("In Progress / Being Implemented", style_td)],
        [Paragraph("FR-005", style_td), Paragraph("Academic Risk Prediction", style_td), Paragraph("In Progress / Being Implemented", style_td)],
        [Paragraph("FR-006", style_td), Paragraph("Coding Assignment Creation", style_td), Paragraph("In Progress / Being Implemented", style_td)],
        [Paragraph("FR-007", style_td), Paragraph("Automated Code Evaluation", style_td), Paragraph("In Progress / Being Implemented", style_td)],
        [Paragraph("FR-008", style_td), Paragraph("Coding Leaderboard", style_td), Paragraph("In Progress / Being Implemented", style_td)],
        [Paragraph("FR-009", style_td), Paragraph("HOD Performance Reporting", style_td), Paragraph("In Progress / Being Implemented", style_td)],
    ]
    status_table = Table(status_data, colWidths=[90, 210, 204])
    status_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#EAEAEA")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#000000")),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(status_table)
    story.append(PageBreak())

    # =========================================================================
    # SECTION 5: PRELIMINARY RESULTS AND METRICS
    # =========================================================================
    story.append(Paragraph("5. Preliminary Results and Performance Metrics", style_h1))
    story.append(Paragraph("• Dashboard update target: approximately 15 seconds for newly entered marks or submissions.", style_bullet))
    story.append(Paragraph("• Database integrity: foreign keys and relational constraints shall maintain consistent academic records.", style_bullet))
    story.append(Paragraph("• Risk prediction: students shall be classified into Low, Medium, or High risk.", style_bullet))
    story.append(Paragraph("• Coding evaluation: submissions shall be evaluated against defined test cases through Judge0.", style_bullet))
    story.append(Paragraph("• Usability: charts shall be clearly labelled and understandable without specialized technical training.", style_bullet))
    story.append(Spacer(1, 10))

    # =========================================================================
    # SECTION 6: SCOPE
    # =========================================================================
    story.append(Paragraph("6. Scope", style_h1))
    story.append(Paragraph("<b>Included</b>", style_h2))
    story.append(Paragraph("• Coverage limited to the Department of Computer Science.", style_bullet))
    story.append(Paragraph("• Role-based login for HOD, Faculty, and Students.", style_bullet))
    story.append(Paragraph("• Semester 1 and Semester 2 marks and attendance tracking.", style_bullet))
    story.append(Paragraph("• Machine-learning-based academic risk prediction.", style_bullet))
    story.append(Paragraph("• Coding-assignment submission, automated evaluation, and leaderboard.", style_bullet))
    story.append(Paragraph("• Near real-time performance dashboard.", style_bullet))
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>Not Included</b>", style_h2))
    story.append(Paragraph("• Comparison across multiple departments.", style_bullet))
    story.append(Paragraph("• Integration with the official university ERP or examination system.", style_bullet))
    story.append(Paragraph("• Financial, fee, or accounts management.", style_bullet))
    story.append(Paragraph("• Native mobile application.", style_bullet))
    story.append(Paragraph("• Large-scale plagiarism detection.", style_bullet))
    story.append(Spacer(1, 10))

    # =========================================================================
    # SECTION 7: FEASIBILITY STUDY
    # =========================================================================
    story.append(Paragraph("7. Feasibility Study", style_h1))
    story.append(Paragraph("<b>Technical Feasibility</b>", style_h2))
    story.append(Paragraph(
        "The system uses freely available, well-documented technologies including Python, FastAPI, SQLite, scikit-learn, "
        "Streamlit, Pandas, NumPy, and Judge0 API. These can operate on a standard development laptop without specialized hardware.",
        style_body
    ))
    story.append(Paragraph("<b>Operational Feasibility</b>", style_h2))
    story.append(Paragraph(
        "Faculty and students are familiar with web-based forms and dashboards. Semester 1 and Semester 2 data is being "
        "collected through a Google Form already used by the class.",
        style_body
    ))
    story.append(Paragraph("<b>Economic / Resource Feasibility</b>", style_h2))
    story.append(Paragraph(
        "The core components are free and open source. The only potential cost is exceeding the free tier of the coding-judge "
        "API, which is not required for a semester-scale demonstration.",
        style_body
    ))
    story.append(PageBreak())

    # =========================================================================
    # SECTION 8: PRELIMINARY DEVELOPMENT PLAN
    # =========================================================================
    story.append(Paragraph("8. Preliminary Development Plan", style_h1))
    plan_data = [
        [Paragraph("Phase", style_th), Paragraph("Activity", style_th)],
        [Paragraph("1", style_td), Paragraph("Problem identification and data collection", style_td)],
        [Paragraph("2", style_td), Paragraph("Requirements analysis", style_td)],
        [Paragraph("3", style_td), Paragraph("System design and architecture", style_td)],
        [Paragraph("4", style_td), Paragraph("Database design and implementation", style_td)],
        [Paragraph("5", style_td), Paragraph("Backend and authentication implementation", style_td)],
        [Paragraph("6", style_td), Paragraph("Machine-learning model development and training", style_td)],
        [Paragraph("7", style_td), Paragraph("Coding-assignment module integration", style_td)],
        [Paragraph("8", style_td), Paragraph("Dashboard development", style_td)],
        [Paragraph("9", style_td), Paragraph("Testing", style_td)],
        [Paragraph("10", style_td), Paragraph("Documentation and presentation", style_td)]
    ]
    plan_table = Table(plan_data, colWidths=[60, 444])
    plan_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#EAEAEA")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#000000")),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(plan_table)
    story.append(Spacer(1, 10))

    # =========================================================================
    # SECTION 9: EXPECTED OUTCOME
    # =========================================================================
    story.append(Paragraph("9. Expected Outcome", style_h1))
    story.append(Paragraph(
        "A working prototype, scoped to a single Computer Science class, that demonstrates centralized academic data "
        "storage, secure role-based access, machine-learning-based early identification of at-risk students, and automated "
        "evaluation of coding assignments through a live, near real-time dashboard.",
        style_body
    ))
    story.append(Spacer(1, 10))

    # =========================================================================
    # SECTION 10: REFERENCES
    # =========================================================================
    story.append(Paragraph("10. References", style_h1))
    refs = [
        "[1] R. S. Pressman and B. R. Maxim, Software Engineering: A Practitioner’s Approach, 9th ed., McGraw-Hill Education, 2019.",
        "[2] FastAPI, \"FastAPI documentation,\" 2026.",
        "[3] Streamlit Inc., \"Streamlit documentation,\" 2026.",
        "[4] scikit-learn developers, \"scikit-learn: Machine learning in Python,\" 2026.",
        "[5] SQLAlchemy, \"SQLAlchemy documentation,\" 2026.",
        "[6] Judge0, \"Judge0 CE API documentation,\" 2026."
    ]
    for r in refs:
        story.append(Paragraph(r, style_body))

    # Build PDF
    doc.build(story, canvasmaker=NumberedCanvas)
    print("Formal B&W PDF generated successfully:", pdf_filename)
    return pdf_filename

if __name__ == "__main__":
    build_srs_pdf()
