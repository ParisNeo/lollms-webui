FROM python:3.10

WORKDIR /srv
COPY ./requirements.txt .

COPY ./app.py /srv/app.py
COPY ./api /srv/api
COPY ./static /srv/static
COPY ./templates /srv/templates
COPY ./web /srv/web
COPY ./assets /srv/assets

# TODO: this is monkey-patch for check_update() function, should be disabled in Docker
COPY ./.git /srv/.git

VOLUME [ "/data" ]

# Monkey-patch (1): because "binding_zoo" install the packets inside venv, we cannot do pip install on build time
# Monkey-patch (2): send a "enter" keystroke to python to confirm the first launch process
CMD ["/bin/bash", "-c", " \
  python -m venv /data/venv; \
  source /data/venv/bin/activate; \
  python -m pip install --no-cache-dir -r requirements.txt --upgrade pip; \
  echo -ne '\n' | \
  python app.py \
  --host 0.0.0.0 \
  --port 9600 \
  --db_path /data/Documents/databases/database.db \
  --config /configs/config.yaml \
  "]
