from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel
from docx import Document
import uuid
import os

app = FastAPI()

# Ensure output directory exists
OUTPUT_DIR = "generated_docs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# -----------------------------
# Health Check (for Render)
# -----------------------------
@app.get("/health")
def health_check():
    return {"status": "ok"}


# -----------------------------
# Request Schema
# -----------------------------
class AARRequest(BaseModel):
    certification_level: str
    cct_experience_level: str
    scenario_id: str
    scenario_title: str
    aar_text: str


# -----------------------------
# AAR Generator Endpoint
# -----------------------------
@app.post("/generate-aar")
def generate_aar(data: AARRequest):

    # Generate random learner ID (4-char alphanumeric)
    learner_id = uuid.uuid4().hex[:4].upper()

    # Create document
    doc = Document()

    doc.add_heading("After Action Report (AAR)", 0)

    doc.add_paragraph(f"Learner ID: {learner_id}")
    doc.add_paragraph(f"Certification Level: {data.certification_level}")
    doc.add_paragraph(f"CCT Experience Level: {data.cct_experience_level}")
    doc.add_paragraph(f"Scenario ID: {data.scenario_id}")
    doc.add_paragraph(f"Scenario Title: {data.scenario_title}")

    doc.add_paragraph("")  # spacer

    # Add AAR text (preserve formatting)
    for line in data.aar_text.split("\n"):
        doc.add_paragraph(line)

    # Save file
    filename = f"{learner_id}.docx"
    file_path = os.path.join(OUTPUT_DIR, filename)
    doc.save(file_path)

    # Return download path
    return {
        "learner_id": learner_id,
        "download_url": f"/download/{filename}"
    }


# -----------------------------
# File Download Endpoint
# -----------------------------
@app.get("/download/{filename}")
def download_file(filename: str):
    file_path = os.path.join(OUTPUT_DIR, filename)
    return FileResponse(file_path, media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
