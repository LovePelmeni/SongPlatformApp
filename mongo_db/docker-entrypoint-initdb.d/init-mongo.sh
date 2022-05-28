#!/bin/sh

set -e

mongo <<EOF

rs.initiate();


rs.add('localhost:27012');
rs.add('localhost:27013');


use admin
db.auth("mongo_user", "mongo_password")
database = db.getSiblingDB('mongo_sub_db');

database.createUser(
{ user: "mongo_sub_user", pwd: "mongo_sub_password",
roles: [{ role: "readWrite", db: "mongo_sub_db" }]
});

database.auth('mongo_sub_user', 'mongo_sub_password');
database.createCollection("sub_collection");

EOF