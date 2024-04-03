EMS_REPORT = ${PWD}/ems-report/src/
LOG_PARSE = ${PWD}/log-parse/src/
export PYTHONPATH = ${EMS_REPORT}:${LOG_PARSE}

install:
	python -m pip install --upgrade pip && \
	python -m pip install -r requirements-all.txt

install-lambda-deps:
	python -m pip install --upgrade pip && \
	python -m pip install -r requirements-ems-report.txt -t ems-report/src/ && \
	python -m pip install -r requirements-log-parse.txt -t log-parse/src/

test_file ?= tests/
pytest:
	pytest $(test_file)
