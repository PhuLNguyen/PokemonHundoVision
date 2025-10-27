#!/bin_DIR/bash
# Script to import Hundo CP data on MongoDB container startup

# Wait for MongoDB to be fully ready
# This simple sleep often suffices in a docker-compose environment but is less robust than a loop check.
sleep 5 

echo "Attempting to import hundo-data.jsonl into 'pogo' database..."

# Use mongoimport to load the JSONL file
# --db: specifies the database name (pogo)
# --collection: specifies the collection name (hundodata)
# --file: the path to the file inside the container
mongoimport --db pogo --collection hundodata --file /docker-entrypoint-initdb.d/hundo-data.jsonl --type json --maintainInsertionOrder

echo "Data import complete."