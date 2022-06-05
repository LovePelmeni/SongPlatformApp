FROM python:3.18.13-buster
WORKDIR /project/app/

ENV PYTHONUNBUFFERED=1
RUN pip --upgrade pip
COPY ./requirements.txt requirements.txt

RUN pip install psycopg2-binary --no-cache-dir --no-input
RUN pip install -r requirements.txt

COPY . .
ENTRYPOINT ["sh", "./proj-entrypoint.sh"]


