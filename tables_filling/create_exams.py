from faker import Faker
import psycopg2


def generate_exams():
    def create_exams(db_config, faker: Faker, subject_count, classroom_count):
        with psycopg2.connect(**db_config) as conn:
            with conn.cursor() as cur:
                exam_data = []
                exam_id = 0
                for classroom_number in range(classroom_count):
                    for subject_id in range(subject_count):
                        exam_data.append(
                            (
                                exam_id,
                                faker.date_time_between(start_date="-1y", end_date="now"),
                                subject_id,
                                classroom_number
                            )
                        )
                        exam_id += 1

                cur.executemany(
                    "insert into exam (exam_id, date_time, subject_id, classroom_id) values (%s, %s, %s, %s);",
                    exam_data,
                )
        return exam_data

    def main():
        from config.config import db_config, SUBJECT_COUNT

        faker = Faker("ru_RU")
        exam_data = create_exams(db_config, faker, SUBJECT_COUNT, 500)

    main()
