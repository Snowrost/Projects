from fastapi import APIRouter, HTTPException, Depends
from src.repository import DataProcessing
from src.models import Meeting, Participant, User, Check
from src.controllers.validation import Validate
from src.controllers.security import get_current_active_user
from src.schemas import ParticipantData, MeetingIds
from typing import Annotated

router = APIRouter()
data_processing = DataProcessing()


@router.post("/meetings/{meeting_id}/{user_id}/participants", summary="Add users to meetings", tags=["Participants"])
async def add_user_to_meeting(data: ParticipantData,  current: Annotated[User, Depends(get_current_active_user)]):
    meeting = await data_processing.get_data_from_model_filter(Meeting, id=data.meeting_id)
    Validate.meeting_dont_exists(meeting)
    Validate.owner_of_meeting(meeting, current)
    for user_id in data.user_ids:
        user = await data_processing.get_data_from_model_filter(User, id=user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        existing_participant = await data_processing.get_data_from_model_filter(
            Participant,
            meeting_id=data.meeting_id,
            user_id=user_id
        )
        Validate.is_participant(existing_participant)
        participant_data = {
            "meeting_id": data.meeting_id,
            "user_id": user_id,
        }
        await data_processing.save_data(Participant, participant_data)
    return {"message": "User added to the meeting successfully"}


@router.post("/meetings/{meeting_id}/join", summary="Join the meetings", tags=["Participants"])
async def join_meeting_as_participant(data: MeetingIds,  current: Annotated[User, Depends(get_current_active_user)]):
    for meeting_id in data.meeting_ids:
        meeting = await data_processing.get_data_from_model_filter(Meeting, id=meeting_id)
        Validate.meeting_dont_exists(meeting)
        Validate.not_owner_of_meeting(meeting, current)
        existing_participant = await data_processing.get_data_from_model_filter(Participant, meeting_id=meeting_id,
                                                                                user_id=current.id)
        Validate.is_participant(existing_participant)
        participant_data = {
            "meeting_id": meeting_id,
            "user_id": current.id,
        }
        await data_processing.save_data(Participant, participant_data)
    return {"message": "You have successfully joined the meeting as a participant"}


@router.delete("/meetings/{meeting_id}/leave", summary="Leave the meeting", tags=["Participants"])
async def leave_meeting_as_participant(data: MeetingIds,  current: Annotated[User, Depends(get_current_active_user)]):
    for meeting_id in data.meeting_ids:
        meeting = await data_processing.get_data_from_model_filter(Meeting, id=meeting_id)
        Validate.meeting_dont_exists(meeting)
        Validate.not_owner_of_meeting(meeting, current)
        participant = await data_processing.get_data_from_model_filter(Participant, meeting_id=meeting_id,
                                                                       user_id=current.id)
        Validate.is_participant(participant)
        check_exists = await data_processing.get_data_from_model_filter(Check, participant_id=participant.id)
        if check_exists:
            raise HTTPException(status_code=400,
                                detail="Cannot leave meeting while u exists in some bills")
        await data_processing.delete_data(Participant, id=participant.id)
    return {"message": "You have successfully left the meeting as a participant"}


@router.delete("/meetings/{meeting_id}/{user_id}/remove", summary="Remove the users from meeting", tags=["Participants"])
async def delete_participant_from_meeting(data: ParticipantData,
                                          current: Annotated[User, Depends(get_current_active_user)]):
    meeting = await data_processing.get_data_from_model_filter(Meeting, id=data.meeting_id)
    Validate.meeting_dont_exists(meeting)
    Validate.owner_of_meeting(meeting, current)
    for user_id in data.user_ids:
        participant = await data_processing.get_data_from_model_filter(
            Participant,
            meeting_id=data.meeting_id,
            user_id=user_id,
        )
        Validate.is_not_participant(participant)
        check_exists = await data_processing.get_data_from_model_filter(Check, participant_id=participant.id)
        if check_exists:
            raise HTTPException(status_code=400,
                                detail="Cannot remove from meeting while users exists in some bills")
        await data_processing.delete_data(Participant, id=participant.id)
    return {"message": "Participants deleted successfully"}


