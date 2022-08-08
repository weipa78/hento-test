SHELL=/bin/bash

build-staging:
	sam build --config-env staging

deploy-staging:
	sam deploy --config-env staging

migrate:
	python -m tools.migrate

make-venv:
	python -m venv .venv
	( \
		source ./.venv/bin/activate; \
		pip install -r requirements.txt; \
	)
