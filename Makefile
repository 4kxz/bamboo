
all: fmt lint type

fmt: venv/bin/black
	$< src/main/python

lint: venv/bin/flake8
	$< src/main/python

type: venv/bin/mypy
	$< src/main/python

venv/bin/black: venv/bin/pip
	$< install black

venv/bin/flake8: venv/bin/pip
	$< install flake8

venv/bin/mypy: venv/bin/pip
	$< install mypy

venv/bin/pip:
	python3 -m venv venv
	$@ install -r requirements.txt

clean:
	rm -rf venv
	rm -rf .mypy_cache
