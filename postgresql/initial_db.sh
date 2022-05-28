#!/bin/sh

set -e
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DATABASE" <<-EOSQL
  CREATE DATABASE sub_db;
  CREATE USER postgres_sub_user WITH PASSWORD 'Kirill';
  GRANT ALL PRIVILEGES ON DATABASE sub_db TO postgres_sub_user;

EOSQL