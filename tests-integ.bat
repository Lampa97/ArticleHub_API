set TEST_CMD=pytest tests/integration -vv
docker-compose -f docker-compose.test.yml up --abort-on-container-exit --exit-code-from backend-test