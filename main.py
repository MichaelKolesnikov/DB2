from tables_creating.tables_creating import create_tables
from tables_filling.create_exams import generate_exams

from tables_filling.create_schoolchildren import generate_schoolchildren
from tables_filling.create_schools import generate_school
from tables_filling.create_tasks import generate_tasks
from tables_filling.create_teachers import generate_teachers


def main():
    create_tables()
    generate_tasks()
    generate_school()
    generate_exams()
    generate_teachers()
    generate_schoolchildren()


if __name__ == "__main__":
    main()
