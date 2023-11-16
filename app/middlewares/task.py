from flask import request
from functools import wraps
from app.middlewares import validate_query, validate_body


def list_task_validation(f):
    @wraps(f)
    def fn(*args, **kwargs):
        """
        query
            statuses
            due_dates
            due_date_since
            due_date_until
            created_users
            updated_users
            order
            limit
            offset
        """
        query = request.args

        try:
            validate_query(query, "limit", "int", False, False, None)
            validate_query(query, "offset", "int", False, False, None)
            validate_query(
                query,
                "order",
                "str",
                False,
                False,
                ["ASC", "DESC", "asc", "desc"],
            )
            validate_query(
                query,
                "statuses",
                "str",
                False,
                True,
                ["created", "pending", "in_progress", "completed"],
            )

            if "due_dates" in query:
                validate_query(query, "due_dates", "date", False, True, None)
            else:
                validate_query(query, "due_date_since", "date", False, False, None)
                validate_query(query, "due_date_until", "date", False, False, None)

                # has due_date_until but not due_date_since
                if "due_date_until" in query and "due_date_since" not in query:
                    return {
                        "error": "Bad request",
                        "message": "due_date_until must use with due_date_since",
                    }, 400

                # due_date_since > due_date_until
                due_date_since = query.get("due_date_since")
                due_date_until = query.get("due_date_until")
                if (
                    due_date_since
                    and due_date_until
                    and due_date_since > due_date_until
                ):
                    return {
                        "error": "Bad request",
                        "message": "due_date_since can't be greater than due_date_until",
                    }, 400

        except ValueError as e:
            return {"error": "Bad request", "message": str(e)}, 400

        return f(*args, **kwargs)

    return fn


def add_task_validation(f):
    @wraps(f)
    def fn(*args, **kwargs):
        """
        body
            id
            title (required)
            description (required)
            due_date (required)
        """
        if not request.is_json:
            return {
                "error": "Bad request",
                "message": "Invalid request body format",
            }, 400

        body = request.get_json()
        task_id = body.get("id")

        try:
            validate_body(body, "id", str, False, None)
            validate_body(body, "title", str, True, None)
            validate_body(body, "description", str, True, None)
            validate_body(body, "due_date", "date", True, None)

            if task_id and not task_id.isalnum():
                return {"error": "Bad request", "message": "id is invalid"}, 400

        except ValueError as e:
            return {"error": "Bad request", "message": str(e)}, 400

        return f(*args, **kwargs)

    return fn


def update_task_validation(f):
    @wraps(f)
    def fn(*args, **kwargs):
        """
        body
            title
            description
            due_date
            status
        """
        if not request.is_json:
            return {
                "error": "Bad request",
                "message": "Invalid request body format",
            }, 400

        body = request.get_json()

        try:
            validate_body(body, "title", str, False, None)
            validate_body(body, "description", str, False, None)
            validate_body(body, "due_date", "date", False, None)
            validate_body(
                body,
                "status",
                str,
                False,
                ["created", "pending", "in_progress", "completed"],
            )
        except ValueError as e:
            return {"error": "Bad request", "message": str(e)}, 400

        return f(*args, **kwargs)

    return fn
