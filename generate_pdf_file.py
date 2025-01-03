from fpdf import FPDF
from abstra.common import get_persistent_dir
import os
from uuid import uuid4
from PIL import Image

persistent_dir = get_persistent_dir()
pdf_folder = persistent_dir / "pdf"
anomalies_folder = persistent_dir / "anomalies"

if not pdf_folder.exists():
    os.makedirs(pdf_folder)

if not anomalies_folder.exists():
    os.makedirs(anomalies_folder)

logo_path = "logo.png"

# Templated texts
engineer_text = """
Engineer in Charge: {name} - {email}
Job Title: {job_title} - {credentials}
"""
reviewer_text = """
Reviewer: {name} - {email}
Job Title: {job_title} - {credentials}
"""
request_text = """
Solicitor: {name} - {email}
Location: {address} - {zip}
Reason: {reason}
"""
inspection_text = """
Inspector: {name} - {email}
Job Title: {job_title} - {credentials}
Date: {date}
Analyzed Scopes: {scopes}
"""
anomaly_text = """
Type: {type}
Location: {location}
"""
conclusion_text = """
Decision: {engineer_decision}
Conclusion: {conclusion}
"""


def image_dimensions(image_path):
    with Image.open(image_path) as img:
        return img.size


class PDF(FPDF):
    font = "Arial"

    def header(self):
        logo_width = 35
        page_width = self.w
        x_position = (page_width - logo_width) / 2
        self.image(str(logo_path), x_position, 10, logo_width)
        self.ln(30)

    def add_image(self, image_path):
        # Check if image will fit in the page
        if self.get_y() + 55 > self.h:
            self.add_page()

        # Get image dimensions
        image_width, image_height = image_dimensions(image_path)

        # Calculate display position to make it centered
        display_height = 50
        display_width = float(image_width * display_height) / image_height

        image_x_pos = float(self.w - display_width) / 2

        # Add image to the page
        self.image(str(image_path), image_x_pos, self.get_y(), h=display_height)
        self.ln(55)

    def footer(self):
        self.set_y(-15)
        self.set_font(PDF.font, "", 8)
        self.cell(0, 10, f"{self.page_no()}", 0, 0, "C")

    def chapter_title(self, title):
        self.set_font(PDF.font, "B", 16)
        self.cell(0, 10, title, 0, 1, "C")
        self.ln(10)

    def chapter_body(
        self, body, *, font_size=8, style="", align="", indent=0, color="black"
    ):
        self.set_text_color(0, 0, 0)

        if color == "red":
            self.set_text_color(255, 0, 0)

        self.set_font(PDF.font, style, font_size)

        self.set_left_margin(self.l_margin + indent * 10)
        self.set_right_margin(self.r_margin + indent * 10)

        self.multi_cell(0, (font_size / 2) + 1, body, align=align)

        self.set_left_margin(self.l_margin - indent * 10)
        self.set_right_margin(self.r_margin - indent * 10)
        self.ln()


def generate_pdf_file(task):
    task_payload = task.get_payload()

    solicitor = task_payload["solicitor"]
    inspector = task_payload["plan"]["inspector"]
    report = task_payload["report"]
    engineer = report["engineer"]
    review = task_payload.get("review", {})
    reviewer = review.get("reviewer", None)

    pdf = PDF()
    pdf.add_page()

    # Info
    pdf.chapter_title("Technical Inspection")
    pdf.ln(50)
    pdf.chapter_body(
        engineer_text.format(
            name=engineer["name"],
            email=engineer["email"],
            job_title=engineer["title"],
            credentials=engineer["credentials"],
        ),
        align="C",
    )

    if reviewer is not None:
        pdf.chapter_body(
            reviewer_text.format(
                name=reviewer["name"],
                email=reviewer["email"],
                job_title=reviewer["title"],
                credentials=reviewer["credentials"],
            ),
            align="C",
        )
    else:
        pdf.chapter_body("Document not reviewed", align="C", color="red")

    # Request
    pdf.add_page()
    pdf.chapter_body("1. Request Details", font_size=12, style="B")
    pdf.chapter_body(
        request_text.format(
            name=solicitor["name"],
            email=solicitor["email"],
            address=task_payload["address"],
            zip=task_payload["zip"],
            reason=task_payload["reason"],
        ),
        indent=1,
    )
    pdf.ln(10)

    # Inspection
    pdf.chapter_body("2. Inspection Details", font_size=12, style="B")
    pdf.chapter_body(
        inspection_text.format(
            name=inspector["name"],
            email=inspector["email"],
            job_title=inspector["title"],
            credentials=inspector["credentials"],
            date=task_payload["plan"]["date"]["begin"].split("T")[0],
            scopes=", ".join([s["scope"] for s in task_payload["inspected_scopes"]]),
        ),
        indent=1,
    )

    # Anomalies
    pdf.add_page()
    pdf.chapter_body("3. Field Data", font_size=12, style="B")

    n_scope = 0
    for scope in task_payload["inspected_scopes"]:
        n_scope += 1
        pdf.chapter_body(
            f"3.{n_scope}. {scope['scope']}", font_size=10, style="B", indent=1
        )

        if scope["anomaly_present"]:
            pdf.chapter_body("Anomalies found:", indent=1)

            for anomaly in scope["anomalies_found"]:
                pdf.chapter_body(
                    anomaly_text.format(
                        type=anomaly["type"],
                        location=anomaly["location"],
                    ),
                    indent=1,
                )
                image_path = anomalies_folder / anomaly["file"]
                if image_path.exists():
                    pdf.add_image(image_path)

                pdf.ln(5)
        else:
            pdf.chapter_body("No anomalies found.", indent=1)
            pdf.ln(5)

    # Conclusion
    pdf.add_page()
    pdf.chapter_body("4. Conclusion", font_size=12, style="B")
    pdf.chapter_body(
        conclusion_text.format(
            engineer_decision=report["engineer_decision"],
            conclusion=report["conclusion"],
        ),
        indent=1,
    )

    # Export PDF
    file_name = f"{str(uuid4())}.pdf"
    file_path = pdf_folder / file_name

    pdf.output(str(file_path))

    return file_name
