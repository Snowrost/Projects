import pytest
from sqlalchemy import select
from src.domain import Participant, User, Meeting, Check, CustomItem
from tests.sessions import db, add_data, clean_data
from tests.test_models import meeting_data, user_data, custom_item_data


@pytest.mark.asyncio
async def test_create_and_read_check(db, meeting_data, user_data, custom_item_data):
    # given
    testing_data_custom_item = CustomItem(**custom_item_data)
    testing_data_user = User(**user_data)
    testing_data_meeting = Meeting(**meeting_data)
    add_data(db, testing_data_user)
    add_data(db, testing_data_meeting)
    add_data(db, testing_data_custom_item)
    meeting = db.execute(select(Meeting).where(Meeting.meeting_name == "tes Meeting"))
    meeting = meeting.scalar()
    user = db.execute(select(User).where(User.email == "test@example.com"))
    user = user.scalar()
    custom_item = db.execute(select(CustomItem).where(CustomItem.item_name == "test_item"))
    custom_item = custom_item.scalar()
    test_participant_data = {
        "user_id": user.id,
        "meeting_id": meeting.id
    }
    testing_data_participants = Participant(**test_participant_data)
    add_data(db, testing_data_participants)
    participant = db.execute(select(Participant).where(Participant.meeting_id == meeting.id))
    participant = participant.scalar()
    test_check_data = {
        "participant_id": participant.id,
        "custom_item_id": custom_item.id,
        "custom_item_number": 2,
        "splited_bill": 333.33,
    }
    testing_data_check = Check(**test_check_data)
    add_data(db, testing_data_check)

    # when
    bill = db.execute(select(Check).where(Check.custom_item_id == custom_item.id))
    bill = bill.scalar()

    # then
    assert bill.id is not None
    assert bill.participant_id == participant.id
    assert bill.custom_item_id == custom_item.id
    assert bill.custom_item_number == 2
    assert bill.splited_bill == 333.33

    clean_data(db, testing_data_check)
    clean_data(db, testing_data_custom_item)
    clean_data(db, testing_data_participants)
    clean_data(db, testing_data_meeting)
    clean_data(db, testing_data_user)










