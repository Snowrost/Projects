import pytest
from sqlalchemy import select
from src.domain import Meeting
from tests.sessions import db, add_data, clean_data


@pytest.fixture()
def meeting_data():
    test_data = {
        "meeting_name": "tes Meeting",
        "date_of_activity": "2023-09-13 01:48"
        }
    return test_data


@pytest.mark.asyncio
async def test_create_and_read_meeting(db, meeting_data):
    # given
    testing_data = Meeting(**meeting_data)
    add_data(db, testing_data)

    # when
    meeting = db.execute(select(Meeting).where(Meeting.meeting_name == "tes Meeting"))
    meeting = meeting.scalar()

    # then
    assert meeting.id is not None
    assert meeting.meeting_name == "tes Meeting"
    assert meeting.date_of_activity.strftime("%Y-%m-%d %H:%M") == "2023-09-13 01:48"

    clean_data(db, testing_data)
