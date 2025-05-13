from faker import Faker
import psycopg2
import pickle


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
        from initial_data_preparing.cities_creating import get_cities_states_info
        city_id_to_name, city_id_to_state_id, state_id_to_name = get_cities_states_info()

        faker = Faker("ru_RU")
        exam_data = create_exams(db_config, faker, SUBJECT_COUNT, 500)
        city_to_exam = {}
        for exam_id, _, subject_id, school_id in exam_data:
            city_ = school_id % len(city_id_to_name)
            if city_ not in city_to_exam:
                city_to_exam[city_] = []
            city_to_exam[city_].append([exam_id, subject_id])
        with open('city_to_exam.pkl', 'wb') as f:
            pickle.dump(city_to_exam, f)

    main()
