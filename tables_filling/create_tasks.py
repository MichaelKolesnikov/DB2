import pickle
import psycopg2
from config.config import db_config, number_of_variants_per_subject
from initial_data_preparing.create_subject import create_and_get_subjects_data


def generate_tasks():
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

    def create_tasks(cur, subject_id_to_name, subjects_points, number_of_variants: int):
        tasks_data = []
        task_id = 0
        task_id_to_task_data = []
        task_number_subject_to_ids = {}
        for subject_id in subject_id_to_name:
            subject_name = subject_id_to_name[subject_id]
            for task_number in subjects_points[subject_name]:
                for variant_number in range(number_of_variants):
                    price = subjects_points[subject_name][task_number]
                    description = f"{subject_name}-task"
                    tasks_data.append(
                        (task_id, task_number, description, price, variant_number, subject_id)
                    )
                    task_id_to_task_data.append([task_number, subject_name])

                    if (task_number, subject_id) not in task_number_subject_to_ids:
                        task_number_subject_to_ids[task_number, subject_id] = []
                    task_number_subject_to_ids[task_number, subject_id].append(task_id)
                    task_id += 1
        cur.executemany(
            "insert into task (task_id, number, description, price, variant, subject_id) values (%s, %s, %s, %s, %s, %s);",
            tasks_data,
        )
        assert task_id == len(task_id_to_task_data)
        return task_id_to_task_data, task_number_subject_to_ids

    def main():
        subjects_points = parse_subject_mapping("initial_data_preparing/subject_data.txt")

        with psycopg2.connect(**db_config) as conn:
            with conn.cursor() as cur:
                subject_id_to_name, subject_name_to_id, subject_id_to_tasks = create_and_get_subjects_data()

                task_id_to_task_data, task_number_subject_to_ids = create_tasks(
                    cur, 
                    subject_id_to_name, 
                    subjects_points, 
                    number_of_variants_per_subject
                )

                with open('subject_id_to_tasks.pkl', 'wb') as f:
                    pickle.dump(subject_id_to_tasks, f)
                with open('task_id_to_task_data.pkl', 'wb') as f:
                    pickle.dump(task_id_to_task_data, f)
                with open('task_number_subject_to_ids.pkl', 'wb') as f:
                    pickle.dump(task_number_subject_to_ids, f)

    main()
