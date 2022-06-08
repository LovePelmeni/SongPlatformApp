FROM python:3.18.13-buster

RUN pip install --upgrade pip
COPY .project/requirements.txt ./requirements.txt
RUN pip install -r requirements.txt
COPY . .

RUN chmod +x ./proj-entrypoint.sh
ENTRYPOINT ["sh", "proj-entrypoint.sh"]





