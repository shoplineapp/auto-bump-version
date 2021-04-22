FROM python:3.9-alpine

RUN apk update && apk add git

COPY requirements.txt /
RUN pip install -r /requirements.txt

COPY pipe /

ENTRYPOINT ["python3", "/pipe.py"]
