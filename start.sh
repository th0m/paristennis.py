#!/bin/bash
export LANG=en_US.UTF-8
echo Start Mongo
mongod --fork --logpath /home/tennis/log/mongo.log
echo Start Redis
redis-server > /home/tennis/log/redis.log &
echo Start Postfix
postfix start 
echo Start Rest
/home/tennis/rest.py > /home/tennis/log/rest.log &
echo Start Back
/home/tennis/back.py > /home/tennis/log/back.log
