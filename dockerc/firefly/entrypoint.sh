#!/bin/bash
set -e
cmd="$@"

if [ -z "$DB_URI" ]; then
    export DB_URI=mongodb://0.0.0.0:27017
fi

function mongo_ready(){
python << END
import sys
import pymongo
maxSevSelDelay = 1
try:
    client = pymongo.MongoClient("$DB_URI", serverSelectionTimeoutMS=maxSevSelDelay)
except pymongo.errors.ServerSelectionTimeoutError as err:
    sys.exit(-1)
sys.exit(0)
END
}

until mongo_ready; do
  >&2 echo "MongoDB is unavailable - sleeping"
  sleep 1
done

>&2 echo "MongoDB is up - continuing..."

exec $cmd
