#!bin/sh

rabbitmqctl add_user --username rabbitmq_broker_user --password rabbitmq_broker_password
rabbitmqctl add_vhost rabbitmq_vhost
rabbitmqctl set_user_tags rabbitmq_broker_user administrator
rabbitmqctl set_permissions --vhost rabbitmq_broker_vhost rabbitmq_broker_user ".*", ".*", ".*"