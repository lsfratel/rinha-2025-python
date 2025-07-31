from python:3.10-alpine

RUN apk add --no-cache \
    build-base         \
    python3-dev        \
    libev-dev

RUN pip install --upgrade pip
RUN pip install pdm

WORKDIR /app
COPY . .

RUN pdm install --prod
ENV PATH="/app/.venv/bin:$PATH"
