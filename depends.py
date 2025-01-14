from fastapi.security import OAuth2PasswordBearer
from auth_user import UserUseCase 
from fastapi import Depends
from sqlalchemy.orm import Session
from db.connection import Session as dbSession

oauth_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_db_session():
    try:
        session = dbSession()
        yield session
    finally:
        session.close()

def token_verifier(
    db_session: Session = Depends(get_db_session), token = Depends(oauth_scheme)
    ): #pegar o token do header da requisicao):`
    uc = UserUseCase(db_session=db_session)
    uc.verify_token(acess_token=token)
