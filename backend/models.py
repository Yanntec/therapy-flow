from sqlalchemy import (
    Column, Integer, String, Text, TIMESTAMP,
    ForeignKey, text, Boolean)
from database import Base

class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    geburtsdatum = Column(String(50), nullable=False)
    qr_code = Column(String(255), unique=True, nullable=False)

    # User who owns this patient record
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)
    datum = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    therapeut_id = Column(String(100))

# sessions_id + tag zusammen als PK, damit derselbe tag nicht doppelt an
# einer session hängen kann
class SessionTag(Base):
    __tablename__ = "sessions_tags"

    sessions_id = Column(Integer, ForeignKey("sessions.id", ondelete="CASCADE"), primary_key=True)
    tag = Column(String(100), nullable=False, primary_key=True)

# sessions_id ist hier die PK -> es kann also nur eine Notiz pro Session geben,
# nicht mehrere
class Note(Base):
    __tablename__ = "notes"

    sessions_id = Column(Integer, ForeignKey("sessions.id", ondelete="CASCADE"), primary_key=True)
    freitext = Column(Text)
    textbaustein_id = Column(Integer)

class Template(Base):
    __tablename__ = "templates"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    docx_pfad = Column(String(255), nullable=False)

class GeneratedDocument(Base):
    __tablename__ = "generated_documents"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)
    template_id = Column(Integer, ForeignKey("templates.id", ondelete="CASCADE"), nullable=False)
    erstellt_am = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)