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
                if(not user.password):
                    raise HTTPException(status_code=404, detail="Password is required.")
                elif(not user.email):
                    raise HTTPException(status_code=404, detail="Email is required.")
                elif(not user.nome):
                    raise HTTPException(status_code=404, detail="Name is required.")
                else:
                    db_user = models.UserSchema(
                    email=user.email,
                    password=bcrypt_context.hash(user.password),
                    biometric_data=user.biometric_data,
                    facebook_id=user.facebook_id,
                    google_sub=user.google_sub,
                    nome=user.nome,
                    documento=user.documento,
                    data_nascimento=user.data_nascimento,
                    data_criacao=user.data_criacao,
                    telefone=user.telefone
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
                        documento=user.documento,
                        data_nascimento=user.data_nascimento,
                        data_criacao=user.data_criacao,
                        telefone=user.telefone
                    )
            # elif type == FACEBOOK:
            #     //TODO
            
            self.db_session.add(db_user)
            self.db_session.commit()
            self.db_session.refresh(db_user)
            return db_user
        except sqlalchemy.exc.IntegrityError:
            raise HTTPException(status_code=409, detail="User already exists.")
        except Exception as e:
            raise HTTPException(status_code=404, detail=str(e))

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
                        return {"access_token": acess_token}
                    raise HTTPException(status_code=401, detail="Invalid username or password.")
                    return      
                raise HTTPException(status_code=404,verify_tokendetail="Invalid or empty body elements at request.")
            
            elif login_type == GOOGLE:
                if self.is_auth_social_registered(user, GOOGLE):
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
                        raise HTTPException(status_code=404, detail="User authenticated but invalid google token.")
                    raise HTTPException(status_code=404, detail="User registered but not with google.")
                else:
                    raise HTTPException(status_code=503, detail="User not registered yet.")
            
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
        except HTTPException as e:
            raise HTTPException(status_code=e.status_code, detail=e.detail)     
        
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

    def check_user_auth_social(self, user: models.Login):
            try:
                db_user = self.db_session.query(models.UserSchema).filter_by(email=user.email).first()
            except Exception as e:
                raise HTTPException(status_code=404, detail=str(e))
            
            if db_user:
                #google + password login
                if(db_user.google_sub == user.id_token):
                    if(db_user.email == user.email):
                        raise HTTPException(status_code=200, detail="User registered with google and password.")
                    raise HTTPException(status_code=200, detail="User registered with google.")
                #facebook + password login
                if(db_user.facebook_id == getattr(user, "id_token", None)):
                    if(db_user.email == getattr(user, "email", None)):
                        raise HTTPException(status_code=200, detail="User registered with facebook and password.")
                    raise HTTPException(status_code=200, detail="User registered with facebook.")
                if(db_user.email == user.email):
                    raise HTTPException(status_code=200, detail="User registered with password.")
                raise HTTPException(status_code=404, detail="User not registered yet.")
            else:   
                raise HTTPException(status_code=404, detail="User not registered yet.")

    def is_auth_social_registered(self, user: models.Login, socialType: str):
        if socialType == GOOGLE:
            try:
                db_user = self.db_session.query(models.UserSchema).filter_by(email=user.email).first()
                if(db_user):
                    if(db_user.google_sub == user.id_token):
                        return True
                return False
            except Exception as e:
                return False