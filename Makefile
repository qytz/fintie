.PHONY: clean virtualenv test docker dist dist-upload

clean:
	find . -name '*.py[co]' -delete

virtualenv:
	virtualenv --prompt '|> fintie <| ' .env
	.env/bin/pip install pipenv
	.env/bin/pipenv install --dev
	.env/bin/python setup.py develop
	@echo
	@echo "VirtualENV Setup Complete. Now run: source .env/bin/activate"
	@echo

test:
	python -m pytest \
		-v \
		--cov=fintie \
		--cov-report=term \
		--cov-report=html:coverage-report \
		tests/

docker: clean
	docker build -t fintie:latest .

dist: clean
	rm -rf dist/*
	python setup.py sdist
	python setup.py bdist_wheel

dist-upload:
	twine upload dist/*
