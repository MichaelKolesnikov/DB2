import faker

from initial_data_preparing.cities_creating import generate_cities_info_file
from initial_data_preparing.create_subject import create_and_get_subjects_data
from tables_creating.tables_creating import create_tables
from tables_filling.create_exams import generate_exams
from tables_filling.create_schools import generate_school
from tables_filling.create_tasks import generate_tasks
from tables_filling.create_teachers import generate_teachers


def main():
    create_tables()
    generate_tasks()
    generate_school()
    generate_exams()
    generate_teachers()




if __name__ == "__main__":
    main()
