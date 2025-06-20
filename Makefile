.DEFAULT_GOAL := default

default: install test lint

install:
	@uv pip install mcp
	@uv sync


start.mcp:
	@LOCAL_MODEL_PATH="" uv run main.py --host 0.0.0.0 --port 7860 --reload


# Start the terminal chat client
start.terminal:
	@python finaid_admin_mcp_client/src/interfaces/cli/terminal_chat.py --api http://localhost:8090


test:
	@pytest tests

test.coverage:
	@uv run coverage run -m pytest -v tests
	@uv run coverage report -m --omit='*/clients/*' --fail-under=75

typecheck:
	@mypy src tests main.py

pre_commit.install:
	@pre-commit install

lint: lint.code format.check

lint.code:
	@pylint main.py src tests  --rcfile=.pylintrc

format.check:
	@black . --check

format.write:
	@black .


build.docker:
	@docker compose up --build


hf.deploy:
	@huggingface-cli upload student-services-demo-mcp . --repo-type=space