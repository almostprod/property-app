web: poetry run property
client: yarn lerna exec -- yarn start
proxy: docker-compose run --name app_proxy --no-deps --rm --service-ports proxy
redis: docker-compose run --name app_redis --no-deps --rm --service-ports redis
db: docker-compose run --name app_db --no-deps --rm --service-ports db
pgweb: pgweb --url=$DATABASE_URI --listen=8081 --bind=0.0.0.0 --prefix=pgweb
