from faker import Faker
from faker.providers import BaseProvider
import random
import csv
import os
import sys

filepath = ""


class LanguageProvider(BaseProvider):
    def language(self):
        return random.choice(
            ["English", "Chinese", "Italian", "Spanish", "French", "Japanese", "Korean"]
        )


fake = Faker("en_GB")
fake.add_provider(LanguageProvider)

person_id_count = 0
ranks = ["Bronze", "Silver", "Gold", "Platinum", "Diamond", "Master"]
rank_thresholds = [0, 25, 50, 75, 100, 125]


def _get_person_id():
    global person_id_count
    person_id_count += 1
    return person_id_count


def _get_street_address():
    return fake.street_address().replace("\n", " ").title()


def _get_phone_number():
    number = random.randint(000000000, 999999999)
    return f"+44{number:09d}"


def _get_score():
    wins = random.randint(0, 50)
    losses = random.randint(0, 50)
    ties = random.randint(0, 50)
    played = wins + losses + ties
    points = ((wins * 5) - (losses * 4)) + ties
    if points < 0:
        points = 0

    rank = ranks[sum(points >= x for x in rank_thresholds) - 1]

    return [played, wins, losses, ties, points, rank]


def _generate_data():
    score = _get_score()
    return [
        _get_person_id(),
        fake.first_name(),
        fake.last_name(),
        _get_street_address(),
        fake.city(),
        fake.postcode(),
        _get_phone_number(),
        fake.date_between(start_date="-50y", end_date="-18y"),
        score[0],
        score[1],
        score[2],
        score[3],
        score[4],
        score[5],
        fake.language(),
    ]


def fake_csv(filepath):

    if not isinstance(filepath, str) or not filepath:
        filepath = "../dummydata.csv"
        print(f"Filepath not included, defaulting to {filepath}\n")

    check = filepath.rsplit(".", 1)[1]
    if check != "csv":
        raise Exception("Target file is not .csv extension")

    if os.access(filepath, os.F_OK) is True:
        if os.access(filepath, os.W_OK) is False:
            print(f"File {filepath} exists and is not writeable, Aborting")
            sys.exit()
        else:
            overwrite = ""
            while overwrite != "y" and overwrite != "n":
                print(f"{overwrite=}")
                overwrite = input(
                    f"File {filepath} already exists, overwrite? (y/n):"
                ).lower()
            if overwrite != "y":
                print("Closing...")
                sys.exit()

    with open(filepath, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(
            [
                "id",
                "First Name",
                "Last Name",
                "Street Address",
                "City",
                "Postcode",
                "Phone Number",
                "Date of Birth",
                "Played",
                "Wins",
                "Losses",
                "Ties",
                "Points",
                "Rank",
                "Language",
            ]
        )
        file_size = 0
        while file_size < 1:
            file_size = os.stat(filepath).st_size / (1024 * 1024)
            writer.writerow(_generate_data())

        return filepath


if __name__ == "__main__":
    if len(sys.argv) > 1:
        filepath = sys.argv[1]

    print(filepath)
    fake_csv(filepath)
