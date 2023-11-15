import config
from db import db
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


def init_db():
    commands = (
        f"""
            DROP TABLE IF EXISTS {config.POSTGRES_TASK_TABLENAME}
        """,
        f""" 
            DROP TABLE IF EXISTS {config.POSTGRES_USER_TABLENAME}
        """,
        f"""
            CREATE TABLE IF NOT EXISTS {config.POSTGRES_USER_TABLENAME} (
            id VARCHAR(255) PRIMARY KEY,
            name VARCHAR(255) NOT NULL
        )
        """,
        f"""
            CREATE TABLE IF NOT EXISTS {config.POSTGRES_TASK_TABLENAME} (
            id VARCHAR(255) PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            description VARCHAR(255) NOT NULL,
            due_date DATE NOT NULL,
            status VARCHAR(255) NOT NULL,
            created_by VARCHAR(255) NOT NULL REFERENCES {config.POSTGRES_USER_TABLENAME} (id),
            created_time TIMESTAMPTZ NOT NULL,
            updated_by VARCHAR(255) NOT NULL REFERENCES {config.POSTGRES_USER_TABLENAME} (id),
            updated_time TIMESTAMPTZ NOT NULL
        )
        """,
        f"""
            INSERT INTO {config.POSTGRES_USER_TABLENAME} (id, name) VALUES ('user1', 'name1'), ('user2', 'name2'), ('user3', 'name3'), ('user4', 'name4'), ('user5', 'name5')
        """,
    )
    db.connect(
        host=config.POSTGRES_HOST,
        dbname=config.POSTGRES_DBNAME,
        user=config.POSTGRES_USER,
        password=config.POSTGRES_PASS,
        port=config.POSTGRES_PORT,
    )

    db._connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

    cursor = db._connection.cursor()

    for command in commands:
        cursor.execute(command)

    cursor.close()
    db._connection.commit()
    print("Initial Database Success")
    return


init_db()
