#!/bin/sh

rabbitmqctl add_user rabbitmq_user rabbitmq_password
echo "rabbitmq user has been created..."
sleep 3

rabbitmqctl add_vhost rabbitmq_vhost
echo "rabbitmq vhost has been created..."
sleep 3

rabbtimqctl set_user_tags --user rabbitmq_user administrator
echo "set rabbitmq user as admin..."
sleep 3

rabbitmqctl set_permissions --vhost rabbitmq_vhost --user rabbitmq_user ".*" ".*" ".*"
echo "rabbitmq user has permissions..."
sleep 3


