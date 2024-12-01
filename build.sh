#!/usr/bin/bash

docker build --output=nginx/dist frontend
docker compose -f docker-compose.yml -f docker-compose.ssl.yml up --build