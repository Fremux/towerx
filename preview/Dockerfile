FROM python:3.12

WORKDIR /app
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements.txt

WORKDIR /app/src
COPY src .

CMD [ "python", "main.py" ]