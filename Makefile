install:
	python -m pip install --upgrade pip && \
	python -m pip install -r requirements-all.txt

install-lambda-deps:
	python -m pip install --upgrade pip && \
	python -m pip install -r requirements-ems-report.txt -t ems-report/src/ && \
	python -m pip install -r requirements-log-parse.txt -t log-parse/src/
