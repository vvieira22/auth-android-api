from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, field_validator
from sqlalchemy import Column, String, Date, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(BaseModel):
    email: str
    password: str
    facebook_token: Optional[str] = None
    gmail_token: Optional[str] = None
    biometric_data: Optional[str] = None
    nome: str
    sobrenome: str
    data_nascimento: date
    data_criacao: datetime
    
class UserSchema(Base):
    __tablename__ = "usuarios"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    email: str = Column(String, unique=True)
    password: str = Column(String)
    facebook_token: Optional[str] = Column(String)
    gmail_token: Optional[str] = Column(String)
    biometric_data: Optional[str] = Column(String)
    nome: str = Column(String)
    sobrenome: str = Column(String)
    data_nascimento: date = Column(Date)
    data_criacao: datetime = Column(DateTime)

    #se eu precisasse validar algo internamnete (acho que e papel da aplicacao que chama essa api)
    # @field_validator('nome')
    # def validate_name(cls, value):
    #     if len(value) < 3:
    #         raise ValueError('nome must be at least 3 characters long')
    #     return value    
    
class Login(BaseModel):
    grand_type: str #password, google, facebook, biometric
    email: Optional[str] = None
    password: Optional[str] = None
    id_token: Optional[str] = None #google and facebook auth
    biometric_data: Optional[str] = None