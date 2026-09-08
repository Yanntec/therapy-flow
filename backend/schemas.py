from pydantic import BaseModel
from typing import List, Optional

class PatientResponse(BaseModel):
    id: int
    name: str
    geburtsdatum: str
    qr_code: str

    class Config:
        from_attributes = True

class SessionCreate(BaseModel):
    patient_id: int
    therapeut_id: Optional[str] = "Nicole"  # solang nur eine therapeutin das nutzt, reicht der default
    tags: List[str] = []
    freitext: Optional[str] = ""
    textbaustein_id: Optional[int] = None