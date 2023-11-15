from flask import request
from functools import wraps
from app.middlewares import is_valid_date


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
        order = request.args.get("order")
        limit = request.args.get("limit")
        offset = request.args.get("offset")
        statuses = request.args.get("statuses")
        due_dates = request.args.get("due_dates")
        due_date_since = request.args.get("due_date_since")
        due_date_until = request.args.get("due_date_until")

        if order and order.upper() not in ["ASC", "DESC"]:
            return {"error": "Bad request", "message": "Invalid order"}, 400

        if (limit and not limit.isdigit()) or (offset and not offset.isdigit()):
            return {"error": "Bad request", "message": "Invalid limit or offset"}, 400

        if statuses and [
            status
            for status in statuses.split(",")
            if status not in ["created", "pending", "in_progress", "completed"]
        ]:
            return {
                "error": "Bad request",
                "message": "Invalid statuses",
            }, 400

        if due_dates:
            if [date for date in due_dates.split(",") if not is_valid_date(date)]:
                return {"error": "Bad request", "message": "Invalid due_dates"}, 400

        elif due_date_since:
            if not is_valid_date(due_date_since):
                return {
                    "error": "Bad request",
                    "message": "Invalid due_date_since",
                }, 400

            if due_date_until:
                if not is_valid_date(due_date_until):
                    return {
                        "error": "Bad request",
                        "message": "Invalid due_date_until",
                    }, 400
                if due_date_since > due_date_until:
                    return {
                        "error": "Bad request",
                        "message": "due_date_since can't be greater than due_date_until",
                    }, 400

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
        title = body.get("title")
        due_date = body.get("due_date")
        description = body.get("description")

        if "id" in body and (type(task_id) != str or not task_id.isalnum()):
            return {"error": "Bad request", "message": "Invalid id"}, 400

        if type(title) != str or not title:
            return {"error": "Bad request", "message": "Invalid title"}, 400

        if type(description) != str or not description:
            return {"error": "Bad request", "message": "Invalid description"}, 400

        if type(due_date) != str or not is_valid_date(due_date):
            return {"error": "Bad request", "message": "Invalid due_date"}, 400

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
        title = body.get("title")
        status = body.get("status")
        due_date = body.get("due_date")
        description = body.get("description")

        if "title" in body and (type(title) != str or not title):
            return {"error": "Bad request", "message": "Invalid title"}, 400

        if "description" in body and (type(description) != str or not description):
            return {"error": "Bad request", "message": "Invalid description"}, 400

        if "status" in body and (
            type(status) != str
            or not status
            or status not in ["created", "pending", "in_progress", "completed"]
        ):
            return {"error": "Bad request", "message": "Invalid status"}, 400

        if "due_date" in body and (
            type(due_date) != str or not is_valid_date(due_date)
        ):
            return {"error": "Bad request", "message": "Invalid due_date"}, 400

        return f(*args, **kwargs)

    return fn
