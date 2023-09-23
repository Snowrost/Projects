import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.core import config

engine = create_engine(config.write_database.sync_connection_string())
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture()
def db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


def clean_data(db, data):
    return db.delete(data), db.commit()


def add_data(db, data):
    return db.add(data),db.commit()

