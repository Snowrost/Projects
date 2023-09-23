from fastapi import HTTPException
from src.repository import DataProcessing
from src.models import Participant, User, Meeting, CustomItem, Check
from src.schemas import Data
from src.controllers.validation import Validate
from src.core.db import session, reset_session_context, set_session_context
from sqlalchemy import select

data_processing = DataProcessing()


async def create_custom_item(data):
    custom_item_data = {
        "item_name": data.item_name,
        "price": data.price,
    }
    item = await data_processing.save_data(CustomItem, custom_item_data)
    return item


def split_bill_calculate(participants, custom_item, number):
    total_participants = len(participants)
    custom_item_price = custom_item.price * number
    split_bill = custom_item_price / total_participants
    return split_bill


async def calculate_check_create(data, item):
    if data.participant_ids is not None:
        split = split_bill_calculate(data.participant_ids, item, data.custom_item_number)
        for participant_id in data.participant_ids:            
            participant = await data_processing.get_data_from_model_filter(Participant, id=participant_id,
                                                                           meeting_id=data.meeting_id)
            if not participant:
                raise HTTPException(status_code=404, detail=f"Participant {participant_id} not found in this meeting")
            check_data = {
                "participant_id": participant_id,
                "custom_item_id": item.id,
                "custom_item_number": data.custom_item_number,
                "splited_bill": split,
            }
            await data_processing.save_data(Check, check_data)
    if data.participant_ids is None:
        participants = await data_processing.get_data_all_from_model_filter(Participant, meeting_id=data.meeting_id)
        split_for_all = split_bill_calculate(participants, item, data.custom_item_number)
        for participant in participants:
            if not participant:
                raise HTTPException(status_code=404, detail=f"Participant {participant.id} not found in this meeting")
            check_data = {
                "participant_id": participant.id,
                "custom_item_id": item.id,
                "custom_item_number": data.custom_item_number,
                "splited_bill": split_for_all
            }
            await data_processing.save_data(Check, check_data)


async def update_calculate_and_item(data, update_item):
    if update_item.item_name is not None:
        await data_processing.update_data(CustomItem, {"item_name": update_item.item_name}, id=data.custom_item_id)
    if update_item.price is not None:
        await data_processing.update_data(CustomItem, {"price": update_item.price}, id=data.custom_item_id)
        if update_item.custom_item_number is None:
            updated_item = await data_processing.get_data_from_model_filter(CustomItem, id=data.custom_item_id)
            checks = await data_processing.get_data_all_from_model_filter(Check, custom_item_id=data.custom_item_id)
            get_number = await data_processing.get_data_from_model_filter(Check, custom_item_id=data.custom_item_id)
            number = get_number.custom_item_number
            update_split = {
                "splited_bill": split_bill_calculate(checks, updated_item, number)
            }
            return await data_processing.update_data(Check, update_split, custom_item_id=data.custom_item_id)
        if update_item.custom_item_number is not None:
            updated_item = await data_processing.get_data_from_model_filter(CustomItem, id=data.custom_item_id)
            checks = await data_processing.get_data_all_from_model_filter(Check, custom_item_id=data.custom_item_id)
            update_split = {
                "splited_bill": split_bill_calculate(checks, updated_item, update_item.custom_item_number),
                "custom_item_number": update_item.custom_item_number
            }
            return await data_processing.update_data(Check, update_split, custom_item_id=data.custom_item_id)
    if update_item.custom_item_number is not None and update_item.price is None:
        await data_processing.update_data(Check, {"custom_item_number": update_item.custom_item_number},
                                          custom_item_id=data.custom_item_id)
        get_price = await data_processing.get_data_from_model_filter(CustomItem, id=data.custom_item_id)
        checks = await data_processing.get_data_all_from_model_filter(Check, custom_item_id=data.custom_item_id)
        update_split = {
            "splited_bill": split_bill_calculate(checks, get_price, update_item.custom_item_number),
            "custom_item_number": update_item.custom_item_number
        }
        return await data_processing.update_data(Check, update_split, custom_item_id=data.custom_item_id)


async def remove_from_check_recalculate(data, custom_item):
    bills = await data_processing.get_data_all_from_model_filter(Check, custom_item_id=data.custom_item_id)
    if len(bills) == len(data.participant_ids):
        for participant_id in data.participant_ids:
            participant = await data_processing.get_data_from_model_filter(Participant, id=participant_id,
                                                                           meeting_id=data.meeting_id)
            if not participant:
                raise HTTPException(status_code=404, detail=f"Participant {participant_id} not found in this meeting")
        await data_processing.delete_data(Check, custom_item_id=data.custom_item_id)
        await data_processing.delete_data(CustomItem, id=data.custom_item_id)
    else:
        for participant_id in data.participant_ids:
            participant = await data_processing.get_data_from_model_filter(Participant, id=participant_id,
                                                                           meeting_id=data.meeting_id)
            if not participant:
                raise HTTPException(status_code=404, detail=f"Participant {participant_id} not found in this meeting")
            await data_processing.delete_data(Check, participant_id=participant.id, custom_item_id=data.custom_item_id)
        bills = await data_processing.get_data_all_from_model_filter(Check, custom_item_id=data.custom_item_id)
        get_number = await data_processing.get_data_from_model_filter(Check, custom_item_id=data.custom_item_id)
        number = get_number.custom_item_number
        update_split = {
            "splited_bill": split_bill_calculate(bills, custom_item, number)
        }
        await data_processing.update_data(Check, update_split, custom_item_id=data.custom_item_id)


async def user_check_rows(participant):
    query = (select(CustomItem.item_name, Check.splited_bill, Check.custom_item_number)
             .join(Check)
             .where(Check.participant_id == participant.id)
             )
    context = set_session_context("query")
    async with session() as db:
        results = await db.execute(query)
        reset_session_context(context)
    rows = results.fetchall()
    return rows


async def meeting_check_rows(participants):
    check_data = []
    for participant in participants:
        query = (
            select(CustomItem.item_name, Check.splited_bill, Check.custom_item_number)
            .join(Check)
            .where(Check.participant_id == participant.id)
        )
        context = set_session_context("query")
        async with session() as db:
            results = await db.execute(query)
            reset_session_context(context)
        rows = results.fetchall()
        check_explain = [{"item_name": row[0], "price": row[1], "number of position": row[2]} for row in rows]
        total_splited_bill = sum(row[1] for row in rows)
        user = await data_processing.get_data_from_model_filter(User, id=participant.user_id)
        participant_name = user.name if user else ""
        check_data.append({
            "participant_name": participant_name,
            "check_name": check_explain,
            "total_splited_bill": total_splited_bill,
        })
    return check_data






