
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

