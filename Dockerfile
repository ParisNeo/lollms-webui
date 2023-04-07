FROM python:3.10

WORKDIR /srv
COPY ./requirements.txt .

RUN python3 -m venv venv && . venv/bin/activate
RUN python3 -m pip install --no-cache-dir -r requirements.txt --upgrade pip

COPY ./app.py /srv/app.py
COPY ./static /srv/static
COPY ./templates /srv/templates

COPY ./models /srv/models
CMD ["python", "app.py", "--host", "0.0.0.0", "--port", "4685", "--db_path", "data/database.db"]
