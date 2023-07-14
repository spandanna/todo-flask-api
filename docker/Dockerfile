FROM python:3.9

WORKDIR /code

RUN python3 -m venv /opt/venv
ENV PATH=opt/venv/bin:$PATH

COPY requirements.txt /code
RUN python3 -m pip install -r requirements.txt

COPY . .

ENV FLASK_APP app.py
ENV FLASK_ENV development
ENV FLASK_RUN_PORT 5000
ENV FLASK_RUN_HOST 0.0.0.0
ENV SQLALCHEMY_DATABASE_URI sqlite:////code/data/todo.db

ENTRYPOINT flask run --host=${FLASK_RUN_HOST}
EXPOSE 5000
