from fastapi import APIRouter, HTTPException, Depends
from src.repository import DataProcessing
from src.models import Meeting, Participant, User, Check
from src.controllers import convert_date_time
from src.schemas import UpdateMeeting, MeetingData
from src.controllers.validation import Validate
from src.controllers.security import get_current_active_user
from typing import Annotated

router = APIRouter()
data_processing = DataProcessing()


@router.post("/create-meeting", summary="Create new meeting", tags=["Meeting"])
async def create_meeting(data: MeetingData, current: Annotated[User, Depends(get_current_active_user)]):
    meeting_data_dict = {
        "meeting_name": data.meeting_name,
        "date_of_activity": convert_date_time(data),
        "owner_id": current.id}
    await data_processing.save_data(Meeting, meeting_data_dict)
    new_meeting = await data_processing.get_data_from_model_filter(Meeting, **meeting_data_dict)
    await data_processing.save_data(Participant, {"meeting_id": new_meeting.id, "user_id": current.id})
    return {"message": "Meeting create successful", " new_meeting_id =": new_meeting.id}


@router.get("/meetings/participants", summary="Return all meetings with participant", tags=["Meeting"])
async def get_meeting_list(current: Annotated[User, Depends(get_current_active_user)]):
    meetings = await data_processing.get_data_from_model_all(Meeting)
    meetings_with_participants = []
    for meeting in meetings:
        is_owner = meeting.owner_id == current.id
        participants = await data_processing.get_data_all_from_model_filter(Participant, meeting_id=meeting.id)
        participant_names = []
        for participant in participants:
            # Retrieve the participant's name using User.name
            user = await data_processing.get_data_from_model_filter(User, id=participant.user_id)
            participant_name = user.name if user else ""
            participant_names.append(participant_name)
        meetings_with_participants.append({
            "meeting_name": meeting.meeting_name,
            "participants": participant_names,
            "created by current user": is_owner,
        })
    return {"Meetings with Participants": meetings_with_participants}


@router.get("/meetings/{meeting_id}/participants", summary="Return meeting by id with participant", tags=["Meeting"])
async def get_meeting_by_id(meeting_id: str, current: Annotated[User, Depends(get_current_active_user)]):
    meeting = await data_processing.get_data_from_model_filter(Meeting, id=meeting_id)
    Validate.meeting_dont_exists(meeting)
    is_owner = meeting.owner_id == current.id
    participants = await data_processing.get_data_all_from_model_filter(Participant, meeting_id=meeting_id)
    participant_names = []
    for participant in participants:
        user = await data_processing.get_data_from_model_filter(User, id=participant.user_id)
        participant_name = user.name if user else ""
        participant_names.append(participant_name)

    meeting_with_participants = {
        "meeting_name": meeting.meeting_name,
        "participants": participant_names,
        "is_owner": is_owner,
    }
    return {"Meeting with Participants": meeting_with_participants}


@router.put("/meetings/{meeting_id}", summary="Update meeting values", tags=["Meeting"])
async def update_meeting(data: UpdateMeeting, current: Annotated[User, Depends(get_current_active_user)]):
    meeting = await data_processing.get_data_from_model_filter(Meeting, id=data.meeting_id)
    Validate.meeting_dont_exists(meeting)
    Validate.owner_of_meeting(meeting, current)
    update_dict = {}
    if data.meeting_name:
        update_dict["meeting_name"] = data.meeting_name
    if data.date_of_activity:
        update_dict["date_of_activity"] = convert_date_time(data)
    await data_processing.update_data(Meeting, update_dict, id=data.meeting_id)
    return {"message": "Meeting updated successfully"}


@router.delete("/delete-meeting/{meeting_id}", summary="Delete meetings from base", tags=["Meeting"])
async def delete_meeting_(meeting_ids: list[str], current: Annotated[User, Depends(get_current_active_user)]):
    for meeting_id in meeting_ids:
        meeting = await data_processing.get_data_from_model_filter(Meeting, id=meeting_id)
        Validate.meeting_dont_exists(meeting)
        Validate.owner_of_meeting(meeting, current)
        participants = await data_processing.get_data_all_from_model_filter(Participant, meeting_id=meeting_id)
        for participant in participants:
            check_exists = await data_processing.get_data_from_model_filter(Check, participant_id=participant.id)
            if check_exists:
                raise HTTPException(status_code=400,
                                    detail="Cannot delete the meeting as participants have associated custom items in Check")
        await data_processing.delete_data(Participant, meeting_id=meeting_id)
        await data_processing.delete_data(Meeting, id=meeting_id)
    return {"message": "Meeting deleted successfully"}
