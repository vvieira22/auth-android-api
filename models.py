from typing import Optional
from pydantic import BaseModel, field_validator
from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(BaseModel):
    email: str
    password: str
    facebook_id: Optional[str] = None
    google_sub: Optional[str] = None
    biometric_data: Optional[str] = None
    nome: str
    data_nascimento: Optional[str] = None
    data_criacao: Optional[str] = None
    
class UserSchema(Base):
    __tablename__ = "usuarios"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    email: str = Column(String, unique=True)
    password: Optional[str] = Column(String)
    facebook_id: Optional[str] = Column(String)
    google_sub: Optional[str] = Column(String)
    biometric_data: Optional[str] = Column(String)
    nome: str = Column(String)
    data_nascimento: Optional[str] = Column(String) #pode ter ou n essa informacao com login social.
    data_criacao: Optional[str] = Column(String)

    #se eu precisasse validar algo internamente (acho que e papel da aplicacao que chama essa api)
    # @field_validator('nome')
    # def validate_name(cls, value):
    #     if len(value) < 3:
    #         raise ValueError('nome must be at least 3 characters long')
    #     return value    
    
class Login(BaseModel):
    email: Optional[str] = None
    password: Optional[str] = None
    id_token: Optional[str] = None #google and facebook auth
    biometric_data: Optional[str] = None