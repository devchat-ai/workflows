div = $(shell printf '=%.0s' {1..120})

setup-dev:
	@echo "Setting up development environment..."
	@echo "Installing dev dependencies..."
	@~/.chat/mamba/envs/devchat-commands/bin/pip install -r requirements-dev.txt
	@echo "Done!"

check:
	@echo ${div}
	~/.chat/mamba/envs/devchat-commands/bin/python -m ruff check .
	~/.chat/mamba/envs/devchat-commands/bin/python -m ruff format . --check
	@echo "Done!"

fix:
	@echo ${div}
	~/.chat/mamba/envs/devchat-commands/bin/python -m ruff format .
	@echo ${div}
	~/.chat/mamba/envs/devchat-commands/bin/python -m ruff check . --fix
	@echo "Done!"
