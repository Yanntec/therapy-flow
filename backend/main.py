import os
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from datetime import date
from docx import Document

import models
import schemas
from database import engine, get_db, SessionLocal

app = FastAPI(title="TherapieFlow API", version="1.0")

# CORS aktivieren
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Erlaubt Anfragen von allen Quellen (für die Entwicklung ideal)
    allow_credentials=True,
    allow_methods=["*"],  # Erlaubt alle HTTP-Methoden (GET, POST, etc.)
    allow_headers=["*"],  # Erlaubt alle Header
)

# 1. Tabellen automatisch erstellen
models.Base.metadata.create_all(bind=engine)


def init_db():
    db = SessionLocal()
    if db.query(models.Patient).count() == 0:
        db.add(models.Patient(name="Anna Schmidt", geburtsdatum="14.05.1995", qr_code="QR-ANNA-001"))
        db.add(models.Patient(name="Max Mustermann", geburtsdatum="14.05.1995", qr_code="QR-MAX-002"))
        db.commit()
    db.close()

init_db()

@app.get("/patients", response_model=List[schemas.PatientResponse])
def get_patients(db: Session = Depends(get_db)):
    patients = db.query(models.Patient).all()
    return patients

# --- Endpunkte für Tags und Textbausteine ---

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

# -----------------------------------------------

@app.post("/sessions")
def create_session(session_data: schemas.SessionCreate, db: Session = Depends(get_db)):
    # 1. Session anlegen
    db_session = models.Session(
        patient_id=session_data.patient_id,
        therapeut_id=session_data.therapeut_id
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)

    # 2. Tags speichern
    for tag in session_data.tags:
        db_tag = models.SessionTag(sessions_id=db_session.id, tag=tag)
        db.add(db_tag)

    # 3. Notiz speichern
    if session_data.freitext or session_data.textbaustein_id:
        db_note = models.Note(
            sessions_id=db_session.id,
            freitext=session_data.freitext,
            textbaustein_id=session_data.textbaustein_id
        )
        db.add(db_note)

    db.commit()
    return {"status": "success", "session_id": db_session.id}


# --- Dokument-Generierung nur für den aktiven Patienten ---

@app.get("/generate-doc/{patient_id}")
def generate_patient_document(patient_id: int, db: Session = Depends(get_db)):
    # 1. Patient aus der Datenbank laden
    patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient nicht gefunden")

    # 2. NUR die Sitzungen holen, die exakt zu dieser patient_id gehören
    sessions = db.query(models.Session).filter(models.Session.patient_id == patient_id).all()

    # 3. Word-Dokument erstellen
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
            
            # Zugehörige Tags für diese Sitzung abrufen
            tags = db.query(models.SessionTag).filter(models.SessionTag.sessions_id == session.id).all()
            tags_str = ", ".join([t.tag for t in tags])
            if tags_str:
                doc.add_paragraph(f"Schwerpunkte / Tags: {tags_str}")
            
            # Zugehörige Notiz für diese Sitzung abrufen
            note = db.query(models.Note).filter(models.Note.sessions_id == session.id).first()
            if note and note.freitext:
                doc.add_paragraph(f"Notizen:\n{note.freitext}")
            else:
                doc.add_paragraph("Keine Notizen hinterlegt.")
            
            doc.add_paragraph("-" * 40)

    # 4. Datei temporär speichern
    filename = f"Verlaufsbericht_{patient.name.replace(' ', '_')}.docx"
    file_path = os.path.join("/tmp", filename) if os.name != 'nt' else filename
    doc.save(file_path)

    # 5. Als Datei an den Browser zurücksenden
    return FileResponse(
        path=file_path, 
        filename=filename, 
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )


# --- NEU: Patient per QR-Code abfragen ---

@app.get("/patient-by-qr/{qr_code}", response_model=schemas.PatientResponse)
def get_patient_by_qr(qr_code: str, db: Session = Depends(get_db)):
    patient = db.query(models.Patient).filter(models.Patient.qr_code == qr_code).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient mit diesem QR-Code nicht gefunden")
    return patient