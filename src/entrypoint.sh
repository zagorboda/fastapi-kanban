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

#if [ ! -d /usr/src/media ]; then
#  mkdir /usr/src/media
#fi
#
#if [ ! -d /usr/src/media/profile_pic ]; then
#  mkdir /usr/src/media/profile_pic
#fi

#uvicorn app.server:app --reload --host 0.0.0.0 --port 8000
