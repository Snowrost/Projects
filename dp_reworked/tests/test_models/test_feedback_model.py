import pytest
from sqlalchemy import select
from src.domain import Feedback, User, Meeting
from tests.sessions import db, add_data, clean_data
from tests.test_models import meeting_data, user_data


@pytest.mark.asyncio
async def test_create_and_read_feedback(db, meeting_data, user_data):
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
        "meeting_id": meeting.id,
        "comment": "Test Comment Join The Dark Side"
    }
    testing_data_feedback = Feedback(**test_data)
    add_data(db, testing_data_feedback)

    # when
    feedback = db.execute(select(Feedback).where(Feedback.meeting_id == meeting.id))
    feedback = feedback.scalar()
    # then
    assert feedback.id is not None
    assert feedback.meeting_id == meeting.id
    assert feedback.user_id == user.id
    assert feedback.comment == "Test Comment Join The Dark Side"

    clean_data(db, testing_data_feedback)
    clean_data(db, testing_data_meeting)
    clean_data(db, testing_data_user)

