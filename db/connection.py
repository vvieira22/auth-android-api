from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
from sqlalchemy.orm import sessionmaker
from models import Base  # Importe a base dos modelos

load_dotenv()
DB_URL = os.getenv("DB_URL")

#pool pre ping, test db connection before using it
engine = create_engine(DB_URL, pool_pre_ping=True)

# Crie as tabelas automaticamente no banco de dados se não existirem
Base.metadata.create_all(bind=engine)

Session = sessionmaker(bind=engine)