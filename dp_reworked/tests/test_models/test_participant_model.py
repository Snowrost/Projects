import pytest
from sqlalchemy import select
from src.domain import Participant, User, Meeting
from tests.sessions import db, add_data, clean_data
from tests.test_models import meeting_data, user_data


@pytest.mark.asyncio
async def test_create_and_read_participant(db, meeting_data, user_data):
    # given
    testing_data_user = User(**user_data)
    testing_data_meeting = Meeting(**meeting_data)
    add_data(db, testing_data_user)
    add_data(db, testing_data_meeting)
    meeting = db.execute(select(Meeting).where(Meeting.meeting_name == "tes Meeting"))
    meeting = meeting.scalar()
    user = db.execute(select(User).where(User.email == "test@example.com"))
    user = user.scalar()
    test_data = {
        "user_id": user.id,
        "meeting_id": meeting.id
    }
    testing_data_participants = Participant(**test_data)
    add_data(db, testing_data_participants)

    # when
    participant = db.execute(select(Participant).where(Participant.meeting_id == meeting.id))
    participant = participant.scalar()
    # then
    assert participant.id is not None
    assert participant.meeting_id == meeting.id
    assert participant.user_id == user.id

    clean_data(db, testing_data_participants)
    clean_data(db, testing_data_meeting)
    clean_data(db, testing_data_user)

