from faker import Faker
import psycopg2
import random
import pickle

from initial_data_preparing.cities_creating import get_cities_states_info


def generate_teachers():
    def create_teachers(db_config, faker: Faker, teacher_count,
                        subject_count, city_to_exam, city_id_to_name, city_id_to_state_id, state_id_to_name,
                        school_count):
        with psycopg2.connect(**db_config) as conn:
            with conn.cursor() as cur:
                teachers_data = []
                addresses_data = []
                teacher_with_exam_data = []

                address_id = school_count
                teacher_id = 0
                for teacher_number in range(teacher_count):
                    school_id = random.randint(0, school_count - 1)
                    city_id = school_id % len(city_id_to_state_id)
                    subject_id = random.randint(0, subject_count - 1)
                    addresses_data.append(
                        (
                            address_id,
                            state_id_to_name[city_id_to_state_id[city_id]],
                            city_id_to_name[city_id],
                            faker.street_name(),
                            faker.postcode(),
                        )
                    )
                    teachers_data.append(
                        [
                            teacher_id,
                            str(random.randint(1000, 9999)),  # преобразование в строку
                            str(random.randint(100000, 999999)),
                            faker.last_name(),
                            faker.first_name(),  # используем first_name вместо name
                            faker.middle_name(),
                            faker.date_of_birth().strftime('%Y-%m-%d'),  # форматируем дату в формат YYYY-MM-DD
                            'Teacher',  # убедитесь, что это значение соответствует ENUM в БД
                            address_id,
                            school_id,
                            subject_id,
                        ]
                    )

                    if city_id in city_to_exam:
                        for ex_id, sub_id in random.sample(city_to_exam[city_id], 10):
                            if sub_id == subject_id:
                                continue
                            teacher_with_exam_data.append(
                                (
                                    ex_id,
                                    teacher_id
                                )
                            )

                    address_id += 1
                    teacher_id += 1

                cur.executemany(
                    "INSERT INTO Address (address_id, region, city, street, postal_code) VALUES (%s, %s, %s, %s, %s);",
                    addresses_data,
                )
                cur.executemany(
                    """INSERT INTO Person 
                    (person_id, passport_series, passport_number, last_name, first_name, middle_name, birthday, role, address_id, school_id, subject_id) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);""",
                    teachers_data,
                )
                cur.executemany(
                    "insert into PersonExam (exam_id, person_id) values (%s, %s);",
                    teacher_with_exam_data,
                )
    def main():
        from config.config import db_config, teacher_count, SUBJECT_COUNT, school_count
        faker = Faker("ru_RU")
        with open('city_to_exam.pkl', 'rb') as f:
            city_to_exam = pickle.load(f)
        city_id_to_name, city_id_to_state_id, state_id_to_name = get_cities_states_info()
        create_teachers(db_config, faker, teacher_count, SUBJECT_COUNT, city_to_exam, city_id_to_name, city_id_to_state_id, state_id_to_name, school_count)
    main()
