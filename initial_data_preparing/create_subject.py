import json
import psycopg2
from config.config import db_config


def parse_subject_mapping(file_path):
    points = {}

    with open(file_path, 'r', encoding='utf-8') as file:
        current_subject = None
        for line in file.read().split('\n'):
            if not line:
                continue
            if line[0].isalpha():
                current_subject = line
                points[current_subject] = {}
                continue

            tasks, price = line.split()
            if '-' in tasks:
                task1, task2 = map(int, tasks.split('-'))
            else:
                task1 = task2 = int(tasks)
            for i in range(task1, task2 + 1):
                points[current_subject][i] = price

    return points


def create_and_get_subjects_data():
    def create_subjects(cur):
        subjects_points = parse_subject_mapping("initial_data_preparing/subject_data.txt")
        subjects_data = []
        subject_id_to_tasks = [0] * 17
        sub_id = 0
        subject_id_to_name = []
        for subject in subjects_points:
            score_mapping = subjects_points[subject]
            score_mapping_json = json.dumps(score_mapping, ensure_ascii=False)
            subjects_data.append((sub_id, subject, score_mapping_json))

            subject_id_to_tasks[sub_id] = subjects_points[subject]
            subject_id_to_name.append(subject)
            sub_id += 1
        cur.executemany(
            "INSERT INTO Subject (subject_id, name, score_mapping_json) VALUES (%s, %s, %s);",
            subjects_data,
        )

        cur.execute("SELECT subject_id, name FROM Subject;")
        subject_id_to_name = {row[0]: row[1] for row in cur.fetchall()}
        subject_name_to_id = {subject_id_to_name[i]: i for i in subject_id_to_name}
        return subject_id_to_name, subject_name_to_id, subject_id_to_tasks


    with psycopg2.connect(**db_config) as conn:
        with conn.cursor() as connection_cursor:
            return create_subjects(connection_cursor)
