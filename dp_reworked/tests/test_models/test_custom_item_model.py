import pytest
from sqlalchemy import select
from src.domain import CustomItem
from tests.sessions import db, add_data, clean_data


@pytest.fixture()
def custom_item_data():
    test_data = {
        "item_name": "test_item",
        "price": 500.00,
    }
    return test_data


@pytest.mark.asyncio
async def test_create_and_read_model(db, custom_item_data):
    # given
    test_item = CustomItem(**custom_item_data)
    add_data(db, test_item)
    # when
    custom_item = db.execute(select(CustomItem).where(CustomItem.item_name == "test_item"))
    custom_item = custom_item.scalar()
    # then
    assert custom_item.id is not None
    assert custom_item.item_name == "test_item"
    assert custom_item.price == 500.00
    clean_data(db, test_item)
