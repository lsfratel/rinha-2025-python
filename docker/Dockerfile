FROM python:3.10-alpine

ENV PYTHONUNBUFFERED=1

RUN apk add --no-cache --virtual .build-deps \
    build-base \
    libev-dev

RUN apk add --no-cache libev netcat-openbsd

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir pdm

WORKDIR /app
COPY . .

RUN pdm install --prod && \
    apk del .build-deps && \
    rm -rf /root/.cache/pip

ENV PATH="/app/.venv/bin:$PATH"
