PYTHON = $(shell which python3 || echo python)
PIP = $(shell which pip3 || echo pip)

make:
	@$(PYTHON) setup.py bdist_wheel

install: make
	sudo $(PIP) install dist/catcher-*

tests:
	@$(PYTHON) -m pytest --capture=sys --ignore=postgres-data

deploy: make
	twine upload dist/*

.PHONY: install
