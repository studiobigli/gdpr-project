from faker import Faker
from faker.providers import BaseProvider
from datetime import datetime
import random
import csv
import os

class GenreProvider(BaseProvider):
    def movie_genre(self):
        return random.choice(['Action', 'Comedy', 'Thriller', 'Horror', 'Political', 'Documentary'])

class LanguageProvider(BaseProvider):
    def language(self):
        return random.choice(['English', 'Chinese', 'Italian', 'Spanish', 'French', 'Japanese', 'Korean'])

fake = Faker()

fake.add_provider(GenreProvider)
fake.add_provider(LanguageProvider)

movie_id_count = 0

def movie_id():
    global movie_id_count
    movie_id_count += 1
    return movie_id_count

def get_movie_name():
    words = fake.words()

    capitalized_words = list(map(str.capitalize, words))
    return ' '.join(capitalized_words)

def get_movie_date():
    return datetime.strftime(fake.date_time_this_decade(), "%B %d, %Y")

def get_movie_len():
    return random.randrange(50, 150)

def get_movie_rating():
    return round(random.uniform(1.0,10.0), 1)

def generate_movie():
    return [movie_id(), get_movie_name(), fake.movie_genre(), get_movie_date(), get_movie_len(), get_movie_rating(), fake.language()]

with open('movie_data.csv', 'w') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Title', 'Genre', 'Premiere', 'Runtime', 'IMDB Score', 'Language'])
    file_size = 0
    while file_size < 1:
        file_size = os.stat('movie_data.csv').st_size / (1024 * 1024)
        writer.writerow(generate_movie())

