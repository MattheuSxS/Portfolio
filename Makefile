.PHONY: test coverage


test:
	@echo "Running tests..."
	@pytest -v \
	--junitxml=tests-result.xml \
	--html=dist/reports/html/tests-result.html

coverage:
	@echo "Running tests with coverage..."
	@pytest -v \
	--junitxml=tests-result.xml \
	--html=dist/reports/html/tests-result.html \
	--cov-report term \
	--cov-branch \
	--cov=. \
	&& coverage xml -o coverage.xml \
	&& coverage html -d dist/reports/html/coverage_html
