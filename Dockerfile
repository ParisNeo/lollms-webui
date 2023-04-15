FROM python:3.10

WORKDIR /srv
COPY ./requirements.txt .

RUN python3 -m venv venv && . venv/bin/activate
RUN python3 -m pip install --no-cache-dir -r requirements.txt --upgrade pip

COPY ./app.py /srv/app.py
COPY ./pyGpt4All/api.py /srv/pyGpt4All/api.py
COPY ./pyGpt4All/db.py /srv/pyGpt4All/db.py
COPY ./pyGpt4All/config.py /srv/pyGpt4All/config.py
COPY ./pyGpt4All/extension.py /srv/pyGpt4All/extension.py
COPY ./static /srv/static
COPY ./templates /srv/templates

# COPY ./models /srv/models  # Mounting model is more efficient
CMD ["python", "app.py", "--host", "0.0.0.0", "--port", "9600", "--db_path", "data/database.db"]
