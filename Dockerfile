FROM python:3.9-slim

RUN mkdir -p /usr/src/app

COPY . /usr/src/app
RUN cd /usr/src/app \
 && pip install --no-cache-dir -r requirements.txt

WORKDIR /

ENTRYPOINT ["cleanit"]
CMD ["--help"]
