import os
from sqlite3 import IntegrityError
from fastapi import APIRouter, HTTPException
from fastapi.security import OAuth2PasswordBearer
import jwt
from passlib.context import CryptContext
from pydantic import BaseModel
import sqlalchemy
from sqlalchemy.orm import Session
from config import DEFAULTLOGIN, FACEBOOK, GMAIL
import models
import validators
from datetime import datetime, timedelta, UTC

SECRET_KEY = os.getenv("SECRET_KEY")    
ALGORITHM = os.getenv("ALGORITHM")
TIMEOUT_TOKEN = os.getenv("TIMEOUT_TOKEN")
ALGORITHM_PASSWORD = os.getenv("ALGORITHM_PASSWORD")

bcrypt_context = CryptContext(schemes=[ALGORITHM_PASSWORD])

class UserUseCase:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def user_register(self, user: models.User):
        db_user = models.UserSchema(
            email=user.email,
            password=bcrypt_context.hash(user.password),
            biometric_data=user.biometric_data,
            facebook_token=user.facebook_token,
            gmail_token=user.gmail_token,
            nome=user.nome,
            sobrenome=user.sobrenome,
            data_nascimento=user.data_nascimento,
            data_criacao=user.data_criacao
        )
        try:
            self.db_session.add(db_user)
            self.db_session.commit()
            self.db_session.refresh(db_user)
            return db_user
        except sqlalchemy.exc.IntegrityError:
            raise HTTPException(status_code=400, detail="User already exists")
        
    def user_login(self, user: models.Login, expires_in: int = 45):    
        login_type = user.grand_type
        payload = {}
        exp = datetime.now(UTC) + timedelta(minutes=expires_in)
        
        try:
            if login_type == DEFAULTLOGIN:
                if user.email and user.password:
                    db_user = self.db_session.query(models.UserSchema).filter_by(email=user.email).first()
                    if db_user and bcrypt_context.verify(user.password, db_user.password):
                        payload = {
                            "sub": user.email,
                            "exp": exp
                        }
                        acess_token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
                        return acess_token
                    raise HTTPException(status_code=404, detail="Invalid username or password.")       
                raise HTTPException(status_code=404, detail="Invalid or empty body elements at request.")
            
            elif login_type == FACEBOOK:
                if user.id_token:
                    db_user = self.db_session.query(models.UserSchema).filter_by(facebook_token=user.id_token).first()
                    if db_user and db_user.facebook_token == user.id_token:
                        payload = {
                            "sub": user.id_token,
                            "exp": exp
                        }
                        acess_token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
                        return acess_token
                    raise HTTPException(status_code=404, detail="Invalid facebook user or not registered yet.")
                raise HTTPException(status_code=404, detail="Invalid or empty body elements at request.")
            
            elif login_type == GMAIL:
                if user.id_token:
                    db_user = self.db_session.query(models.UserSchema).filter_by(gmail_token=user.id_token).first()
                    if db_user and db_user.gmail_token == user.id_token:
                        payload = {
                            "sub": user.id_token,
                            "exp": exp
                        }
                        acess_token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
                        return acess_token
                    raise HTTPException(status_code=404, detail="Invalid gmail user or not registered yet.")
                raise HTTPException(status_code=404, detail="Invalid or empty body elements at request.")
                
            elif login_type == "biometric" :
                if user.biometric_data :
                    db_user = self.db_session.query(models.UserSchema).filter_by(biometric_data=user.biometric_data).first()
                    if db_user and db_user.biometric_data == user.biometric_data:
                        payload = {
                            "sub": user.biometric_data,
                            "exp": exp
                        }
                        acess_token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
                        return acess_token
                    raise HTTPException(status_code=404, detail="Invalid biometric data or not registered yet.")
                raise HTTPException(status_code=404, detail="Invalid or empty body elements at request.")
            else:
                raise HTTPException(status_code=404, detail="Invalid login type.")
        except Exception as e:
            raise HTTPException(status_code=404, detail=str(e))