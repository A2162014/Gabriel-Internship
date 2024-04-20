import calendar
import datetime

def get_working_days(year, month):
    cal = calendar.Calendar()
    working_days = [
        day for day in cal.itermonthdays(year, month)
        if day != 0 and datetime.date(year, month, day).weekday() <= 5
    ]
    return working_days

# Get the current year and month
current_year = 2020
current_month = 2

working_days = get_working_days(current_year, current_month)
print("Working days of the current month:", working_days)
print("Total number of days in the month:", len(working_days))
