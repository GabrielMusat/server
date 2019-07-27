FROM python:3.6

WORKDIR /app

COPY logger.py /app/
COPY sanity_checker.py /app/
COPY artenea_server.json /app/
COPY requirements.txt /app/
COPY server.py /app/

RUN pip install -r requirements.txt