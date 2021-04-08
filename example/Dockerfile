FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

COPY ./app /app/app

WORKDIR /app/app

RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /

ARG CONNECTION_STRING
ARG DATABASE
ARG NODES
ARG USER_POOL_ID
ARG USER_POOL_WEB_CLIENT_ID

ENV CONNECTION_STRING=$CONNECTION_STRING
ENV DATABASE=$DATABASE
ENV NODES=$NODES
ENV USER_POOL_ID=$USER_POOL_ID
ENV USER_POOL_WEB_CLIENT_ID=$USER_POOL_WEB_CLIENT_ID

RUN openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.crt -days 365 -nodes -subj "/C=CA/ST=ON/L=TORONTO/O=Blockmedi Solutions/CN=Blockmedi"

CMD ["gunicorn", "-b", "0.0.0.0:443", "--keyfile", "key.pem", "--certfile", "cert.crt", "-k", "uvicorn.workers.UvicornWorker", "app.main:app"]