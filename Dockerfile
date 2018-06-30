FROM python:3-alpine

ADD pysurfcast.py /
RUN apk --no-cache add py-pip gcc musl-dev libjpeg-turbo-dev python-dev zlib-dev
ENV LIBRARY_PATH=/lib:/usr/lib
RUN pip install pillow

ENTRYPOINT [ "python", "./pysurfcast.py" ]
