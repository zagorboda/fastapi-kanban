**Stack:**

- Python 3.9
- FastAPI 0.63
- PostgreSQL
- Docker
- Pytest
- GINO (not) ORM
- Alembic

**Demo:**

https://www.zagorboda.me/fastapi-kanban/docs

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

Create coverage report
```bash
docker-compose exec web coverage run -m pytest
```
```bash
docker-compose exec web coverage report -m
```
OR
```bash
docker-compose exec web coverage html
```