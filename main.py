from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlmodel import SQLModel

import validators
from config import FACEBOOK, GMAIL, DEFAULTLOGIN, engine, SessionLocal
import models
from fastapi import FastAPI, HTTPException, Depends
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer
import jwt

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
def get_current_user(token: str = Depends(oauth2_scheme), SECRET_KEY="sua_chave_secreta"):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return "Token valid"
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.PyJWTError:
        raise credentials_exception

@app.post("/cadastro/", dependencies=[Depends(get_current_user)])
def create_user(usr: models.User, db: db_dependency):
    db_user = models.UserSchema(
        email=usr.email,
        password=usr.password,
        facebook_provider=usr.facebook_provider,
        gmail_provider=usr.gmail_provider,
        nome=usr.nome,
        sobrenome=usr.sobrenome,
        data_nascimento=usr.data_nascimento,
        data_criacao=usr.data_criacao
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/login/", dependencies=[Depends(get_current_user)])
def login(usr: models.Login, db: db_dependency):
    try:
        logintype = validators.validar_campos_login(usr)
        if logintype:
            try:
                if logintype == FACEBOOK:
                    user = db.query(models.UserSchema).filter(
                        models.UserSchema.facebook_provider 
                        == usr.facebook_provider).first()
                elif logintype == GMAIL:
                    user = db.query(models.UserSchema).filter(
                        models.UserSchema.gmail_provider 
                        == usr.gmail_provider).first()
                elif logintype == DEFAULTLOGIN: #talvez no futuro tratar melhor essa senha, em vez de comparar direto com o banco
                    user = db.query(models.UserSchema).filter(
                        models.UserSchema.password == usr.password and models.UserSchema.email == usr.email).first()
                else:  
                    raise HTTPException(status_code=404, detail="Usuário não encontrado no sistema.")
            except Exception as e: #tratar erros de consulta/conexao banco, nao necessariamente tem algo errado com os dados
                return e
            if user:
                return user
        else:
            raise HTTPException(status_code=404, detail="Dados incompletos ou faltantes.")
    except Exception as e:
        return e

@app.get("/usuarios/")
def usuarios(db: db_dependency):
    return db.query(models.UserSchema).all()