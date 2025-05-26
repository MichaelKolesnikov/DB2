from faker import Faker
import psycopg2
import random


def generate_teachers():
    def create_teachers(
            db_config,
            faker: Faker,
            teacher_count,
            subject_count,
            school_count):
        with psycopg2.connect(**db_config) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT exam_id, subject_id from exam;")
                rows = cur.fetchall()
                exam_ids = [(row[0], row[1]) for row in rows]

        teachers_data = []
        addresses_data = (
            (
                address_id,
                faker.street_name(),
                faker.postcode(),
            ) for address_id in range(school_count, school_count + teacher_count)
        )
        teacher_with_exam_data = []

        address_id = school_count
        teacher_id = 0
        for teacher_number in range(teacher_count):
            school_id = random.randint(0, school_count - 1)
            subject_id = random.randint(0, subject_count - 1)
            teachers_data.append(
                [
                    teacher_id,
                    str(random.randint(1000, 9999)),
                    str(random.randint(100000, 999999)),
                    faker.last_name(),
                    faker.first_name(),
                    faker.middle_name(),
                    faker.date_of_birth().strftime('%Y-%m-%d'),
                    'Teacher',
                    address_id,
                    school_id,
                    subject_id,
                ]
            )

            for ex_id, sub_id in random.sample(exam_ids, 10):
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

        with psycopg2.connect(**db_config) as conn:
            with conn.cursor() as cur:
                cur.executemany(
                    "INSERT INTO Address (address_id, street, postal_code) VALUES (%s, %s, %s);",
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
        create_teachers(db_config, faker, teacher_count, SUBJECT_COUNT, school_count)

    main()
