FROM ubuntu:20.04

RUN apt-get install python3.9 -y
RUN pip install --upgrade pip
COPY .project/requirements.txt ./requirements.txt
RUN pip install -r requirements.txt
COPY . .

RUN chmod +x ./proj-entrypoint.sh
ENTRYPOINT ["sh", "proj-entrypoint.sh"]