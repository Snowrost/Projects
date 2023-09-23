from datetime import datetime


def convert_date_time(data):
    date_of_activity = datetime.strptime(data.date_of_activity, "%Y-%m-%d %H:%M")
    return date_of_activity
