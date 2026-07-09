from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Nome do banco SQLite
DATABASE_URL = "sqlite:///nfe_demo.db"

# Conexão com SQLite
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# Sessão do banco
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Classe base para todos os modelos
Base = declarative_base()


def get_db():
    """
    Cria uma sessão com o banco para cada requisição.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()