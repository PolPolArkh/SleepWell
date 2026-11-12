from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DBURL = "postgresql+psycopg2://postgres:Mega5493257@127.0.0.1:5432/treeshop" 
engine = create_engine(DBURL)
SessionLocal = sessionmaker(bind=engine)

class Base(DeclarativeBase):
    pass
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()