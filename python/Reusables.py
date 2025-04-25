from datetime import datetime

#The calculate age function to help in getting the age of the clients
def calculate_age(date_of_birth):
    birth_date = datetime.strptime(date_of_birth, '%Y-%m-%d')  # Assuming the format is 'YYYY-MM-DD'
    today = datetime.today()
    age = today.year - birth_date.year
    if today.month < birth_date.month or (today.month == birth_date.month and today.day < birth_date.day):
        age -= 1
    return age