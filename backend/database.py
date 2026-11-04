import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base

# PostgreSQL é o único banco suportado
# DATABASE_URL deve estar definida no ambiente
DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL não está definida. Defina a variável de ambiente com a URL do PostgreSQL. "
        "Exemplo: postgresql://usuario:senha@localhost:5432/almoxarifado"
    )

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()