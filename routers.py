import json
from typing import Optional
from fastapi import APIRouter, Depends, Form, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from auth_user import UserUseCase
from depends import get_db_session, token_verifier
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import models

router = APIRouter(prefix='/user')

#da pra colocar dependencias direto aqui, para evitar ter que colocar em cada rota.
test_router = APIRouter(prefix='/test', dependencies=[Depends(token_verifier)])

@router.post('/register/{type}')
def register(
    type: str,
    usr: models.User,
    db_session: Session = Depends(get_db_session)):
    uc = UserUseCase(db_session = db_session)
    print("Request:" + str(usr))
    uc.register(user = usr, type = type)
    return JSONResponse(
        content = json.dumps({"message": "User created"}),
        status_code = status.HTTP_201_CREATED
    )    

@router.post('/login/{type}')
def login(
    type: str,
    request_form_user: models.Login,
    db_session: Session = Depends(get_db_session)):
    uc = UserUseCase(db_session = db_session)
    
    user = models.Login(
        email = request_form_user.email,
        password = request_form_user.password,
        id_token = request_form_user.id_token,
        biometric_data = request_form_user.biometric_data
    )
    
    auth_data = uc.login(user=user, login_type=type)
    return JSONResponse(
        content = auth_data,  # Convertendo auth_data para JSON serializável
        status_code = status.HTTP_200_OK
    )

@test_router.get('/testtoken')
def teste_token():
    return {"message": "Token valid"}