.PHONY: setup-dev check fix

div = $(shell printf '=%.0s' {1..120})

setup-dev:
	@echo "Setting up development environment..."
	@echo "Installing dev dependencies..."
	@pip install -r requirements-dev.txt
	@echo "Done!"

T="."
check:
	@echo ${div}
	ruff check $(T)
	ruff format $(T) --check
	@echo "Done!"

fix:
	@echo ${div}
	ruff format $(T)
	@echo ${div}
	ruff check $(T) --fix
	@echo "Done!"
