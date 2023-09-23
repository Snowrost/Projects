from fastapi import APIRouter, HTTPException, Depends
from src.repository import DataProcessing
from src.models import Meeting, Feedback, User, Participant
from src.controllers.security import get_current_active_user
from typing import Annotated
from src.schemas import FeedbackData, FeedbackId, UpdateFeedback
from src.controllers.validation import Validate
from src.controllers import get_comments_with_names_and_data_meeting, get_comments_with_names_and_data_user


router = APIRouter()
data_processing = DataProcessing()


@router.post("/meetings/{meeting_id}/{user_id}/comments", summary="Add feedback for meeting", tags=["Comments"])
async def create_feedback_for_meeting(data: FeedbackData, current: Annotated[User, Depends(get_current_active_user)]):
    meeting = await data_processing.get_data_from_model_filter(Meeting, id=data.meeting_id)
    Validate.meeting_dont_exists(meeting)
    if meeting.owner_id == current.id:
        raise HTTPException(status_code=400, detail="You are the owner of this meeting and cannot create feedback")
    participant = await data_processing.get_data_from_model_filter(Participant, meeting_id=data.meeting_id, user_id=current.id)
    Validate.is_not_participant(participant)
    feedback_data = {
        "user_id": current.id,
        "meeting_id": data.meeting_id,
        "comment": data.feedback_text
    }
    await data_processing.save_data(Feedback, feedback_data)
    return {"message": "Feedback created successfully"}


@router.put("/comments/{feedback_id}/", summary="Update comments", tags=["Comments"])
async def update_feedback(data: UpdateFeedback, current: Annotated[User, Depends(get_current_active_user)]):
    feedback = await data_processing.get_data_from_model_filter(Feedback, id=data.feedback_id)
    Validate.feedback_dont_exists(feedback)
    Validate.feedback_creator(feedback, current)
    await data_processing.update_data(Feedback, {"comment": data.feedback_text}, id=data.feedback_id)
    return {"message": "Feedback updated successfully"}


@router.delete("/comments/{feedback_id}", summary="Delete comments", tags=["Comments"])
async def delete_feedback(data: FeedbackId, current: Annotated[User, Depends(get_current_active_user)]):
    feedback = await data_processing.get_data_from_model_filter(Feedback, id=data.feedback_id)
    Validate.feedback_dont_exists(feedback)
    Validate.feedback_creator(feedback, current)
    await data_processing.delete_data(Feedback, id=data.feedback_id)
    return {"message": "Feedback deleted successfully"}


@router.get("/meetings/{meeting_id}/comments",  summary="Get all comments for meeting", tags=["Comments"])
async def get_feedbacks_for_meeting(meeting_id:str, current: Annotated[User, Depends(get_current_active_user)]):
    meeting = await data_processing.get_data_from_model_filter(Meeting, id=meeting_id)
    Validate.meeting_dont_exists(meeting)
    feedbacks = await data_processing.get_data_from_model_filter(Feedback, id=meeting_id)
    if feedbacks:
        raise HTTPException(status_code=400, detail="This meeting dont have any feedbacks yet")
    # rows = await get_comments_with_names_and_data_meeting(meeting_id)
    feedback_data = await get_comments_with_names_and_data_meeting(meeting_id)
    return feedback_data


@router.get("/comments",  summary="Get all comments what write current user", tags=["Comments"])
async def get_user_feedbacks(current: Annotated[User, Depends(get_current_active_user)]):
    feedback = await data_processing.get_data_from_model_filter(Feedback, user_id=current.id)
    if feedback is None:
        raise HTTPException(status_code=400, detail="You dont have any feedbacks yet")
    feedback_data = await get_comments_with_names_and_data_user(current)
    return {"user_feedback": feedback_data}



