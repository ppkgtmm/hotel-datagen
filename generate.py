import pandas as pd
from faker import Faker
from faker.generator import random
from datetime import timedelta
from os import getenv
from constants import room_variations


class DataGenerator:
    def __init__(self, seed: str, genders: list[str] = None):
        self.seed = seed
        self.fake = Faker()
        Faker.seed(self.seed)
        self.genders = genders if genders else ["M", "F", "Prefer not to say"]

    @staticmethod
    def to_dataframe(data: list[dict]):
        return pd.DataFrame(data)

    @staticmethod
    def get_locations():
        url = getenv("LOCATION_FILE")
        locations = pd.read_csv(url)
        return locations[["name", "admin"]]

    def generate_rooms(self, floors: int, floor_rooms: int):
        result = []
        room_types = DataGenerator.to_dataframe(room_variations)
        room_types = room_types.sort_values(by="price", ascending=False)
        room_types = room_types.reset_index(drop=True)
        weights = [(i + 1) / room_types.shape[0] for i in room_types.index]

        for room_number in range(1, floor_rooms + 1):
            room_type = random.choices(room_types.name.tolist(), weights=weights, k=1)
            for floor in range(1, floors + 1):
                result.append(dict(floor=floor, number=room_number, type=room_type[0]))

        return result

    def generate_bookings(self, count: int, max_stay: int):
        bookings = []
        stay_duration = list(range(1, max_stay + 1))
        max_stay, sum_stay = max(stay_duration), sum(stay_duration)
        stay_weight = [(max_stay - stay + 1) / sum_stay for stay in stay_duration]

        for _ in range(count):
            checkin = self.fake.date_between(start_date="-1y", end_date="today")
            stay_days = random.choices(stay_duration, weights=stay_weight, k=1)[0]
            checkout = checkin + timedelta(days=stay_days)
            bookings.append(dict(checkin=checkin, checkout=checkout))

        return bookings

    def generate_persons(self, count: int, locations: pd.DataFrame):
        persons, locations = [], locations.values
        for _ in range(count):
            fname, lname = self.fake.first_name(), self.fake.last_name()
            gender = random.choice(self.genders)
            email = f"{fname}.{lname}@{self.fake.free_email().split('@')[-1]}".lower()
            dob = self.fake.date_between(start_date="-80y", end_date="-20y")

            location = random.choice(locations)
            persons.append(
                dict(
                    firstname=fname,
                    lastname=lname,
                    gender=gender,
                    email=email,
                    dob=dob,
                    state=location[0],
                    country=location[1],
                )
            )
        return persons
    