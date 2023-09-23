from fastapi import HTTPException


class Validate:
    @staticmethod
    def user_exist(user_):
        if user_ is not None:
            raise HTTPException(status_code=400, detail="Email already in use by another user")

    @staticmethod
    def not_user(user):
        if not user:
            raise HTTPException(status_code=400, detail="User not found")

    @staticmethod
    def activated(user):
        if user.user_status == "active":
            raise HTTPException(status_code=400, detail="User already activated")

    @staticmethod
    def owner_of_meeting(meetings, user_current):
        if meetings.owner_id != user_current.id:
            raise HTTPException(status_code=403, detail="You do not have permission")

    @staticmethod
    def not_owner_of_meeting(meetings, user_current):
        if meetings.owner_id == user_current.id:
            raise HTTPException(status_code=403, detail="You do not have permission")

    @staticmethod
    def is_participant(participants):
        if participants:
            raise HTTPException(status_code=400, detail="The User is all already a participant in this meeting")

    @staticmethod
    def is_not_participant(participants):
        if not participants:
            raise HTTPException(status_code=400, detail="User is not a participant of this meeting")

    @staticmethod
    def meeting_dont_exists(meeting):
        if not meeting:
            raise HTTPException(status_code=404, detail="Meeting not found")

    @staticmethod
    def feedback_dont_exists(feedback):
        if not feedback:
            raise HTTPException(status_code=404, detail="Feedback not found")

    @staticmethod
    def feedback_exists(feedback):
        if feedback:
            raise HTTPException(status_code=404, detail="Only 1 comment per Meeting")

    @staticmethod
    def feedback_creator(feedback, user):
        if feedback.user_id != user.id:
            raise HTTPException(status_code=403, detail="You do not have permission to update  or delete this feedback")

    @staticmethod
    def custom_item_exists(custom_item):
        if not custom_item:
            raise HTTPException(status_code=404, detail="Custom item not found")

    @staticmethod
    def check_exists(check):
        if check:
            raise HTTPException(status_code=400, detail="A check for this custom item in this meeting already exists")

    @staticmethod
    def check_dont_exists(check):
        if not check:
            raise HTTPException(status_code=403, detail="A check for this custom item doesnt exists")