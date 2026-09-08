import os
import io
import secrets
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from datetime import date
from docx import Document
import qrcode

import models
import schemas
from database import engine, get_db, SessionLocal

app = FastAPI(title="TherapieFlow API", version="1.0")

# erstmal alles offen für localhost-testing, für den scharfen Betrieb enger machen!
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

models.Base.metadata.create_all(bind=engine)


def init_db():
    db = SessionLocal()
    # beim allerersten Start ist die Tabelle leer, dann 2 Test-Patienten reinpacken
    if db.query(models.Patient).count() == 0:
        db.add(models.Patient(name="Anna Schmidt", geburtsdatum="14.05.1995", qr_code=secrets.token_urlsafe(16)))
        db.add(models.Patient(name="Max Mustermann", geburtsdatum="14.05.1995", qr_code=secrets.token_urlsafe(16)))
        db.commit()
    db.close()

init_db()

@app.get("/patients", response_model=List[schemas.PatientResponse])
def get_patients(db: Session = Depends(get_db)):
    patients = db.query(models.Patient).all()
    return patients

@app.get("/tags")
def get_tags():
    return [
        "#Motorik", "#Gleichgewicht", "#GuteTagesform", 
        "#Schmerzreduktion", "#Kraftaufbau", "#Eingeschränkt", "#Fortschritt"
    ]

@app.get("/textbausteine")
def get_textbausteine():
    return {
        "Allgemein": [
            "Patient kam pünktlich und motiviert zur Einheit.",
            "Therapieverlauf stabil, Übungen wurden gut angenommen."
        ],
        "Motorik & Koordination": [
            "Feinmotorische Übungen zeigten verbesserte Koordination im Vergleich zur Vorwoche.",
            "Grobmotorischer Aufbau stabil, Belastbarkeit gesteigert."
        ]
    }

@app.post("/sessions")
def create_session(session_data: schemas.SessionCreate, db: Session = Depends(get_db)):
    db_session = models.Session(
        patient_id=session_data.patient_id,
        therapeut_id=session_data.therapeut_id
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)

    for tag in session_data.tags:
        db_tag = models.SessionTag(sessions_id=db_session.id, tag=tag)
        db.add(db_tag)

    # nur speichern wenn wirklich was drinsteht, sonst haben wir am ende
    # leere notiz-zeilen für jede session in der db
    if session_data.freitext or session_data.textbaustein_id:
        db_note = models.Note(
            sessions_id=db_session.id,
            freitext=session_data.freitext,
            textbaustein_id=session_data.textbaustein_id
        )
        db.add(db_note)

    db.commit()
    return {"status": "success", "session_id": db_session.id}


@app.get("/generate-doc/{patient_id}")
def generate_patient_document(patient_id: int, db: Session = Depends(get_db)):
    patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient nicht gefunden")

    sessions = db.query(models.Session).filter(models.Session.patient_id == patient_id).all()

    doc = Document()
    doc.add_heading(f"Verlaufsbericht: {patient.name}", level=1)
    doc.add_paragraph(f"Geburtsdatum: {patient.geburtsdatum}")
    doc.add_paragraph(f"Patienten-ID: {patient.id}")
    
    doc.add_heading("Dokumentierte Sitzungen", level=2)

    if not sessions:
        doc.add_paragraph("Für diesen Patienten sind noch keine Sitzungen erfasst worden.")
    else:
        for idx, session in enumerate(sessions, start=1):
            doc.add_heading(f"Sitzung {idx}", level=3)

            tags = db.query(models.SessionTag).filter(models.SessionTag.sessions_id == session.id).all()
            tags_str = ", ".join([t.tag for t in tags])
            if tags_str:
                doc.add_paragraph(f"Schwerpunkte / Tags: {tags_str}")

            note = db.query(models.Note).filter(models.Note.sessions_id == session.id).first()
            if note and note.freitext:
                doc.add_paragraph(f"Notizen:\n{note.freitext}")
            else:
                doc.add_paragraph("Keine Notizen hinterlegt.")
            
            doc.add_paragraph("-" * 40)

    filename = f"Verlaufsbericht_{patient.name.replace(' ', '_')}.docx"
    # /tmp gibts unter windows so nicht, deshalb hier einfach ins arbeitsverzeichnis speichern
    file_path = os.path.join("/tmp", filename) if os.name != 'nt' else filename
    doc.save(file_path)

    return FileResponse(
        path=file_path, 
        filename=filename, 
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )


@app.get("/patient-by-qr/{qr_code}", response_model=schemas.PatientResponse)
def get_patient_by_qr(qr_code: str, db: Session = Depends(get_db)):
    patient = db.query(models.Patient).filter(models.Patient.qr_code == qr_code).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient mit diesem QR-Code nicht gefunden")
    return patient


@app.get("/patients/{patient_id}/qr-image")
def get_patient_qr_image(patient_id: int, db: Session = Depends(get_db)):
    patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient nicht gefunden")

    # bild landet nirgends auf der platte, wird nur im ram gebaut und direkt
    # als stream durchgereicht - spart uns das aufräumen von temp-dateien
    img = qrcode.make(patient.qr_code, box_size=10, border=2)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)

    return StreamingResponse(
        buf,
        media_type="image/png",
        headers={"Cache-Control": "no-store"},  # sonst zeigt der browser nach nem neuen code noch den alten
    )


@app.post("/patients/{patient_id}/regenerate-qr", response_model=schemas.PatientResponse)
def regenerate_patient_qr(patient_id: int, db: Session = Depends(get_db)):
    patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient nicht gefunden")

    # random token, hat nix mit name oder id zu tun - sonst könnte man
    # den code für andere patienten erraten
    patient.qr_code = secrets.token_urlsafe(16)
    db.commit()
    db.refresh(patient)
    return patient