from sqlalchemy.future import select
from src.models import Feedback, User, Meeting
from src.core.db.session import session, set_session_context, reset_session_context


async def get_comments_with_names_and_data_meeting(meeting_id):
    query = (
            select(Feedback.comment, User.name, Feedback.created_at)
            .join(User)
            .where(Feedback.meeting_id == meeting_id)
        )
    context = set_session_context("query")
    async with session() as db:
        result = await db.execute(query)
        reset_session_context(context)
    rows = result.fetchall()
    feedback_data = [{"comment": row[0], "created_by": row[1], "created_at": row[2]}for row in rows]
    return feedback_data


async def get_comments_with_names_and_data_user(current):
    query = (
        select(Feedback.comment, Meeting.meeting_name, Feedback.created_at)
        .join(Meeting)
        .where(Feedback.user_id == current.id)
    )

    context = set_session_context("query")
    async with (session() as db):
        result = await db.execute(query)
        reset_session_context(context)
    rows = result.fetchall()
    feedback_data = [{"comment": row[0], "created_for meeting": row[1], "created_at": row[2]} for row in rows]
    return feedback_data



