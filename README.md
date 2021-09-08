Run project
```bash
docker-compose up --build
```

Run tests
```bash
docker-compose exec web pytest
```

Connect to db

```bash
docker-compose exec db psql -U admin -d fastapi_dev
``` 

Run migrations

```bash
docker-compose exec web alembic revision -m 'New migrations' --autogenerate
docker-compose exec web alembic upgrade head
```