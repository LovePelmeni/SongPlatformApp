<<<<<<< HEAD

# Music Service. 

Docs Link: [Service API Endpoints Docs.](http://localhost:8000/swagger)

#Introduction 

`Music Service` - One Of The main components of the project.
It is used for serving application data related to customers and their activity.



#Requirements 

`python` 3.8 or above

`postgresql` 13.0 or above 

`docker` 1.4 or above 

`docker-compose` 3.8 (recommended)

`redis` - whatever version 

`RabbitMQ` - any management version.

#

`AWS S3` - have an account with following buckets:

`SONG_AUDIO_FILE_BUCKET` - bucket for storing audio files.
    
`SUBSCRIPTION_PREVIEW_BUCKET` - bucket for storing previews for subscriptions.
    
`USER_AVATAR_BUCKET` - bucket for storing user avatars.


#Technologies 
```ini

[FRAMEWORKS]

 - DJANGO (3.2) 

[DATABASES]

 - PostgresSQL (13.3)
 - REDIS 
 - AWS S3

[MESSAGE_BROKERS]

 - RABBITMQ

[DEPLOYMENT]
 - DOCKER-COMPOSE, DOCKER

```

=======
# Payment Service 

API Documentation Link: [DocLink](http://localhost:8081/docs/)

--- 

`Payment Service` - One of the Components of the Song Platform App.
It Allows People to make transactions and purchase Song Subscriptions on specific period of time, Also make refunds and so on...

---
## Dependencies 
```xml
<requirements>
    
<python>3.8 or above</python>
    
<postgresql>13.3 or above</postgresql>
    
<docker>1.41 or above</docker>
    
<docker-compose>3.9 or higher</docker-compose>
    
</requirements>

```
## Technologies 

For this project I'm using framework FastAPI as a Main Framework with following additions:

`ORM` - `Ormar and SQLAlchemy` as Integrator chosen the `Alembic`.
`Payment Platform` - `Stripe` one of the most popular  .  
`Database` - `postgresSQL`.

# Deployment 

`Docker` & `Docker-Compose`

### Possible Issues related to Deployment
I was building this API using `MacOS` Operational System on M1 so there probably can be some issues running it on `Windows` (On `Linux` Everything works perfectly).

If You are getting Some Errors, related to Postgresql `SCRAM-Authentication`, try to replace 
```dockerfile 
   ARG arch=amd64
   FROM --platform=linux/${arch} python:3.8.13-buster
```
On 

```dockerfile 
    FROM python:3.8.13-buster
```

# Usage

Clone This Repo to your IDE or Whatever.
```commandline

git clone --branch payment_service git@github.com/LovePelmeni/SongPlatformApp.git
    
```
Go the file in the Main Directory of the Project and run docker-compose.yaml,
then run python file responsible for stripe-cli

```commandline 
   docker-compose up -d 
```

```commandline
   python ./stripe_cli.py
```

#Simple Integration.
### Using python "requests" library
```doctest
   import requests 
   payment_service_url = 'http://localhost:8081/some-url/'
   session = requests.Session()
   http_response = session.method(url=payment_service_url,
   headers=headers, params=params, data=data, timeout=timeout)
```
### Using Curl 

```commandline
   curl -f http://localhost:8081/healthcheck/
```

Done! Make Sure all module/integration test has run successfully. 
### Go to the Link Above to get more info about API.
>>>>>>> origin/payment_service
