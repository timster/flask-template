.PHONY: clean server shell test testcov

clean:
	rm -fr build dist logs .covhtml .coverage .cache
	find . -name '*.egg' -exec rm -fr {} +
	find . -name '*.eggs' -exec rm -fr {} +
	find . -name '*.dist-info' -exec rm -fr {} +
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.pyc' -exec rm -fr {} +
	find . -name '*.pyc' -exec rm -fr {} +
	find . -name '*.log' -exec rm -fr {} +
	find . -name '*~' -exec rm -fr {} +
	find . -name '__pycache__' -exec rm -fr {} +

server:
	FLASK_DEBUG=1 FLASK_APP=flaskapi.wsgi flask run

shell:
	FLASK_DEBUG=1 FLASK_APP=flaskapi.wsgi flask shell

test:
	py.test

testcov:
	py.test --cov=.
	coverage html --directory=.covhtml
	open .covhtml/index.html
