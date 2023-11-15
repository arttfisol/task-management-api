import os
from dotenv import load_dotenv

load_dotenv()


def get_env(name, default=None, required=False, type_converter=None):
    value = os.getenv(name, default)

    if value is None and required:
        raise ValueError(f"{name} is required.")

    if value is not None and type_converter is not None:
        try:
            value = type_converter(value)
        except ValueError:
            raise ValueError(f"{name} must be a valid {type_converter.__name__}")

    return value


NODE_ENV = get_env(name="NODE_ENV", default="development")
PORT = get_env(name="PORT", default=6060, type_converter=int)
POSTGRES_HOST = get_env(name="POSTGRES_HOST", required=True)
POSTGRES_USER = get_env(name="POSTGRES_USER", required=True)
POSTGRES_PASS = get_env(name="POSTGRES_PASS", required=True)
POSTGRES_PORT = get_env(name="POSTGRES_PORT", default=5432, type_converter=int)
POSTGRES_DBNAME = get_env(name="POSTGRES_DBNAME", required=True)
POSTGRES_TASK_TABLENAME = get_env(name="POSTGRES_TASK_TABLENAME", default="tasks")
POSTGRES_USER_TABLENAME = get_env(name="POSTGRES_USER_TABLENAME", default="users")
