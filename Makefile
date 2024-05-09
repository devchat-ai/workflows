.PHONY: setup-dev check fix

div = $(shell printf '=%.0s' {1..120})

setup-dev:
	@echo "Setting up development environment..."
	@echo "Installing dev dependencies..."
	@pip install -r requirements-dev.txt
	@echo "Done!"

check:
	@echo ${div}
	ruff check .
	ruff format . --check
	@echo "Done!"

fix:
	@echo ${div}
	ruff format .
	@echo ${div}
	ruff check . --fix
	@echo "Done!"
