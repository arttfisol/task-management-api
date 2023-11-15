from db import db
from psycopg2 import IntegrityError
from flask import Blueprint, request, g
from app.middlewares.task import (
    list_task_validation,
    add_task_validation,
    update_task_validation,
)

task_bp = Blueprint("task", __name__)


@task_bp.before_request
def middleware():
    user_id = request.headers.get("Authorization")
    user = db.get_user(user_id)
    if not user:
        return {"error": "Unauthorized"}, 401
    g.user_id = user_id
    return


@task_bp.route("/", methods=["GET"])
@list_task_validation
def list_tasks():
    try:
        limit = request.args.get("limit") or "10"
        offset = request.args.get("offset") or "0"
        order = (request.args.get("order") or "DESC").upper()

        tasks = db.get_task_list(
            order=order,
            limit=limit,
            offset=offset,
            statuses=request.args.get("statuses"),
            due_dates=request.args.get("due_dates"),
            created_users=request.args.get("created_users"),
            updated_users=request.args.get("updated_users"),
            due_date_since=request.args.get("due_date_since"),
            due_date_until=request.args.get("due_date_until"),
        )
        return {"error": False, "tasks": tasks, "limit": limit, "offset": offset}
    except Exception as e:
        raise e


@task_bp.route("/", methods=["POST"])
@add_task_validation
def add_task():
    try:
        body = request.get_json()
        created_by = g.user_id
        task_id = body.get("id")
        title = body.get("title")
        due_date = body.get("due_date")
        description = body.get("description")

        inserted_id = db.add_task(
            title=title,
            task_id=task_id,
            due_date=due_date,
            created_by=created_by,
            description=description,
        )
        return {"error": False, "id": inserted_id}
    except IntegrityError as e:
        print(e.pgerror)
        return {"error": "Bad request", "message": e.pgerror}, 400
    except Exception as e:
        raise e


@task_bp.route("/<task_id>", methods=["GET"])
def get_task(task_id):
    try:
        task = db.get_task(task_id)
        if not task:
            return {"error": "Not found", "message": "Task not found"}, 404

        return {"error": False, "task": task}
    except Exception as e:
        raise e


@task_bp.route("/<task_id>", methods=["PUT"])
@update_task_validation
def update_task(task_id):
    try:
        task = db.get_task(task_id)
        if not task:
            return {"error": "Not found", "message": "Task not found"}, 404

        body = request.get_json()
        user_id = g.user_id
        title = body.get("title")
        status = body.get("status")
        due_date = body.get("due_date")
        description = body.get("description")

        db.update_task(
            title=title,
            status=status,
            task_id=task_id,
            user_id=user_id,
            due_date=due_date,
            description=description,
        )

        return {"error": False, "id": task_id}
    except Exception as e:
        raise e


@task_bp.route("/<task_id>", methods=["DELETE"])
def delete_task(task_id):
    try:
        task = db.get_task(task_id)
        if not task:
            return {"error": "Not found", "message": "Task not found"}, 404

        db.delete_task(task_id)
        return {"error": False, "id": task_id}
    except Exception as e:
        raise e
