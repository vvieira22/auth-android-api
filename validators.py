from config import FACEBOOK, GMAIL, DEFAULTLOGIN
import models

def validar_campos_login(login: models.Login):
    if login.facebook_provider and not login.gmail_provider:
        return FACEBOOK
    if login.gmail_provider and not login.facebook_provider:
        return GMAIL
    if login.email and login.password:
        return DEFAULTLOGIN
    if login.facebook_provider and login.gmail_provider: # a prova de idiotas
        return False
    # print(login)"
    return ""