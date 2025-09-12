.PHONY: test-all
test-all:
	$(eval TEST_CMD=pytest -vv)
	docker-compose -f docker-compose.test.yml up --abort-on-container-exit --exit-code-from backend-test

.PHONY: test-unit
test-unit:
	$(eval TEST_CMD=pytest tests/unit)
	docker-compose -f docker-compose.test.yml up --abort-on-container-exit --exit-code-from backend-test

.PHONY: test-integration
test-integration:
	$(eval TEST_CMD=pytest tests/integration)
	docker-compose -f docker-compose.test.yml up --abort-on-container-exit --exit-code-from backend-test

.PHONY: run
run:
	docker-compose -f docker-compose.yml up --build