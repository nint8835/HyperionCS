FROM python:3.9-slim-buster

WORKDIR /opt/app
COPY . .

RUN python -m pip install -U pip &&\
    pip install poetry &&\
    poetry install --no-dev

CMD ["gunicorn", "-w", "9", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0", "hyperioncs:app"]