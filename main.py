from fastapi import FastAPI, HTTPException, Depends, Request
from routers import router

app = FastAPI()

app.include_router(router)