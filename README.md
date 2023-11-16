# Task Management API
This api is compatible with `Python` (version 3) and `PostgreSQL` by using `flask` for API and `psycopg2` for connect to database

## Prerequisite
Required to have `docker` in machine, Below are commands to install `docker`

```
curl -sSL https://get.docker.com/ | sh
```
or
```
wget -qO- https://get.docker.com/ | sh
```

## Step to run
### Installing Database (If doesn't have)
1. Pull PostgreSQL image
```
docker pull postgres:12.16-bullseye
```
1. Run service (replace `{password}` with your passward)
```
docker run --name postgres -e POSTGRES_PASSWORD={password} -d -p 5432:5432 postgres:12.16-bullseye
```
1. Create database (replace `{db_name}` with your db name)
```
docker exec -it postgres sh
```
```
psql -U postgres -c "CREATE DATABASE {db_name}"
```
and then exit
```
exit
```
---
### Clone Repository
1. Clone repository when you are in desired directory
```
git clone git@github.com:arttfisol/task-management-api.git
```
or
```
git clone https://github.com/arttfisol/task-management-api.git
```
1. Change directory to the project
```
cd task-management-api
```
---
### Build Docker Image

```
docker build -t task-management-api:1.0.0 .
```
---
### Run API
1. Create .env file at root of project's directory and put config to it (change config to yours), Below is the example of .env file
```
NODE_ENV=development
PORT=6060
POSTGRES_HOST=localhost
POSTGRES_USER=postgres
POSTGRES_PASS=password
POSTGRES_DBNAME=test_db
POSTGRES_TASK_TABLENAME=test_tasks
POSTGRES_USER_TABLENAME=test_users
```
Ps. if your `PostgreSQL` run in the same machine and in `Docker`, run the command below to retrieve `POSTGRES_HOST` and replace it in .env file
```
docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' {container_name or container ID}
```
2. Run API (Change the `{port}` to `PORT` in .env file before run this command)
```
docker run -d --name task-management-api -v $(pwd)/.env:/usr/src/.env -p {port}:{port} task-management-api:1.0.0 
```
1. Initial Database (there are commands to drop table to make sure that DB name and tabel name in .env file are correct) 
**`POSTGRES_DBNAME` must exist before run this command**
```
docker exec -it task-management-api sh
```
```
python db.py
```
and then exit
```
exit
```
## Testing
For testing, you can use curl in example below to request to API, or use [task_management_api.postman_collection.json](https://github.com/arttfisol/task-management-api/blob/master/task_management_api.postman_collection.json) by import to your postman
## About Database
From script to initial database, we create 2 tables\
The first one is `user` table, there are only 2 fields
```
{
    "id": str,
    "name": str
}
```
that we already insert 5 records as ('user1', 'name1'), ('user2', 'name2') ...

The second one is `task` table that `created_by` and `updated_by` reference to user.id
```
{
    "id": str,
    "title": str,
    "description": str,
    "due_date": date,
    "status": str enum["created", "pending", "in_progress", "completed"],
    "created_by": str,
    "created_time": timestamptz,
    "updated_by": str,
    "updated_time": timestamptz
}
```
## About API Path

We provide 6 paths (including path for ping)\
*PS. All path except ping path will need to put `headers.Authorization` = `{user.id}` for use as a mock authentication (can use every user from id `user1` to `user5`)*
## Ping
Path for health check service
```
GET /ping
```
Request Example
```
curl -i http://localhost:6060/ping
```
Response Example
```
HTTP/1.1 200 OK
Content-Type: text/html; charset=utf-8
Content-Length: 4
Access-Control-Allow-Origin: *
Date: Sun, 12 Nov 2023 09:22:46 GMT

pong
```
## List Tasks
Path for list tasks, filter by query string
```
GET /api/tasks
```
There are 7 query string that can be used in this path\
If it's not provide any field in query string means get all for that field
| Query String | Description | Format | Example |
| ------------ | ----------- | ------ | ------- |
| `statuses` | status that need to query, can be multiple status (combine with comma) | | created,in_progress |
| `due_dates` | due date that need to query, can be multiple status (combine with comma) | %Y-%m-%d | 2023-05-18,2022-06-01 |
| `due_date_since` | due date that need to query as a range, use with due_date_until, (it will work if due_dates  isn't include in query string) | %Y-%m-%d | 2023-01-05 |
| `due_date_until` | due date that need to query as a range, use with due_date_since, (it will work if due_dates  isn't include in query string) (default value is today) | %Y-%m-%d | 2023-01-05 |
| `limit` | maximum number of result that need to return, it will return all if value is 0 (default value is 10) | | 15 |
| `offset` | number of result that need to skip (default value is 0) | | 15 |
| `order` | sort result with field `created_time` (default value is DESC) | ASC,DESC | ASC |

\
Request Example
```
curl -i -H 'Authorization: user1'  http://localhost:6060/api/tasks?statuses=created,pending&due_date_since=2023-05-01&due_date_until=2023-10-31&limit=15&offset=5&order=ASC
```

Response Example
```
HTTP/1.1 200 OK
Content-Type: application/json
Content-Length: 31
Access-Control-Allow-Origin: *
Date: Sun, 12 Nov 2023 09:08:08 GMT

{"error":false,"id":"task001"}
```

## Add Task
Path for add task. If add task success, user.id in `headers.Authorization` will be user who created and latest updated the task. `status` of task will be `created`.
```
POST /api/tasks
```
| Body | Description | Required | Example |
| ---- | ----------- | -------- | ------- |
| `id` | Task ID (automatically generate if `id` not include in body), can be only English alphabets and number | No | "taskid001"
| `title` | Title of task | Yes | "This is title of task" |
| `description` | Description of task | Yes | "This is description of task |
| `due_date` | Due date of task | Yes | "2023-05-01" |

\
Request Example
```
curl -i -H 'Authorization: user1' -H "Content-Type: application/json" -d '{"id":"task001","title":"title of task","description":"desc","due_date": "2023-05-01"}' -X POST http://localhost:6060/api/tasks
```
Response Example
```
HTTP/1.1 200 OK
Content-Type: application/json
Content-Length: 31
Access-Control-Allow-Origin: *
Date: Sun, 12 Nov 2023 09:08:08 GMT

{"error":false,"id":"task001"}
```
## Get Task
Path for get specific task
```
GET /api/tasks/<task_id>
```
Request Example
```
curl -i -H 'Authorization: user1' http://localhost:6060/api/tasks/task001
```
Response Example
```
HTTP/1.1 200 OK
Content-Type: application/json
Content-Length: 314
Access-Control-Allow-Origin: *
Date: Sun, 12 Nov 2023 09:16:49 GMT

{"error":false,"task":{"created_by":{"id":"user1","name":"name1"},"created_time":"2023-11-15T09:08:08.391847+00:00","description":"desc","due_date":"2023-05-01","id":"task001","status":"created","title":"title of task","updated_by":{"id":"user1","name":"name1"},"updated_time":"2023-11-15T09:08:08.391847+00:00"}}
```
## Update Task
Path for update specific task. If add update success, user.id in `headers.Authorization` will be user who updated the task.
```
PUT /api/tasks/<task_id>
```

| Body | Description | Required | Example |
| ---- | ----------- | -------- | ------- |
| `title` | Title of task | No | "Edited title"
| `description` | Description of task | No | "Edited Desciption" |
| `due_date` | Due date of task | No | "2033-12-01" |
| `status` | Status of task | No | "completed" |

\
Request Example
```
curl -i -H 'Authorization: user1' -H "Content-Type: application/json" -d '{"title":"Edited title","title":"title of task","description":"desc","due_date": "2023-05-01"}' -X PUT http://localhost:6060/api/tasks/task001
```
Response Example
```
HTTP/1.1 200 OK
Content-Type: application/json
Content-Length: 31
Access-Control-Allow-Origin: *
Date: Sun, 12 Nov 2023 09:27:09 GMT

{"error":false,"id":"task001"}
```
## Delete Task
Path for delete specific task
```
DELEET /api/tasks/<task_id>
```
Request Example
```
curl -i -H 'Authorization: user1' -X DELETE http://localhost:6060/api/tasks/task001
```
Response Example
```
HTTP/1.1 200 OK
Content-Type: application/json
Content-Length: 31
Access-Control-Allow-Origin: *
Date: Sun, 12 Nov 2023 09:28:02 GMT

{"error":false,"id":"task001"}
```
   
