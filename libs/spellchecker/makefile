.DEFAULT_GOAL := help

# Run PyTest requiring at least 65% coverage.
test:
	pytest ./tests \
	  --cov=src \
	  --cov=tests \
	  --cov-report term \
	  --cov-report html  --cov-report xml \
	  -vvv

# Install "requirements.txt" and "requirements-dev.txt", as well as pre-commit
install:
	pip3 install -r requirements.txt

# Install "requirements.txt" and "requirements-dev.txt", as well as pre-commit
install-dev:
	pip3 install -r requirements.txt -r requirements-dev.txt
	pre-commit install
	
# Validate Python code according to the style guide.
flake:
	flake8 ./tests --count --max-complexity=10 --max-line-length=127 --statistics

# Reformat Python code to conform to the PEP 8 style guide.
autopep:
	autopep8 --in-place --aggressive --aggressive -a -r ./src

# Reformat Python code according to the style guide.
black:
	black .

venv:
	virtualenv .venv \
	&& source .venv/bin/activate

build:
	docker build $(if $(noCache),--no-cache,) --pull -t pfizer/content-quality-service-spellcheck .

bash:
	docker run --rm -it --env-file .env pfizer/content-quality-service-spellcheck /bin/bash

# Run this like: `make run-command command="python3 --version"` OR make run command command="python3 -m src.main {options}"
run-command:
	docker run --rm --env-file .env pfizer/content-quality-service-spellcheck ${command}
