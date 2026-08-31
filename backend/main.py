from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

import models
import schemas
from database import engine, get_db

app = FastAPI(title="TherapieFlow API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Erlaubt Anfragen von allen Quellen (für die Entwicklung ideal)
    allow_credentials=True,
    allow_methods=["*"],  # Erlaubt alle HTTP-Methoden (GET, POST, etc.)
    allow_headers=["*"],  # Erlaubt alle Header
)

@app.get("/patients", response_model=List[schemas.PatientResponse])
def get_patients(db: Session = Depends(get_db)):
    patients = db.query(models.Patient).all()
    return patients

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