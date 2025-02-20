"""Connector class that also sets up the DB"""
import os

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database

from src.utils.env_config import read_env, EnvConfig

runtime_config: EnvConfig = read_env()
assert runtime_config.db_conn_str.startswith("sqlite:///")

# "sqlite:///./test.db"
SQLALCHEMY_DATABASE_URL = runtime_config.db_conn_str
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def run_migrations():
    if not database_exists(engine.url):
        create_database(engine.url)

    alembic_cfg = Config(f"{os.getcwd()}/alembic.ini")
    command.upgrade(alembic_cfg, "head")