#!/bin/sh

#while !</dev/tcp/db/5432;
#  do sleep 1;
#done;

# TODO: find cause of key duplication error
alembic upgrade head

#FIRST_CONTAINER_START="/usr/FIRST_CONTAINER_START"
#if [ ! -e $FIRST_CONTAINER_START ]; then
#  touch $FIRST_CONTAINER_START
#fi

mkdir /usr/src/media
mkdir /usr/src/media/profile_pic

uvicorn app.server:app --reload --host 0.0.0.0 --port 8000
