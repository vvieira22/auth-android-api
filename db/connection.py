from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
from sqlalchemy.orm import sessionmaker

load_dotenv()
DB_URL = os.getenv("DB_URL")

#pool pre ping, test db connection before using it
engine = create_engine(DB_URL, pool_pre_ping=True)
Session = sessionmaker(bind=engine)