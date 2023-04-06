FROM python:3.10

WORKDIR /srv
COPY ./requirements.txt .

RUN python3.10 -m venv env
RUN . env/bin/activate
RUN python3.10 -m pip install -r requirements.txt --upgrade pip

COPY ./app.py /srv/app.py
COPY ./static /srv/static
COPY ./templates /srv/templates

CMD ["python", "app.py", "--host", "0.0.0.0", "--port", "4685", "--db_path", "data/database.db"]
