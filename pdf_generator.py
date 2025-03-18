'''from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer,ListFlowable, ListItem, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet

def validate_link(link):
    """Ensures links are valid and contain a proper scheme (http/https)."""
    if link and link.strip().startswith(("http://", "https://")):
        return link.strip()
    return "Not Provided"  # Replace invalid links

def generate_pdf(user_data):
    pdf_path = "cv_output.pdf"
    doc = SimpleDocTemplate(pdf_path, pagesize=letter)
    styles = getSampleStyleSheet()
    content = []

    # Title: Name & Contact Info
    title = Paragraph(f"<b>{user_data.get('name', 'Name')}</b>", styles["Title"])

    contact_info = Paragraph(
        f"{user_data.get('phone', 'N/A')} | {user_data.get('email', 'N/A')} | "
        f"LeetCode: {validate_link(user_data.get('leetcode', ''))} | GitHub: {validate_link(user_data.get('github', ''))}",
        styles["Normal"]
    )
    
    content.append(title)
    content.append(contact_info)
    content.append(Spacer(1, 12))

    # Function to Add Sections
    def add_section(title, key, is_list=False):
        if user_data.get(key) and user_data[key]:
            content.append(Paragraph(f"<b>{title}</b>", styles["Heading2"]))
            content.append(Spacer(1, 6))

            if is_list and isinstance(user_data[key], list):
                bullet_items = [ListItem(Paragraph(item, styles["Normal"]), leftIndent=20) for item in user_data[key]]
                content.append(ListFlowable(bullet_items, bulletType="bullet", start="•"))
            else:
                content.append(Paragraph(user_data[key], styles["Normal"]))

            content.append(Spacer(1, 12))

    #Objectives        
    content.append(Paragraph("<b>OBJECTIVE</b>", styles["Heading2"]))
    content.append(Spacer(1, 6))

    # Retrieve the objective from user_data
    objective_text = user_data.get("objective", "No objective provided.")

    content.append(Paragraph(objective_text, styles["Normal"]))
    content.append(Spacer(1, 12))  # Extra space before the next section

    # Education Section
    content.append(Paragraph("<b>EDUCATION</b>", styles["Heading2"]))
    content.append(Spacer(1, 6))
    for edu in user_data.get("education", []):
        if isinstance(edu, dict):  # Ensure edu is a dictionary
            edu_text = (
                f"<b>{edu.get('course', 'Course Name')}</b><br/>"
                f"{edu.get('institute', 'Institute Name')} | {edu.get('start_date', 'Start Date')} - {edu.get('end_date', 'End Date')}"
            )
        else:
            edu_text = f"<b>{edu}</b>"

        content.append(Paragraph(edu_text, styles["Normal"]))
        content.append(Spacer(1, 6))

    content.append(Spacer(1, 12))

    # Experience Section
    content.append(Paragraph("<b>EXPERIENCE</b>", styles["Heading2"]))
    content.append(Spacer(1, 6))
    for exp in user_data.get("experience", []):
        if isinstance(exp, dict):
            exp_text = (
                f"<b>{exp.get('role', 'Role')}</b> - {exp.get('company', 'Company Name')}<br/><br/>"
                f"<i>{exp.get('start_date', 'Start Date')} - {exp.get('end_date', 'End Date')}</i><br/><br/>"
                f"{exp.get('description', 'Description')}<br/><br/>"
            )
        else:
            exp_text = f"<b>{exp}</b>"

        content.append(Paragraph(exp_text, styles["Normal"]))
        content.append(Spacer(1, 6))

    content.append(Spacer(1, 12))

    # Projects Section
    content.append(Paragraph("<b>PROJECTS</b>", styles["Heading2"]))
    content.append(Spacer(1, 6))
    for project in user_data.get("projects", []):
        if isinstance(project, dict):
            project_link = validate_link(project.get("link", ""))

            project_text = (
                f"<b>{project.get('name', 'Project Name')}</b> [{project.get('tech', 'Technology Used')}]<br/>"
                f"<a href='{project_link}'>{project_link if project_link != 'Not Provided' else 'No Link Provided'}</a><br/>"
                f"{project.get('description', 'Description')}"
            )
        else:
            project_text = f"<b>{project}</b>"
        content.append(Paragraph(project_text, styles["Normal"]))
        content.append(Spacer(1, 6))

    content.append(Spacer(1, 12))

    # Skills Section
    add_section("SKILLS", "skills", is_list=True)
    content.append(Spacer(1, 6))
    
    # Volunteer Section
    if user_data.get("volunteer"):
        content.append(Paragraph("<b>VOLUNTEER EXPERIENCE</b>", styles["Heading2"]))
        content.append(Spacer(1, 6))

        if isinstance(user_data["volunteer"], list):
            for vol in user_data["volunteer"]:
                if isinstance(vol, dict):
                    vol_text = (
                        f"<b>{vol.get('role', 'Role')}</b> - {vol.get('organization', 'Organization Name')}<br/>"
                        f"{vol.get('start_date', 'Start Date')} - {vol.get('end_date', 'End Date')}<br/>"
                        f"{vol.get('description', 'Description')}"
                    )
                else:
                    vol_text = f"<b>{vol}</b>"

                content.append(Paragraph(vol_text, styles["Normal"]))
                content.append(Spacer(1, 6))

        content.append(Spacer(1, 12))

    # Achievements Section
    if user_data.get("achievements"):
        content.append(Paragraph("<b>ACHIEVEMENTS</b>", styles["Heading2"]))
        content.append(Spacer(1, 6))

        if isinstance(user_data["achievements"], list):
            bullet_items = [
                ListItem(Paragraph(achievement, styles["Normal"]), leftIndent=10)
                for achievement in user_data["achievements"]
                if isinstance(achievement, str)
            ]

            if bullet_items:
                content.append(ListFlowable(bullet_items, bulletType="bullet"))
            else:
                content.append(Paragraph("No achievements listed.", styles["Normal"]))

    content.append(Spacer(1, 12))  # Adds spacing before next section

    # Build the PDF
    if content:
        doc.build(content)

    return pdf_path
'''

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem
from reportlab.lib.styles import getSampleStyleSheet

def validate_link(link):
    """Ensures links are valid and contain a proper scheme (http/https)."""
    if link and link.strip().startswith(("http://", "https://")):
        return link.strip()
    return None  # Remove invalid links

def generate_pdf(user_data):
    """Generates a structured PDF CV and removes skipped sections."""
    pdf_path = "cv_output.pdf"
    doc = SimpleDocTemplate(pdf_path, pagesize=letter)
    styles = getSampleStyleSheet()
    content = []

    # Title: Name & Contact Info
    if user_data.get("name"):
        content.append(Paragraph(f"<b>{user_data['name']}</b>", styles["Title"]))

    contact_details = []
    if user_data.get("phone"):
        contact_details.append(user_data["phone"])
    if user_data.get("email"):
        contact_details.append(user_data["email"])
    if validate_link(user_data.get("leetcode")):
        contact_details.append(f"LeetCode: {validate_link(user_data['leetcode'])}")
    if validate_link(user_data.get("github")):
        contact_details.append(f"GitHub: {validate_link(user_data['github'])}")

    if contact_details:
        content.append(Paragraph(" | ".join(contact_details), styles["Normal"]))
        content.append(Spacer(1, 12))

    # Objective
    if user_data.get("objective"):
        content.append(Paragraph("<b>OBJECTIVE</b>", styles["Heading2"]))
        content.append(Spacer(1, 6))
        content.append(Paragraph(user_data["objective"], styles["Normal"]))
        content.append(Spacer(1, 12))
    
    # Education
    if user_data.get("education"):
        content.append(Paragraph("<b>EDUCATION</b>", styles["Heading2"]))
        content.append(Spacer(1, 6))
        for edu in user_data["education"]:
            if isinstance(edu, dict):
                edu_text = ""
                if edu.get("course"):
                    edu_text += f"<b>{edu['course']}</b>"
                if edu.get("institute"):
                    edu_text += f"<br/>{edu['institute']}"
                
                start_date = edu.get('start_date', '').strip()
                end_date = edu.get('end_date', '').strip()
                date_text = f" | {start_date} - {end_date}" if start_date and end_date else ""
                edu_text += date_text
                
                if edu_text:
                    content.append(Paragraph(edu_text, styles["Normal"]))
                    content.append(Spacer(1, 6))
        content.append(Spacer(1, 12))
 
    #experience section
    if user_data.get("experience"):
        content.append(Paragraph("<b>EXPERIENCE</b>", styles["Heading2"]))
        content.append(Spacer(1, 6))
        
        for exp in user_data["experience"]:
            if isinstance(exp, dict):
                exp_text = ""
                
                # Role and Company
                if exp.get("role"):
                    exp_text += f"<b>{exp['role']}</b>"
                if exp.get("company"):
                    exp_text += f" - {exp['company']}"
                
                # Start Date and End Date: Only add if both exist
                start_date = exp.get("start_date", "").strip()
                end_date = exp.get("end_date", "").strip()
                if start_date.lower() != "unknown" and end_date.lower() != "unknown" and start_date and end_date:
                    exp_text += f"<br/><i>{start_date} - {end_date}</i>"
                
                # Description
                if exp.get("description"):
                    exp_text += f"<br/>{exp['description']}"
                
                # Add only if text exists
                if exp_text.strip():
                    content.append(Paragraph(exp_text, styles["Normal"]))
                    content.append(Spacer(1, 6))
        
        content.append(Spacer(1, 12))
        
    #project section
    if user_data.get("projects"):
        content.append(Paragraph("<b>PROJECTS</b>", styles["Heading2"]))
        content.append(Spacer(1, 6))

        if isinstance(user_data["projects"], list):
            for project in user_data["projects"]:
                if isinstance(project, dict):
                    project_text = ""

                    # Add project name and tech stack only if they exist
                    if project.get("name"):
                        project_text += f"<b>{project['name']}</b>"
                    if project.get("tech"):
                        project_text += f" [{project['tech']}]"
                    
                    # Add project link only if it exists and is valid
                    project_link = validate_link(project.get("link", ""))
                    if project_link:
                        project_text += f"<br/><a href='{project_link}'>{project_link}</a>"

                    # Add description only if it exists
                    if project.get("description"):
                        project_text += f"<br/>{project['description']}"

                    if project_text:  # Only add if there is content
                        content.append(Paragraph(project_text, styles["Normal"]))
                        content.append(Spacer(1, 6))

        content.append(Spacer(1, 12))

    # Skills (List)
    if user_data.get("skills"):
        content.append(Paragraph("<b>SKILLS</b>", styles["Heading2"]))
        content.append(Spacer(1, 6))

        if isinstance(user_data["skills"], list):
            bullet_items = [
                ListItem(Paragraph(skill, styles["Normal"]), leftIndent=10)
                for skill in user_data["skills"]
            ]
            if bullet_items:
                content.append(ListFlowable(bullet_items, bulletType="bullet"))

        content.append(Spacer(1, 12))
    
    # Volunteer Experience
    if user_data.get("volunteer"):
        content.append(Paragraph("<b>VOLUNTEER EXPERIENCE</b>", styles["Heading2"]))
        content.append(Spacer(1, 6))
        for vol in user_data["volunteer"]:
            if isinstance(vol, dict):
                vol_text = ""
                if vol.get("role"):
                    vol_text += f"<b>{vol['role']}</b>"
                if vol.get("organization"):
                    vol_text += f" - {vol['organization']}"
                
                start_date = vol.get('start_date', '').strip()
                end_date = vol.get('end_date', '').strip()
                date_text = f"<br/>{start_date} - {end_date}" if start_date and end_date else ""
                vol_text += date_text
                
                if vol.get("description"):
                    vol_text += f"<br/>{vol['description']}"
                
                if vol_text:
                    content.append(Paragraph(vol_text, styles["Normal"]))
                    content.append(Spacer(1, 6))
        content.append(Spacer(1, 12))
        
    # Achievements (List)
    if user_data.get("achievements"):
        content.append(Paragraph("<b>ACHIEVEMENTS</b>", styles["Heading2"]))
        content.append(Spacer(1, 6))

        if isinstance(user_data["achievements"], list):
            bullet_items = [
                ListItem(Paragraph(achievement, styles["Normal"]), leftIndent=10)
                for achievement in user_data["achievements"]
                if isinstance(achievement, str)
            ]
            if bullet_items:
                content.append(ListFlowable(bullet_items, bulletType="bullet"))

        content.append(Spacer(1, 12))

    # Build the PDF only if content exists
    if content:
        doc.build(content)

    return pdf_path

   
 