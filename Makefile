make:
	python setup.py bdist_wheel

install: make
	sudo pip install dist/catcher-*

tests:
	python -m pytest --capture=sys

deploy: make
	twine upload dist/*

.PHONY: install
