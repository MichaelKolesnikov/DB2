from faker import Faker
import random
import psycopg2
import pickle

from config.config import teacher_count
from initial_data_preparing.create_subject import parse_subject_mapping


def create_school_children(
        db_config,
        faker: Faker,
        school_count,
        school_children_count,
        task_number_subject_to_ids,
        subject_id_to_tasks,
        address_id_first
):
    subject_points = parse_subject_mapping("initial_data_preparing/subject_data.txt")

    exam_statuses = [
        'Registered',
        'Passed',
        'Failed',
        'Absent',
        'Appealed',
        'Canceled',
        'Processing',
        'Waiting'
    ]
    exam_result_data = []
    written_task_data = []

    addresses_data = tuple(
        (
            school_children_id,
            faker.street_name(),
            faker.postcode()
        ) for school_children_id in range(address_id_first, address_id_first + school_children_count)
    )
    with psycopg2.connect(**db_config) as conn:
        with conn.cursor() as cur:
            cur.executemany(
                "INSERT INTO Address (address_id, street, postal_code) VALUES (%s, %s, %s);",
                addresses_data,
            )
    del addresses_data

    school_children_data = tuple(
        (
            school_children_id,
            str(random.randint(1000, 9999)),
            str(random.randint(100000, 999999)),
            faker.last_name(),
            faker.first_name(),
            faker.middle_name(),
            faker.date_of_birth().strftime('%Y-%m-%d'),
            'SchoolChild',
            school_children_id,
            random.randint(0, school_count - 1),
            None,
        ) for school_children_id in range(address_id_first, address_id_first + school_children_count)
    )
    with psycopg2.connect(**db_config) as conn:
        with conn.cursor() as cur:
            cur.executemany(
                """INSERT INTO Person
                (person_id, passport_series, passport_number, last_name, first_name, middle_name, birthday, role, address_id, school_id, subject_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);""",
                school_children_data,
            )
    del school_children_data

    with psycopg2.connect(**db_config) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT subject_id, name FROM Subject")
            rows = cur.fetchall()
            subject_id_to_name = {row[0]: row[1] for row in rows}
            cur.execute("SELECT exam_id from exam where subject_id=2;")
            rows = cur.fetchall()
            rus_exam_ids = [row[0] for row in rows]
            cur.execute("SELECT exam_id from exam where subject_id=0;")
            rows = cur.fetchall()
            math_base_exam_ids = [row[0] for row in rows]
            cur.execute("SELECT exam_id from exam where subject_id=1;")
            rows = cur.fetchall()
            math_prof_exam_ids = [row[0] for row in rows]
            cur.execute("SELECT exam_id, subject_id from exam where subject_id > 2;")
            rows = cur.fetchall()
            third_exam_ids = [(row[0], row[1]) for row in rows]

    schoolchild_with_exam_data = tuple(
        (
            school_children_id,
            ex_id,
        )
        for school_children_id in range(address_id_first, address_id_first + school_children_count)
        for ex_id in (
            random.choice(rus_exam_ids),
            random.choice(math_prof_exam_ids) if random.getrandbits(1) else random.choice(math_base_exam_ids),
            random.choice(third_exam_ids)[0]
        )
    )

    for school_children_id, ex_id in schoolchild_with_exam_data:
        sub_id = (ex_id - 1) % 16
        exam_status = random.choice(exam_statuses)
        if exam_status not in ("Passed", "Failed", "Appealed"):
            exam_result_data.append((
                0,
                exam_status,
                "some comments",
                school_children_id,
                sub_id,
                ex_id
            ))

        cur_task_data = [
            (
                random.choice(task_number_subject_to_ids[task_number, sub_id]),
                school_children_id,
                random.randint(0, int(subject_points[subject_id_to_name[sub_id]][task_number]))
            ) for task_number in range(1, len(subject_id_to_tasks[sub_id]) + 1)
        ]
        written_task_data += cur_task_data

        exam_result_data.append((
            sum(i[0] for i in cur_task_data),
            exam_status,
            "some comments",
            school_children_id,
            sub_id,
            ex_id
        ))

    with psycopg2.connect(**db_config) as conn:
        with conn.cursor() as cur:
            cur.executemany(
                "insert into ExamResult (score, status, comments, person_id, subject_id, exam_id) values (%s, %s, %s, %s, %s, %s);",
                exam_result_data,
            )
            cur.executemany(
                "insert into PersonExam (person_id, exam_id) values (%s, %s);",
                schoolchild_with_exam_data,
            )

            cur.executemany(
                "insert into WrittenTask (task_id, person_id, grade) values (%s, %s, %s);",
                written_task_data,
            )
            conn.commit()



def generate_schoolchildren():
    from config.config import db_config, school_children_count, school_count, teacher_count
    faker = Faker("ru_RU")

    with open('subject_id_to_tasks.pkl', 'rb') as f:
        subject_id_to_tasks = pickle.load(f)
    with open('task_number_subject_to_ids.pkl', 'rb') as f:
        task_number_subject_to_ids = pickle.load(f)

    create_school_children(
        db_config,
        faker,
        school_count,
        school_children_count,
        task_number_subject_to_ids,
        subject_id_to_tasks,
        school_count + teacher_count
    )
