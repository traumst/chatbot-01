"""Connector class for Sqlite db"""
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database
from alembic import command
from alembic.config import Config

from src.utils.env_config import read_env, EnvConfig

runtime_config: EnvConfig = read_env()
assert runtime_config.db_conn_str.startswith("sqlite:///")

SQLALCHEMY_DATABASE_URL = runtime_config.db_conn_str
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def upgrade_db():
    """
    Creates target sqlite db file if does not exist,
        checks current migrations and applies changes.
    """

    if not database_exists(engine.url):
        create_database(engine.url)

    alembic_cfg = Config(f"{os.getcwd()}/alembic.ini")
    command.upgrade(alembic_cfg, "head")
