"""Build André Vargas's ATS-friendly CV PDF (single column, selectable text)."""

import os

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, HRFlowable, KeepTogether,
)

OUT = "/home/andrevargas/projects/my_portfolio/static/Andre_Vargas_CV.pdf"
EMOJI_TTF = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "fonts", "NotoEmoji.ttf")

pdfmetrics.registerFont(TTFont("NotoEmoji", EMOJI_TTF))


def emj(ch):
    """An inline monochrome emoji glyph from Noto Emoji."""
    return f'<font face="NotoEmoji" color="#444444">{ch}</font>'


INK = HexColor("#1a1a1a")
MUTED = HexColor("#444444")
ACCENT = HexColor("#0d6e6e")  # teal, matches the site's accent

styles = {
    "name": ParagraphStyle(
        "name", fontName="Helvetica-Bold", fontSize=19, leading=23,
        alignment=TA_CENTER, textColor=INK, spaceAfter=2,
    ),
    "role": ParagraphStyle(
        "role", fontName="Helvetica", fontSize=11, leading=14,
        alignment=TA_CENTER, textColor=ACCENT, spaceAfter=5,
    ),
    "contact": ParagraphStyle(
        "contact", fontName="Helvetica", fontSize=8.5, leading=13,
        alignment=TA_CENTER, textColor=MUTED, spaceAfter=0,
    ),
    "h2": ParagraphStyle(
        "h2", fontName="Helvetica-Bold", fontSize=10.5, leading=13,
        textColor=ACCENT, spaceBefore=10, spaceAfter=2,
    ),
    "jobtitle": ParagraphStyle(
        "jobtitle", fontName="Helvetica-Bold", fontSize=10, leading=13,
        textColor=INK, spaceBefore=6, spaceAfter=0,
    ),
    "jobmeta": ParagraphStyle(
        "jobmeta", fontName="Helvetica", fontSize=9, leading=12.5,
        textColor=MUTED, spaceAfter=2,
    ),
    "body": ParagraphStyle(
        "body", fontName="Helvetica", fontSize=9, leading=13,
        textColor=INK, spaceAfter=2,
    ),
    "bullet": ParagraphStyle(
        "bullet", fontName="Helvetica", fontSize=9, leading=13,
        textColor=INK, leftIndent=12, bulletIndent=2, spaceAfter=1.5,
    ),
}


def rule():
    return HRFlowable(width="100%", thickness=0.7, color=ACCENT,
                      spaceBefore=0, spaceAfter=4)


def section(title):
    return [Paragraph(title.upper(), styles["h2"]), rule()]


def job(title, meta, bullets=None):
    header = [Paragraph(title, styles["jobtitle"]),
              Paragraph(meta, styles["jobmeta"])]
    items = [Paragraph(b, styles["bullet"], bulletText="•")
             for b in bullets or []]
    # Keep the job header glued to its first bullet
    return [KeepTogether(header + items[:1])] + items[1:]


story = []

# ---------------------------------------------------------------- header
story.append(Paragraph("André Vargas", styles["name"]))
story.append(Paragraph(
    "Machine Learning Engineer Specialist", styles["role"]))
story.append(Paragraph(
    f'{emj("🌐")} <link href="https://andrevargas.com.br" color="#444444">andrevargas.com.br</link> &nbsp;|&nbsp; '
    f'{emj("📧")} <link href="mailto:andrevargas22@gmail.com" color="#444444">andrevargas22@gmail.com</link>',
    styles["contact"]))
story.append(Paragraph(
    f'{emj("💻")} <link href="https://github.com/andrevargas22" color="#444444">github.com/andrevargas22</link> &nbsp;|&nbsp; '
    f'{emj("💼")} <link href="https://www.linkedin.com/in/andrevargas22/" color="#444444">linkedin.com/in/andrevargas22</link>',
    styles["contact"]))
story.append(Paragraph(
    f'{emj("📍")} Minas Gerais, Brazil', styles["contact"]))
story.append(Spacer(1, 6))

# ---------------------------------------------------------------- summary
story += section("Summary")
story.append(Paragraph(
    "Machine Learning Engineer specialising in MLOps, LLMOps and AIOps, "
    "building and deploying production-ready ML and AI systems. Solid "
    "background in cloud architecture (GCP, Azure, AWS), CI/CD, Databricks "
    "and MLflow, with a career path that went from hardware and IoT to Data "
    "Science, ML Engineering, MLOps, and now generative and agentic AI.",
    styles["body"]))

# ---------------------------------------------------------------- experience
story += section("Professional Experience")

story += job(
    "Machine Learning Engineer Specialist | Telefónica",
    "October 2026 - Present | Remote",
)

story += job(
    "Tech Lead · Machine Learning Engineer Specialist | Grupo Casas Bahia",
    "August 2024 - September 2026 | Remote",
    bullets=[
        "Led a team of 5 machine learning engineers, organising and driving projects, epics, KRs, and other initiatives "
        "in the development of Grupo Casas Bahia's AI Platform.",
        "Supported the migration of analytical datasets and ML pipelines "
        "from Azure to GCP (3,500+ processes) within a company-wide "
        "modernisation effort, enhancing performance, cost, and governance "
        "foundations.",
        "Engineered a new end-to-end CI/CD pipeline (Databricks + Airflow + "
        "GitHub Actions) for reproducible model and data deployments.",
        "Contributed to Cerberus, an internal tool to optimise the company's "
        "use of MLflow, improving governance, traceability, and "
        "reproducibility across ML models and LLM projects.",
        "Designed and built “Sauron”, an internal Databricks-based "
        "monitoring framework that automates data quality and drift "
        "dashboards across dev and prod via asset bundles, cutting manual "
        "setup time from hours to minutes.",
        "Created a versioning solution for Databricks Genie Agents, enabling "
        "a deployment pipeline for Genies and improving governance for the "
        "agents team.",
        "Monitored and operated 20+ Machine Learning models deployed and "
        "orchestrated on Databricks and Google Cloud.",
    ],
)

story += job(
    "Senior Data Scientist | Stefanini Brasil (Banco do Brasil)",
    "January 2024 - July 2024 | Remote",
    bullets=[
        "Built credit risk models to estimate the probability of asset "
        "default, supporting decision-making in portfolio management and "
        "regulatory compliance.",
        "Developed managerial market projection models to forecast financial "
        "trends, enabling strategic planning and business insights for "
        "senior stakeholders.",
    ],
)

story += job(
    "Machine Learning Engineer · Data Scientist | Falconi",
    "March 2022 - December 2023 | Remote",
    bullets=[
        "Designed cloud architecture solutions for Machine Learning systems "
        "and deployed models and APIs to production.",
        "Applied MLOps and CI/CD best practices; helped develop Falconi's "
        "internal MLOps stack and deployed its MLflow Server on Google "
        "Cloud Platform.",
        "Developed supervised and unsupervised Machine Learning models for "
        "a range of business problems, plus data apps and internal "
        "libraries to accelerate project delivery.",
    ],
)

story += job(
    "Hardware Engineer · Technology Specialist | SENAI-SP",
    "May 2018 - February 2022 | São Paulo, Brazil",
    bullets=[
        "Designed and prototyped hardware for industrial applications, from "
        "electronics and microcontrollers to embedded firmware.",
        "Delivered projects in the Internet of Things, Industrial "
        "Automation, Industry 4.0, and Digital Transformation.",
        "Took my first steps in Data Science, applying it to industrial "
        "projects, which set the direction for the rest of my career.",
    ],
)

# ---------------------------------------------------------------- education
story.append(KeepTogether(section("Education") + job(
    "B.Sc. in Mechatronics Engineering | Universidade de Brasília, Brazil",
    "2011 - 2017",
    bullets=[
        "Exchange year abroad at Cardiff University, United Kingdom "
        "(2014 - 2015).",
    ],
)))

# ---------------------------------------------------------------- skills
story += section("Technical Skills")
skills = [
    ("Machine Learning Platform &amp; Monitoring",
     "Databricks (Spark, Delta Lake, Unity Catalog), Lakehouse Monitoring, "
     "Asset Bundles, MLflow (tracking, registry, model packaging)"),
    ("GenAI, LLMOps &amp; Agents",
     "LLM lifecycle and governance with MLflow (tracking, evaluation, "
     "traceability), Databricks Genie Agents (versioning and deployment "
     "pipelines)"),
    ("Data Engineering &amp; Orchestration",
     "PySpark / Spark SQL, Airflow, SQL"),
    ("CI/CD &amp; Platform Engineering",
     "GitHub Actions, Docker, Kubernetes, GitOps workflows"),
    ("Cloud &amp; Infrastructure",
     "Google Cloud Platform (GCP), Microsoft Azure, Amazon Web Services "
     "(AWS)"),
    ("Model Serving &amp; Applications", "FastAPI, Streamlit, Flask"),
    ("Programming &amp; Core", "Python, SQL, Bash scripting"),
]
for label, items in skills:
    story.append(Paragraph(f"<b>{label}:</b> {items}", styles["bullet"]))

# ---------------------------------------------------------------- languages
story += section("Languages")
story.append(Paragraph(
    "Portuguese (native) &nbsp;|&nbsp; English (fluent) &nbsp;|&nbsp; "
    "Spanish (advanced) &nbsp;|&nbsp; Italian (basic)",
    styles["body"]))

doc = SimpleDocTemplate(
    OUT, pagesize=A4,
    leftMargin=1.9 * cm, rightMargin=1.9 * cm,
    topMargin=1.5 * cm, bottomMargin=1.5 * cm,
    title="André Vargas - CV",
    author="André Vargas",
    subject="Machine Learning Engineer Specialist",
)
doc.build(story)
print("written:", OUT)
