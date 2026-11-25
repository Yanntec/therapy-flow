from pydantic import BaseModel
from typing import List, Optional

class PatientCreate(BaseModel):
    name: str
    geburtsdatum: str
    
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


class UserCreate(BaseModel):
    name: str
    email: str
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    is_active: bool

    class Config:
        from_attributes = True
