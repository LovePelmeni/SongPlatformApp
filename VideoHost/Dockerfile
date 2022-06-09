FROM python:3.8.13-buster

RUN pip install --upgrade pip
RUN pip install psycopg2-binary --no-cache-dir --no-input

COPY ./project/requirements.txt ./requirements.txt
RUN pip install -r requirements.txt
COPY . .

RUN chmod +x ./proj-entrypoint.sh
ENTRYPOINT ["sh", "proj-entrypoint.sh"]



