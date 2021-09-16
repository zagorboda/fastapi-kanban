FROM python:3.9-slim-buster

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /usr/src/app/requirements.txt

RUN pip install --upgrade pip  setuptools wheel \
    && pip install -r /usr/src/app/requirements.txt \
    && rm -rf /root/.cache/pip

COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

COPY . ./

ENTRYPOINT ["sh","/usr/src/app/entrypoint.sh"]

#RUN chmod 777 ./startup.sh
#RUN chmod +x ./startup.sh
#RUN ./startup.sh

#ENTRYPOINT echo "Hello World"
#ENTRYPOINT ["./startup.sh"]
