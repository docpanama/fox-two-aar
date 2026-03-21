from pathlib import Path
import uuid
import random
import string

from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel
from docx import Document

app = FastAPI()

OUTPUT_DIR = Path("generated_aars")
OUTPUT_DIR.mkdir(exist_ok=True)


def generate_learner_id(length: int = 4) -> str:
    chars = string.ascii_uppercase + string.digits
    return "".join(random.choices(chars, k=length))


class AARRequest(BaseModel):
    certification_level: str
    cct_experience_level: str
    scenario_id: str
    scenario_title: str
    aar_text: str


@app.get("/")
def home():
    return {"message": "AAR generator is running"}


@app.post("/generate-aar")
def generate_aar(data: AARRequest):
    learner_id = generate_learner_id()
    filename = f"{learner_id}_{uuid.uuid4().hex[:6]}.docx"
    file_path = OUTPUT_DIR / filename

    doc = Document()
    doc.add_heading("After Action Report (AAR)", 0)

    doc.add_paragraph(f"Learner ID: {learner_id}")
    doc.add_paragraph(f"Certification Level: {data.certification_level}")
    doc.add_paragraph(f"CCT Experience Level: {data.cct_experience_level}")
    doc.add_paragraph(f"Scenario ID: {data.scenario_id}")
    doc.add_paragraph(f"Scenario Title: {data.scenario_title}")
    doc.add_paragraph("")

    for line in data.aar_text.splitlines():
        if line.strip() == "":
            doc.add_paragraph("")
        elif line.startswith("## "):
            doc.add_heading(line[3:].strip(), level=1)
        elif line.startswith("- "):
            doc.add_paragraph(line[2:].strip(), style="List Bullet")
        else:
            doc.add_paragraph(line)

    doc.save(file_path)

    return {
        "success": True,
        "learner_id": learner_id,
        "filename": filename,
        "download_url": f"/download/{filename}"
    }


@app.get("/download/{filename}")
def download_file(filename: str):
    file_path = OUTPUT_DIR / filename
    return FileResponse(file_path)
