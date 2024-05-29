from dotenv import load_dotenv
from os import getenv, path
import pandas as pd
from generate import DataGenerator
from constants import *
from google.cloud import storage

load_dotenv()

data_dir = getenv("SEED_DIR")


def get_static_data():
    return {
        "room_types": DataGenerator.to_dataframe(room_variations),
        "amenities": DataGenerator.to_dataframe(addons),
    }


def get_person_data(datagen: DataGenerator, locations: pd.DataFrame):
    users = datagen.generate_persons(num_users, locations)
    guests = datagen.generate_persons(num_guests, locations)
    return {
        "guests": (
            DataGenerator.to_dataframe(users + guests).drop_duplicates(subset=["email"])
        ),
        "users": (
            DataGenerator.to_dataframe(users)
            .drop_duplicates(subset=["email"])
            .drop(columns=["dob"])
        ),
    }


def get_hotel_data(datagen: DataGenerator, users: pd.DataFrame):
    bookings = DataGenerator.to_dataframe(
        datagen.generate_bookings(num_bookings, max_stay)
    )
    bookings["idx"] = bookings.index % users.shape[0]
    return {
        "rooms": (
            DataGenerator.to_dataframe(datagen.generate_rooms(floors, floor_rooms))
        ),
        "bookings": (
            bookings.merge(users["email"], left_on="idx", right_index=True)
            .drop(columns=["idx"])
            .rename(columns={"email": "user"})
        ),
    }


def get_generated_data(event, context):
    locations = DataGenerator.get_locations()
    datagen = DataGenerator(getenv("SEED"))
    static_data = get_static_data()
    person_data = get_person_data(datagen, locations)
    hotel_data = get_hotel_data(datagen, person_data["users"])
    all_data = {**static_data, **person_data, **hotel_data}
    storage_client = storage.Client()
    bucket = storage_client.bucket(getenv('GCS_BUCKET'))
    for name, data in all_data.items():
        file_path = path.join(data_dir, name + ".csv")
        bucket.blob(file_path).upload_from_string(data.to_csv(index=False))
    return "success"
