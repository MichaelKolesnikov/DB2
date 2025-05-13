import psycopg2

from config.config import db_config


def create_tables():
    try:
        with open("tables_creating/tables_creating.sql") as f:
            create_command = f.read()
        with psycopg2.connect(**db_config) as conn:
            with conn.cursor() as cur:
                cur.execute(create_command)

    except Exception as e:
        print(e)
