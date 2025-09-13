set TEST_CMD=pytest --cov=. --cov-config=.coveragerc.unit tests/unit
docker compose -f docker-compose.test.yml down
docker-compose -f docker-compose.test.yml up --abort-on-container-exit --exit-code-from backend-test