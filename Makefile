.PHONY: test-all
test-all:
	$(eval TEST_CMD=pytest --cov=. --cov-config=.coveragerc.all)
	docker-compose -f docker-compose.test.yml up --abort-on-container-exit --exit-code-from backend-test

.PHONY: test-unit
test-unit:
	$(eval TEST_CMD=pytest --cov=. --cov-config=.coveragerc.unit tests/unit)
	docker-compose -f docker-compose.test.yml up --abort-on-container-exit --exit-code-from backend-test

.PHONY: test-integration
test-integration:
	$(eval TEST_CMD=pytest --cov=. --cov-config=.coveragerc.integration tests/integration)
	docker-compose -f docker-compose.test.yml up --abort-on-container-exit --exit-code-from backend-test

.PHONY: run
run:
	docker-compose -f docker-compose-dev.yml up --build