from fastapi import FastAPI, HTTPException, Depends, Request
from routers import router, test_router
import models  # Importe os modelos

app = FastAPI()

app.include_router(router)
app.include_router(test_router)