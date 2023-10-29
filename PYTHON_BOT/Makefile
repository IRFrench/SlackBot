DEFAULT: help

env: ## Create the poetry environment
	poetry install --no-root

run: env ## Run the slack bot
	poetry run python3 app.py

run-dev: env ## Run the slack bot
	DEV=true poetry run python3 app.py


help: ## Show commands of the makefile (and any included files)
	@awk 'BEGIN {FS = ":.*?## "}; /^[0-9a-zA-Z_.-]+:.*?## .*/ {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)