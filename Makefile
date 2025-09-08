PY=python3
APP=app.main:app
PORT?=8000

.PHONY: install run test docker-build docker-run lint

install:
	$(PY) -m pip install -r requirements.txt

run:
	uvicorn $(APP) --host 0.0.0.0 --port $(PORT)

test:
	pytest -q

docker-build:
	docker build -t urlshort:mvp .

docker-run:
	docker run --rm -p $(PORT):8000 urlshort:mvp
