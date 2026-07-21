from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class UsuarioRegistro(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)
    first_name: str = Field(..., min_length=2)
    last_name: str = Field(..., min_length=2)
    rol: str = Field(default='agricultor')
    telefono: Optional[str] = ''
    municipio: Optional[str] = ''
    
class UsuarioLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = 'bearer'

class UsuarioRespuesta(BaseModel):
    id: int
    username: str
    email: str
    first_name: str
    last_name: str
    rol: str
    telefono: str
    municipio: str
    
    class Config:
        from_attributes = True