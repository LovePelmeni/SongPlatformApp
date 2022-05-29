FROM python:3.8.13-buster

WORKDIR /project/app/
ENV PYTHONUNBUFFERED=1
RUN pip --upgrade pip
COPY ./requirements.txt requirements.txt

RUN pip install psycopg2-binary --no-cache-dir --no-input
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000
ENTRYPOINT ["sh", "./project-docker-entrypoint.sh"]