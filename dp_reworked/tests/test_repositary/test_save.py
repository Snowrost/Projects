import pytest
from src.core import DataProcessing
from src.domain import User
from tests.sessions import db


@pytest.fixture()
def user_data():
    test_user_data = {
        "email": "test@example.com",
        "password": "test_password",
        "name": "Test User",
        "lastname": "Lastname",
    }
    return test_user_data


@pytest.fixture
def data_processing_instance():
    return DataProcessing()


@pytest.fixture()
def updated_user():
    test_data = {
        "email": "updatedtest@example.com",
        "password": "updatedtest_password",
        "name": "Test User",
        "lastname": "UpdatedLastname",
    }
    return test_data


@pytest.mark.asyncio
async def test_data_processing(db, data_processing_instance, user_data, updated_user):

    await data_processing_instance.save_data(User, user_data)
    saved_data = await data_processing_instance.get_data_from_model_filter(User, name="Test User")
    assert saved_data is not None
    assert saved_data.name == "Test User"
    assert saved_data.password == "test_password"
    await data_processing_instance.update_data(User, updated_user, email="test@example.com")
    updated = await data_processing_instance.get_data_from_model_filter(User, email="updatedtest@example.com")
    assert updated.email == "updatedtest@example.com"
    assert updated.password == "updatedtest_password"
    await data_processing_instance.delete_data(User, name="Test User")
    fetch = await data_processing_instance.get_data_from_model_filter(User, name="Test User")

    # then
    assert fetch is None
