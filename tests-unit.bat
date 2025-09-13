set TEST_CMD=pytest tests/unit -vv
docker-compose -f docker-compose.test.yml up --abort-on-container-exit --exit-code-from backend-test