import os
from sqlite3 import IntegrityError
from fastapi import APIRouter, HTTPException
from fastapi.security import OAuth2PasswordBearer
import jwt
from passlib.context import CryptContext
from pydantic import BaseModel
import sqlalchemy
from sqlalchemy.orm import Session
from config import DEFAULTLOGIN, FACEBOOK, GOOGLE
import models
from utils import get_google_data
from datetime import datetime, timedelta, UTC
from google.oauth2 import id_token
from google.auth.transport import requests
from jwt.algorithms import get_default_algorithms

SECRET_KEY = os.getenv("SECRET_KEY")    
ALGORITHM = os.getenv("ALGORITHM_TOKEN")    
TIMEOUT_TOKEN = int(os.getenv("TIMEOUT_TOKEN"))
ALGORITHM_PASSWORD = os.getenv("ALGORITHM_PASSWORD")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")

bcrypt_context = CryptContext(schemes=[ALGORITHM_PASSWORD])

class UserUseCase:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def register(self, user: models.User, type: str):
        try:
            if type == DEFAULTLOGIN:
                db_user = models.UserSchema(
                email=user.email,
                password=bcrypt_context.hash(user.password),
                biometric_data=user.biometric_data,
                facebook_id=user.facebook_id,
                google_sub=user.google_sub,
                nome=user.nome,
                data_nascimento=user.data_nascimento,
                data_criacao=user.data_criacao
            )
            elif type == GOOGLE:
                usr_data = get_google_data(user.google_sub)
                if usr_data:
                    db_user = models.UserSchema(
                        email=usr_data.get("email"),
                        password=bcrypt_context.hash(user.password) if user.password  else "", #so cryptografar se tiver senha
                        biometric_data=user.biometric_data,
                        facebook_id=user.facebook_id,
                        google_sub=usr_data.get("sub"),
                        nome=usr_data.get("name"),
                        data_nascimento=user.data_nascimento,
                        data_criacao=user.data_criacao
                    )
            # elif type == FACEBOOK:
            #     //TODO
            
            self.db_session.add(db_user)
            self.db_session.commit()
            self.db_session.refresh(db_user)
            return db_user
        except sqlalchemy.exc.IntegrityError:
            raise HTTPException(status_code=208, detail="User already exists.")
        
    def login(self, user: models.Login, login_type: str , expires_in: int = TIMEOUT_TOKEN): 
        try:
            payload = {}
            exp = datetime.now(UTC) + timedelta(minutes=expires_in)
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
            
            elif login_type == GOOGLE:
                if user.id_token:
                    usr_data = get_google_data(user.id_token)
                    if usr_data:
                        sub = usr_data.get("sub") #from api google auth    
                        db_user = self.db_session.query(models.UserSchema).filter_by(google_sub=sub).first()

                        if db_user and db_user.google_sub == sub:
                            payload = {
                                "sub": sub,
                                "exp": exp
                            }

                            acess_token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
                            return {acess_token}
                    
                    raise HTTPException(status_code=404, detail="Invalid google user or not registered yet.")
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
        
    def verify_token(self, acess_token):
        try:
            data = jwt.decode(acess_token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_exp": False})
        except Exception as e:
            raise HTTPException(status_code=404, detail=str(e))
        try:
            db_user_password = self.db_session.query(models.UserSchema).filter_by(email=data['sub']).first()
            if(db_user_password):
                return
            
            #facebook
            db_user_face = self.db_session.query(models.UserSchema).filter_by(facebook_id=data['sub']).first() 
            if(db_user_face):
                pass
            
            #google
            db_user_google = self.db_session.query(models.UserSchema).filter_by(google_sub=data['sub']).first()     
            if(db_user_google):
                return {"message": "User found for this credentials."}
            
            #biometric 
            db_user_biometric = self.db_session.query(models.UserSchema).filter_by(biometric_data=data['sub']).first()
            if(db_user_biometric):
                pass
            
            raise HTTPException(status_code=404, detail="User not found for this credentials.")
        except Exception as e:
            raise HTTPException(status_code=404, detail=str(e))
