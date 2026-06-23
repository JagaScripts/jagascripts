from __future__ import annotations
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.core.settings import settings


class Base(DeclarativeBase):
    """ Clase base para todos los modelos ORM de SQLAlchemy. """

    pass


engine = create_engine(
    settings.database_url,
    echo=settings.db_echo,
    pool_pre_ping=True,
)

# Fábrica de sesiones de base de datos para gestionar transacciones.
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
