import time
import math
import config
import psycopg2
from pytz import timezone
from datetime import datetime


class Database:
    _instance = None
    SELECT_TASK = f"""
        SELECT {config.POSTGRES_TASK_TABLENAME}.id, {config.POSTGRES_TASK_TABLENAME}.title, {config.POSTGRES_TASK_TABLENAME}.description, TO_CHAR({config.POSTGRES_TASK_TABLENAME}.due_date, 'YYYY-MM-DD'), {config.POSTGRES_TASK_TABLENAME}.status, json_build_object('id', created_user.id, 'name', created_user.name) AS created_by, TO_CHAR({config.POSTGRES_TASK_TABLENAME}.created_time, 'YYYY-MM-DD"T"HH24:MI:SS.USOF') || ':00', json_build_object('id', updated_user.id, 'name', updated_user.name) AS updated_by, TO_CHAR({config.POSTGRES_TASK_TABLENAME}.updated_time, 'YYYY-MM-DD"T"HH24:MI:SS.USOF') || ':00'
        FROM {config.POSTGRES_TASK_TABLENAME}
        JOIN {config.POSTGRES_USER_TABLENAME} AS created_user ON {config.POSTGRES_TASK_TABLENAME}.created_by = created_user.id
        JOIN {config.POSTGRES_USER_TABLENAME} AS updated_user ON {config.POSTGRES_TASK_TABLENAME}.updated_by = updated_user.id
    """

    # handle singleton in pyrhon
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._connection = None
        return cls._instance

    def connect(self, host, port, dbname, user, password):
        try:
            self._connection = psycopg2.connect(
                host=host, port=port, dbname=dbname, user=user, password=password
            )
            print("Database connected.")
        except Exception as e:
            print(f"Failed to connect to database: {e}")

    def close(self):
        if self._connection:
            self._connection.close()
            print("Database closed.")

    def get_task_list(
        self,
        statuses,
        due_dates,
        due_date_since,
        due_date_until,
        created_users,
        updated_users,
        order,
        limit,
        offset,
    ):
        try:
            cursor = self._connection.cursor()

            # convert "txt1,txt2,txt3" to "IN ('txt1', 'txt2', 'txt3')"
            statuses = self.format_input(statuses)
            due_dates = self.format_input(due_dates)
            created_users = self.format_input(created_users)
            updated_users = self.format_input(updated_users)

            # if due_dates is empty and due_date_since is not
            # change query to BETWEEN with since and until
            if not due_dates and due_date_since:
                # if due_date_until is empty, replace with today
                if not due_date_until:
                    due_date_until = datetime.now().strftime("%Y-%m-%d")

                due_dates = f"BETWEEN '{due_date_since}' AND '{due_date_until}'"

            # assemble all condition
            condition = ""
            if statuses or due_dates or created_users or updated_users:
                condition_list = []

                if statuses:
                    condition_list.append(
                        f"{config.POSTGRES_TASK_TABLENAME}.status {statuses}"
                    )
                if due_dates:
                    condition_list.append(
                        f"{config.POSTGRES_TASK_TABLENAME}.due_date {due_dates}"
                    )

                if created_users:
                    condition_list.append(
                        f"{config.POSTGRES_TASK_TABLENAME}.created_by {created_users}"
                    )
                if updated_users:
                    condition_list.append(
                        f"{config.POSTGRES_TASK_TABLENAME}.updated_by {updated_users}"
                    )
                condition_list = " AND ".join(condition_list)
                condition = f"\nWHERE {condition_list}"

            # assemble order by, limit, offset
            suffix = ""
            if order:
                suffix += f"\nORDER BY created_time {order}"
            if limit and limit != "0":
                suffix += f"\nLIMIT {limit}"
            if offset:
                suffix += f"\nOFFSET {offset}"

            cursor.execute(f"{self.SELECT_TASK}{condition}{suffix}")
            records = cursor.fetchall()
            result = []
            for record in records:
                result.append(self.format_result(record))
            cursor.close()
            return result
        except Exception as e:
            self._connection.rollback()
            if cursor:
                cursor.close()
            raise e

    def get_task(self, task_id):
        try:
            cursor = self._connection.cursor()
            cursor.execute(
                f"{self.SELECT_TASK} WHERE {config.POSTGRES_TASK_TABLENAME}.id = '{task_id}'"
            )
            record = cursor.fetchone()
            cursor.close()
            return self.format_result(record)
        except Exception as e:
            self._connection.rollback()
            if cursor:
                cursor.close()
            raise e

    def add_task(self, task_id, title, description, due_date, created_by):
        try:
            unix = time.time_ns()

            # set default value of id
            if not task_id:
                task_id = str(math.floor(unix / 1000000))

            created_time = datetime.fromtimestamp(unix / 1000000000, timezone("UTC"))

            # insert
            cursor = self._connection.cursor()
            cursor.execute(
                f"""
                    INSERT INTO {config.POSTGRES_TASK_TABLENAME} (id, title, description, due_date, status, created_by, created_time, updated_by, updated_time)
                    VALUES ('{task_id}', '{title}', '{description}', '{due_date}', 'created', '{created_by}', '{created_time}', '{created_by}', '{created_time}')
                """
            )
            self._connection.commit()
            cursor.close()
            return task_id
        except Exception as e:
            self._connection.rollback()
            if cursor:
                cursor.close()
            raise e

    def update_task(self, task_id, user_id, title, description, due_date, status):
        try:
            set_query = ""
            if title or description or due_date or status:
                set_list = []
                if title:
                    set_list.append(f"title = '{title}'")
                if description:
                    set_list.append(f"description = '{description}'")
                if due_date:
                    set_list.append(f"due_date = '{due_date}'")
                if status:
                    set_list.append(f"status = '{status}'")
                set_query = ", ".join(set_list)
            else:
                return

            updated_time = datetime.now(timezone("UTC"))
            set_query += f", updated_by = '{user_id}', updated_time = '{updated_time}'"
            cursor = self._connection.cursor()
            cursor.execute(
                f"""
                    UPDATE {config.POSTGRES_TASK_TABLENAME}
                    SET {set_query}
                    WHERE id = '{task_id}'
                """
            )
            self._connection.commit()
            cursor.close()
            return
        except Exception as e:
            self._connection.rollback()
            if cursor:
                cursor.close()
            raise e

    def delete_task(self, task_id):
        try:
            query = (
                f"DELETE FROM {config.POSTGRES_TASK_TABLENAME} WHERE id = '{task_id}'"
            )
            cursor = self._connection.cursor()
            cursor.execute(query)
            self._connection.commit()
            cursor.close()
            return
        except Exception as e:
            self._connection.rollback()
            if cursor:
                cursor.close()
            raise e

    def get_user(self, user_id):
        try:
            cursor = self._connection.cursor()
            cursor.execute(
                f"SELECT * FROM {config.POSTGRES_USER_TABLENAME} WHERE {config.POSTGRES_USER_TABLENAME}.id = '{user_id}'"
            )
            record = cursor.fetchone()
            cursor.close()
            return record
        except Exception as e:
            self._connection.rollback()
            if cursor:
                cursor.close()
            raise e

    def format_result(self, record):
        if type(record) is tuple:
            return {
                "id": record[0],
                "title": record[1],
                "description": record[2],
                "due_date": record[3],
                "status": record[4],
                "created_by": record[5],
                "created_time": record[6],
                "updated_by": record[7],
                "updated_time": record[8],
            }

    def format_input(self, txt):
        if txt:
            temp = ",".join(["'{}'".format(element) for element in txt.split(",")])
            return f"IN ({temp})"


db = Database()
