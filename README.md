
### Run locally
```
docker run -d --name authservice -p 8010:8010 -e DB_ENGINE=django.db.backends.postgresql -e POSTGRES_HOST=localhost -e POSTGRES_PORT=5440 -e POSTGRES_DB=udlafutbolappusuarios -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=0000 dase123/udlaia-stats:authservice
```