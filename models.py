from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel
from sqlalchemy import Column, String, Date, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(BaseModel):
    email: str
    password: str
    facebook_provider: Optional[str] = None
    gmail_provider: Optional[str] = None
    nome: str
    sobrenome: str
    data_nascimento: date
    data_criacao: datetime

class Login(BaseModel):
    email: Optional[str] = None
    password: Optional[str] = None
    facebook_provider: Optional[str] = None
    gmail_provider: Optional[str] = None

class UserSchema(Base):
    __tablename__ = "usuarios"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    email: str = Column(String)
    password: str = Column(String)
    facebook_provider: Optional[str] = Column(String)
    gmail_provider: Optional[str] = Column(String)
    nome: str = Column(String)
    sobrenome: str = Column(String)
    data_nascimento: date = Column(Date)
    data_criacao: datetime = Column(DateTime)