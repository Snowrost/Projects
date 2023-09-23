from src.repository import DataProcessing
from src.models import User
from passlib.context import CryptContext
import smtplib
from fastapi import HTTPException
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
data_processing = DataProcessing()


def get_password(password: str):
    return password_context.hash(password)


def verify_password(password: str, hashed_pass: str):
    return password_context.verify(password, hashed_pass)


async def authenticate_user(email: str, password: str):
    user = await data_processing.get_data_from_model_filter(User, email=email)
    if not user:
        raise HTTPException(status_code=400, detail="User not found")
    if not verify_password(password, user.password):
        raise HTTPException(status_code=401, detail="Invalid password")
    if user.user_status == "new":
        raise HTTPException(status_code=400, detail="User arent confirm his email")
    return user


async def send_email(email):
    gmail_user = "meetingproject3@gmail.com"
    gmail_password = "atzg eawv hbxy ryxn"
    sent_from = gmail_user
    user = await data_processing.get_data_from_model_filter(User, email=email)
    to = [user.email]
    subject = 'Meetings APP Team'
    link = f"http://0.0.0.0:8000/users/activation/{user.id}"
    body = f"""
    <html>
    <head></head>
    <body>
        <h1 style="color: #007bff;">Hello and Welcome!</h1>
        <p>This is an email from the Meetings APP Team.</p>
        <p>Thank you for joining our app. Please visit our <a href="{link}">website</a> for more information.</p>
    </body>
    </html>
    """

    email_text = MIMEMultipart()
    email_text['From'] = sent_from
    email_text['To'] = ", ".join(to)
    email_text['Subject'] = subject
    email_text.attach(MIMEText(body, 'html'))

    try:
        smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        smtp_server.ehlo()
        smtp_server.login(gmail_user, gmail_password)
        smtp_server.sendmail(sent_from, to, email_text.as_string())
        smtp_server.close()
    except Exception as ex:
        print("Something went wrong….", ex)


async def update_user_parameters(data, current):
    update_dict = {}
    if data.name:
        update_dict["name"] = data.name
    if data.lastname:
        update_dict["lastname"] = data.lastname
    if data.password:
        update_dict["password"] = get_password(data.password)
    if data.email:
        existing_email_user = await data_processing.get_data_from_model_filter(User, email=current.email)
        if existing_email_user is not None:
            raise HTTPException(status_code=400, detail="Email is already in use by another user")
        update_dict["email"] = data.email
    return update_dict


