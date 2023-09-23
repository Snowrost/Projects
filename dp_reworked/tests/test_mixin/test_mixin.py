import pytest
from sqlalchemy import select
from src.domain import User
from tests.sessions import db, add_data, clean_data
from tests.test_models import user_data

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
    assert user.created_at is not None
    assert user.updated_at is not None
    clean_data(db, new_user)
