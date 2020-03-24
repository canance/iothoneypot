#!/bin/bash 

psql postgres <<EOF
    CREATE USER firmadyne WITH password 'firmadyne';
EOF
createdb -O firmadyne firmware
psql -d firmware < /docker-entrypoint-initdb.d/schema 
