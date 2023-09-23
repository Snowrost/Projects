from fastapi import APIRouter, Depends
from src.repository import DataProcessing
from src.models import User
from fastapi.security import OAuth2PasswordRequestForm
from src.schemas import UserSchema, UpdateUser, Token
from src.controllers import get_password, authenticate_user, send_email, update_user_parameters
from src.controllers.validation import Validate
from src.controllers.security import (create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES,
                                      get_current_active_user)
from typing import Annotated
from datetime import timedelta

router = APIRouter()
data_processing = DataProcessing()
current_user = None


@router.post("/signup", summary="Create new user", tags=["User"])
async def register_user(data: UserSchema):
    existing_user = await data_processing.get_data_from_model_filter(User, email=data.email)
    Validate.user_exist(existing_user)
    user_data = {"email": data.email, "password": get_password(data.password)}
    await data_processing.save_data(User, user_data)
    await send_email(data.email)
    return {"message": "Registration successful"}


# Make method get just to test that email working, i know that it must be put or patch
@router.get("/activation/{user_id}", summary="Activating user", tags=["User"])
async def activation(user_id: str):
    user = await data_processing.get_data_from_model_filter(User, id=user_id)
    Validate.not_user(user)
    Validate.activated(user)
    update_dict = {"user_status": "active"}
    await data_processing.update_data(User, update_dict, id=user_id)
    return {"User activated successful"}


@router.post("/login", summary="Create access for user", tags=["User"], response_model=Token)
async def login_user(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user_ = await authenticate_user(form_data.username, form_data.password)
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = await create_access_token(data={"sub": user_.email}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}


@router.put("/update-user", summary="Update user info", tags=["User"])
async def update_user_data(data: UpdateUser, current: Annotated[User, Depends(get_current_active_user)]):
    await data_processing.update_data(User, await update_user_parameters(data, current), id=current.id)
    return {"message": "User data updated successfully"}
