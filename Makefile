.PHONY: test

test:
	PYTHONPATH=backend uv run python -m unittest discover -s backend/tests
