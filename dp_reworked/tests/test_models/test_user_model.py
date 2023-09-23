import pytest
from sqlalchemy import select
from src.domain import User
from tests.sessions import db, add_data, clean_data


@pytest.fixture()
def user_data():
    test_user_data = {
        "email": "test@example.com",
        "password": "test_password",
        "name": "Test User",
        "lastname": "Lastname",
        }
    return test_user_data


@pytest.fixture()
def invalid_data():
    invalid_data = {
        "email": "ivalid email",
        "password": "test_password",
        "name": "Test User",
        "lastname": "Lastname",
        }
    return invalid_data


@pytest.mark.asyncio
async def test_create_and_read_user(db, user_data):
    # given
    new_user = User(**user_data)
    add_data(db, new_user)
    # when
    user = db.execute(select(User).where(User.email == "test@example.com"))
    user = user.scalar()
    # then
    assert user.id is not None
    assert user.email == "test@example.com"
    assert user.name == "Test User"
    assert user.lastname == "Lastname"
    assert user.password == "test_password"
    clean_data(db, new_user)

@pytest.mark.asyncio
async def invalid_email(db, invalid_data):
    test_invalid = User(**invalid_data)
    with pytest.raises(ValueError, match="Invalid email format")as exc_info2:
        add_data(db, test_invalid)
    assert str(exc_info2.value) == "Invalid email format"


