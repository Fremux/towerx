

```bash
 docker build --output=nginx/dist frontend
```

```bash
docker compose up --build -d
```

```bash
docker compose -f docker-compose.yml -f docker-compose.ssl.yml up --build
```
