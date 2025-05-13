import random

from faker import Faker
import psycopg2

from initial_data_preparing.cities_creating import get_cities_states_info


def generate_school():
    def create_addresses_for_schools(cur, faker: Faker, count, city_id_to_name, city_id_to_state_id, state_id_to_name):
        city_count = len(city_id_to_state_id)
        final_data = []
        for address_id in range(count):
            city_id = address_id % city_count
            address = (
                address_id,
                state_id_to_name[city_id_to_state_id[city_id]],
                city_id_to_name[city_id],
                faker.street_name(),
                faker.postcode(),
            )
            final_data.append(address)

        cur.executemany(
            "INSERT INTO Address (address_id, region, city, street, postal_code) VALUES (%s, %s, %s, %s, %s);",
            final_data,
        )

    def create_schools(cur, faker, school_count, city_id_to_name, city_id_to_state_id, state_id_to_name):
        create_addresses_for_schools(cur, faker, school_count, city_id_to_name, city_id_to_state_id, state_id_to_name)
        school_data = []
        for i in range(school_count):
            school_name = f"Школа №{i}"
            school_data.append(
                (i, school_name, i)
            )
        cur.executemany(
            "INSERT INTO School (school_id, school_name, address_id) VALUES (%s, %s, %s);",
            school_data,
        )

    def create_classrooms(cur, school_count):
        classroom_data = []
        classroom_id = 0
        for school_number in range(school_count):
            for classroom_number in range(500):
                classroom_data.append(
                    (classroom_id, classroom_number, school_number)
                )
                classroom_id += 1
        cur.executemany(
            "INSERT INTO Classroom (classroom_id, number, school_id) VALUES (%s, %s, %s);",
            classroom_data
        )

    def main():
        from config.config import db_config, school_count
        faker = Faker("ru_RU")

        with psycopg2.connect(**db_config) as conn:
            with conn.cursor() as cur:
                city_id_to_name, city_id_to_state_id, state_id_to_name = get_cities_states_info()
                create_schools(cur, faker, school_count, city_id_to_name, city_id_to_state_id, state_id_to_name)
                create_classrooms(cur, school_count)


    main()
