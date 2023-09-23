from fastapi import APIRouter, Depends
from src.repository import DataProcessing
from src.models import Meeting, Participant, User, CustomItem, Check
from src.schemas import CheckData, ItemData, PurchaseData, UpdateItem, RemoveFromCheckData
from src.controllers.security import get_current_active_user
from typing import Annotated
from src.controllers import (create_custom_item, calculate_check_create, update_calculate_and_item,
                             remove_from_check_recalculate, user_check_rows, meeting_check_rows)
from src.controllers.validation import Validate


router = APIRouter()
data_processing = DataProcessing()


# Create a check for a custom item in a meeting
@router.post("/meetings/{meeting_id}/{participant_id}/purchase", summary="Add custom item to purchase", tags=["Purchases"])
async def create_check_with_participants(data: CheckData, item_data: ItemData,
                                         current: Annotated[User, Depends(get_current_active_user)]):
    await create_custom_item(item_data)
    item = await data_processing.get_data_from_model_filter(CustomItem, item_name=item_data.item_name)
    meeting = await data_processing.get_data_from_model_filter(Meeting, id=data.meeting_id)
    Validate.meeting_dont_exists(meeting)
    existing_participant = await data_processing.get_data_from_model_filter(Participant, meeting_id=data.meeting_id,
                                                                            user_id=current.id)
    Validate.is_not_participant(existing_participant)
    existing_check = await data_processing.get_data_from_model_filter(Check, custom_item_id=item.id)
    Validate.check_exists(existing_check)
    await calculate_check_create(data, item)
    return {"message": "Check created successfully"}


@router.delete("/meetings/{meeting_id}/{custom_item_id}/purchase", summary="Delete custom item from purchase", tags=["Purchases"])
async def delete_custom_item(data: PurchaseData, current: Annotated[User, Depends(get_current_active_user)]):
    custom_item = await data_processing.get_data_from_model_filter(CustomItem, id=data.custom_item_id)
    Validate.custom_item_exists(custom_item)
    existing_participant = await data_processing.get_data_from_model_filter(Participant, meeting_id=data.meeting_id,
                                                                            user_id=current.id)
    Validate.is_not_participant(existing_participant)
    await data_processing.delete_data(Check, custom_item_id=data.custom_item_id)
    await data_processing.delete_data(CustomItem, id=data.custom_item_id)
    return {"message": "Custom item and associated check records deleted successfully"}


@router.put("/meetings/{meeting_id}/{custom_item_id}/purchase,",
            summary="Update custom item price, quantity of items in purchase", tags=["Purchases"])
async def update_check(data: PurchaseData, update_item: UpdateItem,
                       current: Annotated[User, Depends(get_current_active_user)]):

    custom_item = await data_processing.get_data_from_model_filter(CustomItem, id=data.custom_item_id)
    Validate.custom_item_exists(custom_item)
    meeting = await data_processing.get_data_from_model_filter(Meeting, id=data.meeting_id)
    Validate.meeting_dont_exists(meeting)
    existing_participant = await data_processing.get_data_from_model_filter(Participant, meeting_id=data.meeting_id,
                                                                            user_id=current.id)
    Validate.is_not_participant(existing_participant)
    await update_calculate_and_item(data, update_item)
    return {"message": "Check and custom item updated successfully"}


@router.delete("/meetings/{meeting_id}/{custom_item_id}/{participant_id}/purchase",
               summary="Remove from check participant", tags=["Purchases"])
async def delete_from_check(data: RemoveFromCheckData, current: Annotated[User, Depends(get_current_active_user)]):
    custom_item = await data_processing.get_data_from_model_filter(CustomItem, id=data.custom_item_id)
    Validate.custom_item_exists(custom_item)
    meeting = await data_processing.get_data_from_model_filter(Meeting, id=data.meeting_id)
    Validate.meeting_dont_exists(meeting)
    existing_participant = await data_processing.get_data_from_model_filter(Participant, meeting_id=data.meeting_id,
                                                                            user_id=current.id)
    Validate.is_not_participant(existing_participant)
    existing_check = await data_processing.get_data_from_model_filter(Check, custom_item_id=data.custom_item_id)
    Validate.check_dont_exists(existing_check)
    await remove_from_check_recalculate(data, custom_item)
    return {"message": "Removed from check participants successfully"}


@router.get("/{meeting_id}/calculation", summary="Get personal check for meeting", tags=["Purchases"])
async def user_check(meeting_id: str, current: Annotated[User, Depends(get_current_active_user)]):
    meeting = await data_processing.get_data_from_model_filter(Meeting, id=meeting_id)
    Validate.meeting_dont_exists(meeting)
    participant = await data_processing.get_data_from_model_filter(Participant, user_id=current.id,
                                                                   meeting_id=meeting_id)
    Validate.is_not_participant(participant)
    rows = await user_check_rows(participant)
    amount = sum(row[1] for row in rows)
    check_data = [{"item_name": row[0], "price": row[1], "number of position": row[2]} for row in rows]
    return {"Check": check_data, "total amount": amount}


@router.get("/meetings/{meeting_id}/calculation", summary="Get checks for all for meeting_id", tags=["Purchases"])
async def meeting_check(meeting_id: str, current: Annotated[User, Depends(get_current_active_user)]):
    meeting = await data_processing.get_data_from_model_filter(Meeting, id=meeting_id)
    Validate.meeting_dont_exists(meeting)
    participants = await data_processing.get_data_all_from_model_filter(Participant, meeting_id=meeting_id)
    check_data = await meeting_check_rows(participants)
    return {"Check Data": check_data}
