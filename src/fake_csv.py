from faker import Faker 
from faker.providers import BaseProvider 
from datetime import datetime
import random
import csv
import os

#GDPR Relevant fields required
#phone_number
#date_of_birth
#games_played
#won_games
#drawn_games
#lost_games
#points
#rank

class LanguageProvider(BaseProvider):
    def language(self):
        return random.choice(['English', 'Chinese', 'Italian', 'Spanish', 'French', 'Japanese', 'Korean'])

fake = Faker('en_GB')
fake.add_provider(LanguageProvider)

person_id_count = 0

def get_person_id():
    global person_id_count
    person_id_count += 1
    return person_id_count

def get_street_address():
    return fake.street_address().replace('\n', ' ').title()

def get_phone_number():
    number = random.randint(000000000, 999999999)
    return f"+44{number:09d}"

def generate_data():
    return [get_person_id(), 
            fake.first_name(), 
            fake.last_name(), 
            get_street_address(), 
            fake.city(), 
            fake.postcode(), 
            get_phone_number(),
            fake.date_between(start_date="-50y", end_date="-18y")
            ]

with open('fake_data.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['id', 
                     'First Name', 
                     'Last Name', 
                     'Street Address', 
                     'City', 
                     'Postcode',
                     'Phone Number',
                     'Date of Birth'])
    file_size = 0
    while file_size < 1:
        file_size = os.stat('fake_data.csv').st_size / (1024 * 1024)
        writer.writerow(generate_data())

