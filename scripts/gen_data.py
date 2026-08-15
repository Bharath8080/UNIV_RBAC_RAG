"""
scripts/gen_data.py

Generates 12 authentic, high-density, text-focused, multi-page (solidly 5-7 pages each)
PDF documents for a FERPA-compliant University Campus RBAC RAG system.

All numerical marks, student fee ledgers, and grade tables are eliminated in favor of
rich qualitative prose, case studies, policy frameworks, curriculum syllabi, advisory memos,
and administrative governance texts. Numerical tabular data is managed via CSV / SQL agents.

Document Tiers (data/<tier>/):
  public/   -> campus_policies_2025.pdf, academic_calendar_2025.pdf, course_catalog.pdf
  faculty/  -> exam_answer_keys_cs301.pdf, grading_rubric_2025.pdf, cs_lesson_plan.pdf
  advisor/  -> student_academic_advising.pdf, academic_standing_interventions.pdf,
               financial_aid_and_scholarships.pdf
  dean/     -> faculty_tenure_review.pdf, department_strategic_plan.pdf,
               disciplinary_hearings.pdf
"""

import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
    PageBreak,
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

TIER_KEYWORDS = {
    "public":  "access-tier:public",
    "faculty": "access-tier:faculty",
    "advisor": "access-tier:advisor",
    "dean":    "access-tier:dean",
}


# ---------------------------------------------------------------------------
# Styles
# ---------------------------------------------------------------------------
def get_custom_styles():
    styles = getSampleStyleSheet()
    doc_title = ParagraphStyle(
        "DocTitle", parent=styles["Title"], fontName="Helvetica-Bold",
        fontSize=13.0, leading=16.5, textColor=colors.HexColor("#0F172A"),
        alignment=0, spaceAfter=3)
    doc_sub = ParagraphStyle(
        "DocSubtitle", parent=styles["Normal"], fontName="Helvetica",
        fontSize=8.5, leading=11.5, textColor=colors.HexColor("#475569"), spaceAfter=5)
    h1 = ParagraphStyle(
        "SectionH1", parent=styles["Heading1"], fontName="Helvetica-Bold",
        fontSize=9.5, leading=12.5, textColor=colors.HexColor("#1E3A8A"),
        spaceBefore=8, spaceAfter=3, keepWithNext=True)
    h2 = ParagraphStyle(
        "SectionH2", parent=styles["Heading2"], fontName="Helvetica-Bold",
        fontSize=8.6, leading=11.6, textColor=colors.HexColor("#334155"),
        spaceBefore=5, spaceAfter=2.5, keepWithNext=True)
    body = ParagraphStyle(
        "DocBody", parent=styles["BodyText"], fontName="Helvetica",
        fontSize=8.2, leading=12.0, textColor=colors.HexColor("#1E293B"), spaceAfter=5)
    bullet = ParagraphStyle(
        "DocBullet", parent=body, leftIndent=12, spaceAfter=3)
    callout = ParagraphStyle(
        "CalloutText", parent=styles["Normal"], fontName="Helvetica",
        fontSize=8.0, leading=11.2, textColor=colors.HexColor("#1E293B"))
    return {"title": doc_title, "subtitle": doc_sub, "h1": h1, "h2": h2,
            "body": body, "bullet": bullet, "callout": callout}


def make_callout(text, styles, bg_color="#F1F5F9", border_color="#CBD5E1"):
    t = Table([[Paragraph(text, styles["callout"])]], colWidths=[7.0 * inch])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor(bg_color)),
        ("BOX",        (0, 0), (-1, -1), 0.5, colors.HexColor(border_color)),
        ("PADDING",    (0, 0), (-1, -1), 6),
        ("VALIGN",     (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return t


def build_pdf(filepath, title, subtitle, story_content, tier):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    doc = SimpleDocTemplate(
        filepath, pagesize=letter,
        rightMargin=0.72 * inch, leftMargin=0.72 * inch,
        topMargin=0.72 * inch, bottomMargin=0.72 * inch,
        title=title,
        author="Northgate Institute of Technology and Higher Learning",
        subject=f"Official Institutional Documentation | {TIER_KEYWORDS[tier]}",
        keywords=[TIER_KEYWORDS[tier], "university", "academic-record", "governance"],
    )
    st = get_custom_styles()
    story = [
        Paragraph(title, st["title"]),
        Paragraph(subtitle, st["subtitle"]),
        HRFlowable(width="100%", thickness=1.4, color=colors.HexColor("#1E3A8A"), spaceAfter=6),
    ]
    story.extend(story_content)
    doc.build(story)
    pages = getattr(doc, "page", "?")
    print(f"  Generated [{tier}] ({pages} pages): {os.path.basename(filepath)}")


# =============================================================================
# 1. PUBLIC — campus_policies_2025.pdf
# =============================================================================
def generate_campus_policies():
    st = get_custom_styles()
    s = []

    # ── Section 1 ──────────────────────────────────────────────────────────
    s.append(Paragraph("1. Institutional Charter, Legal Basis & Scope of Governance", st["h1"]))
    s.append(Paragraph(
        "Northgate Institute of Technology ('the University') is an autonomous institution of higher learning "
        "committed to advanced engineering education, scientific inquiry, technological innovation, and "
        "ethical leadership. Founded in 1982 under state government ordinance and subsequently granted "
        "autonomous status by the University Grants Commission (UGC) in 1999, the University has grown "
        "into one of South Asia's premier technical institutions with an enrollment exceeding 12,000 "
        "undergraduate, postgraduate, and doctoral scholars across four residential campuses.", st["body"]))
    s.append(Paragraph(
        "This Campus Policies and Academic Regulations Handbook is enacted under the statutory authority of "
        "the Board of Governors and the University Academic Senate to establish uniform standards of "
        "scholarship, community welfare, civic responsibility, and institutional governance across all "
        "academic faculties, research centers, specialized laboratories, and residential facilities. The "
        "provisions herein are updated annually by the Office of the Registrar in consultation with the "
        "Dean of Academic Affairs, the Dean of Student Welfare, and the Faculty Senate. All amendments "
        "require a two-thirds majority vote of the Academic Senate and formal ratification by the "
        "President of the University before they take effect in any subsequent semester.", st["body"]))
    s.append(Paragraph(
        "All academic policies, administrative rules, and disciplinary procedures contained herein comply "
        "with applicable national regulations, including UGC guidelines, All India Council for Technical "
        "Education (AICTE) norms, the Rights of Persons with Disabilities Act 2016, the Prevention of "
        "Sexual Harassment (POSH) at Workplace Act 2013, and statutory data-confidentiality standards "
        "functionally equivalent to the US Family Educational Rights and Privacy Act (FERPA). The "
        "governance structure operates through a bicameral framework: the Board of Governors (responsible "
        "for fiduciary oversight, capital planning, and executive leadership) and the Academic Senate "
        "(responsible for curricular standards, degree requirements, faculty appointments, and ethics).", st["body"]))

    # ── Section 2 ──────────────────────────────────────────────────────────
    s.append(Paragraph("2. Comprehensive Code of Academic Integrity & Honor Pledge", st["h1"]))
    s.append(Paragraph(
        "Academic honesty is the foundational pillar of all scholarly pursuits at Northgate Institute. "
        "Every student, upon matriculation, signs and accepts the University Honor Pledge: 'I pledge on my "
        "honor that I have neither given nor received unauthorized aid in this academic work, that all "
        "sources and intellectual contributions have been truthfully acknowledged, and that I uphold the "
        "highest ethical standards in all assignments, examinations, laboratory experiments, and research "
        "activities.' Violations are adjudicated by the Departmental Academic Integrity Committee (DAIC) "
        "and the Central Disciplinary Board (CDB).", st["body"]))
    s.append(Paragraph(
        "The University's academic integrity framework is grounded in the UGC (Promotion of Academic "
        "Integrity and Prevention of Plagiarism in Higher Educational Institutions) Regulations, 2018, "
        "supplemented by the AICTE task-force advisory on AI disclosure (2024). Core prohibited practices "
        "and their prescribed institutional responses include:", st["body"]))
    s.append(Paragraph(
        "• <b>Plagiarism and Verbatim Copying:</b> Submitting source code, technical reports, homework "
        "assignments, or research papers without explicit attribution constitutes plagiarism. The "
        "University employs automated similarity engines (MOSS, JPlag, Turnitin with AI-detection). A "
        "non-attributable similarity index exceeding 25% in non-boilerplate logic triggers mandatory DAIC "
        "review. UGC tier thresholds apply: 10-40% similarity requires revision and resubmission within "
        "6 months; 40-60% bars resubmission for one academic year; above 60% may result in cancellation "
        "of registration. Faculty assigning coursework must run all submissions through the university's "
        "designated detection portal within 5 days of the submission deadline.", st["bullet"]))
    s.append(Paragraph(
        "• <b>Generative AI & LLM Usage Policy (Effective August 2025):</b> Utilizing large language "
        "models (LLMs) or generative AI tools (ChatGPT, GitHub Copilot, Claude, Gemini, etc.) for graded "
        "coursework is strictly prohibited unless the course instructor explicitly authorizes specific use "
        "in the published course syllabus. When authorized, students must provide an 'AI Usage Appendix' "
        "detailing all prompts submitted, tool model and version, output used, and the substantive "
        "intellectual modifications made by the student. Core theses, original data interpretation, "
        "algorithms designed by the student, and laboratory experiment analysis must be entirely the "
        "student's own intellectual work regardless of LLM authorization. AI-generated content flagged "
        "above 20% by AI-detection tools triggers mandatory review under Clause 5.7 of the Disciplinary "
        "Matrix.", st["bullet"]))
    s.append(Paragraph(
        "• <b>Unauthorized Collaboration & Repository Sharing:</b> Sharing private code repositories, "
        "laboratory solution files, assignment source, or exam prompts with current or future cohort "
        "students constitutes a Level 2 integrity violation. Public posting of assignment solutions on "
        "platforms such as GitHub, Chegg, or Stack Overflow within the same academic year of the "
        "assignment's validity is treated equivalently.", st["bullet"]))
    s.append(Paragraph(
        "• <b>Examination Malpractice & Identity Fraud:</b> Bringing unauthorized notes, smart devices, "
        "wireless earphones, or other communication apparatus into examination halls, or facilitating "
        "another student's impersonation in any form of assessment, leads to immediate course "
        "cancellation (all units), one-semester suspension, and a permanent conduct notation on the "
        "official transcript.", st["bullet"]))
    s.append(Paragraph(
        "• <b>Digital Infrastructure Integrity:</b> Unauthorized port scanning, SQL-injection probing, "
        "denial-of-service attempts, man-in-the-middle packet sniffing, or keystroke-logging against "
        "university servers, faculty portals, examination systems, or research databases constitutes a "
        "Level 3 violation carrying permanent IT access revocation, immediate academic suspension, and "
        "mandatory criminal referral to law enforcement under the Information Technology (Amendment) Act "
        "2008 and Indian Penal Code Section 66.", st["bullet"]))
    s.append(Paragraph(
        "• <b>Research Misconduct:</b> Fabricating experimental data, falsifying laboratory observations, "
        "misrepresenting statistical results, or engaging in salami-slicing of publications in funded "
        "research projects constitutes research misconduct under the University's Research Ethics Charter. "
        "All funded research activities must obtain prior clearance from the Institutional Research Ethics "
        "Committee (IREC) before data collection commences.", st["bullet"]))

    # ── Section 3 ──────────────────────────────────────────────────────────
    s.append(Paragraph("3. Attendance Regulations, Absence Verification & Medical Condonation", st["h1"]))
    s.append(Paragraph(
        "Regular class engagement and active laboratory participation are prerequisites for academic "
        "success. All undergraduate B.Tech and postgraduate M.Tech programmes mandate a minimum "
        "attendance of 75% in each registered theory course and 80% in each laboratory-practical course "
        "to qualify for the End-Semester Examination. These thresholds align with AICTE's minimum "
        "instructional contact norms (90 teaching days per 15-week semester). Condonation for attendance "
        "shortages in the 65%-74% bracket is permissible only for: (a) documented hospitalization "
        "confirmed by the University Chief Medical Officer; (b) verified institutional duty representation "
        "at national or international events; (c) participation in AICTE-recognized national competitive "
        "examinations (GATE, CAT, GRE). Condonation applications must be filed no later than 5 working "
        "days after the cause of absence ends. Students with attendance below 50% receive a mandatory "
        "'Detained' (DE) grade and must repeat the course in its entirety in the next available offering.", st["body"]))
    s.append(Paragraph(
        "Absence due to medical reasons requires certified documentation from the University Health Center "
        "Chief Medical Officer within 5 working days of resuming classes. Private medical certificates "
        "are subject to verification. For institutional duty — technical competitions, cultural fests, "
        "sports meets, academic conferences, or industry delegations — the sponsoring department must "
        "submit an Institutional Duty Leave notification to the Registrar at least 7 days prior to "
        "travel. Retroactive duty-leave applications are not accepted under any circumstances. Faculty "
        "instructors maintain real-time biometric and RFID-based attendance records through the Digital "
        "Course Management Portal (DCMP v3.0). Students receive automated SMS and email alerts when "
        "cumulative attendance falls below the 80% threshold, triggering mandatory advisor notification.", st["body"]))

    # ── Section 4 ──────────────────────────────────────────────────────────
    s.append(Paragraph("4. Academic Grievance & Multi-Stage Grade Appeal Procedures", st["h1"]))
    s.append(Paragraph(
        "Students who believe their final course grade was calculated incorrectly, applied without "
        "reference to the published rubric, or awarded through demonstrable procedural bias may seek "
        "formal redress through the University's three-stage appeal mechanism:", st["body"]))
    s.append(Paragraph(
        "• <b>Stage 1 — Informal Faculty Review (Deadline: 5 Working Days Post Grade Publication):</b> "
        "The student requests a direct consultation with the Course Instructor of Record, presenting "
        "specific written documentation of the alleged error or inconsistency. The instructor must "
        "respond in writing within 3 working days.", st["bullet"]))
    s.append(Paragraph(
        "• <b>Stage 2 — Departmental Review Committee (Deadline: 10 Working Days Post Stage 1 Response):</b> "
        "A formal written petition is submitted to the Head of Department, who appoints a three-member "
        "Faculty Review Committee that inspects all graded materials, verifies computation against the "
        "rubric, and issues a binding written determination within 7 working days.", st["bullet"]))
    s.append(Paragraph(
        "• <b>Stage 3 — Standing Academic Appeals Board (Final; Deadline: 15 Working Days Post Stage 2):</b> "
        "Final institutional appeal adjudicated by a five-member board comprising the Dean of Academic "
        "Affairs (chair), Controller of Examinations, and three senior faculty members. The board "
        "reviews all prior documentation and may request oral presentations. Its decision is final, "
        "binding on all parties, and cannot be further appealed within institutional channels.", st["bullet"]))
    s.append(Paragraph(
        "Critical note: Mere disagreement with an instructor's exercise of academic judgment on "
        "subjective creative or analytical questions does not constitute valid grounds for Stage 3 "
        "adjudication. The appellant bears the burden of proving procedural error, computational "
        "mistake, or verifiable rubric non-compliance.", st["body"]))

    # ── Section 5 ──────────────────────────────────────────────────────────
    s.append(Paragraph("5. Anti-Ragging Directives, Zero Tolerance Policy & Statutory Campus Safety", st["h1"]))
    s.append(Paragraph(
        "Northgate Institute enforces an absolute Zero Tolerance Policy toward ragging. In compliance "
        "with the Hon'ble Supreme Court of India's directives in SLP (C) No. 24295/2006 and UGC "
        "(Prevention, Prohibition and Punishment of Ragging in Higher Educational Institutions) "
        "Regulations 2009, ragging is a cognizable criminal offense under Sections 339, 340, 341, 342, "
        "and 506 of the Indian Penal Code. Any student engaging in physical abuse, verbal harassment, "
        "emotional coercion, cyber-bullying, or forced participation in degrading acts against fellow "
        "scholars faces: (a) immediate suspension from all academic activities; (b) expulsion from "
        "residential hostels; (c) forfeiture of all scholarships and financial aid; (d) mandatory filing "
        "of an FIR with local police. The 24/7 Anti-Ragging Squad conducts surprise inspections across "
        "all hostel blocks, common areas, canteens, and transport vehicles.", st["body"]))
    s.append(Paragraph(
        "Every incoming student and their parent/guardian must complete mandatory online anti-ragging "
        "affidavits via the national UGC anti-ragging web portal (www.antiragging.in) as a prerequisite "
        "for hostel allotment and library access activation. Confidential complaints may be lodged via "
        "the Anti-Ragging Toll-Free Helpline (1800-180-5522), through anonymous physical dropboxes in "
        "all hostel common rooms, or electronically via the encrypted University Grievance Portal "
        "(accessible 24/7 with anonymous filing options).", st["body"]))

    # ── Section 6 ──────────────────────────────────────────────────────────
    s.append(Paragraph("6. Equal Opportunity Cell, POSH Compliance & Disability Accommodation", st["h1"]))
    s.append(Paragraph(
        "The University maintains an inclusive, non-discriminatory learning environment. The Internal "
        "Complaints Committee (ICC), constituted under the POSH Act 2013, investigates all grievances "
        "concerning gender-based harassment, sexual harassment, and hostile workplace conduct with "
        "absolute confidentiality. The ICC comprises the Presiding Officer (a senior woman faculty "
        "member), two faculty members committed to women's causes, two non-teaching staff members, and "
        "one external member from an NGO working on women's rights — satisfying statutory composition "
        "requirements. Written complaints must be acknowledged within 7 days and formal inquiry reports "
        "submitted within 30 days of filing. All parties are guaranteed procedural fairness, legal "
        "representation assistance, and protection from retaliation.", st["body"]))
    s.append(Paragraph(
        "The Equal Opportunity Cell (EOC) provides specialized accessibility accommodations for "
        "differently-abled scholars under the Rights of Persons with Disabilities Act 2016, including: "
        "assistive screen-reading software on all central computing workstations; wheelchair-accessible "
        "ramps and designated seating in all lecture theaters, laboratories, and examination halls; "
        "scribe and extra-time allowances (25% additional time) in all timed examinations; priority "
        "hostel room allocation on ground floors; and dedicated counseling from the EOC Student "
        "Accessibility Coordinator. Disability accommodations must be requested by the third week of "
        "each semester.", st["body"]))

    # ── Section 7 ──────────────────────────────────────────────────────────
    s.append(Paragraph("7. Hostel & Residential Life Regulations", st["h1"]))
    s.append(Paragraph(
        "Residential facilities include Sarojini Devi Hall (women, Blocks A–D, 840 rooms) and "
        "Vivekananda Hall (men, Blocks E–H, 960 rooms), accommodating approximately 3,600 resident "
        "scholars. Key conduct standards: (1) Mandatory biometric in-time is 09:30 PM weekdays and "
        "10:30 PM weekends and gazetted holidays; (2) Possession, consumption, or distribution of "
        "alcohol, tobacco products, narcotics, or NDPS-scheduled substances is strictly forbidden and "
        "triggers immediate expulsion from hostel with FIR; (3) Unauthorized high-wattage electrical "
        "appliances (>500 W — including induction cookers, electric irons, and hair straighteners) are "
        "banned due to fire risk; (4) Quiet hours are strictly enforced 11:00 PM–06:00 AM; (5) "
        "Visitors of the opposite gender are not permitted in residential rooms under any circumstances. "
        "Violations trigger progressive disciplinary action: first offense — written warning; second "
        "offense — residential probation; third offense — permanent hostel expulsion.", st["body"]))
    s.append(Paragraph(
        "Hostel rooms undergo periodic safety and maintenance inspections by the Chief Warden and "
        "resident advisors. Overnight leave requires submission through the Digital Hostel Management "
        "Portal a minimum of 24 hours in advance, with mandatory SMS confirmation from the parent or "
        "designated guardian. Weekend local leaves (within 50 km radius) require advisor endorsement. "
        "Outstation leaves exceeding 3 nights require written parental consent and Dean's approval.", st["body"]))

    # ── Section 8 ──────────────────────────────────────────────────────────
    s.append(Paragraph("8. Information Technology Acceptable Use Policy (IT-AUP 2025)", st["h1"]))
    s.append(Paragraph(
        "All computing resources, campus-wide Wi-Fi networks (8.4 Gbps aggregate capacity across 420 "
        "access points), licensed software platforms, cloud compute allocations, and research computing "
        "infrastructure are provided exclusively for academic, research, and authorized administrative "
        "purposes. Network credentials (LDAP accounts) are strictly non-transferable. Prohibited "
        "activities include: (a) hosting commercial servers or crypto-mining operations; (b) "
        "distributing copyrighted media, software, or proprietary research datasets without license "
        "authorization; (c) running any commercial business, e-commerce platform, or subscription "
        "service using university network bandwidth; (d) bypassing firewall configurations using "
        "unauthorized VPN tunneling or proxy services; (e) installing peer-to-peer software or "
        "BitTorrent clients on campus machines.", st["body"]))
    s.append(Paragraph(
        "The IT Services Division operates a Security Operations Center (SOC) that continuously "
        "monitors network traffic, authentication sessions, and endpoint security telemetry via a "
        "SIEM (Security Information and Event Management) platform. Anomalous traffic patterns "
        "automatically trigger account suspension pending investigation. First-time minor violations "
        "(bandwidth abuse, unauthorized streaming) receive a written warning. Serious violations "
        "involving hacking, social engineering, or data exfiltration result in immediate permanent "
        "account termination, asset seizure for forensic examination, academic suspension, and "
        "mandatory referral to the Cyber Crime Cell under IT Act 2000 Section 43 and Section 66.", st["body"]))

    # ── Section 9 ──────────────────────────────────────────────────────────
    s.append(Paragraph("9. Student Rights, Representation & Co-curricular Participation", st["h1"]))
    s.append(Paragraph(
        "All enrolled students hold the right to: transparent academic evaluation with timely written "
        "feedback on submitted coursework; access to certified course syllabi and learning outcome "
        "mappings; participation in recognized technical chapters (IEEE-CS Chapter, ACM Student "
        "Chapter, ISTE Chapter, Robotics & Autonomous Systems Club, Cybersecurity CTF Team); "
        "representation on the Departmental Student Advisory Committee (DSAC); and petition to any "
        "institutional authority without fear of academic retaliation. Students on active academic "
        "probation or subject to pending disciplinary investigations are disqualified from holding "
        "executive offices in student council or representing the University externally.", st["body"]))

    # ── Section 10 ──────────────────────────────────────────────────────────
    s.append(Paragraph("10. Library Access, Digital Repositories & Resource Governance", st["h1"]))
    s.append(Paragraph(
        "The Central University Library (Dr. APJ Abdul Kalam Knowledge Center) houses over 148,000 "
        "physical volumes, maintains IEEE Xplore, ACM Digital Library, ScienceDirect, Springer, and "
        "JSTOR institutional subscriptions, and operates a 24/7 digital reading room. Borrowing "
        "entitlements: B.Tech students — 4 volumes, 14-day loan; M.Tech and Ph.D. scholars — 8 "
        "volumes, 30-day loan; faculty — 15 volumes, 90-day loan. Reference-only materials (bound "
        "theses, reserve textbooks, rare manuscripts) may not leave the premises. Overdue penalties: "
        "Rs. 10 per volume per day (waived once per semester on formal application). Unreturned "
        "materials 30 days past due trigger a Library Hold that blocks pre-registration, transcript "
        "issuance, and graduation clearance until resolved.", st["body"]))

    # ── Section 11 ──────────────────────────────────────────────────────────
    s.append(Paragraph("11. Campus Placement, Internship Eligibility & Career Services", st["h1"]))
    s.append(Paragraph(
        "The Department of Training & Placement (T&P) facilitates on-campus and off-campus recruitment "
        "for graduating seniors and final-year postgraduate students. Eligibility for campus placement "
        "drives requires: (a) minimum CGPA of 6.50 on a 10-point scale; (b) zero active backlogs at "
        "the time of the specific drive; (c) clean disciplinary record with no pending CDB cases. "
        "The One-Offer Policy mandates that students accepting a Tier-1 offer (CTC > Rs. 15 Lakhs per "
        "annum) are excluded from subsequent drives to ensure equitable opportunity distribution. "
        "Dream offers (>Rs. 25 LPA) are governed by the Dream Company Policy requiring Head of "
        "Department written approval for reappearance in further drives. "
        "Mandatory 8-week summer internships must be completed between Semesters VI and VII at "
        "recognized industrial organizations or academic research labs. Students must submit completion "
        "certificates, project reports, and industry mentor evaluation forms to earn the 2 mandatory "
        "internship credits under the CBCS scheme.", st["body"]))

    # ── Section 12 ──────────────────────────────────────────────────────────
    s.append(Paragraph("12. Health Center, Mental Wellness & Medical Emergency Protocols", st["h1"]))
    s.append(Paragraph(
        "The University Health Center (UHC) operates 24 hours, 7 days a week, staffed by 4 resident "
        "physicians (including 1 psychiatrist and 1 orthopedic consultant), 12 nursing staff, and a "
        "dedicated campus ambulance with AED capability. All enrolled students are mandatorily covered "
        "under the University Student Health Insurance Scheme (hospitalization cover up to Rs. 3 "
        "Lakhs per annum). The Student Wellness Cell provides confidential psychological counseling, "
        "cognitive behavioral therapy sessions, stress management workshops, and crisis intervention "
        "through 6 certified clinical psychologists. Mental health services are strictly confidential; "
        "no academic or disciplinary consequences flow from voluntary self-referral.", st["body"]))

    # ── Section 13 ──────────────────────────────────────────────────────────
    s.append(Paragraph("13. Anti-Ragging Compliance, Drug Policy & Campus Safety Infrastructure", st["h1"]))
    s.append(Paragraph(
        "Beyond anti-ragging provisions, campus safety is maintained through: (a) installation of "
        "CCTV cameras across all academic buildings, hostel common areas, canteens, and parking zones; "
        "(b) a 24/7 Security Control Room with trained personnel monitoring all live feeds; (c) "
        "biometric access control at server rooms, research labs, and examination cell storage vaults; "
        "(d) random vehicle checks at campus entry gates by authorized security personnel. The Narcotics "
        "Control Bureau (NCB) liaison officer conducts periodic awareness workshops and surprise "
        "inspections in coordination with the campus administration.", st["body"]))

    # ── Section 14 ──────────────────────────────────────────────────────────
    s.append(Paragraph("14. Environmental Sustainability, Green Campus Initiatives & Transport", st["h1"]))
    s.append(Paragraph(
        "Northgate Institute holds a 4-Star Green Campus Certification from the Bureau of Energy "
        "Efficiency (BEE). Campus sustainability initiatives include: 2.4 MW solar power generation "
        "meeting 38% of campus energy requirements; a zero-liquid-discharge sewage treatment plant; "
        "14 electric shuttle buses serving inter-campus routes on 20-minute intervals; and a bicycle-"
        "sharing network of 320 cycles at 18 docking stations. Private petrol/diesel vehicles are "
        "restricted to outer perimeter Parking Zone B. Littering, improper e-waste disposal in non-"
        "designated bins, or damage to campus green spaces incurs mandatory community service of 10-40 "
        "hours assigned by the Green Campus Committee.", st["body"]))

    # ── Section 15 ──────────────────────────────────────────────────────────
    s.append(Paragraph("15. Student Innovation & Incubation Center (SIIC) Guidelines", st["h1"]))
    s.append(Paragraph(
        "The SIIC provides a structured pathway from idea to enterprise: Ideation Lab (co-working "
        "space, 60 seats), Prototype Studio (fabrication equipment, 3D printers, soldering stations), "
        "and the Scale-Up Incubator (dedicated office space for registered startups, 12 active tenants "
        "as of August 2025). Registered SIIC ventures receive: seed grants up to Rs. 5 Lakhs from "
        "the University Innovation Fund; patent filing assistance (university bears provisional filing "
        "costs up to Rs. 25,000); mentorship from the 40-member Industry Advisory Board; and access "
        "to the SIIC Alumni Investor Network (55 angel investors). Students with verified startup "
        "operations demonstrating monthly active users or revenue may petition the Academic Senate for "
        "a Startup Sabbatical of up to two semesters while retaining student status and hostel access.", st["body"]))

    # ── Section 16 ──────────────────────────────────────────────────────────
    s.append(Paragraph("16. National Education Policy (NEP) 2020 Implementation Framework", st["h1"]))
    s.append(Paragraph(
        "In alignment with the Government of India's National Education Policy 2020, Northgate "
        "Institute has implemented: (a) a multiple entry and exit framework allowing students to "
        "exit with a Certificate after Year 1, a Diploma after Year 2, a B.Tech after Year 3 (under "
        "the Academic Bank of Credits), or a full Honors/Research degree after Year 4; (b) "
        "Multidisciplinary Minor programmes enabling CSE students to earn a Minor in Data Science, "
        "Entrepreneurship, or Cognitive Science; (c) integration of Indian Knowledge Systems modules "
        "and Environmental Science into the mandatory humanities curriculum; (d) promotion of regional "
        "language instruction support for first-year students. The Academic Bank of Credits (ABC) "
        "account registration is mandatory for all enrolled students from AY 2025-2026.", st["body"]))

    # ── Section 17 ──────────────────────────────────────────────────────────
    s.append(Paragraph("17. Sports, Physical Fitness & Inter-Collegiate Competitions", st["h1"]))
    s.append(Paragraph(
        "The Sports & Physical Education Department manages facilities including 2 cricket grounds, "
        "4 basketball courts, 6 badminton courts, a 400-meter athletics track, a 25-meter swimming "
        "pool, and a fully equipped gymnasium. Physical Education (PE) courses of 1 credit each are "
        "compulsory in Semesters I and II. Students representing the University in inter-collegiate "
        "competitions recognized by the Association of Indian Universities (AIU) receive institutional "
        "duty leave and may apply for Sports Achievement Scholarships (up to Rs. 50,000 per annum for "
        "national and above level representatives).", st["body"]))

    # ── Section 18: FERPA ─────────────────────────────────────────────────
    s.append(Paragraph("18. Statutory Educational Records Privacy & Data Governance", st["h1"]))
    s.append(make_callout(
        "<b>Confidentiality of Educational Records Notice:</b> Under University Data Governance "
        "Regulations (aligned with UGC guidelines and FERPA equivalents), all student academic records — "
        "including semester grade ledgers, GPA transcripts, internal assessment sheets, fee payment "
        "balances, disciplinary dossiers, health records, and financial aid files — are classified as "
        "Confidential Educational Records. Access is restricted strictly to authorized university "
        "personnel with documented 'Legitimate Educational Interest'. Directory information (name, "
        "degree programme, branch, enrollment dates) may be published unless the student files a "
        "written Directory Information Opt-Out form with the Registrar by the second Friday of each "
        "semester. Violations of this policy by staff members constitute a disciplinary offense "
        "attracting service suspension and legal liability under applicable data-protection legislation.",
        st, bg_color="#EFF6FF", border_color="#93C5FD"))

    build_pdf(
        os.path.join(DATA_DIR, "public", "campus_policies_2025.pdf"),
        "Campus Policies & Academic Regulations Handbook 2025-2026",
        "Northgate Institute of Technology | Governance, Academic Integrity, Student Conduct & Privacy",
        s, "public")


# =============================================================================
# 2. PUBLIC — academic_calendar_2025.pdf
# =============================================================================
def generate_academic_calendar():
    st = get_custom_styles()
    s = []

    s.append(Paragraph("1. Academic Year 2025-2026: Structure & Institutional Framework", st["h1"]))
    s.append(Paragraph(
        "The Academic Year 2025-2026 at Northgate Institute of Technology is organized in accordance "
        "with AICTE's Approval Process Handbook 2024-27 and the University Academic Senate Resolution "
        "USR-2025-04. It comprises two standard 15-week instructional semesters — the Odd Semester "
        "(Monsoon Term: August 2025 to December 2025) and the Even Semester (Spring Term: January 2026 "
        "to May 2026) — followed by an intensive 6-week Summer / Supplementary Term (June 2026 to July "
        "2026). Each standard semester provides a minimum of 90 instructional contact days, satisfying "
        "UGC, AICTE, and Washington Accord (Tier-1 NBA) curricular mandates.", st["body"]))
    s.append(Paragraph(
        "The academic calendar is jointly approved by the Academic Senate and the Controller of "
        "Examinations and constitutes the official administrative schedule for all student registrations, "
        "continuous assessments, mid-semester evaluations, project reviews, practical examinations, "
        "reading days, supplementary examinations, and institutional convocations. Divergence from "
        "this calendar requires written authorization from the Dean of Academic Affairs and notification "
        "to the Registrar at least 48 hours in advance.", st["body"]))

    s.append(Paragraph("2. Monsoon Term (Odd Semester) 2025: Week-by-Week Operational Milestones", st["h1"]))
    s.append(Paragraph(
        "The Monsoon Term commences Monday, August 4, 2025. Detailed operational phases:", st["body"]))
    s.append(Paragraph(
        "• <b>Pre-Term: Orientation Week (July 28 – August 1, 2025):</b> First-year student "
        "induction programme, NEP 2020 Academic Bank of Credits (ABC) registration, hostel check-in, "
        "ID card issuance, biometric enrollment, and campus safety orientation.", st["bullet"]))
    s.append(Paragraph(
        "• <b>Week 1-2: Instruction Commencement & Add/Drop Window (Aug 4 – Aug 15, 2025):</b> "
        "Regular lectures, tutorials, and laboratory practicals begin. Course Add/Drop window "
        "closes Friday August 15 at 5:00 PM. No retroactive course additions after this deadline.", st["bullet"]))
    s.append(Paragraph(
        "• <b>Week 3-4: Enrollment Census & Roster Freezing (August 25, 2025):</b> Official "
        "enrollment rosters frozen for state-level AICTE reporting, Ministry of Education data "
        "submission, and government scholarship disbursements (NSP, PM-YASASVI).", st["bullet"]))
    s.append(Paragraph(
        "• <b>Week 6-7: Continuous Assessment Test I — CAT-1 (Sep 15 – Sep 20, 2025):</b> "
        "Centralized 90-minute theory assessments covering Units I and II. CAT-1 marks must be "
        "entered into DCMP within 7 days of test completion by course instructors.", st["bullet"]))
    s.append(Paragraph(
        "• <b>Week 9: Mid-Term Academic Deficiency Alert (October 4, 2025):</b> Course instructors "
        "issue formal mid-semester alert notifications through DCMP for students below 50% in CIE "
        "component or below 75% attendance. Alerts trigger mandatory advisor-student conferences.", st["bullet"]))
    s.append(Paragraph(
        "• <b>Week 10: National Technical Symposium — TechX 2025 (October 10-12, 2025):</b> Annual "
        "inter-university technical competition; instructional classes suspended for 3 days. "
        "Participants retain attendance credit under institutional duty leave provisions.", st["bullet"]))
    s.append(Paragraph(
        "• <b>Week 12-13: Continuous Assessment Test II — CAT-2 (Oct 27 – Oct 31, 2025):</b> "
        "Theory assessments covering Units III and IV. CAT-2 marks entry deadline: November 7.", st["bullet"]))
    s.append(Paragraph(
        "• <b>Week 14: Course Withdrawal Deadline (November 7, 2025):</b> Last date to formally "
        "withdraw from a registered course with a neutral 'W' notation on the official transcript. "
        "Tuition refund follows the 50% refund rule applicable after the 30-day census cutoff.", st["bullet"]))
    s.append(Paragraph(
        "• <b>Week 14-15: Mini-Project & Seminar Internal Reviews (November 10-14, 2025):</b> "
        "Semester V Mini-Project progress reviews and Seminar presentations evaluated by faculty panels.", st["bullet"]))
    s.append(Paragraph(
        "• <b>Week 15: End-of-Instruction Day (November 28, 2025):</b> Last day of formal classroom "
        "instruction. All continuous internal assessment (CIA) component marks frozen in DCMP at "
        "11:59 PM. Post-freeze modifications require signed order from the Department Academic Committee.", st["bullet"]))
    s.append(Paragraph(
        "• <b>Practical Examinations (November 17 – November 22, 2025):</b> Laboratory practicals, "
        "coding evaluations, and embedded systems demonstrations conducted with external examiners.", st["bullet"]))
    s.append(Paragraph(
        "• <b>Reading Days (November 29 – December 3, 2025):</b> Five mandatory study days. No "
        "supplementary lectures, assignment submissions, or quiz assessments may be scheduled.", st["bullet"]))
    s.append(Paragraph(
        "• <b>End-Semester Theory Examinations (December 4 – December 18, 2025):</b> Centralized "
        "3-hour comprehensive examinations across all slots. Hall tickets issued via SIS portal "
        "5 days in advance. Students with unresolved Bursar Holds or Library Holds are ineligible "
        "to appear until holds are cleared through the respective offices.", st["bullet"]))
    s.append(Paragraph(
        "• <b>Supplementary Answer Sheet Review (December 20-22, 2025):</b> Evaluated answer sheets "
        "made available for optional student review subject to Rs. 200 administrative fee per script.", st["bullet"]))
    s.append(Paragraph(
        "• <b>Result Publication (January 9, 2026):</b> Official grade cards published on the "
        "Student Information System (SIS) portal. Grade cards with institutional seal issued from "
        "the Registrar's counter from January 12, 2026.", st["bullet"]))

    s.append(Paragraph("3. Spring Term (Even Semester) 2026: Comprehensive Operational Timeline", st["h1"]))
    s.append(Paragraph(
        "The Spring Term commences Monday, January 12, 2026:", st["body"]))
    s.append(Paragraph(
        "• <b>Pre-Registration & Fee Clearance (January 5 – January 9, 2026):</b> Online course "
        "selection through SIS portal. Students with active Bursar Holds are automatically locked "
        "from course pre-registration pending fee resolution.", st["bullet"]))
    s.append(Paragraph(
        "• <b>Instruction Begins (January 12, 2026):</b> Opening of Spring lectures, tutorials, and "
        "laboratory sessions. First tutorial of each course should establish course policy, grading "
        "breakdown, and assessment calendar consistent with this institutional schedule.", st["bullet"]))
    s.append(Paragraph(
        "• <b>Add/Drop Closes (January 23, 2026):</b> Final adjustments to Spring course tracks.", st["bullet"]))
    s.append(Paragraph(
        "• <b>CAT-1 (February 23 – February 28, 2026):</b> Mid-term assessment covering Units I & II.", st["bullet"]))
    s.append(Paragraph(
        "• <b>Cultural & Literary Fest — Vibrance 2026 (March 12–15, 2026):</b> Four-day "
        "inter-university cultural event; classes suspended for duration.", st["bullet"]))
    s.append(Paragraph(
        "• <b>CAT-2 (April 6 – April 11, 2026):</b> Assessment covering Units III and IV.", st["bullet"]))
    s.append(Paragraph(
        "• <b>Senior Capstone (B.Tech Major Project) Final Submission (April 24, 2026):</b> Bound "
        "dissertations and software submissions to the Departmental Project Committee.", st["bullet"]))
    s.append(Paragraph(
        "• <b>Practical Exams & Capstone Viva Voce (April 27 – May 2, 2026):</b> External examiner-"
        "evaluated lab practicals and capstone oral defenses.", st["bullet"]))
    s.append(Paragraph(
        "• <b>End-Semester Theory Examinations (May 6 – May 20, 2026):</b> Final theory papers.", st["bullet"]))
    s.append(Paragraph(
        "• <b>Spring Results (June 3, 2026):</b> Final grades and graduation eligibility clearance "
        "lists published. Students failing to achieve minimum CGPA of 5.00 are referred to the "
        "Academic Standing Board for mandatory counseling and pathway determination.", st["bullet"]))
    s.append(Paragraph(
        "• <b>Annual Convocation (June 6, 2026):</b> Formal conferral of B.Tech, M.Tech, MBA, and "
        "Ph.D. degrees. Chief Guest: nominated by the Board of Governors. Dress code: formal "
        "academic gown as prescribed by the University Registrar's circular.", st["bullet"]))

    s.append(Paragraph("4. Summer / Supplementary Term 2026", st["h1"]))
    s.append(Paragraph(
        "The Summer / Supplementary Term runs June 8, 2026 – July 18, 2026 (6 intensive weeks). "
        "Students carrying backlog theory courses may register for a maximum of 2 courses (8 credits "
        "maximum). Summer classes meet daily for 3-hour sessions to satisfy 45-lecture contact norms. "
        "Summer examination dates: July 20–24, 2026. Tuition: Rs. 4,500 per credit on a per-credit "
        "billing basis. Registration requires written clearance from the faculty advisor and a "
        "confirmed academic standing report from the Registrar.", st["body"]))

    s.append(Paragraph("5. Continuous Assessment Mark Freezing, Moderation & Audit", st["h1"]))
    s.append(Paragraph(
        "Continuous Internal Assessment (CIA) marks represent 50% of the total course grade. All "
        "CIA component marks (CAT-1, CAT-2, quizzes, assignments, attendance) must be entered "
        "into DCMP by instructors on the following schedule: CAT-1 marks within 7 days of the test "
        "session; CAT-2 marks within 7 days; and the full CIA total frozen 48 hours before the "
        "start of practical examinations. Post-freeze alterations require a signed order from the "
        "Department Academic Committee, countersigned by the Head of Department, and uploaded to "
        "DCMP before 5:00 PM on the working day of the change. Retroactive alterations within "
        "10 days of end-semester results publication will trigger automatic Grade Moderation "
        "Committee audit.", st["body"]))

    s.append(Paragraph("6. Practical Examination Administration & External Examiner Protocols", st["h1"]))
    s.append(Paragraph(
        "Practical examinations are conducted over 6 working days in batched laboratory slots. "
        "External Examiners are appointed by the Dean of Academic Affairs from the approved university "
        "panel or from industry partners. Duties include: (a) reviewing the pre-lab design "
        "(flowcharts, schemas, pseudocode) submitted in the lab record book; (b) witnessing live "
        "code execution and embedded system demonstration; (c) conducting viva voce covering "
        "underlying theory, algorithmic trade-offs, and design decisions; (d) independently uploading "
        "awarded marks on the exam portal within 2 hours of each session. Disputes over practical "
        "marks must be raised in writing within 24 hours of the session.", st["body"]))

    s.append(Paragraph("7. Reading Days: Institutional Policies & Library Extended Operation", st["h1"]))
    s.append(Paragraph(
        "During the 5-day Reading Period, the Dr. APJ Abdul Kalam Knowledge Center, the Digital "
        "Learning Center (DLC), and all departmental reading rooms operate 24 hours daily with "
        "enhanced Wi-Fi capacity and dedicated exam-support staff. No new academic obligations "
        "(assignments, surprise tests, mandatory lectures, or project reviews) may be scheduled "
        "during this period. Violations by faculty are reportable to the Dean of Academic Affairs "
        "and constitute a breach of the Academic Calendar Compliance Policy.", st["body"]))

    s.append(Paragraph("8. Gazetted National Holidays & Campus Observances 2025-2026", st["h1"]))
    s.append(Paragraph(
        "The University observes all central government gazetted holidays applicable to educational "
        "institutions: Independence Day (Aug 15), Ganesh Chaturthi (Aug 27), Mahatma Gandhi Jayanti "
        "(Oct 2), Dussehra/Vijayadashami (Oct 12), Diwali Break (Nov 1–3), Guru Nanak Jayanti "
        "(Nov 15), Christmas (Dec 25), New Year's Day (Jan 1), Republic Day (Jan 26), Maha Shivratri "
        "(Feb 17), Holi (Mar 14), Good Friday (Apr 3), Eid-ul-Fitr (Apr 11), and Buddha Purnima "
        "(May 12). Additional state-specific holidays as announced by the state government are "
        "incorporated into the calendar with minimum 48 hours' institutional notice.", st["body"]))

    s.append(Paragraph("9. Doctoral Research Milestones, Colloquium & Thesis Submission", st["h1"]))
    s.append(Paragraph(
        "Doctoral researchers (Ph.D. scholars) must fulfill mandatory annual milestones: (a) Annual "
        "Progress Seminar at the Departmental Doctoral Colloquium during Week 8 of the Odd Semester; "
        "(b) Interim Thesis Report submission by November 30 each year; (c) Pre-synopsis public "
        "seminar with 14 days advance notice on the university portal; (d) final Ph.D. thesis "
        "submission to the Controller of Examinations following successful pre-submission review "
        "and Similarity Index check (maximum 10% excluding references). Viva voce scheduling "
        "requires a minimum of 2 external examiners from institutions outside the university system.", st["body"]))

    s.append(Paragraph("10. Course Registration, Late Penalties & Voluntary Leave of Absence", st["h1"]))
    s.append(Paragraph(
        "Online course registration opens two weeks before term commencement. Late registration "
        "during Week 1 incurs an administrative fee of Rs. 500. Registration portal closes on the "
        "second Friday of the semester. Students who fail to register within this window are "
        "classified as having taken a Voluntary Semester Leave of Absence (VSLA). VSLA requires "
        "formal notification to the Registrar and triggers a mandatory re-admission procedure before "
        "the following semester's registration window. A student may take a maximum of 2 VSLAs over "
        "the course of their degree programme.", st["body"]))

    build_pdf(
        os.path.join(DATA_DIR, "public", "academic_calendar_2025.pdf"),
        "Annual Academic Calendar & Examination Timetable 2025-2026",
        "Northgate Institute of Technology | Term Schedules, Assessment Windows & Institutional Events",
        s, "public")


# =============================================================================
# 3. PUBLIC — course_catalog.pdf
# =============================================================================
def generate_course_catalog():
    st = get_custom_styles()
    s = []

    s.append(Paragraph("1. B.Tech CSE Degree Architecture & CBCS Curriculum Framework", st["h1"]))
    s.append(Paragraph(
        "The Bachelor of Technology (B.Tech) in Computer Science and Engineering at Northgate Institute "
        "is an 8-semester, 4-year professional engineering programme structured under the Choice-Based "
        "Credit System (CBCS) in accordance with AICTE Model Curriculum 2022 and NBA Tier-1 accreditation "
        "criteria. It requires a minimum of 160 academic credits distributed across seven curricular "
        "categories. The programme is aligned with the Washington Accord Graduate Attributes and "
        "prepares students for careers in software engineering, data science, systems architecture, "
        "AI/ML research, cloud computing, and entrepreneurship.", st["body"]))
    s.append(Paragraph("• <b>Basic Sciences (BSC — 24 Credits):</b> Engineering Mathematics I (Linear Algebra & Calculus), Mathematics II (ODE & Complex Analysis), Mathematics III (Probability, Statistics & Transforms), Mathematics IV (Numerical Methods & Graph Theory), Engineering Physics with Lab, Engineering Chemistry with Lab.", st["bullet"]))
    s.append(Paragraph("• <b>Engineering Sciences (ESC — 20 Credits):</b> Basic Electrical & Electronics Engineering, Engineering Graphics & Product Design using CAD, Programming Fundamentals with Python, Manufacturing Processes (Workshop Practice), Digital Logic & Circuit Design.", st["bullet"]))
    s.append(Paragraph("• <b>Humanities, Social Sciences & Management (HSMC — 12 Credits):</b> Professional Communication & Technical Writing, Environmental Science & Sustainability, Ethics, Human Values & IPR, Technology Entrepreneurship & Business Models.", st["bullet"]))
    s.append(Paragraph("• <b>Professional Core Courses (PCC — 64 Credits):</b> Data Structures, Algorithms, Computer Architecture, Discrete Mathematics, Database Systems (CS301), Operating Systems, Computer Networks, Automata Theory & Compilers, Machine Learning, Software Engineering & System Design — 16 courses across Semesters III–VII.", st["bullet"]))
    s.append(Paragraph("• <b>Professional Electives (PEC — 20 Credits):</b> 5 electives from a designated specialization track (AI/ML, Cyber Security, or Cloud & Distributed Systems) — Semesters VI–VIII.", st["bullet"]))
    s.append(Paragraph("• <b>Open Electives (OEC — 8 Credits):</b> 2 interdisciplinary courses from offered management, economics, cognitive sciences, or law schools.", st["bullet"]))
    s.append(Paragraph("• <b>Project Work, Internship & Seminars (PROJ — 12 Credits):</b> Mini-Project (Sem V, 2 Cr), Industrial Internship (Sem VI, 2 Cr), Capstone Major Project Phase I (Sem VII, 4 Cr), Capstone Major Project Phase II (Sem VIII, 4 Cr).", st["bullet"]))

    s.append(Paragraph("2. Semester I & II — Foundation Engineering Sciences", st["h1"]))
    s.append(Paragraph(
        "Semesters I and II build rigorous mathematical, computational, and engineering foundations. "
        "The curriculum integrates theory with laboratory practice to develop algorithmic thinking, "
        "circuit understanding, professional communication, and engineering drawing skills.", st["body"]))
    s.append(Paragraph("<b>MA101 Engineering Mathematics I — Linear Algebra & Calculus (4 Credits | 3-1-0)</b>", st["h2"]))
    s.append(Paragraph(
        "Vector spaces, subspaces, basis and dimension, linear transformations, eigenvalues and eigenvectors, "
        "diagonalization, singular value decomposition. Multivariable calculus: partial derivatives, "
        "gradient, Jacobian, Taylor expansion, Lagrange multipliers. Multiple integrals, line and surface "
        "integrals, Green's Theorem, Stokes' Theorem, Divergence Theorem. Application to computer graphics, "
        "machine learning (PCA, SVD), and network analysis.", st["body"]))
    s.append(Paragraph("<b>CS101 Programming Fundamentals with Python (4 Credits | 3-0-2)</b>", st["h2"]))
    s.append(Paragraph(
        "Computational thinking, algorithmic problem decomposition, Python 3 syntax: variables, types, "
        "control flow (if/elif/else, for, while), function definition and scope, recursion and memoization, "
        "Python data structures (list, tuple, dict, set, frozenset), comprehensions, generators and "
        "iterators, file I/O (text, CSV, JSON), exception handling, modules and packages, OOP fundamentals "
        "(classes, inheritance, polymorphism, dunder methods). Introduction to NumPy and Matplotlib for "
        "scientific computing. Lab: 15 practical exercises covering number theory, string algorithms, "
        "sorting and searching, matrix operations, and data visualization.", st["body"]))

    s.append(Paragraph("3. Semester III & IV — Core CS Foundations", st["h1"]))
    s.append(Paragraph("<b>CS201 Data Structures & Algorithm Design (4 Credits | 3-1-2)</b>", st["h2"]))
    s.append(Paragraph(
        "Sequential structures: arrays (multi-dimensional, jagged), singly/doubly/circular linked lists, "
        "stacks (balanced parentheses, expression evaluation), queues (circular, deque, priority queue). "
        "Non-linear structures: binary trees, BST operations (insert, delete, traversal), AVL trees "
        "(rotation cases, balance factor), Red-Black trees, heaps (heapify, heapsort, priority queues), "
        "hash tables (separate chaining, open addressing, load factor, universal hashing), tries. "
        "Graphs: adjacency matrix vs list, BFS, DFS, topological sort (DFS-based and Kahn's), "
        "shortest paths (Dijkstra, Bellman-Ford, Floyd-Warshall), minimum spanning trees "
        "(Kruskal's with DSU, Prim's with priority queue). Algorithm paradigms: divide and conquer, "
        "dynamic programming (coin change, LCS, edit distance, 0-1 knapsack, matrix chain), greedy "
        "(activity selection, Huffman encoding). Amortized analysis. NP-completeness introduction.", st["body"]))
    s.append(Paragraph("<b>CS210 Discrete Mathematical Structures (4 Credits | 3-1-0)</b>", st["h2"]))
    s.append(Paragraph(
        "Propositional and predicate logic, logical equivalences, proof methods: direct, indirect, "
        "proof by contradiction, mathematical induction (strong induction), well-ordering principle. "
        "Set theory: operations, power sets, Cartesian product, Venn diagrams. Relations: reflexive, "
        "symmetric, transitive, equivalence relations, partial orders, Hasse diagrams. Functions: "
        "injective, surjective, bijective, composition, inverse. Combinatorics: pigeonhole principle, "
        "permutations, combinations, inclusion-exclusion, generating functions, recurrence relations "
        "(linear homogeneous, Fibonacci, Catalan numbers). Graph theory: Eulerian and Hamiltonian "
        "paths, graph coloring (chromatic number, four-color theorem), planar graphs, trees and "
        "spanning trees. Algebraic structures: groups, rings, fields, lattices, Boolean algebras.", st["body"]))
    s.append(Paragraph("<b>CS240 Computer Organization & Architecture (4 Credits | 3-0-2)</b>", st["h2"]))
    s.append(Paragraph(
        "Number representations: two's complement, IEEE 754 floating point, signed overflow. "
        "ISA design: MIPS and RISC-V instruction formats, addressing modes, calling conventions, "
        "ABI and stack frames. Datapath design: ALU, multiplexers, register file, single-cycle "
        "vs pipelined implementation. Pipeline hazards: data hazards (forwarding, stalls), structural "
        "hazards, control hazards (branch prediction: always-taken, two-bit predictor, BHT, BTB). "
        "Memory hierarchy: SRAM vs DRAM, direct-mapped, N-way set-associative and fully-associative "
        "cache, write-back vs write-through, cache coherence (MESI protocol). Virtual memory: TLBs, "
        "multi-level page tables (x86-64 4-level), page fault handling. I/O: programmed I/O, "
        "interrupt-driven I/O, DMA controller operation. Lab: MIPS assembly programming, "
        "Logisim circuit simulation, cache performance analysis using valgrind.", st["body"]))

    s.append(Paragraph("4. Semester V — Core Professional Track", st["h1"]))
    s.append(Paragraph("<b>CS301 Database Management Systems (4 Credits | 3-1-2)</b>", st["h2"]))
    s.append(Paragraph(
        "Unit I: File systems vs DBMS, three-schema architecture, data independence, relational/hierarchical/"
        "network models. ER modeling: entity sets, attributes (composite, multivalued, derived), "
        "relationship sets (cardinality: 1:1, 1:N, M:N), weak entities, identifying relationships, "
        "extended ER (specialization, generalization, aggregation), 7-step ER-to-relational mapping. "
        "Unit II: Relational algebra (select σ, project π, rename ρ, cross product ×, natural join ⋈, "
        "theta join, outer joins, division ÷). SQL DDL (CREATE, ALTER, DROP, constraints), DML (SELECT "
        "with subqueries, correlated subqueries, EXISTS, aggregates, GROUP BY, HAVING), window functions "
        "(RANK, DENSE_RANK, ROW_NUMBER, LAG, LEAD), CTEs, views, triggers, stored procedures. "
        "Unit III: Functional dependencies (FD), Armstrong's axioms (reflexivity, augmentation, transitivity), "
        "attribute closure, canonical covers, normal forms (1NF, 2NF, 3NF, BCNF), lossless-join "
        "decomposition, dependency-preservation, Bernstein's 3NF synthesis, multi-valued dependencies, 4NF. "
        "Unit IV: Transactions, ACID properties, concurrency anomalies (dirty read, non-repeatable read, "
        "phantom read), conflict serializability, precedence graph, recoverability, cascadeless schedules, "
        "Two-Phase Locking (strict 2PL, rigorous 2PL), timestamp ordering, MVCC, deadlock detection "
        "(wait-for graph), prevention (wound-wait, wait-die), ARIES recovery: write-ahead logging, "
        "checkpoint, analysis pass, redo pass, undo pass. "
        "Unit V: Physical storage (heap files, sorted files, clustered/unclustered), RAID levels "
        "(0, 1, 4, 5, 6, 1+0), B+ tree structure (internal vs leaf nodes, insertion/deletion algorithms, "
        "bulk loading), hash-based indexes, bitmap indexes. Heuristic query optimization: equivalence "
        "rules, selection/projection push-down, join ordering, statistics-based cost estimation. "
        "Lab: PostgreSQL schema design, SQL performance tuning with EXPLAIN ANALYZE, B+ tree "
        "insertion benchmarking, transaction isolation level experiments.", st["body"]))
    s.append(Paragraph("<b>CS340 Operating Systems Architecture (4 Credits | 3-1-2)</b>", st["h2"]))
    s.append(Paragraph(
        "Monolithic vs microkernel vs hybrid OS designs. Process lifecycle, PCB, process creation "
        "(fork/exec), context switching overhead analysis. Threading: kernel threads vs user threads, "
        "POSIX pthreads, thread pools. CPU scheduling: FCFS, SJF (preemptive SRTF), Round Robin "
        "(quantum selection trade-offs), Priority Scheduling, Multilevel Feedback Queue (MLFQ). "
        "Synchronization: Race conditions, critical section problem, Peterson's solution, "
        "hardware atomics (TestAndSet, CompareAndSwap), spinlocks, semaphores (binary, counting), "
        "mutex locks, monitors, condition variables. Classical problems: Bounded Buffer, "
        "Readers-Writers (3 variants), Dining Philosophers (Chandy-Misra solution). "
        "Deadlocks: 4 Coffman conditions, RAG, Banker's safety algorithm, detection & recovery. "
        "Memory: logical vs physical address spaces, MMU, segmentation, paging, multi-level page "
        "tables, inverted page tables, TLB shootdown, demand paging, page replacement "
        "(FIFO — Belady's anomaly, Optimal, LRU via stack/clock approximation), thrashing and "
        "working set model. File systems: VFS, inode structure, directory traversal, allocation "
        "methods, fsck recovery. I/O: device drivers, interrupt handling, disk scheduling "
        "(SSTF, SCAN, C-SCAN, LOOK). Virtualization: Type-1 (bare-metal) and Type-2 hypervisors, "
        "hardware-assisted virtualization (VT-x, AMD-V), container isolation via Linux namespaces "
        "and cgroups, Docker internals.", st["body"]))
    s.append(Paragraph("<b>CS355 Computer Networks & Internet Protocols (4 Credits | 3-0-2)</b>", st["h2"]))
    s.append(Paragraph(
        "OSI vs TCP/IP 5-layer model. Physical layer: Nyquist/Shannon theorems, encoding schemes, "
        "fiber vs copper. Data link: framing, CRC polynomial division, sliding window protocols "
        "(Stop-and-Wait, Go-Back-N, Selective Repeat), MAC sub-layer, Ethernet CSMA/CD, 802.11 "
        "CSMA/CA, spanning tree protocol. Network layer: IPv4 addressing and subnetting (VLSM, "
        "CIDR), IPv6 (128-bit, stateless autoconfiguration), ARP, ICMP, NAT. Routing: Dijkstra "
        "OSPF (link-state), Bellman-Ford RIP (distance vector), BGP (path vector, AS policies), "
        "MPLS labels. Transport: TCP three-way handshake, state machine, reliable delivery via "
        "retransmission, congestion control (slow start, congestion avoidance, AIMD, fast retransmit, "
        "Reno, CUBIC, BBR), UDP checksum. Application: HTTP/1.1 vs HTTP/2 vs HTTP/3 (QUIC), "
        "DNS hierarchy and resolution, SMTP/IMAP, TLS 1.3 handshake, CDN architecture. "
        "Lab: Wireshark packet analysis, socket programming (TCP/UDP client-server), "
        "mininet network emulation.", st["body"]))
    s.append(Paragraph("<b>CS360 Automata Theory & Compiler Design (4 Credits | 3-1-0)</b>", st["h2"]))
    s.append(Paragraph(
        "Part A — Formal Languages: DFAs and NFAs (subset construction, Myhill-Nerode minimization), "
        "regular expressions (Kleene's theorem, Arden's equation), pumping lemma for regularity, "
        "closure properties of regular languages. CFGs: derivation, parse trees, ambiguity, "
        "simplification (CNF, GNF), pumping lemma for CFLs, closure properties. PDAs (NPDA from "
        "CFG, determinism), Turing Machines (variants: multi-tape, non-deterministic), decidability, "
        "the Halting Problem, Rice's Theorem, reducibility, complexity classes P and NP. "
        "Part B — Compilers: Lexical analysis (maximal munch, Flex tool, DFA-based scanner), "
        "syntax analysis: predictive parsing (FIRST/FOLLOW, LL(1) table construction), bottom-up "
        "parsing (LR(0) items, SLR(1), LALR(1), CLR(1)), error recovery strategies. Semantic "
        "analysis: symbol table management, type checking (Hindley-Milner inference), scope rules. "
        "Intermediate code generation: three-address code (TAC), SSA form, AST lowering. "
        "Code optimization: constant folding, dead-code elimination, loop-invariant code motion, "
        "register allocation (graph coloring). Target code generation for RISC-V.", st["body"]))

    s.append(Paragraph("5. Semester VI — Advanced Core & System Design", st["h1"]))
    s.append(Paragraph("<b>CS420 Applied Machine Learning & AI (4 Credits | 3-0-2)</b>", st["h2"]))
    s.append(Paragraph(
        "Unit I: Supervised learning — hypothesis space, empirical risk minimization, Linear Regression "
        "(OLS, Lasso L1, Ridge L2, ElasticNet), feature engineering, polynomial features, bias-variance "
        "tradeoff, cross-validation (k-fold, stratified), hyperparameter tuning (grid search, Bayesian "
        "optimization). Logistic Regression (sigmoid, softmax, multi-class OvR/OvO). "
        "Unit II: Decision Trees (Gini impurity, information gain, entropy, CART algorithm, pruning), "
        "Random Forests (bagging, feature sub-sampling, variable importance), Gradient Boosting "
        "(functional gradient descent, XGBoost, LightGBM, CatBoost), SVMs (hard/soft margin, kernel "
        "trick: RBF, polynomial, sigmoid, Mercer's condition). "
        "Unit III: Neural Networks — perceptron, MLP, activation functions (sigmoid, tanh, ReLU, "
        "Leaky ReLU, GELU, Swish), backpropagation derivation via chain rule, weight initialization "
        "(Xavier, He), optimizers (SGD, Momentum, RMSProp, Adam, AdamW), batch normalization, "
        "dropout, L2 regularization. Deep learning: CNNs (convolution, pooling, receptive field, "
        "ResNet residual connections, batch norm), RNNs (vanishing gradient problem, LSTM gates, "
        "GRU), Transformer architecture (scaled dot-product attention, multi-head attention, "
        "positional encoding, BERT, GPT), LoRA fine-tuning for LLMs. "
        "Unit IV: Unsupervised learning — K-Means++ initialization, Elbow method, DBSCAN "
        "(epsilon-neighborhood, MinPts, noise points), hierarchical clustering (Ward linkage), "
        "PCA (covariance eigendecomposition, scree plot), t-SNE (KL divergence optimization), "
        "UMAP, Gaussian Mixture Models (EM algorithm). "
        "Unit V: Evaluation metrics, confusion matrix, ROC-AUC, PR curve, F1, MCC, calibration. "
        "Responsible AI: fairness metrics (demographic parity, equalized odds), explainability "
        "(SHAP, LIME, Integrated Gradients), data governance, model cards. "
        "Lab: Python (scikit-learn, PyTorch) — end-to-end ML pipelines, CNN image classification, "
        "LLM prompt engineering and fine-tuning workshop.", st["body"]))
    s.append(Paragraph("<b>CS460 Software Engineering & System Design (4 Credits | 3-0-2)</b>", st["h2"]))
    s.append(Paragraph(
        "Part 1 — Low-Level Design (LLD): SDLC models (Waterfall, Agile Scrum, Kanban, XP), "
        "OOP principles (encapsulation, abstraction, inheritance, polymorphism), SOLID principles "
        "(SRP, OCP, LSP, ISP, DIP) with anti-pattern examples. Design Patterns (GoF 23): Creational "
        "(Thread-safe Singleton, Factory Method, Abstract Factory, Builder, Prototype), Structural "
        "(Adapter, Bridge, Composite, Decorator, Facade, Flyweight, Proxy), Behavioral "
        "(Strategy, Observer Pub-Sub, Command Undo/Redo, Template Method, Iterator, State Machine, "
        "Mediator, Chain of Responsibility). UML diagrams: Class, Sequence, Activity, State, "
        "Component, Deployment. Case study: Enterprise Parking Lot System — multi-gate architecture, "
        "vehicle types (two-wheeler, four-wheeler, bus), smart pricing strategies, reservations. "
        "Part 2 — High-Level Design (HLD): Scalability (vertical vs horizontal), load balancing "
        "(L4 vs L7, round-robin, least-connections, consistent hashing, rendezvous hashing). "
        "Storage: SQL vs NoSQL decision framework, replication (leader-follower, multi-leader, "
        "leaderless), database sharding (range, hash, directory-based), connection pooling. "
        "Caching: Cache-aside, Read-through, Write-through, Write-behind, LRU/LFU eviction, Redis "
        "clusters, CDN edge caching. CAP theorem (formal proof), PACELC extension, BASE properties. "
        "Message queues: Apache Kafka (topics, partitions, consumer groups, ISR), RabbitMQ. "
        "Microservices: bounded contexts (DDD), API gateway (rate limiting — token bucket, leaky "
        "bucket; circuit breaker — Hystrix/Resilience4j), service mesh (Envoy, Istio). "
        "Distributed transactions: 2PC, SAGA (orchestration vs choreography). Consensus: Raft "
        "(leader election, log replication, safety guarantee). End-to-end system design case studies: "
        "URL shortener (TinyURL — 100M daily writes, Base62, KGS), push notification system "
        "(WebSocket, FCM/APNS, deduplication), distributed online exam proctoring platform "
        "(auto-scaling, WebRTC, anti-cheating AI).", st["body"]))

    s.append(Paragraph("6. Professional Elective Tracks & Course Offerings (Semesters VI–VIII)", st["h1"]))
    s.append(Paragraph(
        "<b>Track A — AI & Intelligent Systems:</b> (1) CS501 Natural Language Processing: "
        "tokenization, word embeddings (Word2Vec, GloVe, FastText), seq2seq, BERT pre-training, "
        "GPT architecture, retrieval-augmented generation (RAG), knowledge graphs. (2) CS502 "
        "Computer Vision: image formation, edge detection, HOG features, CNN architectures "
        "(AlexNet, VGG, ResNet, EfficientNet), object detection (YOLO v8, DETR, SAM), "
        "generative models (VAE, GAN, Stable Diffusion). (3) CS503 Reinforcement Learning: "
        "MDP formulation, Bellman equations, Q-learning, DQN, policy gradient (REINFORCE, PPO, SAC).", st["body"]))
    s.append(Paragraph(
        "<b>Track B — Systems & Cybersecurity:</b> (1) CS511 Network Security & Cryptography: "
        "symmetric encryption (AES-256, ChaCha20), asymmetric (RSA, ECC), hash functions "
        "(SHA-3), TLS internals, PKI, digital certificates, zero-trust architecture, firewall "
        "design, IDS/IPS. (2) CS512 Blockchain & Decentralized Systems: consensus mechanisms "
        "(PoW, PoS, dBFT, Tendermint), smart contracts (Solidity, EVM), DeFi primitives, "
        "supply-chain provenance. (3) CS513 Penetration Testing & Cyber Forensics: OWASP Top-10 "
        "web vulnerabilities, Metasploit, reverse engineering, memory forensics, incident response.", st["body"]))
    s.append(Paragraph(
        "<b>Track C — Cloud & Distributed Computing:</b> (1) CS521 Cloud Architecture: "
        "AWS/GCP/Azure services comparison, IaaS/PaaS/SaaS, Kubernetes orchestration (pods, "
        "deployments, services, ingress, HPA), Terraform IaC, serverless (Lambda/Cloud Functions). "
        "(2) CS522 Distributed Databases: BigTable, Spanner, DynamoDB, CockroachDB, TiDB, "
        "vector databases (Pinecone, Qdrant, Weaviate) for RAG applications. "
        "(3) CS523 Edge Computing & IoT: edge inference optimization (model quantization, pruning, "
        "knowledge distillation), MQTT, fog computing frameworks, real-time data pipelines.", st["body"]))

    s.append(Paragraph("7. Academic Progression, Prerequisite Policy & Credit Overload", st["h1"]))
    s.append(Paragraph(
        "Students must pass all listed prerequisites with a minimum grade of 'C' (5.0 grade points) "
        "before enrolling in dependent upper-division courses. Standard maximum semester registration "
        "is 24 credits. Students maintaining a cumulative CGPA >= 8.50 with no active backlogs may "
        "petition for a Credit Overload up to 28 credits to pursue the Honors Research stream or "
        "dual elective specialization. Students carrying more than 12 credit-hours of active backlogs "
        "are administratively limited to 18 credits in the subsequent semester. The Honors Thesis "
        "Programme (CS490H, 6 credits, replacing Capstone Phase II) requires written endorsement "
        "from a faculty supervisor with active research funding and approval from the Department "
        "Research Committee.", st["body"]))

    s.append(Paragraph("8. M.Tech Computer Science & Engineering Programme Overview", st["h1"]))
    s.append(Paragraph(
        "The M.Tech programme (2-year, 4 semesters, 72 credits) admits students through GATE CS/DA "
        "scores, with a minimum qualifying GATE percentile of 85. Specializations: AI & Machine "
        "Learning, Software Systems & Security, and Data Engineering & Cloud Computing. The programme "
        "requires: 8 core theory courses (32 Cr), 4 elective courses (16 Cr), a 2-semester research "
        "thesis (20 Cr), and 1 seminar (4 Cr). Thesis evaluation includes an open seminar before "
        "submission and final viva voce with 2 external examiners.", st["body"]))

    build_pdf(
        os.path.join(DATA_DIR, "public", "course_catalog.pdf"),
        "Undergraduate & Postgraduate Course Catalog AY 2025-2026",
        "School of Computing & Engineering | B.Tech & M.Tech CSE Programme Specifications",
        s, "public")


# =============================================================================
# 4. FACULTY — exam_answer_keys_cs301.pdf
# =============================================================================
def generate_exam_answer_keys():
    st = get_custom_styles()
    s = []

    s.append(make_callout(
        "<b>CONFIDENTIAL — FACULTY & TEACHING ASSISTANT USE ONLY.</b> This CS301 Database Management "
        "Systems examination solution compendium is restricted to the Course Instructor of Record and "
        "certified teaching assistants. Unauthorized disclosure to students prior to official result "
        "publication constitutes a Level 3 Academic Integrity Policy Violation under Section 6.3 of "
        "the University Disciplinary Matrix.", st, bg_color="#FEF2F2", border_color="#FCA5A5"))

    s.append(Paragraph("1. Examination Administrative Overview", st["h1"]))
    s.append(Paragraph(
        "Course: CS301 Database Management Systems | Term: Fall 2025 | Duration: 3 Hours "
        "Total Marks: 100 | Passing Floor: 50 | Lead Examiner: Dr. Elena Marsh, Associate Professor. "
        "Evaluator Guidance: Award marks based on conceptual clarity, formal correctness, and sound "
        "architectural reasoning. Alternate valid formalisms and SQL syntaxes yielding equivalent "
        "logical execution receive full credit. Deduct 20% of section marks for each major conceptual "
        "error. Deduct 10% for each minor computational error with otherwise correct method.", st["body"]))

    s.append(Paragraph("2. Unit I: ER Modeling & Relational Schema Design (Q1 — 20 Marks)", st["h1"]))
    s.append(Paragraph("<b>Q1.1: Entity vs Relationship; Weak Entity Mapping — 10 Marks</b>", st["h2"]))
    s.append(Paragraph(
        "<b>Model Answer:</b> An <b>Entity</b> represents a distinguishable real-world object or "
        "concept with independent existence, characterized by descriptive attributes — e.g., Student "
        "(StudentID, Name, Programme), Course (CourseCode, Title, Credits), Department (DeptID, Name). "
        "A <b>Relationship</b> captures a semantic association among entity instances — e.g., "
        "Student ENROLLS_IN Course (with attributes: Grade, EnrollmentDate), Professor ADVISES Student. "
        "Relationships may carry their own attributes when the attribute belongs to the association "
        "rather than either participating entity.<br/>"
        "A <b>Weak Entity Set</b> lacks sufficient own attributes to form a primary key; its existence "
        "depends entirely on an <i>identifying (owner) entity set</i> via an <i>identifying "
        "relationship</i>. Key example: Dependent (Name, DateOfBirth, Relationship) exists only in "
        "relation to Employee — the discriminator 'Dependent_Name' alone cannot uniquely identify a "
        "Dependent across all employees.<br/>"
        "Relational Mapping of Weak Entities (7-step algorithm, Step 5): (1) Create a table for the "
        "weak entity with all its attributes. (2) Include the complete Primary Key of the owner entity "
        "as a Foreign Key. (3) The Primary Key of the resulting table is the composite {Owner_PK + "
        "Discriminator_Attribute}. (4) Define the FK constraint with ON DELETE CASCADE to enforce "
        "total existential dependency.<br/>"
        "<b>Marking:</b> 4M (entity vs relationship distinction with example); 3M (weak entity, "
        "identifying relationship, discriminator concept); 3M (exact relational mapping with composite "
        "PK and ON DELETE CASCADE).", st["body"]))
    s.append(Paragraph("<b>Q1.2: Specialization, Generalization, and Aggregation — 10 Marks</b>", st["h2"]))
    s.append(Paragraph(
        "<b>Model Answer:</b><br/>"
        "• <b>Specialization (Top-down):</b> Defining sub-groups within a higher-level entity set based "
        "on distinguishing characteristics. E.g., Employee specializes into Faculty (Tenure_Status, "
        "ResearchArea) and AdministrativeStaff (Department_Assigned, Grade_Level). Implemented "
        "relationally by creating separate tables for each sub-entity containing only subtype-specific "
        "attributes plus the supertype PK as FK.<br/>"
        "• <b>Generalization (Bottom-up):</b> Synthesizing multiple entity sets sharing common "
        "attributes into a single higher-level superclass. E.g., Car and Motorcycle are generalized "
        "into Vehicle (VehicleID, VIN, ManufacturingYear, OwnerID). Disjoint vs overlapping "
        "constraints; total vs partial participation constraints determine whether every superclass "
        "instance must belong to a subclass.<br/>"
        "• <b>Aggregation:</b> Treats a relationship and its participating entities as a composite "
        "higher-level entity, enabling a relationship to participate in another relationship. E.g., "
        "the 'Employee WORKS_ON Project' relationship is aggregated as a unit, then associated with "
        "'Manager SUPERVISES {Employee-WORKS_ON-Project}'. This models supervision of a work "
        "assignment rather than supervision of an employee globally.<br/>"
        "<b>Marking:</b> 3M (specialization with mapping rule); 3M (generalization with disjoint/"
        "overlapping distinction); 4M (aggregation with illustrative diagram and relational mapping).", st["body"]))

    s.append(Paragraph("3. Unit II & III: Normalization Theory & Functional Dependencies (Q2 — 30 Marks)", st["h1"]))
    s.append(Paragraph("<b>Q2.1: Armstrong's Axioms — Transitivity Proof — 10 Marks</b>", st["h2"]))
    s.append(Paragraph(
        "<b>Model Answer:</b> A <b>Functional Dependency</b> X → Y holds on relation schema R if "
        "for all legal instances r of R, ∀ t1, t2 ∈ r: t1[X] = t2[X] ⟹ t1[Y] = t2[Y]. "
        "X functionally determines Y; Y is functionally dependent on X.<br/>"
        "<b>Armstrong's Axioms (Sound and Complete):</b><br/>"
        "A1 — Reflexivity: If Y ⊆ X, then X → Y (trivial dependency).<br/>"
        "A2 — Augmentation: If X → Y, then XZ → YZ for any attribute set Z.<br/>"
        "A3 — Transitivity: If X → Y and Y → Z, then X → Z.<br/>"
        "<b>Derived Rules:</b> Union (X→Y, X→Z ⟹ X→YZ), Decomposition (X→YZ ⟹ X→Y, X→Z), "
        "Pseudotransitivity (X→Y, WY→Z ⟹ WX→Z).<br/>"
        "<b>Formal Proof of Transitivity:</b><br/>"
        "Given: X → Y (1) and Y → Z (2). Prove: X → Z.<br/>"
        "Step 1: From (1) by A2 (augment with X): XX → XY ⟹ X → XY.<br/>"
        "Step 2: From (2) by A2 (augment with X): XY → XZ.<br/>"
        "Step 3: From Steps 1 and 2, since X → XY and XY → XZ, by A3: X → XZ.<br/>"
        "Step 4: By A1 (reflexivity): XZ → Z (since Z ⊆ XZ).<br/>"
        "Step 5: By A3 from Steps 3 and 4: X → Z. ∎ Q.E.D.<br/>"
        "<b>Marking:</b> 3M (FD formal definition); 4M (three axioms with derived rules); 3M (formal proof).", st["body"]))
    s.append(Paragraph("<b>Q2.2: Candidate Keys, Normal Form Determination, and 3NF Decomposition — 20 Marks</b>", st["h2"]))
    s.append(Paragraph(
        "<b>Given:</b> R(A, B, C, D, E) with F = { A → BC, CD → E, B → D, E → A }.<br/>"
        "<b>(i) All Candidate Keys — 6M:</b><br/>"
        "Strategy: Compute attribute closures to find all minimal superkeys.<br/>"
        "• A⁺ = {A} → {A,B,C} (via A→BC) → {A,B,C,D} (via B→D) → {A,B,C,D,E} (via CD→E). "
        "A⁺ = ABCDE → <b>A is a candidate key.</b><br/>"
        "• E⁺ = {E,A,B,C,D,E} (via E→A, then A→BC, B→D, CD→E) = ABCDE → <b>E is a candidate key.</b><br/>"
        "• B⁺ = {B,D} (via B→D). B⁺ ≠ ABCDE → B is NOT a CK.<br/>"
        "• BC⁺ = {B,C,D} → {B,C,D,E} (via CD→E) → {A,B,C,D,E} (via E→A) = ABCDE → "
        "<b>BC is a candidate key.</b><br/>"
        "• CD⁺ = {C,D,E} (via CD→E) → {A,B,C,D,E} (via E→A, A→BC) = ABCDE → "
        "<b>CD is a candidate key.</b><br/>"
        "Prime attributes = {A, B, C, D, E} (every attribute appears in at least one CK). "
        "Non-prime attributes = {} (empty set).<br/>"
        "<b>(ii) Highest Normal Form — 6M:</b><br/>"
        "BCNF requires: for every non-trivial FD X→Y in F⁺, X must be a superkey.<br/>"
        "• A→BC: A is a CK → satisfies BCNF. ✓<br/>"
        "• CD→E: CD is a CK → satisfies BCNF. ✓<br/>"
        "• B→D: B is NOT a superkey → VIOLATES BCNF. However, D is a prime attribute "
        "(D ∈ CK={CD}). Since D is prime, B→D satisfies 3NF (3NF condition: either X is a "
        "superkey, or Y−X contains only prime attributes). ✓ 3NF.<br/>"
        "• E→A: E is a CK → satisfies BCNF. ✓<br/>"
        "<b>Conclusion: R is in 3NF but NOT in BCNF</b> due to the BCNF violation of B→D.<br/>"
        "<b>(iii) 3NF Decomposition via Bernstein's Synthesis — 8M:</b><br/>"
        "Step 1: Compute canonical cover Fc:<br/>"
        "  A→BC decomposes to A→B, A→C (no extraneous attributes since B and C are independent).<br/>"
        "  Fc = {A→B, A→C, B→D, CD→E, E→A}.<br/>"
        "Step 2: Create one relation for each FD in Fc:<br/>"
        "  R1(A,B) with PK=A; R2(A,C) with PK=A; R3(B,D) with PK=B; R4(C,D,E) with PK={C,D}; "
        "R5(E,A) with PK=E.<br/>"
        "Step 3: Merge relations with same key: R1(A,B) and R2(A,C) merge to R12(A,B,C) PK=A.<br/>"
        "Step 4: Final decomposition: {R12(A,B,C), R3(B,D), R4(C,D,E), R5(E,A)}.<br/>"
        "Step 5: Verify candidate key containment: R12 contains CK A ✓, R4 contains CK CD ✓, "
        "R5 contains CK E ✓ → no additional universal-key relation needed.<br/>"
        "Proof of Lossless-Join: The join on R12 ⋈ R3 ⋈ R4 ⋈ R5 reconstructs R without spurious tuples "
        "(verified by tableau method). Proof of Dependency-Preservation: All FDs in Fc are preserved "
        "in individual relations. Both properties satisfied. ∎", st["body"]))

    s.append(Paragraph("4. Unit IV: Transactions, ACID & Concurrency (Q3 — 30 Marks)", st["h1"]))
    s.append(Paragraph("<b>Q3.1: ACID Properties & Write-Ahead Logging (WAL) / ARIES Recovery — 15 Marks</b>", st["h2"]))
    s.append(Paragraph(
        "<b>Model Answer:</b><br/>"
        "• <b>Atomicity:</b> All operations of a transaction execute to completion, or none take effect. "
        "Ensures no partial updates reach the database. Enforced via undo-logging (ROLLBACK on abort).<br/>"
        "• <b>Consistency:</b> A transaction transforms the database from one integrity-valid state to "
        "another. All integrity constraints, foreign keys, domain constraints, and application-level "
        "invariants must hold before and after each transaction.<br/>"
        "• <b>Isolation:</b> Concurrent transactions execute as if they were serial. Each transaction "
        "sees a consistent snapshot. Enforced via lock managers (2PL) or MVCC. Isolation levels: "
        "Read Uncommitted, Read Committed, Repeatable Read, Serializable (ANSI SQL).<br/>"
        "• <b>Durability:</b> Once a transaction commits, its effects persist permanently through any "
        "subsequent system failure. Enforced via redo-logging and stable (non-volatile) storage.<br/>"
        "<b>Write-Ahead Logging (WAL) — Core Rules:</b><br/>"
        "Rule 1 — Write-Ahead Rule: Before any modified data page is written from the buffer pool to "
        "disk, all log records for that page (including undo information) must first be flushed to "
        "stable storage (the WAL log file).<br/>"
        "Rule 2 — Commit Rule: A transaction is not declared committed until its COMMIT log record "
        "has been force-flushed to stable storage.<br/>"
        "<b>ARIES Recovery Algorithm (3 Phases):</b><br/>"
        "Phase 1 — Analysis Pass: Scan the log forward from the last stable checkpoint. Reconstruct "
        "the dirty-page table (DPT — pages modified but not yet written to disk) and the active-"
        "transaction table (ATT — transactions not yet committed at crash time). Determine the "
        "RedoLSN (earliest log record from which redo must begin).<br/>"
        "Phase 2 — Redo Pass: Replay all logged operations from RedoLSN forward, bringing the database "
        "to the exact state it was in at the moment of crash. Redo is applied even to already-committed "
        "transactions to handle cases where buffer pages had not been flushed.<br/>"
        "Phase 3 — Undo Pass: Roll back all transactions listed as active (uncommitted) at crash time "
        "in reverse chronological order using the CLR (Compensation Log Records) mechanism to ensure "
        "idempotent recovery.", st["body"]))
    s.append(Paragraph("<b>Q3.2: Strict 2PL — Conflict Serializability Proof & Cascading Abort Prevention — 15 Marks</b>", st["h2"]))
    s.append(Paragraph(
        "<b>Two-Phase Locking (2PL):</b> Standard 2PL restricts each transaction to two distinct phases: "
        "(1) Growing Phase: transaction acquires locks (shared S or exclusive X) as needed. "
        "(2) Shrinking Phase: transaction only releases locks; no new locks may be acquired once the "
        "first lock is released. The point of first lock release is the transaction's <i>lock point</i>.<br/>"
        "<b>Strict 2PL:</b> All exclusive (X) locks are held until after the transaction commits or "
        "aborts, preventing dirty reads.<br/>"
        "<b>Proof of Conflict Serializability:</b> "
        "Assume for contradiction that a schedule S produced by strict 2PL is NOT conflict-serializable. "
        "Then S has a cycle T₁ → T₂ → … → Tₙ → T₁ in its precedence (serialization) graph. "
        "An edge Tᵢ → Tⱼ implies Tᵢ performed an operation on data item X before Tⱼ performed a "
        "conflicting operation on X, requiring Tᵢ to have released its lock on X before Tⱼ acquired it. "
        "Therefore, lock_point(Tᵢ) < lock_point(Tⱼ). For the cycle T₁ → T₂ → … → Tₙ → T₁, this "
        "requires lock_point(T₁) < lock_point(T₂) < … < lock_point(Tₙ) < lock_point(T₁), which is "
        "a contradiction (a real number cannot be strictly less than itself). Therefore, no such cycle "
        "can exist; every strict 2PL schedule is conflict-serializable. ∎<br/>"
        "<b>Prevention of Cascading Aborts:</b> A cascading rollback occurs when T₁ writes X, T₂ reads "
        "T₁'s uncommitted write, T₁ aborts → T₂ must also abort, potentially propagating to T₃, etc. "
        "Under Strict 2PL, T₁ retains its X-lock on X until commit/abort. Therefore, T₂ cannot "
        "acquire even a shared read lock on X while T₁ holds the X-lock. Dirty reads are structurally "
        "prevented, and cascading aborts are entirely eliminated.", st["body"]))

    s.append(Paragraph("5. Unit V: Indexing & Query Optimization (Q4 — 20 Marks)", st["h1"]))
    s.append(Paragraph("<b>Q4.1: B-Tree vs B+ Tree; Superiority for Disk-Based Storage — 10 Marks</b>", st["h2"]))
    s.append(Paragraph(
        "<b>B-Tree:</b> In a B-Tree of order m, both internal (index) nodes and leaf nodes store "
        "search key values AND pointers to actual data records. This means data can be found at any "
        "level of the tree during a search traversal.<br/>"
        "<b>B+ Tree:</b> Internal nodes store only search keys and child pointers — acting as a pure "
        "navigation/routing layer. All actual data pointers (or full data tuples in a clustered index) "
        "are stored exclusively in the leaf nodes. All leaf nodes are linked together in a sorted "
        "doubly-linked list (leaf sibling pointers).<br/>"
        "<b>Why B+ Trees Dominate Relational Database Indexes:</b><br/>"
        "1. <b>Higher Fan-out → Shallower Tree Height:</b> Since internal nodes contain only keys (no "
        "data pointers), more keys fit in one disk page (page size typically 8KB or 16KB). Higher "
        "branching factor reduces tree height. A B+ tree of order 200 can index 200³ = 8 million "
        "records with height 3, requiring only 3 disk I/Os for point lookups.<br/>"
        "2. <b>Superior Range Query Performance:</b> B-Tree range queries require complex in-order "
        "traversal across multiple tree levels. B+ Tree range queries locate the starting leaf node "
        "and then traverse the linked list horizontally across leaf nodes — efficient, sequential "
        "disk reads ideal for buffer prefetching.<br/>"
        "3. <b>Uniform Query Latency:</b> Every key lookup traverses exactly root-to-leaf depth "
        "(same number of disk I/Os), enabling predictable query performance without worst-case "
        "variability.<br/>"
        "4. <b>Clustered Index Implementation:</b> Since leaves store full tuples (or row pointers) in "
        "sorted key order, the B+ Tree naturally supports clustered index access — records with "
        "similar key values are physically collocated on disk, minimizing random I/O for range scans.", st["body"]))
    s.append(Paragraph("<b>Q4.2: Heuristic Query Optimization & Equivalence Rules — 10 Marks</b>", st["h2"]))
    s.append(Paragraph(
        "<b>Query Optimization Goal:</b> Rewrite a logically correct query into an equivalent but "
        "computationally cheaper execution plan, reducing disk I/O, memory consumption, and CPU cycles.<br/>"
        "<b>Heuristic Rules (Algebraic Equivalence Transformations):</b><br/>"
        "Rule 1 — <b>Selection Push-Down (Cascade):</b> Push selection operations as early as possible "
        "in the query tree, applying them immediately after the table scan. Reduces intermediate "
        "relation cardinality before expensive join operations. E.g., σ_{Dept='CS'}(Employee ⋈ Dept) "
        "→ σ_{Dept='CS'}(Employee) ⋈ Dept.<br/>"
        "Rule 2 — <b>Projection Push-Down:</b> Push projection operations down to remove unnecessary "
        "columns early, reducing tuple byte width. Fewer bytes per tuple → more tuples fit in one "
        "buffer block → fewer disk I/Os for subsequent operations.<br/>"
        "Rule 3 — <b>Combining Cascaded Unary Operations:</b> Merge consecutive selections "
        "(σ_{C1}(σ_{C2}(R)) = σ_{C1 ∧ C2}(R)) and combine adjacent selections with projections "
        "into single passes over the relation.<br/>"
        "Rule 4 — <b>Join Ordering by Selectivity:</b> Execute the most selective joins first "
        "(those producing the smallest intermediate result) to minimize the size of data flowing "
        "into subsequent join stages. Dynamic programming over all join orderings gives the "
        "globally optimal plan (used in PostgreSQL's planner for N ≤ 8 relations; Genetic Query "
        "Optimizer (GEQO) for N > 8).<br/>"
        "Rule 5 — <b>Replace Cartesian Products with Joins:</b> Wherever a Cartesian product "
        "(×) is followed by a selection condition linking the two relations, replace them with "
        "the corresponding join operator. Cartesian products produce |R|×|S| tuples before "
        "filtering; joins apply the predicate during the merge step.<br/>"
        "<b>Implementation Techniques:</b> Index Nested Loop Join (use existing B+ tree index on "
        "join attribute), Sort-Merge Join (for sorted or sortable inputs), Hash Join (for large "
        "unsorted inputs with equality join predicates).", st["body"]))

    s.append(Paragraph("6. Marking Summary & Grade Boundary Reference", st["h1"]))
    s.append(Paragraph(
        "Question-wise Mark Distribution: Q1 (20M): Q1.1=10, Q1.2=10. Q2 (30M): Q2.1=10, Q2.2=20. "
        "Q3 (30M): Q3.1=15, Q3.2=15. Q4 (20M): Q4.1=10, Q4.2=10. Total: 100M. "
        "Grade boundaries: O (Outstanding) ≥ 90; A+ (Excellent) ≥ 80; A (Very Good) ≥ 70; "
        "B+ (Good) ≥ 60; B (Above Average) ≥ 55; C (Pass) ≥ 50; F (Fail) < 50.", st["body"]))

    build_pdf(
        os.path.join(DATA_DIR, "faculty", "exam_answer_keys_cs301.pdf"),
        "CS301 Database Systems — Final Examination Master Solution Compendium",
        "Fall 2025 | CONFIDENTIAL — Faculty & Teaching Assistants Only",
        s, "faculty")


# =============================================================================
# 5. FACULTY — grading_rubric_2025.pdf
# =============================================================================
def generate_grading_rubric():
    st = get_custom_styles()
    s = []

    s.append(Paragraph("1. Institutional Assessment Standards & OBE Pedagogical Framework", st["h1"]))
    s.append(Paragraph(
        "The School of Computing and Engineering enforces an Outcome-Based Education (OBE) assessment "
        "model meeting National Board of Accreditation (NBA) Tier-1 criteria and aligned with the "
        "Washington Accord's graduate attribute taxonomy. OBE shifts the educational paradigm from "
        "input-based delivery to demonstrable learning outcomes: every assessment must explicitly "
        "measure defined Course Outcomes (COs) mapped to Programme Outcomes (POs) and Programme "
        "Specific Outcomes (PSOs). Bloom's Revised Taxonomy (2001) provides the cognitive depth "
        "hierarchy — Remember (L1), Understand (L2), Apply (L3), Analyze (L4), Evaluate (L5), "
        "Create (L6) — and each question in every assessment must be tagged with the appropriate "
        "Bloom's level and corresponding CO. The attainment of each CO is quantitatively measured "
        "through direct assessment (examination marks) and indirect assessment (exit surveys, "
        "peer evaluation) to drive continuous quality improvement mandated by the NAAC IDP.", st["body"]))
    s.append(Paragraph(
        "Assessment at Northgate Institute is distributed across Continuous Internal Evaluation "
        "(CIE — 50% of total grade) and End-Semester Examinations (ESE — 50% of total grade). "
        "Course instructors must prepare question papers with explicit CO-PO-Bloom's mapping in the "
        "Question Paper Blueprint submitted to the Controller of Examinations 14 days before each "
        "examination.", st["body"]))

    s.append(Paragraph("2. Continuous Internal Assessment (CIE) Component Weights", st["h1"]))
    s.append(Paragraph(
        "For a standard 4-credit Professional Core Course (contact hours 3L-1T-2P per week):", st["body"]))
    s.append(Paragraph("• <b>CAT-1 (25% of CIE):</b> 90-minute centralized written exam covering Units I & II. Bloom's L2–L4. Q-paper: 5 questions × 6 marks = 30 marks scaled to 25. Faculty must upload marks to DCMP within 7 days of the test date.", st["bullet"]))
    s.append(Paragraph("• <b>CAT-2 (25% of CIE):</b> 90-minute centralized exam covering Units III & IV. Same structure and upload timeline as CAT-1.", st["bullet"]))
    s.append(Paragraph("• <b>Online Quizzes & Surprise Tests (15% of CIE):</b> Three auto-graded objective quizzes administered via DCMP LMS, each 20 questions (MCQ + Fill-in), covering the preceding 2 weeks of lectures. Average of best 2 out of 3 quizzes.", st["bullet"]))
    s.append(Paragraph("• <b>Homework Problem Sets & Analytical Proofs (15% of CIE):</b> Four individual written assignments requiring formal proofs, algorithm derivations, or design documents. Each assignment involves a mandatory plagiarism check (MOSS/Turnitin). Late submissions: 20% deduction per working day, no credit after 5 days.", st["bullet"]))
    s.append(Paragraph("• <b>Tutorial Participation & Board Work (10% of CIE):</b> Engagement in weekly problem-solving tutorials. Teaching assistants evaluate on a 3-point scale (Active Engagement, Partial Engagement, Absent). Attendance at 75% of tutorials is mandatory for tutorial credit.", st["bullet"]))
    s.append(Paragraph("• <b>Attendance Incentive (10% of CIE):</b> Pro-rated allocation: ≥ 95% = 10 pts; 90–94% = 8 pts; 85–89% = 6 pts; 80–84% = 4 pts; 75–79% = 2 pts; < 75% = 0 pts (and ineligible for ESE).", st["bullet"]))

    s.append(Paragraph("3. Programming Assignment & Laboratory Evaluation Matrix", st["h1"]))
    s.append(Paragraph(
        "Programming assignments (theory courses with lab components) are evaluated on five dimensions:", st["body"]))
    s.append(Paragraph("• <b>Functional Correctness (35%):</b> Code must pass all published test cases AND 8 hidden edge-case tests without runtime errors, incorrect output, or memory leaks. Full marks only if all tests pass; partial credit scaled to pass rate.", st["bullet"]))
    s.append(Paragraph("• <b>Algorithmic Complexity & Efficiency (20%):</b> Implementation must meet the optimal or near-optimal time and space complexity specified in the assignment brief. Asymptotic analysis (Big-O, Big-Theta, Big-Omega) with proof must be submitted in the README.", st["bullet"]))
    s.append(Paragraph("• <b>Software Design & Code Quality (15%):</b> Adherence to SOLID principles, clean modular decomposition, meaningful identifier naming (PEP8/Google style for Python; Google C++ Style for C++), appropriate comments, and absence of global state abuse or anti-patterns.", st["bullet"]))
    s.append(Paragraph("• <b>Documentation & Test Coverage (15%):</b> Comprehensive docstrings in Sphinx/Doxygen format, API contract documentation, and a unit test suite using pytest/Google Test achieving ≥ 85% branch coverage verified by coverage.py.", st["bullet"]))
    s.append(Paragraph("• <b>Academic Integrity (15%):</b> MOSS code similarity < 15% across all submitted solutions in the cohort. Submissions exceeding the threshold trigger DAIC review with potential zero-grade and further disciplinary action.", st["bullet"]))

    s.append(Paragraph("4. Laboratory Practical Examination & Comprehensive Viva Voce Rubric", st["h1"]))
    s.append(Paragraph(
        "End-semester laboratory examinations are jointly conducted by the Course Instructor and an "
        "External Examiner appointed by the Dean. A 3-hour practical session evaluates four components:", st["body"]))
    s.append(Paragraph("• <b>Pre-Lab Design & Documentation (20%):</b> Flowchart or pseudocode (Sem I–IV), UML class diagram or schema (Sem V–VIII), algorithm analysis, submitted in the lab record book 15 minutes before the session begins.", st["bullet"]))
    s.append(Paragraph("• <b>Implementation & Execution (40%):</b> Code compiles without errors, runs on the examiner-provided input, produces correct output for all test cases, and handles edge cases (empty input, maximum bounds).", st["bullet"]))
    s.append(Paragraph("• <b>Live Code Walkthrough & Debugging (20%):</b> Student explains their design, traces execution for a chosen input, and makes a minor modification requested by the examiner within 10 minutes.", st["bullet"]))
    s.append(Paragraph("• <b>Viva Voce Technical Defense (20%):</b> 5 oral questions covering underlying theory, design trade-offs, algorithm complexity, alternative approaches, and real-world applications. Depth and correctness of responses evaluated.", st["bullet"]))

    s.append(Paragraph("5. Mini-Project Evaluation Matrix (CS390, Semester V — 2 Credits)", st["h1"]))
    s.append(Paragraph(
        "Semester V teams of 2–3 students design, implement, and demonstrate a functional software "
        "system or embedded hardware-software prototype. Evaluation across 4 review milestones:", st["body"]))
    s.append(Paragraph("• <b>Review 1 — Problem Formulation & Feasibility (15%):</b> Problem statement clarity, domain literature review (≥ 5 academic/industry references), technology stack justification, project timeline (Gantt chart).", st["bullet"]))
    s.append(Paragraph("• <b>Review 2 — Architecture & Design (25%):</b> System architecture diagram, database ER schema or NoSQL data model, API contract (OpenAPI 3.0 spec), unit test plan.", st["bullet"]))
    s.append(Paragraph("• <b>Review 3 — Working Prototype Demonstration (40%):</b> Live demo of core features, code quality review, CI/CD pipeline demonstration, security assessment (basic OWASP scan).", st["bullet"]))
    s.append(Paragraph("• <b>Review 4 — Final Report & Presentation (20%):</b> IEEE-format technical report (≥ 8 pages), PowerPoint presentation, team contribution matrix, reflection on lessons learned.", st["bullet"]))

    s.append(Paragraph("6. Senior Capstone Project Evaluation (CS490, Semesters VII-VIII — 8 Credits)", st["h1"]))
    s.append(Paragraph(
        "B.Tech Capstone Projects are evaluated over two terms by a 3-member Faculty Review Panel "
        "(Primary Supervisor, Second Reader, External Examiner from industry or academia). "
        "Evaluation criteria:", st["body"]))
    s.append(Paragraph("• <b>Problem Formulation & Survey (15%):</b> Research problem novelty, comprehensive literature survey (≥ 20 references), identification of research gaps, measurable success criteria.", st["bullet"]))
    s.append(Paragraph("• <b>System Architecture & Design Spec (25%):</b> HLD (architectural diagram, service boundaries, data flow), LLD (class diagrams, sequence diagrams, DB schema), rationale for design decisions.", st["bullet"]))
    s.append(Paragraph("• <b>Engineering Implementation (30%):</b> Production-ready code with CI/CD pipeline, automated test suite (≥ 90% coverage), performance benchmarks, deployment documentation.", st["bullet"]))
    s.append(Paragraph("• <b>Technical Dissertation (15%):</b> IEEE-format thesis (≥ 40 pages), abstract, methodology, results, critical discussion, future work, Similarity Index < 15%.", st["bullet"]))
    s.append(Paragraph("• <b>Oral Defense & Q&A (15%):</b> 20-minute presentation + 15 minutes of panel Q&A assessing depth of technical understanding and ability to defend design choices.", st["bullet"]))

    s.append(Paragraph("7. M.Tech Thesis & Research Seminar Assessment Rubric", st["h1"]))
    s.append(Paragraph(
        "M.Tech theses (20 credits) are evaluated by an External Examiner and the Thesis Supervisor. "
        "Key criteria: (a) Originality and contribution to knowledge; (b) Research methodology rigor; "
        "(c) Quality of experimental design and validation; (d) Clarity of technical writing; "
        "(e) Viva voce defense quality. Pre-submission similarity index must be < 10% (excluding "
        "references). The Annual Research Seminar (4 credits) is evaluated on: literature survey depth, "
        "critical analysis and synthesis, and oral presentation clarity with slide design.", st["body"]))

    s.append(Paragraph("8. Institutional Letter Grading Scale & SGPA/CGPA Computation", st["h1"]))
    s.append(Paragraph(
        "Northgate Institute adopts a 10-point absolute grading system with relative moderation when "
        "statistically justified. Conversion: 90–100 → O (Outstanding, 10.0); 80–89 → A+ (9.0); "
        "70–79 → A (8.0); 60–69 → B+ (7.0); 55–59 → B (6.0); 50–54 → C (5.0); < 50 → F (0.0). "
        "SGPA = Σ(Credit_i × GradePoint_i) / Σ Credit_i for the current semester. "
        "CGPA = Σ(Credit_i × GradePoint_i) / Σ Credit_i across all completed semesters. "
        "Repeated course grades replace the prior F grade in the CGPA computation.", st["body"]))

    s.append(Paragraph("9. Grade Moderation, Statistical Parity & Inter-Section Equity", st["h1"]))
    s.append(Paragraph(
        "The Departmental Grade Moderation Committee (GMC) convenes within 10 days of end-semester "
        "result preparation. The GMC performs: (a) cross-section comparison of mean, median, and "
        "standard deviation for each course; (b) identification of statistically significant "
        "inter-section disparities (p < 0.05 on Mann-Whitney U test); (c) application of linear "
        "scaling adjustments or addition of a uniform scaling constant when inter-section parity "
        "violations are confirmed; (d) mandatory review of any course with a failure rate exceeding "
        "30% to determine whether course design, assessment calibration, or instructional factors "
        "require intervention.", st["body"]))

    s.append(Paragraph("10. Supplementary Examinations & Grade Improvement Policy", st["h1"]))
    s.append(Paragraph(
        "Students earning an 'F' grade may appear for the Supplementary Examination (conducted during "
        "the subsequent term break). The maximum grade achievable through a supplementary exam is 'B+' "
        "(7.0 grade points), regardless of marks scored, to maintain fairness with students who cleared "
        "the course in the regular examination. Students wishing to improve a passing grade (C or B) "
        "may re-register for the course in the next available offering, forfeiting the prior grade. "
        "The improved grade replaces the original grade in the CGPA computation from the next "
        "semester results onwards.", st["body"]))

    s.append(Paragraph("11. AI Proctoring, Remote Assessment & Digital Examination Integrity", st["h1"]))
    s.append(Paragraph(
        "For online assessments conducted via the DCMP LMS, the University employs AI-based proctoring "
        "tools that monitor: (a) face detection and identity verification via webcam; (b) screen "
        "recording with keystroke logging for suspicious activity (rapid copy-paste, browser tab "
        "switching); (c) audio monitoring for voice input or communication with third parties. "
        "AI proctoring flags are reviewed by the DAIC before any disciplinary action is initiated. "
        "False positives must be appealed within 48 hours of the assessment conclusion.", st["body"]))

    build_pdf(
        os.path.join(DATA_DIR, "faculty", "grading_rubric_2025.pdf"),
        "Standardized Faculty Grading Rubric & Assessment Matrix AY 2025-2026",
        "School of Computing & Engineering | OBE Assessment, Lab Evaluation & Capstone Criteria",
        s, "faculty")


# =============================================================================
# 6. FACULTY — cs_lesson_plan.pdf
# =============================================================================
def generate_cs_lesson_plan():
    st = get_custom_styles()
    s = []

    s.append(Paragraph("1. Departmental Lesson Plan Governance & Submission Requirements", st["h1"]))
    s.append(Paragraph(
        "This Lesson Plan Repository is an official instructional governance document maintained by the "
        "Department of Computer Science & Engineering at Northgate Institute. In accordance with NBA "
        "Tier-1 accreditation criteria (SAR Section 2.1.1) and AICTE Approval Process Handbook 2024-27, "
        "every course instructor must prepare, submit, and execute a structured lesson-by-lesson plan "
        "through DCMP before the end of Orientation Week. The plan must include: (a) Lesson-wise "
        "objectives mapped to Bloom's Taxonomy level and specific Course Outcomes (COs); (b) teaching "
        "methodology (lecture, tutorial, flipped classroom, industry case study, peer review); "
        "(c) prescribed and reference texts; (d) lab exercise list with expected outcomes; and "
        "(e) approximate mark allocation per unit. Deviations from the approved plan exceeding 20% "
        "of contact hours require Head of Department approval.", st["body"]))

    s.append(Paragraph("2. CS301: Database Management Systems — 45-Lecture Blueprint", st["h1"]))
    s.append(Paragraph("<b>Instructor:</b> Dr. Elena Marsh | <b>Credits:</b> 4 (3L-1T-2P) | <b>Semesters:</b> V", st["body"]))
    s.append(Paragraph(
        "<b>Course Outcomes:</b> CO1: Analyze real-world data requirements and design normalized ER "
        "schemas (Bloom L4). CO2: Construct and optimize SQL queries for complex retrieval and "
        "aggregation tasks (L3). CO3: Apply normalization theory to decompose anomalous relations "
        "into BCNF/3NF while preserving dependencies (L3). CO4: Evaluate concurrency control "
        "protocols for correctness and performance trade-offs (L5). CO5: Design indexed access paths "
        "for performance-optimized query plans (L5).", st["body"]))
    s.append(Paragraph(
        "• <b>Unit I — Data Models & ER Design (L1–L9):</b> L1: File systems limitations (redundancy, "
        "isolation, integrity, atomicity failure). L2: Three-schema architecture (external/conceptual/"
        "internal), data independence (logical, physical). L3: Data model categories (relational, "
        "hierarchical, network, object-relational). L4–L5: ER modeling — entities, attributes "
        "(simple, composite, multivalued, derived), relationship sets, cardinality constraints "
        "(1:1, 1:N, M:N), participation constraints (total, partial), weak entity sets. L6–L7: "
        "Extended ER — specialization (disjoint, overlapping), generalization, aggregation, "
        "converting EER to relational tables. L8–L9: 7-step ER-to-Relational Mapping algorithm "
        "with full worked example (university schema).", st["bullet"]))
    s.append(Paragraph(
        "• <b>Unit II — Relational Model & SQL (L10–L18):</b> L10–L12: Relational Algebra — "
        "selection σ, projection π, rename ρ, union ∪, set difference −, Cartesian product ×, "
        "natural join ⋈, theta join, outer joins (left, right, full), division ÷. L13–L14: SQL "
        "DDL (CREATE TABLE, ALTER, DROP, CHECK, UNIQUE, FK with CASCADE), DML (SELECT, FROM, "
        "WHERE, GROUP BY, HAVING, ORDER BY, LIMIT). L15–L17: Advanced SQL — correlated subqueries, "
        "EXISTS/NOT EXISTS, ALL/ANY, set operations (UNION, INTERSECT, EXCEPT), CTEs (WITH clause), "
        "views (updatable conditions), triggers (BEFORE/AFTER, row-level). L18: Window functions "
        "(RANK, DENSE_RANK, ROW_NUMBER, NTILE, LAG, LEAD, FIRST_VALUE, LAST_VALUE, OVER clause "
        "with PARTITION BY and ORDER BY).", st["bullet"]))
    s.append(Paragraph(
        "• <b>Unit III — Normalization Theory (L19–L26):</b> L19–L21: Functional dependencies, "
        "attribute closure algorithm, Armstrong's axioms (proof of soundness and completeness), "
        "canonical cover computation (extraneous attribute removal, FD set minimization). "
        "L22–L24: Normal forms — 1NF (atomic domains), 2NF (no partial dependencies on CK), "
        "3NF (no transitive dependencies on non-prime attributes), BCNF (every determinant is "
        "a superkey), worked examples with relation decomposition. L25–L26: Multi-valued "
        "dependencies (MVDs), 4NF, lossless-join property (Abelian group test), dependency "
        "preservation property, Bernstein's 3NF synthesis algorithm (detailed worked example).", st["bullet"]))
    s.append(Paragraph(
        "• <b>Unit IV — Transaction Processing & Concurrency (L27–L35):</b> L27–L28: Transaction "
        "concept, ACID properties (detailed), transaction states (active, partially committed, "
        "committed, failed, aborted), schedules. L29–L30: Serial and non-serial schedules, conflict "
        "operations, conflict serializability, precedence graph construction and cycle detection. "
        "Recoverability, cascadeless and strict schedules. L31–L33: Locking — shared/exclusive locks, "
        "lock compatibility matrix, 2PL (basic, strict, rigorous), lock conversion, MVCC (snapshot "
        "isolation, read-your-writes), timestamp ordering protocol. L34–L35: Deadlock handling — "
        "prevention (wound-wait, wait-die), detection (wait-for graph, rollback strategy), "
        "ARIES logging and recovery (WAL, checkpoint, analysis, redo, undo passes), CLRs.", st["bullet"]))
    s.append(Paragraph(
        "• <b>Unit V — Storage, Indexing & Optimization (L36–L45):</b> L36–L37: Storage organization "
        "(heap file, sequential file, clustering), buffer pool management (replacement policies: LRU, "
        "Clock, MRU), RAID levels (0, 1, 4, 5, 6). L38–L40: Dense vs sparse indexes, clustered vs "
        "unclustered, B+ tree structure and properties, insertion (split propagation), deletion (merge "
        "and redistribution), bulk loading. L41–L45: Heuristic query optimization — relational algebra "
        "equivalence rules, selection/projection push-down, join ordering. Cost-based optimization "
        "fundamentals: statistics (histogram, NDV), selectivity estimation, join size estimation, "
        "nested loop join, sort-merge join, hash join algorithms and cost models.", st["bullet"]))

    s.append(Paragraph("3. CS340: Operating Systems Architecture — 45-Lecture Blueprint", st["h1"]))
    s.append(Paragraph("<b>Instructor:</b> Dr. Ravi Subramaniam | <b>Credits:</b> 4 (3L-1T-2P) | <b>Semester:</b> V", st["body"]))
    s.append(Paragraph(
        "• <b>Unit I — Process Management & Scheduling (L1–L9):</b> L1: OS roles and structure "
        "(monolithic, microkernel, hybrid, exokernel). L2: Process abstraction, PCB fields, "
        "process lifecycle state machine. L3: System calls, context switch overhead analysis. "
        "L4: Threading — user-mode vs kernel-mode, M:N hybrid model, POSIX pthreads API. "
        "L5–L7: CPU scheduling algorithms — FCFS (convoy effect), SJF/SRTF (preemptive), "
        "Round Robin (quantum trade-offs), Priority (starvation and aging), MLFQ design and "
        "rules (Ousterhout's 3 rules). L8: Real-time scheduling (EDF, RMS, rate monotonic "
        "analysis). L9: Multiprocessor scheduling (load balancing, affinity, NUMA awareness).", st["bullet"]))
    s.append(Paragraph(
        "• <b>Unit II — Synchronization & Deadlock (L10–L18):</b> L10: Race conditions, critical "
        "section requirements (mutual exclusion, progress, bounded waiting). L11: Peterson's "
        "algorithm (proof of correctness), hardware memory barriers, TestAndSet, CompareAndSwap. "
        "L12–L13: Semaphores (binary/counting, P/V operations), mutex locks, monitors (Mesa vs "
        "Hoare semantics), condition variables. L14–L15: Classical sync problems — Producer-Consumer "
        "(3 semaphore solution), Readers-Writers (3 variants with starvation analysis), Dining "
        "Philosophers (Chandy-Misra napkin solution). L16–L17: Deadlock — 4 Coffman conditions, "
        "Resource Allocation Graph (single vs multi-instance), Banker's Algorithm (safety check, "
        "resource request), detection and recovery (rollback strategies). L18: Lock-free and "
        "wait-free data structures (CAS-based stack, Michael-Scott queue), transactional memory.", st["bullet"]))
    s.append(Paragraph(
        "• <b>Unit III — Memory Management & Virtual Memory (L19–L28):</b> L19–L20: Logical vs "
        "physical address, static vs dynamic binding, swapping, contiguous allocation (first fit, "
        "best fit, worst fit), external vs internal fragmentation. L21–L22: Paging — page table "
        "structure, TLB operation, effective access time, multi-level page tables (2-level, 4-level "
        "x86-64), inverted page tables. L23–L24: Segmentation, segment descriptor table, "
        "segmentation+paging (x86). L25–L26: Virtual memory — demand paging, page fault handling "
        "sequence, copy-on-write, thrashing analysis. L27–L28: Page replacement algorithms — "
        "FIFO (Belady's anomaly), Optimal (OPT/MIN), LRU (stack algorithm, working set model), "
        "Clock/Second-Chance approximation, NRU, Working Set Window. Memory-mapped files, "
        "prepaging, page size trade-offs.", st["bullet"]))
    s.append(Paragraph(
        "• <b>Unit IV — File Systems & I/O Subsystems (L29–L36):</b> L29–L30: File abstraction, "
        "directory structure (flat, tree, DAG, symlinks), VFS layer, inode structure (direct, "
        "indirect, double-indirect pointers), hard links vs symbolic links. L31: File allocation "
        "methods (contiguous, linked, indexed, extent-based), free-space management (bitmap, "
        "free list, grouping). L32: File system recovery — fsck algorithm, journaling (write-ahead "
        "log, ordered journal, full data journal), ext4/NTFS/ZFS internals. L33–L34: I/O subsystem "
        "— device drivers, interrupt handling, DMA controller, I/O scheduling for SSDs vs HDDs. "
        "L35–L36: Disk scheduling — SSTF, SCAN, C-SCAN, LOOK, C-LOOK; SSD characteristics "
        "(wear leveling, FTL, garbage collection, TRIM).", st["bullet"]))
    s.append(Paragraph(
        "• <b>Unit V — Security, Protection & Virtualization (L37–L45):</b> L37–L38: Protection "
        "domain, access matrix (ACL, capability list), role-based access control (RBAC), mandatory "
        "access control (MAC — Bell-LaPadula, Biba). L39: Program threats (buffer overflow, "
        "stack smashing, ROP chains, ASLR mitigation). L40: OS security hardening (SELinux, "
        "AppArmor, seccomp-bpf). L41–L42: Virtualization — Type-1 vs Type-2 hypervisors, "
        "hardware-assisted virtualization (Intel VT-x, AMD-V, IOMMU), memory ballooning, "
        "VM live migration. L43–L44: Container internals — Linux namespaces (pid, net, mnt, "
        "uts, ipc, user), cgroups v2 resource limits, overlay filesystems, Docker layered "
        "image architecture, Kubernetes pod lifecycle. L45: Cloud OS design, serverless "
        "runtime (AWS Lambda firecracker microVMs), unikernel architectures.", st["bullet"]))

    s.append(Paragraph("4. CS420: Applied Machine Learning & AI — 45-Lecture Blueprint", st["h1"]))
    s.append(Paragraph("<b>Instructor:</b> Dr. Ananya Krishnan | <b>Credits:</b> 4 (3L-2P) | <b>Semester:</b> VI", st["body"]))
    s.append(Paragraph(
        "• <b>Unit I — Supervised Learning Foundations (L1–L9):</b> L1–L2: ML paradigm (supervised, "
        "unsupervised, self-supervised, RL), PAC learning theory, hypothesis spaces, empirical risk "
        "minimization. L3–L4: Linear Regression (OLS derivation, normal equations, closed-form "
        "solution, gradient descent update rule, stochastic and mini-batch GD). L5: Regularization "
        "(Ridge L2 — Tikhonov, Lasso L1 — sparsity, ElasticNet), bias-variance decomposition "
        "proof. L6–L7: Model evaluation — k-fold cross-validation, stratified CV, learning "
        "curves, hyperparameter tuning (grid search, random search, Bayesian optimization with "
        "Gaussian Processes). L8–L9: Logistic Regression (sigmoid derivation, MLE, softmax "
        "multi-class, decision boundaries).", st["bullet"]))
    s.append(Paragraph(
        "• <b>Unit II — Classification & Ensemble Methods (L10–L18):</b> L10–L11: Decision Trees "
        "(CART, ID3, C4.5, information gain, entropy, Gini impurity, pruning strategies, "
        "minimum description length). L12–L13: Ensemble methods — bagging (variance reduction), "
        "Random Forests (feature sub-sampling, out-of-bag error, feature importance). L14–L15: "
        "Gradient Boosting — functional gradient descent, AdaBoost, XGBoost (tree structure "
        "optimization, L1/L2 regularization, column sub-sampling, weighted quantile sketch), "
        "LightGBM (GOSS, EFB, leaf-wise growth), CatBoost (ordered boosting). L16–L17: Support "
        "Vector Machines — maximum margin classifier, soft margin (C parameter), kernel trick "
        "(Mercer's theorem), RBF kernel, polynomial, sigmoid, dual formulation and KKT conditions. "
        "L18: SVM multi-class (OvR, OvO), calibration (Platt scaling, isotonic regression).", st["bullet"]))
    s.append(Paragraph(
        "• <b>Unit III — Deep Neural Networks (L19–L27):</b> L19: Perceptron, MLP motivation, "
        "universal approximation theorem. L20: Activation functions — sigmoid, tanh, ReLU "
        "(dying ReLU problem), Leaky ReLU, ELU, GELU, Swish, PReLU. L21: Backpropagation — "
        "computational graph, chain rule derivation, vanishing/exploding gradients. L22: "
        "Weight initialization (Xavier/Glorot for sigmoid/tanh, He/Kaiming for ReLU), batch "
        "normalization (internal covariate shift, running mean/variance, γ/β parameters), "
        "layer normalization, dropout (Bernoulli mask, inverted dropout). L23: Optimizers — "
        "SGD with momentum, RMSProp, Adam (bias correction), AdamW (decoupled weight decay), "
        "learning rate schedules (cosine annealing, warm restart, one-cycle). L24–L25: CNNs — "
        "convolution operation (cross-correlation, filter banks, feature maps), pooling, receptive "
        "field computation, modern architectures (AlexNet, VGG, ResNet — residual connections and "
        "vanishing gradient solution, EfficientNet — compound scaling). L26: Sequence models — "
        "RNNs (BPTT, vanishing gradient), LSTM (forget, input, output gates, cell state), GRU "
        "(simplified gating). L27: Attention mechanism (scaled dot-product, multi-head attention), "
        "Transformer encoder-decoder, positional encoding, BERT (masked LM, NSP), GPT (autoregressive "
        "language modeling), parameter-efficient fine-tuning (LoRA, prefix tuning).", st["bullet"]))
    s.append(Paragraph(
        "• <b>Unit IV — Unsupervised Learning & Generative Models (L28–L36):</b> L28: Clustering "
        "objectives, K-Means algorithm (Lloyd's), K-Means++ initialization, Elbow method, "
        "Silhouette score. L29: DBSCAN (ε-neighborhood, MinPts, core/border/noise points, "
        "algorithm complexity), HDBSCAN. L30: Hierarchical clustering (agglomerative with "
        "dendrograms, Ward/average/complete linkage). L31: Dimensionality reduction — PCA "
        "(covariance eigendecomposition, scree plot, variance explained, reconstruction error), "
        "kernel PCA, LDA. L32: Non-linear DR — t-SNE (KL divergence minimization, perplexity, "
        "crowding problem), UMAP (topological data analysis, manifold learning). L33: Anomaly "
        "detection — Isolation Forest, One-Class SVM, Autoencoder reconstruction error. "
        "L34–L35: Generative models — Variational Autoencoders (ELBO, reparameterization trick), "
        "GANs (min-max game, mode collapse, Wasserstein GAN), Diffusion Models (DDPM, "
        "score matching, DDIM). L36: Large-scale clustering and vector databases for RAG "
        "applications (Faiss, Qdrant, Weaviate).", st["bullet"]))
    s.append(Paragraph(
        "• <b>Unit V — Responsible AI, Evaluation & Production (L37–L45):</b> L37–L38: Evaluation "
        "metrics — confusion matrix, Precision/Recall/F1, Matthews CC, ROC-AUC, PR curve, "
        "Cohen's Kappa, calibration (reliability diagram, ECE, MCE). L39: Class imbalance "
        "handling — SMOTE, ADASYN, cost-sensitive learning, threshold optimization. L40: "
        "Responsible AI — fairness metrics (demographic parity, equalized odds, individual "
        "fairness), bias auditing (AIF360), model documentation (model cards). L41: "
        "Explainability — SHAP (TreeSHAP, KernelSHAP), LIME, Integrated Gradients, "
        "attention visualization, saliency maps. L42–L43: ML Ops — experiment tracking "
        "(MLflow), model registry, feature stores, data versioning (DVC), CI/CD for ML "
        "(GitHub Actions + Docker). L44–L45: LLMs in production — retrieval-augmented "
        "generation (RAG) architecture, vector search (ANN algorithms: HNSW, IVF), "
        "embedding models, chunking strategies, re-ranking, evaluation (RAGAs framework).", st["bullet"]))

    s.append(Paragraph("5. CS460: System Design LLD & HLD — Lesson-by-Lesson Blueprint", st["h1"]))
    s.append(Paragraph("<b>Instructor:</b> Dr. Vikram Nair | <b>Credits:</b> 4 (3L-2 Design Studio) | <b>Semester:</b> VI", st["body"]))
    s.append(Paragraph(
        "• <b>Lesson 1 — System Design Fundamentals & Scalability:</b> Vertical scaling (CPU/RAM "
        "upgrade limits), horizontal scaling (commodity hardware, stateless service design). "
        "Latency vs throughput (Little's Law: L = λW), tail latency percentiles (P50/P95/P99), "
        "SLA vs SLO vs SLI. Load balancing — Layer-4 (TCP/IP) vs Layer-7 (HTTP/gRPC), algorithms "
        "(round-robin, least-connections, IP hash, consistent hashing, rendezvous hashing). "
        "Consistent hashing ring: virtual nodes, load distribution analysis. CAP Theorem: "
        "network partition unavoidability proof, CP systems (HBase, Zookeeper, etcd), AP systems "
        "(Cassandra, CouchDB, DynamoDB). PACELC extension. BASE properties. High availability "
        "patterns: active-passive vs active-active, multi-AZ deployment.", st["bullet"]))
    s.append(Paragraph(
        "• <b>Lesson 2 — Low-Level Design: SOLID & OOP:</b> Encapsulation, abstraction, "
        "inheritance (fragile base class problem), polymorphism (subtype and parametric). "
        "SOLID principles in depth: SRP (cohesion metric, single axis of change), OCP "
        "(extension without modification — strategy pattern implementation), LSP (Liskov "
        "substitution formal definition, covariance/contravariance), ISP (fat interface "
        "anti-pattern, role interfaces), DIP (dependency injection frameworks — Spring, "
        "Guice). Composition over inheritance principle. YAGNI and DRY principles. "
        "UML modeling: Class diagram (association, aggregation, composition, dependency, "
        "realization, generalization multiplicities), Sequence diagram (lifelines, messages, "
        "activation bars, alt/loop/opt fragments), State Machine diagram, Activity diagram.", st["bullet"]))
    s.append(Paragraph(
        "• <b>Lesson 3 — Low-Level Design: Design Patterns Practicum:</b> Creational: "
        "Thread-safe Singleton (double-checked locking, Bill Pugh initialization-on-demand), "
        "Factory Method (defer instantiation to subclasses), Abstract Factory (product families), "
        "Builder (fluent API, Director class), Prototype (deep vs shallow clone). "
        "Structural: Adapter (object vs class adapter), Bridge (decouple abstraction from "
        "implementation), Composite (tree structures, uniform leaf/branch treatment), "
        "Decorator (dynamic responsibility addition, Java I/O streams), Facade (subsystem "
        "simplification), Proxy (virtual, remote, protection proxy types). "
        "Behavioral: Strategy (algorithm family encapsulation — sorting strategies, payment "
        "processors), Observer (Event bus, reactive programming, Pub-Sub with weak references), "
        "Command (undo/redo history, macro recording), Template Method (Hollywood principle), "
        "Iterator (internal vs external, lazy sequences), State Machine (vending machine, "
        "order state transitions), Mediator (chat room, air traffic control), "
        "Chain of Responsibility (logging filter chain, HTTP middleware pipeline). "
        "Full case study: Enterprise Parking Lot System design — entry/exit gates, vehicle "
        "types (two-wheeler, four-wheeler, heavy vehicle), spot allocation strategy, pricing "
        "engine (hourly/flat-rate/subscription), ParkingTicket, PaymentProcessor, "
        "SecurityCamera integration.", st["bullet"]))
    s.append(Paragraph(
        "• <b>Lesson 4 — High-Level Design: Storage, Sharding & Caching:</b> SQL vs NoSQL "
        "decision framework (ACID requirements, schema flexibility, query patterns, scale). "
        "NoSQL taxonomy: document (MongoDB), key-value (Redis, DynamoDB), columnar (Cassandra, "
        "HBase), graph (Neo4j). Replication: synchronous (strong consistency, write latency), "
        "asynchronous (eventual consistency, replication lag), semi-synchronous; leader-follower "
        "vs multi-leader vs leaderless (quorum: W+R > N). Database sharding strategies: "
        "range sharding (hot shard problem), hash sharding (modulo vs consistent hash), "
        "directory-based sharding (shard map service). Cross-shard joins and distributed "
        "transactions overhead. Caching topologies: Cache-Aside (lazy loading), Read-Through "
        "(synchronous population), Write-Through (strong consistency), Write-Behind (async "
        "flush, durability risk). Eviction policies: LRU (LinkedHashMap implementation), "
        "LFU (min-heap + frequency map), CLOCK. Redis data structures (string, hash, list, "
        "set, sorted set, stream, geo) and their use cases. CDN edge caching: cache-control "
        "headers, TTL, origin shield, invalidation strategies.", st["bullet"]))
    s.append(Paragraph(
        "• <b>Lesson 5 — High-Level Design: Distributed Systems & Microservices:</b> Monolith "
        "decomposition patterns: Strangler Fig, Anti-Corruption Layer, Branch by Abstraction. "
        "Domain-Driven Design: bounded contexts, context maps, aggregates, domain events. "
        "API Gateway: authentication (JWT/OAuth2), rate limiting (Token Bucket, Leaky Bucket, "
        "Sliding Window Counter), request aggregation, SSL termination. Circuit Breaker pattern "
        "(Closed/Open/Half-Open states, failure threshold, Hystrix/Resilience4j). Service Mesh: "
        "sidecar proxy (Envoy), mTLS, observability (Prometheus metrics, Jaeger distributed "
        "tracing, ELK logs). Message queues: Apache Kafka architecture (brokers, topics, "
        "partitions, consumer groups, ISR, log compaction, exactly-once semantics), RabbitMQ "
        "(exchanges, bindings, AMQP). Distributed transactions: Two-Phase Commit (coordinator "
        "failure problem), SAGA pattern (orchestration vs choreography, compensating transactions). "
        "Distributed consensus: Raft protocol (leader election, log replication, commit rule, "
        "safety proof), Paxos comparison. API design: REST constraints (HATEOAS, versioning "
        "strategies), gRPC (Protocol Buffers, bidirectional streaming), GraphQL (N+1 problem, "
        "DataLoader batching). Idempotency keys for exactly-once client retries.", st["bullet"]))
    s.append(Paragraph(
        "• <b>Lesson 6 — End-to-End System Design Case Studies:</b> "
        "(1) Distributed URL Shortener (TinyURL scale: 100M writes/day, 1B reads/day): "
        "Base62 encoding, Key Generation Service (pre-generated key pool), Redis cache for "
        "hot URLs, Cassandra for URL metadata, CDN for redirect headers, analytics pipeline "
        "(Kafka → Flink → ClickHouse). "
        "(2) Real-Time Push Notification System (1B subscribers, 10M pushes/minute): "
        "WebSocket connection server with sticky load balancing, FCM/APNS integration, "
        "notification deduplication (Redis Bloom Filter), priority queues (Kafka), "
        "retry with exponential backoff, delivery receipt tracking. "
        "(3) Distributed Online Examination Proctoring Platform: "
        "Auto-scaling WebRTC streaming servers (Kubernetes HPA), AI-based anomaly detection "
        "(eye-tracking, background noise analysis), immutable blockchain audit log for exam "
        "answers (Hyperledger Fabric), S3 video recording with lifecycle policies, "
        "real-time grading pipeline. "
        "(4) Social Photo-Sharing Platform (Instagram scale: 500M DAU): "
        "Hybrid feed generation (push fanout for celebrities, pull for normal users, "
        "threshold-based switching), CDN image storage with WebP transcoding, Cassandra "
        "denormalized follow graph, Elasticsearch for hashtag search.", st["bullet"]))

    s.append(Paragraph("6. Active Learning Pedagogies, Lab Rotation & Reference Texts", st["h1"]))
    s.append(Paragraph(
        "All courses integrate flipped classroom pre-lecture videos (15-minute YouTube playlists), "
        "peer code review sessions (pair programming rubric), industry guest lectures (minimum "
        "3 per semester per course from T&P industry panel), and competitive programming practice "
        "(LeetCode company-tagged problems aligned to each unit). "
        "Reference Texts: (1) Silberschatz, Korth & Sudarshan — Database System Concepts, 7th Ed.; "
        "(2) Silberschatz, Galvin & Gagne — Operating System Concepts, 10th Ed.; "
        "(3) Christopher Bishop — Pattern Recognition and Machine Learning; "
        "(4) Ian Goodfellow, Bengio & Courville — Deep Learning; "
        "(5) Martin Kleppmann — Designing Data-Intensive Applications; "
        "(6) Alex Xu — System Design Interview: An Insider's Guide (Vols. I & II); "
        "(7) Gamma, Helm, Johnson & Vlissides — Design Patterns: Elements of Reusable OO Software; "
        "(8) Michael Nygard — Release It! Design and Deploy Production-Ready Software, 2nd Ed.", st["body"]))

    build_pdf(
        os.path.join(DATA_DIR, "faculty", "cs_lesson_plan.pdf"),
        "Department of Computer Science — Master Lesson Plan Repository AY 2025-2026",
        "Semesters V & VI | DBMS, Operating Systems, Machine Learning & System Design LLD/HLD",
        s, "faculty")


# =============================================================================
# 7. ADVISOR — student_academic_advising.pdf
# =============================================================================
def generate_student_academic_advising():
    st = get_custom_styles()
    s = []

    s.append(make_callout(
        "<b>STATUTORY FERPA EDUCATION RECORD — RESTRICTED ACCESS.</b> This academic advising dossier "
        "contains confidential student counseling notes, degree audit reports, prerequisite waiver "
        "petitions, major change evaluations, and graduation clearance memos. Access is restricted "
        "to authorized Academic Advisors, the Office of the Registrar, and the Dean of Academic "
        "Affairs. Unauthorized disclosure constitutes a breach of the University Data Governance "
        "Policy and applicable education records privacy laws.",
        st, bg_color="#FEF2F2", border_color="#FCA5A5"))

    s.append(Paragraph("1. Academic Advising Philosophy, Framework & Institutional Goals", st["h1"]))
    s.append(Paragraph(
        "Academic Advising at Northgate Institute of Technology constitutes a developmental, "
        "educational partnership between assigned faculty mentors and enrolled scholars. Drawing on "
        "the National Academic Advising Association (NACADA) Core Competencies and the NEP 2020 "
        "emphasis on holistic student development, the Office of Academic Advising (OAA) has "
        "transitioned from transactional (course-selection-only) advising toward a comprehensive "
        "model encompassing: academic performance monitoring, career pathway exploration, mental "
        "well-being integration, early-intervention for at-risk students, and international "
        "opportunity development.", st["body"]))
    s.append(Paragraph(
        "The AI-augmented advising platform integrated in AY 2025-2026 (powered by the DCMP "
        "Analytics Dashboard) enables early identification of at-risk students by tracking "
        "engagement metrics: LMS login frequency, assignment submission timeliness, attendance "
        "patterns, and quiz performance trajectories. The platform generates automated 'Early "
        "Alert Notifications' for advisors when a student's composite risk score crosses the "
        "defined intervention threshold. However, all consequential advising decisions are made "
        "by human faculty advisors in direct consultation with the student.", st["body"]))
    s.append(Paragraph(
        "Each student is assigned a permanent Faculty Advisor upon first-semester registration. "
        "Advisors are responsible for: (a) mandatory pre-registration conference each semester; "
        "(b) monitoring automated academic warning alerts via DCMP; (c) signing degree audit "
        "clearance forms; (d) endorsing prerequisite waiver petitions; and (e) submitting "
        "semester progress notes to the advising dossier within 7 days of each scheduled meeting. "
        "Faculty maintaining insufficient advising records for assigned students are flagged by "
        "the Advising Quality Assurance Committee during its mid-semester audit.", st["body"]))

    s.append(Paragraph("2. Advising Case File: Marcus D. Whitfield (Roll No: 2023BCSE042)", st["h1"]))
    s.append(Paragraph(
        "<b>Programme:</b> B.Tech CSE, Year 3 (Junior) | <b>Advisor:</b> Dr. Robert Hughes, Assoc. Prof. "
        "<b>Standing:</b> Academic Probation — Term 2 | <b>CGPA After Semester IV:</b> 5.42/10.0 "
        "<b>Active Backlogs:</b> CS210 Discrete Math (F), CS240 Computer Architecture (F)", st["body"]))
    s.append(Paragraph(
        "<b>Conference Summary (August 8, 2025):</b> Student attended the mandatory Pre-Semester "
        "Advising Conference at 10:30 AM in Room 214B, CSE Building. This is the student's second "
        "consecutive semester on Academic Probation following a CGPA decline from 6.82 (Sem I–II) "
        "to 5.42 by Sem IV. Comprehensive diagnostic dialogue revealed a pattern of chronic "
        "foundational deficiencies in discrete mathematics (formal proofs, graph theory) and "
        "computer architecture (pipeline hazards, cache organization) that were not identified or "
        "remediated during the freshman and sophomore years. Contributing factors: excessive "
        "extracurricular leadership roles (served as Technical Secretary, IEEE-CS chapter) "
        "creating unsustainable time commitments; poor examination preparation strategy (cramming "
        "in the 48 hours before exams with no spaced repetition); reported family financial "
        "pressures causing part-time employment (10 hours/week).", st["body"]))
    s.append(Paragraph(
        "<b>Intervention Plan Executed:</b> (1) Administrative credit cap set to 12 credits for "
        "Monsoon 2025 (CS301 DBMS, CS340 OS, PE-01 Professional Elective). (2) Mandatory "
        "Academic Support Center attendance 4 hours per week (Monday 3-5 PM for proofs, "
        "Wednesday 3-5 PM for systems). (3) Assigned peer tutor: Teaching Assistant Vikram "
        "Seth (Ph.D. scholar, CS Systems lab). (4) Formal petition approved for Summer Term "
        "re-registration of CS210. (5) Student requested and received Emergency Financial Aid "
        "Bridge Grant referral (Office of Financial Aid). (6) Mandatory withdrawal from all "
        "IEEE chapter executive roles for the duration of probation. (7) Bi-weekly check-in "
        "scheduled: every second and fourth Tuesday 2:00 PM.", st["body"]))
    s.append(Paragraph(
        "<b>Advisor Assessment:</b> Student demonstrates strong intrinsic motivation and genuine "
        "commitment to improvement. The gap appears primarily due to inadequate foundational "
        "scaffolding rather than intellectual inability. Prognosis is cautiously optimistic "
        "provided the prescribed interventions are followed consistently.", st["body"]))

    s.append(Paragraph("3. Advising Case File: Priya S. Nandakumar (Roll No: 2023BCSE018)", st["h1"]))
    s.append(Paragraph(
        "<b>Programme:</b> B.Tech CSE (Honors Track — AI & ML Specialization), Year 3 "
        "<b>Advisor:</b> Dr. Elena Marsh | <b>Standing:</b> Good Standing | <b>CGPA:</b> 9.31/10.0 "
        "<b>Honors Research Stream:</b> Enrolled (Thesis Supervisor: Dr. Ananya Krishnan)", st["body"]))
    s.append(Paragraph(
        "<b>Conference Summary (August 6, 2025):</b> Student attended pre-semester advising "
        "conference on August 6. Advisor approved credit overload petition to register 26 credits "
        "in Semester V (includes 2 additional graduate-level courses: CS501 NLP and CS522 "
        "Distributed Databases, taken as audit-plus-credit under the Honors Track provisions). "
        "Student is currently co-authoring a paper on 'Adaptive RAG with Role-Filtered Vector "
        "Retrieval' under Dr. Krishnan's supervision, targeting submission to ACL 2026 Rolling "
        "Review. Advisor provided detailed guidance on: (a) GRE Subject Test preparation "
        "(Computer Science) — recommended 3-month structured schedule; (b) international PhD "
        "program shortlisting (Stanford, CMU, MIT, ETH Zurich, IIT Bombay Direct PhD); "
        "(c) NSF-funded research exchange opportunity with University of Massachusetts Amherst "
        "(letter of support from Dr. Krishnan already in process).", st["body"]))

    s.append(Paragraph("4. Advising Case File: Devon K. Ramirez (Roll No: 2024BDSE009)", st["h1"]))
    s.append(Paragraph(
        "<b>Programme:</b> B.Tech Data Science & Engineering, Year 2 (Sophomore) "
        "<b>Advisor:</b> Dr. Sarah Jenkins | <b>Standing:</b> Academic Probation — Term 1 "
        "<b>CGPA After Semester II:</b> 5.88/10.0 | <b>Active Backlogs:</b> MA102 Engineering "
        "Mathematics II (F), EE101 Basic Electrical Eng. (D)", st["body"]))
    s.append(Paragraph(
        "<b>Conference Summary (September 2, 2025):</b> Review revealed significant transition "
        "difficulties — student excelled in school (93rd percentile at regional CBSE board) but "
        "is struggling with the pace and depth of university-level mathematics. The advisor "
        "utilized the Early Alert data from DCMP showing Devon's LMS engagement dropped to "
        "28% in weeks 7–10 of Semester II (corresponding to the Fourier Transform and Complex "
        "Analysis units of MA102). Reported test anxiety manifesting as blanking during "
        "examination scenarios, confirmed by Student Wellness Cell intake assessment. "
        "<b>Intervention Plan:</b> 14-credit cap (MA102 repeat, CS201, CS210, PE-00 Intro "
        "to Data Science Lab). Enrollment in University Mathematics Clinic (Monday/Friday "
        "5–6 PM). Weekly study-log submission to advisor signed by course instructors. "
        "Student Wellness Center referral for 6-session CBT-based test anxiety program. "
        "Assigned peer mentor: Senior (Year 4) student Meera Iyer (Data Science, CGPA 8.7) "
        "through the Culturally Responsive Peer Mentorship Programme.", st["body"]))

    s.append(Paragraph("5. Advising Case File: Aaliyah R. Foster (Roll No: 2022BSE014)", st["h1"]))
    s.append(Paragraph(
        "<b>Programme:</b> B.Tech Software Engineering, Year 4 (Senior) "
        "<b>Advisor:</b> Dr. Robert Hughes | <b>Standing:</b> Good Standing "
        "<b>CGPA:</b> 8.84/10.0 | <b>Status:</b> Graduation Clearance Audit — Spring 2026", st["body"]))
    s.append(Paragraph(
        "<b>Degree Audit Summary (August 12, 2025):</b> Comprehensive degree audit confirms "
        "Aaliyah has successfully completed all 160 required graduation credits: BSC (24 Cr "
        "complete, GPA 8.5), ESC (20 Cr, GPA 8.9), HSMC (12 Cr, GPA 9.1), PCC (64 Cr, "
        "GPA 8.7), PEC — Cloud & Cybersecurity Track (20 Cr, GPA 9.0), OEC (8 Cr, GPA 8.8), "
        "PROJ — Mini Project (2 Cr, A+), Internship at TCS Innovation Labs Bangalore (2 Cr, "
        "A+), Capstone Phase I defense: Approved with Distinction (faculty vote: 3/3 Excellent). "
        "Zero outstanding backlogs. Library Hold: cleared. Bursar account: fully settled. "
        "<b>Status: CLEARED FOR GRADUATION — June 2026 Convocation.</b> "
        "Career advising: Student has 2 offers — TCS Research (Rs. 11.2 LPA) and a pre-placement "
        "offer from Capgemini Engineering (Rs. 9.8 LPA). Advisor provided nuanced guidance on "
        "weighing growth trajectory, learning opportunities, and work-life considerations. "
        "Also discussed a 2-year deferred Master's track application timeline.", st["body"]))

    s.append(Paragraph("6. Advising Case File: Jordan A. Vance (Roll No: 2022BCE021)", st["h1"]))
    s.append(Paragraph(
        "<b>Programme:</b> B.Tech Computer Engineering, Year 4 <b>Advisor:</b> Dr. Ravi Subramaniam "
        "<b>Standing:</b> Good Standing | <b>CGPA:</b> 7.48/10.0", st["body"]))
    s.append(Paragraph(
        "<b>Conference Summary (August 14, 2025):</b> Final year advising focused on capstone "
        "project scope validation. Project: 'FPGA-Accelerated Real-Time Object Detection for "
        "Autonomous Vehicles using Quantized Neural Networks.' Advisor approved scope as technically "
        "rigorous and industry-relevant. Directed student to Dr. Vance (ECE) for FPGA co-supervision "
        "and arranged lab access to the VLSI Design Lab (Xilinx Ultrascale+ boards). Placement "
        "advising: Jordan is targeting embedded systems and hardware engineering roles at NVIDIA, "
        "Qualcomm, and Intel. T&P cell notified to flag Jordan's profile for hardware-track drives.", st["body"]))

    s.append(Paragraph("7. Prerequisite Waiver & Course Substitution Petition Procedures", st["h1"]))
    s.append(Paragraph(
        "A student may petition to enroll in an upper-division course without satisfying the "
        "formal prerequisite under three recognized justifications: (a) Demonstrated Equivalent "
        "Competency — supported by professional internship deliverables, external course "
        "transcripts from an accredited institution, or research publications directly relevant "
        "to prerequisite content; (b) Academic Bank of Credits Transfer — course equivalency "
        "established through the national ABC portal (NEP 2020 framework); (c) Special Research "
        "Programme Admission — Ph.D. and M.Tech students whose research areas directly require "
        "specific upper-division undergraduate courses may waive prerequisites with Department "
        "Research Committee endorsement.", st["body"]))
    s.append(Paragraph(
        "The petition workflow: (1) Student submits Waiver Form to Course Instructor with "
        "supporting evidence. (2) Instructor provides written assessment of equivalency. "
        "(3) Head of Department reviews and approves/denies. (4) Registrar records approved "
        "substitution in the student's digital degree audit file with documentation. All "
        "approved waivers are noted with the substituted course code, credit equivalency, "
        "justification category, and signatures of Instructor, HoD, and Curriculum Chair.", st["body"]))

    s.append(Paragraph("8. Major Declaration, Branch Transfer & NEP Dual Degree Pathways", st["h1"]))
    s.append(Paragraph(
        "Inter-departmental branch transfer applications are accepted at the end of Semester II "
        "for entry into Semester III of the target department. Eligibility: CGPA >= 8.50 with "
        "zero backlogs, subject to available seats (capped at 10% of sanctioned intake of the "
        "destination department). Transfer students carry forward all completed credits subject "
        "to equivalency mapping by the Curriculum Chair. Applications for the Integrated B.Tech "
        "+ M.Tech Dual Degree Programme (5 years, 200 credits) are evaluated in Semester IV "
        "based on CGPA >= 8.00, faculty recommendation letters, and a short technical interview "
        "before the Departmental Admissions Panel.", st["body"]))

    s.append(Paragraph("9. Study Abroad, Exchange Semester & Credit Transfer Protocols", st["h1"]))
    s.append(Paragraph(
        "Northgate Institute has active MoU exchange agreements with 14 international partner "
        "universities (including TU Delft, KTH Stockholm, NUS Singapore, University of Toronto, "
        "and KAIST). Students in Good Standing with CGPA >= 7.50 may apply for a one-semester "
        "exchange in Semesters VI or VII. Course syllabi, credit hours, and laboratory components "
        "of courses taken abroad are assessed by the Registrar's International Equivalency "
        "Committee against the home curriculum. A maximum of 24 transfer credits may be applied "
        "toward degree requirements. Transferred grades appear as 'P' (Pass) on the official "
        "transcript without impacting the CGPA divisor.", st["body"]))

    build_pdf(
        os.path.join(DATA_DIR, "advisor", "student_academic_advising.pdf"),
        "Student Academic Advising Dossiers & Degree Audit Records AY 2025-2026",
        "Office of Academic Advising & Registrar | Certified Case Notes, Interventions & Progress",
        s, "advisor")


# =============================================================================
# 8. ADVISOR — academic_standing_interventions.pdf
# =============================================================================
def generate_academic_standing_interventions():
    st = get_custom_styles()
    s = []

    s.append(make_callout(
        "<b>STRICTLY CONFIDENTIAL — ACADEMIC STANDING INTERVENTION DOSSIER.</b> This document "
        "contains formal diagnostic evaluations, cognitive remedial strategies, peer tutoring "
        "session logs, and Academic Standing Committee deliberation records for students subject "
        "to Academic Warning, Probation, or Suspension. Access is restricted to the assigned "
        "Faculty Advisor, Academic Standing Board, Registrar, and Dean of Academic Affairs.",
        st, bg_color="#FEF2F2", border_color="#FCA5A5"))

    s.append(Paragraph("1. Academic Standing Framework, Tier Definitions & Early Warning System", st["h1"]))
    s.append(Paragraph(
        "Northgate Institute's Academic Standing Framework reflects current best practices in "
        "university student success research, specifically drawing on the MDRC's CUNY ASAP model "
        "and AI-augmented early intervention systems adopted at forward-thinking institutions since "
        "2024. The framework operates on a 4-tier classification updated at the end of each semester "
        "by the Registrar's office:", st["body"]))
    s.append(Paragraph(
        "• <b>Tier 1 — Good Standing:</b> Cumulative CGPA >= 6.00/10.0 with normal credit completion "
        "velocity (completing ≥ 75% of registered credits each semester). No action required.", st["bullet"]))
    s.append(Paragraph(
        "• <b>Tier 2 — Academic Warning:</b> Semester SGPA < 5.50 while cumulative CGPA remains "
        ">= 6.00; OR completion rate drops below 75% for the first time. Triggers: automated DCMP "
        "alert to student and advisor; mandatory advisor conference within 10 days of result "
        "publication; recommended (non-mandatory) load reduction; referral to Student Wellness "
        "Center for academic stress screening.", st["bullet"]))
    s.append(Paragraph(
        "• <b>Tier 3 — Academic Probation:</b> Cumulative CGPA < 6.00; OR two consecutive "
        "semesters at Academic Warning. Requires: mandatory signed Academic Recovery Contract (ARC) "
        "within 10 working days of semester commencement; administrative registration cap of 14 "
        "credits; mandatory 3 hours/week Academic Support Center attendance with verified sign-in "
        "log; bi-weekly advisor conferences; disqualification from extracurricular leadership "
        "positions and external competition representation; Bursar Hold exemption review for "
        "financial aid recipients.", st["bullet"]))
    s.append(Paragraph(
        "• <b>Tier 4 — Academic Suspension:</b> Cumulative CGPA < 5.00 for three consecutive "
        "semesters; OR accumulated uncompleted credits exceeding 24 (more than 1.5 semesters "
        "of normal load). Triggers: 1-year mandatory academic separation; hostel room must be "
        "vacated within 15 days; student may petition the Standing Committee for reinstatement "
        "during the January or August review windows.", st["bullet"]))

    s.append(Paragraph("2. AI-Augmented Early Warning System: Technical Architecture", st["h1"]))
    s.append(Paragraph(
        "The DCMP Early Alert system integrates data from 6 sources — LMS engagement logs, "
        "attendance biometric records, assignment submission timestamps, quiz performance "
        "trajectories, library access frequency, and counseling center self-referral — to "
        "compute a composite 'Academic Risk Score' (ARS) on a 0–100 scale. An ARS ≥ 65 in "
        "any rolling 3-week window triggers an automatic Level-1 alert to the faculty advisor. "
        "An ARS ≥ 80 triggers a Level-2 alert also escalated to the Head of Department. The "
        "system was trained on 8 years of anonymized historical data (N = 42,000 student-"
        "semester observations) and achieves a precision of 0.81 and recall of 0.78 for "
        "identifying students who ultimately require formal probation intervention. Advisors "
        "are required to act on all Level-1 and Level-2 alerts within 5 working days.", st["body"]))

    s.append(Paragraph("3. Diagnostic Case Study: Marcus D. Whitfield (Term 2 Probation)", st["h1"]))
    s.append(Paragraph(
        "<b>CGPA Trajectory:</b> Sem I: 7.12 → Sem II: 6.89 → Sem III: 6.41 → Sem IV: 5.42 "
        "(decline of 1.70 grade points over 4 semesters, constituting a 24% cumulative drop). "
        "<b>Root Cause Analysis:</b> Comprehensive diagnostic evaluation (standardized learning "
        "style inventory, mathematics anxiety scale — MAS-R, time-management self-efficacy "
        "questionnaire) confirmed: (1) Mathematical proof construction anxiety — scoring at the "
        "78th percentile on MAS-R, indicating high mathematics anxiety specifically in "
        "formal-proof contexts; (2) Ineffective retrieval practice — student reports highlighting "
        "textbook notes rather than active recall; (3) Leadership role overcommitment — serving "
        "as Technical Secretary of IEEE-CS Chapter required an estimated 18 hours/week during "
        "Semester IV (confirmed by student self-report); (4) Part-time employment — 10 hours/week "
        "at a private tutoring center for supplemental income due to reported family financial "
        "pressure.", st["body"]))
    s.append(Paragraph(
        "<b>Remedial Prescription (Academic Recovery Contract Terms):</b> "
        "(1) Term credit cap: 12 credits (CS301, CS340, PE-01 only). "
        "(2) Peer tutor assignment: TA Vikram Seth — 3 hours/week, Tuesday/Thursday 4-5:30 PM, "
        "focused on formal proofs, data structure analysis, and OS concurrency concepts. "
        "(3) Academic Support Center mandatory attendance: Monday 3-5 PM (Mathematical Reasoning "
        "Clinic), Wednesday 3-5 PM (Systems Programming Workshop). Attendance log must be "
        "submitted to advisor by Friday 5 PM each week. "
        "(4) Study strategy restructuring: Advisor prescribed the Leitner flashcard system "
        "for concept retention, Feynman technique for complex proofs, and the Pomodoro "
        "technique (25-min focused blocks) for time management. "
        "(5) Financial Aid Bridge Grant referral: student connected with the Emergency "
        "Student Welfare Relief Fund to reduce employment hours. "
        "(6) Progress review: bi-weekly advisor conferences (2nd and 4th Tuesday, 2 PM).", st["body"]))

    s.append(Paragraph("4. Diagnostic Case Study: Devon K. Ramirez (Term 1 Probation)", st["h1"]))
    s.append(Paragraph(
        "<b>Root Cause Analysis:</b> Adaptive diagnostic testing (administered via DCMP "
        "diagnostic module) revealed performance breakdowns in: (a) Multivariable calculus "
        "(surface integrals, vector fields) — score at 23rd percentile; (b) Complex number "
        "theory applications in signal processing — 19th percentile; (c) Basic circuit analysis "
        "(Thevenin's theorem, AC impedance) — 31st percentile. Student report revealed: "
        "attended competitive engineering coaching centre in Class XI-XII but received instruction "
        "focused on multiple-choice exam strategy rather than conceptual depth. The exam-pattern "
        "gap (MCQ coaching vs. proof-based university assessment) appears to be the primary "
        "structural cause.", st["body"]))
    s.append(Paragraph(
        "<b>Remedial Prescription:</b> Mathematics Clinic enrollment (2 sessions/week, "
        "each 90 minutes); CBT-based test anxiety program (6 sessions, Student Wellness Center); "
        "credit load reduction to 14 credits; weekly verified homework submission; assigned "
        "peer mentor Meera Iyer (Data Science, CGPA 8.7) through the Peer Mentorship Programme; "
        "required to attend all tutorial sessions for MA102 and CS201.", st["body"]))

    s.append(Paragraph("5. Diagnostic Case Study: Naomi L. Chen (Term 3 Probation — Committee Review)", st["h1"]))
    s.append(Paragraph(
        "<b>CGPA Trajectory:</b> Sem I: 7.44 → Sem II: 7.01 → Sem III: 5.92 (major drop) → "
        "Sem IV: 5.68 → Sem V: 5.44. The Standing Committee reviewed Naomi's case on August 14. "
        "Medical documentation (certified by University Chief Medical Officer) confirmed a "
        "diagnosis of Major Depressive Disorder (MDD) treated with pharmacotherapy since October "
        "2023, coinciding with the Semester III decline. The Committee's deliberation: voting "
        "4 in favor (extension) vs 1 opposed (suspension). <b>Decision:</b> One final probationary "
        "extension term. Strict conditions: minimum SGPA of 6.50 in Monsoon 2025; mandatory "
        "bi-weekly psychiatric follow-up confirmed by medical progress notes; maximum 16 credit "
        "registration; personal faculty advisor Dr. Sarah Jenkins designated as primary contact "
        "for coordinated academic-health support. Failure to meet the SGPA threshold will result "
        "in immediate academic suspension effective January 2026.", st["body"]))

    s.append(Paragraph("6. Diagnostic Case Study: Tyler R. Scott (Suspension Warning — Final Term)", st["h1"]))
    s.append(Paragraph(
        "<b>CGPA Trajectory:</b> Sem I: 6.42 → Sem II: 6.01 → Sem III: 5.44 → Sem IV: 4.80. "
        "<b>Uncompleted credits:</b> 28 credits across 4 semesters (exceeds the 24-credit "
        "suspension trigger). <b>Committee Action:</b> Final warning issued — effective suspension "
        "trigger if CGPA falls below 5.00 or SGPA in Monsoon 2025 is below 5.50. Required: "
        "withdrawal from all campus sports council positions, 10-credit maximum registration "
        "(CS201 backlog, CS210 backlog, and one first-year repeat), mandatory weekly meeting "
        "with Faculty Advisor Dr. Julian Vance.", st["body"]))

    s.append(Paragraph("7. Academic Recovery Contract (ARC) — Legal Terms & Enforcement Clauses", st["h1"]))
    s.append(Paragraph(
        "Students placed on Academic Probation must sign the ARC within 10 working days of "
        "semester commencement. Failure to sign results in registration hold. The ARC terms "
        "constitute a binding institutional agreement and are referenced in any subsequent "
        "readmission petition. Terms include: (a) Credit cap as specified by the Standing "
        "Committee; (b) Minimum Academic Support Center attendance hours with verified logs; "
        "(c) Bi-weekly advisor conference attendance; (d) Disqualification from extracurricular "
        "leadership and external representation; (e) The student acknowledges that failure to "
        "meet the SGPA target in the probationary term will trigger the next-tier consequence "
        "(suspension or further restriction) automatically without further hearing, unless "
        "extraordinary medical or personal circumstances are formally documented and certified "
        "by the University Chief Medical Officer.", st["body"]))

    s.append(Paragraph("8. Reinstatement Petitions & Academic Standing Appeal Procedures", st["h1"]))
    s.append(Paragraph(
        "Students subject to academic suspension may file a Reinstatement Petition to the Dean "
        "of Academic Affairs within 14 days of suspension notification. The petition must include: "
        "(a) a personal statement explaining the circumstances that led to the academic decline; "
        "(b) certified medical or psychological documentation for health-related cases; (c) an "
        "evidence-based Academic Recovery Plan outlining specific behavioral changes, study "
        "strategies, and support systems; (d) letters of support from at least one faculty member "
        "and one non-academic support professional (counselor, advisor). The Academic Standing "
        "Board convenes in the first week of August and January to hear reinstatement petitions. "
        "Reinstatement decisions are communicated in writing within 21 days of the hearing. "
        "Students reinstated from suspension are placed on Tier 3 Probation for the subsequent "
        "two semesters and must satisfy an accelerated recovery CGPA target.", st["body"]))

    build_pdf(
        os.path.join(DATA_DIR, "advisor", "academic_standing_interventions.pdf"),
        "Academic Standing, Probation & Remedial Intervention Dossiers AY 2025-2026",
        "School of Computing & Engineering | Office of Academic Advising & Registrar",
        s, "advisor")


# =============================================================================
# 9. ADVISOR — financial_aid_and_scholarships.pdf
# =============================================================================
def generate_financial_aid_and_scholarships():
    st = get_custom_styles()
    s = []

    s.append(Paragraph("1. Institutional Financial Aid Policy & Statutory Governance Framework", st["h1"]))
    s.append(Paragraph(
        "Northgate Institute of Technology is committed to ensuring that no academically qualified "
        "student is denied access to engineering education due to financial hardship. The Office of "
        "Financial Aid and Student Welfare (OFASW) administers institutional endowments, central "
        "and state government scholarships, corporate social responsibility (CSR) fellowships, and "
        "emergency student grants under the framework enacted by the Board of Governors (Financial "
        "Aid Governance Resolution FGR-2024-07) and aligned with guidelines from the Ministry of "
        "Education, UGC, and the National Scholarship Portal (NSP — scholarships.gov.in).", st["body"]))
    s.append(Paragraph(
        "All aid decisions are subject to annual audit by the University's Internal Audit Department "
        "and certified by the statutory auditor. Income verification is conducted against income tax "
        "returns (Form 16/ITR-1), revenue department income certificates, and Aadhaar-linked bank "
        "account verification through the NSP's Aadhaar-based payment infrastructure. No aid "
        "disbursement is made without successful verification.", st["body"]))

    s.append(Paragraph("2. Merit-Based Institutional Fellowship Programs", st["h1"]))
    s.append(Paragraph(
        "• <b>Presidential Merit Fellowship (PMF):</b> Full tuition waiver (100%) plus a monthly "
        "living stipend of Rs. 6,000 for undergraduate scholars admitted within the top 500 rank "
        "in JEE Advanced or the top 1,000 rank in state engineering entrance examinations. Renewal "
        "requires a cumulative CGPA >= 9.00 maintained at the end of each even semester, with zero "
        "academic backlogs. PMF is revoked if CGPA drops below 8.50 in any semester and is "
        "reinstated only after CGPA recovery above the threshold.", st["bullet"]))
    s.append(Paragraph(
        "• <b>Dean's Engineering Excellence Scholarship (DEES):</b> 50% tuition waiver awarded "
        "annually to the top 5% of students by CGPA within each engineering department (minimum "
        "threshold: CGPA >= 8.50 by the Spring term grade publication date). Evaluated each June. "
        "Applicable to both domestic and international admitted students.", st["bullet"]))
    s.append(Paragraph(
        "• <b>Women in Technology Leadership Award (WTLA):</b> Earmarked endowment providing 50% "
        "tuition waiver to outstanding female scholars in Computer Science and Data Science who "
        "demonstrate exceptional academic performance (CGPA >= 8.00) AND documented leadership "
        "in technical domains (hackathon wins, open-source contributions, published research). "
        "Applications reviewed by the WTLA Committee each semester.", st["bullet"]))
    s.append(Paragraph(
        "• <b>Sports Achievement Scholarship (SAS):</b> Rs. 50,000 per annum for students "
        "representing the University at national or international sporting competitions recognized "
        "by the Association of Indian Universities (AIU). Subject to Good Standing requirement.", st["bullet"]))
    s.append(Paragraph(
        "• <b>Innovation & Entrepreneurship Grant:</b> Rs. 1,00,000 seed grant (one-time, non-"
        "repayable) for students with SIIC-registered ventures demonstrating verified product "
        "traction (minimum 500 active users or Rs. 50,000 in revenue). Disbursed upon SIIC "
        "Advisory Board certification.", st["bullet"]))

    s.append(Paragraph("3. Government Scholarship Schemes: Central & State", st["h1"]))
    s.append(Paragraph(
        "• <b>Central Sector Scheme of Scholarships (CSSS / PM-USP):</b> Administered by the "
        "Ministry of Education through NSP. Supports meritorious students from low-income "
        "families (income < Rs. 6 Lakhs/year) who score above the 80th percentile in Class XII "
        "state/central board exams. Application opens annually in October on the NSP portal. "
        "Students must complete One-Time Registration (OTR) using Aadhaar/AEI.", st["bullet"]))
    s.append(Paragraph(
        "• <b>PM-YASASVI Scholarship (Pre-Matric & Post-Matric):</b> Supports OBC/EBC/DNT "
        "category students through the Social Justice & Empowerment Ministry. Post-matric "
        "scholarship covers tuition, hostel, and book allowance for eligible engineering students.", st["bullet"]))
    s.append(Paragraph(
        "• <b>SC/ST Post-Matric Scholarship:</b> Full tuition and maintenance allowance for "
        "Scheduled Caste and Scheduled Tribe students meeting income and course eligibility "
        "criteria under Ministry of Social Justice guidelines.", st["bullet"]))
    s.append(Paragraph(
        "• <b>State Minority Scholarship:</b> State government scholarship for minority community "
        "students (Muslim, Christian, Sikh, Buddhist, Jain, Zoroastrian) with household income "
        "< Rs. 2.5 Lakhs/year, covering 50% tuition.", st["bullet"]))

    s.append(Paragraph("4. Need-Based Institutional Aid: EWS Freeship & Equalization Grants", st["h1"]))
    s.append(Paragraph(
        "• <b>Economically Weaker Section (EWS) Freeship:</b> Full (100%) tuition fee concession "
        "for students whose gross annual household income is below Rs. 3,00,000 per annum, "
        "verified through certified government revenue authority income certificates and cross-"
        "checked against ITR. Partial freeship (75%) available for income between Rs. 3,00,001 "
        "and Rs. 4,50,000.", st["bullet"]))
    s.append(Paragraph(
        "• <b>Tuition Equalization Grants (TEG):</b> Need-based grants covering 25–50% of "
        "semester tuition for families with annual incomes between Rs. 4,50,001 and Rs. 8,00,000, "
        "with further consideration of family obligations (siblings in education, medical expenses, "
        "agricultural dependency). Applications undergo holistic socio-economic review.", st["bullet"]))
    s.append(Paragraph(
        "• <b>Campus Work-Study Programme (CWSP):</b> Eligible students may work up to 15 hours "
        "per week in campus roles: research lab assistant, library assistant, department student "
        "coordinator, canteen quality auditor, or IT help desk support. Hourly stipend: Rs. 80/hour "
        "credited monthly to the student's dining and hostel account. CWSP positions are awarded "
        "preferentially to students with demonstrated financial need.", st["bullet"]))

    s.append(Paragraph("5. Emergency Student Welfare Relief Fund (ESWRF)", st["h1"]))
    s.append(Paragraph(
        "The ESWRF provides non-repayable emergency grants for students experiencing sudden, "
        "unforeseen financial crises — including loss of the primary family earner (death, "
        "disability, job loss), catastrophic medical emergencies (critical illness, accident, "
        "surgery), natural disaster damage to family property, or other extraordinary circumstances "
        "that threaten enrollment continuation. Maximum single grant: Rs. 75,000. Applications are "
        "reviewed by the Dean of Student Welfare within 72 hours on an expedited basis. Supporting "
        "documentation: death certificate, hospital bills, FIR, or equivalent certifying the event. "
        "A student may apply for ESWRF at most twice during their degree programme.", st["body"]))

    s.append(Paragraph("6. Bursar Registration Hold & Fee Governance Policy (Clause 5.2)", st["h1"]))
    s.append(make_callout(
        "<b>Bursar Policy Clause 5.2 — Registration Hold Enforcement:</b> Any student account "
        "with unsettled tuition, laboratory, hostel, or library dues past the 45-day census "
        "deadline is automatically flagged with an administrative Bursar Hold through DCMP. "
        "The Hold blocks: (a) online course pre-registration; (b) official transcript issuance; "
        "(c) hall ticket generation for end-semester examinations; (d) degree certificate "
        "collection; (e) SIIC seed grant disbursement. Students awaiting confirmed bank education "
        "loan disbursement (PM-Vidyalaxmi or NBCFDC) may apply for an Administrative Hold Waiver "
        "by submitting a formal bank sanction letter, disbursement timeline confirmation, and "
        "signed undertaking to the Bursar's Office. The Bursar reviews waiver applications within "
        "3 working days. Waiver is granted for a maximum of 60 days, after which fees must be "
        "settled or the Hold reinstates automatically.",
        st, bg_color="#EFF6FF", border_color="#93C5FD"))

    s.append(Paragraph("7. PM-Vidyalaxmi & Bank Education Loan Facilitation", st["h1"]))
    s.append(Paragraph(
        "The PM-Vidyalaxmi Scheme (launched November 2024, Ministry of Education) provides "
        "collateral-free and guarantor-free education loans for students of Quality Higher "
        "Education Institutions (QHEIs — NIRF Top-100 or NBA/NAAC-accredited). Key features: "
        "(a) loan coverage up to Rs. 10 Lakhs for domestic institutions; (b) 3% interest "
        "subvention for families with annual income ≤ Rs. 8 Lakhs for the in-study period; "
        "(c) moratorium period of 12 months post-study completion before EMI commencement. "
        "Application via the official portal (pmvidyalaxmi.co.in) with Aadhaar-based identity "
        "verification and institution verification code.", st["body"]))
    s.append(Paragraph(
        "The University's Financial Services Office maintains a Bank Liaison Cell (BLC) "
        "partnering with: State Bank of India (Scholar Loan, up to Rs. 20 Lakhs at MCLR + 1.0%), "
        "Canara Bank (Vidya Turant, up to Rs. 20 Lakhs), HDFC Credila (up to Rs. 40 Lakhs, "
        "faster approval for premium institutions), PNB Udaan (NBCFDC-backed for backward "
        "class students up to Rs. 25 Lakhs at 5% simple interest), and Axis Bank Education Loan. "
        "BLC counselors are available Monday–Friday 10 AM–4 PM at the Financial Aid Office "
        "(Admin Block, Room 108) and by appointment via the DCMP portal.", st["body"]))

    s.append(Paragraph("8. Corporate Fellowships & CSR Scholarship Partners", st["h1"]))
    s.append(Paragraph(
        "Active industry-sponsored fellowships for AY 2025-2026 include: (1) <b>Google AI "
        "Research Fellowship</b> (4 recipients, full tuition + Rs. 10,000/month stipend, priority "
        "Google summer internship placement); (2) <b>Infosys Foundation STEM Grant</b> (10 "
        "recipients, Rs. 1.5 Lakhs/year, focus on first-generation college students from rural "
        "backgrounds); (3) <b>Qualcomm Wireless Innovation Award</b> (3 recipients, full tuition "
        "waiver + hardware development kit, priority Qualcomm pre-placement interview); "
        "(4) <b>TCS Research Endowment</b> (6 recipients, Rs. 1 Lakh/year, research co-mentorship "
        "by TCS Innovation Labs senior researchers); (5) <b>Reliance Foundation UG Scholarship</b> "
        "(household income < Rs. 15 Lakhs, financial need + merit combined criterion, "
        "Rs. 2 Lakhs/year).", st["body"]))

    s.append(Paragraph("9. Fee Refund, Withdrawal & Tuition Adjustment Regulations", st["h1"]))
    s.append(Paragraph(
        "Fee refund requests upon voluntary programme withdrawal or transfer are adjudicated under "
        "UGC Fee Refund Regulations 2023: (a) 100% refund (less Rs. 1,000 administrative "
        "processing fee) if formal withdrawal notice is received ≥ 15 days before scheduled "
        "class commencement; (b) 90% refund if withdrawal is within 0–15 days of commencement; "
        "(c) 80% refund if between 16 and 30 days after commencement; (d) 50% refund if between "
        "31 and 60 days; (e) zero refund after the 60-day post-commencement cutoff for "
        "discretionary withdrawals. Refunds are processed to the original payment source within "
        "21 working days of the approved withdrawal application.", st["body"]))

    build_pdf(
        os.path.join(DATA_DIR, "advisor", "financial_aid_and_scholarships.pdf"),
        "Institutional Financial Aid, Scholarships & Bursar Governance Policies AY 2025-2026",
        "Office of Financial Aid & Student Welfare | Endowments, Government Aid, Loans & Holds",
        s, "advisor")


# =============================================================================
# 10. DEAN — faculty_tenure_review.pdf
# =============================================================================
def generate_faculty_tenure_review():
    st = get_custom_styles()
    s = []

    s.append(make_callout(
        "<b>HIGHLY CONFIDENTIAL — PROVOST, DEAN & TENURE COMMITTEE USE ONLY.</b> This dossier "
        "contains peer evaluation letters, personnel committee deliberations, student evaluation "
        "aggregates, sponsored research financial records, and promotion votes. Distribution "
        "beyond the Tenure Committee, Dean's Office, and Provost's Office is strictly prohibited "
        "under Section 14.3 of the University Service Rules.",
        st, bg_color="#FEF2F2", border_color="#FCA5A5"))

    s.append(Paragraph("1. Tenure & Promotion Review Framework: UGC CAS & PBAS System", st["h1"]))
    s.append(Paragraph(
        "All tenure and promotion decisions at Northgate Institute are governed by the UGC "
        "Minimum Qualifications for Appointment of Teachers Regulations 2018 (4th Amendment 2024) "
        "and the University Career Advancement Scheme (CAS) as detailed in University Ordinance "
        "UO-2023-ACAD-11. The Performance-Based Appraisal System (PBAS) utilizes Academic "
        "Performance Indicators (API) across three categories: Category I (Teaching, Learning & "
        "Evaluation — minimum 80 API points/year), Category II (Co-curricular, Extension & "
        "Professional Development — minimum 15 API points/year), Category III (Research, "
        "Publications, Projects & Patents — minimum 25 API points/year for promotion to "
        "Associate Professor; 40 API points/year for promotion to Professor). Total minimum "
        "API score for tenure consideration: 120 points/year averaged over the review period. "
        "A mandatory Ph.D. remains an eligibility prerequisite for all Assistant Professor and "
        "above appointments per UGC Regulations.", st["body"]))
    s.append(Paragraph(
        "The review process follows a documented multi-stage workflow: (1) Candidate submits "
        "Annual Self-Appraisal Report (ASAR) and PBAS proforma with objective documentary "
        "evidence. (2) Head of Department verifies submissions and provides a confidential "
        "narrative assessment. (3) The Screening-cum-Evaluation Committee (for CAS-based "
        "promotion) or Selection Committee (for fresh appointment and major promotions) reviews "
        "all materials. (4) External blind peer review letters (minimum 5, from institutions "
        "outside the University system and outside the state) are solicited for tenure "
        "decisions. (5) The Promotion & Tenure Committee (P&TC) convenes for a formal "
        "deliberation session and records a written recommendation. (6) Dean's endorsement "
        "and Provost's ratification complete the process.", st["body"]))

    s.append(Paragraph("2. 6th-Year Tenure Review: Dr. Elena Marsh — Assistant → Associate Professor", st["h1"]))
    s.append(Paragraph(
        "<b>Candidate:</b> Dr. Elena Marsh, Ph.D. (CS, IIT Bombay 2015), Post-Doc Stanford University "
        "(2015-2019), appointed Assistant Professor at Northgate Institute August 2019. "
        "<b>Review milestone:</b> Mandatory 6th-year comprehensive tenure evaluation (AY 2025-2026).", st["body"]))
    s.append(Paragraph(
        "<b>Research & Scholarly Productivity (Category III):</b> Published 12 peer-reviewed "
        "articles in top-tier venues: IEEE Transactions on Knowledge and Data Engineering (2 papers), "
        "ACM SIGMOD Conference (3 papers, including 1 Best Paper Honorable Mention), VLDB "
        "Endowment (2 papers), IEEE ICDE (3 papers), ACM PODS (2 papers). h-index: 15, total "
        "citations: 1,247 (Google Scholar). Principal Investigator on active DST-SERB CRG grant: "
        "Rs. 45 Lakhs (2022-2025, '3-year, Distributed Concurrency Control in Heterogeneous "
        "HTAP Systems'). Co-PI on MeitY AI Consortium Grant: Rs. 1.2 Crores (2023-2026, "
        "'Responsible AI for Enterprise Knowledge Retrieval'). Two patent applications filed "
        "(Indian Patent Office): (1) Adaptive Query Plan Cache Management System, Application "
        "No. 202341004782; (2) Role-Based Vector Retrieval for Confidential Enterprise RAG "
        "Systems, Application No. 202341019321 — both under examination.", st["body"]))
    s.append(Paragraph(
        "<b>Teaching Effectiveness (Category I):</b> Consistently teaches CS301 DBMS (5 years) "
        "and CS420 Machine Learning (3 years). Student teaching evaluation average: 4.63/5.0 "
        "across 10 evaluated semesters (School average: 4.12/5.0). Developed and open-sourced "
        "the 'Northgate QueryBench' — a database performance benchmarking laboratory toolkit "
        "adopted by 8 Indian universities and 2 international institutions. Supervised: "
        "17 B.Tech capstone projects, 6 M.Tech theses, and 2 Ph.D. scholars (1 awarded June 2025).", st["body"]))
    s.append(Paragraph(
        "<b>External Referee Evaluation Summary (5 blind letters):</b> All 5 referees "
        "independently classified Dr. Marsh's research as 'High-Impact' or 'Excellent.' "
        "Representative quotes: 'Her work on Strict 2PL optimizations under distributed partition "
        "scenarios represents the most rigorous theoretical treatment I have seen in recent years' "
        "(Referee A, Professor, Carnegie Mellon University). 'The QueryBench toolkit has become "
        "an indispensable resource for database systems education globally' (Referee E, "
        "Distinguished Scientist, Google DeepMind).", st["body"]))
    s.append(Paragraph(
        "<b>P&TC Vote:</b> 6–0 Unanimous In Favor of Tenure and Promotion to Associate Professor. "
        "<b>Dean's Recommendation:</b> Full endorsement. Forwarded to Provost for ratification. "
        "Salary revision and designation change effective January 1, 2026.", st["body"]))

    s.append(Paragraph("3. Post-Tenure 5-Year Review: Dr. Owen T. Baptiste — Associate Professor", st["h1"]))
    s.append(Paragraph(
        "<b>Candidate:</b> Dr. Owen T. Baptiste, Ph.D. (Applied Economics, LSE 2007), tenured "
        "Associate Professor, Management & Humanities Division. <b>Review Cycle:</b> Quinquennial "
        "post-tenure performance evaluation (UO-2023-ACAD-11, Section 8). "
        "<b>Committee Finding:</b> SATISFACTORY PERFORMANCE — Unanimous (5-0). "
        "Notable outputs: textbook 'Technology Economics for Engineers' (published Oxford University "
        "Press India, 2023, adopted in 14 institutions); supervised 4 completed Ph.D. dissertations; "
        "external examiner for 8 M.Tech theses at IITs and NITs. Teaching evaluation: 4.24/5.0. "
        "Next post-tenure review scheduled AY 2030-2031.", st["body"]))

    s.append(Paragraph("4. 3rd-Year Pre-Tenure Reappointment: Dr. Julian Vance — Assistant Professor (ECE)", st["h1"]))
    s.append(Paragraph(
        "<b>Candidate:</b> Dr. Julian Vance, Ph.D. (ECE, IISc Bangalore 2021), appointed August 2022. "
        "<b>Interim Review Milestone:</b> 3rd-year evaluation for second 3-year term reappointment. "
        "Publications: 4 IEEE journal papers (JSTQE, TMTT), 6 conference papers (IMS, EuMC). "
        "Current grants: DST Early Career Research Award (Rs. 25 Lakhs, 2023-2025). "
        "<b>Committee Recommendation:</b> Reappointed for second 3-year term. Mandated "
        "improvements: accelerate grant submissions to DST-DRDO Aeronautics Program and "
        "ISRO RESPOND; increase Ph.D. student supervised count from 2 to 4 by the 6th-year "
        "review. Teaching evaluation: 4.11/5.0. Next review: AY 2028-2029 for tenure decision.", st["body"]))

    s.append(Paragraph("5. 6th-Year Tenure Dossier: Dr. Ananya Krishnan — Asst. → Associate Professor (CS-AI/ML)", st["h1"]))
    s.append(Paragraph(
        "<b>Candidate:</b> Dr. Ananya Krishnan, Ph.D. (CS, CMU 2018), appointed Assistant Professor "
        "August 2019. <b>Research:</b> 9 top-tier ML venue publications (NeurIPS × 3, ICLR × 2, "
        "CVPR × 2, ICML × 2). Google Scholar h-index: 12, citations: 843. Sponsored research "
        "funding: Rs. 38,00,000 (DST-SERB + Infosys Foundation + Google Faculty Research Award). "
        "Patents filed: 1 (AI-based anomaly detection in educational assessment environments). "
        "Supervised: 3 Ph.D. scholars (1 awarded, 2 ongoing), 11 M.Tech theses, 22 B.Tech capstones. "
        "<b>Committee Vote:</b> 5 In Favor, 1 Opposed (dissenting note on insufficient industry "
        "grant portfolio). <b>Recommendation:</b> Promotion to Associate Professor with Tenure granted. "
        "Dean endorses. The dissent is noted; Dr. Krishnan is encouraged to pursue DST "
        "Technology Development Project grants in AY 2025-2026.", st["body"]))

    s.append(Paragraph("6. Post-Tenure Exemplary Review: Dr. Ravi Subramaniam — Professor (Systems & OS)", st["h1"]))
    s.append(Paragraph(
        "<b>Candidate:</b> Dr. Ravi Subramaniam, Ph.D. (CS, IIT Madras 1999), Professor and Head "
        "of the Systems Research Group. <b>Review Cycle:</b> 5-year post-tenure review (2020-2025). "
        "<b>Finding:</b> EXEMPLARY PERFORMANCE — Unanimous (5-0). "
        "Doctoral supervision: 7 Ph.D. scholars to completion (2020-2025), 4 ongoing. "
        "2 granted patents (Indian Patent Office) on kernel-level memory tiering for heterogeneous "
        "memory systems. PI on DRDO Research Project: Rs. 85,00,000 (2022-2026, 'Secure OS "
        "Architectures for Military Edge Computing'). Teaching evaluation average: 4.71/5.0 "
        "(highest in department). Elected to the IEEE Computer Society Technical Committee on "
        "Operating Systems (TCOS). Awarded the Institute's Distinguished Teaching Award 2024.", st["body"]))

    s.append(Paragraph("7. 3rd-Year Pre-Tenure Review: Dr. Priya Sharma — Assistant Professor (Data Science)", st["h1"]))
    s.append(Paragraph(
        "<b>Candidate:</b> Dr. Priya Sharma, Ph.D. (Statistics & ML, University of Edinburgh 2021), "
        "appointed January 2023. <b>Review:</b> 3rd-year reappointment assessment. "
        "Publications: 4 IEEE Transactions journal papers (TNNLS, TBME), 5 conference papers "
        "(NeurIPS workshops, ECML-PKDD). Early Career Research Grant: Rs. 15,00,000 (SERB, 2024). "
        "<b>Recommendation:</b> Reappointed for second 3-year term. Guidance: submit to A* venues "
        "(NeurIPS/ICML main track); develop industry collaboration with Biocon or GE Healthcare "
        "given her healthcare AI specialization. Next review: AY 2028-2029.", st["body"]))

    s.append(Paragraph("8. Faculty Development Programme & Continuous Professional Growth", st["h1"]))
    s.append(Paragraph(
        "The University Teaching & Learning Center (UTLC) offers structured pedagogical development "
        "for all faculty: (a) Annual Teaching Orientation Workshop (2 days, August) covering OBE "
        "rubric design, DCMP LMS usage, and AI-proctored assessment best practices; (b) "
        "Micro-Teaching Observation Programme — peer faculty observe and review 1 lecture/semester "
        "with structured feedback using the Class Observation Protocol (COP) instrument; "
        "(c) Educational Technology Bootcamp — 5-day intensive on flipped classroom design, "
        "gamification, and learning analytics interpretation; (d) Faculty Exchange Programme — "
        "2-week reciprocal teaching visits at partner universities funded by the Faculty Development "
        "Budget (Rs. 12 Lakhs/year pool). Faculty maintaining student satisfaction scores < 3.5/5.0 "
        "for two consecutive semesters are required to complete the Pedagogical Mentorship Programme "
        "under UTLC supervision.", st["body"]))

    build_pdf(
        os.path.join(DATA_DIR, "dean", "faculty_tenure_review.pdf"),
        "Faculty Tenure, Promotion & Career Advancement Dossiers AY 2025-2026",
        "Office of the Dean & Provost | STRICTLY CONFIDENTIAL Faculty Appraisal Archives",
        s, "dean")


# =============================================================================
# 11. DEAN — department_strategic_plan.pdf
# =============================================================================
def generate_department_strategic_plan():
    st = get_custom_styles()
    s = []

    s.append(Paragraph("1. Executive Vision & Strategic Intent 2025-2030", st["h1"]))
    s.append(Paragraph(
        "The School of Computing and Engineering at Northgate Institute of Technology presents this "
        "Five-Year Strategic Development and Institutional Governance Plan to the Board of Governors "
        "for approval and funding commitment. The plan positions the School to achieve: (a) entry "
        "into the NIRF Top-50 Engineering Institutions ranking by 2027 (current position: Rank 87); "
        "(b) achievement of NIRF Top-30 by 2030; (c) completion of ABET Tier-1 accreditation for all "
        "B.Tech and M.Tech programmes by Winter 2026; (d) establishment as a nationally recognized "
        "center for applied AI research and responsible computing. The plan is aligned with NEP 2020 "
        "multidisciplinary learning mandates, the IndiaAI Mission's capacity-building objectives, "
        "and the 'Viksit Bharat @ 2047' technology readiness goals.", st["body"]))
    s.append(Paragraph(
        "NIRF ranking improvement strategy draws on the methodology-aware approach recommended by "
        "education consulting firms: the School's primary focus areas are Teaching, Learning & "
        "Resources (TLR — 30% NIRF weight) and Research & Professional Practice (RP — 30% NIRF "
        "weight), which together constitute 60% of the composite score. Secondary targets are "
        "Graduation Outcomes (GO — 20%), Outreach & Inclusivity (OI — 15%), and Perception "
        "(PR — 5%). Data integrity for NIRF submissions is managed by a dedicated NIRF Data "
        "Management Cell established under the Dean's office.", st["body"]))

    s.append(Paragraph("2. Strategic Pillar 1: AI Supercomputing Infrastructure (Budget: Rs. 14.2 Crores)", st["h1"]))
    s.append(Paragraph(
        "The School has commissioned the establishment of the High-Performance AI Supercomputing "
        "Center (HPAISC) — 'Project Swarnim' — co-funded through a DST-FIST matching grant "
        "(Rs. 6 Crores) and University capital expenditure (Rs. 8.2 Crores). Phase 1 (Q1 2026): "
        "Procurement and installation of 8 interconnected NVIDIA H100 SXM5 GPU compute nodes "
        "(80GB HBM3 per node) delivering over 32 petaflops of FP8 tensor computing capacity, "
        "interconnected via 400 Gbps InfiniBand NDR fabric. Phase 2 (Q3 2026): Integration of "
        "a 4 PB all-flash NVMe storage cluster (Dell PowerScale F910) for high-throughput ML "
        "training datasets. Phase 3 (Q1 2027): Establishment of an AI Model Repository and "
        "collaboration portal enabling shared access for 6 partner universities under the "
        "National Supercomputing Mission (NSM) collaborative network.", st["body"]))
    s.append(Paragraph(
        "The HPAISC will provide dedicated computational allocations for: doctoral dissertations "
        "(priority queue, 24h allocation per active Ph.D. scholar/week), faculty PI-approved "
        "research grants (proportional to grant quantum), industry-sponsored AI consortia "
        "(premium paid access, supporting the School's tech-transfer revenue model), and B.Tech "
        "Honors track students (2h/week allocation for capstone research). An Ethical AI "
        "Governance Committee will oversee access policies and ensure compliance with the "
        "IndiaAI Mission's Responsible AI framework.", st["body"]))

    s.append(Paragraph("3. Strategic Pillar 2: Faculty Recruitment & Endowed Chair Programme", st["h1"]))
    s.append(Paragraph(
        "To improve TLR scores and research capacity simultaneously, the School will execute the "
        "most ambitious faculty hiring programme in its history: 18 tenure-track Assistant Professor "
        "positions and 4 Distinguished Endowed Chair positions over 5 years (2025-2030). "
        "Target specializations: (a) Generative AI & Foundation Models (4 positions); "
        "(b) Quantum Computing Architectures (2 positions); (c) Hardware Security & Trusted "
        "Execution Environments (2 positions); (d) Edge Computing & IoT Systems (2 positions); "
        "(e) Cybersecurity & Zero-Trust Architecture (2 positions); (f) Data Engineering & "
        "LLMOps (2 positions); (g) Human-Computer Interaction & Assistive Technology (2 positions); "
        "(h) Bioinformatics & Computational Genomics (2 positions, multi-disciplinary with "
        "Life Sciences).", st["body"]))
    s.append(Paragraph(
        "Endowed Chair holders (funded at Rs. 25 Lakhs/year research discretionary from the "
        "University Innovation Endowment) must: (a) lead one of the 3 Centers of Excellence; "
        "(b) attract minimum Rs. 1 Crore in external grants within 3 years; (c) mentor 2 early-"
        "career faculty members annually; (d) deliver 2 public distinguished lectures per year. "
        "International recruitment campaigns will target returning Indian diaspora researchers "
        "from leading institutions (MIT, Stanford, CMU, Google Research, Microsoft Research, "
        "DeepMind) through the 'Vasudhaiva Kutumbakam' Faculty Homecoming Programme.", st["body"]))

    s.append(Paragraph("4. Strategic Pillar 3: Three Centers of Excellence (CoEs)", st["h1"]))
    s.append(Paragraph(
        "• <b>Center for Trustworthy AI & Algorithmic Ethics (CTAAE):</b> Directed by Dr. Ananya "
        "Krishnan. Research focus: safety, fairness, robustness, and explainability of AI systems "
        "deployed in critical decision-making contexts (healthcare triage, credit scoring, criminal "
        "justice, university admissions). Founding industry partners: Persistent Systems, Wipro AI "
        "Labs. Target: 5 NeurIPS/ICML/FAccT papers/year by Year 3; Rs. 2 Crores DST-funded "
        "project by Year 2.", st["bullet"]))
    s.append(Paragraph(
        "• <b>Center for Cyber Defense & Zero-Trust Architecture (CCDZT):</b> Directed by "
        "Dr. Julian Vance. Focus: critical infrastructure protection, hardware-rooted trust, "
        "automotive cybersecurity (ISO 21434), and quantum-safe cryptography transition. "
        "Partners: CERT-In, DRDO, Bosch Engineering. Target: quarterly CTF (Capture The Flag) "
        "competition for students and industry practitioners; 2 DRDO-funded projects by Year 2.", st["bullet"]))
    s.append(Paragraph(
        "• <b>Center for Sustainable Cloud & Edge Systems (CSCES):</b> Directed by Dr. Ravi "
        "Subramaniam. Focus: carbon-aware distributed computing, energy-proportional data centers, "
        "workload scheduling for renewable energy integration, edge inference efficiency "
        "(quantization, pruning, neural architecture search). Partners: AWS Sustainability, "
        "Microsoft Azure Research, NVIDIA AI Enterprise. Target: 2 IEEE/ACM systems conference "
        "papers/year; ISO 50001 energy management certification for HPAISC facility by Year 2.", st["bullet"]))

    s.append(Paragraph("5. Strategic Pillar 4: ABET & NAAC Accreditation Roadmap", st["h1"]))
    s.append(Paragraph(
        "The School aims to complete ABET accreditation (Criteria for Programs in Computing — "
        "CAC) for all B.Tech and M.Tech programmes by Winter 2026. The Department Curriculum "
        "Committee has been restructured as a standing body meeting monthly, responsible for: "
        "(a) mapping all Course Outcomes (COs) to ABET Student Outcomes (a)–(j) and AICTE "
        "Graduate Attributes; (b) executing direct and indirect assessment of CO attainment "
        "each semester; (c) closing the loop through documented curriculum revisions based on "
        "assessment data. NAAC institutional accreditation renewal (target: Grade A++, current: "
        "A) requires submission of the Institutional Development Plan (IDP) by December 2025 "
        "and a site visit in Q2 2026. The School contributes data for 4 NAAC criteria: Curricular "
        "Aspects (C1), Teaching-Learning & Evaluation (C2), Research, Innovation & Extension (C3), "
        "and Infrastructure & Learning Resources (C4).", st["body"]))

    s.append(Paragraph("6. Strategic Pillar 5: Industry Consortia, Tech Transfer & Incubation", st["h1"]))
    s.append(Paragraph(
        "The School is establishing a formal Industry-Academia Technology Consortium (IATC) with "
        "10 founding corporate members (Microsoft, AWS, Infosys, Qualcomm, Bosch, TCS, Wipro, "
        "HCL, ISRO-SAC, and DRDO-CAIR) each contributing Rs. 25 Lakhs/year in consortium fees "
        "for access to: dedicated research collaboration with faculty, priority campus recruitment "
        "access, co-development of 2 specialized elective courses annually, and IP licensing "
        "right-of-first-negotiation on School-developed patents.", st["body"]))
    s.append(Paragraph(
        "The Student Innovation & Incubation Center (SIIC) expansion plan (Phase 2): increase "
        "active incubated startups from 12 to 30 by Year 3; establish an Alumni Angel Network "
        "(target: 100 accredited investors by Year 2); launch the Deep-Tech Accelerator Programme "
        "in partnership with NASSCOM 10,000 Startups (12-week cohort, 2 cohorts/year, Rs. 5 Lakhs "
        "seed + cloud credits + mentorship). The School's patent filing rate target: 10 "
        "provisional patents/year by Year 3.", st["body"]))

    s.append(Paragraph("7. Strategic Pillar 6: Diversity, Equity & International Partnerships", st["h1"]))
    s.append(Paragraph(
        "The School commits to increasing female student enrollment in engineering programmes from "
        "the current 28% to 40% by 2030 through: (a) the WTLA scholarship expansion (increasing "
        "awardees from 10 to 25); (b) Girls4Tech outreach programme visiting 100 partner schools "
        "annually in Tier-2 and Tier-3 cities; (c) women-only hackathon 'CodeHer' with Rs. 5 "
        "Lakhs prize pool; (d) mentorship matching with women alumni in senior industry positions. "
        "International partnerships: expand MoU exchange network from 14 to 25 partner universities "
        "by 2028, with particular focus on ASEAN, European, and African institutions to fulfill "
        "NEP 2020's internationalization mandate.", st["body"]))

    s.append(Paragraph("8. Research Grant & IDC Revenue Model", st["h1"]))
    s.append(Paragraph(
        "Indirect cost overheads (IDC) from external grants are distributed per the University "
        "Research Finance Policy: 50% to the Central University Research Facilitation Fund "
        "(CURFF) supporting shared infrastructure; 30% to the Host Department for equipment, "
        "lab consumables, and RA stipends; 20% to the PI's Professional Development Account for "
        "conference travel, equipment purchases, and researcher training. The School's aggregate "
        "externally funded research portfolio target: Rs. 15 Crores/year by Year 5 (current: "
        "Rs. 4.2 Crores/year). Faculty eligible for Research Sabbaticals (1 year, paid, "
        "extendable by 6 months unpaid) after 6 consecutive service years, contingent on "
        "completion of all current student supervision commitments.", st["body"]))

    build_pdf(
        os.path.join(DATA_DIR, "dean", "department_strategic_plan.pdf"),
        "School of Computing & Engineering 5-Year Strategic Development Plan (2025-2030)",
        "Office of the Dean & Provost | Research Excellence, Infrastructure & NIRF/ABET Roadmap",
        s, "dean")


# =============================================================================
# 12. DEAN — disciplinary_hearings.pdf
# =============================================================================
def generate_disciplinary_hearings():
    st = get_custom_styles()
    s = []

    s.append(make_callout(
        "<b>STRICTLY CONFIDENTIAL — DISCIPLINARY COMMITTEE HEARING ARCHIVES.</b> This document "
        "contains formal findings, forensic evidence summaries, legal deliberations, and sanctions "
        "issued by the University Disciplinary Committee and Academic Integrity Board. Distribution "
        "to unauthorized personnel constitutes a direct violation of institutional confidentiality "
        "regulations and applicable privacy statutes. Access: Dean of Students Affairs, Registrar, "
        "Dean of Academic Affairs, University Legal Counsel, and Provost only.",
        st, bg_color="#FEF2F2", border_color="#FCA5A5"))

    s.append(Paragraph("1. Disciplinary Committee Structure, Quorum & Procedural Standards", st["h1"]))
    s.append(Paragraph(
        "The University Disciplinary Committee (UDC) is constituted under University Statute "
        "Chapter 12 and the UGC (Prevention, Prohibition and Punishment of Ragging in HEIs) "
        "Regulations 2009. The UDC comprises: the Dean of Student Affairs (Chair), the Registrar, "
        "two senior professors nominated by the Academic Senate (one of whom must be a woman), one "
        "legal adviser (qualified advocate), and one student ombudsperson representative. Quorum "
        "requires 4 members including the Chair. All hearings are conducted in accordance with "
        "principles of natural justice: respondents are guaranteed: (a) written notice of charges "
        "at least 5 working days before hearing; (b) right to review all evidence; (c) right to "
        "present a defense and submit written response; (d) right to be accompanied by a faculty "
        "representative; (e) right to appeal the UDC decision to the Dean within 10 working days.", st["body"]))

    s.append(Paragraph("2. Hearing DH-2025-014: Academic Dishonesty — Devon K. Ramirez", st["h1"]))
    s.append(Paragraph(
        "<b>Respondent:</b> Devon K. Ramirez (Roll No: 2024BDSE009, Sem II, Data Science) "
        "<b>Complainant:</b> Dr. Elena Marsh, CS301 Course Instructor "
        "<b>Hearing Date:</b> November 3, 2025 | <b>Panel Chair:</b> Prof. Marcus Vance, "
        "Chair of Academic Integrity Board", st["body"]))
    s.append(Paragraph(
        "<b>Charges:</b> Level 2 Academic Dishonesty — submission of CS301 Laboratory "
        "Assignment 3 (SQL Query Design for E-Commerce Schema) containing 92% syntactic "
        "similarity to a solution posted on a public repository (GitHub gist: [redacted]) "
        "and distributing solution files to 3 peer students via WhatsApp group chat.", st["body"]))
    s.append(Paragraph(
        "<b>Forensic Evidence:</b> (a) MOSS code similarity analysis (Stanford MOSS, run "
        "November 1, 2025) reported 92% non-trivial structural similarity between the "
        "respondent's submission and the external repository. (b) WhatsApp message export "
        "(voluntarily produced by complainant student) showed respondent sharing the file "
        "'assignment3_solution_final.sql' at 11:42 PM on October 29, 2025, 18 hours before "
        "the submission deadline. (c) Examination of submission metadata confirmed identical "
        "SQL comments, identical column aliases, and a unique typographic error ('INNERJOIN' "
        "without space) replicated verbatim from the source repository.", st["body"]))
    s.append(Paragraph(
        "<b>Respondent Defense:</b> Student submitted a written defense acknowledging use of "
        "an 'online reference' but denied intentional plagiarism, claiming lack of clarity "
        "about what constituted academic misconduct in SQL lab assignments. The Panel noted "
        "that the course syllabus explicitly prohibits external solution references and that "
        "the student had signed the Honor Pledge at semester commencement.", st["body"]))
    s.append(Paragraph(
        "<b>Findings & Sanctions (Panel Vote: 4–1 Uphold):</b> (1) Zero credit (0/50) on "
        "Laboratory Assignment 3. (2) Final course grade reduced by one full letter grade "
        "(the student's earned B+ becomes B). (3) Mandatory 4-week Academic Ethics and "
        "Integrity Workshop (AEIWRM program, next cohort starts January 12, 2026). "
        "(4) Formal Conduct Warning entered into the student's confidential institutional "
        "dossier (retained for 5 years or until graduation, whichever is later). "
        "(5) The 3 students who received the shared file receive formal written cautions; "
        "their submissions will be assigned reduced credit (20% penalty) pending individual "
        "intent assessment.", st["body"]))

    s.append(Paragraph("3. Hearing DH-2025-021: Hostel Regulations Violation — Naomi L. Chen", st["h1"]))
    s.append(Paragraph(
        "<b>Respondent:</b> Naomi L. Chen (Roll No: 2022BSWE012) <b>Incident Date:</b> "
        "October 28, 2025, 12:45 AM | <b>Location:</b> Sarojini Hostel Block B, Room B-214 "
        "<b>Charge:</b> Violation of Hostel Regulations Section 4.2 (noise breach during "
        "mandatory quiet hours 11 PM–6 AM) and Section 4.6 (unauthorized guests — 2 non-"
        "resident students present after 10:30 PM gate closure). "
        "<b>Evidence:</b> CCTV footage from Block B corridor at 12:45 AM showing 2 additional "
        "persons entering Room B-214; warden's inspection log documenting noise complaint "
        "from neighboring Room B-216. "
        "<b>Sanctions Imposed:</b> Written Reprimand (Level 1); administrative hostel fine "
        "of Rs. 2,500 (processed to student's campus account); 15 hours of campus library "
        "community service (shelving and cataloging) to be completed before November 30.", st["body"]))

    s.append(Paragraph("4. Hearing DH-2025-035: Cybersecurity Violation — Liam P. O'Connor", st["h1"]))
    s.append(Paragraph(
        "<b>Respondent:</b> Liam P. O'Connor (Roll No: 2023BCSE031, Year 3 CSE) "
        "<b>Hearing Date:</b> November 24, 2025 | <b>Panel Chair:</b> Dean Arthur Pendelton", st["body"]))
    s.append(Paragraph(
        "<b>Charges (Level 3 — Major Violation):</b> Unauthorized access attempt against the "
        "University Faculty Grading Server (secure.grades.northgate.edu) on November 12, 2025 "
        "from 02:14 AM to 02:47 AM via: (a) automated port scan of 4,096 ports (Nmap scan "
        "detected by the SOC SIEM at 02:16 AM); (b) attempted SQL injection against the "
        "faculty login form (8 distinct injection payloads detected by WAF, logged at 02:23 AM); "
        "(c) directory traversal attempt targeting '/admin/grade_upload' endpoint "
        "(blocked by Apache ModSecurity, logged at 02:41 AM).", st["body"]))
    s.append(Paragraph(
        "<b>Forensic Evidence:</b> (a) SOC incident log INC-2025-1112-0047 confirming all "
        "attack traffic originated from IP address 10.42.87.211 (assigned to respondent's "
        "registered laptop via university RADIUS server at 02:13 AM); (b) respondent's "
        "device found to contain Nmap, SQLmap, and Burp Suite Community Edition installed "
        "(surrendered to IT Security during device forensic examination); (c) respondent's "
        "LDAP authentication log shows a failed 'grade_admin' login attempt at 02:38 AM. "
        "Respondent produced no credible defense — claimed 'testing cybersecurity knowledge "
        "for academic purposes' without any instructor authorization or lab clearance.", st["body"]))
    s.append(Paragraph(
        "<b>Sanctions (Panel Vote: 5-0 Uphold — Unanimous):</b> (1) One-semester mandatory "
        "academic suspension for Spring 2026 (all academic activities suspended). "
        "(2) Permanent revocation of all campus computing laboratory, Wi-Fi, and server "
        "access — no reinstatement permissible under any circumstances. (3) Mandatory parent "
        "and legal guardian counseling session with the Dean of Student Affairs before any "
        "readmission petition is considered. (4) Referral to University Legal Counsel for "
        "assessment of criminal cybersecurity charges under IT Act 2000 Sections 43 and "
        "66 — report filed with local Cyber Crime Cell. (5) Conduct notation on academic "
        "transcript: 'Academic Suspension — IT Act Cybersecurity Violation Nov 2025.'", st["body"]))

    s.append(Paragraph("5. Hearing DH-2025-042: Unauthorized Examination Material Procurement — Tyler R. Scott", st["h1"]))
    s.append(Paragraph(
        "<b>Respondent:</b> Tyler R. Scott (Roll No: 2023BCE019) <b>Hearing Date:</b> December 2, 2025 "
        "<b>Charge:</b> Level 3 — Unauthorized procurement of draft CAT-2 examination question "
        "papers for 3 courses prior to the examination date. "
        "<b>Evidence:</b> Laboratory printer audit log (Print Server Log: PSL-2025-1022-003) "
        "showing respondent's LDAP credential authenticated a print job titled 'CAT2_Draft_"
        "CS301_CS340_CS355.pdf' from a research lab workstation at 4:47 PM on October 22, 2025 "
        "(draft papers stored on shared faculty network drive, accessible due to misconfigured "
        "permissions — remediated November 1). Physical copies of the papers recovered from "
        "respondent's hostel room during authorized search. "
        "<b>Sanctions:</b> (1) 'F' grade assigned to all 3 registered courses for Fall 2025 "
        "semester. (2) One-year academic suspension effective January 2026. (3) University "
        "Information Security team implemented mandatory role-based access control (RBAC) "
        "audit of all faculty network shares as a remedial system action.", st["body"]))

    s.append(Paragraph("6. Hearing DH-2025-055: Disruptive Conduct — Marcus D. Whitfield", st["h1"]))
    s.append(Paragraph(
        "<b>Respondent:</b> Marcus D. Whitfield (Roll No: 2023BCSE042) "
        "<b>Hearing Date:</b> October 14, 2025 "
        "<b>Charge:</b> Level 1 — Disruptive conduct in the Central Computing Center during "
        "the Semester V Practical Examination Session 2B (October 13, 2025). Specifically: "
        "refusal to vacate allocated computing terminal 45 minutes after the 3-hour session "
        "concluded, preventing the next batch from beginning their allotted examination time; "
        "and verbal confrontation with the laboratory invigilator involving raised voice and "
        "use of inappropriate language. "
        "<b>Respondent Statement:</b> Student acknowledges the confrontation and attributes "
        "it to severe examination stress. Student expressed sincere remorse in writing. "
        "<b>Sanctions:</b> (1) Formal Written Reprimand. (2) 10 hours of supervised community "
        "service in the Central Computing Center (equipment cleaning and maintenance, weekends). "
        "(3) Mandatory 2-session anger management and stress resilience workshop through the "
        "Student Wellness Center. (4) This incident factored into the advisor's comprehensive "
        "assessment in the student's Academic Probation case file.", st["body"]))

    s.append(Paragraph("7. Hearing DH-2025-062: Unauthorized Drone Operation — Hannah M. Zhao", st["h1"]))
    s.append(Paragraph(
        "<b>Respondent:</b> Hannah M. Zhao (Roll No: 2023BEE011) <b>Hearing Date:</b> November 18, 2025 "
        "<b>Charge:</b> Level 1 — Operating an unregistered commercial quadcopter drone (DJI Mini 4 Pro) "
        "over Sarojini Hostel residential zone and the Women's Sports Ground on October 30, 2025 "
        "without prior security clearance, drone registration (DGCA UAS portal), and written "
        "authorization from Campus Security. The drone was operated for 22 minutes between "
        "6:18 PM and 6:40 PM, recording video footage. "
        "<b>Evidence:</b> Real-time drone detection alert from campus RF monitoring system "
        "(DroneShield installed Aug 2025); CCTV footage of respondent operating controller; "
        "drone registration check confirmed no DGCA UAS ID assigned. "
        "<b>Sanctions:</b> (1) Drone apparatus and controller confiscated and held by Campus "
        "Security until June 2026 or degree completion, whichever is later. (2) Written "
        "Reprimand. (3) Mandatory DGCA UAS Rules 2021 compliance training (online, 4 hours). "
        "(4) Written undertaking from respondent not to operate UAVs on campus without prior "
        "clearance through the new Campus UAS Authorization Protocol (CUAP) effective "
        "January 2026.", st["body"]))

    s.append(Paragraph("8. University Statutory Disciplinary Sanctions Matrix", st["h1"]))
    s.append(Paragraph(
        "Misconduct is classified into three severity tiers with prescribed sanction ranges: "
        "<b>Level 1 (Minor):</b> Unintentional citation omission, hostel quiet-hour breach, "
        "first-time unauthorized software installation, minor noise violation. Sanctions: "
        "Written Reprimand; assignment resubmission with 20% grade penalty; community service "
        "10–20 hours. <b>Level 2 (Moderate):</b> Plagiarism on course assignment, unauthorized "
        "collaboration in programming lab, sharing solution files. Sanctions: Zero grade on "
        "component; course grade reduction by one letter; mandatory Academic Ethics Workshop; "
        "formal conduct warning on record. <b>Level 3 (Major/Severe):</b> Examination paper "
        "procurement/distribution, server hacking, impersonation, physical assault. Sanctions: "
        "'F' grade in all courses for the term; one-year academic suspension to permanent "
        "expulsion; transcript conduct notation; criminal referral when warranted.", st["body"]))

    s.append(Paragraph("9. Disciplinary Records Retention, Expungement & Privacy Protocols", st["h1"]))
    s.append(Paragraph(
        "Disciplinary case dossiers are maintained under sealed custody in the Office of Student "
        "Conduct (physical: fireproof vault, Room 004B, Admin Block; digital: encrypted DCMP "
        "Disciplinary Module with role-gated access). Retention schedules: Level 1 records are "
        "expunged from the active dossier 3 years after graduation, provided no further "
        "infractions; Level 2 records retained for 7 years; Level 3 records retained "
        "permanently. External disclosure of disciplinary records is permissible only upon: "
        "(a) written consent of the affected student; (b) valid court subpoena or law "
        "enforcement order; (c) request from a professional licensing board or security "
        "clearance authority citing a legal basis. Internal sharing follows a strict "
        "need-to-know principle: only the Dean, Registrar, and the student's assigned "
        "Faculty Advisor have read access to the full dossier.", st["body"]))

    build_pdf(
        os.path.join(DATA_DIR, "dean", "disciplinary_hearings.pdf"),
        "University Disciplinary Committee Hearing Records & Formal Findings AY 2025-2026",
        "Office of Student Conduct & Dean of Students | CONFIDENTIAL Case Dossiers & Sanctions",
        s, "dean")


# =============================================================================
# Main
# =============================================================================
def generate_all_pdfs():
    print("=" * 70)
    print("  Northgate Institute of Technology — RBAC University RAG PDF Generator")
    print("  Generating 12 text-rich, multi-page institutional documents...")
    print("=" * 70)

    print("\n[PUBLIC TIER — accessible by all roles]")
    generate_campus_policies()
    generate_academic_calendar()
    generate_course_catalog()

    print("\n[FACULTY TIER — accessible by faculty, advisor, and dean]")
    generate_exam_answer_keys()
    generate_grading_rubric()
    generate_cs_lesson_plan()

    print("\n[ADVISOR TIER — accessible by advisor and dean]")
    generate_student_academic_advising()
    generate_academic_standing_interventions()
    generate_financial_aid_and_scholarships()

    print("\n[DEAN TIER — accessible by dean only]")
    generate_faculty_tenure_review()
    generate_department_strategic_plan()
    generate_disciplinary_hearings()

    print("\n" + "=" * 70)
    print("  All 12 PDFs successfully generated!")
    print("=" * 70)


if __name__ == "__main__":
    generate_all_pdfs()