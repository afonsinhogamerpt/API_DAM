from sqlalchemy.orm import sessionmaker # type: ignore
from sqlalchemy import create_engine # type: ignore
from sqlalchemy.ext.declarative import declarative_base # type: ignore

DATABASE_URL = "mssql+pyodbc://fonsi12@fonsi:Afonsinhogamerpt123%40@fonsi.database.windows.net:1433/dbfonsi?driver=ODBC+Driver+17+for+SQL+Server"



engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()