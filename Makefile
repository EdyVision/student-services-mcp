.DEFAULT_GOAL := default

default: install test lint

install:
	@python -m pip install --upgrade pip
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
	@uv run coverage report -m --omit='*/clients/*' --fail-under=80

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

#cdk.deploy:
#	@export PYTHONPATH=$(PYTHONPATH) && cdk deploy ${STACK} --require-approval=never
#
#cdk.deploy.json:
#	@export PYTHONPATH=$(PYTHONPATH) && cdk deploy ${STACK} --require-approval=never --outputs-file=${CDK_OUTPUT_PATH}
#
#cdk.deploy_promote:
#	@export PYTHONPATH=$(PYTHONPATH) && cdk deploy ${STACK} --require-approval=never && \
#    $(MAKE) -C data_sync promote-live

# cdk.diff:
# 	@cdk diff

# cdk.synth:
# 	@cdk synth --require-approval never

# cdk.deploy:
# 	@cdk deploy