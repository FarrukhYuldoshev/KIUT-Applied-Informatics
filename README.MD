## Welcome to
# AI Department (API)


### About the Project

soon...

### About the BackEnd

soon...

### About the FrontEnd
You can view project in github with link: 


***

## Tech

* [FastAPI](https://fastapi.tiangolo.com/) - is a high-level `Python Web framework`
* [PostgreSQL](https://www.postgresql.org/) - open source object-relational database system

And many other libraries.

Dillinger requires [Python](https://www.python.org) `v3.11.0 > 3.11.6 <3.12`.

```shell
$ git clone https://github.com/FarrukhYuldoshev/Applied-Informatics.git
```

***

## Setting project

* `Linux`
```shell
$ virtualenv -p /usr/bin/python3 .venv
$ source .venv/bin/activate
$ pip install -r requirements.txt
```

* `Windows`
```shell
$ python -m venv ./venv
$ venv\Scripts\activate
$ pip install -r requirements.txt
```

* `MacBook`
```shell
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
```

***

## Development
### Configure `PostgreSQL`
Create clear database named `ai_department_db`.

Create `master_db_user` db user with password `applied-informatics-master` and grand privileges to him.

If you want to create a database with a different name, user and password, you can change the initial configuration to your own configuration.
```shell
$ sudo -u postgres psql
postgres=# ...
CREATE DATABASE ai_department_db;
CREATE USER master_db_user WITH PASSWORD 'applied-informatics-master';
ALTER ROLE master_db_user SET client_encoding TO 'utf8';
ALTER ROLE master_db_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE ai_department_db TO master_db_user;
GRANT ALL PRIVILEGES ON SCHEMA public TO master_db_user;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
\q
```
Migrate to database and run project.
```shell
$ python manage.py makemigrations
$ python manage.py migrate
$ python manage.py runserver
```
`Output`
```shell
INFO:     Will watch for changes in these directories: ['/current path/']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [28389] using StatReload
INFO:     Started server process [28391]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```
Open http://127.0.0.1:8000 in your browser for see result.
