import json
from fastapi import APIRouter, Depends, Form, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from auth_user import UserUseCase
from depends import get_db_session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import models

router = APIRouter(prefix='/user')

@router.post('/register')
def user_register(
    usr: models.User,
    db_session: Session = Depends(get_db_session)):
    
    uc = UserUseCase(db_session = db_session)
    uc.user_register(user = usr)
    return JSONResponse(
        content = json.dumps({"message": "User created"}),
        status_code = status.HTTP_201_CREATED
    )    

@router.post('/login')
def user_login(
    request_form_user: models.Login = Depends(),
    db_session: Session = Depends(get_db_session)):
    
    uc = UserUseCase(db_session = db_session)
    user = models.Login(
        grand_type = request_form_user.grand_type,
        email = request_form_user.email,
        password = request_form_user.password,
        id_token = request_form_user.id_token,
        biometric_data = request_form_user.biometric_data
    )
    auth_data = uc.user_login(user=user)
    return JSONResponse(
        content = json.dumps(auth_data),
        status_code = status.HTTP_200_OK
    )
    